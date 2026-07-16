from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_region_merge_planner import analyze_region_merge_plan
from otbm_region_merge_planner_tool import _write_report
from otbm_world_index import build_world_index
from test_otbm_semantic_diff import make_variant


class RegionMergePlannerTests(unittest.TestCase):
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
        self.current_map = self.root / "current.otbm"
        self.donor_map = self.root / "donor.otbm"
        self.current_index = self.root / "current.widx"
        self.donor_index = self.root / "donor.widx"
        self.current_manifest = self.root / "current.widx.json"
        self.donor_manifest = self.root / "donor.widx.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _valid_variant(tiles: list[dict[str, object]]) -> list[dict[str, object]]:
        prepared: list[dict[str, object]] = json.loads(json.dumps(tiles))
        if not any(isinstance(tile.get("items"), list) and tile["items"] for tile in prepared):
            prepared.append({"x": 499, "ground": 100, "items": [{"id": 200}]})
        return prepared

    def build(self, current_tiles: list[dict[str, object]], donor_tiles: list[dict[str, object]]) -> None:
        make_variant(self.current_map, self._valid_variant(current_tiles))
        make_variant(self.donor_map, self._valid_variant(donor_tiles))
        build_world_index(
            map_path=self.current_map,
            scanner=self.scanner,
            output=self.current_index,
            manifest_output=self.current_manifest,
        )
        build_world_index(
            map_path=self.donor_map,
            scanner=self.scanner,
            output=self.donor_index,
            manifest_output=self.donor_manifest,
        )

    def analyze(self, **kwargs: object) -> dict[str, object]:
        return analyze_region_merge_plan(
            artifact_root=self.root,
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            donor_from=(300, 600, 7),
            donor_to=(301, 600, 7),
            target_origin=(400, 600, 7),
            **kwargs,
        )

    @staticmethod
    def action_kinds(report: dict[str, object]) -> dict[str, int]:
        return report["summary"]["actions"]["byKind"]  # type: ignore[index,return-value]

    @staticmethod
    def conflict_kinds(report: dict[str, object]) -> dict[str, int]:
        return report["summary"]["conflicts"]["byKind"]  # type: ignore[index,return-value]

    def test_translation_adds_donor_tile_without_writing_maps(self) -> None:
        self.build([], [{"x": 300, "ground": 100, "items": [{"id": 200}]}])
        current_before = self.current_map.read_bytes()
        donor_before = self.donor_map.read_bytes()
        report = self.analyze()
        self.assertEqual(self.action_kinds(report), {"add": 1})
        self.assertEqual(report["translation"]["delta"], [100, 0, 0])  # type: ignore[index]
        self.assertFalse(report["writerReady"])
        self.assertEqual(self.current_map.read_bytes(), current_before)
        self.assertEqual(self.donor_map.read_bytes(), donor_before)

    def test_delta_zero_with_internal_teleport_is_unchanged(self) -> None:
        tiles = [
            {
                "x": 300,
                "ground": 100,
                "items": [{"id": 202, "teleport": (301, 600, 7)}],
            },
            {"x": 301, "ground": 100, "items": [{"id": 200}]},
        ]
        self.build(tiles, tiles)
        report = analyze_region_merge_plan(
            artifact_root=self.root,
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            donor_from=(300, 600, 7),
            donor_to=(301, 600, 7),
            target_origin=(300, 600, 7),
        )
        self.assertEqual(self.action_kinds(report), {"unchanged": 2})
        self.assertEqual(report["summary"]["conflicts"]["total"], 0)  # type: ignore[index]

    def test_replace_region_emits_delete_candidate_for_current_only_tile(self) -> None:
        self.build(
            [{"x": 400, "ground": 100}, {"x": 401, "ground": 100}],
            [{"x": 300, "ground": 100}],
        )
        report = self.analyze(policy="replace-region")
        self.assertEqual(self.action_kinds(report), {"delete-candidate": 1, "unchanged": 1})
        self.assertEqual(self.conflict_kinds(report), {"current-content-delete-candidate": 1})
        self.assertTrue(report["requiresHumanReview"])

    def test_overlay_preserves_current_only_tile(self) -> None:
        self.build(
            [{"x": 400, "ground": 100}, {"x": 401, "ground": 100}],
            [{"x": 300, "ground": 100}],
        )
        report = self.analyze(policy="overlay")
        self.assertEqual(self.action_kinds(report), {"preserve-current-only": 1, "unchanged": 1})
        self.assertEqual(report["summary"]["conflicts"]["total"], 0)  # type: ignore[index]

    def test_global_unique_id_collision_outside_target_region_is_blocking(self) -> None:
        self.build(
            [{"x": 350, "ground": 100, "items": [{"id": 205, "unique": 6000}]}],
            [{"x": 300, "ground": 100, "items": [{"id": 205, "unique": 6000}]}],
        )
        report = self.analyze()
        self.assertEqual(self.conflict_kinds(report), {"unique-id-collision": 1})
        self.assertEqual(report["summary"]["blockingConflicts"], 1)  # type: ignore[index]
        self.assertFalse(report["ok"])

    def test_action_id_reuse_without_resolution_evidence_is_unresolved(self) -> None:
        self.build(
            [{"x": 350, "ground": 100, "items": [{"id": 200, "action": 1000}]}],
            [{"x": 300, "ground": 100, "items": [{"id": 200, "action": 1000}]}],
        )
        report = self.analyze()
        self.assertEqual(self.conflict_kinds(report), {"action-id-reuse-unresolved": 1})
        self.assertFalse(report["ok"])

    def test_action_id_reuse_same_handler_is_review_not_blocking(self) -> None:
        self.build(
            [{"x": 350, "ground": 100, "items": [{"id": 200, "action": 1000}]}],
            [{"x": 300, "ground": 100, "items": [{"id": 200, "action": 1000}]}],
        )
        report_document = {
            "format": "canary-otbm-script-resolution-v1",
            "identifiers": {
                "actionId": [
                    {
                        "value": 1000,
                        "status": "handled-directly",
                        "handlers": [
                            {
                                "eventType": "Action:onUse",
                                "handler": "doorAction",
                                "mode": "literal",
                                "generic": False,
                                "origin": "lua",
                                "source": {"path": "data/scripts/actions/door.lua", "line": 10},
                            }
                        ],
                    }
                ],
                "uniqueId": [],
            },
        }
        current_report = self.root / "current-script.json"
        donor_report = self.root / "donor-script.json"
        current_report.write_text(json.dumps(report_document), encoding="utf-8")
        donor_report.write_text(json.dumps(report_document), encoding="utf-8")
        report = self.analyze(
            current_script_resolution_path=Path(current_report.name),
            donor_script_resolution_path=Path(donor_report.name),
        )
        self.assertEqual(self.conflict_kinds(report), {"action-id-reuse-same-handler": 1})
        self.assertEqual(report["summary"]["blockingConflicts"], 0)  # type: ignore[index]
        self.assertTrue(report["ok"])

    def test_internal_teleport_destination_is_translated(self) -> None:
        self.build(
            [],
            [
                {
                    "x": 300,
                    "ground": 100,
                    "items": [{"id": 202, "teleport": (301, 600, 7)}],
                },
                {"x": 301, "ground": 100},
            ],
        )
        report = self.analyze()
        add_actions = [entry for entry in report["actions"] if entry["kind"] == "add"]  # type: ignore[index]
        source_action = next(entry for entry in add_actions if entry["position"] == [400, 600, 7])
        placement = source_action["proposed"]["placements"][1]
        self.assertEqual(placement["donorTeleportDestination"], [301, 600, 7])
        self.assertEqual(placement["teleportDestination"], [401, 600, 7])
        self.assertNotIn("teleport-destination-missing-after-plan", self.conflict_kinds(report))

    def test_external_teleport_without_current_destination_is_blocking(self) -> None:
        self.build(
            [],
            [{"x": 300, "ground": 100, "items": [{"id": 202, "teleport": (310, 620, 7)}]}],
        )
        report = self.analyze()
        self.assertEqual(self.conflict_kinds(report), {"external-teleport-destination-missing-current": 1})
        self.assertFalse(report["ok"])

    def test_target_translation_overflow_fails_closed(self) -> None:
        self.build([], [{"x": 300, "ground": 100}, {"x": 301, "ground": 100}])
        with self.assertRaisesRegex(Exception, "outside the OTBM coordinate range"):
            self.analyze(target_origin=(65535, 600, 7))

    def test_action_samples_are_bounded_but_totals_are_exact(self) -> None:
        donor = [
            {"x": 300, "ground": 100},
            {"x": 301, "ground": 100},
        ]
        self.build([], donor)
        report = self.analyze(sample_limit=1)
        self.assertEqual(report["summary"]["actions"]["total"], 2)  # type: ignore[index]
        self.assertEqual(report["summary"]["actions"]["sampled"], 1)  # type: ignore[index]
        self.assertTrue(report["summary"]["actions"]["truncated"])  # type: ignore[index]

    def test_report_output_does_not_overwrite_without_flag(self) -> None:
        output = self.root / "plan.json"
        output.write_text("sentinel", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            _write_report(
                Path(output.name),
                {"format": "test"},
                artifact_root=self.root,
                overwrite=False,
            )
        self.assertEqual(output.read_text(encoding="utf-8"), "sentinel")


if __name__ == "__main__":
    unittest.main()
