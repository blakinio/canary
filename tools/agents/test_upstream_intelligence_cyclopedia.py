#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry, load_json
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceCyclopediaTests(unittest.TestCase):
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

    def test_server_source_maps_only_server_cyclopedia_boundaries(self) -> None:
        candidate = self.candidate(
            [
                "src/io/iobestiary.cpp",
                "src/io/io_bosstiary.cpp",
                "src/creatures/players/components/player_cyclopedia.cpp",
                "src/creatures/players/components/player_title.cpp",
            ]
        )

        map_candidate(candidate, self.registry, self.server_source)

        self.assertEqual(candidate["mapping_state"], "mapped")
        self.assertEqual(candidate["module_ids"], sorted(candidate["module_ids"]))
        for expected in (
            "bestiary",
            "bosstiary",
            "cyclopedia",
            "cyclopedia-character",
            "player-persistence",
            "titles",
        ):
            self.assertIn(expected, candidate["module_ids"])
        self.assertNotIn("protocol", candidate["module_ids"])
        self.assertFalse(
            any(row["bucket"] == "client" for row in candidate["mapped_paths"])
        )
        self.assertEqual(candidate["unmapped_paths"], [])
        self.assertEqual(candidate["triage_status"], "needs-triage")
        self.assertEqual(candidate["decision_state"], "none")

    def test_client_source_maps_narrow_tabs_without_server_ownership(self) -> None:
        candidate = self.candidate(
            [
                "modules/game_cyclopedia/tab/bestiary/bestiary.lua",
                "modules/game_cyclopedia/tab/bosstiary/bosstiary.lua",
                "modules/game_cyclopedia/tab/character/character.lua",
            ]
        )

        map_candidate(candidate, self.registry, self.client_source)

        self.assertEqual(candidate["mapping_state"], "mapped")
        self.assertEqual(candidate["module_ids"], sorted(candidate["module_ids"]))
        for expected in (
            "bestiary",
            "bosstiary",
            "cyclopedia",
            "cyclopedia-character",
            "protocol",
            "titles",
        ):
            self.assertIn(expected, candidate["module_ids"])
        self.assertNotIn("player-persistence", candidate["module_ids"])
        self.assertFalse(
            any(row["bucket"] == "server" for row in candidate["mapped_paths"])
        )
        self.assertEqual(candidate["unmapped_paths"], [])
        self.assertEqual(candidate["triage_status"], "needs-triage")
        self.assertEqual(candidate["decision_state"], "none")


if __name__ == "__main__":
    unittest.main()
