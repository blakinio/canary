#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
DRIVER_PATH = ROOT / "tools" / "security" / "game_session_runtime.py"

spec = importlib.util.spec_from_file_location("game_session_runtime", DRIVER_PATH)
assert spec is not None and spec.loader is not None
runtime = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runtime
spec.loader.exec_module(runtime)


def _challenge_packet(timestamp: int = 0x12345678, random_value: int = 0x5A) -> bytes:
    body = b"\x01\x1f" + struct.pack("<I", timestamp) + bytes([random_value, 0x71])
    return struct.pack("<H", 1) + struct.pack("<I", zlib.adler32(body) & 0xFFFFFFFF) + body


def _server_frame(payload: bytes, *, sequence: int = 7, compressed: bool = False) -> bytes:
    raw_sequence = sequence
    body = payload
    if compressed:
        compressor = zlib.compressobj(level=6, wbits=-15)
        body = compressor.compress(body) + compressor.flush()
        raw_sequence |= 0x80000000
    padding_size = 8 - (len(body) % 8) - 1
    plaintext = bytes([padding_size]) + body + (b"\x00" * padding_size)
    ciphertext = runtime._xtea_encrypt_blocks(plaintext)
    return struct.pack("<H", len(ciphertext) // 8) + struct.pack("<I", raw_sequence) + ciphertext


class GameSessionRuntimeTests(unittest.TestCase):
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
            "id": "test-game-session",
            "authorized_repository": runtime.AUTHORIZED_REPOSITORY,
            "driver": runtime.DRIVER_ID,
            "service": runtime.SERVICE_ID,
            "cases": cases or [runtime.CASE_AUTHENTICATED_CONTROL],
        }
        payload.update(overrides)
        path = self.root / "plan.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def context(self) -> SimpleNamespace:
        return SimpleNamespace(
            host="127.0.0.1",
            game_port=7472,
            binary_path=self.binary,
            artifact_dir=self.artifact_dir,
            stdout_path=self.stdout_path,
            stderr_path=self.stderr_path,
        )

    def test_fixed_case_registry_and_fixture_capacity_are_bounded(self) -> None:
        self.assertEqual(
            runtime.CASES,
            {
                "authenticated-control",
                "post-login-zero-sequence",
                "post-login-sequence-gap",
                "post-login-sequence-replay",
                "post-login-invalid-xtea-padding",
            },
        )
        self.assertEqual(len(runtime.FIXTURES), 12)
        self.assertEqual(runtime.FIXTURES[0][0], "fixture-01")
        self.assertEqual(runtime.FIXTURES[-1][0], "fixture-12")

    def test_plan_accepts_only_exact_code_owned_case_contract(self) -> None:
        path = self.write_plan([
            runtime.CASE_AUTHENTICATED_CONTROL,
            runtime.CASE_ZERO_SEQUENCE,
        ])
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)
        self.assertEqual(plan["cases"], [runtime.CASE_AUTHENTICATED_CONTROL, runtime.CASE_ZERO_SEQUENCE])

        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["password"] = "not-allowed"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(runtime.SecurityPlanError, "fields mismatch"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

    def test_plan_rejects_repository_mismatch_duplicates_unknown_and_fixture_overflow(self) -> None:
        path = self.write_plan()
        with self.assertRaisesRegex(runtime.SecurityPlanError, "caller repository is not authorized"):
            runtime.load_plan(path, "opentibiabr/canary")

        path = self.write_plan([runtime.CASE_ZERO_SEQUENCE, runtime.CASE_ZERO_SEQUENCE])
        with self.assertRaisesRegex(runtime.SecurityPlanError, "duplicate case ids"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

        path = self.write_plan(["arbitrary-packet"])
        with self.assertRaisesRegex(runtime.SecurityPlanError, "unknown case ids"):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

        payload = {
            "schema": runtime.PLAN_SCHEMA,
            "id": "fixture-overflow",
            "authorized_repository": runtime.AUTHORIZED_REPOSITORY,
            "driver": runtime.DRIVER_ID,
            "service": runtime.SERVICE_ID,
            "cases": list(runtime.CASES) + [f"extra-{index}" for index in range(7)],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(runtime.SecurityPlanError):
            runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)

    def test_target_requires_exact_literal_loopback(self) -> None:
        with self.assertRaisesRegex(runtime.ProbeFailure, "target-not-literal-ip"):
            runtime._require_loopback_target("localhost", 7472)
        with self.assertRaisesRegex(runtime.ProbeFailure, "target-not-authorized-loopback"):
            runtime._require_loopback_target("127.0.0.2", 7472)
        runtime._require_loopback_target("127.0.0.1", 7472)

    def test_challenge_parser_requires_exact_current_shape_and_checksum(self) -> None:
        packet = _challenge_packet()
        challenge = runtime.decode_game_challenge(packet)
        self.assertEqual(challenge.timestamp, 0x12345678)
        self.assertEqual(challenge.random, 0x5A)
        self.assertEqual(challenge.packet_sha256, hashlib.sha256(packet).hexdigest())

        corrupted = bytearray(packet)
        corrupted[2] ^= 0x01
        with self.assertRaisesRegex(runtime.ProbeFailure, "challenge-checksum-mismatch"):
            runtime.decode_game_challenge(bytes(corrupted))

    def test_game_login_packet_is_deterministic_for_fixed_challenge_and_uses_sequence_one(self) -> None:
        challenge = runtime.GameChallenge(0x12345678, 0x5A, "fixed")
        packet = runtime.build_game_login_packet("@test1", "test", "Knight 1", challenge)
        self.assertEqual(len(packet), 166)
        self.assertEqual(int.from_bytes(packet[:2], "little"), 20)
        self.assertEqual(int.from_bytes(packet[2:6], "little"), 1)
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "5d8b421a401e1580bb4ea2535529093de8956a4b72385ee50f68f5c0a18c1bd6",
        )

    def test_xtea_round_trip_and_client_frame_shape(self) -> None:
        plaintext = bytes(range(24))
        self.assertEqual(runtime._xtea_decrypt_blocks(runtime._xtea_encrypt_blocks(plaintext)), plaintext)
        packet = runtime.build_client_game_frame(bytes([runtime.PING_OPCODE]), 2)
        self.assertEqual(len(packet), 14)
        self.assertEqual(int.from_bytes(packet[:2], "little"), 1)
        self.assertEqual(int.from_bytes(packet[2:6], "little"), 2)
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "eb125300b1b26b73770d4275558513dfe2bcff4342e11c01d68745a48807f82b",
        )

    def test_invalid_padding_frame_is_fixed_and_keeps_requested_sequence(self) -> None:
        packet = runtime.build_invalid_padding_frame(3)
        self.assertEqual(int.from_bytes(packet[:2], "little"), 1)
        self.assertEqual(int.from_bytes(packet[2:6], "little"), 3)
        self.assertEqual(
            hashlib.sha256(packet).hexdigest(),
            "ba10a38db52abff1e901921d4c790a8de97b92726ade5a495107347f55d95d24",
        )
        plaintext = runtime._xtea_decrypt_blocks(packet[6:])
        self.assertEqual(plaintext[0], 0xFF)

    def test_server_game_frame_decoder_supports_plain_and_raw_deflate_payloads(self) -> None:
        plain = runtime.decode_server_game_frame(_server_frame(b"\x1d", sequence=7))
        self.assertEqual(plain.sequence, 7)
        self.assertFalse(plain.compressed)
        self.assertEqual(plain.payload, b"\x1d")

        payload = b"abc" * 100
        compressed = runtime.decode_server_game_frame(_server_frame(payload, sequence=9, compressed=True))
        self.assertEqual(compressed.sequence, 9)
        self.assertTrue(compressed.compressed)
        self.assertEqual(compressed.payload, payload)

    def test_authentication_error_opcode_is_rejected_as_session_evidence(self) -> None:
        frame = runtime.DecodedGameFrame(1, False, bytes([runtime.AUTH_ERROR_OPCODE]), "hash")
        with self.assertRaisesRegex(runtime.ProbeFailure, "game-authentication-rejected"):
            runtime.require_non_auth_error_frame(frame)

    def test_fatal_or_sanitizer_log_signature_is_detected(self) -> None:
        self.stderr_path.write_text("ERROR: AddressSanitizer: heap-use-after-free\n", encoding="utf-8")
        signatures = {finding["signature"] for finding in runtime.scan_fatal_logs(self.stdout_path, self.stderr_path)}
        self.assertIn("addresssanitizer", signatures)
        self.assertIn("heap-use-after-free", signatures)

    def test_report_generation_is_deterministic_for_identical_inputs(self) -> None:
        path = self.write_plan()
        plan = runtime.load_plan(path, runtime.AUTHORIZED_REPOSITORY)
        runner = ROOT / "tools" / "security" / "game_session_runtime_runner.py"
        first = runtime.build_report(
            plan=plan,
            plan_sha256=runtime._sha256_file(path),
            context=self.context(),
            runner_path=runner,
            case_results=[{"id": runtime.CASE_AUTHENTICATED_CONTROL, "case_probe": "pass"}],
            fatal_findings=[],
            status="success",
            failure=None,
        )
        second = runtime.build_report(
            plan=plan,
            plan_sha256=runtime._sha256_file(path),
            context=self.context(),
            runner_path=runner,
            case_results=[{"id": runtime.CASE_AUTHENTICATED_CONTROL, "case_probe": "pass"}],
            fatal_findings=[],
            status="success",
            failure=None,
        )
        self.assertEqual(runtime._canonical_json(first), runtime._canonical_json(second))


if __name__ == "__main__":
    unittest.main()
