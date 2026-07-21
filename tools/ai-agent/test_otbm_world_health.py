from __future__ import annotations

import copy
import unittest

from otbm_world_health import (
    COVERAGE_FORMAT,
    MAP_QUALITY_FORMAT,
    REACHABILITY_FORMAT,
    WorldHealthError,
    build_world_health_report,
)

MAP_SHA = "a" * 64
OTHER_MAP_SHA = "b" * 64
WORLD_SHA = "c" * 64
OTHER_WORLD_SHA = "d" * 64


def pin(report_format: str, digest: str, name: str) -> dict:
    return {
        "fileName": name,
        "size": 123,
        "sha256": digest,
        "format": report_format,
    }


def component(
    *,
    source_sha: str = MAP_SHA,
    counts: dict[str, int] | None = None,
    truncated: bool = False,
    **extra: int,
) -> dict:
    return {
        "format": "component-v1",
        "sourceSha256": source_sha,
        "input": pin("source-v1", "9" * 64, "source.json"),
        "inputOk": True,
        "inputComplete": True,
        "outcomeCounts": counts or {"error": 0, "warning": 0, "unresolved": 0, "info": 0},
        "findingsAvailableForSampling": 0,
        "findingsTruncatedByComponent": truncated,
        **extra,
    }


def map_quality_report(*, source_sha: str = MAP_SHA) -> dict:
    return {
        "format": MAP_QUALITY_FORMAT,
        "schemaVersion": 1,
        "ok": False,
        "source": {"sha256": source_sha},
        "policy": {},
        "coverage": {
            "geometry": {"from": [100, 100, 7], "to": [120, 120, 7]},
            "reachability": {"from": [100, 100, 7], "to": [120, 120, 7]},
            "sameRegion": True,
            "globalCoverageProven": False,
        },
        "components": {
            "geometry": component(
                source_sha=source_sha,
                counts={"error": 1, "warning": 1, "unresolved": 0, "info": 0},
                truncated=True,
            ),
            "reachability": component(
                source_sha=source_sha,
                counts={"error": 0, "warning": 1, "unresolved": 0, "info": 1},
            ),
            "scriptResolution": component(
                source_sha=source_sha,
                counts={"error": 1, "warning": 0, "unresolved": 2, "info": 0},
                unreviewedIdentifiers=3,
                unresolvedDynamicRegistrations=4,
            ),
        },
        "summary": {
            "total": 7,
            "outcomeCounts": {"error": 2, "warning": 2, "unresolved": 2, "info": 1},
            "sampled": 2,
            "truncated": True,
            "availableForSampling": 7,
        },
        "findings": [
            {
                "id": "1" * 24,
                "component": "geometry",
                "outcome": "error",
                "kind": "duplicate-ground",
                "message": "structural",
                "position": [101, 100, 7],
                "evidence": {},
            },
            {
                "id": "2" * 24,
                "component": "scriptResolution",
                "outcome": "unresolved",
                "kind": "runtime-handler",
                "message": "unresolved",
                "position": [102, 100, 7],
                "evidence": {},
            },
        ],
        "notes": [],
    }


def reachability_report(
    *,
    source_sha: str = MAP_SHA,
    world_sha: str = WORLD_SHA,
    offset: int = 0,
) -> dict:
    return {
        "format": REACHABILITY_FORMAT,
        "schemaVersion": 1,
        "ok": False,
        "provenance": {
            "worldIndex": {"sha256": world_sha},
            "worldIndexManifest": {
                "source": {"sha256": source_sha},
                "index": {"sha256": world_sha},
            },
        },
        "region": {
            "from": [100 + offset, 100, 7],
            "to": [110 + offset, 110, 7],
            "coordinateCount": 121,
            "indexedTileCount": 100,
        },
        "policy": {},
        "summary": {
            "routes": 2,
            "routeStatusCounts": {"confirmed": 1, "conditional": 1},
            "origins": 1,
            "transitions": 2,
            "transitionStatusCounts": {"confirmed": 1, "invalid": 1},
            "oneWayTransitions": 1,
            "deadEndTransitions": 1,
            "transitionLoops": 1,
            "mechanics": 3,
            "mechanicStatusCounts": {"confirmed": 1, "conditional": 1, "unreachable": 1},
            "strictReachableTiles": 10,
            "optimisticReachableTiles": 12,
            "tileStatusCounts": {"strict-walkable": 10, "conditional": 2},
            "findings": {"total": 0, "bySeverity": {}, "byCode": {}, "truncated": False},
        },
        "routes": [
            {
                "start": [100 + offset, 100, 7],
                "goal": [101 + offset, 100, 7],
                "status": "confirmed",
                "strictDistance": 1,
                "optimisticDistance": 1,
                "path": [],
                "pathTruncated": False,
                "transitionIdsUsed": [],
                "issues": [],
            },
            {
                "start": [100 + offset, 101, 7],
                "goal": [102 + offset, 101, 7],
                "status": "conditional",
                "strictDistance": None,
                "optimisticDistance": 2,
                "path": [],
                "pathTruncated": True,
                "transitionIdsUsed": ["transition-1"],
                "issues": ["conditional blocker"],
            },
        ],
        "transitions": [
            {
                "id": f"transition-{offset}-ok",
                "kind": "teleport",
                "origin": "world-index",
                "source": [103 + offset, 100, 7],
                "destination": [104 + offset, 100, 7],
                "itemId": 1387,
                "expectedItemIds": [],
                "bidirectional": False,
                "uncertainties": [],
                "scriptStatus": "confirmed",
                "status": "confirmed",
                "valid": True,
                "strictEligible": True,
                "optimisticEligible": True,
                "issues": [],
            },
            {
                "id": f"transition-{offset}-bad",
                "kind": "teleport",
                "origin": "world-index",
                "source": [105 + offset, 100, 7],
                "destination": [106 + offset, 100, 7],
                "itemId": 1387,
                "expectedItemIds": [],
                "bidirectional": False,
                "uncertainties": ["unresolved"],
                "scriptStatus": "unresolved",
                "status": "invalid",
                "valid": False,
                "strictEligible": False,
                "optimisticEligible": False,
                "issues": ["invalid transition"],
            },
        ],
        "transitionsTruncated": False,
        "transitionLoops": [{"positions": [[107 + offset, 100, 7]], "closed": True, "outgoing": []}],
        "transitionLoopsTruncated": False,
        "mechanics": [
            {
                "placementOrdinal": offset * 10,
                "itemId": 100,
                "position": [108 + offset, 100, 7],
                "actionId": None,
                "uniqueId": None,
                "houseDoorId": None,
                "teleportDestination": None,
                "status": "confirmed",
            },
            {
                "placementOrdinal": offset * 10 + 1,
                "itemId": 101,
                "position": [109 + offset, 100, 7],
                "actionId": 500,
                "uniqueId": None,
                "houseDoorId": None,
                "teleportDestination": None,
                "status": "conditional",
            },
            {
                "placementOrdinal": offset * 10 + 2,
                "itemId": 102,
                "position": [110 + offset, 100, 7],
                "actionId": 501,
                "uniqueId": None,
                "houseDoorId": None,
                "teleportDestination": None,
                "status": "unreachable",
            },
        ],
        "mechanicsTruncated": False,
        "tileDiagnostics": [],
        "tileDiagnosticsTruncated": False,
        "findings": [],
    }


def coverage_matrix(*, source_sha: str = MAP_SHA, world_sha: str = WORLD_SHA) -> dict:
    return {
        "format": COVERAGE_FORMAT,
        "schemaVersion": 1,
        "currentMap": {"mapSha256": source_sha, "worldIndexSha256": world_sha},
        "provenance": {},
        "summary": {
            "targets": 2,
            "staticallyIndexed": 2,
            "scriptResolved": 2,
            "reachabilityCovered": 2,
            "physicalScenarioPresent": 1,
            "physicallyRuntimeProven": 1,
            "physicallyRuntimeProvenOnCurrentMap": 1,
            "staleAgainstCurrentMapProvenance": 1,
            "missingPhysicalScenario": 1,
            "findings": 2,
        },
        "mechanics": [
            {
                "id": "quest.gate",
                "reason": "reviewed target",
                "selector": {"position": [200, 200, 7]},
                "static": {"indexed": True, "uniqueMatch": True, "matchCount": 1},
                "script": {"covered": True, "uniqueMatch": True, "matchCount": 1, "status": "confirmed", "resolved": True},
                "reachability": {"covered": True, "status": "confirmed", "currentEvidence": [], "staleEvidence": [], "staleStatus": None},
                "physical": {
                    "scenarioPresent": True,
                    "scenarios": ["scenario-a"],
                    "runtimeProven": True,
                    "runtimeProvenScenarios": ["scenario-a"],
                    "runtimeProvenOnCurrentMap": True,
                    "currentMapScenarios": ["scenario-a"],
                    "staleMapScenarios": [],
                },
                "staleAgainstCurrentMapProvenance": False,
                "missingPhysicalScenario": False,
            },
            {
                "id": "quest.teleport",
                "reason": "reviewed target",
                "selector": {"position": [201, 200, 7]},
                "static": {"indexed": True, "uniqueMatch": True, "matchCount": 1},
                "script": {"covered": True, "uniqueMatch": True, "matchCount": 1, "status": "confirmed", "resolved": True},
                "reachability": {"covered": True, "status": "conditional", "currentEvidence": [], "staleEvidence": [], "staleStatus": "conditional"},
                "physical": {
                    "scenarioPresent": False,
                    "scenarios": [],
                    "runtimeProven": False,
                    "runtimeProvenScenarios": [],
                    "runtimeProvenOnCurrentMap": False,
                    "currentMapScenarios": [],
                    "staleMapScenarios": ["scenario-old"],
                },
                "staleAgainstCurrentMapProvenance": True,
                "missingPhysicalScenario": True,
            },
        ],
        "findings": [],
        "notes": [],
    }


def input_pins(*, reachability_count: int = 1, coverage_count: int = 1) -> dict:
    return {
        "mapQuality": pin(MAP_QUALITY_FORMAT, "1" * 64, "quality.json"),
        "reachability": [
            pin(REACHABILITY_FORMAT, f"{index + 2:x}" * 64, f"reachability-{index}.json")
            for index in range(reachability_count)
        ],
        "coverageMatrices": [
            pin(COVERAGE_FORMAT, f"{index + 8:x}" * 64, f"coverage-{index}.json")
            for index in range(coverage_count)
        ],
    }


class AggregationTests(unittest.TestCase):
    def test_explicit_dimensions_preserve_exact_counts_and_provenance(self) -> None:
        report = build_world_health_report(
            map_quality=map_quality_report(),
            reachability_reports=[reachability_report()],
            coverage_matrices=[coverage_matrix()],
            input_pins=input_pins(),
            sample_limit=20,
        )

        self.assertEqual(report["format"], "canary-otbm-world-health-v1")
        self.assertEqual(report["source"], {"mapSha256": MAP_SHA, "worldIndexSha256": WORLD_SHA})
        self.assertEqual(
            report["dimensions"]["structural"]["outcomeCounts"],
            {"error": 1, "warning": 2, "unresolved": 0, "info": 1},
        )
        self.assertEqual(report["dimensions"]["structural"]["total"], 4)
        self.assertTrue(report["dimensions"]["structural"]["sourceEvidenceTruncated"])
        runtime = report["dimensions"]["runtimeHandlers"]
        self.assertEqual(runtime["placementFindingsTotal"], 3)
        self.assertEqual(runtime["conflictingPlacements"], 1)
        self.assertEqual(runtime["unresolvedPlacements"], 2)
        self.assertEqual(runtime["unreviewedIdentifiers"], 3)
        self.assertEqual(runtime["unresolvedDynamicRegistrations"], 4)
        reachability = report["dimensions"]["reachability"]
        self.assertEqual(reachability["mechanics"]["statusCounts"], {"conditional": 1, "confirmed": 1, "unreachable": 1})
        self.assertEqual(reachability["mechanics"]["attentionTotal"], 2)
        self.assertEqual(reachability["transitions"]["deadEnd"], 1)
        self.assertEqual(report["dimensions"]["staleEvidence"]["total"], 1)
        self.assertEqual(report["dimensions"]["missingPhysicalCoverage"]["missingScenarioTotal"], 1)
        self.assertEqual(report["dimensions"]["missingPhysicalCoverage"]["runtimeNotProvenOnCurrentMapTotal"], 1)
        self.assertFalse(report["coverage"]["globalCoverageProven"])
        self.assertFalse(report["policy"]["crossDimensionDeduplication"])
        self.assertFalse(report["policy"]["healthScoreEmitted"])

    def test_optional_evidence_absence_remains_explicit_not_global_absence(self) -> None:
        report = build_world_health_report(
            map_quality=map_quality_report(),
            input_pins=input_pins(reachability_count=0, coverage_count=0),
        )
        self.assertIsNone(report["source"]["worldIndexSha256"])
        self.assertFalse(report["dimensions"]["reachability"]["evidencePresent"])
        self.assertFalse(report["dimensions"]["staleEvidence"]["evidencePresent"])
        self.assertFalse(report["dimensions"]["missingPhysicalCoverage"]["evidencePresent"])
        self.assertFalse(report["policy"]["globalAbsenceInferred"])

    def test_exact_totals_do_not_depend_on_map_quality_samples(self) -> None:
        quality = map_quality_report()
        quality["findings"] = []
        quality["summary"]["sampled"] = 0
        report = build_world_health_report(
            map_quality=quality,
            input_pins=input_pins(reachability_count=0, coverage_count=0),
        )
        self.assertEqual(report["dimensions"]["structural"]["total"], 4)
        self.assertEqual(report["dimensions"]["runtimeHandlers"]["placementFindingsTotal"], 3)
        self.assertTrue(report["dimensions"]["runtimeHandlers"]["truncated"])

    def test_report_order_does_not_change_semantic_output(self) -> None:
        first = reachability_report(offset=0)
        second = reachability_report(offset=20)
        pins = input_pins(reachability_count=2, coverage_count=0)
        forward = build_world_health_report(
            map_quality=map_quality_report(),
            reachability_reports=[first, second],
            input_pins=pins,
            sample_limit=50,
        )
        reverse = build_world_health_report(
            map_quality=map_quality_report(),
            reachability_reports=[second, first],
            input_pins={
                "mapQuality": pins["mapQuality"],
                "reachability": list(reversed(pins["reachability"])),
                "coverageMatrices": [],
            },
            sample_limit=50,
        )
        self.assertEqual(forward, reverse)


class FailClosedTests(unittest.TestCase):
    def test_mismatched_map_sha_fails_closed(self) -> None:
        with self.assertRaisesRegex(WorldHealthError, "same source map"):
            build_world_health_report(
                map_quality=map_quality_report(),
                reachability_reports=[reachability_report(source_sha=OTHER_MAP_SHA)],
                input_pins=input_pins(reachability_count=1, coverage_count=0),
            )

    def test_mismatched_world_index_sha_fails_closed(self) -> None:
        with self.assertRaisesRegex(WorldHealthError, "same World Index"):
            build_world_health_report(
                map_quality=map_quality_report(),
                reachability_reports=[reachability_report()],
                coverage_matrices=[coverage_matrix(world_sha=OTHER_WORLD_SHA)],
                input_pins=input_pins(),
            )

    def test_duplicate_report_sha_fails_closed(self) -> None:
        pins = input_pins(reachability_count=1, coverage_count=1)
        pins["coverageMatrices"][0]["sha256"] = pins["reachability"][0]["sha256"]
        with self.assertRaisesRegex(WorldHealthError, "must be unique"):
            build_world_health_report(
                map_quality=map_quality_report(),
                reachability_reports=[reachability_report()],
                coverage_matrices=[coverage_matrix()],
                input_pins=pins,
            )

    def test_inconsistent_coverage_summary_fails_closed(self) -> None:
        coverage = coverage_matrix()
        coverage["summary"]["missingPhysicalScenario"] = 0
        with self.assertRaisesRegex(WorldHealthError, "missing-physical summary"):
            build_world_health_report(
                map_quality=map_quality_report(),
                coverage_matrices=[coverage],
                input_pins=input_pins(reachability_count=0, coverage_count=1),
            )

    def test_inconsistent_reachability_status_total_fails_closed(self) -> None:
        reachability = reachability_report()
        reachability["summary"]["mechanicStatusCounts"] = {"confirmed": 1}
        with self.assertRaisesRegex(WorldHealthError, "does not match its status counts"):
            build_world_health_report(
                map_quality=map_quality_report(),
                reachability_reports=[reachability],
                input_pins=input_pins(reachability_count=1, coverage_count=0),
            )

    def test_map_quality_component_source_mismatch_fails_closed(self) -> None:
        quality = copy.deepcopy(map_quality_report())
        quality["components"]["geometry"]["sourceSha256"] = OTHER_MAP_SHA
        with self.assertRaisesRegex(WorldHealthError, "does not prove the report source map"):
            build_world_health_report(
                map_quality=quality,
                input_pins=input_pins(reachability_count=0, coverage_count=0),
            )


if __name__ == "__main__":
    unittest.main()
