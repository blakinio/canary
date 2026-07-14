from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class ItemsRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_007_records_are_bounded(self) -> None:
        self.assertGreaterEqual(len(self.registry.modules), 49)
        expected_dependencies = {
            "item-definitions": [],
            "item-instances": ["item-definitions"],
            "containers": ["item-instances"],
            "item-decay": ["engine-scheduler", "item-instances"],
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
            "item-movement",
            "item-stacking",
            "item-attributes",
            "item-serialization",
            "depots",
            "inbox-mailbox",
            "reward-containers",
            "stash-managed-containers",
            "account-coins",
            "npc-trade",
        ):
            self.assertNotIn(merged_or_deferred, self.registry.modules)

    def test_existing_economy_boundaries_remain_stable(self) -> None:
        for module_id in (
            "market",
            "imbuements",
            "exaltation-forge",
            "weapons",
            "boss-encounters",
            "player-persistence",
            "protocol",
        ):
            self.assertIn(module_id, self.registry.modules)

    def test_item_paths_map_to_narrow_modules(self) -> None:
        cases = {
            "src/items/items.cpp": {"item-definitions"},
            "src/items/functions/item/item_parse.cpp": {"item-definitions"},
            "data/items/items.xml": {"item-definitions"},
            "src/items/item.cpp": {"item-instances"},
            "src/items/functions/item/attribute.cpp": {"item-instances"},
            "src/items/containers/container.cpp": {"containers"},
            "src/items/cylinder.cpp": {"containers"},
            "src/items/decay/decay.cpp": {"item-decay"},
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_item_movement_does_not_create_fake_module(self) -> None:
        ids = [
            module_id
            for module_id, _, _ in self.registry.matched_modules("src/game/game.cpp")
        ]
        self.assertNotIn("item-movement", ids)
        self.assertNotIn("containers", ids)
        self.assertNotIn("item-instances", ids)

    def test_dependency_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
