from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PERSISTENCE_PATH = ROOT / "tools" / "e2e" / "persistence_assertions.py"
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
DRIVER_PATH = ROOT / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


persistence = load_module("test_e2e_persistence_assertions", PERSISTENCE_PATH)
runner = load_module("test_e2e_run_agent_e2e_persistence", RUNNER_PATH)


class PersistenceAssertionCompilerTests(unittest.TestCase):
    def test_compiles_whitelisted_player_fields_to_scalar_selects(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {"id": "level", "type": "player_field", "field": "level", "equals": 500},
                {"id": "vocation", "type": "player_field", "field": "vocation", "equals": 4},
            ],
        }

        queries = persistence.compile_persistence_assertions(raw, character="Knight 1")

        self.assertEqual(
            queries,
            [
                "SELECT IF((SELECT `level` FROM `players` WHERE `name` = 'Knight 1') = 500, 1, 0)",
                "SELECT IF((SELECT `vocation` FROM `players` WHERE `name` = 'Knight 1') = 4, 1, 0)",
            ],
        )
        self.assertTrue(all(";" not in query for query in queries))

    def test_character_literal_is_sql_escaped(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {"id": "experience", "type": "player_field", "field": "experience", "equals": 0},
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="O'Brien")

        self.assertIn("WHERE `name` = 'O''Brien'", query)

    def test_rejects_arbitrary_type_and_field(self) -> None:
        invalid_type = {
            "required": True,
            "checks": [{"id": "x", "type": "sql", "field": "level", "equals": 1}],
        }
        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "type unsupported"):
            persistence.compile_persistence_assertions(invalid_type, character="Knight 1")

        invalid_field = {
            "required": True,
            "checks": [{"id": "x", "type": "player_field", "field": "lastip", "equals": 1}],
        }
        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "field unsupported"):
            persistence.compile_persistence_assertions(invalid_field, character="Knight 1")

    def test_rejects_invalid_integer_values(self) -> None:
        for value in (-1, True, 9_223_372_036_854_775_808):
            raw = {
                "required": True,
                "checks": [{"id": "x", "type": "player_field", "field": "level", "equals": value}],
            }
            with self.subTest(value=value):
                with self.assertRaises(persistence.PersistenceAssertionError):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_rejects_duplicate_ids_and_unknown_fields(self) -> None:
        duplicate = {
            "required": True,
            "checks": [
                {"id": "same", "type": "player_field", "field": "level", "equals": 500},
                {"id": "same", "type": "player_field", "field": "vocation", "equals": 4},
            ],
        }
        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "duplicate id"):
            persistence.compile_persistence_assertions(duplicate, character="Knight 1")

        unknown = {
            "required": True,
            "checks": [
                {"id": "x", "type": "player_field", "field": "level", "equals": 500, "sql": "SELECT 1"}
            ],
        }
        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "unknown field"):
            persistence.compile_persistence_assertions(unknown, character="Knight 1")

    def test_required_contract_is_explicit(self) -> None:
        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "must not be empty"):
            persistence.compile_persistence_assertions({"required": True, "checks": []}, character="Knight 1")

        raw = {
            "required": False,
            "checks": [{"id": "x", "type": "player_field", "field": "level", "equals": 500}],
        }
        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "required must be true"):
            persistence.compile_persistence_assertions(raw, character="Knight 1")

        self.assertEqual(
            persistence.compile_persistence_assertions({"required": False, "checks": []}, character="Knight 1"),
            [],
        )

    def test_assertion_count_is_bounded(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {"id": f"check-{index}", "type": "player_field", "field": "level", "equals": 500}
                for index in range(persistence.MAX_ASSERTIONS + 1)
            ],
        }
        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "at most"):
            persistence.compile_persistence_assertions(raw, character="Knight 1")


class PersistenceManifestIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        scenario_dir = self.root / "tests" / "e2e" / "scenarios" / "platform"
        scenario_dir.mkdir(parents=True)
        automation = self.root / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"
        automation.parent.mkdir(parents=True)
        automation.write_text("-- test automation\n", encoding="utf-8")
        self.path = scenario_dir / "persistence.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def scenario_data(self) -> dict:
        return {
            "schema_version": 1,
            "id": "persistence",
            "suite": "platform",
            "name": "Persistence contract",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "description": "Persistence contract test",
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

    def write(self, data: dict) -> runner.Scenario:
        self.path.write_text(json.dumps(data), encoding="utf-8")
        return runner.validate_scenario(self.path, self.root)

    def test_normalized_manifest_appends_compiled_persistence_without_mutating_source(self) -> None:
        data = self.scenario_data()
        data["assertions"]["persistence"] = {
            "required": True,
            "checks": [
                {"id": "level", "type": "player_field", "field": "level", "equals": 500},
            ],
        }
        scenario = self.write(data)

        manifest = runner.normalized_manifest(scenario)

        self.assertEqual(scenario.data["assertions"]["sql"], ["SELECT 1"])
        self.assertEqual(
            manifest["scenario"]["assertions"]["sql"],
            [
                "SELECT 1",
                "SELECT IF((SELECT `level` FROM `players` WHERE `name` = 'Knight 1') = 500, 1, 0)",
            ],
        )
        self.assertEqual(manifest["scenario"]["assertions"]["persistence"], data["assertions"]["persistence"])

    def test_lua_plan_contains_phase_two_persistence_checks(self) -> None:
        data = self.scenario_data()
        data["assertions"]["persistence"] = {
            "required": True,
            "checks": [
                {"id": "level", "type": "player_field", "field": "level", "equals": 500},
                {"id": "vocation", "type": "player_field", "field": "vocation", "equals": 4},
            ],
        }
        scenario = self.write(data)

        rendered = runner.render_lua_plan(scenario)

        self.assertIn("persistence_checks = {", rendered)
        self.assertIn('field = "level"', rendered)
        self.assertIn('field = "vocation"', rendered)
        self.assertIn("equals = 500", rendered)
        self.assertIn("equals = 4", rendered)

    def test_scenario_without_persistence_is_backward_compatible(self) -> None:
        scenario = self.write(self.scenario_data())

        manifest = runner.normalized_manifest(scenario)
        rendered = runner.render_lua_plan(scenario)

        self.assertEqual(manifest["scenario"]["assertions"]["sql"], ["SELECT 1"])
        self.assertNotIn("persistence", manifest["scenario"]["assertions"])
        self.assertIn("persistence_checks = {\n  },", rendered)

    def test_invalid_persistence_contract_is_rejected_during_scenario_validation(self) -> None:
        data = self.scenario_data()
        data["assertions"]["persistence"] = {
            "required": True,
            "checks": [{"id": "bad", "type": "player_field", "field": "password", "equals": 1}],
        }
        self.path.write_text(json.dumps(data), encoding="utf-8")

        with self.assertRaisesRegex(runner.ScenarioError, "field unsupported"):
            runner.validate_scenario(self.path, self.root)

    def test_runtime_driver_executes_persistence_checks_only_in_phase_two(self) -> None:
        driver = DRIVER_PATH.read_text(encoding="utf-8")

        self.assertIn("function runNextPersistenceCheck()", driver)
        self.assertIn('if finished or phase ~= 2 or not phaseStarted then', driver)
        self.assertIn('appendEvent("persistence_plan", "success")', driver)
        self.assertIn('return player:getLevel(), nil', driver)
        self.assertIn('return player:getVocation(), nil', driver)
        self.assertIn('return player:getExperience(), nil', driver)
        self.assertIn('elseif plan and #plan.persistence_checks > 0 then', driver)
        self.assertLess(driver.index("runNextPersistenceCheck()"), driver.rindex("requestLogout(expectedPhase)"))


if __name__ == "__main__":
    unittest.main()
