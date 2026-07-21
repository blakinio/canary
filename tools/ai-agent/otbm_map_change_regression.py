from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

REPORT_FORMAT = "canary-otbm-map-change-regression-v1"
SCHEMA_VERSION = 1
SEMANTIC_DIFF_FORMAT = "canary-otbm-semantic-diff-v1"
IMPACTED_SELECTION_FORMAT = "canary-otbm-e2e-impacted-selection-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FINDING_ID_RE = re.compile(r"^otbm-diff:[0-9a-f]{24}$")

STATIC_VALIDATORS = (
    "otbm-geometry-audit",
    "otbm-reachability",
    "otbm-script-resolution",
    "quest-map-validation",
    "otbm-spawn-npc-validation",
    "otbm-storage-dependency-graph",
    "otbm-map-quality",
)

KNOWN_CLASSIFICATIONS = {
    "added",
    "removed",
    "changed",
    "unchanged",
    "walkability-regression",
    "walkability-improvement",
    "handler-affected",
    "quest-evidence-affected",
    "spawn-npc-evidence-affected",
    "storage-evidence-affected",
    "unresolved",
    "conflicting",
    "truncated",
    "invalid-input",
}

KNOWN_FINDING_KINDS = {
    "tile-added",
    "tile-removed",
    "tile-kind-changed",
    "tile-flags-changed",
    "house-id-changed",
    "stack-order-changed",
    "item-replaced",
    "item-removed",
    "item-added",
    "mechanic-added",
    "mechanic-removed",
    "teleport-source-added",
    "teleport-source-removed",
    "teleport-destination-changed",
    "action-id-changed",
    "unique-id-changed",
    "house-door-id-changed",
    "strict-to-conditional",
    "strict-walkable-to-blocked",
    "conditional-to-strict",
    "blocked-to-strict-walkable",
    "optimistic-walkable-to-blocked",
    "ground-removed",
    "ground-added",
    "ground-changed",
    "static-blocker-added",
    "static-blocker-removed",
    "conditional-blocker-added",
    "conditional-blocker-removed",
    "unknown-appearance-added",
    "unknown-appearance-removed",
}

MECHANIC_FINDING_KINDS = {
    "mechanic-added",
    "mechanic-removed",
    "teleport-source-added",
    "teleport-source-removed",
    "teleport-destination-changed",
    "action-id-changed",
    "unique-id-changed",
    "house-door-id-changed",
}

FAIL_CLOSED_CLASSIFICATIONS = {"unresolved", "conflicting", "truncated", "invalid-input"}


class RegressionGuardError(ValueError):
    """Raised when existing change-impact evidence cannot safely authorize a regression plan."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RegressionGuardError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise RegressionGuardError(f"{label} must be an array")
    return value


def _non_negative(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RegressionGuardError(f"{label} must be a non-negative integer")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise RegressionGuardError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _position(value: Any, label: str, *, nullable: bool = False) -> list[int] | None:
    if nullable and value is None:
        return None
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 3:
        raise RegressionGuardError(f"{label} must be an [x,y,z] position")
    if any(isinstance(part, bool) or not isinstance(part, int) for part in value):
        raise RegressionGuardError(f"{label} must contain integers")
    x, y, z = (int(part) for part in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise RegressionGuardError(f"{label} is outside OTBM coordinate bounds")
    return [x, y, z]


def _pin(value: Any, label: str, expected_format: str) -> dict[str, Any]:
    pin = _mapping(value, label)
    file_name = pin.get("fileName")
    if not isinstance(file_name, str) or not file_name:
        raise RegressionGuardError(f"{label}.fileName must be a non-empty string")
    if pin.get("format") != expected_format:
        raise RegressionGuardError(f"{label}.format must be {expected_format}")
    return {
        "fileName": file_name,
        "size": _non_negative(pin.get("size"), f"{label}.size"),
        "sha256": _sha256(pin.get("sha256"), f"{label}.sha256"),
        "format": expected_format,
    }


def _index_identity(value: Any, label: str) -> tuple[str, str]:
    provenance = _mapping(value, label)
    source_map = _mapping(provenance.get("sourceMap"), f"{label}.sourceMap")
    world_index = _mapping(provenance.get("worldIndex"), f"{label}.worldIndex")
    return (
        _sha256(source_map.get("sha256"), f"{label}.sourceMap.sha256"),
        _sha256(world_index.get("sha256"), f"{label}.worldIndex.sha256"),
    )


def _finding_summary(value: Any) -> dict[str, Any]:
    summary = _mapping(value, "semanticDiff.summary.findings")
    by_kind_raw = _mapping(summary.get("byKind"), "semanticDiff.summary.findings.byKind")
    by_classification_raw = _mapping(
        summary.get("byClassification"),
        "semanticDiff.summary.findings.byClassification",
    )
    by_evidence_raw = _mapping(summary.get("byEvidenceLevel"), "semanticDiff.summary.findings.byEvidenceLevel")
    by_kind = {
        str(key): _non_negative(count, f"semanticDiff.summary.findings.byKind.{key}")
        for key, count in by_kind_raw.items()
        if isinstance(key, str) and key
    }
    if len(by_kind) != len(by_kind_raw):
        raise RegressionGuardError("semanticDiff.summary.findings.byKind keys must be non-empty strings")
    by_classification = {
        str(key): _non_negative(count, f"semanticDiff.summary.findings.byClassification.{key}")
        for key, count in by_classification_raw.items()
        if isinstance(key, str) and key
    }
    if len(by_classification) != len(by_classification_raw):
        raise RegressionGuardError("semanticDiff.summary.findings.byClassification keys must be non-empty strings")
    unknown_classes = sorted(set(by_classification) - KNOWN_CLASSIFICATIONS)
    if unknown_classes:
        raise RegressionGuardError(f"semanticDiff has unsupported finding classifications: {unknown_classes}")
    by_evidence = {
        str(key): _non_negative(count, f"semanticDiff.summary.findings.byEvidenceLevel.{key}")
        for key, count in by_evidence_raw.items()
        if isinstance(key, str) and key
    }
    if len(by_evidence) != len(by_evidence_raw):
        raise RegressionGuardError("semanticDiff.summary.findings.byEvidenceLevel keys must be non-empty strings")
    total = _non_negative(summary.get("total"), "semanticDiff.summary.findings.total")
    sample_count = _non_negative(summary.get("sampleCount"), "semanticDiff.summary.findings.sampleCount")
    truncated = summary.get("truncated")
    if not isinstance(truncated, bool):
        raise RegressionGuardError("semanticDiff.summary.findings.truncated must be boolean")
    if sum(by_kind.values()) != total:
        raise RegressionGuardError("semanticDiff finding kind totals do not match findings.total")
    if sample_count > total:
        raise RegressionGuardError("semanticDiff finding sampleCount exceeds findings.total")
    return {
        "total": total,
        "sampleCount": sample_count,
        "truncated": truncated,
        "byKind": dict(sorted(by_kind.items())),
        "byClassification": dict(sorted(by_classification.items())),
        "byEvidenceLevel": dict(sorted(by_evidence.items())),
    }


def _normalize_finding(value: Any, index: int) -> dict[str, Any]:
    finding = _mapping(value, f"semanticDiff.findings[{index}]")
    finding_id = finding.get("id")
    if not isinstance(finding_id, str) or FINDING_ID_RE.fullmatch(finding_id) is None:
        raise RegressionGuardError(f"semanticDiff.findings[{index}].id is invalid")
    kind = finding.get("kind")
    if not isinstance(kind, str) or not kind:
        raise RegressionGuardError(f"semanticDiff.findings[{index}].kind must be a non-empty string")
    raw_classifications = _array(finding.get("classifications"), f"semanticDiff.findings[{index}].classifications")
    classifications: list[str] = []
    for classification in raw_classifications:
        if not isinstance(classification, str) or classification not in KNOWN_CLASSIFICATIONS:
            raise RegressionGuardError(
                f"semanticDiff.findings[{index}] has unsupported classification {classification!r}"
            )
        classifications.append(classification)
    if len(set(classifications)) != len(classifications):
        raise RegressionGuardError(f"semanticDiff.findings[{index}].classifications contains duplicates")
    position = _position(finding.get("position"), f"semanticDiff.findings[{index}].position", nullable=True)
    details = _mapping(finding.get("details"), f"semanticDiff.findings[{index}].details")
    correlations = _array(finding.get("correlations"), f"semanticDiff.findings[{index}].correlations")
    normalized = {
        "id": finding_id,
        "kind": kind,
        "classifications": sorted(classifications),
        "evidenceLevel": str(finding.get("evidenceLevel", "")),
        "position": position,
        "before": finding.get("before"),
        "after": finding.get("after"),
        "details": dict(details),
        "message": str(finding.get("message", "")),
        "correlations": [dict(_mapping(entry, f"semanticDiff.findings[{index}].correlations[]")) for entry in correlations],
    }
    if not normalized["message"]:
        raise RegressionGuardError(f"semanticDiff.findings[{index}].message must be non-empty")
    return normalized


def _semantic_diff_identity(report: Mapping[str, Any]) -> dict[str, Any]:
    if report.get("format") != SEMANTIC_DIFF_FORMAT or report.get("schemaVersion") != 1:
        raise RegressionGuardError(f"semantic diff must use {SEMANTIC_DIFF_FORMAT} schemaVersion 1")
    if report.get("ok") is not True:
        raise RegressionGuardError("semantic diff must be ok=true")
    compatibility = _mapping(report.get("compatibility"), "semanticDiff.compatibility")
    if compatibility.get("compatible") is not True:
        raise RegressionGuardError("semantic diff compatibility must be explicitly true")
    provenance = _mapping(report.get("provenance"), "semanticDiff.provenance")
    before_map, before_index = _index_identity(provenance.get("before"), "semanticDiff.provenance.before")
    after_map, after_index = _index_identity(provenance.get("after"), "semanticDiff.provenance.after")
    scope = _mapping(report.get("scope"), "semanticDiff.scope")
    scope_type = scope.get("type")
    if scope_type not in {"full-index", "bounded-region"}:
        raise RegressionGuardError("semanticDiff.scope.type must be full-index or bounded-region")
    lower = _position(scope.get("from"), "semanticDiff.scope.from", nullable=True)
    upper = _position(scope.get("to"), "semanticDiff.scope.to", nullable=True)
    if scope_type == "full-index" and (lower is not None or upper is not None):
        raise RegressionGuardError("full-index Semantic Diff must not have bounded coordinates")
    if scope_type == "bounded-region" and (lower is None or upper is None):
        raise RegressionGuardError("bounded-region Semantic Diff must include from/to coordinates")
    summary = _mapping(report.get("summary"), "semanticDiff.summary")
    finding_summary = _finding_summary(summary.get("findings"))
    findings = [_normalize_finding(item, index) for index, item in enumerate(_array(report.get("findings"), "semanticDiff.findings"))]
    ids = [finding["id"] for finding in findings]
    if len(set(ids)) != len(ids):
        raise RegressionGuardError("semanticDiff.findings contains duplicate IDs")
    if len(findings) != finding_summary["sampleCount"]:
        raise RegressionGuardError("semanticDiff findings array length does not match summary sampleCount")
    if not finding_summary["truncated"] and len(findings) != finding_summary["total"]:
        raise RegressionGuardError("non-truncated Semantic Diff must contain every finding")
    correlation = _mapping(report.get("correlation"), "semanticDiff.correlation")
    reports = _array(correlation.get("reports"), "semanticDiff.correlation.reports")
    correlation_roles: list[str] = []
    for index, raw_entry in enumerate(reports):
        entry = _mapping(raw_entry, f"semanticDiff.correlation.reports[{index}]")
        role = entry.get("role")
        if not isinstance(role, str) or not role:
            raise RegressionGuardError(f"semanticDiff.correlation.reports[{index}].role must be non-empty")
        correlation_roles.append(role)
    changed_positions = _non_negative(summary.get("changedPositions"), "semanticDiff.summary.changedPositions")
    return {
        "beforeMapSha256": before_map,
        "afterMapSha256": after_map,
        "beforeWorldIndexSha256": before_index,
        "afterWorldIndexSha256": after_index,
        "scopeType": scope_type,
        "scopeFrom": lower,
        "scopeTo": upper,
        "changedPositions": changed_positions,
        "findingSummary": finding_summary,
        "findings": findings,
        "correlationRoles": sorted(set(correlation_roles)),
    }


def _impact_regions(positions: Sequence[list[int]]) -> list[dict[str, Any]]:
    by_floor: dict[int, list[list[int]]] = {}
    for position in positions:
        by_floor.setdefault(position[2], []).append(position)
    regions: list[dict[str, Any]] = []
    for z in sorted(by_floor):
        floor_positions = by_floor[z]
        regions.append(
            {
                "from": [min(position[0] for position in floor_positions), min(position[1] for position in floor_positions), z],
                "to": [max(position[0] for position in floor_positions), max(position[1] for position in floor_positions), z],
                "sampledPositionCount": len(floor_positions),
            }
        )
    return regions


def _static_plan(identity: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    findings: list[dict[str, Any]] = list(identity["findings"])
    summary = _mapping(identity["findingSummary"], "findingSummary")
    total = int(summary["total"])
    truncated = bool(summary["truncated"])
    scope_type = str(identity["scopeType"])
    positions = sorted(
        {tuple(finding["position"]) for finding in findings if finding["position"] is not None},
        key=lambda position: (position[2], position[1], position[0]),
    )
    position_lists = [list(position) for position in positions]
    sampled_ids = sorted(finding["id"] for finding in findings)
    unknown_kind_ids = sorted(finding["id"] for finding in findings if finding["kind"] not in KNOWN_FINDING_KINDS)
    missing_position_ids = sorted(finding["id"] for finding in findings if finding["position"] is None)
    uncertain_ids = sorted(
        finding["id"]
        for finding in findings
        if FAIL_CLOSED_CLASSIFICATIONS.intersection(finding["classifications"])
    )

    reasons: list[str] = []
    fail_closed = False
    exact_no_change = total == 0 and scope_type == "full-index" and not truncated
    if scope_type != "full-index":
        reasons.append("SEMANTIC_DIFF_SCOPE_NOT_FULL_INDEX")
        fail_closed = True
    if truncated:
        reasons.append("SEMANTIC_DIFF_FINDINGS_TRUNCATED")
        fail_closed = True
    if missing_position_ids:
        reasons.append("SEMANTIC_DIFF_FINDING_POSITION_UNKNOWN")
        fail_closed = True
    if uncertain_ids:
        reasons.append("SEMANTIC_DIFF_UNRESOLVED_OR_CONFLICTING")
        fail_closed = True
    if unknown_kind_ids:
        reasons.append("SEMANTIC_DIFF_FINDING_KIND_UNKNOWN")
        fail_closed = True
    if total > 0:
        reasons.append("SEMANTIC_DIFF_HAS_FINDINGS")

    selected: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    if exact_no_change:
        for validator in STATIC_VALIDATORS:
            skipped.append(
                {
                    "validator": validator,
                    "reason": "EXACT_FULL_INDEX_DIFF_PROVES_NO_OTBM_CHANGE",
                    "skipAuthorized": True,
                }
            )
    else:
        for validator in STATIC_VALIDATORS:
            selected.append(
                {
                    "validator": validator,
                    "reasonCodes": reasons or ["NON_IMPACT_NOT_PROVEN"],
                    "impactedFindingIds": sampled_ids,
                    "findingIdsComplete": not truncated,
                    "selectionMode": "fail-closed" if fail_closed or total == 0 else "changed-map",
                }
            )

    mechanic_findings = [
        {
            "findingId": finding["id"],
            "kind": finding["kind"],
            "position": finding["position"],
            "before": finding["before"],
            "after": finding["after"],
            "details": finding["details"],
        }
        for finding in findings
        if finding["kind"] in MECHANIC_FINDING_KINDS
    ]
    impact = {
        "sampledFindingIds": sampled_ids,
        "sampledPositions": position_lists,
        "sampledRegions": _impact_regions(position_lists),
        "sampledMechanics": mechanic_findings,
        "coverageIncomplete": scope_type != "full-index" or truncated or bool(missing_position_ids),
        "unknownFindingKindIds": unknown_kind_ids,
        "missingPositionFindingIds": missing_position_ids,
        "uncertainFindingIds": uncertain_ids,
    }
    static = {
        "nonImpactProven": exact_no_change,
        "failClosed": fail_closed or (total == 0 and not exact_no_change),
        "reasonCodes": reasons,
        "selected": selected,
        "skipped": skipped,
    }
    return static, impact


def _reason_codes(value: Any, label: str) -> list[dict[str, str]]:
    reasons = _array(value, label)
    normalized: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, raw_reason in enumerate(reasons):
        reason = _mapping(raw_reason, f"{label}[{index}]")
        code = reason.get("code")
        if not isinstance(code, str) or not code:
            raise RegressionGuardError(f"{label}[{index}].code must be non-empty")
        detail = reason.get("detail", "")
        if not isinstance(detail, str):
            raise RegressionGuardError(f"{label}[{index}].detail must be a string")
        pair = (code, detail)
        if pair in seen:
            raise RegressionGuardError(f"{label} contains duplicate reason entries")
        seen.add(pair)
        entry = {"code": code}
        if detail:
            entry["detail"] = detail
        normalized.append(entry)
    normalized.sort(key=lambda item: (item["code"], item.get("detail", "")))
    return normalized


def _selection_plan(
    report: Mapping[str, Any] | None,
    *,
    pin: Mapping[str, Any] | None,
    identity: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if report is None:
        return (
            {
                "evidencePresent": False,
                "mode": "manual-selection-required",
                "manualSelectionRequired": True,
                "canSkipAny": False,
                "reasonCodes": ["IMPACTED_SELECTION_NOT_PROVIDED"],
                "summary": {
                    "scenarioCount": 0,
                    "selectedCount": 0,
                    "skippedCount": 0,
                    "failClosedCount": 0,
                },
                "scenarios": [],
            },
            None,
        )
    if pin is None:
        raise RegressionGuardError("impacted selection report requires an input pin")
    if report.get("format") != IMPACTED_SELECTION_FORMAT or report.get("schemaVersion") != 1:
        raise RegressionGuardError(f"impacted selection must use {IMPACTED_SELECTION_FORMAT} schemaVersion 1")
    if report.get("ok") is not True:
        raise RegressionGuardError("impacted selection must be ok=true")
    semantic = _mapping(report.get("semanticDiff"), "impactedSelection.semanticDiff")
    expected = {
        "beforeMapSha256": identity["beforeMapSha256"],
        "afterMapSha256": identity["afterMapSha256"],
        "beforeWorldIndexSha256": identity["beforeWorldIndexSha256"],
        "afterWorldIndexSha256": identity["afterWorldIndexSha256"],
        "scopeType": identity["scopeType"],
        "findingsTotal": identity["findingSummary"]["total"],
        "findingsTruncated": identity["findingSummary"]["truncated"],
    }
    if _sha256(semantic.get("sha256"), "impactedSelection.semanticDiff.sha256") != pin["semanticDiffSha256"]:
        raise RegressionGuardError("impacted selection does not pin the supplied Semantic Diff report")
    for key, expected_value in expected.items():
        if semantic.get(key) != expected_value:
            raise RegressionGuardError(f"impacted selection {key} does not match supplied Semantic Diff")

    scenarios = _array(report.get("scenarios"), "impactedSelection.scenarios")
    normalized_scenarios: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    sampled_finding_ids = {finding["id"] for finding in identity["findings"]}
    for index, raw_scenario in enumerate(scenarios):
        scenario = _mapping(raw_scenario, f"impactedSelection.scenarios[{index}]")
        suite = scenario.get("suite")
        scenario_id = scenario.get("id")
        if not isinstance(suite, str) or not suite or not isinstance(scenario_id, str) or not scenario_id:
            raise RegressionGuardError(f"impactedSelection.scenarios[{index}] requires non-empty suite/id")
        key = (suite, scenario_id)
        if key in seen:
            raise RegressionGuardError(f"duplicate impacted-selection scenario {suite}/{scenario_id}")
        seen.add(key)
        selected = scenario.get("selected")
        fail_closed = scenario.get("failClosed")
        decision = scenario.get("decision")
        if not isinstance(selected, bool) or not isinstance(fail_closed, bool):
            raise RegressionGuardError(f"impactedSelection.scenarios[{index}] selected/failClosed must be boolean")
        if decision not in {"selected", "skipped"} or selected != (decision == "selected"):
            raise RegressionGuardError(f"impactedSelection.scenarios[{index}] decision does not match selected")
        reasons = _reason_codes(scenario.get("reasons"), f"impactedSelection.scenarios[{index}].reasons")
        impacted_ids = _array(
            scenario.get("impactedFindingIds"),
            f"impactedSelection.scenarios[{index}].impactedFindingIds",
        )
        if any(not isinstance(item, str) or FINDING_ID_RE.fullmatch(item) is None for item in impacted_ids):
            raise RegressionGuardError(f"impactedSelection.scenarios[{index}] has invalid impacted finding ID")
        if not set(impacted_ids).issubset(sampled_finding_ids):
            raise RegressionGuardError(f"impactedSelection.scenarios[{index}] references unknown Semantic Diff finding IDs")
        route_plans = _array(scenario.get("routePlans"), f"impactedSelection.scenarios[{index}].routePlans")
        normalized_routes: list[dict[str, Any]] = []
        for route_index, raw_route in enumerate(route_plans):
            route = _mapping(raw_route, f"impactedSelection.scenarios[{index}].routePlans[{route_index}]")
            route_id = route.get("routeId")
            if not isinstance(route_id, str) or not route_id:
                raise RegressionGuardError("impacted selection routePlan.routeId must be non-empty")
            route_sha = route.get("sha256")
            if route_sha is not None:
                route_sha = _sha256(route_sha, "impacted selection routePlan.sha256")
            normalized_routes.append(
                {
                    "routeId": route_id,
                    "path": str(route.get("path", "")),
                    "sha256": route_sha,
                    "baselineCompatible": bool(route.get("baselineCompatible")),
                    "positionCount": _non_negative(route.get("positionCount"), "impacted selection routePlan.positionCount"),
                }
            )
        normalized_routes.sort(key=lambda item: item["routeId"])

        if not selected:
            reason_codes = {reason["code"] for reason in reasons}
            if fail_closed:
                raise RegressionGuardError("a skipped impacted-selection scenario cannot be failClosed")
            if "EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT" not in reason_codes:
                raise RegressionGuardError("every skipped scenario must retain exact full-index non-impact evidence")
            if impacted_ids:
                raise RegressionGuardError("a skipped scenario cannot retain impacted Semantic Diff finding IDs")
            if identity["scopeType"] != "full-index" or identity["findingSummary"]["truncated"]:
                raise RegressionGuardError("bounded or truncated Semantic Diff cannot authorize a physical scenario skip")
            if not normalized_routes or any(not route["baselineCompatible"] or route["sha256"] is None for route in normalized_routes):
                raise RegressionGuardError("every skipped scenario requires compatible SHA-pinned baseline route evidence")

        manifest = _mapping(scenario.get("manifest"), f"impactedSelection.scenarios[{index}].manifest")
        manifest_sha = _sha256(manifest.get("sha256"), f"impactedSelection.scenarios[{index}].manifest.sha256")
        normalized_scenarios.append(
            {
                "suite": suite,
                "id": scenario_id,
                "manifest": {"path": str(manifest.get("path", "")), "sha256": manifest_sha},
                "selected": selected,
                "decision": decision,
                "failClosed": fail_closed,
                "reasons": reasons,
                "impactedFindingIds": sorted(set(impacted_ids)),
                "routePlans": normalized_routes,
            }
        )

    normalized_scenarios.sort(key=lambda item: (item["suite"], item["id"]))
    selected_count = sum(1 for scenario in normalized_scenarios if scenario["selected"])
    skipped_count = len(normalized_scenarios) - selected_count
    fail_closed_count = sum(1 for scenario in normalized_scenarios if scenario["failClosed"])
    summary = _mapping(report.get("summary"), "impactedSelection.summary")
    expected_summary = {
        "scenarioCount": len(normalized_scenarios),
        "selectedCount": selected_count,
        "skippedCount": skipped_count,
        "failClosedCount": fail_closed_count,
    }
    for key, expected_value in expected_summary.items():
        if summary.get(key) != expected_value:
            raise RegressionGuardError(f"impacted selection summary.{key} is inconsistent")

    normalized_pin = {
        "input": {
            "fileName": pin["fileName"],
            "size": pin["size"],
            "sha256": pin["sha256"],
            "format": IMPACTED_SELECTION_FORMAT,
        },
        "semanticDiffSha256": pin["semanticDiffSha256"],
    }
    return (
        {
            "evidencePresent": True,
            "mode": "otbm-e2e-008",
            "manualSelectionRequired": False,
            "canSkipAny": skipped_count > 0,
            "reasonCodes": [],
            "summary": expected_summary,
            "scenarios": normalized_scenarios,
        },
        normalized_pin,
    )


def build_regression_plan(
    *,
    semantic_diff: Mapping[str, Any],
    impacted_selection: Mapping[str, Any] | None = None,
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    pins = _mapping(input_pins, "input_pins")
    semantic_pin = _pin(pins.get("semanticDiff"), "input_pins.semanticDiff", SEMANTIC_DIFF_FORMAT)
    selection_pin_raw = pins.get("impactedSelection")
    selection_pin: dict[str, Any] | None = None
    if impacted_selection is not None:
        selection_pin = _pin(selection_pin_raw, "input_pins.impactedSelection", IMPACTED_SELECTION_FORMAT)
        selection_pin["semanticDiffSha256"] = semantic_pin["sha256"]
    elif selection_pin_raw is not None:
        raise RegressionGuardError("impacted selection pin was supplied without an impacted selection report")
    if selection_pin is not None and selection_pin["sha256"] == semantic_pin["sha256"]:
        raise RegressionGuardError("Semantic Diff and impacted-selection report SHA-256 pins must be distinct")

    semantic_object = _mapping(semantic_diff, "semantic_diff")
    identity = _semantic_diff_identity(semantic_object)
    static_validation, impact = _static_plan(identity)
    physical_validation, normalized_selection_pin = _selection_plan(
        _mapping(impacted_selection, "impacted_selection") if impacted_selection is not None else None,
        pin=selection_pin,
        identity=identity,
    )

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "source": {
            "beforeMapSha256": identity["beforeMapSha256"],
            "afterMapSha256": identity["afterMapSha256"],
            "beforeWorldIndexSha256": identity["beforeWorldIndexSha256"],
            "afterWorldIndexSha256": identity["afterWorldIndexSha256"],
        },
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "semanticDiffRecomputed": False,
            "impactedSelectionRecomputed": False,
            "physicalE2eExecuted": False,
            "unrelatedNonOtbmSuitesSuppressed": False,
            "uncertaintySelectsMoreValidation": True,
            "selectedScopeAbsenceMeansGlobalAbsence": False,
            "visualSimilarityAuthorizesSkip": False,
            "skipRequiresExactFullIndexNonImpact": True,
        },
        "provenance": {
            "semanticDiff": {
                "input": semantic_pin,
                "beforeMapSha256": identity["beforeMapSha256"],
                "afterMapSha256": identity["afterMapSha256"],
                "beforeWorldIndexSha256": identity["beforeWorldIndexSha256"],
                "afterWorldIndexSha256": identity["afterWorldIndexSha256"],
            },
            "impactedSelection": normalized_selection_pin,
        },
        "semanticDiff": {
            "scopeType": identity["scopeType"],
            "from": identity["scopeFrom"],
            "to": identity["scopeTo"],
            "changedPositions": identity["changedPositions"],
            "findingsTotal": identity["findingSummary"]["total"],
            "findingSampleCount": identity["findingSummary"]["sampleCount"],
            "findingsTruncated": identity["findingSummary"]["truncated"],
            "correlationRoles": identity["correlationRoles"],
        },
        "impactEvidence": impact,
        "staticValidation": static_validation,
        "physicalValidation": physical_validation,
        "summary": {
            "staticValidatorCount": len(STATIC_VALIDATORS),
            "selectedStaticValidatorCount": len(static_validation["selected"]),
            "skippedStaticValidatorCount": len(static_validation["skipped"]),
            "physicalScenarioCount": physical_validation["summary"]["scenarioCount"],
            "selectedPhysicalScenarioCount": physical_validation["summary"]["selectedCount"],
            "skippedPhysicalScenarioCount": physical_validation["summary"]["skippedCount"],
            "failClosedPhysicalScenarioCount": physical_validation["summary"]["failClosedCount"],
            "manualPhysicalSelectionRequired": physical_validation["manualSelectionRequired"],
        },
        "notes": [
            "Static OTBM validators are skipped only when an exact full-index non-truncated Semantic Diff proves zero OTBM findings.",
            "Any changed, bounded, truncated, unknown-position, unresolved, conflicting or unknown-kind evidence selects static validation rather than authorizing a skip.",
            "Physical scenario decisions are reused from OTBM-E2E-008 and are not recomputed by this guard.",
            "A skipped Physical E2E scenario must retain exact full-index non-impact evidence and compatible SHA-pinned baseline route plans.",
            "This OTBM guard never suppresses unrelated non-OTBM suites and does not prove gameplay correctness or player intent.",
        ],
    }


def canonical_report_sha256(report: Mapping[str, Any]) -> str:
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
