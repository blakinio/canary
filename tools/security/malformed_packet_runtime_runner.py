#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = REPO_ROOT / "tools" / "security" / "malformed_packet_runtime.py"
CONTROL_PROBE_ATTEMPTS = 4
CONTROL_PROBE_RETRY_DELAY_SECONDS = 0.05


def _load_core() -> ModuleType:
    spec = importlib.util.spec_from_file_location("malformed_packet_runtime_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load malformed packet core: {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = _load_core()


def probe_status_control_with_retries(host: str, port: int, timeout_seconds: float) -> None:
    """Require canonical status recovery within a fixed code-owned retry window."""

    last_failure: Exception | None = None
    for attempt in range(CONTROL_PROBE_ATTEMPTS):
        try:
            core.probe_status_control(host, port, timeout_seconds)
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

    for case_id in plan["cases"]:
        case = core.CASES[case_id]
        result: dict[str, Any] = {
            "id": case.case_id,
            "payload_sha256": core._sha256_bytes(case.payload),
            "payload_size": len(case.payload),
            "malformed_probe": "pending",
            "control_probe": "pending",
        }
        case_results.append(result)
        try:
            core.probe_malformed_case(case, context.host, int(context.status_port), timeout_seconds)
            result["malformed_probe"] = "connection-terminated"
            probe_status_control_with_retries(context.host, int(context.status_port), timeout_seconds)
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
