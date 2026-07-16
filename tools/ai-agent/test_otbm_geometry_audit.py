from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_geometry_audit import GeometryAuditError, analyze_index_paths, write_report
from otbm_geometry_audit_render import RENDER_FORMAT, build_render_manifest
from otbm_geometry_audit_types import RULES_FORMAT
from otbm_world_index import build_world_index
from test_otbm_world_index import (
    ATTR_ITEM,
    ATTR_TILE_FLAGS,
    OTBM_HOUSETILE,
    OTBM_MAP_DATA,
    OTBM_TILE,
    OTBM_TILE_AREA,
    item,
    node,
)


def make_map(path: Path, tiles: list[dict[str, object]]) -> None:
    base_x, base_y, floor = 256, 512, 7
    tile_nodes: list[bytes] = []
    for spec in tiles:
        x = int(spec["x"])
        y = int(spec["y"])
        properties = bytes((x - base_x, y - base_y))
        tile_type = OTBM_TILE
        if "house" in spec:
            properties += struct.pack("<I", int(spec["house"]))
            tile_type = OTBM_HOUSETILE
        flags = int(spec.get("flags", 0))
        if flags:
            properties += bytes((ATTR_TILE_FLAGS,)) + struct.pack("<I", flags)
        ground = spec.get("ground", 100)
        if ground is not None:
            properties += bytes((ATTR_ITEM,)) + struct.pack("<H", int(ground))
        raw_items = list(spec.get("items", []))  # type: ignore[arg-type]
        if not raw_items:
            raw_items.append(200)
        children = [item(int(item_id)) for item_id in raw_items]
        tile_nodes.append(node(tile_type, properties, children))
    area = node(OTBM_TILE_AREA, struct.pack("<HHB", base_x, base_y, floor), tile_nodes)
    map_data = node(OTBM_MAP_DATA, b"", [area])
    root = node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


def clean_tiles() -> list[dict[str, object]]:
    return [
        {"x": 300, "y": 600, "ground": 100},
        {"x": 301, "y": 600, "ground": 100},
        {"x": 300, "y": 601, "ground": 100},
        {"x": 301, "y": 601, "ground": 100},
    ]


class GeometryAuditTests(unittest.TestCase):
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
        self.map = self.root / "map.otbm"
        self.index = self.root / "map.widx"
        self.manifest = self.root / "map.widx.json"
        self.appearances = self.root / "appearances.json"
        self.rules = self.root / "rules.json"
        self.appearances.write_text(
            json.dumps(
                {
                    "format": "canary-appearances-index-v1",
                    "ok": True,
                    "appearances": [
                        {"category": "object", "id": 100, "flags": {"bank": {}}, "frameGroups": [{"spriteInfo": {"spriteIds": [1000]}}]},
                        {"category": "object", "id": 101, "flags": {"bank": {}}, "frameGroups": [{"spriteInfo": {"spriteIds": [1001]}}]},
                        {"category": "object", "id": 200, "flags": {}, "frameGroups": [{"spriteInfo": {"spriteIds": [1200]}}]},
                        {"category": "object", "id": 300, "flags": {"unpassable": True}, "frameGroups": [{"spriteInfo": {"spriteIds": []}}]},
                        {"category": "object", "id": 301, "flags": {"unpassable": True}, "frameGroups": [{"spriteInfo": {"spriteIds": [1301]}}]},
                        {"category": "object", "id": 400, "flags": {}, "frameGroups": [{"spriteInfo": {"spriteIds": [1400]}}]},
                        {"category": "object", "id": 401, "flags": {}, "frameGroups": [{"spriteInfo": {"spriteIds": [1401]}}]},
                    ],
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def build(self, tiles: list[dict[str, object]]) -> None:
        make_map(self.map, tiles)
        build_world_index(map_path=self.map, scanner=self.scanner, output=self.index, manifest_output=self.manifest)

    def analyze(self, **kwargs: object) -> dict[str, object]:
        return analyze_index_paths(
            artifact_root=self.root,
            index_path=Path(self.index.name),
            manifest_path=Path(self.manifest.name),
            appearances_path=Path(self.appearances.name),
            lower=(299, 599, 7),
            upper=(305, 605, 7),
            sample_limit=1000,
            orphan_max_tiles=1,
            **kwargs,
        )

    @staticmethod
    def kinds(report: dict[str, object]) -> list[str]:
        return [entry["kind"] for entry in report["findings"]]  # type: ignore[index]

    def test_01_clean_connected_region(self) -> None:
        self.build(clean_tiles())
        report = self.analyze()
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["findings"]["total"], 0)  # type: ignore[index]

    def test_02_item_without_floor_is_error(self) -> None:
        self.build([{"x": 300, "y": 600, "ground": None, "items": [200]}])
        report = self.analyze()
        self.assertFalse(report["ok"])
        self.assertIn("item-without-floor", self.kinds(report))

    def test_03_multiple_ground_is_warning(self) -> None:
        self.build([{"x": 300, "y": 600, "ground": 100, "items": [101]}])
        self.assertIn("multiple-ground-items", self.kinds(self.analyze()))

    def test_04_unknown_appearance_is_explicit(self) -> None:
        self.build([{"x": 300, "y": 600, "ground": 100, "items": [999]}])
        self.assertIn("unknown-appearance", self.kinds(self.analyze()))

    def test_05_unpassable_without_sprite_is_candidate(self) -> None:
        self.build([{"x": 300, "y": 600, "ground": 100, "items": [300]}])
        report = self.analyze()
        finding = next(entry for entry in report["findings"] if entry["kind"] == "invisible-blocker-candidate")  # type: ignore[index]
        self.assertEqual(finding["confidence"], "low")

    def test_06_unpassable_with_sprite_is_not_invisible_candidate(self) -> None:
        self.build([{"x": 300, "y": 600, "ground": 100, "items": [301]}])
        self.assertNotIn("invisible-blocker-candidate", self.kinds(self.analyze()))

    def test_07_small_disconnected_component_is_reported(self) -> None:
        self.build(clean_tiles() + [{"x": 304, "y": 604, "ground": 100}])
        self.assertIn("orphan-tile-component", self.kinds(self.analyze()))

    def test_08_disconnected_house_components(self) -> None:
        self.build([
            {"x": 300, "y": 600, "house": 77, "ground": 100},
            {"x": 304, "y": 604, "house": 77, "ground": 100},
        ])
        self.assertIn("house-disconnected-components", self.kinds(self.analyze()))

    def test_09_house_component_mixed_pz(self) -> None:
        self.build([
            {"x": 300, "y": 600, "house": 77, "flags": 1, "ground": 100},
            {"x": 301, "y": 600, "house": 77, "ground": 100},
        ])
        self.assertIn("house-component-mixed-pz", self.kinds(self.analyze()))

    def test_10_isolated_pz_tile(self) -> None:
        self.build([{"x": 300, "y": 600, "flags": 1, "ground": 100}])
        self.assertIn("isolated-pz-tile", self.kinds(self.analyze()))

    def test_11_pz_enclosed_gap(self) -> None:
        self.build([
            {"x": 301, "y": 601, "ground": 100},
            {"x": 301, "y": 600, "flags": 1, "ground": 100},
            {"x": 302, "y": 601, "flags": 1, "ground": 100},
            {"x": 301, "y": 602, "flags": 1, "ground": 100},
            {"x": 300, "y": 601, "flags": 1, "ground": 100},
        ])
        self.assertIn("pz-enclosed-gap", self.kinds(self.analyze()))

    def write_rules(self) -> None:
        self.rules.write_text(json.dumps({
            "format": RULES_FORMAT,
            "schemaVersion": 1,
            "adjacencyRules": [{
                "id": "stone-wall-east",
                "category": "wall",
                "sourceItemIds": [400],
                "direction": "east",
                "requiredNeighborItemIds": [401],
                "severity": "warning",
                "confidence": "high",
                "message": "Stone wall requires its reviewed east neighbor",
            }],
        }, sort_keys=True), encoding="utf-8")

    def test_12_reviewed_wall_rule_passes(self) -> None:
        self.write_rules()
        self.build([
            {"x": 300, "y": 600, "ground": 100, "items": [400]},
            {"x": 301, "y": 600, "ground": 100, "items": [401]},
        ])
        self.assertNotIn("wall-adjacency-mismatch", self.kinds(self.analyze(rules_path=Path(self.rules.name))))

    def test_13_reviewed_wall_rule_fails(self) -> None:
        self.write_rules()
        self.build([{"x": 300, "y": 600, "ground": 100, "items": [400]}])
        self.assertIn("wall-adjacency-mismatch", self.kinds(self.analyze(rules_path=Path(self.rules.name))))

    def test_14_rules_are_optional_and_not_inferred(self) -> None:
        self.build([{"x": 300, "y": 600, "ground": 100, "items": [400]}])
        self.assertNotIn("wall-adjacency-mismatch", self.kinds(self.analyze()))

    def test_15_invalid_rule_direction_fails_closed(self) -> None:
        self.write_rules()
        document = json.loads(self.rules.read_text(encoding="utf-8"))
        document["adjacencyRules"][0]["direction"] = "up"
        self.rules.write_text(json.dumps(document), encoding="utf-8")
        self.build(clean_tiles())
        with self.assertRaises(GeometryAuditError):
            self.analyze(rules_path=Path(self.rules.name))

    def test_16_index_hash_mismatch_fails_closed(self) -> None:
        self.build(clean_tiles())
        document = json.loads(self.manifest.read_text(encoding="utf-8"))
        document["index"]["sha256"] = "0" * 64
        self.manifest.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaises(GeometryAuditError):
            self.analyze()

    def test_17_path_escape_is_rejected(self) -> None:
        self.build(clean_tiles())
        with self.assertRaises(GeometryAuditError):
            analyze_index_paths(
                artifact_root=self.root,
                index_path=Path("../outside.widx"),
                manifest_path=Path(self.manifest.name),
                appearances_path=Path(self.appearances.name),
                lower=(299, 599, 7),
                upper=(305, 605, 7),
            )

    def test_18_output_overwrite_and_symlink_safety(self) -> None:
        self.build(clean_tiles())
        report = self.analyze()
        output = Path("report.json")
        write_report(report, artifact_root=self.root, output_path=output)
        with self.assertRaises(GeometryAuditError):
            write_report(report, artifact_root=self.root, output_path=output)
        write_report(report, artifact_root=self.root, output_path=output, overwrite=True)
        if hasattr(os, "symlink"):
            target = self.root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = self.root / "link.json"
            try:
                link.symlink_to(target)
            except OSError:
                return
            with self.assertRaises(GeometryAuditError):
                write_report(report, artifact_root=self.root, output_path=Path(link.name), overwrite=True)

    def test_19_render_manifest_uses_existing_tool_commands(self) -> None:
        self.build([{"x": 300, "y": 600, "ground": None, "items": [200]}])
        manifest = build_render_manifest(
            self.analyze(), map_path=self.map, assets_path=self.root / "assets", output_dir=self.root / "renders"
        )
        self.assertEqual(manifest["format"], RENDER_FORMAT)
        self.assertEqual(manifest["requestCount"], 1)
        self.assertIn("tools/ai-agent/otbm_render_tool.py", manifest["requests"][0]["command"])

    def test_20_report_is_deterministic(self) -> None:
        self.build(clean_tiles() + [{"x": 304, "y": 604, "ground": 100}])
        first = self.analyze()
        second = self.analyze()
        self.assertEqual(json.dumps(first, sort_keys=True, separators=(",", ":")), json.dumps(second, sort_keys=True, separators=(",", ":")))

    def test_21_region_limit_fails_closed(self) -> None:
        self.build(clean_tiles())
        with self.assertRaises(GeometryAuditError):
            analyze_index_paths(
                artifact_root=self.root,
                index_path=Path(self.index.name),
                manifest_path=Path(self.manifest.name),
                appearances_path=Path(self.appearances.name),
                lower=(0, 0, 0),
                upper=(2000, 2000, 15),
            )


if __name__ == "__main__":
    unittest.main()
