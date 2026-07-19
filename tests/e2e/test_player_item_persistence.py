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


persistence = load_module("test_e2e_player_item_persistence", PERSISTENCE_PATH)
runner = load_module("test_e2e_run_agent_e2e_player_item", RUNNER_PATH)


class PlayerItemPresenceCompilerTests(unittest.TestCase):
    def test_compiles_each_location_to_fixed_table(self) -> None:
        cases = {
            "inventory": "player_items",
            "depot": "player_depotitems",
            "inbox": "player_inboxitems",
        }
        for location, table in cases.items():
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": f"{location}-item",
                        "type": "player_item_presence",
                        "location": location,
                        "item_id": 3031,
                        "present": True,
                    }
                ],
            }

            with self.subTest(location=location):
                [query] = persistence.compile_persistence_assertions(raw, character="Knight 1")
                self.assertEqual(
                    query,
                    "SELECT IF(EXISTS(SELECT 1 FROM `"
                    + table
                    + "` AS `pi` INNER JOIN `players` AS `p` ON `p`.`id` = `pi`.`player_id` "
                    "WHERE `p`.`name` = 'Knight 1' AND `pi`.`itemtype` = 3031), 1, 0)",
                )
                self.assertNotIn(";", query)

    def test_absence_compiles_to_not_exists(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {
                    "id": "missing-item",
                    "type": "player_item_presence",
                    "location": "inventory",
                    "item_id": 3031,
                    "present": False,
                }
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="Knight 1")

        self.assertIn("SELECT IF(NOT EXISTS(SELECT 1 FROM `player_items`", query)

    def test_character_literal_is_sql_escaped(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {
                    "id": "inventory-item",
                    "type": "player_item_presence",
                    "location": "inventory",
                    "item_id": 1,
                    "present": True,
                }
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="O'Brien")

        self.assertIn("WHERE `p`.`name` = 'O''Brien'", query)

    def test_item_id_range_is_enforced(self) -> None:
        for item_id in (0, -1, True, persistence.MAX_UINT16 + 1):
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": "item",
                        "type": "player_item_presence",
                        "location": "inventory",
                        "item_id": item_id,
                        "present": True,
                    }
                ],
            }
            with self.subTest(item_id=item_id):
                with self.assertRaises(persistence.PersistenceAssertionError):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_location_and_present_are_strict(self) -> None:
        for location in ("", "store-inbox", "inventory; DROP TABLE players"):
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": "item",
                        "type": "player_item_presence",
                        "location": location,
                        "item_id": 1,
                        "present": True,
                    }
                ],
            }
            with self.subTest(location=location):
                with self.assertRaises(persistence.PersistenceAssertionError):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

        raw = {
            "required": True,
            "checks": [
                {
                    "id": "item",
                    "type": "player_item_presence",
                    "location": "inventory",
                    "item_id": 1,
                    "present": 1,
                }
            ],
        }
        with self.assertRaises(persistence.PersistenceAssertionError):
            persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_rejects_hierarchy_quantity_and_sql_fields(self) -> None:
        for extra_field in ("count", "pid", "sid", "table", "where"):
            check = {
                "id": "item",
                "type": "player_item_presence",
                "location": "inventory",
                "item_id": 1,
                "present": True,
                extra_field: 1,
            }
            raw = {"required": True, "checks": [check]}
            with self.subTest(extra_field=extra_field):
                with self.assertRaisesRegex(persistence.PersistenceAssertionError, "unknown field"):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_only_player_field_is_returned_for_phase_two(self) -> None:
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
            ],
        }

        self.assertEqual(
            persistence.validate_persistence_assertions(raw),
            [{"id": "level", "type": "player_field", "field": "level", "equals": 500}],
        )
        self.assertEqual(len(persistence.compile_persistence_assertions(raw, character="Knight 1")), 3)


class PlayerItemPresenceManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        scenario_dir = self.root / "tests" / "e2e" / "scenarios" / "platform"
        scenario_dir.mkdir(parents=True)
        automation = self.root / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"
        automation.parent.mkdir(parents=True)
        automation.write_text("-- test automation\n", encoding="utf-8")
        self.path = scenario_dir / "item-persistence.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def scenario_data(self) -> dict:
        return {
            "schema_version": 1,
            "id": "item-persistence",
            "suite": "platform",
            "name": "Item persistence contract",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "description": "Item persistence contract test",
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
                        {
                            "id": "inventory-item",
                            "type": "player_item_presence",
                            "location": "inventory",
                            "item_id": 3031,
                            "present": True,
                        },
                    ],
                },
            },
            "artifacts": ["result.json"],
        }

    def write(self) -> runner.Scenario:
        self.path.write_text(json.dumps(self.scenario_data()), encoding="utf-8")
        return runner.validate_scenario(self.path, self.root)

    def test_mixed_contract_appends_all_sql_but_only_player_field_to_lua(self) -> None:
        scenario = self.write()

        manifest = runner.normalized_manifest(scenario)
        rendered = runner.render_lua_plan(scenario)
        sql_checks = manifest["scenario"]["assertions"]["sql"]

        self.assertEqual(len(sql_checks), 4)
        self.assertTrue(any("FROM `player_storage` AS `ps`" in query for query in sql_checks))
        self.assertTrue(any("FROM `player_items` AS `pi`" in query for query in sql_checks))
        self.assertIn('field = "level"', rendered)
        self.assertNotIn('type = "player_storage"', rendered)
        self.assertNotIn('type = "player_item_presence"', rendered)
        self.assertNotIn("item_id = 3031", rendered)
        self.assertNotIn('location = "inventory"', rendered)


if __name__ == "__main__":
    unittest.main()
