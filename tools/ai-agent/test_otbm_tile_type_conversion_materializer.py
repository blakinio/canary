from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_semantic_diff_types import sha256_path
from otbm_tile_materializer import _canonical_tile, scan_tile_spans
from otbm_tile_type_conversion_materializer import (
    APPROVAL_FORMAT,
    RESULT_FORMAT,
    TileTypeConversionMaterializerError,
    materialize_tile_type_conversions,
)
from otbm_world_index import WorldIndex, build_world_index
from test_otbm_area_materializer import make_area_map
from test_otbm_tile_materializer import make_house_map


def pin(path: Path) -> dict[str, object]:
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


def make_tile_map(path: Path, *, x: int, y: int, z: int = 7, ground: int = 100, item_id: int = 200) -> None:
    make_area_map(
        path,
        [
            {
                "baseX": x & 0xFF00,
                "baseY": y & 0xFF00,
                "z": z,
                "tiles": [
                    {
                        "x": x,
                        "y": y,
                        "ground": ground,
                        "items": [{"id": item_id}],
                    }
                ],
            }
        ],
    )


class TileTypeConversionMaterializerTests(unittest.TestCase):
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
        self.position = (300, 600, 7)

    def tearDown(self) -> None:
        self.temp.cleanup()

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

    def write_approval(self) -> dict[str, object]:
        workspace = self.root / "span-workspace"
        workspace.mkdir(exist_ok=True)
        current_report = scan_tile_spans(
            map_path=self.current,
            scanner=self.scanner,
            workspace=workspace,
            role="current",
        )
        donor_report = scan_tile_spans(
            map_path=self.donor,
            scanner=self.scanner,
            workspace=workspace,
            role="donor",
        )
        current_span = current_report["tiles"][0]
        donor_span = donor_report["tiles"][0]
        with WorldIndex(self.current_index) as current_index, WorldIndex(self.donor_index) as donor_index:
            current_canonical, _ = _canonical_tile(current_index, self.position)
            donor_canonical, _ = _canonical_tile(donor_index, self.position)
        approval: dict[str, object] = {
            "format": APPROVAL_FORMAT,
            "schemaVersion": 1,
            "decision": "approved",
            "rationale": "Synthetic approval for exact same-coordinate complete raw tile type conversion.",
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
            "selections": [
                {
                    "position": list(self.position),
                    "areaKey": [256, 512, 7],
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
            ],
        }
        self.approval_path.write_text(
            json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return approval

    def materialize(self) -> dict[str, object]:
        return materialize_tile_type_conversions(
            artifact_root=self.root,
            current_map_path=self.current,
            donor_map_path=self.donor,
            scanner_path=self.scanner,
            approval_path=Path(self.approval_path.name),
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            output_map_path=Path("output.otbm"),
            evidence_dir=Path("evidence"),
        )

    def test_converts_tile_to_house_tile_with_exact_donor_subtree(self) -> None:
        make_tile_map(self.current, x=300, y=600, ground=100, item_id=200)
        make_house_map(self.donor, x=300, y=600, house_id=42, ground=101)
        current_before = self.current.read_bytes()
        donor_before = self.donor.read_bytes()
        self.build_indexes()
        self.write_approval()

        result = self.materialize()

        self.assertEqual(result["format"], RESULT_FORMAT)
        self.assertTrue(result["ok"])
        self.assertEqual(
            result["rawConfinement"]["operations"],
            {"replace": 0, "convert": 1, "insert": 0, "delete": 0},
        )
        self.assertEqual(result["selection"]["conversions"][0]["fromNodeType"], 5)
        self.assertEqual(result["selection"]["conversions"][0]["toNodeType"], 14)
        self.assertEqual(self.current.read_bytes(), current_before)
        self.assertEqual(self.donor.read_bytes(), donor_before)
        with WorldIndex(self.donor_index) as donor_index, WorldIndex(
            self.root / "evidence" / "output.widx"
        ) as output_index:
            self.assertEqual(
                _canonical_tile(output_index, self.position)[0],
                _canonical_tile(donor_index, self.position)[0],
            )
            found = output_index.find_tile(self.position)
            self.assertIsNotNone(found)
            assert found is not None
            self.assertEqual(found[1].kind, "house")
            self.assertEqual(found[1].house_id, 42)

    def test_converts_house_tile_to_tile_with_exact_donor_subtree(self) -> None:
        make_house_map(self.current, x=300, y=600, house_id=77, ground=100)
        make_tile_map(self.donor, x=300, y=600, ground=102, item_id=220)
        self.build_indexes()
        self.write_approval()

        result = self.materialize()

        self.assertEqual(result["selection"]["conversions"][0]["fromNodeType"], 14)
        self.assertEqual(result["selection"]["conversions"][0]["toNodeType"], 5)
        with WorldIndex(self.donor_index) as donor_index, WorldIndex(
            self.root / "evidence" / "output.widx"
        ) as output_index:
            self.assertEqual(
                _canonical_tile(output_index, self.position)[0],
                _canonical_tile(donor_index, self.position)[0],
            )
            found = output_index.find_tile(self.position)
            self.assertIsNotNone(found)
            assert found is not None
            self.assertEqual(found[1].kind, "tile")
            self.assertIsNone(found[1].house_id)

    def test_rejects_same_node_type(self) -> None:
        make_tile_map(self.current, x=300, y=600, ground=100, item_id=200)
        make_tile_map(self.donor, x=300, y=600, ground=101, item_id=210)
        self.build_indexes()
        self.write_approval()

        with self.assertRaisesRegex(
            TileTypeConversionMaterializerError, "requires different current/donor node types"
        ):
            self.materialize()

    def test_rejects_stale_current_raw_sha(self) -> None:
        make_tile_map(self.current, x=300, y=600, ground=100, item_id=200)
        make_house_map(self.donor, x=300, y=600, house_id=42, ground=101)
        self.build_indexes()
        approval = self.write_approval()
        approval["selections"][0]["current"]["rawSha256"] = "0" * 64  # type: ignore[index]
        self.approval_path.write_text(
            json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        with self.assertRaisesRegex(RuntimeError, "raw tile SHA-256 does not match approval"):
            self.materialize()


if __name__ == "__main__":
    unittest.main()
