from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Any, Iterable, Iterator, Mapping

from otbm_reachability_transition import _classify_tile
from otbm_reachability_types import FindingCollector as ReachabilityFindingCollector

from otbm_semantic_diff_types import (
    MECHANIC_FIELDS,
    FindingCollector,
    Position,
    SemanticDiffError,
    TileSnapshot,
    canonical_json,
    in_bounds,
)

CORRELATION_CLASSIFICATIONS = {
    "script-resolution": "handler-affected",
    "quest-validation": "quest-evidence-affected",
    "reachability": "changed",
    "spawn-npc": "spawn-npc-evidence-affected",
    "storage-graph": "storage-evidence-affected",
}


def _position_key(position: Position) -> tuple[int, int, int]:
    return position[2], position[1], position[0]


def _semantic_placement(raw: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "itemId": int(raw["itemId"]),
        "itemDepth": int(raw.get("itemDepth", -1)),
        "source": str(raw.get("source", "unknown")),
    }
    for field in MECHANIC_FIELDS:
        value = raw.get(field)
        if value is not None:
            result[field] = list(value) if field == "teleportDestination" else value
    return result


def _base_item_signature(item: Mapping[str, Any]) -> tuple[Any, ...]:
    return int(item["itemId"]), int(item.get("itemDepth", -1)), str(item.get("source", "unknown"))


def _full_item_signature(item: Mapping[str, Any]) -> str:
    return canonical_json(item)


def snapshot_tile(
    index: Any,
    tile_index: int,
    tile: Any,
    appearances: Mapping[int, Any] | None,
) -> TileSnapshot:
    placements = tuple(
        _semantic_placement(index.placement(ordinal))
        for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count)
    )
    walkability: dict[str, Any] | None = None
    if appearances is not None:
        phase3_findings = ReachabilityFindingCollector(1)
        state = _classify_tile(index, tile_index, tile, appearances, phase3_findings)
        ground_ids = sorted(
            int(item["itemId"])
            for item in placements
            if int(item["itemId"]) in appearances and appearances[int(item["itemId"])].ground
        )
        walkability = {
            "hasGround": state.has_ground,
            "groundItemIds": ground_ids,
            "strictWalkable": state.strict_walkable,
            "optimisticWalkable": state.optimistic_walkable,
            "staticBlockers": list(state.static_blockers),
            "conditionalBlockers": list(state.conditional_blockers),
            "unknownAppearances": list(state.unknown_appearances),
            "avoidItems": list(state.avoid_items),
            "uncertainties": list(state.uncertainties),
        }
    return TileSnapshot(
        position=(int(tile.x), int(tile.y), int(tile.z)),
        kind=str(tile.kind),
        house_id=tile.house_id,
        flags=int(tile.flags),
        placements=placements,
        walkability=walkability,
    )


def iter_snapshots(index: Any, appearances: Mapping[int, Any] | None, bounds: tuple[Position, Position] | None) -> Iterator[TileSnapshot]:
    if bounds is None:
        iterator: Iterable[tuple[int, Any]] = ((tile_index, index.tile(tile_index)) for tile_index in range(index.header.tile_count))
    else:
        iterator = index.iter_region_tiles(bounds[0], bounds[1])
    previous: tuple[int, int, int] | None = None
    for tile_index, tile in iterator:
        snapshot = snapshot_tile(index, tile_index, tile, appearances)
        key = _position_key(snapshot.position)
        if previous is not None and key <= previous:
            raise SemanticDiffError("World Index tile iteration is not strictly ordered")
        previous = key
        yield snapshot


def _walk_nodes(value: Any, *, path: tuple[str, ...] = (), depth: int = 0) -> Iterator[tuple[tuple[str, ...], Mapping[str, Any]]]:
    if depth > 32:
        raise SemanticDiffError("Optional correlation report exceeds the maximum nesting depth")
    if isinstance(value, dict):
        yield path, value
        for key in sorted(value):
            yield from _walk_nodes(value[key], path=(*path, str(key)), depth=depth + 1)
    elif isinstance(value, list):
        for index, entry in enumerate(value):
            yield from _walk_nodes(entry, path=(*path, str(index)), depth=depth + 1)


def _node_positions(node: Mapping[str, Any]) -> set[Position]:
    positions: set[Position] = set()
    for key in ("position", "source", "destination"):
        value = node.get(key)
        if isinstance(value, (list, tuple)) and len(value) == 3 and all(isinstance(part, int) and not isinstance(part, bool) for part in value):
            position = (int(value[0]), int(value[1]), int(value[2]))
            if 0 <= position[0] <= 0xFFFF and 0 <= position[1] <= 0xFFFF and 0 <= position[2] <= 15:
                positions.add(position)
    return positions


def _node_mechanics(node: Mapping[str, Any]) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for field in ("itemId", "actionId", "uniqueId", "houseDoorId"):
        value = node.get(field)
        if isinstance(value, int) and not isinstance(value, bool):
            result.add((field, str(value)))
    destination = node.get("teleportDestination")
    if isinstance(destination, (list, tuple)) and len(destination) == 3:
        result.add(("teleportDestination", canonical_json(list(destination))))
    return result


def build_correlation_index(documents: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    by_position: dict[Position, list[dict[str, Any]]] = {}
    by_mechanic: dict[tuple[str, str], list[dict[str, Any]]] = {}
    provenance: list[dict[str, Any]] = []
    node_count = 0
    keep_keys = {
        "id",
        "code",
        "status",
        "classification",
        "kind",
        "name",
        "path",
        "sourcePath",
        "line",
        "position",
        "source",
        "destination",
        "itemId",
        "actionId",
        "uniqueId",
        "houseDoorId",
        "teleportDestination",
        "namespace",
        "storageKey",
        "operation",
    }
    for role, document in sorted(documents.items()):
        provenance.append({"role": role, "format": document.get("format")})
        for path, node in _walk_nodes(document):
            node_count += 1
            if node_count > 1_000_000:
                raise SemanticDiffError("Optional correlation reports contain more than 1000000 JSON nodes")
            positions = _node_positions(node)
            mechanics = _node_mechanics(node)
            if not positions and not mechanics:
                continue
            evidence = {
                "role": role,
                "format": document.get("format"),
                "jsonPath": "/" + "/".join(path),
                "evidence": {key: node[key] for key in sorted(keep_keys.intersection(node))},
            }
            for position in positions:
                by_position.setdefault(position, []).append(evidence)
            for mechanic in mechanics:
                by_mechanic.setdefault(mechanic, []).append(evidence)
    for entries in (*by_position.values(), *by_mechanic.values()):
        entries.sort(key=lambda entry: (entry["role"], entry["jsonPath"], canonical_json(entry["evidence"])))
    return {
        "byPosition": by_position,
        "byMechanic": by_mechanic,
        "provenance": provenance,
        "indexedNodes": node_count,
    }


def correlate(
    correlation_index: Mapping[str, Any] | None,
    position: Position,
    before: Any,
    after: Any,
    *,
    limit: int = 50,
) -> tuple[list[dict[str, Any]], list[str], int]:
    if correlation_index is None:
        return [], [], 0
    matches: dict[tuple[str, str], dict[str, Any]] = {}
    for entry in correlation_index["byPosition"].get(position, []):
        matches[(entry["role"], entry["jsonPath"])] = entry

    def collect_mechanics(value: Any) -> set[tuple[str, str]]:
        found: set[tuple[str, str]] = set()
        if isinstance(value, dict):
            found.update(_node_mechanics(value))
            for child in value.values():
                found.update(collect_mechanics(child))
        elif isinstance(value, list):
            for child in value:
                found.update(collect_mechanics(child))
        return found

    for mechanic in collect_mechanics(before) | collect_mechanics(after):
        for entry in correlation_index["byMechanic"].get(mechanic, []):
            matches[(entry["role"], entry["jsonPath"])] = entry
    ordered = [matches[key] for key in sorted(matches)]
    classifications = sorted(
        {
            CORRELATION_CLASSIFICATIONS[entry["role"]]
            for entry in ordered
            if entry["role"] in CORRELATION_CLASSIFICATIONS
        }
    )
    statuses = {
        str(entry.get("evidence", {}).get("status", ""))
        for entry in ordered
    } | {
        str(entry.get("evidence", {}).get("classification", ""))
        for entry in ordered
    }
    if "unresolved" in statuses or "partially-resolved" in statuses or "referenced-only" in statuses:
        classifications.append("unresolved")
    if "conflicting" in statuses or "conflict" in statuses:
        classifications.append("conflicting")
    return ordered[:limit], sorted(set(classifications)), len(ordered)


def _add(
    collector: FindingCollector,
    correlation_index: Mapping[str, Any] | None,
    *,
    kind: str,
    classifications: list[str],
    evidence_level: str,
    position: Position,
    before: Any,
    after: Any,
    message: str,
    details: Mapping[str, Any] | None = None,
) -> None:
    correlations, correlation_classes, correlation_total = correlate(correlation_index, position, before, after)
    combined = sorted(set(classifications + correlation_classes))
    payload_details = dict(details or {})
    if correlation_total:
        payload_details["correlationTotalCount"] = correlation_total
        payload_details["correlationsTruncated"] = correlation_total > len(correlations)
        evidence_level = "correlated"
    collector.add(
        kind=kind,
        classifications=combined,
        evidence_level=evidence_level,
        position=position,
        before=before,
        after=after,
        message=message,
        details=payload_details,
        correlations=correlations,
    )


def _emit_mechanic_change(
    collector: FindingCollector,
    correlation_index: Mapping[str, Any] | None,
    position: Position,
    before_item: Mapping[str, Any],
    after_item: Mapping[str, Any],
    before_index: int,
    after_index: int,
) -> int:
    changes = 0
    for field in MECHANIC_FIELDS:
        before_value = before_item.get(field)
        after_value = after_item.get(field)
        if before_value == after_value:
            continue
        changes += 1
        if before_value is None:
            kind = "teleport-source-added" if field == "teleportDestination" else "mechanic-added"
            classifications = ["added"]
        elif after_value is None:
            kind = "teleport-source-removed" if field == "teleportDestination" else "mechanic-removed"
            classifications = ["removed"]
        elif field == "teleportDestination":
            kind = "teleport-destination-changed"
            classifications = ["changed"]
        else:
            kind = {
                "actionId": "action-id-changed",
                "uniqueId": "unique-id-changed",
                "houseDoorId": "house-door-id-changed",
            }[field]
            classifications = ["changed"]
        _add(
            collector,
            correlation_index,
            kind=kind,
            classifications=classifications,
            evidence_level="semantic",
            position=position,
            before=before_value,
            after=after_value,
            message=f"{field} changed at an exactly aligned item stack slot",
            details={
                "mechanicType": field,
                "itemId": before_item["itemId"],
                "beforeStackIndex": before_index,
                "afterStackIndex": after_index,
            },
        )
    return changes


def _edit_script(before: tuple[Mapping[str, Any], ...], after: tuple[Mapping[str, Any], ...]) -> list[tuple[str, int | None, int | None]]:
    n, m = len(before), len(after)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n, -1, -1):
        dp[i][m] = n - i
    for j in range(m, -1, -1):
        dp[n][j] = m - j
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            if _base_item_signature(before[i]) == _base_item_signature(after[j]):
                dp[i][j] = dp[i + 1][j + 1]
            else:
                dp[i][j] = 1 + min(dp[i + 1][j + 1], dp[i + 1][j], dp[i][j + 1])
    operations: list[tuple[str, int | None, int | None]] = []
    i = j = 0
    while i < n or j < m:
        if i < n and j < m and _base_item_signature(before[i]) == _base_item_signature(after[j]) and dp[i][j] == dp[i + 1][j + 1]:
            operations.append(("match", i, j))
            i += 1
            j += 1
            continue
        candidates: list[tuple[int, int, str]] = []
        if i < n and j < m:
            candidates.append((1 + dp[i + 1][j + 1], 0, "replace"))
        if i < n:
            candidates.append((1 + dp[i + 1][j], 1, "remove"))
        if j < m:
            candidates.append((1 + dp[i][j + 1], 2, "add"))
        _, _, operation = min(candidates)
        if operation == "replace":
            operations.append((operation, i, j))
            i += 1
            j += 1
        elif operation == "remove":
            operations.append((operation, i, None))
            i += 1
        else:
            operations.append((operation, None, j))
            j += 1
    return operations


def compare_item_stacks(
    collector: FindingCollector,
    correlation_index: Mapping[str, Any] | None,
    position: Position,
    before: tuple[Mapping[str, Any], ...],
    after: tuple[Mapping[str, Any], ...],
) -> int:
    before_signatures = [_full_item_signature(item) for item in before]
    after_signatures = [_full_item_signature(item) for item in after]
    if before_signatures == after_signatures:
        return 0
    if Counter(before_signatures) == Counter(after_signatures):
        _add(
            collector,
            correlation_index,
            kind="stack-order-changed",
            classifications=["changed"],
            evidence_level="semantic",
            position=position,
            before=[{"stackIndex": index, **dict(item)} for index, item in enumerate(before)],
            after=[{"stackIndex": index, **dict(item)} for index, item in enumerate(after)],
            message="The exact same item evidence remains on the tile but stack traversal order changed",
            details={"itemCount": len(before), "addRemoveSuppressed": True},
        )
        return 1
    changes = 0
    for operation, before_index, after_index in _edit_script(before, after):
        if operation == "match":
            assert before_index is not None and after_index is not None
            changes += _emit_mechanic_change(
                collector,
                correlation_index,
                position,
                before[before_index],
                after[after_index],
                before_index,
                after_index,
            )
        elif operation == "replace":
            assert before_index is not None and after_index is not None
            changes += 1
            _add(
                collector,
                correlation_index,
                kind="item-replaced",
                classifications=["changed"],
                evidence_level="semantic",
                position=position,
                before={"stackIndex": before_index, **dict(before[before_index])},
                after={"stackIndex": after_index, **dict(after[after_index])},
                message="An item stack slot was replaced under the deterministic minimal edit contract",
                details={"beforeStackIndex": before_index, "afterStackIndex": after_index},
            )
        elif operation == "remove":
            assert before_index is not None
            changes += 1
            _add(
                collector,
                correlation_index,
                kind="item-removed",
                classifications=["removed"],
                evidence_level="structural",
                position=position,
                before={"stackIndex": before_index, **dict(before[before_index])},
                after=None,
                message="An exact item placement was removed from the tile stack",
                details={"beforeStackIndex": before_index, "afterStackIndex": None},
            )
        else:
            assert after_index is not None
            changes += 1
            _add(
                collector,
                correlation_index,
                kind="item-added",
                classifications=["added"],
                evidence_level="structural",
                position=position,
                before=None,
                after={"stackIndex": after_index, **dict(after[after_index])},
                message="An exact item placement was added to the tile stack",
                details={"beforeStackIndex": None, "afterStackIndex": after_index},
            )
    return changes


def compare_walkability(
    collector: FindingCollector,
    correlation_index: Mapping[str, Any] | None,
    position: Position,
    before: Mapping[str, Any] | None,
    after: Mapping[str, Any] | None,
) -> int:
    if before is None or after is None:
        return 0
    changes = 0

    def emit(kind: str, classifications: list[str], message: str, before_value: Any, after_value: Any, details: Mapping[str, Any] | None = None) -> None:
        nonlocal changes
        changes += 1
        _add(
            collector,
            correlation_index,
            kind=kind,
            classifications=classifications,
            evidence_level="regression" if "walkability-regression" in classifications else "semantic",
            position=position,
            before=before_value,
            after=after_value,
            message=message,
            details=details,
        )

    b_strict = bool(before["strictWalkable"])
    a_strict = bool(after["strictWalkable"])
    b_opt = bool(before["optimisticWalkable"])
    a_opt = bool(after["optimisticWalkable"])
    if b_strict and not a_strict:
        if a_opt:
            emit(
                "strict-to-conditional",
                ["changed", "walkability-regression"],
                "A Phase 3 strict-walkable tile became conditional",
                before,
                after,
            )
        else:
            emit(
                "strict-walkable-to-blocked",
                ["changed", "walkability-regression"],
                "A Phase 3 strict-walkable tile became blocked",
                before,
                after,
            )
    elif not b_strict and a_strict:
        if b_opt:
            emit(
                "conditional-to-strict",
                ["changed", "walkability-improvement"],
                "A Phase 3 conditional tile became strict-walkable",
                before,
                after,
            )
        else:
            emit(
                "blocked-to-strict-walkable",
                ["changed", "walkability-improvement"],
                "A Phase 3 blocked tile became strict-walkable",
                before,
                after,
            )
    if b_opt and not a_opt:
        emit(
            "optimistic-walkable-to-blocked",
            ["changed", "walkability-regression"],
            "A Phase 3 optimistic-walkable tile became blocked",
            before,
            after,
        )
    if bool(before["hasGround"]) and not bool(after["hasGround"]):
        emit("ground-removed", ["removed", "walkability-regression"], "Confirmed ground was removed", before["groundItemIds"], after["groundItemIds"])
    elif not bool(before["hasGround"]) and bool(after["hasGround"]):
        emit("ground-added", ["added", "walkability-improvement"], "Confirmed ground was added", before["groundItemIds"], after["groundItemIds"])
    elif before["groundItemIds"] != after["groundItemIds"]:
        emit("ground-changed", ["changed"], "The exact confirmed ground item evidence changed", before["groundItemIds"], after["groundItemIds"])

    for field, added_kind, removed_kind, regression, improvement in (
        ("staticBlockers", "static-blocker-added", "static-blocker-removed", True, True),
        ("conditionalBlockers", "conditional-blocker-added", "conditional-blocker-removed", True, True),
        ("unknownAppearances", "unknown-appearance-added", "unknown-appearance-removed", True, True),
    ):
        before_set = set(before[field])
        after_set = set(after[field])
        added = sorted(after_set - before_set)
        removed = sorted(before_set - after_set)
        if added:
            emit(
                added_kind,
                ["added", "walkability-regression"] if regression else ["added"],
                f"{field} evidence was added",
                [],
                added,
                {"itemIds": added},
            )
        if removed:
            emit(
                removed_kind,
                ["removed", "walkability-improvement"] if improvement else ["removed"],
                f"{field} evidence was removed",
                removed,
                [],
                {"itemIds": removed},
            )
    return changes


def _emit_all_items(
    collector: FindingCollector,
    correlation_index: Mapping[str, Any] | None,
    snapshot: TileSnapshot,
    *,
    added: bool,
) -> int:
    count = 0
    for index, item in enumerate(snapshot.placements):
        count += 1
        _add(
            collector,
            correlation_index,
            kind="item-added" if added else "item-removed",
            classifications=["added" if added else "removed"],
            evidence_level="structural",
            position=snapshot.position,
            before=None if added else {"stackIndex": index, **dict(item)},
            after={"stackIndex": index, **dict(item)} if added else None,
            message="An exact item placement was added with its tile" if added else "An exact item placement was removed with its tile",
            details={"beforeStackIndex": None if added else index, "afterStackIndex": index if added else None},
        )
        for field in MECHANIC_FIELDS:
            if field not in item:
                continue
            _add(
                collector,
                correlation_index,
                kind="teleport-source-added" if added and field == "teleportDestination" else (
                    "teleport-source-removed" if not added and field == "teleportDestination" else (
                        "mechanic-added" if added else "mechanic-removed"
                    )
                ),
                classifications=["added" if added else "removed"],
                evidence_level="semantic",
                position=snapshot.position,
                before=None if added else item[field],
                after=item[field] if added else None,
                message="A map mechanic was added with its item" if added else "A map mechanic was removed with its item",
                details={"mechanicType": field, "stackIndex": index, "itemId": item["itemId"]},
            )
            count += 1
    return count


def compare_worlds(
    before_index: Any,
    after_index: Any,
    *,
    appearances: Mapping[int, Any] | None,
    bounds: tuple[Position, Position] | None,
    sample_limit: int,
    correlation_documents: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    collector = FindingCollector(sample_limit)
    correlation_index = build_correlation_index(correlation_documents or {}) if correlation_documents else None
    before_iterator = iter(iter_snapshots(before_index, appearances, bounds))
    after_iterator = iter(iter_snapshots(after_index, appearances, bounds))
    before_current = next(before_iterator, None)
    after_current = next(after_iterator, None)
    before_tiles = after_tiles = unchanged_tiles = changed_positions = 0
    before_placements = after_placements = 0

    while before_current is not None or after_current is not None:
        if before_current is None:
            relation = 1
        elif after_current is None:
            relation = -1
        else:
            relation = (_position_key(before_current.position) > _position_key(after_current.position)) - (
                _position_key(before_current.position) < _position_key(after_current.position)
            )
        start_total = collector.total
        if relation < 0:
            snapshot = before_current
            assert snapshot is not None
            before_tiles += 1
            before_placements += len(snapshot.placements)
            _add(
                collector,
                correlation_index,
                kind="tile-removed",
                classifications=["removed"],
                evidence_level="structural",
                position=snapshot.position,
                before=snapshot.tile_json(),
                after=None,
                message="An exact indexed tile position was removed",
            )
            _emit_all_items(collector, correlation_index, snapshot, added=False)
            before_current = next(before_iterator, None)
        elif relation > 0:
            snapshot = after_current
            assert snapshot is not None
            after_tiles += 1
            after_placements += len(snapshot.placements)
            _add(
                collector,
                correlation_index,
                kind="tile-added",
                classifications=["added"],
                evidence_level="structural",
                position=snapshot.position,
                before=None,
                after=snapshot.tile_json(),
                message="An exact indexed tile position was added",
            )
            _emit_all_items(collector, correlation_index, snapshot, added=True)
            after_current = next(after_iterator, None)
        else:
            before_snapshot = before_current
            after_snapshot = after_current
            assert before_snapshot is not None and after_snapshot is not None
            before_tiles += 1
            after_tiles += 1
            before_placements += len(before_snapshot.placements)
            after_placements += len(after_snapshot.placements)
            position = before_snapshot.position
            if before_snapshot.kind != after_snapshot.kind:
                _add(
                    collector,
                    correlation_index,
                    kind="tile-kind-changed",
                    classifications=["changed"],
                    evidence_level="structural",
                    position=position,
                    before=before_snapshot.kind,
                    after=after_snapshot.kind,
                    message="Tile kind changed between regular and house tile",
                )
            if before_snapshot.flags != after_snapshot.flags:
                _add(
                    collector,
                    correlation_index,
                    kind="tile-flags-changed",
                    classifications=["changed"],
                    evidence_level="static",
                    position=position,
                    before=before_snapshot.flags,
                    after=after_snapshot.flags,
                    message="Tile flags changed",
                )
            if before_snapshot.house_id != after_snapshot.house_id:
                _add(
                    collector,
                    correlation_index,
                    kind="house-id-changed",
                    classifications=["changed"],
                    evidence_level="static",
                    position=position,
                    before=before_snapshot.house_id,
                    after=after_snapshot.house_id,
                    message="House ID changed",
                )
            compare_item_stacks(
                collector,
                correlation_index,
                position,
                before_snapshot.placements,
                after_snapshot.placements,
            )
            compare_walkability(
                collector,
                correlation_index,
                position,
                before_snapshot.walkability,
                after_snapshot.walkability,
            )
            if collector.total == start_total:
                unchanged_tiles += 1
            before_current = next(before_iterator, None)
            after_current = next(after_iterator, None)
        if collector.total > start_total:
            changed_positions += 1

    findings, finding_summary = collector.finish()
    return {
        "scope": {
            "type": "bounded-region" if bounds is not None else "full-index",
            "from": list(bounds[0]) if bounds is not None else None,
            "to": list(bounds[1]) if bounds is not None else None,
        },
        "summary": {
            "beforeTiles": before_tiles,
            "afterTiles": after_tiles,
            "beforePlacements": before_placements,
            "afterPlacements": after_placements,
            "unchangedTiles": unchanged_tiles,
            "changedPositions": changed_positions,
            "findings": finding_summary,
        },
        "findings": findings,
        "correlation": {
            "enabled": correlation_index is not None,
            "reports": correlation_index["provenance"] if correlation_index is not None else [],
            "indexedNodes": correlation_index["indexedNodes"] if correlation_index is not None else 0,
        },
    }
