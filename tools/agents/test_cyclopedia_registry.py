from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class CyclopediaRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_004_records_are_bounded(self) -> None:
        self.assertGreaterEqual(len(self.registry.modules), 39)
        expected_dependencies = {
            "bestiary": ["cyclopedia", "player-persistence"],
            "bosstiary": ["cyclopedia", "player-persistence"],
            "cyclopedia-character": ["cyclopedia", "player-persistence"],
            "titles": ["cyclopedia-character", "player-persistence"],
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
            self.assertNotIn("modules/game_cyclopedia/**", module["paths"]["client"])
            self.assertNotIn("data/monster/**", module["paths"]["data"])
            self.assertNotIn("data-otservbr-global/monster/**", module["paths"]["data"])

        for merged_or_covered in (
            "cyclopedia-items",
            "cyclopedia-map",
            "cyclopedia-houses",
            "outfits",
            "mounts",
            "familiars",
            "podiums-displays",
        ):
            self.assertNotIn(merged_or_covered, self.registry.modules)

    def test_existing_cyclopedia_boundaries_remain_stable(self) -> None:
        cyclopedia = self.registry.modules["cyclopedia"]
        self.assertEqual(cyclopedia["lifecycle"]["status"], "mapped")
        self.assertEqual(
            cyclopedia["paths"]["server"],
            [
                "src/io/iobestiary.*",
                "src/creatures/players/**",
                "src/server/network/protocol/**",
            ],
        )
        self.assertEqual(cyclopedia["paths"]["client"], ["modules/game_cyclopedia/**"])

        charms = self.registry.modules["charms"]
        self.assertEqual(charms["lifecycle"]["status"], "inventory")
        self.assertEqual(
            charms["relationships"]["depends_on"],
            ["combat", "cyclopedia", "player-persistence", "protocol"],
        )

        self.assertIn("houses", self.registry.modules)
        self.assertIn("achievements", self.registry.modules)
        self.assertIn("protocol", self.registry.modules)

    def test_server_paths_keep_broad_and_narrow_discovery(self) -> None:
        cases = {
            "src/io/iobestiary.cpp": {"bestiary", "cyclopedia"},
            "src/io/io_bosstiary.cpp": {"bosstiary"},
            "src/creatures/players/components/player_cyclopedia.cpp": {
                "cyclopedia",
                "cyclopedia-character",
                "player-persistence",
            },
            "src/creatures/players/components/player_title.cpp": {
                "cyclopedia",
                "player-persistence",
                "titles",
            },
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [
                    module_id
                    for module_id, _, _ in self.registry.matched_modules(path)
                ]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_client_paths_are_narrow_and_overlapping(self) -> None:
        cases = {
            "modules/game_cyclopedia/tab/bestiary/bestiary.lua": {
                "bestiary",
                "cyclopedia",
                "protocol",
            },
            "modules/game_cyclopedia/tab/bosstiary/bosstiary.lua": {
                "bosstiary",
                "cyclopedia",
                "protocol",
            },
            "modules/game_cyclopedia/tab/character/character.lua": {
                "cyclopedia",
                "cyclopedia-character",
                "protocol",
                "titles",
            },
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [
                    module_id
                    for module_id, _, _ in self.registry.matched_modules(path)
                ]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_dependency_graph_remains_valid(self) -> None:
        result = self.registry.validate()
        self.assertEqual(result.errors, ())


if __name__ == "__main__":
    unittest.main()
