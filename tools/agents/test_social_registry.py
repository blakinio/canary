from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class SocialRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_009_records_are_bounded(self) -> None:
        self.assertGreaterEqual(len(self.registry.modules), 56)
        expected_dependencies = {
            "chat-communication": ["character-lifecycle"],
            "parties": ["character-lifecycle"],
            "guilds": ["character-lifecycle", "database-connection"],
            "sanctions": ["database-connection"],
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
            "public-chat",
            "private-chat",
            "party-chat",
            "guild-chat",
            "shared-experience",
            "guild-wars",
            "direct-messaging",
            "moderation-audit-platform",
            "player-groups-permissions",
            "chat-safety-intelligence",
            "security-analytics",
            "ai-investigation",
        ):
            self.assertNotIn(merged_or_deferred, self.registry.modules)

    def test_existing_social_and_persistence_boundaries_remain_stable(self) -> None:
        for module_id in (
            "account-authentication",
            "account-lifecycle",
            "character-lifecycle",
            "npcs",
            "protocol",
            "player-persistence",
            "world-persistence",
        ):
            self.assertIn(module_id, self.registry.modules)

    def test_social_paths_map_to_narrow_modules(self) -> None:
        cases = {
            "src/creatures/interactions/chat.cpp": {"chat-communication"},
            "src/creatures/players/grouping/party.cpp": {"parties"},
            "src/creatures/players/grouping/guild.cpp": {"guilds"},
            "src/io/ioguild.cpp": {"guilds", "player-persistence", "world-persistence"},
            "src/creatures/players/management/ban.cpp": {"sanctions"},
            "data/chatchannels/chatchannels.xml": {"chat-communication"},
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_protocol_paths_do_not_move_into_social_modules(self) -> None:
        ids = [
            module_id
            for module_id, _, _ in self.registry.matched_modules(
                "src/server/network/protocol/protocolgame.cpp"
            )
        ]
        self.assertIn("protocol", ids)
        for social in ("chat-communication", "parties", "guilds", "sanctions"):
            self.assertNotIn(social, ids)

    def test_dependency_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
