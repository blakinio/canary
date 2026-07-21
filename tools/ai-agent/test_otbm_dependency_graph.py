from __future__ import annotations

import unittest

from otbm_dependency_graph import (
    COVERAGE_FORMAT,
    MANIFEST_FORMAT,
    REGRESSION_FORMAT,
    REPORT_FORMAT,
    WORLD_HEALTH_FORMAT,
    DependencyGraphError,
    build_dependency_graph_report,
    canonical_report_sha256,
)


def sha(char: str) -> str:
    return char * 64


def pin(name: str, digest: str, fmt: str) -> dict:
    return {"fileName": name, "size": 123, "sha256": digest, "format": fmt}


def fixtures():
    world = {
        "format": WORLD_HEALTH_FORMAT,
        "schemaVersion": 1,
        "source": {"mapSha256": sha("b"), "worldIndexSha256": sha("d")},
        "dimensions": {
            "runtimeHandlers": {
                "samples": [
                    {"id": "handler-1", "evidence": {"selector": {"actionId": 1000}, "status": "resolved"}}
                ]
            }
        },
        "summary": {"structuralFindings": 0},
    }
    regression = {
        "format": REGRESSION_FORMAT,
        "schemaVersion": 1,
        "source": {
            "beforeMapSha256": sha("a"),
            "afterMapSha256": sha("b"),
            "beforeWorldIndexSha256": sha("c"),
            "afterWorldIndexSha256": sha("d"),
        },
        "impactEvidence": {
            "sampledFindingIds": ["otbm-diff:111111111111111111111111"],
            "sampledMechanics": [
                {
                    "findingId": "otbm-diff:111111111111111111111111",
                    "kind": "action-id-changed",
                    "position": [100, 200, 7],
                    "details": {"before": 1000, "after": 1001},
                }
            ],
        },
    }
    coverage = {
        "format": COVERAGE_FORMAT,
        "schemaVersion": 1,
        "currentMap": {"mapSha256": sha("b"), "worldIndexSha256": sha("d")},
        "targets": [{"id": "quest.demo", "kind": "quest", "requirementsSatisfied": False}],
    }
    pins = {
        "manifest": pin("manifest.json", sha("e"), MANIFEST_FORMAT),
        "worldHealth": pin("world.json", sha("f"), WORLD_HEALTH_FORMAT),
        "regressionGuard": pin("regression.json", sha("1"), REGRESSION_FORMAT),
        "coverageDashboard": pin("coverage.json", sha("2"), COVERAGE_FORMAT),
    }
    manifest = {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "source": {"mapSha256": sha("b"), "worldIndexSha256": sha("d")},
        "nodes": [
            {
                "id": "change.aid1000",
                "kind": "action-id",
                "selector": {"actionId": 1000},
                "evidence": [
                    {
                        "reportSha256": sha("1"),
                        "pointer": "/impactEvidence/sampledMechanics/0",
                        "expectation": {"mode": "subset", "value": {"kind": "action-id-changed"}},
                    }
                ],
            },
            {
                "id": "handler.aid1000",
                "kind": "script-handler",
                "selector": {"actionId": 1000},
                "evidence": [
                    {
                        "reportSha256": sha("f"),
                        "pointer": "/dimensions/runtimeHandlers/samples/0/evidence",
                        "expectation": {"mode": "subset", "value": {"selector": {"actionId": 1000}}},
                    }
                ],
            },
            {
                "id": "quest.demo",
                "kind": "quest",
                "selector": {"targetId": "quest.demo"},
                "evidence": [
                    {
                        "reportSha256": sha("2"),
                        "pointer": "/targets/0",
                        "expectation": {"mode": "subset", "value": {"id": "quest.demo", "kind": "quest"}},
                    }
                ],
            },
            {
                "id": "scenario.demo",
                "kind": "scenario",
                "selector": {"suite": "demo", "id": "scenario"},
                "evidence": [
                    {
                        "reportSha256": sha("2"),
                        "pointer": "/targets/0/id",
                        "expectation": {"mode": "equals", "value": "quest.demo"},
                    }
                ],
            },
        ],
        "edges": [
            {
                "id": "edge.change-handler",
                "source": "change.aid1000",
                "target": "handler.aid1000",
                "relation": "affected-by",
                "evidence": [
                    {"reportSha256": sha("1"), "pointer": "/impactEvidence/sampledFindingIds/0"}
                ],
            },
            {
                "id": "edge.handler-quest",
                "source": "handler.aid1000",
                "target": "quest.demo",
                "relation": "depends-on",
                "evidence": [
                    {"reportSha256": sha("f"), "pointer": "/dimensions/runtimeHandlers/samples/0/id"}
                ],
            },
            {
                "id": "edge.quest-scenario",
                "source": "quest.demo",
                "target": "scenario.demo",
                "relation": "covers",
                "evidence": [
                    {
                        "reportSha256": sha("2"),
                        "pointer": "/targets/0/requirementsSatisfied",
                        "expectation": {"mode": "equals", "value": False},
                    }
                ],
            },
        ],
        "queries": [{"id": "blast.change", "roots": ["change.aid1000"], "maxDepth": 8}],
    }
    return world, regression, coverage, manifest, pins


class DependencyGraphTests(unittest.TestCase):
    def test_proven_edges_produce_deterministic_transitive_blast_radius(self):
        world, regression, coverage, manifest, pins = fixtures()
        report = build_dependency_graph_report(
            manifest=manifest,
            world_health=world,
            regression_guard=regression,
            coverage_dashboard=coverage,
            input_pins=pins,
        )
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["summary"]["provenNodeCount"], 4)
        self.assertEqual(report["summary"]["provenEdgeCount"], 3)
        query = report["queries"][0]
        self.assertEqual([item["nodeId"] for item in query["directImpacts"]], ["handler.aid1000"])
        self.assertEqual(
            [(item["nodeId"], item["depth"]) for item in query["transitiveImpacts"]],
            [("handler.aid1000", 1), ("quest.demo", 2), ("scenario.demo", 3)],
        )
        self.assertEqual(
            query["transitiveImpacts"][-1]["pathEdgeIds"],
            ["edge.change-handler", "edge.handler-quest", "edge.quest-scenario"],
        )
        again = build_dependency_graph_report(
            manifest=manifest,
            world_health=world,
            regression_guard=regression,
            coverage_dashboard=coverage,
            input_pins=pins,
        )
        self.assertEqual(canonical_report_sha256(report), canonical_report_sha256(again))

    def test_unresolved_edge_is_boundary_and_is_not_traversed(self):
        world, regression, coverage, manifest, pins = fixtures()
        manifest["edges"][1]["evidence"][0]["pointer"] = "/dimensions/runtimeHandlers/missing"
        report = build_dependency_graph_report(
            manifest=manifest,
            world_health=world,
            regression_guard=regression,
            coverage_dashboard=coverage,
            input_pins=pins,
        )
        query = report["queries"][0]
        self.assertEqual([item["nodeId"] for item in query["transitiveImpacts"]], ["handler.aid1000"])
        self.assertEqual(query["unresolvedBoundaries"][0]["edgeId"], "edge.handler-quest")
        self.assertIn("EVIDENCE_POINTER_NOT_FOUND", query["unresolvedBoundaries"][0]["blockers"])

    def test_expectation_mismatch_makes_node_and_dependent_edges_unresolved(self):
        world, regression, coverage, manifest, pins = fixtures()
        manifest["nodes"][1]["evidence"][0]["expectation"]["value"]["selector"]["actionId"] = 9999
        report = build_dependency_graph_report(
            manifest=manifest,
            world_health=world,
            regression_guard=regression,
            coverage_dashboard=coverage,
            input_pins=pins,
        )
        handler = next(node for node in report["nodes"] if node["id"] == "handler.aid1000")
        self.assertEqual(handler["state"], "unresolved")
        self.assertIn("EVIDENCE_EXPECTATION_MISMATCH", handler["blockers"])
        self.assertEqual(report["queries"][0]["transitiveImpacts"], [])
        self.assertIn("TARGET_NODE_UNPROVEN", report["queries"][0]["unresolvedBoundaries"][0]["blockers"])

    def test_proven_cycle_terminates_and_keeps_shortest_paths(self):
        world, regression, coverage, manifest, pins = fixtures()
        manifest["edges"].append(
            {
                "id": "edge.quest-handler",
                "source": "quest.demo",
                "target": "handler.aid1000",
                "relation": "references",
                "evidence": [{"reportSha256": sha("2"), "pointer": "/targets/0/id"}],
            }
        )
        report = build_dependency_graph_report(
            manifest=manifest,
            world_health=world,
            regression_guard=regression,
            coverage_dashboard=coverage,
            input_pins=pins,
        )
        items = {item["nodeId"]: item for item in report["queries"][0]["transitiveImpacts"]}
        self.assertEqual(items["handler.aid1000"]["depth"], 1)
        self.assertEqual(items["quest.demo"]["depth"], 2)

    def test_world_health_must_match_regression_after_map(self):
        world, regression, coverage, manifest, pins = fixtures()
        world["source"]["mapSha256"] = sha("9")
        with self.assertRaisesRegex(DependencyGraphError, "after-map"):
            build_dependency_graph_report(
                manifest=manifest,
                world_health=world,
                regression_guard=regression,
                coverage_dashboard=coverage,
                input_pins=pins,
            )

    def test_coverage_dashboard_provenance_must_match(self):
        world, regression, coverage, manifest, pins = fixtures()
        coverage["currentMap"]["worldIndexSha256"] = sha("9")
        with self.assertRaisesRegex(DependencyGraphError, "same current map and World Index"):
            build_dependency_graph_report(
                manifest=manifest,
                world_health=world,
                regression_guard=regression,
                coverage_dashboard=coverage,
                input_pins=pins,
            )

    def test_unknown_node_reference_fails_closed(self):
        world, regression, coverage, manifest, pins = fixtures()
        manifest["edges"][0]["target"] = "missing"
        with self.assertRaisesRegex(DependencyGraphError, "unknown node"):
            build_dependency_graph_report(
                manifest=manifest,
                world_health=world,
                regression_guard=regression,
                coverage_dashboard=coverage,
                input_pins=pins,
            )


if __name__ == "__main__":
    unittest.main()
