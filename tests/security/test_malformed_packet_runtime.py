#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import socket
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
DRIVER_PATH = ROOT / "tools" / "security" / "malformed_packet_runtime.py"

spec = importlib.util.spec_from_file_location("malformed_packet_runtime", DRIVER_PATH)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runtime
spec.loader.exec_module(runtime)


class FakeStatusServer:
    XML_RESPONSE = b'<?xml version="1.0"?><tsqp version="1.0"><serverinfo uptime="1"/></tsqp>'

    def __init__(self, *, hold_invalid: bool = False, control_response: bool = True) -> None:
        self.hold_invalid = hold_invalid
        self.control_response = control_response
        self._stop = threading.Event()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(("127.0.0.1", 0))
        self._socket.listen(32)
        self._socket.settimeout(0.1)
        self.port = int(self._socket.getsockname()[1])
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._stop.set()
        self._socket.close()
        self._thread.join(timeout=2)

    def _serve(self) -> None:
        while not self._stop.is_set():
            try:
                connection, _ = self._socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            try:
                self._handle(connection)
            finally:
                connection.close()

    def _handle(self, connection: socket.socket) -> None:
        connection.settimeout(0.2)
        data = bytearray()
        try:
            while len(data) < 2:
                chunk = connection.recv(4096)
                if not chunk:
                    return
                data.extend(chunk)
            declared = int.from_bytes(data[:2], "little")
            target_size = 2 + declared
            if 0 < declared <= 4096:
                while len(data) < target_size:
                    chunk = connection.recv(4096)
                    if not chunk:
                        break
                    data.extend(chunk)
        except (socket.timeout, OSError):
            pass

        if bytes(data) == runtime.CONTROL_STATUS_REQUEST:
            if self.control_response:
                connection.sendall(self.XML_RESPONSE)
            return
        if self.hold_invalid:
            time.sleep(0.4)


class MalformedPacketRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.binary = self.root / "canary"
        self.binary.write_bytes(b"exact-canary-binary")
        self.artifact_dir = self.root / "artifacts"
        self.artifact_dir.mkdir()
        self.stdout_path = self.artifact_dir / "canary.stdout.log"
        self.stderr_path = self.artifact_dir / "canary.stderr.log"
        self.stdout_path.write_text("server online!\n", encoding="utf-8")
        self.stderr_path.write_text("", encoding="utf-8")

    def write_plan(self, cases: list[str] | None = None, **overrides) -> Path:
        payload = {
            "schema": runtime.PLAN_SCHEMA,
            "id": "test-status-parser",
            "authorized_repository": runtime.AUTHORIZED_REPOSITORY,
            "driver": runtime.DRIVER_ID,
            "service": runtime.SERVICE_ID,
            "cases": cases or ["zero-length-frame"],
        }
        payload.update(overrides)
        path = self.root / "plan.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def context(self, port: int, *, host: str = "127.0.0.1") -> SimpleNamespace:
        return SimpleNamespace(
            host=host,
            status_port=port,
            binary_path=self.binary,
            artifact_dir=self.artifact_dir,
            stdout_path=self.stdout_path,
            stderr_path=self.stderr_path,
            server_pid=1234,
        )

    def read_report(self) -> dict:
        path = self.artifact_dir / "malformed-packet-report.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_fixed_case_registry_is_reviewable_and_stable(self) -> None:
        self.assertEqual(
            {case_id: case.payload.hex() for case_id, case in runtime.CASES.items()},
            {
                "zero-length-frame": "0000",
                "oversized-length-frame": "ffff",
                "truncated-declared-body": "0800ff",
                "unknown-service-identifier": "01007e",
                "status-service-only": "0100ff",
                "status-opcode-only": "0200ffff",
                "status-truncated-info": "0500ffff696e66",
                "status-unknown-opcode": "0200ff7f",
            },
        )
        self.assertTrue(runtime.CASES["truncated-declared-body"].half_close_write)

    def test_plan_accepts_only_exact_bounded_contract(self) -> None:
        path = self.write_plan(["zero-length-frame", "status-unknown-opcode"])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)
        self.assertEqual(plan["cases"], ["zero-length-frame", "status-unknown-opcode"])

        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["payload_hex"] = "0000"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(runtime.SecurityPlanError, "fields mismatch"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

    def test_plan_rejects_repository_mismatch_duplicates_and_unknown_cases(self) -> None:
        path = self.write_plan()
        with self.assertRaisesRegex(runtime.SecurityPlanError, "caller repository is not authorized"):
            runtime.load_plan(path, "opentibiabr/canary")

        path = self.write_plan(["zero-length-frame", "zero-length-frame"])
        with self.assertRaisesRegex(runtime.SecurityPlanError, "duplicate case ids"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

        path = self.write_plan(["invented-packet"])
        with self.assertRaisesRegex(runtime.SecurityPlanError, "unknown case ids"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

    def test_target_requires_exact_literal_ipv4_loopback(self) -> None:
        with self.assertRaisesRegex(runtime.ProbeFailure, "target-not-literal-ip"):
            runtime._require_loopback_target("localhost", 7173)
        with self.assertRaisesRegex(runtime.ProbeFailure, "target-not-authorized-loopback"):
            runtime._require_loopback_target("127.0.0.2", 7173)
        runtime._require_loopback_target("127.0.0.1", 7173)

    def test_all_built_in_cases_terminate_and_preserve_control_responsiveness(self) -> None:
        server = FakeStatusServer()
        self.addCleanup(server.close)
        path = self.write_plan(list(runtime.CASES))
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

        result = runtime.execute_plan(path, plan, self.context(server.port), timeout_seconds=0.5)
        self.assertEqual(result, 0)
        report = self.read_report()
        self.assertEqual(report["schema"], runtime.REPORT_SCHEMA)
        self.assertEqual(report["status"], "success")
        self.assertIsNone(report["failure"])
        self.assertEqual(len(report["cases"]), len(runtime.CASES))
        self.assertTrue(all(case["malformed_probe"] == "connection-terminated" for case in report["cases"]))
        self.assertTrue(all(case["control_probe"] == "pass" for case in report["cases"]))
        self.assertEqual(report["fatal_log_findings"], [])
        self.assertEqual(report["runtime"], {"host": "127.0.0.1", "status_port": server.port})
        self.assertEqual(report["authorization"]["repository"], runtime.AUTHORIZED_REPOSITORY)

    def test_malformed_timeout_fails_closed(self) -> None:
        server = FakeStatusServer(hold_invalid=True)
        self.addCleanup(server.close)
        path = self.write_plan(["zero-length-frame"])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

        result = runtime.execute_plan(path, plan, self.context(server.port), timeout_seconds=0.1)
        self.assertEqual(result, 1)
        report = self.read_report()
        self.assertEqual(report["status"], "failure")
        self.assertEqual(report["failure"], "zero-length-frame:malformed-timeout")
        self.assertEqual(report["cases"][0]["failure"], "malformed-timeout")

    def test_failed_control_probe_fails_closed(self) -> None:
        server = FakeStatusServer(control_response=False)
        self.addCleanup(server.close)
        path = self.write_plan(["unknown-service-identifier"])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

        result = runtime.execute_plan(path, plan, self.context(server.port), timeout_seconds=0.5)
        self.assertEqual(result, 1)
        report = self.read_report()
        self.assertEqual(report["failure"], "unknown-service-identifier:control-invalid-response")
        self.assertEqual(report["cases"][0]["malformed_probe"], "connection-terminated")
        self.assertEqual(report["cases"][0]["control_probe"], "pending")

    def test_fatal_or_sanitizer_log_signature_fails_closed(self) -> None:
        server = FakeStatusServer()
        self.addCleanup(server.close)
        self.stderr_path.write_text("ERROR: AddressSanitizer: heap-use-after-free\n", encoding="utf-8")
        path = self.write_plan(["status-unknown-opcode"])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

        result = runtime.execute_plan(path, plan, self.context(server.port), timeout_seconds=0.5)
        self.assertEqual(result, 1)
        report = self.read_report()
        self.assertEqual(report["failure"], "fatal-log-signature")
        signatures = {finding["signature"] for finding in report["fatal_log_findings"]}
        self.assertIn("addresssanitizer", signatures)
        self.assertIn("heap-use-after-free", signatures)

    def test_report_generation_is_deterministic_for_identical_inputs(self) -> None:
        path = self.write_plan(["zero-length-frame"])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)
        context = self.context(7473)
        case_results = [
            {
                "id": "zero-length-frame",
                "payload_sha256": runtime._sha256_bytes(runtime.CASES["zero-length-frame"].payload),
                "payload_size": 2,
                "malformed_probe": "connection-terminated",
                "control_probe": "pass",
            }
        ]
        kwargs = {
            "plan": plan,
            "plan_sha256": runtime._sha256_file(path),
            "context": context,
            "case_results": case_results,
            "fatal_findings": [],
            "status": "success",
            "failure": None,
        }
        first = runtime._canonical_json(runtime.build_report(**kwargs))
        second = runtime._canonical_json(runtime.build_report(**kwargs))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
