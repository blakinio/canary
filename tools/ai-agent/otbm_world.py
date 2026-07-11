from __future__ import annotations

import hashlib
import struct
import xml.etree.ElementTree as ET
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from otbm_binary import (
    OTBM_HOUSETILE,
    OTBM_TILE,
    OTBM_TILE_AREA,
    OTBM_TILE_ZONE,
    OTBM_TOWN,
    OTBM_TOWNS,
    OTBM_WAYPOINT,
    OTBM_WAYPOINTS,
    MappedFile,
    _read_string,
    _read_u16,
    _read_u32,
    _require,
    get_node_properties,
    iter_child_nodes,
    parse_header,
    parse_map_attributes,
    sha256_path,
)

WORLD_INDEX_FORMAT = "canary-otbm-world-index-v1"

COMPANION_SPECS = {
    "monster": ("monsterFile", "monster", "monsters"),
    "npc": ("npcFile", "npc", "npcs"),
    "house": ("houseFile", "house", "houses"),
    "zones": ("zoneFile", "zones", "zones"),
}


@dataclass
class IssueCollector:
    issues: list[dict[str, Any]] = field(default_factory=list)

    def add(self, severity: str, code: str, message: str, **details: Any) -> None:
        self.issues.append({"severity": severity, "code": code, "message": message, **details})

    def summary(self) -> dict[str, int]:
        counts = Counter(issue["severity"] for issue in self.issues)
        return {key: counts.get(key, 0) for key in ("error", "warning", "info")}


@dataclass(frozen=True)
class MapWorldData:
    towns: list[dict[str, Any]]
    waypoints: list[dict[str, Any]]
    house_ids: set[int]
    zone_ids: set[int]
    tile_areas: int
    tiles: int
    house_tiles: int
    zone_references: int


def _position(properties: bytes, offset: int) -> tuple[list[int], int]:
    x, offset = _read_u16(properties, offset)
    y, offset = _read_u16(properties, offset)
    _require(offset < len(properties), "Unexpected end of properties while reading Z coordinate")
    z = properties[offset]
    return [x, y, z], offset + 1


def _parse_towns(data: bytes | Any, node_start: int, issues: IssueCollector) -> list[dict[str, Any]]:
    towns: list[dict[str, Any]] = []
    ids: set[int] = set()
    names: set[str] = set()
    for child_start, _, child_type in iter_child_nodes(data, node_start):
        if child_type != OTBM_TOWN:
            issues.add("error", "unexpected_town_node", f"Unexpected node type {child_type} in towns node", offset=child_start)
            continue
        try:
            properties = get_node_properties(data, child_start)
            town_id, offset = _read_u32(properties, 0)
            name, offset = _read_string(properties, offset)
            temple, offset = _position(properties, offset)
            _require(offset == len(properties), "Town node contains trailing properties")
        except Exception as exc:
            issues.add("error", "invalid_town", str(exc), offset=child_start)
            continue
        if town_id in ids:
            issues.add("error", "duplicate_town_id", f"Town ID {town_id} is defined more than once", townId=town_id)
        if name in names:
            issues.add("warning", "duplicate_town_name", f"Town name {name!r} is defined more than once", townName=name)
        ids.add(town_id)
        names.add(name)
        towns.append({"id": town_id, "name": name, "templePosition": temple})
    return towns


def _parse_waypoints(data: bytes | Any, node_start: int, issues: IssueCollector) -> list[dict[str, Any]]:
    waypoints: list[dict[str, Any]] = []
    names: set[str] = set()
    for child_start, _, child_type in iter_child_nodes(data, node_start):
        if child_type != OTBM_WAYPOINT:
            issues.add("error", "unexpected_waypoint_node", f"Unexpected node type {child_type} in waypoints node", offset=child_start)
            continue
        try:
            properties = get_node_properties(data, child_start)
            name, offset = _read_string(properties, 0)
            position, offset = _position(properties, offset)
            _require(offset == len(properties), "Waypoint node contains trailing properties")
        except Exception as exc:
            issues.add("error", "invalid_waypoint", str(exc), offset=child_start)
            continue
        if name in names:
            issues.add("warning", "duplicate_waypoint_name", f"Waypoint {name!r} is defined more than once", waypoint=name)
        names.add(name)
        waypoints.append({"name": name, "position": position})
    return waypoints


def _parse_zone_node(properties: bytes, issues: IssueCollector, position: list[int]) -> tuple[set[int], int]:
    try:
        count, offset = _read_u16(properties, 0)
        zone_ids: set[int] = set()
        for _ in range(count):
            zone_id, offset = _read_u16(properties, offset)
            if zone_id == 0:
                issues.add("error", "zero_zone_id", "Map tile references zone ID 0", position=position)
            else:
                zone_ids.add(zone_id)
        _require(offset == len(properties), "Zone node contains trailing properties")
        return zone_ids, count
    except Exception as exc:
        issues.add("error", "invalid_tile_zone", str(exc), position=position)
        return set(), 0


def read_map_world(path: Path, issues: IssueCollector) -> tuple[dict[str, Any], MapWorldData]:
    towns: list[dict[str, Any]] = []
    waypoints: list[dict[str, Any]] = []
    house_ids: set[int] = set()
    zone_ids: set[int] = set()
    tile_areas = 0
    tiles = 0
    house_tiles = 0
    zone_references = 0
    with MappedFile(path) as mm:
        header = parse_header(mm)
        map_attributes = parse_map_attributes(get_node_properties(mm, header.map_data_start))
        for child_start, _, child_type in iter_child_nodes(mm, header.map_data_start):
            if child_type == OTBM_TOWNS:
                if towns:
                    issues.add("warning", "multiple_towns_nodes", "Map contains multiple towns nodes")
                towns.extend(_parse_towns(mm, child_start, issues))
                continue
            if child_type == OTBM_WAYPOINTS:
                if waypoints:
                    issues.add("warning", "multiple_waypoints_nodes", "Map contains multiple waypoints nodes")
                waypoints.extend(_parse_waypoints(mm, child_start, issues))
                continue
            if child_type != OTBM_TILE_AREA:
                continue
            tile_areas += 1
            area_properties = get_node_properties(mm, child_start)
            if len(area_properties) != 5:
                issues.add("error", "invalid_tile_area", f"Tile area has {len(area_properties)} property bytes", offset=child_start)
                continue
            base_x, base_y, base_z = struct.unpack("<HHB", area_properties)
            for tile_start, _, tile_type in iter_child_nodes(mm, child_start):
                if tile_type not in (OTBM_TILE, OTBM_HOUSETILE):
                    issues.add("error", "unexpected_tile_node", f"Unexpected node type {tile_type} in tile area", offset=tile_start)
                    continue
                tiles += 1
                tile_properties = get_node_properties(mm, tile_start)
                if len(tile_properties) < 2:
                    issues.add("error", "truncated_tile", "Tile has fewer than two coordinate bytes", offset=tile_start)
                    continue
                position = [base_x + tile_properties[0], base_y + tile_properties[1], base_z]
                if tile_type == OTBM_HOUSETILE:
                    house_tiles += 1
                    if len(tile_properties) < 6:
                        issues.add("error", "truncated_house_tile", "House tile is missing house ID", position=position)
                    else:
                        house_id = struct.unpack_from("<I", tile_properties, 2)[0]
                        if house_id == 0:
                            issues.add("error", "zero_house_id", "House tile references house ID 0", position=position)
                        else:
                            house_ids.add(house_id)
                for item_start, _, item_type in iter_child_nodes(mm, tile_start):
                    if item_type != OTBM_TILE_ZONE:
                        continue
                    found_ids, count = _parse_zone_node(get_node_properties(mm, item_start), issues, position)
                    zone_ids.update(found_ids)
                    zone_references += count
    metadata = {
        "identifierHex": header.identifier.hex(),
        "version": header.version,
        "width": header.width,
        "height": header.height,
        "itemsMajor": header.items_major,
        "itemsMinor": header.items_minor,
        "attributes": map_attributes,
    }
    return metadata, MapWorldData(
        towns=towns,
        waypoints=waypoints,
        house_ids=house_ids,
        zone_ids=zone_ids,
        tile_areas=tile_areas,
        tiles=tiles,
        house_tiles=house_tiles,
        zone_references=zone_references,
    )


def _xml_sha256(path: Path) -> str:
    return sha256_path(path)


def _int_attribute(element: ET.Element, name: str, default: int | None, issues: IssueCollector, location: str) -> int | None:
    value = element.attrib.get(name)
    if value is None or value == "":
        if default is None:
            issues.add("error", "missing_xml_attribute", f"Missing required attribute {name!r}", location=location)
        return default
    try:
        return int(value)
    except ValueError:
        issues.add("error", "invalid_xml_integer", f"Attribute {name!r} is not an integer: {value!r}", location=location)
        return default


def _read_xml_root(path: Path, expected_root: str, issues: IssueCollector) -> ET.Element | None:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        issues.add("error", "xml_parse_error", str(exc), path=str(path))
        return None
    if root.tag.rsplit("}", 1)[-1].lower() != expected_root:
        issues.add("error", "unexpected_xml_root", f"Expected root <{expected_root}>, found <{root.tag}>", path=str(path))
        return None
    return root


def _parse_houses(path: Path, town_ids: set[int], issues: IssueCollector) -> dict[str, Any]:
    root = _read_xml_root(path, "houses", issues)
    if root is None:
        return {"entries": [], "houseIds": []}
    entries: list[dict[str, Any]] = []
    ids: set[int] = set()
    client_ids: set[int] = set()
    for index, element in enumerate(root):
        location = f"{path.name}:house[{index}]"
        house_id = _int_attribute(element, "houseid", None, issues, location)
        if house_id is None:
            continue
        if house_id in ids:
            issues.add("error", "duplicate_house_id", f"House ID {house_id} appears more than once", path=str(path), houseId=house_id)
        ids.add(house_id)
        entry = [
            _int_attribute(element, "entryx", 0, issues, location),
            _int_attribute(element, "entryy", 0, issues, location),
            _int_attribute(element, "entryz", 0, issues, location),
        ]
        town_id = _int_attribute(element, "townid", 0, issues, location) or 0
        client_id = _int_attribute(element, "clientid", 0, issues, location) or 0
        if town_ids and town_id not in town_ids:
            issues.add("error", "unknown_house_town", f"House {house_id} references unknown town {town_id}", houseId=house_id, townId=town_id)
        if client_id and client_id in client_ids:
            issues.add("warning", "duplicate_house_client_id", f"House client ID {client_id} appears more than once", clientId=client_id)
        client_ids.add(client_id)
        entries.append(
            {
                "houseId": house_id,
                "name": element.attrib.get("name", ""),
                "entryPosition": entry,
                "rent": _int_attribute(element, "rent", 0, issues, location),
                "size": _int_attribute(element, "size", 0, issues, location),
                "townId": town_id,
                "clientId": client_id,
                "guildhall": element.attrib.get("guildhall", "false").lower() in {"1", "true", "yes"},
                "beds": _int_attribute(element, "beds", -1, issues, location),
            }
        )
    return {"entries": entries, "houseIds": sorted(ids)}


def _parse_spawns(path: Path, kind: str, issues: IssueCollector) -> dict[str, Any]:
    root_name = "monsters" if kind == "monster" else "npcs"
    root = _read_xml_root(path, root_name, issues)
    if root is None:
        return {"groups": [], "entities": []}
    groups: list[dict[str, Any]] = []
    entities: list[dict[str, Any]] = []
    names: Counter[str] = Counter()
    for group_index, spawn in enumerate(root):
        location = f"{path.name}:spawn[{group_index}]"
        center = [
            _int_attribute(spawn, "centerx", 0, issues, location) or 0,
            _int_attribute(spawn, "centery", 0, issues, location) or 0,
            _int_attribute(spawn, "centerz", 0, issues, location) or 0,
        ]
        radius = _int_attribute(spawn, "radius", -1, issues, location)
        group_entities = 0
        for child_index, child in enumerate(spawn):
            if child.tag.rsplit("}", 1)[-1].lower() != kind:
                continue
            child_location = f"{location}:{kind}[{child_index}]"
            name = child.attrib.get("name", "").strip()
            if not name:
                issues.add("error", "missing_spawn_name", f"{kind.title()} spawn has no name", location=child_location)
                continue
            x_offset = _int_attribute(child, "x", 0, issues, child_location) or 0
            y_offset = _int_attribute(child, "y", 0, issues, child_location) or 0
            position = [center[0] + x_offset, center[1] + y_offset, center[2]]
            if not (0 <= position[0] <= 65535 and 0 <= position[1] <= 65535 and 0 <= position[2] <= 15):
                issues.add("error", "spawn_position_out_of_range", f"{kind.title()} {name!r} resolves outside OTBM coordinates", position=position)
            spawntime = _int_attribute(child, "spawntime", 0, issues, child_location) or 0
            if kind == "npc" and not 1 <= spawntime <= 86400:
                issues.add("warning", "npc_spawntime_out_of_range", f"NPC {name!r} spawntime is outside Canary's 1..86400 second range", spawntime=spawntime)
            if kind == "monster" and spawntime < 0:
                issues.add("error", "negative_monster_spawntime", f"Monster {name!r} has negative spawntime", spawntime=spawntime)
            names[name.lower()] += 1
            entities.append(
                {
                    "name": name,
                    "position": position,
                    "centerPosition": center,
                    "offset": [x_offset, y_offset],
                    "direction": _int_attribute(child, "direction", 0, issues, child_location),
                    "spawntime": spawntime,
                    "weight": _int_attribute(child, "weight", 1, issues, child_location) if kind == "monster" else None,
                }
            )
            group_entities += 1
        if group_entities == 0:
            issues.add("warning", "empty_spawn_group", f"Spawn group at {center} has no valid {kind} entries", path=str(path))
        groups.append({"centerPosition": center, "radius": radius, "entityCount": group_entities})
    return {
        "groups": groups,
        "entities": entities,
        "names": [{"name": name, "count": count} for name, count in sorted(names.items())],
    }


def _parse_zones(path: Path, issues: IssueCollector) -> dict[str, Any]:
    root = _read_xml_root(path, "zones", issues)
    if root is None:
        return {"entries": [], "zoneIds": []}
    entries: list[dict[str, Any]] = []
    ids: set[int] = set()
    names: set[str] = set()
    for index, element in enumerate(root):
        location = f"{path.name}:zone[{index}]"
        name = element.attrib.get("name", "").strip()
        zone_id = _int_attribute(element, "zoneid", 0, issues, location) or 0
        if not name:
            issues.add("error", "missing_zone_name", "Zone has no name", location=location)
        if name == "default":
            issues.add("error", "reserved_zone_name", "Zone name 'default' is reserved", location=location)
        if name in names:
            issues.add("error", "duplicate_zone_name", f"Zone name {name!r} appears more than once", zoneName=name)
        if zone_id and zone_id in ids:
            issues.add("error", "duplicate_zone_id", f"Zone ID {zone_id} appears more than once", zoneId=zone_id)
        names.add(name)
        if zone_id:
            ids.add(zone_id)
        entries.append({"name": name, "zoneId": zone_id})
    return {"entries": entries, "zoneIds": sorted(ids)}


def _attribute_values(attributes: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for attribute in attributes:
        name = attribute.get("name")
        value = attribute.get("value")
        if isinstance(name, str) and isinstance(value, str):
            result[name] = value
    return result


def _companion_paths(map_path: Path, attributes: Iterable[Mapping[str, Any]], issues: IssueCollector) -> dict[str, dict[str, Any]]:
    values = _attribute_values(attributes)
    result: dict[str, dict[str, Any]] = {}
    for kind, (attribute_name, suffix, _) in COMPANION_SPECS.items():
        filename = values.get(attribute_name)
        source = "mapAttribute"
        if not filename:
            filename = f"{map_path.stem}-{suffix}.xml"
            source = "convention"
            issues.add("info", "guessed_companion_file", f"No {attribute_name} attribute; using {filename}", kind=kind)
        path = (map_path.resolve().parent / filename).resolve()
        result[kind] = {"path": str(path), "filename": filename, "source": source, "exists": path.is_file()}
    return result


def build_world_index(map_path: Path, *, include_entries: bool = True) -> dict[str, Any]:
    source = map_path.resolve()
    _require(source.is_file(), f"Map file does not exist: {source}")
    issues = IssueCollector()
    map_metadata, world = read_map_world(source, issues)
    town_ids = {entry["id"] for entry in world.towns}
    companion_paths = _companion_paths(source, map_metadata["attributes"], issues)
    companions: dict[str, Any] = {}

    for kind, path_data in companion_paths.items():
        path = Path(path_data["path"])
        payload: dict[str, Any] = dict(path_data)
        if not path.is_file():
            issues.add("error", "missing_companion_file", f"Referenced {kind} file does not exist", path=str(path), kind=kind)
            payload.update({"sha256": None, "summary": {}, "entries": []})
            companions[kind] = payload
            continue
        payload["sha256"] = _xml_sha256(path)
        if kind == "house":
            parsed = _parse_houses(path, town_ids, issues)
            entries = parsed["entries"]
            xml_ids = set(parsed["houseIds"])
            for house_id in sorted(world.house_ids - xml_ids):
                issues.add("error", "house_missing_from_xml", f"Map house ID {house_id} is missing from house XML", houseId=house_id)
            for house_id in sorted(xml_ids - world.house_ids):
                issues.add("warning", "house_missing_from_map", f"House XML ID {house_id} has no house tile in the map", houseId=house_id)
            summary = {"houseCount": len(entries), "mapHouseIdCount": len(world.house_ids)}
        elif kind in {"monster", "npc"}:
            parsed = _parse_spawns(path, kind, issues)
            entries = parsed["entities"]
            summary = {"groupCount": len(parsed["groups"]), "entityCount": len(entries), "uniqueNameCount": len(parsed["names"])}
            payload["groups"] = parsed["groups"] if include_entries else []
            payload["names"] = parsed["names"]
        else:
            parsed = _parse_zones(path, issues)
            entries = parsed["entries"]
            xml_ids = set(parsed["zoneIds"])
            for zone_id in sorted(world.zone_ids - xml_ids):
                issues.add("error", "zone_missing_from_xml", f"Map zone ID {zone_id} is missing from zones XML", zoneId=zone_id)
            for zone_id in sorted(xml_ids - world.zone_ids):
                issues.add("info", "zone_missing_from_map", f"Zones XML ID {zone_id} is not referenced by a map tile", zoneId=zone_id)
            summary = {"zoneCount": len(entries), "mapZoneIdCount": len(world.zone_ids)}
        payload["summary"] = summary
        payload["entries"] = entries if include_entries else []
        companions[kind] = payload

    summary = {
        "townCount": len(world.towns),
        "waypointCount": len(world.waypoints),
        "tileAreaCount": world.tile_areas,
        "tileCount": world.tiles,
        "houseTileCount": world.house_tiles,
        "mapHouseIdCount": len(world.house_ids),
        "mapZoneIdCount": len(world.zone_ids),
        "zoneReferenceCount": world.zone_references,
        "companionFilesPresent": sum(1 for data in companions.values() if data["exists"]),
        "companionFilesExpected": len(companions),
    }
    issue_summary = issues.summary()
    return {
        "format": WORLD_INDEX_FORMAT,
        "ok": issue_summary["error"] == 0,
        "source": {"path": str(source), "sha256": sha256_path(source), "fileSize": source.stat().st_size},
        "map": {
            **map_metadata,
            "towns": world.towns,
            "waypoints": world.waypoints,
            "houseIds": sorted(world.house_ids),
            "zoneIds": sorted(world.zone_ids),
        },
        "companions": companions,
        "summary": summary,
        "issueSummary": issue_summary,
        "issues": issues.issues,
    }
