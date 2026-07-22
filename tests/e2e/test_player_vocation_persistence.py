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


EXPECTED_VOCATIONS = {
    "none": (0, 0),
    "sorcerer": (1, 3),
    "druid": (2, 4),
    "paladin": (3, 2),
    "knight": (4, 1),
    "master_sorcerer": (5, 13),
    "elder_druid": (6, 14),
    "royal_paladin": (7, 12),
    "elite_knight": (8, 11),
    "monk": (9, 5),
    "exalted_monk": (10, 15),
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


persistence = load_module("test_e2e_player_vocation_persistence", PERSISTENCE_PATH)
runner = load_module("test_e2e_run_agent_e2e_player_vocation", RUNNER_PATH)


class PlayerVocationCompilerTests(unittest.TestCase):
    def test_fixed_mapping_matches_reviewed_server_and_client_vocation_ids(self) -> None:
        self.assertEqual(
            {
                name: (mapping["server_vocation_id"], mapping["client_vocation_id"])
                for name, mapping in persistence.PLAYER_VOCATIONS.items()
            },
            EXPECTED_VOCATIONS,
        )

    def test_compiles_each_semantic_vocation_to_fixed_server_id_without_client_phase_two_check(self) -> None:
        for vocation, (server_vocation_id, _client_vocation_id) in EXPECTED_VOCATIONS.items():
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": "vocation",
                        "type": "player_vocation",
                        "vocation": vocation,
                    }
                ],
            }
            with self.subTest(vocation=vocation):
                [query] = persistence.compile_persistence_assertions(raw, character="Knight 1")
                client_checks = persistence.validate_persistence_assertions(raw)
                self.assertEqual(
                    query,
                    "SELECT IF((SELECT `vocation` FROM `players` WHERE `name` = "
                    f"'Knight 1') = {server_vocation_id}, 1, 0)",
                )
                self.assertEqual(client_checks, [])
                self.assertNotIn(";", query)

    def test_rejects_unknown_or_numeric_vocation(self) -> None:
        for vocation in ("rookgaard", "custom", 4, 15, True, ""):
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": "vocation",
                        "type": "player_vocation",
                        "vocation": vocation,
                    }
                ],
            }
            with self.subTest(vocation=vocation):
                with self.assertRaises(persistence.PersistenceAssertionError):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_rejects_arbitrary_mapping_and_sql_surfaces(self) -> None:
        for extra_field in (
            "server_vocation_id",
            "client_vocation_id",
            "server_id",
            "client_id",
            "id_value",
            "field",
            "equals",
            "column",
            "table",
            "sql",
            "predicate",
        ):
            check = {
                "id": "vocation",
                "type": "player_vocation",
                "vocation": "knight",
                extra_field: 4,
            }
            with self.subTest(extra_field=extra_field):
                with self.assertRaisesRegex(persistence.PersistenceAssertionError, "unknown field"):
                    persistence.compile_persistence_assertions(
                        {"required": True, "checks": [check]},
                        character="Knight 1",
                    )

    def test_raw_player_field_vocation_remains_rejected(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {
                    "id": "vocation",
                    "type": "player_field",
                    "field": "vocation",
                    "equals": 4,
                }
            ],
        }

        with self.assertRaisesRegex(persistence.PersistenceAssertionError, "field unsupported"):
            persistence.compile_persistence_assertions(raw, character="Knight 1")

    def test_character_literal_is_sql_escaped(self) -> None:
        raw = {
            "required": True,
            "checks": [
                {
                    "id": "vocation",
                    "type": "player_vocation",
                    "vocation": "elite_knight",
                }
            ],
        }

        [query] = persistence.compile_persistence_assertions(raw, character="O'Brien")

        self.assertIn("WHERE `name` = 'O''Brien'", query)
        self.assertIn(") = 8, 1, 0)", query)

    def test_existing_client_readable_types_are_preserved_while_vocation_stays_sql_only(self) -> None:
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
                {
                    "id": "sword-level",
                    "type": "player_skill_level",
                    "skill": "sword",
                    "equals": 90,
                },
                {
                    "id": "vocation",
                    "type": "player_vocation",
                    "vocation": "elite_knight",
                },
            ],
        }

        self.assertEqual(
            persistence.validate_persistence_assertions(raw),
            [
                {"id": "level", "type": "player_field", "field": "level", "equals": 500},
                {"id": "bank-balance", "type": "player_balance", "equals": 1000},
                {"id": "magic-level", "type": "player_magic_level", "equals": 42},
                {
                    "id": "sword-level",
                    "type": "player_skill_level",
                    "skill": "sword",
                    "client_skill_id": 2,
                    "equals": 90,
                },
            ],
        )
        self.assertEqual(len(persistence.compile_persistence_assertions(raw, character="Knight 1")), 7)


class PlayerVocationManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        scenario_dir = self.root / "tests" / "e2e" / "scenarios" / "platform"
        scenario_dir.mkdir(parents=True)
        automation = self.root / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"
        automation.parent.mkdir(parents=True)
        automation.write_text("-- test automation\n", encoding="utf-8")
        self.path = scenario_dir / "vocation-persistence.json"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def scenario_data(self) -> dict:
        return {
            "schema_version": 1,
            "id": "vocation-persistence",
            "suite": "platform",
            "name": "Vocation persistence contract",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "description": "Vocation persistence contract test",
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
                        {
                            "id": "vocation",
                            "type": "player_vocation",
                            "vocation": "knight",
                        }
                    ],
                },
            },
            "artifacts": ["result.json"],
        }

    def write(self) -> runner.Scenario:
        self.path.write_text(json.dumps(self.scenario_data()), encoding="utf-8")
        return runner.validate_scenario(self.path, self.root)

    def test_vocation_uses_server_id_for_sql_and_is_omitted_from_phase_two_lua(self) -> None:
        scenario = self.write()

        manifest = runner.normalized_manifest(scenario)
        rendered = runner.render_lua_plan(scenario)
        sql_checks = manifest["scenario"]["assertions"]["sql"]

        self.assertEqual(len(sql_checks), 2)
        self.assertTrue(
            any("SELECT `vocation` FROM `players`" in query and ") = 4, 1, 0)" in query for query in sql_checks)
        )
        self.assertNotIn('id = "vocation"', rendered)
        self.assertNotIn('field = "vocation"', rendered)
        self.assertNotIn('type = "player_vocation"', rendered)


if __name__ == "__main__":
    unittest.main()
