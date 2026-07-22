from __future__ import annotations

import unittest

from otbm_content_completeness import (
    COVERAGE_FORMAT,
    DEPENDENCY_FORMAT,
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    ContentCompletenessError,
    build_content_completeness_report,
    canonical_report_sha256,
)


def sha(char: str) -> str:
    return char * 64


def pin(name: str, digest: str, fmt: str) -> dict:
    return {"fileName": name, "size": 123, "sha256": digest, "format": fmt}


def fixtures():
    dependency = {
        "format": DEPENDENCY_FORMAT,
        "schemaVersion": 1,
        "source": {"currentMapSha256": sha("a"), "currentWorldIndexSha256": sha("b")},
        "nodes": [
            {"id": "entry", "kind": "landmark", "state": "proven", "blockers": []},
            {"id": "lever", "kind": "mechanic", "state": "proven", "blockers": []},
            {"id": "handler", "kind": "script-handler", "state": "proven", "blockers": []},
            {"id": "quest", "kind": "quest", "state": "proven", "blockers": []},
            {"id": "orphan.map", "kind": "mechanic", "state": "proven", "blockers": []},
            {"id": "orphan.script", "kind": "script-handler", "state": "proven", "blockers": []},
        ],
        "edges": [
            {
                "id": "edge.lever-handler",
                "source": "lever",
                "target": "handler",
                "relation": "activates",
                "state": "proven",
                "blockers": [],
            },
            {
                "id": "edge.handler-quest",
                "source": "handler",
                "target": "quest",
                "relation": "depends-on",
                "state": "proven",
                "blockers": [],
            },
        ],
        "queries": [
            {
                "id": "route.quest",
                "roots": ["entry"],
                "provenRootNodeIds": ["entry"],
                "unresolvedRootNodeIds": [],
                "transitiveImpacts": [
                    {"nodeId": "lever", "depth": 1, "pathNodeIds": ["entry", "lever"], "pathEdgeIds": ["e1"]},
                    {"nodeId": "quest", "depth": 2, "pathNodeIds": ["entry", "lever", "quest"], "pathEdgeIds": ["e1", "e2"]},
                ],
                "unresolvedBoundaries": [],
            }
        ],
    }
    coverage = {
        "format": COVERAGE_FORMAT,
        "schemaVersion": 1,
        "currentMap": {"mapSha256": sha("a"), "worldIndexSha256": sha("b")},
        "targets": [
            {
                "id": "quest.demo",
                "kind": "quest",
                "dimensions": {
                    "indexedOnExactMap": {"state": "proven", "blockers": []},
                    "scriptResolved": {"state": "proven", "blockers": []},
                    "physicallyRuntimeProven": {"state": "not-evaluated", "blockers": []},
                },
            }
        ],
    }
    manifest = {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "source": {"mapSha256": sha("a"), "worldIndexSha256": sha("b")},
        "targets": [
            {
                "id": "quest.demo",
                "kind": "quest",
                "reason": "Reviewed demo quest completeness target",
                "stages": [
                    {
                        "id": "entry-stage",
                        "role": "entry",
                        "required": True,
                        "nodeIds": ["entry"],
                    },
                    {
                        "id": "mechanic-stage",
                        "role": "mechanic",
                        "required": True,
                        "nodeIds": ["lever", "handler"],
                        "coverageRequirements": [
                            {"targetId": "quest.demo", "dimension": "indexedOnExactMap"},
                            {"targetId": "quest.demo", "dimension": "scriptResolved"},
                        ],
                    },
                    {
                        "id": "path-stage",
                        "role": "exit",
                        "required": True,
                        "pathRequirement": {"queryId": "route.quest", "targetNodeIds": ["quest"]},
                    },
                ],
                "orphanChecks": [
                    {
                        "id": "lever-handler",
                        "nodeId": "lever",
                        "direction": "outgoing",
                        "relations": ["activates"],
                        "counterpartKinds": ["script-handler"],
                        "missingClassification": "map-only",
                        "findingKind": "placement-without-handler",
                    },
                    {
                        "id": "map-only",
                        "nodeId": "orphan.map",
                        "direction": "outgoing",
                        "relations": ["activates"],
                        "counterpartKinds": ["script-handler"],
                        "missingClassification": "map-only",
                        "findingKind": "placement-without-handler",
                    },
                    {
                        "id": "script-only",
                        "nodeId": "orphan.script",
                        "direction": "incoming",
                        "relations": ["activates"],
                        "counterpartKinds": ["mechanic"],
                        "missingClassification": "script-only",
                        "findingKind": "handler-without-placement",
                    },
                ],
            }
        ],
    }
    pins = {
        "manifest": pin("manifest.json", sha("c"), MANIFEST_FORMAT),
        "dependencyGraph": pin("dependency.json", sha("d"), DEPENDENCY_FORMAT),
        "coverageDashboard": pin("coverage.json", sha("e"), COVERAGE_FORMAT),
    }
    return dependency, coverage, manifest, pins


class ContentCompletenessTests(unittest.TestCase):
    def build(self):
        dependency, coverage, manifest, pins = fixtures()
        return build_content_completeness_report(
            manifest=manifest,
            dependency_graph=dependency,
            coverage_dashboard=coverage,
            input_pins=pins,
        )

    def test_confirmed_stages_and_explicit_orphan_classifications(self):
        report = self.build()
        self.assertEqual(report["format"], REPORT_FORMAT)
        target = report["targets"][0]
        self.assertTrue(target["requirementsSatisfied"])
        self.assertFalse(target["runtimeGameplayCompletionProven"])
        self.assertTrue(all(stage["classification"] == "confirmed" for stage in target["stages"]))
        checks = {check["id"]: check for check in target["orphanChecks"]}
        self.assertFalse(checks["lever-handler"]["finding"])
        self.assertEqual(checks["map-only"]["classification"], "map-only")
        self.assertEqual(checks["script-only"]["classification"], "script-only")
        self.assertEqual(report["summary"]["findingCount"], 2)
        self.assertFalse(report["policy"]["runtimeGameplayCompletionClaimed"])

    def test_missing_required_stage_remains_unresolved(self):
        dependency, coverage, manifest, pins = fixtures()
        manifest["targets"][0]["stages"].append(
            {"id": "reward-missing", "role": "reward", "required": True, "missingClassification": "unresolved"}
        )
        report = build_content_completeness_report(
            manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
        )
        stage = next(item for item in report["targets"][0]["stages"] if item["id"] == "reward-missing")
        self.assertEqual(stage["classification"], "unresolved")
        self.assertIn("MISSING_REQUIRED_STAGE_EVIDENCE", stage["findingCodes"])
        self.assertFalse(report["targets"][0]["requirementsSatisfied"])
        self.assertFalse(report["policy"]["globalAbsenceInferred"])

    def test_unproven_required_path_is_unresolved_not_runtime_impossible(self):
        dependency, coverage, manifest, pins = fixtures()
        dependency["queries"][0]["transitiveImpacts"] = []
        report = build_content_completeness_report(
            manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
        )
        stage = next(item for item in report["targets"][0]["stages"] if item["id"] == "path-stage")
        self.assertEqual(stage["classification"], "unresolved")
        self.assertIn("REQUIRED_PATH_NOT_PROVEN", stage["findingCodes"])
        self.assertFalse(report["policy"]["runtimeGameplayCompletionClaimed"])

    def test_stale_coverage_is_conflicting(self):
        dependency, coverage, manifest, pins = fixtures()
        coverage["targets"][0]["dimensions"]["scriptResolved"]["state"] = "stale"
        report = build_content_completeness_report(
            manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
        )
        stage = next(item for item in report["targets"][0]["stages"] if item["id"] == "mechanic-stage")
        self.assertEqual(stage["classification"], "conflicting")
        self.assertFalse(report["targets"][0]["requirementsSatisfied"])

    def test_ambiguous_dependency_node_is_conflicting(self):
        dependency, coverage, manifest, pins = fixtures()
        dependency["nodes"][1]["state"] = "unresolved"
        dependency["nodes"][1]["blockers"] = ["NODE_DECLARED_AMBIGUOUS"]
        report = build_content_completeness_report(
            manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
        )
        stage = next(item for item in report["targets"][0]["stages"] if item["id"] == "mechanic-stage")
        self.assertEqual(stage["classification"], "conflicting")

    def test_unknown_dependency_node_fails_closed(self):
        dependency, coverage, manifest, pins = fixtures()
        manifest["targets"][0]["stages"][0]["nodeIds"] = ["missing"]
        with self.assertRaisesRegex(ContentCompletenessError, "unknown dependency node"):
            build_content_completeness_report(
                manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
            )

    def test_provenance_mismatch_fails_closed(self):
        dependency, coverage, manifest, pins = fixtures()
        coverage["currentMap"]["worldIndexSha256"] = sha("9")
        with self.assertRaisesRegex(ContentCompletenessError, "must match Dependency Graph"):
            build_content_completeness_report(
                manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
            )

    def test_unresolved_matching_edge_never_becomes_map_only(self):
        dependency, coverage, manifest, pins = fixtures()
        dependency["edges"][0]["state"] = "unresolved"
        dependency["edges"][0]["blockers"] = ["EVIDENCE_POINTER_NOT_FOUND"]
        report = build_content_completeness_report(
            manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
        )
        check = next(item for item in report["targets"][0]["orphanChecks"] if item["id"] == "lever-handler")
        self.assertEqual(check["classification"], "unresolved")
        self.assertEqual(check["unresolvedEdgeIds"], ["edge.lever-handler"])

    def test_unsupported_orphan_relation_fails_closed(self):
        dependency, coverage, manifest, pins = fixtures()
        manifest["targets"][0]["orphanChecks"][0]["relations"] = ["guessed-nearby"]
        with self.assertRaisesRegex(ContentCompletenessError, "unsupported relations"):
            build_content_completeness_report(
                manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
            )

    def test_output_is_deterministic(self):
        dependency, coverage, manifest, pins = fixtures()
        first = build_content_completeness_report(
            manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
        )
        second = build_content_completeness_report(
            manifest=manifest, dependency_graph=dependency, coverage_dashboard=coverage, input_pins=pins
        )
        self.assertEqual(canonical_report_sha256(first), canonical_report_sha256(second))


if __name__ == "__main__":
    unittest.main()
