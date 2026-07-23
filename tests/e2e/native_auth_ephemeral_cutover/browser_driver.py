#!/usr/bin/env python3
from __future__ import annotations

import http.cookiejar
import os
import ssl
import sys
import time
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
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{int(time.time())}\t{key}\t{value}\n")


def main() -> int:
    url_file = Path(os.environ["REHEARSAL_AUTH_URL_FILE"])
    events = Path(os.environ["REHEARSAL_BROWSER_EVENTS"])
    ca_file = os.environ["REHEARSAL_CA_FILE"]
    email = os.environ["REHEARSAL_IDENTITY_EMAIL"]
    password = os.environ["REHEARSAL_IDENTITY_PASSWORD"]

    events.write_text("timestamp\tkey\tvalue\n", encoding="utf-8")
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline and not url_file.exists():
        time.sleep(0.1)
    if not url_file.exists():
        append_event(events, "browser", "authorization_url_timeout")
        return 2

    authorization_url = url_file.read_text(encoding="utf-8").strip()
    url_file.unlink(missing_ok=True)
    if not authorization_url.startswith("https://platform.oteryn.test/oauth/authorize?"):
        append_event(events, "browser", "unsafe_authorization_url")
        return 3

    context = ssl.create_default_context(cafile=ca_file)
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies),
        urllib.request.HTTPSHandler(context=context),
    )

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
        current_url, html = submit(opener, current_url, login_form, {"email": email, "password": password})
        append_event(events, "login", "submitted")

        forms = parse_forms(html)
        approval_form = next(
            (form for form in forms if "auth_token" in dict(form.get("inputs") or {}) and "client_id" in dict(form.get("inputs") or {})),
            None,
        )
        if approval_form is None:
            # Some login responses redirect to the authorization endpoint only after a final GET.
            current_url, html = read_response(opener.open(current_url, timeout=20))
            forms = parse_forms(html)
            approval_form = next(
                (form for form in forms if "auth_token" in dict(form.get("inputs") or {}) and "client_id" in dict(form.get("inputs") or {})),
                None,
            )
        if approval_form is None:
            append_event(events, "authorize", "approval_form_missing")
            return 5

        final_url, _ = submit(opener, current_url, approval_form, {})
        if not final_url.startswith("http://127.0.0.1:") or "/callback" not in final_url:
            append_event(events, "callback", "unexpected_target")
            return 6
        append_event(events, "authorize", "approved")
        append_event(events, "callback", "delivered")
        append_event(events, "browser", "success")
        return 0
    except Exception as exc:  # noqa: BLE001
        append_event(events, "browser", "failure_" + type(exc).__name__)
        return 10


if __name__ == "__main__":
    sys.exit(main())
