#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import socket
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PROVIDER = REPO_ROOT / "tools" / "e2e" / "run_agent_load_runtime.py"
AUTHORIZED_REPOSITORY = "blakinio/canary"
PLAN_SCHEMA = "ots-security-game-session-plan-v1"
REPORT_SCHEMA = "ots-security-game-session-report-v1"
DRIVER_ID = "canary-game-session-v1"
SERVICE_ID = "game"
CURRENT_CLIENT_VERSION = 1525
CURRENT_CLIENT_VERSION_STRING = "15.25.794c2e"
CLIENT_OS_WINDOWS = 2
RSA_BLOCK_SIZE = 128
RSA_PUBLIC_EXPONENT = 65537
RSA_PUBLIC_MODULUS = int(
    "109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413"
)
XTEA_KEY = (0x10203040, 0x50607080, 0x90A0B0C0, 0xD0E0F000)
MAX_CASES = 12
MAX_RESPONSE_BYTES = 1024 * 1024
PLAN_FIELDS = {"schema", "id", "authorized_repository", "driver", "service", "cases"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
PING_OPCODE = 0x1E
AUTH_ERROR_OPCODE = 0x14
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

# These are repository-owned disposable test fixtures imported by
# .github/scripts/smoke_test_canary.py. They are deliberately code-owned and
# never accepted from a scenario manifest.
FIXTURES = tuple(
    (f"fixture-{index:02d}", f"@test{index}", "test", f"Knight {index}")
    for index in range(1, 13)
)

CASE_AUTHENTICATED_CONTROL = "authenticated-control"
CASE_ZERO_SEQUENCE = "post-login-zero-sequence"
CASE_SEQUENCE_GAP = "post-login-sequence-gap"
CASE_SEQUENCE_REPLAY = "post-login-sequence-replay"
CASE_INVALID_XTEA_PADDING = "post-login-invalid-xtea-padding"
CASES = {
    CASE_AUTHENTICATED_CONTROL,
    CASE_ZERO_SEQUENCE,
    CASE_SEQUENCE_GAP,
    CASE_SEQUENCE_REPLAY,
    CASE_INVALID_XTEA_PADDING,
}


class SecurityPlanError(ValueError):
    pass


class ProbeFailure(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class GameChallenge:
    timestamp: int
    random: int
    packet_sha256: str


@dataclass(frozen=True)
class DecodedGameFrame:
    sequence: int
    compressed: bool
    payload: bytes
    packet_sha256: str


def _u16(value: int) -> bytes:
    return struct.pack("<H", value)


def _u32(value: int) -> bytes:
    return struct.pack("<I", value)


def _add_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    if len(encoded) > 0xFFFF:
        raise ValueError("string too long")
    return _u16(len(encoded)) + encoded


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
    unknown_cases = sorted(set(case_ids) - CASES)
    if unknown_cases:
        raise SecurityPlanError(f"unknown case ids: {unknown_cases}")
    if len(case_ids) * 2 > len(FIXTURES):
        raise SecurityPlanError("plan exceeds code-owned disposable fixture capacity")
    return payload


def _require_loopback_target(host: str, port: int) -> None:
    try:
        address = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ProbeFailure("target-not-literal-ip") from exc
    if host != "127.0.0.1" or not address.is_loopback:
        raise ProbeFailure("target-not-authorized-loopback")
    if not 1 <= int(port) <= 65535:
        raise ProbeFailure("target-port-out-of-range")


def _raw_rsa_encrypt(plaintext: bytes) -> bytes:
    if len(plaintext) != RSA_BLOCK_SIZE:
        raise ValueError(f"RSA plaintext must be exactly {RSA_BLOCK_SIZE} bytes")
    value = int.from_bytes(plaintext, "big")
    if value >= RSA_PUBLIC_MODULUS:
        raise ValueError("RSA plaintext is not below the public modulus")
    encrypted = pow(value, RSA_PUBLIC_EXPONENT, RSA_PUBLIC_MODULUS)
    return encrypted.to_bytes(RSA_BLOCK_SIZE, "big")


def _xtea_encrypt_blocks(plaintext: bytes, key: tuple[int, int, int, int] = XTEA_KEY) -> bytes:
    if not plaintext or len(plaintext) % 8 != 0:
        raise ValueError("XTEA plaintext length must be a non-zero multiple of 8")
    output = bytearray()
    mask = 0xFFFFFFFF
    delta = 0x9E3779B9
    for offset in range(0, len(plaintext), 8):
        v0, v1 = struct.unpack("<II", plaintext[offset : offset + 8])
        total = 0
        for _ in range(32):
            v0 = (v0 + ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ ((total + key[total & 3]) & mask))) & mask
            total = (total + delta) & mask
            v1 = (v1 + ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ ((total + key[(total >> 11) & 3]) & mask))) & mask
        output.extend(struct.pack("<II", v0, v1))
    return bytes(output)


def _xtea_decrypt_blocks(ciphertext: bytes, key: tuple[int, int, int, int] = XTEA_KEY) -> bytes:
    if not ciphertext or len(ciphertext) % 8 != 0:
        raise ProbeFailure("server-frame-xtea-block-size")
    output = bytearray()
    mask = 0xFFFFFFFF
    delta = 0x9E3779B9
    for offset in range(0, len(ciphertext), 8):
        v0, v1 = struct.unpack("<II", ciphertext[offset : offset + 8])
        total = 0xC6EF3720
        for _ in range(32):
            v1 = (v1 - ((((v0 << 4) ^ (v0 >> 5)) + v0) ^ ((total + key[(total >> 11) & 3]) & mask))) & mask
            total = (total - delta) & mask
            v0 = (v0 - ((((v1 << 4) ^ (v1 >> 5)) + v1) ^ ((total + key[total & 3]) & mask))) & mask
        output.extend(struct.pack("<II", v0, v1))
    return bytes(output)


def _rsa_game_plaintext(
    account_descriptor: str,
    password: str,
    character_name: str,
    challenge: GameChallenge,
) -> bytes:
    payload = bytearray([0])
    for word in XTEA_KEY:
        payload.extend(_u32(word))
    payload.append(0)
    payload.extend(_add_string(f"{account_descriptor}\n{password}"))
    payload.extend(_add_string(character_name))
    payload.extend(_u32(challenge.timestamp))
    payload.append(challenge.random)
    payload.extend(_u16(0))
    if len(payload) > RSA_BLOCK_SIZE:
        raise ValueError("game RSA plaintext exceeds one block")
    payload.extend(b"\x00" * (RSA_BLOCK_SIZE - len(payload)))
    return bytes(payload)


def build_game_login_packet(
    account_descriptor: str,
    password: str,
    character_name: str,
    challenge: GameChallenge,
) -> bytes:
    rsa_block = _raw_rsa_encrypt(
        _rsa_game_plaintext(account_descriptor, password, character_name, challenge)
    )
    payload = bytearray()
    payload.extend(_u16(CLIENT_OS_WINDOWS))
    payload.extend(_u16(CURRENT_CLIENT_VERSION))
    payload.extend(_u32(CURRENT_CLIENT_VERSION))
    payload.extend(_add_string(CURRENT_CLIENT_VERSION_STRING))
    payload.extend(_add_string(""))
    payload.append(0)
    payload.extend(rsa_block)
    padding = (-len(payload)) % 8
    payload.extend(b"\x00" * padding)
    return _u16(len(payload) // 8) + _u32(1) + bytes(payload)


def build_client_game_frame(
    payload: bytes,
    sequence: int,
    *,
    key: tuple[int, int, int, int] = XTEA_KEY,
) -> bytes:
    if not payload:
        raise ValueError("game payload must not be empty")
    if not 0 <= sequence <= 0xFFFFFFFF:
        raise ValueError("sequence out of range")
    padding_size = 8 - (len(payload) % 8) - 1
    plaintext = bytes([padding_size]) + payload + (b"\x00" * padding_size)
    ciphertext = _xtea_encrypt_blocks(plaintext, key)
    return _u16(len(ciphertext) // 8) + _u32(sequence) + ciphertext


def build_invalid_padding_frame(
    sequence: int,
    *,
    key: tuple[int, int, int, int] = XTEA_KEY,
) -> bytes:
    plaintext = b"\xFF" + (b"\x00" * 7)
    ciphertext = _xtea_encrypt_blocks(plaintext, key)
    return _u16(1) + _u32(sequence) + ciphertext


def recv_exact(connection: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        try:
            chunk = connection.recv(size - len(data))
        except socket.timeout as exc:
            raise ProbeFailure("probe-timeout") from exc
        except OSError as exc:
            raise ProbeFailure("probe-transport-error") from exc
        if not chunk:
            raise ProbeFailure("probe-connection-closed")
        data.extend(chunk)
    return bytes(data)


def read_wire_frame(connection: socket.socket) -> bytes:
    header = recv_exact(connection, 2)
    block_count = int.from_bytes(header, "little")
    if block_count == 0:
        raise ProbeFailure("server-frame-zero-blocks")
    body_size = (block_count * 8) + 4
    if body_size > MAX_RESPONSE_BYTES:
        raise ProbeFailure("server-frame-too-large")
    return header + recv_exact(connection, body_size)


def decode_game_challenge(packet: bytes) -> GameChallenge:
    if len(packet) != 14:
        raise ProbeFailure("challenge-length-mismatch")
    block_count = int.from_bytes(packet[:2], "little")
    if block_count != 1:
        raise ProbeFailure("challenge-block-count-mismatch")
    received_checksum = int.from_bytes(packet[2:6], "little")
    body = packet[6:]
    if (zlib.adler32(body) & 0xFFFFFFFF) != received_checksum:
        raise ProbeFailure("challenge-checksum-mismatch")
    if len(body) != 8 or body[0] != 0x01 or body[1] != 0x1F or body[7] != 0x71:
        raise ProbeFailure("challenge-shape-mismatch")
    return GameChallenge(
        timestamp=int.from_bytes(body[2:6], "little"),
        random=body[6],
        packet_sha256=_sha256_bytes(packet),
    )


def decode_server_game_frame(
    packet: bytes,
    *,
    key: tuple[int, int, int, int] = XTEA_KEY,
) -> DecodedGameFrame:
    if len(packet) < 14:
        raise ProbeFailure("server-frame-too-short")
    block_count = int.from_bytes(packet[:2], "little")
    ciphertext_size = block_count * 8
    if block_count == 0 or len(packet) != 2 + 4 + ciphertext_size:
        raise ProbeFailure("server-frame-length-mismatch")
    raw_sequence = int.from_bytes(packet[2:6], "little")
    compressed = bool(raw_sequence & 0x80000000)
    sequence = raw_sequence & 0x7FFFFFFF
    if sequence == 0:
        raise ProbeFailure("server-frame-zero-sequence")
    plaintext = _xtea_decrypt_blocks(packet[6:], key)
    padding_size = plaintext[0]
    if padding_size > len(plaintext) - 1:
        raise ProbeFailure("server-frame-padding-invalid")
    body_end = len(plaintext) - padding_size
    payload = plaintext[1:body_end]
    if not payload:
        raise ProbeFailure("server-frame-empty-payload")
    if compressed:
        try:
            payload = zlib.decompress(payload, wbits=-15)
        except zlib.error as exc:
            raise ProbeFailure("server-frame-compression-invalid") from exc
        if not payload:
            raise ProbeFailure("server-frame-empty-compressed-payload")
    return DecodedGameFrame(
        sequence=sequence,
        compressed=compressed,
        payload=payload,
        packet_sha256=_sha256_bytes(packet),
    )


def require_non_auth_error_frame(frame: DecodedGameFrame) -> None:
    if frame.payload and frame.payload[0] == AUTH_ERROR_OPCODE:
        raise ProbeFailure("game-authentication-rejected")


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
    runner_path: Path,
    case_results: list[dict[str, Any]],
    fatal_findings: list[dict[str, str]],
    status: str,
    failure: str | None,
) -> dict[str, Any]:
    provider_paths = (Path(__file__).resolve(), runner_path.resolve(), RUNTIME_PROVIDER.resolve())
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
        "runtime": {"host": context.host, "game_port": int(context.game_port)},
        "evidence": {
            "binary_sha256": _sha256_file(Path(context.binary_path)),
            "provider_sha256": dict(sorted(provider_hashes.items())),
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
    parser = argparse.ArgumentParser(description="Run bounded authenticated game-session transport probes against disposable Canary.")
    parser.add_argument("--binary-path", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--authorized-repository", required=True)
    parser.add_argument("--artifact-dir", default="artifacts/security-game-session")
    parser.add_argument("--db-port", type=int, default=3306)
    parser.add_argument("--db-password", default="root")
    parser.add_argument("--db-name", default="canary_security_game_session")
    parser.add_argument("--login-port", type=int, default=7471)
    parser.add_argument("--game-port", type=int, default=7472)
    parser.add_argument("--status-port", type=int, default=7473)
    parser.add_argument("--startup-timeout-seconds", type=int, default=420)
    parser.add_argument("--probe-timeout-seconds", type=_bounded_timeout, default=3.0)
    return parser.parse_args()
