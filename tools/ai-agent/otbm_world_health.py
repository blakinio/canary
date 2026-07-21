from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

REPORT_FORMAT = "canary-otbm-world-health-v1"
SCHEMA_VERSION = 1
MAP_QUALITY_FORMAT = "canary-otbm-map-quality-v1"
REACHABILITY_FORMAT = "canary-otbm-reachability-v1"
COVERAGE_FORMAT = "canary-otbm-e2e-coverage-matrix-v1"
DEFAULT_SAMPLE_LIMIT = 500
MAX_SAMPLE_LIMIT = 10_000
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
OUTCOMES = ("error", "warning", "unresolved", "info")
ROUTE_STATUSES = {"confirmed", "conditional", "unreachable", "invalid"}
TRANSITION_STATUSES = {"confirmed", "conditional", "invalid"}
MECHANIC_STATUSES = {"confirmed", "conditional", "unreachable"}
DIMENSION_ORDER = {
    "structural": 0,
    "runtimeHandlers": 1,
    "reachability": 2,
    "staleEvidence": 3,
    "missingPhysicalCoverage": 4,
}


class WorldHealthError(ValueError):
    """Raised when existing OTBM evidence cannot be aggregated safely."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WorldHealthError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise WorldHealthError(f"{label} must be an array")
    return value


def _count(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise WorldHealthError(f"{label} must be a non-negative integer")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise WorldHealthError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _position(value: Any) -> list[int] | None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 3:
        return None
    if any(isinstance(entry, bool) or not isinstance(entry, int) for entry in value):
        return None
    x, y, z = (int(entry) for entry in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        return None
    return [x, y, z]


def _required_position(value: Any, label: str) -> list[int]:
    position = _position(value)
    if position is None:
        raise WorldHealthError(f"{label} must be an [x,y,z] position")
    return position


def _count_object(
    value: Any,
    label: str,
    *,
    allowed_keys: set[str] | None = None,
) -> dict[str, int]:
    source = _mapping(value, label)
    result: dict[str, int] = {}
    for raw_key, raw_count in source.items():
        if not isinstance(raw_key, str) or not raw_key:
            raise WorldHealthError(f"{label} keys must be non-empty strings")
        if allowed_keys is not None and raw_key not in allowed_keys:
            raise WorldHealthError(f"{label} has unsupported status {raw_key!r}")
        result[raw_key] = _count(raw_count, f"{label}.{raw_key}")
    return dict(sorted(result.items()))


def _outcome_counts(value: Any, label: str) -> dict[str, int]:
    source = _mapping(value, label)
    return {outcome: _count(source.get(outcome, 0), f"{label}.{outcome}") for outcome in OUTCOMES}


def _sum_count_objects(values: Sequence[Mapping[str, int]]) -> dict[str, int]:
    keys = sorted({key for value in values for key in value})
    return {key: sum(value.get(key, 0) for value in values) for key in keys}


def _validate_input_pin(value: Any, label: str, expected_format: str) -> dict[str, Any]:
    pin = _mapping(value, label)
    file_name = pin.get("fileName")
    if not isinstance(file_name, str) or not file_name:
        raise WorldHealthError(f"{label}.fileName must be a non-empty string")
    size = _count(pin.get("size"), f"{label}.size")
    digest = _sha256(pin.get("sha256"), f"{label}.sha256")
    report_format = pin.get("format")
    if report_format != expected_format:
        raise WorldHealthError(f"{label}.format must be {expected_format}")
    return {
        "fileName": file_name,
        "size": size,
        "sha256": digest,
        "format": expected_format,
    }


def _sorted_report_pairs(
    reports: Sequence[Mapping[str, Any]],
    pins: Sequence[Mapping[str, Any]],
    *,
    label: str,
    expected_format: str,
) -> list[tuple[Mapping[str, Any], dict[str, Any]]]:
    if len(reports) != len(pins):
        raise WorldHealthError(f"{label} reports and input pins must have the same length")
    pairs: list[tuple[Mapping[str, Any], dict[str, Any]]] = []
    seen_hashes: set[str] = set()
    for index, (report, raw_pin) in enumerate(zip(reports, pins, strict=True)):
        report_object = _mapping(report, f"{label}[{index}]")
        if report_object.get("format") != expected_format:
            raise WorldHealthError(f"{label}[{index}] must use format {expected_format}")
        pin = _validate_input_pin(raw_pin, f"{label}Pins[{index}]", expected_format)
        if pin["sha256"] in seen_hashes:
            raise WorldHealthError(f"duplicate {label} report SHA-256 is not allowed: {pin['sha256']}")
        seen_hashes.add(pin["sha256"])
        pairs.append((report_object, pin))
    pairs.sort(key=lambda pair: (pair[1]["sha256"], pair[1]["fileName"]))
    return pairs


def _map_quality_source_sha256(report: Mapping[str, Any]) -> str:
    if report.get("format") != MAP_QUALITY_FORMAT:
        raise WorldHealthError(f"map-quality report must use format {MAP_QUALITY_FORMAT}")
    source = _mapping(report.get("source"), "mapQuality.source")
    return _sha256(source.get("sha256"), "mapQuality.source.sha256")


def _reachability_identity(report: Mapping[str, Any], label: str) -> tuple[str, str, dict[str, Any]]:
    if report.get("format") != REACHABILITY_FORMAT:
        raise WorldHealthError(f"{label} must use format {REACHABILITY_FORMAT}")
    provenance = _mapping(report.get("provenance"), f"{label}.provenance")
    world_index = _mapping(provenance.get("worldIndex"), f"{label}.provenance.worldIndex")
    world_index_sha = _sha256(world_index.get("sha256"), f"{label}.provenance.worldIndex.sha256")
    manifest = _mapping(provenance.get("worldIndexManifest"), f"{label}.provenance.worldIndexManifest")
    source = _mapping(manifest.get("source"), f"{label}.provenance.worldIndexManifest.source")
    source_sha = _sha256(source.get("sha256"), f"{label}.provenance.worldIndexManifest.source.sha256")
    manifest_index = _mapping(manifest.get("index"), f"{label}.provenance.worldIndexManifest.index")
    manifest_index_sha = _sha256(
        manifest_index.get("sha256"),
        f"{label}.provenance.worldIndexManifest.index.sha256",
    )
    if manifest_index_sha != world_index_sha:
        raise WorldHealthError(f"{label} World Index hash does not match its manifest provenance")
    region = _mapping(report.get("region"), f"{label}.region")
    normalized_region = {
        "from": _required_position(region.get("from"), f"{label}.region.from"),
        "to": _required_position(region.get("to"), f"{label}.region.to"),
        "coordinateCount": _count(region.get("coordinateCount", 0), f"{label}.region.coordinateCount"),
        "indexedTileCount": _count(region.get("indexedTileCount", 0), f"{label}.region.indexedTileCount"),
    }
    return source_sha, world_index_sha, normalized_region


def _coverage_identity(report: Mapping[str, Any], label: str) -> tuple[str, str]:
    if report.get("format") != COVERAGE_FORMAT:
        raise WorldHealthError(f"{label} must use format {COVERAGE_FORMAT}")
    current_map = _mapping(report.get("currentMap"), f"{label}.currentMap")
    return (
        _sha256(current_map.get("mapSha256"), f"{label}.currentMap.mapSha256"),
        _sha256(current_map.get("worldIndexSha256"), f"{label}.currentMap.worldIndexSha256"),
    )


def _component(report: Mapping[str, Any], name: str, source_sha: str) -> Mapping[str, Any]:
    components = _mapping(report.get("components"), "mapQuality.components")
    component = _mapping(components.get(name), f"mapQuality.components.{name}")
    component_source = _sha256(
        component.get("sourceSha256"),
        f"mapQuality.components.{name}.sourceSha256",
    )
    if component_source != source_sha:
        raise WorldHealthError(f"map-quality component {name} does not prove the report source map")
    return component


def _sample_id(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def _sample(
    *,
    dimension: str,
    kind: str,
    status: str,
    source_format: str,
    source_report_sha256: str,
    evidence: Mapping[str, Any],
    position: Any = None,
    source_id: str | None = None,
) -> dict[str, Any]:
    if dimension not in DIMENSION_ORDER:
        raise WorldHealthError(f"unsupported health dimension: {dimension}")
    payload: dict[str, Any] = {
        "dimension": dimension,
        "kind": str(kind),
        "status": str(status),
        "sourceFormat": source_format,
        "sourceReportSha256": source_report_sha256,
        "evidence": dict(evidence),
    }
    normalized_position = _position(position)
    if normalized_position is not None:
        payload["position"] = normalized_position
    if source_id is not None:
        payload["sourceId"] = str(source_id)
    payload["id"] = _sample_id(payload)
    return payload


def _sample_sort_key(sample: Mapping[str, Any]) -> tuple[Any, ...]:
    position = _position(sample.get("position")) or [0x10000, 0x10000, 16]
    return (
        DIMENSION_ORDER[str(sample["dimension"])],
        str(sample.get("status", "")),
        position[2],
        position[1],
        position[0],
        str(sample.get("kind", "")),
        str(sample.get("sourceReportSha256", "")),
        str(sample.get("sourceId", "")),
        str(sample.get("id", "")),
    )


def _bounded_samples(candidates: Sequence[dict[str, Any]], sample_limit: int) -> tuple[list[dict[str, Any]], bool]:
    ordered = sorted(candidates, key=_sample_sort_key)
    return ordered[:sample_limit], len(ordered) > sample_limit


def _map_quality_dimensions(
    report: Mapping[str, Any],
    *,
    source_sha: str,
    report_pin: Mapping[str, Any],
    sample_limit: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    geometry = _component(report, "geometry", source_sha)
    reachability = _component(report, "reachability", source_sha)
    script_resolution = _component(report, "scriptResolution", source_sha)

    geometry_counts = _outcome_counts(geometry.get("outcomeCounts"), "mapQuality.components.geometry.outcomeCounts")
    reachability_counts = _outcome_counts(
        reachability.get("outcomeCounts"),
        "mapQuality.components.reachability.outcomeCounts",
    )
    structural_counts = {
        outcome: geometry_counts[outcome] + reachability_counts[outcome]
        for outcome in OUTCOMES
    }
    structural_total = sum(structural_counts.values())

    runtime_counts = _outcome_counts(
        script_resolution.get("outcomeCounts"),
        "mapQuality.components.scriptResolution.outcomeCounts",
    )
    runtime_total = sum(runtime_counts.values())
    unreviewed_identifiers = _count(
        script_resolution.get("unreviewedIdentifiers", 0),
        "mapQuality.components.scriptResolution.unreviewedIdentifiers",
    )
    unresolved_dynamic = _count(
        script_resolution.get("unresolvedDynamicRegistrations", 0),
        "mapQuality.components.scriptResolution.unresolvedDynamicRegistrations",
    )

    structural_candidates: list[dict[str, Any]] = []
    runtime_candidates: list[dict[str, Any]] = []
    for index, raw_finding in enumerate(_list(report.get("findings"), "mapQuality.findings")):
        finding = _mapping(raw_finding, f"mapQuality.findings[{index}]")
        component_name = str(finding.get("component", ""))
        outcome = str(finding.get("outcome", ""))
        if outcome not in OUTCOMES:
            raise WorldHealthError(f"mapQuality.findings[{index}] has unsupported outcome {outcome!r}")
        source_id = str(finding.get("id")) if finding.get("id") is not None else None
        if component_name in {"geometry", "reachability"}:
            structural_candidates.append(
                _sample(
                    dimension="structural",
                    kind=str(finding.get("kind", component_name)),
                    status=outcome,
                    source_format=MAP_QUALITY_FORMAT,
                    source_report_sha256=str(report_pin["sha256"]),
                    evidence=finding,
                    position=finding.get("position"),
                    source_id=source_id,
                )
            )
        elif component_name == "scriptResolution":
            runtime_candidates.append(
                _sample(
                    dimension="runtimeHandlers",
                    kind=str(finding.get("kind", "script-resolution")),
                    status=outcome,
                    source_format=MAP_QUALITY_FORMAT,
                    source_report_sha256=str(report_pin["sha256"]),
                    evidence=finding,
                    position=finding.get("position"),
                    source_id=source_id,
                )
            )
        else:
            raise WorldHealthError(f"mapQuality.findings[{index}] has unsupported component {component_name!r}")

    structural_samples, structural_output_truncated = _bounded_samples(structural_candidates, sample_limit)
    runtime_samples, runtime_output_truncated = _bounded_samples(runtime_candidates, sample_limit)
    map_summary = _mapping(report.get("summary"), "mapQuality.summary")
    map_summary_truncated = bool(map_summary.get("truncated"))
    structural_source_truncated = map_summary_truncated or any(
        bool(component.get("findingsTruncatedByComponent")) for component in (geometry, reachability)
    )
    runtime_source_truncated = map_summary_truncated or bool(script_resolution.get("findingsTruncatedByComponent"))

    structural_dimension = {
        "evidencePresent": True,
        "total": structural_total,
        "outcomeCounts": structural_counts,
        "sampled": len(structural_samples),
        "truncated": structural_output_truncated or structural_source_truncated,
        "outputSampleTruncated": structural_output_truncated,
        "sourceEvidenceTruncated": structural_source_truncated,
        "samples": structural_samples,
    }
    runtime_dimension = {
        "evidencePresent": True,
        "placementFindingsTotal": runtime_total,
        "outcomeCounts": runtime_counts,
        "conflictingPlacements": runtime_counts["error"],
        "unresolvedPlacements": runtime_counts["unresolved"],
        "unreviewedIdentifiers": unreviewed_identifiers,
        "unresolvedDynamicRegistrations": unresolved_dynamic,
        "sampled": len(runtime_samples),
        "truncated": runtime_output_truncated or runtime_source_truncated,
        "outputSampleTruncated": runtime_output_truncated,
        "sourceEvidenceTruncated": runtime_source_truncated,
        "samples": runtime_samples,
    }
    return structural_dimension, runtime_dimension


def _validate_category_total(total: int, counts: Mapping[str, int], label: str) -> None:
    if total != sum(counts.values()):
        raise WorldHealthError(f"{label} total does not match its status counts")


def _reachability_dimension(
    pairs: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
    *,
    expected_map_sha: str,
    expected_world_index_sha: str | None,
    sample_limit: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], str | None]:
    route_counts_list: list[Mapping[str, int]] = []
    transition_counts_list: list[Mapping[str, int]] = []
    mechanic_counts_list: list[Mapping[str, int]] = []
    tile_counts_list: list[Mapping[str, int]] = []
    route_total = transition_total = mechanic_total = 0
    one_way = dead_end = loops = 0
    candidates: list[dict[str, Any]] = []
    source_truncated = False
    provenance_entries: list[dict[str, Any]] = []
    resolved_world_sha = expected_world_index_sha

    for index, (report, pin) in enumerate(pairs):
        label = f"reachability[{index}]"
        source_sha, world_sha, region = _reachability_identity(report, label)
        if source_sha != expected_map_sha:
            raise WorldHealthError(f"{label} does not prove the same source map as Map Quality")
        if resolved_world_sha is None:
            resolved_world_sha = world_sha
        elif world_sha != resolved_world_sha:
            raise WorldHealthError("reachability reports do not prove the same World Index")

        summary = _mapping(report.get("summary"), f"{label}.summary")
        routes = _count(summary.get("routes"), f"{label}.summary.routes")
        route_counts = _count_object(
            summary.get("routeStatusCounts"),
            f"{label}.summary.routeStatusCounts",
            allowed_keys=ROUTE_STATUSES,
        )
        _validate_category_total(routes, route_counts, f"{label}.summary.routes")
        transitions = _count(summary.get("transitions"), f"{label}.summary.transitions")
        transition_counts = _count_object(
            summary.get("transitionStatusCounts"),
            f"{label}.summary.transitionStatusCounts",
            allowed_keys=TRANSITION_STATUSES,
        )
        _validate_category_total(transitions, transition_counts, f"{label}.summary.transitions")
        mechanics = _count(summary.get("mechanics"), f"{label}.summary.mechanics")
        mechanic_counts = _count_object(
            summary.get("mechanicStatusCounts"),
            f"{label}.summary.mechanicStatusCounts",
            allowed_keys=MECHANIC_STATUSES,
        )
        _validate_category_total(mechanics, mechanic_counts, f"{label}.summary.mechanics")
        tile_counts = _count_object(summary.get("tileStatusCounts"), f"{label}.summary.tileStatusCounts")

        route_rows = _list(report.get("routes"), f"{label}.routes")
        if len(route_rows) != routes:
            raise WorldHealthError(f"{label}.routes length does not match summary.routes")
        transition_rows = _list(report.get("transitions"), f"{label}.transitions")
        transitions_truncated = bool(report.get("transitionsTruncated"))
        if len(transition_rows) > transitions or (not transitions_truncated and len(transition_rows) != transitions):
            raise WorldHealthError(f"{label}.transitions sample does not match summary/truncation evidence")
        mechanic_rows = _list(report.get("mechanics"), f"{label}.mechanics")
        mechanics_truncated = bool(report.get("mechanicsTruncated"))
        if len(mechanic_rows) > mechanics or (not mechanics_truncated and len(mechanic_rows) != mechanics):
            raise WorldHealthError(f"{label}.mechanics sample does not match summary/truncation evidence")
        loops_total = _count(summary.get("transitionLoops"), f"{label}.summary.transitionLoops")
        loop_rows = _list(report.get("transitionLoops"), f"{label}.transitionLoops")
        loops_truncated = bool(report.get("transitionLoopsTruncated"))
        if len(loop_rows) > loops_total or (not loops_truncated and len(loop_rows) != loops_total):
            raise WorldHealthError(f"{label}.transitionLoops sample does not match summary/truncation evidence")

        route_total += routes
        transition_total += transitions
        mechanic_total += mechanics
        one_way += _count(summary.get("oneWayTransitions"), f"{label}.summary.oneWayTransitions")
        dead_end += _count(summary.get("deadEndTransitions"), f"{label}.summary.deadEndTransitions")
        loops += loops_total
        route_counts_list.append(route_counts)
        transition_counts_list.append(transition_counts)
        mechanic_counts_list.append(mechanic_counts)
        tile_counts_list.append(tile_counts)
        source_truncated = source_truncated or transitions_truncated or mechanics_truncated or loops_truncated

        provenance_entries.append(
            {
                "input": dict(pin),
                "sourceMapSha256": source_sha,
                "worldIndexSha256": world_sha,
                "region": region,
                "inputOk": bool(report.get("ok")),
            }
        )

        for row_index, raw_route in enumerate(route_rows):
            route = _mapping(raw_route, f"{label}.routes[{row_index}]")
            status = str(route.get("status", ""))
            if status not in ROUTE_STATUSES:
                raise WorldHealthError(f"{label}.routes[{row_index}] has unsupported status {status!r}")
            if status == "confirmed":
                continue
            start = _required_position(route.get("start"), f"{label}.routes[{row_index}].start")
            goal = _required_position(route.get("goal"), f"{label}.routes[{row_index}].goal")
            evidence = {
                "start": start,
                "goal": goal,
                "status": status,
                "strictDistance": route.get("strictDistance"),
                "optimisticDistance": route.get("optimisticDistance"),
                "pathTruncated": bool(route.get("pathTruncated")),
                "transitionIdsUsed": list(route.get("transitionIdsUsed", [])),
                "issues": list(route.get("issues", [])),
            }
            candidates.append(
                _sample(
                    dimension="reachability",
                    kind="route",
                    status=status,
                    source_format=REACHABILITY_FORMAT,
                    source_report_sha256=str(pin["sha256"]),
                    evidence=evidence,
                    position=start,
                    source_id=f"{start}->{goal}",
                )
            )

        for row_index, raw_transition in enumerate(transition_rows):
            transition = _mapping(raw_transition, f"{label}.transitions[{row_index}]")
            status = str(transition.get("status", ""))
            if status not in TRANSITION_STATUSES:
                raise WorldHealthError(f"{label}.transitions[{row_index}] has unsupported status {status!r}")
            if status == "confirmed":
                continue
            source = _required_position(transition.get("source"), f"{label}.transitions[{row_index}].source")
            candidates.append(
                _sample(
                    dimension="reachability",
                    kind="transition",
                    status=status,
                    source_format=REACHABILITY_FORMAT,
                    source_report_sha256=str(pin["sha256"]),
                    evidence=transition,
                    position=source,
                    source_id=str(transition.get("id", row_index)),
                )
            )

        for row_index, raw_mechanic in enumerate(mechanic_rows):
            mechanic = _mapping(raw_mechanic, f"{label}.mechanics[{row_index}]")
            status = str(mechanic.get("status", ""))
            if status not in MECHANIC_STATUSES:
                raise WorldHealthError(f"{label}.mechanics[{row_index}] has unsupported status {status!r}")
            if status == "confirmed":
                continue
            position = _required_position(mechanic.get("position"), f"{label}.mechanics[{row_index}].position")
            candidates.append(
                _sample(
                    dimension="reachability",
                    kind="mechanic",
                    status=status,
                    source_format=REACHABILITY_FORMAT,
                    source_report_sha256=str(pin["sha256"]),
                    evidence=mechanic,
                    position=position,
                    source_id=str(mechanic.get("placementOrdinal", row_index)),
                )
            )

    route_counts_merged = _sum_count_objects(route_counts_list)
    transition_counts_merged = _sum_count_objects(transition_counts_list)
    mechanic_counts_merged = _sum_count_objects(mechanic_counts_list)
    tile_counts_merged = _sum_count_objects(tile_counts_list)
    samples, output_truncated = _bounded_samples(candidates, sample_limit)
    attention_mechanics = mechanic_counts_merged.get("conditional", 0) + mechanic_counts_merged.get("unreachable", 0)

    dimension = {
        "evidencePresent": bool(pairs),
        "reportCount": len(pairs),
        "routes": {"total": route_total, "statusCounts": route_counts_merged},
        "transitions": {
            "total": transition_total,
            "statusCounts": transition_counts_merged,
            "oneWay": one_way,
            "deadEnd": dead_end,
            "loops": loops,
        },
        "mechanics": {
            "total": mechanic_total,
            "statusCounts": mechanic_counts_merged,
            "attentionTotal": attention_mechanics,
        },
        "tiles": {"statusCounts": tile_counts_merged},
        "sampled": len(samples),
        "truncated": output_truncated or source_truncated,
        "outputSampleTruncated": output_truncated,
        "sourceEvidenceTruncated": source_truncated,
        "samples": samples,
    }
    return dimension, provenance_entries, resolved_world_sha


def _coverage_dimensions(
    pairs: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]],
    *,
    expected_map_sha: str,
    expected_world_index_sha: str | None,
    sample_limit: int,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], str | None]:
    stale_total = 0
    missing_total = 0
    targets_total = 0
    proven_current_total = 0
    stale_candidates: list[dict[str, Any]] = []
    missing_candidates: list[dict[str, Any]] = []
    provenance_entries: list[dict[str, Any]] = []
    resolved_world_sha = expected_world_index_sha

    for index, (report, pin) in enumerate(pairs):
        label = f"coverageMatrices[{index}]"
        source_sha, world_sha = _coverage_identity(report, label)
        if source_sha != expected_map_sha:
            raise WorldHealthError(f"{label} does not prove the same source map as Map Quality")
        if resolved_world_sha is None:
            resolved_world_sha = world_sha
        elif world_sha != resolved_world_sha:
            raise WorldHealthError("coverage matrices and reachability evidence do not prove the same World Index")

        summary = _mapping(report.get("summary"), f"{label}.summary")
        targets = _count(summary.get("targets"), f"{label}.summary.targets")
        stale = _count(
            summary.get("staleAgainstCurrentMapProvenance"),
            f"{label}.summary.staleAgainstCurrentMapProvenance",
        )
        missing = _count(summary.get("missingPhysicalScenario"), f"{label}.summary.missingPhysicalScenario")
        proven_current = _count(
            summary.get("physicallyRuntimeProvenOnCurrentMap"),
            f"{label}.summary.physicallyRuntimeProvenOnCurrentMap",
        )
        if proven_current > targets:
            raise WorldHealthError(f"{label} current-map physical proof count exceeds target count")
        mechanics = _list(report.get("mechanics"), f"{label}.mechanics")
        if len(mechanics) != targets:
            raise WorldHealthError(f"{label}.mechanics length does not match summary.targets")

        observed_stale = 0
        observed_missing = 0
        observed_proven_current = 0
        for row_index, raw_mechanic in enumerate(mechanics):
            mechanic = _mapping(raw_mechanic, f"{label}.mechanics[{row_index}]")
            target_id = mechanic.get("id")
            if not isinstance(target_id, str) or not target_id:
                raise WorldHealthError(f"{label}.mechanics[{row_index}].id must be a non-empty string")
            selector = _mapping(mechanic.get("selector"), f"{label}.mechanics[{row_index}].selector")
            position = _required_position(selector.get("position"), f"{label}.mechanics[{row_index}].selector.position")
            stale_flag = mechanic.get("staleAgainstCurrentMapProvenance") is True
            missing_flag = mechanic.get("missingPhysicalScenario") is True
            physical = _mapping(mechanic.get("physical"), f"{label}.mechanics[{row_index}].physical")
            current_proven = physical.get("runtimeProvenOnCurrentMap") is True
            observed_stale += int(stale_flag)
            observed_missing += int(missing_flag)
            observed_proven_current += int(current_proven)
            if stale_flag:
                stale_candidates.append(
                    _sample(
                        dimension="staleEvidence",
                        kind="coverage-target",
                        status="stale",
                        source_format=COVERAGE_FORMAT,
                        source_report_sha256=str(pin["sha256"]),
                        evidence=mechanic,
                        position=position,
                        source_id=target_id,
                    )
                )
            if missing_flag:
                missing_candidates.append(
                    _sample(
                        dimension="missingPhysicalCoverage",
                        kind="coverage-target",
                        status="missing-scenario",
                        source_format=COVERAGE_FORMAT,
                        source_report_sha256=str(pin["sha256"]),
                        evidence=mechanic,
                        position=position,
                        source_id=target_id,
                    )
                )
        if observed_stale != stale:
            raise WorldHealthError(f"{label} stale summary does not match mechanic evidence")
        if observed_missing != missing:
            raise WorldHealthError(f"{label} missing-physical summary does not match mechanic evidence")
        if observed_proven_current != proven_current:
            raise WorldHealthError(f"{label} current-map physical proof summary does not match mechanic evidence")

        targets_total += targets
        stale_total += stale
        missing_total += missing
        proven_current_total += proven_current
        provenance_entries.append(
            {
                "input": dict(pin),
                "sourceMapSha256": source_sha,
                "worldIndexSha256": world_sha,
                "targets": targets,
            }
        )

    stale_samples, stale_output_truncated = _bounded_samples(stale_candidates, sample_limit)
    missing_samples, missing_output_truncated = _bounded_samples(missing_candidates, sample_limit)
    stale_dimension = {
        "evidencePresent": bool(pairs),
        "reportCount": len(pairs),
        "total": stale_total,
        "sampled": len(stale_samples),
        "truncated": stale_output_truncated,
        "outputSampleTruncated": stale_output_truncated,
        "sourceEvidenceTruncated": False,
        "samples": stale_samples,
    }
    missing_dimension = {
        "evidencePresent": bool(pairs),
        "reportCount": len(pairs),
        "targets": targets_total,
        "total": missing_total,
        "missingScenarioTotal": missing_total,
        "runtimeNotProvenOnCurrentMapTotal": targets_total - proven_current_total,
        "sampled": len(missing_samples),
        "truncated": missing_output_truncated,
        "outputSampleTruncated": missing_output_truncated,
        "sourceEvidenceTruncated": False,
        "samples": missing_samples,
    }
    return stale_dimension, missing_dimension, provenance_entries, resolved_world_sha


def build_world_health_report(
    *,
    map_quality: Mapping[str, Any],
    reachability_reports: Sequence[Mapping[str, Any]] = (),
    coverage_matrices: Sequence[Mapping[str, Any]] = (),
    input_pins: Mapping[str, Any],
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    if isinstance(sample_limit, bool) or not isinstance(sample_limit, int) or not 1 <= sample_limit <= MAX_SAMPLE_LIMIT:
        raise WorldHealthError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")

    pins = _mapping(input_pins, "input_pins")
    map_quality_pin = _validate_input_pin(pins.get("mapQuality"), "input_pins.mapQuality", MAP_QUALITY_FORMAT)
    reachability_pins = _list(pins.get("reachability", []), "input_pins.reachability")
    coverage_pins = _list(pins.get("coverageMatrices", []), "input_pins.coverageMatrices")
    reachability_pairs = _sorted_report_pairs(
        reachability_reports,
        reachability_pins,
        label="reachability",
        expected_format=REACHABILITY_FORMAT,
    )
    coverage_pairs = _sorted_report_pairs(
        coverage_matrices,
        coverage_pins,
        label="coverageMatrices",
        expected_format=COVERAGE_FORMAT,
    )
    all_hashes = [map_quality_pin["sha256"]] + [pin["sha256"] for _, pin in reachability_pairs] + [
        pin["sha256"] for _, pin in coverage_pairs
    ]
    if len(set(all_hashes)) != len(all_hashes):
        raise WorldHealthError("contributing report SHA-256 pins must be unique")

    map_quality_object = _mapping(map_quality, "map_quality")
    source_map_sha = _map_quality_source_sha256(map_quality_object)
    structural, runtime_handlers = _map_quality_dimensions(
        map_quality_object,
        source_sha=source_map_sha,
        report_pin=map_quality_pin,
        sample_limit=sample_limit,
    )

    reachability, reachability_provenance, world_index_sha = _reachability_dimension(
        reachability_pairs,
        expected_map_sha=source_map_sha,
        expected_world_index_sha=None,
        sample_limit=sample_limit,
    )
    stale_evidence, missing_physical, coverage_provenance, world_index_sha = _coverage_dimensions(
        coverage_pairs,
        expected_map_sha=source_map_sha,
        expected_world_index_sha=world_index_sha,
        sample_limit=sample_limit,
    )

    map_quality_coverage = _mapping(map_quality_object.get("coverage"), "mapQuality.coverage")
    report = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "source": {
            "mapSha256": source_map_sha,
            "worldIndexSha256": world_index_sha,
        },
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "otbmParsedIndependently": False,
            "dynamicLuaExecuted": False,
            "crossDimensionDeduplication": False,
            "gameplayCorrectnessProven": False,
            "playerIntentProven": False,
            "globalAbsenceInferred": False,
            "healthScoreEmitted": False,
            "sampleLimitPerDimension": sample_limit,
        },
        "provenance": {
            "mapQuality": {
                "input": map_quality_pin,
                "sourceMapSha256": source_map_sha,
            },
            "reachability": reachability_provenance,
            "coverageMatrices": coverage_provenance,
        },
        "coverage": {
            "mapQuality": {
                "geometry": map_quality_coverage.get("geometry"),
                "reachability": map_quality_coverage.get("reachability"),
                "sameRegion": bool(map_quality_coverage.get("sameRegion")),
                "globalCoverageProven": False,
            },
            "reachabilityRegions": [entry["region"] for entry in reachability_provenance],
            "coverageMatrixCount": len(coverage_provenance),
            "globalCoverageProven": False,
        },
        "dimensions": {
            "structural": structural,
            "runtimeHandlers": runtime_handlers,
            "reachability": reachability,
            "staleEvidence": stale_evidence,
            "missingPhysicalCoverage": missing_physical,
        },
        "summary": {
            "structuralFindings": structural["total"],
            "runtimeHandlerPlacementFindings": runtime_handlers["placementFindingsTotal"],
            "attentionMechanics": reachability["mechanics"]["attentionTotal"],
            "staleEvidenceTargets": stale_evidence["total"],
            "missingPhysicalScenarioTargets": missing_physical["missingScenarioTotal"],
            "runtimeNotProvenOnCurrentMapTargets": missing_physical["runtimeNotProvenOnCurrentMapTotal"],
        },
        "notes": [
            "Counts are evidence events summed across explicit contributing reports; no cross-report or cross-dimension deduplication is inferred.",
            "Absent optional evidence remains explicit through evidencePresent=false and never proves global absence.",
            "Reachability is static geometry evidence; Physical E2E coverage remains a separate proof dimension.",
            "A missing Physical E2E scenario is a coverage gap, not proof that the mechanic is broken.",
            "This report emits no opaque health score and is not by itself a gameplay or certification gate.",
        ],
    }
    return report
