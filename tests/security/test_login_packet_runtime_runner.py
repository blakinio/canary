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
RUNNER_PATH = ROOT / "tools" / "security" / "login_packet_runtime_runner.py"

spec = importlib.util.spec_from_file_location("login_packet_runtime_runner", RUNNER_PATH)
assert spec is not None and spec.loader is not None
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


class LoginPacketRuntimeRunnerTests(unittest.TestCase):
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
            login_port=7471,
            binary_path=self.binary,
            artifact_dir=self.artifact_dir,
            stdout_path=self.stdout_path,
            stderr_path=self.stderr_path,
            server_pid=1234,
        )
        self.plan_path = self.root / "plan.json"
        self.plan = {
            "schema": runner.core.PLAN_SCHEMA,
            "id": "test-login-parser",
            "authorized_repository": runner.core.AUTHORIZED_REPOSITORY,
            "driver": runner.core.DRIVER_ID,
            "service": runner.core.SERVICE_ID,
            "cases": ["current-prelude-only"],
        }
        self.plan_path.write_text(json.dumps(self.plan, indent=2) + "\n", encoding="utf-8")

    def test_case_sources_are_deterministic_distinct_loopback_pairs(self) -> None:
        pairs = [runner.source_ips_for_case(index) for index in range(runner.core.MAX_CASES)]
        self.assertEqual(pairs[0], ("127.0.0.40", "127.0.0.41"))
        self.assertEqual(pairs[-1], ("127.0.0.70", "127.0.0.71"))
        flattened = [source for pair in pairs for source in pair]
        self.assertEqual(len(set(flattened)), runner.core.MAX_CASES * 2)
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-index-out-of-range"):
            runner.source_ips_for_case(runner.core.MAX_CASES)

    def test_source_requires_literal_ipv4_loopback(self) -> None:
        runner._require_loopback_source("127.0.0.40")
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-literal-ip"):
            runner._require_loopback_source("localhost")
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-loopback"):
            runner._require_loopback_source("10.0.0.1")
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-loopback"):
            runner._require_loopback_source("::1")

    def test_execute_plan_uses_distinct_case_and_control_sources(self) -> None:
        case_calls: list[tuple[str, int, float, str]] = []
        control_calls: list[tuple[str, int, float, str]] = []

        def case_probe(case, host: str, port: int, timeout: float, source_ip: str) -> tuple[bytes, str | None]:
            del case
            case_calls.append((host, port, timeout, source_ip))
            return b"", None

        def control(host: str, port: int, timeout: float, source_ip: str) -> tuple[bytes, str]:
            control_calls.append((host, port, timeout, source_ip))
            return b"control", runner.core.CONTROL_ERROR

        with mock.patch.object(runner, "probe_case_from_source", side_effect=case_probe), mock.patch.object(
            runner, "probe_login_control_from_source", side_effect=control
        ):
            result = runner.execute_plan(self.plan_path, self.plan, self.context, timeout_seconds=0.2)

        self.assertEqual(result, 0)
        self.assertEqual(case_calls, [("127.0.0.1", 7471, 0.2, "127.0.0.40")])
        self.assertEqual(control_calls, [("127.0.0.1", 7471, 0.2, "127.0.0.41")])
        report = json.loads((self.artifact_dir / "login-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "success")
        self.assertEqual(report["cases"][0]["case_source_ip"], "127.0.0.40")
        self.assertEqual(report["cases"][0]["control_source_ip"], "127.0.0.41")
        self.assertEqual(report["cases"][0]["case_probe"], "connection-terminated")
        self.assertEqual(report["cases"][0]["control_probe"], "pass")
        self.assertEqual(report["cases"][0]["control_error"], runner.core.CONTROL_ERROR)
        self.assertIn("tools/security/login_packet_runtime_runner.py", report["evidence"]["provider_sha256"])

    def test_execute_plan_records_decoded_current_login_error(self) -> None:
        plan = dict(self.plan)
        plan["cases"] = ["current-rsa-empty-account"]
        self.plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        with mock.patch.object(
            runner,
            "probe_case_from_source",
            return_value=(b"response", runner.core.CONTROL_ERROR),
        ), mock.patch.object(
            runner,
            "probe_login_control_from_source",
            return_value=(b"control", runner.core.CONTROL_ERROR),
        ):
            result = runner.execute_plan(self.plan_path, plan, self.context, timeout_seconds=0.2)
        self.assertEqual(result, 0)
        report = json.loads((self.artifact_dir / "login-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["cases"][0]["case_probe"], "bounded-response")
        self.assertEqual(report["cases"][0]["decoded_error"], runner.core.CONTROL_ERROR)
        self.assertEqual(report["cases"][0]["response_policy"], runner.core.RESPONSE_CURRENT_LOGIN_ERROR)

    def test_execute_plan_fails_closed_when_control_probe_fails(self) -> None:
        with mock.patch.object(runner, "probe_case_from_source", return_value=(b"", None)), mock.patch.object(
            runner,
            "probe_login_control_from_source",
            side_effect=runner.core.ProbeFailure("control-response-missing"),
        ):
            result = runner.execute_plan(self.plan_path, self.plan, self.context, timeout_seconds=0.2)
        self.assertEqual(result, 1)
        report = json.loads((self.artifact_dir / "login-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["failure"], "current-prelude-only:control-response-missing")
        self.assertEqual(report["cases"][0]["failure"], "control-response-missing")

    def test_execute_plan_stops_after_first_failed_case(self) -> None:
        plan = dict(self.plan)
        plan["cases"] = ["current-prelude-only", "current-truncated-rsa"]
        self.plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        sources: list[str] = []

        def case_probe(case, host: str, port: int, timeout: float, source_ip: str) -> tuple[bytes, str | None]:
            del case, host, port, timeout
            sources.append(source_ip)
            raise runner.core.ProbeFailure("probe-timeout")

        with mock.patch.object(runner, "probe_case_from_source", side_effect=case_probe):
            result = runner.execute_plan(self.plan_path, plan, self.context, timeout_seconds=0.2)
        self.assertEqual(result, 1)
        self.assertEqual(sources, ["127.0.0.40"])
        report = json.loads((self.artifact_dir / "login-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(len(report["cases"]), 1)
        self.assertEqual(report["cases"][0]["id"], "current-prelude-only")


if __name__ == "__main__":
    unittest.main()
