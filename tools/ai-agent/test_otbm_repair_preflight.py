from __future__ import annotations

import json
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_binary import (
    ATTR_ACTION_ID,
    OTBM_ITEM,
    OTBM_MAP_DATA,
    OTBM_TILE,
    OTBM_TILE_AREA,
    encode_item_attributes,
    encode_node,
    encode_tile_properties,
)
from otbm_repair_preflight import (
    PreflightError,
    build_draft_plan,
    build_hypothetical_item_audit,
    build_preflight_report,
    correlate_candidates,
)
from otbm_repair_preflight_tool import main as preflight_main


def item_audit():
    return {
        "format": "canary-otbm-item-audit-v1",
        "mechanicPlacements": [
            {
                "itemId": 100,
                "position": [1025, 2050, 7],
                "itemDepth": 0,
                "actionId": 1000,
            },
            {
                "itemId": 101,
                "position": [1026, 2050, 7],
                "itemDepth": 1,
                "uniqueId": 2000,
                "actionId": 200,
            },
        ],
    }


def anchors():
    return {
        "format": "canary-otbm-patch-anchors-native-v1",
        "source": {
            "path": "world.otbm",
            "size": 123,
            "otbmVersion": 4,
            "itemsMajor": 3,
            "itemsMinor": 57,
        },
        "anchors": [
            {
                "position": [1025, 2050, 7],
                "tilePlacementIndex": 3,
                "itemId": 100,
                "itemDepth": 0,
                "attribute": "actionId",
                "value": 1000,
                "bytes": [],
            },
            {
                "position": [1026, 2050, 7],
                "tilePlacementIndex": 4,
                "itemId": 101,
                "itemDepth": 1,
                "attribute": "actionId",
                "value": 200,
                "bytes": [],
            },
            {
                "position": [1026, 2050, 7],
                "tilePlacementIndex": 4,
                "itemId": 101,
                "itemDepth": 1,
                "attribute": "uniqueId",
                "value": 2000,
                "bytes": [],
            },
        ],
    }


def resolution():
    return {
        "format": "canary-otbm-script-resolution-v1",
        "placements": [
            {
                "index": 0,
                "itemId": 100,
                "position": [1025, 2050, 7],
                "depth": 0,
                "status": "handled-directly",
                "resolutions": {"actionId": {"status": "handled-directly", "handlers": []}},
            },
            {
                "index": 1,
                "itemId": 101,
                "position": [1026, 2050, 7],
                "depth": 1,
                "status": "partially-resolved",
                "resolutions": {
                    "actionId": {"status": "handled-directly", "handlers": []},
                    "uniqueId": {"status": "unresolved"},
                },
            },
        ],
    }


def source():
    return {
        "fileName": "world.otbm",
        "sha256": "a" * 64,
        "size": 123,
        "otbmVersion": 4,
        "itemsMajor": 3,
        "itemsMinor": 57,
    }


class CorrelationTests(unittest.TestCase):
    def test_exact_selector_correlates_patch_identity_and_script_evidence(self):
        candidates = correlate_candidates(
            item_audit=item_audit(),
            anchor_report=anchors(),
            script_resolution=resolution(),
            selector={"position": [1025, 2050, 7], "actionId": 1000},
        )
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["anchorStatus"], "exact")
        self.assertEqual(candidates[0]["tilePlacementIndex"], 3)
        self.assertEqual(candidates[0]["scriptResolution"]["status"], "handled-directly")

    def test_unresolved_status_is_preserved(self):
        report = build_preflight_report(
            item_audit=item_audit(),
            anchor_report=anchors(),
            script_resolution=resolution(),
            selector={"uniqueId": 2000},
            source=source(),
        )
        self.assertEqual(report["candidates"][0]["scriptResolution"]["status"], "partially-resolved")
        self.assertEqual(report["summary"]["runtimeUnresolvedCandidates"], 1)
        self.assertTrue(report["review"]["unresolvedEvidencePreserved"])
        self.assertFalse(report["review"]["mapModified"])

    def test_duplicate_exact_placement_groups_are_ambiguous(self):
        duplicate = anchors()
        duplicate["anchors"].append(
            {
                "position": [1025, 2050, 7],
                "tilePlacementIndex": 9,
                "itemId": 100,
                "itemDepth": 0,
                "attribute": "actionId",
                "value": 1000,
                "bytes": [],
            }
        )
        candidates = correlate_candidates(
            item_audit=item_audit(),
            anchor_report=duplicate,
            script_resolution=resolution(),
            selector={"actionId": 1000},
        )
        self.assertEqual(candidates[0]["anchorStatus"], "ambiguous")
        self.assertIsNone(candidates[0]["tilePlacementIndex"])

    def test_duplicate_attribute_in_one_tile_placement_is_ambiguous(self):
        duplicate = anchors()
        duplicate["anchors"].append(
            {
                "position": [1025, 2050, 7],
                "tilePlacementIndex": 3,
                "itemId": 100,
                "itemDepth": 0,
                "attribute": "actionId",
                "value": 1000,
                "bytes": [],
            }
        )
        candidates = correlate_candidates(
            item_audit=item_audit(),
            anchor_report=duplicate,
            script_resolution=resolution(),
            selector={"actionId": 1000},
        )
        self.assertEqual(candidates[0]["anchorStatus"], "ambiguous")
        self.assertIsNone(candidates[0]["tilePlacementIndex"])

    def test_incomplete_script_resolution_is_rejected(self):
        script = resolution()
        script["placements"].pop()
        with self.assertRaisesRegex(PreflightError, "do not exactly cover"):
            correlate_candidates(
                item_audit=item_audit(),
                anchor_report=anchors(),
                script_resolution=script,
                selector={"actionId": 1000},
            )

    def test_mismatched_script_resolution_identity_is_rejected(self):
        script = resolution()
        script["placements"][0]["itemId"] = 999
        with self.assertRaisesRegex(PreflightError, "identity does not match"):
            correlate_candidates(
                item_audit=item_audit(),
                anchor_report=anchors(),
                script_resolution=script,
                selector={"actionId": 1000},
            )


class DraftPlanTests(unittest.TestCase):
    def test_builds_existing_phase8_plan_for_one_exact_anchor(self):
        report = build_preflight_report(
            item_audit=item_audit(),
            anchor_report=anchors(),
            script_resolution=resolution(),
            selector={"itemId": 100, "position": [1025, 2050, 7]},
            source=source(),
            operation_kind="set-action-id",
            replacement=1001,
            operation_id="repair-action",
        )
        self.assertTrue(report["summary"]["draftPlanReady"])
        plan = report["draftPlan"]
        self.assertEqual(plan["format"], "canary-otbm-bounded-patch-plan-v1")
        self.assertEqual(plan["region"]["from"], [1025, 2050, 7])
        self.assertEqual(plan["operations"][0]["tilePlacementIndex"], 3)
        self.assertEqual(plan["operations"][0]["expected"], 1000)
        self.assertEqual(plan["operations"][0]["replacement"], 1001)

    def test_rejects_plan_when_attribute_does_not_exist(self):
        candidates = correlate_candidates(
            item_audit=item_audit(),
            anchor_report=anchors(),
            script_resolution=resolution(),
            selector={"actionId": 1000},
        )
        with self.assertRaisesRegex(PreflightError, "existing uniqueId anchor"):
            build_draft_plan(
                candidate=candidates[0],
                source=source(),
                operation_kind="set-unique-id",
                replacement=2001,
                operation_id="bad",
            )

    def test_rejects_escape_width_change_before_plan_is_ready(self):
        audit = item_audit()
        audit["mechanicPlacements"][0]["actionId"] = 0x00FC
        anchor = anchors()
        anchor["anchors"][0]["value"] = 0x00FC
        report = build_preflight_report(
            item_audit=audit,
            anchor_report=anchor,
            script_resolution=resolution(),
            selector={"actionId": 0x00FC},
            source=source(),
            operation_kind="set-action-id",
            replacement=0x00FD,
        )
        self.assertFalse(report["summary"]["draftPlanReady"])
        self.assertIn("escape width", report["draftPlanError"])

    def test_multiple_candidates_do_not_guess_a_draft_plan(self):
        audit = item_audit()
        audit["mechanicPlacements"].append(
            {"itemId": 100, "position": [1027, 2050, 7], "itemDepth": 0, "actionId": 1000}
        )
        anchor = anchors()
        anchor["anchors"].append(
            {
                "position": [1027, 2050, 7],
                "tilePlacementIndex": 1,
                "itemId": 100,
                "itemDepth": 0,
                "attribute": "actionId",
                "value": 1000,
                "bytes": [],
            }
        )
        script = resolution()
        script["placements"].append(
            {
                "index": 2,
                "itemId": 100,
                "position": [1027, 2050, 7],
                "depth": 0,
                "status": "handled-directly",
                "resolutions": {},
            }
        )
        report = build_preflight_report(
            item_audit=audit,
            anchor_report=anchor,
            script_resolution=script,
            selector={"actionId": 1000},
            source=source(),
            operation_kind="set-action-id",
            replacement=1001,
        )
        self.assertEqual(report["summary"]["matchedCandidates"], 2)
        self.assertFalse(report["summary"]["draftPlanReady"])
        self.assertIn("exactly one matched candidate", report["draftPlanError"])

    def test_hypothetical_item_audit_changes_only_selected_existing_attribute(self):
        audit = item_audit()
        updated = build_hypothetical_item_audit(
            item_audit=audit,
            audit_index=0,
            operation_kind="set-action-id",
            replacement=1001,
        )
        self.assertEqual(updated["mechanicPlacements"][0]["actionId"], 1001)
        self.assertEqual(audit["mechanicPlacements"][0]["actionId"], 1000)
        self.assertEqual(updated["mechanicPlacements"][1], audit["mechanicPlacements"][1])

    def test_no_matches_remain_a_factual_report_not_a_guess(self):
        report = build_preflight_report(
            item_audit=item_audit(),
            anchor_report=anchors(),
            script_resolution=resolution(),
            selector={"actionId": 9999},
            source=source(),
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["matchedCandidates"], 0)
        self.assertIsNone(report["draftPlan"])


@unittest.skipUnless(shutil.which("c++") or shutil.which("g++"), "A C++ compiler is required")
class PreflightCliIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compiler = shutil.which("c++") or shutil.which("g++")
        cls.build = tempfile.TemporaryDirectory(prefix="otbm-repair-preflight-scanner-")
        cls.scanner = Path(cls.build.name) / "otbm_item_audit_scan"
        source_path = Path(__file__).with_name("otbm_item_audit_scan.cpp")
        completed = subprocess.run(
            [
                str(cls.compiler),
                "-O2",
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                str(source_path),
                "-o",
                str(cls.scanner),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or completed.stdout)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build.cleanup()

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="otbm-repair-preflight-cli-")
        self.root = Path(self.temporary.name)
        self.map_path = self.root / "fixture.otbm"
        self.appearances = self.root / "appearances.json"
        self.items_xml = self.root / "items.xml"
        self.repository = self.root / "repository"
        self.output = self.root / "preflight.json"
        self.plan = self.root / "draft-plan.json"
        self._write_fixture_map()
        self._write_metadata()
        self._write_script()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_fixture_map(self) -> None:
        item = encode_node(
            OTBM_ITEM,
            struct.pack("<H", 100) + encode_item_attributes([{"type": ATTR_ACTION_ID, "value": 1000}]),
        )
        tile = encode_node(
            OTBM_TILE,
            encode_tile_properties(
                node_type=OTBM_TILE,
                offset_x=44,
                offset_y=88,
                house_id=None,
                flags=0,
                inline_item_id=None,
            ),
            [item],
        )
        area = encode_node(OTBM_TILE_AREA, struct.pack("<HHB", 256, 512, 7), [tile])
        map_data = encode_node(OTBM_MAP_DATA, b"", [area])
        root = encode_node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
        self.map_path.write_bytes(b"\0\0\0\0" + root)

    def _write_metadata(self) -> None:
        self.appearances.write_text(
            json.dumps(
                {
                    "format": "canary-appearances-index-v1",
                    "ok": True,
                    "source": {"path": "appearances.dat", "size": 1, "sha256": "0" * 64},
                    "appearances": [
                        {
                            "category": "object",
                            "id": 100,
                            "name": "test action item",
                            "frameGroups": [],
                            "flags": {"usable": True},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.items_xml.write_text('<items><item id="100" name="test action item"/></items>', encoding="utf-8")

    def _write_script(self) -> None:
        script = self.repository / "data" / "scripts" / "actions" / "test_action.lua"
        script.parent.mkdir(parents=True)
        script.write_text(
            "local action = Action()\n"
            "function action.onUse(player, item, fromPosition, target, toPosition, isHotkey)\n"
            "    return true\n"
            "end\n"
            "action:aid(1000)\n"
            "action:register()\n",
            encoding="utf-8",
        )

    def test_cli_reuses_real_scanner_resolver_and_leaves_map_unchanged(self) -> None:
        original = self.map_path.read_bytes()
        result = preflight_main(
            [
                str(self.map_path),
                "--scanner",
                str(self.scanner),
                "--appearances-index",
                str(self.appearances),
                "--items-xml",
                str(self.items_xml),
                "--repository-root",
                str(self.repository),
                "--script-root",
                "data",
                "--position",
                "300,600,7",
                "--action-id",
                "1000",
                "--operation-kind",
                "set-action-id",
                "--replacement",
                "1001",
                "--output",
                str(self.output),
                "--draft-plan",
                str(self.plan),
                "--timeout",
                "60",
            ]
        )
        self.assertEqual(result, 0)
        self.assertEqual(self.map_path.read_bytes(), original)
        report = json.loads(self.output.read_text(encoding="utf-8"))
        plan = json.loads(self.plan.read_text(encoding="utf-8"))
        self.assertEqual(report["format"], "canary-otbm-repair-preflight-v1")
        self.assertEqual(report["summary"]["matchedCandidates"], 1)
        self.assertEqual(report["candidates"][0]["anchorStatus"], "exact")
        self.assertEqual(report["candidates"][0]["tilePlacementIndex"], 0)
        self.assertEqual(report["candidates"][0]["scriptResolution"]["status"], "handled-directly")
        self.assertEqual(report["replacementScriptResolution"]["afterStatus"], "unresolved")
        self.assertFalse(report["review"]["mapModified"])
        self.assertEqual(plan["operations"][0]["expected"], 1000)
        self.assertEqual(plan["operations"][0]["replacement"], 1001)

    def test_cli_rejects_report_path_equal_to_source_map(self) -> None:
        with self.assertRaises(SystemExit):
            preflight_main(
                [
                    str(self.map_path),
                    "--scanner",
                    str(self.scanner),
                    "--appearances-index",
                    str(self.appearances),
                    "--items-xml",
                    str(self.items_xml),
                    "--repository-root",
                    str(self.repository),
                    "--script-root",
                    "data",
                    "--action-id",
                    "1000",
                    "--output",
                    str(self.map_path),
                ]
            )


if __name__ == "__main__":
    unittest.main()
