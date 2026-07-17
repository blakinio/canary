from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_area_materializer import _area_index, scan_tile_area_spans
from otbm_semantic_diff_types import sha256_path
from otbm_tile_insertion_materializer import (
    APPROVAL_FORMAT,
    RESULT_FORMAT,
    TileInsertionMaterializerError,
    materialize_tile_insertions,
)
from otbm_tile_materializer import _canonical_tile, scan_tile_spans
from otbm_world_index import WorldIndex, build_world_index
from test_otbm_area_materializer import make_area_map
from test_otbm_tile_materializer import make_house_map


def pin(path: Path) -> dict[str, object]:
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


class TileInsertionMaterializerTests(unittest.TestCase):
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
        self.approval = self.root / "approval.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def area(tiles: list[dict[str, object]]) -> dict[str, object]:
        return {"baseX": 256, "baseY": 512, "z": 7, "tiles": tiles}

    @staticmethod
    def tile(x: int, *, ground: int = 100, item_id: int | None = None) -> dict[str, object]:
        items: list[dict[str, object]] = []
        if item_id is not None:
            items.append({"id": item_id})
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

    def write_approval(self, positions: list[tuple[int, int, int]]) -> dict[str, object]:
        workspace = self.root / "scan"
        workspace.mkdir(exist_ok=True)
        current_areas = scan_tile_area_spans(
            map_path=self.current,
            scanner=self.scanner,
            workspace=workspace,
            role="current",
        )
        donor_tiles = scan_tile_spans(
            map_path=self.donor,
            scanner=self.scanner,
            workspace=workspace,
            role="donor",
        )
        areas = _area_index(current_areas)
        donor_by_position = {
            (int(entry["x"]), int(entry["y"]), int(entry["z"])): entry
            for entry in donor_tiles["tiles"]
        }
        selections: list[dict[str, object]] = []
        with WorldIndex(self.donor_index) as donor_index:
            for position in positions:
                area = (position[0] & 0xFF00, position[1] & 0xFF00, position[2])
                area_span = areas[area][0]
                donor_span = donor_by_position[position]
                donor_canonical, _ = _canonical_tile(donor_index, position)
                selections.append(
                    {
                        "position": list(position),
                        "areaKey": list(area),
                        "currentArea": {
                            "rawSha256": area_span["sha256"],
                            "rawByteLength": area_span["byteLength"],
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
            "rationale": "Synthetic exact-coordinate raw tile insertion approval.",
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
        self.approval.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return approval

    def run_materializer(self) -> dict[str, object]:
        return materialize_tile_insertions(
            artifact_root=self.root,
            current_map_path=self.current,
            donor_map_path=self.donor,
            scanner_path=self.scanner,
            approval_path=Path(self.approval.name),
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            output_map_path=Path("output.otbm"),
            evidence_dir=Path("evidence"),
        )

    def test_01_inserts_missing_tile_and_preserves_complete_current_byte_sequence(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, item_id=200)])])
        make_area_map(self.donor, [self.area([self.tile(300, item_id=999), self.tile(301, ground=101, item_id=201)])])
        current_before = self.current.read_bytes()
        self.build_indexes()
        self.write_approval([(301, 600, 7)])
        result = self.run_materializer()
        self.assertEqual(result["format"], RESULT_FORMAT)
        self.assertEqual(result["rawConfinement"]["operations"], {"replace": 0, "insert": 1, "delete": 0})
        self.assertTrue(result["rawConfinement"]["retainedBytes"]["exactlyPreserved"])
        self.assertEqual(self.current.read_bytes(), current_before)
        with WorldIndex(self.current_index) as current_index, WorldIndex(self.donor_index) as donor_index, WorldIndex(
            self.root / "evidence" / "output.widx"
        ) as output_index:
            self.assertEqual(_canonical_tile(output_index, (301, 600, 7))[0], _canonical_tile(donor_index, (301, 600, 7))[0])
            self.assertEqual(_canonical_tile(output_index, (300, 600, 7))[0], _canonical_tile(current_index, (300, 600, 7))[0])
        self.assertTrue((self.root / "evidence" / "semantic-diff.json").is_file())

    def test_02_inserts_multiple_tiles_into_empty_existing_area_in_deterministic_position_order(self) -> None:
        make_area_map(self.current, [self.area([])])
        make_area_map(self.donor, [self.area([self.tile(302, item_id=202), self.tile(300, item_id=200)])])
        self.build_indexes()
        self.write_approval([(302, 600, 7), (300, 600, 7)])
        result = self.run_materializer()
        spans = result["rawConfinement"]["outputInsertedSpans"]
        self.assertLess(spans["300,600,7"][0], spans["302,600,7"][0])
        with WorldIndex(self.root / "evidence" / "output.widx") as output_index:
            self.assertIsNotNone(output_index.find_tile((300, 600, 7)))
            self.assertIsNotNone(output_index.find_tile((302, 600, 7)))

    def test_03_rejects_position_that_already_exists_in_current(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, item_id=200)])])
        make_area_map(self.donor, [self.area([self.tile(300, item_id=210)])])
        self.build_indexes()
        self.write_approval([(300, 600, 7)])
        with self.assertRaisesRegex(TileInsertionMaterializerError, "already exists in current"):
            self.run_materializer()

    def test_04_rejects_stale_target_tile_area_hash(self) -> None:
        make_area_map(self.current, [self.area([])])
        make_area_map(self.donor, [self.area([self.tile(300, item_id=210)])])
        self.build_indexes()
        approval = self.write_approval([(300, 600, 7)])
        approval["selections"][0]["currentArea"]["rawSha256"] = "0" * 64
        self.approval.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(TileInsertionMaterializerError, "TILE_AREA.*SHA-256"):
            self.run_materializer()

    def test_05_inserts_complete_house_tile_without_type_conversion(self) -> None:
        make_area_map(self.current, [self.area([])])
        make_house_map(self.donor, x=300, y=600, ground=210)
        self.build_indexes()
        self.write_approval([(300, 600, 7)])
        result = self.run_materializer()
        self.assertTrue(result["verification"]["insertedTilesEqualDonor"])
        with WorldIndex(self.root / "evidence" / "output.widx") as output_index:
            found = output_index.find_tile((300, 600, 7))
            self.assertIsNotNone(found)
            assert found is not None
            self.assertEqual(found[1].kind, "house")


if __name__ == "__main__":
    unittest.main()
