from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_quest_state_reachability import (
    GOAL_CLASSIFICATIONS,
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    STORAGE_NAMESPACES,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY_MANIFEST.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_QUEST_STATE_REACHABILITY.schema.json"


class QuestStateReachabilitySchemaTests(unittest.TestCase):
    def test_manifest_schema_matches_public_contract(self) -> None:
        schema = json.loads(MANIFEST_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertEqual(set(schema["$defs"]["namespace"]["enum"]), STORAGE_NAMESPACES)
        self.assertEqual(
            schema["$defs"]["interactionQuery"]["anyOf"],
            [{"required": ["transitionId"]}, {"required": ["position"]}],
        )

    def test_report_schema_preserves_reachability_classifications(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(set(schema["$defs"]["goal"]["properties"]["classification"]["enum"]), GOAL_CLASSIFICATIONS)
        self.assertFalse(schema["$defs"]["target"]["properties"]["runtimeGameplayCompletionProven"]["const"])

    def test_policy_forbids_duplicate_analysis_and_runtime_claims(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        policy = schema["properties"]["policy"]["properties"]
        self.assertFalse(policy["storageGraphRecomputed"]["const"])
        self.assertTrue(policy["routeInteractionResolverReused"]["const"])
        for field in (
            "dynamicLuaExecuted",
            "executionOrderInferred",
            "globalImpossibilityClaimed",
            "runtimeGameplayCompletionClaimed",
        ):
            self.assertFalse(policy[field]["const"], field)
        self.assertEqual(policy["missingSelectedProducerMeans"]["const"], "external-or-unproven")


if __name__ == "__main__":
    unittest.main()
