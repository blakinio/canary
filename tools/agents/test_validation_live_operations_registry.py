from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class ValidationLiveOperationsRegistryDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_tsd_012_adds_only_deployment_operations(self) -> None:
        self.assertEqual(len(self.registry.modules), 62)
        module = self.registry.modules["deployment-operations"]
        self.assertEqual(module["category"], "platform-tooling")
        self.assertEqual(module["lifecycle"]["status"], "inventory")
        self.assertEqual(module["relationships"]["depends_on"], ["build-system"])
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

    def test_existing_validation_platform_boundaries_remain_stable(self) -> None:
        otbm = self.registry.modules["otbm-tooling"]
        self.assertEqual(otbm["lifecycle"]["status"], "active")
        self.assertEqual(otbm["maturity"]["implementation"], "mapped")
        self.assertEqual(otbm["maturity"]["evidence"], "audited")

        e2e = self.registry.modules["physical-client-e2e"]
        self.assertEqual(e2e["lifecycle"]["status"], "active")
        self.assertEqual(e2e["maturity"]["implementation"], "partial")

        upstream = self.registry.modules["upstream-intelligence"]
        self.assertEqual(upstream["lifecycle"]["status"], "active")
        self.assertEqual(upstream["maturity"]["implementation"], "partial")

    def test_duplicate_validation_umbrellas_are_not_registered(self) -> None:
        for module_id in (
            "quest-map-validation",
            "otbm-reachability",
            "otbm-spawn-npc-validation",
            "otbm-storage-graph",
            "otbm-semantic-diff",
            "otbm-geometry-audit",
            "validation-platform",
            "second-physical-client-e2e",
            "second-upstream-intelligence",
        ):
            self.assertNotIn(module_id, self.registry.modules)

    def test_deployment_paths_map_to_new_boundary(self) -> None:
        for path in (
            "tools/deploy/run_canary_deployment.py",
            "tools/deploy/release_manager.py",
            "docs/systems/ai-content-deployment.md",
        ):
            with self.subTest(path=path):
                ids = [module_id for module_id, _, _ in self.registry.matched_modules(path)]
                self.assertEqual(ids, sorted(ids))
                self.assertIn("deployment-operations", ids)

    def test_dependency_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
