#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import socket
import struct
import sys
import tempfile
import threading
import time
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
DRIVER_PATH = ROOT / "tools" / "security" / "login_packet_runtime.py"

spec = importlib.util.spec_from_file_location("login_packet_runtime", DRIVER_PATH)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runtime
spec.loader.exec_module(runtime)


def _xtea_encrypt_blocks(plaintext: bytes) -> bytes:
    if not plaintext or len(plaintext) % 8 != 0:
        raise ValueError("plaintext must contain complete XTEA blocks")
    output = bytearray()
    delta = 0x61C88647
    mask = 0xFFFFFFFF
    for offset in range(0, len(plaintext), 8):
        v0, v1 = struct.unpack("<II", plaintext[offset : offset + 8])
        total = 0
        for _ in range(32):
            mix0 = ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ ((total + runtime.XTEA_KEY[total & 3]) & mask)) & mask
            v0 = (v0 + mix0) & mask
            total = (total - delta) & mask
            mix1 = ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ ((total + runtime.XTEA_KEY[(total >> 11) & 3]) & mask)) & mask
            v1 = (v1 + mix1) & mask
        output.extend(struct.pack("<II", v0, v1))
    return bytes(output)


def _current_login_error_response(message: str) -> bytes:
    encoded = message.encode("utf-8")
    payload = b"\x0b" + struct.pack("<H", len(encoded)) + encoded
    padding_size = 8 - (len(payload) % 8) - 1
    plaintext = bytes([padding_size]) + payload + (b"\x00" * padding_size)
    ciphertext = _xtea_encrypt_blocks(plaintext)
    checksum = zlib.adler32(ciphertext) & 0xFFFFFFFF
    return struct.pack("<H", len(ciphertext) // 8) + struct.pack("<I", checksum) + ciphertext


class FakeLoginServer:
    def __init__(self, *, suppress_responses: bool = False, hold: bool = False) -> None:
        self.suppress_responses = suppress_responses
        self.hold = hold
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
            while len(data) < target_size:
                chunk = connection.recv(4096)
                if not chunk:
                    break
                data.extend(chunk)
        except (socket.timeout, OSError):
            pass
        if self.hold:
            time.sleep(0.4)
            return
        if self.suppress_responses:
            return
        packet = bytes(data)
        if packet == runtime.CASES["unsupported-version"].payload:
            connection.sendall(b"plain-unsupported-version")
        elif packet == runtime.CASES["current-rsa-empty-account"].payload:
            connection.sendall(_current_login_error_response(runtime.CONTROL_ERROR))
        elif packet == runtime.CASES["current-rsa-empty-password"].payload:
            connection.sendall(_current_login_error_response("Invalid password."))


class LoginPacketRuntimeTests(unittest.TestCase):
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
            "id": "test-login-parser",
            "authorized_repository": runtime.AUTHORIZED_REPOSITORY,
            "driver": runtime.DRIVER_ID,
            "service": runtime.SERVICE_ID,
            "cases": cases or ["current-prelude-only"],
        }
        payload.update(overrides)
        path = self.root / "plan.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def context(self, port: int, *, host: str = "127.0.0.1") -> SimpleNamespace:
        return SimpleNamespace(
            host=host,
            login_port=port,
            binary_path=self.binary,
            artifact_dir=self.artifact_dir,
            stdout_path=self.stdout_path,
            stderr_path=self.stderr_path,
            server_pid=1234,
        )

    def test_fixed_case_registry_is_reviewable_and_stable(self) -> None:
        self.assertEqual(
            {
                case_id: (hashlib.sha256(case.payload).hexdigest(), case.response_policy, case.expected_error)
                for case_id, case in runtime.CASES.items()
            },
            {
                "unsupported-version": ("09084d11daa00d35e1c7111ae2ded127213bfa5c60f7920f19ee6e83adf3c7ac", runtime.RESPONSE_ANY, None),
                "current-prelude-only": ("ff1d93f43e3aa725705bfa534b425c3cc3868c710f1d9772fb3254bfa28aa3b1", runtime.RESPONSE_NONE, None),
                "current-truncated-rsa": ("0fddeb6a4e330044e90802cf7ac9510ea67a21828052e17f45dee94ebaf592e1", runtime.RESPONSE_NONE, None),
                "current-invalid-rsa-marker": ("889763125f5f56ba8580812864858c7adf0fffa94d7e09d97285af042738d75b", runtime.RESPONSE_NONE, None),
                "current-rsa-empty-account": ("1aac5c6a914b2cda0cc864d2d6b783ba94a23f5d7556d3259c3dcc1814a1fe95", runtime.RESPONSE_CURRENT_LOGIN_ERROR, runtime.CONTROL_ERROR),
                "current-rsa-empty-password": ("2a3cb33b0e5658e2fb086051289f0303abef0f3b2fa79dfcdb0fe693016b7761", runtime.RESPONSE_CURRENT_LOGIN_ERROR, "Invalid password."),
            },
        )
        self.assertEqual(hashlib.sha256(runtime.CONTROL_PACKET).hexdigest(), "1aac5c6a914b2cda0cc864d2d6b783ba94a23f5d7556d3259c3dcc1814a1fe95")

    def test_framed_packets_have_valid_checksum_and_login_protocol_identifier(self) -> None:
        for case in runtime.CASES.values():
            declared = struct.unpack("<H", case.payload[:2])[0]
            self.assertEqual(declared, len(case.payload) - 2)
            received_checksum = struct.unpack("<I", case.payload[2:6])[0]
            self.assertEqual(received_checksum, zlib.adler32(case.payload[6:]) & 0xFFFFFFFF)
            self.assertEqual(case.payload[6], runtime.PROTOCOL_IDENTIFIER)

    def test_raw_rsa_public_fixture_is_deterministic(self) -> None:
        cipher = runtime._raw_rsa_encrypt(runtime._rsa_plaintext(marker=1))
        self.assertEqual(len(cipher), runtime.RSA_BLOCK_SIZE)
        self.assertEqual(hashlib.sha256(cipher).hexdigest(), "9974df41f444739b937a9a6e214253ff7c4bb0e960d3324ba4b82f297afe18a3")
        with self.assertRaisesRegex(ValueError, "exactly 128 bytes"):
            runtime._raw_rsa_encrypt(b"short")

    def test_current_login_response_decoder_requires_xtea_checksum_and_error_payload(self) -> None:
        response = _current_login_error_response(runtime.CONTROL_ERROR)
        self.assertEqual(runtime.decode_current_login_error(response), runtime.CONTROL_ERROR)
        corrupted = bytearray(response)
        corrupted[2] ^= 0x01
        with self.assertRaisesRegex(runtime.ProbeFailure, "checksum-mismatch"):
            runtime.decode_current_login_error(bytes(corrupted))
        with self.assertRaisesRegex(runtime.ProbeFailure, "too-short"):
            runtime.decode_current_login_error(b"plain")

    def test_plan_accepts_only_exact_bounded_contract(self) -> None:
        path = self.write_plan(["current-prelude-only", "current-rsa-empty-account"])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)
        self.assertEqual(plan["cases"], ["current-prelude-only", "current-rsa-empty-account"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["packet_hex"] = "00"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(runtime.SecurityPlanError, "fields mismatch"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

    def test_plan_rejects_repository_mismatch_duplicates_and_unknown_cases(self) -> None:
        path = self.write_plan()
        with self.assertRaisesRegex(runtime.SecurityPlanError, "caller repository is not authorized"):
            runtime.load_plan(path, "opentibiabr/canary")
        path = self.write_plan(["current-prelude-only", "current-prelude-only"])
        with self.assertRaisesRegex(runtime.SecurityPlanError, "duplicate case ids"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)
        path = self.write_plan(["invented-packet"])
        with self.assertRaisesRegex(runtime.SecurityPlanError, "unknown case ids"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

    def test_target_requires_exact_literal_ipv4_loopback(self) -> None:
        with self.assertRaisesRegex(runtime.ProbeFailure, "target-not-literal-ip"):
            runtime._require_loopback_target("localhost", 7171)
        with self.assertRaisesRegex(runtime.ProbeFailure, "target-not-authorized-loopback"):
            runtime._require_loopback_target("127.0.0.2", 7171)
        runtime._require_loopback_target("127.0.0.1", 7171)

    def test_all_built_in_cases_match_response_policy_and_control_proves_rsa_xtea_handoff(self) -> None:
        server = FakeLoginServer()
        self.addCleanup(server.close)
        for case in runtime.CASES.values():
            response, decoded_error = runtime.probe_case(case, "127.0.0.1", server.port, 0.5)
            if case.response_policy == runtime.RESPONSE_NONE:
                self.assertEqual(response, b"")
            else:
                self.assertTrue(response)
            if case.response_policy == runtime.RESPONSE_CURRENT_LOGIN_ERROR:
                self.assertEqual(decoded_error, case.expected_error)
            control_response, control_error = runtime.probe_login_control("127.0.0.1", server.port, 0.5)
            self.assertTrue(control_response)
            self.assertEqual(control_error, runtime.CONTROL_ERROR)

    def test_plain_response_cannot_satisfy_current_login_control(self) -> None:
        with self.assertRaises(runtime.ProbeFailure):
            runtime.decode_current_login_error(b"plain-unsupported-version")

    def test_missing_control_response_fails_closed(self) -> None:
        server = FakeLoginServer(suppress_responses=True)
        self.addCleanup(server.close)
        with self.assertRaisesRegex(runtime.ProbeFailure, "control-response-missing"):
            runtime.probe_login_control("127.0.0.1", server.port, 0.5)

    def test_probe_timeout_fails_closed(self) -> None:
        server = FakeLoginServer(hold=True)
        self.addCleanup(server.close)
        with self.assertRaisesRegex(runtime.ProbeFailure, "probe-timeout"):
            runtime.probe_case(runtime.CASES["current-prelude-only"], "127.0.0.1", server.port, 0.1)

    def test_fatal_or_sanitizer_log_signature_is_detected(self) -> None:
        self.stderr_path.write_text("ERROR: AddressSanitizer: heap-use-after-free\n", encoding="utf-8")
        signatures = {finding["signature"] for finding in runtime.scan_fatal_logs(self.stdout_path, self.stderr_path)}
        self.assertIn("addresssanitizer", signatures)
        self.assertIn("heap-use-after-free", signatures)

    def test_report_generation_is_deterministic_for_identical_inputs(self) -> None:
        path = self.write_plan(["current-prelude-only"])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)
        context = self.context(7471)
        case_results = [{
            "id": "current-prelude-only",
            "payload_sha256": runtime._sha256_bytes(runtime.CASES["current-prelude-only"].payload),
            "payload_size": len(runtime.CASES["current-prelude-only"].payload),
            "response_policy": runtime.RESPONSE_NONE,
            "case_probe": "connection-terminated",
            "control_probe": "pass",
        }]
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
