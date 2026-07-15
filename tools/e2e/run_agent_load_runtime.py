#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_HELPER = REPO_ROOT / ".github" / "scripts" / "smoke_test_canary.py"
LOAD_RUNNER = REPO_ROOT / "tools" / "e2e" / "run_agent_load.py"


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
    binary = smoke.repo_path(args.binary_path)
    profile = smoke.repo_path(args.profile)
    artifact_dir = smoke.repo_path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary_path = artifact_dir / "runtime-summary.json"
    stdout_path = artifact_dir / "canary.stdout.log"
    stderr_path = artifact_dir / "canary.stderr.log"
    result_path = artifact_dir / "load-result.json"
    config_path = REPO_ROOT / "config.lua"
    config_existed = config_path.exists()
    previous_config = config_path.read_bytes() if config_existed else None
    process: subprocess.Popen[bytes] | None = None
    phase = "bootstrap"
    load_exit_code: int | None = None

    try:
        if not binary.exists():
            raise RuntimeError(f"Canary binary not found: {binary}")
        if not profile.exists():
            raise RuntimeError(f"load profile not found: {profile}")
        if sys.platform != "win32":
            binary.chmod(binary.stat().st_mode | 0o111)

        phase = "database-initialization"
        smoke.prepare_map(args)
        smoke.initialize_database(args)
        phase = "server-configuration"
        smoke.write_smoke_config(args)

        phase = "server-startup"
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            process = subprocess.Popen([str(binary)], cwd=REPO_ROOT, stdout=stdout_file, stderr=stderr_file)

        deadline = time.time() + args.startup_timeout_seconds
        while time.time() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Canary exited before becoming online with code {process.returncode}")
            if "server online!" in smoke.read_logs([stdout_path, stderr_path]).lower():
                break
            time.sleep(1)
        else:
            raise RuntimeError("Canary did not become online before timeout")

        phase = "load"
        command = [
            sys.executable,
            str(LOAD_RUNNER),
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
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
        (artifact_dir / "load.stdout.log").write_text(completed.stdout, encoding="utf-8")
        (artifact_dir / "load.stderr.log").write_text(completed.stderr, encoding="utf-8")
        load_exit_code = completed.returncode
        if completed.returncode != 0:
            raise RuntimeError(f"load runner failed with exit code {completed.returncode}")
        if process.poll() is not None:
            raise RuntimeError(f"Canary exited during load with code {process.returncode}")

        phase = "complete"
        _write_summary(
            summary_path,
            schema_version=1,
            status="success",
            phase=phase,
            load_exit_code=load_exit_code,
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
            load_exit_code=load_exit_code,
            canary_exit_code=process.poll() if process else None,
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if process is not None:
            smoke.stop_process(process)
        smoke.restore_config(config_path, config_existed, previous_config)


if __name__ == "__main__":
    raise SystemExit(main())
