from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable, Mapping, Sequence

TARGETS_FORMAT = "canary-otbm-coverage-dashboard-targets-v1"
REPORT_FORMAT = "canary-otbm-coverage-dashboard-v1"
COVERAGE_FORMAT = "canary-otbm-e2e-coverage-matrix-v1"
MAP_QUALITY_FORMAT = "canary-otbm-map-quality-v1"
WORLD_HEALTH_FORMAT = "canary-otbm-world-health-v1"
QUEST_VALIDATION_FORMAT = "canary-quest-map-validation-v1"
ROUTE_PLAN_FORMAT = "canary-otbm-e2e-route-plan-v1"
CANDIDATE_REPAIR_FORMAT = "canary-otbm-reviewed-candidate-repair-v1"
SCHEMA_VERSION = 1

TARGET_KINDS = {"world", "region", "landmark-route", "quest", "mechanic-set"}
REQUIRED_DIMENSIONS = {
    "indexed-on-exact-map",
    "source-correlated",
    "script-resolved",
    "statically-reachable",
    "interaction-resolved",
    "static-quality-compatible",
    "executable-route-covered",
    "physically-runtime-proven",
    "candidate-map-validated",
    "current-map-provenance",
}
DIMENSION_OUTPUT_KEYS = {
    "indexed-on-exact-map": "indexedOnExactMap",
    "source-correlated": "sourceCorrelated",
    "script-resolved": "scriptResolved",
    "statically-reachable": "staticallyReachable",
    "interaction-resolved": "interactionResolved",
    "static-quality-compatible": "staticQualityCompatible",
    "executable-route-covered": "executableRouteCovered",
    "physically-runtime-proven": "physicallyRuntimeProven",
    "candidate-map-validated": "candidateMapValidated",
}
DIMENSION_STATES = {"proven", "blocked", "stale", "not-evaluated", "not-applicable"}
CURRENT_PROVENANCE_STATES = {"current", "stale", "mixed", "not-evaluated"}


class CoverageDashboardError(ValueError):
    """Raised when dashboard evidence is malformed, incompatible, or overclaims proof."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_report_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CoverageDashboardError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise CoverageDashboardError(f"{label} must be an array")
    return value


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoverageDashboardError(f"{label} must be a non-empty string")
    return value.strip()


def _sha256(value: Any, label: str) -> str:
    if not _is_sha256(value):
        raise CoverageDashboardError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _position(value: Any, label: str) -> list[int]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(isinstance(part, bool) or not isinstance(part, int) for part in value)
    ):
        raise CoverageDashboardError(f"{label} must be an integer x,y,z array")
    x, y, z = value
    if not (0 <= x <= 65535 and 0 <= y <= 65535 and 0 <= z <= 15):
        raise CoverageDashboardError(f"{label} is outside the OTBM coordinate range")
    return [x, y, z]


def _region(value: Any, label: str) -> dict[str, list[int]]:
    region = _mapping(value, label)
    if set(region) != {"from", "to"}:
        raise CoverageDashboardError(f"{label} must contain exactly from/to")
    start = _position(region["from"], f"{label}.from")
    end = _position(region["to"], f"{label}.to")
    if any(start[index] > end[index] for index in range(3)):
        raise CoverageDashboardError(f"{label}.from must be <= to on every axis")
    return {"from": start, "to": end}


def _normalize_selector(value: Any, label: str) -> dict[str, Any]:
    selector = _mapping(value, label)
    allowed = {"position", "itemId", "actionId", "uniqueId", "houseDoorId", "teleportDestination"}
    unknown = set(selector) - allowed
    if unknown:
        raise CoverageDashboardError(f"{label} contains unsupported keys: {sorted(unknown)}")
    if "position" not in selector:
        raise CoverageDashboardError(f"{label}.position is required")
    normalized: dict[str, Any] = {"position": _position(selector["position"], f"{label}.position")}
    for key in ("itemId", "actionId", "uniqueId", "houseDoorId"):
        raw = selector.get(key)
        if raw is None:
            continue
        maximum = 255 if key == "houseDoorId" else 65535
        if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= maximum:
            raise CoverageDashboardError(f"{label}.{key} must be an integer in 0..{maximum}")
        normalized[key] = raw
    if selector.get("teleportDestination") is not None:
        normalized["teleportDestination"] = _position(
            selector["teleportDestination"], f"{label}.teleportDestination"
        )
    return normalized


def _input_pin(value: Any, expected_format: str, label: str) -> dict[str, Any]:
    pin = _mapping(value, f"{label} input pin")
    file_name = _non_empty_string(pin.get("fileName"), f"{label} input pin fileName")
    size = pin.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise CoverageDashboardError(f"{label} input pin size must be a non-negative integer")
    sha = _sha256(pin.get("sha256"), f"{label} input pin sha256")
    if pin.get("format") != expected_format:
        raise CoverageDashboardError(f"{label} input pin format must be {expected_format}")
    return {"fileName": file_name, "size": size, "sha256": sha, "format": expected_format}


def _optional_index(
    entries: Sequence[Mapping[str, Any]] | None,
    expected_format: str,
    label: str,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, raw_entry in enumerate(entries or []):
        entry = _mapping(raw_entry, f"{label}[{index}]")
        report = _mapping(entry.get("report"), f"{label}[{index}].report")
        pin = _input_pin(entry.get("pin"), expected_format, f"{label}[{index}]")
        if report.get("format") != expected_format:
            raise CoverageDashboardError(f"{label}[{index}] report format must be {expected_format}")
        if pin["sha256"] in result:
            raise CoverageDashboardError(f"duplicate {label} report SHA-256: {pin['sha256']}")
        result[pin["sha256"]] = {"report": report, "pin": pin}
    return result


def _normalize_targets(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("format") != TARGETS_FORMAT or manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise CoverageDashboardError(f"targets manifest must use {TARGETS_FORMAT} schemaVersion {SCHEMA_VERSION}")
    raw_targets = _list(manifest.get("targets"), "targets.targets")
    if not raw_targets:
        raise CoverageDashboardError("targets.targets must not be empty")
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_targets):
        target = _mapping(raw, f"targets[{index}]")
        target_id = _non_empty_string(target.get("id"), f"targets[{index}].id")
        if target_id in seen_ids:
            raise CoverageDashboardError(f"duplicate target id: {target_id}")
        seen_ids.add(target_id)
        kind = target.get("kind")
        if kind not in TARGET_KINDS:
            raise CoverageDashboardError(f"targets[{index}].kind is unsupported")
        reason = _non_empty_string(target.get("reason"), f"targets[{index}].reason")
        region = _region(target["region"], f"targets[{index}].region") if "region" in target else None
        mechanic_ids_raw = target.get("mechanicIds", [])
        mechanic_ids = sorted({_non_empty_string(item, f"targets[{index}].mechanicIds") for item in _list(mechanic_ids_raw, f"targets[{index}].mechanicIds")})
        if kind == "world" and mechanic_ids:
            raise CoverageDashboardError("world targets must use the complete reviewed Coverage Matrix population, not mechanicIds")
        if kind == "region" and region is None:
            raise CoverageDashboardError("region targets require an exact region")
        if kind in {"landmark-route", "quest", "mechanic-set"} and not mechanic_ids:
            raise CoverageDashboardError(f"{kind} targets require explicit mechanicIds")
        if kind == "world" and region is not None:
            raise CoverageDashboardError("world targets must not declare a bounded region")

        required_raw = _list(target.get("requiredDimensions"), f"targets[{index}].requiredDimensions")
        required_dimensions = sorted({_non_empty_string(item, f"targets[{index}].requiredDimensions") for item in required_raw})
        if not required_dimensions:
            raise CoverageDashboardError("requiredDimensions must not be empty")
        unknown_required = set(required_dimensions) - REQUIRED_DIMENSIONS
        if unknown_required:
            raise CoverageDashboardError(f"unknown required dimensions: {sorted(unknown_required)}")

        source_bindings: list[dict[str, Any]] = []
        for binding_index, raw_binding in enumerate(_list(target.get("sourceCorrelation", []), f"targets[{index}].sourceCorrelation")):
            binding = _mapping(raw_binding, f"targets[{index}].sourceCorrelation[{binding_index}]")
            report_sha = _sha256(binding.get("reportSha256"), "sourceCorrelation.reportSha256")
            evidence_ids = sorted({_non_empty_string(item, "sourceCorrelation.evidenceIds") for item in _list(binding.get("evidenceIds"), "sourceCorrelation.evidenceIds")})
            if not evidence_ids:
                raise CoverageDashboardError("sourceCorrelation.evidenceIds must not be empty")
            source_bindings.append({"reportSha256": report_sha, "evidenceIds": evidence_ids})
        source_bindings.sort(key=lambda item: (item["reportSha256"], item["evidenceIds"]))

        route_bindings: list[dict[str, Any]] = []
        for binding_index, raw_binding in enumerate(_list(target.get("routePlans", []), f"targets[{index}].routePlans")):
            binding = _mapping(raw_binding, f"targets[{index}].routePlans[{binding_index}]")
            report_sha = _sha256(binding.get("reportSha256"), "routePlans.reportSha256")
            interaction_required = binding.get("interactionRequired")
            if not isinstance(interaction_required, bool):
                raise CoverageDashboardError("routePlans.interactionRequired must be boolean")
            route_bindings.append({"reportSha256": report_sha, "interactionRequired": interaction_required})
        route_bindings.sort(key=lambda item: (item["reportSha256"], item["interactionRequired"]))

        candidate_repairs = sorted({_sha256(item, "candidateRepairs[]") for item in _list(target.get("candidateRepairs", []), f"targets[{index}].candidateRepairs")})
        normalized.append(
            {
                "id": target_id,
                "kind": kind,
                "reason": reason,
                "region": region,
                "mechanicIds": mechanic_ids,
                "requiredDimensions": required_dimensions,
                "sourceCorrelation": source_bindings,
                "routePlans": route_bindings,
                "candidateRepairs": candidate_repairs,
            }
        )
    return sorted(normalized, key=lambda item: item["id"])


def _validate_required_reports(
    coverage_matrix: Mapping[str, Any],
    map_quality: Mapping[str, Any],
    world_health: Mapping[str, Any],
) -> tuple[str, str]:
    if coverage_matrix.get("format") != COVERAGE_FORMAT or coverage_matrix.get("schemaVersion") != SCHEMA_VERSION:
        raise CoverageDashboardError(f"coverage matrix must use {COVERAGE_FORMAT} schemaVersion {SCHEMA_VERSION}")
    if map_quality.get("format") != MAP_QUALITY_FORMAT or map_quality.get("schemaVersion") != SCHEMA_VERSION:
        raise CoverageDashboardError(f"Map Quality must use {MAP_QUALITY_FORMAT} schemaVersion {SCHEMA_VERSION}")
    if world_health.get("format") != WORLD_HEALTH_FORMAT or world_health.get("schemaVersion") != SCHEMA_VERSION:
        raise CoverageDashboardError(f"World Health must use {WORLD_HEALTH_FORMAT} schemaVersion {SCHEMA_VERSION}")
    current_map = _mapping(coverage_matrix.get("currentMap"), "coverageMatrix.currentMap")
    map_sha = _sha256(current_map.get("mapSha256"), "coverageMatrix.currentMap.mapSha256")
    world_index_sha = _sha256(current_map.get("worldIndexSha256"), "coverageMatrix.currentMap.worldIndexSha256")
    map_quality_source = _mapping(map_quality.get("source"), "mapQuality.source")
    if map_quality_source.get("sha256") != map_sha:
        raise CoverageDashboardError("Map Quality source map SHA-256 does not match Coverage Matrix current map")
    world_source = _mapping(world_health.get("source"), "worldHealth.source")
    if world_source.get("mapSha256") != map_sha or world_source.get("worldIndexSha256") != world_index_sha:
        raise CoverageDashboardError("World Health current map/World Index identity does not match Coverage Matrix")
    return map_sha, world_index_sha


def _coverage_mechanics(coverage_matrix: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    mechanics = _list(coverage_matrix.get("mechanics"), "coverageMatrix.mechanics")
    result: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(mechanics):
        mechanic = _mapping(raw, f"coverageMatrix.mechanics[{index}]")
        mechanic_id = _non_empty_string(mechanic.get("id"), f"coverageMatrix.mechanics[{index}].id")
        if mechanic_id in result:
            raise CoverageDashboardError(f"duplicate Coverage Matrix mechanic id: {mechanic_id}")
        normalized = dict(mechanic)
        normalized["selector"] = _normalize_selector(mechanic.get("selector"), f"coverageMatrix.mechanics[{index}].selector")
        result[mechanic_id] = normalized
    return result


def _position_in_region(position: Sequence[int], region: Mapping[str, Sequence[int]]) -> bool:
    return all(region["from"][index] <= position[index] <= region["to"][index] for index in range(3))


def _select_mechanics(target: Mapping[str, Any], mechanics: Mapping[str, dict[str, Any]]) -> list[dict[str, Any]]:
    kind = target["kind"]
    if kind == "world":
        ids = sorted(mechanics)
    elif kind == "region":
        region = target["region"]
        ids = sorted(
            mechanic_id
            for mechanic_id, mechanic in mechanics.items()
            if _position_in_region(mechanic["selector"]["position"], region)
        )
    else:
        ids = target["mechanicIds"]
        unknown = [mechanic_id for mechanic_id in ids if mechanic_id not in mechanics]
        if unknown:
            raise CoverageDashboardError(f"target {target['id']} references unknown Coverage Matrix mechanics: {unknown}")
    return [mechanics[mechanic_id] for mechanic_id in ids]


def _evidence(format_name: str, report_sha: str, source_id: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"format": format_name, "reportSha256": report_sha}
    if source_id is not None:
        result["sourceId"] = source_id
    return result


def _dimension(
    state: str,
    *,
    evidence: Iterable[Mapping[str, Any]] = (),
    member_ids: Iterable[str] = (),
    blockers: Iterable[str] = (),
) -> dict[str, Any]:
    if state not in DIMENSION_STATES:
        raise CoverageDashboardError(f"invalid dimension state: {state}")
    unique_evidence = {
        (item["format"], item["reportSha256"], item.get("sourceId")): dict(item)
        for item in evidence
    }
    return {
        "state": state,
        "evidence": [unique_evidence[key] for key in sorted(unique_evidence, key=lambda key: (key[0], key[1], key[2] or ""))],
        "memberIds": sorted(set(member_ids)),
        "blockers": sorted(set(blockers)),
    }


def _mechanic_dimension(
    mechanics: Sequence[Mapping[str, Any]],
    *,
    coverage_pin: Mapping[str, Any],
    predicate,
    blocker_code: str,
) -> dict[str, Any]:
    if not mechanics:
        return _dimension("not-evaluated", blockers=["NO_REVIEWED_MECHANICS_IN_TARGET_SCOPE"])
    failed = [mechanic["id"] for mechanic in mechanics if not predicate(mechanic)]
    evidence = [_evidence(COVERAGE_FORMAT, coverage_pin["sha256"], mechanic["id"]) for mechanic in mechanics]
    return _dimension(
        "proven" if not failed else "blocked",
        evidence=evidence,
        member_ids=[mechanic["id"] for mechanic in mechanics],
        blockers=[] if not failed else [blocker_code],
    )


def _source_correlation_dimension(
    target: Mapping[str, Any],
    quest_index: Mapping[str, Mapping[str, Any]],
    *,
    current_world_index_sha: str,
) -> tuple[dict[str, Any], list[str]]:
    bindings = target["sourceCorrelation"]
    if not bindings:
        return _dimension("not-evaluated", blockers=["SOURCE_CORRELATION_EVIDENCE_NOT_BOUND"]), []
    evidence_items: list[dict[str, Any]] = []
    classifications: list[str] = []
    stale = False
    for binding in bindings:
        entry = quest_index.get(binding["reportSha256"])
        if entry is None:
            raise CoverageDashboardError(
                f"target {target['id']} references missing Quest Map Validation report {binding['reportSha256']}"
            )
        report = entry["report"]
        if report.get("schemaVersion", 1) != 1:
            raise CoverageDashboardError("Quest Map Validation schemaVersion must be 1 when present")
        sources = _mapping(report.get("sources"), "questValidation.sources")
        world_index = _mapping(sources.get("worldIndex"), "questValidation.sources.worldIndex")
        report_world_index_sha = _sha256(world_index.get("sha256"), "questValidation.sources.worldIndex.sha256")
        if report_world_index_sha != current_world_index_sha:
            stale = True
        findings_by_id: dict[str, Mapping[str, Any]] = {}
        for finding in _list(report.get("findings"), "questValidation.findings"):
            finding_map = _mapping(finding, "questValidation.findings[]")
            evidence_id = _non_empty_string(finding_map.get("evidenceId"), "questValidation.findings[].evidenceId")
            if evidence_id in findings_by_id:
                raise CoverageDashboardError(f"duplicate Quest Map Validation evidenceId: {evidence_id}")
            findings_by_id[evidence_id] = finding_map
        for evidence_id in binding["evidenceIds"]:
            finding = findings_by_id.get(evidence_id)
            if finding is None:
                raise CoverageDashboardError(
                    f"target {target['id']} references unknown Quest Map Validation evidenceId {evidence_id}"
                )
            classification = finding.get("classification")
            if classification not in {"confirmed", "map-only", "script-only", "unresolved", "conflicting"}:
                raise CoverageDashboardError(f"invalid Quest Map Validation classification for {evidence_id}")
            classifications.append(classification)
            evidence_items.append(_evidence(QUEST_VALIDATION_FORMAT, binding["reportSha256"], evidence_id))
    if stale:
        return _dimension("stale", evidence=evidence_items, blockers=["SOURCE_CORRELATION_WORLD_INDEX_STALE"]), ["stale"]
    failed = sorted({classification for classification in classifications if classification != "confirmed"})
    if failed:
        return _dimension(
            "blocked",
            evidence=evidence_items,
            blockers=[f"SOURCE_CORRELATION_{classification.upper().replace('-', '_')}" for classification in failed],
        ), ["current"]
    return _dimension("proven", evidence=evidence_items), ["current"]


def _route_dimensions(
    target: Mapping[str, Any],
    route_index: Mapping[str, Mapping[str, Any]],
    *,
    current_map_sha: str,
    current_world_index_sha: str,
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    bindings = target["routePlans"]
    if not bindings:
        return (
            _dimension("not-evaluated", blockers=["ROUTE_PLAN_EVIDENCE_NOT_BOUND"]),
            _dimension("not-evaluated", blockers=["ROUTE_PLAN_EVIDENCE_NOT_BOUND"]),
            [],
        )
    route_evidence: list[dict[str, Any]] = []
    stale_shas: list[str] = []
    blocked_shas: list[str] = []
    current_shas: list[str] = []
    interaction_required = [binding for binding in bindings if binding["interactionRequired"]]
    interaction_blocked = False
    interaction_evidence_found = False
    for binding in bindings:
        report_sha = binding["reportSha256"]
        entry = route_index.get(report_sha)
        if entry is None:
            raise CoverageDashboardError(f"target {target['id']} references missing route plan {report_sha}")
        report = entry["report"]
        provenance = _mapping(report.get("provenance"), "routePlan.provenance")
        map_pin = _mapping(provenance.get("map"), "routePlan.provenance.map")
        index_pin = _mapping(provenance.get("worldIndex"), "routePlan.provenance.worldIndex")
        current = map_pin.get("sha256") == current_map_sha and index_pin.get("sha256") == current_world_index_sha
        route_evidence.append(_evidence(ROUTE_PLAN_FORMAT, report_sha))
        if not current:
            stale_shas.append(report_sha)
            continue
        current_shas.append(report_sha)
        if report.get("executionStatus") != "executable" or report.get("pathComplete") is not True:
            blocked_shas.append(report_sha)
        if binding["interactionRequired"]:
            if report.get("routingMode") != "executable":
                interaction_blocked = True
                continue
            registry = provenance.get("interactionRegistry")
            if not isinstance(registry, Mapping) or not _is_sha256(registry.get("sha256")):
                interaction_blocked = True
                continue
            plan_interactions: list[Mapping[str, Any]] = []
            for edge in _list(report.get("edges"), "routePlan.edges"):
                edge_map = _mapping(edge, "routePlan.edges[]")
                for interaction in edge_map.get("interactions", []) or []:
                    plan_interactions.append(_mapping(interaction, "routePlan.edges[].interactions[]"))
            if not plan_interactions:
                interaction_blocked = True
                continue
            interaction_evidence_found = True
            if any(
                interaction.get("executionStatus") != "executable" or bool(interaction.get("blockers"))
                for interaction in plan_interactions
            ):
                interaction_blocked = True
    if stale_shas:
        route_state = _dimension("stale", evidence=route_evidence, blockers=["ROUTE_PLAN_PROVENANCE_STALE"])
    elif blocked_shas:
        route_state = _dimension("blocked", evidence=route_evidence, blockers=["ROUTE_PLAN_NOT_EXECUTABLE"])
    else:
        route_state = _dimension("proven", evidence=route_evidence)

    if not interaction_required:
        interaction_state = _dimension("not-applicable", evidence=route_evidence)
    elif stale_shas:
        interaction_state = _dimension("stale", evidence=route_evidence, blockers=["INTERACTION_ROUTE_PROVENANCE_STALE"])
    elif interaction_blocked or not interaction_evidence_found:
        interaction_state = _dimension("blocked", evidence=route_evidence, blockers=["INTERACTION_RESOLUTION_NOT_EXECUTABLE"])
    else:
        interaction_state = _dimension("proven", evidence=route_evidence)
    provenance_states = ["stale"] * len(stale_shas) + ["current"] * len(current_shas)
    return route_state, interaction_state, provenance_states


def _static_quality_dimension(
    target: Mapping[str, Any],
    map_quality: Mapping[str, Any],
    map_quality_pin: Mapping[str, Any],
) -> dict[str, Any]:
    coverage = _mapping(map_quality.get("coverage"), "mapQuality.coverage")
    evidence = [_evidence(MAP_QUALITY_FORMAT, map_quality_pin["sha256"])]
    if target["kind"] == "world":
        return _dimension("not-evaluated", evidence=evidence, blockers=["GLOBAL_MAP_QUALITY_NOT_PROVEN"])
    region = target.get("region")
    if region is None:
        return _dimension("not-evaluated", evidence=evidence, blockers=["TARGET_REGION_NOT_BOUND_FOR_STATIC_QUALITY"])
    if coverage.get("geometry") != region or coverage.get("reachability") != region or coverage.get("sameRegion") is not True:
        return _dimension("not-evaluated", evidence=evidence, blockers=["MAP_QUALITY_SCOPE_NOT_EXACT_TARGET_REGION"])
    components = _mapping(map_quality.get("components"), "mapQuality.components")
    compatible = map_quality.get("ok") is True
    for component_name in ("geometry", "reachability", "scriptResolution"):
        component = _mapping(components.get(component_name), f"mapQuality.components.{component_name}")
        compatible = compatible and component.get("inputOk") is True and component.get("inputComplete") is True
    return _dimension(
        "proven" if compatible else "blocked",
        evidence=evidence,
        blockers=[] if compatible else ["MAP_QUALITY_NOT_GREEN_OR_INCOMPLETE"],
    )


def _candidate_dimension(
    target: Mapping[str, Any],
    mechanics: Sequence[Mapping[str, Any]],
    candidate_index: Mapping[str, Mapping[str, Any]],
    *,
    current_map_sha: str,
) -> tuple[dict[str, Any], list[str]]:
    references = target["candidateRepairs"]
    if not references:
        return _dimension("not-evaluated", blockers=["CANDIDATE_VALIDATION_EVIDENCE_NOT_BOUND"]), []
    selectors = {canonical_json(mechanic["selector"]) for mechanic in mechanics}
    evidence_items: list[dict[str, Any]] = []
    stale = False
    blocked = False
    for report_sha in references:
        entry = candidate_index.get(report_sha)
        if entry is None:
            raise CoverageDashboardError(f"target {target['id']} references missing QA-004 candidate report {report_sha}")
        report = entry["report"]
        source = _mapping(report.get("source"), "candidateRepair.source")
        recommendation = _mapping(report.get("recommendation"), "candidateRepair.recommendation")
        selector = _normalize_selector(recommendation.get("selector"), "candidateRepair.recommendation.selector")
        if canonical_json(selector) not in selectors:
            raise CoverageDashboardError(
                f"target {target['id']} candidate repair selector is not one of its reviewed Coverage Matrix mechanics"
            )
        evidence_items.append(_evidence(CANDIDATE_REPAIR_FORMAT, report_sha))
        if source.get("mapSha256") != current_map_sha:
            stale = True
        if report.get("ok") is not True or report.get("status") not in {
            "physically-validated",
            "validated-no-physical-e2e-required",
        }:
            blocked = True
    if stale:
        return _dimension("stale", evidence=evidence_items, blockers=["CANDIDATE_VALIDATION_SOURCE_MAP_STALE"]), ["stale"]
    if blocked:
        return _dimension("blocked", evidence=evidence_items, blockers=["CANDIDATE_VALIDATION_NOT_SUCCESSFUL"]), ["current"]
    return _dimension("proven", evidence=evidence_items), ["current"]


def _current_provenance_dimension(
    mechanics: Sequence[Mapping[str, Any]],
    optional_states: Sequence[str],
    coverage_pin: Mapping[str, Any],
) -> dict[str, Any]:
    states: list[str] = list(optional_states)
    evidence = [_evidence(COVERAGE_FORMAT, coverage_pin["sha256"], mechanic["id"]) for mechanic in mechanics]
    for mechanic in mechanics:
        stale = mechanic.get("staleAgainstCurrentMapProvenance")
        if stale is True:
            states.append("stale")
        elif stale is False:
            states.append("current")
        else:
            states.append("unknown")
    if not states:
        state = "not-evaluated"
    else:
        known = {item for item in states if item in {"current", "stale"}}
        unknown = any(item == "unknown" for item in states)
        if known == {"current"} and not unknown:
            state = "current"
        elif known == {"stale"} and not unknown:
            state = "stale"
        elif not known:
            state = "not-evaluated"
        else:
            state = "mixed"
    if state not in CURRENT_PROVENANCE_STATES:
        raise CoverageDashboardError("invalid current-map provenance state")
    blockers = [] if state == "current" else ["CURRENT_MAP_PROVENANCE_NOT_FULLY_PROVEN"]
    return {"state": state, "evidence": evidence, "blockers": blockers}


def _required_satisfied(required_dimensions: Sequence[str], dimensions: Mapping[str, Any], provenance: Mapping[str, Any]) -> bool:
    for dimension in required_dimensions:
        if dimension == "current-map-provenance":
            if provenance.get("state") != "current":
                return False
            continue
        output_key = DIMENSION_OUTPUT_KEYS[dimension]
        if _mapping(dimensions.get(output_key), output_key).get("state") != "proven":
            return False
    return True


def _coverage_gaps(target_id: str, required_dimensions: Sequence[str], dimensions: Mapping[str, Any], provenance: Mapping[str, Any]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    required_set = set(required_dimensions)
    for dimension_name, output_key in sorted(DIMENSION_OUTPUT_KEYS.items()):
        state = _mapping(dimensions[output_key], output_key)["state"]
        if state in {"proven", "not-applicable"}:
            continue
        gaps.append(
            {
                "targetId": target_id,
                "dimension": dimension_name,
                "state": state,
                "required": dimension_name in required_set,
                "code": {
                    "blocked": "EVIDENCE_BLOCKED",
                    "stale": "EVIDENCE_STALE",
                    "not-evaluated": "EVIDENCE_NOT_EVALUATED",
                }[state],
            }
        )
    provenance_state = provenance["state"]
    if provenance_state != "current":
        gaps.append(
            {
                "targetId": target_id,
                "dimension": "current-map-provenance",
                "state": provenance_state,
                "required": "current-map-provenance" in required_set,
                "code": "CURRENT_MAP_PROVENANCE_NOT_FULLY_PROVEN",
            }
        )
    return sorted(gaps, key=lambda item: (item["targetId"], item["dimension"], item["code"]))


def build_coverage_dashboard_report(
    *,
    targets_manifest: Mapping[str, Any],
    coverage_matrix: Mapping[str, Any],
    map_quality: Mapping[str, Any],
    world_health: Mapping[str, Any],
    quest_validations: Sequence[Mapping[str, Any]] | None = None,
    route_plans: Sequence[Mapping[str, Any]] | None = None,
    candidate_repairs: Sequence[Mapping[str, Any]] | None = None,
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    targets_pin = _input_pin(input_pins.get("targets"), TARGETS_FORMAT, "targets")
    coverage_pin = _input_pin(input_pins.get("coverageMatrix"), COVERAGE_FORMAT, "coverageMatrix")
    map_quality_pin = _input_pin(input_pins.get("mapQuality"), MAP_QUALITY_FORMAT, "mapQuality")
    world_health_pin = _input_pin(input_pins.get("worldHealth"), WORLD_HEALTH_FORMAT, "worldHealth")
    current_map_sha, current_world_index_sha = _validate_required_reports(coverage_matrix, map_quality, world_health)
    targets = _normalize_targets(targets_manifest)
    mechanics_by_id = _coverage_mechanics(coverage_matrix)
    quest_index = _optional_index(quest_validations, QUEST_VALIDATION_FORMAT, "questValidations")
    route_index = _optional_index(route_plans, ROUTE_PLAN_FORMAT, "routePlans")
    candidate_index = _optional_index(candidate_repairs, CANDIDATE_REPAIR_FORMAT, "candidateRepairs")

    target_reports: list[dict[str, Any]] = []
    all_gaps: list[dict[str, Any]] = []
    dimension_counters: dict[str, Counter[str]] = {
        output_key: Counter() for output_key in DIMENSION_OUTPUT_KEYS.values()
    }
    provenance_counter: Counter[str] = Counter()
    satisfied_count = 0

    for target in targets:
        selected_mechanics = _select_mechanics(target, mechanics_by_id)
        mechanic_ids = [mechanic["id"] for mechanic in selected_mechanics]
        indexed = _mechanic_dimension(
            selected_mechanics,
            coverage_pin=coverage_pin,
            predicate=lambda mechanic: _mapping(mechanic.get("static"), "mechanic.static").get("indexed") is True
            and _mapping(mechanic.get("static"), "mechanic.static").get("uniqueMatch") is True,
            blocker_code="REVIEWED_MECHANIC_NOT_UNIQUELY_INDEXED",
        )
        script = _mechanic_dimension(
            selected_mechanics,
            coverage_pin=coverage_pin,
            predicate=lambda mechanic: _mapping(mechanic.get("script"), "mechanic.script").get("resolved") is True
            and _mapping(mechanic.get("script"), "mechanic.script").get("uniqueMatch") is True,
            blocker_code="REVIEWED_MECHANIC_SCRIPT_NOT_RESOLVED",
        )
        reachability = _mechanic_dimension(
            selected_mechanics,
            coverage_pin=coverage_pin,
            predicate=lambda mechanic: _mapping(mechanic.get("reachability"), "mechanic.reachability").get("covered") is True,
            blocker_code="REVIEWED_MECHANIC_REACHABILITY_NOT_COVERED",
        )
        if selected_mechanics:
            physical_failed = [
                mechanic["id"]
                for mechanic in selected_mechanics
                if _mapping(mechanic.get("physical"), "mechanic.physical").get("runtimeProvenOnCurrentMap") is not True
            ]
            physical_stale = any(
                _mapping(mechanic.get("physical"), "mechanic.physical").get("runtimeProven") is True
                and _mapping(mechanic.get("physical"), "mechanic.physical").get("staleMapScenarios")
                for mechanic in selected_mechanics
            )
            physical_evidence = [
                _evidence(COVERAGE_FORMAT, coverage_pin["sha256"], mechanic["id"]) for mechanic in selected_mechanics
            ]
            if not physical_failed:
                physical = _dimension("proven", evidence=physical_evidence, member_ids=mechanic_ids)
            elif physical_stale:
                physical = _dimension(
                    "stale",
                    evidence=physical_evidence,
                    member_ids=mechanic_ids,
                    blockers=["PHYSICAL_RUNTIME_PROOF_STALE"],
                )
            else:
                physical = _dimension(
                    "blocked",
                    evidence=physical_evidence,
                    member_ids=mechanic_ids,
                    blockers=["PHYSICAL_RUNTIME_NOT_PROVEN_ON_CURRENT_MAP"],
                )
        else:
            physical = _dimension("not-evaluated", blockers=["NO_REVIEWED_MECHANICS_IN_TARGET_SCOPE"])

        source_correlation, source_provenance_states = _source_correlation_dimension(
            target, quest_index, current_world_index_sha=current_world_index_sha
        )
        executable_route, interaction, route_provenance_states = _route_dimensions(
            target,
            route_index,
            current_map_sha=current_map_sha,
            current_world_index_sha=current_world_index_sha,
        )
        static_quality = _static_quality_dimension(target, map_quality, map_quality_pin)
        candidate, candidate_provenance_states = _candidate_dimension(
            target, selected_mechanics, candidate_index, current_map_sha=current_map_sha
        )
        current_provenance = _current_provenance_dimension(
            selected_mechanics,
            source_provenance_states + route_provenance_states + candidate_provenance_states,
            coverage_pin,
        )

        dimensions = {
            "indexedOnExactMap": indexed,
            "sourceCorrelated": source_correlation,
            "scriptResolved": script,
            "staticallyReachable": reachability,
            "interactionResolved": interaction,
            "staticQualityCompatible": static_quality,
            "executableRouteCovered": executable_route,
            "physicallyRuntimeProven": physical,
            "candidateMapValidated": candidate,
        }
        requirements_satisfied = _required_satisfied(target["requiredDimensions"], dimensions, current_provenance)
        if requirements_satisfied:
            satisfied_count += 1
        gaps = _coverage_gaps(target["id"], target["requiredDimensions"], dimensions, current_provenance)
        all_gaps.extend(gaps)
        for output_key, dimension in dimensions.items():
            dimension_counters[output_key][dimension["state"]] += 1
        provenance_counter[current_provenance["state"]] += 1

        target_reports.append(
            {
                "id": target["id"],
                "kind": target["kind"],
                "reason": target["reason"],
                "region": target["region"],
                "population": {
                    "kind": "all-reviewed-coverage-matrix-mechanics"
                    if target["kind"] == "world"
                    else "region-reviewed-coverage-matrix-mechanics"
                    if target["kind"] == "region"
                    else "explicit-reviewed-mechanic-ids",
                    "mechanicIds": mechanic_ids,
                    "mechanicCount": len(mechanic_ids),
                    "globalMapMechanicCoverageProven": False,
                },
                "requiredDimensions": target["requiredDimensions"],
                "dimensions": dimensions,
                "staleAgainstCurrentMap": current_provenance,
                "requirementsSatisfied": requirements_satisfied,
                "formalCertificationLevel": None,
                "coverageGaps": gaps,
            }
        )

    summary_by_kind = Counter(target["kind"] for target in target_reports)
    summary_dimension_states = {
        key: {state: dimension_counters[key].get(state, 0) for state in sorted(DIMENSION_STATES)}
        for key in sorted(dimension_counters)
    }
    summary_provenance = {state: provenance_counter.get(state, 0) for state in sorted(CURRENT_PROVENANCE_STATES)}
    world_summary = _mapping(world_health.get("summary"), "worldHealth.summary")
    world_coverage = _mapping(world_health.get("coverage"), "worldHealth.coverage")

    optional_provenance = {
        "questValidations": [entry["pin"] for _, entry in sorted(quest_index.items())],
        "routePlans": [entry["pin"] for _, entry in sorted(route_index.items())],
        "candidateRepairs": [entry["pin"] for _, entry in sorted(candidate_index.items())],
    }
    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "currentMap": {"mapSha256": current_map_sha, "worldIndexSha256": current_world_index_sha},
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "otbmParsedIndependently": False,
            "validatorsRecomputed": False,
            "routeGenerated": False,
            "physicalE2eExecuted": False,
            "candidateValidationExecuted": False,
            "formalCertificationAssigned": False,
            "opaqueScoreEmitted": False,
            "missingEvidenceMeansGlobalAbsence": False,
            "downstreamScenarioPrioritizationDirected": False,
        },
        "provenance": {
            "targets": targets_pin,
            "coverageMatrix": coverage_pin,
            "mapQuality": map_quality_pin,
            "worldHealth": world_health_pin,
            **optional_provenance,
        },
        "worldContext": {
            "summary": dict(world_summary),
            "globalCoverageProven": world_coverage.get("globalCoverageProven") is True,
        },
        "summary": {
            "targets": len(target_reports),
            "requirementsSatisfied": satisfied_count,
            "requirementsNotSatisfied": len(target_reports) - satisfied_count,
            "coverageGaps": len(all_gaps),
            "byKind": {kind: summary_by_kind.get(kind, 0) for kind in sorted(TARGET_KINDS)},
            "dimensionStates": summary_dimension_states,
            "currentMapProvenanceStates": summary_provenance,
        },
        "targets": target_reports,
        "coverageGaps": sorted(all_gaps, key=lambda item: (item["targetId"], item["dimension"], item["code"])),
        "notes": [
            "Dashboard populations are reviewed Coverage Matrix targets, not proof that every mechanic in the map has been enumerated.",
            "Missing optional evidence remains not-evaluated; it is never promoted to global absence or a formal certification level.",
            "requirementsSatisfied is derived only from each target's explicit requiredDimensions and does not assign QA-006 C0-C7 certification.",
            "Coverage gaps are factual evidence for downstream owners and do not instruct creation or prioritization of a specific Physical E2E scenario.",
        ],
    }
