from __future__ import annotations

from typing import Any, Mapping

from otbm_reachability_types import (
    ALLOWED_TRANSITION_KINDS,
    BLOCKING_UNCERTAINTIES,
    AppearanceSemantics,
    FindingCollector,
    Position,
    ReachabilityError,
    TileState,
    TransitionSpec,
    TransitionState,
    _position,
)


def _classify_tile(
    index: Any,
    tile_index: int,
    tile: Any,
    appearances: Mapping[int, AppearanceSemantics],
    findings: FindingCollector,
) -> TileState:
    ordinals = tuple(range(tile.placement_start, tile.placement_start + tile.placement_count))
    placements = [index.placement(ordinal) for ordinal in ordinals]
    item_ids = tuple(int(entry["itemId"]) for entry in placements)
    ground = False
    static_blockers: list[int] = []
    conditional_blockers: list[int] = []
    unknown: list[int] = []
    avoid: list[int] = []
    uncertainties: set[str] = set()
    for placement in placements:
        item_id = int(placement["itemId"])
        semantics = appearances.get(item_id)
        if semantics is None:
            unknown.append(item_id)
            uncertainties.add("unknown-appearance")
            continue
        ground = ground or semantics.ground
        if semantics.avoid:
            avoid.append(item_id)
        if not semantics.unpassable:
            continue
        conditional = False
        if placement.get("houseDoorId") is not None:
            conditional = True
            uncertainties.add("door-state")
        elif placement.get("actionId") is not None or placement.get("uniqueId") is not None:
            conditional = True
            uncertainties.add("quest-state")
        elif semantics.usable or semantics.multi_use or semantics.force_use:
            conditional = True
            uncertainties.add("interactive-state")
        if conditional:
            conditional_blockers.append(item_id)
        else:
            static_blockers.append(item_id)
    strict = ground and not static_blockers and not conditional_blockers and not unknown
    optimistic = ground and not static_blockers
    position: Position = (tile.x, tile.y, tile.z)
    if not ground:
        findings.add("error", "tile_missing_ground", "Indexed tile has no confirmed ground appearance", position=list(position))
    if static_blockers:
        findings.add(
            "info",
            "tile_static_blocker",
            "Tile contains a confirmed unpassable static item",
            position=list(position),
            itemIds=sorted(set(static_blockers)),
        )
    if conditional_blockers:
        findings.add(
            "info",
            "tile_conditional_blocker",
            "Tile is blocked in strict mode but may open or transform at runtime",
            position=list(position),
            itemIds=sorted(set(conditional_blockers)),
            uncertainties=sorted(uncertainties),
        )
    if unknown:
        findings.add(
            "warning",
            "tile_unknown_appearance",
            "Tile contains item IDs missing from the supplied appearances catalogue",
            position=list(position),
            itemIds=sorted(set(unknown)),
        )
    if avoid:
        findings.add(
            "info",
            "tile_avoid_item",
            "Tile contains an appearance marked avoid; it remains geometrically traversable",
            position=list(position),
            itemIds=sorted(set(avoid)),
        )
    return TileState(
        position=position,
        tile_index=tile_index,
        kind=str(getattr(tile, "kind", "tile")),
        house_id=getattr(tile, "house_id", None),
        flags=int(getattr(tile, "flags", 0)),
        placement_ordinals=ordinals,
        item_ids=item_ids,
        has_ground=ground,
        strict_walkable=strict,
        optimistic_walkable=optimistic,
        static_blockers=tuple(sorted(static_blockers)),
        conditional_blockers=tuple(sorted(conditional_blockers)),
        unknown_appearances=tuple(sorted(unknown)),
        avoid_items=tuple(sorted(avoid)),
        uncertainties=tuple(sorted(uncertainties)),
    )


def _transition_from_manifest(raw: Any, seen_ids: set[str]) -> TransitionSpec:
    if not isinstance(raw, dict):
        raise ReachabilityError("Every transition manifest entry must be an object")
    transition_id = raw.get("id")
    if not isinstance(transition_id, str) or not transition_id or len(transition_id) > 160:
        raise ReachabilityError("Transition id must be a non-empty string of at most 160 characters")
    if transition_id in seen_ids:
        raise ReachabilityError(f"Duplicate transition id: {transition_id}")
    seen_ids.add(transition_id)
    kind = raw.get("kind")
    if kind not in ALLOWED_TRANSITION_KINDS - {"teleport"}:
        raise ReachabilityError(f"Unsupported explicit transition kind {kind!r} for {transition_id}")
    source = _position(raw.get("source"), f"transition {transition_id} source")
    if "destination" in raw and "delta" in raw:
        raise ReachabilityError(f"Transition {transition_id} must use destination or delta, not both")
    if "destination" in raw:
        destination = _position(raw.get("destination"), f"transition {transition_id} destination")
    else:
        delta = raw.get("delta")
        if not isinstance(delta, list) or len(delta) != 3 or any(not isinstance(part, int) for part in delta):
            raise ReachabilityError(f"Transition {transition_id} requires destination or integer delta")
        destination = _position(
            [source[0] + delta[0], source[1] + delta[1], source[2] + delta[2]],
            f"transition {transition_id} computed destination",
        )
    expected = raw.get("expectedItemIds", [])
    if not isinstance(expected, list) or any(
        not isinstance(item_id, int) or isinstance(item_id, bool) or not 0 <= item_id <= 0xFFFF for item_id in expected
    ):
        raise ReachabilityError(f"Transition {transition_id} expectedItemIds must contain item IDs")
    uncertainty = raw.get("uncertainties", [])
    if not isinstance(uncertainty, list) or any(
        not isinstance(value, str) or not value or len(value) > 80 for value in uncertainty
    ):
        raise ReachabilityError(f"Transition {transition_id} uncertainties must contain bounded strings")
    bidirectional = raw.get("bidirectional", False)
    if not isinstance(bidirectional, bool):
        raise ReachabilityError(f"Transition {transition_id} bidirectional must be boolean")
    evidence = raw.get("evidence")
    if evidence is not None and not isinstance(evidence, dict):
        raise ReachabilityError(f"Transition {transition_id} evidence must be an object")
    return TransitionSpec(
        transition_id=transition_id,
        kind=kind,
        source=source,
        destination=destination,
        origin="manifest",
        item_id=None,
        expected_item_ids=tuple(sorted(set(expected))),
        bidirectional=bidirectional,
        uncertainties=tuple(sorted(set(uncertainty))),
        evidence=evidence,
    )


def _validate_transition(
    spec: TransitionSpec,
    *,
    index: Any,
    region_tiles: Mapping[Position, TileState],
    appearances: Mapping[int, AppearanceSemantics],
    lower: Position,
    upper: Position,
    findings: FindingCollector,
) -> TransitionState:
    issues: list[str] = []
    source_found = index.find_tile(spec.source)
    destination_found = index.find_tile(spec.destination)
    source_state = region_tiles.get(spec.source)
    if source_state is None and source_found is not None:
        tile_index, tile = source_found
        source_state = _classify_tile(index, tile_index, tile, appearances, findings)
    destination_state = region_tiles.get(spec.destination)
    if destination_state is None and destination_found is not None:
        tile_index, tile = destination_found
        destination_state = _classify_tile(index, tile_index, tile, appearances, findings)

    if source_found is None:
        issues.append("source-tile-missing")
        findings.add(
            "error",
            "transition_source_missing",
            "Transition source does not exist in the world index",
            transitionId=spec.transition_id,
            source=list(spec.source),
        )
    if destination_found is None:
        issues.append("destination-tile-missing")
        findings.add(
            "error",
            "transition_destination_missing",
            "Transition destination does not exist in the world index",
            transitionId=spec.transition_id,
            source=list(spec.source),
            destination=list(spec.destination),
        )
    if source_state is not None and not source_state.has_ground:
        issues.append("source-without-ground")
    if destination_state is not None and not destination_state.has_ground:
        issues.append("destination-without-ground")
        findings.add(
            "error",
            "transition_destination_without_ground",
            "Transition destination has no confirmed ground appearance",
            transitionId=spec.transition_id,
            destination=list(spec.destination),
        )
    if spec.expected_item_ids and source_state is not None and not set(spec.expected_item_ids).intersection(source_state.item_ids):
        issues.append("expected-item-missing")
        findings.add(
            "error",
            "transition_expected_item_missing",
            "Explicit floor transition source does not contain any expected item ID",
            transitionId=spec.transition_id,
            source=list(spec.source),
            expectedItemIds=list(spec.expected_item_ids),
            actualItemIds=list(source_state.item_ids),
        )

    invalid_issues = {
        "source-tile-missing",
        "destination-tile-missing",
        "source-without-ground",
        "destination-without-ground",
        "expected-item-missing",
    }
    valid = not any(issue in invalid_issues for issue in issues)
    strict_eligible = bool(
        valid
        and source_state
        and destination_state
        and source_state.strict_walkable
        and destination_state.strict_walkable
    )
    blocking_uncertainty = bool(BLOCKING_UNCERTAINTIES.intersection(spec.uncertainties))
    if blocking_uncertainty:
        strict_eligible = False
    optimistic_eligible = bool(
        valid and source_state and destination_state and source_state.optimistic_walkable and destination_state.optimistic_walkable
    )
    if valid and not optimistic_eligible:
        issues.append("blocked-destination-or-source")
        findings.add(
            "error",
            "transition_blocked",
            "Transition source or destination is statically blocked",
            transitionId=spec.transition_id,
            source=list(spec.source),
            destination=list(spec.destination),
        )
    elif valid and not strict_eligible and optimistic_eligible:
        issues.append("conditional")
        findings.add(
            "warning",
            "transition_conditional",
            "Transition is usable only in optimistic mode because runtime state is uncertain",
            transitionId=spec.transition_id,
            source=list(spec.source),
            destination=list(spec.destination),
            uncertainties=list(spec.uncertainties),
        )
    status = "invalid" if not valid or not optimistic_eligible else ("confirmed" if strict_eligible else "conditional")
    return TransitionState(spec, valid and optimistic_eligible, strict_eligible, optimistic_eligible, status, tuple(sorted(set(issues))))
