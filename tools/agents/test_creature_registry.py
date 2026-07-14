from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class CreatureRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_006_records_are_bounded(self) -> None:
        self.assertEqual(len(self.registry.modules), 45)
        expected_dependencies = {
            "creature-definitions": [],
            "creature-ai": ["creature-definitions"],
            "boss-encounters": ["creature-definitions", "player-persistence"],
            "raids": ["creature-definitions", "engine-scheduler"],
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

        for merged_or_covered in (
            "monster-types",
            "monster-spells",
            "monster-loot",
            "monster-summons",
            "target-selection",
            "pathfinding-fleeing",
            "spawn-placement",
            "dynamic-creation",
            "hunting-tasks",
            "bestiary-credit",
            "bosstiary-credit",
            "boss-definitions",
            "boss-ai",
            "boss-reward-eligibility",
            "boss-score",
            "boss-loot",
            "boss-cooldowns",
            "raid-scheduling",
            "raid-announcements",
            "raid-spawns",
        ):
            self.assertNotIn(merged_or_covered, self.registry.modules)

    def test_existing_hunting_and_spawn_boundaries_remain_stable(self) -> None:
        self.assertEqual(self.registry.modules["spawns"]["lifecycle"]["status"], "inventory")
        self.assertEqual(self.registry.modules["prey"]["lifecycle"]["status"], "inventory")
        self.assertEqual(self.registry.modules["bestiary"]["lifecycle"]["status"], "inventory")
        self.assertEqual(self.registry.modules["bosstiary"]["lifecycle"]["status"], "inventory")

    def test_paths_map_to_narrow_creature_modules(self) -> None:
        cases = {
            "src/creatures/monsters/monsters.cpp": {"creature-definitions"},
            "src/creatures/monsters/monster.cpp": {"creature-ai"},
            "data-otservbr-global/monster/bosses/example.lua": {"creature-definitions"},
            "data/scripts/systems/reward_chest.lua": {"boss-encounters"},
            "src/lua/creature/raids.cpp": {"lua-runtime", "raids"},
            "data/raids/raids.xml": {"raids"},
            "data-otservbr-global/scripts/raids/example.lua": {"raids", "spawns"},
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_dependency_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
