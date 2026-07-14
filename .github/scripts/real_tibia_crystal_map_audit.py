from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
sys.path.insert(0, str((ROOT / "tools/ai-agent").resolve()))

from otbm_world_index import (  # noqa: E402
    MECHANIC_STRUCT,
    NO_MECHANIC,
    PLACEMENT_STRUCT,
    POSTING_STRUCT,
    TILE_STRUCT,
    WorldIndex,
)

OUTPUT = ROOT / "audit/output"
BASELINE_MAP = ROOT / "audit/maps/baseline.otbm"
CRYSTAL_MAP = ROOT / "audit/maps/crystal.otbm"
BASELINE_INDEX = ROOT / "audit/index/baseline.widx"
CRYSTAL_INDEX = ROOT / "audit/index/crystal.widx"
CANARY_WORLD = ROOT / "data-otservbr-global/world"
CRYSTAL_ROOT = ROOT / "external/crystalserver/data-global"
CRYSTAL_WORLD = CRYSTAL_ROOT / "world"
EXPECTED_BASELINE = os.environ["BASELINE_SHA256"]
CRYSTAL_COMMIT = os.environ["CRYSTAL_SHA"]
CANARY_COMMIT = os.environ["CANARY_SHA"]
SAMPLE_LIMIT = 12


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def tile_raw(world: WorldIndex, tile_index: int) -> tuple[int, ...]:
    offset = world.header.tile_offset + tile_index * TILE_STRUCT.size
    return TILE_STRUCT.unpack_from(world._mmap, offset)


def area_tiles(world: WorldIndex, area: Any) -> list[tuple[tuple[int, int], tuple[int, ...]]]:
    result: list[tuple[tuple[int, int], tuple[int, ...]]] = []
    for local_index in range(area.tile_count):
        posting_offset = (
            world.header.area_postings_offset
            + (area.postings_start + local_index) * POSTING_STRUCT.size
        )
        tile_index = POSTING_STRUCT.unpack_from(world._mmap, posting_offset)[0]
        raw = tile_raw(world, tile_index)
        result.append(((raw[1], raw[0]), raw))
    result.sort(key=lambda row: row[0])
    return result


def mechanic_payload(
    world: WorldIndex,
    mechanic_index: int,
    placement_ordinal: int,
) -> tuple[int, ...] | None:
    if mechanic_index == NO_MECHANIC:
        return None
    offset = world.header.mechanic_offset + mechanic_index * MECHANIC_STRUCT.size
    values = MECHANIC_STRUCT.unpack_from(world._mmap, offset)
    if values[-1] != placement_ordinal:
        raise RuntimeError(
            f"mechanic {mechanic_index} points to {values[-1]}, "
            f"expected {placement_ordinal}"
        )
    return values[:-1]


def placement_raw(
    world: WorldIndex,
    ordinal: int,
) -> tuple[int, int, tuple[int, ...] | None]:
    offset = world.header.placement_offset + ordinal * PLACEMENT_STRUCT.size
    item_id, meta, mechanic_index, _tile_index = PLACEMENT_STRUCT.unpack_from(
        world._mmap,
        offset,
    )
    return item_id, meta, mechanic_payload(world, mechanic_index, ordinal)


def compare_stacks(
    left: WorldIndex,
    left_raw: tuple[int, ...],
    right: WorldIndex,
    right_raw: tuple[int, ...],
) -> tuple[bool, bool]:
    left_start, left_count = left_raw[6], left_raw[7]
    right_start, right_count = right_raw[6], right_raw[7]
    item_changed = left_count != right_count
    mechanic_changed = False
    shared = min(left_count, right_count)
    for offset in range(shared):
        left_item, left_meta, left_mechanic = placement_raw(left, left_start + offset)
        right_item, right_meta, right_mechanic = placement_raw(right, right_start + offset)
        if (left_item, left_meta) != (right_item, right_meta):
            item_changed = True
        if left_mechanic != right_mechanic:
            mechanic_changed = True
    if left_count != right_count:
        for offset in range(shared, left_count):
            if placement_raw(left, left_start + offset)[2] is not None:
                mechanic_changed = True
                break
        if not mechanic_changed:
            for offset in range(shared, right_count):
                if placement_raw(right, right_start + offset)[2] is not None:
                    mechanic_changed = True
                    break
    return item_changed, mechanic_changed


def stack_json(world: WorldIndex, raw: tuple[int, ...]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    start, count = raw[6], raw[7]
    for offset in range(count):
        item_id, meta, mechanic = placement_raw(world, start + offset)
        node = bool(meta & 0x8000)
        row: dict[str, Any] = {
            "itemId": item_id,
            "source": "node" if node else "inline",
            "depth": (meta & 0x7FFF) if node else -1,
        }
        if mechanic is not None:
            flags, action_id, unique_id, house_door_id, tele_x, tele_y, tele_z = mechanic
            if flags & 1:
                row["actionId"] = action_id
            if flags & 2:
                row["uniqueId"] = unique_id
            if flags & 4:
                row["houseDoorId"] = house_door_id
            if flags & 8:
                row["teleportDestination"] = [tele_x, tele_y, tele_z]
        result.append(row)
    return result


def map_summary(world: WorldIndex, map_path: Path, index_path: Path) -> dict[str, Any]:
    header = world.header
    return {
        "mapSize": map_path.stat().st_size,
        "mapSha256": sha256_path(map_path),
        "indexSize": index_path.stat().st_size,
        "indexSha256": sha256_path(index_path),
        "otbmVersion": header.otbm_version,
        "mapWidth": header.map_width,
        "mapHeight": header.map_height,
        "itemsMajor": header.items_major,
        "itemsMinor": header.items_minor,
        "tiles": header.tile_count,
        "placements": header.placement_count,
        "mechanics": header.mechanic_count,
        "areas": header.area_count,
        "rawAreas": header.raw_area_count,
        "unknownAttributeTails": header.unknown_attribute_tails,
        "maxItemDepth": header.max_item_depth,
    }


def update_bounds(
    target: dict[str, dict[str, dict[str, int]]],
    category: str,
    x: int,
    y: int,
    z: int,
) -> None:
    floor = target.setdefault(str(z), {})
    entry = floor.setdefault(
        category,
        {"count": 0, "minX": x, "maxX": x, "minY": y, "maxY": y},
    )
    entry["count"] += 1
    entry["minX"] = min(entry["minX"], x)
    entry["maxX"] = max(entry["maxX"], x)
    entry["minY"] = min(entry["minY"], y)
    entry["maxY"] = max(entry["maxY"], y)


def add_sample(
    samples: dict[str, list[dict[str, Any]]],
    category: str,
    row: dict[str, Any],
) -> None:
    bucket = samples.setdefault(category, [])
    if len(bucket) < SAMPLE_LIMIT:
        bucket.append(row)


def sidecar_inventory(root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.xml")):
        if not any(token in path.name.lower() for token in ("house", "spawn", "npc", "zone")):
            continue
        row: dict[str, Any] = {
            "name": path.name,
            "size": path.stat().st_size,
            "sha256": sha256_path(path),
        }
        try:
            xml_root = ET.parse(path).getroot()
            row["rootTag"] = xml_root.tag
            row["directChildren"] = len(list(xml_root))
        except ET.ParseError as error:
            row["parseError"] = str(error)
        result.append(row)
    return result


def house_file(root: Path) -> Path | None:
    candidates = sorted(root.glob("*house*.xml"))
    return candidates[0] if candidates else None


def houses(path: Path | None) -> dict[int, dict[str, str]]:
    if path is None:
        return {}
    result: dict[int, dict[str, str]] = {}
    for node in ET.parse(path).getroot().findall(".//house"):
        attrs = dict(sorted(node.attrib.items()))
        raw_id = attrs.get("houseid") or attrs.get("id")
        if raw_id is not None:
            result[int(raw_id)] = attrs
    return result


def file_tree(path: Path) -> dict[str, str]:
    if not path.is_dir():
        return {}
    return {
        file.relative_to(path).as_posix(): sha256_path(file)
        for file in sorted(path.rglob("*"))
        if file.is_file()
    }


def record_one_sided(
    totals: Counter[str],
    bounds: dict[str, dict[str, dict[str, int]]],
    hotspots: Counter[tuple[int, int, int]],
    samples: dict[str, list[dict[str, Any]]],
    category: str,
    area_key: tuple[int, int, int],
    world: WorldIndex,
    raw: tuple[int, ...],
) -> None:
    x, y, z = raw[0], raw[1], raw[2]
    totals[f"{category}Tiles"] += 1
    totals["anyChangedPositions"] += 1
    hotspots[area_key] += 1
    update_bounds(bounds, category, x, y, z)
    update_bounds(bounds, "anyChanged", x, y, z)
    add_sample(
        samples,
        category,
        {"position": [x, y, z], "stack": stack_json(world, raw)},
    )


def compare_worlds() -> dict[str, Any]:
    totals: Counter[str] = Counter()
    bounds: dict[str, dict[str, dict[str, int]]] = {}
    hotspots: Counter[tuple[int, int, int]] = Counter()
    samples: dict[str, list[dict[str, Any]]] = {}

    with WorldIndex(BASELINE_INDEX) as baseline, WorldIndex(CRYSTAL_INDEX) as crystal:
        baseline_summary = map_summary(baseline, BASELINE_MAP, BASELINE_INDEX)
        crystal_summary = map_summary(crystal, CRYSTAL_MAP, CRYSTAL_INDEX)
        if baseline_summary["mapSha256"] != EXPECTED_BASELINE:
            raise RuntimeError("baseline hash drifted during comparison")

        left_area = 0
        right_area = 0
        processed_area_keys = 0
        while left_area < len(baseline.areas) or right_area < len(crystal.areas):
            left = baseline.areas[left_area] if left_area < len(baseline.areas) else None
            right = crystal.areas[right_area] if right_area < len(crystal.areas) else None
            left_key = (left.z, left.base_y, left.base_x) if left else None
            right_key = (right.z, right.base_y, right.base_x) if right else None

            if right is None or (left is not None and left_key < right_key):
                area_key = (left.base_x, left.base_y, left.z)
                for _position, raw in area_tiles(baseline, left):
                    record_one_sided(
                        totals,
                        bounds,
                        hotspots,
                        samples,
                        "baselineOnly",
                        area_key,
                        baseline,
                        raw,
                    )
                left_area += 1
            elif left is None or right_key < left_key:
                area_key = (right.base_x, right.base_y, right.z)
                for _position, raw in area_tiles(crystal, right):
                    record_one_sided(
                        totals,
                        bounds,
                        hotspots,
                        samples,
                        "crystalOnly",
                        area_key,
                        crystal,
                        raw,
                    )
                right_area += 1
            else:
                area_key = (left.base_x, left.base_y, left.z)
                left_tiles = area_tiles(baseline, left)
                right_tiles = area_tiles(crystal, right)
                left_tile = 0
                right_tile = 0
                while left_tile < len(left_tiles) or right_tile < len(right_tiles):
                    left_row = left_tiles[left_tile] if left_tile < len(left_tiles) else None
                    right_row = right_tiles[right_tile] if right_tile < len(right_tiles) else None
                    left_position = left_row[0] if left_row else None
                    right_position = right_row[0] if right_row else None

                    if right_row is None or (
                        left_row is not None and left_position < right_position
                    ):
                        record_one_sided(
                            totals,
                            bounds,
                            hotspots,
                            samples,
                            "baselineOnly",
                            area_key,
                            baseline,
                            left_row[1],
                        )
                        left_tile += 1
                    elif left_row is None or right_position < left_position:
                        record_one_sided(
                            totals,
                            bounds,
                            hotspots,
                            samples,
                            "crystalOnly",
                            area_key,
                            crystal,
                            right_row[1],
                        )
                        right_tile += 1
                    else:
                        left_raw = left_row[1]
                        right_raw = right_row[1]
                        x, y, z = left_raw[0], left_raw[1], left_raw[2]
                        totals["commonTiles"] += 1
                        metadata_changed = left_raw[3:6] != right_raw[3:6]
                        item_changed, mechanic_changed = compare_stacks(
                            baseline,
                            left_raw,
                            crystal,
                            right_raw,
                        )
                        categories: list[str] = []
                        if metadata_changed:
                            totals["tileMetadataChanged"] += 1
                            update_bounds(bounds, "metadataChanged", x, y, z)
                            categories.append("metadata")
                        if item_changed:
                            totals["itemStackChanged"] += 1
                            update_bounds(bounds, "itemStackChanged", x, y, z)
                            categories.append("items")
                        if mechanic_changed:
                            totals["mechanicChanged"] += 1
                            update_bounds(bounds, "mechanicChanged", x, y, z)
                            categories.append("mechanics")
                        if categories:
                            totals["commonChangedPositions"] += 1
                            totals["anyChangedPositions"] += 1
                            hotspots[area_key] += 1
                            update_bounds(bounds, "anyChanged", x, y, z)
                            add_sample(
                                samples,
                                "commonChanged",
                                {
                                    "position": [x, y, z],
                                    "categories": categories,
                                    "baseline": {
                                        "tile": {
                                            "kind": left_raw[3],
                                            "houseId": left_raw[4],
                                            "flags": left_raw[5],
                                        },
                                        "stack": stack_json(baseline, left_raw),
                                    },
                                    "crystal": {
                                        "tile": {
                                            "kind": right_raw[3],
                                            "houseId": right_raw[4],
                                            "flags": right_raw[5],
                                        },
                                        "stack": stack_json(crystal, right_raw),
                                    },
                                },
                            )
                        else:
                            totals["identicalCommonTiles"] += 1
                        left_tile += 1
                        right_tile += 1
                left_area += 1
                right_area += 1

            processed_area_keys += 1
            if processed_area_keys % 100 == 0:
                print(
                    f"processed {processed_area_keys} area keys; "
                    f"changed positions={totals['anyChangedPositions']}",
                    flush=True,
                )

    baseline_houses = houses(house_file(CANARY_WORLD))
    crystal_houses = houses(house_file(CRYSTAL_WORLD))
    added_house_ids = sorted(set(crystal_houses) - set(baseline_houses))
    removed_house_ids = sorted(set(baseline_houses) - set(crystal_houses))
    changed_house_ids = sorted(
        house_id
        for house_id in set(baseline_houses) & set(crystal_houses)
        if baseline_houses[house_id] != crystal_houses[house_id]
    )

    quest_inventory: dict[str, Any] = {}
    for quest_name in ("targuna", "newhaven"):
        canary_files = file_tree(ROOT / "data-otservbr-global/scripts/quests" / quest_name)
        crystal_files = file_tree(CRYSTAL_ROOT / "scripts/quests" / quest_name)
        quest_inventory[quest_name] = {
            "canaryCount": len(canary_files),
            "crystalCount": len(crystal_files),
            "onlyInCanary": sorted(set(canary_files) - set(crystal_files)),
            "onlyInCrystal": sorted(set(crystal_files) - set(canary_files)),
            "sameRelativePathChanged": sorted(
                name
                for name in set(canary_files) & set(crystal_files)
                if canary_files[name] != crystal_files[name]
            ),
        }

    return {
        "format": "canary-real-tibia-crystal-map-audit-v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "targetRepository": "blakinio/canary",
        "targetCommit": CANARY_COMMIT,
        "crystalRepository": "zimbadev/crystalserver",
        "crystalCommit": CRYSTAL_COMMIT,
        "baseline": baseline_summary,
        "crystal": crystal_summary,
        "comparison": dict(sorted(totals.items())),
        "changedBoundsByFloor": bounds,
        "topChangedAreas": [
            {
                "baseX": base_x,
                "baseY": base_y,
                "z": z,
                "changedPositions": count,
            }
            for (base_x, base_y, z), count in hotspots.most_common(50)
        ],
        "samples": samples,
        "sidecars": {
            "canary": sidecar_inventory(CANARY_WORLD),
            "crystal": sidecar_inventory(CRYSTAL_WORLD),
            "houses": {
                "canaryCount": len(baseline_houses),
                "crystalCount": len(crystal_houses),
                "added": [crystal_houses[house_id] for house_id in added_house_ids],
                "removed": [baseline_houses[house_id] for house_id in removed_house_ids],
                "changedIds": changed_house_ids,
            },
        },
        "questInventory": quest_inventory,
        "limitations": [
            "Static OTBM and source-sidecar evidence is not live gameplay proof.",
            "Spawn/NPC/zone files are inventoried and hashed, not runtime-resolved in this task.",
            "This report authorizes no direct map, item-catalogue, asset or datapack import.",
            "Reusable semantic-diff implementation remains owned by PR #311.",
        ],
    }


def markdown(report: dict[str, Any]) -> str:
    baseline = report["baseline"]
    crystal = report["crystal"]
    comparison = report["comparison"]
    lines = [
        "# Real Tibia Crystal global-map snapshot audit",
        "",
        f"- Canary commit: `{report['targetCommit']}`",
        f"- CrystalServer commit: `{report['crystalCommit']}`",
        f"- Baseline map: `{baseline['mapSha256']}` ({baseline['mapSize']:,} bytes)",
        f"- Crystal map: `{crystal['mapSha256']}` ({crystal['mapSize']:,} bytes)",
        "",
        "## World-index summary",
        "",
        "| Metric | Baseline | Crystal | Delta |",
        "|---|---:|---:|---:|",
    ]
    for key, label in (
        ("tiles", "Tiles"),
        ("placements", "Placements"),
        ("mechanics", "Mechanics"),
        ("areas", "Query areas"),
        ("rawAreas", "Raw OTBM areas"),
    ):
        left = baseline[key]
        right = crystal[key]
        lines.append(f"| {label} | {left:,} | {right:,} | {right - left:+,} |")

    lines.extend(
        [
            "",
            "## Exact coordinate comparison",
            "",
            "| Category | Count |",
            "|---|---:|",
        ]
    )
    for key in (
        "identicalCommonTiles",
        "commonChangedPositions",
        "baselineOnlyTiles",
        "crystalOnlyTiles",
        "tileMetadataChanged",
        "itemStackChanged",
        "mechanicChanged",
        "anyChangedPositions",
    ):
        lines.append(f"| `{key}` | {comparison.get(key, 0):,} |")

    lines.extend(
        [
            "",
            "## Top changed 256x256 areas",
            "",
            "| Base X | Base Y | Z | Changed positions |",
            "|---:|---:|---:|---:|",
        ]
    )
    for row in report["topChangedAreas"][:25]:
        lines.append(
            f"| {row['baseX']} | {row['baseY']} | {row['z']} | "
            f"{row['changedPositions']:,} |"
        )

    houses_report = report["sidecars"]["houses"]
    lines.extend(
        [
            "",
            "## House sidecar",
            "",
            f"- Canary houses: **{houses_report['canaryCount']:,}**",
            f"- Crystal houses: **{houses_report['crystalCount']:,}**",
            f"- Added houses: `{[row.get('houseid') for row in houses_report['added']]}`",
            f"- Removed houses: `{[row.get('houseid') for row in houses_report['removed']]}`",
            f"- Changed shared house IDs: **{len(houses_report['changedIds']):,}**",
            "",
            "## Quest-source inventory",
            "",
        ]
    )
    for quest_name, inventory in report["questInventory"].items():
        lines.append(
            f"- `{quest_name}`: Canary {inventory['canaryCount']} files; "
            f"Crystal {inventory['crystalCount']} files; "
            f"Crystal-only {len(inventory['onlyInCrystal'])}."
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "This report proves static differences between two exact snapshots. It does not "
            "prove Real Tibia runtime parity and does not authorize a whole-map replacement. "
            "The JSON report contains per-floor bounds, samples, sidecar hashes and quest inventories.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = compare_worlds()
    json_path = OUTPUT / "real-tibia-crystal-map-audit.json"
    markdown_path = OUTPUT / "real-tibia-crystal-map-audit.md"
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(markdown(report), encoding="utf-8")
    print("=== REAL_TIBIA_CRYSTAL_MAP_AUDIT_MARKDOWN ===")
    print(markdown_path.read_text(encoding="utf-8"))
    print("=== END_REAL_TIBIA_CRYSTAL_MAP_AUDIT ===")


if __name__ == "__main__":
    main()
