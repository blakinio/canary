from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "e2e" / "run_agent_e2e.py"
SPEC = importlib.util.spec_from_file_location("run_agent_e2e", MODULE_PATH)
assert SPEC and SPEC.loader
run_agent_e2e = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_agent_e2e
SPEC.loader.exec_module(run_agent_e2e)


class ScenarioPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "tests" / "e2e" / "scenarios" / "gameplay").mkdir(parents=True)
        automation = self.root / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"
        automation.parent.mkdir(parents=True)
        automation.write_text("-- test automation\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def scenario_data(self) -> dict:
        return {
            "schema_version": 1,
            "id": "smoke",
            "suite": "gameplay",
            "name": "Gameplay smoke",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "description": "Test scenario",
            "client": {
                "repository": "blakinio/otclient",
                "ref": "abc123",
                "automation": "tools/e2e/client/agent_e2e_scenario.lua",
            },
            "server": {
                "database_image": "mariadb:11.4",
                "datapack": "data-otservbr-global",
                "map": "otservbr",
            },
            "fixture": {
                "account": "@test1",
                "password_env": "AGENT_E2E_TEST_PASSWORD",
                "character": "Knight 1",
                "world": "Canary E2E",
                "host": "127.0.0.1",
                "game_port": 7172,
            },
            "timing": {
                "global_timeout_seconds": 180,
                "session_hold_ms": 7000,
                "relog_delay_ms": 1500,
            },
            "assertions": {
                "required_markers": ["e2e=success"],
                "sql": ["SELECT 1"],
            },
            "artifacts": ["result.json"],
        }

    def write_scenario(self, data: dict) -> Path:
        path = self.root / "tests" / "e2e" / "scenarios" / "gameplay" / "smoke.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_legacy_scenario_without_steps_remains_valid(self) -> None:
        scenario = run_agent_e2e.validate_scenario(self.write_scenario(self.scenario_data()), self.root)
        self.assertEqual(run_agent_e2e.validate_steps(scenario.data), [])
        rendered = run_agent_e2e.render_lua_plan(scenario)
        self.assertIn("steps = {", rendered)
        self.assertNotIn("action =", rendered)

    def test_valid_steps_render_deterministically_and_escape_text(self) -> None:
        data = self.scenario_data()
        data["steps"] = [
            {"id": "move-east", "action": "walk", "direction": "east", "count": 2, "interval_ms": 300},
            {"id": "cast", "action": "talk", "text": 'exura "vita"'},
            {"id": "online", "action": "observe_online", "expected": True},
        ]
        scenario = run_agent_e2e.validate_scenario(self.write_scenario(data), self.root)
        first = run_agent_e2e.render_lua_plan(scenario)
        second = run_agent_e2e.render_lua_plan(scenario)
        self.assertEqual(first, second)
        self.assertIn('action = "walk"', first)
        self.assertIn('direction = "east"', first)
        self.assertIn('text = "exura \\"vita\\""', first)
        self.assertIn("expected = true", first)

    def test_unknown_action_is_rejected(self) -> None:
        data = self.scenario_data()
        data["steps"] = [{"id": "bad", "action": "shell", "command": "not-allowed"}]
        with self.assertRaisesRegex(run_agent_e2e.ScenarioError, "unsupported"):
            run_agent_e2e.validate_scenario(self.write_scenario(data), self.root)

    def test_unknown_step_field_is_rejected(self) -> None:
        data = self.scenario_data()
        data["steps"] = [{"id": "wait", "action": "wait", "ms": 100, "extra": True}]
        with self.assertRaisesRegex(run_agent_e2e.ScenarioError, "unknown field"):
            run_agent_e2e.validate_scenario(self.write_scenario(data), self.root)

    def test_step_text_rejects_newline(self) -> None:
        data = self.scenario_data()
        data["steps"] = [{"id": "talk", "action": "talk", "text": "hello\nworld"}]
        with self.assertRaisesRegex(run_agent_e2e.ScenarioError, "newlines"):
            run_agent_e2e.validate_scenario(self.write_scenario(data), self.root)

    def test_duplicate_step_id_is_rejected(self) -> None:
        data = self.scenario_data()
        data["steps"] = [
            {"id": "same", "action": "wait", "ms": 100},
            {"id": "same", "action": "request_channels"},
        ]
        with self.assertRaisesRegex(run_agent_e2e.ScenarioError, "duplicate id"):
            run_agent_e2e.validate_scenario(self.write_scenario(data), self.root)

    def test_plan_is_bounded(self) -> None:
        data = self.scenario_data()
        data["steps"] = [
            {"id": f"wait-{index}", "action": "wait", "ms": 1}
            for index in range(run_agent_e2e.MAX_STEPS + 1)
        ]
        with self.assertRaisesRegex(run_agent_e2e.ScenarioError, "at most"):
            run_agent_e2e.validate_scenario(self.write_scenario(data), self.root)

    def test_resolve_writes_sibling_plan_for_step_scenario(self) -> None:
        data = self.scenario_data()
        data["steps"] = [{"id": "channels", "action": "request_channels"}]
        self.write_scenario(data)
        manifest = self.root / "artifacts" / "scenario-manifest.json"
        env = self.root / "artifacts" / "scenario.env"
        result = run_agent_e2e.main(
            [
                "--root",
                str(self.root),
                "resolve",
                "--suite",
                "gameplay",
                "--scenario",
                "smoke",
                "--manifest",
                str(manifest),
                "--github-env",
                str(env),
            ]
        )
        self.assertEqual(result, 0)
        plan = manifest.with_name("scenario-plan.lua")
        self.assertTrue(plan.is_file())
        self.assertIn('action = "request_channels"', plan.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
