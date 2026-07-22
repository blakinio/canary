from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass

from otbm_critical_access_integrity import (
    CriticalAccessIntegrityError,
    build_critical_access_report,
    validate_target_manifest,
)

MAP_SHA = "a" * 64
INDEX_SHA = "b" * 64


@dataclass
class _Tile:
    kind: str = "house"
    house_id: int | None = 7
    placement_start: int = 0
    placement_count: int = 1


class _Index:
    def __init__(self, *, placement: dict | None = None, tile: _Tile | None = None) -> None:
        self._placement = placement or {
            "placementOrdinal": 0,
            "itemId": 1223,
            "position": [20, 20, 7],
            "houseDoorId": 3,
        }
        self._tile = tile or _Tile()

    def find_tile(self, position: tuple[int, int, int]):
        if position != (20, 20, 7):
            return None
        return 12, self._tile

    def placement(self, ordinal: int):
        if ordinal != 0:
            raise AssertionError(ordinal)
        return copy.deepcopy(self._placement)


def _review() -> dict:
    return {"status": "reviewed", "references": ["fixture-review"]}


def _manifest() -> dict:
    return {
        "format": "canary-otbm-critical-access-targets-v1",
        "schemaVersion": 1,
        "provenance": {
            "sourceMap": {"sha256": MAP_SHA},
            "worldIndex": {"sha256": INDEX_SHA},
        },
        "targets": {
            "criticalLandmarks": [
                {
                    "id": "critical-depot",
                    "criticality": "depot",
                    "landmarkId": "fixture.depot",
                    "anchorId": "destination",
                    "routeId": "landmark-route",
                    "review": _review(),
                }
            ],
            "houses": [
                {
                    "id": "house-seven",
                    "houseId": 7,
                    "houseDoorId": 3,
                    "doorPosition": [20, 20, 7],
                    "interiorPosition": [20, 21, 7],
                    "routeId": "house-route",
                    "review": _review(),
                }
            ],
            "spawnAccess": [
                {
                    "id": "boss-access",
                    "entityRole": "boss",
                    "placementId": "spawn-1",
                    "position": [30, 30, 7],
                    "routeId": "spawn-route",
                    "accessExpectation": "public",
                    "review": _review(),
                }
            ],
        },
    }


def _landmarks() -> dict:
    return {
        "format": "canary-otbm-semantic-landmarks-v1",
        "schemaVersion": 1,
        "registryStatus": "reviewed",
        "provenance": {
            "sourceMap": {"sha256": MAP_SHA},
            "worldIndex": {"sha256": INDEX_SHA},
        },
        "regions": [
            {"id": "fixture-region", "bounds": {"from": [1, 1, 7], "to": [40, 40, 7]}}
        ],
        "landmarks": [
            {
                "id": "fixture.depot",
                "regionId": "fixture-region",
                "anchors": [
                    {
                        "id": "destination",
                        "role": "route-destination",
                        "position": [10, 10, 7],
                        "evidence": _review(),
                    }
                ],
            }
        ],
    }


def _route(route_id: str, goal: list[int], path: list[list[int]], mode: str = "strict") -> dict:
    return {
        "id": route_id,
        "start": [1, 1, 7],
        "goal": goal,
        "mode": mode,
        "reachable": True,
        "distance": len(path) - 1,
        "conditionalOnly": mode == "optimistic",
        "baselinePath": path,
        "baselineEdges": [],
        "criticalEdges": [],
        "alternativePath": None,
        "alternativeEdgeDisjoint": False,
        "classification": "resilient" if mode != "optimistic" else "conditional",
    }


def _connectivity() -> dict:
    return {
        "format": "canary-otbm-connectivity-resilience-v1",
        "source": {"mapSha256": MAP_SHA, "worldIndexSha256": INDEX_SHA},
        "routes": [
            _route("landmark-route", [10, 10, 7], [[1, 1, 7], [10, 10, 7]]),
            _route("house-route", [20, 21, 7], [[19, 20, 7], [20, 20, 7], [20, 21, 7]], "executable"),
            _route("spawn-route", [30, 30, 7], [[29, 30, 7], [30, 30, 7]]),
        ],
    }


def _geometry() -> dict:
    return {
        "format": "canary-otbm-geometry-audit-v1",
        "complete": True,
        "provenance": {
            "source": {"sha256": MAP_SHA},
            "index": {"sha256": INDEX_SHA},
        },
        "summary": {"findings": {"truncated": False}},
        "findings": [],
    }


def _spawn() -> dict:
    return {
        "format": "canary-otbm-spawn-npc-validation-v1",
        "provenance": {"worldIndex": {"sha256": INDEX_SHA}},
        "placementsTruncated": False,
        "placements": [
            {
                "id": "spawn-1",
                "kind": "monster",
                "name": "Fixture Boss",
                "position": [30, 30, 7],
                "rewardBossLiteral": True,
                "status": "confirmed",
            }
        ],
    }


class CriticalAccessIntegrityTests(unittest.TestCase):
    def _build(self, **overrides):
        values = {
            "manifest": _manifest(),
            "landmark_registry": _landmarks(),
            "connectivity_report": _connectivity(),
            "geometry_report": _geometry(),
            "spawn_validation_report": _spawn(),
            "world_index": _Index(),
            "actual_world_index_sha256": INDEX_SHA,
        }
        values.update(overrides)
        return build_critical_access_report(**values)

    def test_confirmed_reviewed_targets_reuse_existing_evidence(self) -> None:
        report = self._build()
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["classifications"]["confirmed"], 3)
        self.assertEqual(report["criticalLandmarks"][0]["classification"], "confirmed")
        self.assertEqual(report["houses"][0]["doorEvidence"]["status"], "confirmed")
        self.assertEqual(report["houses"][0]["routeEvidence"]["mode"], "executable")
        self.assertEqual(report["spawnAccess"][0]["classification"], "confirmed")
        self.assertTrue(report["spawnAccess"][0]["intendedPublicAccessibilityDeclared"])
        self.assertFalse(report["spawnAccess"][0]["intendedPublicAccessibilityProven"])
        self.assertFalse(report["policy"]["pathfindingPerformed"])
        self.assertFalse(report["policy"]["runtimeAccessClaimed"])

    def test_geometry_house_finding_remains_review_required(self) -> None:
        geometry = _geometry()
        geometry["findings"] = [
            {
                "id": "finding-1",
                "kind": "house-disconnected-components",
                "houseId": 7,
                "severity": "warning",
            }
        ]
        report = self._build(geometry_report=geometry)
        self.assertEqual(report["houses"][0]["classification"], "review-required")
        self.assertEqual(report["houses"][0]["geometryEvidence"]["status"], "review-required")
        self.assertTrue(report["ok"])

    def test_missing_spawn_id_in_truncated_report_fails_closed(self) -> None:
        spawn = _spawn()
        spawn["placements"] = []
        spawn["placementsTruncated"] = True
        report = self._build(spawn_validation_report=spawn)
        result = report["spawnAccess"][0]
        self.assertEqual(result["classification"], "unresolved")
        self.assertEqual(
            result["placementEvidence"]["reason"],
            "placement-id-not-visible-in-truncated-report",
        )
        self.assertFalse(report["ok"])

    def test_house_route_must_cross_exact_reviewed_door_position(self) -> None:
        connectivity = _connectivity()
        house_route = next(entry for entry in connectivity["routes"] if entry["id"] == "house-route")
        house_route["baselinePath"] = [[19, 21, 7], [20, 21, 7]]
        report = self._build(connectivity_report=connectivity)
        self.assertEqual(report["houses"][0]["classification"], "conflicting")
        self.assertEqual(
            report["houses"][0]["routeEvidence"]["reason"],
            "required-position-not-on-proven-route",
        )
        self.assertFalse(report["ok"])

    def test_world_index_provenance_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(CriticalAccessIntegrityError, "World Index file SHA-256"):
            self._build(actual_world_index_sha256="c" * 64)

    def test_target_manifest_rejects_unreviewed_criticality(self) -> None:
        manifest = _manifest()
        manifest["targets"]["criticalLandmarks"][0]["review"]["status"] = "draft"
        with self.assertRaisesRegex(CriticalAccessIntegrityError, "must be reviewed"):
            validate_target_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
