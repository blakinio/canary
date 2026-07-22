from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from otbm_reachability import _load_world_manifest, _manifest_source_sha256
from otbm_reachability_analysis import _movement_execution_resolver, _transition_execution_resolver
from otbm_reachability_graph import _bfs, _movement_neighbors, _reconstruct_route, _tarjan_cycles, _transition_edges
from otbm_reachability_transition import _classify_tile, _transition_from_manifest, _validate_transition
from otbm_reachability_types import (
    ALLOWED_TRANSITION_KINDS,
    MAX_TRANSITIONS,
    AppearanceSemantics,
    FindingCollector,
    GraphEdge,
    Position,
    ReachabilityError,
    TileState,
    TransitionSpec,
    TransitionState,
    _in_bounds,
    _placement_script_status,
    _position,
    _script_lookup,
    _sha256,
    load_appearance_semantics,
    load_script_resolution,
    load_transition_manifest,
    normalize_bounds,
)
from otbm_route_interactions import REGISTRY_FORMAT as INTERACTION_REGISTRY_FORMAT
from otbm_route_interactions import load_registry as load_interaction_registry

MANIFEST_FORMAT = "canary-otbm-connectivity-resilience-manifest-v1"
REPORT_FORMAT = "canary-otbm-connectivity-resilience-v1"
SCHEMA_VERSION = 1
MODES = {"strict", "optimistic", "executable"}
ROUTE_CLASSIFICATIONS = {
    "unreachable",
    "single-edge-fragile",
    "edge-disjoint-alternative",
    "single-edge-resilient-no-full-disjoint-alternative",
}
SHA256_LENGTH = 64

MovementPolicy = Callable[[Position, Position, TileState], bool]
EdgeIdentity = tuple[Position, Position, str | None]


class ConnectivityResilienceError(ValueError):
    """Raised when connectivity resilience evidence cannot be composed safely."""


@dataclass(frozen=True)
class ModeGraph:
    mode: str
    strict: bool
    transition_edges: Mapping[Position, Sequence[GraphEdge]]
    movement_edge_allowed: MovementPolicy | None = None


@dataclass(frozen=True)
class ConnectivityContext:
    lower: Position
    upper: Position
    allow_diagonal: bool
    tiles: Mapping[Position, TileState]
    transitions: Sequence[TransitionState]
    modes: Mapping[str, ModeGraph]
    provenance: Mapping[str, Any]
    canonical_findings: Sequence[Mapping[str, Any]]
    canonical_finding_summary: Mapping[str, Any]


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ConnectivityResilienceError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ConnectivityResilienceError(f"{label} must be an array")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConnectivityResilienceError(f"{label} must be a non-empty string")
    return value


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != SHA256_LENGTH or any(ch not in "0123456789abcdef" for ch in value):
        raise ConnectivityResilienceError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _mode(value: Any, label: str) -> str:
    mode = _string(value, label)
    if mode not in MODES:
        raise ConnectivityResilienceError(f"{label} must be one of {sorted(MODES)}")
    return mode


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_report_sha256(report: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical(report).encode("utf-8")).hexdigest()


def _normalize_position(value: Any, label: str) -> Position:
    try:
        return _position(value, label)
    except ReachabilityError as exc:
        raise ConnectivityResilienceError(str(exc)) from exc


def _edge_json(edge: EdgeIdentity) -> dict[str, Any]:
    source, destination, transition_id = edge
    return {
        "from": list(source),
        "to": list(destination),
        "kind": "transition" if transition_id is not None else "movement",
        "transitionId": transition_id,
    }


def _edge_key(edge: EdgeIdentity) -> tuple[Any, ...]:
    source, destination, transition_id = edge
    return source, destination, transition_id or ""


def _normalize_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if manifest.get("format") != MANIFEST_FORMAT or manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise ConnectivityResilienceError(
            f"manifest must use {MANIFEST_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    source = _mapping(manifest.get("source"), "manifest.source")
    region = _mapping(manifest.get("region"), "manifest.region")
    lower, upper = normalize_bounds(
        _normalize_position(region.get("from"), "manifest.region.from"),
        _normalize_position(region.get("to"), "manifest.region.to"),
    )
    allow_diagonal = region.get("allowDiagonal", False)
    if not isinstance(allow_diagonal, bool):
        raise ConnectivityResilienceError("manifest.region.allowDiagonal must be boolean")

    routes: list[dict[str, Any]] = []
    route_ids: set[str] = set()
    for index, raw in enumerate(_array(manifest.get("routes", []), "manifest.routes")):
        label = f"manifest.routes[{index}]"
        route = _mapping(raw, label)
        route_id = _string(route.get("id"), f"{label}.id")
        if route_id in route_ids:
            raise ConnectivityResilienceError(f"duplicate route id: {route_id}")
        route_ids.add(route_id)
        start = _normalize_position(route.get("start"), f"{label}.start")
        goal = _normalize_position(route.get("goal"), f"{label}.goal")
        if not (_in_bounds(start, lower, upper) and _in_bounds(goal, lower, upper)):
            raise ConnectivityResilienceError(f"{label} start and goal must be inside manifest.region")
        routes.append(
            {
                "id": route_id,
                "reason": _string(route.get("reason"), f"{label}.reason"),
                "mode": _mode(route.get("mode", "strict"), f"{label}.mode"),
                "start": start,
                "goal": goal,
            }
        )

    entrapment_targets: list[dict[str, Any]] = []
    entrapment_ids: set[str] = set()
    for index, raw in enumerate(_array(manifest.get("entrapmentTargets", []), "manifest.entrapmentTargets")):
        label = f"manifest.entrapmentTargets[{index}]"
        target = _mapping(raw, label)
        target_id = _string(target.get("id"), f"{label}.id")
        if target_id in entrapment_ids:
            raise ConnectivityResilienceError(f"duplicate entrapment target id: {target_id}")
        entrapment_ids.add(target_id)
        entry = _normalize_position(target.get("entry"), f"{label}.entry")
        exits = [
            _normalize_position(value, f"{label}.exits[{exit_index}]")
            for exit_index, value in enumerate(_array(target.get("exits"), f"{label}.exits"))
        ]
        if not exits:
            raise ConnectivityResilienceError(f"{label}.exits must not be empty")
        if not _in_bounds(entry, lower, upper) or any(not _in_bounds(value, lower, upper) for value in exits):
            raise ConnectivityResilienceError(f"{label} entry and exits must be inside manifest.region")
        entrapment_targets.append(
            {
                "id": target_id,
                "reason": _string(target.get("reason"), f"{label}.reason"),
                "mode": _mode(target.get("mode", "strict"), f"{label}.mode"),
                "entry": entry,
                "exits": tuple(sorted(set(exits))),
            }
        )

    topology_raw = manifest.get("topology")
    topology: dict[str, Any] | None = None
    if topology_raw is not None:
        value = _mapping(topology_raw, "manifest.topology")
        kinds = value.get("kinds", sorted(ALLOWED_TRANSITION_KINDS))
        normalized_kinds = sorted(set(_string(item, "manifest.topology.kinds[]") for item in _array(kinds, "manifest.topology.kinds")))
        invalid = sorted(set(normalized_kinds) - set(ALLOWED_TRANSITION_KINDS))
        if invalid:
            raise ConnectivityResilienceError(f"manifest.topology.kinds contains unsupported kinds: {invalid}")
        topology = {
            "mode": _mode(value.get("mode", "optimistic"), "manifest.topology.mode"),
            "kinds": normalized_kinds,
        }

    if not routes and not entrapment_targets and topology is None:
        raise ConnectivityResilienceError("manifest must select at least one route, entrapment target, or topology view")

    return {
        "source": {
            "mapSha256": _sha(source.get("mapSha256"), "manifest.source.mapSha256"),
            "worldIndexSha256": _sha(source.get("worldIndexSha256"), "manifest.source.worldIndexSha256"),
        },
        "region": {"from": lower, "to": upper, "allowDiagonal": allow_diagonal},
        "routes": sorted(routes, key=lambda item: item["id"]),
        "entrapmentTargets": sorted(entrapment_targets, key=lambda item: item["id"]),
        "topology": topology,
    }


def _filtered_transition_edges(
    transition_edges: Mapping[Position, Sequence[GraphEdge]],
    excluded: set[EdgeIdentity],
) -> dict[Position, list[GraphEdge]]:
    result: dict[Position, list[GraphEdge]] = {}
    for source, edges in transition_edges.items():
        kept = [
            edge
            for edge in edges
            if (source, edge.destination, edge.transition_id) not in excluded
        ]
        if kept:
            result[source] = kept
    return result


def _movement_policy_with_exclusions(
    base: MovementPolicy | None,
    excluded: set[EdgeIdentity],
) -> MovementPolicy | None:
    movement_excluded = {(source, destination) for source, destination, transition_id in excluded if transition_id is None}
    if base is None and not movement_excluded:
        return None

    def allowed(source: Position, destination: Position, state: TileState) -> bool:
        if (source, destination) in movement_excluded:
            return False
        return True if base is None else base(source, destination, state)

    return allowed


def _run_bfs(
    start: Position,
    context: ConnectivityContext,
    mode: str,
    *,
    excluded: set[EdgeIdentity] | None = None,
) -> tuple[dict[Position, int], dict[Position, tuple[Position, str | None]]]:
    graph = context.modes.get(mode)
    if graph is None:
        raise ConnectivityResilienceError(f"mode {mode!r} is unavailable for the supplied evidence")
    excluded = excluded or set()
    transitions = _filtered_transition_edges(graph.transition_edges, excluded) if excluded else graph.transition_edges
    movement_policy = _movement_policy_with_exclusions(graph.movement_edge_allowed, excluded)
    return _bfs(
        start,
        context.tiles,
        transitions,
        strict=graph.strict,
        allow_diagonal=context.allow_diagonal,
        edge_allowed=movement_policy,
    )


def _route_edges(
    start: Position,
    goal: Position,
    previous: Mapping[Position, tuple[Position, str | None]],
) -> tuple[list[Position], list[EdgeIdentity]]:
    points, raw_edges = _reconstruct_route(start, goal, previous)
    return points, [(source, destination, transition_id) for source, destination, transition_id in raw_edges]


def _evaluate_route(target: Mapping[str, Any], context: ConnectivityContext) -> dict[str, Any]:
    start = target["start"]
    goal = target["goal"]
    mode = str(target["mode"])
    strict_distances, _ = _run_bfs(start, context, "strict")
    optimistic_distances, _ = _run_bfs(start, context, "optimistic")
    distances, previous = _run_bfs(start, context, mode)
    if goal not in distances:
        return {
            "id": target["id"],
            "reason": target["reason"],
            "mode": mode,
            "start": list(start),
            "goal": list(goal),
            "reachable": False,
            "distance": None,
            "strictReachable": goal in strict_distances,
            "optimisticReachable": goal in optimistic_distances,
            "conditionalOnly": goal not in strict_distances and goal in optimistic_distances,
            "baselinePath": [],
            "baselineEdges": [],
            "criticalEdges": [],
            "alternativeEdgeDisjointPath": [],
            "alternativeEdgeDisjointEdges": [],
            "classification": "unreachable",
        }

    points, edges = _route_edges(start, goal, previous)
    if not points or len(points) != distances[goal] + 1:
        raise ConnectivityResilienceError(f"canonical predecessor reconstruction failed for route {target['id']}")

    critical_edges: list[EdgeIdentity] = []
    for edge in edges:
        perturbed_distances, _ = _run_bfs(start, context, mode, excluded={edge})
        if goal not in perturbed_distances:
            critical_edges.append(edge)

    all_baseline_edges = set(edges)
    alternative_distances, alternative_previous = _run_bfs(
        start,
        context,
        mode,
        excluded=all_baseline_edges,
    )
    alternative_points: list[Position] = []
    alternative_edges: list[EdgeIdentity] = []
    if goal in alternative_distances:
        alternative_points, alternative_edges = _route_edges(start, goal, alternative_previous)
        if not alternative_points:
            raise ConnectivityResilienceError(f"alternative predecessor reconstruction failed for route {target['id']}")

    if critical_edges:
        classification = "single-edge-fragile"
    elif alternative_points:
        classification = "edge-disjoint-alternative"
    else:
        classification = "single-edge-resilient-no-full-disjoint-alternative"

    return {
        "id": target["id"],
        "reason": target["reason"],
        "mode": mode,
        "start": list(start),
        "goal": list(goal),
        "reachable": True,
        "distance": distances[goal],
        "strictReachable": goal in strict_distances,
        "optimisticReachable": goal in optimistic_distances,
        "conditionalOnly": goal not in strict_distances and goal in optimistic_distances,
        "baselinePath": [list(value) for value in points],
        "baselineEdges": [_edge_json(edge) for edge in edges],
        "criticalEdges": [_edge_json(edge) for edge in sorted(critical_edges, key=_edge_key)],
        "alternativeEdgeDisjointPath": [list(value) for value in alternative_points],
        "alternativeEdgeDisjointEdges": [_edge_json(edge) for edge in alternative_edges],
        "classification": classification,
    }


def _evaluate_entrapment(target: Mapping[str, Any], context: ConnectivityContext) -> dict[str, Any]:
    entry = target["entry"]
    mode = str(target["mode"])
    distances, previous = _run_bfs(entry, context, mode)
    reachable_exits = [value for value in target["exits"] if value in distances]
    nearest_exit: Position | None = None
    path: list[Position] = []
    edges: list[EdgeIdentity] = []
    if reachable_exits:
        nearest_exit = min(reachable_exits, key=lambda value: (distances[value], value))
        path, edges = _route_edges(entry, nearest_exit, previous)
    return {
        "id": target["id"],
        "reason": target["reason"],
        "mode": mode,
        "entry": list(entry),
        "selectedExits": [list(value) for value in target["exits"]],
        "reachableExits": [list(value) for value in sorted(reachable_exits)],
        "nearestReachableExit": None if nearest_exit is None else list(nearest_exit),
        "escapePath": [list(value) for value in path],
        "escapeEdges": [_edge_json(edge) for edge in edges],
        "classification": "exit-proven" if reachable_exits else "static-entrapment-candidate",
        "runtimeEntrapmentProven": False,
    }


def _mode_transition_pairs(context: ConnectivityContext, mode: str) -> dict[tuple[Position, Position], set[str]]:
    graph = context.modes.get(mode)
    if graph is None:
        raise ConnectivityResilienceError(f"mode {mode!r} is unavailable for the supplied evidence")
    result: dict[tuple[Position, Position], set[str]] = {}
    for source, edges in graph.transition_edges.items():
        for edge in edges:
            if edge.transition_id is not None:
                result.setdefault((source, edge.destination), set()).add(edge.transition_id)
    return result


def _evaluate_topology(selection: Mapping[str, Any], context: ConnectivityContext) -> dict[str, Any]:
    mode = str(selection["mode"])
    kinds = set(selection["kinds"])
    transition_by_id = {value.spec.transition_id: value for value in context.transitions if value.spec.kind in kinds}
    pairs = _mode_transition_pairs(context, mode)
    selected_pairs: dict[tuple[Position, Position], set[str]] = {}
    for pair, transition_ids in pairs.items():
        retained = {value for value in transition_ids if value in transition_by_id}
        if retained:
            selected_pairs[pair] = retained

    one_way: list[dict[str, Any]] = []
    dead_ends: list[dict[str, Any]] = []
    adjacency: dict[Position, list[Position]] = {}
    graph = context.modes[mode]
    for (source, destination), transition_ids in sorted(selected_pairs.items()):
        adjacency.setdefault(source, []).append(destination)
        if (destination, source) not in selected_pairs:
            for transition_id in sorted(transition_ids):
                transition = transition_by_id[transition_id]
                intentional = "one-way-intended" in transition.spec.uncertainties
                one_way.append(
                    {
                        "transitionId": transition_id,
                        "kind": transition.spec.kind,
                        "source": list(source),
                        "destination": list(destination),
                        "intentionalReviewed": intentional,
                        "classification": "reviewed-one-way-intended" if intentional else "one-way-review-candidate",
                    }
                )
        if not _in_bounds(destination, context.lower, context.upper):
            continue
        movement_exits = list(
            _movement_neighbors(
                destination,
                context.tiles,
                strict=graph.strict,
                allow_diagonal=context.allow_diagonal,
                edge_allowed=graph.movement_edge_allowed,
            )
        )
        transition_exits = graph.transition_edges.get(destination, ())
        if not movement_exits and not transition_exits:
            for transition_id in sorted(transition_ids):
                transition = transition_by_id[transition_id]
                dead_ends.append(
                    {
                        "transitionId": transition_id,
                        "kind": transition.spec.kind,
                        "destination": list(destination),
                        "classification": "transition-dead-end-review-candidate",
                    }
                )

    cycles = _tarjan_cycles(adjacency)
    cycle_results: list[dict[str, Any]] = []
    for component in cycles:
        members = set(component)
        outgoing = sorted(
            {
                target
                for source in component
                for target in adjacency.get(source, ())
                if target not in members
            }
        )
        cycle_results.append(
            {
                "positions": [list(value) for value in component],
                "closed": not outgoing,
                "outgoing": [list(value) for value in outgoing],
                "classification": "closed-cycle-review-candidate" if not outgoing else "cycle-with-transition-exit",
            }
        )

    return {
        "mode": mode,
        "kinds": sorted(kinds),
        "directedTransitionEdgeCount": sum(len(value) for value in selected_pairs.values()),
        "oneWayEdges": sorted(one_way, key=lambda item: (item["source"], item["destination"], item["transitionId"])),
        "deadEnds": sorted(dead_ends, key=lambda item: (item["destination"], item["transitionId"])),
        "cycles": cycle_results,
    }


def build_connectivity_resilience_report(
    *,
    manifest: Mapping[str, Any],
    context: ConnectivityContext,
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    normalized = _normalize_manifest(manifest)
    region = normalized["region"]
    if region["from"] != context.lower or region["to"] != context.upper:
        raise ConnectivityResilienceError("manifest region does not match the prepared canonical Reachability context")
    if region["allowDiagonal"] != context.allow_diagonal:
        raise ConnectivityResilienceError("manifest allowDiagonal does not match the prepared canonical Reachability context")

    source = normalized["source"]
    provenance_map_sha = context.provenance.get("mapSha256")
    provenance_index_sha = context.provenance.get("worldIndexSha256")
    if source["mapSha256"] != provenance_map_sha:
        raise ConnectivityResilienceError("manifest source map SHA-256 does not match canonical Reachability provenance")
    if source["worldIndexSha256"] != provenance_index_sha:
        raise ConnectivityResilienceError("manifest World Index SHA-256 does not match canonical Reachability provenance")

    requested_modes = {
        str(value["mode"])
        for value in normalized["routes"] + normalized["entrapmentTargets"]
    }
    if normalized["topology"] is not None:
        requested_modes.add(str(normalized["topology"]["mode"]))
    unavailable = sorted(requested_modes - set(context.modes))
    if unavailable:
        raise ConnectivityResilienceError(f"requested evidence modes are unavailable: {unavailable}")

    routes = [_evaluate_route(value, context) for value in normalized["routes"]]
    entrapment = [_evaluate_entrapment(value, context) for value in normalized["entrapmentTargets"]]
    topology = None if normalized["topology"] is None else _evaluate_topology(normalized["topology"], context)

    findings: list[dict[str, Any]] = []
    for route in routes:
        if route["classification"] == "single-edge-fragile":
            findings.append(
                {
                    "code": "ROUTE_SINGLE_EDGE_FRAGILE",
                    "targetId": route["id"],
                    "classification": route["classification"],
                    "criticalEdges": copy.deepcopy(route["criticalEdges"]),
                }
            )
        elif not route["reachable"]:
            findings.append(
                {
                    "code": "REVIEWED_ROUTE_UNREACHABLE",
                    "targetId": route["id"],
                    "classification": route["classification"],
                    "criticalEdges": [],
                }
            )
        if route["conditionalOnly"]:
            findings.append(
                {
                    "code": "ROUTE_REQUIRES_CONDITIONAL_EVIDENCE",
                    "targetId": route["id"],
                    "classification": "conditional-only",
                    "criticalEdges": [],
                }
            )
    for target in entrapment:
        if target["classification"] == "static-entrapment-candidate":
            findings.append(
                {
                    "code": "STATIC_ENTRAPMENT_CANDIDATE",
                    "targetId": target["id"],
                    "classification": target["classification"],
                    "criticalEdges": [],
                }
            )
    if topology is not None:
        for value in topology["oneWayEdges"]:
            if not value["intentionalReviewed"]:
                findings.append(
                    {
                        "code": "TRANSITION_ONE_WAY_REVIEW_CANDIDATE",
                        "targetId": value["transitionId"],
                        "classification": value["classification"],
                        "criticalEdges": [],
                    }
                )
        for value in topology["deadEnds"]:
            findings.append(
                {
                    "code": "TRANSITION_DEAD_END_REVIEW_CANDIDATE",
                    "targetId": value["transitionId"],
                    "classification": value["classification"],
                    "criticalEdges": [],
                }
            )
        for index, value in enumerate(topology["cycles"]):
            if value["closed"]:
                findings.append(
                    {
                        "code": "TRANSITION_CLOSED_CYCLE_REVIEW_CANDIDATE",
                        "targetId": f"cycle:{index}",
                        "classification": value["classification"],
                        "criticalEdges": [],
                    }
                )
    findings.sort(key=lambda item: (item["code"], item["targetId"]))

    summary = {
        "routeCount": len(routes),
        "reachableRouteCount": sum(bool(value["reachable"]) for value in routes),
        "singleEdgeFragileRouteCount": sum(value["classification"] == "single-edge-fragile" for value in routes),
        "edgeDisjointAlternativeRouteCount": sum(value["classification"] == "edge-disjoint-alternative" for value in routes),
        "conditionalOnlyRouteCount": sum(bool(value["conditionalOnly"]) for value in routes),
        "entrapmentTargetCount": len(entrapment),
        "staticEntrapmentCandidateCount": sum(value["classification"] == "static-entrapment-candidate" for value in entrapment),
        "findingCount": len(findings),
    }

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": not any(
            value["code"] in {"REVIEWED_ROUTE_UNREACHABLE", "STATIC_ENTRAPMENT_CANDIDATE"}
            for value in findings
        ),
        "source": copy.deepcopy(source),
        "region": {
            "from": list(context.lower),
            "to": list(context.upper),
            "allowDiagonal": context.allow_diagonal,
        },
        "inputs": copy.deepcopy(dict(input_pins)),
        "policy": {
            "canonicalReachabilityBfsReused": True,
            "canonicalMovementNeighborsReused": True,
            "canonicalTransitionEdgesReused": True,
            "canonicalCycleDetectionReused": True,
            "secondPathfinderImplemented": False,
            "dynamicLuaExecuted": False,
            "runtimeEntrapmentClaimed": False,
            "globalConnectivityClaimed": False,
            "physicalE2EExecuted": False,
        },
        "canonicalReachabilityValidation": {
            "findings": [copy.deepcopy(dict(value)) for value in context.canonical_findings],
            "summary": copy.deepcopy(dict(context.canonical_finding_summary)),
        },
        "summary": summary,
        "routes": routes,
        "entrapmentTargets": entrapment,
        "topology": topology,
        "findings": findings,
    }


def prepare_connectivity_context(
    *,
    index_path: Path,
    appearances_path: Path,
    manifest: Mapping[str, Any],
    world_manifest_path: Path | None = None,
    transitions_path: Path | None = None,
    script_resolution_path: Path | None = None,
    interaction_registry_path: Path | None = None,
) -> tuple[ConnectivityContext, dict[str, Any]]:
    normalized = _normalize_manifest(manifest)
    lower = normalized["region"]["from"]
    upper = normalized["region"]["to"]
    allow_diagonal = bool(normalized["region"]["allowDiagonal"])

    index_path = index_path.expanduser().resolve()
    if not index_path.is_file():
        raise FileNotFoundError(index_path)
    try:
        from otbm_world_index import WorldIndex
    except ImportError as exc:
        raise ConnectivityResilienceError("otbm_world_index.py is required") from exc

    appearances, appearances_provenance = load_appearance_semantics(appearances_path)
    transition_entries, transition_provenance = load_transition_manifest(transitions_path)
    script_resolution, script_provenance = load_script_resolution(script_resolution_path)
    index_hash = _sha256(index_path)
    world_manifest = _load_world_manifest(index_path, world_manifest_path, index_hash)
    map_hash = _manifest_source_sha256(world_manifest)
    if map_hash is None:
        raise ConnectivityResilienceError(
            "QA-011 requires a World Index manifest with exact source-map SHA-256 provenance"
        )
    if normalized["source"]["mapSha256"] != map_hash:
        raise ConnectivityResilienceError("manifest source map SHA-256 does not match World Index provenance")
    if normalized["source"]["worldIndexSha256"] != index_hash:
        raise ConnectivityResilienceError("manifest World Index SHA-256 does not match the supplied index")

    interaction_registry: dict[str, Any] | None = None
    interaction_provenance: dict[str, Any] | None = None
    if interaction_registry_path is not None:
        candidate = interaction_registry_path.expanduser().resolve()
        interaction_registry = load_interaction_registry(
            candidate,
            expected_source_map_sha256=map_hash,
            expected_world_index_sha256=index_hash,
            expected_transition_manifest_sha256=(
                transition_provenance.get("sha256") if transition_provenance is not None else None
            ),
            expected_script_resolution_sha256=(
                script_provenance.get("sha256") if script_provenance is not None else None
            ),
            require_reviewed=True,
        )
        interaction_provenance = {
            "path": candidate.name,
            "size": candidate.stat().st_size,
            "sha256": _sha256(candidate),
            "format": INTERACTION_REGISTRY_FORMAT,
        }

    canonical_provenance: dict[str, Any] = {
        "worldIndex": {
            "path": index_path.name,
            "size": index_path.stat().st_size,
            "sha256": index_hash,
            "format": "canary-otbm-world-index-v1",
        },
        "appearances": appearances_provenance,
        "transitionManifest": transition_provenance,
        "scriptResolution": script_provenance,
        "interactionRegistry": interaction_provenance,
        "worldIndexManifest": {
            "source": world_manifest.get("source") if world_manifest is not None else None,
            "index": world_manifest.get("index") if world_manifest is not None else None,
        },
    }

    findings = FindingCollector(10_000)
    with WorldIndex(index_path) as index:
        region_tiles: dict[Position, TileState] = {}
        all_region_placements: list[dict[str, Any]] = []
        for tile_index, tile in index.iter_region_tiles(lower, upper):
            state = _classify_tile(index, tile_index, tile, appearances, findings)
            if state.position in region_tiles:
                raise ConnectivityResilienceError(f"duplicate tile position in World Index: {state.position}")
            region_tiles[state.position] = state
            all_region_placements.extend(index.placement(ordinal) for ordinal in state.placement_ordinals)

        script_lookup = _script_lookup(script_resolution)
        transition_specs: list[TransitionSpec] = []
        seen_transition_ids: set[str] = set()
        for placement in all_region_placements:
            destination = placement.get("teleportDestination")
            if not isinstance(destination, list):
                continue
            source = _normalize_position(placement.get("position"), "teleport source")
            target = _normalize_position(destination, "teleport destination")
            placement_ordinal = int(placement.get("placementOrdinal", len(transition_specs)))
            transition_id = f"teleport:{placement_ordinal}"
            seen_transition_ids.add(transition_id)
            status = _placement_script_status(placement, script_lookup)
            uncertainties: set[str] = set()
            if status == "conflicting":
                uncertainties.add("script-resolution-conflicting")
            elif status in {"unresolved", "partially-resolved", "referenced-only"}:
                uncertainties.add(f"script-resolution-{status}")
            elif script_resolution is not None and status is None and (
                placement.get("actionId") is not None or placement.get("uniqueId") is not None
            ):
                uncertainties.add("script-resolution-missing")
            elif script_resolution is None and (
                placement.get("actionId") is not None or placement.get("uniqueId") is not None
            ):
                uncertainties.add("dynamic-script")
            transition_specs.append(
                TransitionSpec(
                    transition_id=transition_id,
                    kind="teleport",
                    source=source,
                    destination=target,
                    origin="world-index",
                    item_id=int(placement["itemId"]),
                    expected_item_ids=(int(placement["itemId"]),),
                    bidirectional=False,
                    uncertainties=tuple(sorted(uncertainties)),
                    evidence={"placementOrdinal": placement_ordinal},
                    script_status=status,
                )
            )
        for raw in transition_entries:
            transition_specs.append(_transition_from_manifest(raw, seen_transition_ids))
        if len(transition_specs) > MAX_TRANSITIONS:
            raise ConnectivityResilienceError(f"region and manifest contain more than {MAX_TRANSITIONS} transitions")
        transition_specs.sort(key=lambda spec: (spec.source, spec.destination, spec.kind, spec.transition_id))
        transitions = [
            _validate_transition(
                spec,
                index=index,
                region_tiles=region_tiles,
                appearances=appearances,
                lower=lower,
                upper=upper,
                findings=findings,
            )
            for spec in transition_specs
        ]

    strict_edges = _transition_edges(transitions, lower, upper, strict=True)
    optimistic_edges = _transition_edges(transitions, lower, upper, strict=False)
    modes: dict[str, ModeGraph] = {
        "strict": ModeGraph("strict", True, strict_edges, None),
        "optimistic": ModeGraph("optimistic", False, optimistic_edges, None),
    }

    if interaction_registry is not None:
        placements_by_ordinal = {
            int(value["placementOrdinal"]): value
            for value in all_region_placements
            if isinstance(value.get("placementOrdinal"), int)
        }
        movement_execution = _movement_execution_resolver(
            region_tiles=region_tiles,
            placements_by_ordinal=placements_by_ordinal,
            interaction_registry=interaction_registry,
            script_lookup=script_lookup,
            provenance=canonical_provenance,
        )
        transition_execution = _transition_execution_resolver(
            interaction_registry=interaction_registry,
            provenance=canonical_provenance,
        )
        executable_edges = _transition_edges(
            transitions,
            lower,
            upper,
            strict=False,
            edge_allowed=lambda transition, source, destination: transition_execution(
                transition, source, destination
            )["allowed"],
        )

        def executable_movement(source: Position, destination: Position, _state: TileState) -> bool:
            return bool(movement_execution(source, destination)["allowed"])

        modes["executable"] = ModeGraph("executable", True, executable_edges, executable_movement)

    canonical_findings, canonical_summary = findings.finish()
    context = ConnectivityContext(
        lower=lower,
        upper=upper,
        allow_diagonal=allow_diagonal,
        tiles=region_tiles,
        transitions=tuple(transitions),
        modes=modes,
        provenance={"mapSha256": map_hash, "worldIndexSha256": index_hash},
        canonical_findings=tuple(canonical_findings),
        canonical_finding_summary=canonical_summary,
    )
    input_pins = {
        "worldIndex": canonical_provenance["worldIndex"],
        "appearances": appearances_provenance,
        "worldIndexManifest": canonical_provenance["worldIndexManifest"],
        "transitionManifest": transition_provenance,
        "scriptResolution": script_provenance,
        "interactionRegistry": interaction_provenance,
    }
    return context, input_pins
