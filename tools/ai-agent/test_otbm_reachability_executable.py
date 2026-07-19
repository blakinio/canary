from __future__ import annotations

import unittest
from dataclasses import dataclass

from otbm_reachability import AppearanceSemantics, analyze_world


@dataclass(frozen=True)
class FakeTile:
    x: int
    y: int
    z: int
    placement_start: int
    placement_count: int
    kind: str = "tile"
    house_id: int | None = None
    flags: int = 0


class FakeWorldIndex:
    def __init__(self) -> None:
        self.tiles: list[FakeTile] = []
        self.by_position: dict[tuple[int, int, int], tuple[int, FakeTile]] = {}
        self.placements: list[dict] = []

    def add_tile(self, position: tuple[int, int, int], items: list[dict]) -> None:
        start = len(self.placements)
        tile_index = len(self.tiles)
        tile = FakeTile(*position, start, len(items))
        self.tiles.append(tile)
        self.by_position[position] = (tile_index, tile)
        for item in items:
            ordinal = len(self.placements)
            self.placements.append(
                {
                    "placementOrdinal": ordinal,
                    "itemId": item["itemId"],
                    "position": list(position),
                    "itemDepth": -1,
                    "source": "fixture",
                    "tileIndex": tile_index,
                    **{key: value for key, value in item.items() if key != "itemId"},
                }
            )

    def iter_region_tiles(self, lower, upper):
        for index, tile in enumerate(self.tiles):
            if lower[0] <= tile.x <= upper[0] and lower[1] <= tile.y <= upper[1] and lower[2] <= tile.z <= upper[2]:
                yield index, tile

    def placement(self, ordinal):
        return dict(self.placements[ordinal])

    def find_tile(self, position):
        return self.by_position.get(tuple(position))


APPEARANCES = {
    1: AppearanceSemantics(1, True, False, False, False, False, False),
    3: AppearanceSemantics(3, False, True, False, True, False, False),
    4: AppearanceSemantics(4, False, False, False, False, False, False),
}

MAP_SHA = "3" * 64
WORLD_INDEX_SHA = "1" * 64
APPEARANCES_SHA = "2" * 64
INTERACTIONS_SHA = "4" * 64


def route_provenance(*, script_sha: str | None = None) -> dict:
    return {
        "worldIndex": {
            "path": "fixture.widx",
            "size": 123,
            "sha256": WORLD_INDEX_SHA,
            "format": "canary-otbm-world-index-v1",
        },
        "appearances": {
            "path": "appearances.json",
            "size": 456,
            "sha256": APPEARANCES_SHA,
            "format": "canary-appearances-index-v1",
            "objectCount": len(APPEARANCES),
        },
        "transitionManifest": None,
        "scriptResolution": (
            None
            if script_sha is None
            else {
                "path": "script-resolution.json",
                "size": 100,
                "sha256": script_sha,
                "format": "canary-otbm-script-resolution-v1",
            }
        ),
        "interactionRegistry": {
            "path": "interactions.json",
            "size": 200,
            "sha256": INTERACTIONS_SHA,
            "format": "canary-otbm-route-interactions-v1",
        },
        "worldIndexManifest": {
            "source": {
                "path": "fixture.otbm",
                "size": 789,
                "sha256": MAP_SHA,
            },
            "index": {
                "path": "fixture.widx",
                "sha256": WORLD_INDEX_SHA,
            },
        },
    }


def reviewed_registry(entries: list[dict], *, script_sha: str | None = None) -> dict:
    return {
        "format": "canary-otbm-route-interactions-v1",
        "schemaVersion": 1,
        "registryStatus": "reviewed",
        "provenance": {
            "sourceMap": {"sha256": MAP_SHA},
            "worldIndex": {"sha256": WORLD_INDEX_SHA},
            "transitionManifest": None,
            "scriptResolution": None if script_sha is None else {"sha256": script_sha},
        },
        "entries": entries,
    }


def mechanic_entry(
    entry_id: str,
    position: list[int],
    item_id: int,
    *,
    action_id: int | None = None,
) -> dict:
    selector = {"position": position, "itemId": item_id}
    if action_id is not None:
        selector["actionId"] = action_id
    return {
        "id": entry_id,
        "selector": selector,
        "activation": {"kind": "use-map-item", "target": "selector-position"},
        "requirements": {
            "transitionKinds": [],
            "transitionEvidenceSources": [],
            "scriptResolution": {"required": False, "allowedStatuses": []},
        },
        "evidence": {"status": "reviewed", "references": ["unit-test-reviewed-mechanic"]},
    }


def transition_entry(entry_id: str, transition_id: str) -> dict:
    return {
        "id": entry_id,
        "selector": {"transitionId": transition_id},
        "activation": {"kind": "step-on"},
        "requirements": {
            "transitionKinds": ["teleport"],
            "transitionEvidenceSources": ["worldIndex"],
            "scriptResolution": {"required": False, "allowedStatuses": []},
        },
        "evidence": {"status": "reviewed", "references": ["unit-test-reviewed-transition"]},
    }


def door_vs_unknown_world() -> FakeWorldIndex:
    world = FakeWorldIndex()
    for position in (
        (0, 1, 7),
        (1, 1, 7),
        (2, 1, 7),
        (3, 1, 7),
        (4, 1, 7),
        (1, 2, 7),
        (2, 2, 7),
        (3, 2, 7),
    ):
        items = [{"itemId": 1}]
        if position == (2, 1, 7):
            items.append({"itemId": 999})
        if position == (2, 2, 7):
            items.append({"itemId": 3})
        world.add_tile(position, items)
    return world


class ExecutableReachabilityTests(unittest.TestCase):
    def test_executable_bfs_rejects_unknown_shortcut_and_selects_reviewed_door(self) -> None:
        registry = reviewed_registry([mechanic_entry("reviewed-door", [2, 2, 7], 3)])
        report = analyze_world(
            door_vs_unknown_world(),
            appearances=APPEARANCES,
            lower=(0, 1, 7),
            upper=(4, 2, 7),
            routes=[((0, 1, 7), (4, 1, 7))],
            interaction_registry=registry,
            route_plan_max_positions=20,
            provenance=route_provenance(),
        )
        route = report["routes"][0]
        plan = route["routePlan"]
        self.assertEqual(route["status"], "conditional")
        self.assertIsNone(route["strictDistance"])
        self.assertEqual(route["optimisticDistance"], 4)
        self.assertEqual(route["executableDistance"], 6)
        self.assertEqual(plan["routingMode"], "executable")
        self.assertEqual(plan["executionStatus"], "executable")
        self.assertEqual(plan["distance"], 6)
        self.assertIn([2, 2, 7], plan["path"])
        self.assertNotIn([2, 1, 7], plan["path"])
        door_edge = next(edge for edge in plan["edges"] if edge["to"] == [2, 2, 7])
        self.assertEqual(door_edge["kind"], "movement")
        self.assertEqual(len(door_edge["interactions"]), 1)
        self.assertEqual(door_edge["interactions"][0]["matchedEntryId"], "reviewed-door")
        self.assertEqual(door_edge["interactions"][0]["activation"]["kind"], "use-map-item")
        self.assertEqual(door_edge["executionBlockers"], [])

    def test_removing_door_interaction_evidence_makes_route_non_executable(self) -> None:
        report = analyze_world(
            door_vs_unknown_world(),
            appearances=APPEARANCES,
            lower=(0, 1, 7),
            upper=(4, 2, 7),
            routes=[((0, 1, 7), (4, 1, 7))],
            interaction_registry=reviewed_registry([]),
            route_plan_max_positions=20,
            provenance=route_provenance(),
        )
        route = report["routes"][0]
        plan = route["routePlan"]
        self.assertEqual(route["status"], "conditional")
        self.assertIsNone(route["executableDistance"])
        self.assertEqual(plan["executionStatus"], "blocked")
        self.assertIn("executable-route-unavailable", {entry["code"] for entry in plan["blockers"]})

    def test_reviewed_selector_cannot_promote_unknown_appearance(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((1, 0, 7), [{"itemId": 1}, {"itemId": 999}])
        world.add_tile((2, 0, 7), [{"itemId": 1}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            interaction_registry=reviewed_registry([mechanic_entry("unknown-not-a-contract", [1, 0, 7], 999)]),
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )
        route = report["routes"][0]
        self.assertEqual(route["status"], "conditional")
        self.assertEqual(route["optimisticDistance"], 2)
        self.assertIsNone(route["executableDistance"])
        self.assertEqual(route["routePlan"]["executionStatus"], "blocked")

    def test_reviewed_transition_is_executable_on_exact_existing_bfs_edge(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}, {"itemId": 4, "teleportDestination": [0, 0, 8]}])
        world.add_tile((0, 0, 8), [{"itemId": 1}])
        registry = reviewed_registry([transition_entry("reviewed-teleport", "teleport:1")])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(0, 0, 8),
            routes=[((0, 0, 7), (0, 0, 8))],
            interaction_registry=registry,
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )
        route = report["routes"][0]
        plan = route["routePlan"]
        self.assertEqual(route["status"], "confirmed")
        self.assertEqual(route["strictDistance"], 1)
        self.assertEqual(route["executableDistance"], 1)
        self.assertEqual(plan["executionStatus"], "executable")
        self.assertEqual(plan["routingMode"], "executable")
        self.assertEqual(plan["edges"][0]["transitionId"], "teleport:1")
        self.assertEqual(plan["edges"][0]["interactions"][0]["matchedEntryId"], "reviewed-teleport")
        self.assertEqual(plan["edges"][0]["interactions"][0]["activation"]["kind"], "step-on")

    def test_unreviewed_transition_remains_blocked_in_interaction_aware_mode(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}, {"itemId": 4, "teleportDestination": [0, 0, 8]}])
        world.add_tile((0, 0, 8), [{"itemId": 1}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(0, 0, 8),
            routes=[((0, 0, 7), (0, 0, 8))],
            interaction_registry=reviewed_registry([]),
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )
        route = report["routes"][0]
        self.assertEqual(route["status"], "confirmed")
        self.assertIsNone(route["executableDistance"])
        self.assertEqual(route["routePlan"]["executionStatus"], "blocked")
        self.assertIn("executable-route-unavailable", {entry["code"] for entry in route["routePlan"]["blockers"]})

    def test_action_id_barrier_without_resolved_script_status_fails_closed(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((1, 0, 7), [{"itemId": 1}, {"itemId": 3, "actionId": 100}])
        world.add_tile((2, 0, 7), [{"itemId": 1}])
        registry = reviewed_registry([mechanic_entry("aid-door", [1, 0, 7], 3, action_id=100)])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            interaction_registry=registry,
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )
        route = report["routes"][0]
        self.assertEqual(route["status"], "conditional")
        self.assertEqual(route["optimisticDistance"], 2)
        self.assertIsNone(route["executableDistance"])
        self.assertEqual(route["routePlan"]["executionStatus"], "blocked")

    def test_interaction_aware_route_plan_is_deterministic(self) -> None:
        registry = reviewed_registry([mechanic_entry("reviewed-door", [2, 2, 7], 3)])
        kwargs = dict(
            appearances=APPEARANCES,
            lower=(0, 1, 7),
            upper=(4, 2, 7),
            routes=[((0, 1, 7), (4, 1, 7))],
            interaction_registry=registry,
            route_plan_max_positions=20,
            provenance=route_provenance(),
        )
        first = analyze_world(door_vs_unknown_world(), **kwargs)["routes"][0]["routePlan"]
        second = analyze_world(door_vs_unknown_world(), **kwargs)["routes"][0]["routePlan"]
        self.assertEqual(first, second)
        self.assertEqual(first["inputHashSha256"], second["inputHashSha256"])
        self.assertEqual(first["planHashSha256"], second["planHashSha256"])


if __name__ == "__main__":
    unittest.main()
