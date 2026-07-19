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


persistence = load_module("test_e2e_player_magic_level_persistence", PERSISTENCE_PATH)
runner = load_module("test_e2e_run_agent_e2e_player_magic_level", RUNNER_PATH)


class PlayerMagicLevelCompilerTests(unittest.TestCase):
    def test_compiles_exact_magic_level(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {
                    "id": "magic-level",
                    "type": "player_magic_level",
                    "equals": 42,
                }
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="Knight 1")

        self.assertEqual(
            query,
            "SELECT IF((SELECT `maglevel` FROM `players` WHERE `name` = 'Knight 1') = 42, 1, 0)",
        )
        self.assertNotIn(";", query)

    def test_accepts_uint16_boundaries(self) -> None:
        for value in (0, persistence.MAX_UINT16):
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": "magic-level",
                        "type": "player_magic_level",
                        "equals": value,
                    }
                ],
            }
            with self.subTest(value=value):
                [query] = persistence.compile_persistence_assertions(raw, character="Knight 1")
                self.assertIn(f") = {value}, 1, 0)", query)

    def test_rejects_values_outside_uint16_boundary(self) -> None:
        for value in (-1, True, 1.5, "1", persistence.MAX_UINT16 + 1):
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": "magic-level",
                        "type": "player_magic_level",
                        "equals": value,
                    }
                ],
            }
            with self.subTest(value=value):
                with self.assertRaises(persistence.PersistenceAssertionError):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_rejects_arbitrary_sql_surface(self) -> None:
        for extra_field in ("table", "column", "where", "sql", "predicate", "field"):
            check = {
                "id": "magic-level",
                "type": "player_magic_level",
                "equals": 42,
                extra_field: "players",
            }
            with self.subTest(extra_field=extra_field):
                with self.assertRaisesRegex(persistence.PersistenceAssertionError, "unknown field"):
                    persistence.compile_persistence_assertions(
                        {"required": True, "checks": [check]},
                        character="Knight 1",
                    )

    def test_character_literal_is_sql_escaped(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {
                    "id": "magic-level",
                    "type": "player_magic_level",
                    "equals": 42,
                }
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="O'Brien")

        self.assertIn("WHERE `name` = 'O''Brien'", query)

    def test_client_readable_types_include_magic_level_and_balance(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {"id": "level", "type": "player_field", "field": "level", "equals": 500},
                {"id": "quest-stage", "type": "player_storage", "key": 123456, "equals": 7},
                {
                    "id": "inventory-item",
                    "type": "player_item_presence",
                    "location": "inventory",
                    "item_id": 3031,
                    "present": True,
                },
                {"id": "bank-balance", "type": "player_balance", "equals": 1000},
                {"id": "magic-level", "type": "player_magic_level", "equals": 42},
            ],
        }

        self.assertEqual(
            persistence.validate_persistence_assertions(raw),
            [
                {"id": "level", "type": "player_field", "field": "level", "equals": 500},
                {"id": "bank-balance", "type": "player_balance", "equals": 1000},
                {"id": "magic-level", "type": "player_magic_level", "equals": 42},
            ],
        )
        self.assertEqual(len(persistence.compile_persistence_assertions(raw, character="Knight 1")), 5)


class PlayerMagicLevelManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        scenario_dir = self.root / "tests" / "e2e" / "scenarios" / "platform"
        scenario_dir.mkdir(parents=True)
        automation = self.root / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"
        automation.parent.mkdir(parents=True)
        automation.write_text("-- test automation\n", encoding="utf-8")
        self.path = scenario_dir / "magic-level-persistence.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def scenario_data(self) -> dict:
        return {
            "schema_version": 1,
            "id": "magic-level-persistence",
            "suite": "platform",
            "name": "Magic level persistence contract",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "description": "Magic level persistence contract test",
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
                "persistence": {
                    "required": True,
                    "checks": [
                        {"id": "level", "type": "player_field", "field": "level", "equals": 500},
                        {"id": "bank-balance", "type": "player_balance", "equals": 1000},
                        {"id": "magic-level", "type": "player_magic_level", "equals": 42},
                    ],
                },
            },
            "artifacts": ["result.json"],
        }

    def write(self) -> runner.Scenario:
        self.path.write_text(json.dumps(self.scenario_data()), encoding="utf-8")
        return runner.validate_scenario(self.path, self.root)

    def test_magic_level_appends_sql_and_phase_two_lua(self) -> None:
        scenario = self.write()

        manifest = runner.normalized_manifest(scenario)
        rendered = runner.render_lua_plan(scenario)
        sql_checks = manifest["scenario"]["assertions"]["sql"]

        self.assertEqual(len(sql_checks), 4)
        self.assertTrue(any("SELECT `maglevel` FROM `players`" in query for query in sql_checks))
        self.assertIn('id = "bank-balance"', rendered)
        self.assertIn('type = "player_balance"', rendered)
        self.assertIn('id = "magic-level"', rendered)
        self.assertIn('type = "player_magic_level"', rendered)
        self.assertIn("equals = 42", rendered)
        self.assertNotIn('field = "maglevel"', rendered)


class PlayerMagicLevelRuntimeSourceTests(unittest.TestCase):
    def test_driver_reads_maintained_magic_level_getter(self) -> None:
        source = DRIVER_PATH.read_text(encoding="utf-8")

        self.assertIn('if check.type == "player_magic_level" then', source)
        self.assertIn("player:getMagicLevel()", source)
        self.assertIn('elseif check.type == "player_magic_level" then', source)
        self.assertIn("invalid runtime player_magic_level persistence check", source)
        self.assertIn('if step.action == "follow_route" then', source)
        self.assertIn("player:getResourceBalance(RESOURCE_BANK_BALANCE)", source)


if __name__ == "__main__":
    unittest.main()
