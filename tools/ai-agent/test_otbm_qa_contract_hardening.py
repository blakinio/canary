from __future__ import annotations

import copy
import itertools
import unittest

from otbm_asset_compatibility import AssetCompatibilityContext, build_asset_compatibility_report
from otbm_continuous_assurance import (
    CERTIFICATION_FORMAT,
    EXECUTION_FORMAT,
    REGRESSION_FORMAT as CONTINUOUS_REGRESSION_FORMAT,
    WORLD_HEALTH_FORMAT,
    ContinuousAssuranceError,
    build_continuous_assurance_report,
)
from otbm_map_change_regression import (
    IMPACTED_SELECTION_FORMAT,
    SEMANTIC_DIFF_FORMAT,
    RegressionGuardError,
    build_regression_plan,
    canonical_report_sha256 as regression_report_sha256,
)
from otbm_region_quest_certification import (
    COVERAGE_FORMAT,
    MANIFEST_FORMAT,
    build_certification_report,
    canonical_report_sha256 as certification_report_sha256,
)
from otbm_release_provenance import (
    BOM_FORMAT,
    build_release_provenance_report,
)


BEFORE_MAP = "1" * 64
AFTER_MAP = "2" * 64
BEFORE_INDEX = "3" * 64
AFTER_INDEX = "4" * 64
SEMANTIC_PIN = "5" * 64
SELECTION_PIN = "6" * 64


def pin(report_format: str, digest: str, name: str) -> dict:
    return {"fileName": name, "size": 123, "sha256": digest, "format": report_format}


def semantic_finding(identifier: str, kind: str, position: list[int]) -> dict:
    return {
        "id": identifier,
        "kind": kind,
        "classifications": ["changed", "handler-affected"],
        "evidenceLevel": "semantic",
        "position": position,
        "before": 1000,
        "after": 1001,
        "details": {"itemId": 1949, "mechanicType": kind},
        "message": f"{kind} changed",
        "correlations": [],
    }


def semantic_diff(
    findings: list[dict] | None = None,
    *,
    scope_type: str = "full-index",
    truncated: bool = False,
    total: int | None = None,
) -> dict:
    samples = list(findings or [])
    exact_total = len(samples) if total is None else total
    by_kind: dict[str, int] = {}
    by_classification: dict[str, int] = {}
    by_evidence: dict[str, int] = {}
    for sample in samples:
        by_kind[sample["kind"]] = by_kind.get(sample["kind"], 0) + 1
        for classification in sample["classifications"]:
            by_classification[classification] = by_classification.get(classification, 0) + 1
        level = sample["evidenceLevel"]
        by_evidence[level] = by_evidence.get(level, 0) + 1
    if exact_total > len(samples) and samples:
        by_kind = {samples[0]["kind"]: exact_total}
        by_classification = {value: exact_total for value in samples[0]["classifications"]}
        by_evidence = {samples[0]["evidenceLevel"]: exact_total}
    return {
        "format": SEMANTIC_DIFF_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "provenance": {
            "before": {"sourceMap": {"sha256": BEFORE_MAP}, "worldIndex": {"sha256": BEFORE_INDEX}},
            "after": {"sourceMap": {"sha256": AFTER_MAP}, "worldIndex": {"sha256": AFTER_INDEX}},
        },
        "compatibility": {"compatible": True},
        "scope": {
            "type": scope_type,
            "from": None if scope_type == "full-index" else [90, 90, 7],
            "to": None if scope_type == "full-index" else [110, 110, 7],
        },
        "summary": {
            "changedPositions": 0 if exact_total == 0 else len({tuple(item["position"]) for item in samples}),
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


def skipped_selection(*, scope_type: str, findings_total: int = 0, truncated: bool = False) -> dict:
    return {
        "format": IMPACTED_SELECTION_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "semanticDiff": {
            "sha256": SEMANTIC_PIN,
            "beforeMapSha256": BEFORE_MAP,
            "afterMapSha256": AFTER_MAP,
            "beforeWorldIndexSha256": BEFORE_INDEX,
            "afterWorldIndexSha256": AFTER_INDEX,
            "scopeType": scope_type,
            "findingsTotal": findings_total,
            "findingsTruncated": truncated,
        },
        "summary": {"scenarioCount": 1, "selectedCount": 0, "skippedCount": 1, "failClosedCount": 0},
        "scenarios": [
            {
                "suite": "universal-e2e",
                "id": "route-a",
                "manifest": {"path": "route-a.json", "sha256": "7" * 64},
                "selected": False,
                "decision": "skipped",
                "failClosed": False,
                "reasons": [{"code": "EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT"}],
                "impactedFindingIds": [],
                "routePlans": [
                    {
                        "routeId": "route-a",
                        "path": "route-a-plan.json",
                        "sha256": "8" * 64,
                        "baselineCompatible": True,
                        "positionCount": 10,
                    }
                ],
            }
        ],
    }


def regression_pins(*, include_selection: bool = False) -> dict:
    result = {"semanticDiff": pin(SEMANTIC_DIFF_FORMAT, SEMANTIC_PIN, "semantic-diff.json")}
    if include_selection:
        result["impactedSelection"] = pin(IMPACTED_SELECTION_FORMAT, SELECTION_PIN, "selection.json")
    return result


def release_bom(release_id: str, *, appearance_sha: str = "a") -> dict:
    return {
        "format": BOM_FORMAT,
        "releaseId": release_id,
        "components": [
            {"id": "map", "kind": "source-map", "sha256": "b" * 64},
            {"id": "appearances", "kind": "appearances", "sha256": appearance_sha * 64},
            {"id": "assets", "kind": "asset-index", "sha256": "c" * 64},
        ],
        "dimensions": [
            {"id": "source-correlation", "dependsOn": ["map"]},
            {"id": "reachability", "dependsOn": ["map", "appearances"]},
            {"id": "render", "dependsOn": ["appearances", "assets"]},
        ],
    }


def certification_dimension(state: str) -> dict:
    return {"state": state, "evidence": [], "memberIds": [], "blockers": []}


def coverage_target(target_id: str, *, provenance_state: str = "current") -> dict:
    dimensions = {
        key: certification_dimension("proven")
        for key in (
            "indexedOnExactMap",
            "sourceCorrelated",
            "scriptResolved",
            "staticallyReachable",
            "interactionResolved",
            "staticQualityCompatible",
            "executableRouteCovered",
            "physicallyRuntimeProven",
            "candidateMapValidated",
        )
    }
    dimensions["interactionResolved"] = certification_dimension("not-applicable")
    return {
        "id": target_id,
        "kind": "quest",
        "formalCertificationLevel": None,
        "requirementsSatisfied": True,
        "dimensions": dimensions,
        "staleAgainstCurrentMap": {"state": provenance_state, "evidence": [], "blockers": []},
    }


def certification_manifest(target_ids: list[str]) -> dict:
    return {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "targets": [
            {
                "targetId": target_id,
                "maximumLevel": "C7_CANDIDATE_CHANGE_REVALIDATED",
                "reason": "adversarial fixture",
            }
            for target_id in target_ids
        ],
    }


def coverage_dashboard(targets: list[dict]) -> dict:
    return {
        "format": COVERAGE_FORMAT,
        "schemaVersion": 1,
        "policy": {"formalCertificationAssigned": False},
        "currentMap": {"mapSha256": AFTER_MAP, "worldIndexSha256": AFTER_INDEX},
        "targets": targets,
    }


def certification_pins() -> dict:
    return {
        "manifest": pin(MANIFEST_FORMAT, "9" * 64, "certification-targets.json"),
        "coverageDashboard": pin(COVERAGE_FORMAT, "a" * 64, "coverage.json"),
    }


def continuous_pins() -> dict:
    return {
        "executionLedger": pin(EXECUTION_FORMAT, "a" * 64, "execution.json"),
        "regressionPlan": pin(CONTINUOUS_REGRESSION_FORMAT, "b" * 64, "regression.json"),
        "beforeWorldHealth": pin(WORLD_HEALTH_FORMAT, "c" * 64, "before-health.json"),
        "afterWorldHealth": pin(WORLD_HEALTH_FORMAT, "d" * 64, "after-health.json"),
        "beforeCertification": pin(CERTIFICATION_FORMAT, "e" * 64, "before-certification.json"),
        "afterCertification": pin(CERTIFICATION_FORMAT, "f" * 64, "after-certification.json"),
    }


def continuous_regression(*, reverse: bool = False) -> dict:
    validators = [{"validator": "otbm-map-quality"}, {"validator": "otbm-script-resolution"}]
    scenarios = [
        {"suite": "quest", "id": "alpha", "selected": True},
        {"suite": "route", "id": "beta", "selected": True},
    ]
    if reverse:
        validators.reverse()
        scenarios.reverse()
    return {
        "format": CONTINUOUS_REGRESSION_FORMAT,
        "schemaVersion": 1,
        "source": {
            "beforeMapSha256": BEFORE_MAP,
            "afterMapSha256": AFTER_MAP,
            "beforeWorldIndexSha256": BEFORE_INDEX,
            "afterWorldIndexSha256": AFTER_INDEX,
        },
        "staticValidation": {"failClosed": False, "selected": validators, "skipped": []},
        "physicalValidation": {"manualSelectionRequired": False, "scenarios": scenarios},
    }


def world_health(*, before: bool) -> dict:
    summary = {
        "structuralFindings": 0,
        "runtimeHandlerPlacementFindings": 0,
        "attentionMechanics": 0,
        "staleEvidenceTargets": 0,
        "missingPhysicalScenarioTargets": 0,
        "runtimeNotProvenOnCurrentMapTargets": 0,
    }
    return {
        "format": WORLD_HEALTH_FORMAT,
        "schemaVersion": 1,
        "source": {
            "mapSha256": BEFORE_MAP if before else AFTER_MAP,
            "worldIndexSha256": BEFORE_INDEX if before else AFTER_INDEX,
        },
        "summary": summary,
    }


def continuous_certification(*, before: bool, state: str = "certified") -> dict:
    return {
        "format": CERTIFICATION_FORMAT,
        "schemaVersion": 1,
        "currentMap": {
            "mapSha256": BEFORE_MAP if before else AFTER_MAP,
            "worldIndexSha256": BEFORE_INDEX if before else AFTER_INDEX,
        },
        "certifications": [
            {
                "targetId": "quest.alpha",
                "certificationLevel": "C4_STATIC_QUALITY_GREEN",
                "certificationState": state,
            }
        ],
    }


def continuous_execution(pins: dict, *, reverse: bool = False) -> dict:
    static_results = [
        {
            "validator": "otbm-map-quality",
            "status": "passed",
            "evidence": {"format": "canary-otbm-map-quality-v1", "sha256": "1" * 64},
        },
        {
            "validator": "otbm-script-resolution",
            "status": "passed",
            "evidence": {"format": "canary-otbm-script-resolution-v1", "sha256": "2" * 64},
        },
    ]
    physical_results = [
        {
            "suite": "quest",
            "id": "alpha",
            "status": "passed",
            "evidence": {"format": "universal-agent-e2e-result-v1", "sha256": "3" * 64},
        },
        {
            "suite": "route",
            "id": "beta",
            "status": "passed",
            "evidence": {"format": "universal-agent-e2e-result-v1", "sha256": "4" * 64},
        },
    ]
    if reverse:
        static_results.reverse()
        physical_results.reverse()
    return {
        "format": EXECUTION_FORMAT,
        "schemaVersion": 1,
        "inputs": {
            "regressionPlanSha256": pins["regressionPlan"]["sha256"],
            "beforeWorldHealthSha256": pins["beforeWorldHealth"]["sha256"],
            "afterWorldHealthSha256": pins["afterWorldHealth"]["sha256"],
            "beforeCertificationSha256": pins["beforeCertification"]["sha256"],
            "afterCertificationSha256": pins["afterCertification"]["sha256"],
        },
        "staticValidation": static_results,
        "physicalValidation": physical_results,
    }


def build_continuous(*, reverse: bool = False, after_state: str = "certified", after_map_sha: str | None = None) -> dict:
    pins = continuous_pins()
    after_certification = continuous_certification(before=False, state=after_state)
    if after_map_sha is not None:
        after_certification["currentMap"]["mapSha256"] = after_map_sha
    return build_continuous_assurance_report(
        execution_ledger=continuous_execution(pins, reverse=reverse),
        regression_plan=continuous_regression(reverse=reverse),
        before_world_health=world_health(before=True),
        after_world_health=world_health(before=False),
        before_certification=continuous_certification(before=True),
        after_certification=after_certification,
        input_pins=pins,
    )


class RegressionDeterminismHardeningTests(unittest.TestCase):
    def test_semantically_unordered_findings_have_canonical_output(self) -> None:
        findings = [
            semantic_finding("otbm-diff:" + "a" * 24, "action-id-changed", [100, 101, 7]),
            semantic_finding("otbm-diff:" + "b" * 24, "unique-id-changed", [102, 101, 7]),
        ]
        reports = [
            build_regression_plan(
                semantic_diff=semantic_diff(list(order)),
                input_pins=regression_pins(),
            )
            for order in itertools.permutations(findings)
        ]
        self.assertTrue(all(report == reports[0] for report in reports[1:]))
        self.assertEqual(
            {regression_report_sha256(report) for report in reports},
            {regression_report_sha256(reports[0])},
        )

    def test_bounded_evidence_cannot_authorize_physical_skip(self) -> None:
        with self.assertRaisesRegex(RegressionGuardError, "bounded or truncated"):
            build_regression_plan(
                semantic_diff=semantic_diff(scope_type="bounded-region"),
                impacted_selection=skipped_selection(scope_type="bounded-region"),
                input_pins=regression_pins(include_selection=True),
            )

    def test_regression_inputs_are_not_mutated(self) -> None:
        diff = semantic_diff([semantic_finding("otbm-diff:" + "c" * 24, "action-id-changed", [10, 11, 7])])
        pins = regression_pins()
        original_diff = copy.deepcopy(diff)
        original_pins = copy.deepcopy(pins)
        build_regression_plan(semantic_diff=diff, input_pins=pins)
        self.assertEqual(diff, original_diff)
        self.assertEqual(pins, original_pins)


class ReleaseProvenanceHardeningTests(unittest.TestCase):
    def test_permutations_are_canonical_and_invalidation_is_dependency_scoped(self) -> None:
        previous = release_bom("r1", appearance_sha="a")
        current = release_bom("r2", appearance_sha="d")
        baseline = build_release_provenance_report(current, previous)
        statuses = {entry["dimensionId"]: entry for entry in baseline["dimensionFreshness"]}
        self.assertEqual(statuses["source-correlation"]["status"], "current")
        self.assertEqual(statuses["reachability"]["status"], "stale")
        self.assertEqual(statuses["render"]["status"], "stale")
        self.assertEqual(statuses["reachability"]["changedDependencies"], ["appearances"])
        self.assertEqual(statuses["render"]["changedDependencies"], ["appearances"])

        for component_order in itertools.permutations(current["components"]):
            for dimension_order in itertools.permutations(current["dimensions"]):
                candidate = copy.deepcopy(current)
                candidate["components"] = list(component_order)
                candidate["dimensions"] = list(dimension_order)
                for dimension in candidate["dimensions"]:
                    dimension["dependsOn"] = list(reversed(dimension["dependsOn"]))
                self.assertEqual(build_release_provenance_report(candidate, previous), baseline)

    def test_release_provenance_inputs_are_not_mutated(self) -> None:
        previous = release_bom("r1")
        current = release_bom("r2", appearance_sha="d")
        originals = (copy.deepcopy(current), copy.deepcopy(previous))
        build_release_provenance_report(current, previous)
        self.assertEqual(current, originals[0])
        self.assertEqual(previous, originals[1])


class CertificationHardeningTests(unittest.TestCase):
    def test_manifest_and_coverage_target_order_are_canonical(self) -> None:
        target_ids = ["quest.alpha", "quest.beta"]
        baseline = build_certification_report(
            manifest=certification_manifest(target_ids),
            coverage_dashboard=coverage_dashboard([coverage_target(value) for value in target_ids]),
            input_pins=certification_pins(),
        )
        for manifest_order in itertools.permutations(target_ids):
            for coverage_order in itertools.permutations(target_ids):
                report = build_certification_report(
                    manifest=certification_manifest(list(manifest_order)),
                    coverage_dashboard=coverage_dashboard([coverage_target(value) for value in coverage_order]),
                    input_pins=certification_pins(),
                )
                self.assertEqual(report, baseline)
                self.assertEqual(certification_report_sha256(report), certification_report_sha256(baseline))

    def test_non_current_provenance_always_collapses_to_c0(self) -> None:
        expected_states = {"stale": "stale", "mixed": "stale", "not-evaluated": "not-evaluated"}
        for provenance_state, certification_state in expected_states.items():
            with self.subTest(provenance_state=provenance_state):
                report = build_certification_report(
                    manifest=certification_manifest(["quest.alpha"]),
                    coverage_dashboard=coverage_dashboard([coverage_target("quest.alpha", provenance_state=provenance_state)]),
                    input_pins=certification_pins(),
                )
                certification = report["certifications"][0]
                self.assertEqual(certification["certificationLevel"], "C0_NOT_EVALUATED")
                self.assertEqual(certification["certificationState"], certification_state)
                self.assertIn("CURRENT_MAP_PROVENANCE_NOT_CURRENT", certification["blockers"])


class ContinuousAssuranceHardeningTests(unittest.TestCase):
    def test_unordered_selected_and_execution_results_are_canonical(self) -> None:
        first = build_continuous(reverse=False)
        second = build_continuous(reverse=True)
        self.assertEqual(first, second)

    def test_cross_contract_map_provenance_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(ContinuousAssuranceError, "after Certification provenance"):
            build_continuous(after_map_sha="9" * 64)

    def test_stale_after_certification_blocks_even_without_level_drop(self) -> None:
        report = build_continuous(after_state="stale")
        self.assertFalse(report["gate"]["passed"])
        self.assertIn("CERTIFICATION_STALE_AFTER:quest.alpha", report["gate"]["blockers"])


class AssetCompatibilityHardeningTests(unittest.TestCase):
    def test_missing_appearance_is_incompatible_and_input_order_does_not_change_output(self) -> None:
        appearances = {
            "appearances": [
                {"category": "object", "id": 100, "flags": {}, "frameGroups": []},
            ]
        }
        assets = {"sprites": []}
        provenance = {
            "sourceMapSha256": "a" * 64,
            "worldIndexSha256": "b" * 64,
            "appearancesSha256": "c" * 64,
            "assetIndexSha256": "d" * 64,
            "baselineAppearancesSha256": None,
        }
        first_context = AssetCompatibilityContext({}, {}, (999, 100), appearances, assets, None, provenance)
        second_context = AssetCompatibilityContext({}, {}, (100, 999), copy.deepcopy(appearances), copy.deepcopy(assets), None, copy.deepcopy(provenance))
        original_appearances = copy.deepcopy(appearances)
        original_assets = copy.deepcopy(assets)

        first = build_asset_compatibility_report(first_context)
        second = build_asset_compatibility_report(second_context)

        self.assertEqual(first, second)
        self.assertFalse(first["ok"])
        self.assertEqual(first["summary"]["missingObjectAppearances"], 1)
        self.assertTrue(any(item["code"] == "missing-object-appearance" and item["severity"] == "error" for item in first["findings"]))
        self.assertEqual(appearances, original_appearances)
        self.assertEqual(assets, original_assets)


if __name__ == "__main__":
    unittest.main()
