from __future__ import annotations

import json
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
WORLD_DIR = Path("/mnt/data/otbm_world_impl")
STUB_DIR = MODULE_DIR / "stubs"
sys.path.insert(0, str(STUB_DIR))
sys.path.insert(1, str(MODULE_DIR))
sys.path.insert(2, str(WORLD_DIR))

from quest_map_validation import (
    EVIDENCE_FORMAT,
    VALIDATION_FORMAT,
    QuestMapValidationError,
    mask_lua_noncode,
    scan_quest_sources,
    validate_quest_evidence,
)
from otbm_world_index import build_world_index

NODE_ESCAPE = 0xFD
NODE_START = 0xFE
NODE_END = 0xFF
OTBM_MAP_DATA = 2
OTBM_TILE_AREA = 4
OTBM_TILE = 5
OTBM_ITEM = 6
ATTR_ITEM = 9
ATTR_ACTION_ID = 4
ATTR_UNIQUE_ID = 5
ATTR_TELE_DEST = 8
ATTR_HOUSEDOOR_ID = 14


def esc(data: bytes) -> bytes:
    out = bytearray()
    for value in data:
        if value in {NODE_ESCAPE, NODE_START, NODE_END}:
            out.append(NODE_ESCAPE)
        out.append(value)
    return bytes(out)


def node(node_type: int, properties: bytes, children: list[bytes] | None = None) -> bytes:
    return bytes((NODE_START, node_type)) + esc(properties) + b"".join(children or []) + bytes((NODE_END,))


def item(item_id: int, attrs: bytes = b"") -> bytes:
    return node(OTBM_ITEM, struct.pack("<H", item_id) + attrs)


def tile(offset_x: int, offset_y: int, inline: int, children: list[bytes]) -> bytes:
    return node(OTBM_TILE, bytes((offset_x, offset_y, ATTR_ITEM)) + struct.pack("<H", inline), children)


def make_map(path: Path) -> None:
    base = (256, 512, 7)
    t1 = tile(
        44,
        88,
        100,
        [
            item(200, bytes((ATTR_ACTION_ID,)) + struct.pack("<H", 8026)),
            item(201, bytes((ATTR_UNIQUE_ID,)) + struct.pack("<H", 62135)),
            item(202, bytes((ATTR_TELE_DEST,)) + struct.pack("<HHB", 310, 620, 8)),
            item(203, bytes((ATTR_HOUSEDOOR_ID, 7))),
        ],
    )
    t2 = tile(45, 88, 101, [item(7772)])
    area = node(OTBM_TILE_AREA, struct.pack("<HHB", *base), [t1, t2])
    map_data = node(OTBM_MAP_DATA, b"", [area])
    root = node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


def script_resolution(*entries: tuple[str, int, str]) -> dict:
    grouped = {"actionId": [], "uniqueId": []}
    for namespace, value, status in entries:
        grouped[namespace].append({"value": value, "runtimeStatus": status})
    return {"format": "canary-otbm-script-resolution-v1", "sources": {}, "identifiers": grouped}


class QuestMapValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = WORLD_DIR / "otbm_item_audit_scan"
        if not cls.scanner.is_file():
            raise unittest.SkipTest("compiled world-index scanner is unavailable")

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data/quests").mkdir(parents=True)
        self.map_path = self.root / "fixture.otbm"
        self.index_path = self.root / "fixture.widx"
        self.manifest_path = self.root / "fixture.json"
        make_map(self.map_path)
        build_world_index(
            map_path=self.map_path,
            scanner=self.scanner,
            output=self.index_path,
            manifest_output=self.manifest_path,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_lua(self, name: str, content: str) -> Path:
        path = self.root / "data/quests" / name
        path.write_text(content, encoding="utf-8")
        return path

    def scan(self, includes: list[str] | None = None, excludes: list[str] | None = None) -> dict:
        return scan_quest_sources(
            repository_root=self.root,
            source_roots=["data"],
            includes=includes or ["data/quests/*.lua"],
            excludes=excludes or [],
        )

    def test_masks_comments_and_strings_but_preserves_lines(self) -> None:
        text = "-- Position(1,2,3)\nlocal x = 'addItem(999)'\nlocal p = Position(300,600,7)\n"
        masked = mask_lua_noncode(text)
        self.assertEqual(masked.count("\n"), text.count("\n"))
        self.assertNotIn("Position(1,2,3)", masked)
        self.assertNotIn("addItem(999)", masked)
        self.assertIn("Position(300,600,7)", masked)

    def test_scans_static_registrations_items_positions_teleports_and_storages(self) -> None:
        self.write_lua(
            "quest.lua",
            """
local action = Action()
action:aid(8026)
action:register()
local reward = 7772
local exitPos = Position(310, 620, 8)
player:addItem(reward, 1)
player:removeItem(3031, 100)
player:teleportTo(exitPos)
if player:getStorageValue(Storage.Quest.Sample) < 1 then
  player:setStorageValue(Storage.Quest.Sample, 1)
end
""",
        )
        report = self.scan()
        self.assertEqual(report["format"], EVIDENCE_FORMAT)
        values = {(entry["kind"], json.dumps(entry["value"], sort_keys=True), entry["role"]) for entry in report["evidence"]}
        self.assertIn(("actionId", "8026", "registration"), values)
        self.assertIn(("itemId", "7772", "item-reward"), values)
        self.assertIn(("itemId", "3031", "item-consume"), values)
        self.assertIn(("teleportDestination", "[310, 620, 8]", "teleport-destination"), values)
        self.assertIn(("storage", '"Storage.Quest.Sample"', "storage-read"), values)
        self.assertIn(("storage", '"Storage.Quest.Sample"', "storage-write"), values)

    def test_ignores_fake_references_inside_comments_and_strings(self) -> None:
        self.write_lua(
            "fake.lua",
            """
-- player:addItem(9999, 1)
local message = "Position(1, 2, 3) player:removeItem(8888, 1)"
local p = Position(300, 600, 7)
""",
        )
        report = self.scan()
        item_values = {entry["value"] for entry in report["evidence"] if entry["kind"] == "itemId"}
        position_values = {tuple(entry["value"]) for entry in report["evidence"] if entry["kind"] == "position"}
        self.assertNotIn(9999, item_values)
        self.assertNotIn(8888, item_values)
        self.assertIn((300, 600, 7), position_values)

    def test_dynamic_references_remain_unresolved(self) -> None:
        self.write_lua(
            "dynamic.lua",
            """
local action = Action()
action:aid(config.action)
action:register()
player:addItem(config.reward, 1)
player:setStorageValue(config.storage, 1)
local p = Position(config.x, 600, 7)
""",
        )
        report = self.scan()
        kinds = {entry["kind"] for entry in report["unresolved"]}
        self.assertTrue({"actionId", "itemId", "storage", "position"}.issubset(kinds))

    def test_include_exclude_selection_and_determinism(self) -> None:
        self.write_lua("a.lua", "player:addItem(7772, 1)\n")
        self.write_lua("b.lua", "player:addItem(3031, 1)\n")
        first = self.scan(excludes=["**/b.lua"])
        second = self.scan(excludes=["**/b.lua"])
        self.assertEqual(first, second)
        self.assertEqual(first["summary"]["filesScanned"], 1)
        self.assertEqual({entry["value"] for entry in first["evidence"] if entry["kind"] == "itemId"}, {7772})

    def test_requires_explicit_include_glob(self) -> None:
        with self.assertRaises(QuestMapValidationError):
            scan_quest_sources(repository_root=self.root, source_roots=["data"], includes=[])

    def test_validation_classifies_confirmed_and_script_only(self) -> None:
        self.write_lua(
            "quest.lua",
            """
local action = Action()
action:aid(8026)
action:register()
player:addItem(7772, 1)
player:addItem(9999, 1)
local p = Position(300, 600, 7)
local missing = Position(400, 700, 7)
""",
        )
        evidence = self.scan()
        report = validate_quest_evidence(
            evidence_report=evidence,
            world_index=self.index_path,
            script_resolution=script_resolution(("actionId", 8026, "handled-directly")),
            sample_limit=2,
        )
        self.assertEqual(report["format"], VALIDATION_FORMAT)
        classification = {(entry["kind"], json.dumps(entry["value"])): entry["classification"] for entry in report["findings"]}
        self.assertEqual(classification[("actionId", "8026")], "confirmed")
        self.assertEqual(classification[("itemId", "7772")], "confirmed")
        self.assertEqual(classification[("itemId", "9999")], "script-only")
        self.assertEqual(classification[("position", "[400, 700, 7]")], "script-only")

    def test_validation_preserves_conflicting_script_resolution(self) -> None:
        self.write_lua("quest.lua", "local action=Action()\naction:aid(8026)\naction:register()\n")
        report = validate_quest_evidence(
            evidence_report=self.scan(),
            world_index=self.index_path,
            script_resolution=script_resolution(("actionId", 8026, "conflicting")),
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["byClassification"]["conflicting"], 1)

    def test_region_reports_unreferenced_map_mechanics_as_map_only(self) -> None:
        self.write_lua("quest.lua", "local action=Action()\naction:aid(8026)\naction:register()\n")
        report = validate_quest_evidence(
            evidence_report=self.scan(),
            world_index=self.index_path,
            script_resolution=script_resolution(("actionId", 8026, "handled-directly")),
            region=((300, 600, 7), (301, 600, 7)),
            sample_limit=1,
        )
        keys = {(entry["kind"], json.dumps(entry["value"])) for entry in report["mapOnlyRegionMechanics"]}
        self.assertIn(("uniqueId", "62135"), keys)
        self.assertIn(("teleportDestination", "[310, 620, 8]"), keys)
        self.assertNotIn(("actionId", "8026"), keys)

    def test_samples_are_bounded_but_counts_are_exact(self) -> None:
        self.write_lua("quest.lua", "player:addItem(7772, 1)\n")
        report = validate_quest_evidence(evidence_report=self.scan(), world_index=self.index_path, sample_limit=1)
        entry = next(item for item in report["findings"] if item["kind"] == "itemId")
        self.assertEqual(entry["map"]["count"], 1)
        self.assertLessEqual(len(entry["map"]["samples"]), 1)

    def test_storage_is_inventory_only_and_unresolved(self) -> None:
        self.write_lua("quest.lua", "player:getStorageValue(45001)\n")
        report = validate_quest_evidence(evidence_report=self.scan(), world_index=self.index_path)
        storage = next(item for item in report["findings"] if item["kind"] == "storage")
        self.assertEqual(storage["classification"], "unresolved")
        self.assertIn("later phase", storage["reason"])

    def test_invalid_formats_and_region_limits_fail(self) -> None:
        with self.assertRaises(QuestMapValidationError):
            validate_quest_evidence(evidence_report={"format": "wrong"}, world_index=self.index_path)
        self.write_lua("quest.lua", "player:addItem(7772, 1)\n")
        with self.assertRaises(QuestMapValidationError):
            validate_quest_evidence(
                evidence_report=self.scan(),
                world_index=self.index_path,
                region=((0, 0, 0), (1000, 1000, 1)),
            )


if __name__ == "__main__":
    unittest.main()
