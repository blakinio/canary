#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import ipaddress
import socket
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = REPO_ROOT / "tools" / "security" / "malformed_packet_runtime.py"
CONTROL_PROBE_ATTEMPTS = 4
CONTROL_PROBE_RETRY_DELAY_SECONDS = 0.05
FIRST_CASE_SOURCE_HOST = 2


def _load_core() -> ModuleType:
    spec = importlib.util.spec_from_file_location("malformed_packet_runtime_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load malformed packet core: {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = _load_core()


def source_ip_for_case(case_index: int) -> str:
    if not 0 <= case_index < core.MAX_CASES:
        raise core.ProbeFailure("source-index-out-of-range")
    source_ip = f"127.0.0.{FIRST_CASE_SOURCE_HOST + case_index}"
    address = ipaddress.ip_address(source_ip)
    if not address.is_loopback:
        raise core.ProbeFailure("source-not-loopback")
    return source_ip


def probe_malformed_case_from_source(
    case: Any,
    host: str,
    port: int,
    timeout_seconds: float,
    source_ip: str,
) -> None:
    core._require_loopback_target(host, port)
    if not ipaddress.ip_address(source_ip).is_loopback:
        raise core.ProbeFailure("source-not-loopback")
    try:
        connection = socket.create_connection(
            (host, port),
            timeout=timeout_seconds,
            source_address=(source_ip, 0),
        )
    except OSError as exc:
        raise core.ProbeFailure("malformed-connect-failed") from exc
    with connection:
        connection.settimeout(timeout_seconds)
        try:
            connection.sendall(case.payload)
            if case.half_close_write:
                connection.shutdown(socket.SHUT_WR)
            response = connection.recv(4096)
        except socket.timeout as exc:
            raise core.ProbeFailure("malformed-timeout") from exc
        except OSError as exc:
            if core._is_reset_error(exc):
                return
            raise core.ProbeFailure("malformed-transport-error") from exc
        if response:
            raise core.ProbeFailure("malformed-unexpected-response")


def probe_status_control_from_source(
    host: str,
    port: int,
    timeout_seconds: float,
    source_ip: str,
) -> None:
    core._require_loopback_target(host, port)
    if not ipaddress.ip_address(source_ip).is_loopback:
        raise core.ProbeFailure("source-not-loopback")
    try:
        connection = socket.create_connection(
            (host, port),
            timeout=timeout_seconds,
            source_address=(source_ip, 0),
        )
    except OSError as exc:
        raise core.ProbeFailure("control-connect-failed") from exc
    response = bytearray()
    with connection:
        connection.settimeout(timeout_seconds)
        try:
            connection.sendall(core.CONTROL_STATUS_REQUEST)
            while len(response) <= core.MAX_CONTROL_RESPONSE_BYTES:
                chunk = connection.recv(65536)
                if not chunk:
                    break
                response.extend(chunk)
        except socket.timeout as exc:
            raise core.ProbeFailure("control-timeout") from exc
        except OSError as exc:
            raise core.ProbeFailure("control-transport-error") from exc
    if len(response) > core.MAX_CONTROL_RESPONSE_BYTES:
        raise core.ProbeFailure("control-response-too-large")
    raw = bytes(response)
    if b"<tsqp" not in raw or b"<serverinfo" not in raw:
        raise core.ProbeFailure("control-invalid-response")


def probe_status_control_with_retries(
    host: str,
    port: int,
    timeout_seconds: float,
    source_ip: str,
) -> None:
    """Require canonical status recovery within a fixed code-owned retry window.

    Each parser case gets its own deterministic loopback source address. This keeps the
    malformed/control pair below Canary's normal per-IP connection-admission threshold
    without disabling or modifying that protection. Retries remain bounded so a genuinely
    unresponsive status service still fails closed.
    """

    last_failure: Exception | None = None
    for attempt in range(CONTROL_PROBE_ATTEMPTS):
        try:
            probe_status_control_from_source(host, port, timeout_seconds, source_ip)
            return
        except core.ProbeFailure as exc:
            last_failure = exc
            if attempt + 1 < CONTROL_PROBE_ATTEMPTS:
                time.sleep(CONTROL_PROBE_RETRY_DELAY_SECONDS)
    raise core.ProbeFailure("control-unresponsive") from last_failure


def build_report(**kwargs: Any) -> dict[str, Any]:
    report = core.build_report(**kwargs)
    report["evidence"]["provider_sha256"][
        str(Path(__file__).resolve().relative_to(REPO_ROOT))
    ] = core._sha256_file(Path(__file__).resolve())
    report["evidence"]["provider_sha256"] = dict(sorted(report["evidence"]["provider_sha256"].items()))
    return report


def execute_plan(
    plan_path: Path,
    plan: dict[str, Any],
    context: Any,
    *,
    timeout_seconds: float,
) -> int:
    core._require_loopback_target(context.host, int(context.status_port))
    report_path = Path(context.artifact_dir) / "malformed-packet-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    plan_sha256 = core._sha256_file(plan_path)
    case_results: list[dict[str, Any]] = []
    failure: str | None = None

    for case_index, case_id in enumerate(plan["cases"]):
        case = core.CASES[case_id]
        source_ip = source_ip_for_case(case_index)
        result: dict[str, Any] = {
            "id": case.case_id,
            "source_ip": source_ip,
            "payload_sha256": core._sha256_bytes(case.payload),
            "payload_size": len(case.payload),
            "malformed_probe": "pending",
            "control_probe": "pending",
        }
        case_results.append(result)
        try:
            probe_malformed_case_from_source(
                case,
                context.host,
                int(context.status_port),
                timeout_seconds,
                source_ip,
            )
            result["malformed_probe"] = "connection-terminated"
            probe_status_control_with_retries(
                context.host,
                int(context.status_port),
                timeout_seconds,
                source_ip,
            )
            result["control_probe"] = "pass"
        except core.ProbeFailure as exc:
            failure = f"{case.case_id}:{exc.code}"
            result["failure"] = exc.code
            break

    fatal_findings = core.scan_fatal_logs(Path(context.stdout_path), Path(context.stderr_path))
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
    report_path.write_text(core._canonical_json(report), encoding="utf-8")
    return 0 if status == "success" else 1


def main() -> int:
    args = core.parse_args()
    plan_path = Path(args.plan).resolve()
    try:
        plan = core.load_plan(plan_path, args.authorized_repository)
    except core.SecurityPlanError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    runtime = core._load_runtime_provider()
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
