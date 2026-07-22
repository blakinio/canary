from __future__ import annotations

import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
PERSISTENCE_PATH = ROOT / "tools" / "e2e" / "persistence_assertions.py"
SCENARIO_PATH = ROOT / "tests" / "e2e" / "scenarios" / "npc" / "canary-promotion.json"
NPC_SOURCE_PATH = ROOT / "data-canary" / "npc" / "canary.lua"
NPC_SPAWN_PATH = ROOT / "data-canary" / "world" / "canary-npc.xml"
NPC_MODULES_PATH = ROOT / "data" / "npclib" / "npc_system" / "modules.lua"
ADD_MONEY_PATH = ROOT / "data" / "scripts" / "talkactions" / "god" / "add_money.lua"
ACCOUNTS_PATH = ROOT / "docker" / "data" / "01-test_account.sql"
PLAYERS_PATH = ROOT / "docker" / "data" / "02-test_account_players.sql"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("test_e2e_canary_promotion_runner", RUNNER_PATH)
persistence = load_module("test_e2e_canary_promotion_persistence", PERSISTENCE_PATH)


class CanaryNpcPromotionEvidenceTests(unittest.TestCase):
    def test_repository_npc_owns_exact_promotion_contract(self) -> None:
        npc_source = NPC_SOURCE_PATH.read_text(encoding="utf-8")
        modules_source = NPC_MODULES_PATH.read_text(encoding="utf-8")

        self.assertIn('local npcName = "Canary"', npc_source)
        self.assertIn('keywordHandler:addKeyword({ "promot" }', npc_source)
        self.assertIn('node1:addChildKeyword({ "yes" }, StdModule.promotePlayer', npc_source)
        self.assertIn("cost = 20000", npc_source)
        self.assertIn("level = 20", npc_source)

        self.assertIn("function StdModule.promotePlayer", modules_source)
        self.assertIn("player:removeMoneyBank(parameters.cost)", modules_source)
        self.assertIn("player:setVocation(promotion)", modules_source)
        self.assertIn('player:kv():set("promoted", true)', modules_source)

    def test_existing_admin_setup_and_player_fixture_are_exact(self) -> None:
        add_money = ADD_MONEY_PATH.read_text(encoding="utf-8")
        accounts = ACCOUNTS_PATH.read_text(encoding="utf-8")
        players = PLAYERS_PATH.read_text(encoding="utf-8")

        self.assertIn('TalkAction("/addmoney")', add_money)
        self.assertIn("Bank.credit(name, amount)", add_money)
        self.assertIn('addMoney:groupType("god")', add_money)

        self.assertIn("(115 , 'test15', '@test15'", accounts)
        self.assertIn("'@test15' , 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3', 6", accounts)
        self.assertIn("'Paladin 15'      , 1         , 115          , 500    , 3", players)

    def test_selected_canary_spawn_is_stationary_and_adjacent(self) -> None:
        root = ET.parse(NPC_SPAWN_PATH).getroot()
        selected = [
            group
            for group in root.findall("npc")
            if (
                group.attrib.get("centerx"),
                group.attrib.get("centery"),
                group.attrib.get("centerz"),
            )
            == ("1943", "1345", "7")
        ]

        self.assertEqual(len(selected), 1)
        group = selected[0]
        self.assertEqual(group.attrib.get("radius"), "0")
        children = group.findall("npc")
        self.assertEqual(len(children), 1)
        self.assertEqual(
            children[0].attrib,
            {"name": "Canary", "x": "0", "y": "0", "z": "7", "spawntime": "60"},
        )

    def test_scenario_uses_existing_bounded_actions_and_m3_assertions(self) -> None:
        scenario = runner.validate_scenario(SCENARIO_PATH, ROOT)
        data = scenario.data
        steps = data["steps"]

        self.assertEqual(data["suite"], "npc")
        self.assertEqual(data["server"], {"database_image": "mariadb:11.4", "datapack": "data-canary", "map": "canary"})
        self.assertEqual(data["fixture"]["account"], "@test15")
        self.assertEqual(data["fixture"]["character"], "Paladin 15")
        self.assertEqual(data["client"]["automation"], "tools/e2e/client/agent_e2e_scenario.lua")

        self.assertEqual(
            [step["id"] for step in steps],
            [
                "online",
                "npc-visible",
                "seed-balance",
                "seed-settle",
                "greet",
                "greet-settle",
                "promotion-offer",
                "offer-settle",
                "accept",
                "promote-settle",
            ],
        )
        self.assertEqual(steps[1], {"id": "npc-visible", "action": "wait_creature", "creature": "Canary", "present": True, "timeout_ms": 10000})
        self.assertEqual(steps[2], {"id": "seed-balance", "action": "talk", "text": "/addmoney Paladin 15, 20000"})
        self.assertEqual(steps[4], {"id": "greet", "action": "talk", "text": "hi"})
        self.assertEqual(steps[6], {"id": "promotion-offer", "action": "talk_npc", "receiver": "Canary", "text": "promot"})
        self.assertEqual(steps[8], {"id": "accept", "action": "talk_npc", "receiver": "Canary", "text": "yes"})
        self.assertFalse(any(step["action"] in {"walk", "walk_edge", "follow_route"} for step in steps))

        checks = data["assertions"]["persistence"]["checks"]
        self.assertEqual(
            checks,
            [
                {"id": "promoted-vocation", "type": "player_vocation", "vocation": "royal_paladin"},
                {"id": "spent-balance", "type": "player_balance", "equals": 0},
            ],
        )
        self.assertEqual(persistence.PLAYER_VOCATIONS["royal_paladin"]["server_vocation_id"], 7)
        self.assertEqual(persistence.PLAYER_VOCATIONS["royal_paladin"]["client_vocation_id"], 12)

        manifest = runner.normalized_manifest(scenario)
        sql = manifest["scenario"]["assertions"]["sql"]
        self.assertTrue(any("`vocation`" in query and ") = 7, 1, 0)" in query for query in sql))
        self.assertTrue(any("`balance`" in query and ") = 0, 1, 0)" in query for query in sql))

        required = data["assertions"]["required_markers"]
        for marker in (
            "initial_position=1942,1345,7",
            "step_npc-visible=success",
            "step_seed-balance=success",
            "step_greet=success",
            "step_promotion-offer=success",
            "step_accept=success",
            "plan=success",
            "persistence_check_promoted-vocation=success",
            "persistence_check_promoted-vocation_detail=12",
            "persistence_check_spent-balance=success",
            "persistence_check_spent-balance_detail=0",
            "persistence_plan=success",
            "e2e=success",
        ):
            self.assertIn(marker, required)


if __name__ == "__main__":
    unittest.main()
