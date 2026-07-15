#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_HELPER_PATH = REPO_ROOT / ".github" / "scripts" / "smoke_test_canary.py"
LOAD_RUNNER_PATH = REPO_ROOT / "tools" / "e2e" / "run_agent_load.py"


class RuntimeErrorWithPhase(RuntimeError):
    def __init__(self, phase: str, message: str) -> None:
        super().__init__(message)
        self.phase = phase


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO_ROOT / path


def _read_logs(paths: list[Path]) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in paths
        if path.exists()
    )


def _wait_until_online(process: subprocess.Popen[bytes], log_paths: list[Path], timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeErrorWithPhase(
                "server-startup",
                f"Canary exited before becoming online with exit code {process.returncode}",
            )
        if "server online!" in _read_logs(log_paths).lower():
            return
        time.sleep(1)
    raise RuntimeErrorWithPhase("server-startup", "Canary did not become ready before timeout")


def _build_smoke_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        binary_path=str(_resolve_repo_path(args.binary_path)),
        data_pack=args.data_pack,
        map_name=args.map_name,
        map_download_url=args.map_download_url,
        map_cache_path=args.map_cache_path,
        db_host=args.db_host,
        db_port=args.db_port,
        db_user=args.db_user,
        db_password=args.db_password,
        db_name=args.db_name,
        login_port=args.login_port,
        game_port=args.game_port,
        status_port=args.status_port,
        startup_timeout_seconds=args.startup_timeout_seconds,
        fail_on_warnings=False,
        skip_database_init=False,
    )


def _write_runtime_summary(
    path: Path,
    *,
    status: str,
    phase: str,
    canary_pid: int | None,
    load_exit_code: int | None,
    error: str | None,
) -> None:
    payload = {
        "schema_version": 1,
        "status": status,
        "phase": phase,
        "canary_pid": canary_pid,
        "load_exit_code": load_exit_code,
        "error": error,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    smoke = _load_module("canary_smoke_helpers", SMOKE_HELPER_PATH)
    profile = _resolve_repo_path(args.profile).resolve()
    binary = _resolve_repo_path(args.binary_path).resolve()
    output_dir = _resolve_repo_path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not profile.is_file():
        raise RuntimeErrorWithPhase("validation", f"load profile not found: {profile}")
    if not binary.is_file():
        raise RuntimeErrorWithPhase("validation", f"Canary binary not found: {binary}")
    if os.name != "nt":
        binary.chmod(binary.stat().st_mode | 0o111)

    smoke_args = _build_smoke_args(args)
    config_path = REPO_ROOT / "config.lua"
    config_existed = config_path.exists()
    previous_config = config_path.read_bytes() if config_existed else None
    stdout_path = output_dir / "canary.stdout.log"
    stderr_path = output_dir / "canary.stderr.log"
    result_path = output_dir / "load-result.json"
    summary_path = output_dir / "runtime-summary.json"
    process: subprocess.Popen[bytes] | None = None
    load_exit_code: int | None = None
    phase = "bootstrap"

    try:
        phase = "database-initialization"
        smoke.prepare_map(smoke_args)
        smoke.initialize_database(smoke_args)

        phase = "server-configuration"
        smoke.write_smoke_config(smoke_args)

        phase = "server-startup"
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            process = subprocess.Popen([str(binary)], cwd=REPO_ROOT, stdout=stdout_file, stderr=stderr_file)
        (output_dir / "canary.pid").write_text(f"{process.pid}\n", encoding="utf-8")
        _wait_until_online(process, [stdout_path, stderr_path], args.startup_timeout_seconds)

        phase = "load-execution"
        command = [
            sys.executable,
            str(LOAD_RUNNER_PATH),
            "--profile",
            str(profile),
            "--output",
            str(result_path),
            "--host",
            "127.0.0.1",
            "--port",
            str(args.status_port),
            "--server-pid",
            str(process.pid),
        ]
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True)
        load_exit_code = completed.returncode

        if process.poll() is not None:
            raise RuntimeErrorWithPhase(
                "load-execution",
                f"Canary exited during load with exit code {process.returncode}",
            )
        if load_exit_code != 0:
            raise RuntimeErrorWithPhase(
                "load-evaluation",
                f"load runner failed its gate with exit code {load_exit_code}",
            )

        phase = "runtime-log-evaluation"
        runtime_log = _read_logs([stdout_path, stderr_path])
        smoke.assert_clean_log(runtime_log, fail_on_warnings=False)
        _write_runtime_summary(
            summary_path,
            status="success",
            phase="complete",
            canary_pid=process.pid,
            load_exit_code=load_exit_code,
            error=None,
        )
        return 0
    except Exception as exc:
        error_phase = exc.phase if isinstance(exc, RuntimeErrorWithPhase) else phase
        _write_runtime_summary(
            summary_path,
            status="failure",
            phase=error_phase,
            canary_pid=process.pid if process is not None else None,
            load_exit_code=load_exit_code,
            error=str(exc),
        )
        print(f"ERROR [{error_phase}]: {exc}", file=sys.stderr)
        return 1
    finally:
        if process is not None:
            smoke.stop_process(process)
        smoke.restore_config(config_path, config_existed, previous_config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Start an exact-head local Canary runtime and execute one loopback load profile."
    )
    parser.add_argument("--binary-path", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--data-pack", choices=["data-canary", "data-otservbr-global"], default="data-canary")
    parser.add_argument("--map-name", default="canary")
    parser.add_argument("--map-download-url", default="")
    parser.add_argument("--map-cache-path", default="")
    parser.add_argument("--db-host", default="127.0.0.1")
    parser.add_argument("--db-port", type=int, default=3306)
    parser.add_argument("--db-user", default="root")
    parser.add_argument("--db-password", default="root")
    parser.add_argument("--db-name", default="canary_agent_load")
    parser.add_argument("--login-port", type=int, default=7471)
    parser.add_argument("--game-port", type=int, default=7472)
    parser.add_argument("--status-port", type=int, default=7473)
    parser.add_argument("--startup-timeout-seconds", type=int, default=300)
    return parser


def main(argv: list[str] | None = None) -> int:
    return run(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
