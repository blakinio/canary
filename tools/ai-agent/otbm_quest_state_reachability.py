from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import deque
from typing import Any, Mapping, Sequence

from otbm_route_interactions import RouteInteractionError, resolve_interaction

MANIFEST_FORMAT = "canary-otbm-quest-state-reachability-manifest-v1"
REPORT_FORMAT = "canary-otbm-quest-state-reachability-v1"
STORAGE_GRAPH_FORMAT = "canary-otbm-storage-graph-v1"
INTERACTION_REGISTRY_FORMAT = "canary-otbm-route-interactions-v1"
SCHEMA_VERSION = 1

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TARGET_KINDS = {"quest", "mechanic-set"}
STORAGE_NAMESPACES = {
    "player-storage",
    "account-storage",
    "player-kv",
    "account-kv",
    "global-storage",
    "global-kv",
    "database",
}
GOAL_CLASSIFICATIONS = {
    "reachable",
    "blocked-by-evidence",
    "unreachable-in-selected-scope",
    "external-or-unproven",
}


class QuestStateReachabilityError(ValueError):
    """Raised when selected-scope quest-state evidence cannot be composed safely."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise QuestStateReachabilityError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise QuestStateReachabilityError(f"{label} must be an array")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise QuestStateReachabilityError(f"{label} must be a non-empty string")
    return value


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise QuestStateReachabilityError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _literal(value: Any, label: str) -> Any:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise QuestStateReachabilityError(f"{label} must be a JSON literal supported by Storage Graph")


def _storage_key(value: Any, label: str) -> int | str:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str) and value:
        return value
    raise QuestStateReachabilityError(f"{label} must be a non-empty string or integer")


def _pin(value: Any, label: str, expected_format: str) -> dict[str, Any]:
    pin = _mapping(value, label)
    if pin.get("format") != expected_format:
        raise QuestStateReachabilityError(f"{label}.format must be {expected_format}")
    size = pin.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise QuestStateReachabilityError(f"{label}.size must be a non-negative integer")
    return {
        "fileName": _string(pin.get("fileName"), f"{label}.fileName"),
        "size": size,
        "sha256": _sha(pin.get("sha256"), f"{label}.sha256"),
        "format": expected_format,
    }


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_report_sha256(report: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(report).encode("utf-8")).hexdigest()


def _normalize_state(value: Any, label: str) -> dict[str, Any]:
    state = _mapping(value, label)
    namespace = state.get("namespace")
    if namespace not in STORAGE_NAMESPACES:
        raise QuestStateReachabilityError(f"{label}.namespace is unsupported: {namespace!r}")
    return {
        "namespace": namespace,
        "key": _storage_key(state.get("key"), f"{label}.key"),
        "value": _literal(state.get("value"), f"{label}.value"),
    }


def _state_key(state: Mapping[str, Any]) -> str:
    return _canonical([state["namespace"], state["key"], state["value"]])


def _transition_states(transition: Mapping[str, Any], label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    namespace = transition.get("namespace")
    if namespace not in STORAGE_NAMESPACES:
        raise QuestStateReachabilityError(f"{label}.namespace is unsupported: {namespace!r}")
    key = _storage_key(transition.get("key"), f"{label}.key")
    prerequisite = _mapping(transition.get("prerequisite"), f"{label}.prerequisite")
    if prerequisite.get("operator") != "==":
        raise QuestStateReachabilityError(f"{label} must use an exact == prerequisite")
    before = {
        "namespace": namespace,
        "key": key,
        "value": _literal(prerequisite.get("value"), f"{label}.prerequisite.value"),
    }
    result = _mapping(transition.get("result"), f"{label}.result")
    kind = result.get("kind")
    if kind not in {"literal", "delta", "delete"}:
        raise QuestStateReachabilityError(f"{label}.result.kind is unsupported: {kind!r}")
    after_value = _literal(result.get("value"), f"{label}.result.value")
    if kind == "delta":
        delta = result.get("delta")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise QuestStateReachabilityError(f"{label}.result.delta must be an integer")
        if isinstance(before["value"], bool) or not isinstance(before["value"], int):
            raise QuestStateReachabilityError(f"{label} delta transition requires an integer exact prerequisite")
        expected = before["value"] + delta
        if after_value != expected:
            raise QuestStateReachabilityError(
                f"{label}.result.value must equal prerequisite + delta ({expected})"
            )
    if kind == "delete" and after_value is not None:
        raise QuestStateReachabilityError(f"{label}.result.value must be null for delete transitions")
    after = {"namespace": namespace, "key": key, "value": after_value}
    return before, after


def _validate_storage_graph(storage_graph: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if storage_graph.get("format") != STORAGE_GRAPH_FORMAT or storage_graph.get("schemaVersion") != SCHEMA_VERSION:
        raise QuestStateReachabilityError(
            f"Storage Graph must use {STORAGE_GRAPH_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    if storage_graph.get("complete") is not True:
        raise QuestStateReachabilityError("Storage Graph must be complete before state reachability can be evaluated")
    transitions = _array(storage_graph.get("transitions"), "storageGraph.transitions")
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, raw_transition in enumerate(transitions):
        transition = _mapping(raw_transition, f"storageGraph.transitions[{index}]")
        transition_id = _string(transition.get("id"), f"storageGraph.transitions[{index}].id")
        if transition_id in by_id:
            raise QuestStateReachabilityError(f"duplicate Storage Graph transition id: {transition_id}")
        _transition_states(transition, f"storageGraph transition {transition_id}")
        by_id[transition_id] = transition
    return by_id


def _normalize_interaction(value: Any, label: str) -> dict[str, Any] | None:
    if value is None:
        return None
    interaction = _mapping(value, label)
    query = dict(_mapping(interaction.get("query"), f"{label}.query"))
    if "transitionId" not in query and "position" not in query:
        raise QuestStateReachabilityError(f"{label}.query must contain transitionId or exact position evidence")
    allowed_query = {
        "transitionId",
        "transitionKind",
        "transitionEvidenceSource",
        "position",
        "itemId",
        "actionId",
        "uniqueId",
        "houseDoorId",
        "scriptStatus",
    }
    unknown = sorted(set(query) - allowed_query)
    if unknown:
        raise QuestStateReachabilityError(f"{label}.query contains unsupported fields: {unknown}")
    normalized: dict[str, Any] = {"query": copy.deepcopy(query)}
    for field in ("expectedTransitionManifestSha256", "expectedScriptResolutionSha256"):
        raw = interaction.get(field)
        normalized[field] = None if raw is None else _sha(raw, f"{label}.{field}")
    return normalized


def _normalize_manifest(
    manifest: Mapping[str, Any],
    *,
    transition_by_id: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    if manifest.get("format") != MANIFEST_FORMAT or manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise QuestStateReachabilityError(
            f"manifest must use {MANIFEST_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    source = _mapping(manifest.get("source"), "manifest.source")
    source_identity = {
        "mapSha256": _sha(source.get("mapSha256"), "manifest.source.mapSha256"),
        "worldIndexSha256": _sha(source.get("worldIndexSha256"), "manifest.source.worldIndexSha256"),
    }
    targets: list[dict[str, Any]] = []
    target_ids: set[str] = set()
    for target_index, raw_target in enumerate(_array(manifest.get("targets"), "manifest.targets")):
        label = f"manifest.targets[{target_index}]"
        target = _mapping(raw_target, label)
        target_id = _string(target.get("id"), f"{label}.id")
        if target_id in target_ids:
            raise QuestStateReachabilityError(f"duplicate reachability target id: {target_id}")
        target_ids.add(target_id)
        kind = target.get("kind")
        if kind not in TARGET_KINDS:
            raise QuestStateReachabilityError(f"unsupported reachability target kind: {kind!r}")
        reason = _string(target.get("reason"), f"{label}.reason")

        initial_states: list[dict[str, Any]] = []
        seen_initial: set[str] = set()
        for state_index, raw_state in enumerate(_array(target.get("initialStates"), f"{label}.initialStates")):
            state = _normalize_state(raw_state, f"{label}.initialStates[{state_index}]")
            key = _state_key(state)
            if key not in seen_initial:
                seen_initial.add(key)
                initial_states.append(state)
        if not initial_states:
            raise QuestStateReachabilityError(f"{label}.initialStates must not be empty")

        selections: list[dict[str, Any]] = []
        seen_transitions: set[str] = set()
        for selection_index, raw_selection in enumerate(_array(target.get("transitions"), f"{label}.transitions")):
            selection_label = f"{label}.transitions[{selection_index}]"
            selection = _mapping(raw_selection, selection_label)
            transition_id = _string(selection.get("transitionId"), f"{selection_label}.transitionId")
            if transition_id in seen_transitions:
                raise QuestStateReachabilityError(f"duplicate transition {transition_id} in target {target_id}")
            seen_transitions.add(transition_id)
            if transition_id not in transition_by_id:
                raise QuestStateReachabilityError(f"unknown Storage Graph transition: {transition_id}")
            expected_context = [
                copy.deepcopy(dict(_mapping(item, f"{selection_label}.mapContextExpected[]")))
                for item in _array(selection.get("mapContextExpected", []), f"{selection_label}.mapContextExpected")
            ]
            interaction = _normalize_interaction(selection.get("interaction"), f"{selection_label}.interaction")
            if not expected_context and interaction is None:
                raise QuestStateReachabilityError(
                    f"{selection_label} must declare exact mapContextExpected evidence or a reviewed interaction requirement"
                )
            selections.append(
                {
                    "transitionId": transition_id,
                    "mapContextExpected": expected_context,
                    "interaction": interaction,
                }
            )

        goals: list[dict[str, Any]] = []
        goal_ids: set[str] = set()
        for goal_index, raw_goal in enumerate(_array(target.get("goals"), f"{label}.goals")):
            goal_label = f"{label}.goals[{goal_index}]"
            goal = _mapping(raw_goal, goal_label)
            goal_id = _string(goal.get("id"), f"{goal_label}.id")
            if goal_id in goal_ids:
                raise QuestStateReachabilityError(f"duplicate goal id in {target_id}: {goal_id}")
            goal_ids.add(goal_id)
            state = _normalize_state(goal, goal_label)
            goals.append({"id": goal_id, **state})
        if not goals:
            raise QuestStateReachabilityError(f"{label}.goals must not be empty")

        targets.append(
            {
                "id": target_id,
                "kind": kind,
                "reason": reason,
                "initialStates": sorted(initial_states, key=_state_key),
                "transitions": sorted(selections, key=lambda item: item["transitionId"]),
                "goals": sorted(goals, key=lambda item: item["id"]),
            }
        )
    if not targets:
        raise QuestStateReachabilityError("manifest.targets must not be empty")
    return source_identity, sorted(targets, key=lambda item: item["id"])


def _map_context_blockers(
    transition: Mapping[str, Any],
    expected: Sequence[Mapping[str, Any]],
    *,
    quest_validation_provided: bool,
) -> list[dict[str, Any]]:
    if not expected:
        return []
    blockers: list[dict[str, Any]] = []
    if not quest_validation_provided:
        blockers.append({"code": "QUEST_VALIDATION_PROVENANCE_REQUIRED"})
    actual = transition.get("mapContext")
    if not isinstance(actual, list):
        actual = []
    actual_values = {_canonical(item) for item in actual if isinstance(item, Mapping)}
    missing = [copy.deepcopy(dict(item)) for item in expected if _canonical(item) not in actual_values]
    if missing:
        blockers.append({"code": "MAP_CONTEXT_MISMATCH", "missingExpected": missing})
    return blockers


def _interaction_blockers(
    interaction: Mapping[str, Any] | None,
    *,
    registry: Mapping[str, Any] | None,
    source: Mapping[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    if interaction is None:
        return [], None
    if registry is None:
        return [{"code": "INTERACTION_REGISTRY_REQUIRED"}], None
    query = _mapping(interaction.get("query"), "interaction.query")
    try:
        resolution = resolve_interaction(
            registry,
            expected_source_map_sha256=source["mapSha256"],
            expected_world_index_sha256=source["worldIndexSha256"],
            transition_id=query.get("transitionId"),
            transition_kind=query.get("transitionKind"),
            transition_evidence_source=query.get("transitionEvidenceSource"),
            position=query.get("position"),
            item_id=query.get("itemId"),
            action_id=query.get("actionId"),
            unique_id=query.get("uniqueId"),
            house_door_id=query.get("houseDoorId"),
            script_status=query.get("scriptStatus"),
            expected_transition_manifest_sha256=interaction.get("expectedTransitionManifestSha256"),
            expected_script_resolution_sha256=interaction.get("expectedScriptResolutionSha256"),
        )
    except RouteInteractionError as exc:
        return [{"code": "INTERACTION_RESOLUTION_ERROR", "message": str(exc)}], None
    if resolution.get("executionStatus") == "executable":
        return [], resolution
    blockers = []
    for item in resolution.get("blockers", []):
        if isinstance(item, Mapping):
            blockers.append({"code": f"INTERACTION_{str(item.get('code', 'blocked')).upper().replace('-', '_')}", "detail": copy.deepcopy(dict(item))})
    return blockers or [{"code": "INTERACTION_BLOCKED"}], resolution


def _evaluate_transition(
    selection: Mapping[str, Any],
    *,
    transition: Mapping[str, Any],
    registry: Mapping[str, Any] | None,
    source: Mapping[str, str],
    quest_validation_provided: bool,
) -> dict[str, Any]:
    transition_id = str(selection["transitionId"])
    before, after = _transition_states(transition, f"Storage Graph transition {transition_id}")
    blockers = _map_context_blockers(
        transition,
        selection.get("mapContextExpected", []),
        quest_validation_provided=quest_validation_provided,
    )
    issues = transition.get("issues", [])
    if isinstance(issues, list) and issues:
        blockers.append({"code": "STORAGE_TRANSITION_HAS_ISSUES", "issues": sorted(str(item) for item in issues)})
    interaction_blockers, resolution = _interaction_blockers(
        selection.get("interaction"), registry=registry, source=source
    )
    blockers.extend(interaction_blockers)
    blockers = sorted(blockers, key=lambda item: (_string(item.get("code"), "blocker.code"), _canonical(item)))
    return {
        "transitionId": transition_id,
        "from": before,
        "to": after,
        "status": "proven" if not blockers else "blocked",
        "blockers": blockers,
        "mapContextExpected": copy.deepcopy(selection.get("mapContextExpected", [])),
        "interactionResolution": copy.deepcopy(resolution),
    }


def _traverse(initial_keys: set[str], edges: Sequence[Mapping[str, Any]], *, proven_only: bool) -> tuple[set[str], dict[str, tuple[str, str]]]:
    adjacency: dict[str, list[Mapping[str, Any]]] = {}
    for edge in edges:
        if proven_only and edge.get("status") != "proven":
            continue
        adjacency.setdefault(_state_key(_mapping(edge["from"], "edge.from")), []).append(edge)
    for values in adjacency.values():
        values.sort(key=lambda item: str(item["transitionId"]))
    reached = set(initial_keys)
    predecessor: dict[str, tuple[str, str]] = {}
    queue = deque(sorted(initial_keys))
    while queue:
        current = queue.popleft()
        for edge in adjacency.get(current, []):
            target = _state_key(_mapping(edge["to"], "edge.to"))
            if target in reached:
                continue
            reached.add(target)
            predecessor[target] = (current, str(edge["transitionId"]))
            queue.append(target)
    return reached, predecessor


def _path_transition_ids(state_key: str, predecessor: Mapping[str, tuple[str, str]]) -> list[str]:
    result: list[str] = []
    current = state_key
    while current in predecessor:
        previous, transition_id = predecessor[current]
        result.append(transition_id)
        current = previous
    result.reverse()
    return result


def _evaluate_target(
    target: Mapping[str, Any],
    *,
    transition_by_id: Mapping[str, Mapping[str, Any]],
    registry: Mapping[str, Any] | None,
    source: Mapping[str, str],
    quest_validation_provided: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    evaluated_edges = [
        _evaluate_transition(
            selection,
            transition=transition_by_id[str(selection["transitionId"])],
            registry=registry,
            source=source,
            quest_validation_provided=quest_validation_provided,
        )
        for selection in target["transitions"]
    ]
    evaluated_edges.sort(key=lambda item: item["transitionId"])
    initial_states = copy.deepcopy(target["initialStates"])
    initial_keys = {_state_key(state) for state in initial_states}
    proven_reached, proven_predecessor = _traverse(initial_keys, evaluated_edges, proven_only=True)
    candidate_reached, candidate_predecessor = _traverse(initial_keys, evaluated_edges, proven_only=False)

    state_by_key: dict[str, dict[str, Any]] = {_state_key(state): copy.deepcopy(state) for state in initial_states}
    produced_keys: set[str] = set()
    consumed_keys: set[str] = set()
    edge_by_id = {str(edge["transitionId"]): edge for edge in evaluated_edges}
    for edge in evaluated_edges:
        before = _mapping(edge["from"], "edge.from")
        after = _mapping(edge["to"], "edge.to")
        before_key = _state_key(before)
        after_key = _state_key(after)
        state_by_key.setdefault(before_key, copy.deepcopy(dict(before)))
        state_by_key.setdefault(after_key, copy.deepcopy(dict(after)))
        consumed_keys.add(before_key)
        produced_keys.add(after_key)

    reachable_states = [
        {
            **state_by_key[key],
            "pathTransitionIds": _path_transition_ids(key, proven_predecessor),
        }
        for key in sorted(proven_reached)
        if key in state_by_key
    ]

    findings: list[dict[str, Any]] = []
    goals: list[dict[str, Any]] = []
    for goal in target["goals"]:
        goal_state = {"namespace": goal["namespace"], "key": goal["key"], "value": goal["value"]}
        key = _state_key(goal_state)
        blockers: list[dict[str, Any]] = []
        if key in proven_reached:
            classification = "reachable"
            path_ids = _path_transition_ids(key, proven_predecessor)
        elif key in candidate_reached:
            classification = "blocked-by-evidence"
            path_ids = _path_transition_ids(key, candidate_predecessor)
            for transition_id in path_ids:
                edge = edge_by_id[transition_id]
                if edge["status"] != "proven":
                    blockers.extend(copy.deepcopy(edge["blockers"]))
        elif key not in produced_keys:
            classification = "external-or-unproven"
            path_ids = []
        else:
            classification = "unreachable-in-selected-scope"
            path_ids = []
        if classification not in GOAL_CLASSIFICATIONS:
            raise AssertionError(classification)
        goal_result = {
            "id": goal["id"],
            **goal_state,
            "classification": classification,
            "pathTransitionIds": path_ids,
            "blockers": blockers,
        }
        goals.append(goal_result)
        if classification != "reachable":
            code = {
                "blocked-by-evidence": "QUEST_STATE_BLOCKED_BY_EVIDENCE",
                "unreachable-in-selected-scope": "POTENTIALLY_UNREACHABLE_QUEST_STATE",
                "external-or-unproven": "QUEST_STATE_EXTERNAL_OR_UNPROVEN",
            }[classification]
            findings.append(
                {
                    "targetId": target["id"],
                    "goalId": goal["id"],
                    "code": code,
                    "classification": classification,
                    "state": copy.deepcopy(goal_state),
                    "blockers": blockers,
                }
            )

    external_prerequisites = [
        {
            **state_by_key[key],
            "classification": "external-or-unproven",
        }
        for key in sorted(consumed_keys - proven_reached - produced_keys)
    ]
    target_report = {
        "id": target["id"],
        "kind": target["kind"],
        "reason": target["reason"],
        "initialStates": initial_states,
        "transitions": evaluated_edges,
        "reachableStates": reachable_states,
        "externalPrerequisites": external_prerequisites,
        "goals": goals,
        "requirementsSatisfied": all(goal["classification"] == "reachable" for goal in goals),
        "runtimeGameplayCompletionProven": False,
    }
    return target_report, findings


def build_quest_state_reachability_report(
    *,
    manifest: Mapping[str, Any],
    storage_graph: Mapping[str, Any],
    route_interactions: Mapping[str, Any] | None,
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    transition_by_id = _validate_storage_graph(storage_graph)
    source, targets = _normalize_manifest(manifest, transition_by_id=transition_by_id)

    manifest_pin = _pin(input_pins.get("manifest"), "inputPins.manifest", MANIFEST_FORMAT)
    storage_pin = _pin(input_pins.get("storageGraph"), "inputPins.storageGraph", STORAGE_GRAPH_FORMAT)
    interaction_pin_raw = input_pins.get("routeInteractions")
    interaction_pin = None
    if route_interactions is not None:
        if route_interactions.get("format") != INTERACTION_REGISTRY_FORMAT:
            raise QuestStateReachabilityError(
                f"Route Interaction Registry must use {INTERACTION_REGISTRY_FORMAT}"
            )
        interaction_pin = _pin(
            interaction_pin_raw,
            "inputPins.routeInteractions",
            INTERACTION_REGISTRY_FORMAT,
        )
    elif interaction_pin_raw is not None:
        raise QuestStateReachabilityError("routeInteractions input pin requires a Route Interaction Registry document")

    inputs = _mapping(storage_graph.get("inputs"), "storageGraph.inputs")
    quest_validation_provided = inputs.get("questValidation") is not None

    target_reports: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for target in targets:
        target_report, target_findings = _evaluate_target(
            target,
            transition_by_id=transition_by_id,
            registry=route_interactions,
            source=source,
            quest_validation_provided=quest_validation_provided,
        )
        target_reports.append(target_report)
        findings.extend(target_findings)
    findings.sort(key=lambda item: (item["targetId"], item["goalId"], item["code"]))

    goals = [goal for target in target_reports for goal in target["goals"]]
    summary = {
        "targetCount": len(target_reports),
        "selectedTransitionCount": sum(len(target["transitions"]) for target in target_reports),
        "goalCount": len(goals),
        "reachableGoalCount": sum(goal["classification"] == "reachable" for goal in goals),
        "blockedGoalCount": sum(goal["classification"] == "blocked-by-evidence" for goal in goals),
        "unreachableSelectedGoalCount": sum(
            goal["classification"] == "unreachable-in-selected-scope" for goal in goals
        ),
        "externalOrUnprovenGoalCount": sum(
            goal["classification"] == "external-or-unproven" for goal in goals
        ),
        "findingCount": len(findings),
    }
    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": all(target["requirementsSatisfied"] for target in target_reports),
        "source": copy.deepcopy(source),
        "inputs": {
            "manifest": manifest_pin,
            "storageGraph": storage_pin,
            "routeInteractions": interaction_pin,
        },
        "policy": {
            "storageGraphRecomputed": False,
            "routeInteractionResolverReused": True,
            "dynamicLuaExecuted": False,
            "executionOrderInferred": False,
            "globalImpossibilityClaimed": False,
            "runtimeGameplayCompletionClaimed": False,
            "missingSelectedProducerMeans": "external-or-unproven",
        },
        "summary": summary,
        "targets": target_reports,
        "findings": findings,
    }
