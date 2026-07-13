from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from otbm_reachability import (
    APPEARANCES_INDEX_FORMAT,
    MOVEMENT_CATALOG_FORMAT,
    Bounds,
    MovementRule,
    ReachabilityError,
    audit_transitions,
    load_appearances,
    load_movement_catalog,
    parse_position,
    tile_evidence,
    validate_route,
    write_json_atomic,
)


@dataclass
class FakeTile:
    x: int
    y: int
    z: int
    placement_start: int
    placement_count: int
    kind: str = "tile"
    house_id: int | None = None
    flags: int = 0


class FakeIndex:
    def __init__(self, tiles: dict[tuple[int, int, int], list[dict]], mechanics: list[dict] | None = None):
        self.tiles: dict[tuple[int, int, int], tuple[int, FakeTile]] = {}
        self.placements: list[dict] = []
        self.item_postings: dict[int, list[int]] = {}
        for tile_index, (position, entries) in enumerate(sorted(tiles.items(), key=lambda item: (item[0][2], item[0][1], item[0][0]))):
            start = len(self.placements)
            for entry in entries:
                ordinal = len(self.placements)
                placement = {
                    "placementOrdinal": ordinal,
                    "itemId": entry["itemId"],
                    "position": list(position),
                    "tileIndex": tile_index,
                    "itemDepth": -1,
                    "source": "inline",
                    **{key: value for key, value in entry.items() if key != "itemId"},
                }
                self.placements.append(placement)
                self.item_postings.setdefault(entry["itemId"], []).append(ordinal)
            self.tiles[position] = (tile_index, FakeTile(*position, start, len(entries)))
        self.mechanics = mechanics or []
        self.header = SimpleNamespace(mechanic_count=len(self.mechanics))

    def find_tile(self, position):
        return self.tiles.get(position)

    def placement(self, ordinal):
        return dict(self.placements[ordinal])

    def mechanic_record(self, index):
        entry = self.mechanics[index]
        return entry["placementOrdinal"], dict(entry["mechanic"])

    def iter_region_tiles(self, lower, upper):
        for position, value in self.tiles.items():
            if all(lower[index] <= position[index] <= upper[index] for index in range(3)):
                yield value

    def item_directory(self, item_id):
        postings = self.item_postings.get(item_id, [])
        all_postings = []
        for current_id in sorted(self.item_postings):
            if current_id == item_id:
                return len(all_postings), len(postings)
            all_postings.extend(self.item_postings[current_id])
        return len(all_postings), 0

    def posting(self, posting_index):
        all_postings = []
        for current_id in sorted(self.item_postings):
            all_postings.extend(self.item_postings[current_id])
        return all_postings[posting_index]


APPEARANCES = {
    100: {"id": 100, "flags": {"bank": {"waypoints": 0}}},
    200: {"id": 200, "flags": {"unpassable": True}},
    201: {"id": 201, "flags": {"unpassable": True, "multiUse": True}},
    300: {"id": 300, "flags": {"avoid": True}},
    400: {"id": 400, "flags": {}},
    500: {"id": 500, "flags": {}},
}


class ReachabilityTests(unittest.TestCase):
    def test_parse_position_and_bounds_reject_invalid_input(self):
        self.assertEqual(parse_position("100,200,7"), (100, 200, 7))
        with self.assertRaises(ReachabilityError):
            parse_position("100,200")
        with self.assertRaises(ReachabilityError):
            Bounds((0, 0, 0), (1000, 1000, 15))

    def test_tile_evidence_walkable_blocked_conditional_and_unresolved(self):
        index = FakeIndex(
            {
                (1, 1, 7): [{"itemId": 100}],
                (2, 1, 7): [{"itemId": 100}, {"itemId": 200}],
                (3, 1, 7): [{"itemId": 100}, {"itemId": 201, "actionId": 900}],
                (4, 1, 7): [{"itemId": 999}],
            }
        )
        self.assertEqual(tile_evidence(index, APPEARANCES, (1, 1, 7))["walkability"], "walkable")
        self.assertEqual(tile_evidence(index, APPEARANCES, (2, 1, 7))["walkability"], "blocked")
        self.assertEqual(tile_evidence(index, APPEARANCES, (3, 1, 7))["walkability"], "conditional")
        self.assertEqual(tile_evidence(index, APPEARANCES, (4, 1, 7))["walkability"], "unresolved")
        self.assertEqual(tile_evidence(index, APPEARANCES, (9, 9, 7))["reasons"], ["missing-tile"])

    def test_missing_floor_is_blocked_when_appearances_are_known(self):
        index = FakeIndex({(1, 1, 7): [{"itemId": 400}]})
        evidence = tile_evidence(index, APPEARANCES, (1, 1, 7))
        self.assertEqual(evidence["floor"], "absent")
        self.assertEqual(evidence["walkability"], "blocked")
        self.assertIn("missing-floor", evidence["reasons"])

    def test_teleport_audit_detects_pair_one_way_self_and_missing_destination(self):
        index = FakeIndex(
            {
                (1, 1, 7): [{"itemId": 100}, {"itemId": 500}],
                (2, 1, 7): [{"itemId": 100}, {"itemId": 500}],
                (3, 1, 7): [{"itemId": 100}, {"itemId": 500}],
                (4, 1, 7): [{"itemId": 100}, {"itemId": 500}],
            },
            mechanics=[
                {"placementOrdinal": 1, "mechanic": {"teleportDestination": [2, 1, 7]}},
                {"placementOrdinal": 3, "mechanic": {"teleportDestination": [1, 1, 7]}},
                {"placementOrdinal": 5, "mechanic": {"teleportDestination": [9, 9, 7]}},
                {"placementOrdinal": 7, "mechanic": {"teleportDestination": [4, 1, 7]}},
            ],
        )
        result = audit_transitions(index, APPEARANCES, {}, sample_limit=20)
        self.assertEqual(result["totalCount"], 4)
        self.assertEqual(result["counts"]["reversePaired"], 2)
        self.assertEqual(result["counts"]["oneWay"], 2)
        self.assertEqual(result["counts"]["selfLoop"], 1)
        self.assertEqual(result["counts"]["invalid"], 2)
        codes = [code for finding in result["findings"] for code in finding["codes"]]
        self.assertIn("missing-destination-tile", codes)
        self.assertIn("self-loop", codes)

    def test_confirmed_route_uses_only_definite_tiles(self):
        index = FakeIndex({(x, 1, 7): [{"itemId": 100}] for x in range(1, 5)})
        result = validate_route(
            index,
            APPEARANCES,
            {},
            bounds=Bounds((1, 1, 7), (4, 1, 7)),
            start=(1, 1, 7),
            goal=(4, 1, 7),
        )
        self.assertEqual(result["status"], "confirmed")
        self.assertEqual(result["pathLength"], 3)

    def test_conditional_route_is_unresolved_not_confirmed(self):
        index = FakeIndex(
            {
                (1, 1, 7): [{"itemId": 100}],
                (2, 1, 7): [{"itemId": 100}, {"itemId": 201, "uniqueId": 42}],
                (3, 1, 7): [{"itemId": 100}],
            }
        )
        result = validate_route(
            index,
            APPEARANCES,
            {},
            bounds=Bounds((1, 1, 7), (3, 1, 7)),
            start=(1, 1, 7),
            goal=(3, 1, 7),
        )
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["conditionalPathPositions"], [[2, 1, 7]])

    def test_static_blocker_makes_route_unreachable(self):
        index = FakeIndex(
            {
                (1, 1, 7): [{"itemId": 100}],
                (2, 1, 7): [{"itemId": 100}, {"itemId": 200}],
                (3, 1, 7): [{"itemId": 100}],
            }
        )
        result = validate_route(
            index,
            APPEARANCES,
            {},
            bounds=Bounds((1, 1, 7), (3, 1, 7)),
            start=(1, 1, 7),
            goal=(3, 1, 7),
        )
        self.assertEqual(result["status"], "unreachable")

    def test_teleport_edge_can_connect_disconnected_tiles(self):
        index = FakeIndex(
            {
                (1, 1, 7): [{"itemId": 100}, {"itemId": 500}],
                (9, 9, 7): [{"itemId": 100}],
            },
            mechanics=[{"placementOrdinal": 1, "mechanic": {"teleportDestination": [9, 9, 7]}}],
        )
        result = validate_route(
            index,
            APPEARANCES,
            {},
            bounds=Bounds((1, 1, 7), (9, 9, 7)),
            start=(1, 1, 7),
            goal=(9, 9, 7),
        )
        self.assertEqual(result["status"], "confirmed")
        self.assertEqual(result["pathLength"], 1)

    def test_reviewed_relative_transition_connects_floors(self):
        index = FakeIndex(
            {
                (1, 1, 7): [{"itemId": 100}, {"itemId": 500}],
                (1, 1, 6): [{"itemId": 100}],
            }
        )
        result = validate_route(
            index,
            APPEARANCES,
            {500: MovementRule(500, "ladder", (0, 0, -1))},
            bounds=Bounds((1, 1, 6), (1, 1, 7)),
            start=(1, 1, 7),
            goal=(1, 1, 6),
        )
        self.assertEqual(result["status"], "confirmed")
        self.assertEqual(result["transitionEdgeCount"], 1)

    def test_node_limit_is_enforced(self):
        index = FakeIndex({(x, 1, 7): [{"itemId": 100}] for x in range(1, 4)})
        with self.assertRaises(ReachabilityError):
            validate_route(
                index,
                APPEARANCES,
                {},
                bounds=Bounds((1, 1, 7), (3, 1, 7)),
                start=(1, 1, 7),
                goal=(3, 1, 7),
                max_nodes=2,
            )

    def test_appearance_and_movement_catalog_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            appearances_path = root / "appearances.json"
            appearances_path.write_text(
                json.dumps(
                    {
                        "format": APPEARANCES_INDEX_FORMAT,
                        "source": {"path": "appearances.dat", "sha256": "0" * 64},
                        "appearances": [{"category": "object", "id": 100, "flags": {"bank": {}}}],
                    }
                ),
                encoding="utf-8",
            )
            appearances, provenance = load_appearances(appearances_path)
            self.assertIn(100, appearances)
            self.assertEqual(provenance["objectCount"], 1)

            catalog_path = root / "movement.json"
            catalog_path.write_text(
                json.dumps(
                    {
                        "format": MOVEMENT_CATALOG_FORMAT,
                        "rules": [{"itemId": 500, "role": "stairs", "offset": [1, 0, -1], "bidirectional": True}],
                    }
                ),
                encoding="utf-8",
            )
            rules, catalog = load_movement_catalog(catalog_path)
            self.assertEqual(rules[500].offset, (1, 0, -1))
            self.assertEqual(catalog["ruleCount"], 1)

    def test_atomic_output_refuses_existing_and_symlink_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "report.json"
            write_json_atomic(target, {"ok": True})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"ok": True})
            with self.assertRaises(FileExistsError):
                write_json_atomic(target, {"ok": False})
            write_json_atomic(target, {"ok": False}, overwrite=True)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"ok": False})
            link = root / "link.json"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlinks are unavailable")
            with self.assertRaises(ReachabilityError):
                write_json_atomic(link, {"ok": True}, overwrite=True)


if __name__ == "__main__":
    unittest.main()
