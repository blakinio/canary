from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_area_materializer import _area_index, scan_tile_area_spans
from otbm_semantic_diff_types import sha256_path
from otbm_tile_deletion_materializer import (
    APPROVAL_FORMAT,
    RESULT_FORMAT,
    TileDeletionMaterializerError,
    materialize_tile_deletions,
)
from otbm_tile_materializer import _canonical_tile, scan_tile_spans
from otbm_world_index import WorldIndex, build_world_index
from test_otbm_area_materializer import make_area_map


def pin(path: Path) -> dict[str, object]:
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


class TileDeletionMaterializerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++") or shutil.which("g++")
        if compiler is None:
            raise unittest.SkipTest("A C++ compiler is required")
        cls.compiler_temp = tempfile.TemporaryDirectory()
        cls.scanner = Path(cls.compiler_temp.name) / "otbm_area_materializer_scan"
        source = Path(__file__).with_name("otbm_area_materializer_scan.cpp")
        result = subprocess.run(
            [compiler, "-O2", "-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror", str(source), "-o", str(cls.scanner)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.compiler_temp.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.current = self.root / "current.otbm"
        self.current_index = self.root / "current.widx"
        self.current_manifest = self.root / "current.widx.json"
        self.approval = self.root / "approval.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def area(tiles: list[dict[str, object]], *, base_x: int = 256) -> dict[str, object]:
        return {"baseX": base_x, "baseY": 512, "z": 7, "tiles": tiles}

    @staticmethod
    def tile(x: int, item_id: int) -> dict[str, object]:
        return {"x": x, "y": 600, "ground": 100, "items": [{"id": item_id}]}

    def build_index(self) -> None:
        build_world_index(
            map_path=self.current,
            scanner=self.scanner,
            output=self.current_index,
            manifest_output=self.current_manifest,
        )

    def write_approval(self, positions: list[tuple[int, int, int]]) -> dict[str, object]:
        workspace = self.root / "scan"
        workspace.mkdir(exist_ok=True)
        report = scan_tile_spans(
            map_path=self.current,
            scanner=self.scanner,
            workspace=workspace,
            role="current",
        )
        spans = {(int(entry["x"]), int(entry["y"]), int(entry["z"])): entry for entry in report["tiles"]}
        selections: list[dict[str, object]] = []
        with WorldIndex(self.current_index) as index:
            for position in positions:
                span = spans[position]
                canonical, _ = _canonical_tile(index, position)
                selections.append(
                    {
                        "position": list(position),
                        "areaKey": [position[0] & 0xFF00, position[1] & 0xFF00, position[2]],
                        "current": {
                            "rawSha256": span["sha256"],
                            "rawByteLength": span["byteLength"],
                            "nodeType": span["nodeType"],
                            "canonicalSha256": canonical,
                        },
                    }
                )
        approval: dict[str, object] = {
            "format": APPROVAL_FORMAT,
            "schemaVersion": 1,
            "decision": "approved",
            "rationale": "Synthetic exact-coordinate raw tile deletion approval.",
            "provenance": {
                "current": {
                    "sourceMap": pin(self.current),
                    "worldIndex": pin(self.current_index),
                    "manifest": pin(self.current_manifest),
                }
            },
            "selections": selections,
        }
        self.approval.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return approval

    def run_materializer(self) -> dict[str, object]:
        return materialize_tile_deletions(
            artifact_root=self.root,
            current_map_path=self.current,
            scanner_path=self.scanner,
            approval_path=Path(self.approval.name),
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            output_map_path=Path("output.otbm"),
            evidence_dir=Path("evidence"),
        )

    def test_01_deletes_one_tile_and_preserves_unselected_tile(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, 200), self.tile(301, 201)])])
        self.build_index()
        self.write_approval([(301, 600, 7)])
        result = self.run_materializer()
        self.assertEqual(result["format"], RESULT_FORMAT)
        self.assertEqual(result["rawConfinement"]["operations"], {"replace": 0, "insert": 0, "delete": 1})
        self.assertTrue(result["rawConfinement"]["retainedBytes"]["exactlyPreserved"])
        with WorldIndex(self.current_index) as before, WorldIndex(self.root / "evidence" / "output.widx") as after:
            self.assertIsNone(after.find_tile((301, 600, 7)))
            self.assertEqual(_canonical_tile(after, (300, 600, 7))[0], _canonical_tile(before, (300, 600, 7))[0])

    def test_02_deletes_multiple_selected_spans(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, 200), self.tile(301, 201), self.tile(302, 202)])])
        self.build_index()
        self.write_approval([(302, 600, 7), (300, 600, 7)])
        result = self.run_materializer()
        self.assertEqual(result["selection"]["count"], 2)
        with WorldIndex(self.root / "evidence" / "output.widx") as after:
            self.assertIsNone(after.find_tile((300, 600, 7)))
            self.assertIsNotNone(after.find_tile((301, 600, 7)))
            self.assertIsNone(after.find_tile((302, 600, 7)))

    def test_03_deletes_last_tile_but_preserves_parent_tile_area(self) -> None:
        make_area_map(
            self.current,
            [
                self.area([self.tile(300, 200)]),
                self.area([{"x": 512, "y": 600, "ground": 100, "items": [{"id": 250}]}], base_x=512),
            ],
        )
        self.build_index()
        self.write_approval([(300, 600, 7)])
        result = self.run_materializer()
        self.assertTrue(result["verification"]["parentTileAreasPreserved"])
        workspace = self.root / "post-scan"
        workspace.mkdir()
        areas = _area_index(
            scan_tile_area_spans(
                map_path=self.root / "output.otbm",
                scanner=self.scanner,
                workspace=workspace,
                role="output",
            )
        )
        self.assertEqual(len(areas[(256, 512, 7)]), 1)

    def test_04_rejects_position_missing_from_current(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, 200)])])
        self.build_index()
        approval = self.write_approval([(300, 600, 7)])
        approval["selections"][0]["position"] = [301, 600, 7]
        approval["selections"][0]["areaKey"] = [256, 512, 7]
        self.approval.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(TileDeletionMaterializerError, "must exist exactly once"):
            self.run_materializer()

    def test_05_rejects_stale_current_raw_hash(self) -> None:
        make_area_map(self.current, [self.area([self.tile(300, 200)])])
        self.build_index()
        approval = self.write_approval([(300, 600, 7)])
        approval["selections"][0]["current"]["rawSha256"] = "0" * 64
        self.approval.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(TileDeletionMaterializerError, "raw tile SHA-256"):
            self.run_materializer()


if __name__ == "__main__":
    unittest.main()
