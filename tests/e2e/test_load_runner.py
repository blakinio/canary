#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_load.py"
RUNTIME_PATH = ROOT / "tools" / "e2e" / "run_agent_load_runtime.py"

spec = importlib.util.spec_from_file_location("run_agent_load", RUNNER_PATH)
assert spec is not None and spec.loader is not None
load = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = load
spec.loader.exec_module(load)

runtime_spec = importlib.util.spec_from_file_location("run_agent_load_runtime", RUNTIME_PATH)
assert runtime_spec is not None and runtime_spec.loader is not None
runtime = importlib.util.module_from_spec(runtime_spec)
sys.modules[runtime_spec.name] = runtime
runtime_spec.loader.exec_module(runtime)


def profile_payload(port: int, *, mode: str = "load", gate: bool = True) -> dict:
    stages = [
        {
            "name": "baseline",
            "requests": 20,
            "concurrency": 5,
            "request_timeout_seconds": 2,
            "thresholds": {"max_error_rate": 0.0, "max_p95_ms": 2000, "min_successes": 20},
        }
    ]
    if mode == "stress":
        stages.append(
            {
                "name": "higher",
                "requests": 30,
                "concurrency": 10,
                "request_timeout_seconds": 2,
                "thresholds": {"max_error_rate": 0.0, "max_p95_ms": 2000, "min_successes": 30},
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

    def test_status_request_models_service_identifier_then_protocol_payload(self) -> None:
        self.assertEqual(load.STATUS_REQUEST, b"\x06\x00\xff\xffinfo")
        self.assertEqual(load.STATUS_REQUEST_BODY[:1], b"\xff")
        self.assertEqual(load.STATUS_REQUEST_BODY[1:], b"\xffinfo")

    def test_unique_loopback_sources_are_deterministic_and_distinct(self) -> None:
        self.assertEqual(load._source_ip(0), "127.0.0.1")
        self.assertEqual(load._source_ip(1), "127.0.0.2")
        self.assertEqual(load._source_ip(255), "127.0.1.0")
        self.assertEqual(len({load._source_ip(index) for index in range(1000)}), 1000)

    def test_rejects_non_loopback_target(self) -> None:
        payload = profile_payload(7173)
        payload["target"]["host"] = "example.com"
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
        self.assertEqual([profile.profile_id for profile in profiles], ["status-load", "status-smoke", "status-stress"])
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
        self.port = int(self.server.sockets[0].getsockname()[1])

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

    async def test_stress_profile_runs_all_stages(self) -> None:
        profile = load.load_profile(self.write_profile(profile_payload(self.port, mode="stress", gate=False)))
        result = await load.run_profile(profile)
        self.assertEqual([stage["name"] for stage in result["stages"]], ["baseline", "higher"])
        self.assertEqual(result["aggregate"]["attempts"], 50)
        self.assertTrue(result["gate_passed"])


class FakeProcess:
    def __init__(self, pid: int = 4242) -> None:
        self.pid = pid
        self.returncode: int | None = None

    def poll(self) -> int | None:
        return self.returncode


class FakeSmoke:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.stopped = False
        self.restored = False

    def repo_path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else self.root / path

    def prepare_map(self, args: SimpleNamespace) -> None:
        del args

    def initialize_database(self, args: SimpleNamespace) -> None:
        del args

    def write_smoke_config(self, args: SimpleNamespace) -> None:
        del args
        (self.root / "config.lua").write_text("temporary\n", encoding="utf-8")

    def read_logs(self, paths: list[Path]) -> str:
        del paths
        return "Server Online!"

    def stop_process(self, process: FakeProcess) -> None:
        del process
        self.stopped = True

    def restore_config(self, path: Path, existed: bool, previous: bytes | None) -> None:
        self.restored = True
        if existed and previous is not None:
            path.write_bytes(previous)
        else:
            path.unlink(missing_ok=True)


class RuntimeCallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        (self.root / "canary").write_bytes(b"fake")
        (self.root / "config.lua").write_text("original\n", encoding="utf-8")
        self.args = SimpleNamespace(
            binary_path="canary",
            artifact_dir="artifacts/runtime",
            data_pack="data-canary",
            map_name="canary",
            map_download_url="",
            map_cache_path="",
            db_host="127.0.0.1",
            db_port=3306,
            db_user="root",
            db_password="root",
            db_name="test",
            skip_database_init=False,
            login_port=7471,
            game_port=7472,
            status_port=7473,
            startup_timeout_seconds=1,
        )
        self.smoke = FakeSmoke(self.root)
        self.process = FakeProcess()
        self.process_factory = lambda *args, **kwargs: self.process

    def run_runtime(self, executor):
        with mock.patch.object(runtime, "REPO_ROOT", self.root):
            return runtime.run_runtime(
                self.args,
                executor,
                operation_name="security-probe",
                exit_code_field="driver_exit_code",
                smoke_module=self.smoke,
                process_factory=self.process_factory,
            )

    def summary(self) -> dict:
        path = self.root / "artifacts" / "runtime" / "runtime-summary.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_callback_receives_bounded_context_and_cleanup_restores_config(self) -> None:
        captured = []

        def executor(context) -> int:
            captured.append(context)
            return 0

        self.assertEqual(self.run_runtime(executor), 0)
        self.assertEqual(len(captured), 1)
        context = captured[0]
        self.assertEqual(context.repo_root, self.root)
        self.assertEqual(context.binary_path, self.root / "canary")
        self.assertEqual(context.server_pid, 4242)
        self.assertEqual(context.host, "127.0.0.1")
        self.assertEqual((context.login_port, context.game_port, context.status_port), (7471, 7472, 7473))
        self.assertTrue(self.smoke.stopped)
        self.assertTrue(self.smoke.restored)
        self.assertEqual((self.root / "config.lua").read_text(encoding="utf-8"), "original\n")
        self.assertEqual(
            self.summary(),
            {
                "canary_exit_code": None,
                "driver_exit_code": 0,
                "phase": "complete",
                "schema_version": 1,
                "status": "success",
            },
        )

    def test_callback_failure_is_fail_closed_and_cleanup_still_runs(self) -> None:
        self.assertEqual(self.run_runtime(lambda context: 7), 1)
        summary = self.summary()
        self.assertEqual(summary["status"], "failure")
        self.assertEqual(summary["phase"], "security-probe")
        self.assertEqual(summary["driver_exit_code"], 7)
        self.assertIn("executor failed with exit code 7", summary["error"])
        self.assertTrue(self.smoke.stopped)
        self.assertTrue(self.smoke.restored)

    def test_server_exit_after_callback_is_detected(self) -> None:
        def executor(context) -> int:
            del context
            self.process.returncode = 9
            return 0

        self.assertEqual(self.run_runtime(executor), 1)
        summary = self.summary()
        self.assertEqual(summary["status"], "failure")
        self.assertEqual(summary["canary_exit_code"], 9)
        self.assertIn("Canary exited during security-probe with code 9", summary["error"])

    def test_load_executor_preserves_existing_command_contract(self) -> None:
        artifact_dir = self.root / "artifacts" / "runtime"
        artifact_dir.mkdir(parents=True)
        profile = self.root / "profile.json"
        profile.write_text("{}", encoding="utf-8")
        context = runtime.RuntimeContext(
            repo_root=self.root,
            binary_path=self.root / "canary",
            artifact_dir=artifact_dir,
            server_pid=4242,
            host="127.0.0.1",
            login_port=7471,
            game_port=7472,
            status_port=7473,
            stdout_path=artifact_dir / "canary.stdout.log",
            stderr_path=artifact_dir / "canary.stderr.log",
        )
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok\n", stderr="")
        with mock.patch.object(runtime.subprocess, "run", return_value=completed) as run:
            self.assertEqual(runtime._load_executor(profile)(context), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[command.index("--profile") + 1], str(profile))
        self.assertEqual(command[command.index("--host") + 1], "127.0.0.1")
        self.assertEqual(command[command.index("--port") + 1], "7473")
        self.assertEqual(command[command.index("--server-pid") + 1], "4242")
        self.assertEqual((artifact_dir / "load.stdout.log").read_text(encoding="utf-8"), "ok\n")


if __name__ == "__main__":
    unittest.main()
