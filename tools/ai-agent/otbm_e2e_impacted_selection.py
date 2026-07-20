#!/usr/bin/env python3
"""Select OTBM-aware Physical E2E scenarios impacted by Semantic OTBM Diff evidence.

This tool is a deterministic evidence bridge. It consumes an existing
canary-otbm-semantic-diff-v1 report, reviewed Universal E2E scenario manifests,
and existing canary-otbm-e2e-route-plan-v1 baseline plans. It does not parse
OTBM, build a World Index, calculate routes, or execute Physical E2E.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable, Sequence

FORMAT = "canary-otbm-e2e-impacted-selection-v1"
SCHEMA_VERSION = 1
SEMANTIC_DIFF_FORMAT = "canary-otbm-semantic-diff-v1"
ROUTE_PLAN_FORMAT = "canary-otbm-e2e-route-plan-v1"
MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_SCENARIOS = 256
MAX_ROUTES_PER_SCENARIO = 64
MAX_REASONS = 128


class SelectionError(ValueError):
    """Raised when selection inputs are malformed or unsupported."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        stat = path.stat()
    except OSError as exc:
        raise SelectionError(f"cannot stat {label} {path}: {exc}") from exc
    if not path.is_file():
        raise SelectionError(f"{label} must be a file: {path}")
    if path.is_symlink():
        raise SelectionError(f"{label} must not be a symlink: {path}")
    if stat.st_size > MAX_INPUT_BYTES:
        raise SelectionError(f"{label} exceeds {MAX_INPUT_BYTES} bytes: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SelectionError(f"cannot parse {label} {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SelectionError(f"{label} must contain a JSON object: {path}")
    return payload


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _position(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, list) or len(value) != 3:
        return None
    if any(not isinstance(item, int) or isinstance(item, bool) for item in value):
        return None
    x, y, z = value
    if not (0 <= x <= 65535 and 0 <= y <= 65535 and 0 <= z <= 15):
        return None
    return x, y, z


def _nested(mapping: dict[str, Any], *keys: str) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _semantic_diff_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("format") != SEMANTIC_DIFF_FORMAT or payload.get("schemaVersion") != 1:
        raise SelectionError(f"semantic diff must be {SEMANTIC_DIFF_FORMAT} schemaVersion 1")
    if payload.get("ok") is not True:
        raise SelectionError("semantic diff ok must be true")
    if _nested(payload, "compatibility", "compatible") is not True:
        raise SelectionError("semantic diff compatibility.compatible must be true")

    before_map = _nested(payload, "provenance", "before", "sourceMap", "sha256")
    after_map = _nested(payload, "provenance", "after", "sourceMap", "sha256")
    before_index = _nested(payload, "provenance", "before", "worldIndex", "sha256")
    after_index = _nested(payload, "provenance", "after", "worldIndex", "sha256")
    for label, value in (
        ("before source map", before_map),
        ("after source map", after_map),
        ("before World Index", before_index),
        ("after World Index", after_index),
    ):
        if not _is_sha256(value):
            raise SelectionError(f"semantic diff {label} SHA-256 is missing or invalid")

    scope_type = _nested(payload, "scope", "type")
    if scope_type not in {"full-index", "bounded-region"}:
        raise SelectionError("semantic diff scope.type must be full-index or bounded-region")

    findings = payload.get("findings")
    if not isinstance(findings, list):
        raise SelectionError("semantic diff findings must be an array")
    summary_findings = _nested(payload, "summary", "findings")
    if not isinstance(summary_findings, dict):
        raise SelectionError("semantic diff summary.findings must be an object")
    total = summary_findings.get("total")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise SelectionError("semantic diff summary.findings.total must be a non-negative integer")
    truncated = summary_findings.get("truncated")
    if not isinstance(truncated, bool):
        raise SelectionError("semantic diff summary.findings.truncated must be boolean")

    normalized_findings: list[dict[str, Any]] = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise SelectionError(f"semantic diff findings[{index}] must be an object")
        finding_id = finding.get("id")
        if not isinstance(finding_id, str) or not finding_id:
            raise SelectionError(f"semantic diff findings[{index}].id must be a non-empty string")
        raw_position = finding.get("position")
        normalized_findings.append(
            {
                "id": finding_id,
                "position": _position(raw_position),
                "positionMissing": raw_position is None or _position(raw_position) is None,
            }
        )

    return {
        "beforeMapSha256": before_map,
        "afterMapSha256": after_map,
        "beforeWorldIndexSha256": before_index,
        "afterWorldIndexSha256": after_index,
        "scopeType": scope_type,
        "truncated": truncated,
        "findings": normalized_findings,
        "findingsTotal": total,
    }


def _scenario_identity(payload: dict[str, Any], path: Path) -> tuple[str, str]:
    if payload.get("schema_version") != 1:
        raise SelectionError(f"scenario {path} schema_version must be 1")
    scenario_id = payload.get("id")
    suite = payload.get("suite")
    if not isinstance(scenario_id, str) or not scenario_id:
        raise SelectionError(f"scenario {path} id must be a non-empty string")
    if not isinstance(suite, str) or not suite:
        raise SelectionError(f"scenario {path} suite must be a non-empty string")
    return suite, scenario_id


def _follow_routes(payload: dict[str, Any], path: Path) -> list[str]:
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise SelectionError(f"scenario {path} steps must be an array")
    routes: list[str] = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise SelectionError(f"scenario {path} steps[{index}] must be an object")
        if step.get("action") != "follow_route":
            continue
        route = step.get("route")
        if not isinstance(route, str) or not route:
            raise SelectionError(f"scenario {path} follow_route step {index} route must be non-empty")
        routes.append(route)
    unique_routes = sorted(set(routes))
    if len(unique_routes) > MAX_ROUTES_PER_SCENARIO:
        raise SelectionError(f"scenario {path} exceeds {MAX_ROUTES_PER_SCENARIO} unique follow_route plans")
    return unique_routes


def _collect_positions(value: Any, *, key_hint: str = "") -> set[tuple[int, int, int]]:
    positions: set[tuple[int, int, int]] = set()
    direct = _position(value)
    if direct is not None and key_hint in {"position", "source", "destination", "from", "to"}:
        positions.add(direct)
        return positions
    if isinstance(value, dict):
        for key, item in value.items():
            positions.update(_collect_positions(item, key_hint=str(key)))
    elif isinstance(value, list):
        for item in value:
            positions.update(_collect_positions(item, key_hint=key_hint))
    return positions


def _route_plan_evidence(
    payload: dict[str, Any],
    path: Path,
    *,
    before_map_sha256: str,
    before_world_index_sha256: str,
) -> tuple[bool, set[tuple[int, int, int]], list[str]]:
    reasons: list[str] = []
    if payload.get("format") != ROUTE_PLAN_FORMAT or payload.get("schemaVersion") != 1:
        return False, set(), ["BASELINE_ROUTE_PLAN_FORMAT_INVALID"]
    if payload.get("executionStatus") != "executable" or payload.get("pathComplete") is not True:
        reasons.append("BASELINE_ROUTE_NOT_EXECUTABLE")

    map_sha = _nested(payload, "provenance", "map", "sha256")
    index_sha = _nested(payload, "provenance", "worldIndex", "sha256")
    if map_sha != before_map_sha256:
        reasons.append("BASELINE_ROUTE_MAP_PROVENANCE_STALE")
    if index_sha != before_world_index_sha256:
        reasons.append("BASELINE_ROUTE_WORLD_INDEX_PROVENANCE_STALE")

    raw_path = payload.get("path")
    if not isinstance(raw_path, list) or not raw_path:
        reasons.append("BASELINE_ROUTE_PATH_MISSING")
        route_positions: set[tuple[int, int, int]] = set()
    else:
        route_positions = set()
        for item in raw_path:
            pos = _position(item)
            if pos is None:
                reasons.append("BASELINE_ROUTE_PATH_POSITION_INVALID")
                break
            route_positions.add(pos)

    edges = payload.get("edges")
    if not isinstance(edges, list):
        reasons.append("BASELINE_ROUTE_EDGES_MISSING")
    else:
        route_positions.update(_collect_positions(edges))

    return not reasons, route_positions, sorted(set(reasons))


def _decision_reason(code: str, *, detail: str = "") -> dict[str, str]:
    result = {"code": code}
    if detail:
        result["detail"] = detail
    return result


def select_impacted_scenarios(
    *,
    semantic_diff_path: Path,
    scenario_paths: Iterable[Path],
    route_plan_root: Path,
) -> dict[str, Any]:
    semantic_diff_path = semantic_diff_path.resolve()
    route_plan_root = route_plan_root.resolve()
    diff_payload = _read_json(semantic_diff_path, "semantic diff")
    diff = _semantic_diff_evidence(diff_payload)

    paths = [path.resolve() for path in scenario_paths]
    if not paths:
        raise SelectionError("at least one --scenario is required")
    if len(paths) > MAX_SCENARIOS:
        raise SelectionError(f"scenario count exceeds {MAX_SCENARIOS}")

    scenarios: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    for scenario_path in paths:
        payload = _read_json(scenario_path, "scenario")
        suite, scenario_id = _scenario_identity(payload, scenario_path)
        key = (suite, scenario_id)
        if key in seen_keys:
            raise SelectionError(f"duplicate scenario identity: {suite}/{scenario_id}")
        seen_keys.add(key)
        routes = _follow_routes(payload, scenario_path)
        scenarios.append(
            {
                "suite": suite,
                "id": scenario_id,
                "path": scenario_path,
                "sha256": _sha256(scenario_path),
                "routes": routes,
            }
        )

    scenarios.sort(key=lambda item: (item["suite"], item["id"], str(item["path"])))
    finding_positions = {
        item["id"]: item["position"] for item in diff["findings"] if item["position"] is not None
    }
    unknown_position_ids = sorted(item["id"] for item in diff["findings"] if item["positionMissing"])

    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        selected = False
        fail_closed = False
        reasons: list[dict[str, str]] = []
        impacted_ids: set[str] = set()
        route_entries: list[dict[str, Any]] = []
        route_positions: set[tuple[int, int, int]] = set()

        if diff["scopeType"] != "full-index":
            selected = True
            fail_closed = True
            reasons.append(_decision_reason("SEMANTIC_DIFF_SCOPE_NOT_FULL_INDEX"))
        if diff["truncated"]:
            selected = True
            fail_closed = True
            reasons.append(_decision_reason("SEMANTIC_DIFF_FINDINGS_TRUNCATED"))
        if unknown_position_ids:
            selected = True
            fail_closed = True
            reasons.append(
                _decision_reason(
                    "SEMANTIC_DIFF_FINDING_POSITION_UNKNOWN",
                    detail=",".join(unknown_position_ids[:16]),
                )
            )

        if not scenario["routes"]:
            selected = True
            fail_closed = True
            reasons.append(_decision_reason("SCENARIO_FOLLOW_ROUTE_MISSING"))

        for route_id in scenario["routes"]:
            plan_path = route_plan_root / f"route-{route_id}.json"
            if not plan_path.is_file() or plan_path.is_symlink():
                selected = True
                fail_closed = True
                reasons.append(_decision_reason("BASELINE_ROUTE_PLAN_MISSING", detail=route_id))
                route_entries.append(
                    {
                        "routeId": route_id,
                        "path": str(plan_path),
                        "sha256": None,
                        "baselineCompatible": False,
                        "positionCount": 0,
                    }
                )
                continue
            try:
                plan_payload = _read_json(plan_path, "route plan")
            except SelectionError as exc:
                selected = True
                fail_closed = True
                reasons.append(_decision_reason("BASELINE_ROUTE_PLAN_INVALID", detail=f"{route_id}: {exc}"))
                route_entries.append(
                    {
                        "routeId": route_id,
                        "path": str(plan_path),
                        "sha256": None,
                        "baselineCompatible": False,
                        "positionCount": 0,
                    }
                )
                continue

            compatible, positions, route_reasons = _route_plan_evidence(
                plan_payload,
                plan_path,
                before_map_sha256=diff["beforeMapSha256"],
                before_world_index_sha256=diff["beforeWorldIndexSha256"],
            )
            route_positions.update(positions)
            route_entries.append(
                {
                    "routeId": route_id,
                    "path": str(plan_path),
                    "sha256": _sha256(plan_path),
                    "baselineCompatible": compatible,
                    "positionCount": len(positions),
                }
            )
            if not compatible:
                selected = True
                fail_closed = True
                for code in route_reasons:
                    reasons.append(_decision_reason(code, detail=route_id))

        if not fail_closed:
            for finding_id, position in finding_positions.items():
                if position in route_positions:
                    impacted_ids.add(finding_id)
            if impacted_ids:
                selected = True
                reasons.append(_decision_reason("SEMANTIC_DIFF_INTERSECTS_BASELINE_ROUTE"))
            else:
                reasons.append(_decision_reason("EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT"))

        if len(reasons) > MAX_REASONS:
            raise SelectionError(f"scenario {scenario['suite']}/{scenario['id']} produced too many decision reasons")
        deduped_reasons = []
        seen_reason_pairs: set[tuple[str, str]] = set()
        for reason in reasons:
            pair = (reason["code"], reason.get("detail", ""))
            if pair in seen_reason_pairs:
                continue
            seen_reason_pairs.add(pair)
            deduped_reasons.append(reason)
        deduped_reasons.sort(key=lambda item: (item["code"], item.get("detail", "")))
        route_entries.sort(key=lambda item: item["routeId"])
        results.append(
            {
                "suite": scenario["suite"],
                "id": scenario["id"],
                "manifest": {"path": str(scenario["path"]), "sha256": scenario["sha256"]},
                "selected": selected,
                "decision": "selected" if selected else "skipped",
                "failClosed": fail_closed,
                "reasons": deduped_reasons,
                "impactedFindingIds": sorted(impacted_ids),
                "routePlans": route_entries,
            }
        )

    selected_count = sum(1 for item in results if item["selected"])
    fail_closed_count = sum(1 for item in results if item["failClosed"])
    return {
        "format": FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": True,
        "semanticDiff": {
            "path": str(semantic_diff_path),
            "sha256": _sha256(semantic_diff_path),
            "beforeMapSha256": diff["beforeMapSha256"],
            "afterMapSha256": diff["afterMapSha256"],
            "beforeWorldIndexSha256": diff["beforeWorldIndexSha256"],
            "afterWorldIndexSha256": diff["afterWorldIndexSha256"],
            "scopeType": diff["scopeType"],
            "findingsTotal": diff["findingsTotal"],
            "findingsTruncated": diff["truncated"],
        },
        "policy": {
            "fullIndexRequiredForSkip": True,
            "truncatedDiffSelectsAll": True,
            "unknownFindingPositionSelectsAll": True,
            "staleOrMissingBaselineRouteSelectsScenario": True,
            "otbmParsed": False,
            "worldIndexBuilt": False,
            "routeCalculated": False,
            "physicalE2eExecuted": False,
            "mapModified": False,
        },
        "summary": {
            "scenarioCount": len(results),
            "selectedCount": selected_count,
            "skippedCount": len(results) - selected_count,
            "failClosedCount": fail_closed_count,
        },
        "scenarios": results,
    }


def _write_json(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    path = path.resolve()
    if path.exists() and not overwrite:
        raise SelectionError(f"output exists; pass --overwrite to replace it: {path}")
    if path.exists() and path.is_symlink():
        raise SelectionError(f"output must not be a symlink: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temp.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semantic-diff", type=Path, required=True)
    parser.add_argument("--scenario", type=Path, action="append", required=True)
    parser.add_argument("--route-plan-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = select_impacted_scenarios(
            semantic_diff_path=args.semantic_diff,
            scenario_paths=args.scenario,
            route_plan_root=args.route_plan_root,
        )
        _write_json(args.output, payload, args.overwrite)
    except SelectionError as exc:
        print(f"error: {exc}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
