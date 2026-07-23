from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
NPC_PATH = ROOT / "tests" / "e2e" / "scenarios" / "npc" / "quentin-adventurer-stone.json"
ROUTE_SCENARIO_PATH = (
    ROOT / "tests" / "e2e" / "scenarios" / "movement" / "physical-thais-temple-depot.json"
)
ROUTE_REQUEST_PATH = ROOT / "tests" / "e2e" / "routes" / "thais-temple-depot.json"
JOURNEY_PATH = (
    ROOT
    / "tests"
    / "e2e"
    / "scenarios"
    / "journeys"
    / "quentin-stone-thais-depot-persistence.json"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("test_e2e_run_agent_e2e_representative_journey_002", RUNNER_PATH)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class RepresentativeJourney002Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.npc = load_json(NPC_PATH)
        cls.route_scenario = load_json(ROUTE_SCENARIO_PATH)
        cls.route_request = load_json(ROUTE_REQUEST_PATH)
        cls.journey = load_json(JOURNEY_PATH)

    def test_journey_reuses_same_proven_global_runtime_and_fixture(self) -> None:
        self.assertEqual(self.journey["server"], self.npc["server"])
        self.assertEqual(self.journey["server"], self.route_scenario["server"])
        self.assertEqual(self.journey["fixture"], self.npc["fixture"])
        self.assertEqual(self.journey["fixture"], self.route_scenario["fixture"])

        for key in ("repository", "ref"):
            with self.subTest(key=key):
                self.assertEqual(self.journey["client"][key], self.npc["client"][key])
                self.assertEqual(self.journey["client"][key], self.route_scenario["client"][key])

        self.assertEqual(
            self.journey["client"]["automation"],
            self.npc["client"]["automation"],
        )
        self.assertEqual(
            self.journey["timing"]["global_timeout_seconds"],
            max(
                self.npc["timing"]["global_timeout_seconds"],
                self.route_scenario["timing"]["global_timeout_seconds"],
            ),
        )
        for key in ("session_hold_ms", "relog_delay_ms"):
            with self.subTest(key=key):
                self.assertEqual(self.journey["timing"][key], self.npc["timing"][key])
                self.assertEqual(self.journey["timing"][key], self.route_scenario["timing"][key])

    def test_journey_is_exact_online_then_quentin_then_follow_route_composition(self) -> None:
        expected_steps = [
            self.route_scenario["steps"][0],
            *self.npc["steps"],
            self.route_scenario["steps"][1],
        ]
        self.assertEqual(self.journey["steps"], expected_steps)

        npc_actions = {step["action"] for step in self.npc["steps"]}
        route_actions = {step["action"] for step in self.route_scenario["steps"]}
        journey_actions = {step["action"] for step in self.journey["steps"]}
        self.assertLessEqual(journey_actions, npc_actions | route_actions)

        step_ids = [step["id"] for step in self.journey["steps"]]
        self.assertLess(step_ids.index("dialogue_wait"), step_ids.index("temple-to-depot"))

    def test_journey_uses_canonical_semantic_route_request(self) -> None:
        [follow_route] = [
            step for step in self.journey["steps"] if step["action"] == "follow_route"
        ]
        self.assertEqual(follow_route, self.route_scenario["steps"][1])
        self.assertEqual(follow_route["route"], "thais-temple-depot")
        self.assertEqual(self.route_request["from"]["landmarkId"], "thais.temple")
        self.assertEqual(self.route_request["to"]["landmarkId"], "thais.depot")

    def test_journey_preserves_quentin_reward_and_persistence_contract(self) -> None:
        self.assertEqual(
            self.journey["assertions"]["persistence"],
            self.npc["assertions"]["persistence"],
        )
        self.assertEqual(
            self.journey["assertions"]["sql"],
            self.npc["assertions"]["sql"],
        )

        markers = self.journey["assertions"]["required_markers"]
        marker_set = set(markers)
        self.assertLess(
            markers.index("quentin_reward_response=confirmed"),
            markers.index("route_temple-to-depot=success"),
        )
        self.assertTrue(set(self.npc["assertions"]["required_markers"]).issubset(marker_set))

        for marker in (
            "route_plans=1",
            "step_online=success",
            "route_temple-to-depot=success",
            "step_temple-to-depot=success",
            "step_temple-to-depot_detail=32352,32226,7",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, marker_set)

        [check] = self.journey["assertions"]["persistence"]["checks"]
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

    def test_journey_retains_route_preflight_and_focused_npc_artifacts(self) -> None:
        artifacts = set(self.journey["artifacts"])
        self.assertTrue(set(self.npc["artifacts"]).issubset(artifacts))
        self.assertTrue(set(self.route_scenario["artifacts"]).issubset(artifacts))
        for artifact in (
            "route-thais-temple-depot.json",
            "route-thais-temple-depot-preflight.json",
            "route-thais-temple-depot-world-index-manifest.json",
            "route-preparation.json",
        ):
            with self.subTest(artifact=artifact):
                self.assertIn(artifact, artifacts)

    def test_manifest_is_valid_through_existing_runner_contract(self) -> None:
        scenario = runner.validate_scenario(JOURNEY_PATH, ROOT)
        self.assertEqual(scenario.key, "journeys/quentin-stone-thais-depot-persistence")

        normalized = runner.normalized_manifest(scenario)
        compiled_sql = normalized["scenario"]["assertions"]["sql"]
        self.assertTrue(
            any(
                "FROM `player_items` AS `pi`" in query
                and "`pi`.`itemtype` = 16277" in query
                for query in compiled_sql
            )
        )


if __name__ == "__main__":
    unittest.main()
