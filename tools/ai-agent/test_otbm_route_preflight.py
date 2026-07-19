from __future__ import annotations

import copy
import hashlib
import json
import unittest

from otbm_route_preflight import PREFLIGHT_FORMAT, preflight_route_plan

MAP_SHA = "a" * 64
INDEX_SHA = "b" * 64
APPEARANCES_SHA = "c" * 64
INTERACTION_SHA = "d" * 64


def _rehash(plan: dict) -> dict:
    plan = copy.deepcopy(plan)
    plan.pop("planHashSha256", None)
    encoded = json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    plan["planHashSha256"] = hashlib.sha256(encoded).hexdigest()
    return plan


def _runtime_evidence(*, interaction: bool = False) -> dict[str, str | None]:
    return {
        "map": MAP_SHA,
        "worldIndex": INDEX_SHA,
        "appearances": APPEARANCES_SHA,
        "transitionManifest": None,
        "scriptResolution": None,
        "interactionRegistry": INTERACTION_SHA if interaction else None,
    }


def _movement_edge(source: list[int], target: list[int]) -> dict:
    return {
        "from": source,
        "to": target,
        "kind": "movement",
        "isTransition": False,
        "transitionId": None,
        "evidence": {
            "source": "reachability-bfs-predecessor",
            "edgeSource": "_movement_neighbors",
            "routingMode": "strict",
        },
    }


def _strict_plan() -> dict:
    plan = {
        "format": "canary-otbm-e2e-route-plan-v1",
        "schemaVersion": 1,
        "provenance": {
            "map": {"sha256": MAP_SHA},
            "worldIndex": {"sha256": INDEX_SHA},
            "appearances": {"sha256": APPEARANCES_SHA},
            "transitionManifest": None,
            "scriptResolution": None,
            "interactionRegistry": None,
        },
        "inputHashSha256": "e" * 64,
        "origin": [0, 0, 7],
        "destination": [2, 0, 7],
        "routingBounds": {"from": [0, 0, 7], "to": [2, 1, 7]},
        "routingOptions": {
            "allowDiagonal": False,
            "diagonalCornerCutting": False,
            "maxExecutablePositions": 10,
            "interactionAware": False,
        },
        "routeStatus": "confirmed",
        "executionStatus": "executable",
        "routingMode": "strict",
        "distance": 2,
        "strictDistance": 2,
        "optimisticDistance": 2,
        "executableDistance": None,
        "pathComplete": True,
        "path": [[0, 0, 7], [1, 0, 7], [2, 0, 7]],
        "edges": [
            _movement_edge([0, 0, 7], [1, 0, 7]),
            _movement_edge([1, 0, 7], [2, 0, 7]),
        ],
        "blockers": [],
    }
    return _rehash(plan)


def _transition_resolution(*, activation: str = "step-on", script_status: str | None = None) -> dict:
    query: dict = {
        "transitionId": "teleport:7",
        "transitionKind": "teleport",
        "transitionEvidenceSource": "worldIndex",
    }
    if script_status is not None:
        query["scriptStatus"] = script_status
    return {
        "format": "canary-otbm-route-interaction-resolution-v1",
        "schemaVersion": 1,
        "executionStatus": "executable",
        "selectorQuery": query,
        "matchedEntryId": "teleport-step-on",
        "matchedEntryIds": ["teleport-step-on"],
        "activation": {"kind": activation},
        "evidence": {"status": "reviewed", "references": ["fixture"]},
        "blockers": [],
    }


def _transition_plan() -> dict:
    transition = {
        "id": "teleport:7",
        "kind": "teleport",
        "origin": "world-index",
        "source": [1, 0, 7],
        "destination": [1, 0, 8],
        "itemId": 4,
        "expectedItemIds": [],
        "bidirectional": False,
        "uncertainties": [],
        "scriptStatus": None,
        "status": "confirmed",
        "valid": True,
        "strictEligible": True,
        "optimisticEligible": True,
        "issues": [],
    }
    plan = {
        "format": "canary-otbm-e2e-route-plan-v1",
        "schemaVersion": 1,
        "provenance": {
            "map": {"sha256": MAP_SHA},
            "worldIndex": {"sha256": INDEX_SHA},
            "appearances": {"sha256": APPEARANCES_SHA},
            "transitionManifest": None,
            "scriptResolution": None,
            "interactionRegistry": {"sha256": INTERACTION_SHA},
        },
        "inputHashSha256": "f" * 64,
        "origin": [0, 0, 7],
        "destination": [1, 0, 8],
        "routingBounds": {"from": [0, 0, 7], "to": [1, 0, 8]},
        "routingOptions": {
            "allowDiagonal": False,
            "diagonalCornerCutting": False,
            "maxExecutablePositions": 10,
            "interactionAware": True,
        },
        "routeStatus": "confirmed",
        "executionStatus": "executable",
        "routingMode": "executable",
        "distance": 2,
        "strictDistance": 2,
        "optimisticDistance": 2,
        "executableDistance": 2,
        "pathComplete": True,
        "path": [[0, 0, 7], [1, 0, 7], [1, 0, 8]],
        "edges": [
            {
                **_movement_edge([0, 0, 7], [1, 0, 7]),
                "evidence": {
                    "source": "reachability-bfs-predecessor",
                    "edgeSource": "_movement_neighbors",
                    "routingMode": "executable",
                },
                "interactions": [],
                "executionBlockers": [],
            },
            {
                "from": [1, 0, 7],
                "to": [1, 0, 8],
                "kind": "transition",
                "isTransition": True,
                "transitionId": "teleport:7",
                "evidence": {
                    "source": "validated-transition-edge",
                    "provenanceKey": "worldIndex",
                    "transition": transition,
                },
                "interactions": [_transition_resolution()],
                "executionBlockers": [],
            },
        ],
        "blockers": [],
    }
    return _rehash(plan)


def _landmark_registry(*, map_sha: str = MAP_SHA) -> dict:
    return {
        "format": "canary-otbm-semantic-landmarks-v1",
        "schemaVersion": 1,
        "registryStatus": "reviewed",
        "provenance": {
            "sourceMap": {"sha256": map_sha},
            "worldIndex": {"sha256": INDEX_SHA},
        },
        "regions": [
            {"id": "fixture.city", "bounds": {"from": [0, 0, 7], "to": [2, 1, 7]}},
        ],
        "landmarks": [
            {
                "id": "fixture.origin",
                "regionId": "fixture.city",
                "anchors": [
                    {
                        "id": "origin",
                        "role": "route-origin",
                        "position": [0, 0, 7],
                        "evidence": {"status": "reviewed", "references": ["fixture"]},
                    }
                ],
            },
            {
                "id": "fixture.destination",
                "regionId": "fixture.city",
                "anchors": [
                    {
                        "id": "destination",
                        "role": "route-destination",
                        "position": [2, 0, 7],
                        "evidence": {"status": "reviewed", "references": ["fixture"]},
                    }
                ],
            },
        ],
    }


def _landmark_request() -> dict:
    return {
        "from": {"landmarkId": "fixture.origin"},
        "to": {"landmarkId": "fixture.destination"},
    }


class RoutePreflightTests(unittest.TestCase):
    def test_exact_current_strict_plan_passes(self) -> None:
        plan = _strict_plan()
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence(), current_plan=copy.deepcopy(plan))
        self.assertEqual(result["format"], PREFLIGHT_FORMAT)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "passed")
        self.assertIsNone(result["firstBlocker"])
        self.assertTrue(result["staticEvidenceOnly"])

    def test_runtime_map_provenance_mismatch_fails_closed(self) -> None:
        plan = _strict_plan()
        evidence = _runtime_evidence()
        evidence["map"] = "0" * 64
        result = preflight_route_plan(plan, runtime_evidence=evidence, current_plan=copy.deepcopy(plan))
        self.assertFalse(result["ok"])
        self.assertEqual(result["firstBlocker"]["code"], "ROUTE_PROVENANCE_MISMATCH")

    def test_plan_hash_tamper_is_rejected(self) -> None:
        plan = _strict_plan()
        plan["destination"] = [1, 0, 7]
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence())
        self.assertFalse(result["ok"])
        self.assertEqual(result["firstBlocker"]["code"], "ROUTE_PLAN_HASH_MISMATCH")

    def test_non_adjacent_movement_is_rejected(self) -> None:
        plan = _strict_plan()
        plan["path"] = [[0, 0, 7], [2, 0, 7], [2, 0, 7]]
        plan["edges"][0]["to"] = [2, 0, 7]
        plan["edges"][1]["from"] = [2, 0, 7]
        plan = _rehash(plan)
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence())
        self.assertFalse(result["ok"])
        self.assertIn("MOVEMENT_EDGE_INVALID", result["summary"]["byCode"])

    def test_diagonal_edge_is_rejected_when_disabled(self) -> None:
        plan = _strict_plan()
        plan["destination"] = [1, 1, 7]
        plan["distance"] = 1
        plan["strictDistance"] = 1
        plan["optimisticDistance"] = 1
        plan["path"] = [[0, 0, 7], [1, 1, 7]]
        plan["edges"] = [_movement_edge([0, 0, 7], [1, 1, 7])]
        plan = _rehash(plan)
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence())
        self.assertFalse(result["ok"])
        self.assertIn("DIAGONAL_NOT_ALLOWED", result["summary"]["byCode"])

    def test_current_canonical_plan_detects_stale_transition(self) -> None:
        plan = _transition_plan()
        current = copy.deepcopy(plan)
        current["path"][2] = [2, 0, 8]
        current["destination"] = [2, 0, 8]
        current["edges"][1]["to"] = [2, 0, 8]
        current["edges"][1]["evidence"]["transition"]["destination"] = [2, 0, 8]
        current = _rehash(current)
        result = preflight_route_plan(
            plan,
            runtime_evidence=_runtime_evidence(interaction=True),
            current_plan=current,
        )
        self.assertFalse(result["ok"])
        self.assertIn("TRANSITION_STALE", result["summary"]["byCode"])

    def test_fail_closed_script_status_is_rejected(self) -> None:
        plan = _transition_plan()
        plan["edges"][1]["interactions"][0] = _transition_resolution(script_status="unresolved")
        plan = _rehash(plan)
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence(interaction=True))
        self.assertFalse(result["ok"])
        self.assertIn("SCRIPT_RESOLUTION_BLOCKED", result["summary"]["byCode"])

    def test_unsupported_activation_is_rejected(self) -> None:
        plan = _transition_plan()
        plan["edges"][1]["interactions"][0] = _transition_resolution(activation="teleport-magic")
        plan = _rehash(plan)
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence(interaction=True))
        self.assertFalse(result["ok"])
        self.assertIn("INTERACTION_UNSUPPORTED", result["summary"]["byCode"])

    def test_truncated_route_is_rejected(self) -> None:
        plan = _strict_plan()
        plan["pathComplete"] = False
        plan = _rehash(plan)
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence())
        self.assertFalse(result["ok"])
        self.assertIn("ROUTE_TRUNCATED", result["summary"]["byCode"])

    def test_current_route_blocked_by_unknown_evidence_is_rejected(self) -> None:
        plan = _strict_plan()
        current = copy.deepcopy(plan)
        current["executionStatus"] = "blocked"
        current["blockers"] = [{"code": "unknown-appearance"}]
        current = _rehash(current)
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence(), current_plan=current)
        self.assertFalse(result["ok"])
        self.assertIn("ROUTE_NOT_CURRENTLY_EXECUTABLE", result["summary"]["byCode"])

    def test_reviewed_landmark_request_resolves_exact_plan_endpoints(self) -> None:
        plan = _strict_plan()
        result = preflight_route_plan(
            plan,
            runtime_evidence={**_runtime_evidence(), "landmarkRegistry": "9" * 64},
            current_plan=copy.deepcopy(plan),
            landmark_registry=_landmark_registry(),
            landmark_request=_landmark_request(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["landmarkResolution"]["from"]["anchor"]["position"], [0, 0, 7])
        self.assertEqual(result["landmarkResolution"]["to"]["anchor"]["position"], [2, 0, 7])

    def test_stale_landmark_registry_provenance_fails_closed(self) -> None:
        plan = _strict_plan()
        result = preflight_route_plan(
            plan,
            runtime_evidence={**_runtime_evidence(), "landmarkRegistry": "9" * 64},
            landmark_registry=_landmark_registry(map_sha="8" * 64),
            landmark_request=_landmark_request(),
        )
        self.assertFalse(result["ok"])
        self.assertIn("LANDMARK_STALE", result["summary"]["byCode"])

    def test_current_plan_route_change_is_rejected_even_when_still_executable(self) -> None:
        plan = _strict_plan()
        current = copy.deepcopy(plan)
        current["path"] = [[0, 0, 7], [0, 1, 7], [1, 1, 7], [2, 1, 7], [2, 0, 7]]
        current["distance"] = 4
        current["strictDistance"] = 4
        current["optimisticDistance"] = 4
        current["edges"] = [
            _movement_edge([0, 0, 7], [0, 1, 7]),
            _movement_edge([0, 1, 7], [1, 1, 7]),
            _movement_edge([1, 1, 7], [2, 1, 7]),
            _movement_edge([2, 1, 7], [2, 0, 7]),
        ]
        current = _rehash(current)
        result = preflight_route_plan(plan, runtime_evidence=_runtime_evidence(), current_plan=current)
        self.assertFalse(result["ok"])
        self.assertIn("ROUTE_CURRENT_EVIDENCE_MISMATCH", result["summary"]["byCode"])

    def test_current_evidence_loader_error_is_reported_as_first_class_blocker(self) -> None:
        plan = _strict_plan()
        result = preflight_route_plan(
            plan,
            runtime_evidence=_runtime_evidence(),
            current_plan_error={
                "code": "WORLD_INDEX_MANIFEST_INVALID",
                "message": "fixture manifest mismatch",
            },
        )
        self.assertFalse(result["ok"])
        self.assertIn("WORLD_INDEX_MANIFEST_INVALID", result["summary"]["byCode"])


if __name__ == "__main__":
    unittest.main()
