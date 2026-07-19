from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
DRIVER_PATH = ROOT / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"


def load_runner():
    spec = importlib.util.spec_from_file_location("canary_e2e_runner_exact_movement", RUNNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_runner()


def edge(**overrides):
    value = {
        "id": "edge-one",
        "action": "walk_edge",
        "from_x": 32369,
        "from_y": 32241,
        "from_z": 7,
        "to_x": 32370,
        "to_y": 32241,
        "to_z": 7,
        "timeout_ms": 5000,
    }
    value.update(overrides)
    return value


class ExactMovementEdgeTests(unittest.TestCase):
    def test_derives_all_supported_adjacent_directions(self):
        expected = {
            (0, -1): "north",
            (1, -1): "northeast",
            (1, 0): "east",
            (1, 1): "southeast",
            (0, 1): "south",
            (-1, 1): "southwest",
            (-1, 0): "west",
            (-1, -1): "northwest",
        }
        for (delta_x, delta_y), direction in expected.items():
            with self.subTest(direction=direction):
                step = edge(
                    from_x=100,
                    from_y=100,
                    to_x=100 + delta_x,
                    to_y=100 + delta_y,
                )
                self.assertEqual(runner.walk_edge_direction(step), direction)
                self.assertEqual(runner.validate_steps({"steps": [step]}), [step])

    def test_coordinate_zero_is_valid(self):
        step = edge(from_x=0, from_y=0, from_z=0, to_x=1, to_y=0, to_z=0)
        self.assertEqual(runner.walk_edge_direction(step), "east")

    def test_rejects_out_of_range_coordinates(self):
        with self.assertRaisesRegex(runner.ScenarioError, "from_x must be an integer between 0 and 65535"):
            runner.validate_steps({"steps": [edge(from_x=65536)]})
        with self.assertRaisesRegex(runner.ScenarioError, "to_z must be an integer between 0 and 15"):
            runner.validate_steps({"steps": [edge(to_z=16)]})

    def test_rejects_zero_length_multi_tile_and_floor_changing_edges(self):
        with self.assertRaisesRegex(runner.ScenarioError, "exactly one adjacent movement edge"):
            runner.validate_steps({"steps": [edge(to_x=32369)]})
        with self.assertRaisesRegex(runner.ScenarioError, "exactly one adjacent movement edge"):
            runner.validate_steps({"steps": [edge(to_x=32371)]})
        with self.assertRaisesRegex(runner.ScenarioError, "must remain on one floor"):
            runner.validate_steps({"steps": [edge(to_z=8)]})

    def test_rejects_caller_supplied_direction_and_unbounded_timeout(self):
        with self.assertRaisesRegex(runner.ScenarioError, "unknown field"):
            runner.validate_steps({"steps": [edge(direction="east")]})
        with self.assertRaisesRegex(runner.ScenarioError, "timeout_ms must be <="):
            runner.validate_steps({"steps": [edge(timeout_ms=runner.MAX_STEP_DELAY_MS + 1)]})

    def test_rendered_plan_contains_exact_coordinates_not_derived_direction(self):
        data = {
            "suite": "movement",
            "id": "exact-edge-contract",
            "fixture": {"character": "Knight 1"},
            "steps": [edge()],
            "assertions": {"persistence": None},
        }
        scenario = runner.Scenario(Path("tests/e2e/scenarios/movement/exact-edge-contract.json"), data)
        rendered = runner.render_lua_plan(scenario)
        self.assertIn('action = "walk_edge"', rendered)
        self.assertIn("from_x = 32369", rendered)
        self.assertIn("to_x = 32370", rendered)
        self.assertNotIn('direction = "east"', rendered)

    def test_runtime_asserts_source_walks_once_and_waits_for_exact_destination(self):
        source = DRIVER_PATH.read_text(encoding="utf-8")
        start = source.index('if step.action == "walk_edge" then')
        end = source.index('if step.action == "talk" then', start)
        block = source[start:end]
        self.assertIn("source mismatch actual=", block)
        self.assertIn("samePosition(current, source)", block)
        self.assertIn("WALK_EDGE_DIRECTIONS", block)
        self.assertEqual(block.count("g_game.walk(direction)"), 1)
        self.assertIn("pollUntil(step, step.timeout_ms or 10000", block)
        self.assertIn("samePosition(livePosition, destination)", block)
        self.assertIn("route drift actual=", block)


if __name__ == "__main__":
    unittest.main()
