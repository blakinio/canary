#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "security" / "malformed_packet_runtime_runner.py"

spec = importlib.util.spec_from_file_location("malformed_packet_runtime_runner", RUNNER_PATH)
assert spec is not None and spec.loader is not None
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


class MalformedPacketRuntimeRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.artifact_dir = self.root / "artifacts"
        self.artifact_dir.mkdir()
        self.binary = self.root / "canary"
        self.binary.write_bytes(b"exact-canary-binary")
        self.stdout_path = self.artifact_dir / "canary.stdout.log"
        self.stderr_path = self.artifact_dir / "canary.stderr.log"
        self.stdout_path.write_text("server online!\n", encoding="utf-8")
        self.stderr_path.write_text("", encoding="utf-8")
        self.context = SimpleNamespace(
            host="127.0.0.1",
            status_port=7473,
            binary_path=self.binary,
            artifact_dir=self.artifact_dir,
            stdout_path=self.stdout_path,
            stderr_path=self.stderr_path,
            server_pid=1234,
        )
        self.plan_path = self.root / "plan.json"
        self.plan = {
            "schema": runner.core.PLAN_SCHEMA,
            "id": "test-status-parser",
            "authorized_repository": runner.core.AUTHORIZED_REPOSITORY,
            "driver": runner.core.DRIVER_ID,
            "service": runner.core.SERVICE_ID,
            "cases": ["zero-length-frame"],
        }
        self.plan_path.write_text(json.dumps(self.plan, indent=2) + "\n", encoding="utf-8")

    def test_case_sources_are_deterministic_distinct_loopback_pairs(self) -> None:
        pairs = [runner.source_ips_for_case(index) for index in range(runner.core.MAX_CASES)]
        self.assertEqual(pairs[0], ("127.0.0.2", "127.0.0.3"))
        self.assertEqual(pairs[-1], ("127.0.0.32", "127.0.0.33"))
        flattened = [source for pair in pairs for source in pair]
        self.assertEqual(len(set(flattened)), runner.core.MAX_CASES * 2)
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-index-out-of-range"):
            runner.source_ips_for_case(runner.core.MAX_CASES)

    def test_source_requires_literal_ipv4_loopback(self) -> None:
        runner._require_loopback_source("127.0.0.2")
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-literal-ip"):
            runner._require_loopback_source("localhost")
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-loopback"):
            runner._require_loopback_source("10.0.0.1")
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-loopback"):
            runner._require_loopback_source("::1")

    def test_execute_plan_uses_distinct_malformed_and_control_sources(self) -> None:
        malformed_calls: list[tuple[str, int, float, str]] = []
        control_calls: list[tuple[str, int, float, str]] = []

        def malformed(case, host: str, port: int, timeout: float, source_ip: str) -> None:
            del case
            malformed_calls.append((host, port, timeout, source_ip))

        def control(host: str, port: int, timeout: float, source_ip: str) -> None:
            control_calls.append((host, port, timeout, source_ip))

        with mock.patch.object(runner, "probe_malformed_case_from_source", side_effect=malformed), mock.patch.object(
            runner, "probe_status_control_from_source", side_effect=control
        ):
            result = runner.execute_plan(self.plan_path, self.plan, self.context, timeout_seconds=0.2)

        self.assertEqual(result, 0)
        self.assertEqual(malformed_calls, [("127.0.0.1", 7473, 0.2, "127.0.0.2")])
        self.assertEqual(control_calls, [("127.0.0.1", 7473, 0.2, "127.0.0.3")])
        report = json.loads((self.artifact_dir / "malformed-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "success")
        self.assertEqual(report["cases"][0]["malformed_source_ip"], "127.0.0.2")
        self.assertEqual(report["cases"][0]["control_source_ip"], "127.0.0.3")
        self.assertEqual(report["cases"][0]["malformed_probe"], "connection-terminated")
        self.assertEqual(report["cases"][0]["control_probe"], "pass")
        self.assertIn("tools/security/malformed_packet_runtime_runner.py", report["evidence"]["provider_sha256"])

    def test_execute_plan_fails_closed_when_control_probe_fails(self) -> None:
        with mock.patch.object(runner, "probe_malformed_case_from_source", return_value=None), mock.patch.object(
            runner,
            "probe_status_control_from_source",
            side_effect=runner.core.ProbeFailure("control-invalid-response"),
        ):
            result = runner.execute_plan(self.plan_path, self.plan, self.context, timeout_seconds=0.2)

        self.assertEqual(result, 1)
        report = json.loads((self.artifact_dir / "malformed-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["failure"], "zero-length-frame:control-invalid-response")
        self.assertEqual(report["cases"][0]["failure"], "control-invalid-response")
        self.assertEqual(report["cases"][0]["malformed_source_ip"], "127.0.0.2")
        self.assertEqual(report["cases"][0]["control_source_ip"], "127.0.0.3")

    def test_execute_plan_stops_after_first_failed_case(self) -> None:
        plan = dict(self.plan)
        plan["cases"] = ["zero-length-frame", "oversized-length-frame"]
        self.plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

        malformed_sources: list[str] = []
        control_sources: list[str] = []

        def malformed(case, host: str, port: int, timeout: float, source_ip: str) -> None:
            del case, host, port, timeout
            malformed_sources.append(source_ip)

        def control(host: str, port: int, timeout: float, source_ip: str) -> None:
            del host, port, timeout
            control_sources.append(source_ip)
            raise runner.core.ProbeFailure("control-invalid-response")

        with mock.patch.object(runner, "probe_malformed_case_from_source", side_effect=malformed), mock.patch.object(
            runner, "probe_status_control_from_source", side_effect=control
        ):
            result = runner.execute_plan(self.plan_path, plan, self.context, timeout_seconds=0.2)

        self.assertEqual(result, 1)
        self.assertEqual(malformed_sources, ["127.0.0.2"])
        self.assertEqual(control_sources, ["127.0.0.3"])
        report = json.loads((self.artifact_dir / "malformed-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(len(report["cases"]), 1)
        self.assertEqual(report["cases"][0]["id"], "zero-length-frame")


if __name__ == "__main__":
    unittest.main()
