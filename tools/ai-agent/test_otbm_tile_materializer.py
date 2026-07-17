from __future__ import annotations

import json
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_semantic_diff_types import sha256_path
from otbm_tile_materializer import (
    APPROVAL_FORMAT,
    RESULT_FORMAT,
    TILE_SPAN_FORMAT,
    TileMaterializerError,
    _canonical_tile,
    materialize_tile_replacements,
    scan_tile_spans,
)
from otbm_world_index import WorldIndex, build_world_index
from test_otbm_area_materializer import make_area_map
from test_otbm_world_index import ATTR_ITEM, OTBM_MAP_DATA, OTBM_TILE_AREA, node

OTBM_HOUSETILE = 14


def pin(path: Path) -> dict[str, object]:
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


def make_house_map(path: Path, *, x: int, y: int, z: int = 7, house_id: int = 42, ground: int = 100) -> None:
    base_x = x & 0xFF00
    base_y = y & 0xFF00
    properties = bytes((x - base_x, y - base_y)) + struct.pack("<I", house_id)
    properties += bytes((ATTR_ITEM,)) + struct.pack("<H", ground)
    tile = node(OTBM_HOUSETILE, properties, [])
    area = node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, z), [tile])
    map_data = node(OTBM_MAP_DATA, b"", [area])
    root = node(0, struct.pack("<IHHII", 4, 2048, 2048, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


class TileMaterializerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++") or shutil.which("g++")
        if compiler is None:
            raise unittest.SkipTest("A C++ compiler is required")
        cls.compiler_temp = tempfile.TemporaryDirectory()
        cls.scanner = Path(cls.compiler_temp.name) / "otbm_area_materializer_scan"
        source = Path(__file__).with_name("otbm_area_materializer_scan.cpp")
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
        cls.compiler_temp.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.current = self.root / "current.otbm"
        self.donor = self.root / "donor.otbm"
        self.current_index = self.root / "current.widx"
        self.current_manifest = self.root / "current.widx.json"
        self.donor_index = self.root / "donor.widx"
        self.donor_manifest = self.root / "donor.widx.json"
        self.approval_path = self.root / "approval.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def area(tiles: list[dict[str, object]]) -> dict[str, object]:
        return {"baseX": 256, "baseY": 512, "z": 7, "tiles": tiles}

    @staticmethod
    def tile(
        x: int,
        *,
        ground: int = 100,
        item_id: int | None = None,
        action: int | None = None,
        extra_items: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        items: list[dict[str, object]] = []
        if item_id is not None:
            child: dict[str, object] = {"id": item_id}
            if action is not None:
                child["action"] = action
            items.append(child)
        items.extend(extra_items or [])
        return {"x": x, "y": 600, "ground": ground, "items": items}

    def build_indexes(self) -> None:
        build_world_index(
            map_path=self.current,
            scanner=self.scanner,
            output=self.current_index,
            manifest_output=self.current_manifest,
        )
        build_world_index(
            map_path=self.donor,
            scanner=self.scanner,
            output=self.donor_index,
            manifest_output=self.donor_manifest,
        )

    def span_reports(self) -> tuple[dict[str, object], dict[str, object]]:
        workspace = self.root / "span-workspace"
        workspace.mkdir(exist_ok=True)
        current = scan_tile_spans(
            map_path=self.current,
            scanner=self.scanner,
            workspace=workspace,
            role="current",
        )
        donor = scan_tile_spans(
            map_path=self.donor,
            scanner=self.scanner,
            workspace=workspace,
            role="donor",
        )
        return current, donor

    def write_approval(self, positions: list[tuple[int, int, int]]) -> dict[str, object]:
        current_report, donor_report = self.span_reports()
        current_by_position = {
            (int(entry["x"]), int(entry["y"]), int(entry["z"])): entry
            for entry in current_report["tiles"]  # type: ignore[index]
        }
        donor_by_position = {
            (int(entry["x"]), int(entry["y"]), int(entry["z"])): entry
            for entry in donor_report["tiles"]  # type: ignore[index]
        }
        selections: list[dict[str, object]] = []
        with WorldIndex(self.current_index) as current_index, WorldIndex(self.donor_index) as donor_index:
            for position in positions:
                current_span = current_by_position[position]
                donor_span = donor_by_position[position]
                current_canonical, _ = _canonical_tile(current_index, position)
                donor_canonical, _ = _canonical_tile(donor_index, position)
                selections.append(
                    {
                        "position": list(position),
                        "areaKey": [position[0] & 0xFF00, position[1] & 0xFF00, position[2]],
                        "current": {
                            "rawSha256": current_span["sha256"],
                            "rawByteLength": current_span["byteLength"],
                            "nodeType": current_span["nodeType"],
                            "canonicalSha256": current_canonical,
                        },
                        "donor": {
                            "rawSha256": donor_span["sha256"],
                            "rawByteLength": donor_span["byteLength"],
                            "nodeType": donor_span["nodeType"],
                            "canonicalSha256": donor_canonical,
                        },
                    }
                )
        approval: dict[str, object] = {
            "format": APPROVAL_FORMAT,
            "schemaVersion": 1,
            "decision": "approved",
            "rationale": "Synthetic integration-test approval for exact same-coordinate complete raw tile replacement.",
            "provenance": {
                "current": {
                    "sourceMap": pin(self.current),
                    "worldIndex": pin(self.current_index),
                    "manifest": pin(self.current_manifest),
                },
                "donor": {
                    "sourceMap": pin(self.donor),
                    "worldIndex": pin(self.donor_index),
                    "manifest": pin(self.donor_manifest),
                },
            },
            "selections": selections,
        }
        self.approval_path.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return approval

    def materialize(self, output_name: str = "output.otbm", evidence_name: str = "evidence") -> dict[str, object]:
        return materialize_tile_replacements(
            artifact_root=self.root,
            current_map_path=self.current,
            donor_map_path=self.donor,
            scanner_path=self.scanner,
            approval_path=Path(self.approval_path.name),
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            output_map_path=Path(output_name),
            evidence_dir=Path(evidence_name),
        )

    def test_01_extended_scanner_delegates_world_index_and_reports_raw_tile_spans(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, item_id=200)])])
        build_world_index(
            map_path=self.current,
            scanner=self.scanner,
            output=self.current_index,
            manifest_output=self.current_manifest,
        )
        workspace = self.root / "scan-workspace"
        workspace.mkdir()
        report = scan_tile_spans(
            map_path=self.current,
            scanner=self.scanner,
            workspace=workspace,
            role="current",
        )
        self.assertEqual(report["format"], TILE_SPAN_FORMAT)
        self.assertEqual(len(report["tiles"]), 1)
        span = report["tiles"][0]
        self.assertEqual((span["areaBaseX"], span["areaBaseY"], span["areaZ"]), (256, 512, 7))
        self.assertEqual((span["x"], span["y"], span["z"]), (300, 600, 7))
        self.assertEqual(span["nodeType"], 5)
        with WorldIndex(self.current_index) as index:
            self.assertIsNotNone(index.find_tile((300, 600, 7)))

    def test_02_replaces_only_selected_tile_and_preserves_sources_and_unselected_current_tile(self) -> None:
        make_area_map(
            self.current,
            [self.area([self.tile(300, ground=100, item_id=200, action=1000), self.tile(301, ground=101, item_id=201)])],
        )
        make_area_map(
            self.donor,
            [self.area([self.tile(300, ground=102, item_id=206, action=1001), self.tile(301, ground=999, item_id=207)])],
        )
        current_before = self.current.read_bytes()
        donor_before = self.donor.read_bytes()
        self.build_indexes()
        self.write_approval([(300, 600, 7)])
        result = self.materialize()
        self.assertEqual(result["format"], RESULT_FORMAT)
        self.assertTrue(result["ok"])
        self.assertEqual(result["rawConfinement"]["operations"], {"replace": 1, "insert": 0, "delete": 0})
        self.assertTrue(result["rawConfinement"]["retainedBytes"]["exactlyPreserved"])
        self.assertEqual(self.current.read_bytes(), current_before)
        self.assertEqual(self.donor.read_bytes(), donor_before)
        with WorldIndex(self.current_index) as current_index, WorldIndex(self.donor_index) as donor_index, WorldIndex(
            self.root / "evidence" / "output.widx"
        ) as output_index:
            self.assertEqual(_canonical_tile(output_index, (300, 600, 7))[0], _canonical_tile(donor_index, (300, 600, 7))[0])
            self.assertEqual(_canonical_tile(output_index, (301, 600, 7))[0], _canonical_tile(current_index, (301, 600, 7))[0])
            self.assertNotEqual(_canonical_tile(output_index, (301, 600, 7))[0], _canonical_tile(donor_index, (301, 600, 7))[0])
        self.assertTrue((self.root / "evidence" / "materialization-result.json").is_file())
        self.assertTrue((self.root / "evidence" / "semantic-diff.json").is_file())
        with self.assertRaises(RuntimeError):
            self.materialize()

    def test_03_replaces_multiple_tiles_with_different_raw_lengths_and_preserves_retained_bytes(self) -> None:
        make_area_map(
            self.current,
            [self.area([self.tile(300, item_id=200), self.tile(301, item_id=201), self.tile(302, item_id=202)])],
        )
        make_area_map(
            self.donor,
            [
                self.area(
                    [
                        self.tile(300, item_id=210, extra_items=[{"id": 211}, {"id": 212}]),
                        self.tile(301, item_id=220),
                        self.tile(302, item_id=230, extra_items=[{"id": 231}]),
                    ]
                )
            ],
        )
        self.build_indexes()
        self.write_approval([(300, 600, 7), (302, 600, 7)])
        result = self.materialize()
        self.assertEqual(result["rawConfinement"]["operations"]["replace"], 2)
        self.assertTrue(result["verification"]["selectedTilesEqualDonor"])
        self.assertTrue(result["verification"]["nonSelectedCurrentBytesExact"])
        with WorldIndex(self.current_index) as current_index, WorldIndex(self.donor_index) as donor_index, WorldIndex(
            self.root / "evidence" / "output.widx"
        ) as output_index:
            for position in ((300, 600, 7), (302, 600, 7)):
                self.assertEqual(_canonical_tile(output_index, position)[0], _canonical_tile(donor_index, position)[0])
            self.assertEqual(_canonical_tile(output_index, (301, 600, 7))[0], _canonical_tile(current_index, (301, 600, 7))[0])

    def test_04_rejects_selected_position_missing_from_donor(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, item_id=200), self.tile(301, item_id=201)])])
        make_area_map(self.donor, [self.area([self.tile(300, item_id=210)])])
        self.build_indexes()
        approval = self.write_approval([(300, 600, 7)])
        selection = approval["selections"][0]
        selection["position"] = [301, 600, 7]
        selection["areaKey"] = [256, 512, 7]
        self.approval_path.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(TileMaterializerError, "exist exactly once in both"):
            self.materialize()

    def test_05_rejects_stale_expected_current_raw_hash(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, item_id=200)])])
        make_area_map(self.donor, [self.area([self.tile(300, item_id=210)])])
        self.build_indexes()
        approval = self.write_approval([(300, 600, 7)])
        approval["selections"][0]["current"]["rawSha256"] = "0" * 64
        self.approval_path.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(TileMaterializerError, "raw tile SHA-256 does not match approval"):
            self.materialize()

    def test_06_rejects_current_donor_tile_node_type_mismatch(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, item_id=200)])])
        make_house_map(self.donor, x=300, y=600, ground=210)
        self.build_indexes()
        self.write_approval([(300, 600, 7)])
        with self.assertRaisesRegex(TileMaterializerError, "same current/donor node type"):
            self.materialize()


if __name__ == "__main__":
    unittest.main()
