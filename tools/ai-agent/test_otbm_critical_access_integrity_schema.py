from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_critical_access_integrity import (
    ACCESS_EXPECTATIONS,
    CLASSIFICATIONS,
    CRITICALITY_KINDS,
    ENTITY_ROLES,
    MANIFEST_FORMAT,
    REPORT_FORMAT,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGETS_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_CRITICAL_ACCESS_TARGETS.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.schema.json"


class CriticalAccessIntegritySchemaTests(unittest.TestCase):
    def test_targets_schema_matches_public_contract(self) -> None:
        schema = json.loads(TARGETS_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertEqual(
            set(schema["$defs"]["criticalLandmark"]["properties"]["criticality"]["enum"]),
            CRITICALITY_KINDS,
        )
        self.assertEqual(set(schema["$defs"]["spawnAccess"]["properties"]["entityRole"]["enum"]), ENTITY_ROLES)
        self.assertEqual(
            set(schema["$defs"]["spawnAccess"]["properties"]["accessExpectation"]["enum"]),
            ACCESS_EXPECTATIONS,
        )

    def test_report_schema_matches_classifications_and_static_boundaries(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(set(schema["$defs"]["classification"]["enum"]), CLASSIFICATIONS)
        policy = schema["properties"]["policy"]["properties"]
        for field in (
            "readOnly",
            "semanticLandmarkResolverReused",
            "worldIndexReused",
            "connectivityReportConsumed",
        ):
            self.assertTrue(policy[field]["const"], field)
        for field in (
            "criticalityInferred",
            "pathfindingPerformed",
            "geometryRecomputed",
            "spawnNpcRescanned",
            "dynamicLuaExecuted",
            "runtimeAccessClaimed",
            "publicAccessibilityInferred",
            "mapModified",
            "physicalE2EExecuted",
            "changeBypassSeverClaimed",
        ):
            self.assertFalse(policy[field]["const"], field)
        self.assertFalse(
            schema["$defs"]["spawnResult"]["properties"]["intendedPublicAccessibilityProven"]["const"]
        )
        self.assertFalse(schema["$defs"]["houseResult"]["properties"]["runtimeAccessProven"]["const"])


if __name__ == "__main__":
    unittest.main()
