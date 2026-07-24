#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

CONTRACT = "canary-universal-e2e-cleanup-certification-v1"
SCHEMA_VERSION = 1
RESULT_NAME = "cleanup-certification.json"
BASELINE_NAME = "cleanup-baseline.json"
CHECK_STATES = {"pass", "fail", "not-applicable", "unknown"}
PID_RE = re.compile(r"^[1-9][0-9]{0,9}$")
MARKERS = (
    ".agent-e2e-restart-request",
    ".agent-e2e-fault-injection",
    ".agent-e2e-cleanup-pending",
)


class CleanupCertificationError(ValueError):
    pass


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_state(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        return {"exists": True, "kind": "symlink", "target": os.readlink(path)}
    if path.is_file():
        return {
            "exists": True,
            "kind": "file",
            "sha256": _sha256(path),
            "size": path.stat().st_size,
        }
    if path.is_dir():
        return {"exists": True, "kind": "directory"}
    return {"exists": False, "kind": "missing"}


def capture_baseline(
    *, artifact_dir: Path, repo_root: Path, otclient_root: Path
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    repo_root = repo_root.resolve()
    otclient_root = otclient_root.resolve()
    files = {
        "repo_config": {
            "root": "repo",
            "path": "config.lua",
            "state": _file_state(repo_root / "config.lua"),
        },
        "otclientrc": {
            "root": "otclient",
            "path": "otclientrc.lua",
            "state": _file_state(otclient_root / "otclientrc.lua"),
        },
        "otclient_init": {
            "root": "otclient",
            "path": "init.lua",
            "state": _file_state(otclient_root / "init.lua"),
        },
    }
    payload = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT,
        "files": files,
        "markers": {name: _file_state(repo_root / name) for name in MARKERS},
    }
    _write_json(artifact_dir / BASELINE_NAME, payload)
    return payload


def _check(
    check_id: str,
    state: str,
    *,
    required: bool = True,
    expected: Any = None,
    observed: Any = None,
    evidence: Any = None,
) -> dict[str, Any]:
    if state not in CHECK_STATES:
        raise CleanupCertificationError(f"invalid check state: {state}")
    return {
        "id": check_id,
        "required": required,
        "status": state,
        "expected": expected,
        "observed": observed,
        "evidence": evidence,
    }


def _read_pid(path: Path) -> tuple[int | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None, "missing"
    if not PID_RE.fullmatch(text):
        return None, "invalid"
    return int(text), None


def _alive(pid: int, proc_root: Path) -> bool:
    return (proc_root / str(pid)).exists()


def _pg_members(pgid: int, proc_root: Path, excluded: Iterable[int]) -> list[int]:
    result: list[int] = []
    excluded_set = set(excluded)
    if pgid <= 0 or not proc_root.is_dir():
        return result
    for entry in proc_root.iterdir():
        if not entry.name.isdigit() or int(entry.name) in excluded_set:
            continue
        try:
            raw = (entry / "stat").read_text(encoding="utf-8")
            tail = raw[raw.rfind(")") + 2 :].split()
            entry_pgid = int(tail[2])
        except (OSError, ValueError, IndexError):
            continue
        if entry_pgid == pgid:
            result.append(int(entry.name))
    return sorted(result)


def reap_process_group(
    pgid: int,
    proc_root: Path = Path("/proc"),
    *,
    killpg: Callable[[int, int], None] = os.killpg,
    sleep: Callable[[float], None] = time.sleep,
    term_attempts: int = 50,
    kill_attempts: int = 20,
) -> dict[str, Any]:
    excluded = {os.getpid(), os.getppid()}
    before = _pg_members(pgid, proc_root, excluded)
    signals: list[str] = []
    errors: list[str] = []
    remaining = before
    if remaining:
        try:
            killpg(pgid, signal.SIGTERM)
            signals.append("SIGTERM")
        except ProcessLookupError:
            remaining = []
        except OSError as exc:
            errors.append(f"SIGTERM:{exc.__class__.__name__}")
        for _ in range(term_attempts):
            remaining = _pg_members(pgid, proc_root, excluded)
            if not remaining:
                break
            sleep(0.1)
    if remaining:
        try:
            killpg(pgid, signal.SIGKILL)
            signals.append("SIGKILL")
        except ProcessLookupError:
            remaining = []
        except OSError as exc:
            errors.append(f"SIGKILL:{exc.__class__.__name__}")
        for _ in range(kill_attempts):
            remaining = _pg_members(pgid, proc_root, excluded)
            if not remaining:
                break
            sleep(0.1)
    return {
        "pgid": pgid,
        "members_before": before,
        "signals": signals,
        "members_after": _pg_members(pgid, proc_root, excluded),
        "errors": errors,
    }


def _secondary_ids(manifest: Mapping[str, Any]) -> list[str]:
    scenario = manifest.get("scenario") if isinstance(manifest, Mapping) else None
    multi = scenario.get("multi_client") if isinstance(scenario, Mapping) else None
    secondary = multi.get("secondary") if isinstance(multi, Mapping) else None
    actor_id = secondary.get("id") if isinstance(secondary, Mapping) else None
    return (
        [actor_id]
        if isinstance(actor_id, str)
        and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", actor_id)
        else []
    )


def _process_checks(
    artifact_dir: Path,
    lifecycle_pid: int,
    lifecycle_pgid: int,
    proc_root: Path,
) -> list[dict[str, Any]]:
    members = _pg_members(lifecycle_pgid, proc_root, {os.getpid(), os.getppid()})
    lifecycle_alive = _alive(lifecycle_pid, proc_root)
    checks = [
        _check(
            "runner_process_group_empty",
            "pass" if not members else "fail",
            expected=[],
            observed=members,
            evidence={"pgid": lifecycle_pgid},
        ),
        _check(
            "lifecycle_process_stopped",
            "pass" if not lifecycle_alive else "fail",
            expected=False,
            observed=lifecycle_alive,
            evidence={"pid": lifecycle_pid},
        ),
    ]
    resources = {
        "primary_client": (
            "otclient.pid",
            (
                "client-events.tsv",
                "otclient.stdout.log",
                "otclient.stderr.log",
                "otclient-exit-code.txt",
            ),
        ),
        "canary": ("canary.pid", ("canary.stdout.log", "canary.stderr.log")),
        "xvfb": ("xvfb.pid", ("xvfb.log",)),
        "tcpdump": (
            "tcpdump.pid",
            ("game-port-7172.pcap", "tcpdump.stderr.log"),
        ),
    }
    for name, (pid_name, activity) in resources.items():
        pid_path = artifact_dir / pid_name
        pid, error = _read_pid(pid_path)
        expected = any((artifact_dir / item).exists() for item in activity)
        if error == "missing":
            checks.append(
                _check(
                    f"process_stopped:{name}",
                    "fail" if expected else "not-applicable",
                    required=expected,
                    expected="valid stopped pid" if expected else None,
                    observed="missing",
                    evidence=pid_name,
                )
            )
        elif error or pid is None:
            checks.append(
                _check(
                    f"process_stopped:{name}",
                    "fail",
                    expected="valid stopped pid",
                    observed="invalid",
                    evidence=pid_name,
                )
            )
        else:
            alive = _alive(pid, proc_root)
            checks.append(
                _check(
                    f"process_stopped:{name}",
                    "pass" if not alive else "fail",
                    expected=False,
                    observed=alive,
                    evidence={"path": pid_name, "pid": pid},
                )
            )

    primary_pid_present = (artifact_dir / "otclient.pid").exists()
    primary_exit = (artifact_dir / "otclient-exit-code.txt").is_file()
    checks.append(
        _check(
            "primary_client_exit_evidence",
            "pass"
            if primary_exit
            else ("fail" if primary_pid_present else "not-applicable"),
            required=primary_pid_present,
            expected=True if primary_pid_present else None,
            observed=primary_exit,
            evidence="otclient-exit-code.txt",
        )
    )

    manifest = _read_json(artifact_dir / "scenario-manifest.json", {})
    for actor_id in _secondary_ids(
        manifest if isinstance(manifest, Mapping) else {}
    ):
        root = artifact_dir / "actors" / actor_id
        pid, error = _read_pid(root / "otclient.pid")
        stopped = error is None and pid is not None and not _alive(pid, proc_root)
        exit_exists = (root / "otclient-exit-code.txt").is_file()
        checks.append(
            _check(
                f"secondary_client_stopped:{actor_id}",
                "pass" if stopped else "fail",
                expected=True,
                observed=stopped,
                evidence=f"actors/{actor_id}/otclient.pid",
            )
        )
        checks.append(
            _check(
                f"secondary_client_exit_evidence:{actor_id}",
                "pass" if exit_exists else "fail",
                expected=True,
                observed=exit_exists,
                evidence=f"actors/{actor_id}/otclient-exit-code.txt",
            )
        )
    return checks


def _workspace_checks(
    artifact_dir: Path, repo_root: Path, otclient_root: Path
) -> list[dict[str, Any]]:
    baseline = _read_json(artifact_dir / BASELINE_NAME, {})
    files = baseline.get("files") if isinstance(baseline, Mapping) else None
    if not isinstance(files, Mapping):
        return [
            _check(
                "workspace_baseline_available",
                "fail",
                expected=True,
                observed=False,
                evidence=BASELINE_NAME,
            )
        ]
    roots = {"repo": repo_root, "otclient": otclient_root}
    checks = [
        _check(
            "workspace_baseline_available",
            "pass",
            expected=True,
            observed=True,
            evidence=BASELINE_NAME,
        )
    ]
    for name, raw in sorted(files.items()):
        entry = raw if isinstance(raw, Mapping) else {}
        root = roots.get(entry.get("root"))
        relative = entry.get("path")
        relative_path = Path(relative) if isinstance(relative, str) else None
        path = (
            root / relative_path
            if root is not None
            and relative_path is not None
            and relative
            and not relative_path.is_absolute()
            and ".." not in relative_path.parts
            else None
        )
        expected = entry.get("state")
        observed = _file_state(path) if path else None
        checks.append(
            _check(
                f"workspace_restore:{name}",
                "pass" if observed == expected else "fail",
                expected=expected,
                observed=observed,
                evidence=relative,
            )
        )
    for marker in MARKERS:
        observed = _file_state(repo_root / marker)
        checks.append(
            _check(
                f"temporary_marker:{marker}",
                "pass" if not observed["exists"] else "fail",
                expected={"exists": False},
                observed=observed,
                evidence=marker,
            )
        )
    return checks


def _run_scalar(
    command: Sequence[str], query: str, env: Mapping[str, str]
) -> tuple[int, str, str]:
    completed = subprocess.run(
        [*command, "-N", "-s", "-e", query],
        env=dict(env),
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def _db_checks(
    artifact_dir: Path,
    command: Sequence[str],
    env: Mapping[str, str],
    runner: Callable[
        [Sequence[str], str, Mapping[str, str]], tuple[int, str, str]
    ]
    | None,
) -> list[dict[str, Any]]:
    execute = runner or _run_scalar
    checks: list[dict[str, Any]] = []
    fixed = (
        ("players_online_zero", "SELECT COUNT(*) FROM players_online"),
        (
            "active_test_db_transactions_zero",
            "SELECT COUNT(*) FROM information_schema.innodb_trx "
            "WHERE trx_mysql_thread_id <> CONNECTION_ID()",
        ),
    )
    for check_id, query in fixed:
        code, stdout, stderr = execute(command, query, env)
        checks.append(
            _check(
                check_id,
                "pass" if code == 0 and stdout == "0" else "fail",
                expected="0",
                observed={
                    "returncode": code,
                    "stdout": stdout,
                    "stderr": stderr[:512],
                },
                evidence={"query_id": check_id},
            )
        )

    manifest = _read_json(artifact_dir / "scenario-manifest.json", {})
    scenario = manifest.get("scenario") if isinstance(manifest, Mapping) else None
    fixture = scenario.get("fixture") if isinstance(scenario, Mapping) else None
    multi = scenario.get("multi_client") if isinstance(scenario, Mapping) else None
    secondary = multi.get("secondary") if isinstance(multi, Mapping) else None
    characters = sorted(
        {
            value
            for value in (
                fixture.get("character") if isinstance(fixture, Mapping) else None,
                secondary.get("character")
                if isinstance(secondary, Mapping)
                else None,
            )
            if isinstance(value, str) and value
        }
    )
    if not characters:
        checks.append(
            _check(
                "declared_fixture_ghost_sessions_zero",
                "not-applicable",
                required=False,
                expected="declared fixture character",
                observed=None,
                evidence="scenario-manifest.json",
            )
        )
    else:
        quoted = ",".join(
            "'" + value.replace("'", "''") + "'" for value in characters
        )
        query = (
            "SELECT COUNT(*) FROM players_online po "
            "JOIN players p ON p.id=po.player_id "
            f"WHERE p.name IN ({quoted})"
        )
        code, stdout, stderr = execute(command, query, env)
        checks.append(
            _check(
                "declared_fixture_ghost_sessions_zero",
                "pass" if code == 0 and stdout == "0" else "fail",
                expected="0",
                observed={
                    "returncode": code,
                    "stdout": stdout,
                    "stderr": stderr[:512],
                },
                evidence={"characters": characters},
            )
        )
    return checks


def validate_report(report: Mapping[str, Any]) -> None:
    if (
        report.get("schema_version") != SCHEMA_VERSION
        or report.get("contract") != CONTRACT
    ):
        raise CleanupCertificationError("unsupported cleanup contract or schema")
    if report.get("status") not in {
        "certified",
        "partial",
        "failed",
    } or not isinstance(report.get("cleanup_certified"), bool):
        raise CleanupCertificationError("invalid cleanup status")
    process_group_cleanup = report.get("process_group_cleanup")
    if (
        not isinstance(process_group_cleanup, Mapping)
        or not isinstance(process_group_cleanup.get("members_before"), list)
        or not isinstance(process_group_cleanup.get("members_after"), list)
    ):
        raise CleanupCertificationError("process group cleanup evidence is missing")
    checks = report.get("checks")
    if not isinstance(checks, list) or not checks:
        raise CleanupCertificationError("checks must be a non-empty list")
    ids: set[str] = set()
    for item in checks:
        if (
            not isinstance(item, Mapping)
            or not isinstance(item.get("id"), str)
            or not item.get("id")
            or item.get("id") in ids
        ):
            raise CleanupCertificationError(
                "check ids must be unique non-empty strings"
            )
        ids.add(item["id"])
        if item.get("status") not in CHECK_STATES or not isinstance(
            item.get("required"), bool
        ):
            raise CleanupCertificationError(f"invalid check {item['id']}")
    all_required = all(
        item["status"] == "pass" for item in checks if item["required"]
    )
    if report["cleanup_certified"] != all_required or report[
        "cleanup_certified"
    ] != (report["status"] == "certified"):
        raise CleanupCertificationError(
            "cleanup certification is inconsistent with required checks"
        )


def _merge_summary(artifact_dir: Path, report: Mapping[str, Any]) -> None:
    path = artifact_dir / "result.json"
    result = _read_json(path, {})
    if not isinstance(result, dict):
        result = {}
    if result.get("contract") == "canary-universal-e2e-result-envelope-v1" and isinstance(
        result.get("legacy_result"), dict
    ):
        result["legacy_result"] = {
            **result["legacy_result"],
            "cleanup_summary": report,
        }
    result["cleanup_summary"] = report
    _write_json(path, result)


def certify(
    *,
    artifact_dir: Path,
    repo_root: Path,
    otclient_root: Path,
    lifecycle_pid: int,
    lifecycle_pgid: int,
    lifecycle_exit_code: int,
    db_command: Sequence[str],
    db_env: Mapping[str, str],
    proc_root: Path = Path("/proc"),
    db_runner: Callable[
        [Sequence[str], str, Mapping[str, str]], tuple[int, str, str]
    ]
    | None = None,
    group_reaper: Callable[[int, Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    repo_root = repo_root.resolve()
    otclient_root = otclient_root.resolve()
    reaper = group_reaper or (
        lambda pgid, root: reap_process_group(pgid, root)
    )
    process_group_cleanup = dict(reaper(lifecycle_pgid, proc_root))
    checks = _process_checks(
        artifact_dir, lifecycle_pid, lifecycle_pgid, proc_root
    )
    checks.extend(
        _workspace_checks(artifact_dir, repo_root, otclient_root)
    )
    checks.extend(_db_checks(artifact_dir, db_command, db_env, db_runner))
    checks.append(
        _check(
            "workflow_service_handoff",
            "pass",
            expected=(
                "workflow-owned MariaDB remains outside lifecycle ownership"
            ),
            observed="handoff",
            evidence={"lifecycle_owned_containers": 0},
        )
    )
    required = [item for item in checks if item["required"]]
    passed = sum(item["status"] == "pass" for item in required)
    certified = bool(required) and passed == len(required)
    legacy = _read_json(artifact_dir / "result.json", {})
    report = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT,
        "status": "certified"
        if certified
        else ("partial" if passed else "failed"),
        "cleanup_certified": certified,
        "gameplay_status": legacy.get("status")
        if isinstance(legacy, Mapping)
        else None,
        "lifecycle_exit_code": lifecycle_exit_code,
        "lifecycle_process": {
            "pid": lifecycle_pid,
            "pgid": lifecycle_pgid,
        },
        "process_group_cleanup": process_group_cleanup,
        "resource_scope": (
            "runner-owned-exact-process-group-and-fixed-disposable-database"
        ),
        "checks": checks,
        "summary": {
            "required": len(required),
            "passed": passed,
            "failed": len(required) - passed,
        },
        "unknowns": sorted(
            item["id"] for item in checks if item["status"] == "unknown"
        ),
        "warnings": [],
    }
    validate_report(report)
    _write_json(artifact_dir / RESULT_NAME, report)
    _merge_summary(artifact_dir, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Certify runner-owned Universal Physical E2E cleanup."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    baseline = sub.add_parser("baseline")
    baseline.add_argument("--artifact-dir", type=Path, required=True)
    baseline.add_argument("--repo-root", type=Path, required=True)
    baseline.add_argument("--otclient-root", type=Path, required=True)
    run = sub.add_parser("certify")
    run.add_argument("--artifact-dir", type=Path, required=True)
    run.add_argument("--repo-root", type=Path, required=True)
    run.add_argument("--otclient-root", type=Path, required=True)
    run.add_argument("--lifecycle-pid", type=int, required=True)
    run.add_argument("--lifecycle-pgid", type=int, required=True)
    run.add_argument("--lifecycle-exit-code", type=int, required=True)
    run.add_argument(
        "--db-host", default=os.environ.get("DB_HOST", "127.0.0.1")
    )
    run.add_argument(
        "--db-port",
        type=int,
        default=int(os.environ.get("DB_PORT", "3306")),
    )
    run.add_argument("--db-user", default=os.environ.get("DB_USER", "root"))
    run.add_argument(
        "--db-name", default=os.environ.get("DB_NAME", "agent_e2e")
    )
    validate = sub.add_parser("validate")
    validate.add_argument("path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "baseline":
            payload = capture_baseline(
                artifact_dir=args.artifact_dir,
                repo_root=args.repo_root,
                otclient_root=args.otclient_root,
            )
            print(json.dumps(payload, indent=2, sort_keys=True))
            return 0
        if args.command == "certify":
            report = certify(
                artifact_dir=args.artifact_dir,
                repo_root=args.repo_root,
                otclient_root=args.otclient_root,
                lifecycle_pid=args.lifecycle_pid,
                lifecycle_pgid=args.lifecycle_pgid,
                lifecycle_exit_code=args.lifecycle_exit_code,
                db_command=[
                    "mariadb",
                    "-h",
                    args.db_host,
                    "-P",
                    str(args.db_port),
                    "-u",
                    args.db_user,
                    "-D",
                    args.db_name,
                ],
                db_env=os.environ.copy(),
            )
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["cleanup_certified"] else 1
        report = _read_json(args.path, None)
        if not isinstance(report, Mapping):
            raise CleanupCertificationError("report root must be an object")
        validate_report(report)
        print(
            f"Validated {args.path}: {CONTRACT} schema {SCHEMA_VERSION}"
        )
        return 0
    except (
        CleanupCertificationError,
        OSError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"cleanup certification error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
