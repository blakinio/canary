#!/usr/bin/env python3
from __future__ import annotations

import argparse
import errno
import hashlib
import importlib.util
import ipaddress
import json
import os
import re
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PROVIDER = REPO_ROOT / "tools" / "e2e" / "run_agent_load_runtime.py"
AUTHORIZED_REPOSITORY = "blakinio/canary"
PLAN_SCHEMA = "ots-security-malformed-packet-plan-v1"
REPORT_SCHEMA = "ots-security-malformed-packet-report-v1"
DRIVER_ID = "canary-status-parser-v1"
SERVICE_ID = "status"
MAX_CASES = 16
MAX_CONTROL_RESPONSE_BYTES = 1024 * 1024
CONTROL_STATUS_REQUEST = b"\x06\x00\xff\xffinfo"
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


class SecurityPlanError(ValueError):
    pass


class ProbeFailure(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class MalformedCase:
    case_id: str
    payload: bytes
    half_close_write: bool = False


CASES: dict[str, MalformedCase] = {
    "zero-length-frame": MalformedCase("zero-length-frame", b"\x00\x00"),
    "oversized-length-frame": MalformedCase("oversized-length-frame", b"\xff\xff"),
    "truncated-declared-body": MalformedCase("truncated-declared-body", b"\x08\x00\xff", True),
    "unknown-service-identifier": MalformedCase("unknown-service-identifier", b"\x01\x00\x7e"),
    "status-service-only": MalformedCase("status-service-only", b"\x01\x00\xff"),
    "status-opcode-only": MalformedCase("status-opcode-only", b"\x02\x00\xff\xff"),
    "status-truncated-info": MalformedCase("status-truncated-info", b"\x05\x00\xff\xffinf"),
    "status-unknown-opcode": MalformedCase("status-unknown-opcode", b"\x02\x00\xff\x7f"),
}


def _load_runtime_provider() -> ModuleType:
    spec = importlib.util.spec_from_file_location("security_runtime_provider", RUNTIME_PROVIDER)
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


def probe_malformed_case(case: MalformedCase, host: str, port: int, timeout_seconds: float) -> None:
    _require_loopback_target(host, port)
    try:
        connection = socket.create_connection((host, port), timeout=timeout_seconds)
    except OSError as exc:
        raise ProbeFailure("malformed-connect-failed") from exc
    with connection:
        connection.settimeout(timeout_seconds)
        try:
            connection.sendall(case.payload)
            if case.half_close_write:
                connection.shutdown(socket.SHUT_WR)
            response = connection.recv(4096)
        except socket.timeout as exc:
            raise ProbeFailure("malformed-timeout") from exc
        except OSError as exc:
            if _is_reset_error(exc):
                return
            raise ProbeFailure("malformed-transport-error") from exc
        if response:
            raise ProbeFailure("malformed-unexpected-response")


def probe_status_control(host: str, port: int, timeout_seconds: float) -> None:
    _require_loopback_target(host, port)
    try:
        connection = socket.create_connection((host, port), timeout=timeout_seconds)
    except OSError as exc:
        raise ProbeFailure("control-connect-failed") from exc
    response = bytearray()
    with connection:
        connection.settimeout(timeout_seconds)
        try:
            connection.sendall(CONTROL_STATUS_REQUEST)
            while len(response) <= MAX_CONTROL_RESPONSE_BYTES:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                response.extend(chunk)
        except socket.timeout as exc:
            raise ProbeFailure("control-timeout") from exc
        except OSError as exc:
            raise ProbeFailure("control-transport-error") from exc
    if len(response) > MAX_CONTROL_RESPONSE_BYTES:
        raise ProbeFailure("control-response-too-large")
    raw = bytes(response)
    if b"<tsqp" not in raw or b"<serverinfo" not in raw:
        raise ProbeFailure("control-invalid-response")


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
    provider_paths = (
        Path(__file__).resolve(),
        RUNTIME_PROVIDER.resolve(),
    )
    provider_hashes = {
        str(path.relative_to(REPO_ROOT)): _sha256_file(path)
        for path in provider_paths
    }
    report: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "status": status,
        "plan": {"id": plan["id"], "sha256": plan_sha256},
        "authorization": {"repository": AUTHORIZED_REPOSITORY},
        "driver": DRIVER_ID,
        "service": SERVICE_ID,
        "runtime": {"host": context.host, "status_port": int(context.status_port)},
        "evidence": {
            "binary_sha256": _sha256_file(Path(context.binary_path)),
            "provider_sha256": provider_hashes,
        },
        "cases": case_results,
        "fatal_log_findings": fatal_findings,
        "failure": failure,
    }
    return report


def execute_plan(
    plan_path: Path,
    plan: dict[str, Any],
    context: Any,
    *,
    timeout_seconds: float,
) -> int:
    _require_loopback_target(context.host, int(context.status_port))
    report_path = Path(context.artifact_dir) / "malformed-packet-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    plan_sha256 = _sha256_file(plan_path)
    case_results: list[dict[str, Any]] = []
    failure: str | None = None

    for case_id in plan["cases"]:
        case = CASES[case_id]
        result: dict[str, Any] = {
            "id": case.case_id,
            "payload_sha256": _sha256_bytes(case.payload),
            "payload_size": len(case.payload),
            "malformed_probe": "pending",
            "control_probe": "pending",
        }
        case_results.append(result)
        try:
            probe_malformed_case(case, context.host, int(context.status_port), timeout_seconds)
            result["malformed_probe"] = "connection-terminated"
            probe_status_control(context.host, int(context.status_port), timeout_seconds)
            result["control_probe"] = "pass"
        except ProbeFailure as exc:
            failure = f"{case.case_id}:{exc.code}"
            result["failure"] = exc.code
            break

    fatal_findings = scan_fatal_logs(Path(context.stdout_path), Path(context.stderr_path))
    if failure is None and fatal_findings:
        failure = "fatal-log-signature"

    status = "success" if failure is None else "failure"
    report = build_report(
        plan=plan,
        plan_sha256=plan_sha256,
        context=context,
        case_results=case_results,
        fatal_findings=fatal_findings,
        status=status,
        failure=failure,
    )
    report_path.write_text(_canonical_json(report), encoding="utf-8")
    return 0 if status == "success" else 1


def _bounded_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be numeric") from exc
    if not 0.1 <= timeout <= 10.0:
        raise argparse.ArgumentTypeError("timeout must be between 0.1 and 10 seconds")
    return timeout


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bounded malformed status-parser probes against disposable Canary.")
    parser.add_argument("--binary-path", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--authorized-repository", required=True)
    parser.add_argument("--artifact-dir", default="artifacts/security-malformed-packets")
    parser.add_argument("--db-port", type=_port, default=3306)
    parser.add_argument("--db-password", default="root")
    parser.add_argument("--db-name", default="canary_security_runtime")
    parser.add_argument("--login-port", type=_port, default=7471)
    parser.add_argument("--game-port", type=_port, default=7472)
    parser.add_argument("--status-port", type=_port, default=7473)
    parser.add_argument("--startup-timeout-seconds", type=int, default=420)
    parser.add_argument("--probe-timeout-seconds", type=_bounded_timeout, default=2.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan_path = Path(args.plan).resolve()
    try:
        plan = load_plan(plan_path, args.authorized_repository)
    except SecurityPlanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    runtime = _load_runtime_provider()
    runtime_args = argparse.Namespace(
        binary_path=args.binary_path,
        artifact_dir=args.artifact_dir,
        data_pack="data-canary",
        map_name="canary",
        map_download_url="",
        map_cache_path="",
        db_host="127.0.0.1",
        db_port=args.db_port,
        db_user="root",
        db_password=args.db_password,
        db_name=args.db_name,
        skip_database_init=False,
        login_port=args.login_port,
        game_port=args.game_port,
        status_port=args.status_port,
        startup_timeout_seconds=args.startup_timeout_seconds,
    )

    def executor(context: Any) -> int:
        return execute_plan(plan_path, plan, context, timeout_seconds=args.probe_timeout_seconds)

    return runtime.run_runtime(
        runtime_args,
        executor,
        operation_name="malformed-packet-security",
        exit_code_field="security_driver_exit_code",
    )


if __name__ == "__main__":
    raise SystemExit(main())
