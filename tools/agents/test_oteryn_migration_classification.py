from __future__ import annotations

import re
import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry


class OterynMigrationClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)
        cls.report = (
            cls.root
            / "docs/agents/real-tibia/TSD_013_OTERYN_MIGRATION_CLASSIFICATION_REPORT.md"
        ).read_text(encoding="utf-8")

    def test_classification_covers_live_canonical_registry_without_id_copy(self) -> None:
        self.assertEqual(len(self.registry.modules), 62)
        marker = re.search(
            r"<!-- TSD013_CLASSIFICATION\n"
            r"registry_snapshot_sha: ([0-9a-f]{40})\n"
            r"registry_total: (\d+)\n"
            r"scope: ([A-Z_]+)\n"
            r"disposition: ([A-Z_]+)\n"
            r"-->",
            self.report,
        )
        self.assertIsNotNone(marker)
        assert marker is not None
        self.assertEqual(int(marker.group(2)), len(self.registry.modules))
        self.assertEqual(marker.group(3), "ALL_CANONICAL_MODULES")
        self.assertEqual(marker.group(4), "REVALIDATE")

        # The report must not become a second per-module registry.
        module_id_mentions = sum(
            1 for module_id in self.registry.modules if f"`{module_id}`" in self.report
        )
        self.assertLess(module_id_mentions, len(self.registry.modules))

    def test_revalidate_is_not_presented_as_readiness_or_copy_authorization(self) -> None:
        required_limits = (
            "does **not** mean",
            "copy the implementation",
            "port the implementation as-is",
            "declare the module Oteryn-ready",
            "No code transfer",
            "no write to an Oteryn repository",
        )
        for text in required_limits:
            with self.subTest(text=text):
                self.assertIn(text, self.report)

    def test_target_architecture_is_required_for_stronger_disposition(self) -> None:
        self.assertIn("No target architecture contract is registered", self.report)
        self.assertIn("explicit Oteryn repository/architecture contract", self.report)
        self.assertIn("the module remains `REVALIDATE`", self.report)

    def test_registry_graph_remains_valid(self) -> None:
        self.assertEqual(self.registry.validate().errors, ())


if __name__ == "__main__":
    unittest.main()
