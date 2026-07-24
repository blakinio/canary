#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

CONTRACT = "canary-universal-e2e-coverage-dashboard-v1"
SCHEMA_VERSION = 1
RESULT_CONTRACT = "canary-universal-e2e-result-envelope-v1"
RESULT_SCHEMA_VERSION = 3
CLEANUP_CONTRACT = "canary-universal-e2e-cleanup-certification-v1"
CLEANUP_SCHEMA_VERSION = 1

MATURITY_LEVELS = ("M0", "M1", "M2", "M3", "M4", "M5")
MATURITY_RANK = {name: index for index, name in enumerate(MATURITY_LEVELS)}
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
RESULT_STATUSES = {"success", "failure", "cancelled", "timeout"}
FRESHNESS_STATES = {"current", "stale", "missing", "not-evaluated"}

_RESULT_ENVELOPE = None
_SCENARIO_RUNNER = None


class CoverageDashboardError(ValueError):
    """Raised when dashboard inputs or output violate the factual contract."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CoverageDashboardError(f"cannot load required module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _result_envelope_module():
    global _RESULT_ENVELOPE
    if _RESULT_ENVELOPE is None:
        _RESULT_ENVELOPE = _load_module(
            "canary_e2e_coverage_result_envelope",
            Path(__file__).with_name("result_envelope.py"),
        )
    return _RESULT_ENVELOPE


def _scenario_runner_module():
    global _SCENARIO_RUNNER
    if _SCENARIO_RUNNER is None:
        _SCENARIO_RUNNER = _load_module(
            "canary_e2e_coverage_scenario_runner",
            Path(__file__).with_name("run_agent_e2e.py"),
        )
    return _SCENARIO_RUNNER


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def serialize_report(report: Mapping[str, Any]) -> str:
    validate_report(report)
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CoverageDashboardError(f"cannot read JSON evidence: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CoverageDashboardError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CoverageDashboardError(f"{label} must be a non-empty ISO-8601 timestamp")
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise CoverageDashboardError(f"{label} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise CoverageDashboardError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def _scenario_key(result: Mapping[str, Any]) -> str:
    scenario = result.get("scenario")
    if isinstance(scenario, str) and scenario.count("/") == 1:
        suite, scenario_id = scenario.split("/", 1)
    else:
        suite = result.get("suite")
        scenario_id = result.get("scenario_id")
    if not isinstance(suite, str) or not suite or "/" in suite:
        raise CoverageDashboardError("result suite must be a non-empty path-safe string")
    if not isinstance(scenario_id, str) or not scenario_id or "/" in scenario_id:
        raise CoverageDashboardError(
            "result scenario_id must be a non-empty path-safe string"
        )
    key = f"{suite}/{scenario_id}"
    if isinstance(scenario, str) and scenario != key:
        raise CoverageDashboardError(
            f"result scenario key {scenario!r} disagrees with suite/scenario_id {key!r}"
        )
    return key


def _validate_cleanup(result: Mapping[str, Any]) -> dict[str, Any]:
    summary = result.get("cleanup_summary")
    dimensions = result.get("quality_dimensions")
    cleanup_dimension = (
        dimensions.get("cleanup") if isinstance(dimensions, Mapping) else None
    )
    if not isinstance(summary, Mapping):
        return {
            "status": "missing",
            "cleanup_certified": False,
            "contract_valid": False,
        }
    if (
        summary.get("contract") != CLEANUP_CONTRACT
        or summary.get("schema_version") != CLEANUP_SCHEMA_VERSION
    ):
        return {
            "status": "missing",
            "cleanup_certified": False,
            "contract_valid": False,
        }
    certified = summary.get("cleanup_certified")
    status = summary.get("status")
    if not isinstance(certified, bool) or status not in {
        "certified",
        "partial",
        "failed",
    }:
        raise CoverageDashboardError("cleanup_summary has an invalid schema-v1 status")
    expected_dimension = "pass" if certified else "fail"
    if cleanup_dimension != expected_dimension:
        raise CoverageDashboardError(
            "cleanup_summary certification disagrees with the cleanup quality dimension"
        )
    return {
        "status": status,
        "cleanup_certified": certified,
        "contract_valid": True,
    }


def normalize_result(
    payload: Mapping[str, Any], *, root_id: str, relative_path: str
) -> dict[str, Any]:
    try:
        _result_envelope_module().validate_envelope(payload)
    except Exception as exc:
        raise CoverageDashboardError(f"invalid result envelope: {exc}") from exc
    if (
        payload.get("contract") != RESULT_CONTRACT
        or payload.get("schema_version") != RESULT_SCHEMA_VERSION
    ):
        raise CoverageDashboardError(
            f"result must use {RESULT_CONTRACT} schema {RESULT_SCHEMA_VERSION}"
        )
    key = _scenario_key(payload)
    ended_at = _parse_timestamp(payload.get("ended_at"), "result.ended_at")
    started_at = _parse_timestamp(payload.get("started_at"), "result.started_at")
    if started_at > ended_at:
        raise CoverageDashboardError("result.started_at must not be after ended_at")
    dimensions = payload.get("quality_dimensions")
    if not isinstance(dimensions, Mapping) or set(dimensions) != set(
        QUALITY_DIMENSIONS
    ):
        raise CoverageDashboardError(
            "result quality_dimensions must contain the canonical dimension set"
        )
    if any(state not in QUALITY_STATES for state in dimensions.values()):
        raise CoverageDashboardError("result contains an unsupported quality state")
    status = payload.get("status")
    if status not in RESULT_STATUSES:
        raise CoverageDashboardError("result contains an unsupported status")
    maturity = payload.get("evidence_maturity")
    if maturity not in {*MATURITY_LEVELS, "unknown", "not_proven"}:
        raise CoverageDashboardError("result contains an unsupported evidence maturity")
    run_id = payload.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise CoverageDashboardError("result.run_id must be a non-empty string")
    cleanup = _validate_cleanup(payload)
    server = payload.get("server") if isinstance(payload.get("server"), Mapping) else {}
    client = payload.get("client") if isinstance(payload.get("client"), Mapping) else {}
    warnings = payload.get("warnings") if isinstance(payload.get("warnings"), list) else []
    unknowns = payload.get("unknowns") if isinstance(payload.get("unknowns"), list) else []
    return {
        "scenario": key,
        "run_id": run_id,
        "status": status,
        "evidence_maturity": maturity,
        "quality_dimensions": dict(dimensions),
        "started_at": _format_timestamp(started_at),
        "ended_at": _format_timestamp(ended_at),
        "ended_at_epoch": ended_at.timestamp(),
        "duration_ms": payload.get("duration_ms"),
        "execution_tier": payload.get("execution_tier"),
        "server_revision": server.get("revision"),
        "client_revision": client.get("revision"),
        "datapack": server.get("datapack"),
        "cleanup": cleanup,
        "warnings": sorted({str(item) for item in warnings}),
        "unknowns": sorted({str(item) for item in unknowns}),
        "source": {"root_id": root_id, "path": relative_path},
    }


def discover_registered_scenarios(repo_root: Path) -> list[dict[str, str]]:
    root = repo_root.resolve()
    runner = _scenario_runner_module()
    try:
        scenarios = runner.discover(root)
    except Exception as exc:
        raise CoverageDashboardError(f"cannot discover registered scenarios: {exc}") from exc
    registered: list[dict[str, str]] = []
    for scenario in scenarios:
        try:
            source = scenario.path.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            raise CoverageDashboardError(
                "registered scenario source escaped the repository root"
            ) from exc
        registered.append({"scenario": scenario.key, "source": source})
    return sorted(registered, key=lambda item: item["scenario"])


def discover_result_evidence(
    evidence_roots: Sequence[Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    roots: list[dict[str, Any]] = []
    seen_files: set[Path] = set()
    for index, raw_root in enumerate(evidence_roots, start=1):
        root = raw_root.resolve()
        if not root.is_dir():
            raise CoverageDashboardError(f"evidence root {index} is not a directory")
        root_id = f"evidence-{index}"
        result_paths = sorted(root.rglob("result.json"))
        roots.append({"id": root_id, "result_files": len(result_paths)})
        for path in result_paths:
            resolved = path.resolve()
            if resolved in seen_files:
                continue
            seen_files.add(resolved)
            relative = resolved.relative_to(root).as_posix()
            try:
                payload = _read_json(resolved)
                if not isinstance(payload, Mapping):
                    raise CoverageDashboardError("result envelope root must be an object")
                valid.append(
                    normalize_result(
                        payload,
                        root_id=root_id,
                        relative_path=relative,
                    )
                )
            except CoverageDashboardError as exc:
                invalid.append(
                    {
                        "source": {"root_id": root_id, "path": relative},
                        "error": str(exc),
                    }
                )
    valid.sort(
        key=lambda item: (
            item["scenario"],
            item["ended_at_epoch"],
            item["run_id"],
            item["source"]["root_id"],
            item["source"]["path"],
        )
    )
    invalid.sort(key=lambda item: (item["source"]["root_id"], item["source"]["path"]))
    return valid, invalid, roots


def _evidence_reference(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "run_id": item["run_id"],
        "status": item["status"],
        "evidence_maturity": item["evidence_maturity"],
        "started_at": item["started_at"],
        "ended_at": item["ended_at"],
        "duration_ms": item["duration_ms"],
        "execution_tier": item["execution_tier"],
        "server_revision": item["server_revision"],
        "client_revision": item["client_revision"],
        "datapack": item["datapack"],
        "cleanup": item["cleanup"],
        "warnings": item["warnings"],
        "unknowns": item["unknowns"],
        "source": item["source"],
    }


def _strongest_maturity(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    candidates = [
        item
        for item in items
        if item["status"] == "success" and item["evidence_maturity"] in MATURITY_RANK
    ]
    if not candidates:
        return {"level": "not-proven", "evidence": None}
    selected = max(
        candidates,
        key=lambda item: (
            MATURITY_RANK[item["evidence_maturity"]],
            item["ended_at_epoch"],
            item["run_id"],
        ),
    )
    return {
        "level": selected["evidence_maturity"],
        "evidence": _evidence_reference(selected),
    }


def _quality_coverage(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for dimension in QUALITY_DIMENSIONS:
        evaluated = [
            item
            for item in items
            if item["quality_dimensions"][dimension] != "not-evaluated"
        ]
        if not evaluated:
            result[dimension] = {"state": "not-evaluated", "evidence": None}
            continue
        selected = max(
            evaluated,
            key=lambda item: (
                item["ended_at_epoch"],
                item["run_id"],
                item["source"]["root_id"],
                item["source"]["path"],
            ),
        )
        result[dimension] = {
            "state": selected["quality_dimensions"][dimension],
            "evidence": _evidence_reference(selected),
        }
    return result


def _freshness(
    items: Sequence[Mapping[str, Any]],
    *,
    as_of: datetime,
    stale_after_days: int | None,
) -> dict[str, Any]:
    if not items:
        return {"status": "missing", "age_days": None, "latest_ended_at": None}
    latest = max(items, key=lambda item: (item["ended_at_epoch"], item["run_id"]))
    ended = datetime.fromtimestamp(latest["ended_at_epoch"], timezone.utc)
    age_seconds = max(0.0, (as_of - ended).total_seconds())
    age_days = round(age_seconds / 86400.0, 3)
    if stale_after_days is None:
        status = "not-evaluated"
    else:
        status = "stale" if age_seconds > stale_after_days * 86400 else "current"
    return {
        "status": status,
        "age_days": age_days,
        "latest_ended_at": latest["ended_at"],
    }


def _gaps(
    *,
    registered: bool,
    items: Sequence[Mapping[str, Any]],
    strongest: Mapping[str, Any],
    dimensions: Mapping[str, Any],
    freshness: Mapping[str, Any],
) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    if not registered:
        gaps.append(
            {
                "code": "unregistered-scenario-evidence",
                "detail": "Retained evidence exists for a scenario absent from current discovery.",
            }
        )
    if not items:
        gaps.append(
            {
                "code": "missing-result-evidence",
                "detail": "No valid retained schema-v3 result envelope was supplied.",
            }
        )
    elif not any(item["status"] == "success" for item in items):
        gaps.append(
            {
                "code": "no-successful-run",
                "detail": "Retained evidence contains no successful run.",
            }
        )
    if strongest["level"] == "not-proven":
        gaps.append(
            {
                "code": "maturity-not-proven",
                "detail": "No successful retained run proves M0-M5 maturity.",
            }
        )
    if freshness["status"] == "stale":
        gaps.append(
            {
                "code": "stale-evidence",
                "detail": "The latest retained run exceeds the explicit freshness policy.",
            }
        )
    for name in QUALITY_DIMENSIONS:
        state = dimensions[name]["state"]
        if state == "pass":
            continue
        gaps.append(
            {
                "code": f"quality-dimension-{state}",
                "detail": f"{name} is {state} in the latest retained evaluated evidence.",
            }
        )
    return sorted(gaps, key=lambda item: (item["code"], item["detail"]))


def build_report(
    *,
    registered_scenarios: Sequence[Mapping[str, str]],
    evidence: Sequence[Mapping[str, Any]],
    invalid_evidence: Sequence[Mapping[str, Any]],
    evidence_roots: Sequence[Mapping[str, Any]],
    as_of: datetime,
    stale_after_days: int | None = None,
) -> dict[str, Any]:
    as_of = as_of.astimezone(timezone.utc)
    if stale_after_days is not None and (
        isinstance(stale_after_days, bool) or stale_after_days < 0
    ):
        raise CoverageDashboardError("stale_after_days must be a non-negative integer")
    registered_index: dict[str, str] = {}
    for raw in registered_scenarios:
        key = raw.get("scenario")
        source = raw.get("source")
        if not isinstance(key, str) or key.count("/") != 1:
            raise CoverageDashboardError("registered scenario key must be suite/scenario_id")
        if not isinstance(source, str) or not source:
            raise CoverageDashboardError("registered scenario source must be repository-relative")
        if key in registered_index:
            raise CoverageDashboardError(f"duplicate registered scenario: {key}")
        registered_index[key] = source

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in evidence:
        key = item.get("scenario")
        if not isinstance(key, str):
            raise CoverageDashboardError("normalized evidence is missing scenario identity")
        grouped[key].append(item)
    scenario_keys = sorted(set(registered_index) | set(grouped))
    rows: list[dict[str, Any]] = []
    for key in scenario_keys:
        items = sorted(
            grouped.get(key, []),
            key=lambda item: (
                item["ended_at_epoch"],
                item["run_id"],
                item["source"]["root_id"],
                item["source"]["path"],
            ),
        )
        latest = items[-1] if items else None
        successes = [item for item in items if item["status"] == "success"]
        failures = [item for item in items if item["status"] != "success"]
        strongest = _strongest_maturity(items)
        dimensions = _quality_coverage(items)
        freshness = _freshness(
            items, as_of=as_of, stale_after_days=stale_after_days
        )
        registered = key in registered_index
        rows.append(
            {
                "scenario": key,
                "registered": registered,
                "scenario_source": registered_index.get(key),
                "retained_result_count": len(items),
                "strongest_proven_maturity": strongest,
                "quality_dimensions": dimensions,
                "latest_run": _evidence_reference(latest) if latest else None,
                "last_success": _evidence_reference(successes[-1])
                if successes
                else None,
                "last_failure": _evidence_reference(failures[-1])
                if failures
                else None,
                "freshness": freshness,
                "warnings": sorted(
                    {warning for item in items for warning in item["warnings"]}
                ),
                "unknowns": sorted(
                    {unknown for item in items for unknown in item["unknowns"]}
                ),
                "coverage_gaps": _gaps(
                    registered=registered,
                    items=items,
                    strongest=strongest,
                    dimensions=dimensions,
                    freshness=freshness,
                ),
            }
        )

    maturity_counts = Counter(
        row["strongest_proven_maturity"]["level"] for row in rows
    )
    status_counts = Counter(
        item["status"] for item in evidence if item.get("status") in RESULT_STATUSES
    )
    dimension_counts = {
        dimension: dict(
            sorted(
                Counter(
                    row["quality_dimensions"][dimension]["state"] for row in rows
                ).items()
            )
        )
        for dimension in QUALITY_DIMENSIONS
    }
    report = {
        "contract": CONTRACT,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _format_timestamp(as_of),
        "evidence_boundary": {
            "source": "explicit-local-extracted-artifact-roots",
            "roots": list(evidence_roots),
            "valid_result_count": len(evidence),
            "invalid_result_count": len(invalid_evidence),
            "collection_and_retention": "external-to-this-contract",
        },
        "freshness_policy": {
            "as_of": _format_timestamp(as_of),
            "stale_after_days": stale_after_days,
            "status_without_threshold": "not-evaluated",
        },
        "summary": {
            "registered_scenarios": len(registered_index),
            "reported_scenarios": len(rows),
            "scenarios_with_valid_evidence": sum(
                row["retained_result_count"] > 0 for row in rows
            ),
            "scenarios_with_success": sum(row["last_success"] is not None for row in rows),
            "maturity_counts": dict(sorted(maturity_counts.items())),
            "run_status_counts": dict(sorted(status_counts.items())),
            "quality_state_counts": dimension_counts,
            "coverage_gap_count": sum(len(row["coverage_gaps"]) for row in rows),
        },
        "scenarios": rows,
        "invalid_evidence": list(invalid_evidence),
    }
    validate_report(report)
    return report


def validate_report(report: Mapping[str, Any]) -> None:
    if report.get("contract") != CONTRACT or report.get("schema_version") != SCHEMA_VERSION:
        raise CoverageDashboardError("unsupported coverage dashboard contract or schema")
    _parse_timestamp(report.get("generated_at"), "generated_at")
    scenarios = report.get("scenarios")
    if not isinstance(scenarios, list):
        raise CoverageDashboardError("scenarios must be an array")
    keys: list[str] = []
    for index, row in enumerate(scenarios):
        if not isinstance(row, Mapping):
            raise CoverageDashboardError(f"scenarios[{index}] must be an object")
        key = row.get("scenario")
        if not isinstance(key, str) or key.count("/") != 1:
            raise CoverageDashboardError(f"scenarios[{index}].scenario is invalid")
        keys.append(key)
        dimensions = row.get("quality_dimensions")
        if not isinstance(dimensions, Mapping) or set(dimensions) != set(
            QUALITY_DIMENSIONS
        ):
            raise CoverageDashboardError(
                f"scenarios[{index}].quality_dimensions is incomplete"
            )
        for name, detail in dimensions.items():
            if not isinstance(detail, Mapping) or detail.get("state") not in QUALITY_STATES:
                raise CoverageDashboardError(
                    f"scenarios[{index}].quality_dimensions.{name} is invalid"
                )
        freshness = row.get("freshness")
        if not isinstance(freshness, Mapping) or freshness.get("status") not in FRESHNESS_STATES:
            raise CoverageDashboardError(f"scenarios[{index}].freshness is invalid")
        strongest = row.get("strongest_proven_maturity")
        if not isinstance(strongest, Mapping) or strongest.get("level") not in {
            *MATURITY_LEVELS,
            "not-proven",
        }:
            raise CoverageDashboardError(
                f"scenarios[{index}].strongest_proven_maturity is invalid"
            )
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise CoverageDashboardError("scenario rows must be unique and sorted")
    invalid = report.get("invalid_evidence")
    if not isinstance(invalid, list):
        raise CoverageDashboardError("invalid_evidence must be an array")


def render_markdown(report: Mapping[str, Any]) -> str:
    validate_report(report)
    summary = report["summary"]
    policy = report["freshness_policy"]
    lines = [
        "# Universal E2E factual coverage dashboard",
        "",
        f"- Contract: `{CONTRACT}` schema `{SCHEMA_VERSION}`",
        f"- As of: `{report['generated_at']}`",
        f"- Freshness threshold: `{policy['stale_after_days']}` days"
        if policy["stale_after_days"] is not None
        else "- Freshness threshold: `not evaluated`",
        f"- Registered scenarios: `{summary['registered_scenarios']}`",
        f"- Scenarios with valid evidence: `{summary['scenarios_with_valid_evidence']}`",
        f"- Valid retained runs: `{report['evidence_boundary']['valid_result_count']}`",
        f"- Invalid retained results: `{report['evidence_boundary']['invalid_result_count']}`",
        "",
        "No score is calculated. Registration, maturity and quality dimensions remain independent factual fields.",
        "",
        "## Scenario coverage",
        "",
        "| Scenario | Registered | Strongest proven | Latest status | Freshness | Gaps |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["scenarios"]:
        latest = row["latest_run"]
        latest_status = latest["status"] if latest else "missing"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['scenario']}`",
                    "yes" if row["registered"] else "no",
                    row["strongest_proven_maturity"]["level"],
                    latest_status,
                    row["freshness"]["status"],
                    str(len(row["coverage_gaps"])),
                ]
            )
            + " |"
        )
    for row in report["scenarios"]:
        lines.extend(["", f"### `{row['scenario']}`", ""])
        if row["scenario_source"]:
            lines.append(f"Registered source: `{row['scenario_source']}`")
        else:
            lines.append("Registered source: `missing from current discovery`")
        lines.extend(
            [
                "",
                f"Strongest proven maturity: **{row['strongest_proven_maturity']['level']}**",
                "",
                "Quality dimensions:",
                "",
            ]
        )
        for dimension in QUALITY_DIMENSIONS:
            detail = row["quality_dimensions"][dimension]
            evidence = detail["evidence"]
            suffix = (
                f" (`{evidence['run_id']}`, `{evidence['ended_at']}`)"
                if evidence
                else ""
            )
            lines.append(f"- `{dimension}`: **{detail['state']}**{suffix}")
        lines.extend(["", "Coverage gaps:", ""])
        if row["coverage_gaps"]:
            for gap in row["coverage_gaps"]:
                lines.append(f"- `{gap['code']}` — {gap['detail']}")
        else:
            lines.append("- none in the supplied evidence boundary")
        if row["warnings"]:
            lines.extend(["", "Retained warnings:", ""])
            lines.extend(f"- {item}" for item in row["warnings"])
        if row["unknowns"]:
            lines.extend(["", "Retained unknowns:", ""])
            lines.extend(f"- {item}" for item in row["unknowns"])
    if report["invalid_evidence"]:
        lines.extend(["", "## Invalid evidence", ""])
        for item in report["invalid_evidence"]:
            source = item["source"]
            lines.append(
                f"- `{source['root_id']}:{source['path']}` — {item['error']}"
            )
    lines.append("")
    return "\n".join(lines)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and validate the factual Universal E2E coverage dashboard."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("--repo-root", type=Path, default=repository_root())
    build.add_argument("--evidence-root", type=Path, action="append", required=True)
    build.add_argument("--as-of", required=True)
    build.add_argument("--stale-after-days", type=int)
    build.add_argument("--json-output", type=Path, required=True)
    build.add_argument("--markdown-output", type=Path, required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("path", type=Path)

    render = subparsers.add_parser("render")
    render.add_argument("path", type=Path)
    render.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "build":
            registered = discover_registered_scenarios(args.repo_root)
            evidence, invalid, roots = discover_result_evidence(args.evidence_root)
            report = build_report(
                registered_scenarios=registered,
                evidence=evidence,
                invalid_evidence=invalid,
                evidence_roots=roots,
                as_of=_parse_timestamp(args.as_of, "--as-of"),
                stale_after_days=args.stale_after_days,
            )
            _write_text(args.json_output, serialize_report(report))
            _write_text(args.markdown_output, render_markdown(report))
            print(
                f"Built {CONTRACT} schema {SCHEMA_VERSION}: "
                f"{len(report['scenarios'])} scenarios, "
                f"{report['evidence_boundary']['valid_result_count']} valid runs, "
                f"{report['evidence_boundary']['invalid_result_count']} invalid results"
            )
        elif args.command == "validate":
            payload = _read_json(args.path)
            if not isinstance(payload, Mapping):
                raise CoverageDashboardError("dashboard root must be an object")
            validate_report(payload)
            print(f"Validated {args.path}: {CONTRACT} schema {SCHEMA_VERSION}")
        elif args.command == "render":
            payload = _read_json(args.path)
            if not isinstance(payload, Mapping):
                raise CoverageDashboardError("dashboard root must be an object")
            _write_text(args.output, render_markdown(payload))
        else:  # pragma: no cover
            raise CoverageDashboardError(f"unsupported command: {args.command}")
    except (CoverageDashboardError, OSError) as exc:
        print(f"coverage dashboard error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
