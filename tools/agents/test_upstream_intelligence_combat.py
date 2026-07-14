#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry, load_json
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceCombatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)
        config = load_json(cls.root / "docs/agents/upstream/registry/sources.yaml")
        cls.server_source = next(
            source
            for source in config["sources"]
            if source["id"] == "opentibiabr-canary"
        )
        cls.client_source = next(
            source
            for source in config["sources"]
            if source["id"] == "opentibiabr-otclient"
        )

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

    def test_server_source_maps_combat_conditions_and_weapons(self) -> None:
        candidate = self.candidate(
            [
                "src/creatures/combat/combat.cpp",
                "src/creatures/combat/condition.cpp",
                "src/creatures/combat/spells/spell.cpp",
                "src/items/weapons/weapons.cpp",
                "data/scripts/weapons/example.lua",
                "src/creatures/players/vocations/vocation.cpp",
                "src/creatures/players/components/weapon_proficiency.cpp",
            ]
        )

        map_candidate(candidate, self.registry, self.server_source)

        self.assertEqual(candidate["mapping_state"], "mapped")
        self.assertEqual(candidate["module_ids"], sorted(candidate["module_ids"]))
        for expected in (
            "combat",
            "combat-conditions",
            "spells",
            "vocations",
            "weapon-proficiency",
            "weapons",
        ):
            self.assertIn(expected, candidate["module_ids"])
        self.assertNotIn("protocol", candidate["module_ids"])
        self.assertFalse(
            any(row["bucket"] == "client" for row in candidate["mapped_paths"])
        )
        self.assertEqual(candidate["unmapped_paths"], [])
        self.assertEqual(candidate["triage_status"], "needs-triage")
        self.assertEqual(candidate["decision_state"], "none")
        self.assertEqual(
            candidate["mapped_paths"],
            sorted(
                candidate["mapped_paths"],
                key=lambda row: (
                    row["path"],
                    row["module_id"],
                    row["bucket"],
                    row["pattern"],
                ),
            ),
        )

    def test_client_source_does_not_consume_server_combat_paths(self) -> None:
        candidate = self.candidate(
            [
                "src/creatures/combat/condition.cpp",
                "src/items/weapons/weapons.cpp",
            ]
        )

        map_candidate(candidate, self.registry, self.client_source)

        self.assertEqual(candidate["mapping_state"], "unmapped")
        self.assertEqual(candidate["module_ids"], [])
        self.assertEqual(candidate["mapped_paths"], [])
        self.assertEqual(
            candidate["unmapped_paths"],
            [
                "src/creatures/combat/condition.cpp",
                "src/items/weapons/weapons.cpp",
            ],
        )
        self.assertEqual(candidate["triage_status"], "needs-triage")
        self.assertEqual(candidate["decision_state"], "none")


if __name__ == "__main__":
    unittest.main()
