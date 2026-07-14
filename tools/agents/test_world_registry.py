from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class WorldRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_008_records_are_bounded(self) -> None:
        self.assertEqual(len(self.registry.modules), 52)
        expected_dependencies = {
            "world-map-runtime": ["item-definitions", "item-instances"],
            "world-zones": ["world-map-runtime"],
            "instances": ["world-map-runtime"],
        }
        for module_id, dependencies in expected_dependencies.items():
            module = self.registry.modules[module_id]
            self.assertEqual(module["lifecycle"]["status"], "inventory")
            self.assertEqual(module["maturity"]["implementation"], "inventory")
            self.assertEqual(module["maturity"]["evidence"], "inventory")
            for dimension in (
                "persistence",
                "protocol",
                "automated_tests",
                "runtime_validation",
                "gameplay_e2e",
            ):
                self.assertEqual(module["maturity"][dimension], "not-assessed")
            self.assertEqual(module["relationships"]["depends_on"], dependencies)
            self.assertNotIn("src/**", module["paths"]["server"])

        for merged_or_deferred in (
            "map-loading",
            "tiles",
            "movement",
            "pathfinding",
            "visibility-spectators",
            "towns",
            "waypoints",
            "teleports",
            "floor-transitions",
            "npc-travel",
            "boats-carpet-travel",
            "otbm-runtime-loader",
            "instance-arena",
        ):
            self.assertNotIn(merged_or_deferred, self.registry.modules)

    def test_existing_world_boundaries_remain_stable(self) -> None:
        for module_id in (
            "quests",
            "npcs",
            "houses",
            "otbm-tooling",
            "raids",
            "spawns",
            "containers",
            "item-instances",
            "world-persistence",
            "physical-client-e2e",
        ):
            self.assertIn(module_id, self.registry.modules)

    def test_world_paths_map_to_narrow_modules(self) -> None:
        cases = {
            "src/map/map.cpp": {"world-map-runtime"},
            "src/map/mapcache.cpp": {"world-map-runtime"},
            "src/map/spectators.cpp": {"world-map-runtime"},
            "src/map/utils/astarnodes.cpp": {"world-map-runtime"},
            "src/items/tile.cpp": {"world-map-runtime"},
            "src/io/iomap.cpp": {"world-map-runtime"},
            "src/game/zones/zone.cpp": {"world-zones"},
            "src/game/instance/instance_manager.cpp": {"instances"},
            "tests/unit/game/instance/instance_manager_test.cpp": {"combat", "instances"},
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_house_and_persistence_paths_do_not_move_into_runtime_map(self) -> None:
        house_ids = [
            module_id
            for module_id, _, _ in self.registry.matched_modules("src/map/house/house.cpp")
        ]
        self.assertIn("houses", house_ids)
        self.assertNotIn("world-map-runtime", house_ids)

        persistence_ids = [
            module_id
            for module_id, _, _ in self.registry.matched_modules("src/io/iomapserialize.cpp")
        ]
        self.assertIn("world-persistence", persistence_ids)
        self.assertNotIn("world-map-runtime", persistence_ids)

    def test_dependency_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
