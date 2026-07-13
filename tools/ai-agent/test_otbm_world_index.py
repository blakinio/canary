from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_world_index import (
    WORLD_INDEX_FORMAT,
    WORLD_QUERY_FORMAT,
    WorldIndex,
    WorldIndexError,
    build_world_index,
    index_summary,
    query_action,
    query_house_door,
    query_item,
    query_position,
    query_region,
    query_teleport_destination,
    query_unique,
)

NODE_ESCAPE = 0xFD
NODE_START = 0xFE
NODE_END = 0xFF
OTBM_MAP_DATA = 2
OTBM_TILE_AREA = 4
OTBM_TILE = 5
OTBM_ITEM = 6
OTBM_HOUSETILE = 14
ATTR_TILE_FLAGS = 3
ATTR_ACTION_ID = 4
ATTR_UNIQUE_ID = 5
ATTR_TELE_DEST = 8
ATTR_ITEM = 9
ATTR_HOUSEDOOR_ID = 14


def escape(data: bytes) -> bytes:
    out = bytearray()
    for value in data:
        if value in (NODE_ESCAPE, NODE_START, NODE_END):
            out.append(NODE_ESCAPE)
        out.append(value)
    return bytes(out)


def node(node_type: int, properties: bytes, children: list[bytes] | None = None) -> bytes:
    return bytes((NODE_START, node_type)) + escape(properties) + b"".join(children or []) + bytes((NODE_END,))


def attr_u16(attr: int, value: int) -> bytes:
    return bytes((attr,)) + struct.pack("<H", value)


def attr_u8(attr: int, value: int) -> bytes:
    return bytes((attr, value))


def attr_position(attr: int, value: tuple[int, int, int]) -> bytes:
    return bytes((attr,)) + struct.pack("<HHB", *value)


def item(item_id: int, attributes: bytes = b"", children: list[bytes] | None = None) -> bytes:
    return node(OTBM_ITEM, struct.pack("<H", item_id) + attributes, children)


def make_map(path: Path, *, duplicate_tile: bool = False, split_areas: bool = False) -> None:
    base_x, base_y, floor = 256, 512, 7
    nested = item(201, attr_u16(ATTR_UNIQUE_ID, 62135))
    container = item(200, attr_u16(ATTR_ACTION_ID, 8026), [nested])
    teleporter = item(202, attr_position(ATTR_TELE_DEST, (310, 620, 8)))
    door = item(203, attr_u8(ATTR_HOUSEDOOR_ID, 7))
    decoration = item(204)
    tile1_props = bytes((44, 88, ATTR_ITEM)) + struct.pack("<H", 100)
    tile1 = node(OTBM_TILE, tile1_props, [container, teleporter, door, decoration])

    tile2_props = (
        bytes((45, 88))
        + struct.pack("<I", 99)
        + bytes((ATTR_TILE_FLAGS,))
        + struct.pack("<I", 4)
        + bytes((ATTR_ITEM,))
        + struct.pack("<H", 100)
    )
    tile2 = node(OTBM_HOUSETILE, tile2_props, [item(205, attr_u16(ATTR_ACTION_ID, 8026))])
    children = [tile1, tile2]
    if duplicate_tile:
        children.append(tile1)
    if split_areas:
        areas = [
            node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, floor), [tile1]),
            node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, floor), [tile2]),
        ]
    else:
        areas = [node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, floor), children)]
    map_data = node(OTBM_MAP_DATA, b"", areas)
    root = node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


class WorldIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++") or shutil.which("g++")
        if compiler is None:
            raise unittest.SkipTest("A C++ compiler is required")
        cls.build = tempfile.TemporaryDirectory()
        cls.scanner = Path(cls.build.name) / "otbm_item_audit_scan"
        source = Path(__file__).with_name("otbm_item_audit_scan.cpp")
        completed = subprocess.run(
            [
                compiler,
                "-O2",
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                str(source),
                "-o",
                str(cls.scanner),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.map = self.root / "fixture.otbm"
        self.index = self.root / "world.widx"
        self.manifest = self.root / "world.json"
        make_map(self.map)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build_index(self, *, output: Path | None = None, manifest: Path | None = None, overwrite: bool = False):
        return build_world_index(
            map_path=self.map,
            scanner=self.scanner,
            output=output or self.index,
            manifest_output=manifest or self.manifest,
            overwrite=overwrite,
        )

    def test_scanner_legacy_contract_remains_compatible(self) -> None:
        output = self.root / "legacy.json"
        completed = subprocess.run(
            [str(self.scanner), str(self.map), str(output)], capture_output=True, text=True, check=False
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["format"], "canary-otbm-item-scan-v1")
        self.assertEqual(report["tileCount"], 2)
        self.assertEqual(report["totalPlacements"], 8)
        self.assertEqual(report["uniqueItemIds"], 7)
        self.assertEqual(len(report["mechanicPlacements"]), 5)

    def test_build_and_query_all_index_dimensions(self) -> None:
        manifest = self.build_index()
        self.assertEqual(manifest["format"], WORLD_INDEX_FORMAT)
        self.assertTrue(manifest["ok"])
        self.assertEqual(manifest["summary"]["tileCount"], 2)
        self.assertEqual(manifest["summary"]["totalPlacements"], 8)
        self.assertEqual(manifest["summary"]["mechanicPlacements"], 5)
        self.assertEqual(manifest["summary"]["tileAreaCount"], 1)
        self.assertEqual(manifest["summary"]["rawTileAreaNodes"], 1)
        self.assertEqual(manifest["summary"]["usedItemIds"], 7)
        self.assertEqual(len(manifest["source"]["sha256"]), 64)
        self.assertEqual(manifest["index"]["sha256"], hashlib.sha256(self.index.read_bytes()).hexdigest())

        item_result = query_item(self.index, 100)
        self.assertEqual(item_result["format"], WORLD_QUERY_FORMAT)
        self.assertEqual(item_result["totalCount"], 2)
        self.assertEqual([entry["position"] for entry in item_result["placements"]], [[300, 600, 7], [301, 600, 7]])

        action_result = query_action(self.index, 8026)
        self.assertEqual(action_result["totalCount"], 2)
        self.assertEqual([entry["itemId"] for entry in action_result["placements"]], [200, 205])

        unique_result = query_unique(self.index, 62135)
        self.assertEqual(unique_result["totalCount"], 1)
        self.assertEqual(unique_result["placements"][0]["itemDepth"], 1)

        door_result = query_house_door(self.index, 7)
        self.assertEqual(door_result["placements"][0]["itemId"], 203)

        destination = query_teleport_destination(self.index, (310, 620, 8))
        self.assertEqual(destination["placements"][0]["itemId"], 202)

        at = query_position(self.index, (301, 600, 7))
        self.assertEqual(at["tile"]["kind"], "house")
        self.assertEqual(at["tile"]["houseId"], 99)
        self.assertEqual(at["tile"]["flags"], 4)
        self.assertEqual([entry["itemId"] for entry in at["placements"]], [100, 205])

        region = query_region(self.index, (301, 600, 7), (300, 600, 7))
        self.assertEqual(region["totalCount"], 8)
        self.assertEqual(region["tileTotalCount"], 2)
        self.assertEqual([entry["kind"] for entry in region["tiles"]], ["tile", "house"])

    def test_pagination_is_bounded_and_deterministic(self) -> None:
        self.build_index()
        first = query_action(self.index, 8026, limit=1)
        second = query_action(self.index, 8026, limit=1, offset=1)
        self.assertTrue(first["truncated"])
        self.assertFalse(second["truncated"])
        self.assertEqual(first["placements"][0]["itemId"], 200)
        self.assertEqual(second["placements"][0]["itemId"], 205)
        with self.assertRaises(WorldIndexError):
            query_action(self.index, 8026, limit=10001)

    def test_summary_reads_binary_and_manifest_provenance(self) -> None:
        manifest = self.build_index()
        summary = index_summary(self.index, self.manifest)
        self.assertEqual(summary["summary"], manifest["summary"])
        self.assertEqual(summary["manifest"]["source"], manifest["source"])
        self.assertEqual(summary["otbm"]["version"], 4)
        self.assertEqual(summary["otbm"]["width"], 1024)

    def test_binary_output_is_deterministic(self) -> None:
        first_manifest = self.build_index()
        second_index = self.root / "second.widx"
        second_manifest_path = self.root / "second.json"
        second_manifest = self.build_index(output=second_index, manifest=second_manifest_path)
        self.assertEqual(first_manifest["index"]["sha256"], second_manifest["index"]["sha256"])
        self.assertEqual(self.index.read_bytes(), second_index.read_bytes())

    def test_repeated_raw_area_nodes_are_merged_into_one_query_area(self) -> None:
        make_map(self.map, split_areas=True)
        manifest = self.build_index()
        self.assertEqual(manifest["summary"]["tileAreaCount"], 1)
        self.assertEqual(manifest["summary"]["rawTileAreaNodes"], 2)
        self.assertEqual(query_position(self.index, (300, 600, 7))["tile"]["kind"], "tile")
        self.assertEqual(query_position(self.index, (301, 600, 7))["tile"]["kind"], "house")
        region = query_region(self.index, (300, 600, 7), (301, 600, 7))
        self.assertEqual(region["tileTotalCount"], 2)
        self.assertEqual(region["totalCount"], 8)

    def test_duplicate_tile_is_rejected_without_partial_output(self) -> None:
        make_map(self.map, duplicate_tile=True)
        with self.assertRaises(WorldIndexError):
            self.build_index()
        self.assertFalse(self.index.exists())
        self.assertFalse(self.manifest.exists())

    def test_existing_output_requires_explicit_overwrite(self) -> None:
        first = self.build_index()
        with self.assertRaises(WorldIndexError):
            self.build_index()
        second = self.build_index(overwrite=True)
        self.assertEqual(first["source"]["sha256"], second["source"]["sha256"])
        self.assertEqual(first["index"]["sha256"], second["index"]["sha256"])

    def test_corrupt_header_is_rejected(self) -> None:
        self.build_index()
        with self.index.open("r+b") as stream:
            stream.seek(0)
            stream.write(b"BROKEN!!")
        with self.assertRaises(WorldIndexError):
            WorldIndex(self.index)

    @unittest.skipIf(os.name == "nt", "symlink creation often requires elevated privileges on Windows")
    def test_symlink_output_is_rejected(self) -> None:
        target = self.root / "target.widx"
        target.write_bytes(b"")
        self.index.symlink_to(target)
        with self.assertRaises(WorldIndexError):
            self.build_index()


if __name__ == "__main__":
    unittest.main()
