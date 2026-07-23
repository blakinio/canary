from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
PROMOTION_PATH = ROOT / "tests" / "e2e" / "scenarios" / "npc" / "canary-promotion.json"
COMBAT_PATH = ROOT / "tests" / "e2e" / "scenarios" / "combat" / "deterministic-combat.json"
JOURNEY_PATH = (
    ROOT
    / "tests"
    / "e2e"
    / "scenarios"
    / "journeys"
    / "promotion-combat-persistence.json"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("test_e2e_run_agent_e2e_cross_system_journey", RUNNER_PATH)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CrossSystemPromotionCombatJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.promotion = load_json(PROMOTION_PATH)
        cls.combat = load_json(COMBAT_PATH)
        cls.journey = load_json(JOURNEY_PATH)

    def test_journey_uses_the_same_proven_runtime_and_fixture_boundaries(self) -> None:
        for key in ("client", "server", "fixture", "timing"):
            with self.subTest(key=key):
                self.assertEqual(self.journey[key], self.promotion[key])
                self.assertEqual(self.journey[key], self.combat[key])

    def test_journey_steps_are_exact_combat_then_promotion_composition(self) -> None:
        expected_steps = [*self.combat["steps"], *self.promotion["steps"][1:]]
        self.assertEqual(self.journey["steps"], expected_steps)

        promotion_actions = {step["action"] for step in self.promotion["steps"]}
        combat_actions = {step["action"] for step in self.combat["steps"]}
        journey_actions = {step["action"] for step in self.journey["steps"]}
        self.assertLessEqual(journey_actions, promotion_actions | combat_actions)

    def test_arena_cleanup_precedes_return_to_npc_flow(self) -> None:
        step_ids = [step["id"] for step in self.journey["steps"]]
        self.assertLess(step_ids.index("close_arena"), step_ids.index("npc-visible"))

    def test_journey_preserves_proven_persistence_contract(self) -> None:
        self.assertEqual(
            self.journey["assertions"]["persistence"],
            self.promotion["assertions"]["persistence"],
        )
        self.assertEqual(
            self.journey["assertions"]["sql"],
            self.promotion["assertions"]["sql"],
        )

    def test_every_composed_step_has_required_success_marker(self) -> None:
        markers = set(self.journey["assertions"]["required_markers"])
        for step in self.journey["steps"]:
            with self.subTest(step=step["id"]):
                self.assertIn(f"step_{step['id']}=success", markers)

    def test_manifest_is_valid_through_existing_runner_contract(self) -> None:
        scenario = runner.validate_scenario(JOURNEY_PATH, ROOT)
        self.assertEqual(scenario.key, "journeys/promotion-combat-persistence")

        normalized = runner.normalized_manifest(scenario)
        sql = normalized["scenario"]["assertions"]["sql"]
        self.assertGreater(len(sql), len(self.journey["assertions"]["sql"]))
        self.assertTrue(any("`vocation`" in query for query in sql))
        self.assertTrue(any("`balance`" in query for query in sql))


if __name__ == "__main__":
    unittest.main()
