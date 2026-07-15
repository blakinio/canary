#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER_PATH = Path(__file__).resolve().parents[2] / "tools" / "e2e" / "run_agent_load.py"
spec = importlib.util.spec_from_file_location("run_agent_load", RUNNER_PATH)
assert spec is not None and spec.loader is not None
load = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = load
spec.loader.exec_module(load)


def profile_payload(port: int, *, mode: str = "load", gate: bool = True) -> dict:
    stages = [
        {
            "name": "baseline",
            "requests": 20,
            "concurrency": 5,
            "request_timeout_seconds": 2,
            "thresholds": {
                "max_error_rate": 0.0,
                "max_p95_ms": 2000,
                "min_successes": 20,
            },
        }
    ]
    if mode == "stress":
        stages.append(
            {
                "name": "higher",
                "requests": 30,
                "concurrency": 10,
                "request_timeout_seconds": 2,
                "thresholds": {
                    "max_error_rate": 0.0,
                    "max_p95_ms": 2000,
                    "min_successes": 30,
                },
            }
        )
    return {
        "schema_version": 1,
        "id": "test-profile",
        "mode": mode,
        "protocol": "status-xml",
        "target": {"host": "127.0.0.1", "port": port},
        "policy": {"gate": gate, "sample_interval_ms": 25},
        "stages": stages,
    }


class ProfileValidationTests(unittest.TestCase):
    def write_profile(self, payload: dict) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "profile.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_status_request_contains_service_identifier_and_xml_command(self) -> None:
        self.assertEqual(load.STATUS_REQUEST, b"\x06\x00\xff\xffinfo")
        self.assertEqual(load.STATUS_REQUEST_BODY[:1], b"\xff")
        self.assertEqual(load.STATUS_REQUEST_BODY[1:], b"\xffinfo")

    def test_unique_loopback_sources_are_deterministic_and_distinct(self) -> None:
        self.assertEqual(load._unique_loopback_source(0), "127.0.0.1")
        self.assertEqual(load._unique_loopback_source(1), "127.0.0.2")
        self.assertEqual(load._unique_loopback_source(255), "127.0.1.0")
        self.assertEqual(len({load._unique_loopback_source(index) for index in range(1000)}), 1000)

    def test_rejects_non_loopback_target(self) -> None:
        payload = profile_payload(7173)
        payload["target"]["host"] = "example.com"
        with self.assertRaises(load.LoadConfigError):
            load.load_profile(self.write_profile(payload))

    def test_unique_loopback_strategy_requires_ipv4_loopback_target(self) -> None:
        payload = profile_payload(7173)
        payload["target"]["host"] = "::1"
        payload["policy"]["source_ip_strategy"] = "unique-loopback-v4"
        with self.assertRaises(load.LoadConfigError):
            load.load_profile(self.write_profile(payload))

    def test_stress_requires_multiple_stages(self) -> None:
        payload = profile_payload(7173)
        payload["mode"] = "stress"
        with self.assertRaises(load.LoadConfigError):
            load.load_profile(self.write_profile(payload))

    def test_bundled_profiles_are_valid_and_loopback_only(self) -> None:
        profile_dir = Path(__file__).resolve().parent / "load"
        profiles = [load.load_profile(path) for path in sorted(profile_dir.glob("*.json"))]
        self.assertEqual(
            [profile.profile_id for profile in profiles],
            ["status-load", "status-smoke", "status-stress"],
        )
        self.assertTrue(all(profile.host in load.LOOPBACK_HOSTS for profile in profiles))
        self.assertTrue(all(profile.source_ip_strategy == "unique-loopback-v4" for profile in profiles))
        self.assertTrue(next(profile for profile in profiles if profile.profile_id == "status-smoke").gate)
        self.assertFalse(next(profile for profile in profiles if profile.profile_id == "status-stress").gate)


class RunnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.response = (
            b'<?xml version="1.0"?><tsqp version="1.0">'
            b'<serverinfo uptime="1" servername="Test"/></tsqp>'
        )

        async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            try:
                header = await reader.readexactly(2)
                body_size = int.from_bytes(header, "little")
                body = await reader.readexactly(body_size)
                service_identifier = body[:1]
                protocol_payload = body[1:]
                if service_identifier == b"\xff" and protocol_payload == b"\xffinfo":
                    writer.write(self.response)
                    await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()

        self.server = await asyncio.start_server(handler, "127.0.0.1", 0)
        socket = self.server.sockets[0]
        self.port = int(socket.getsockname()[1])

    async def asyncTearDown(self) -> None:
        self.server.close()
        await self.server.wait_closed()

    def write_profile(self, payload: dict) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "profile.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    async def test_load_profile_succeeds_against_valid_status_server(self) -> None:
        profile = load.load_profile(self.write_profile(profile_payload(self.port)))
        result = await load.run_profile(profile)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["aggregate"]["attempts"], 20)
        self.assertEqual(result["aggregate"]["successes"], 20)
        self.assertEqual(result["aggregate"]["failures"], 0)
        self.assertGreater(result["aggregate"]["bytes_received"], 0)

    async def test_stress_profile_runs_all_stages(self) -> None:
        profile = load.load_profile(
            self.write_profile(profile_payload(self.port, mode="stress", gate=False))
        )
        result = await load.run_profile(profile)
        self.assertEqual([stage["name"] for stage in result["stages"]], ["baseline", "higher"])
        self.assertEqual(result["aggregate"]["attempts"], 50)
        self.assertTrue(result["gate_passed"])


if __name__ == "__main__":
    unittest.main()
