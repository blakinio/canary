from __future__ import annotations

import copy
import unittest
from pathlib import Path

from otbm_route_interactions import (
    REGISTRY_FORMAT,
    RESOLUTION_FORMAT,
    RouteInteractionError,
    load_registry,
    resolve_interaction,
    validate_registry,
)

MAP_SHA256 = "1" * 64
WORLD_INDEX_SHA256 = "2" * 64
TRANSITION_MANIFEST_SHA256 = "3" * 64
SCRIPT_RESOLUTION_SHA256 = "4" * 64


def reviewed_registry() -> dict:
    return {
        "format": REGISTRY_FORMAT,
        "schemaVersion": 1,
        "registryStatus": "reviewed",
        "provenance": {
            "sourceMap": {"sha256": MAP_SHA256},
            "worldIndex": {"sha256": WORLD_INDEX_SHA256},
            "transitionManifest": {"sha256": TRANSITION_MANIFEST_SHA256},
            "scriptResolution": {"sha256": SCRIPT_RESOLUTION_SHA256},
        },
        "entries": [
            {
                "id": "fixture.teleport-step-on",
                "selector": {"transitionId": "teleport:fixture"},
                "activation": {"kind": "step-on"},
                "requirements": {
                    "transitionKinds": ["teleport"],
                    "transitionEvidenceSources": ["worldIndex"],
                    "scriptResolution": {"required": False, "allowedStatuses": []},
                },
                "evidence": {
                    "status": "reviewed",
                    "references": ["unit-test:engine-teleport"],
                },
            },
            {
                "id": "fixture.ladder-use",
                "selector": {"transitionId": "ladder:fixture"},
                "activation": {"kind": "use-map-item", "target": "transition-source"},
                "requirements": {
                    "transitionKinds": ["ladder"],
                    "transitionEvidenceSources": ["transitionManifest"],
                    "scriptResolution": {"required": False, "allowedStatuses": []},
                },
                "evidence": {
                    "status": "reviewed",
                    "references": ["unit-test:reviewed-ladder"],
                },
            },
            {
                "id": "fixture.aid-door",
                "selector": {
                    "position": [100, 100, 7],
                    "itemId": 1234,
                    "actionId": 45001,
                },
                "activation": {"kind": "use-map-item", "target": "selector-position"},
                "requirements": {
                    "transitionKinds": [],
                    "transitionEvidenceSources": [],
                    "scriptResolution": {
                        "required": True,
                        "allowedStatuses": ["handled-by-action-id"],
                    },
                },
                "evidence": {
                    "status": "reviewed",
                    "references": ["unit-test:aid-door"],
                },
            },
        ],
    }


class RouteInteractionRegistryTests(unittest.TestCase):
    def test_engine_teleport_resolves_to_step_on_deterministically(self) -> None:
        registry = reviewed_registry()
        first = resolve_interaction(
            registry,
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            transition_id="teleport:fixture",
            transition_kind="teleport",
            transition_evidence_source="worldIndex",
        )
        second = resolve_interaction(
            registry,
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            transition_id="teleport:fixture",
            transition_kind="teleport",
            transition_evidence_source="worldIndex",
        )

        self.assertEqual(first["format"], RESOLUTION_FORMAT)
        self.assertEqual(first["executionStatus"], "executable")
        self.assertEqual(first["activation"], {"kind": "step-on"})
        self.assertEqual(first["blockers"], [])
        self.assertEqual(first, second)

    def test_reviewed_ladder_requires_transition_manifest_provenance(self) -> None:
        blocked = resolve_interaction(
            reviewed_registry(),
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            transition_id="ladder:fixture",
            transition_kind="ladder",
            transition_evidence_source="transitionManifest",
        )
        self.assertEqual(blocked["executionStatus"], "blocked")
        self.assertEqual(blocked["blockers"], [{"code": "transition-manifest-provenance-required"}])

        resolved = resolve_interaction(
            reviewed_registry(),
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            expected_transition_manifest_sha256=TRANSITION_MANIFEST_SHA256,
            transition_id="ladder:fixture",
            transition_kind="ladder",
            transition_evidence_source="transitionManifest",
        )
        self.assertEqual(resolved["executionStatus"], "executable")
        self.assertEqual(resolved["activation"], {"kind": "use-map-item", "target": "transition-source"})

    def test_handler_gated_door_requires_allowed_script_status(self) -> None:
        resolved = resolve_interaction(
            reviewed_registry(),
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            expected_script_resolution_sha256=SCRIPT_RESOLUTION_SHA256,
            position=[100, 100, 7],
            item_id=1234,
            action_id=45001,
            script_status="handled-by-action-id",
        )
        self.assertEqual(resolved["executionStatus"], "executable")
        self.assertEqual(resolved["matchedEntryId"], "fixture.aid-door")
        self.assertEqual(resolved["activation"], {"kind": "use-map-item", "target": "selector-position"})

    def test_unresolved_and_conflicting_script_evidence_fail_closed(self) -> None:
        for status in ("unresolved", "partially-resolved", "referenced-only", "conflicting"):
            with self.subTest(status=status):
                result = resolve_interaction(
                    reviewed_registry(),
                    expected_source_map_sha256=MAP_SHA256,
                    expected_world_index_sha256=WORLD_INDEX_SHA256,
                    expected_script_resolution_sha256=SCRIPT_RESOLUTION_SHA256,
                    position=[100, 100, 7],
                    item_id=1234,
                    action_id=45001,
                    script_status=status,
                )
                self.assertEqual(result["executionStatus"], "blocked")
                self.assertIsNone(result["activation"])
                self.assertEqual(
                    result["blockers"],
                    [{"code": "script-status-fail-closed", "status": status}],
                )

    def test_script_resolution_provenance_and_status_are_required_for_door(self) -> None:
        result = resolve_interaction(
            reviewed_registry(),
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            position=[100, 100, 7],
            item_id=1234,
            action_id=45001,
        )
        self.assertEqual(result["executionStatus"], "blocked")
        self.assertEqual(
            result["blockers"],
            [
                {"code": "script-resolution-provenance-required"},
                {"code": "script-status-required"},
            ],
        )

    def test_unknown_door_or_barrier_is_not_silently_usable(self) -> None:
        result = resolve_interaction(
            reviewed_registry(),
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            position=[101, 100, 7],
            item_id=9999,
            action_id=45002,
            script_status="handled-by-action-id",
            expected_script_resolution_sha256=SCRIPT_RESOLUTION_SHA256,
        )
        self.assertEqual(result["executionStatus"], "blocked")
        self.assertEqual(result["matchedEntryId"], None)
        self.assertEqual(result["blockers"], [{"code": "interaction-not-reviewed"}])

    def test_transition_kind_and_evidence_source_must_match_reviewed_contract(self) -> None:
        result = resolve_interaction(
            reviewed_registry(),
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            transition_id="teleport:fixture",
            transition_kind="ladder",
            transition_evidence_source="transitionManifest",
            expected_transition_manifest_sha256=TRANSITION_MANIFEST_SHA256,
        )
        self.assertEqual(result["executionStatus"], "blocked")
        self.assertEqual(
            result["blockers"],
            [
                {"code": "transition-kind-not-allowed", "actual": "ladder", "allowed": ["teleport"]},
                {
                    "code": "transition-evidence-source-not-allowed",
                    "actual": "transitionManifest",
                    "allowed": ["worldIndex"],
                },
            ],
        )

    def test_rejects_duplicate_exact_selectors(self) -> None:
        registry = reviewed_registry()
        duplicate = copy.deepcopy(registry["entries"][0])
        duplicate["id"] = "fixture.teleport-step-on-duplicate"
        registry["entries"].append(duplicate)
        with self.assertRaisesRegex(RouteInteractionError, "Duplicate route interaction selector"):
            validate_registry(registry)

    def test_overlapping_mechanic_selectors_fail_closed_as_ambiguous(self) -> None:
        registry = reviewed_registry()
        registry["entries"].append(
            {
                "id": "fixture.item-door-broad",
                "selector": {"position": [100, 100, 7], "itemId": 1234},
                "activation": {"kind": "use-map-item", "target": "selector-position"},
                "requirements": {
                    "transitionKinds": [],
                    "transitionEvidenceSources": [],
                    "scriptResolution": {"required": False, "allowedStatuses": []},
                },
                "evidence": {"status": "reviewed", "references": ["unit-test:broad-overlap"]},
            }
        )
        result = resolve_interaction(
            registry,
            expected_source_map_sha256=MAP_SHA256,
            expected_world_index_sha256=WORLD_INDEX_SHA256,
            expected_script_resolution_sha256=SCRIPT_RESOLUTION_SHA256,
            position=[100, 100, 7],
            item_id=1234,
            action_id=45001,
            script_status="handled-by-action-id",
        )
        self.assertEqual(result["executionStatus"], "blocked")
        self.assertEqual(result["blockers"][0]["code"], "interaction-selector-ambiguous")
        self.assertEqual(
            result["matchedEntryIds"],
            ["fixture.aid-door", "fixture.item-door-broad"],
        )

    def test_rejects_stale_exact_provenance(self) -> None:
        with self.assertRaisesRegex(RouteInteractionError, "source-map SHA-256"):
            resolve_interaction(
                reviewed_registry(),
                expected_source_map_sha256="5" * 64,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
                transition_id="teleport:fixture",
                transition_kind="teleport",
                transition_evidence_source="worldIndex",
            )
        with self.assertRaisesRegex(RouteInteractionError, "transition-manifest SHA-256"):
            resolve_interaction(
                reviewed_registry(),
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
                expected_transition_manifest_sha256="6" * 64,
                transition_id="ladder:fixture",
                transition_kind="ladder",
                transition_evidence_source="transitionManifest",
            )
        with self.assertRaisesRegex(RouteInteractionError, "script-resolution SHA-256"):
            resolve_interaction(
                reviewed_registry(),
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
                expected_script_resolution_sha256="7" * 64,
                position=[100, 100, 7],
                item_id=1234,
                action_id=45001,
                script_status="handled-by-action-id",
            )

    def test_committed_seed_is_unbound_and_empty(self) -> None:
        seed = load_registry(Path("docs/ai-agent/OTBM_ROUTE_INTERACTIONS.json"))
        self.assertEqual(seed["registryStatus"], "unbound")
        self.assertIsNone(seed["provenance"])
        self.assertEqual(seed["entries"], [])
        with self.assertRaisesRegex(RouteInteractionError, "unbound"):
            resolve_interaction(
                seed,
                expected_source_map_sha256=MAP_SHA256,
                expected_world_index_sha256=WORLD_INDEX_SHA256,
                transition_id="teleport:fixture",
                transition_kind="teleport",
                transition_evidence_source="worldIndex",
            )

    def test_rejects_broad_mechanic_selector_and_unsafe_allowed_status(self) -> None:
        registry = reviewed_registry()
        registry["entries"][2]["selector"] = {"position": [100, 100, 7]}
        with self.assertRaisesRegex(RouteInteractionError, "at least one of itemId"):
            validate_registry(registry)

        registry = reviewed_registry()
        registry["entries"][2]["requirements"]["scriptResolution"]["allowedStatuses"] = ["unresolved"]
        with self.assertRaisesRegex(RouteInteractionError, "unsupported"):
            validate_registry(registry)

    def test_rejects_unreviewed_evidence_and_invalid_activation_selector_pair(self) -> None:
        registry = reviewed_registry()
        registry["entries"][0]["evidence"]["status"] = "guessed"
        with self.assertRaisesRegex(RouteInteractionError, "status must be reviewed"):
            validate_registry(registry)

        registry = reviewed_registry()
        registry["entries"][2]["activation"] = {"kind": "step-on"}
        with self.assertRaisesRegex(RouteInteractionError, "requires a transitionId selector"):
            validate_registry(registry)


if __name__ == "__main__":
    unittest.main()
