from __future__ import annotations

import json
import unittest
from pathlib import Path

from tibia_reference_adoption_router import (
    ALL_TARGETS,
    REPORT_FORMAT,
    REQUEST_FORMAT,
)

ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = ROOT / "docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING_REQUEST.schema.json"
REPORT_SCHEMA = ROOT / "docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING.schema.json"


class AdoptionRouterSchemaTests(unittest.TestCase):
    def load(self, path: Path) -> dict[str, object]:
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(document, dict)
        return document

    def test_request_schema_target_inventory_matches_code_allowlist(self) -> None:
        schema = self.load(REQUEST_SCHEMA)
        self.assertEqual(schema["properties"]["format"]["const"], REQUEST_FORMAT)
        target_options = schema["$defs"]["target"]["oneOf"]
        schema_targets = {
            (
                option["properties"]["owner"]["const"],
                option["properties"]["capability"]["const"],
            )
            for option in target_options
        }
        self.assertEqual(schema_targets, ALL_TARGETS)
        for option in target_options:
            self.assertEqual(option["type"], "object")
            self.assertFalse(option["additionalProperties"])
            self.assertEqual(option["required"], ["owner", "capability"])
        self.assertNotIn(
            ("otbm-area-materializer", "canary-otbm-area-materialization-result-v1"),
            schema_targets,
        )
        self.assertNotIn(
            ("otbm-bounded-phase8-writer", "canary-otbm-bounded-patch-result-v1"),
            schema_targets,
        )

    def test_report_schema_preserves_non_execution_policy(self) -> None:
        schema = self.load(REPORT_SCHEMA)
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        policy = schema["properties"]["policy"]["properties"]
        self.assertTrue(policy["readOnlyRouting"]["const"])
        self.assertTrue(policy["reviewedRequestRequired"]["const"])
        self.assertTrue(policy["exactFindingReferencesRequired"]["const"])
        self.assertFalse(policy["infersMutationTarget"]["const"])
        self.assertFalse(policy["expandsWriters"]["const"])
        self.assertFalse(policy["generatesApproval"]["const"])
        self.assertFalse(policy["executesWriterOrMaterializer"]["const"])
        self.assertFalse(policy["mutatesMapOrGameState"]["const"])
        self.assertFalse(policy["deploys"]["const"])
        self.assertFalse(policy["runsE2e"]["const"])
        self.assertFalse(policy["claimsGameplayParity"]["const"])
        self.assertTrue(policy["mapChangesRouteThroughQa003"]["const"])
        self.assertTrue(policy["unsupportedOutcomesPreserved"]["const"])


if __name__ == "__main__":
    unittest.main()
