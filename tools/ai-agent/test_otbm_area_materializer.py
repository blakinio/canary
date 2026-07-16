from __future__ import annotations

import json
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_area_materializer import (
    APPROVAL_FORMAT,
    RESULT_FORMAT,
    SPAN_FORMAT,
    AreaMaterializerError,
    materialize_area_plan,
    scan_tile_area_spans,
)
from otbm_region_merge_planner import analyze_region_merge_plan
from otbm_semantic_diff_types import sha256_path
from otbm_world_index import WorldIndex, build_world_index
from test_otbm_world_index import ATTR_ACTION_ID, ATTR_ITEM, OTBM_ITEM, OTBM_MAP_DATA, OTBM_TILE, OTBM_TILE_AREA, attr_u16, item, node


def make_area_map(path: Path, areas: list[dict[str, object]]) -> None:
    area_nodes: list[bytes] = []
    for area_spec in areas:
        base_x = int(area_spec["baseX"])
        base_y = int(area_spec["baseY"])
        z = int(area_spec.get("z", 7))
        tile_nodes: list[bytes] = []
        for tile_spec in area_spec.get("tiles", []):  # type: ignore[union-attr]
            x = int(tile_spec["x"])
            y = int(tile_spec["y"])
            properties = bytes((x - base_x, y - base_y))
            ground = tile_spec.get("ground", 100)
            if ground is not None:
                properties += bytes((ATTR_ITEM,)) + struct.pack("<H", int(ground))
            children: list[bytes] = []
            for child in tile_spec.get("items", []):
                attributes = b""
                if "action" in child:
                    attributes += attr_u16(ATTR_ACTION_ID, int(child["action"]))
                children.append(item(int(child["id"]), attributes))
            tile_nodes.append(node(OTBM_TILE, properties, children))
        area_nodes.append(node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, z), tile_nodes))
    map_data = node(OTBM_MAP_DATA, b"", area_nodes)
    root = node(0, struct.pack("<IHHII", 4, 2048, 2048, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


class AreaMaterializerTests(unittest.TestCase):
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
        self.plan_path = self.root / "plan.json"
        self.approval_path = self.root / "approval.json"

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

    def make_plan(
        self,
        *,
        donor_from: tuple[int, int, int],
        donor_to: tuple[int, int, int],
        target_origin: tuple[int, int, int] | None = None,
    ) -> dict[str, object]:
        plan = analyze_region_merge_plan(
            artifact_root=self.root,
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            donor_from=donor_from,
            donor_to=donor_to,
            target_origin=target_origin or donor_from,
            policy="replace-region",
            sample_limit=10_000,
        )
        self.plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return plan

    def approve(self, plan: dict[str, object], keys: list[tuple[int, int, int]], *, omit_conflict: bool = False) -> None:
        conflict_ids = [entry["id"] for entry in plan["conflicts"]]  # type: ignore[index]
        if omit_conflict and conflict_ids:
            conflict_ids = conflict_ids[:-1]
        approval = {
            "format": APPROVAL_FORMAT,
            "schemaVersion": 1,
            "decision": "approved",
            "rationale": "Synthetic integration-test approval for the exact reviewed complete tile-area replacement.",
            "plan": {"format": "canary-otbm-region-merge-plan-v1", "sha256": sha256_path(self.plan_path)},
            "approvedAreaKeys": [
                {"baseX": base_x, "baseY": base_y, "z": z} for base_x, base_y, z in keys
            ],
            "approvedConflictIds": conflict_ids,
        }
        self.approval_path.write_text(json.dumps(approval, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def materialize(self, output_name: str = "output.otbm", evidence_name: str = "evidence") -> dict[str, object]:
        return materialize_area_plan(
            artifact_root=self.root,
            current_map_path=self.current,
            donor_map_path=self.donor,
            scanner_path=self.scanner,
            plan_path=Path(self.plan_path.name),
            approval_path=Path(self.approval_path.name),
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            output_map_path=Path(output_name),
            evidence_dir=Path(evidence_name),
        )

    @staticmethod
    def area(base_x: int, *, item_id: int, action: int | None = None) -> dict[str, object]:
        child: dict[str, object] = {"id": item_id}
        if action is not None:
            child["action"] = action
        return {
            "baseX": base_x,
            "baseY": 512,
            "z": 7,
            "tiles": [{"x": base_x + 44, "y": 600, "ground": 100, "items": [child]}],
        }

    def test_01_extended_scanner_delegates_world_index_and_reports_raw_area_spans(self) -> None:
        make_area_map(self.current, [self.area(256, item_id=200)])
        build_world_index(
            map_path=self.current,
            scanner=self.scanner,
            output=self.current_index,
            manifest_output=self.current_manifest,
        )
        workspace = self.root / "scan-workspace"
        workspace.mkdir()
        report = scan_tile_area_spans(
            map_path=self.current,
            scanner=self.scanner,
            workspace=workspace,
            role="current",
        )
        self.assertEqual(report["format"], SPAN_FORMAT)
        self.assertEqual(len(report["areas"]), 1)
        self.assertEqual(
            (report["areas"][0]["baseX"], report["areas"][0]["baseY"], report["areas"][0]["z"]),
            (256, 512, 7),
        )
        self.assertTrue(report["mapData"]["tileAreaSectionContiguous"])
        with WorldIndex(self.current_index) as index:
            self.assertIsNotNone(index.find_tile((300, 600, 7)))

    def test_02_replaces_complete_same_coordinate_area_and_preserves_sources(self) -> None:
        make_area_map(self.current, [self.area(256, item_id=200, action=1000)])
        make_area_map(self.donor, [self.area(256, item_id=206, action=1001)])
        current_before = self.current.read_bytes()
        donor_before = self.donor.read_bytes()
        self.build_indexes()
        plan = self.make_plan(donor_from=(256, 512, 7), donor_to=(511, 767, 7))
        self.assertTrue(plan["ok"])
        self.approve(plan, [(256, 512, 7)])
        result = self.materialize()
        self.assertEqual(result["format"], RESULT_FORMAT)
        self.assertTrue(result["ok"])
        self.assertTrue(result["verification"]["selectedAreasEqualDonor"])  # type: ignore[index]
        self.assertEqual(self.current.read_bytes(), current_before)
        self.assertEqual(self.donor.read_bytes(), donor_before)
        self.assertEqual((self.root / "output.otbm").read_bytes(), donor_before)
        self.assertTrue((self.root / "evidence" / "materialization-result.json").is_file())
        self.assertTrue((self.root / "evidence" / "semantic-diff.json").is_file())
        with self.assertRaises(AreaMaterializerError):
            self.materialize()

    def test_03_inserts_missing_complete_area_without_changing_retained_area(self) -> None:
        current_area = self.area(256, item_id=200)
        donor_area = self.area(512, item_id=206)
        make_area_map(self.current, [current_area])
        make_area_map(self.donor, [current_area, donor_area])
        self.build_indexes()
        plan = self.make_plan(donor_from=(512, 512, 7), donor_to=(767, 767, 7))
        self.approve(plan, [(512, 512, 7)])
        result = self.materialize()
        self.assertEqual(result["rawConfinement"]["operations"]["insert"], 1)  # type: ignore[index]
        output = self.root / "output.otbm"
        output_index = self.root / "evidence" / "output.widx"
        with WorldIndex(output_index) as index:
            self.assertIsNotNone(index.find_tile((300, 600, 7)))
            self.assertIsNotNone(index.find_tile((556, 600, 7)))
        self.assertTrue(output.stat().st_size > self.current.stat().st_size)
        self.assertTrue(result["rawConfinement"]["retainedBytes"]["exactlyPreserved"])  # type: ignore[index]

    def test_04_deletes_selected_area_when_donor_region_is_empty(self) -> None:
        first = self.area(256, item_id=200)
        second = self.area(512, item_id=206)
        make_area_map(self.current, [first, second])
        make_area_map(self.donor, [first])
        self.build_indexes()
        plan = self.make_plan(donor_from=(512, 512, 7), donor_to=(767, 767, 7))
        self.approve(plan, [(512, 512, 7)])
        result = self.materialize()
        self.assertEqual(result["rawConfinement"]["operations"]["delete"], 1)  # type: ignore[index]
        with WorldIndex(self.root / "evidence" / "output.widx") as index:
            self.assertIsNone(index.find_tile((556, 600, 7)))
            self.assertIsNotNone(index.find_tile((300, 600, 7)))

    def test_05_rejects_nonzero_translation(self) -> None:
        make_area_map(self.current, [self.area(256, item_id=200)])
        make_area_map(self.donor, [self.area(256, item_id=206)])
        self.build_indexes()
        plan = self.make_plan(
            donor_from=(256, 512, 7),
            donor_to=(511, 767, 7),
            target_origin=(512, 512, 7),
        )
        self.approve(plan, [(256, 512, 7)])
        with self.assertRaisesRegex(AreaMaterializerError, "zero donor-to-target translation"):
            self.materialize()

    def test_06_rejects_incomplete_conflict_approval(self) -> None:
        make_area_map(self.current, [self.area(256, item_id=200)])
        make_area_map(self.donor, [self.area(256, item_id=206)])
        self.build_indexes()
        plan = self.make_plan(donor_from=(256, 512, 7), donor_to=(511, 767, 7))
        self.assertGreater(len(plan["conflicts"]), 0)  # type: ignore[arg-type]
        self.approve(plan, [(256, 512, 7)], omit_conflict=True)
        with self.assertRaisesRegex(AreaMaterializerError, "cover every non-blocking"):
            self.materialize()

    def test_07_rejects_partial_tile_area_bounds(self) -> None:
        make_area_map(self.current, [self.area(256, item_id=200)])
        make_area_map(self.donor, [self.area(256, item_id=206)])
        self.build_indexes()
        plan = self.make_plan(donor_from=(300, 600, 7), donor_to=(301, 600, 7))
        self.approve(plan, [])
        with self.assertRaisesRegex(AreaMaterializerError, "complete 256x256"):
            self.materialize()


if __name__ == "__main__":
    unittest.main()
