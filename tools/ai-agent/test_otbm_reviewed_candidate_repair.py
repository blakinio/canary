from __future__ import annotations

import copy
import unittest

from otbm_reviewed_candidate_repair import (
    APPROVAL_FORMAT,
    IMPACTED_SELECTION_FORMAT,
    PHYSICAL_VALIDATION_FORMAT,
    PIPELINE_FORMAT,
    RECOMMENDATION_FORMAT,
    REPORT_FORMAT,
    SEMANTIC_DIFF_FORMAT,
    ReviewedCandidateRepairError,
    build_reviewed_candidate_repair_report,
)

SOURCE_SHA = "1" * 64
CANDIDATE_SHA = "2" * 64
BEFORE_INDEX_SHA = "3" * 64
AFTER_INDEX_SHA = "4" * 64
AUTH_SHA = "5" * 64
RECOMMENDATION_SHA = "a" * 64
APPROVAL_SHA = "b" * 64
PIPELINE_SHA = "c" * 64
DIFF_SHA = "d" * 64
SELECTION_SHA = "e" * 64
PHYSICAL_SHA = "f" * 64

MODE_CASES = {
    "attribute": {
        "state": "supported-by-existing-attribute-path",
        "family": "phase8-attribute",
        "capabilityMode": "set-action-id",
        "mutationKind": "attribute-replacement",
        "operationKind": "set-action-id",
        "pipelineMode": "fixed-width-attribute",
        "authorizationFormat": "canary-otbm-bounded-patch-plan-v1",
    },
    "tile-area": {
        "state": "supported-by-existing-tile-area-path",
        "family": "tile-area",
        "capabilityMode": "complete-zero-translation-replace-region",
        "mutationKind": "tile-area-materialization",
        "pipelineMode": "tile-area",
        "authorizationFormat": "canary-otbm-area-materialization-approval-v1",
    },
    "tile-replacement": {
        "state": "supported-by-existing-raw-tile-path",
        "family": "raw-tile",
        "capabilityMode": "bounded-raw-tile-replacement",
        "mutationKind": "raw-tile-replacement",
        "pipelineMode": "tile-replacement",
        "authorizationFormat": "canary-otbm-tile-materialization-approval-v1",
    },
    "tile-insertion": {
        "state": "supported-by-existing-raw-tile-path",
        "family": "raw-tile",
        "capabilityMode": "bounded-raw-tile-insertion",
        "mutationKind": "raw-tile-insertion",
        "pipelineMode": "tile-insertion",
        "authorizationFormat": "canary-otbm-tile-insertion-approval-v1",
    },
    "tile-deletion": {
        "state": "supported-by-existing-raw-tile-path",
        "family": "raw-tile",
        "capabilityMode": "bounded-raw-tile-deletion",
        "mutationKind": "raw-tile-deletion",
        "pipelineMode": "tile-deletion",
        "authorizationFormat": "canary-otbm-tile-deletion-approval-v1",
    },
    "tile-type-conversion": {
        "state": "supported-by-existing-raw-tile-path",
        "family": "raw-tile",
        "capabilityMode": "bounded-raw-tile-type-conversion",
        "mutationKind": "raw-tile-type-conversion",
        "pipelineMode": "tile-type-conversion",
        "authorizationFormat": "canary-otbm-tile-type-conversion-approval-v1",
    },
}


def input_pins() -> dict:
    return {
        "recommendation": {"fileName": "recommendation.json", "size": 10, "sha256": RECOMMENDATION_SHA, "format": RECOMMENDATION_FORMAT},
        "approval": {"fileName": "approval.json", "size": 11, "sha256": APPROVAL_SHA, "format": APPROVAL_FORMAT},
        "pipelineResult": {"fileName": "pipeline.json", "size": 12, "sha256": PIPELINE_SHA, "format": PIPELINE_FORMAT},
        "semanticDiff": {"fileName": "diff.json", "size": 13, "sha256": DIFF_SHA, "format": SEMANTIC_DIFF_FORMAT},
        "impactedSelection": {"fileName": "selection.json", "size": 14, "sha256": SELECTION_SHA, "format": IMPACTED_SELECTION_FORMAT},
        "physicalValidation": {"fileName": "physical.json", "size": 15, "sha256": PHYSICAL_SHA, "format": PHYSICAL_VALIDATION_FORMAT},
    }


def make_bundle(case_name: str = "attribute", *, selected_count: int = 1, performed: bool = True) -> dict:
    case = MODE_CASES[case_name]
    selector = {"position": [100, 101, 7], "actionId": 1234}
    old_state = {"value": "old"}
    target_state = {"value": "new"}
    mutation = {
        "kind": case["mutationKind"],
        "expectedOldState": old_state,
        "proposedTargetState": target_state,
    }
    if "operationKind" in case:
        mutation["operationKind"] = case["operationKind"]

    recommendation = {
        "format": RECOMMENDATION_FORMAT,
        "schemaVersion": 1,
        "state": case["state"],
        "source": {"mapSha256": SOURCE_SHA, "finding": {"reportFormat": "fixture", "reportSha256": "6" * 64, "id": "finding-1"}},
        "selector": selector,
        "mutation": mutation,
        "capability": {
            "family": case["family"],
            "mode": case["capabilityMode"],
            "technicalPathSupported": True,
            "capabilityOnly": True,
        },
        "blockers": [],
    }
    approval = {
        "format": APPROVAL_FORMAT,
        "schemaVersion": 1,
        "approved": True,
        "recommendationSha256": RECOMMENDATION_SHA,
        "sourceMapSha256": SOURCE_SHA,
        "selector": selector,
        "expectedOldState": old_state,
        "intendedTargetState": target_state,
        "pipelineMode": case["pipelineMode"],
        "mutationAuthorization": {"format": case["authorizationFormat"], "sha256": AUTH_SHA},
        "review": {"reviewer": "reviewer@example.invalid", "rationale": "Exact reviewed repair fixture."},
    }
    pipeline = {
        "format": PIPELINE_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "mode": case["pipelineMode"],
        "source": {"sha256": SOURCE_SHA, "unchanged": True},
        "output": {"sha256": CANDIDATE_SHA, "createNew": True, "byteIdenticalToVerifiedCandidate": True},
        "inputs": {
            "authorization": {"fileName": "authorization.json", "size": 1, "sha256": AUTH_SHA, "format": case["authorizationFormat"]},
            "other": {"fileName": "other.json", "size": 1, "sha256": "7" * 64, "format": "fixture-v1"},
        },
        "quality": {"format": "canary-otbm-map-quality-v1", "ok": True, "sourceSha256": CANDIDATE_SHA},
        "safety": {
            "sourceModifiedInPlace": False,
            "silentOverwrite": False,
            "existingMutationBoundaryReused": True,
            "existingMapQualityGateReused": True,
            "productionMapExecutionAuthorized": False,
        },
    }
    semantic_diff = {
        "format": SEMANTIC_DIFF_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "provenance": {
            "before": {"sourceMap": {"sha256": SOURCE_SHA}, "worldIndex": {"sha256": BEFORE_INDEX_SHA}},
            "after": {"sourceMap": {"sha256": CANDIDATE_SHA}, "worldIndex": {"sha256": AFTER_INDEX_SHA}},
        },
        "scope": {"type": "full-index"},
        "summary": {"findings": {"total": 1, "truncated": False}},
    }

    scenario_selected = selected_count == 1
    impacted_selection = {
        "format": IMPACTED_SELECTION_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "semanticDiff": {
            "sha256": DIFF_SHA,
            "beforeMapSha256": SOURCE_SHA,
            "afterMapSha256": CANDIDATE_SHA,
            "beforeWorldIndexSha256": BEFORE_INDEX_SHA,
            "afterWorldIndexSha256": AFTER_INDEX_SHA,
            "scopeType": "full-index",
            "findingsTotal": 1,
            "findingsTruncated": False,
        },
        "summary": {
            "scenarioCount": 1,
            "selectedCount": selected_count,
            "skippedCount": 1 - selected_count,
            "failClosedCount": 0,
        },
        "scenarios": [{"selected": scenario_selected}],
    }

    execution_scenarios = []
    if selected_count and performed:
        execution_scenarios = [{"executed": True, "returnCode": 0, "runtimeMapSha256": CANDIDATE_SHA}]
    physical_validation = {
        "format": PHYSICAL_VALIDATION_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "mode": "execute" if performed else "validate-only",
        "source": {"sha256": SOURCE_SHA, "unchanged": True},
        "candidate": {"sha256": CANDIDATE_SHA, "createNew": True},
        "evidence": {
            "pipelineResult": {"sha256": PIPELINE_SHA},
            "semanticDiff": {"sha256": DIFF_SHA},
            "impactedSelection": {"sha256": SELECTION_SHA},
        },
        "selection": {
            "scenarioCount": 1,
            "selectedCount": selected_count,
            "skippedCount": 1 - selected_count,
            "failClosedCount": 0,
            "selectedScenarios": [{}] if selected_count else [],
        },
        "execution": {
            "requested": performed,
            "required": bool(selected_count),
            "performed": performed,
            "runtimeWorkspaceRemoved": True,
            "scenarios": execution_scenarios,
        },
    }
    return {
        "recommendation": recommendation,
        "approval": approval,
        "pipeline_result": pipeline,
        "semantic_diff": semantic_diff,
        "impacted_selection": impacted_selection,
        "physical_validation": physical_validation,
        "input_pins": input_pins(),
    }


def build(bundle: dict) -> dict:
    return build_reviewed_candidate_repair_report(**bundle)


class ReviewedCandidateRepairTests(unittest.TestCase):
    def test_all_existing_pipeline_mode_bindings_validate(self) -> None:
        for case_name, case in MODE_CASES.items():
            with self.subTest(case=case_name):
                report = build(make_bundle(case_name))
                self.assertTrue(report["ok"])
                self.assertEqual(report["status"], "physically-validated")
                self.assertEqual(report["pipeline"]["mode"], case["pipelineMode"])
                self.assertEqual(report["approval"]["mutationAuthorization"]["format"], case["authorizationFormat"])

    def test_zero_selected_scenarios_is_validated_without_physical_execution(self) -> None:
        report = build(make_bundle(selected_count=0, performed=False))
        self.assertTrue(report["ok"])
        self.assertEqual(report["status"], "validated-no-physical-e2e-required")
        self.assertFalse(report["physicalValidation"]["required"])
        self.assertFalse(report["physicalValidation"]["performed"])
        self.assertEqual(report["blockers"], [])

    def test_selected_scenario_without_execution_is_explicitly_pending(self) -> None:
        report = build(make_bundle(selected_count=1, performed=False))
        self.assertFalse(report["ok"])
        self.assertEqual(report["status"], "physical-e2e-required")
        self.assertEqual(report["blockers"], ["SELECTED_PHYSICAL_E2E_NOT_EXECUTED"])

    def test_same_inputs_are_deterministic(self) -> None:
        bundle = make_bundle()
        self.assertEqual(build(bundle), build(copy.deepcopy(bundle)))

    def test_non_supported_recommendation_fails_closed(self) -> None:
        bundle = make_bundle()
        bundle["recommendation"]["state"] = "review-required"
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_approval_recommendation_sha_mismatch_fails(self) -> None:
        bundle = make_bundle()
        bundle["approval"]["recommendationSha256"] = "9" * 64
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_approval_mode_mismatch_fails(self) -> None:
        bundle = make_bundle()
        bundle["approval"]["pipelineMode"] = "tile-area"
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_pipeline_must_contain_exact_authorization_pin(self) -> None:
        bundle = make_bundle()
        bundle["pipeline_result"]["inputs"]["authorization"]["sha256"] = "8" * 64
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_semantic_diff_candidate_mismatch_fails(self) -> None:
        bundle = make_bundle()
        bundle["semantic_diff"]["provenance"]["after"]["sourceMap"]["sha256"] = "8" * 64
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_impacted_selection_semantic_diff_pin_mismatch_fails(self) -> None:
        bundle = make_bundle()
        bundle["impacted_selection"]["semanticDiff"]["sha256"] = "8" * 64
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_physical_validation_pipeline_pin_mismatch_fails(self) -> None:
        bundle = make_bundle()
        bundle["physical_validation"]["evidence"]["pipelineResult"]["sha256"] = "8" * 64
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_performed_physical_validation_requires_candidate_runtime_hash(self) -> None:
        bundle = make_bundle()
        bundle["physical_validation"]["execution"]["scenarios"][0]["runtimeMapSha256"] = "8" * 64
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_selected_count_must_match_scenario_decisions(self) -> None:
        bundle = make_bundle()
        bundle["impacted_selection"]["scenarios"][0]["selected"] = False
        with self.assertRaises(ReviewedCandidateRepairError):
            build(bundle)

    def test_output_contract_keeps_orchestrator_non_mutating(self) -> None:
        report = build(make_bundle())
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertFalse(report["safety"]["mapModified"])
        self.assertFalse(report["safety"]["approvalGenerated"])
        self.assertFalse(report["safety"]["pipelineExecutedByOrchestrator"])
        self.assertFalse(report["safety"]["physicalE2eExecutedByOrchestrator"])
        self.assertFalse(report["safety"]["productionMapDeployed"])


if __name__ == "__main__":
    unittest.main()
