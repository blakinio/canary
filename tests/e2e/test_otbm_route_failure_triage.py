from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "e2e" / "otbm_route_failure_triage.py"
SPEC = importlib.util.spec_from_file_location("otbm_route_failure_triage", MODULE_PATH)
assert SPEC and SPEC.loader
triage = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = triage
SPEC.loader.exec_module(triage)


class OtbmRouteFailureTriageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.artifacts = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_manifest(self, *, route_aware: bool = True) -> None:
        steps = (
            [{"id": "route-step", "action": "follow_route", "route": "test-route"}]
            if route_aware
            else [{"id": "wait", "action": "wait", "ms": 1}]
        )
        (self.artifacts / "scenario-manifest.json").write_text(
            json.dumps({"schema_version": 1, "key": "movement/fixture", "scenario": {"steps": steps}}),
            encoding="utf-8",
        )

    def write_route_preparation(self) -> None:
        (self.artifacts / "route-preparer.sha256").write_text(
            "abc  prepare_otbm_route.py\n", encoding="utf-8"
        )
        (self.artifacts / "route-preparation.json").write_text(
            json.dumps({"status": "passed", "routeIds": ["test-route"]}),
            encoding="utf-8",
        )

    def write_route(self, edge: dict | None = None) -> None:
        route_edge = edge or {
            "kind": "movement",
            "from": [100, 100, 7],
            "to": [101, 100, 7],
        }
        (self.artifacts / "route-test-route.json").write_text(
            json.dumps(
                {
                    "format": "canary-otbm-e2e-route-plan-v1",
                    "origin": [100, 100, 7],
                    "destination": route_edge["to"],
                    "edges": [route_edge],
                }
            ),
            encoding="utf-8",
        )

    def write_events(self, *rows: tuple[str, str]) -> None:
        content = "timestamp\tkey\tvalue\n"
        content += "\n".join(
            f"{index}\t{key}\t{value}" for index, (key, value) in enumerate(rows, start=1)
        )
        content += "\n"
        (self.artifacts / "client-events.tsv").write_text(content, encoding="utf-8")

    def write_route_failure(self, message: str, *, edge: dict | None = None) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route(edge)
        self.write_events(
            ("route_route-step_edge_1", "start"),
            ("route_route-step_edge_1", "failure"),
            ("e2e", "failure"),
            ("error", f"step route-step (follow_route) failed: {message}"),
        )

    def category(self) -> str | None:
        return triage.classify_artifacts(self.artifacts)["failureCategory"]

    def test_success_has_no_failure_category(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        self.write_events(("e2e", "success"))
        (self.artifacts / "result.json").write_text(
            json.dumps({"schema_version": 2, "status": "success", "checks": {}}),
            encoding="utf-8",
        )
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["status"], "success")
        self.assertIsNone(result["failureCategory"])

    def test_non_route_scenario_is_not_applicable(self) -> None:
        self.write_manifest(route_aware=False)
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["status"], "not-applicable")
        self.assertFalse(result["routeAware"])

    def test_missing_manifest_fails_closed_unclassified(self) -> None:
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["status"], "unclassified")
        self.assertIsNone(result["routeAware"])

    def test_route_resolution_failure_requires_preparer_invocation_evidence(self) -> None:
        self.write_manifest()
        (self.artifacts / "route-preparer.sha256").write_text("abc\n", encoding="utf-8")
        self.assertEqual(self.category(), "ROUTE_RESOLUTION_FAILURE")

    def test_missing_preparer_evidence_is_not_guessed_as_route_resolution_failure(self) -> None:
        self.write_manifest()
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["status"], "unclassified")
        self.assertIsNone(result["failureCategory"])

    def test_route_preflight_failure_precedes_missing_preparation_summary(self) -> None:
        self.write_manifest()
        (self.artifacts / "route-preparer.sha256").write_text("abc\n", encoding="utf-8")
        (self.artifacts / "route-test-route-preflight.json").write_text(
            json.dumps(
                {
                    "format": "canary-otbm-e2e-route-preflight-v1",
                    "status": "failed",
                    "ok": False,
                    "firstBlocker": {"code": "MAP_HASH_MISMATCH"},
                }
            ),
            encoding="utf-8",
        )
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["failureCategory"], "ROUTE_PREFLIGHT_FAILURE")
        self.assertIn("MAP_HASH_MISMATCH", result["firstFailure"]["detail"])

    def test_plan_load_failure_from_client_error(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        self.write_events(
            ("e2e", "failure"),
            ("error", "failed to open scenario plan: unavailable"),
        )
        self.assertEqual(self.category(), "PLAN_LOAD_FAILURE")

    def test_plan_load_failure_from_runner_scenario_resolution_phase(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        (self.artifacts / "result.json").write_text(
            json.dumps({"schema_version": 1, "status": "failure", "phase": "scenario-resolution"}),
            encoding="utf-8",
        )
        self.assertEqual(self.category(), "PLAN_LOAD_FAILURE")

    def test_initial_position_mismatch(self) -> None:
        self.write_route_failure(
            "INITIAL_POSITION_MISMATCH: route origin mismatch actual=100,101,7 expected=100,100,7"
        )
        self.assertEqual(self.category(), "INITIAL_POSITION_MISMATCH")

    def test_movement_divergence(self) -> None:
        self.write_route_failure(
            "MOVEMENT_DIVERGENCE: route drift actual=102,100,7 expected=101,100,7"
        )
        self.assertEqual(self.category(), "MOVEMENT_DIVERGENCE")

    def test_movement_timeout_maps_to_blocked_tile_without_guessing_actor(self) -> None:
        self.write_route_failure(
            "MOVEMENT_TIMEOUT: position=100,100,7 expected=101,100,7 timeout_ms=5000"
        )
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["failureCategory"], "BLOCKED_TILE")
        self.assertEqual(result["firstFailure"]["edgeIndex"], 1)
        self.assertNotIn("creature", result["firstFailure"]["detail"].lower())

    def test_explicit_unsupported_interaction(self) -> None:
        self.write_route_failure("INTERACTION_FAILED: unsupported route edge kind: custom")
        self.assertEqual(self.category(), "INTERACTION_UNSUPPORTED")

    def test_ambiguous_interaction_failure_stays_unclassified(self) -> None:
        self.write_route_failure("INTERACTION_FAILED: target item 1234 unavailable at 100,100,7")
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["status"], "unclassified")
        self.assertEqual(result["firstFailure"]["code"], "INTERACTION_FAILED")

    def test_interaction_timeout(self) -> None:
        edge = {
            "kind": "transition",
            "transitionKind": "ladder",
            "from": [100, 100, 8],
            "to": [100, 100, 7],
        }
        self.write_route_failure(
            "INTERACTION_TIMEOUT: position=100,100,8 expected=100,100,7 timeout_ms=5000",
            edge=edge,
        )
        self.assertEqual(self.category(), "INTERACTION_TIMEOUT")

    def test_teleport_not_triggered_uses_route_edge_context(self) -> None:
        edge = {
            "kind": "transition",
            "transitionKind": "teleport",
            "from": [100, 100, 7],
            "to": [110, 110, 7],
        }
        self.write_route_failure(
            "TRANSITION_NOT_TRIGGERED: position=100,100,7 expected=110,110,7 timeout_ms=5000",
            edge=edge,
        )
        self.assertEqual(self.category(), "TELEPORT_NOT_TRIGGERED")

    def test_non_teleport_transition_not_triggered_maps_to_interaction_timeout(self) -> None:
        edge = {
            "kind": "transition",
            "transitionKind": "stairs",
            "from": [100, 100, 8],
            "to": [100, 100, 7],
        }
        self.write_route_failure(
            "TRANSITION_NOT_TRIGGERED: position=100,100,8 expected=100,100,7 timeout_ms=5000",
            edge=edge,
        )
        self.assertEqual(self.category(), "INTERACTION_TIMEOUT")

    def test_wrong_transition_destination(self) -> None:
        edge = {
            "kind": "transition",
            "transitionKind": "teleport",
            "from": [100, 100, 7],
            "to": [110, 110, 7],
        }
        self.write_route_failure(
            "WRONG_TRANSITION_DESTINATION: actual=109,110,7 expected=110,110,7",
            edge=edge,
        )
        self.assertEqual(self.category(), "WRONG_TRANSITION_DESTINATION")

    def test_wrong_floor_delta_requires_matching_expected_xy(self) -> None:
        edge = {
            "kind": "transition",
            "transitionKind": "stairs",
            "from": [100, 100, 8],
            "to": [100, 100, 7],
        }
        self.write_route_failure(
            "WRONG_TRANSITION_DESTINATION: actual=100,100,6 expected=100,100,7",
            edge=edge,
        )
        self.assertEqual(self.category(), "WRONG_FLOOR_DELTA")

    def test_server_disconnect(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        self.write_events(
            ("login_1", "success"),
            ("e2e", "failure"),
            ("error", "unexpected disconnect before safe logout in phase 1"),
        )
        self.assertEqual(self.category(), "SERVER_DISCONNECT")

    def test_persistence_failure_from_explicit_check(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        self.write_events(
            ("server_persistence_1", "confirmed"),
            ("login_2", "success"),
            ("e2e", "failure"),
            ("error", "persistence check level (level) failed: actual=499 expected=500"),
        )
        self.assertEqual(self.category(), "PERSISTENCE_FAILURE")

    def test_persistence_failure_from_result_checks(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        (self.artifacts / "result.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "status": "failure",
                    "checks": {
                        "scenario_sql_assertions": False,
                        "lastlogin_persisted": True,
                        "lastlogout_persisted": True,
                    },
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(self.category(), "PERSISTENCE_FAILURE")

    def test_relog_failure_from_phase_two_login_error(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        self.write_events(
            ("login_1", "success"),
            ("logout_1", "complete"),
            ("server_persistence_1", "confirmed"),
            ("e2e", "failure"),
            ("error", "login error in phase 2: account name or password is not correct"),
        )
        self.assertEqual(self.category(), "RELOG_FAILURE")

    def test_relog_failure_from_result_and_lifecycle_markers(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        self.write_events(
            ("login_1", "success"),
            ("logout_1", "complete"),
            ("server_persistence_1", "confirmed"),
        )
        (self.artifacts / "result.json").write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "status": "failure",
                    "checks": {
                        "two_server_logins_observed": False,
                        "scenario_sql_assertions": True,
                        "lastlogin_persisted": True,
                        "lastlogout_persisted": True,
                    },
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(self.category(), "RELOG_FAILURE")

    def test_unmapped_explicit_error_fails_closed(self) -> None:
        self.write_manifest()
        self.write_route_preparation()
        self.write_route()
        self.write_events(("e2e", "failure"), ("error", "unknown deterministic fixture failure"))
        result = triage.classify_artifacts(self.artifacts)
        self.assertEqual(result["status"], "unclassified")
        self.assertIsNone(result["failureCategory"])

    def test_write_triage_uses_default_artifact_name(self) -> None:
        self.write_manifest(route_aware=False)
        result = triage.write_triage(self.artifacts)
        output = self.artifacts / "otbm-route-failure-triage.json"
        self.assertTrue(output.is_file())
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), result)


if __name__ == "__main__":
    unittest.main()
