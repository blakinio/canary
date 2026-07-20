from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("otbm_e2e_impacted_selection.py")
spec = importlib.util.spec_from_file_location("otbm_e2e_impacted_selection", MODULE_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

A = "a" * 64
B = "b" * 64
C = "c" * 64
D = "d" * 64


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def diff_payload(*, positions=(), truncated=False, scope="full-index", null_position=False):
    findings = []
    for index, position in enumerate(positions):
        findings.append({"id": f"otbm-diff:{index:024x}", "position": list(position)})
    if null_position:
        findings.append({"id": "otbm-diff:" + "f" * 24, "position": None})
    return {
        "format": "canary-otbm-semantic-diff-v1",
        "schemaVersion": 1,
        "ok": True,
        "compatibility": {"compatible": True},
        "provenance": {
            "before": {"sourceMap": {"sha256": A}, "worldIndex": {"sha256": B}},
            "after": {"sourceMap": {"sha256": C}, "worldIndex": {"sha256": D}},
        },
        "scope": {"type": scope},
        "summary": {"findings": {"total": len(findings), "truncated": truncated}},
        "findings": findings,
    }


def scenario_payload(scenario_id="route-one", suite="movement", route="alpha", follow=True):
    steps = [{"id": "online", "action": "observe_online", "expected": True}]
    if follow:
        steps.append({"id": "route", "action": "follow_route", "route": route, "timeout_ms": 5000})
    return {"schema_version": 1, "id": scenario_id, "suite": suite, "steps": steps}


def route_payload(*, path=((10, 10, 7), (11, 10, 7)), map_sha=A, index_sha=B, executable=True, interaction_position=None):
    edges = [
        {
            "from": [10, 10, 7],
            "to": [11, 10, 7],
            "kind": "movement",
            "isTransition": False,
            "transitionId": None,
            "evidence": {"source": "reachability-bfs-predecessor", "edgeSource": "_movement_neighbors", "routingMode": "strict"},
        }
    ]
    if interaction_position is not None:
        edges[0]["interactions"] = [
            {
                "format": "canary-otbm-route-interaction-resolution-v1",
                "schemaVersion": 1,
                "executionStatus": "executable",
                "selectorQuery": {"position": list(interaction_position), "itemId": 100},
                "matchedEntryIds": ["x"],
                "blockers": [],
            }
        ]
    return {
        "format": "canary-otbm-e2e-route-plan-v1",
        "schemaVersion": 1,
        "provenance": {"map": {"sha256": map_sha}, "worldIndex": {"sha256": index_sha}},
        "executionStatus": "executable" if executable else "blocked",
        "pathComplete": executable,
        "path": [list(item) for item in path],
        "edges": edges,
    }


class ImpactSelectionTests(unittest.TestCase):
    def run_selection(self, diff, scenarios, routes):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        diff_path = root / "diff.json"
        write_json(diff_path, diff)
        scenario_paths = []
        for name, payload in scenarios.items():
            path = root / "scenarios" / f"{name}.json"
            write_json(path, payload)
            scenario_paths.append(path)
        route_root = root / "routes"
        for route_id, payload in routes.items():
            write_json(route_root / f"route-{route_id}.json", payload)
        return mod.select_impacted_scenarios(
            semantic_diff_path=diff_path,
            scenario_paths=scenario_paths,
            route_plan_root=route_root,
        )

    def single(self, payload):
        self.assertEqual(payload["summary"]["scenarioCount"], 1)
        return payload["scenarios"][0]

    def test_full_diff_no_intersection_skips(self):
        result = self.single(self.run_selection(diff_payload(positions=[(50, 50, 7)]), {"s": scenario_payload()}, {"alpha": route_payload()}))
        self.assertFalse(result["selected"])
        self.assertEqual(result["reasons"][0]["code"], "EXACT_FULL_INDEX_DIFF_PROVES_NON_IMPACT")

    def test_path_intersection_selects(self):
        result = self.single(self.run_selection(diff_payload(positions=[(11, 10, 7)]), {"s": scenario_payload()}, {"alpha": route_payload()}))
        self.assertTrue(result["selected"])
        self.assertFalse(result["failClosed"])
        self.assertEqual(len(result["impactedFindingIds"]), 1)

    def test_interaction_target_intersection_selects(self):
        result = self.single(self.run_selection(diff_payload(positions=[(12, 10, 7)]), {"s": scenario_payload()}, {"alpha": route_payload(interaction_position=(12, 10, 7))}))
        self.assertTrue(result["selected"])

    def test_truncated_diff_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(truncated=True), {"s": scenario_payload()}, {"alpha": route_payload()}))
        self.assertTrue(result["selected"])
        self.assertTrue(result["failClosed"])
        self.assertIn("SEMANTIC_DIFF_FINDINGS_TRUNCATED", {r["code"] for r in result["reasons"]})

    def test_bounded_scope_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(scope="bounded-region"), {"s": scenario_payload()}, {"alpha": route_payload()}))
        self.assertTrue(result["selected"])
        self.assertIn("SEMANTIC_DIFF_SCOPE_NOT_FULL_INDEX", {r["code"] for r in result["reasons"]})

    def test_null_position_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(null_position=True), {"s": scenario_payload()}, {"alpha": route_payload()}))
        self.assertTrue(result["selected"])
        self.assertIn("SEMANTIC_DIFF_FINDING_POSITION_UNKNOWN", {r["code"] for r in result["reasons"]})

    def test_stale_map_provenance_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(), {"s": scenario_payload()}, {"alpha": route_payload(map_sha=C)}))
        self.assertTrue(result["selected"])
        self.assertIn("BASELINE_ROUTE_MAP_PROVENANCE_STALE", {r["code"] for r in result["reasons"]})

    def test_stale_world_index_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(), {"s": scenario_payload()}, {"alpha": route_payload(index_sha=D)}))
        self.assertTrue(result["selected"])
        self.assertIn("BASELINE_ROUTE_WORLD_INDEX_PROVENANCE_STALE", {r["code"] for r in result["reasons"]})

    def test_missing_route_plan_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(), {"s": scenario_payload()}, {}))
        self.assertTrue(result["selected"])
        self.assertIn("BASELINE_ROUTE_PLAN_MISSING", {r["code"] for r in result["reasons"]})

    def test_blocked_route_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(), {"s": scenario_payload()}, {"alpha": route_payload(executable=False)}))
        self.assertTrue(result["selected"])
        self.assertIn("BASELINE_ROUTE_NOT_EXECUTABLE", {r["code"] for r in result["reasons"]})

    def test_scenario_without_follow_route_selects_fail_closed(self):
        result = self.single(self.run_selection(diff_payload(), {"s": scenario_payload(follow=False)}, {}))
        self.assertTrue(result["selected"])
        self.assertIn("SCENARIO_FOLLOW_ROUTE_MISSING", {r["code"] for r in result["reasons"]})

    def test_duplicate_scenario_identity_rejected(self):
        with self.assertRaises(mod.SelectionError):
            self.run_selection(diff_payload(), {"a": scenario_payload(), "b": scenario_payload()}, {"alpha": route_payload()})

    def test_unsupported_diff_rejected(self):
        bad = diff_payload()
        bad["format"] = "wrong"
        with self.assertRaises(mod.SelectionError):
            self.run_selection(bad, {"s": scenario_payload()}, {"alpha": route_payload()})

    def test_deterministic_scenario_order(self):
        payload = self.run_selection(
            diff_payload(),
            {"z": scenario_payload("z", "movement", "zroute"), "a": scenario_payload("a", "login", "aroute")},
            {"zroute": route_payload(), "aroute": route_payload()},
        )
        self.assertEqual([(s["suite"], s["id"]) for s in payload["scenarios"]], [("login", "a"), ("movement", "z")])

    def test_policy_declares_no_parser_pathfinder_or_execution(self):
        payload = self.run_selection(diff_payload(), {"s": scenario_payload()}, {"alpha": route_payload()})
        self.assertFalse(payload["policy"]["otbmParsed"])
        self.assertFalse(payload["policy"]["worldIndexBuilt"])
        self.assertFalse(payload["policy"]["routeCalculated"])
        self.assertFalse(payload["policy"]["physicalE2eExecuted"])
        self.assertFalse(payload["policy"]["mapModified"])


if __name__ == "__main__":
    unittest.main()
