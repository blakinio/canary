from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_reviewed_candidate_repair import APPROVAL_FORMAT, REPORT_FORMAT

REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVAL_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR_APPROVAL.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR.schema.json"


class ReviewedCandidateRepairSchemaTests(unittest.TestCase):
    def test_approval_schema_pins_exact_review_and_mutation_authorization(self) -> None:
        schema = json.loads(APPROVAL_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], APPROVAL_FORMAT)
        required = set(schema["required"])
        self.assertTrue(
            {
                "approved",
                "recommendationSha256",
                "sourceMapSha256",
                "selector",
                "expectedOldState",
                "intendedTargetState",
                "pipelineMode",
                "mutationAuthorization",
                "review",
            }.issubset(required)
        )
        self.assertEqual(
            set(schema["properties"]["pipelineMode"]["enum"]),
            {
                "fixed-width-attribute",
                "tile-area",
                "tile-replacement",
                "tile-insertion",
                "tile-deletion",
                "tile-type-conversion",
            },
        )
        self.assertEqual(
            set(schema["properties"]["mutationAuthorization"]["properties"]["format"]["enum"]),
            {
                "canary-otbm-bounded-patch-plan-v1",
                "canary-otbm-area-materialization-approval-v1",
                "canary-otbm-tile-materialization-approval-v1",
                "canary-otbm-tile-insertion-approval-v1",
                "canary-otbm-tile-deletion-approval-v1",
                "canary-otbm-tile-type-conversion-approval-v1",
            },
        )

    def test_report_schema_preserves_separate_evidence_stages(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(
            set(schema["properties"]["status"]["enum"]),
            {"physically-validated", "validated-no-physical-e2e-required", "physical-e2e-required"},
        )
        provenance_required = set(schema["properties"]["provenance"]["required"])
        self.assertEqual(
            provenance_required,
            {
                "recommendation",
                "approval",
                "pipelineResult",
                "semanticDiff",
                "impactedSelection",
                "physicalValidation",
            },
        )
        safety = schema["properties"]["safety"]["properties"]
        self.assertFalse(safety["approvalGenerated"]["const"])
        self.assertFalse(safety["mapModified"]["const"])
        self.assertFalse(safety["pipelineExecutedByOrchestrator"]["const"])
        self.assertFalse(safety["physicalE2eExecutedByOrchestrator"]["const"])
        self.assertTrue(safety["existingMutationBoundaryReused"]["const"])
        self.assertTrue(safety["existingCandidateValidationReused"]["const"])
        self.assertFalse(safety["productionMapDeployed"]["const"])
        self.assertFalse(safety["globalGameplayCorrectnessProven"]["const"])

    def test_pending_physical_e2e_state_is_fail_closed_in_schema(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        conditional = schema["allOf"][0]
        self.assertEqual(
            conditional["if"]["properties"]["status"]["const"],
            "physical-e2e-required",
        )
        self.assertFalse(conditional["then"]["properties"]["ok"]["const"])
        self.assertEqual(
            conditional["then"]["properties"]["blockers"]["contains"]["const"],
            "SELECTED_PHYSICAL_E2E_NOT_EXECUTED",
        )
        self.assertTrue(conditional["else"]["properties"]["ok"]["const"])


if __name__ == "__main__":
    unittest.main()
