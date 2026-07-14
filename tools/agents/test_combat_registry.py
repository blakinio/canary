from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class CombatRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_005_records_are_bounded(self) -> None:
        self.assertEqual(len(self.registry.modules), 41)
        expected_dependencies = {
            "combat-conditions": ["combat"],
            "weapons": ["combat"],
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
            "combat-targeting",
            "combat-permissions",
            "combat-formulas",
            "damage-healing",
            "combat-mitigation",
            "combat-ordering",
            "combat-areas",
            "combat-chains",
            "critical-leech",
            "buffs-debuffs",
            "damage-over-time",
            "regeneration",
            "mana-shield",
            "condition-persistence",
            "melee-weapons",
            "distance-weapons",
            "wands",
            "weapon-permissions",
            "weapon-formulas",
            "weapon-resource-consumption",
            "vocation-combat-modifiers",
            "monk-harmony",
            "monk-virtues",
        ):
            self.assertNotIn(merged_or_covered, self.registry.modules)

    def test_existing_combat_boundaries_remain_stable(self) -> None:
        combat = self.registry.modules["combat"]
        self.assertEqual(combat["lifecycle"]["status"], "mapped")
        self.assertEqual(
            combat["paths"]["server"],
            ["src/creatures/combat/**", "src/game/functions/**"],
        )

        spells = self.registry.modules["spells"]
        self.assertEqual(spells["lifecycle"]["status"], "mapped")
        self.assertEqual(spells["relationships"]["depends_on"], ["combat"])

        self.assertIn("vocations", self.registry.modules)
        self.assertIn("weapon-proficiency", self.registry.modules)
        self.assertIn("character-progression", self.registry.modules)
        self.assertIn("player-persistence", self.registry.modules)

    def test_server_paths_keep_broad_and_narrow_discovery(self) -> None:
        cases = {
            "src/creatures/combat/condition.cpp": {
                "combat",
                "combat-conditions",
            },
            "src/items/weapons/weapons.cpp": {"weapons"},
            "data/scripts/weapons/example.lua": {"weapons"},
            "src/creatures/combat/combat.cpp": {"combat"},
            "src/creatures/combat/spells/spell.cpp": {"combat", "spells"},
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [
                    module_id
                    for module_id, _, _ in self.registry.matched_modules(path)
                ]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_combat_helpers_remain_inside_umbrella(self) -> None:
        combat_ids = [
            module_id
            for module_id, _, _ in self.registry.matched_modules(
                "src/creatures/combat/combat.cpp"
            )
        ]
        self.assertEqual(combat_ids, sorted(combat_ids))
        self.assertIn("combat", combat_ids)
        self.assertNotIn("combat-conditions", combat_ids)
        self.assertNotIn("weapons", combat_ids)

    def test_dependency_graph_remains_valid(self) -> None:
        result = self.registry.validate()
        self.assertEqual(result.errors, ())


if __name__ == "__main__":
    unittest.main()
