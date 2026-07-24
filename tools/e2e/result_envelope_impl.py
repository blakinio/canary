#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

CONTRACT = "canary-universal-e2e-result-envelope-v1"
SCHEMA_VERSION = 3

STATUS_VALUES = {"success", "failure", "cancelled", "timeout"}
EVIDENCE_MATURITY_VALUES = {"M0", "M1", "M2", "M3", "M4", "M5", "unknown", "not_proven"}
QUALITY_DIMENSIONS = (
    "determinism",
    "stability",
    "resilience",
    "exactly_once",
    "concurrency",
    "cleanup",
    "performance",
    "compatibility",
    "diagnostics",
)
QUALITY_STATES = {"not-evaluated", "pass", "fail", "unstable", "blocked"}
EXECUTION_TIERS = {"pr-required", "scheduled", "release-certification", "on-demand", "unknown"}
FAILURE_CLASSIFICATIONS = {
    "scenario_resolution",
    "static_preflight",
    "fixture_bootstrap",
    "server_startup",
    "client_build_startup",
    "login_world_entry",
    "route_execution",
    "world_interaction",
    "feature_action",
    "assertion",
    "persistence",
    "restart_recovery",
    "cleanup",
    "infrastructure",
    "cancelled",
    "timeout",
    "unknown",
}
FAILURE_CATEGORIES = {"gameplay", "test-contract", "infrastructure", "cancelled", "timeout", "unknown"}

_SECRET_KEY_RE = re.compile(
    r"(?:password|passwd|secret|token|private[_-]?key|authorization|cookie|connection[_-]?string)$",
    re.IGNORECASE,
)
_ALLOWED_REFERENCE_KEYS = {"password_env", "password_reference"}
_URI_CREDENTIAL_RE = re.compile(r"(?P<scheme>[a-z][a-z0-9+.-]*://)[^/@\s]+@", re.IGNORECASE)
_ENV_SECRET_RE = re.compile(
    r"(?i)\b(?:password|passwd|secret|token|private[_-]?key|authorization|cookie)\s*=\s*[^\s;,]+"
)
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

_PHASE_ORDER = (
    "bootstrap",
    "scenario-resolution",
    "runtime-contract",
    "database-initialization",
    "server-configuration",
    "client-configuration",
    "server-startup",
    "physical-client",
    "database-final-state",
    "evidence-evaluation",
    "complete",
)

_CHECK_PRIORITY = (
    "required_markers",
    "client_exit_zero",
    "two_server_logins_observed",
    "two_packet_records_present",
    "lastlogin_persisted",
    "lastlogout_persisted",
    "scenario_sql_assertions",
    "no_fatal_runtime_log",
)

_RESERVED_FIELDS = {
    "schema_version",
    "contract",
    "run_id",
    "scenario_id",
    "suite",
    "status",
    "evidence_maturity",
    "quality_dimensions",
    "server",
    "client",
    "fixture_identity",
    "started_at",
    "ended_at",
    "duration_ms",
    "execution_tier",
    "actors",
    "phases",
    "steps",
    "last_successful_step",
    "first_failed_step",
    "failure",
    "positions",
    "route_plan",
    "persistence_assertions",
    "sql_assertion_summary",
    "process_exit_status",
    "cleanup_summary",
    "artifacts",
    "infrastructure_failure",
    "attempt_history",
    "warnings",
    "unknowns",
    "legacy_result",
}


class EnvelopeError(ValueError):
    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _read_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return default


def _read_int(path: Path, default: int | None = None) -> int | None:
    try:
        return int(_read_text(path))
    except (TypeError, ValueError):
        return default


def _sanitize_string(value: str, *, maximum: int = 2048) -> str:
    sanitized = _CONTROL_RE.sub("", value).replace("\r\n", "\n").replace("\r", "\n")
    sanitized = _URI_CREDENTIAL_RE.sub(r"\g<scheme>[REDACTED]@", sanitized)
    sanitized = _ENV_SECRET_RE.sub("[REDACTED]", sanitized)
    if len(sanitized) > maximum:
        return sanitized[: maximum - 14] + "...[truncated]"
    return sanitized


def sanitize(value: Any, *, key: str | None = None) -> Any:
    if key and _SECRET_KEY_RE.search(key) and key not in _ALLOWED_REFERENCE_KEYS:
        return "[REDACTED]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return _sanitize_string(value)
    if isinstance(value, Mapping):
        return {
            _sanitize_string(str(child_key), maximum=256): sanitize(child_value, key=str(child_key))
            for child_key, child_value in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [sanitize(child) for child in value]
    return _sanitize_string(str(value))


def _safe_relative_path(path: str) -> str | None:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    rendered = candidate.as_posix()
    return rendered if rendered and rendered != "." else None


def _sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _artifact_kind(path: str) -> str:
    name = Path(path).name.lower()
    if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "screenshot"
    if name.endswith((".pcap", ".record")):
        return "session-record"
    if name.endswith(".json"):
        return "json"
    if "log" in name or name.endswith((".stdout", ".stderr")):
        return "log"
    if "sha256" in name or "hash" in name:
        return "integrity"
    return "evidence"


def _artifact_references(artifacts: Path, manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    declared = manifest.get("scenario", {}).get("artifacts", []) if isinstance(manifest, Mapping) else []
    candidates: list[str] = []
    if isinstance(declared, list):
        candidates.extend(str(item) for item in declared if isinstance(item, str))
    candidates.extend(
        [
            "result.json",
            "scenario-manifest.json",
            "runtime-contract.txt",
            "runtime-hashes.txt",
            "sql-assertions.json",
            "canary-restart-evidence.json",
            "client-events.tsv",
            "canary.stdout.log",
            "canary.stderr.log",
            "otclient.stdout.log",
            "otclient.stderr.log",
        ]
    )
    references: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in candidates:
        safe = _safe_relative_path(raw)
        if safe is None or safe in seen:
            continue
        seen.add(safe)
        target = artifacts / safe
        exists = target.is_file()
        reference: dict[str, Any] = {
            "path": safe,
            "kind": _artifact_kind(safe),
            "exists": exists,
        }
        if exists:
            try:
                reference["size_bytes"] = target.stat().st_size
            except OSError:
                reference["size_bytes"] = None
            if safe != "result.json":
                digest = _sha256(target)
                if digest:
                    reference["sha256"] = digest
        references.append(reference)
    return references


def _scenario_identity(manifest: Mapping[str, Any], legacy: Mapping[str, Any]) -> tuple[str, str, str]:
    scenario = manifest.get("scenario") if isinstance(manifest, Mapping) else None
    if isinstance(scenario, Mapping):
        suite = str(scenario.get("suite") or "unknown")
        scenario_id = str(scenario.get("id") or "unknown")
        key = str(manifest.get("key") or f"{suite}/{scenario_id}")
        return suite, scenario_id, key
    key = str(legacy.get("scenario") or "unknown/unknown")
    if "/" in key:
        suite, scenario_id = key.split("/", 1)
    else:
        suite, scenario_id = "unknown", key
    return suite or "unknown", scenario_id or "unknown", key


def _run_id(
    *,
    scenario_key: str,
    started_at: str,
    environment: Mapping[str, str],
) -> str:
    explicit = environment.get("AGENT_E2E_RUN_ID")
    if explicit:
        return _sanitize_string(explicit, maximum=256)
    github_run = environment.get("GITHUB_RUN_ID")
    if github_run:
        attempt = environment.get("GITHUB_RUN_ATTEMPT", "1")
        return f"github-{github_run}-{attempt}-{scenario_key.replace('/', '-')}"
    material = f"{scenario_key}\0{started_at}\0{environment.get('GITHUB_SHA', 'local')}"
    return "local-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:20]


def _determine_times(
    artifacts: Path,
    *,
    started_at: str | None,
    ended_at: str | None,
    now: datetime | None,
) -> tuple[str, str, int]:
    end_dt = _parse_timestamp(ended_at) or now or _utc_now()
    start_dt = _parse_timestamp(started_at)
    if start_dt is None:
        start_dt = _parse_timestamp(_read_text(artifacts / "run-started-at.txt"))
    if start_dt is None:
        mtimes: list[float] = []
        try:
            for path in artifacts.iterdir():
                try:
                    mtimes.append(path.stat().st_mtime)
                except OSError:
                    continue
        except OSError:
            pass
        if mtimes:
            start_dt = datetime.fromtimestamp(min(mtimes), timezone.utc)
        else:
            start_dt = end_dt
    if start_dt > end_dt:
        start_dt = end_dt
    duration_ms = max(0, int(round((end_dt - start_dt).total_seconds() * 1000)))
    return _format_timestamp(start_dt), _format_timestamp(end_dt), duration_ms


def _status(legacy: Mapping[str, Any], shell_exit_code: int) -> str:
    if shell_exit_code in {124, 137}:
        return "timeout"
    if shell_exit_code in {130, 143}:
        return "cancelled"
    value = str(legacy.get("status") or "").lower()
    if shell_exit_code == 0 and value == "success":
        return "success"
    return "failure"


def _ordered_checks(legacy: Mapping[str, Any]) -> list[tuple[str, bool]]:
    checks = legacy.get("checks")
    if not isinstance(checks, Mapping):
        return []
    names = list(_CHECK_PRIORITY)
    names.extend(sorted(str(name) for name in checks if str(name) not in _CHECK_PRIORITY))
    ordered: list[tuple[str, bool]] = []
    seen: set[str] = set()
    for name in names:
        if name in seen or name not in checks:
            continue
        seen.add(name)
        ordered.append((name, bool(checks[name])))
    return ordered


def _failure_from_marker(marker: str) -> tuple[str, str]:
    lowered = marker.lower()
    if "login" in lowered or "online" in lowered or "world" in lowered:
        return "login_world_entry", "gameplay"
    if "route" in lowered or "walk" in lowered or "position" in lowered or "floor" in lowered:
        return "route_execution", "gameplay"
    if "persist" in lowered or "relog" in lowered or "lastlogin" in lowered or "lastlogout" in lowered:
        return "persistence", "gameplay"
    if "restart" in lowered or "reconnect" in lowered or "recovery" in lowered:
        return "restart_recovery", "gameplay"
    if "cleanup" in lowered or "exit" in lowered:
        return "cleanup", "test-contract"
    if "assert" in lowered or "sql" in lowered or "marker" in lowered:
        return "assertion", "test-contract"
    if "client" in lowered:
        return "client_build_startup", "infrastructure"
    if "server" in lowered or "canary" in lowered:
        return "server_startup", "infrastructure"
    return "feature_action", "gameplay"


def _classification(current_phase: str, legacy: Mapping[str, Any], status: str) -> tuple[str, str]:
    if status == "success":
        return "unknown", "unknown"
    if status == "timeout":
        return "timeout", "timeout"
    if status == "cancelled":
        return "cancelled", "cancelled"
    ordered = _ordered_checks(legacy)
    first_check = next((name for name, passed in ordered if not passed), None)
    if first_check == "required_markers":
        missing = legacy.get("missing_markers")
        if isinstance(missing, list) and missing:
            return _failure_from_marker(str(missing[0]))
    if first_check:
        return _failure_from_marker(first_check)
    if current_phase.startswith("restart-"):
        return "restart_recovery", "gameplay"
    phase_map = {
        "bootstrap": ("infrastructure", "infrastructure"),
        "scenario-resolution": ("scenario_resolution", "test-contract"),
        "runtime-contract": ("static_preflight", "test-contract"),
        "database-initialization": ("fixture_bootstrap", "infrastructure"),
        "server-configuration": ("static_preflight", "test-contract"),
        "client-configuration": ("client_build_startup", "infrastructure"),
        "server-startup": ("server_startup", "infrastructure"),
        "physical-client": ("login_world_entry", "gameplay"),
        "database-final-state": ("persistence", "gameplay"),
        "evidence-evaluation": ("assertion", "test-contract"),
        "cleanup": ("cleanup", "test-contract"),
    }
    return phase_map.get(current_phase, ("unknown", "unknown"))


def _failure_evidence(
    *,
    current_phase: str,
    legacy: Mapping[str, Any],
    status: str,
    artifact_refs: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    ordered = _ordered_checks(legacy)
    first_failed_name = next((name for name, passed in ordered if not passed), None)
    last_successful_name: str | None = None
    for name, passed in ordered:
        if not passed:
            break
        last_successful_name = name

    if status == "success":
        last = (
            {"id": f"check:{last_successful_name}", "phase": "evidence-evaluation", "status": "success"}
            if last_successful_name
            else {"id": "phase:complete", "phase": "complete", "status": "success"}
        )
        return None, last, None

    classification, category = _classification(current_phase, legacy, status)
    expected: Any = True
    observed: Any = False
    relevant_state: dict[str, Any] = {}
    failed_id = f"phase:{current_phase}"
    failed_phase = current_phase
    if first_failed_name:
        failed_id = f"check:{first_failed_name}"
        failed_phase = "evidence-evaluation"
        if first_failed_name == "required_markers":
            expected = sanitize(legacy.get("legacy_required_markers") or "all required scenario markers")
            observed = {"missing_markers": sanitize(legacy.get("missing_markers") or [])}
        else:
            observed = sanitize(legacy.get(first_failed_name, legacy.get("checks", {}).get(first_failed_name)))
        relevant_state["check"] = first_failed_name
    elif "shell_exit_code" in legacy:
        expected = 0
        observed = legacy.get("shell_exit_code")

    relevant_state.update(
        {
            "phase": current_phase,
            "shell_exit_code": legacy.get("shell_exit_code"),
            "missing_markers": sanitize(legacy.get("missing_markers") or []),
            "fatal_log_hit_count": len(legacy.get("fatal_log_hits") or [])
            if isinstance(legacy.get("fatal_log_hits"), list)
            else 0,
        }
    )
    references = [
        {"path": ref["path"], "kind": ref["kind"]}
        for ref in artifact_refs
        if ref.get("exists") and ref.get("kind") in {"log", "json", "screenshot", "session-record"}
    ][:16]
    first_failed = {
        "id": failed_id,
        "phase": failed_phase,
        "status": "failure",
    }
    last_successful = (
        {"id": f"check:{last_successful_name}", "phase": "evidence-evaluation", "status": "success"}
        if last_successful_name
        else None
    )
    failure = {
        "classification": classification,
        "category": category,
        "phase": current_phase,
        "actor": "primary" if classification not in {"infrastructure", "scenario_resolution", "static_preflight"} else None,
        "expected": sanitize(expected),
        "observed": sanitize(observed),
        "relevant_state": sanitize(relevant_state),
        "artifact_references": references,
    }
    return failure, last_successful, first_failed


def _phases(current_phase: str, status: str, artifacts: Path) -> list[dict[str, Any]]:
    phases: list[dict[str, Any]] = []
    try:
        current_index = _PHASE_ORDER.index(current_phase)
    except ValueError:
        current_index = -1
    for index, name in enumerate(_PHASE_ORDER):
        if status == "success":
            phase_status = "success"
        elif index < current_index:
            phase_status = "success"
        elif index == current_index:
            phase_status = status
        else:
            phase_status = "not-run"
        phases.append({"id": name.replace("-", "_"), "name": name, "status": phase_status})

    restart_path = artifacts / "canary-restart-evidence.json"
    restart = _read_json(restart_path, {})
    restart_phases = restart.get("phases") if isinstance(restart, Mapping) else None
    if isinstance(restart_phases, Mapping):
        for name, raw in restart_phases.items():
            detail = raw if isinstance(raw, Mapping) else {}
            phases.append(
                {
                    "id": f"restart_{str(name).replace('-', '_')}",
                    "name": f"restart-{name}",
                    "status": str(detail.get("status") or "unknown"),
                    "detail": sanitize(detail.get("detail") or ""),
                }
            )
    return phases


def _steps(manifest: Mapping[str, Any], legacy: Mapping[str, Any], status: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    scenario = manifest.get("scenario") if isinstance(manifest, Mapping) else None
    declared = scenario.get("steps") if isinstance(scenario, Mapping) else None
    if isinstance(declared, list):
        for index, raw in enumerate(declared):
            if not isinstance(raw, Mapping):
                continue
            entries.append(
                {
                    "id": str(raw.get("id") or f"step-{index + 1}"),
                    "action": str(raw.get("action") or "unknown"),
                    "actor": str(raw.get("actor") or "primary"),
                    "status": "success" if status == "success" else "unknown",
                }
            )
    first_failure_seen = False
    for name, passed in _ordered_checks(legacy):
        if not passed:
            first_failure_seen = True
        entries.append(
            {
                "id": f"check:{name}",
                "action": "assert",
                "actor": "primary",
                "status": "failure" if not passed else ("success" if not first_failure_seen else "success"),
                "expected": True,
                "observed": passed,
            }
        )
    return entries


def _actors(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    scenario = manifest.get("scenario") if isinstance(manifest, Mapping) else None
    if not isinstance(scenario, Mapping):
        return []
    fixture = scenario.get("fixture")
    actors: list[dict[str, Any]] = []
    if isinstance(fixture, Mapping):
        actors.append(
            {
                "id": "primary",
                "role": "primary",
                "account": sanitize(fixture.get("account")),
                "character": sanitize(fixture.get("character")),
            }
        )
    multi_client = scenario.get("multi_client")
    secondary = multi_client.get("secondary") if isinstance(multi_client, Mapping) else None
    if isinstance(secondary, Mapping):
        actors.append(
            {
                "id": sanitize(secondary.get("id") or "secondary"),
                "role": "secondary",
                "account": sanitize(secondary.get("account")),
                "character": sanitize(secondary.get("character")),
            }
        )
    return actors


def _positions(legacy: Mapping[str, Any]) -> list[dict[str, Any]]:
    events = legacy.get("events")
    if not isinstance(events, list):
        return []
    positions: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, Mapping):
            continue
        key = str(event.get("key") or "")
        if "position" not in key.lower() and not key.lower().endswith(("_x", "_y", "_z")):
            continue
        positions.append(
            {
                "timestamp": sanitize(event.get("timestamp")),
                "key": sanitize(key),
                "value": sanitize(event.get("value")),
            }
        )
    return positions[:256]


def _route_plan(artifacts: Path) -> dict[str, Any] | None:
    candidates = (
        "route-plan.json",
        "prepared-route-plan.json",
        "executable-route-plan.json",
        "scenario-plan.lua",
    )
    for name in candidates:
        path = artifacts / name
        if not path.is_file():
            continue
        return {
            "path": name,
            "sha256": _sha256(path),
            "identity": _sha256(path),
        }
    return None


def _sql_summary(legacy: Mapping[str, Any]) -> dict[str, Any]:
    payload = legacy.get("sql_assertions")
    assertions = payload.get("assertions") if isinstance(payload, Mapping) else None
    if not isinstance(assertions, list):
        return {"total": 0, "passed": 0, "failed": 0, "not_executed": 0, "all_passed": None}
    total = len(assertions)
    passed = sum(1 for item in assertions if isinstance(item, Mapping) and item.get("passed") is True)
    executed = sum(1 for item in assertions if isinstance(item, Mapping) and item.get("executed") is True)
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "not_executed": total - executed,
        "all_passed": bool(payload.get("all_passed")) if isinstance(payload, Mapping) else False,
    }


def _persistence_summary(manifest: Mapping[str, Any], legacy: Mapping[str, Any]) -> dict[str, Any]:
    scenario = manifest.get("scenario") if isinstance(manifest, Mapping) else None
    assertions = scenario.get("assertions") if isinstance(scenario, Mapping) else None
    persistence = assertions.get("persistence") if isinstance(assertions, Mapping) else None
    required = bool(persistence.get("required")) if isinstance(persistence, Mapping) else False
    checks = persistence.get("checks") if isinstance(persistence, Mapping) else []
    count = len(checks) if isinstance(checks, list) else 0
    passed_value = legacy.get("sql_assertions_passed")
    passed = passed_value == 1 if required else None
    return {
        "required": required,
        "declared_check_count": count,
        "status": "pass" if passed is True else "fail" if passed is False else "not-evaluated",
    }


def _process_exit_status(artifacts: Path, legacy: Mapping[str, Any]) -> dict[str, Any]:
    actors: dict[str, Any] = {
        "primary_client": legacy.get("client_exit_code", _read_int(artifacts / "otclient-exit-code.txt")),
        "canary": _read_int(artifacts / "canary-exit-code.txt"),
        "xvfb": _read_int(artifacts / "xvfb-exit-code.txt"),
    }
    actor_root = artifacts / "actors"
    if actor_root.is_dir():
        for child in sorted(actor_root.iterdir()):
            if child.is_dir():
                actors[f"client:{child.name}"] = _read_int(child / "otclient-exit-code.txt")
    return actors


def _cleanup_summary(artifacts: Path, legacy: Mapping[str, Any]) -> dict[str, Any]:
    after_online = legacy.get("after_online_count")
    if not isinstance(after_online, int):
        after_online = _read_int(artifacts / "database-after-online-count.txt")
    return {
        "contract": None,
        "cleanup_certified": False,
        "status": "not-certified",
        "observations": {
            "players_online_after": after_online,
            "primary_client_exit_code": legacy.get("client_exit_code"),
        },
        "unknowns": [
            "QRI-006 cleanup certification has not evaluated every runner-owned resource.",
        ],
    }


def _quality_dimensions(legacy: Mapping[str, Any], status: str) -> dict[str, str]:
    dimensions = {name: "not-evaluated" for name in QUALITY_DIMENSIONS}
    dimensions["diagnostics"] = "pass" if status in STATUS_VALUES else "fail"
    restart = legacy.get("restart_evidence")
    if isinstance(restart, Mapping):
        dimensions["resilience"] = "pass" if restart.get("status") == "success" else "fail"
    return dimensions


def _map_identity(artifacts: Path, scenario: Mapping[str, Any]) -> dict[str, Any]:
    digest = _read_text(artifacts / "map.sha256").split(maxsplit=1)[0]
    if not _SHA256_RE.fullmatch(digest):
        digest = None
    server = scenario.get("server") if isinstance(scenario, Mapping) else None
    return {
        "name": sanitize(server.get("map")) if isinstance(server, Mapping) else None,
        "sha256": digest,
    }


def _server_revision(artifacts: Path, legacy: Mapping[str, Any], environment: Mapping[str, str]) -> str:
    explicit = _read_text(artifacts / "server-source-commit.txt")
    return explicit or str(legacy.get("canary_head") or environment.get("GITHUB_SHA") or "unknown")


def _client_revision(artifacts: Path, legacy: Mapping[str, Any], scenario: Mapping[str, Any]) -> str:
    explicit = _read_text(artifacts / "otclient-source-commit.txt")
    client = scenario.get("client") if isinstance(scenario, Mapping) else None
    return explicit or str(legacy.get("client_ref") or (client.get("ref") if isinstance(client, Mapping) else None) or "unknown")


def _attempt_history(
    *,
    legacy: Mapping[str, Any],
    run_id: str,
    attempt_number: int,
    status: str,
    started_at: str,
    ended_at: str,
    duration_ms: int,
    first_failed_step: Mapping[str, Any] | None,
    failure: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    history_raw = legacy.get("attempt_history")
    if not isinstance(history_raw, list):
        history_raw = legacy.get("attempts")
    history = [sanitize(item) for item in history_raw] if isinstance(history_raw, list) else []
    current = {
        "run_id": run_id,
        "attempt": attempt_number,
        "status": status,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": duration_ms,
        "first_failed_step": sanitize(first_failed_step),
        "failure_classification": failure.get("classification") if isinstance(failure, Mapping) else None,
    }
    if not any(
        isinstance(item, Mapping)
        and item.get("run_id") == run_id
        and item.get("attempt") == attempt_number
        for item in history
    ):
        history.append(current)
    return history


def build_envelope(
    artifacts: Path,
    *,
    current_phase: str,
    shell_exit_code: int,
    execution_tier: str = "unknown",
    environment: Mapping[str, str] | None = None,
    started_at: str | None = None,
    ended_at: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    environment = dict(os.environ if environment is None else environment)
    artifacts = artifacts.resolve()
    manifest_raw = _read_json(artifacts / "scenario-manifest.json", {})
    manifest = manifest_raw if isinstance(manifest_raw, Mapping) else {}
    legacy_raw = _read_json(artifacts / "result.json", {})
    if isinstance(legacy_raw, Mapping) and legacy_raw.get("contract") == CONTRACT:
        legacy_candidate = legacy_raw.get("legacy_result")
        legacy = legacy_candidate if isinstance(legacy_candidate, Mapping) else legacy_raw
    else:
        legacy = legacy_raw if isinstance(legacy_raw, Mapping) else {}
    legacy = sanitize(dict(legacy))

    suite, scenario_id, scenario_key = _scenario_identity(manifest, legacy)
    start_text, end_text, duration_ms = _determine_times(
        artifacts,
        started_at=started_at,
        ended_at=ended_at,
        now=now,
    )
    status = _status(legacy, shell_exit_code)
    tier = execution_tier if execution_tier in EXECUTION_TIERS else "unknown"
    run_id = _run_id(scenario_key=scenario_key, started_at=start_text, environment=environment)
    try:
        attempt_number = max(1, int(environment.get("GITHUB_RUN_ATTEMPT", "1")))
    except ValueError:
        attempt_number = 1

    artifact_refs = _artifact_references(artifacts, manifest)
    failure, last_successful, first_failed = _failure_evidence(
        current_phase=current_phase,
        legacy=legacy,
        status=status,
        artifact_refs=artifact_refs,
    )
    scenario = manifest.get("scenario") if isinstance(manifest.get("scenario"), Mapping) else {}
    server = scenario.get("server") if isinstance(scenario, Mapping) else {}
    client = scenario.get("client") if isinstance(scenario, Mapping) else {}
    fixture = scenario.get("fixture") if isinstance(scenario, Mapping) else {}

    maturity = str(scenario.get("evidence_maturity") or "unknown") if isinstance(scenario, Mapping) else "unknown"
    if maturity not in EVIDENCE_MATURITY_VALUES:
        maturity = "unknown"

    warnings: list[str] = []
    unknowns: list[str] = []
    if maturity in {"unknown", "not_proven"}:
        unknowns.append("Scenario evidence maturity is not declared in the current scenario manifest.")
    if _route_plan(artifacts) is None:
        unknowns.append("No route-plan identity was present for this run; the scenario may not use routed execution.")
    unknowns.append("Cleanup is observed only and is not QRI-006 certified.")
    if not manifest:
        warnings.append("scenario-manifest.json was unavailable; scenario identity is derived from legacy result evidence.")
    if not legacy:
        warnings.append("Legacy result evidence was unavailable; failure evidence is limited to lifecycle phase and shell exit status.")

    envelope: dict[str, Any] = {}
    for key, value in legacy.items():
        if key not in _RESERVED_FIELDS:
            envelope[key] = value

    envelope.update(
        {
            "schema_version": SCHEMA_VERSION,
            "contract": CONTRACT,
            "run_id": run_id,
            "scenario_id": scenario_id,
            "suite": suite,
            "scenario": scenario_key,
            "status": status,
            "evidence_maturity": maturity,
            "quality_dimensions": _quality_dimensions(legacy, status),
            "server": {
                "repository": sanitize(environment.get("GITHUB_REPOSITORY") or "blakinio/canary"),
                "revision": _server_revision(artifacts, legacy, environment),
                "datapack": sanitize(server.get("datapack")) if isinstance(server, Mapping) else None,
                "map": _map_identity(artifacts, scenario),
            },
            "client": {
                "repository": sanitize(client.get("repository")) if isinstance(client, Mapping) else legacy.get("client_repository"),
                "revision": _client_revision(artifacts, legacy, scenario),
            },
            "fixture_identity": {
                "account": sanitize(fixture.get("account")) if isinstance(fixture, Mapping) else None,
                "character": sanitize(fixture.get("character")) if isinstance(fixture, Mapping) else None,
                "world": sanitize(fixture.get("world")) if isinstance(fixture, Mapping) else None,
                "password_reference": sanitize(fixture.get("password_env"), key="password_reference")
                if isinstance(fixture, Mapping)
                else None,
            },
            "started_at": start_text,
            "ended_at": end_text,
            "duration_ms": duration_ms,
            "execution_tier": tier,
            "actors": _actors(manifest),
            "phases": _phases(current_phase, status, artifacts),
            "steps": _steps(manifest, legacy, status),
            "last_successful_step": last_successful,
            "first_failed_step": first_failed,
            "failure": failure,
            "positions": _positions(legacy),
            "route_plan": _route_plan(artifacts),
            "persistence_assertions": _persistence_summary(manifest, legacy),
            "sql_assertion_summary": _sql_summary(legacy),
            "process_exit_status": _process_exit_status(artifacts, legacy),
            "cleanup_summary": _cleanup_summary(artifacts, legacy),
            "artifacts": artifact_refs,
            "infrastructure_failure": (
                {
                    "classification": failure.get("classification"),
                    "phase": failure.get("phase"),
                }
                if isinstance(failure, Mapping) and failure.get("category") == "infrastructure"
                else None
            ),
            "attempt_history": _attempt_history(
                legacy=legacy,
                run_id=run_id,
                attempt_number=attempt_number,
                status=status,
                started_at=start_text,
                ended_at=end_text,
                duration_ms=duration_ms,
                first_failed_step=first_failed,
                failure=failure,
            ),
            "warnings": sorted(set(warnings)),
            "unknowns": sorted(set(unknowns)),
            "legacy_result": legacy,
        }
    )
    validate_envelope(envelope)
    return envelope


def validate_envelope(envelope: Mapping[str, Any]) -> None:
    if envelope.get("schema_version") != SCHEMA_VERSION:
        raise EnvelopeError(f"schema_version must be {SCHEMA_VERSION}")
    if envelope.get("contract") != CONTRACT:
        raise EnvelopeError(f"contract must be {CONTRACT}")
    for key in (
        "run_id",
        "scenario_id",
        "suite",
        "status",
        "evidence_maturity",
        "quality_dimensions",
        "started_at",
        "ended_at",
        "duration_ms",
        "execution_tier",
        "actors",
        "phases",
        "steps",
        "attempt_history",
        "warnings",
        "unknowns",
    ):
        if key not in envelope:
            raise EnvelopeError(f"missing required field: {key}")
    if not isinstance(envelope.get("run_id"), str) or not envelope["run_id"]:
        raise EnvelopeError("run_id must be a non-empty string")
    if envelope.get("status") not in STATUS_VALUES:
        raise EnvelopeError(f"invalid status: {envelope.get('status')!r}")
    if envelope.get("evidence_maturity") not in EVIDENCE_MATURITY_VALUES:
        raise EnvelopeError(f"invalid evidence_maturity: {envelope.get('evidence_maturity')!r}")
    if envelope.get("execution_tier") not in EXECUTION_TIERS:
        raise EnvelopeError(f"invalid execution_tier: {envelope.get('execution_tier')!r}")
    dimensions = envelope.get("quality_dimensions")
    if not isinstance(dimensions, Mapping) or set(dimensions) != set(QUALITY_DIMENSIONS):
        raise EnvelopeError("quality_dimensions must contain the canonical dimension set")
    invalid_dimensions = {name: state for name, state in dimensions.items() if state not in QUALITY_STATES}
    if invalid_dimensions:
        raise EnvelopeError(f"invalid quality dimension state(s): {invalid_dimensions}")
    duration = envelope.get("duration_ms")
    if not isinstance(duration, int) or isinstance(duration, bool) or duration < 0:
        raise EnvelopeError("duration_ms must be a non-negative integer")
    failure = envelope.get("failure")
    if failure is not None:
        if not isinstance(failure, Mapping):
            raise EnvelopeError("failure must be an object or null")
        if failure.get("classification") not in FAILURE_CLASSIFICATIONS:
            raise EnvelopeError(f"invalid failure classification: {failure.get('classification')!r}")
        if failure.get("category") not in FAILURE_CATEGORIES:
            raise EnvelopeError(f"invalid failure category: {failure.get('category')!r}")
    if envelope.get("status") == "success" and failure is not None:
        raise EnvelopeError("successful envelope must not contain failure evidence")
    if envelope.get("status") != "success" and failure is None:
        raise EnvelopeError("non-success envelope must contain failure evidence")
    attempts = envelope.get("attempt_history")
    if not isinstance(attempts, list) or not attempts:
        raise EnvelopeError("attempt_history must contain at least one attempt")
    serialized = json.dumps(envelope, sort_keys=True)
    lowered = serialized.lower()
    if "root:root@" in lowered or "password=root" in lowered:
        raise EnvelopeError("serialized envelope contains an unsanitized credential")


def serialize_envelope(envelope: Mapping[str, Any]) -> str:
    validate_envelope(envelope)
    return json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_envelope(path: Path, envelope: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(serialize_envelope(envelope), encoding="utf-8")
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and validate the canonical Universal E2E result envelope.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    finalize = subparsers.add_parser("finalize", help="Normalize the current physical-run result.json in place.")
    finalize.add_argument("--artifact-dir", type=Path, required=True)
    finalize.add_argument("--phase", required=True)
    finalize.add_argument("--shell-exit-code", type=int, required=True)
    finalize.add_argument("--execution-tier", default=os.environ.get("AGENT_E2E_EXECUTION_TIER", "unknown"))
    finalize.add_argument("--started-at")
    finalize.add_argument("--ended-at")
    finalize.add_argument("--output", type=Path)

    validate = subparsers.add_parser("validate", help="Validate an existing envelope JSON file.")
    validate.add_argument("path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "finalize":
            output = args.output or args.artifact_dir / "result.json"
            envelope = build_envelope(
                args.artifact_dir,
                current_phase=args.phase,
                shell_exit_code=args.shell_exit_code,
                execution_tier=args.execution_tier,
                started_at=args.started_at,
                ended_at=args.ended_at,
            )
            write_envelope(output, envelope)
            print(serialize_envelope(envelope), end="")
        elif args.command == "validate":
            payload = _read_json(args.path, None)
            if not isinstance(payload, Mapping):
                raise EnvelopeError("envelope root must be an object")
            validate_envelope(payload)
            print(f"Validated {args.path}: {CONTRACT} schema {SCHEMA_VERSION}")
        else:  # pragma: no cover
            raise EnvelopeError(f"unsupported command: {args.command}")
    except (EnvelopeError, OSError) as exc:
        print(f"result envelope error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
