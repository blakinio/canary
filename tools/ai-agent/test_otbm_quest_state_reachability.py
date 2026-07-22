from __future__ import annotations

import copy
import unittest

from otbm_quest_state_reachability import (
    INTERACTION_REGISTRY_FORMAT,
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    STORAGE_GRAPH_FORMAT,
    QuestStateReachabilityError,
    build_quest_state_reachability_report,
    canonical_report_sha256,
)


def sha(char: str) -> str:
    return char * 64


def pin(name: str, digest: str, fmt: str) -> dict:
    return {"fileName": name, "size": 123, "sha256": digest, "format": fmt}


def transition(transition_id: str, before: int, after: int, *, context: dict | None = None) -> dict:
    return {
        "id": transition_id,
        "namespace": "player-storage",
        "key": "Storage.Quest.Demo.Stage",
        "prerequisite": {"operator": "==", "value": before},
        "result": {"kind": "literal", "value": after},
        "mapContext": [context or {"position": [100, 100, 7], "actionId": 45001}],
        "issues": [],
    }


def fixtures():
    t1 = "1" * 20
    t2 = "2" * 20
    storage = {
        "format": STORAGE_GRAPH_FORMAT,
        "schemaVersion": 1,
        "complete": True,
        "inputs": {
            "questEvidence": {"path": "quest.json", "sha256": sha("a"), "format": "canary-quest-map-evidence-v1"},
            "questValidation": {"path": "validation.json", "sha256": sha("b"), "format": "canary-quest-map-validation-v1"},
            "spawnNpcEvidence": None,
            "spawnNpcValidation": None,
            "reachability": None,
        },
        "transitions": [transition(t1, 0, 1), transition(t2, 1, 2)],
    }
    manifest = {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "source": {"mapSha256": sha("c"), "worldIndexSha256": sha("d")},
        "targets": [
            {
                "id": "quest.demo",
                "kind": "quest",
                "reason": "Reviewed demo state chain",
                "initialStates": [
                    {"namespace": "player-storage", "key": "Storage.Quest.Demo.Stage", "value": 0}
                ],
                "transitions": [
                    {
                        "transitionId": t1,
                        "mapContextExpected": [{"position": [100, 100, 7], "actionId": 45001}],
                        "interaction": None,
                    },
                    {
                        "transitionId": t2,
                        "mapContextExpected": [{"position": [100, 100, 7], "actionId": 45001}],
                        "interaction": None,
                    },
                ],
                "goals": [
                    {"id": "stage-two", "namespace": "player-storage", "key": "Storage.Quest.Demo.Stage", "value": 2}
                ],
            }
        ],
    }
    registry = {
        "format": INTERACTION_REGISTRY_FORMAT,
        "schemaVersion": 1,
        "registryStatus": "reviewed",
        "provenance": {
            "sourceMap": {"sha256": sha("c")},
            "worldIndex": {"sha256": sha("d")},
            "transitionManifest": None,
            "scriptResolution": None,
        },
        "entries": [
            {
                "id": "demo.lever",
                "selector": {"position": [100, 100, 7], "actionId": 45001},
                "activation": {"kind": "use-map-item", "target": "selector-position"},
                "requirements": {
                    "transitionKinds": [],
                    "transitionEvidenceSources": [],
                    "scriptResolution": {"required": False, "allowedStatuses": []},
                },
                "evidence": {"status": "reviewed", "references": ["review:demo-lever"]},
            }
        ],
    }
    pins = {
        "manifest": pin("manifest.json", sha("e"), MANIFEST_FORMAT),
        "storageGraph": pin("storage.json", sha("f"), STORAGE_GRAPH_FORMAT),
        "routeInteractions": None,
    }
    return storage, manifest, registry, pins


class QuestStateReachabilityTests(unittest.TestCase):
    def build(self):
        storage, manifest, _registry, pins = fixtures()
        return build_quest_state_reachability_report(
            manifest=manifest,
            storage_graph=storage,
            route_interactions=None,
            input_pins=pins,
        )

    def test_exact_selected_chain_is_reachable(self):
        report = self.build()
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertTrue(report["ok"])
        target = report["targets"][0]
        self.assertTrue(target["requirementsSatisfied"])
        self.assertFalse(target["runtimeGameplayCompletionProven"])
        self.assertEqual(target["goals"][0]["classification"], "reachable")
        self.assertEqual(target["goals"][0]["pathTransitionIds"], ["1" * 20, "2" * 20])
        self.assertFalse(report["policy"]["runtimeGameplayCompletionClaimed"])
        self.assertFalse(report["policy"]["executionOrderInferred"])

    def test_map_context_mismatch_blocks_candidate_path(self):
        storage, manifest, _registry, pins = fixtures()
        manifest["targets"][0]["transitions"][1]["mapContextExpected"] = [
            {"position": [101, 100, 7], "actionId": 45001}
        ]
        report = build_quest_state_reachability_report(
            manifest=manifest, storage_graph=storage, route_interactions=None, input_pins=pins
        )
        goal = report["targets"][0]["goals"][0]
        self.assertEqual(goal["classification"], "blocked-by-evidence")
        self.assertIn("MAP_CONTEXT_MISMATCH", {item["code"] for item in goal["blockers"]})

    def test_interaction_requirement_reuses_existing_resolver(self):
        storage, manifest, registry, pins = fixtures()
        manifest["targets"][0]["transitions"][1]["interaction"] = {
            "query": {"position": [100, 100, 7], "actionId": 45001}
        }
        pins["routeInteractions"] = pin("interactions.json", sha("9"), INTERACTION_REGISTRY_FORMAT)
        report = build_quest_state_reachability_report(
            manifest=manifest,
            storage_graph=storage,
            route_interactions=registry,
            input_pins=pins,
        )
        edge = report["targets"][0]["transitions"][1]
        self.assertEqual(edge["status"], "proven")
        self.assertEqual(edge["interactionResolution"]["executionStatus"], "executable")
        self.assertTrue(report["targets"][0]["requirementsSatisfied"])

    def test_missing_interaction_registry_blocks_transition(self):
        storage, manifest, _registry, pins = fixtures()
        manifest["targets"][0]["transitions"][1]["interaction"] = {
            "query": {"position": [100, 100, 7], "actionId": 45001}
        }
        report = build_quest_state_reachability_report(
            manifest=manifest, storage_graph=storage, route_interactions=None, input_pins=pins
        )
        goal = report["targets"][0]["goals"][0]
        self.assertEqual(goal["classification"], "blocked-by-evidence")
        self.assertIn("INTERACTION_REGISTRY_REQUIRED", {item["code"] for item in goal["blockers"]})

    def test_goal_without_selected_producer_is_external_or_unproven(self):
        storage, manifest, _registry, pins = fixtures()
        manifest["targets"][0]["goals"][0]["value"] = 9
        report = build_quest_state_reachability_report(
            manifest=manifest, storage_graph=storage, route_interactions=None, input_pins=pins
        )
        goal = report["targets"][0]["goals"][0]
        self.assertEqual(goal["classification"], "external-or-unproven")
        self.assertEqual(report["findings"][0]["code"], "QUEST_STATE_EXTERNAL_OR_UNPROVEN")
        self.assertFalse(report["policy"]["globalImpossibilityClaimed"])

    def test_disconnected_selected_producer_is_unreachable_in_selected_scope(self):
        storage, manifest, _registry, pins = fixtures()
        t3 = "3" * 20
        storage["transitions"].append(transition(t3, 5, 9))
        manifest["targets"][0]["transitions"] = [
            {
                "transitionId": t3,
                "mapContextExpected": [{"position": [100, 100, 7], "actionId": 45001}],
                "interaction": None,
            }
        ]
        manifest["targets"][0]["goals"][0]["value"] = 9
        report = build_quest_state_reachability_report(
            manifest=manifest, storage_graph=storage, route_interactions=None, input_pins=pins
        )
        target = report["targets"][0]
        self.assertEqual(target["goals"][0]["classification"], "unreachable-in-selected-scope")
        self.assertEqual(target["externalPrerequisites"][0]["value"], 5)
        self.assertEqual(report["findings"][0]["code"], "POTENTIALLY_UNREACHABLE_QUEST_STATE")

    def test_unknown_transition_fails_closed(self):
        storage, manifest, _registry, pins = fixtures()
        manifest["targets"][0]["transitions"][0]["transitionId"] = "9" * 20
        with self.assertRaisesRegex(QuestStateReachabilityError, "unknown Storage Graph transition"):
            build_quest_state_reachability_report(
                manifest=manifest, storage_graph=storage, route_interactions=None, input_pins=pins
            )

    def test_incomplete_storage_graph_fails_closed(self):
        storage, manifest, _registry, pins = fixtures()
        storage["complete"] = False
        with self.assertRaisesRegex(QuestStateReachabilityError, "must be complete"):
            build_quest_state_reachability_report(
                manifest=manifest, storage_graph=storage, route_interactions=None, input_pins=pins
            )

    def test_map_context_requires_quest_validation_provenance(self):
        storage, manifest, _registry, pins = fixtures()
        storage["inputs"]["questValidation"] = None
        report = build_quest_state_reachability_report(
            manifest=manifest, storage_graph=storage, route_interactions=None, input_pins=pins
        )
        goal = report["targets"][0]["goals"][0]
        self.assertEqual(goal["classification"], "blocked-by-evidence")
        self.assertIn("QUEST_VALIDATION_PROVENANCE_REQUIRED", {item["code"] for item in goal["blockers"]})

    def test_output_is_deterministic(self):
        storage, manifest, registry, pins = fixtures()
        pins_with_registry = copy.deepcopy(pins)
        pins_with_registry["routeInteractions"] = pin("interactions.json", sha("9"), INTERACTION_REGISTRY_FORMAT)
        manifest["targets"][0]["transitions"][0]["interaction"] = {
            "query": {"position": [100, 100, 7], "actionId": 45001}
        }
        first = build_quest_state_reachability_report(
            manifest=manifest,
            storage_graph=storage,
            route_interactions=registry,
            input_pins=pins_with_registry,
        )
        second = build_quest_state_reachability_report(
            manifest=manifest,
            storage_graph=storage,
            route_interactions=registry,
            input_pins=pins_with_registry,
        )
        self.assertEqual(canonical_report_sha256(first), canonical_report_sha256(second))


if __name__ == "__main__":
    unittest.main()
