#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_HELPER = REPO_ROOT / ".github" / "scripts" / "smoke_test_canary.py"
LOAD_RUNNER = REPO_ROOT / "tools" / "e2e" / "run_agent_load.py"


@dataclass(frozen=True)
class RuntimeContext:
    repo_root: Path
    binary_path: Path
    artifact_dir: Path
    server_pid: int
    host: str
    login_port: int
    game_port: int
    status_port: int
    stdout_path: Path
    stderr_path: Path


RuntimeExecutor = Callable[[RuntimeContext], int]
RuntimePreflight = Callable[[], None]


def _load_smoke_helper():
    spec = importlib.util.spec_from_file_location("canary_smoke_helper", SMOKE_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load smoke helper: {SMOKE_HELPER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_summary(path: Path, **values: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(values, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_executor(profile: Path) -> RuntimeExecutor:
    def execute(context: RuntimeContext) -> int:
        result_path = context.artifact_dir / "load-result.json"
        command = [
            sys.executable,
            str(LOAD_RUNNER),
            "--profile",
            str(profile),
            "--output",
            str(result_path),
            "--host",
            context.host,
            "--port",
            str(context.status_port),
            "--server-pid",
            str(context.server_pid),
        ]
        completed = subprocess.run(command, cwd=context.repo_root, text=True, capture_output=True)
        (context.artifact_dir / "load.stdout.log").write_text(completed.stdout, encoding="utf-8")
        (context.artifact_dir / "load.stderr.log").write_text(completed.stderr, encoding="utf-8")
        return completed.returncode

    return execute


def run_runtime(
    args: argparse.Namespace,
    executor: RuntimeExecutor,
    *,
    operation_name: str,
    exit_code_field: str,
    preflight: RuntimePreflight | None = None,
    smoke_module: Any | None = None,
    process_factory: Callable[..., Any] = subprocess.Popen,
) -> int:
    """Run one code-owned executor inside the existing disposable Canary lifecycle.

    The callback receives resolved loopback runtime metadata only after Canary reports
    online. No command, executable path, host or callback is loaded from a manifest.
    """

    if not operation_name or not operation_name.replace("-", "").replace("_", "").isalnum():
        raise ValueError("operation_name must be a non-empty identifier")
    if not exit_code_field or not exit_code_field.replace("_", "").isalnum():
        raise ValueError("exit_code_field must be a non-empty identifier")

    smoke = smoke_module or _load_smoke_helper()
    binary = smoke.repo_path(args.binary_path)
    artifact_dir = smoke.repo_path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary_path = artifact_dir / "runtime-summary.json"
    stdout_path = artifact_dir / "canary.stdout.log"
    stderr_path = artifact_dir / "canary.stderr.log"
    config_path = REPO_ROOT / "config.lua"
    config_existed = config_path.exists()
    previous_config = config_path.read_bytes() if config_existed else None
    process: Any | None = None
    phase = "bootstrap"
    executor_exit_code: int | None = None

    try:
        if not binary.exists():
            raise RuntimeError(f"Canary binary not found: {binary}")
        if sys.platform != "win32":
            binary.chmod(binary.stat().st_mode | 0o111)
        if preflight is not None:
            preflight()

        phase = "database-initialization"
        smoke.prepare_map(args)
        smoke.initialize_database(args)
        phase = "server-configuration"
        smoke.write_smoke_config(args)

        phase = "server-startup"
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            process = process_factory([str(binary)], cwd=REPO_ROOT, stdout=stdout_file, stderr=stderr_file)

        deadline = time.time() + args.startup_timeout_seconds
        while time.time() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Canary exited before becoming online with code {process.returncode}")
            if "server online!" in smoke.read_logs([stdout_path, stderr_path]).lower():
                break
            time.sleep(1)
        else:
            raise RuntimeError("Canary did not become online before timeout")

        phase = operation_name
        context = RuntimeContext(
            repo_root=REPO_ROOT,
            binary_path=binary,
            artifact_dir=artifact_dir,
            server_pid=int(process.pid),
            host="127.0.0.1",
            login_port=int(args.login_port),
            game_port=int(args.game_port),
            status_port=int(args.status_port),
            stdout_path=stdout_path,
            stderr_path=stderr_path,
        )
        executor_exit_code = executor(context)
        if isinstance(executor_exit_code, bool) or not isinstance(executor_exit_code, int):
            raise RuntimeError(f"{operation_name} executor must return an integer exit code")
        if executor_exit_code != 0:
            raise RuntimeError(f"{operation_name} executor failed with exit code {executor_exit_code}")
        if process.poll() is not None:
            raise RuntimeError(f"Canary exited during {operation_name} with code {process.returncode}")

        phase = "complete"
        _write_summary(
            summary_path,
            schema_version=1,
            status="success",
            phase=phase,
            **{exit_code_field: executor_exit_code},
            canary_exit_code=None,
        )
        return 0
    except Exception as exc:
        _write_summary(
            summary_path,
            schema_version=1,
            status="failure",
            phase=phase,
            error=f"{type(exc).__name__}: {exc}",
            **{exit_code_field: executor_exit_code},
            canary_exit_code=process.poll() if process else None,
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if process is not None:
            smoke.stop_process(process)
        smoke.restore_config(config_path, config_existed, previous_config)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start exact-head Canary and run one local load profile.")
    parser.add_argument("--binary-path", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--artifact-dir", default="artifacts/agent-load")
    parser.add_argument("--data-pack", default="data-canary", choices=["data-canary", "data-otservbr-global"])
    parser.add_argument("--map-name", default="canary")
    parser.add_argument("--map-download-url", default="")
    parser.add_argument("--map-cache-path", default="")
    parser.add_argument("--db-host", default="127.0.0.1")
    parser.add_argument("--db-port", type=int, default=3306)
    parser.add_argument("--db-user", default="root")
    parser.add_argument("--db-password", default="root")
    parser.add_argument("--db-name", default="canary_agent_load")
    parser.add_argument("--skip-database-init", action="store_true")
    parser.add_argument("--login-port", type=int, default=7471)
    parser.add_argument("--game-port", type=int, default=7472)
    parser.add_argument("--status-port", type=int, default=7473)
    parser.add_argument("--startup-timeout-seconds", type=int, default=420)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    smoke = _load_smoke_helper()
    profile = smoke.repo_path(args.profile)

    def preflight() -> None:
        if not profile.exists():
            raise RuntimeError(f"load profile not found: {profile}")

    return run_runtime(
        args,
        _load_executor(profile),
        operation_name="load",
        exit_code_field="load_exit_code",
        preflight=preflight,
        smoke_module=smoke,
    )


if __name__ == "__main__":
    raise SystemExit(main())
