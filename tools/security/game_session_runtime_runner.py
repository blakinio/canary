#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import ipaddress
import select
import socket
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = REPO_ROOT / "tools" / "security" / "game_session_runtime.py"
FIRST_SESSION_SOURCE_HOST = 80


def _load_core() -> ModuleType:
    spec = importlib.util.spec_from_file_location("game_session_runtime_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load game-session core: {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = _load_core()


def _require_loopback_source(source_ip: str) -> None:
    try:
        address = ipaddress.ip_address(source_ip)
    except ValueError as exc:
        raise core.ProbeFailure("source-not-literal-ip") from exc
    if address.version != 4 or not address.is_loopback:
        raise core.ProbeFailure("source-not-loopback")


def source_ips_for_case(case_index: int) -> tuple[str, str]:
    if not 0 <= case_index < core.MAX_CASES:
        raise core.ProbeFailure("source-index-out-of-range")
    case_host = FIRST_SESSION_SOURCE_HOST + (case_index * 2)
    case_source_ip = f"127.0.0.{case_host}"
    control_source_ip = f"127.0.0.{case_host + 1}"
    _require_loopback_source(case_source_ip)
    _require_loopback_source(control_source_ip)
    return case_source_ip, control_source_ip


def _connect_from_source(host: str, port: int, timeout_seconds: float, source_ip: str) -> socket.socket:
    core._require_loopback_target(host, port)
    _require_loopback_source(source_ip)
    try:
        connection = socket.create_connection(
            (host, port),
            timeout=timeout_seconds,
            source_address=(source_ip, 0),
        )
    except OSError as exc:
        raise core.ProbeFailure("probe-connect-failed") from exc
    connection.settimeout(timeout_seconds)
    return connection


def _frame_evidence(frame: Any) -> dict[str, Any]:
    return {
        "packet_sha256": frame.packet_sha256,
        "sequence": frame.sequence,
        "compressed": frame.compressed,
        "payload_sha256": core._sha256_bytes(frame.payload),
        "payload_size": len(frame.payload),
    }


def _read_server_frame(connection: socket.socket) -> Any:
    packet = core.read_wire_frame(connection)
    frame = core.decode_server_game_frame(packet)
    core.require_non_auth_error_frame(frame)
    return frame


def _drain_available_frames(connection: socket.socket, *, max_frames: int = 32) -> list[Any]:
    drained: list[Any] = []
    for _ in range(max_frames):
        readable, _, _ = select.select([connection], [], [], 0.05)
        if not readable:
            break
        drained.append(_read_server_frame(connection))
    return drained


def _send_ping_and_require_response(connection: socket.socket, sequence: int) -> tuple[bytes, Any]:
    packet = core.build_client_game_frame(bytes([core.PING_OPCODE]), sequence)
    try:
        connection.sendall(packet)
    except OSError as exc:
        raise core.ProbeFailure("probe-send-failed") from exc
    frame = _read_server_frame(connection)
    return packet, frame


def _establish_authenticated_session(
    context: Any,
    *,
    source_ip: str,
    fixture: tuple[str, str, str, str],
    timeout_seconds: float,
) -> tuple[socket.socket, dict[str, Any], int]:
    fixture_id, account_descriptor, password, character_name = fixture
    connection = _connect_from_source(context.host, int(context.game_port), timeout_seconds, source_ip)
    try:
        challenge_packet = core.read_wire_frame(connection)
        challenge = core.decode_game_challenge(challenge_packet)
        login_packet = core.build_game_login_packet(
            account_descriptor,
            password,
            character_name,
            challenge,
        )
        connection.sendall(login_packet)
        initial_frame = _read_server_frame(connection)
        time.sleep(0.25)
        drained = _drain_available_frames(connection)

        # The first game-login packet uses the pre-XTEA Adler32 envelope and is
        # not part of the post-login client sequence. ProtocolGame therefore
        # expects sequence 1 for the first XTEA-protected client packet.
        baseline_packet, baseline_response = _send_ping_and_require_response(connection, 1)
        evidence = {
            "fixture_id": fixture_id,
            "source_ip": source_ip,
            "challenge_packet_sha256": challenge.packet_sha256,
            "login_packet_sha256": core._sha256_bytes(login_packet),
            "login_packet_size": len(login_packet),
            "initial_server_frame": _frame_evidence(initial_frame),
            "drained_login_frame_count": len(drained),
            "baseline_ping": {
                "sequence": 1,
                "packet_sha256": core._sha256_bytes(baseline_packet),
                "packet_size": len(baseline_packet),
                "response": _frame_evidence(baseline_response),
            },
        }
        return connection, evidence, 2
    except Exception:
        connection.close()
        raise


def _run_case_action(connection: socket.socket, case_id: str, expected_sequence: int) -> dict[str, Any]:
    result: dict[str, Any] = {"expected_sequence_before_case": expected_sequence}

    if case_id == core.CASE_AUTHENTICATED_CONTROL:
        packet, response = _send_ping_and_require_response(connection, expected_sequence)
        result.update(
            {
                "action": "valid-ping",
                "probe_packet_sha256": core._sha256_bytes(packet),
                "probe_packet_size": len(packet),
                "probe_sequence": expected_sequence,
                "recovery_sequence": expected_sequence,
                "recovery_response": _frame_evidence(response),
            }
        )
        return result

    if case_id == core.CASE_ZERO_SEQUENCE:
        malformed = core.build_client_game_frame(bytes([core.PING_OPCODE]), 0)
        recovery_sequence = expected_sequence
    elif case_id == core.CASE_SEQUENCE_GAP:
        malformed = core.build_client_game_frame(bytes([core.PING_OPCODE]), expected_sequence + 1)
        recovery_sequence = expected_sequence
    elif case_id == core.CASE_SEQUENCE_REPLAY:
        accepted_packet, accepted_response = _send_ping_and_require_response(connection, expected_sequence)
        result["accepted_before_replay"] = {
            "sequence": expected_sequence,
            "packet_sha256": core._sha256_bytes(accepted_packet),
            "packet_size": len(accepted_packet),
            "response": _frame_evidence(accepted_response),
        }
        malformed = accepted_packet
        recovery_sequence = expected_sequence + 1
    elif case_id == core.CASE_INVALID_XTEA_PADDING:
        malformed = core.build_invalid_padding_frame(expected_sequence)
        recovery_sequence = expected_sequence
    else:
        raise core.ProbeFailure("unknown-case")

    try:
        connection.sendall(malformed)
    except OSError as exc:
        raise core.ProbeFailure("malformed-probe-send-failed") from exc

    recovery_packet, recovery_response = _send_ping_and_require_response(connection, recovery_sequence)
    result.update(
        {
            "action": "rejection-then-recovery",
            "malformed_packet_sha256": core._sha256_bytes(malformed),
            "malformed_packet_size": len(malformed),
            "recovery_sequence": recovery_sequence,
            "recovery_packet_sha256": core._sha256_bytes(recovery_packet),
            "recovery_packet_size": len(recovery_packet),
            "recovery_response": _frame_evidence(recovery_response),
        }
    )
    return result


def _run_fresh_control_session(
    context: Any,
    *,
    source_ip: str,
    fixture: tuple[str, str, str, str],
    timeout_seconds: float,
) -> dict[str, Any]:
    connection, session_evidence, next_sequence = _establish_authenticated_session(
        context,
        source_ip=source_ip,
        fixture=fixture,
        timeout_seconds=timeout_seconds,
    )
    try:
        packet, response = _send_ping_and_require_response(connection, next_sequence)
        return {
            "session": session_evidence,
            "control_ping": {
                "sequence": next_sequence,
                "packet_sha256": core._sha256_bytes(packet),
                "packet_size": len(packet),
                "response": _frame_evidence(response),
            },
        }
    finally:
        connection.close()


def execute_plan(plan_path: Path, plan: dict[str, Any], context: Any, *, timeout_seconds: float) -> int:
    core._require_loopback_target(context.host, int(context.game_port))
    report_path = Path(context.artifact_dir) / "game-session-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    plan_sha256 = core._sha256_file(plan_path)
    case_results: list[dict[str, Any]] = []
    failure: str | None = None

    for case_index, case_id in enumerate(plan["cases"]):
        case_source_ip, control_source_ip = source_ips_for_case(case_index)
        case_fixture = core.FIXTURES[case_index * 2]
        control_fixture = core.FIXTURES[(case_index * 2) + 1]
        result: dict[str, Any] = {
            "id": case_id,
            "case_source_ip": case_source_ip,
            "control_source_ip": control_source_ip,
            "case_probe": "pending",
            "control_probe": "pending",
        }
        case_results.append(result)

        connection: socket.socket | None = None
        case_failure: str | None = None
        try:
            connection, session_evidence, next_sequence = _establish_authenticated_session(
                context,
                source_ip=case_source_ip,
                fixture=case_fixture,
                timeout_seconds=timeout_seconds,
            )
            result["session"] = session_evidence
            result["case_action"] = _run_case_action(connection, case_id, next_sequence)
            result["case_probe"] = "pass"
        except core.ProbeFailure as exc:
            case_failure = exc.code
            result["case_probe"] = "fail"
            result["case_failure"] = exc.code
        except OSError:
            case_failure = "case-transport-error"
            result["case_probe"] = "fail"
            result["case_failure"] = case_failure
        finally:
            if connection is not None:
                connection.close()

        control_failure: str | None = None
        try:
            result["control"] = _run_fresh_control_session(
                context,
                source_ip=control_source_ip,
                fixture=control_fixture,
                timeout_seconds=timeout_seconds,
            )
            result["control_probe"] = "pass"
        except core.ProbeFailure as exc:
            control_failure = exc.code
            result["control_probe"] = "fail"
            result["control_failure"] = exc.code
        except OSError:
            control_failure = "control-transport-error"
            result["control_probe"] = "fail"
            result["control_failure"] = control_failure

        if case_failure is not None:
            failure = f"{case_id}:{case_failure}"
            break
        if control_failure is not None:
            failure = f"{case_id}:control:{control_failure}"
            break

    fatal_findings = core.scan_fatal_logs(Path(context.stdout_path), Path(context.stderr_path))
    if failure is None and fatal_findings:
        failure = "fatal-log-signature"

    status = "success" if failure is None else "failure"
    report = core.build_report(
        plan=plan,
        plan_sha256=plan_sha256,
        context=context,
        runner_path=Path(__file__),
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

    runtime_spec = importlib.util.spec_from_file_location(
        "security_game_session_runtime_provider", core.RUNTIME_PROVIDER
    )
    if runtime_spec is None or runtime_spec.loader is None:
        print(f"ERROR: cannot load runtime provider: {core.RUNTIME_PROVIDER}", file=sys.stderr)
        return 2
    runtime_module = importlib.util.module_from_spec(runtime_spec)
    sys.modules[runtime_spec.name] = runtime_module
    runtime_spec.loader.exec_module(runtime_module)

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

    return runtime_module.run_runtime(
        runtime_args,
        executor,
        operation_name="game-session-security",
        exit_code_field="security_driver_exit_code",
    )


if __name__ == "__main__":
    raise SystemExit(main())
