from __future__ import annotations

import importlib.util
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "e2e" / "oteryn_native_auth_platform_stub.py"
SPEC = importlib.util.spec_from_file_location("oteryn_native_auth_platform_stub", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
stub = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stub
SPEC.loader.exec_module(stub)


@pytest.fixture()
def running_stub():
    config = stub.StubConfig(
        platform_service_token="platform-service-token",
        game_login_ticket="fresh-ticket",
        canary_account_id=101,
        world_id=1,
        world_name="Canary E2E",
        world_host="127.0.0.1",
        world_port=7172,
        character_name="Knight 1",
    )
    server = stub.build_server("127.0.0.1", 0, config)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", config
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def request_json(url: str, *, method: str = "GET", payload=None, token: str | None = None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    if token is not None:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_health_is_public_and_cache_bounded(running_stub):
    base_url, _ = running_stub
    status, payload = request_json(base_url + "/health")
    assert status == 200
    assert payload == {"status": "ok"}


def test_ticket_is_single_use_and_context_is_service_authenticated(running_stub):
    base_url, config = running_stub

    status, _ = request_json(base_url + f"/internal/v1/game-auth/accounts/{config.canary_account_id}/login-context")
    assert status == 401

    redeem = {
        "protocol_version": 1,
        "ticket": config.game_login_ticket,
        "audience": "oteryn-game-gateway",
    }
    status, payload = request_json(
        base_url + "/internal/v1/game-auth/tickets/redeem",
        method="POST",
        payload=redeem,
        token=config.platform_service_token,
    )
    assert status == 200
    assert payload["authorization"]["canary_account_id"] == config.canary_account_id

    status, _ = request_json(
        base_url + "/internal/v1/game-auth/tickets/redeem",
        method="POST",
        payload=redeem,
        token=config.platform_service_token,
    )
    assert status == 401

    status, payload = request_json(
        base_url + f"/internal/v1/game-auth/accounts/{config.canary_account_id}/login-context",
        token=config.platform_service_token,
    )
    assert status == 200
    assert payload["protocol_version"] == 1
    assert payload["worlds"] == [
        {
            "id": 1,
            "slug": "canary-e2e",
            "name": "Canary E2E",
            "region": "local",
            "host": "127.0.0.1",
            "port": 7172,
        }
    ]
    assert payload["characters"][0]["name"] == "Knight 1"
    assert payload["characters"][0]["world_id"] == 1
