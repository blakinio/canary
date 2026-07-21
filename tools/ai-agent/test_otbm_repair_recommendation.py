from __future__ import annotations

import copy
import unittest

from otbm_repair_recommendation import (
    PATCH_PLAN_FORMAT,
    PREFLIGHT_FORMAT,
    REPORT_FORMAT,
    REQUEST_FORMAT,
    RepairRecommendationError,
    build_repair_recommendation,
    canonical_report_sha256,
)

SOURCE_SHA = "a" * 64
FINDING_SHA = "b" * 64
REQUEST_SHA = "c" * 64
PREFLIGHT_SHA = "d" * 64
SELECTOR = {"position": [100, 101, 7], "actionId": 4501}


def pin(report_format: str, digest: str, name: str) -> dict:
    return {"fileName": name, "size": 123, "sha256": digest, "format": report_format}


def request(
    *,
    kind: str = "attribute-replacement",
    runtime_required: bool = True,
    expected_old_state: object = 4501,
    proposed_target_state: object = 4502,
    operation_kind: str | None = "set-action-id",
    position: list[int] | None = None,
    region: dict | None = None,
) -> dict:
    mutation = {
        "kind": kind,
        "expectedOldState": expected_old_state,
        "proposedTargetState": proposed_target_state,
    }
    if operation_kind is not None:
        mutation["operationKind"] = operation_kind
    if position is not None:
        mutation["position"] = position
    if region is not None:
        mutation["region"] = region
    return {
        "format": REQUEST_FORMAT,
        "schemaVersion": 1,
        "finding": {
            "reportFormat": "canary-otbm-world-health-v1",
            "reportSha256": FINDING_SHA,
            "id": "finding-001",
        },
        "sourceMapSha256": SOURCE_SHA,
        "selector": copy.deepcopy(SELECTOR),
        "mutation": mutation,
        "runtimeHandlingRequired": runtime_required,
        "rationale": "Exact evidence requires human review of the proposed repair path.",
    }


def preflight(
    *,
    matched: int = 1,
    anchor_status: str = "exact",
    runtime_status: str = "handled-directly",
    runtime_resolved: bool = True,
    correlated: bool = True,
    patchable: bool = True,
    review_ready: bool = True,
    draft_plan: dict | None = None,
) -> dict:
    candidates = []
    for index in range(matched):
        candidates.append(
            {
                "auditIndex": index,
                "placement": {"position": [100, 101, 7], "itemId": 1949, "actionId": 4501},
                "anchorStatus": anchor_status,
                "tilePlacementIndex": 0 if anchor_status == "exact" else None,
                "anchors": [],
                "scriptResolution": {"status": runtime_status},
            }
        )
    if draft_plan is None and patchable and review_ready:
        draft_plan = {
            "format": PATCH_PLAN_FORMAT,
            "source": {"sha256": SOURCE_SHA},
            "region": {"from": [100, 101, 7], "to": [100, 101, 7]},
            "operations": [{"kind": "set-action-id"}],
        }
    return {
        "format": PREFLIGHT_FORMAT,
        "ok": matched > 0,
        "selector": copy.deepcopy(SELECTOR),
        "source": {
            "fileName": "world.otbm",
            "sha256": SOURCE_SHA,
            "size": 1000,
            "otbmVersion": 4,
            "itemsMajor": 3,
            "itemsMinor": 57,
        },
        "summary": {
            "matchedCandidates": matched,
            "anchorStatusCounts": {anchor_status: matched} if matched else {},
            "scriptStatusCounts": {runtime_status: matched} if matched else {},
            "runtimeUnresolvedCandidates": 0 if runtime_resolved else matched,
            "conflictingCandidates": matched if runtime_status == "conflicting" else 0,
            "draftPlanReady": bool(draft_plan),
            "readiness": {
                "matched": matched > 0,
                "correlated": correlated,
                "runtimeResolved": runtime_resolved,
                "runtimeStatus": runtime_status,
                "patchable": patchable,
                "reviewReady": review_ready,
            },
        },
        "candidates": candidates,
        "draftPlan": draft_plan,
        "draftPlanError": None,
        "warnings": [],
        "review": {
            "requiresHumanReview": True,
            "gameplayCorrectnessProven": False,
            "playerIntentProven": False,
            "unresolvedEvidencePreserved": True,
            "mapModified": False,
        },
        "replacementScriptResolution": None,
        "evidence": {
            "itemAudit": {"format": "canary-otbm-item-audit-v1", "summary": {}},
            "patchAnchors": {"format": "canary-otbm-patch-anchors-native-v1", "anchors": matched, "scannerSha256": "e" * 64},
            "scriptResolution": {"format": "canary-otbm-script-resolution-v1", "summary": {}, "scriptRoots": []},
        },
    }


def pins() -> dict:
    return {
        "request": pin(REQUEST_FORMAT, REQUEST_SHA, "request.json"),
        "repairPreflight": pin(PREFLIGHT_FORMAT, PREFLIGHT_SHA, "preflight.json"),
    }


class RepairRecommendationTests(unittest.TestCase):
    def test_review_ready_phase8_plan_yields_supported_attribute_path(self) -> None:
        report = build_repair_recommendation(request=request(), repair_preflight=preflight(), input_pins=pins())

        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["state"], "supported-by-existing-attribute-path")
        self.assertEqual(report["capability"]["family"], "phase8-attribute")
        self.assertEqual(report["capability"]["mode"], "set-action-id")
        self.assertTrue(report["capability"]["technicalPathSupported"])
        self.assertTrue(report["review"]["requiresHumanReview"])
        self.assertFalse(report["review"]["approvalGenerated"])
        self.assertFalse(report["review"]["supportedPathMeansRepairCorrect"])

    def test_no_matched_target_is_no_repair_evidence(self) -> None:
        report = build_repair_recommendation(
            request=request(),
            repair_preflight=preflight(matched=0, correlated=False, patchable=False, review_ready=False, draft_plan=None),
            input_pins=pins(),
        )
        self.assertEqual(report["state"], "no-repair-evidence")
        self.assertIn("NO_MATCHED_REPAIR_TARGET", report["blockers"])

    def test_ambiguous_target_fails_closed(self) -> None:
        report = build_repair_recommendation(
            request=request(),
            repair_preflight=preflight(matched=2, anchor_status="ambiguous", correlated=False, patchable=False, review_ready=False, draft_plan=None),
            input_pins=pins(),
        )
        self.assertEqual(report["state"], "ambiguous-target")
        self.assertFalse(report["capability"]["technicalPathSupported"])

    def test_unresolved_runtime_evidence_blocks_runtime_dependent_recommendation(self) -> None:
        report = build_repair_recommendation(
            request=request(runtime_required=True),
            repair_preflight=preflight(runtime_status="unresolved", runtime_resolved=False, patchable=False, review_ready=False, draft_plan=None),
            input_pins=pins(),
        )
        self.assertEqual(report["state"], "blocked-by-runtime-evidence")
        self.assertIn("RUNTIME_EVIDENCE_NOT_RESOLVED", report["blockers"])

    def test_missing_phase8_draft_remains_review_required(self) -> None:
        report = build_repair_recommendation(
            request=request(),
            repair_preflight=preflight(patchable=False, review_ready=False, draft_plan=None),
            input_pins=pins(),
        )
        self.assertEqual(report["state"], "review-required")
        self.assertIn("PHASE8_REVIEW_READY_DRAFT_PLAN_MISSING", report["blockers"])

    def test_complete_zero_translation_tile_area_shape_is_capability_only(self) -> None:
        area_request = request(
            kind="tile-area-materialization",
            runtime_required=False,
            expected_old_state={"regionRole": "current"},
            proposed_target_state={"regionRole": "donor"},
            operation_kind=None,
            region={
                "policy": "replace-region",
                "from": [256, 512, 7],
                "to": [511, 767, 7],
                "translationDelta": [0, 0, 0],
            },
        )
        report = build_repair_recommendation(request=area_request, repair_preflight=preflight(), input_pins=pins())

        self.assertEqual(report["state"], "supported-by-existing-tile-area-path")
        self.assertTrue(report["capability"]["capabilityOnly"])
        self.assertIn("reviewed-region-merge-plan-required", report["downstreamRequirements"])
        self.assertIn("explicit-approval-required", report["downstreamRequirements"])

    def test_partial_tile_area_shape_is_unsupported(self) -> None:
        area_request = request(
            kind="tile-area-materialization",
            runtime_required=False,
            operation_kind=None,
            region={
                "policy": "replace-region",
                "from": [256, 512, 7],
                "to": [500, 700, 7],
                "translationDelta": [0, 0, 0],
            },
        )
        report = build_repair_recommendation(request=area_request, repair_preflight=preflight(), input_pins=pins())
        self.assertEqual(report["state"], "unsupported-mutation-shape")
        self.assertIn("TILE_AREA_PARTIAL_REGION_UNSUPPORTED", report["blockers"])

    def test_raw_tile_replacement_requires_exact_selector_position(self) -> None:
        raw_request = request(
            kind="raw-tile-replacement",
            runtime_required=False,
            operation_kind=None,
            expected_old_state={"rawTileSha256": "1" * 64},
            proposed_target_state={"rawTileSha256": "2" * 64},
            position=[100, 101, 7],
        )
        report = build_repair_recommendation(request=raw_request, repair_preflight=preflight(), input_pins=pins())
        self.assertEqual(report["state"], "supported-by-existing-raw-tile-path")
        self.assertEqual(report["capability"]["mode"], "bounded-raw-tile-replacement")
        self.assertIn("exact-raw-span-and-canonical-tile-evidence-required", report["downstreamRequirements"])

    def test_raw_tile_insertion_requires_absent_old_state(self) -> None:
        raw_request = request(
            kind="raw-tile-insertion",
            runtime_required=False,
            operation_kind=None,
            expected_old_state={"present": True},
            proposed_target_state={"rawTileSha256": "2" * 64},
            position=[100, 101, 7],
        )
        report = build_repair_recommendation(request=raw_request, repair_preflight=preflight(), input_pins=pins())
        self.assertEqual(report["state"], "unsupported-mutation-shape")
        self.assertIn("RAW_TILE_INSERTION_EXPECTS_ABSENT_OLD_STATE", report["blockers"])

    def test_raw_tile_type_conversion_requires_exact_5_14_pair(self) -> None:
        valid = request(
            kind="raw-tile-type-conversion",
            runtime_required=False,
            operation_kind=None,
            expected_old_state={"nodeType": 5},
            proposed_target_state={"nodeType": 14},
            position=[100, 101, 7],
        )
        report = build_repair_recommendation(request=valid, repair_preflight=preflight(), input_pins=pins())
        self.assertEqual(report["state"], "supported-by-existing-raw-tile-path")

        invalid = copy.deepcopy(valid)
        invalid["mutation"]["proposedTargetState"] = {"nodeType": 5}
        invalid_report = build_repair_recommendation(request=invalid, repair_preflight=preflight(), input_pins=pins())
        self.assertEqual(invalid_report["state"], "unsupported-mutation-shape")
        self.assertIn("RAW_TILE_TYPE_CONVERSION_NODE_TYPES_UNSUPPORTED", invalid_report["blockers"])

    def test_selector_or_source_mismatch_is_rejected(self) -> None:
        mismatched_source = preflight()
        mismatched_source["source"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(RepairRecommendationError, "source map SHA-256 does not match"):
            build_repair_recommendation(request=request(), repair_preflight=mismatched_source, input_pins=pins())

        mismatched_selector = preflight()
        mismatched_selector["selector"] = {"position": [100, 101, 7], "actionId": 9999}
        with self.assertRaisesRegex(RepairRecommendationError, "selector does not exactly match"):
            build_repair_recommendation(request=request(), repair_preflight=mismatched_selector, input_pins=pins())

    def test_semantic_output_is_deterministic(self) -> None:
        first = build_repair_recommendation(request=request(), repair_preflight=preflight(), input_pins=pins())
        second = build_repair_recommendation(
            request=copy.deepcopy(request()),
            repair_preflight=copy.deepcopy(preflight()),
            input_pins=copy.deepcopy(pins()),
        )
        self.assertEqual(first, second)
        self.assertEqual(canonical_report_sha256(first), canonical_report_sha256(second))


if __name__ == "__main__":
    unittest.main()
