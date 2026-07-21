from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_content_completeness import (
    CLASSIFICATIONS,
    DEPENDENCY_RELATIONS,
    MANIFEST_FORMAT,
    ORPHAN_FINDING_KINDS,
    REPORT_FORMAT,
    STAGE_ROLES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_CONTENT_COMPLETENESS_MANIFEST.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_CONTENT_COMPLETENESS.schema.json"


class ContentCompletenessSchemaTests(unittest.TestCase):
    def test_manifest_schema_matches_stage_and_orphan_contract(self) -> None:
        schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertEqual(set(schema["$defs"]["stage"]["properties"]["role"]["enum"]), STAGE_ROLES)
        self.assertEqual(set(schema["$defs"]["orphanCheck"]["properties"]["relations"]["items"]["enum"]), DEPENDENCY_RELATIONS)
        self.assertEqual(set(schema["$defs"]["orphanCheck"]["properties"]["findingKind"]["enum"]), ORPHAN_FINDING_KINDS)

    def test_report_schema_preserves_classifications_and_runtime_boundary(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(set(schema["$defs"]["classification"]["enum"]), CLASSIFICATIONS)
        self.assertFalse(schema["$defs"]["target"]["properties"]["runtimeGameplayCompletionProven"]["const"])

    def test_policy_forbids_duplicate_analysis_and_runtime_claims(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        policy = schema["$defs"]["policy"]["properties"]
        self.assertTrue(policy["readOnly"]["const"])
        for name in (
            "mapModified",
            "otbmParsedIndependently",
            "scriptResolutionRecomputed",
            "storageGraphRecomputed",
            "pathfindingExecuted",
            "dependencyGraphRecomputed",
            "physicalE2eExecuted",
            "dynamicLuaExecuted",
            "globalAbsenceInferred",
            "runtimeGameplayCompletionClaimed",
            "automaticRepairDirected",
            "certificationAssigned",
            "scenarioPrioritizationDirected",
        ):
            self.assertFalse(policy[name]["const"], name)


if __name__ == "__main__":
    unittest.main()
