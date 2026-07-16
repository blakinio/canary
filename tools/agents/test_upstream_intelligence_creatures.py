#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry, load_json
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceCreatureTests(unittest.TestCase):
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

    def test_server_source_maps_creature_encounter_and_raid_boundaries(self) -> None:
        row = self.candidate([
            "src/creatures/monsters/monsters.cpp",
            "src/creatures/monsters/monster.cpp",
            "data-otservbr-global/monster/bosses/example.lua",
            "data/scripts/systems/reward_chest.lua",
            "src/lua/creature/raids.cpp",
            "data/raids/raids.xml",
            "data-otservbr-global/scripts/raids/example.lua",
        ])
        map_candidate(row, self.registry, self.server_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertEqual(row["module_ids"], sorted(row["module_ids"]))
        for expected in ("boss-encounters", "creature-ai", "creature-definitions", "raids", "spawns"):
            self.assertIn(expected, row["module_ids"])
        self.assertNotIn("protocol", row["module_ids"])
        self.assertFalse(any(match["bucket"] == "client" for match in row["mapped_paths"]))
        self.assertEqual(row["unmapped_paths"], [])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")
        self.assertEqual(row["mapped_paths"], sorted(row["mapped_paths"], key=lambda match: (match["path"], match["module_id"], match["bucket"], match["pattern"])))

    def test_client_source_does_not_consume_server_creature_modules(self) -> None:
        row = self.candidate([
            "src/creatures/monsters/monster.cpp",
            "src/lua/creature/raids.cpp",
        ])
        map_candidate(row, self.registry, self.client_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertEqual(row["module_ids"], ["protocol"])
        self.assertTrue(all(match["bucket"] == "client" for match in row["mapped_paths"]))
        for invalid in ("creature-ai", "creature-definitions", "raids"):
            self.assertNotIn(invalid, row["module_ids"])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")


if __name__ == "__main__":
    unittest.main()
