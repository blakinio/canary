#!/usr/bin/env python3
from __future__ import annotations

import argparse
import errno
import hashlib
import importlib.util
import ipaddress
import json
import re
import socket
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PROVIDER = REPO_ROOT / "tools" / "e2e" / "run_agent_load_runtime.py"
AUTHORIZED_REPOSITORY = "blakinio/canary"
PLAN_SCHEMA = "ots-security-login-packet-plan-v1"
REPORT_SCHEMA = "ots-security-login-packet-report-v1"
DRIVER_ID = "canary-login-parser-v1"
SERVICE_ID = "login"
CURRENT_CLIENT_VERSION = 1525
PROTOCOL_IDENTIFIER = 0x01
RSA_BLOCK_SIZE = 128
RSA_PUBLIC_EXPONENT = 65537
# Public modulus corresponding to Canary's repository-owned default OpenTibia RSA key.
# Keeping only the public value here avoids duplicating private factors in the test driver.
RSA_PUBLIC_MODULUS = int(
    "109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413"
)
PRE_RSA_SKIP_BYTES = 17
MAX_CASES = 16
MAX_RESPONSE_BYTES = 1024 * 1024
PLAN_FIELDS = {"schema", "id", "authorized_repository", "driver", "service", "cases"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
RESET_ERRNOS = {errno.ECONNRESET, errno.ECONNABORTED, errno.EPIPE}
FATAL_SIGNATURES = (
    "addresssanitizer",
    "undefinedbehaviorsanitizer",
    "leaksanitizer",
    "threadsanitizer",
    "heap-use-after-free",
    "stack-buffer-overflow",
    "double-free",
    "segmentation fault",
    "sigsegv",
    "fatal signal",
    "runtime error:",
    "terminate called",
    "assertion failed",
)
XTEA_KEY = (0x10203040, 0x50607080, 0x90A0B0C0, 0xD0E0F000)
CONTROL_ACCOUNT = "security-probe.invalid"
CONTROL_ERROR = "Invalid email."
RESPONSE_NONE = "none"
RESPONSE_ANY = "any"
RESPONSE_CURRENT_LOGIN_ERROR = "current-login-error"


class SecurityPlanError(ValueError):
    pass


class ProbeFailure(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class LoginCase:
    case_id: str
    payload: bytes
    response_policy: str
    expected_error: str | None = None


def _u16(value: int) -> bytes:
    return struct.pack("<H", value)


def _u32(value: int) -> bytes:
    return struct.pack("<I", value)


def _add_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    if len(encoded) > 0xFFFF:
        raise ValueError("string too long")
    return _u16(len(encoded)) + encoded


def _raw_rsa_encrypt(plaintext: bytes) -> bytes:
    if len(plaintext) != RSA_BLOCK_SIZE:
        raise ValueError(f"RSA plaintext must be exactly {RSA_BLOCK_SIZE} bytes")
    value = int.from_bytes(plaintext, "big")
    if value >= RSA_PUBLIC_MODULUS:
        raise ValueError("RSA plaintext is not below the public modulus")
    encrypted = pow(value, RSA_PUBLIC_EXPONENT, RSA_PUBLIC_MODULUS)
    return encrypted.to_bytes(RSA_BLOCK_SIZE, "big")


def _rsa_plaintext(*, marker: int = 0, account: str | None = None, password: str | None = None) -> bytes:
    if not 0 <= marker <= 0xFF:
        raise ValueError("marker out of range")
    payload = bytearray([marker])
    for word in XTEA_KEY:
        payload.extend(_u32(word))
    if account is not None:
        payload.extend(_add_string(account))
    if password is not None:
        payload.extend(_add_string(password))
    if len(payload) > RSA_BLOCK_SIZE:
        raise ValueError("RSA plaintext fields exceed one block")
    payload.extend(b"\x00" * (RSA_BLOCK_SIZE - len(payload)))
    return bytes(payload)


def _login_payload(version: int, rsa_block: bytes | None = None, *, pre_rsa_bytes: int = PRE_RSA_SKIP_BYTES) -> bytes:
    payload = b"\x00\x00" + _u16(version) + (b"\x00" * pre_rsa_bytes)
    if rsa_block is not None:
        payload += rsa_block
    return payload


def frame_login_packet(payload: bytes) -> bytes:
    body_without_checksum = bytes([PROTOCOL_IDENTIFIER]) + payload
    checksum = zlib.adler32(body_without_checksum) & 0xFFFFFFFF
    body = _u32(checksum) + body_without_checksum
    if len(body) > 0xFFFF:
        raise ValueError("framed login packet is too large")
    return _u16(len(body)) + body


def _build_cases() -> dict[str, LoginCase]:
    valid_empty_account_rsa = _raw_rsa_encrypt(_rsa_plaintext(account=""))
    valid_empty_password_rsa = _raw_rsa_encrypt(_rsa_plaintext(account=CONTROL_ACCOUNT, password=""))
    invalid_marker_rsa = _raw_rsa_encrypt(_rsa_plaintext(marker=1))
    return {
        "unsupported-version": LoginCase(
            "unsupported-version",
            frame_login_packet(b"\x00\x00" + _u16(1)),
            RESPONSE_ANY,
        ),
        "current-prelude-only": LoginCase(
            "current-prelude-only",
            frame_login_packet(_login_payload(CURRENT_CLIENT_VERSION)),
            RESPONSE_NONE,
        ),
        "current-truncated-rsa": LoginCase(
            "current-truncated-rsa",
            frame_login_packet(_login_payload(CURRENT_CLIENT_VERSION, b"\x00" * (RSA_BLOCK_SIZE - 1))),
            RESPONSE_NONE,
        ),
        "current-invalid-rsa-marker": LoginCase(
            "current-invalid-rsa-marker",
            frame_login_packet(_login_payload(CURRENT_CLIENT_VERSION, invalid_marker_rsa)),
            RESPONSE_NONE,
        ),
        "current-rsa-empty-account": LoginCase(
            "current-rsa-empty-account",
            frame_login_packet(_login_payload(CURRENT_CLIENT_VERSION, valid_empty_account_rsa)),
            RESPONSE_CURRENT_LOGIN_ERROR,
            CONTROL_ERROR,
        ),
        "current-rsa-empty-password": LoginCase(
            "current-rsa-empty-password",
            frame_login_packet(_login_payload(CURRENT_CLIENT_VERSION, valid_empty_password_rsa)),
            RESPONSE_CURRENT_LOGIN_ERROR,
            "Invalid password.",
        ),
    }


CASES = _build_cases()
CONTROL_PACKET = CASES["current-rsa-empty-account"].payload


def _load_runtime_provider() -> ModuleType:
    spec = importlib.util.spec_from_file_location("security_login_runtime_provider", RUNTIME_PROVIDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runtime provider: {RUNTIME_PROVIDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"


def _require_exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise SecurityPlanError(f"{label} fields mismatch: missing={missing} unknown={unknown}")


def load_plan(path: Path, authorized_repository: str) -> dict[str, Any]:
    if authorized_repository != AUTHORIZED_REPOSITORY:
        raise SecurityPlanError("caller repository is not authorized")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SecurityPlanError(f"cannot read plan: {type(exc).__name__}") from exc
    if not isinstance(payload, dict):
        raise SecurityPlanError("plan root must be an object")
    _require_exact_fields(payload, PLAN_FIELDS, "plan")
    if payload["schema"] != PLAN_SCHEMA:
        raise SecurityPlanError(f"unsupported plan schema: {payload['schema']!r}")
    plan_id = payload["id"]
    if not isinstance(plan_id, str) or ID_PATTERN.fullmatch(plan_id) is None:
        raise SecurityPlanError("plan id must be a bounded lowercase identifier")
    if payload["authorized_repository"] != AUTHORIZED_REPOSITORY:
        raise SecurityPlanError("plan repository authorization mismatch")
    if payload["authorized_repository"] != authorized_repository:
        raise SecurityPlanError("caller and plan repository authorization differ")
    if payload["driver"] != DRIVER_ID:
        raise SecurityPlanError(f"unsupported driver: {payload['driver']!r}")
    if payload["service"] != SERVICE_ID:
        raise SecurityPlanError(f"unsupported service: {payload['service']!r}")
    case_ids = payload["cases"]
    if not isinstance(case_ids, list) or not 1 <= len(case_ids) <= MAX_CASES:
        raise SecurityPlanError(f"cases must contain between 1 and {MAX_CASES} entries")
    if any(not isinstance(case_id, str) for case_id in case_ids):
        raise SecurityPlanError("every case id must be a string")
    if len(set(case_ids)) != len(case_ids):
        raise SecurityPlanError("duplicate case ids are not allowed")
    unknown_cases = sorted(set(case_ids) - set(CASES))
    if unknown_cases:
        raise SecurityPlanError(f"unknown case ids: {unknown_cases}")
    return payload


def _is_reset_error(exc: OSError) -> bool:
    return isinstance(exc, (ConnectionResetError, BrokenPipeError)) or exc.errno in RESET_ERRNOS


def _require_loopback_target(host: str, port: int) -> None:
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ProbeFailure("target-not-literal-ip") from exc
    if host != "127.0.0.1" or not address.is_loopback:
        raise ProbeFailure("target-not-authorized-loopback")
    if not 1 <= int(port) <= 65535:
        raise ProbeFailure("target-port-out-of-range")


def _xtea_decrypt_blocks(ciphertext: bytes) -> bytes:
    if not ciphertext or len(ciphertext) % 8 != 0:
        raise ProbeFailure("response-xtea-block-size")
    output = bytearray()
    delta = 0x61C88647
    mask = 0xFFFFFFFF
    for offset in range(0, len(ciphertext), 8):
        v0, v1 = struct.unpack("<II", ciphertext[offset : offset + 8])
        total = 0xC6EF3720
        for _ in range(32):
            mix1 = ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ ((total + XTEA_KEY[(total >> 11) & 3]) & mask)) & mask
            v1 = (v1 - mix1) & mask
            total = (total + delta) & mask
            mix0 = ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ ((total + XTEA_KEY[total & 3]) & mask)) & mask
            v0 = (v0 - mix0) & mask
        output.extend(struct.pack("<II", v0, v1))
    return bytes(output)


def decode_current_login_error(response: bytes) -> str:
    if len(response) < 14:
        raise ProbeFailure("response-current-login-too-short")
    block_count = int.from_bytes(response[:2], "little")
    if block_count == 0:
        raise ProbeFailure("response-current-login-zero-blocks")
    ciphertext_size = block_count * 8
    if len(response) != 2 + 4 + ciphertext_size:
        raise ProbeFailure("response-current-login-length-mismatch")
    received_checksum = int.from_bytes(response[2:6], "little")
    ciphertext = response[6:]
    if (zlib.adler32(ciphertext) & 0xFFFFFFFF) != received_checksum:
        raise ProbeFailure("response-current-login-checksum-mismatch")
    plaintext = _xtea_decrypt_blocks(ciphertext)
    padding_size = plaintext[0]
    if padding_size > len(plaintext) - 1:
        raise ProbeFailure("response-current-login-padding-invalid")
    body_end = len(plaintext) - padding_size
    body = plaintext[1:body_end]
    if len(body) < 3 or body[0] != 0x0B:
        raise ProbeFailure("response-current-login-opcode-invalid")
    message_size = int.from_bytes(body[1:3], "little")
    if 3 + message_size != len(body):
        raise ProbeFailure("response-current-login-string-length-invalid")
    try:
        return body[3:].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProbeFailure("response-current-login-string-invalid") from exc


def exchange_packet(packet: bytes, host: str, port: int, timeout_seconds: float) -> bytes:
    _require_loopback_target(host, port)
    try:
        connection = socket.create_connection((host, port), timeout=timeout_seconds)
    except OSError as exc:
        raise ProbeFailure("probe-connect-failed") from exc
    response = bytearray()
    with connection:
        connection.settimeout(timeout_seconds)
        try:
            connection.sendall(packet)
            while len(response) <= MAX_RESPONSE_BYTES:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                response.extend(chunk)
        except socket.timeout as exc:
            raise ProbeFailure("probe-timeout") from exc
        except OSError as exc:
            if not _is_reset_error(exc):
                raise ProbeFailure("probe-transport-error") from exc
    if len(response) > MAX_RESPONSE_BYTES:
        raise ProbeFailure("probe-response-too-large")
    return bytes(response)


def validate_case_response(case: LoginCase, response: bytes) -> str | None:
    if case.response_policy == RESPONSE_NONE:
        if response:
            raise ProbeFailure("unexpected-response")
        return None
    if case.response_policy == RESPONSE_ANY:
        if not response:
            raise ProbeFailure("expected-response-missing")
        return None
    if case.response_policy == RESPONSE_CURRENT_LOGIN_ERROR:
        if not response:
            raise ProbeFailure("expected-response-missing")
        message = decode_current_login_error(response)
        if case.expected_error is not None and message != case.expected_error:
            raise ProbeFailure("response-current-login-error-mismatch")
        return message
    raise ProbeFailure("unknown-response-policy")


def probe_case(case: LoginCase, host: str, port: int, timeout_seconds: float) -> tuple[bytes, str | None]:
    response = exchange_packet(case.payload, host, port, timeout_seconds)
    return response, validate_case_response(case, response)


def probe_login_control(host: str, port: int, timeout_seconds: float) -> tuple[bytes, str]:
    response = exchange_packet(CONTROL_PACKET, host, port, timeout_seconds)
    if not response:
        raise ProbeFailure("control-response-missing")
    message = decode_current_login_error(response)
    if message != CONTROL_ERROR:
        raise ProbeFailure("control-response-error-mismatch")
    return response, message


def scan_fatal_logs(stdout_path: Path, stderr_path: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in (stdout_path, stderr_path):
        try:
            text = path.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        for signature in FATAL_SIGNATURES:
            if signature in text:
                findings.append({"path": path.name, "signature": signature})
    return sorted(findings, key=lambda finding: (finding["path"], finding["signature"]))


def build_report(
    *,
    plan: dict[str, Any],
    plan_sha256: str,
    context: Any,
    case_results: list[dict[str, Any]],
    fatal_findings: list[dict[str, str]],
    status: str,
    failure: str | None,
) -> dict[str, Any]:
    provider_paths = (Path(__file__).resolve(), RUNTIME_PROVIDER.resolve())
    provider_hashes = {
        str(path.relative_to(REPO_ROOT)): _sha256_file(path)
        for path in provider_paths
    }
    return {
        "schema": REPORT_SCHEMA,
        "status": status,
        "plan": {"id": plan["id"], "sha256": plan_sha256},
        "authorization": {"repository": AUTHORIZED_REPOSITORY},
        "driver": DRIVER_ID,
        "service": SERVICE_ID,
        "runtime": {"host": context.host, "login_port": int(context.login_port)},
        "evidence": {
            "binary_sha256": _sha256_file(Path(context.binary_path)),
            "provider_sha256": dict(sorted(provider_hashes.items())),
            "control_packet_sha256": _sha256_bytes(CONTROL_PACKET),
        },
        "cases": case_results,
        "fatal_log_findings": fatal_findings,
        "failure": failure,
    }


def _bounded_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be numeric") from exc
    if not 0.1 <= timeout <= 10.0:
        raise argparse.ArgumentTypeError("timeout must be between 0.1 and 10 seconds")
    return timeout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded login-parser probes against disposable Canary.")
    parser.add_argument("--binary-path", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--authorized-repository", required=True)
    parser.add_argument("--artifact-dir", default="artifacts/security-login-packets")
    parser.add_argument("--db-port", type=int, default=3306)
    parser.add_argument("--db-password", default="root")
    parser.add_argument("--db-name", default="canary_security_login_runtime")
    parser.add_argument("--login-port", type=int, default=7471)
    parser.add_argument("--game-port", type=int, default=7472)
    parser.add_argument("--status-port", type=int, default=7473)
    parser.add_argument("--startup-timeout-seconds", type=int, default=420)
    parser.add_argument("--probe-timeout-seconds", type=_bounded_timeout, default=3.0)
    return parser.parse_args()
