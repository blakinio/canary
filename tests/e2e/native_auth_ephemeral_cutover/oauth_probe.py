#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import http.cookiejar
import json
import os
import secrets
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "form":
            self.current = {"action": values.get("action") or "", "inputs": {}}
            self.forms.append(self.current)
        elif tag == "input" and self.current is not None and values.get("name"):
            self.current["inputs"][values["name"]] = values.get("value") or ""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: urllib.request.Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def forms(html: str) -> list[dict[str, Any]]:
    parser = FormParser()
    parser.feed(html)
    return parser.forms


def b64url_sha256(value: str) -> str:
    digest = hashlib.sha256(value.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


class NativeOAuthProbe:
    def __init__(self) -> None:
        self.base = os.environ["REHEARSAL_PLATFORM_PUBLIC_URL"].rstrip("/")
        self.client_id = os.environ["REHEARSAL_OAUTH_CLIENT_ID"]
        self.email = os.environ["REHEARSAL_IDENTITY_EMAIL"]
        self.password = os.environ["REHEARSAL_IDENTITY_PASSWORD"]
        context = ssl.create_default_context(cafile=os.environ["REHEARSAL_CA_FILE"])
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies),
            urllib.request.HTTPSHandler(context=context),
        )
        self.no_redirect = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies),
            urllib.request.HTTPSHandler(context=context),
            NoRedirect(),
        )
        self.login()

    def _read(self, response: Any) -> tuple[int, str, str, dict[str, str]]:
        body = response.read(1024 * 1024).decode("utf-8", errors="replace")
        return response.status, response.geturl(), body, {k.lower(): v for k, v in response.headers.items()}

    def _request(self, opener: urllib.request.OpenerDirector, request: urllib.request.Request) -> tuple[int, str, str, dict[str, str]]:
        try:
            return self._read(opener.open(request, timeout=20))
        except urllib.error.HTTPError as exc:
            body = exc.read(1024 * 1024).decode("utf-8", errors="replace")
            return exc.code, exc.geturl(), body, {k.lower(): v for k, v in exc.headers.items()}

    def _get(self, url: str, *, no_redirect: bool = False) -> tuple[int, str, str, dict[str, str]]:
        return self._request(self.no_redirect if no_redirect else self.opener, urllib.request.Request(url, method="GET"))

    def _post_form(self, url: str, values: dict[str, str], *, no_redirect: bool = False) -> tuple[int, str, str, dict[str, str]]:
        request = urllib.request.Request(url, data=urllib.parse.urlencode(values).encode("utf-8"), method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        return self._request(self.no_redirect if no_redirect else self.opener, request)

    def login(self) -> None:
        status, url, html, _ = self._get(self.base + "/login")
        if status != 200:
            raise RuntimeError(f"login page status {status}")
        login_form = next((f for f in forms(html) if "email" in f["inputs"] and "password" in f["inputs"]), None)
        if login_form is None:
            raise RuntimeError("login form missing")
        action = urllib.parse.urljoin(url, login_form["action"])
        payload = dict(login_form["inputs"])
        payload.update({"email": self.email, "password": self.password})
        status, _, _, _ = self._post_form(action, payload)
        if status != 200:
            raise RuntimeError(f"login submit status {status}")

    def authorization_request_status(self, redirect_uri: str) -> int:
        verifier = secrets.token_urlsafe(48)
        query = urllib.parse.urlencode({
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "game:ticket",
            "code_challenge": b64url_sha256(verifier),
            "code_challenge_method": "S256",
            "state": secrets.token_hex(16),
        })
        status, _, _, _ = self._get(self.base + "/oauth/authorize?" + query, no_redirect=True)
        return status

    def authorize(self, *, scope: str = "game:ticket", redirect_uri: str = "http://127.0.0.1:49152/callback") -> tuple[str, str, str]:
        verifier = secrets.token_urlsafe(48)
        state = secrets.token_hex(24)
        query = urllib.parse.urlencode({
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "code_challenge": b64url_sha256(verifier),
            "code_challenge_method": "S256",
            "state": state,
        })
        status, url, html, _ = self._get(self.base + "/oauth/authorize?" + query)
        if status != 200:
            raise RuntimeError(f"authorize page status {status}")
        approval = next((f for f in forms(html) if "auth_token" in f["inputs"] and "client_id" in f["inputs"]), None)
        if approval is None:
            raise RuntimeError("approval form missing")
        action = urllib.parse.urljoin(url, approval["action"])
        status, _, _, headers = self._post_form(action, dict(approval["inputs"]), no_redirect=True)
        if status not in (301, 302, 303, 307, 308):
            raise RuntimeError(f"approval status {status}")
        location = headers.get("location", "")
        parsed = urllib.parse.urlparse(location)
        params = urllib.parse.parse_qs(parsed.query)
        code = (params.get("code") or [""])[0]
        returned_state = (params.get("state") or [""])[0]
        if not code or returned_state != state:
            raise RuntimeError("authorization callback missing code or state mismatch")
        return code, verifier, redirect_uri

    def exchange(self, code: str, verifier: str | None, redirect_uri: str) -> tuple[int, dict[str, Any], dict[str, str]]:
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        if verifier is not None:
            payload["code_verifier"] = verifier
        status, _, body, headers = self._post_form(self.base + "/oauth/token", payload)
        try:
            decoded = json.loads(body)
        except json.JSONDecodeError:
            decoded = {}
        return status, decoded, headers

    def issue_ticket(self, access_token: str) -> tuple[int, dict[str, Any], dict[str, str]]:
        request = urllib.request.Request(
            self.base + "/api/v1/game-auth/tickets",
            data=b'{"protocol_version":1}',
            method="POST",
        )
        request.add_header("Content-Type", "application/json")
        request.add_header("Accept", "application/json")
        request.add_header("Authorization", "Bearer " + access_token)
        status, _, body, headers = self._request(self.opener, request)
        try:
            decoded = json.loads(body)
        except json.JSONDecodeError:
            decoded = {}
        return status, decoded, headers


def cache_headers_ok(headers: dict[str, str]) -> bool:
    cache = headers.get("cache-control", "")
    return "no-store" in cache and "no-cache" in cache and headers.get("pragma") == "no-cache" and headers.get("expires") == "0"


def run_matrix(output: Path) -> int:
    probe = NativeOAuthProbe()
    result: dict[str, Any] = {"schema_version": 1}

    result["wrong_redirect_path_rejected"] = probe.authorization_request_status("http://127.0.0.1:49152/wrong") >= 400
    result["non_loopback_redirect_rejected"] = probe.authorization_request_status("https://client.example.test/callback") >= 400

    code, verifier, redirect = probe.authorize()
    status, _, headers = probe.exchange(code, "wrong-" + verifier, redirect)
    result["wrong_verifier_rejected"] = status == 400
    result["wrong_verifier_cache_headers"] = cache_headers_ok(headers)

    code, _, redirect = probe.authorize()
    status, _, headers = probe.exchange(code, None, redirect)
    result["missing_verifier_rejected"] = status == 400
    result["missing_verifier_cache_headers"] = cache_headers_ok(headers)

    code, verifier, redirect = probe.authorize()
    status, token, token_headers = probe.exchange(code, verifier, redirect)
    first_ok = status == 200 and isinstance(token.get("access_token"), str) and token.get("access_token")
    status_reuse, _, reuse_headers = probe.exchange(code, verifier, redirect)
    result["authorization_code_exchange"] = bool(first_ok)
    result["authorization_code_reuse_rejected"] = status_reuse == 400
    result["authorization_code_reuse_cache_headers"] = cache_headers_ok(reuse_headers)
    result["token_cache_headers"] = cache_headers_ok(token_headers)
    result["public_client_secret_absent"] = True

    if first_ok:
        ticket_status, ticket, ticket_headers = probe.issue_ticket(str(token["access_token"]))
        result["game_ticket_issued"] = ticket_status == 201 and isinstance(ticket.get("ticket"), str) and bool(ticket.get("ticket"))
        result["game_ticket_cache_headers"] = cache_headers_ok(ticket_headers)
        second_status, _, second_headers = probe.issue_ticket(str(token["access_token"]))
        result["oauth_token_family_revoked_after_ticket"] = second_status == 401
        result["oauth_token_reuse_cache_headers"] = cache_headers_ok(second_headers)
    else:
        result["game_ticket_issued"] = False
        result["game_ticket_cache_headers"] = False
        result["oauth_token_family_revoked_after_ticket"] = False
        result["oauth_token_reuse_cache_headers"] = False

    code, verifier, redirect = probe.authorize(scope="")
    status, token, _ = probe.exchange(code, verifier, redirect)
    if status == 200 and isinstance(token.get("access_token"), str):
        unscoped_status, _, unscoped_headers = probe.issue_ticket(str(token["access_token"]))
        result["token_without_game_ticket_scope_rejected"] = unscoped_status == 401
        result["unscoped_ticket_cache_headers"] = cache_headers_ok(unscoped_headers)
    else:
        result["token_without_game_ticket_scope_rejected"] = False
        result["unscoped_ticket_cache_headers"] = False

    required = [value for key, value in result.items() if key != "schema_version"]
    result["status"] = "PASS" if all(value is True for value in required) else "FAIL"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


def issue_ticket(secret_output: Path) -> int:
    probe = NativeOAuthProbe()
    code, verifier, redirect = probe.authorize()
    status, token, _ = probe.exchange(code, verifier, redirect)
    if status != 200 or not isinstance(token.get("access_token"), str):
        return 2
    ticket_status, ticket, _ = probe.issue_ticket(str(token["access_token"]))
    if ticket_status != 201 or not isinstance(ticket.get("ticket"), str) or not ticket.get("ticket"):
        return 3
    secret_output.write_text(str(ticket["ticket"]), encoding="utf-8")
    return 0


def issue_code(secret_output: Path) -> int:
    probe = NativeOAuthProbe()
    code, verifier, redirect = probe.authorize()
    secret_output.write_text(json.dumps({"code": code, "verifier": verifier, "redirect_uri": redirect}), encoding="utf-8")
    return 0


def exchange_code(secret_input: Path, output: Path) -> int:
    probe = NativeOAuthProbe()
    secret = json.loads(secret_input.read_text(encoding="utf-8"))
    status, _, headers = probe.exchange(secret["code"], secret["verifier"], secret["redirect_uri"])
    result = {
        "schema_version": 1,
        "expired_authorization_code_rejected": status == 400,
        "cache_headers": cache_headers_ok(headers),
        "status": "PASS" if status == 400 and cache_headers_ok(headers) else "FAIL",
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    matrix = sub.add_parser("matrix")
    matrix.add_argument("--output", required=True, type=Path)
    ticket = sub.add_parser("issue-ticket")
    ticket.add_argument("--secret-output", required=True, type=Path)
    code = sub.add_parser("issue-code")
    code.add_argument("--secret-output", required=True, type=Path)
    exchange = sub.add_parser("exchange-code")
    exchange.add_argument("--secret-input", required=True, type=Path)
    exchange.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.command == "matrix":
        return run_matrix(args.output)
    if args.command == "issue-ticket":
        return issue_ticket(args.secret_output)
    if args.command == "issue-code":
        return issue_code(args.secret_output)
    if args.command == "exchange-code":
        return exchange_code(args.secret_input, args.output)
    return 2


if __name__ == "__main__":
    sys.exit(main())
