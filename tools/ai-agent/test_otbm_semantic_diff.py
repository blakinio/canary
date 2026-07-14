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

from otbm_semantic_diff import SemanticDiffError, analyze_index_paths, write_report
from otbm_semantic_diff_render import RENDER_MANIFEST_FORMAT, build_render_manifest
from otbm_world_index import WorldIndexError, build_world_index
from test_otbm_world_index import (
    ATTR_ACTION_ID,
    ATTR_HOUSEDOOR_ID,
    ATTR_ITEM,
    ATTR_TELE_DEST,
    ATTR_TILE_FLAGS,
    ATTR_UNIQUE_ID,
    OTBM_HOUSETILE,
    OTBM_ITEM,
    OTBM_MAP_DATA,
    OTBM_TILE,
    OTBM_TILE_AREA,
    attr_position,
    attr_u8,
    attr_u16,
    item,
    node,
)


def _item(spec: dict[str, object]) -> bytes:
    attributes = b""
    if "action" in spec:
        attributes += attr_u16(ATTR_ACTION_ID, int(spec["action"]))
    if "unique" in spec:
        attributes += attr_u16(ATTR_UNIQUE_ID, int(spec["unique"]))
    if "door" in spec:
        attributes += attr_u8(ATTR_HOUSEDOOR_ID, int(spec["door"]))
    if "teleport" in spec:
        attributes += attr_position(ATTR_TELE_DEST, tuple(spec["teleport"]))  # type: ignore[arg-type]
    return item(int(spec["id"]), attributes)


def make_variant(path: Path, tiles: list[dict[str, object]]) -> None:
    base_x, base_y, floor = 256, 512, 7
    tile_nodes: list[bytes] = []
    for spec in tiles:
        x = int(spec["x"])
        y = int(spec.get("y", 600))
        house_id = spec.get("house")
        properties = bytes((x - base_x, y - base_y))
        tile_type = OTBM_TILE
        if house_id is not None:
            properties += struct.pack("<I", int(house_id))
            tile_type = OTBM_HOUSETILE
        flags = int(spec.get("flags", 0))
        if flags:
            properties += bytes((ATTR_TILE_FLAGS,)) + struct.pack("<I", flags)
        ground = spec.get("ground", 100)
        if ground is not None:
            properties += bytes((ATTR_ITEM,)) + struct.pack("<H", int(ground))
        children = [_item(child) for child in spec.get("items", [])]  # type: ignore[arg-type]
        tile_nodes.append(node(tile_type, properties, children))
    area = node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, floor), tile_nodes)
    map_data = node(OTBM_MAP_DATA, b"", [area])
    root = node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


def base_tiles() -> list[dict[str, object]]:
    return [
        {
            "x": 300,
            "ground": 100,
            "items": [
                {"id": 200, "action": 1000},
                {"id": 202, "teleport": (310, 620, 8)},
                {"id": 203, "door": 7},
                {"id": 204},
            ],
        },
        {"x": 301, "house": 99, "flags": 4, "ground": 100, "items": [{"id": 205, "unique": 6000}]},
    ]


def copy_tiles() -> list[dict[str, object]]:
    return json.loads(json.dumps(base_tiles()))


class SemanticDiffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++") or shutil.which("g++")
        if compiler is None:
            raise unittest.SkipTest("A C++ compiler is required")
        cls.compiler_temp = tempfile.TemporaryDirectory()
        cls.scanner = Path(cls.compiler_temp.name) / "otbm_item_audit_scan"
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
        cls.compiler_temp.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.before_map = self.root / "before.otbm"
        self.after_map = self.root / "after.otbm"
        self.before_index = self.root / "before.widx"
        self.after_index = self.root / "after.widx"
        self.before_manifest = self.root / "before.widx.json"
        self.after_manifest = self.root / "after.widx.json"
        self.appearances = self.root / "appearances.json"
        self.appearances.write_text(
            json.dumps(
                {
                    "format": "canary-appearances-index-v1",
                    "ok": True,
                    "appearances": [
                        {"category": "object", "id": 100, "flags": {"bank": {}}},
                        {"category": "object", "id": 101, "flags": {"bank": {}}},
                        {"category": "object", "id": 200, "flags": {}},
                        {"category": "object", "id": 202, "flags": {}},
                        {"category": "object", "id": 203, "flags": {}},
                        {"category": "object", "id": 204, "flags": {}},
                        {"category": "object", "id": 205, "flags": {}},
                        {"category": "object", "id": 206, "flags": {}},
                        {"category": "object", "id": 300, "flags": {"unpassable": True}},
                        {"category": "object", "id": 301, "flags": {"unpassable": True, "usable": True}},
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self, before: list[dict[str, object]], after: list[dict[str, object]]) -> None:
        make_variant(self.before_map, before)
        make_variant(self.after_map, after)
        build_world_index(
            map_path=self.before_map,
            scanner=self.scanner,
            output=self.before_index,
            manifest_output=self.before_manifest,
        )
        build_world_index(
            map_path=self.after_map,
            scanner=self.scanner,
            output=self.after_index,
            manifest_output=self.after_manifest,
        )

    def analyze(self, **kwargs: object) -> dict[str, object]:
        return analyze_index_paths(
            artifact_root=self.root,
            before_index_path=self.before_index.name,
            before_manifest_path=self.before_manifest.name,
            after_index_path=self.after_index.name,
            after_manifest_path=self.after_manifest.name,
            appearances_path=self.appearances.name,
            **kwargs,
        )

    @staticmethod
    def kinds(report: dict[str, object]) -> list[str]:
        return [entry["kind"] for entry in report["findings"]]  # type: ignore[index]

    def test_01_identical_indexes_have_zero_changes(self) -> None:
        self.build(base_tiles(), base_tiles())
        report = self.analyze()
        self.assertEqual(report["summary"]["findings"]["total"], 0)  # type: ignore[index]
        self.assertEqual(report["summary"]["unchangedTiles"], 2)  # type: ignore[index]

    def test_02_tile_added(self) -> None:
        before = base_tiles()[:1]
        self.build(before, base_tiles())
        self.assertIn("tile-added", self.kinds(self.analyze()))

    def test_03_tile_removed(self) -> None:
        after = base_tiles()[:1]
        self.build(base_tiles(), after)
        self.assertIn("tile-removed", self.kinds(self.analyze()))

    def test_04_tile_flags_changed(self) -> None:
        after = copy_tiles()
        after[1]["flags"] = 8
        self.build(base_tiles(), after)
        self.assertIn("tile-flags-changed", self.kinds(self.analyze()))

    def test_05_house_id_changed(self) -> None:
        after = copy_tiles()
        after[1]["house"] = 100
        self.build(base_tiles(), after)
        self.assertIn("house-id-changed", self.kinds(self.analyze()))

    def test_06_ground_item_changed(self) -> None:
        after = copy_tiles()
        after[0]["ground"] = 101
        self.build(base_tiles(), after)
        self.assertIn("ground-changed", self.kinds(self.analyze()))

    def test_07_item_added(self) -> None:
        after = copy_tiles()
        after[0]["items"].append({"id": 206})  # type: ignore[union-attr]
        self.build(base_tiles(), after)
        self.assertIn("item-added", self.kinds(self.analyze()))

    def test_08_item_removed(self) -> None:
        after = copy_tiles()
        after[0]["items"].pop()  # type: ignore[union-attr]
        self.build(base_tiles(), after)
        self.assertIn("item-removed", self.kinds(self.analyze()))

    def test_09_stack_order_change_has_no_false_add_remove(self) -> None:
        after = copy_tiles()
        items = after[0]["items"]  # type: ignore[index]
        items[0], items[1] = items[1], items[0]  # type: ignore[index]
        self.build(base_tiles(), after)
        kinds = self.kinds(self.analyze())
        self.assertIn("stack-order-changed", kinds)
        self.assertNotIn("item-added", kinds)
        self.assertNotIn("item-removed", kinds)

    def test_10_action_id_changed(self) -> None:
        after = copy_tiles()
        after[0]["items"][0]["action"] = 1001  # type: ignore[index]
        self.build(base_tiles(), after)
        self.assertIn("action-id-changed", self.kinds(self.analyze()))

    def test_11_unique_id_changed(self) -> None:
        after = copy_tiles()
        after[1]["items"][0]["unique"] = 6001  # type: ignore[index]
        self.build(base_tiles(), after)
        self.assertIn("unique-id-changed", self.kinds(self.analyze()))

    def test_12_house_door_id_changed(self) -> None:
        after = copy_tiles()
        after[0]["items"][2]["door"] = 8  # type: ignore[index]
        self.build(base_tiles(), after)
        self.assertIn("house-door-id-changed", self.kinds(self.analyze()))

    def test_13_teleport_destination_changed(self) -> None:
        after = copy_tiles()
        after[0]["items"][1]["teleport"] = [311, 620, 8]  # type: ignore[index]
        self.build(base_tiles(), after)
        self.assertIn("teleport-destination-changed", self.kinds(self.analyze()))

    def test_14_strict_walkability_regression(self) -> None:
        before = [{"x": 300, "ground": 100, "items": []}]
        after = [{"x": 300, "ground": 100, "items": [{"id": 300}]}]
        self.build(before, after)
        kinds = self.kinds(self.analyze())
        self.assertIn("strict-walkable-to-blocked", kinds)
        self.assertIn("static-blocker-added", kinds)

    def test_15_conditional_walkability_change(self) -> None:
        before = [{"x": 300, "ground": 100, "items": []}]
        after = [{"x": 300, "ground": 100, "items": [{"id": 301}]}]
        self.build(before, after)
        self.assertIn("strict-to-conditional", self.kinds(self.analyze()))

    def test_16_unknown_appearance_is_retained(self) -> None:
        before = [{"x": 300, "ground": 100, "items": [{"id": 999, "action": 1}]}]
        after = [{"x": 300, "ground": 100, "items": [{"id": 999, "action": 2}]}]
        self.build(before, after)
        kinds = self.kinds(self.analyze())
        self.assertIn("action-id-changed", kinds)
        self.assertNotIn("unknown-appearance-added", kinds)
        self.assertNotIn("unknown-appearance-removed", kinds)

    def test_17_bounded_region_excludes_outside_changes(self) -> None:
        after = copy_tiles()
        after[1]["flags"] = 8
        self.build(base_tiles(), after)
        report = self.analyze(lower=(300, 600, 7), upper=(300, 600, 7))
        self.assertEqual(report["summary"]["findings"]["total"], 0)  # type: ignore[index]

    def test_18_exact_totals_survive_sample_truncation(self) -> None:
        after = copy_tiles()
        after[0]["items"].extend([{"id": 206}, {"id": 206}, {"id": 206}])  # type: ignore[union-attr]
        self.build(base_tiles(), after)
        report = self.analyze(sample_limit=1)
        summary = report["summary"]["findings"]  # type: ignore[index]
        self.assertGreater(summary["total"], len(report["findings"]))  # type: ignore[arg-type,index]
        self.assertTrue(summary["truncated"])

    def test_19_output_is_deterministic(self) -> None:
        after = copy_tiles()
        after[0]["items"][0]["action"] = 1001  # type: ignore[index]
        self.build(base_tiles(), after)
        first = self.analyze()
        second = self.analyze()
        self.assertEqual(first, second)

    def test_20_corrupt_index_fails_closed(self) -> None:
        self.build(base_tiles(), base_tiles())
        with self.after_index.open("r+b") as stream:
            stream.seek(0)
            stream.write(b"BROKEN!!")
        with self.assertRaises((WorldIndexError, SemanticDiffError)):
            self.analyze()

    def test_21_mismatched_map_index_provenance_fails_closed(self) -> None:
        self.build(base_tiles(), base_tiles())
        manifest = json.loads(self.after_manifest.read_text(encoding="utf-8"))
        manifest["source"]["size"] += 1
        self.after_manifest.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(SemanticDiffError):
            self.analyze()

    def test_22_output_overwrite_requires_explicit_permission(self) -> None:
        self.build(base_tiles(), base_tiles())
        report = self.analyze()
        output = self.root / "report.json"
        write_report(output.name, report, artifact_root=self.root)
        with self.assertRaises(SemanticDiffError):
            write_report(output.name, report, artifact_root=self.root)
        write_report(output.name, report, artifact_root=self.root, overwrite=True)

    @unittest.skipIf(os.name == "nt", "symlink creation often requires elevated privileges on Windows")
    def test_23_symlink_output_is_rejected(self) -> None:
        self.build(base_tiles(), base_tiles())
        report = self.analyze()
        target = self.root / "target.json"
        target.write_text("{}", encoding="utf-8")
        link = self.root / "report.json"
        link.symlink_to(target)
        with self.assertRaises(SemanticDiffError):
            write_report(link.name, report, artifact_root=self.root)

    def _correlated_change(self, role: str, format_name: str, expected_classification: str | None) -> dict[str, object]:
        after = copy_tiles()
        after[0]["items"][0]["action"] = 1001  # type: ignore[index]
        self.build(base_tiles(), after)
        report_path = self.root / f"{role}.json"
        report_path.write_text(
            json.dumps({"format": format_name, "findings": [{"position": [300, 600, 7], "status": "confirmed"}]}),
            encoding="utf-8",
        )
        keyword = {
            "quest-validation": "quest_validation_path",
            "reachability": "reachability_path",
            "spawn-npc": "spawn_npc_path",
            "storage-graph": "storage_graph_path",
        }[role]
        result = self.analyze(**{keyword: report_path.name})
        finding = next(entry for entry in result["findings"] if entry["kind"] == "action-id-changed")  # type: ignore[index]
        self.assertTrue(finding["correlations"])
        if expected_classification is not None:
            self.assertIn(expected_classification, finding["classifications"])
        return result

    def test_24_optional_phase2_correlation(self) -> None:
        self._correlated_change("quest-validation", "canary-quest-map-validation-v1", "quest-evidence-affected")

    def test_25_optional_phase3_correlation(self) -> None:
        self._correlated_change("reachability", "canary-otbm-reachability-v1", None)

    def test_26_optional_phase4_correlation(self) -> None:
        self._correlated_change("spawn-npc", "canary-otbm-spawn-npc-validation-v1", "spawn-npc-evidence-affected")

    def test_27_optional_phase5_correlation(self) -> None:
        self._correlated_change("storage-graph", "canary-otbm-storage-graph-v1", "storage-evidence-affected")

    def test_28_missing_optional_report_creates_no_false_findings(self) -> None:
        self.build(base_tiles(), base_tiles())
        report = self.analyze()
        self.assertEqual(report["summary"]["findings"]["total"], 0)  # type: ignore[index]
        self.assertFalse(report["correlation"]["enabled"])  # type: ignore[index]

    def test_29_render_manifest_uses_existing_renderer_api(self) -> None:
        make_variant(self.before_map, base_tiles())
        make_variant(self.after_map, base_tiles())
        assets = self.root / "assets"
        assets.mkdir()
        manifest = build_render_manifest(
            artifact_root=self.root,
            before_map_path=Path(self.before_map.name),
            after_map_path=Path(self.after_map.name),
            assets_root=Path(assets.name),
            lower=(300, 600, 7),
            upper=(301, 600, 7),
            output_directory=Path("renders"),
            context_tiles=1,
            execute=False,
        )
        self.assertEqual(manifest["format"], RENDER_MANIFEST_FORMAT)
        self.assertTrue(all(request["renderer"] == "tools/ai-agent/otbm_renderer.py:render_region" for request in manifest["requests"]))
        self.assertTrue(all("tools/ai-agent/otbm_render_tool.py" in request["command"] for request in manifest["requests"]))

    def test_30_map_sources_remain_unchanged(self) -> None:
        self.build(base_tiles(), base_tiles())
        before_hash = hashlib.sha256(self.before_map.read_bytes()).hexdigest()
        after_hash = hashlib.sha256(self.after_map.read_bytes()).hexdigest()
        report = self.analyze(before_map_path=self.before_map.name, after_map_path=self.after_map.name)
        self.assertFalse(report["policy"]["mapModified"])
        self.assertEqual(before_hash, hashlib.sha256(self.before_map.read_bytes()).hexdigest())
        self.assertEqual(after_hash, hashlib.sha256(self.after_map.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
