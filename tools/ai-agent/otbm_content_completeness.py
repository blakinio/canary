from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

MANIFEST_FORMAT = "canary-otbm-content-completeness-manifest-v1"
REPORT_FORMAT = "canary-otbm-content-completeness-audit-v1"
DEPENDENCY_FORMAT = "canary-otbm-dependency-blast-radius-v1"
COVERAGE_FORMAT = "canary-otbm-coverage-dashboard-v1"
SCHEMA_VERSION = 1

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CLASSIFICATIONS = {
    "confirmed",
    "map-only",
    "script-only",
    "unresolved",
    "conflicting",
    "not-applicable",
}
TARGET_KINDS = {"quest", "mechanic-set"}
STAGE_ROLES = {
    "entry",
    "npc-source-trigger",
    "storage-prerequisite",
    "storage-result",
    "mechanic",
    "door",
    "lever",
    "passage",
    "teleport",
    "transition",
    "boss",
    "spawn",
    "reward",
    "exit",
    "return",
}
DEPENDENCY_RELATIONS = {
    "depends-on",
    "references",
    "guards",
    "routes-through",
    "activates",
    "produces",
    "consumes",
    "covers",
    "validates",
    "affected-by",
}
ORPHAN_FINDING_KINDS = {
    "placement-without-handler",
    "handler-without-placement",
    "unreachable-transition",
    "disconnected-spawn-or-npc",
    "storage-producer-consumer-gap",
    "missing-route-interaction-evidence",
    "disconnected-access-context",
}


class ContentCompletenessError(ValueError):
    """Raised when selected-scope completeness evidence cannot be composed safely."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContentCompletenessError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContentCompletenessError(f"{label} must be an array")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContentCompletenessError(f"{label} must be a non-empty string")
    return value


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ContentCompletenessError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _pin(value: Any, label: str, expected_format: str) -> dict[str, Any]:
    pin = _mapping(value, label)
    if pin.get("format") != expected_format:
        raise ContentCompletenessError(f"{label}.format must be {expected_format}")
    size = pin.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ContentCompletenessError(f"{label}.size must be a non-negative integer")
    return {
        "fileName": _string(pin.get("fileName"), f"{label}.fileName"),
        "size": size,
        "sha256": _sha(pin.get("sha256"), f"{label}.sha256"),
        "format": expected_format,
    }


def _dependency_identity(report: Mapping[str, Any]) -> tuple[str, str]:
    if report.get("format") != DEPENDENCY_FORMAT or report.get("schemaVersion") != 1:
        raise ContentCompletenessError(f"Dependency Graph must use {DEPENDENCY_FORMAT} schemaVersion 1")
    source = _mapping(report.get("source"), "dependencyGraph.source")
    return (
        _sha(source.get("currentMapSha256"), "dependencyGraph.source.currentMapSha256"),
        _sha(source.get("currentWorldIndexSha256"), "dependencyGraph.source.currentWorldIndexSha256"),
    )


def _coverage_identity(report: Mapping[str, Any]) -> tuple[str, str]:
    if report.get("format") != COVERAGE_FORMAT or report.get("schemaVersion") != 1:
        raise ContentCompletenessError(f"Coverage Dashboard must use {COVERAGE_FORMAT} schemaVersion 1")
    current = _mapping(report.get("currentMap"), "coverageDashboard.currentMap")
    return (
        _sha(current.get("mapSha256"), "coverageDashboard.currentMap.mapSha256"),
        _sha(current.get("worldIndexSha256"), "coverageDashboard.currentMap.worldIndexSha256"),
    )


def _conflicting(blockers: Sequence[str]) -> bool:
    return any("CONFLICT" in blocker or "AMBIGU" in blocker for blocker in blockers)


def _combine(states: Sequence[str]) -> str:
    if "conflicting" in states:
        return "conflicting"
    if "unresolved" in states:
        return "unresolved"
    if "map-only" in states:
        return "map-only"
    if "script-only" in states:
        return "script-only"
    if states and all(state == "not-applicable" for state in states):
        return "not-applicable"
    return "confirmed"


def _node_state(node: Mapping[str, Any]) -> tuple[str, list[str]]:
    if node.get("state") == "proven":
        return "confirmed", []
    blockers = sorted({str(item) for item in node.get("blockers", [])})
    return ("conflicting" if _conflicting(blockers) else "unresolved"), blockers


def _coverage_state(value: Mapping[str, Any]) -> tuple[str, list[str]]:
    state = value.get("state")
    blockers = sorted({str(item) for item in value.get("blockers", [])})
    if state == "proven":
        return "confirmed", blockers
    if state == "not-applicable":
        return "not-applicable", blockers
    if state in {"stale", "conflicting"} or _conflicting(blockers):
        return "conflicting", blockers or [f"COVERAGE_{str(state).upper().replace('-', '_')}"]
    return "unresolved", blockers or [f"COVERAGE_{str(state or 'UNKNOWN').upper().replace('-', '_')}"]


def _query_reachable_nodes(query: Mapping[str, Any]) -> set[str]:
    reachable = {str(item) for item in query.get("roots", [])}
    for item in query.get("transitiveImpacts", []):
        if isinstance(item, Mapping) and isinstance(item.get("nodeId"), str):
            reachable.add(str(item["nodeId"]))
    return reachable


def _normalized_manifest(
    manifest: Mapping[str, Any],
    *,
    current_map_sha: str,
    current_world_sha: str,
    node_by_id: Mapping[str, Mapping[str, Any]],
    query_by_id: Mapping[str, Mapping[str, Any]],
    coverage_by_id: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if manifest.get("format") != MANIFEST_FORMAT or manifest.get("schemaVersion") != 1:
        raise ContentCompletenessError(f"manifest must use {MANIFEST_FORMAT} schemaVersion 1")
    source = _mapping(manifest.get("source"), "manifest.source")
    if _sha(source.get("mapSha256"), "manifest.source.mapSha256") != current_map_sha:
        raise ContentCompletenessError("manifest map must match Dependency Graph current map")
    if _sha(source.get("worldIndexSha256"), "manifest.source.worldIndexSha256") != current_world_sha:
        raise ContentCompletenessError("manifest World Index must match Dependency Graph current World Index")

    targets: list[dict[str, Any]] = []
    target_ids: set[str] = set()
    for target_index, raw_target in enumerate(_array(manifest.get("targets"), "manifest.targets")):
        target = _mapping(raw_target, f"manifest.targets[{target_index}]")
        target_id = _string(target.get("id"), f"manifest.targets[{target_index}].id")
        if target_id in target_ids:
            raise ContentCompletenessError(f"duplicate completeness target id: {target_id}")
        target_ids.add(target_id)
        kind = target.get("kind")
        if kind not in TARGET_KINDS:
            raise ContentCompletenessError(f"unsupported completeness target kind: {kind!r}")
        reason = _string(target.get("reason"), f"manifest.targets[{target_index}].reason")

        stages: list[dict[str, Any]] = []
        stage_ids: set[str] = set()
        for stage_index, raw_stage in enumerate(_array(target.get("stages"), f"manifest.targets[{target_index}].stages")):
            stage = _mapping(raw_stage, f"manifest.targets[{target_index}].stages[{stage_index}]")
            stage_id = _string(stage.get("id"), f"stage[{stage_index}].id")
            if stage_id in stage_ids:
                raise ContentCompletenessError(f"duplicate stage id in {target_id}: {stage_id}")
            stage_ids.add(stage_id)
            role = stage.get("role")
            if role not in STAGE_ROLES:
                raise ContentCompletenessError(f"unsupported completeness stage role: {role!r}")
            required = stage.get("required", True)
            if not isinstance(required, bool):
                raise ContentCompletenessError(f"stage {stage_id}.required must be boolean")
            missing = stage.get("missingClassification", "unresolved")
            if missing not in CLASSIFICATIONS - {"confirmed", "not-applicable"}:
                raise ContentCompletenessError(f"unsupported missing classification for stage {stage_id}: {missing!r}")

            node_ids: list[str] = []
            for node_id_raw in _array(stage.get("nodeIds", []), f"stage {stage_id}.nodeIds"):
                node_id = _string(node_id_raw, f"stage {stage_id}.nodeIds[]")
                if node_id not in node_by_id:
                    raise ContentCompletenessError(f"unknown dependency node: {node_id}")
                node_ids.append(node_id)

            coverage_requirements: list[dict[str, str]] = []
            for requirement_index, raw_requirement in enumerate(
                _array(stage.get("coverageRequirements", []), f"stage {stage_id}.coverageRequirements")
            ):
                requirement = _mapping(raw_requirement, f"stage {stage_id}.coverageRequirements[{requirement_index}]")
                coverage_id = _string(requirement.get("targetId"), "coverage target id")
                dimension = _string(requirement.get("dimension"), "coverage dimension")
                if coverage_id not in coverage_by_id:
                    raise ContentCompletenessError(f"unknown coverage target: {coverage_id}")
                dimensions = _mapping(coverage_by_id[coverage_id].get("dimensions"), f"coverage target {coverage_id}.dimensions")
                if dimension not in dimensions:
                    raise ContentCompletenessError(f"unknown coverage dimension {dimension} for target {coverage_id}")
                coverage_requirements.append({"targetId": coverage_id, "dimension": dimension})

            path_requirement = stage.get("pathRequirement")
            normalized_path: dict[str, Any] | None = None
            if path_requirement is not None:
                path = _mapping(path_requirement, f"stage {stage_id}.pathRequirement")
                query_id = _string(path.get("queryId"), f"stage {stage_id}.pathRequirement.queryId")
                if query_id not in query_by_id:
                    raise ContentCompletenessError(f"unknown dependency query: {query_id}")
                target_node_ids: list[str] = []
                for node_id_raw in _array(path.get("targetNodeIds"), f"stage {stage_id}.pathRequirement.targetNodeIds"):
                    node_id = _string(node_id_raw, "path target node id")
                    if node_id not in node_by_id:
                        raise ContentCompletenessError(f"unknown dependency node: {node_id}")
                    target_node_ids.append(node_id)
                if not target_node_ids:
                    raise ContentCompletenessError(f"stage {stage_id} pathRequirement.targetNodeIds must not be empty")
                normalized_path = {"queryId": query_id, "targetNodeIds": sorted(set(target_node_ids))}

            stages.append(
                {
                    "id": stage_id,
                    "role": role,
                    "required": required,
                    "nodeIds": sorted(set(node_ids)),
                    "coverageRequirements": sorted(
                        coverage_requirements,
                        key=lambda item: (item["targetId"], item["dimension"]),
                    ),
                    "pathRequirement": normalized_path,
                    "missingClassification": missing,
                }
            )

        checks: list[dict[str, Any]] = []
        check_ids: set[str] = set()
        for check_index, raw_check in enumerate(_array(target.get("orphanChecks", []), f"manifest.targets[{target_index}].orphanChecks")):
            check = _mapping(raw_check, f"manifest.targets[{target_index}].orphanChecks[{check_index}]")
            check_id = _string(check.get("id"), f"orphanChecks[{check_index}].id")
            if check_id in check_ids:
                raise ContentCompletenessError(f"duplicate orphan check id in {target_id}: {check_id}")
            check_ids.add(check_id)
            node_id = _string(check.get("nodeId"), f"orphan check {check_id}.nodeId")
            if node_id not in node_by_id:
                raise ContentCompletenessError(f"unknown dependency node: {node_id}")
            direction = check.get("direction")
            if direction not in {"incoming", "outgoing", "either"}:
                raise ContentCompletenessError(f"orphan check {check_id}.direction must be incoming, outgoing or either")
            relations = sorted({_string(item, "orphan relation") for item in _array(check.get("relations"), f"orphan check {check_id}.relations")})
            unsupported = sorted(set(relations) - DEPENDENCY_RELATIONS)
            if unsupported:
                raise ContentCompletenessError(f"orphan check {check_id} has unsupported relations: {unsupported}")
            counterpart_kinds = sorted(
                {_string(item, "counterpart kind") for item in _array(check.get("counterpartKinds"), f"orphan check {check_id}.counterpartKinds")}
            )
            if not relations or not counterpart_kinds:
                raise ContentCompletenessError(f"orphan check {check_id} relations and counterpartKinds must not be empty")
            missing = check.get("missingClassification", "unresolved")
            if missing not in {"map-only", "script-only", "unresolved", "conflicting"}:
                raise ContentCompletenessError(f"unsupported orphan missing classification: {missing!r}")
            finding_kind = check.get("findingKind")
            if finding_kind not in ORPHAN_FINDING_KINDS:
                raise ContentCompletenessError(f"unsupported orphan finding kind: {finding_kind!r}")
            checks.append(
                {
                    "id": check_id,
                    "nodeId": node_id,
                    "direction": direction,
                    "relations": relations,
                    "counterpartKinds": counterpart_kinds,
                    "missingClassification": missing,
                    "findingKind": finding_kind,
                }
            )

        stages.sort(key=lambda item: (item["role"], item["id"]))
        checks.sort(key=lambda item: item["id"])
        targets.append({"id": target_id, "kind": kind, "reason": reason, "stages": stages, "orphanChecks": checks})
    targets.sort(key=lambda item: (item["kind"], item["id"]))
    return targets


def _evaluate_stage(
    stage: Mapping[str, Any],
    *,
    node_by_id: Mapping[str, Mapping[str, Any]],
    query_by_id: Mapping[str, Mapping[str, Any]],
    coverage_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    states: list[str] = []
    blockers: list[str] = []
    finding_codes: list[str] = []

    for node_id in stage["nodeIds"]:
        state, node_blockers = _node_state(node_by_id[node_id])
        states.append(state)
        blockers.extend(node_blockers)

    coverage_results: list[dict[str, Any]] = []
    for requirement in stage["coverageRequirements"]:
        coverage_target = coverage_by_id[requirement["targetId"]]
        dimension_value = _mapping(
            _mapping(coverage_target.get("dimensions"), "coverage dimensions").get(requirement["dimension"]),
            "coverage dimension",
        )
        state, dimension_blockers = _coverage_state(dimension_value)
        states.append(state)
        blockers.extend(dimension_blockers)
        coverage_results.append({**requirement, "classification": state, "blockers": dimension_blockers})

    path_result: dict[str, Any] | None = None
    if stage["pathRequirement"] is not None:
        path = stage["pathRequirement"]
        query = query_by_id[path["queryId"]]
        reachable = _query_reachable_nodes(query)
        missing_nodes = sorted(set(path["targetNodeIds"]) - reachable)
        if missing_nodes:
            states.append("unresolved")
            finding_codes.append("REQUIRED_PATH_NOT_PROVEN")
        else:
            states.append("confirmed")
        path_result = {
            "queryId": path["queryId"],
            "targetNodeIds": list(path["targetNodeIds"]),
            "missingNodeIds": missing_nodes,
            "classification": "confirmed" if not missing_nodes else "unresolved",
        }

    if not stage["nodeIds"] and not stage["coverageRequirements"] and stage["pathRequirement"] is None:
        states.append(stage["missingClassification"])
        if stage["required"]:
            finding_codes.append("MISSING_REQUIRED_STAGE_EVIDENCE")

    classification = _combine(states)
    if stage["required"] and classification != "confirmed":
        if classification == "conflicting":
            finding_codes.append("REQUIRED_STAGE_CONFLICTING")
        elif classification in {"map-only", "script-only"}:
            finding_codes.append("REQUIRED_STAGE_PARTIAL")
        elif "MISSING_REQUIRED_STAGE_EVIDENCE" not in finding_codes and "REQUIRED_PATH_NOT_PROVEN" not in finding_codes:
            finding_codes.append("REQUIRED_STAGE_UNRESOLVED")

    return {
        "id": stage["id"],
        "role": stage["role"],
        "required": stage["required"],
        "classification": classification,
        "nodeIds": list(stage["nodeIds"]),
        "coverageRequirements": coverage_results,
        "pathRequirement": path_result,
        "blockers": sorted(set(blockers)),
        "findingCodes": sorted(set(finding_codes)),
    }


def _edge_matches(
    edge: Mapping[str, Any],
    check: Mapping[str, Any],
    node_by_id: Mapping[str, Mapping[str, Any]],
) -> bool:
    if edge.get("relation") not in check["relations"]:
        return False
    node_id = check["nodeId"]
    if check["direction"] == "outgoing":
        if edge.get("source") != node_id:
            return False
        counterpart = edge.get("target")
    elif check["direction"] == "incoming":
        if edge.get("target") != node_id:
            return False
        counterpart = edge.get("source")
    else:
        if edge.get("source") == node_id:
            counterpart = edge.get("target")
        elif edge.get("target") == node_id:
            counterpart = edge.get("source")
        else:
            return False
    return isinstance(counterpart, str) and counterpart in node_by_id and node_by_id[counterpart].get("kind") in check["counterpartKinds"]


def _evaluate_orphan_check(
    check: Mapping[str, Any],
    *,
    edges: Sequence[Mapping[str, Any]],
    node_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    matching = [edge for edge in edges if _edge_matches(edge, check, node_by_id)]
    proven = sorted(str(edge["id"]) for edge in matching if edge.get("state") == "proven")
    unresolved = sorted(str(edge["id"]) for edge in matching if edge.get("state") != "proven")
    blockers = sorted(
        {
            str(blocker)
            for edge in matching
            if edge.get("state") != "proven"
            for blocker in edge.get("blockers", [])
        }
    )
    if proven:
        classification = "confirmed"
    elif unresolved:
        classification = "conflicting" if _conflicting(blockers) else "unresolved"
    else:
        classification = check["missingClassification"]
    finding = classification != "confirmed"
    return {
        "id": check["id"],
        "nodeId": check["nodeId"],
        "direction": check["direction"],
        "relations": list(check["relations"]),
        "counterpartKinds": list(check["counterpartKinds"]),
        "classification": classification,
        "finding": finding,
        "findingKind": check["findingKind"] if finding else None,
        "provenEdgeIds": proven,
        "unresolvedEdgeIds": unresolved,
        "blockers": blockers,
    }


def build_content_completeness_report(
    *,
    manifest: Mapping[str, Any],
    dependency_graph: Mapping[str, Any],
    coverage_dashboard: Mapping[str, Any],
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    pins = _mapping(input_pins, "input_pins")
    manifest_pin = _pin(pins.get("manifest"), "input_pins.manifest", MANIFEST_FORMAT)
    dependency_pin = _pin(pins.get("dependencyGraph"), "input_pins.dependencyGraph", DEPENDENCY_FORMAT)
    coverage_pin = _pin(pins.get("coverageDashboard"), "input_pins.coverageDashboard", COVERAGE_FORMAT)
    if len({manifest_pin["sha256"], dependency_pin["sha256"], coverage_pin["sha256"]}) != 3:
        raise ContentCompletenessError("all completeness input SHA-256 pins must be distinct")

    dependency = _mapping(dependency_graph, "dependency_graph")
    coverage = _mapping(coverage_dashboard, "coverage_dashboard")
    current_map_sha, current_world_sha = _dependency_identity(dependency)
    coverage_map_sha, coverage_world_sha = _coverage_identity(coverage)
    if (coverage_map_sha, coverage_world_sha) != (current_map_sha, current_world_sha):
        raise ContentCompletenessError("Coverage Dashboard current map and World Index must match Dependency Graph")

    nodes = [_mapping(item, "dependencyGraph.nodes[]") for item in _array(dependency.get("nodes"), "dependencyGraph.nodes")]
    edges = [_mapping(item, "dependencyGraph.edges[]") for item in _array(dependency.get("edges"), "dependencyGraph.edges")]
    queries = [_mapping(item, "dependencyGraph.queries[]") for item in _array(dependency.get("queries"), "dependencyGraph.queries")]
    node_by_id = {_string(node.get("id"), "dependency node id"): node for node in nodes}
    query_by_id = {_string(query.get("id"), "dependency query id"): query for query in queries}
    if len(node_by_id) != len(nodes) or len(query_by_id) != len(queries):
        raise ContentCompletenessError("Dependency Graph contains duplicate node or query IDs")

    coverage_targets = [_mapping(item, "coverageDashboard.targets[]") for item in _array(coverage.get("targets"), "coverageDashboard.targets")]
    coverage_by_id = {_string(item.get("id"), "coverage target id"): item for item in coverage_targets}
    if len(coverage_by_id) != len(coverage_targets):
        raise ContentCompletenessError("Coverage Dashboard contains duplicate target IDs")

    targets = _normalized_manifest(
        _mapping(manifest, "manifest"),
        current_map_sha=current_map_sha,
        current_world_sha=current_world_sha,
        node_by_id=node_by_id,
        query_by_id=query_by_id,
        coverage_by_id=coverage_by_id,
    )

    target_reports: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for target in targets:
        stage_reports = [
            _evaluate_stage(
                stage,
                node_by_id=node_by_id,
                query_by_id=query_by_id,
                coverage_by_id=coverage_by_id,
            )
            for stage in target["stages"]
        ]
        check_reports = [
            _evaluate_orphan_check(check, edges=edges, node_by_id=node_by_id)
            for check in target["orphanChecks"]
        ]
        required_stages = [stage for stage in stage_reports if stage["required"]]
        requirements_satisfied = all(stage["classification"] == "confirmed" for stage in required_stages)
        for stage in stage_reports:
            for code in stage["findingCodes"]:
                findings.append(
                    {
                        "id": f"{target['id']}:stage:{stage['id']}:{code}",
                        "targetId": target["id"],
                        "kind": "completeness-stage",
                        "classification": stage["classification"],
                        "code": code,
                        "stageId": stage["id"],
                    }
                )
        for check in check_reports:
            if check["finding"]:
                findings.append(
                    {
                        "id": f"{target['id']}:orphan:{check['id']}:{check['findingKind']}",
                        "targetId": target["id"],
                        "kind": "orphan-or-disconnection",
                        "classification": check["classification"],
                        "code": check["findingKind"],
                        "checkId": check["id"],
                    }
                )
        target_reports.append(
            {
                "id": target["id"],
                "kind": target["kind"],
                "reason": target["reason"],
                "requirementsSatisfied": requirements_satisfied,
                "runtimeGameplayCompletionProven": False,
                "stages": stage_reports,
                "orphanChecks": check_reports,
                "summary": {
                    "stageCount": len(stage_reports),
                    "requiredStageCount": len(required_stages),
                    "confirmedRequiredStageCount": sum(
                        1 for stage in required_stages if stage["classification"] == "confirmed"
                    ),
                    "orphanCheckCount": len(check_reports),
                    "orphanFindingCount": sum(1 for check in check_reports if check["finding"]),
                },
            }
        )

    findings.sort(key=lambda item: (item["targetId"], item["kind"], item["id"]))
    target_reports.sort(key=lambda item: (item["kind"], item["id"]))
    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "source": {
            "currentMapSha256": current_map_sha,
            "currentWorldIndexSha256": current_world_sha,
        },
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "otbmParsedIndependently": False,
            "scriptResolutionRecomputed": False,
            "storageGraphRecomputed": False,
            "pathfindingExecuted": False,
            "dependencyGraphRecomputed": False,
            "physicalE2eExecuted": False,
            "dynamicLuaExecuted": False,
            "globalAbsenceInferred": False,
            "runtimeGameplayCompletionClaimed": False,
            "automaticRepairDirected": False,
            "certificationAssigned": False,
            "scenarioPrioritizationDirected": False,
        },
        "provenance": {
            "manifest": manifest_pin,
            "dependencyGraph": dependency_pin,
            "coverageDashboard": coverage_pin,
        },
        "summary": {
            "targetCount": len(target_reports),
            "requirementsSatisfiedTargetCount": sum(1 for target in target_reports if target["requirementsSatisfied"]),
            "findingCount": len(findings),
            "runtimeGameplayCompletionProvenTargetCount": 0,
        },
        "targets": target_reports,
        "findings": findings,
        "notes": [
            "This report is selected-scope static evidence only; absence from the reviewed manifest or graph is not global absence.",
            "Quest/mechanic stages and orphan checks are explicitly reviewed and are not inferred from names, proximity, sprites or source layout.",
            "Unresolved QA-008 dependency edges remain unresolved/conflicting and are never promoted to map-only or script-only absence.",
            "requirementsSatisfied does not prove runtime quest completion; Physical E2E remains owned by Universal E2E.",
        ],
    }


def canonical_report_sha256(report: Mapping[str, Any]) -> str:
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
