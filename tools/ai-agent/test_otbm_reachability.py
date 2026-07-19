from __future__ import annotations

import json
import os
import struct
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from otbm_reachability import (
    APPEARANCES_FORMAT,
    MAX_REGION_COORDINATES,
    REPORT_FORMAT,
    ROUTE_PLAN_FORMAT,
    TRANSITION_FORMAT,
    AppearanceSemantics,
    ReachabilityError,
    analyze_index_path,
    analyze_world,
    load_appearance_semantics,
    load_transition_manifest,
    normalize_bounds,
    write_report,
)

NODE_ESCAPE = 0xFD
NODE_START = 0xFE
NODE_END = 0xFF
OTBM_MAP_DATA = 2
OTBM_TILE_AREA = 4
OTBM_TILE = 5
OTBM_ITEM = 6
ATTR_TELE_DEST = 8
ATTR_ITEM = 9


def _escape(data: bytes) -> bytes:
    output = bytearray()
    for value in data:
        if value in (NODE_ESCAPE, NODE_START, NODE_END):
            output.append(NODE_ESCAPE)
        output.append(value)
    return bytes(output)


def _node(node_type: int, properties: bytes, children: list[bytes] | None = None) -> bytes:
    return bytes((NODE_START, node_type)) + _escape(properties) + b"".join(children or []) + bytes((NODE_END,))


def _item(item_id: int, attributes: bytes = b"") -> bytes:
    return _node(OTBM_ITEM, struct.pack("<H", item_id) + attributes)


def _make_cross_floor_map(path: Path) -> None:
    source = _node(
        OTBM_TILE,
        bytes((10, 10, ATTR_ITEM)) + struct.pack("<H", 1),
        [_item(4, bytes((ATTR_TELE_DEST,)) + struct.pack("<HHB", 10, 10, 8))],
    )
    destination = _node(OTBM_TILE, bytes((10, 10, ATTR_ITEM)) + struct.pack("<H", 1))
    area7 = _node(OTBM_TILE_AREA, struct.pack("<HHB", 0, 0, 7), [source])
    area8 = _node(OTBM_TILE_AREA, struct.pack("<HHB", 0, 0, 8), [destination])
    map_data = _node(OTBM_MAP_DATA, b"", [area7, area8])
    root = _node(0, struct.pack("<IHHII", 4, 1024, 1024, 4, 4), [map_data])
    path.write_bytes(b"\0\0\0\0" + root)


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

    def add_tile(self, position: tuple[int, int, int], items: list[dict], *, kind: str = "tile") -> None:
        start = len(self.placements)
        tile_index = len(self.tiles)
        tile = FakeTile(*position, start, len(items), kind=kind, house_id=9 if kind == "house" else None)
        self.tiles.append(tile)
        self.by_position[position] = (tile_index, tile)
        for item in items:
            ordinal = len(self.placements)
            entry = {
                "placementOrdinal": ordinal,
                "itemId": item["itemId"],
                "position": list(position),
                "itemDepth": -1,
                "source": "inline",
                "tileIndex": tile_index,
                **{key: value for key, value in item.items() if key != "itemId"},
            }
            self.placements.append(entry)

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
    2: AppearanceSemantics(2, False, True, False, False, False, False),
    3: AppearanceSemantics(3, False, True, False, True, False, False),
    4: AppearanceSemantics(4, False, False, False, False, False, False),
    5: AppearanceSemantics(5, False, False, False, True, False, False),
    6: AppearanceSemantics(6, False, False, True, False, False, False),
}


def line_world(length: int = 3) -> FakeWorldIndex:
    world = FakeWorldIndex()
    for x in range(length):
        world.add_tile((x, 0, 7), [{"itemId": 1}])
    return world


def route_provenance() -> dict:
    return {
        "worldIndex": {
            "path": "fixture.widx",
            "size": 123,
            "sha256": "1" * 64,
            "format": "canary-otbm-world-index-v1",
        },
        "appearances": {
            "path": "appearances.json",
            "size": 456,
            "sha256": "2" * 64,
            "format": APPEARANCES_FORMAT,
            "objectCount": len(APPEARANCES),
        },
        "transitionManifest": None,
        "scriptResolution": None,
        "worldIndexManifest": {
            "source": {
                "path": "fixture.otbm",
                "size": 789,
                "sha256": "3" * 64,
            },
            "index": {
                "path": "fixture.widx",
                "sha256": "1" * 64,
            },
        },
    }


class ReachabilityTests(unittest.TestCase):
    def test_confirmed_route_around_static_blocker(self) -> None:
        world = FakeWorldIndex()
        for position in ((0, 0, 7), (1, 0, 7), (2, 0, 7), (0, 1, 7), (1, 1, 7), (2, 1, 7)):
            items = [{"itemId": 1}]
            if position == (1, 0, 7):
                items.append({"itemId": 2})
            world.add_tile(position, items)
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 1, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
        )
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["routes"][0]["status"], "confirmed")
        self.assertEqual(report["routes"][0]["strictDistance"], 4)

    def test_conditional_door_route(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((1, 0, 7), [{"itemId": 1}, {"itemId": 3, "uniqueId": 5000}])
        world.add_tile((2, 0, 7), [{"itemId": 1}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
        )
        self.assertEqual(report["routes"][0]["status"], "conditional")
        self.assertIsNone(report["routes"][0]["strictDistance"])
        self.assertEqual(report["routes"][0]["optimisticDistance"], 2)

    def test_missing_appearance_blocks_strict_not_optimistic(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((1, 0, 7), [{"itemId": 1}, {"itemId": 999}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(1, 0, 7),
            routes=[((0, 0, 7), (1, 0, 7))],
        )
        self.assertEqual(report["routes"][0]["status"], "conditional")
        self.assertEqual(report["summary"]["tileStatusCounts"]["unknownAppearance"], 1)

    def test_teleport_missing_destination_is_error(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}, {"itemId": 4, "teleportDestination": [9, 9, 8]}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(0, 0, 7),
            routes=[((0, 0, 7), (0, 0, 7))],
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["transitions"][0]["status"], "invalid")
        self.assertEqual(report["summary"]["findings"]["byCode"]["transition_destination_missing"], 1)

    def test_teleport_cross_floor_route(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}, {"itemId": 4, "teleportDestination": [0, 0, 8]}])
        world.add_tile((0, 0, 8), [{"itemId": 1}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(0, 0, 8),
            routes=[((0, 0, 7), (0, 0, 8))],
        )
        self.assertEqual(report["routes"][0]["status"], "confirmed")
        self.assertEqual(report["routes"][0]["transitionIdsUsed"], ["teleport:1"])

    def test_route_plan_ordinary_movement_uses_full_path_not_report_sample(self) -> None:
        report = analyze_world(
            line_world(),
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            path_limit=1,
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )
        route = report["routes"][0]
        plan = route["routePlan"]
        self.assertTrue(route["pathTruncated"])
        self.assertEqual(plan["format"], ROUTE_PLAN_FORMAT)
        self.assertEqual(plan["routeStatus"], "confirmed")
        self.assertEqual(plan["executionStatus"], "executable")
        self.assertEqual(plan["distance"], route["strictDistance"])
        self.assertTrue(plan["pathComplete"])
        self.assertEqual(plan["path"], [[0, 0, 7], [1, 0, 7], [2, 0, 7]])
        self.assertEqual(
            [(edge["from"], edge["to"], edge["kind"], edge["transitionId"]) for edge in plan["edges"]],
            [
                ([0, 0, 7], [1, 0, 7], "movement", None),
                ([1, 0, 7], [2, 0, 7], "movement", None),
            ],
        )

    def _movement_transition_report(self) -> dict:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((1, 0, 7), [{"itemId": 1}, {"itemId": 4, "teleportDestination": [1, 0, 8]}])
        world.add_tile((1, 0, 8), [{"itemId": 1}])
        world.add_tile((2, 0, 8), [{"itemId": 1}])
        return analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 8),
            routes=[((0, 0, 7), (2, 0, 8))],
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )

    def test_route_plan_movement_and_transition_matches_reachability_decision(self) -> None:
        report = self._movement_transition_report()
        route = report["routes"][0]
        plan = route["routePlan"]
        self.assertEqual(plan["routeStatus"], route["status"])
        self.assertEqual(plan["distance"], route["strictDistance"])
        self.assertEqual(plan["path"], [[0, 0, 7], [1, 0, 7], [1, 0, 8], [2, 0, 8]])
        self.assertEqual([edge["kind"] for edge in plan["edges"]], ["movement", "transition", "movement"])
        self.assertEqual(plan["edges"][0]["evidence"]["edgeSource"], "_movement_neighbors")
        self.assertEqual(plan["edges"][2]["evidence"]["edgeSource"], "_movement_neighbors")
        transition = plan["edges"][1]["evidence"]["transition"]
        self.assertTrue(transition["valid"])
        self.assertTrue(transition["strictEligible"])
        self.assertEqual(transition["source"], [1, 0, 7])
        self.assertEqual(transition["destination"], [1, 0, 8])

    def test_route_plan_transition_id_is_attached_to_exact_edge(self) -> None:
        plan = self._movement_transition_report()["routes"][0]["routePlan"]
        self.assertIsNone(plan["edges"][0]["transitionId"])
        self.assertEqual(plan["edges"][1]["from"], [1, 0, 7])
        self.assertEqual(plan["edges"][1]["to"], [1, 0, 8])
        self.assertEqual(plan["edges"][1]["transitionId"], "teleport:2")
        self.assertIsNone(plan["edges"][2]["transitionId"])
        self.assertEqual(plan["edges"][1]["evidence"]["transition"]["id"], "teleport:2")

    def test_route_plan_non_executable_statuses_fail_closed(self) -> None:
        conditional_world = FakeWorldIndex()
        conditional_world.add_tile((0, 0, 7), [{"itemId": 1}])
        conditional_world.add_tile((1, 0, 7), [{"itemId": 1}, {"itemId": 3, "uniqueId": 5000}])
        conditional_world.add_tile((2, 0, 7), [{"itemId": 1}])
        conditional = analyze_world(
            conditional_world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )["routes"][0]["routePlan"]
        self.assertEqual(conditional["routeStatus"], "conditional")
        self.assertEqual(conditional["executionStatus"], "blocked")
        self.assertIn("conditional-route-not-executable", {entry["code"] for entry in conditional["blockers"]})

        unreachable_world = FakeWorldIndex()
        unreachable_world.add_tile((0, 0, 7), [{"itemId": 1}])
        unreachable_world.add_tile((2, 0, 7), [{"itemId": 1}])
        unreachable = analyze_world(
            unreachable_world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )["routes"][0]["routePlan"]
        self.assertEqual(unreachable["routeStatus"], "unreachable")
        self.assertEqual(unreachable["executionStatus"], "not-applicable")

        invalid = analyze_world(
            line_world(),
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (3, 0, 7))],
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )["routes"][0]["routePlan"]
        self.assertEqual(invalid["routeStatus"], "invalid")
        self.assertEqual(invalid["executionStatus"], "not-applicable")
        self.assertNotEqual(conditional["executionStatus"], "executable")
        self.assertNotEqual(unreachable["executionStatus"], "executable")
        self.assertNotEqual(invalid["executionStatus"], "executable")

    def test_route_plan_full_route_bound_never_returns_partial_executable_path(self) -> None:
        plan = analyze_world(
            line_world(length=4),
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(3, 0, 7),
            routes=[((0, 0, 7), (3, 0, 7))],
            route_plan_max_positions=2,
            provenance=route_provenance(),
        )["routes"][0]["routePlan"]
        self.assertEqual(plan["routeStatus"], "confirmed")
        self.assertEqual(plan["executionStatus"], "blocked")
        self.assertFalse(plan["pathComplete"])
        self.assertEqual(plan["path"], [])
        self.assertEqual(plan["edges"], [])
        blocker = next(entry for entry in plan["blockers"] if entry["code"] == "route-exceeds-supported-bound")
        self.assertEqual(blocker["requiredPositions"], 4)
        self.assertEqual(blocker["supportedMaxPositions"], 2)

    def test_route_plan_is_deterministic_including_hashes(self) -> None:
        kwargs = dict(
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            route_plan_max_positions=10,
            provenance=route_provenance(),
        )
        first = analyze_world(line_world(), **kwargs)["routes"][0]["routePlan"]
        second = analyze_world(line_world(), **kwargs)["routes"][0]["routePlan"]
        self.assertEqual(first, second)
        self.assertEqual(first["inputHashSha256"], second["inputHashSha256"])
        self.assertEqual(first["planHashSha256"], second["planHashSha256"])
        self.assertEqual(len(first["inputHashSha256"]), 64)
        self.assertEqual(len(first["planHashSha256"]), 64)

    def test_explicit_ladder_item_mismatch(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((0, 0, 6), [{"itemId": 1}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 6),
            upper=(0, 0, 7),
            routes=[((0, 0, 7), (0, 0, 6))],
            transition_entries=[{
                "id": "ladder-a",
                "kind": "ladder",
                "source": [0, 0, 7],
                "destination": [0, 0, 6],
                "expectedItemIds": [5],
            }],
        )
        self.assertFalse(report["ok"])
        self.assertIn("expected-item-missing", report["transitions"][0]["issues"])

    def test_explicit_bidirectional_stairs_and_loop(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}, {"itemId": 5}])
        world.add_tile((0, 0, 6), [{"itemId": 1}, {"itemId": 5}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 6),
            upper=(0, 0, 7),
            routes=[((0, 0, 7), (0, 0, 6))],
            transition_entries=[{
                "id": "stairs-a",
                "kind": "stairs",
                "source": [0, 0, 7],
                "destination": [0, 0, 6],
                "expectedItemIds": [5],
                "bidirectional": True,
            }],
        )
        self.assertEqual(report["routes"][0]["status"], "confirmed")
        self.assertEqual(report["summary"]["transitionLoops"], 1)
        self.assertEqual(report["summary"]["oneWayTransitions"], 0)

    def test_one_way_and_dead_end_are_reported(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}, {"itemId": 5}])
        world.add_tile((2, 0, 7), [{"itemId": 1}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            transition_entries=[{
                "id": "hole-a",
                "kind": "hole",
                "source": [0, 0, 7],
                "destination": [2, 0, 7],
                "expectedItemIds": [5],
            }],
        )
        self.assertEqual(report["summary"]["oneWayTransitions"], 1)
        self.assertEqual(report["summary"]["deadEndTransitions"], 1)

    def test_script_conflict_keeps_teleport_conditional_and_fails(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}, {"itemId": 4, "actionId": 100, "teleportDestination": [1, 0, 7]}])
        world.add_tile((1, 0, 7), [{"itemId": 1}])
        script = {
            "format": "canary-otbm-script-resolution-v1",
            "placements": [{
                "position": [0, 0, 7],
                "itemId": 4,
                "actionId": 100,
                "uniqueId": None,
                "houseDoorId": None,
                "teleportDestination": [1, 0, 7],
                "status": "conflicting",
            }],
        }
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(1, 0, 7),
            routes=[((0, 0, 7), (1, 0, 7))],
            script_resolution=script,
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["transitions"][0]["status"], "conditional")
        self.assertIn("script-resolution-conflicting", report["transitions"][0]["uncertainties"])

    def test_mechanic_reachability(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((1, 0, 7), [{"itemId": 1}, {"itemId": 2}, {"itemId": 5, "actionId": 99}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(1, 0, 7),
            routes=[],
            origins=[(0, 0, 7)],
        )
        self.assertEqual(report["summary"]["mechanicStatusCounts"]["unreachable"], 1)
        self.assertEqual(report["mechanics"][0]["status"], "unreachable")

    def test_diagonal_requires_open_corners(self) -> None:
        world = FakeWorldIndex()
        world.add_tile((0, 0, 7), [{"itemId": 1}])
        world.add_tile((1, 1, 7), [{"itemId": 1}])
        report = analyze_world(
            world,
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(1, 1, 7),
            routes=[((0, 0, 7), (1, 1, 7))],
            allow_diagonal=True,
        )
        self.assertEqual(report["routes"][0]["status"], "unreachable")

    def test_report_is_deterministic(self) -> None:
        world = line_world()
        kwargs = dict(
            appearances=APPEARANCES,
            lower=(0, 0, 7),
            upper=(2, 0, 7),
            routes=[((0, 0, 7), (2, 0, 7))],
            provenance={"worldIndex": {"sha256": "a" * 64}},
        )
        first = analyze_world(world, **kwargs)
        second = analyze_world(world, **kwargs)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_region_bound_is_enforced(self) -> None:
        with self.assertRaises(ReachabilityError):
            normalize_bounds((0, 0, 0), (1000, 1000, 1))
        self.assertLess(MAX_REGION_COORDINATES, 2_004_002)

    def test_manifest_and_appearance_loaders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            appearances = root / "appearances.json"
            appearances.write_text(json.dumps({
                "format": APPEARANCES_FORMAT,
                "appearances": [{"category": "object", "id": 1, "flags": {"bank": {"waypoints": 1}}}],
            }), encoding="utf-8")
            semantics, provenance = load_appearance_semantics(appearances)
            self.assertTrue(semantics[1].ground)
            self.assertEqual(len(provenance["sha256"]), 64)

            manifest = root / "transitions.json"
            manifest.write_text(json.dumps({
                "format": TRANSITION_FORMAT,
                "transitions": [{"id": "x", "kind": "stairs", "source": [1, 1, 7], "delta": [0, 0, -1]}],
            }), encoding="utf-8")
            transitions, metadata = load_transition_manifest(manifest)
            self.assertEqual(transitions[0]["id"], "x")
            self.assertEqual(metadata["format"], TRANSITION_FORMAT)

    @unittest.skipUnless(os.environ.get("OTBM_WORLD_INDEX_SCANNER"), "real scanner path not provided")
    def test_real_world_index_integration(self) -> None:
        from otbm_world_index import build_world_index

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "fixture.otbm"
            index_path = root / "fixture.widx"
            manifest_path = root / "fixture.widx.json"
            appearances_path = root / "appearances.json"
            _make_cross_floor_map(map_path)
            appearances_path.write_text(json.dumps({
                "format": APPEARANCES_FORMAT,
                "appearances": [
                    {"category": "object", "id": 1, "flags": {"bank": {"waypoints": 1}}},
                    {"category": "object", "id": 4, "flags": {}},
                ],
            }), encoding="utf-8")
            build_world_index(
                map_path=map_path,
                scanner=Path(os.environ["OTBM_WORLD_INDEX_SCANNER"]),
                output=index_path,
                manifest_output=manifest_path,
            )
            report = analyze_index_path(
                index_path=index_path,
                appearances_path=appearances_path,
                lower=(10, 10, 7),
                upper=(10, 10, 8),
                routes=[((10, 10, 7), (10, 10, 8))],
                origins=[],
                world_manifest_path=manifest_path,
            )
            self.assertTrue(report["ok"])
            self.assertEqual(report["routes"][0]["status"], "confirmed")
            self.assertEqual(report["summary"]["transitions"], 1)

    @unittest.skipIf(os.name == "nt", "symlink creation often requires elevated privileges on Windows")
    def test_atomic_output_and_symlink_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "report.json"
            write_report(output, {"format": REPORT_FORMAT})
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["format"], REPORT_FORMAT)
            with self.assertRaises(ReachabilityError):
                write_report(output, {"format": REPORT_FORMAT})
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(ReachabilityError):
                write_report(link, {"format": REPORT_FORMAT}, overwrite=True)


if __name__ == "__main__":
    unittest.main()
