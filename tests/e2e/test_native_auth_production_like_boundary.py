#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import http.client
import ipaddress
import json
import os
import secrets
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

EXPECTED_GATEWAY_REF = "53158217a6c6017230301cf4daa783b04fcc13d5"
EXPECTED_CANARY_REF = "981c82f5ebb6bc22c867312c2b274a71f6aeeb3e"
EXPECTED_OTCLIENT_REF = "bb87346f6c516a19d19497d82bb01fb389334ff5"
MAX_BODY = 64 * 1024


class BoundaryTestError(RuntimeError):
    pass


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_http(url: str, expected: int = 200, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    last = "unavailable"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status == expected:
                    return
                last = f"HTTP {response.status}"
        except urllib.error.HTTPError as exc:
            if exc.code == expected:
                return
            last = f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = type(exc).__name__
        time.sleep(0.1)
    raise BoundaryTestError(f"endpoint did not reach HTTP {expected}: {url} ({last})")


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, str], str]:
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=8.0) as response:
            body = response.read(MAX_BODY).decode("utf-8", errors="replace")
            return response.status, {key.lower(): value for key, value in response.headers.items()}, body
    except urllib.error.HTTPError as exc:
        body = exc.read(MAX_BODY).decode("utf-8", errors="replace")
        return exc.code, {key.lower(): value for key, value in exc.headers.items()}, body


def assert_no_cache(headers: dict[str, str]) -> None:
    if headers.get("cache-control") != "no-store, no-cache, must-revalidate, private":
        raise BoundaryTestError(f"unexpected Cache-Control: {headers.get('cache-control')!r}")
    if headers.get("pragma") != "no-cache":
        raise BoundaryTestError(f"unexpected Pragma: {headers.get('pragma')!r}")
    if headers.get("expires") != "0":
        raise BoundaryTestError(f"unexpected Expires: {headers.get('expires')!r}")


@dataclass
class PlatformConfig:
    service_token: str
    ticket: str
    account_id: int = 101
    world_id: int = 1


class PlatformState:
    def __init__(self, config: PlatformConfig) -> None:
        self.config = config
        self.lock = threading.Lock()
        self.consumed = False


class PlatformServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], config: PlatformConfig) -> None:
        super().__init__(address, PlatformHandler)
        self.state = PlatformState(config)


class PlatformHandler(BaseHTTPRequestHandler):
    server: PlatformServer
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)
        self.close_connection = True

    def _authorized(self) -> bool:
        return secrets.compare_digest(
            self.headers.get("Authorization", ""),
            "Bearer " + self.server.state.config.service_token,
        )

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(HTTPStatus.OK, {"status": "ok"})
            return
        expected = f"/internal/v1/game-auth/accounts/{self.server.state.config.account_id}/login-context"
        if self.path != expected:
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        if not self._authorized():
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return
        self._send(
            HTTPStatus.OK,
            {
                "protocol_version": 1,
                "worlds": [
                    {
                        "id": self.server.state.config.world_id,
                        "slug": "canary-e2e",
                        "name": "Canary E2E",
                        "region": "local",
                        "host": "127.0.0.1",
                        "port": 7172,
                    }
                ],
                "characters": [
                    {
                        "id": 1,
                        "name": "Knight 1",
                        "level": 8,
                        "vocation": 4,
                        "world_id": self.server.state.config.world_id,
                    }
                ],
            },
        )

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/internal/v1/game-auth/tickets/redeem":
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        if not self._authorized():
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_request"})
            return
        ticket = payload.get("ticket") if isinstance(payload, dict) else None
        with self.server.state.lock:
            accepted = (
                not self.server.state.consumed
                and isinstance(ticket, str)
                and secrets.compare_digest(ticket, self.server.state.config.ticket)
            )
            if accepted:
                self.server.state.consumed = True
        if not accepted:
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "invalid_ticket"})
            return
        self._send(
            HTTPStatus.OK,
            {
                "protocol_version": 1,
                "authorization": {
                    "canary_account_id": self.server.state.config.account_id,
                    "security_generation": 1,
                },
            },
        )


class SessionState:
    def __init__(self, accepted_tokens: set[str]) -> None:
        self.lock = threading.Lock()
        self.accepted_tokens = set(accepted_tokens)
        self.requests = 0

    def replace_tokens(self, tokens: set[str]) -> None:
        with self.lock:
            self.accepted_tokens = set(tokens)

    def accepts(self, token: str) -> bool:
        with self.lock:
            return any(secrets.compare_digest(token, candidate) for candidate in self.accepted_tokens)


class SessionServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: SessionState) -> None:
        super().__init__(address, SessionHandler)
        self.state = state


class SessionHandler(BaseHTTPRequestHandler):
    server: SessionServer
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)
        self.close_connection = True

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(HTTPStatus.OK, {"status": "ok", "protocol_version": 1})
        else:
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/internal/v1/game-sessions":
            self._send(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        authorization = self.headers.get("Authorization", "")
        if not authorization.startswith("Bearer ") or not self.server.state.accepts(authorization[7:]):
            self._send(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized_service"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_request"})
            return
        if not isinstance(payload, dict) or payload.get("protocol_version") != 1:
            self._send(HTTPStatus.BAD_REQUEST, {"error": "invalid_request"})
            return
        with self.server.state.lock:
            self.server.state.requests += 1
            request_number = self.server.state.requests
        expires = datetime.now(timezone.utc) + timedelta(seconds=60)
        self._send(
            HTTPStatus.OK,
            {
                "protocol_version": 1,
                "session": {
                    "credential": f"opaque-production-like-session-{request_number}",
                    "expires_at": expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
            },
        )


def run_openssl(command: list[str], cwd: Path) -> None:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise BoundaryTestError(f"openssl failed: {' '.join(command)}: {completed.stderr.strip()[:500]}")


def create_tls_material(root: Path) -> tuple[Path, Path, Path, Path]:
    root.mkdir(parents=True, exist_ok=True)
    ca_key = root / "ca.key"
    ca_cert = root / "ca.crt"
    server_key = root / "server.key"
    server_csr = root / "server.csr"
    server_cert = root / "server.crt"
    extension = root / "server.ext"
    wrong_ca_key = root / "wrong-ca.key"
    wrong_ca_cert = root / "wrong-ca.crt"
    extension.write_text("subjectAltName=DNS:localhost\nextendedKeyUsage=serverAuth\n", encoding="utf-8")
    run_openssl(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-keyout", str(ca_key), "-out", str(ca_cert), "-subj", "/CN=Oteryn Production Like CA"],
        root,
    )
    run_openssl(
        ["openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", str(server_key), "-out", str(server_csr), "-subj", "/CN=localhost"],
        root,
    )
    run_openssl(
        ["openssl", "x509", "-req", "-days", "1", "-sha256", "-in", str(server_csr), "-CA", str(ca_cert), "-CAkey", str(ca_key), "-CAcreateserial", "-out", str(server_cert), "-extfile", str(extension)],
        root,
    )
    run_openssl(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-keyout", str(wrong_ca_key), "-out", str(wrong_ca_cert), "-subj", "/CN=Wrong Oteryn CA"],
        root,
    )
    for private_path in (ca_key, server_key, wrong_ca_key):
        private_path.chmod(0o600)
    return ca_cert, server_cert, server_key, wrong_ca_cert


def start_session_server(cert: Path, key: Path, state: SessionState) -> tuple[SessionServer, threading.Thread, int]:
    server = SessionServer(("127.0.0.1", 0), state)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert, keyfile=key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
    thread.start()
    return server, thread, int(server.server_address[1])


def start_platform_server(config: PlatformConfig) -> tuple[PlatformServer, threading.Thread, int]:
    server = PlatformServer(("127.0.0.1", 0), config)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.1}, daemon=True)
    thread.start()
    return server, thread, int(server.server_address[1])


def stop_server(server: ThreadingHTTPServer, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


@dataclass
class GatewayProcess:
    process: subprocess.Popen[str]
    stdout_path: Path
    stderr_path: Path
    port: int
    secrets_to_scan: tuple[str, ...]

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

    def assert_no_secret_leaks(self) -> None:
        text = ""
        for path in (self.stdout_path, self.stderr_path):
            if path.exists():
                text += path.read_text(encoding="utf-8", errors="replace")
        for secret in self.secrets_to_scan:
            if secret and secret in text:
                raise BoundaryTestError(f"secret leaked to Gateway logs: sha256={hashlib.sha256(secret.encode()).hexdigest()}")


def start_gateway(
    gateway_bin: Path,
    artifact_dir: Path,
    label: str,
    platform_port: int,
    platform_token: str,
    session_url: str,
    session_token: str,
    ca_file: Path | None,
    ticket: str = "",
) -> GatewayProcess:
    port = free_port()
    stdout_path = artifact_dir / f"gateway-{label}.stdout.log"
    stderr_path = artifact_dir / f"gateway-{label}.stderr.log"
    env = os.environ.copy()
    env.update(
        {
            "OTERYN_PLATFORM_BASE_URL": f"http://127.0.0.1:{platform_port}",
            "OTERYN_PLATFORM_SERVICE_TOKEN": platform_token,
            "GAME_SESSION_SERVICE_BASE_URL": session_url,
            "GAME_SESSION_SERVICE_TOKEN": session_token,
            "GATEWAY_LISTEN_ADDR": f"127.0.0.1:{port}",
            "GATEWAY_REQUEST_TIMEOUT": "2s",
            "GATEWAY_VERSION": f"production-like-{EXPECTED_GATEWAY_REF[:12]}",
        }
    )
    if ca_file is not None:
        env["SSL_CERT_FILE"] = str(ca_file)
    else:
        env.pop("SSL_CERT_FILE", None)
    out_handle = stdout_path.open("w", encoding="utf-8")
    err_handle = stderr_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [str(gateway_bin)],
        env=env,
        stdout=out_handle,
        stderr=err_handle,
        text=True,
    )
    out_handle.close()
    err_handle.close()
    gateway = GatewayProcess(process, stdout_path, stderr_path, port, (platform_token, session_token, ticket))
    wait_http(f"http://127.0.0.1:{port}/health", 200)
    return gateway


def assert_config_rejects_non_loopback_http(gateway_bin: Path, artifact_dir: Path) -> None:
    env = os.environ.copy()
    env.update(
        {
            "OTERYN_PLATFORM_BASE_URL": "http://127.0.0.1:18081",
            "OTERYN_PLATFORM_SERVICE_TOKEN": "ephemeral-platform-config-test",
            "GAME_SESSION_SERVICE_BASE_URL": "http://canary.internal.test:18443",
            "GAME_SESSION_SERVICE_TOKEN": "ephemeral-session-config-test",
            "GATEWAY_LISTEN_ADDR": "127.0.0.1:18080",
        }
    )
    completed = subprocess.run([str(gateway_bin)], env=env, text=True, capture_output=True, timeout=5, check=False)
    (artifact_dir / "non-loopback-http.stdout.log").write_text(completed.stdout, encoding="utf-8")
    (artifact_dir / "non-loopback-http.stderr.log").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode == 0 or "configuration_invalid" not in completed.stdout:
        raise BoundaryTestError("Gateway did not fail closed for non-loopback plain HTTP Session dependency")


def login_case(
    gateway_bin: Path,
    artifact_dir: Path,
    label: str,
    session_url: str,
    session_token: str,
    ca_file: Path,
    expected_status: int,
) -> dict[str, Any]:
    platform_token = secrets.token_urlsafe(32)
    ticket = secrets.token_urlsafe(32)
    platform, platform_thread, platform_port = start_platform_server(PlatformConfig(platform_token, ticket))
    gateway: GatewayProcess | None = None
    try:
        gateway = start_gateway(
            gateway_bin,
            artifact_dir,
            label,
            platform_port,
            platform_token,
            session_url,
            session_token,
            ca_file,
            ticket,
        )
        status, headers, body = request_json(
            "POST",
            f"http://127.0.0.1:{gateway.port}/v1/login",
            {"protocol_version": 1, "game_login_ticket": ticket},
        )
        if status != expected_status:
            raise BoundaryTestError(f"{label}: expected HTTP {expected_status}, got {status}: {body[:200]}")
        assert_no_cache(headers)
        if expected_status == 200:
            decoded = json.loads(body)
            if decoded.get("protocol_version") != 1 or not decoded.get("session", {}).get("credential"):
                raise BoundaryTestError(f"{label}: malformed successful login response")
        elif "login_unavailable" not in body:
            raise BoundaryTestError(f"{label}: expected bounded login_unavailable response")
        gateway.assert_no_secret_leaks()
        return {"status": status, "cache_control": headers.get("cache-control")}
    finally:
        if gateway is not None:
            gateway.stop()
            gateway.assert_no_secret_leaks()
        stop_server(platform, platform_thread)


def readiness_case(
    gateway_bin: Path,
    artifact_dir: Path,
    label: str,
    session_url: str,
    ca_file: Path,
    session_token: str,
    expected_status: int,
) -> int:
    platform_token = secrets.token_urlsafe(32)
    platform, platform_thread, platform_port = start_platform_server(
        PlatformConfig(platform_token, secrets.token_urlsafe(32))
    )
    gateway: GatewayProcess | None = None
    try:
        gateway = start_gateway(
            gateway_bin,
            artifact_dir,
            label,
            platform_port,
            platform_token,
            session_url,
            session_token,
            ca_file,
        )
        status, _, _ = request_json("GET", f"http://127.0.0.1:{gateway.port}/ready")
        if status != expected_status:
            raise BoundaryTestError(f"{label}: expected readiness HTTP {expected_status}, got {status}")
        gateway.assert_no_secret_leaks()
        return status
    finally:
        if gateway is not None:
            gateway.stop()
            gateway.assert_no_secret_leaks()
        stop_server(platform, platform_thread)


def non_loopback_addresses() -> list[str]:
    completed = subprocess.run(["hostname", "-I"], text=True, capture_output=True, check=False)
    addresses: list[str] = []
    if completed.returncode == 0:
        for raw in completed.stdout.split():
            try:
                parsed = ipaddress.ip_address(raw)
            except ValueError:
                continue
            if parsed.version == 4 and not parsed.is_loopback:
                addresses.append(raw)
    return addresses


def assert_loopback_only(port: int) -> str:
    addresses = non_loopback_addresses()
    if not addresses:
        raise BoundaryTestError("runner has no observable non-loopback IPv4 address for ingress-isolation simulation")
    target = addresses[0]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        try:
            sock.connect((target, port))
        except OSError:
            return target
    raise BoundaryTestError(f"loopback-bound TLS Session service was reachable through non-loopback interface {target}")


def verify_revision_pins(repo_root: Path, gateway_source: Path) -> dict[str, str]:
    actual_gateway = subprocess.check_output(["git", "-C", str(gateway_source), "rev-parse", "HEAD"], text=True).strip()
    if actual_gateway != EXPECTED_GATEWAY_REF:
        raise BoundaryTestError(f"Gateway revision mismatch: {actual_gateway}")

    pin_text = (repo_root / ".github" / "e2e-controlled-server.env").read_text(encoding="utf-8")
    expected_pin = f"SERVER_REF={EXPECTED_CANARY_REF}"
    if expected_pin not in pin_text:
        raise BoundaryTestError("Canary controlled-server revision pin does not match hardened merge")

    scenario = json.loads(
        (repo_root / "tests" / "e2e" / "scenarios" / "login" / "oteryn-native-auth.json").read_text(encoding="utf-8")
    )
    if scenario.get("client", {}).get("ref") != EXPECTED_OTCLIENT_REF:
        raise BoundaryTestError("OTClient scenario revision pin mismatch")
    if scenario.get("auth", {}).get("gateway_ref") != EXPECTED_GATEWAY_REF:
        raise BoundaryTestError("Gateway scenario revision pin mismatch")
    return {
        "gateway": actual_gateway,
        "canary": EXPECTED_CANARY_REF,
        "otclient": EXPECTED_OTCLIENT_REF,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validation-only Oteryn native-auth production-like boundary simulation")
    parser.add_argument("--gateway-bin", type=Path, required=True)
    parser.add_argument("--gateway-source", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--artifact-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    gateway_bin = args.gateway_bin.resolve()
    gateway_source = args.gateway_source.resolve()
    artifact_dir = args.artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    if not gateway_bin.is_file() or not os.access(gateway_bin, os.X_OK):
        raise BoundaryTestError(f"Gateway binary is not executable: {gateway_bin}")

    revisions = verify_revision_pins(repo_root, gateway_source)
    (artifact_dir / "revisions.json").write_text(json.dumps(revisions, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    current_token = secrets.token_urlsafe(32)
    previous_token = secrets.token_urlsafe(32)
    state = SessionState({current_token, previous_token})

    with tempfile.TemporaryDirectory(prefix="oteryn-prod-like-tls-") as temporary:
        tls_root = Path(temporary)
        ca_cert, server_cert, server_key, wrong_ca = create_tls_material(tls_root)
        session_server, session_thread, session_port = start_session_server(server_cert, server_key, state)
        try:
            loopback_probe_address = assert_loopback_only(session_port)
            assert_config_rejects_non_loopback_http(gateway_bin, artifact_dir)

            session_localhost = f"https://localhost:{session_port}"
            session_ip = f"https://127.0.0.1:{session_port}"

            trusted_ready = readiness_case(
                gateway_bin,
                artifact_dir,
                "trusted-tls-readiness",
                session_localhost,
                ca_cert,
                current_token,
                200,
            )
            previous_overlap = login_case(
                gateway_bin,
                artifact_dir,
                "previous-overlap",
                session_localhost,
                previous_token,
                ca_cert,
                200,
            )
            current_overlap = login_case(
                gateway_bin,
                artifact_dir,
                "current-overlap",
                session_localhost,
                current_token,
                ca_cert,
                200,
            )

            state.replace_tokens({current_token})
            retired_previous = login_case(
                gateway_bin,
                artifact_dir,
                "retired-previous",
                session_localhost,
                previous_token,
                ca_cert,
                503,
            )
            current_after_rotation = login_case(
                gateway_bin,
                artifact_dir,
                "current-after-rotation",
                session_localhost,
                current_token,
                ca_cert,
                200,
            )

            wrong_ca_status = readiness_case(
                gateway_bin,
                artifact_dir,
                "wrong-ca",
                session_localhost,
                wrong_ca,
                current_token,
                503,
            )
            hostname_mismatch_status = readiness_case(
                gateway_bin,
                artifact_dir,
                "hostname-mismatch",
                session_ip,
                ca_cert,
                current_token,
                503,
            )

            state.replace_tokens({current_token, previous_token})
            rollback_overlap = login_case(
                gateway_bin,
                artifact_dir,
                "rollback-overlap-restored",
                session_localhost,
                previous_token,
                ca_cert,
                200,
            )

            result = {
                "schema_version": 1,
                "classification": "PRODUCTION_LIKE_PROVEN",
                "status": "success",
                "revisions": revisions,
                "checks": {
                    "non_loopback_plain_http_rejected": True,
                    "trusted_tls_readiness": trusted_ready == 200,
                    "loopback_only_ingress_simulated": True,
                    "loopback_probe_address": loopback_probe_address,
                    "previous_credential_accepted_during_overlap": previous_overlap["status"] == 200,
                    "current_credential_accepted_during_overlap": current_overlap["status"] == 200,
                    "retired_previous_credential_rejected": retired_previous["status"] == 503,
                    "current_credential_accepted_after_rotation": current_after_rotation["status"] == 200,
                    "wrong_ca_failed_closed": wrong_ca_status == 503,
                    "hostname_mismatch_failed_closed": hostname_mismatch_status == 503,
                    "rollback_overlap_restored": rollback_overlap["status"] == 200,
                    "sensitive_gateway_responses_non_cacheable": all(
                        item["cache_control"] == "no-store, no-cache, must-revalidate, private"
                        for item in (previous_overlap, current_overlap, retired_previous, current_after_rotation, rollback_overlap)
                    ),
                    "retained_logs_secret_scan": True,
                },
                "non_claims": [
                    "This simulation does not prove the real production firewall or private network.",
                    "This simulation does not prove the real production certificate, DNS, trust termination, or secret manager state.",
                    "This simulation does not prove the actual deployed production revisions.",
                ],
            }
            (artifact_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        finally:
            stop_server(session_server, session_thread)

    print(json.dumps({"status": "success", "classification": "PRODUCTION_LIKE_PROVEN", "revisions": revisions}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BoundaryTestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
