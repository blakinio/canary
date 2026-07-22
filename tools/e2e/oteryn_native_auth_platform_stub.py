#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hmac
import json
import os
import re
import threading
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

MAX_BODY_BYTES = 64 * 1024
ACCOUNT_CONTEXT_RE = re.compile(r"^/internal/v1/game-auth/accounts/([1-9][0-9]*)/login-context$")


@dataclass(frozen=True)
class StubConfig:
    platform_service_token: str
    game_login_ticket: str
    canary_account_id: int
    world_id: int
    world_name: str
    world_host: str
    world_port: int
    character_name: str

    @classmethod
    def from_environment(cls) -> "StubConfig":
        def required(name: str) -> str:
            value = os.environ.get(name, "")
            if not value:
                raise ValueError(f"{name} is required")
            return value

        def positive_int(name: str, maximum: int | None = None) -> int:
            raw = required(name)
            try:
                value = int(raw)
            except ValueError as exc:
                raise ValueError(f"{name} must be a positive integer") from exc
            if value < 1 or (maximum is not None and value > maximum):
                raise ValueError(f"{name} must be between 1 and {maximum or 'unbounded'}")
            return value

        return cls(
            platform_service_token=required("AGENT_E2E_PLATFORM_SERVICE_TOKEN"),
            game_login_ticket=required("AGENT_E2E_GAME_LOGIN_TICKET"),
            canary_account_id=positive_int("AGENT_E2E_CANARY_ACCOUNT_ID"),
            world_id=positive_int("AGENT_E2E_PLATFORM_WORLD_ID"),
            world_name=required("AGENT_E2E_WORLD"),
            world_host=required("AGENT_E2E_HOST"),
            world_port=positive_int("AGENT_E2E_GAME_PORT", 65535),
            character_name=required("AGENT_E2E_CHARACTER"),
        )


class StubState:
    def __init__(self, config: StubConfig) -> None:
        self.config = config
        self._lock = threading.Lock()
        self._ticket_consumed = False

    def consume_ticket(self, ticket: str) -> bool:
        with self._lock:
            if self._ticket_consumed or not hmac.compare_digest(ticket, self.config.game_login_ticket):
                return False
            self._ticket_consumed = True
            return True


class OterynPlatformStubServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], config: StubConfig) -> None:
        super().__init__(server_address, OterynPlatformStubHandler)
        self.state = StubState(config)


class OterynPlatformStubHandler(BaseHTTPRequestHandler):
    server: OterynPlatformStubServer
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        # Do not emit request headers or bodies: they may contain test credentials.
        return

    def _json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)
        self.close_connection = True

    def _authorized(self) -> bool:
        expected = "Bearer " + self.server.state.config.platform_service_token
        supplied = self.headers.get("Authorization", "")
        return hmac.compare_digest(supplied, expected)

    def _read_json(self) -> dict[str, Any] | None:
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            return None
        try:
            length = int(raw_length)
        except ValueError:
            return None
        if length < 0 or length > MAX_BODY_BYTES:
            return None
        try:
            payload = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return payload if isinstance(payload, dict) else None

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        path = urlparse(self.path).path
        if path == "/health":
            self._json(HTTPStatus.OK, {"status": "ok"})
            return

        match = ACCOUNT_CONTEXT_RE.fullmatch(path)
        if not match:
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        if not self._authorized():
            self._json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return

        account_id = int(match.group(1))
        config = self.server.state.config
        if account_id != config.canary_account_id:
            self._json(HTTPStatus.NOT_FOUND, {"error": "account_unavailable"})
            return

        self._json(
            HTTPStatus.OK,
            {
                "protocol_version": 1,
                "worlds": [
                    {
                        "id": config.world_id,
                        "slug": "canary-e2e",
                        "name": config.world_name,
                        "region": "local",
                        "host": config.world_host,
                        "port": config.world_port,
                    }
                ],
                "characters": [
                    {
                        "id": 1,
                        "name": config.character_name,
                        "level": 8,
                        "vocation": 4,
                        "world_id": config.world_id,
                    }
                ],
            },
        )

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        path = urlparse(self.path).path
        if path != "/internal/v1/game-auth/tickets/redeem":
            self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        if not self._authorized():
            self._json(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            return

        payload = self._read_json()
        if payload is None:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid_request"})
            return
        if set(payload) != {"protocol_version", "ticket", "audience"}:
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid_request"})
            return
        if payload.get("protocol_version") != 1 or payload.get("audience") != "oteryn-game-gateway":
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid_request"})
            return
        ticket = payload.get("ticket")
        if not isinstance(ticket, str) or not self.server.state.consume_ticket(ticket):
            self._json(HTTPStatus.UNAUTHORIZED, {"error": "invalid_ticket"})
            return

        self._json(
            HTTPStatus.OK,
            {
                "protocol_version": 1,
                "authorization": {
                    "canary_account_id": self.server.state.config.canary_account_id,
                    "security_generation": 1,
                },
            },
        )


def build_server(bind: str, port: int, config: StubConfig) -> OterynPlatformStubServer:
    return OterynPlatformStubServer((bind, port), config)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Disposable Oteryn Platform dependency stub for native-auth E2E.")
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--ready-file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.port <= 65535:
        raise SystemExit("--port must be between 1 and 65535")
    try:
        config = StubConfig.from_environment()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    server = build_server(args.bind, args.port, config)
    if args.ready_file:
        args.ready_file.parent.mkdir(parents=True, exist_ok=True)
        args.ready_file.write_text("ready\n", encoding="utf-8")
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
