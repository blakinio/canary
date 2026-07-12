from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_DIR = Path(__file__).parent
sys.path.insert(0, str(MODULE_DIR))

from otbm_script_resolution import (
    REPORT_FORMAT,
    REVIEW_FORMAT,
    build_script_audit,
    load_review_rules,
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placement(
    item_id: int,
    *,
    action_id: int | None = None,
    unique_id: int | None = None,
    teleport: list[int] | None = None,
    house_door: int | None = None,
    x: int = 100,
) -> dict[str, object]:
    result: dict[str, object] = {
        "itemId": item_id,
        "position": [x, 200, 7],
        "itemDepth": 0,
    }
    if action_id is not None:
        result["actionId"] = action_id
    if unique_id is not None:
        result["uniqueId"] = unique_id
    if teleport is not None:
        result["teleportDestination"] = teleport
    if house_door is not None:
        result["houseDoorId"] = house_door
    return result


def item_audit(mechanics: list[dict[str, object]]) -> dict[str, object]:
    ids = sorted({int(entry["itemId"]) for entry in mechanics})
    items = []
    for item_id in ids:
        category = "door" if item_id == 900 else "item"
        item_type = "door" if item_id == 900 else None
        items.append(
            {
                "id": item_id,
                "itemsXml": {
                    "id": item_id,
                    "name": "fixture",
                    "type": item_type,
                    "category": category,
                    "attributes": {},
                },
            }
        )
    return {
        "format": "canary-otbm-item-audit-v1",
        "sources": {"map": "fixture.otbm"},
        "mechanicPlacements": mechanics,
        "mapMechanicItems": items,
    }


class ScriptResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        write(
            self.root / "data/scripts/actions/direct.lua",
            """
local direct = Action()
direct:aid(100)
direct:uid(200)
direct:register()

local stepIn = MoveEvent()
stepIn:type("stepin")
stepIn:aid(300)
stepIn:register()

local stepOut = MoveEvent()
stepOut:type("stepout")
stepOut:aid(300)
stepOut:register()

local ranged = MoveEvent()
ranged:type("stepin")
for aid = 400, 402 do
    ranged:aid(aid)
end
ranged:register()

local ids = { 501, 502 }
local tableAction = Action()
for _, value in ipairs(ids) do
    tableAction:aid(value)
end
tableAction:register()

local dynamic = Action()
dynamic:aid(config.dynamicAid)
dynamic:register()
""",
        )
        write(
            self.root / "data-otservbr-global/scripts/quests/target.lua",
            """
local config = {
    [600] = true,
    [601] = true,
}
local targetAction = Action()
function targetAction.onUse(player, item, fromPosition, target)
    if config[target.actionid] then
        return true
    elseif target.actionid >= 610 and target.actionid <= 612 then
        return true
    end
    return false
end
targetAction:id(850)
targetAction:register()

local quest = Action()
quest:aid(2000)
quest:register()
""",
        )
        write(
            self.root / "data-canary/scripts/actions/inactive.lua",
            """
local inactive = Action()
inactive:aid(9999)
inactive:register()
""",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_resolves_direct_ranges_tables_targets_fallback_and_engine_mechanics(self) -> None:
        mechanics = [
            placement(10, action_id=100, x=100),
            placement(11, unique_id=200, x=101),
            placement(12, action_id=300, x=102),
            placement(13, action_id=401, x=103),
            placement(14, action_id=502, x=104),
            placement(850, action_id=600, x=105),
            placement(850, action_id=611, x=106),
            placement(15, action_id=2000, unique_id=700, x=107),
            placement(900, action_id=800, x=108),
            placement(900, unique_id=801, x=109),
            placement(16, teleport=[110, 210, 8], x=110),
            placement(17, house_door=3, x=111),
        ]
        report = build_script_audit(item_audit=item_audit(mechanics), repository_root=self.root)
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["unreviewedIdentifiers"], 0)
        self.assertEqual(report["summary"]["conflictingPlacements"], 0)
        self.assertGreater(report["summary"]["unresolvedDynamicRegistrations"], 0)

        statuses = {entry["actionId"]: entry["status"] for entry in report["placements"] if entry.get("actionId")}
        self.assertEqual(statuses[100], "handled-directly")
        self.assertEqual(statuses[300], "handled-directly")
        self.assertEqual(statuses[401], "handled-by-range")
        self.assertEqual(statuses[502], "handled-directly")
        self.assertEqual(statuses[600], "handled-as-target")
        self.assertEqual(statuses[611], "handled-as-target")
        self.assertEqual(statuses[800], "handled-by-item-id")

        by_x = {entry["position"][0]: entry for entry in report["placements"]}
        self.assertEqual(by_x[107]["resolutions"]["uniqueId"]["status"], "handled-by-fallback")
        self.assertEqual(by_x[109]["resolutions"]["uniqueId"]["status"], "handled-by-item-id")
        self.assertEqual(by_x[110]["status"], "handled-by-engine")
        self.assertEqual(by_x[111]["status"], "handled-by-engine")

        ids = {entry["value"]: entry for entry in report["identifiers"]["actionId"]}
        self.assertNotIn(9999, ids, "inactive alternative datapack must not be scanned")

    def test_same_moveevent_id_for_stepin_and_stepout_is_not_a_conflict(self) -> None:
        report = build_script_audit(
            item_audit=item_audit([placement(12, action_id=300)]),
            repository_root=self.root,
        )
        self.assertEqual(report["summary"]["conflictingPlacements"], 0)
        handlers = report["placements"][0]["handlers"]
        self.assertEqual({handler["eventType"] for handler in handlers}, {"MoveEvent:stepin", "MoveEvent:stepout"})

    def test_real_conflict_is_reported(self) -> None:
        write(
            self.root / "data/scripts/actions/conflict.lua",
            """
local first = Action()
first:aid(9000)
first:register()
local second = Action()
second:aid(9000)
second:register()
""",
        )
        report = build_script_audit(
            item_audit=item_audit([placement(20, action_id=9000)]),
            repository_root=self.root,
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["conflictingPlacements"], 1)
        self.assertEqual(report["placements"][0]["status"], "conflicting")

    def test_review_rule_preserves_unresolved_identifier_without_claiming_runtime_handler(self) -> None:
        mechanics = [placement(21, action_id=12345)]
        unresolved = build_script_audit(item_audit=item_audit(mechanics), repository_root=self.root)
        self.assertFalse(unresolved["ok"])
        self.assertEqual(unresolved["summary"]["unreviewedIdentifiers"], 1)

        rules_path = self.root / "review.json"
        rules_path.write_text(
            json.dumps(
                {
                    "format": REVIEW_FORMAT,
                    "rules": [
                        {
                            "namespace": "actionId",
                            "values": [12345],
                            "disposition": "needs-manual-review",
                            "reason": "Fixture has no runtime handler; preserve it for explicit gameplay review.",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        reviewed = build_script_audit(
            item_audit=item_audit(mechanics),
            repository_root=self.root,
            review_rules=load_review_rules(rules_path),
        )
        self.assertTrue(reviewed["ok"])
        self.assertEqual(reviewed["summary"]["runtimeUnresolvedIdentifiers"], 1)
        self.assertEqual(reviewed["summary"]["unreviewedIdentifiers"], 0)
        identifier = reviewed["identifiers"]["actionId"][0]
        self.assertEqual(identifier["status"], "unresolved")
        self.assertEqual(identifier["review"]["disposition"], "needs-manual-review")


if __name__ == "__main__":
    unittest.main()
