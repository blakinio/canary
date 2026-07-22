#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_DATAPACK = "data-otservbr-global"
DEFAULT_MAP = "otservbr"
SAFE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NATIVE_AUTH_MODE = "oteryn_gateway"
NATIVE_AUTH_GATEWAY_REPOSITORY = "blakinio/Oteryn-Platform"
PROCESS_TIMEOUT_SECONDS = 900


class ServerSelectionError(ValueError):
    pass


@dataclass(frozen=True)
class ServerSelection:
    datapack: str
    map_name: str
    datapack_path: Path
    map_path: Path
    allow_map_download: bool


@dataclass(frozen=True)
class NativeAuthSelection:
    gateway_repository: str
    gateway_ref: str
    gateway_port: int
    platform_stub_port: int
    session_issuer_port: int
    canary_account_id: int
    platform_world_id: int


def _safe_segment(value: object, field: str) -> str:
    if not isinstance(value, str) or not SAFE_SEGMENT_RE.fullmatch(value):
        raise ServerSelectionError(
            f"scenario.server.{field} must be a safe repository-local path segment matching {SAFE_SEGMENT_RE.pattern}"
        )
    return value


def _inside(path: Path, parent: Path, field: str) -> None:
    if not path.is_relative_to(parent):
        raise ServerSelectionError(f"scenario.server.{field} resolves outside the repository-selected runtime root")


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ServerSelectionError(f"cannot read scenario manifest: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ServerSelectionError("scenario manifest must be a JSON object")
    return manifest


def _scenario(manifest: dict[str, Any]) -> dict[str, Any]:
    scenario = manifest.get("scenario")
    if not isinstance(scenario, dict):
        raise ServerSelectionError("scenario manifest is missing scenario object")
    return scenario


def resolve_server_selection(manifest_path: Path, root: Path) -> ServerSelection:
    manifest = _load_manifest(manifest_path)
    scenario = _scenario(manifest)
    server = scenario.get("server")
    if not isinstance(server, dict):
        raise ServerSelectionError("scenario manifest is missing scenario.server object")

    datapack = _safe_segment(server.get("datapack"), "datapack")
    map_name = _safe_segment(server.get("map"), "map")

    repository_root = root.resolve()
    datapack_path = (repository_root / datapack).resolve(strict=False)
    _inside(datapack_path, repository_root, "datapack")
    if not datapack_path.is_dir():
        raise ServerSelectionError(f"selected datapack directory does not exist: {datapack_path}")

    world_path = (datapack_path / "world").resolve(strict=False)
    _inside(world_path, datapack_path, "datapack")
    map_path = (world_path / f"{map_name}.otbm").resolve(strict=False)
    _inside(map_path, world_path, "map")

    allow_map_download = datapack == DEFAULT_DATAPACK and map_name == DEFAULT_MAP
    if not allow_map_download and (not map_path.is_file() or map_path.stat().st_size <= 0):
        raise ServerSelectionError(f"selected non-default map is missing or empty: {map_path}")

    return ServerSelection(
        datapack=datapack,
        map_name=map_name,
        datapack_path=datapack_path,
        map_path=map_path,
        allow_map_download=allow_map_download,
    )


def _positive_int(value: object, field: str, maximum: int | None = None) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ServerSelectionError(f"scenario.auth.{field} must be a positive integer")
    if maximum is not None and value > maximum:
        raise ServerSelectionError(f"scenario.auth.{field} must be <= {maximum}")
    return value


def resolve_native_auth_selection(manifest_path: Path) -> NativeAuthSelection | None:
    scenario = _scenario(_load_manifest(manifest_path))
    auth = scenario.get("auth")
    if auth is None:
        return None
    if not isinstance(auth, dict):
        raise ServerSelectionError("scenario.auth must be an object when present")

    allowed = {
        "mode",
        "gateway_repository",
        "gateway_ref",
        "gateway_port",
        "platform_stub_port",
        "session_issuer_port",
        "canary_account_id",
        "platform_world_id",
    }
    unknown = sorted(set(auth) - allowed)
    if unknown:
        raise ServerSelectionError(f"scenario.auth contains unknown field(s): {', '.join(unknown)}")
    if auth.get("mode") != NATIVE_AUTH_MODE:
        raise ServerSelectionError(f"scenario.auth.mode must be {NATIVE_AUTH_MODE!r}")

    gateway_repository = auth.get("gateway_repository")
    if gateway_repository != NATIVE_AUTH_GATEWAY_REPOSITORY:
        raise ServerSelectionError(
            f"scenario.auth.gateway_repository must be {NATIVE_AUTH_GATEWAY_REPOSITORY!r} for the maintained native-auth proof"
        )
    gateway_ref = auth.get("gateway_ref")
    if not isinstance(gateway_ref, str) or not SHA_RE.fullmatch(gateway_ref):
        raise ServerSelectionError("scenario.auth.gateway_ref must be an exact 40-character lowercase SHA")

    gateway_port = _positive_int(auth.get("gateway_port"), "gateway_port", 65535)
    platform_stub_port = _positive_int(auth.get("platform_stub_port"), "platform_stub_port", 65535)
    session_issuer_port = _positive_int(auth.get("session_issuer_port"), "session_issuer_port", 65535)
    if len({gateway_port, platform_stub_port, session_issuer_port}) != 3:
        raise ServerSelectionError("scenario.auth gateway/stub/session ports must be distinct")

    return NativeAuthSelection(
        gateway_repository=gateway_repository,
        gateway_ref=gateway_ref,
        gateway_port=gateway_port,
        platform_stub_port=platform_stub_port,
        session_issuer_port=session_issuer_port,
        canary_account_id=_positive_int(auth.get("canary_account_id"), "canary_account_id"),
        platform_world_id=_positive_int(auth.get("platform_world_id"), "platform_world_id"),
    )


def github_environment(selection: ServerSelection) -> dict[str, str]:
    return {
        "AGENT_E2E_SERVER_DATAPACK": selection.datapack,
        "AGENT_E2E_SERVER_MAP": selection.map_name,
        "AGENT_E2E_SERVER_DATAPACK_PATH": str(selection.datapack_path),
        "AGENT_E2E_SERVER_MAP_PATH": str(selection.map_path),
        "AGENT_E2E_SERVER_ALLOW_MAP_DOWNLOAD": "true" if selection.allow_map_download else "false",
    }


def _native_auth_environment(selection: NativeAuthSelection) -> tuple[dict[str, str], dict[str, str]]:
    platform_service_token = secrets.token_urlsafe(32)
    session_service_token = secrets.token_urlsafe(32)
    game_login_ticket = secrets.token_urlsafe(32)
    session_service_hash = hashlib.sha256(session_service_token.encode("utf-8")).hexdigest()

    exported = {
        "AGENT_E2E_AUTH_MODE": NATIVE_AUTH_MODE,
        "AGENT_E2E_GATEWAY_BASE_URL": f"http://127.0.0.1:{selection.gateway_port}",
        "AGENT_E2E_PLATFORM_STUB_PORT": str(selection.platform_stub_port),
        "AGENT_E2E_SESSION_ISSUER_PORT": str(selection.session_issuer_port),
        "AGENT_E2E_CANARY_ACCOUNT_ID": str(selection.canary_account_id),
        "AGENT_E2E_PLATFORM_WORLD_ID": str(selection.platform_world_id),
        "AGENT_E2E_PLATFORM_SERVICE_TOKEN": platform_service_token,
        "AGENT_E2E_SESSION_SERVICE_TOKEN": session_service_token,
        "AGENT_E2E_GAME_LOGIN_TICKET": game_login_ticket,
        "AGENT_E2E_GATEWAY_REPOSITORY": selection.gateway_repository,
        "AGENT_E2E_GATEWAY_REF": selection.gateway_ref,
        "CANARY_GAME_SESSION_ISSUER_ENABLED": "true",
        "CANARY_GAME_SESSION_ISSUER_BIND": "127.0.0.1",
        "CANARY_GAME_SESSION_ISSUER_PORT": str(selection.session_issuer_port),
        "CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256": session_service_hash,
        "CANARY_GAME_SESSION_ISSUER_WORLD_ID": str(selection.platform_world_id),
    }
    runtime = dict(exported)
    return exported, runtime


def _run_checked(command: list[str], *, cwd: Path | None = None, stdout: Path | None = None) -> None:
    output_handle = stdout.open("w", encoding="utf-8") if stdout else subprocess.DEVNULL
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            stdout=output_handle,
            stderr=subprocess.STDOUT if stdout else subprocess.PIPE,
            text=True,
            check=False,
        )
    finally:
        if stdout:
            output_handle.close()
    if completed.returncode != 0:
        detail = ""
        if not stdout and isinstance(completed.stderr, str):
            detail = completed.stderr.strip()[:1000]
        raise ServerSelectionError(f"command failed ({completed.returncode}): {' '.join(command)} {detail}".strip())


def _wait_http_ok(url: str, timeout_seconds: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = "unavailable"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2.0) as response:  # noqa: S310 - literal loopback E2E URLs only
                if response.status == 200:
                    return
                last_error = f"HTTP {response.status}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = type(exc).__name__
        time.sleep(0.25)
    raise ServerSelectionError(f"runtime endpoint did not become healthy: {url} ({last_error})")


def _start_bounded_process(command: list[str], *, env: dict[str, str], stdout: Path, stderr: Path) -> int:
    timeout_binary = shutil.which("timeout")
    if not timeout_binary:
        raise ServerSelectionError("required command not found: timeout")
    with stdout.open("w", encoding="utf-8") as out_handle, stderr.open("w", encoding="utf-8") as err_handle:
        process = subprocess.Popen(
            [timeout_binary, "--signal=TERM", str(PROCESS_TIMEOUT_SECONDS), *command],
            env=env,
            stdout=out_handle,
            stderr=err_handle,
            start_new_session=True,
        )
    return process.pid


def prepare_native_auth_runtime(
    manifest_path: Path,
    root: Path,
    selection: NativeAuthSelection,
) -> dict[str, str]:
    manifest = _load_manifest(manifest_path)
    scenario = _scenario(manifest)
    fixture = scenario.get("fixture")
    if not isinstance(fixture, dict):
        raise ServerSelectionError("scenario manifest is missing scenario.fixture object")

    required_fixture_fields = ("character", "world", "host", "game_port")
    for field in required_fixture_fields:
        if fixture.get(field) in (None, ""):
            raise ServerSelectionError(f"scenario.fixture.{field} is required for native-auth runtime")

    exported, runtime_values = _native_auth_environment(selection)
    artifact_dir = Path(os.environ.get("AGENT_E2E_ARTIFACT_DIR", root / "artifacts")).resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    runtime_root = (root / ".agent-e2e" / "oteryn-native-auth").resolve()
    if not runtime_root.is_relative_to(root.resolve()):
        raise ServerSelectionError("native-auth runtime root escaped repository workspace")
    shutil.rmtree(runtime_root, ignore_errors=True)
    runtime_root.mkdir(parents=True, exist_ok=True)

    for command in ("git", "go"):
        if shutil.which(command) is None:
            raise ServerSelectionError(f"required command not found: {command}")

    platform_root = runtime_root / "oteryn-platform"
    _run_checked(["git", "init", str(platform_root)], stdout=artifact_dir / "gateway-git-init.log")
    _run_checked(
        ["git", "-C", str(platform_root), "remote", "add", "origin", f"https://github.com/{selection.gateway_repository}.git"]
    )
    _run_checked(
        ["git", "-C", str(platform_root), "fetch", "--depth", "1", "origin", selection.gateway_ref],
        stdout=artifact_dir / "gateway-git-fetch.log",
    )
    _run_checked(["git", "-C", str(platform_root), "checkout", "--detach", "FETCH_HEAD"])
    actual_ref = subprocess.check_output(
        ["git", "-C", str(platform_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_ref != selection.gateway_ref:
        raise ServerSelectionError(f"Gateway checkout mismatch: expected {selection.gateway_ref}, got {actual_ref}")
    (artifact_dir / "gateway-source-commit.txt").write_text(actual_ref + "\n", encoding="utf-8")

    gateway_source = platform_root / "services" / "game-gateway"
    gateway_binary = runtime_root / "game-gateway"
    _run_checked(
        ["go", "build", "-trimpath", "-o", str(gateway_binary), "./cmd/game-gateway"],
        cwd=gateway_source,
        stdout=artifact_dir / "gateway-build.log",
    )
    if not gateway_binary.is_file():
        raise ServerSelectionError("Gateway build did not produce an executable")
    gateway_hash = hashlib.sha256(gateway_binary.read_bytes()).hexdigest()
    (artifact_dir / "gateway-binary-sha256.txt").write_text(f"{gateway_hash}  game-gateway\n", encoding="utf-8")

    runtime_env = os.environ.copy()
    runtime_env.update(runtime_values)
    runtime_env.update(
        {
            "AGENT_E2E_CHARACTER": str(fixture["character"]),
            "AGENT_E2E_WORLD": str(fixture["world"]),
            "AGENT_E2E_HOST": str(fixture["host"]),
            "AGENT_E2E_GAME_PORT": str(fixture["game_port"]),
        }
    )

    stub_script = root / "tools" / "e2e" / "oteryn_native_auth_platform_stub.py"
    if not stub_script.is_file():
        raise ServerSelectionError(f"native-auth Platform stub is missing: {stub_script}")
    stub_ready = artifact_dir / "platform-stub-ready.txt"
    stub_pid = _start_bounded_process(
        [
            sys.executable,
            str(stub_script),
            "--bind",
            "127.0.0.1",
            "--port",
            str(selection.platform_stub_port),
            "--ready-file",
            str(stub_ready),
        ],
        env=runtime_env,
        stdout=artifact_dir / "platform-stub.stdout.log",
        stderr=artifact_dir / "platform-stub.stderr.log",
    )

    gateway_env = runtime_env.copy()
    gateway_env.update(
        {
            "OTERYN_PLATFORM_BASE_URL": f"http://127.0.0.1:{selection.platform_stub_port}",
            "OTERYN_PLATFORM_SERVICE_TOKEN": runtime_values["AGENT_E2E_PLATFORM_SERVICE_TOKEN"],
            "GAME_SESSION_SERVICE_BASE_URL": f"http://127.0.0.1:{selection.session_issuer_port}",
            "GAME_SESSION_SERVICE_TOKEN": runtime_values["AGENT_E2E_SESSION_SERVICE_TOKEN"],
            "GATEWAY_LISTEN_ADDR": f"127.0.0.1:{selection.gateway_port}",
            "GATEWAY_REQUEST_TIMEOUT": "5s",
            "GATEWAY_VERSION": f"e2e-{selection.gateway_ref[:12]}",
        }
    )
    gateway_pid = _start_bounded_process(
        [str(gateway_binary)],
        env=gateway_env,
        stdout=artifact_dir / "gateway.stdout.log",
        stderr=artifact_dir / "gateway.stderr.log",
    )

    _wait_http_ok(f"http://127.0.0.1:{selection.platform_stub_port}/health")
    _wait_http_ok(f"http://127.0.0.1:{selection.gateway_port}/health")

    (artifact_dir / "native-auth-runtime.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "gateway_repository": selection.gateway_repository,
                "gateway_ref": selection.gateway_ref,
                "gateway_port": selection.gateway_port,
                "platform_stub_port": selection.platform_stub_port,
                "session_issuer_port": selection.session_issuer_port,
                "canary_account_id": selection.canary_account_id,
                "platform_world_id": selection.platform_world_id,
                "platform_stub_pid": stub_pid,
                "gateway_pid": gateway_pid,
                "process_timeout_seconds": PROCESS_TIMEOUT_SECONDS,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return exported


def write_github_env(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            if "\n" in value or "\r" in value:
                raise ServerSelectionError(f"environment value for {key} contains a newline")
            handle.write(f"{key}={value}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve a repository-confined physical E2E server datapack and map.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--github-env", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest_path = args.manifest.resolve()
        root = args.root.resolve()
        selection = resolve_server_selection(manifest_path, root)
        environment = github_environment(selection)
        native_auth = resolve_native_auth_selection(manifest_path)
        if native_auth is not None:
            environment.update(prepare_native_auth_runtime(manifest_path, root, native_auth))
        write_github_env(args.github_env, environment)
    except (ServerSelectionError, OSError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
