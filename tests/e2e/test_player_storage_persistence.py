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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


persistence = load_module("test_e2e_player_storage_persistence", PERSISTENCE_PATH)
runner = load_module("test_e2e_run_agent_e2e_player_storage", RUNNER_PATH)


class PlayerStoragePersistenceCompilerTests(unittest.TestCase):
    def test_compiles_player_storage_to_fixed_shape_scalar_select(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {"id": "quest-stage", "type": "player_storage", "key": 123456, "equals": -1},
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="Knight 1")

        self.assertEqual(
            query,
            "SELECT IF(EXISTS(SELECT 1 FROM `player_storage` AS `ps` "
            "INNER JOIN `players` AS `p` ON `p`.`id` = `ps`.`player_id` "
            "WHERE `p`.`name` = 'Knight 1' AND `ps`.`key` = 123456 "
            "AND `ps`.`value` = -1), 1, 0)",
        )
        self.assertNotIn(";", query)

    def test_player_storage_character_literal_is_sql_escaped(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {"id": "quest-stage", "type": "player_storage", "key": 1, "equals": 2},
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="O'Brien")

        self.assertIn("WHERE `p`.`name` = 'O''Brien'", query)

    def test_player_storage_schema_ranges_are_enforced(self) -> None:
        for key in (-1, True, persistence.MAX_UINT32 + 1):
            raw = {
                "required": True,
                "checks": [{"id": "storage", "type": "player_storage", "key": key, "equals": 0}],
            }
            with self.subTest(key=key):
                with self.assertRaises(persistence.PersistenceAssertionError):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

        for value in (persistence.MIN_INT32 - 1, True, persistence.MAX_INT32 + 1):
            raw = {
                "required": True,
                "checks": [{"id": "storage", "type": "player_storage", "key": 1, "equals": value}],
            }
            with self.subTest(value=value):
                with self.assertRaises(persistence.PersistenceAssertionError):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_player_storage_rejects_type_specific_unknown_fields(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {
                    "id": "storage",
                    "type": "player_storage",
                    "key": 1,
                    "field": "level",
                    "equals": 2,
                }
            ],
        }

        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "unknown field"):
            persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_only_client_readable_checks_are_returned_for_phase_two(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {"id": "level", "type": "player_field", "field": "level", "equals": 500},
                {"id": "quest-stage", "type": "player_storage", "key": 123456, "equals": 7},
            ],
        }

        self.assertEqual(
            persistence.validate_persistence_assertions(raw),
            [{"id": "level", "type": "player_field", "field": "level", "equals": 500}],
        )
        self.assertEqual(len(persistence.compile_persistence_assertions(raw, character="Knight 1")), 2)


class PlayerStoragePersistenceManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        scenario_dir = self.root / "tests" / "e2e" / "scenarios" / "platform"
        scenario_dir.mkdir(parents=True)
        automation = self.root / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"
        automation.parent.mkdir(parents=True)
        automation.write_text("-- test automation\n", encoding="utf-8")
        self.path = scenario_dir / "storage-persistence.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def scenario_data(self) -> dict:
        return {
            "schema_version": 1,
            "id": "storage-persistence",
            "suite": "platform",
            "name": "Storage persistence contract",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "description": "Storage persistence contract test",
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
                        {"id": "quest-stage", "type": "player_storage", "key": 123456, "equals": 7},
                    ],
                },
            },
            "artifacts": ["result.json"],
        }

    def write(self) -> runner.Scenario:
        self.path.write_text(json.dumps(self.scenario_data()), encoding="utf-8")
        return runner.validate_scenario(self.path, self.root)

    def test_mixed_contract_appends_both_sql_checks_but_only_player_field_to_lua(self) -> None:
        scenario = self.write()

        manifest = runner.normalized_manifest(scenario)
        rendered = runner.render_lua_plan(scenario)

        self.assertEqual(len(manifest["scenario"]["assertions"]["sql"]), 3)
        self.assertTrue(
            any("FROM `player_storage` AS `ps`" in query for query in manifest["scenario"]["assertions"]["sql"])
        )
        self.assertIn('field = "level"', rendered)
        self.assertNotIn('type = "player_storage"', rendered)
        self.assertNotIn("key = 123456", rendered)


if __name__ == "__main__":
    unittest.main()
