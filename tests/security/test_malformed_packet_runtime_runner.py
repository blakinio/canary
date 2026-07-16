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

    def test_control_probe_recovers_after_transient_failures(self) -> None:
        failures = [
            runner.core.ProbeFailure("control-invalid-response"),
            runner.core.ProbeFailure("control-connect-failed"),
            None,
        ]

        def probe(host: str, port: int, timeout: float) -> None:
            self.assertEqual((host, port, timeout), ("127.0.0.1", 7473, 0.2))
            outcome = failures.pop(0)
            if outcome is not None:
                raise outcome

        with mock.patch.object(runner.core, "probe_status_control", side_effect=probe), mock.patch.object(
            runner.time, "sleep"
        ) as sleep:
            runner.probe_status_control_with_retries("127.0.0.1", 7473, 0.2)
        self.assertEqual(sleep.call_count, 2)

    def test_control_probe_exhaustion_fails_closed_with_normalized_code(self) -> None:
        with mock.patch.object(
            runner.core,
            "probe_status_control",
            side_effect=runner.core.ProbeFailure("control-invalid-response"),
        ), mock.patch.object(runner.time, "sleep"):
            with self.assertRaisesRegex(runner.core.ProbeFailure, "control-unresponsive") as raised:
                runner.probe_status_control_with_retries("127.0.0.1", 7473, 0.2)
        self.assertEqual(raised.exception.code, "control-unresponsive")

    def test_execute_plan_normalizes_transient_recovery_without_attempt_count(self) -> None:
        calls = 0

        def control(host: str, port: int, timeout: float) -> None:
            nonlocal calls
            del host, port, timeout
            calls += 1
            if calls == 1:
                raise runner.core.ProbeFailure("control-invalid-response")

        with mock.patch.object(runner.core, "probe_malformed_case", return_value=None), mock.patch.object(
            runner.core, "probe_status_control", side_effect=control
        ), mock.patch.object(runner.time, "sleep"):
            result = runner.execute_plan(self.plan_path, self.plan, self.context, timeout_seconds=0.2)

        self.assertEqual(result, 0)
        report = json.loads((self.artifact_dir / "malformed-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "success")
        self.assertEqual(report["cases"][0]["control_probe"], "pass")
        self.assertNotIn("attempts", report["cases"][0])
        self.assertIn("tools/security/malformed_packet_runtime_runner.py", report["evidence"]["provider_sha256"])

    def test_execute_plan_fails_closed_when_control_never_recovers(self) -> None:
        with mock.patch.object(runner.core, "probe_malformed_case", return_value=None), mock.patch.object(
            runner.core,
            "probe_status_control",
            side_effect=runner.core.ProbeFailure("control-invalid-response"),
        ), mock.patch.object(runner.time, "sleep"):
            result = runner.execute_plan(self.plan_path, self.plan, self.context, timeout_seconds=0.2)

        self.assertEqual(result, 1)
        report = json.loads((self.artifact_dir / "malformed-packet-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["failure"], "zero-length-frame:control-unresponsive")
        self.assertEqual(report["cases"][0]["failure"], "control-unresponsive")


if __name__ == "__main__":
    unittest.main()
