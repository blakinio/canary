from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Mapping, Sequence

from otbm_reachability_graph import (
    _bfs,
    _movement_neighbors,
    _reconstruct_path,
    _reconstruct_route,
    _tarjan_cycles,
    _transition_edges,
)
from otbm_reachability_transition import (
    _classify_tile,
    _transition_from_manifest,
    _validate_transition,
)
from otbm_reachability_types import (
    DEFAULT_PATH_LIMIT,
    DEFAULT_SAMPLE_LIMIT,
    MAX_PATH_LIMIT,
    MAX_ROUTES,
    MAX_ROUTE_STARTS,
    MAX_TRANSITIONS,
    REPORT_FORMAT,
    SCHEMA_VERSION,
    AppearanceSemantics,
    FindingCollector,
    Position,
    ReachabilityError,
    TileState,
    TransitionSpec,
    TransitionState,
    _in_bounds,
    _placement_script_status,
    _position,
    _script_lookup,
    _validate_limits,
    normalize_bounds,
)

ROUTE_PLAN_FORMAT = "canary-otbm-e2e-route-plan-v1"
ROUTE_PLAN_SCHEMA_VERSION = 1
MAX_EXECUTABLE_ROUTE_POSITIONS = MAX_PATH_LIMIT
DEFAULT_EXECUTABLE_ROUTE_POSITIONS = MAX_EXECUTABLE_ROUTE_POSITIONS


def _mapping_or_none(value: Any) -> dict[str, Any] | None:
    return dict(value) if isinstance(value, Mapping) else None


def _route_plan_provenance(provenance: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(provenance or {})
    world_manifest = source.get("worldIndexManifest")
    manifest_mapping = dict(world_manifest) if isinstance(world_manifest, Mapping) else {}
    return {
        "map": _mapping_or_none(manifest_mapping.get("source")),
        "worldIndex": _mapping_or_none(source.get("worldIndex")),
        "appearances": _mapping_or_none(source.get("appearances")),
        "transitionManifest": _mapping_or_none(source.get("transitionManifest")),
        "scriptResolution": _mapping_or_none(source.get("scriptResolution")),
    }


def _has_sha256(value: Any) -> bool:
    return isinstance(value, Mapping) and isinstance(value.get("sha256"), str) and len(value["sha256"]) == 64


def _hash_json(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_route_plan(
    *,
    start: Position,
    goal: Position,
    status: str,
    strict_distance: int | None,
    optimistic_distance: int | None,
    previous: Mapping[Position, tuple[Position, str | None]],
    transitions_by_id: Mapping[str, TransitionState],
    lower: Position,
    upper: Position,
    allow_diagonal: bool,
    max_positions: int,
    provenance: Mapping[str, Any] | None,
    issues: Sequence[str],
) -> dict[str, Any]:
    route_provenance = _route_plan_provenance(provenance)
    routing_mode = "strict" if status == "confirmed" else "optimistic" if status == "conditional" else None
    distance = strict_distance if status == "confirmed" else optimistic_distance if status == "conditional" else None
    blockers: list[dict[str, Any]] = []
    path_complete = status in {"invalid", "unreachable"}
    positions: list[Position] = []
    predecessor_edges: list[tuple[Position, Position, str | None]] = []

    if status in {"confirmed", "conditional"} and distance is not None:
        required_positions = distance + 1
        if required_positions > max_positions:
            blockers.append(
                {
                    "code": "route-exceeds-supported-bound",
                    "requiredPositions": required_positions,
                    "supportedMaxPositions": max_positions,
                }
            )
        else:
            positions, predecessor_edges = _reconstruct_route(start, goal, previous)
            path_complete = bool(positions)
            if not path_complete:
                blockers.append({"code": "predecessor-reconstruction-failed"})

    edges: list[dict[str, Any]] = []
    transition_ids: list[str] = []
    missing_transition_evidence: list[str] = []
    manifest_transition_used = False
    script_evidence_used = False
    for source, destination, transition_id in predecessor_edges:
        if transition_id is None:
            edges.append(
                {
                    "from": list(source),
                    "to": list(destination),
                    "kind": "movement",
                    "isTransition": False,
                    "transitionId": None,
                    "evidence": {
                        "source": "reachability-bfs-predecessor",
                        "edgeSource": "_movement_neighbors",
                        "routingMode": routing_mode,
                    },
                }
            )
            continue

        transition_ids.append(transition_id)
        transition = transitions_by_id.get(transition_id)
        transition_json = transition.to_json() if transition is not None else None
        if transition is None:
            missing_transition_evidence.append(transition_id)
        else:
            manifest_transition_used = manifest_transition_used or transition.spec.origin == "manifest"
            script_evidence_used = script_evidence_used or transition.spec.script_status is not None or any(
                uncertainty.startswith("script-resolution-") or uncertainty == "dynamic-script"
                for uncertainty in transition.spec.uncertainties
            )
        edges.append(
            {
                "from": list(source),
                "to": list(destination),
                "kind": "transition",
                "isTransition": True,
                "transitionId": transition_id,
                "evidence": {
                    "source": "validated-transition-edge",
                    "provenanceKey": (
                        "transitionManifest"
                        if transition is not None and transition.spec.origin == "manifest"
                        else "worldIndex"
                    ),
                    "transition": transition_json,
                },
            }
        )

    if missing_transition_evidence:
        blockers.append(
            {
                "code": "validated-transition-evidence-missing",
                "transitionIds": sorted(set(missing_transition_evidence)),
            }
        )

    if status == "conditional":
        blockers.append({"code": "conditional-route-not-executable"})
    elif status in {"unreachable", "invalid"}:
        blockers.extend({"code": issue} for issue in issues)

    if status == "confirmed":
        if not _has_sha256(route_provenance.get("map")):
            blockers.append({"code": "map-provenance-missing"})
        if not _has_sha256(route_provenance.get("worldIndex")):
            blockers.append({"code": "world-index-provenance-missing"})
        if not _has_sha256(route_provenance.get("appearances")):
            blockers.append({"code": "appearances-provenance-missing"})
        if manifest_transition_used and not _has_sha256(route_provenance.get("transitionManifest")):
            blockers.append({"code": "transition-manifest-provenance-missing"})
        if script_evidence_used and not _has_sha256(route_provenance.get("scriptResolution")):
            blockers.append({"code": "script-resolution-provenance-missing"})
        if transition_ids:
            blockers.append(
                {
                    "code": "transition-interaction-semantics-unresolved",
                    "transitionIds": list(dict.fromkeys(transition_ids)),
                }
            )

    if status in {"unreachable", "invalid"}:
        execution_status = "not-applicable"
    elif blockers:
        execution_status = "blocked"
    else:
        execution_status = "executable"

    input_identity = {
        "provenance": route_provenance,
        "origin": list(start),
        "destination": list(goal),
        "routingBounds": {"from": list(lower), "to": list(upper)},
        "routingOptions": {
            "allowDiagonal": allow_diagonal,
            "diagonalCornerCutting": False,
            "maxExecutablePositions": max_positions,
        },
    }
    plan: dict[str, Any] = {
        "format": ROUTE_PLAN_FORMAT,
        "schemaVersion": ROUTE_PLAN_SCHEMA_VERSION,
        "provenance": route_provenance,
        "inputHashSha256": _hash_json(input_identity),
        "origin": list(start),
        "destination": list(goal),
        "routingBounds": {"from": list(lower), "to": list(upper)},
        "routingOptions": input_identity["routingOptions"],
        "routeStatus": status,
        "executionStatus": execution_status,
        "routingMode": routing_mode,
        "distance": distance,
        "strictDistance": strict_distance,
        "optimisticDistance": optimistic_distance,
        "pathComplete": path_complete,
        "path": [list(position) for position in positions],
        "edges": edges,
        "blockers": blockers,
    }
    plan["planHashSha256"] = _hash_json(plan)
    return plan


def analyze_world(
    index: Any,
    *,
    appearances: Mapping[int, AppearanceSemantics],
    lower: Position,
    upper: Position,
    routes: Sequence[tuple[Position, Position]],
    origins: Sequence[Position] = (),
    transition_entries: Sequence[dict[str, Any]] = (),
    script_resolution: dict[str, Any] | None = None,
    allow_diagonal: bool = False,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    path_limit: int = DEFAULT_PATH_LIMIT,
    provenance: Mapping[str, Any] | None = None,
    route_plan_max_positions: int | None = None,
) -> dict[str, Any]:
    _validate_limits(sample_limit, path_limit)
    if route_plan_max_positions is not None and (
        not isinstance(route_plan_max_positions, int)
        or isinstance(route_plan_max_positions, bool)
        or not 1 <= route_plan_max_positions <= MAX_EXECUTABLE_ROUTE_POSITIONS
    ):
        raise ReachabilityError(
            f"route_plan_max_positions must be in 1..{MAX_EXECUTABLE_ROUTE_POSITIONS}"
        )
    lower, upper = normalize_bounds(lower, upper)
    if len(routes) > MAX_ROUTES:
        raise ReachabilityError(f"At most {MAX_ROUTES} routes may be analyzed")
    normalized_routes = [(_position(start, "route start"), _position(goal, "route goal")) for start, goal in routes]
    normalized_origins = [_position(origin, "origin") for origin in origins]
    all_origins = sorted(set(normalized_origins + [start for start, _ in normalized_routes]))
    if not all_origins:
        raise ReachabilityError("At least one origin or route is required")
    if len(all_origins) > MAX_ROUTE_STARTS:
        raise ReachabilityError(f"At most {MAX_ROUTE_STARTS} distinct route starts/origins may be analyzed")
    if any(not _in_bounds(origin, lower, upper) for origin in all_origins):
        raise ReachabilityError("Every origin and route start must be inside the explicit region")

    findings = FindingCollector(sample_limit)
    region_tiles: dict[Position, TileState] = {}
    all_region_placements: list[dict[str, Any]] = []
    for tile_index, tile in index.iter_region_tiles(lower, upper):
        state = _classify_tile(index, tile_index, tile, appearances, findings)
        if state.position in region_tiles:
            raise ReachabilityError(f"Duplicate tile position in index: {state.position}")
        region_tiles[state.position] = state
        all_region_placements.extend(index.placement(ordinal) for ordinal in state.placement_ordinals)

    script_lookup = _script_lookup(script_resolution)
    transition_specs: list[TransitionSpec] = []
    seen_transition_ids: set[str] = set()
    for placement in all_region_placements:
        destination = placement.get("teleportDestination")
        if not isinstance(destination, list):
            continue
        source = _position(placement.get("position"), "teleport source")
        target = _position(destination, "teleport destination")
        placement_ordinal = int(placement.get("placementOrdinal", len(transition_specs)))
        transition_id = f"teleport:{placement_ordinal}"
        seen_transition_ids.add(transition_id)
        status = _placement_script_status(placement, script_lookup)
        uncertainties: set[str] = set()
        if status == "conflicting":
            uncertainties.add("script-resolution-conflicting")
            findings.add(
                "error",
                "transition_script_conflict",
                "Teleport placement has conflicting active handler evidence",
                transitionId=transition_id,
                source=list(source),
            )
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
        raise ReachabilityError(f"Region and manifest contain more than {MAX_TRANSITIONS} transitions")
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
    transitions_by_id = {transition.spec.transition_id: transition for transition in transitions}

    strict_transition_edges = _transition_edges(transitions, lower, upper, strict=True)
    optimistic_transition_edges = _transition_edges(transitions, lower, upper, strict=False)
    strict_cache: dict[Position, tuple[dict[Position, int], dict[Position, tuple[Position, str | None]]]] = {}
    optimistic_cache: dict[Position, tuple[dict[Position, int], dict[Position, tuple[Position, str | None]]]] = {}
    for origin in all_origins:
        strict_cache[origin] = _bfs(
            origin,
            region_tiles,
            strict_transition_edges,
            strict=True,
            allow_diagonal=allow_diagonal,
        )
        optimistic_cache[origin] = _bfs(
            origin,
            region_tiles,
            optimistic_transition_edges,
            strict=False,
            allow_diagonal=allow_diagonal,
        )

    route_results: list[dict[str, Any]] = []
    for start, goal in normalized_routes:
        if not _in_bounds(goal, lower, upper):
            result = {
                "start": list(start),
                "goal": list(goal),
                "status": "invalid",
                "strictDistance": None,
                "optimisticDistance": None,
                "path": [],
                "pathTruncated": False,
                "transitionIdsUsed": [],
                "issues": ["goal-outside-region"],
            }
            if route_plan_max_positions is not None:
                result["routePlan"] = _build_route_plan(
                    start=start,
                    goal=goal,
                    status="invalid",
                    strict_distance=None,
                    optimistic_distance=None,
                    previous={},
                    transitions_by_id=transitions_by_id,
                    lower=lower,
                    upper=upper,
                    allow_diagonal=allow_diagonal,
                    max_positions=route_plan_max_positions,
                    provenance=provenance,
                    issues=result["issues"],
                )
            findings.add(
                "error",
                "route_goal_outside_region",
                "Route goal is outside the explicit bounded region",
                source=list(start),
                destination=list(goal),
            )
            route_results.append(result)
            continue
        strict_distances, strict_previous = strict_cache[start]
        optimistic_distances, optimistic_previous = optimistic_cache[start]
        selected_previous: Mapping[Position, tuple[Position, str | None]] = {}
        if goal in strict_distances:
            path, used, truncated = _reconstruct_path(start, goal, strict_previous, limit=path_limit)
            status = "confirmed"
            issues: list[str] = []
            selected_previous = strict_previous
        elif goal in optimistic_distances:
            path, used, truncated = _reconstruct_path(start, goal, optimistic_previous, limit=path_limit)
            status = "conditional"
            issues = ["strict-path-unavailable"]
            selected_previous = optimistic_previous
            findings.add(
                "warning",
                "route_conditional",
                "Route is reachable only when conditional or unknown runtime state is treated optimistically",
                source=list(start),
                destination=list(goal),
            )
        else:
            path, used, truncated = [], [], False
            status = "unreachable"
            issues = ["no-path"]
            findings.add(
                "warning",
                "route_unreachable",
                "No strict or optimistic path exists inside the explicit region",
                source=list(start),
                destination=list(goal),
            )
        result = {
            "start": list(start),
            "goal": list(goal),
            "status": status,
            "strictDistance": strict_distances.get(goal),
            "optimisticDistance": optimistic_distances.get(goal),
            "path": path,
            "pathTruncated": truncated,
            "transitionIdsUsed": used,
            "issues": issues,
        }
        if route_plan_max_positions is not None:
            result["routePlan"] = _build_route_plan(
                start=start,
                goal=goal,
                status=status,
                strict_distance=strict_distances.get(goal),
                optimistic_distance=optimistic_distances.get(goal),
                previous=selected_previous,
                transitions_by_id=transitions_by_id,
                lower=lower,
                upper=upper,
                allow_diagonal=allow_diagonal,
                max_positions=route_plan_max_positions,
                provenance=provenance,
                issues=issues,
            )
        route_results.append(result)

    strict_reachable = set().union(*(cache[0].keys() for cache in strict_cache.values()))
    optimistic_reachable = set().union(*(cache[0].keys() for cache in optimistic_cache.values()))
    mechanic_results: list[dict[str, Any]] = []
    mechanic_total = 0
    mechanic_counts: Counter[str] = Counter()
    for placement in sorted(
        all_region_placements,
        key=lambda entry: (tuple(entry.get("position", ())), int(entry.get("placementOrdinal", 0))),
    ):
        if not any(key in placement for key in ("actionId", "uniqueId", "houseDoorId", "teleportDestination")):
            continue
        mechanic_total += 1
        position = tuple(placement["position"])
        if position in strict_reachable:
            status = "confirmed"
        elif position in optimistic_reachable:
            status = "conditional"
        else:
            status = "unreachable"
            findings.add(
                "warning",
                "mechanic_unreachable",
                "Map mechanic is unreachable from every supplied origin inside the explicit region",
                position=list(position),
                itemId=placement.get("itemId"),
                placementOrdinal=placement.get("placementOrdinal"),
            )
        mechanic_counts[status] += 1
        if len(mechanic_results) < sample_limit:
            mechanic_results.append(
                {
                    "placementOrdinal": placement.get("placementOrdinal"),
                    "itemId": placement.get("itemId"),
                    "position": list(position),
                    "actionId": placement.get("actionId"),
                    "uniqueId": placement.get("uniqueId"),
                    "houseDoorId": placement.get("houseDoorId"),
                    "teleportDestination": placement.get("teleportDestination"),
                    "status": status,
                }
            )

    optimistic_pairs: set[tuple[Position, Position]] = set()
    adjacency: dict[Position, list[Position]] = {}
    for transition in transitions:
        if not transition.optimistic_eligible:
            continue
        source = transition.spec.source
        destination = transition.spec.destination
        optimistic_pairs.add((source, destination))
        adjacency.setdefault(source, []).append(destination)
        if transition.spec.bidirectional:
            optimistic_pairs.add((destination, source))
            adjacency.setdefault(destination, []).append(source)
    one_way_count = 0
    dead_end_count = 0
    for transition in transitions:
        if not transition.optimistic_eligible:
            continue
        spec = transition.spec
        if (spec.destination, spec.source) not in optimistic_pairs:
            one_way_count += 1
            severity = "info" if "one-way-intended" in spec.uncertainties else "warning"
            findings.add(
                severity,
                "transition_one_way",
                "No reverse transition edge was confirmed",
                transitionId=spec.transition_id,
                source=list(spec.source),
                destination=list(spec.destination),
            )
        if not _in_bounds(spec.destination, lower, upper):
            continue
        movement_exits = list(
            _movement_neighbors(spec.destination, region_tiles, strict=False, allow_diagonal=allow_diagonal)
        )
        transition_exits = optimistic_transition_edges.get(spec.destination, ())
        if not movement_exits and not transition_exits:
            dead_end_count += 1
            findings.add(
                "warning",
                "transition_dead_end",
                "Transition destination has no optimistic movement or transition exit inside the region",
                transitionId=spec.transition_id,
                destination=list(spec.destination),
            )

    loops = _tarjan_cycles(adjacency)
    loop_results: list[dict[str, Any]] = []
    for component in loops:
        component_set = set(component)
        outgoing = sorted(
            {
                target
                for source in component
                for target in adjacency.get(source, ())
                if target not in component_set
            }
        )
        closed = not outgoing
        findings.add(
            "warning" if closed else "info",
            "transition_closed_loop" if closed else "transition_loop",
            "Transition graph contains a closed cycle" if closed else "Transition graph contains a cycle with an exit",
            positions=[list(value) for value in component],
        )
        if len(loop_results) < sample_limit:
            loop_results.append(
                {
                    "positions": [list(value) for value in component],
                    "closed": closed,
                    "outgoing": [list(value) for value in outgoing[:sample_limit]],
                }
            )

    problematic_tiles = [
        state
        for state in sorted(region_tiles.values(), key=lambda value: value.position)
        if not state.strict_walkable or state.avoid_items or state.uncertainties
    ]
    tile_counts = Counter()
    for state in region_tiles.values():
        tile_counts["hasGround" if state.has_ground else "missingGround"] += 1
        tile_counts["strictWalkable" if state.strict_walkable else "strictBlocked"] += 1
        tile_counts["optimisticWalkable" if state.optimistic_walkable else "optimisticBlocked"] += 1
        if state.conditional_blockers:
            tile_counts["conditional"] += 1
        if state.unknown_appearances:
            tile_counts["unknownAppearance"] += 1
        if state.avoid_items:
            tile_counts["avoid"] += 1

    findings_json, finding_summary = findings.finish()
    transition_status_counts = Counter(transition.status for transition in transitions)
    route_status_counts = Counter(route["status"] for route in route_results)
    coordinate_count = (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1) * (upper[2] - lower[2] + 1)
    report = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": finding_summary["bySeverity"]["error"] == 0,
        "provenance": dict(provenance or {}),
        "region": {
            "from": list(lower),
            "to": list(upper),
            "coordinateCount": coordinate_count,
            "indexedTileCount": len(region_tiles),
        },
        "policy": {
            "allowDiagonal": allow_diagonal,
            "diagonalCornerCutting": False,
            "strictUnknownAppearancesBlocked": True,
            "optimisticUnknownAppearancesAllowedWhenGroundKnown": True,
            "dynamicLuaExecuted": False,
            "mapModified": False,
            "sampleLimit": sample_limit,
            "pathLimit": path_limit,
        },
        "summary": {
            "routes": len(route_results),
            "routeStatusCounts": dict(sorted(route_status_counts.items())),
            "origins": len(all_origins),
            "transitions": len(transitions),
            "transitionStatusCounts": dict(sorted(transition_status_counts.items())),
            "oneWayTransitions": one_way_count,
            "deadEndTransitions": dead_end_count,
            "transitionLoops": len(loops),
            "mechanics": mechanic_total,
            "mechanicStatusCounts": dict(sorted(mechanic_counts.items())),
            "strictReachableTiles": len(strict_reachable),
            "optimisticReachableTiles": len(optimistic_reachable),
            "tileStatusCounts": dict(sorted(tile_counts.items())),
            "findings": finding_summary,
        },
        "routes": route_results,
        "transitions": [transition.to_json() for transition in transitions[:sample_limit]],
        "transitionsTruncated": len(transitions) > sample_limit,
        "transitionLoops": loop_results,
        "transitionLoopsTruncated": len(loops) > len(loop_results),
        "mechanics": mechanic_results,
        "mechanicsTruncated": mechanic_total > len(mechanic_results),
        "tileDiagnostics": [state.diagnostic_json() for state in problematic_tiles[:sample_limit]],
        "tileDiagnosticsTruncated": len(problematic_tiles) > sample_limit,
        "findings": findings_json,
    }
    return report
