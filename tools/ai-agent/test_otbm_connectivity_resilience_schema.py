from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_connectivity_resilience import MANIFEST_FORMAT, MODES, REPORT_FORMAT, ROUTE_CLASSIFICATIONS

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE_MANIFEST.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_CONNECTIVITY_RESILIENCE.schema.json"


class ConnectivityResilienceSchemaTests(unittest.TestCase):
    def test_manifest_schema_matches_public_contract(self) -> None:
        schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertEqual(set(schema["$defs"]["mode"]["enum"]), MODES)
        self.assertEqual(schema["properties"]["region"]["$ref"], "#/$defs/region" if "$ref" in schema["properties"]["region"] else schema["properties"]["region"].get("$ref"))

    def test_report_schema_matches_route_classifications(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(
            set(schema["$defs"]["route"]["properties"]["classification"]["enum"]),
            ROUTE_CLASSIFICATIONS,
        )
        self.assertFalse(schema["$defs"]["entrapment"]["properties"]["runtimeEntrapmentProven"]["const"])

    def test_policy_forbids_duplicate_pathfinding_and_runtime_claims(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        policy = schema["properties"]["policy"]["properties"]
        for field in (
            "canonicalReachabilityBfsReused",
            "canonicalMovementNeighborsReused",
            "canonicalTransitionEdgesReused",
            "canonicalCycleDetectionReused",
        ):
            self.assertTrue(policy[field]["const"], field)
        for field in (
            "secondPathfinderImplemented",
            "dynamicLuaExecuted",
            "runtimeEntrapmentClaimed",
            "globalConnectivityClaimed",
            "physicalE2EExecuted",
        ):
            self.assertFalse(policy[field]["const"], field)


if __name__ == "__main__":
    unittest.main()
