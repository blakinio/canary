from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "e2e" / "multi_client_orchestration.py"
SPEC = importlib.util.spec_from_file_location("canary_multi_client_orchestration", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MultiClientOrchestrationTests(unittest.TestCase):
    def manifest(self) -> dict:
        return {
            "key": "multiclient/shared-world-visibility",
            "scenario": {
                "fixture": {
                    "account": "@test1",
                    "character": "Knight 1",
                },
                "multi_client": {
                    "schema_version": 1,
                    "secondary": {
                        "id": "beta",
                        "account": "@test2",
                        "password_env": "AGENT_E2E_TEST_PASSWORD",
                        "character": "Knight 2",
                    },
                },
            },
        }

    def test_compile_secondary_keeps_raw_password_out_of_materialized_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            values = MODULE.compile_secondary(self.manifest(), artifact_dir=Path(temporary))

        self.assertEqual(values["AGENT_E2E_ACCOUNT"], "@test2")
        self.assertEqual(values["AGENT_E2E_CHARACTER"], "Knight 2")
        self.assertEqual(values["AGENT_E2E_PRIMARY_CHARACTER"], "Knight 1")
        self.assertEqual(values["AGENT_E2E_PASSWORD_ENV"], "AGENT_E2E_TEST_PASSWORD")
        self.assertNotIn("AGENT_E2E_PASSWORD", values)

    def test_secondary_identity_must_be_distinct(self) -> None:
        manifest = self.manifest()
        manifest["scenario"]["multi_client"]["secondary"]["account"] = "@test1"
        with self.assertRaisesRegex(MODULE.MultiClientError, "account must differ"):
            MODULE.compile_secondary(manifest, artifact_dir=Path("/tmp/e2e"))

        manifest = self.manifest()
        manifest["scenario"]["multi_client"]["secondary"]["character"] = "Knight 1"
        with self.assertRaisesRegex(MODULE.MultiClientError, "character must differ"):
            MODULE.compile_secondary(manifest, artifact_dir=Path("/tmp/e2e"))

    def test_password_reference_and_unknown_fields_fail_closed(self) -> None:
        manifest = self.manifest()
        manifest["scenario"]["multi_client"]["secondary"]["password_env"] = "not-safe"
        with self.assertRaisesRegex(MODULE.MultiClientError, "password_env"):
            MODULE.compile_secondary(manifest, artifact_dir=Path("/tmp/e2e"))

        manifest = self.manifest()
        manifest["scenario"]["multi_client"]["secondary"]["command"] = "echo unsafe"
        with self.assertRaisesRegex(MODULE.MultiClientError, "unknown field"):
            MODULE.compile_secondary(manifest, artifact_dir=Path("/tmp/e2e"))

    def test_materialize_writes_reviewable_actor_plan_without_secret_value(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest_path = root / "scenario-manifest.json"
            manifest_path.write_text(json.dumps(self.manifest()), encoding="utf-8")
            MODULE.materialize(manifest_path, root)
            env_text = (root / "multi-client-secondary.env").read_text(encoding="utf-8")
            plan = json.loads((root / "multi-client-plan.json").read_text(encoding="utf-8"))

        self.assertIn("AGENT_E2E_PASSWORD_ENV=AGENT_E2E_TEST_PASSWORD", env_text)
        self.assertNotIn("AGENT_E2E_PASSWORD=", env_text)
        self.assertEqual(plan["primary_character"], "Knight 1")
        self.assertEqual(plan["secondary"]["character"], "Knight 2")
        self.assertEqual(plan["secondary"]["password_env"], "AGENT_E2E_TEST_PASSWORD")

    def test_committed_runtime_contract_is_bounded_and_parent_watched(self) -> None:
        helper = (REPO_ROOT / "tools" / "e2e" / "client" / "agent_e2e_multi_client.lua").read_text(encoding="utf-8")
        secondary = (REPO_ROOT / "tools" / "e2e" / "client" / "agent_e2e_multi_client_secondary.lua").read_text(encoding="utf-8")
        primary = (REPO_ROOT / "tools" / "e2e" / "client" / "agent_e2e_multi_client_visibility.lua").read_text(encoding="utf-8")
        scenario = json.loads(
            (REPO_ROOT / "tests" / "e2e" / "scenarios" / "multiclient" / "shared-world-visibility.json").read_text(encoding="utf-8")
        )

        self.assertIn('timeout --signal=TERM', helper)
        self.assertIn('if ! kill -0 ', helper)
        self.assertIn('AGENT_E2E_PASSWORD_ENV', secondary)
        self.assertIn('multi_client_mutual_visibility', primary)
        self.assertEqual(scenario["multi_client"]["secondary"]["account"], "@test2")
        self.assertEqual(scenario["multi_client"]["secondary"]["character"], "Knight 2")
        self.assertEqual(scenario["fixture"]["character"], "Knight 1")
        self.assertIn("SELECT COUNT(*) = 0 FROM players_online", scenario["assertions"]["sql"])


if __name__ == "__main__":
    unittest.main()
