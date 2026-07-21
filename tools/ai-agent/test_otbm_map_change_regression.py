from __future__ import annotations

import copy
import unittest

from otbm_map_change_regression import (
    IMPACTED_SELECTION_FORMAT,
    REPORT_FORMAT,
    SEMANTIC_DIFF_FORMAT,
    RegressionGuardError,
    build_regression_plan,
    canonical_report_sha256,
)

BEFORE_MAP = "a" * 64
AFTER_MAP = "b" * 64
BEFORE_INDEX = "c" * 64
AFTER_INDEX = "d" * 64
SEMANTIC_PIN_SHA = "1" * 64
SELECTION_PIN_SHA = "2" * 64
FINDING_ID = "otbm-diff:" + "3" * 24


def pin(report_format: str, digest: str, name: str) -> dict:
    return {
        "fileName": name,
        "size": 123,
        "sha256": digest,
        "format": report_format,
    }


def finding(
    *,
    finding_id: str = FINDING_ID,
    kind: str = "action-id-changed",
    classifications: list[str] | None = None,
    position: list[int] | None = None,
) -> dict:
    return {
        "id": finding_id,
        "kind": kind,
        "classifications": classifications or ["changed", "handler-affected"],
        "evidenceLevel": "semantic",
        "position": position if position is not None else [100, 101, 7],
        "before": 5000,
        "after": 5001,
        "details": {"mechanicType": "actionId", "itemId": 1949},
        "message": "actionId changed at an exactly aligned item stack slot",
        "correlations": [],
    }


def semantic_diff(
    *,
    findings: list[dict] | None = None,
    scope_type: str = "full-index",
    truncated: bool = False,
    total: int | None = None,
) -> dict:
    samples = list(findings or [])
    exact_total = len(samples) if total is None else total
    if samples:
        by_kind: dict[str, int] = {}
        by_classification: dict[str, int] = {}
        by_evidence: dict[str, int] = {}
        for sample in samples:
            by_kind[sample["kind"]] = by_kind.get(sample["kind"], 0) + 1
            for classification in sample["classifications"]:
                by_classification[classification] = by_classification.get(classification, 0) + 1
            level = sample["evidenceLevel"]
            by_evidence[level] = by_evidence.get(level, 0) + 1
        if exact_total > len(samples):
            by_kind = {samples[0]["kind"]: exact_total}
            by_classification = {classification: exact_total for classification in samples[0]["classifications"]}
            by_evidence = {samples[0]["evidenceLevel"]: exact_total}
    else:
        by_kind = {}
        by_classification = {}
        by_evidence = {}
    return {
        "format": SEMANTIC_DIFF_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "provenance": {
            "before": {
                "sourceMap": {"sha256": BEFORE_MAP},
                "worldIndex": {"sha256": BEFORE_INDEX},
            },
            "after": {
                "sourceMap": {"sha256": AFTER_MAP},
                "worldIndex": {"sha256": AFTER_INDEX},
            },
        },
        "compatibility": {"compatible": True},
        "policy": {},
        "scope": {
            "type": scope_type,
            "from": None if scope_type == "full-index" else [90, 90, 7],
            "to": None if scope_type == "full-index" else [110, 110, 7],
        },
        "summary": {
            "beforeTiles": 10,
            "afterTiles": 10,
            "beforePlacements": 20,
            "afterPlacements": 20,
            "unchangedTiles": 9,
            "changedPositions": 0 if exact_total == 0 else 1,
            "findings": {
                "total": exact_total,
                "byKind": by_kind,
                "byClassification": by_classification,
                "byEvidenceLevel": by_evidence,
                "sampleCount": len(samples),
                "truncated": truncated,
            },
        },
        "findings": samples,
        "correlation": {"enabled": False, "reports": [], "indexedNodes": 0},
    }


def impacted_selection(*, selected: bool, impacted_ids: list[str] | None = None) -> dict:
    reasons = (
        [{"code": "SEMANTIC_DIFF_INTERSECTS_BASELINE_ROUTE"}]
        if selected
        else [{"code": "EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT"}]
    )
    scenarios = [
        {
            "suite": "universal-e2e",
            "id": "route-a",
            "manifest": {"path": "scenario-a.json", "sha256": "4" * 64},
            "selected": selected,
            "decision": "selected" if selected else "skipped",
            "failClosed": False,
            "reasons": reasons,
            "impactedFindingIds": list(impacted_ids or []),
            "routePlans": [
                {
                    "routeId": "thais-reference",
                    "path": "route-thais-reference.json",
                    "sha256": "5" * 64,
                    "baselineCompatible": True,
                    "positionCount": 42,
                }
            ],
        }
    ]
    return {
        "format": IMPACTED_SELECTION_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "semanticDiff": {
            "path": "semantic-diff.json",
            "sha256": SEMANTIC_PIN_SHA,
            "beforeMapSha256": BEFORE_MAP,
            "afterMapSha256": AFTER_MAP,
            "beforeWorldIndexSha256": BEFORE_INDEX,
            "afterWorldIndexSha256": AFTER_INDEX,
            "scopeType": "full-index",
            "findingsTotal": 1,
            "findingsTruncated": False,
        },
        "policy": {
            "fullIndexRequiredForSkip": True,
            "truncatedDiffSelectsAll": True,
            "unknownFindingPositionSelectsAll": True,
            "staleOrMissingBaselineRouteSelectsScenario": True,
            "otbmParsed": False,
            "worldIndexBuilt": False,
            "routeCalculated": False,
            "physicalE2eExecuted": False,
            "mapModified": False,
        },
        "summary": {
            "scenarioCount": 1,
            "selectedCount": 1 if selected else 0,
            "skippedCount": 0 if selected else 1,
            "failClosedCount": 0,
        },
        "scenarios": scenarios,
    }


def input_pins(*, include_selection: bool = False) -> dict:
    pins = {"semanticDiff": pin(SEMANTIC_DIFF_FORMAT, SEMANTIC_PIN_SHA, "semantic-diff.json")}
    if include_selection:
        pins["impactedSelection"] = pin(IMPACTED_SELECTION_FORMAT, SELECTION_PIN_SHA, "impacted-selection.json")
    return pins


class RegressionGuardTests(unittest.TestCase):
    def test_changed_map_selects_static_validation_and_preserves_exact_finding_ids(self) -> None:
        report = build_regression_plan(
            semantic_diff=semantic_diff(findings=[finding()]),
            input_pins=input_pins(),
        )

        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["source"]["beforeMapSha256"], BEFORE_MAP)
        self.assertEqual(report["source"]["afterMapSha256"], AFTER_MAP)
        self.assertFalse(report["staticValidation"]["nonImpactProven"])
        self.assertEqual(report["summary"]["selectedStaticValidatorCount"], 7)
        for entry in report["staticValidation"]["selected"]:
            self.assertEqual(entry["impactedFindingIds"], [FINDING_ID])
            self.assertTrue(entry["findingIdsComplete"])
        self.assertTrue(report["physicalValidation"]["manualSelectionRequired"])
        self.assertFalse(report["physicalValidation"]["canSkipAny"])

    def test_exact_zero_full_index_diff_is_the_only_static_skip_authority(self) -> None:
        report = build_regression_plan(
            semantic_diff=semantic_diff(),
            input_pins=input_pins(),
        )

        self.assertTrue(report["staticValidation"]["nonImpactProven"])
        self.assertFalse(report["staticValidation"]["failClosed"])
        self.assertEqual(report["summary"]["selectedStaticValidatorCount"], 0)
        self.assertEqual(report["summary"]["skippedStaticValidatorCount"], 7)
        self.assertTrue(all(item["skipAuthorized"] for item in report["staticValidation"]["skipped"]))

    def test_bounded_or_truncated_evidence_fails_closed_toward_more_validation(self) -> None:
        bounded = build_regression_plan(
            semantic_diff=semantic_diff(scope_type="bounded-region"),
            input_pins=input_pins(),
        )
        self.assertTrue(bounded["staticValidation"]["failClosed"])
        self.assertEqual(bounded["summary"]["selectedStaticValidatorCount"], 7)
        self.assertIn("SEMANTIC_DIFF_SCOPE_NOT_FULL_INDEX", bounded["staticValidation"]["reasonCodes"])

        truncated = build_regression_plan(
            semantic_diff=semantic_diff(findings=[finding()], truncated=True, total=2),
            input_pins=input_pins(),
        )
        self.assertTrue(truncated["staticValidation"]["failClosed"])
        self.assertFalse(truncated["impactEvidence"]["coverageIncomplete"] is False)
        self.assertIn("SEMANTIC_DIFF_FINDINGS_TRUNCATED", truncated["staticValidation"]["reasonCodes"])
        for entry in truncated["staticValidation"]["selected"]:
            self.assertFalse(entry["findingIdsComplete"])

    def test_unknown_finding_kind_selects_conservative_validation(self) -> None:
        report = build_regression_plan(
            semantic_diff=semantic_diff(findings=[finding(kind="future-kind")]),
            input_pins=input_pins(),
        )

        self.assertTrue(report["staticValidation"]["failClosed"])
        self.assertEqual(report["impactEvidence"]["unknownFindingKindIds"], [FINDING_ID])
        self.assertIn("SEMANTIC_DIFF_FINDING_KIND_UNKNOWN", report["staticValidation"]["reasonCodes"])

    def test_existing_impacted_selection_is_reused_without_recomputing_decisions(self) -> None:
        report = build_regression_plan(
            semantic_diff=semantic_diff(findings=[finding()]),
            impacted_selection=impacted_selection(selected=True, impacted_ids=[FINDING_ID]),
            input_pins=input_pins(include_selection=True),
        )

        self.assertEqual(report["physicalValidation"]["mode"], "otbm-e2e-008")
        self.assertFalse(report["physicalValidation"]["manualSelectionRequired"])
        scenario = report["physicalValidation"]["scenarios"][0]
        self.assertTrue(scenario["selected"])
        self.assertEqual(scenario["impactedFindingIds"], [FINDING_ID])
        self.assertEqual(report["provenance"]["impactedSelection"]["semanticDiffSha256"], SEMANTIC_PIN_SHA)

    def test_skipped_physical_scenario_requires_exact_non_impact_and_pinned_route(self) -> None:
        report = build_regression_plan(
            semantic_diff=semantic_diff(findings=[finding()]),
            impacted_selection=impacted_selection(selected=False),
            input_pins=input_pins(include_selection=True),
        )

        scenario = report["physicalValidation"]["scenarios"][0]
        self.assertFalse(scenario["selected"])
        self.assertEqual(scenario["reasons"], [{"code": "EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT"}])
        self.assertTrue(report["physicalValidation"]["canSkipAny"])

        invalid = impacted_selection(selected=False)
        invalid["scenarios"][0]["routePlans"][0]["sha256"] = None
        with self.assertRaisesRegex(RegressionGuardError, "compatible SHA-pinned baseline route evidence"):
            build_regression_plan(
                semantic_diff=semantic_diff(findings=[finding()]),
                impacted_selection=invalid,
                input_pins=input_pins(include_selection=True),
            )

    def test_mismatched_impacted_selection_provenance_is_rejected(self) -> None:
        selection = impacted_selection(selected=True, impacted_ids=[FINDING_ID])
        selection["semanticDiff"]["afterMapSha256"] = "f" * 64

        with self.assertRaisesRegex(RegressionGuardError, "afterMapSha256 does not match"):
            build_regression_plan(
                semantic_diff=semantic_diff(findings=[finding()]),
                impacted_selection=selection,
                input_pins=input_pins(include_selection=True),
            )

    def test_semantic_output_is_deterministic(self) -> None:
        first = build_regression_plan(
            semantic_diff=semantic_diff(findings=[finding()]),
            impacted_selection=impacted_selection(selected=True, impacted_ids=[FINDING_ID]),
            input_pins=input_pins(include_selection=True),
        )
        second_input = copy.deepcopy(semantic_diff(findings=[finding()]))
        second = build_regression_plan(
            semantic_diff=second_input,
            impacted_selection=copy.deepcopy(impacted_selection(selected=True, impacted_ids=[FINDING_ID])),
            input_pins=copy.deepcopy(input_pins(include_selection=True)),
        )

        self.assertEqual(first, second)
        self.assertEqual(canonical_report_sha256(first), canonical_report_sha256(second))


if __name__ == "__main__":
    unittest.main()
