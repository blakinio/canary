from __future__ import annotations

import copy
import unittest
from dataclasses import dataclass

from otbm_identifier_integrity import (
    IdentifierIntegrityError,
    build_identifier_integrity_report,
    validate_policy,
)

MAP_SHA = "a" * 64
INDEX_SHA = "b" * 64
SCRIPT_SHA = "c" * 64
TRANSITION_SHA = "d" * 64
INTERACTION_SHA = "e" * 64


@dataclass
class _Header:
    mechanic_count: int


@dataclass
class _Tile:
    house_id: int | None = None


class _Index:
    def __init__(self) -> None:
        self._placements = [
            {"placementOrdinal": 0, "itemId": 1000, "position": [10, 10, 7], "tileIndex": 0, "actionId": 100},
            {"placementOrdinal": 1, "itemId": 1001, "position": [11, 10, 7], "tileIndex": 1, "actionId": 100},
            {"placementOrdinal": 2, "itemId": 1002, "position": [12, 10, 7], "tileIndex": 2, "uniqueId": 200},
            {"placementOrdinal": 3, "itemId": 1003, "position": [13, 10, 7], "tileIndex": 3, "uniqueId": 200},
            {"placementOrdinal": 4, "itemId": 1004, "position": [20, 20, 7], "tileIndex": 4, "houseDoorId": 3},
            {"placementOrdinal": 5, "itemId": 1005, "position": [20, 21, 7], "tileIndex": 5, "houseDoorId": 3},
        ]
        self._tiles = [_Tile(), _Tile(), _Tile(), _Tile(), _Tile(7), _Tile(7)]
        self.header = _Header(len(self._placements))

    def mechanic_record(self, mechanic_index: int):
        return mechanic_index, {}

    def placement(self, ordinal: int):
        return copy.deepcopy(self._placements[ordinal])

    def tile(self, tile_index: int):
        return self._tiles[tile_index]


def _review() -> dict:
    return {"status": "reviewed", "references": ["fixture-review"]}


def _policy(*, expectations: list[dict] | None = None, roles: list[dict] | None = None, script=False, transitions=False, interactions=False) -> dict:
    return {
        "format": "canary-otbm-identifier-integrity-policy-v1",
        "schemaVersion": 1,
        "provenance": {
            "sourceMap": {"sha256": MAP_SHA},
            "worldIndex": {"sha256": INDEX_SHA},
            "scriptResolution": {"sha256": SCRIPT_SHA} if script else None,
            "transitionManifest": {"sha256": TRANSITION_SHA} if transitions else None,
            "interactionRegistry": {"sha256": INTERACTION_SHA} if interactions else None,
        },
        "expectations": expectations or [],
        "placementRoles": roles or [],
    }


def _expectation(identifier: str, namespace: str, value: int, expectation: str, scope: dict | None = None) -> dict:
    return {
        "id": identifier,
        "namespace": namespace,
        "value": value,
        "scope": scope or {"kind": "world"},
        "expectation": expectation,
        "evidence": _review(),
    }


def _script_resolution(status: str = "conflicting") -> dict:
    return {
        "format": "canary-otbm-script-resolution-v1",
        "identifiers": {
            "actionId": [
                {
                    "value": 100,
                    "placements": 2,
                    "status": status,
                    "handlers": [{"handler": "fixture"}],
                    "samplePositions": [[10, 10, 7], [11, 10, 7]],
                }
            ],
            "uniqueId": [],
        },
    }


def _transitions_duplicate() -> dict:
    return {
        "format": "canary-otbm-transition-manifest-v1",
        "transitions": [
            {
                "id": "fixture.stairs",
                "kind": "stairs",
                "source": [10, 10, 7],
                "destination": [10, 10, 6],
            },
            {
                "id": "fixture.stairs",
                "kind": "stairs",
                "source": [11, 10, 7],
                "destination": [11, 10, 6],
            },
        ],
    }


def _interaction_entry(entry_id: str, selector: dict) -> dict:
    return {
        "id": entry_id,
        "selector": selector,
        "activation": {"kind": "use-map-item", "target": "selector-position"},
        "requirements": {
            "transitionKinds": [],
            "transitionEvidenceSources": [],
            "scriptResolution": {"required": False, "allowedStatuses": []},
        },
        "evidence": _review(),
    }


def _interactions_overlap() -> dict:
    return {
        "format": "canary-otbm-route-interactions-v1",
        "schemaVersion": 1,
        "registryStatus": "reviewed",
        "provenance": {
            "sourceMap": {"sha256": MAP_SHA},
            "worldIndex": {"sha256": INDEX_SHA},
            "transitionManifest": None,
            "scriptResolution": None,
        },
        "entries": [
            _interaction_entry("broad", {"position": [10, 10, 7], "itemId": 1000}),
            _interaction_entry("narrow", {"position": [10, 10, 7], "itemId": 1000, "actionId": 100}),
        ],
    }


class IdentifierIntegrityTests(unittest.TestCase):
    def _build(self, **overrides):
        values = {
            "policy": _policy(),
            "world_index": _Index(),
            "source_map_sha256": MAP_SHA,
            "actual_world_index_sha256": INDEX_SHA,
        }
        values.update(overrides)
        return build_identifier_integrity_report(**values)

    def test_repeated_aid_without_policy_is_review_required_not_conflict(self) -> None:
        report = self._build()
        action = next(entry for entry in report["reviewRequired"] if entry["namespace"] == "actionId")
        self.assertEqual(action["value"], 100)
        self.assertEqual(action["classification"], "review-required")
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["conflicts"], 0)

    def test_reviewed_unique_expectation_violation_is_conflicting(self) -> None:
        policy = _policy(expectations=[_expectation("aid-100-unique", "actionId", 100, "unique")])
        report = self._build(policy=policy)
        result = report["expectations"][0]
        self.assertEqual(result["placementCount"], 2)
        self.assertEqual(result["classification"], "conflicting")
        self.assertFalse(report["ok"])

    def test_reviewed_reuse_is_not_conflict(self) -> None:
        policy = _policy(expectations=[_expectation("aid-100-reuse", "actionId", 100, "reviewed-reuse")])
        report = self._build(policy=policy)
        self.assertEqual(report["expectations"][0]["classification"], "reviewed-reuse")
        self.assertTrue(report["ok"])
        self.assertFalse(any(entry["namespace"] == "actionId" for entry in report["reviewRequired"]))

    def test_house_door_uniqueness_is_scoped_by_house(self) -> None:
        policy = _policy(
            expectations=[
                _expectation(
                    "house-seven-door-three",
                    "houseDoorId",
                    3,
                    "unique",
                    {"kind": "house", "houseId": 7},
                )
            ]
        )
        report = self._build(policy=policy)
        self.assertEqual(report["expectations"][0]["classification"], "conflicting")
        self.assertEqual(report["expectations"][0]["placementCount"], 2)

    def test_existing_script_resolution_conflict_is_preserved(self) -> None:
        report = self._build(
            policy=_policy(script=True),
            script_resolution=_script_resolution(),
            script_resolution_sha256=SCRIPT_SHA,
        )
        self.assertEqual(report["summary"]["scriptConflicts"], 1)
        self.assertEqual(report["scriptConflicts"][0]["status"], "conflicting")
        self.assertFalse(report["ok"])

    def test_duplicate_transition_id_is_conflicting(self) -> None:
        report = self._build(
            policy=_policy(transitions=True),
            transition_manifest=_transitions_duplicate(),
            transition_manifest_sha256=TRANSITION_SHA,
        )
        self.assertEqual(report["summary"]["transitionConflicts"], 1)
        self.assertEqual(report["transitionConflicts"][0]["reason"], "duplicate-transition-id-incompatible")
        self.assertFalse(report["ok"])

    def test_non_identical_overlapping_interaction_selectors_are_ambiguous(self) -> None:
        report = self._build(
            policy=_policy(interactions=True),
            interaction_registry=_interactions_overlap(),
            interaction_registry_sha256=INTERACTION_SHA,
        )
        self.assertEqual(report["summary"]["selectorAmbiguities"], 1)
        self.assertEqual(report["selectorAmbiguities"][0]["entryIds"], ["broad", "narrow"])
        self.assertEqual(report["selectorAmbiguities"][0]["witnessQuery"]["actionId"], 100)
        self.assertFalse(report["ok"])

    def test_reviewed_incompatible_roles_require_exact_placement_match(self) -> None:
        roles = [
            {
                "id": "role-a",
                "placementOrdinal": 0,
                "namespace": "actionId",
                "value": 100,
                "role": "lever",
                "compatibilityClass": "lever-family",
                "evidence": _review(),
            },
            {
                "id": "role-b",
                "placementOrdinal": 1,
                "namespace": "actionId",
                "value": 100,
                "role": "quest-door",
                "compatibilityClass": "door-family",
                "evidence": _review(),
            },
        ]
        report = self._build(policy=_policy(roles=roles))
        self.assertEqual(report["summary"]["roleConflicts"], 1)
        self.assertFalse(report["ok"])

    def test_provenance_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(IdentifierIntegrityError, "World Index SHA-256"):
            self._build(actual_world_index_sha256="f" * 64)

    def test_house_door_policy_requires_house_scope(self) -> None:
        policy = _policy(expectations=[_expectation("door", "houseDoorId", 3, "unique")])
        with self.assertRaisesRegex(IdentifierIntegrityError, "scope must be house"):
            validate_policy(policy)


if __name__ == "__main__":
    unittest.main()
