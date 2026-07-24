#!/usr/bin/env python3
from __future__ import annotations

import http.cookiejar
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


class FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, object]] = []
        self._current: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "form":
            self._current = {
                "action": values.get("action") or "",
                "method": (values.get("method") or "get").lower(),
                "inputs": {},
            }
            self.forms.append(self._current)
            return
        if tag == "input" and self._current is not None:
            name = values.get("name")
            if not name:
                return
            inputs = self._current["inputs"]
            assert isinstance(inputs, dict)
            inputs[name] = values.get("value") or ""


def parse_forms(html: str) -> list[dict[str, object]]:
    parser = FormParser()
    parser.feed(html)
    return parser.forms


def read_response(response: object) -> tuple[str, str]:
    body = response.read(1024 * 1024).decode("utf-8", errors="replace")
    return response.geturl(), body


def submit(opener: urllib.request.OpenerDirector, base_url: str, form: dict[str, object], values: dict[str, str]) -> tuple[str, str]:
    action = urllib.parse.urljoin(base_url, str(form.get("action") or base_url))
    inputs = dict(form.get("inputs") or {})
    inputs.update(values)
    encoded = urllib.parse.urlencode(inputs).encode("utf-8")
    request = urllib.request.Request(action, data=encoded, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    return read_response(opener.open(request, timeout=20))


def append_event(path: Path, key: str, value: str) -> None:
    safe_value = str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{int(time.time())}\t{key}\t{safe_value}\n")


def first_value(query: dict[str, list[str]], name: str) -> str:
    values = query.get(name, [])
    return values[0] if values else ""


def record_authorization_metadata(events: Path, authorization_url: str, expected_client_id: str) -> None:
    parsed = urllib.parse.urlparse(authorization_url)
    query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
    redirect = urllib.parse.urlparse(first_value(query, "redirect_uri"))
    state = first_value(query, "state")
    challenge = first_value(query, "code_challenge")

    append_event(events, "authorization_query_keys", ",".join(sorted(query)))
    append_event(events, "authorization_client_id_matches", str(first_value(query, "client_id") == expected_client_id).lower())
    append_event(events, "authorization_response_type", first_value(query, "response_type") or "missing")
    append_event(events, "authorization_scope_present", str(bool(first_value(query, "scope"))).lower())
    append_event(events, "authorization_pkce_method", first_value(query, "code_challenge_method") or "missing")
    append_event(events, "authorization_state_length", str(len(state)))
    append_event(events, "authorization_challenge_length", str(len(challenge)))
    append_event(events, "authorization_redirect_scheme", redirect.scheme or "missing")
    append_event(events, "authorization_redirect_host", redirect.hostname or "missing")
    append_event(events, "authorization_redirect_port_present", str(redirect.port is not None).lower())
    append_event(events, "authorization_redirect_path", redirect.path or "missing")


def classify_error_body(body: str) -> str:
    lowered = body.lower()
    markers = [
        ("invalid_request", "invalid_request"),
        ("invalid_client", "invalid_client"),
        ("invalid_grant", "invalid_grant"),
        ("unsupported_response_type", "unsupported_response_type"),
        ("invalid_scope", "invalid_scope"),
        ("redirect_uri", "redirect_uri"),
        ("code_challenge", "code_challenge"),
        ("pkce", "pkce"),
        ("too many", "rate_limited"),
        ("page expired", "csrf_or_session"),
    ]
    for needle, label in markers:
        if needle in lowered:
            return label
    return "unclassified"


def main() -> int:
    url_file = Path(os.environ["REHEARSAL_AUTH_URL_FILE"])
    events = Path(os.environ["REHEARSAL_BROWSER_EVENTS"])
    ca_file = os.environ["REHEARSAL_CA_FILE"]
    email = os.environ["REHEARSAL_IDENTITY_EMAIL"]
    password = os.environ["REHEARSAL_IDENTITY_PASSWORD"]
    client_id = os.environ.get("REHEARSAL_OAUTH_CLIENT_ID", "")

    events.write_text("timestamp\tkey\tvalue\n", encoding="utf-8")
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline and not url_file.exists():
        time.sleep(0.1)
    if not url_file.exists():
        append_event(events, "browser", "authorization_url_timeout")
        return 2

    authorization_url = url_file.read_text(encoding="utf-8").strip()
    url_file.unlink(missing_ok=True)
    record_authorization_metadata(events, authorization_url, client_id)
    if not authorization_url.startswith("https://platform.oteryn.test/oauth/authorize?"):
        append_event(events, "browser", "unsafe_authorization_url")
        return 3

    context = ssl.create_default_context(cafile=ca_file)
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies),
        urllib.request.HTTPSHandler(context=context),
    )

    phase = "authorize_open"
    try:
        current_url, html = read_response(opener.open(authorization_url, timeout=20))
        append_event(events, "authorize", "opened")

        forms = parse_forms(html)
        login_form = next(
            (form for form in forms if "email" in dict(form.get("inputs") or {}) and "password" in dict(form.get("inputs") or {})),
            None,
        )
        if login_form is None:
            append_event(events, "login", "form_missing")
            return 4
        phase = "login_submit"
        current_url, html = submit(opener, current_url, login_form, {"email": email, "password": password})
        append_event(events, "login", "submitted")

        forms = parse_forms(html)
        approval_form = next(
            (form for form in forms if "auth_token" in dict(form.get("inputs") or {}) and "client_id" in dict(form.get("inputs") or {})),
            None,
        )
        if approval_form is None:
            phase = "authorize_followup"
            current_url, html = read_response(opener.open(current_url, timeout=20))
            forms = parse_forms(html)
            approval_form = next(
                (form for form in forms if "auth_token" in dict(form.get("inputs") or {}) and "client_id" in dict(form.get("inputs") or {})),
                None,
            )
        if approval_form is None:
            append_event(events, "authorize", "approval_form_missing")
            return 5

        phase = "authorize_approve"
        final_url, _ = submit(opener, current_url, approval_form, {})
        if not final_url.startswith("http://127.0.0.1:") or "/callback" not in final_url:
            append_event(events, "callback", "unexpected_target")
            return 6
        append_event(events, "authorize", "approved")
        append_event(events, "callback", "delivered")
        append_event(events, "browser", "success")
        return 0
    except urllib.error.HTTPError as exc:
        body = exc.read(4096).decode("utf-8", errors="replace")
        parsed_error_url = urllib.parse.urlparse(exc.geturl())
        append_event(events, "http_error_phase", phase)
        append_event(events, "http_error_status", str(exc.code))
        append_event(events, "http_error_path", parsed_error_url.path or "missing")
        append_event(events, "http_error_classification", classify_error_body(body))
        append_event(events, "browser", "failure_HTTPError")
        return 10
    except Exception as exc:  # noqa: BLE001
        append_event(events, "failure_phase", phase)
        append_event(events, "browser", "failure_" + type(exc).__name__)
        return 10


if __name__ == "__main__":
    sys.exit(main())
