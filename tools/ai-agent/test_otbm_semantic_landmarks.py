from __future__ import annotations

import copy
import unittest
from pathlib import Path

from otbm_semantic_landmarks import (
    REGISTRY_FORMAT,
    RESOLUTION_FORMAT,
    SemanticLandmarkError,
    load_registry,
    resolve_landmark_anchor,
    validate_registry,
)

MAP_SHA256 = "1" * 64
WORLD_INDEX_SHA256 = "2" * 64


def reviewed_registry() -> dict:
    return {
        "format": REGISTRY_FORMAT,
        "schemaVersion": 1,
        "registryStatus": "reviewed",
        "provenance": {
            "sourceMap": {"sha256": MAP_SHA256},
            "worldIndex": {"sha256": WORLD_INDEX_SHA256},
        },
        "regions": [
            {
                "id": "fixture.central",
                "bounds": {
                    "from": [100, 200, 7],
                    "to": [120, 220, 8],
                },
            }
        ],
        "landmarks": [
            {
                "id": "fixture.origin",
                "regionId": "fixture.central",
                "anchors": [
                    {
                        "id": "west",
                        "role": "route-origin",
                        "position": [101, 201, 7],
                        "evidence": {
                            "status": "reviewed",
                            "references": ["unit-test:fixture-origin"],
                        },
                    }
                ],
            },
            {
                "id": "fixture.destination",
                "regionId": "fixture.central",
                "anchors": [
                    {
                        "id": "east",
                        "role": "route-destination",
                        "position": [119, 219, 7],
                        "evidence": {
                            "status": "reviewed",
                            "references": ["unit-test:fixture-destination"],
                        },
                    },
                    {
                        "id": "entrance",
                        "role": "entrance",
                        "position": [118, 219, 7],
                        "evidence": {
                            "status": "reviewed",
                            "references": ["unit-test:fixture-entrance"],
                            "note": "Synthetic unit-test evidence only.",
                        },
                    },
                ],
            },
        ],
    }


class SemanticLandmarkRegistryTests(unittest.TestCase):
    def test_resolves_two_reviewed_landmarks_deterministically(self) -> None:
        registry = reviewed_registry()
        origin = resolve_landmark_anchor(
            registry,
            landmark_id="fixture.origin",
            role="route-origin",
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
        )
        destination = resolve_landmark_anchor(
            registry,
            landmark_id="fixture.destination",
            anchor_id="east",
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
        )
        repeated = resolve_landmark_anchor(
            registry,
            landmark_id="fixture.destination",
            anchor_id="east",
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
        )

        self.assertEqual(origin["format"], RESOLUTION_FORMAT)
        self.assertEqual(origin["anchor"]["position"], [101, 201, 7])
        self.assertEqual(destination["anchor"]["position"], [119, 219, 7])
        self.assertEqual(destination["routingBounds"], {"from": [100, 200, 7], "to": [120, 220, 8]})
        self.assertEqual(destination, repeated)

    def test_committed_seed_is_unbound_and_empty(self) -> None:
        seed = load_registry(Path("docs/ai-agent/OTBM_SEMANTIC_LANDMARKS.json"))
        self.assertEqual(seed["registryStatus"], "unbound")
        self.assertIsNone(seed["provenance"])
        self.assertEqual(seed["regions"], [])
        self.assertEqual(seed["landmarks"], [])
        with self.assertRaisesRegex(SemanticLandmarkError, "unbound"):
            resolve_landmark_anchor(
                seed,
                landmark_id="fixture.origin",
                role="route-origin",
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
            )

    def test_rejects_duplicate_region_ids(self) -> None:
        registry = reviewed_registry()
        registry["regions"].append(copy.deepcopy(registry["regions"][0]))
        with self.assertRaisesRegex(SemanticLandmarkError, "Duplicate semantic landmark region ID"):
            validate_registry(registry)

    def test_rejects_duplicate_landmark_ids(self) -> None:
        registry = reviewed_registry()
        registry["landmarks"].append(copy.deepcopy(registry["landmarks"][0]))
        with self.assertRaisesRegex(SemanticLandmarkError, "Duplicate semantic landmark ID"):
            validate_registry(registry)

    def test_rejects_duplicate_anchor_ids_within_landmark(self) -> None:
        registry = reviewed_registry()
        duplicate = copy.deepcopy(registry["landmarks"][1]["anchors"][0])
        registry["landmarks"][1]["anchors"].append(duplicate)
        with self.assertRaisesRegex(SemanticLandmarkError, "duplicate anchor ID"):
            validate_registry(registry)

    def test_rejects_invalid_inclusive_bounds(self) -> None:
        registry = reviewed_registry()
        registry["regions"][0]["bounds"] = {"from": [120, 200, 7], "to": [100, 220, 8]}
        with self.assertRaisesRegex(SemanticLandmarkError, "inclusive lower-to-upper"):
            validate_registry(registry)

    def test_enforces_reachability_region_coordinate_bound(self) -> None:
        registry = reviewed_registry()
        registry["regions"][0]["bounds"] = {"from": [0, 0, 7], "to": [999, 999, 7]}
        validate_registry(registry)

        registry["regions"][0]["bounds"] = {"from": [0, 0, 7], "to": [1000, 999, 7]}
        with self.assertRaisesRegex(SemanticLandmarkError, "Reachability maximum is 1000000"):
            validate_registry(registry)

    def test_rejects_anchor_outside_declared_region(self) -> None:
        registry = reviewed_registry()
        registry["landmarks"][0]["anchors"][0]["position"] = [121, 201, 7]
        with self.assertRaisesRegex(SemanticLandmarkError, "outside region fixture.central"):
            validate_registry(registry)

    def test_rejects_unknown_region_reference(self) -> None:
        registry = reviewed_registry()
        registry["landmarks"][0]["regionId"] = "fixture.missing"
        with self.assertRaisesRegex(SemanticLandmarkError, "unknown region fixture.missing"):
            validate_registry(registry)

    def test_rejects_stale_source_map_provenance(self) -> None:
        with self.assertRaisesRegex(SemanticLandmarkError, "source-map SHA-256"):
            resolve_landmark_anchor(
                reviewed_registry(),
                landmark_id="fixture.origin",
                role="route-origin",
                expected_source_map_sha256="3" * 64,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
            )

    def test_rejects_stale_world_index_provenance(self) -> None:
        with self.assertRaisesRegex(SemanticLandmarkError, "World Index SHA-256"):
            resolve_landmark_anchor(
                reviewed_registry(),
                landmark_id="fixture.origin",
                role="route-origin",
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256="4" * 64,
            )

    def test_rejects_unknown_landmark_and_anchor_ids(self) -> None:
        with self.assertRaisesRegex(SemanticLandmarkError, "Unknown semantic landmark ID"):
            resolve_landmark_anchor(
                reviewed_registry(),
                landmark_id="fixture.missing",
                role="route-origin",
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
            )
        with self.assertRaisesRegex(SemanticLandmarkError, "has no anchor missing"):
            resolve_landmark_anchor(
                reviewed_registry(),
                landmark_id="fixture.destination",
                anchor_id="missing",
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
            )

    def test_role_resolution_fails_closed_when_ambiguous(self) -> None:
        registry = reviewed_registry()
        second = copy.deepcopy(registry["landmarks"][1]["anchors"][0])
        second["id"] = "east-alternate"
        registry["landmarks"][1]["anchors"].append(second)
        with self.assertRaisesRegex(SemanticLandmarkError, "ambiguous role route-destination"):
            resolve_landmark_anchor(
                registry,
                landmark_id="fixture.destination",
                role="route-destination",
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
            )

    def test_rejects_unreviewed_evidence_and_unknown_fields(self) -> None:
        registry = reviewed_registry()
        registry["landmarks"][0]["anchors"][0]["evidence"]["status"] = "guessed"
        with self.assertRaisesRegex(SemanticLandmarkError, "status must be reviewed"):
            validate_registry(registry)

        registry = reviewed_registry()
        registry["landmarks"][0]["guess"] = True
        with self.assertRaisesRegex(SemanticLandmarkError, "unknown fields: guess"):
            validate_registry(registry)

    def test_rejects_invalid_hashes_and_requires_exact_selector(self) -> None:
        with self.assertRaisesRegex(SemanticLandmarkError, "64-character SHA-256"):
            resolve_landmark_anchor(
                reviewed_registry(),
                landmark_id="fixture.origin",
                role="route-origin",
                expected_source_map_sha256="not-a-hash",
                expected_world_index_sha256=WORLD_INDEX_SHA256,
            )
        with self.assertRaisesRegex(SemanticLandmarkError, "Exactly one"):
            resolve_landmark_anchor(
                reviewed_registry(),
                landmark_id="fixture.origin",
                role="route-origin",
                anchor_id="west",
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
            )


if __name__ == "__main__":
    unittest.main()
