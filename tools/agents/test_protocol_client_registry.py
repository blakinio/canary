from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class ProtocolClientRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_010_records_are_bounded(self) -> None:
        self.assertGreaterEqual(len(self.registry.modules), 60)
        expected_dependencies = {
            "network-transport": [],
            "login-protocol": ["account-authentication", "network-transport"],
            "protocol-compatibility": [],
            "protocol-session-handoff": ["protocol-compatibility"],
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
            "game-protocol",
            "game-session",
            "connection-session-release",
            "protocol-opcodes",
            "client-game-features",
        ):
            self.assertNotIn(merged_or_deferred, self.registry.modules)

    def test_existing_protocol_boundaries_remain_stable(self) -> None:
        protocol = self.registry.modules["protocol"]
        self.assertEqual(protocol["lifecycle"]["status"], "mapped")
        self.assertEqual(protocol["maturity"]["implementation"], "mapped")
        self.assertEqual(protocol["maturity"]["evidence"], "inventory")
        self.assertEqual(protocol["maturity"]["protocol"], "partial")
        self.assertEqual(protocol["maturity"]["automated_tests"], "unit")

        for module_id in (
            "physical-client-e2e",
            "account-authentication",
            "account-lifecycle",
            "character-lifecycle",
            "player-persistence",
        ):
            self.assertIn(module_id, self.registry.modules)

    def test_server_protocol_paths_map_to_narrow_modules_and_umbrella(self) -> None:
        cases = {
            "src/server/network/connection/connection.cpp": {"network-transport"},
            "src/server/network/protocol/protocol.cpp": {"network-transport", "protocol"},
            "src/server/network/protocol/transport_codec.cpp": {"network-transport", "protocol"},
            "src/server/network/protocol/protocollogin.cpp": {"login-protocol", "protocol"},
            "src/server/network/protocol/protocol_profile.cpp": {"protocol-compatibility", "protocol"},
            "src/server/network/protocol/protocol_session_hint.cpp": {"protocol-session-handoff", "protocol"},
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_client_protocol_paths_map_to_narrow_modules_and_umbrella(self) -> None:
        cases = {
            "src/framework/net/protocol.cpp": {"network-transport", "protocol"},
            "src/framework/net/connection.cpp": {"network-transport", "protocol"},
            "modules/gamelib/protocollogin.lua": {"login-protocol", "protocol"},
            "modules/game_features/features.lua": {"protocol-compatibility", "protocol"},
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertTrue(expected.issubset(set(ids)))

    def test_game_protocol_remains_under_existing_umbrella(self) -> None:
        server_ids = [
            module_id
            for module_id, _, _ in self.registry.matched_modules(
                "src/server/network/protocol/protocolgame.cpp"
            )
        ]
        self.assertIn("protocol", server_ids)
        self.assertNotIn("login-protocol", server_ids)
        self.assertNotIn("protocol-session-handoff", server_ids)

        client_ids = [
            module_id
            for module_id, _, _ in self.registry.matched_modules("src/client/protocolgame.cpp")
        ]
        self.assertIn("protocol", client_ids)
        for narrow in (
            "login-protocol",
            "protocol-compatibility",
            "protocol-session-handoff",
        ):
            self.assertNotIn(narrow, client_ids)

    def test_dependency_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
