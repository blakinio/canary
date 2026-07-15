#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry, load_json
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceAnalyticsSecurityAITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)
        config = load_json(cls.root / "docs/agents/upstream/registry/sources.yaml")
        cls.server_source = next(source for source in config["sources"] if source["id"] == "opentibiabr-canary")
        cls.client_source = next(source for source in config["sources"] if source["id"] == "opentibiabr-otclient")

    @staticmethod
    def candidate(paths: list[str]) -> dict:
        return {
            "paths": paths,
            "module_ids": [],
            "mapped_paths": [],
            "unmapped_paths": [],
            "triage_status": "needs-triage",
            "decision_state": "none",
        }

    def test_server_source_maps_gameplay_analytics_without_inventing_security_ai(self) -> None:
        row = self.candidate([
            "data-otservbr-global/scripts/config/gameplay_analytics.lua",
            "data-otservbr-global/scripts/lib/gameplay_analytics.lua",
            "data-otservbr-global/scripts/systems/gameplay_analytics.lua",
            "tools/analytics/test_analytics.py",
        ])
        map_candidate(row, self.registry, self.server_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertIn("gameplay-analytics", row["module_ids"])
        for forbidden in (
            "security-analytics",
            "chat-safety-intelligence",
            "ai-investigation",
            "ai-agent-tooling",
        ):
            self.assertNotIn(forbidden, row["module_ids"])
        self.assertFalse(any(match["bucket"] == "client" for match in row["mapped_paths"]))
        self.assertEqual(row["unmapped_paths"], [])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")

    def test_client_source_does_not_inherit_gameplay_analytics_from_protocol_paths(self) -> None:
        row = self.candidate([
            "modules/game_features/features.lua",
            "src/framework/net/protocol.cpp",
        ])
        map_candidate(row, self.registry, self.client_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertIn("protocol", row["module_ids"])
        self.assertIn("protocol-compatibility", row["module_ids"])
        self.assertIn("network-transport", row["module_ids"])
        self.assertNotIn("gameplay-analytics", row["module_ids"])
        self.assertTrue(all(match["bucket"] == "client" for match in row["mapped_paths"]))
        self.assertEqual(row["unmapped_paths"], [])


if __name__ == "__main__":
    unittest.main()
