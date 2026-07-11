from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from otbm_binary import OTBMError, _require, sha256_path
from otbm_world import (
    COMPANION_SPECS,
    IssueCollector,
    _parse_houses,
    _parse_spawns,
    _parse_zones,
    read_map_world,
)

WORLD_PATCH_FORMAT = "canary-otbm-world-patch-v1"
WORLD_PATCH_REPORT_FORMAT = "canary-otbm-world-patch-report-v1"
ROOT_NAMES = {"monster": "monsters", "npc": "npcs", "house": "houses", "zones": "zones"}
MAX_OPERATIONS = 10000


@dataclass
class CompanionDocument:
    kind: str
    filename: str
    source_path: Path
    source_sha256: str | None
    tree: ET.ElementTree


@dataclass
class WorldPatchPlan:
    map_path: Path
    patch: dict[str, Any]
    documents: dict[str, CompanionDocument]
    operations: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.conflicts


def _local_name(tag: Any) -> str:
    return str(tag).rsplit("}", 1)[-1].lower()


def _canonical_element_bytes(element: ET.Element) -> bytes:
    clone = copy.deepcopy(element)
    for current in clone.iter():
        if isinstance(current.tag, str):
            attributes = sorted(current.attrib.items())
            current.attrib.clear()
            current.attrib.update(attributes)
        if current.text is not None and not current.text.strip():
            current.text = None
        if current.tail is not None and not current.tail.strip():
            current.tail = None
    return ET.tostring(clone, encoding="utf-8", short_empty_elements=True)


def element_hash(element: ET.Element) -> str:
    return hashlib.sha256(_canonical_element_bytes(element)).hexdigest()


def _safe_relative_filename(filename: str) -> Path:
    relative = Path(filename)
    _require(not relative.is_absolute(), f"Absolute companion path is not allowed for authoring: {filename}")
    _require(relative.parts and all(part not in {"", ".", ".."} for part in relative.parts), f"Unsafe companion path: {filename}")
    return relative


def _load_tree(path: Path, root_name: str) -> ET.ElementTree:
    if not path.is_file():
        return ET.ElementTree(ET.Element(root_name))
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(path, parser=parser)
    _require(_local_name(tree.getroot().tag) == root_name, f"Expected <{root_name}> in {path}")
    return tree


def _map_companion_files(map_path: Path) -> tuple[dict[str, Any], Any, dict[str, tuple[str, Path]]]:
    issues = IssueCollector()
    metadata, world = read_map_world(map_path, issues)
    errors = [issue for issue in issues.issues if issue["severity"] == "error"]
    _require(not errors, f"Cannot author companions for an invalid OTBM map: {errors[:3]}")
    values = {entry.get("name"): entry.get("value") for entry in metadata["attributes"]}
    files: dict[str, tuple[str, Path]] = {}
    for kind, (attribute_name, suffix, _) in COMPANION_SPECS.items():
        value = values.get(attribute_name)
        filename = value if isinstance(value, str) and value else f"{map_path.stem}-{suffix}.xml"
        relative = _safe_relative_filename(filename)
        files[kind] = (filename, (map_path.parent / relative).resolve())
    return metadata, world, files


def _inventory_entry(element: ET.Element, **identity: Any) -> dict[str, Any]:
    return {**identity, "entryHash": element_hash(element)}


def build_world_patch_template(map_path: Path) -> dict[str, Any]:
    source = map_path.resolve()
    _require(source.is_file(), f"Map file does not exist: {source}")
    _, _, files = _map_companion_files(source)
    base_files: dict[str, Any] = {}
    inventory: dict[str, list[dict[str, Any]]] = {kind: [] for kind in ROOT_NAMES}

    for kind, (filename, path) in files.items():
        tree = _load_tree(path, ROOT_NAMES[kind])
        base_files[kind] = {
            "filename": filename,
            "sha256": sha256_path(path) if path.is_file() else None,
        }
        if kind == "house":
            for element in tree.getroot():
                if _local_name(element.tag) != "house":
                    continue
                try:
                    house_id = int(element.attrib.get("houseid", ""))
                except ValueError:
                    continue
                inventory[kind].append(_inventory_entry(element, houseId=house_id, name=element.attrib.get("name", "")))
        elif kind == "zones":
            for element in tree.getroot():
                if _local_name(element.tag) != "zone":
                    continue
                try:
                    zone_id = int(element.attrib.get("zoneid", "0"))
                except ValueError:
                    zone_id = 0
                inventory[kind].append(_inventory_entry(element, zoneId=zone_id, name=element.attrib.get("name", "")))
        else:
            for index, element in enumerate(tree.getroot()):
                if _local_name(element.tag) != "spawn":
                    continue
                center = [int(element.attrib.get(name, "0")) for name in ("centerx", "centery", "centerz")]
                inventory[kind].append(
                    _inventory_entry(element, groupIndex=index, centerPosition=center, radius=int(element.attrib.get("radius", "-1")))
                )

    return {
        "format": WORLD_PATCH_FORMAT,
        "name": f"world-patch-{source.stem}",
        "base": {
            "map": {"filename": source.name, "sha256": sha256_path(source)},
            "files": base_files,
        },
        "inventory": inventory,
        "operations": [],
    }


def _issue(path: str, message: str, code: str) -> dict[str, str]:
    return {"path": path, "message": message, "code": code, "severity": "error"}


def _valid_sha(value: Any, allow_none: bool = False) -> bool:
    if value is None:
        return allow_none
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdefABCDEF" for character in value)


def _valid_position(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(part, int) and not isinstance(part, bool) for part in value)
        and 0 <= value[0] <= 65535
        and 0 <= value[1] <= 65535
        and 0 <= value[2] <= 15
    )


def validate_world_patch(payload: Any) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if not isinstance(payload, dict):
        return {"format": "canary-otbm-world-patch-validation-v1", "ok": False, "issues": [_issue("$", "must be an object", "root_type")]}
    if payload.get("format") != WORLD_PATCH_FORMAT:
        issues.append(_issue("$.format", f"must equal {WORLD_PATCH_FORMAT}", "format"))
    base = payload.get("base")
    if not isinstance(base, dict):
        issues.append(_issue("$.base", "must be an object", "base_type"))
    else:
        map_base = base.get("map")
        if not isinstance(map_base, dict) or not _valid_sha(map_base.get("sha256")):
            issues.append(_issue("$.base.map.sha256", "must be a SHA-256 string", "sha256"))
        files = base.get("files")
        if not isinstance(files, dict):
            issues.append(_issue("$.base.files", "must be an object", "files_type"))
        else:
            for kind in ROOT_NAMES:
                entry = files.get(kind)
                if not isinstance(entry, dict):
                    issues.append(_issue(f"$.base.files.{kind}", "must be an object", "file_base"))
                    continue
                if not isinstance(entry.get("filename"), str) or not entry["filename"]:
                    issues.append(_issue(f"$.base.files.{kind}.filename", "must be a non-empty string", "filename"))
                if not _valid_sha(entry.get("sha256"), allow_none=True):
                    issues.append(_issue(f"$.base.files.{kind}.sha256", "must be SHA-256 or null", "sha256"))

    operations = payload.get("operations")
    if not isinstance(operations, list):
        issues.append(_issue("$.operations", "must be an array", "operations_type"))
        operations = []
    if len(operations) > MAX_OPERATIONS:
        issues.append(_issue("$.operations", f"must contain at most {MAX_OPERATIONS} operations", "operation_limit"))

    supported = {
        "upsert_house",
        "remove_house",
        "upsert_zone",
        "remove_zone",
        "add_spawn_group",
        "replace_spawn_group",
        "remove_spawn_group",
    }
    for index, operation in enumerate(operations):
        path = f"$.operations[{index}]"
        if not isinstance(operation, dict):
            issues.append(_issue(path, "must be an object", "operation_type"))
            continue
        op = operation.get("op")
        if op not in supported:
            issues.append(_issue(f"{path}.op", f"must be one of {sorted(supported)}", "operation_name"))
            continue
        if op in {"upsert_house", "remove_house", "upsert_zone", "remove_zone", "replace_spawn_group", "remove_spawn_group"}:
            if "expectedEntryHash" not in operation or not _valid_sha(operation.get("expectedEntryHash"), allow_none=op.startswith("upsert_")):
                issues.append(_issue(f"{path}.expectedEntryHash", "must be SHA-256; upsert may use null only when adding", "precondition"))
        if op == "upsert_house":
            house = operation.get("house")
            if not isinstance(house, dict):
                issues.append(_issue(f"{path}.house", "must be an object", "house_type"))
            else:
                for field in ("houseId", "name", "entryPosition", "rent", "size", "townId", "clientId"):
                    if field not in house:
                        issues.append(_issue(f"{path}.house.{field}", "is required", "required"))
                if "entryPosition" in house and not _valid_position(house["entryPosition"]):
                    issues.append(_issue(f"{path}.house.entryPosition", "must be [x,y,z] in OTBM range", "position"))
        elif op == "remove_house":
            if not isinstance(operation.get("houseId"), int):
                issues.append(_issue(f"{path}.houseId", "must be an integer", "house_id"))
        elif op == "upsert_zone":
            zone = operation.get("zone")
            if not isinstance(zone, dict) or not isinstance(zone.get("zoneId"), int) or not isinstance(zone.get("name"), str):
                issues.append(_issue(f"{path}.zone", "requires integer zoneId and string name", "zone_type"))
        elif op == "remove_zone":
            if not isinstance(operation.get("zoneId"), int):
                issues.append(_issue(f"{path}.zoneId", "must be an integer", "zone_id"))
        else:
            kind = operation.get("kind")
            if kind not in {"monster", "npc"}:
                issues.append(_issue(f"{path}.kind", "must be monster or npc", "spawn_kind"))
            if op in {"replace_spawn_group", "remove_spawn_group"} and (not isinstance(operation.get("groupIndex"), int) or operation["groupIndex"] < 0):
                issues.append(_issue(f"{path}.groupIndex", "must be a non-negative integer", "group_index"))
            if op in {"add_spawn_group", "replace_spawn_group"}:
                group = operation.get("group")
                if not isinstance(group, dict):
                    issues.append(_issue(f"{path}.group", "must be an object", "group_type"))
                else:
                    if not _valid_position(group.get("centerPosition")):
                        issues.append(_issue(f"{path}.group.centerPosition", "must be [x,y,z] in OTBM range", "position"))
                    if not isinstance(group.get("entities"), list) or not group["entities"]:
                        issues.append(_issue(f"{path}.group.entities", "must be a non-empty array", "entities"))
    return {
        "format": "canary-otbm-world-patch-validation-v1",
        "ok": not issues,
        "operationCount": len(operations),
        "issues": issues,
    }


def load_world_patch(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation = validate_world_patch(payload)
    _require(validation["ok"], f"Invalid world patch: {validation['issues'][:5]}")
    return payload


def _find_by_integer(root: ET.Element, tag: str, attribute: str, value: int) -> list[ET.Element]:
    result: list[ET.Element] = []
    for element in root:
        if _local_name(element.tag) != tag:
            continue
        try:
            current = int(element.attrib.get(attribute, ""))
        except ValueError:
            continue
        if current == value:
            result.append(element)
    return result


def _set_or_remove(element: ET.Element, name: str, value: Any) -> None:
    if value is None:
        element.attrib.pop(name, None)
    elif isinstance(value, bool):
        element.set(name, "true" if value else "false")
    else:
        element.set(name, str(value))


def _apply_house(root: ET.Element, operation: dict[str, Any]) -> None:
    house = operation["house"]
    house_id = int(house["houseId"])
    matches = _find_by_integer(root, "house", "houseid", house_id)
    _require(len(matches) <= 1, f"House ID {house_id} appears more than once")
    existing = matches[0] if matches else None
    expected = operation.get("expectedEntryHash")
    if existing is None:
        _require(expected is None, f"House {house_id} does not exist but expectedEntryHash was supplied")
        existing = ET.SubElement(root, "house")
    else:
        _require(expected == element_hash(existing), f"House {house_id} changed since the patch was prepared")
    position = house["entryPosition"]
    values = {
        "houseid": house_id,
        "name": house["name"],
        "entryx": position[0],
        "entryy": position[1],
        "entryz": position[2],
        "rent": house["rent"],
        "size": house["size"],
        "townid": house["townId"],
        "clientid": house["clientId"],
        "guildhall": house.get("guildhall"),
        "beds": house.get("beds"),
    }
    for name, value in values.items():
        _set_or_remove(existing, name, value)


def _remove_house(root: ET.Element, operation: dict[str, Any]) -> None:
    house_id = int(operation["houseId"])
    matches = _find_by_integer(root, "house", "houseid", house_id)
    _require(len(matches) == 1, f"Expected exactly one house {house_id}, found {len(matches)}")
    _require(operation["expectedEntryHash"] == element_hash(matches[0]), f"House {house_id} changed since the patch was prepared")
    root.remove(matches[0])


def _apply_zone(root: ET.Element, operation: dict[str, Any]) -> None:
    zone = operation["zone"]
    zone_id = int(zone["zoneId"])
    matches = _find_by_integer(root, "zone", "zoneid", zone_id)
    _require(len(matches) <= 1, f"Zone ID {zone_id} appears more than once")
    existing = matches[0] if matches else None
    expected = operation.get("expectedEntryHash")
    if existing is None:
        _require(expected is None, f"Zone {zone_id} does not exist but expectedEntryHash was supplied")
        existing = ET.SubElement(root, "zone")
    else:
        _require(expected == element_hash(existing), f"Zone {zone_id} changed since the patch was prepared")
    existing.set("zoneid", str(zone_id))
    existing.set("name", str(zone["name"]))


def _remove_zone(root: ET.Element, operation: dict[str, Any]) -> None:
    zone_id = int(operation["zoneId"])
    matches = _find_by_integer(root, "zone", "zoneid", zone_id)
    _require(len(matches) == 1, f"Expected exactly one zone {zone_id}, found {len(matches)}")
    _require(operation["expectedEntryHash"] == element_hash(matches[0]), f"Zone {zone_id} changed since the patch was prepared")
    root.remove(matches[0])


def _spawn_group_element(kind: str, group: dict[str, Any]) -> ET.Element:
    center = group["centerPosition"]
    spawn = ET.Element(
        "spawn",
        {
            "centerx": str(center[0]),
            "centery": str(center[1]),
            "centerz": str(center[2]),
            "radius": str(group.get("radius", -1)),
        },
    )
    for entity in group["entities"]:
        _require(isinstance(entity, dict), "Spawn entity must be an object")
        name = str(entity.get("name", "")).strip()
        _require(name, "Spawn entity requires a name")
        offset = entity.get("offset", [0, 0])
        _require(isinstance(offset, list) and len(offset) == 2 and all(isinstance(value, int) for value in offset), "Spawn offset must be [x,y]")
        attributes = {
            "name": name,
            "x": str(offset[0]),
            "y": str(offset[1]),
            "spawntime": str(int(entity.get("spawntime", 0))),
        }
        if entity.get("direction") is not None:
            attributes["direction"] = str(int(entity["direction"]))
        if kind == "monster" and entity.get("weight") is not None:
            attributes["weight"] = str(int(entity["weight"]))
        ET.SubElement(spawn, kind, attributes)
    return spawn


def _spawn_elements(root: ET.Element) -> list[ET.Element]:
    return [element for element in root if _local_name(element.tag) == "spawn"]


def _apply_spawn(root: ET.Element, operation: dict[str, Any]) -> None:
    op = operation["op"]
    if op == "add_spawn_group":
        root.append(_spawn_group_element(operation["kind"], operation["group"]))
        return
    index = int(operation["groupIndex"])
    groups = _spawn_elements(root)
    _require(index < len(groups), f"Spawn group index {index} does not exist")
    current = groups[index]
    _require(operation["expectedEntryHash"] == element_hash(current), f"Spawn group {index} changed since the patch was prepared")
    if op == "remove_spawn_group":
        root.remove(current)
        return
    replacement = _spawn_group_element(operation["kind"], operation["group"])
    child_index = list(root).index(current)
    root.remove(current)
    root.insert(child_index, replacement)


def plan_world_patch(map_path: Path, patch: dict[str, Any]) -> WorldPatchPlan:
    source = map_path.resolve()
    _require(source.is_file(), f"Map file does not exist: {source}")
    validation = validate_world_patch(patch)
    _require(validation["ok"], f"Invalid world patch: {validation['issues'][:5]}")
    _, _, files = _map_companion_files(source)
    conflicts: list[dict[str, Any]] = []
    warnings: list[str] = []
    documents: dict[str, CompanionDocument] = {}

    expected_map_sha = patch["base"]["map"]["sha256"]
    actual_map_sha = sha256_path(source)
    if expected_map_sha != actual_map_sha:
        conflicts.append({"type": "mapHashMismatch", "expected": expected_map_sha, "actual": actual_map_sha})

    for kind, (filename, path) in files.items():
        expected_file = patch["base"]["files"][kind]
        if expected_file["filename"] != filename:
            conflicts.append({"type": "filenameMismatch", "kind": kind, "expected": expected_file["filename"], "actual": filename})
        actual_sha = sha256_path(path) if path.is_file() else None
        if expected_file["sha256"] != actual_sha:
            conflicts.append({"type": "fileHashMismatch", "kind": kind, "expected": expected_file["sha256"], "actual": actual_sha})
        documents[kind] = CompanionDocument(kind, filename, path, actual_sha, _load_tree(path, ROOT_NAMES[kind]))

    operation_results: list[dict[str, Any]] = []
    if not conflicts:
        for index, operation in enumerate(patch["operations"]):
            result = {"index": index, "op": operation["op"], "status": "planned"}
            try:
                op = operation["op"]
                if op == "upsert_house":
                    _apply_house(documents["house"].tree.getroot(), operation)
                elif op == "remove_house":
                    _remove_house(documents["house"].tree.getroot(), operation)
                elif op == "upsert_zone":
                    _apply_zone(documents["zones"].tree.getroot(), operation)
                elif op == "remove_zone":
                    _remove_zone(documents["zones"].tree.getroot(), operation)
                else:
                    _apply_spawn(documents[operation["kind"]].tree.getroot(), operation)
            except (OTBMError, KeyError, TypeError, ValueError) as exc:
                result["status"] = "conflict"
                result["message"] = str(exc)
                conflicts.append({"type": "operationConflict", **result})
            operation_results.append(result)
    return WorldPatchPlan(source, patch, documents, operation_results, conflicts, warnings)


def _write_tree(tree: ET.ElementTree, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clone = copy.deepcopy(tree)
    ET.indent(clone, space="  ")
    clone.write(path, encoding="utf-8", xml_declaration=True, short_empty_elements=True)


def _stage_documents(plan: WorldPatchPlan, stage: Path) -> dict[str, Path]:
    staged: dict[str, Path] = {}
    for kind, document in plan.documents.items():
        relative = _safe_relative_filename(document.filename)
        destination = (stage / relative).resolve()
        _require(destination.is_relative_to(stage.resolve()), f"Companion output escapes staging directory: {document.filename}")
        _write_tree(document.tree, destination)
        staged[kind] = destination
    return staged


def _validate_staged_package(map_path: Path, files: dict[str, Path]) -> dict[str, Any]:
    issues = IssueCollector()
    metadata, world = read_map_world(map_path, issues)
    town_ids = {entry["id"] for entry in world.towns}
    houses = _parse_houses(files["house"], town_ids, issues)
    monsters = _parse_spawns(files["monster"], "monster", issues)
    npcs = _parse_spawns(files["npc"], "npc", issues)
    zones = _parse_zones(files["zones"], issues)
    house_xml_ids = set(houses["houseIds"])
    zone_xml_ids = set(zones["zoneIds"])
    for house_id in sorted(world.house_ids - house_xml_ids):
        issues.add("error", "house_missing_from_xml", f"Map house ID {house_id} is missing from staged house XML", houseId=house_id)
    for house_id in sorted(house_xml_ids - world.house_ids):
        issues.add("warning", "house_missing_from_map", f"Staged house XML ID {house_id} has no house tile in the map", houseId=house_id)
    for zone_id in sorted(world.zone_ids - zone_xml_ids):
        issues.add("error", "zone_missing_from_xml", f"Map zone ID {zone_id} is missing from staged zones XML", zoneId=zone_id)
    summary = issues.summary()
    return {
        "ok": summary["error"] == 0,
        "issueSummary": summary,
        "issues": issues.issues,
        "map": {"townCount": len(world.towns), "houseIdCount": len(world.house_ids), "zoneIdCount": len(world.zone_ids)},
        "companions": {
            "houseCount": len(houses["entries"]),
            "zoneCount": len(zones["entries"]),
            "monsterGroupCount": len(monsters["groups"]),
            "monsterCount": len(monsters["entities"]),
            "npcGroupCount": len(npcs["groups"]),
            "npcCount": len(npcs["entities"]),
        },
        "mapMetadata": metadata,
    }


def execute_world_patch(
    plan: WorldPatchPlan,
    *,
    output_dir: Path | None,
    write: bool,
    overwrite: bool,
) -> dict[str, Any]:
    validation: dict[str, Any] | None = None
    output_files: dict[str, Any] = {}
    backup_dir: Path | None = None
    written = False

    if plan.ok:
        with tempfile.TemporaryDirectory(prefix="canary-world-patch-") as temp_dir:
            stage = Path(temp_dir).resolve()
            staged = _stage_documents(plan, stage)
            validation = _validate_staged_package(plan.map_path, staged)
            if validation["ok"] and write:
                _require(output_dir is not None, "output_dir is required when write=True")
                destination = output_dir.resolve()
                _require(destination != plan.map_path.parent.resolve(), "Output directory must differ from the source map directory")
                destination.parent.mkdir(parents=True, exist_ok=True)
                publish_stage = destination.parent / f".{destination.name}.staging-{os.getpid()}"
                if publish_stage.exists():
                    shutil.rmtree(publish_stage)
                shutil.copytree(stage, publish_stage)
                if destination.exists():
                    _require(overwrite, f"Output directory already exists: {destination}; use --overwrite")
                    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                    backup_dir = destination.with_name(f"{destination.name}.bak.{timestamp}")
                    _require(not backup_dir.exists(), f"Backup directory already exists: {backup_dir}")
                    os.replace(destination, backup_dir)
                os.replace(publish_stage, destination)
                written = True
                for kind, document in plan.documents.items():
                    path = destination / _safe_relative_filename(document.filename)
                    output_files[kind] = {"path": str(path), "sha256": sha256_path(path)}
            else:
                for kind, path in staged.items():
                    output_files[kind] = {"path": None, "sha256": sha256_path(path)}

    ok = plan.ok and validation is not None and validation["ok"]
    return {
        "format": WORLD_PATCH_REPORT_FORMAT,
        "ok": ok,
        "mode": "write" if written else "dry-run",
        "map": {"path": str(plan.map_path), "sha256": sha256_path(plan.map_path)},
        "outputDirectory": str(output_dir.resolve()) if output_dir else None,
        "backupDirectory": str(backup_dir) if backup_dir else None,
        "warnings": plan.warnings,
        "conflicts": plan.conflicts,
        "operations": plan.operations,
        "validation": validation,
        "files": output_files,
    }
