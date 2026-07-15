from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class AnalyticsSecurityAIRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_011_adds_only_gameplay_analytics(self) -> None:
        self.assertEqual(len(self.registry.modules), 61)
        module = self.registry.modules["gameplay-analytics"]
        self.assertEqual(module["category"], "platform-tooling")
        self.assertEqual(module["lifecycle"]["status"], "inventory")
        self.assertEqual(module["relationships"]["depends_on"], ["lua-runtime"])
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

    def test_forbidden_planned_systems_are_not_registered(self) -> None:
        for module_id in (
            "security-analytics",
            "chat-safety-intelligence",
            "ai-investigation",
            "ai-agent-tooling",
        ):
            self.assertNotIn(module_id, self.registry.modules)

    def test_existing_security_and_platform_boundaries_remain_stable(self) -> None:
        for module_id in (
            "account-authentication",
            "sanctions",
            "protocol",
            "upstream-intelligence",
            "otbm-tooling",
            "physical-client-e2e",
        ):
            self.assertIn(module_id, self.registry.modules)

        account_auth = self.registry.modules["account-authentication"]
        self.assertIn("src/security/argon.*", account_auth["paths"]["server"])
        self.assertIn("src/security/login_session_manager.*", account_auth["paths"]["server"])
        self.assertIn("security analytics", self.registry.modules["sanctions"]["scope"]["excludes"])

    def test_gameplay_analytics_paths_map_to_single_new_boundary(self) -> None:
        cases = {
            "data-otservbr-global/scripts/config/gameplay_analytics.lua",
            "data-otservbr-global/scripts/lib/gameplay_analytics.lua",
            "data-otservbr-global/scripts/lib/gameplay_analytics_metrics.lua",
            "data-otservbr-global/scripts/systems/gameplay_analytics.lua",
            "tools/analytics/test_analytics.py",
            ".github/workflows/gameplay-analytics-dry-run.yml",
            "docs/systems/gameplay-analytics-dry-run.md",
        }
        for path in cases:
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertIn("gameplay-analytics", ids)

    def test_dependency_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
