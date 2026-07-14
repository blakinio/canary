from __future__ import annotations

from collections import Counter, deque
from pathlib import Path
from typing import Any, Iterable, Mapping

from otbm_geometry_audit_types import (
    DEFAULT_ORPHAN_MAX_TILES,
    DEFAULT_SAMPLE_LIMIT,
    DIRECTIONS,
    MAX_JSON_BYTES,
    PZ_FLAG_MASK,
    REPORT_FORMAT,
    SCHEMA_VERSION,
    AdjacencyRule,
    FindingCollector,
    GeometryAuditError,
    Position,
    appearance_sprite_evidence,
    component_bounds,
    load_json,
    load_rules,
    normalize_bounds,
    resolve_artifact_path,
    sha256_path,
    touches_boundary,
)
from otbm_reachability_transition import _classify_tile
from otbm_reachability_types import FindingCollector as ReachabilityFindingCollector
from otbm_reachability_types import load_appearance_semantics
from otbm_world_index import WORLD_INDEX_FORMAT, WorldIndex

CARDINAL_STEPS: tuple[Position, ...] = tuple(DIRECTIONS.values())


def _add(position: Position, delta: Position) -> Position:
    return position[0] + delta[0], position[1] + delta[1], position[2] + delta[2]


def _load_appearance_document(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        document = load_json(path, label="appearances document", max_bytes=MAX_JSON_BYTES)
    else:
        try:
            from otbm_appearances import build_appearances_index
        except ImportError as exc:
            raise GeometryAuditError("otbm_appearances.py is required for a binary appearances catalogue") from exc
        document = build_appearances_index(path)
    if not isinstance(document, dict) or document.get("format") != "canary-appearances-index-v1":
        raise GeometryAuditError(f"Unsupported appearances document: {path}")
    return document


def _validate_index_manifest(index_path: Path, manifest_path: Path, index: WorldIndex) -> dict[str, Any]:
    manifest = load_json(manifest_path, label="world-index manifest", max_bytes=4 * 1024 * 1024)
    if not isinstance(manifest, dict) or manifest.get("format") != WORLD_INDEX_FORMAT or manifest.get("schemaVersion") != 1:
        raise GeometryAuditError(f"Unsupported world-index manifest: {manifest_path}")
    index_record = manifest.get("index")
    source_record = manifest.get("source")
    scanner_record = manifest.get("scanner")
    if not isinstance(index_record, dict) or not isinstance(source_record, dict) or not isinstance(scanner_record, dict):
        raise GeometryAuditError("world-index manifest is missing index/source/scanner provenance")
    expected_size = index_record.get("size")
    expected_hash = index_record.get("sha256")
    if expected_size != index_path.stat().st_size:
        raise GeometryAuditError(
            f"world-index size mismatch: manifest={expected_size!r}; actual={index_path.stat().st_size}"
        )
    actual_hash = sha256_path(index_path)
    if expected_hash != actual_hash:
        raise GeometryAuditError(f"world-index SHA-256 mismatch: manifest={expected_hash!r}; actual={actual_hash}")
    header = index.header_json()
    if manifest.get("otbm") != header["otbm"]:
        raise GeometryAuditError("world-index manifest OTBM metadata does not match the binary index")
    if manifest.get("summary") != header["summary"]:
        raise GeometryAuditError("world-index manifest summary does not match the binary index")
    return {
        "index": {
            "path": index_path.name,
            "size": index_path.stat().st_size,
            "sha256": actual_hash,
            "format": WORLD_INDEX_FORMAT,
        },
        "manifest": {
            "path": manifest_path.name,
            "size": manifest_path.stat().st_size,
            "sha256": sha256_path(manifest_path),
        },
        "source": source_record,
        "scanner": scanner_record,
        "otbm": header["otbm"],
        "worldSummary": header["summary"],
    }


def _components(positions: Iterable[Position]) -> list[tuple[Position, ...]]:
    remaining = set(positions)
    result: list[tuple[Position, ...]] = []
    while remaining:
        start = min(remaining, key=lambda position: (position[2], position[1], position[0]))
        remaining.remove(start)
        queue: deque[Position] = deque((start,))
        component: list[Position] = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for step in CARDINAL_STEPS:
                neighbor = _add(current, step)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        component.sort(key=lambda position: (position[2], position[1], position[0]))
        result.append(tuple(component))
    result.sort(key=lambda component: (component[0][2], component[0][1], component[0][0]))
    return result


def _component_detail(component: tuple[Position, ...], lower: Position, upper: Position) -> dict[str, Any]:
    component_lower, component_upper = component_bounds(component)
    boundary = any(touches_boundary(position, lower, upper) for position in component)
    return {
        "componentSize": len(component),
        "componentBounds": {"from": list(component_lower), "to": list(component_upper)},
        "componentPositions": [list(position) for position in component[:32]],
        "componentPositionsTruncated": len(component) > 32,
        "touchesScopeBoundary": boundary,
    }


def _apply_adjacency_rules(
    *,
    rules: list[AdjacencyRule],
    tile_items: Mapping[Position, frozenset[int]],
    findings: FindingCollector,
) -> int:
    checks = 0
    for position in sorted(tile_items, key=lambda value: (value[2], value[1], value[0])):
        item_ids = tile_items[position]
        for rule in rules:
            matched = sorted(item_ids.intersection(rule.source_item_ids))
            if not matched:
                continue
            checks += 1
            neighbor = _add(position, DIRECTIONS[rule.direction])
            neighbor_items = tile_items.get(neighbor)
            if neighbor_items is not None and neighbor_items.intersection(rule.required_neighbor_item_ids):
                continue
            findings.add(
                f"{rule.category}-adjacency-mismatch",
                rule.severity,
                rule.confidence,
                rule.message,
                position=position,
                ruleId=rule.rule_id,
                category=rule.category,
                direction=rule.direction,
                sourceItemIds=matched,
                neighbor=list(neighbor),
                requiredNeighborItemIds=list(rule.required_neighbor_item_ids),
                actualNeighborItemIds=[] if neighbor_items is None else sorted(neighbor_items),
                neighborTileExists=neighbor_items is not None,
                evidence="reviewed-geometry-rule",
            )
    return checks


def analyze_geometry(
    *,
    artifact_root: Path,
    index_path: Path,
    manifest_path: Path,
    appearances_path: Path,
    lower: Position,
    upper: Position,
    rules_path: Path | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    orphan_max_tiles: int = DEFAULT_ORPHAN_MAX_TILES,
) -> dict[str, Any]:
    if not isinstance(orphan_max_tiles, int) or isinstance(orphan_max_tiles, bool) or not 1 <= orphan_max_tiles <= 10_000:
        raise GeometryAuditError("orphan_max_tiles must be in 1..10000")
    lower, upper = normalize_bounds(lower, upper)
    root = artifact_root.expanduser().resolve()
    index_file = resolve_artifact_path(root, index_path, label="world index", max_bytes=4 * 1024 * 1024 * 1024)
    manifest_file = resolve_artifact_path(root, manifest_path, label="world-index manifest", max_bytes=4 * 1024 * 1024)
    appearances_file = resolve_artifact_path(root, appearances_path, label="appearances", max_bytes=512 * 1024 * 1024)
    rules_file = (
        resolve_artifact_path(root, rules_path, label="geometry rules", max_bytes=4 * 1024 * 1024)
        if rules_path is not None
        else None
    )
    rules, rules_provenance = load_rules(rules_file)
    semantics, semantics_provenance = load_appearance_semantics(appearances_file)
    appearance_document = _load_appearance_document(appearances_file)
    sprite_evidence = appearance_sprite_evidence(appearance_document)
    findings = FindingCollector(sample_limit)

    tiles: dict[Position, dict[str, Any]] = {}
    tile_items: dict[Position, frozenset[int]] = {}
    placement_total = 0
    house_tiles: dict[int, set[Position]] = {}
    pz_positions: set[Position] = set()
    unknown_item_ids: Counter[int] = Counter()
    blocker_candidates: set[tuple[Position, int]] = set()

    with WorldIndex(index_file) as index:
        index_provenance = _validate_index_manifest(index_file, manifest_file, index)
        for tile_index, tile in index.iter_region_tiles(lower, upper):
            position: Position = (tile.x, tile.y, tile.z)
            if position in tiles:
                raise GeometryAuditError(f"world index exposes duplicate tile position in selected scope: {position}")
            placements = [
                index.placement(ordinal)
                for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count)
            ]
            placement_total += len(placements)
            reachability_findings = ReachabilityFindingCollector(limit=1)
            state = _classify_tile(index, tile_index, tile, semantics, reachability_findings)
            item_ids = tuple(int(placement["itemId"]) for placement in placements)
            item_set = frozenset(item_ids)
            ground_placements = [
                placement
                for placement in placements
                if sprite_evidence.get(int(placement["itemId"])) is not None
                and sprite_evidence[int(placement["itemId"])].ground
            ]
            if not state.has_ground:
                findings.add(
                    "item-without-floor",
                    "error",
                    "high",
                    "Indexed tile contains item evidence but has no confirmed ground appearance",
                    position=position,
                    itemIds=sorted(item_set),
                    placementCount=len(placements),
                    evidence="world-index+appearances",
                )
            if len(ground_placements) > 1:
                findings.add(
                    "multiple-ground-items",
                    "warning",
                    "medium",
                    "Tile contains more than one placement with confirmed ground appearance",
                    position=position,
                    groundItemIds=[int(placement["itemId"]) for placement in ground_placements],
                    groundPlacementOrdinals=[int(placement["placementOrdinal"]) for placement in ground_placements],
                    evidence="world-index+appearances",
                )
            if state.unknown_appearances:
                for item_id in state.unknown_appearances:
                    unknown_item_ids[item_id] += 1
                findings.add(
                    "unknown-appearance",
                    "warning",
                    "medium",
                    "Tile contains item IDs absent from the supplied appearances catalogue",
                    position=position,
                    itemIds=sorted(set(state.unknown_appearances)),
                    evidence="world-index+appearances",
                )
            for item_id in sorted(item_set):
                evidence = sprite_evidence.get(item_id)
                if evidence is not None and evidence.unpassable and not evidence.has_nonzero_sprite:
                    blocker_candidates.add((position, item_id))
            if tile.kind == "house":
                house_id = tile.house_id
                if house_id is None or house_id <= 0:
                    findings.add(
                        "house-tile-without-house-id",
                        "error",
                        "high",
                        "House tile has no positive house ID",
                        position=position,
                        houseId=house_id,
                        evidence="world-index",
                    )
                else:
                    house_tiles.setdefault(int(house_id), set()).add(position)
            if tile.flags & PZ_FLAG_MASK:
                pz_positions.add(position)
            tiles[position] = {
                "tileIndex": tile_index,
                "kind": tile.kind,
                "houseId": tile.house_id,
                "flags": int(tile.flags),
                "state": state,
                "placements": placements,
            }
            tile_items[position] = item_set

    for position, item_id in sorted(blocker_candidates, key=lambda value: (value[0][2], value[0][1], value[0][0], value[1])):
        findings.add(
            "invisible-blocker-candidate",
            "warning",
            "low",
            "Confirmed unpassable appearance has no nonzero sprite-ID evidence",
            position=position,
            itemId=item_id,
            evidence="appearance-unpassable+sprite-id-absence",
            limitation="No sprite pixels or runtime state were inspected",
        )

    tile_components = _components(tiles)
    orphan_components = 0
    for component in tile_components:
        if len(component) > orphan_max_tiles:
            continue
        orphan_components += 1
        detail = _component_detail(component, lower, upper)
        boundary = bool(detail["touchesScopeBoundary"])
        findings.add(
            "orphan-tile-component",
            "warning",
            "low" if boundary else "medium",
            "Small cardinal tile component is structurally isolated inside the selected scope",
            position=component[0],
            **detail,
            evidence="world-index-cardinal-adjacency",
            limitation=(
                "Component touches the selected scope boundary"
                if boundary
                else "Scripts, reviewed floor transitions and runtime teleportation may provide connectivity"
            ),
        )

    disconnected_houses = 0
    mixed_pz_house_components = 0
    for house_id in sorted(house_tiles):
        components = _components(house_tiles[house_id])
        if len(components) > 1:
            disconnected_houses += 1
            touches = any(
                touches_boundary(position, lower, upper)
                for component in components
                for position in component
            )
            findings.add(
                "house-disconnected-components",
                "warning",
                "low" if touches else "high",
                "One exact house ID occupies multiple cardinal components in the selected scope",
                position=components[0][0],
                houseId=house_id,
                componentCount=len(components),
                componentSizes=[len(component) for component in components],
                componentBounds=[
                    {"from": list(component_bounds(component)[0]), "to": list(component_bounds(component)[1])}
                    for component in components[:64]
                ],
                componentsTruncated=len(components) > 64,
                touchesScopeBoundary=touches,
                evidence="world-index-house-id+cardinal-adjacency",
            )
        for component in components:
            pz_count = sum(position in pz_positions for position in component)
            if 0 < pz_count < len(component):
                mixed_pz_house_components += 1
                detail = _component_detail(component, lower, upper)
                findings.add(
                    "house-component-mixed-pz",
                    "warning",
                    "medium",
                    "One cardinal house component mixes protection-zone and non-protection-zone tile flags",
                    position=component[0],
                    houseId=house_id,
                    protectionZoneTiles=pz_count,
                    nonProtectionZoneTiles=len(component) - pz_count,
                    protectionZoneMask=PZ_FLAG_MASK,
                    **detail,
                    evidence="world-index-house-id+verified-otbm-pz-flag",
                )

    pz_components = _components(pz_positions)
    isolated_pz_tiles = 0
    for component in pz_components:
        if len(component) != 1:
            continue
        isolated_pz_tiles += 1
        position = component[0]
        boundary = touches_boundary(position, lower, upper)
        findings.add(
            "isolated-pz-tile",
            "warning",
            "low",
            "Protection-zone flag occurs as a one-tile cardinal component in the selected scope",
            position=position,
            protectionZoneMask=PZ_FLAG_MASK,
            touchesScopeBoundary=boundary,
            evidence="verified-otbm-pz-flag+cardinal-adjacency",
        )

    pz_enclosed_gaps = 0
    for position in sorted(tiles, key=lambda value: (value[2], value[1], value[0])):
        if position in pz_positions:
            continue
        neighbors = tuple(_add(position, step) for step in CARDINAL_STEPS)
        if all(neighbor in tiles and neighbor in pz_positions for neighbor in neighbors):
            pz_enclosed_gaps += 1
            findings.add(
                "pz-enclosed-gap",
                "warning",
                "medium",
                "Non-PZ tile is cardinally enclosed by PZ tiles",
                position=position,
                neighbors=[list(neighbor) for neighbor in neighbors],
                protectionZoneMask=PZ_FLAG_MASK,
                evidence="verified-otbm-pz-flag+cardinal-adjacency",
            )

    adjacency_checks = _apply_adjacency_rules(rules=rules, tile_items=tile_items, findings=findings)
    samples, finding_summary = findings.finish()
    appearances_provenance = {
        **semantics_provenance,
        "sha256": sha256_path(appearances_file),
        "size": appearances_file.stat().st_size,
        "objectCountWithSpriteEvidence": len(sprite_evidence),
    }
    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": finding_summary["bySeverity"]["error"] == 0,
        "complete": True,
        "policy": {
            "readOnly": True,
            "otbmParsedIndependently": False,
            "phase3ClassifierReused": True,
            "dynamicLuaExecuted": False,
            "visualIntentInferred": False,
            "wallBorderRulesRequired": True,
            "protectionZoneMask": PZ_FLAG_MASK,
            "mapModified": False,
            "aiImageryUsed": False,
            "scopeIsGlobal": False,
        },
        "scope": {
            "from": list(lower),
            "to": list(upper),
            "coordinateCount": (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1) * (upper[2] - lower[2] + 1),
            "orphanMaxTiles": orphan_max_tiles,
            "sampleLimit": sample_limit,
        },
        "provenance": {
            **index_provenance,
            "appearances": appearances_provenance,
            "geometryRules": rules_provenance,
        },
        "summary": {
            "tiles": len(tiles),
            "placements": placement_total,
            "tileComponents": len(tile_components),
            "orphanCandidateComponents": orphan_components,
            "houses": len(house_tiles),
            "disconnectedHouses": disconnected_houses,
            "houseComponentsWithMixedPz": mixed_pz_house_components,
            "protectionZoneTiles": len(pz_positions),
            "protectionZoneComponents": len(pz_components),
            "isolatedProtectionZoneTiles": isolated_pz_tiles,
            "protectionZoneEnclosedGaps": pz_enclosed_gaps,
            "invisibleBlockerCandidates": len(blocker_candidates),
            "unknownAppearancePlacementsByItemId": [
                {"itemId": item_id, "placements": count}
                for item_id, count in sorted(unknown_item_ids.items())
            ],
            "adjacencyRules": len(rules),
            "adjacencyChecks": adjacency_checks,
            "findings": finding_summary,
        },
        "rules": [rule.to_json() for rule in rules],
        "findings": samples,
    }
