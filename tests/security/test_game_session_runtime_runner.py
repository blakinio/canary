#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "security" / "game_session_runtime_runner.py"

spec = importlib.util.spec_from_file_location("game_session_runtime_runner", RUNNER_PATH)
assert spec is not None and spec.loader is not None
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)


class FakeConnection:
    def __init__(self) -> None:
        self.sent: list[bytes] = []
        self.closed = False

    def sendall(self, packet: bytes) -> None:
        self.sent.append(packet)

    def close(self) -> None:
        self.closed = True


class GameSessionRuntimeRunnerTests(unittest.TestCase):
    def frame(self, sequence: int = 1) -> SimpleNamespace:
        return SimpleNamespace(
            packet_sha256=f"packet-{sequence}",
            sequence=sequence,
            compressed=False,
            payload=b"\x1d",
        )

    def test_source_ips_are_deterministic_distinct_loopback_pairs(self) -> None:
        self.assertEqual(runner.source_ips_for_case(0), ("127.0.0.80", "127.0.0.81"))
        self.assertEqual(runner.source_ips_for_case(4), ("127.0.0.88", "127.0.0.89"))
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-index-out-of-range"):
            runner.source_ips_for_case(runner.core.MAX_CASES)

    def test_zero_sequence_recovery_reuses_expected_sequence(self) -> None:
        connection = FakeConnection()
        response = self.frame(7)
        with mock.patch.object(runner, "_send_ping_and_require_response", return_value=(b"recovery", response)) as send_ping:
            result = runner._run_case_action(connection, runner.core.CASE_ZERO_SEQUENCE, 3)
        self.assertEqual(int.from_bytes(connection.sent[0][2:6], "little"), 0)
        send_ping.assert_called_once_with(connection, 3)
        self.assertEqual(result["recovery_sequence"], 3)

    def test_sequence_gap_recovery_reuses_expected_sequence(self) -> None:
        connection = FakeConnection()
        response = self.frame(8)
        with mock.patch.object(runner, "_send_ping_and_require_response", return_value=(b"recovery", response)) as send_ping:
            result = runner._run_case_action(connection, runner.core.CASE_SEQUENCE_GAP, 3)
        self.assertEqual(int.from_bytes(connection.sent[0][2:6], "little"), 4)
        send_ping.assert_called_once_with(connection, 3)
        self.assertEqual(result["recovery_sequence"], 3)

    def test_replay_requires_next_sequence_after_one_accepted_packet(self) -> None:
        connection = FakeConnection()
        first_response = self.frame(10)
        recovery_response = self.frame(11)
        accepted_packet = runner.core.build_client_game_frame(bytes([runner.core.PING_OPCODE]), 3)
        calls = [
            (accepted_packet, first_response),
            (b"recovery", recovery_response),
        ]
        with mock.patch.object(runner, "_send_ping_and_require_response", side_effect=calls) as send_ping:
            result = runner._run_case_action(connection, runner.core.CASE_SEQUENCE_REPLAY, 3)
        self.assertEqual(connection.sent, [accepted_packet])
        self.assertEqual(send_ping.call_args_list, [mock.call(connection, 3), mock.call(connection, 4)])
        self.assertEqual(result["recovery_sequence"], 4)

    def test_invalid_padding_recovery_reuses_sequence_that_failed_decrypt(self) -> None:
        connection = FakeConnection()
        response = self.frame(12)
        with mock.patch.object(runner, "_send_ping_and_require_response", return_value=(b"recovery", response)) as send_ping:
            result = runner._run_case_action(connection, runner.core.CASE_INVALID_XTEA_PADDING, 3)
        plaintext = runner.core._xtea_decrypt_blocks(connection.sent[0][6:])
        self.assertEqual(plaintext[0], 0xFF)
        send_ping.assert_called_once_with(connection, 3)
        self.assertEqual(result["recovery_sequence"], 3)

    def test_authenticated_control_uses_expected_sequence_without_malformed_probe(self) -> None:
        connection = FakeConnection()
        response = self.frame(13)
        packet = runner.core.build_client_game_frame(bytes([runner.core.PING_OPCODE]), 3)
        with mock.patch.object(runner, "_send_ping_and_require_response", return_value=(packet, response)) as send_ping:
            result = runner._run_case_action(connection, runner.core.CASE_AUTHENTICATED_CONTROL, 3)
        self.assertEqual(connection.sent, [])
        send_ping.assert_called_once_with(connection, 3)
        self.assertEqual(result["action"], "valid-ping")

    def test_loopback_source_rejects_hostname_and_non_loopback(self) -> None:
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-literal-ip"):
            runner._require_loopback_source("localhost")
        with self.assertRaisesRegex(runner.core.ProbeFailure, "source-not-loopback"):
            runner._require_loopback_source("192.0.2.1")
        runner._require_loopback_source("127.0.0.80")


if __name__ == "__main__":
    unittest.main()
