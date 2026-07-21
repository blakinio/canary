from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
SCENARIO_PATH = ROOT / "tests" / "e2e" / "scenarios" / "combat" / "deterministic-combat.json"
INSTANCE_SERVICE_CPP = ROOT / "src" / "game" / "instance" / "instance_arena_service.cpp"
INSTANCE_SERVICE_HPP = ROOT / "src" / "game" / "instance" / "instance_arena_service.hpp"
INSTANCE_TALKACTION = ROOT / "data" / "scripts" / "talkactions" / "gm" / "instance_arena.lua"
CAVE_RAT_PATH = ROOT / "data-canary" / "monster" / "mammals" / "cave_rat.lua"
ACCOUNTS_PATH = ROOT / "docker" / "data" / "01-test_account.sql"
PLAYERS_PATH = ROOT / "docker" / "data" / "02-test_account_players.sql"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("test_e2e_deterministic_combat_runner", RUNNER_PATH)


class DeterministicCombatEvidenceTests(unittest.TestCase):
    def test_instance_arena_owns_exact_cave_rat_fixture(self) -> None:
        header = INSTANCE_SERVICE_HPP.read_text(encoding="utf-8")
        source = INSTANCE_SERVICE_CPP.read_text(encoding="utf-8")

        self.assertIn('static constexpr const char* MonsterName = "Cave Rat";', header)
        self.assertIn(".minX = 19976", source)
        self.assertIn(".minY = 19988", source)
        self.assertIn(".minZ = 7", source)
        self.assertIn("const Position entryPosition { region->minX, region->minY, region->minZ };", source)
        self.assertIn("static_cast<uint16_t>(region->minX + 4)", source)
        self.assertIn("static_cast<uint16_t>(region->minY + 3)", source)
        self.assertIn("const auto &monster = monsterFactory(monsterPosition);", source)

    def test_fixture_permissions_and_character_contract(self) -> None:
        accounts = ACCOUNTS_PATH.read_text(encoding="utf-8")
        players = PLAYERS_PATH.read_text(encoding="utf-8")
        talkaction = INSTANCE_TALKACTION.read_text(encoding="utf-8")

        self.assertIn("(115 , 'test15', '@test15'", accounts)
        self.assertIn("'@test15' , 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3', 6", accounts)
        self.assertIn("'Knight 15'       , 1         , 115          , 500    , 4", players)

        self.assertIn('TalkAction("/instancearena")', talkaction)
        self.assertIn('if param == "create" then', talkaction)
        self.assertIn('elseif param == "close" then', talkaction)
        self.assertIn('instanceArena:groupType("gamemaster")', talkaction)

    def test_cave_rat_is_bounded_target(self) -> None:
        source = CAVE_RAT_PATH.read_text(encoding="utf-8")
        self.assertIn('Game.createMonsterType("Cave Rat")', source)
        self.assertIn("monster.health = 30", source)
        self.assertIn("monster.maxHealth = 30", source)
        self.assertIn("attackable = true", source)
        self.assertIn("runHealth = 3", source)

    def test_scenario_uses_existing_bounded_actions(self) -> None:
        scenario = runner.validate_scenario(SCENARIO_PATH, ROOT)
        data = scenario.data
        steps = data["steps"]

        self.assertEqual(data["suite"], "combat")
        self.assertEqual(data["server"]["datapack"], "data-canary")
        self.assertEqual(data["server"]["map"], "canary")
        self.assertEqual(data["fixture"]["account"], "@test15")
        self.assertEqual(data["fixture"]["character"], "Knight 15")
        self.assertEqual(data["client"]["automation"], "tools/e2e/client/agent_e2e_scenario.lua")

        self.assertEqual(steps[1], {"id": "create_arena", "action": "talk", "text": "/instancearena create"})
        self.assertEqual(steps[2]["action"], "wait_creature")
        self.assertEqual(steps[2]["creature"], "Cave Rat")
        self.assertTrue(steps[2]["present"])

        edges = [step for step in steps if step["action"] == "walk_edge"]
        self.assertEqual(
            [(edge["from_x"], edge["from_y"], edge["from_z"], edge["to_x"], edge["to_y"], edge["to_z"]) for edge in edges],
            [
                (19976, 19988, 7, 19977, 19989, 7),
                (19977, 19989, 7, 19978, 19990, 7),
                (19978, 19990, 7, 19979, 19991, 7),
            ],
        )
        self.assertFalse(any(step["action"] == "walk" for step in steps))

        attack = next(step for step in steps if step["id"] == "attack_target")
        self.assertEqual(attack["action"], "attack_visible")
        self.assertEqual(attack["creature"], "Cave Rat")
        self.assertTrue(next(step for step in steps if step["id"] == "attack_confirmed")["expected"])

        defeated = next(step for step in steps if step["id"] == "target_defeated")
        self.assertEqual(defeated["action"], "wait_creature")
        self.assertEqual(defeated["creature"], "Cave Rat")
        self.assertFalse(defeated["present"])
        self.assertLessEqual(defeated["timeout_ms"], 20_000)
        self.assertFalse(next(step for step in steps if step["id"] == "attack_cleared")["expected"])
        self.assertEqual(steps[-1], {"id": "close_arena", "action": "talk", "text": "/instancearena close"})

        required = data["assertions"]["required_markers"]
        for marker in (
            "step_create_arena=success",
            "step_target_visible=success",
            "step_attack_target=success",
            "step_attack_confirmed=success",
            "step_target_defeated=success",
            "step_attack_cleared=success",
            "step_close_arena=success",
            "plan=success",
            "e2e=success",
        ):
            self.assertIn(marker, required)

        self.assertTrue(all("WHERE name = 'Knight 15'" in query for query in data["assertions"]["sql"]))


if __name__ == "__main__":
    unittest.main()
