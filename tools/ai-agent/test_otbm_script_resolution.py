from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

from otbm_script_resolution import REPORT_FORMAT, build_report, scan_repository


class ScriptResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data/scripts").mkdir(parents=True)
        (self.root / "data-otservbr-global/scripts").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_lua(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_scan(self, placements: list[dict]) -> Path:
        path = self.root / "scan.json"
        path.write_text(
            json.dumps(
                {
                    "format": "canary-otbm-item-scan-v1",
                    "source": {"path": "fixture.otbm", "size": 1},
                    "mechanicPlacements": placements,
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_direct_range_numeric_loop_and_table_loop(self) -> None:
        self.write_lua(
            "data/scripts/fixture.lua",
            """
local action = Action()
action:aid(100, 101, 102)
action:uid(500)
action:register()

local movement = MoveEvent()
movement:type("stepin")
for id = 200, 202 do
    movement:aid(id)
end
movement:register()

local ids = { 300, 301, 302 }
local other = MoveEvent()
other:type("stepout")
for _, id in ipairs(ids) do
    other:aid(id)
end
other:register()
""",
        )
        scan = scan_repository(self.root)
        values = {(entry["namespace"], value) for entry in scan["registrations"] for value in entry["values"]}
        for expected in (("actionId", 100), ("actionId", 202), ("actionId", 302), ("uniqueId", 500)):
            self.assertIn(expected, values)

    def test_target_action_and_unique_references(self) -> None:
        self.write_lua(
            "data-otservbr-global/scripts/target.lua",
            """
local config = { [4202] = true, [4203] = true }
local action = Action()
function action.onUse(player, item, fromPosition, target)
    if target.actionid == 8026 then return true end
    if config[target.actionid] then return true end
    if target.uid == 3071 then return true end
end
action:id(1000)
action:register()
""",
        )
        scan = scan_repository(self.root)
        target_entries = [entry for entry in scan["registrations"] if entry["registrationType"] == "target-reference"]
        action_values = {value for entry in target_entries if entry["namespace"] == "actionId" for value in entry["values"]}
        unique_values = {value for entry in target_entries if entry["namespace"] == "uniqueId" for value in entry["values"]}
        self.assertTrue({4202, 4203, 8026}.issubset(action_values))
        self.assertIn(3071, unique_values)

    def test_xml_registration_and_step_pair_not_conflict(self) -> None:
        xml = self.root / "data/actions.xml"
        xml.write_text(
            '<root><action fromaid="700" toaid="702" script="x.lua" />'
            '<moveevent event="stepin" actionid="800" script="in.lua" />'
            '<moveevent event="stepout" actionid="800" script="out.lua" /></root>',
            encoding="utf-8",
        )
        scan_path = self.write_scan(
            [
                {"itemId": 1, "position": [1, 1, 7], "itemDepth": 0, "actionId": 700},
                {"itemId": 1, "position": [2, 1, 7], "itemDepth": 0, "actionId": 800},
            ]
        )
        report = build_report(self.root, scan_path)
        self.assertEqual(report["summary"]["conflicts"], 0)
        self.assertEqual(report["summary"]["unresolvedPlacements"], 0)

    def test_generic_engine_item_fallback_partial_and_dynamic(self) -> None:
        self.write_lua(
            "data/scripts/fallback.lua",
            """
local action = Action()
action:id(900)
action:register()
local dynamic = Action()
dynamic:aid(runtimeValue)
dynamic:register()
""",
        )
        scan_path = self.write_scan(
            [
                {"itemId": 1, "position": [1, 1, 7], "itemDepth": 0, "actionId": 2000},
                {"itemId": 900, "position": [2, 1, 7], "itemDepth": 0, "actionId": 999},
                {"itemId": 1, "position": [3, 1, 7], "itemDepth": 0, "teleportDestination": [4, 4, 7]},
                {"itemId": 1, "position": [4, 1, 7], "itemDepth": 0, "houseDoorId": 1},
                {"itemId": 1, "position": [5, 1, 7], "itemDepth": 0, "uniqueId": 123, "teleportDestination": [4, 4, 7]},
            ]
        )
        report = build_report(self.root, scan_path)
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["summary"]["dynamicRegistrations"], 1)
        statuses = report["summary"]["statusCounts"]
        self.assertEqual(statuses["handled-generically"], 1)
        self.assertEqual(statuses["handled-by-item-id"], 1)
        self.assertEqual(statuses["handled-by-engine"], 3)
        self.assertEqual(report["summary"]["partiallyResolvedPlacements"], 1)

    def test_real_conflict_same_dispatch_slot(self) -> None:
        self.write_lua(
            "data/scripts/a.lua",
            "local a = Action()\na:aid(1000)\na:register()\n",
        )
        self.write_lua(
            "data/scripts/b.lua",
            "local b = Action()\nb:aid(1000)\nb:register()\n",
        )
        scan_path = self.write_scan(
            [{"itemId": 1, "position": [1, 1, 7], "itemDepth": 0, "actionId": 1000}]
        )
        report = build_report(self.root, scan_path)
        self.assertEqual(report["summary"]["conflicts"], 1)
        self.assertFalse(report["ok"])


if __name__ == "__main__":
    unittest.main()
