from __future__ import annotations

import copy
import unittest

from otbm_coverage_dashboard import (
    CANDIDATE_REPAIR_FORMAT,
    COVERAGE_FORMAT,
    MAP_QUALITY_FORMAT,
    QUEST_VALIDATION_FORMAT,
    REPORT_FORMAT,
    ROUTE_PLAN_FORMAT,
    TARGETS_FORMAT,
    WORLD_HEALTH_FORMAT,
    CoverageDashboardError,
    build_coverage_dashboard_report,
)

MAP_SHA = "1" * 64
INDEX_SHA = "2" * 64
TARGETS_SHA = "3" * 64
COVERAGE_SHA = "4" * 64
QUALITY_SHA = "5" * 64
HEALTH_SHA = "6" * 64
QUEST_SHA = "7" * 64
ROUTE_SHA = "8" * 64
CANDIDATE_SHA = "9" * 64
CANDIDATE_MAP_SHA = "a" * 64

REGION = {"from": [100, 100, 7], "to": [110, 110, 7]}
SELECTOR_1 = {"position": [101, 101, 7], "actionId": 5001}
SELECTOR_2 = {"position": [200, 200, 7], "uniqueId": 6001}


def pin(name: str, sha: str, report_format: str) -> dict:
    return {"fileName": name, "size": 10, "sha256": sha, "format": report_format}


def mechanic(
    mechanic_id: str,
    selector: dict,
    *,
    indexed: bool = True,
    script_resolved: bool = True,
    reachable: bool = True,
    physical_current: bool = True,
    physical_any: bool = True,
    stale: bool | None = False,
) -> dict:
    return {
        "id": mechanic_id,
        "reason": "fixture",
        "selector": selector,
        "static": {"indexed": indexed, "uniqueMatch": indexed, "matchCount": 1 if indexed else 0},
        "script": {
            "covered": True,
            "uniqueMatch": script_resolved,
            "matchCount": 1 if script_resolved else 0,
            "status": "handled-directly" if script_resolved else "unresolved",
            "resolved": script_resolved,
        },
        "reachability": {
            "covered": reachable,
            "status": "strictly-reachable" if reachable else "not-covered",
            "currentEvidence": [],
            "staleEvidence": [],
            "staleStatus": [],
        },
        "physical": {
            "scenarioPresent": physical_any,
            "scenarios": [],
            "runtimeProven": physical_any,
            "runtimeProvenScenarios": [],
            "runtimeProvenOnCurrentMap": physical_current,
            "currentMapScenarios": [],
            "staleMapScenarios": ["stale-scenario"] if physical_any and not physical_current else [],
        },
        "staleAgainstCurrentMapProvenance": stale,
        "missingPhysicalScenario": not physical_any,
    }


def coverage_matrix() -> dict:
    return {
        "format": COVERAGE_FORMAT,
        "schemaVersion": 1,
        "currentMap": {"mapSha256": MAP_SHA, "worldIndexSha256": INDEX_SHA},
        "summary": {"targets": 2},
        "mechanics": [mechanic("m2", SELECTOR_2), mechanic("m1", SELECTOR_1)],
        "findings": [],
    }


def map_quality(*, ok: bool = True) -> dict:
    component = {"format": "fixture", "reportSha256": "b" * 64, "inputOk": True, "inputComplete": True}
    return {
        "format": MAP_QUALITY_FORMAT,
        "schemaVersion": 1,
        "ok": ok,
        "source": {"path": "map.otbm", "sha256": MAP_SHA},
        "policy": {"failOn": "error"},
        "coverage": {
            "geometry": REGION,
            "reachability": REGION,
            "sameRegion": True,
            "scriptResolutionScope": "selected-corpus",
            "globalCoverageProven": False,
        },
        "components": {
            "geometry": copy.deepcopy(component),
            "reachability": copy.deepcopy(component),
            "scriptResolution": copy.deepcopy(component),
        },
        "summary": {"total": 0, "bySeverity": {"error": 0, "warning": 0, "unresolved": 0, "info": 0}, "componentTotals": {"geometry": 0, "reachability": 0, "scriptResolution": 0}, "sampleCount": 0, "truncated": False, "complete": True},
        "findings": [],
        "notes": ["fixture"],
    }


def world_health() -> dict:
    return {
        "format": WORLD_HEALTH_FORMAT,
        "schemaVersion": 1,
        "source": {"mapSha256": MAP_SHA, "worldIndexSha256": INDEX_SHA},
        "coverage": {
            "scopes": [],
            "sameBoundedRegion": False,
            "globalCoverageProven": False,
            "routePopulation": {"currentMap": 0, "staleMap": 0, "unknownMap": 0},
        },
        "policy": {},
        "provenance": {},
        "summary": {"dimensions": {}, "totalAttention": 0, "sampleCount": 0, "truncated": False},
        "dimensions": {},
        "notes": ["fixture"],
    }


def quest_report(*, classification: str = "confirmed", world_index_sha: str = INDEX_SHA) -> dict:
    return {
        "format": QUEST_VALIDATION_FORMAT,
        "schemaVersion": 1,
        "ok": classification != "conflicting",
        "complete": classification == "confirmed",
        "sources": {
            "evidenceDigest": "c" * 64,
            "worldIndex": {"path": "world.widx", "sha256": world_index_sha},
            "scriptResolution": None,
        },
        "region": REGION,
        "summary": {},
        "findings": [{"evidenceId": "evidence-1", "classification": classification}],
        "mapOnlyRegionMechanics": [],
        "sourceUnresolved": [],
        "notes": ["fixture"],
    }


def route_plan(*, current: bool = True, executable: bool = True, interaction_status: str = "executable") -> dict:
    return {
        "format": ROUTE_PLAN_FORMAT,
        "schemaVersion": 1,
        "provenance": {
            "map": {"sha256": MAP_SHA if current else "d" * 64},
            "worldIndex": {"sha256": INDEX_SHA},
            "appearances": {"sha256": "e" * 64},
            "transitionManifest": None,
            "scriptResolution": None,
            "interactionRegistry": {"sha256": "f" * 64},
        },
        "inputHashSha256": "0" * 64,
        "planHashSha256": "1" * 64,
        "origin": [100, 100, 7],
        "destination": [101, 101, 7],
        "routingBounds": REGION,
        "routingOptions": {"allowDiagonal": True, "diagonalCornerCutting": False, "maxExecutablePositions": 100, "interactionAware": True},
        "routeStatus": "confirmed" if executable else "unreachable",
        "executionStatus": "executable" if executable else "blocked",
        "routingMode": "executable" if executable else None,
        "distance": 1 if executable else None,
        "strictDistance": 1 if executable else None,
        "optimisticDistance": 1 if executable else None,
        "executableDistance": 1 if executable else None,
        "pathComplete": executable,
        "path": [[100, 100, 7], [101, 101, 7]] if executable else [],
        "edges": [
            {
                "from": [100, 100, 7],
                "to": [101, 101, 7],
                "kind": "movement",
                "isTransition": False,
                "transitionId": None,
                "evidence": {"source": "reachability-bfs-predecessor", "edgeSource": "_movement_neighbors", "routingMode": "executable"},
                "interactions": [
                    {
                        "format": "canary-otbm-route-interaction-resolution-v1",
                        "schemaVersion": 1,
                        "executionStatus": interaction_status,
                        "selectorQuery": {},
                        "matchedEntryIds": ["entry-1"],
                        "blockers": [] if interaction_status == "executable" else [{"code": "blocked"}],
                    }
                ],
                "executionBlockers": [],
            }
        ],
        "blockers": [] if executable else [{"code": "blocked"}],
    }


def candidate_report(*, selector: dict = SELECTOR_1, ok: bool = True, source_sha: str = MAP_SHA) -> dict:
    return {
        "format": CANDIDATE_REPAIR_FORMAT,
        "schemaVersion": 1,
        "ok": ok,
        "status": "physically-validated" if ok else "physical-e2e-required",
        "source": {"mapSha256": source_sha, "unchanged": True},
        "candidate": {"mapSha256": CANDIDATE_MAP_SHA, "createNew": True, "qualitySourceSha256": CANDIDATE_MAP_SHA},
        "recommendation": {
            "state": "supported-by-existing-attribute-path",
            "capability": {"family": "phase8-attribute", "mode": "set-action-id", "technicalPathSupported": True, "capabilityOnly": True},
            "selector": selector,
            "mutation": {},
        },
    }


def required_pins() -> dict:
    return {
        "targets": pin("targets.json", TARGETS_SHA, TARGETS_FORMAT),
        "coverageMatrix": pin("coverage.json", COVERAGE_SHA, COVERAGE_FORMAT),
        "mapQuality": pin("quality.json", QUALITY_SHA, MAP_QUALITY_FORMAT),
        "worldHealth": pin("health.json", HEALTH_SHA, WORLD_HEALTH_FORMAT),
    }


def optional_entry(report: dict, sha: str, report_format: str) -> dict:
    return {"report": report, "pin": pin(f"{sha[:4]}.json", sha, report_format)}


def build(targets: list[dict], *, coverage: dict | None = None, quality: dict | None = None, health: dict | None = None, quests: list[dict] | None = None, routes: list[dict] | None = None, candidates: list[dict] | None = None) -> dict:
    return build_coverage_dashboard_report(
        targets_manifest={"format": TARGETS_FORMAT, "schemaVersion": 1, "targets": targets},
        coverage_matrix=coverage or coverage_matrix(),
        map_quality=quality or map_quality(),
        world_health=health or world_health(),
        quest_validations=quests or [],
        route_plans=routes or [],
        candidate_repairs=candidates or [],
        input_pins=required_pins(),
    )


class CoverageDashboardTests(unittest.TestCase):
    def test_region_target_uses_exact_position_membership_and_exact_quality_scope(self) -> None:
        report = build([
            {
                "id": "region-a",
                "kind": "region",
                "reason": "fixture region",
                "region": REGION,
                "requiredDimensions": ["indexed-on-exact-map", "static-quality-compatible", "current-map-provenance"],
            }
        ])
        target = report["targets"][0]
        self.assertEqual(target["population"]["mechanicIds"], ["m1"])
        self.assertEqual(target["dimensions"]["indexedOnExactMap"]["state"], "proven")
        self.assertEqual(target["dimensions"]["staticQualityCompatible"]["state"], "proven")
        self.assertEqual(target["staleAgainstCurrentMap"]["state"], "current")
        self.assertTrue(target["requirementsSatisfied"])

    def test_world_population_is_all_reviewed_mechanics_not_global_map_claim(self) -> None:
        report = build([
            {
                "id": "world",
                "kind": "world",
                "reason": "reviewed world population",
                "requiredDimensions": ["indexed-on-exact-map"],
            }
        ])
        target = report["targets"][0]
        self.assertEqual(target["population"]["mechanicIds"], ["m1", "m2"])
        self.assertFalse(target["population"]["globalMapMechanicCoverageProven"])
        self.assertEqual(target["dimensions"]["staticQualityCompatible"]["state"], "not-evaluated")
        self.assertFalse(report["worldContext"]["globalCoverageProven"])
        self.assertIsNone(target["formalCertificationLevel"])

    def test_quest_source_correlation_requires_exact_confirmed_evidence(self) -> None:
        report = build(
            [
                {
                    "id": "quest-a",
                    "kind": "quest",
                    "reason": "quest fixture",
                    "mechanicIds": ["m1"],
                    "requiredDimensions": ["source-correlated"],
                    "sourceCorrelation": [{"reportSha256": QUEST_SHA, "evidenceIds": ["evidence-1"]}],
                }
            ],
            quests=[optional_entry(quest_report(), QUEST_SHA, QUEST_VALIDATION_FORMAT)],
        )
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["sourceCorrelated"]["state"], "proven")
        self.assertTrue(target["requirementsSatisfied"])

    def test_unresolved_source_correlation_is_blocked(self) -> None:
        report = build(
            [
                {
                    "id": "quest-a",
                    "kind": "quest",
                    "reason": "quest fixture",
                    "mechanicIds": ["m1"],
                    "requiredDimensions": ["source-correlated"],
                    "sourceCorrelation": [{"reportSha256": QUEST_SHA, "evidenceIds": ["evidence-1"]}],
                }
            ],
            quests=[optional_entry(quest_report(classification="unresolved"), QUEST_SHA, QUEST_VALIDATION_FORMAT)],
        )
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["sourceCorrelated"]["state"], "blocked")
        self.assertFalse(target["requirementsSatisfied"])

    def test_stale_quest_world_index_is_never_promoted(self) -> None:
        report = build(
            [
                {
                    "id": "quest-a",
                    "kind": "quest",
                    "reason": "quest fixture",
                    "mechanicIds": ["m1"],
                    "requiredDimensions": ["source-correlated", "current-map-provenance"],
                    "sourceCorrelation": [{"reportSha256": QUEST_SHA, "evidenceIds": ["evidence-1"]}],
                }
            ],
            quests=[optional_entry(quest_report(world_index_sha="d" * 64), QUEST_SHA, QUEST_VALIDATION_FORMAT)],
        )
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["sourceCorrelated"]["state"], "stale")
        self.assertEqual(target["staleAgainstCurrentMap"]["state"], "mixed")
        self.assertFalse(target["requirementsSatisfied"])

    def test_executable_route_and_required_interaction_are_separate_proofs(self) -> None:
        report = build(
            [
                {
                    "id": "route-a",
                    "kind": "landmark-route",
                    "reason": "route fixture",
                    "mechanicIds": ["m1"],
                    "requiredDimensions": ["executable-route-covered", "interaction-resolved"],
                    "routePlans": [{"reportSha256": ROUTE_SHA, "interactionRequired": True}],
                }
            ],
            routes=[optional_entry(route_plan(), ROUTE_SHA, ROUTE_PLAN_FORMAT)],
        )
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["executableRouteCovered"]["state"], "proven")
        self.assertEqual(target["dimensions"]["interactionResolved"]["state"], "proven")
        self.assertTrue(target["requirementsSatisfied"])

    def test_route_presence_does_not_promote_blocked_interaction(self) -> None:
        report = build(
            [
                {
                    "id": "route-a",
                    "kind": "landmark-route",
                    "reason": "route fixture",
                    "mechanicIds": ["m1"],
                    "requiredDimensions": ["executable-route-covered", "interaction-resolved"],
                    "routePlans": [{"reportSha256": ROUTE_SHA, "interactionRequired": True}],
                }
            ],
            routes=[optional_entry(route_plan(interaction_status="blocked"), ROUTE_SHA, ROUTE_PLAN_FORMAT)],
        )
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["executableRouteCovered"]["state"], "proven")
        self.assertEqual(target["dimensions"]["interactionResolved"]["state"], "blocked")
        self.assertFalse(target["requirementsSatisfied"])

    def test_noninteractive_route_marks_interaction_not_applicable(self) -> None:
        report = build(
            [
                {
                    "id": "route-a",
                    "kind": "landmark-route",
                    "reason": "route fixture",
                    "mechanicIds": ["m1"],
                    "requiredDimensions": ["executable-route-covered"],
                    "routePlans": [{"reportSha256": ROUTE_SHA, "interactionRequired": False}],
                }
            ],
            routes=[optional_entry(route_plan(), ROUTE_SHA, ROUTE_PLAN_FORMAT)],
        )
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["interactionResolved"]["state"], "not-applicable")
        self.assertTrue(target["requirementsSatisfied"])

    def test_candidate_validation_requires_exact_target_member_selector(self) -> None:
        report = build(
            [
                {
                    "id": "mechanic-set",
                    "kind": "mechanic-set",
                    "reason": "candidate fixture",
                    "mechanicIds": ["m1"],
                    "requiredDimensions": ["candidate-map-validated"],
                    "candidateRepairs": [CANDIDATE_SHA],
                }
            ],
            candidates=[optional_entry(candidate_report(), CANDIDATE_SHA, CANDIDATE_REPAIR_FORMAT)],
        )
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["candidateMapValidated"]["state"], "proven")
        self.assertTrue(target["requirementsSatisfied"])

    def test_candidate_selector_outside_target_fails_closed(self) -> None:
        with self.assertRaises(CoverageDashboardError):
            build(
                [
                    {
                        "id": "mechanic-set",
                        "kind": "mechanic-set",
                        "reason": "candidate fixture",
                        "mechanicIds": ["m1"],
                        "requiredDimensions": ["candidate-map-validated"],
                        "candidateRepairs": [CANDIDATE_SHA],
                    }
                ],
                candidates=[optional_entry(candidate_report(selector=SELECTOR_2), CANDIDATE_SHA, CANDIDATE_REPAIR_FORMAT)],
            )

    def test_missing_optional_evidence_stays_not_evaluated(self) -> None:
        report = build([
            {
                "id": "mechanic-set",
                "kind": "mechanic-set",
                "reason": "missing evidence fixture",
                "mechanicIds": ["m1"],
                "requiredDimensions": ["source-correlated", "executable-route-covered", "candidate-map-validated"],
            }
        ])
        target = report["targets"][0]
        self.assertEqual(target["dimensions"]["sourceCorrelated"]["state"], "not-evaluated")
        self.assertEqual(target["dimensions"]["executableRouteCovered"]["state"], "not-evaluated")
        self.assertEqual(target["dimensions"]["candidateMapValidated"]["state"], "not-evaluated")
        self.assertFalse(target["requirementsSatisfied"])
        self.assertFalse(report["policy"]["missingEvidenceMeansGlobalAbsence"])

    def test_unknown_explicit_mechanic_id_fails_closed(self) -> None:
        with self.assertRaises(CoverageDashboardError):
            build([
                {
                    "id": "mechanic-set",
                    "kind": "mechanic-set",
                    "reason": "unknown fixture",
                    "mechanicIds": ["missing"],
                    "requiredDimensions": ["indexed-on-exact-map"],
                }
            ])

    def test_map_quality_source_mismatch_fails_closed(self) -> None:
        quality = map_quality()
        quality["source"]["sha256"] = "d" * 64
        with self.assertRaises(CoverageDashboardError):
            build([
                {
                    "id": "world",
                    "kind": "world",
                    "reason": "mismatch fixture",
                    "requiredDimensions": ["indexed-on-exact-map"],
                }
            ], quality=quality)

    def test_same_inputs_are_deterministic_and_no_formal_certification_is_assigned(self) -> None:
        targets = [
            {
                "id": "region-a",
                "kind": "region",
                "reason": "fixture region",
                "region": REGION,
                "requiredDimensions": ["indexed-on-exact-map", "current-map-provenance"],
            }
        ]
        first = build(targets)
        second = build(copy.deepcopy(targets))
        self.assertEqual(first, second)
        self.assertEqual(first["format"], REPORT_FORMAT)
        self.assertFalse(first["policy"]["formalCertificationAssigned"])
        self.assertFalse(first["policy"]["opaqueScoreEmitted"])
        self.assertFalse(first["policy"]["downstreamScenarioPrioritizationDirected"])


if __name__ == "__main__":
    unittest.main()
