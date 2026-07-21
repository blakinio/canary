from __future__ import annotations

import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
SCENARIO_PATH = ROOT / "tests" / "e2e" / "scenarios" / "npc" / "quentin-adventurer-stone.json"
QUENTIN_PATH = ROOT / "data-otservbr-global" / "npc" / "quentin.lua"
NPC_SPAWNS_PATH = ROOT / "data-otservbr-global" / "world" / "otservbr-npc.xml"
OBSERVER_PATH = ROOT / "tools" / "e2e" / "client" / "quentin_adventurer_stone.lua"
NPC_HANDLER_PATH = ROOT / "data" / "npclib" / "npc_system" / "npc_handler.lua"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("test_e2e_quentin_adventurer_stone_runner", RUNNER_PATH)


class QuentinAdventurerStoneEvidenceTests(unittest.TestCase):
    def test_current_spawn_is_adjacent_to_default_fixture_start(self) -> None:
        root = ET.parse(NPC_SPAWNS_PATH).getroot()
        positions: list[tuple[int, int, int]] = []
        for spawn in root.findall("npc"):
            center_x = int(spawn.attrib["centerx"])
            center_y = int(spawn.attrib["centery"])
            for npc in spawn.findall("npc"):
                if npc.attrib.get("name") != "Quentin":
                    continue
                positions.append(
                    (
                        center_x + int(npc.attrib.get("x", "0")),
                        center_y + int(npc.attrib.get("y", "0")),
                        int(npc.attrib["z"]),
                    )
                )

        self.assertEqual(positions, [(32368, 32240, 7)])
        fixture_start = (32369, 32241, 7)
        quentin = positions[0]
        self.assertEqual(quentin[2], fixture_start[2])
        self.assertEqual(max(abs(quentin[0] - fixture_start[0]), abs(quentin[1] - fixture_start[1])), 1)

    def test_current_quentin_source_owns_free_stone_reward(self) -> None:
        source = QUENTIN_PATH.read_text(encoding="utf-8")

        self.assertIn('addKeyword({ "adventurer stone" }', source)
        self.assertIn('stoneKeyword:addChildKeyword({ "yes" }', source)
        self.assertIn("player:addItem(16277, 1)", source)
        self.assertIn("Storage.Quest.U9_80.AdventurersGuild.FreeStone.Quentin", source)
        self.assertIn("player:setStorageValue(Storage.Quest.U9_80.AdventurersGuild.FreeStone.Quentin, 1)", source)

    def test_focused_npc_handler_requires_private_npc_message_mode(self) -> None:
        source = NPC_HANDLER_PATH.read_text(encoding="utf-8")

        self.assertIn("self:checkInteraction(npc, player) and msgtype == TALKTYPE_PRIVATE_PN", source)

    def test_feature_adapter_reuses_generic_driver_and_drives_response_gated_private_dialogue(self) -> None:
        source = OBSERVER_PATH.read_text(encoding="utf-8")

        self.assertIn('name ~= "Quentin"', source)
        self.assertIn('contains = "Welcome, young"', source)
        self.assertIn('contains = "replace your adventurer\'s stone for free"', source)
        self.assertIn('contains = "Here you are. Take care."', source)
        self.assertIn('nextMessage = "adventurer stone"', source)
        self.assertIn('nextMessage = "yes"', source)
        self.assertIn('g_game.talkPrivate(MessageModes.NpcTo, "Quentin", text)', source)
        self.assertIn('appendEvent("quentin_talk_received", text)', source)
        self.assertIn('io.open(GENERIC_DRIVER_PATH, "r")', source)
        self.assertIn('loadstring(source, "@" .. GENERIC_DRIVER_PATH)', source)
        self.assertNotIn("dofile(", source)

    def test_scenario_uses_greeting_plus_response_markers_and_database_persistence(self) -> None:
        scenario = runner.validate_scenario(SCENARIO_PATH, ROOT)
        data = scenario.data
        steps = data["steps"]

        self.assertEqual(data["suite"], "npc")
        self.assertEqual(data["fixture"]["character"], "Knight 1")
        self.assertEqual(data["client"]["automation"], "tools/e2e/client/quentin_adventurer_stone.lua")
        self.assertEqual(
            [(step["action"], step.get("text")) for step in steps if step["action"] == "talk"],
            [("talk", "hi")],
        )
        self.assertEqual(steps[0]["action"], "wait_creature")
        self.assertEqual(steps[0]["creature"], "Quentin")
        self.assertEqual(steps[-1], {"id": "dialogue_wait", "action": "wait", "ms": 5000})
        self.assertFalse(any(step["action"] == "follow_route" for step in steps))
        self.assertFalse(any(step["action"] == "observe_inventory_count_at_least" for step in steps))

        required = data["assertions"]["required_markers"]
        self.assertIn("quentin_greeting=confirmed", required)
        self.assertIn("quentin_request_stone_sent=private_npc", required)
        self.assertIn("quentin_free_stone_offer=confirmed", required)
        self.assertIn("quentin_accept_stone_sent=private_npc", required)
        self.assertIn("quentin_reward_response=confirmed", required)

        [check] = data["assertions"]["persistence"]["checks"]
        self.assertEqual(
            check,
            {
                "id": "adventurer_stone_inventory",
                "type": "player_item_presence",
                "location": "inventory",
                "item_id": 16277,
                "present": True,
            },
        )

        manifest = runner.normalized_manifest(scenario)
        compiled_sql = manifest["scenario"]["assertions"]["sql"]
        self.assertTrue(any("FROM `player_items` AS `pi`" in query and "`pi`.`itemtype` = 16277" in query for query in compiled_sql))


if __name__ == "__main__":
    unittest.main()
