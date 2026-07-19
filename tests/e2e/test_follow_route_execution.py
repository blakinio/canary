from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
ROUTE_HELPER_PATH = ROOT / "tools" / "e2e" / "route_plan_execution.py"
ROUTE_DRIVER_PATH = ROOT / "tools" / "e2e" / "client" / "agent_e2e_route.lua"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


runner = load_module("canary_e2e_runner_follow_route", RUNNER_PATH)
route_execution = load_module("canary_e2e_route_execution_tests", ROUTE_HELPER_PATH)


def resolution(*, kind: str = "use-map-item", position: list[int] | None = None, item_id: int = 1223) -> dict:
    position = position or [101, 100, 7]
    activation: dict = {"kind": kind}
    query: dict = {"position": position, "itemId": item_id}
    if kind == "use-map-item":
        activation.update({"target": "selector-position"})
    elif kind == "use-inventory-on-map":
        activation.update({"target": "selector-position", "inventoryItemId": 3147})
    return {
        "format": "canary-otbm-route-interaction-resolution-v1",
        "schemaVersion": 1,
        "executionStatus": "executable",
        "selectorQuery": query,
        "matchedEntryId": "reviewed-door",
        "matchedEntryIds": ["reviewed-door"],
        "activation": activation,
        "evidence": {"status": "reviewed", "references": ["test"]},
        "blockers": [],
    }


def movement_plan(*, interaction: dict | None = None) -> dict:
    edge = {
        "from": [100, 100, 7],
        "to": [101, 100, 7],
        "kind": "movement",
        "isTransition": False,
        "transitionId": None,
        "evidence": {
            "source": "reachability-bfs-predecessor",
            "edgeSource": "_movement_neighbors",
            "routingMode": "executable" if interaction else "strict",
        },
        "interactions": [] if interaction is None else [interaction],
        "executionBlockers": [],
    }
    return {
        "format": "canary-otbm-e2e-route-plan-v1",
        "schemaVersion": 1,
        "planHashSha256": "a" * 64,
        "origin": [100, 100, 7],
        "destination": [101, 100, 7],
        "routeStatus": "conditional" if interaction else "confirmed",
        "executionStatus": "executable",
        "routingMode": "executable" if interaction else "strict",
        "pathComplete": True,
        "path": [[100, 100, 7], [101, 100, 7]],
        "edges": [edge],
        "blockers": [],
    }


def transition_plan(*, activation: dict, selector_query: dict | None = None) -> dict:
    selector_query = selector_query or {
        "transitionId": "teleport:1",
        "transitionKind": "teleport",
        "transitionEvidenceSource": "worldIndex",
    }
    edge = {
        "from": [100, 100, 7],
        "to": [200, 200, 8],
        "kind": "transition",
        "isTransition": True,
        "transitionId": "teleport:1",
        "evidence": {
            "source": "validated-transition-edge",
            "provenanceKey": "worldIndex",
            "transition": {
                "id": "teleport:1",
                "kind": "teleport",
                "source": [100, 100, 7],
                "destination": [200, 200, 8],
                "itemId": 1387,
                "expectedItemIds": [1387],
            },
        },
        "interactions": [
            {
                "format": "canary-otbm-route-interaction-resolution-v1",
                "schemaVersion": 1,
                "executionStatus": "executable",
                "selectorQuery": selector_query,
                "matchedEntryId": "reviewed-transition",
                "matchedEntryIds": ["reviewed-transition"],
                "activation": activation,
                "evidence": {"status": "reviewed", "references": ["test"]},
                "blockers": [],
            }
        ],
        "executionBlockers": [],
    }
    return {
        "format": "canary-otbm-e2e-route-plan-v1",
        "schemaVersion": 1,
        "planHashSha256": "b" * 64,
        "origin": [100, 100, 7],
        "destination": [200, 200, 8],
        "routeStatus": "confirmed",
        "executionStatus": "executable",
        "routingMode": "executable",
        "pathComplete": True,
        "path": [[100, 100, 7], [200, 200, 8]],
        "edges": [edge],
        "blockers": [],
    }


class FollowRouteExecutionTests(unittest.TestCase):
    def test_route_artifact_name_is_derived_from_logical_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact_dir = Path(directory)
            (artifact_dir / "route-primary.json").write_text(json.dumps(movement_plan()), encoding="utf-8")
            routes = route_execution.load_route_plans(
                [{"id": "route", "action": "follow_route", "route": "primary"}], artifact_dir
            )
            self.assertEqual(routes["primary"]["origin"], [100, 100, 7])
            self.assertEqual(routes["primary"]["destination"], [101, 100, 7])
            self.assertNotIn("path", routes["primary"])

    def test_missing_canonical_route_artifact_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(route_execution.RoutePlanExecutionError, "canonical route artifact is missing"):
                route_execution.load_route_plans(
                    [{"id": "route", "action": "follow_route", "route": "primary"}], Path(directory)
                )

    def test_plain_optimistic_route_is_not_physically_executable(self) -> None:
        plan = movement_plan()
        plan["routingMode"] = "optimistic"
        with self.assertRaisesRegex(route_execution.RoutePlanExecutionError, "optimistic routes are not physically executable"):
            route_execution.validate_route_plan(plan, route_id="primary")

    def test_unsupported_interaction_kind_fails_before_client_execution(self) -> None:
        plan = transition_plan(activation={"kind": "shell-command"})
        with self.assertRaisesRegex(route_execution.RoutePlanExecutionError, "activation.kind is unsupported"):
            route_execution.validate_route_plan(plan, route_id="primary")

    def test_blocked_interaction_fails_before_client_execution(self) -> None:
        plan = movement_plan(interaction=resolution())
        plan["edges"][0]["interactions"][0]["executionStatus"] = "blocked"
        plan["edges"][0]["interactions"][0]["blockers"] = [{"code": "interaction-not-reviewed"}]
        with self.assertRaisesRegex(route_execution.RoutePlanExecutionError, "is not executable"):
            route_execution.validate_route_plan(plan, route_id="primary")

    def test_use_map_item_resolves_exact_selector_target(self) -> None:
        normalized = route_execution.validate_route_plan(
            movement_plan(interaction=resolution(position=[101, 100, 7], item_id=1223)), route_id="primary"
        )
        interaction = normalized["edges"][0]["interactions"][0]
        self.assertEqual(interaction["kind"], "use-map-item")
        self.assertEqual(interaction["target_position"], [101, 100, 7])
        self.assertEqual(interaction["target_item_id"], 1223)

    def test_use_inventory_on_map_preserves_inventory_and_exact_target_ids(self) -> None:
        normalized = route_execution.validate_route_plan(
            movement_plan(interaction=resolution(kind="use-inventory-on-map", item_id=1223)), route_id="primary"
        )
        interaction = normalized["edges"][0]["interactions"][0]
        self.assertEqual(interaction["inventory_item_id"], 3147)
        self.assertEqual(interaction["target_item_id"], 1223)

    def test_transition_source_target_uses_validated_transition_item_evidence(self) -> None:
        normalized = route_execution.validate_route_plan(
            transition_plan(activation={"kind": "use-map-item", "target": "transition-source"}), route_id="primary"
        )
        interaction = normalized["edges"][0]["interactions"][0]
        self.assertEqual(interaction["target_position"], [100, 100, 7])
        self.assertEqual(interaction["target_item_id"], 1387)

    def test_runtime_contains_exact_first_failure_diagnostics_and_maintained_otclient_calls(self) -> None:
        source = ROUTE_DRIVER_PATH.read_text(encoding="utf-8")
        for code in (
            "INITIAL_POSITION_MISMATCH",
            "MOVEMENT_DIVERGENCE",
            "MOVEMENT_TIMEOUT",
            "INTERACTION_FAILED",
            "TRANSITION_NOT_TRIGGERED",
            "WRONG_TRANSITION_DESTINATION",
            "FINAL_POSITION_MISMATCH",
        ):
            self.assertIn(code, source)
        self.assertIn("g_game.use(targetThing)", source)
        self.assertIn("g_game.useInventoryItemWith(inventoryItemId, targetThing)", source)
        self.assertIn("g_game.walk(direction)", source)
        self.assertIn('"route_" .. step.id .. "_edge_"', source)
        self.assertIn("samePosition(actual, expected)", source)

    def test_follow_route_step_rejects_arbitrary_path_field(self) -> None:
        step = {"id": "route", "action": "follow_route", "route": "primary", "path": "/tmp/route.json"}
        with self.assertRaisesRegex(runner.ScenarioError, "unknown field"):
            runner.validate_steps({"steps": [step]})

    def test_follow_route_step_has_bounded_timeout_and_logical_route_id(self) -> None:
        step = {"id": "route", "action": "follow_route", "route": "primary", "timeout_ms": 5000}
        self.assertEqual(runner.validate_steps({"steps": [step]}), [step])
        with self.assertRaisesRegex(runner.ScenarioError, "route must match"):
            runner.validate_steps({"steps": [{**step, "route": "../../outside"}]})
        with self.assertRaisesRegex(runner.ScenarioError, "timeout_ms must be <="):
            runner.validate_steps({"steps": [{**step, "timeout_ms": runner.MAX_STEP_DELAY_MS + 1}]})


if __name__ == "__main__":
    unittest.main()
