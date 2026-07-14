#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry, load_json
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceWorldTests(unittest.TestCase):
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

    def test_server_source_maps_world_boundaries(self) -> None:
        row = self.candidate([
            "src/map/map.cpp",
            "src/items/tile.cpp",
            "src/io/iomap.cpp",
            "src/game/zones/zone.cpp",
            "src/game/instance/instance_manager.cpp",
        ])
        map_candidate(row, self.registry, self.server_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertEqual(row["module_ids"], sorted(row["module_ids"]))
        for expected in ("instances", "world-map-runtime", "world-zones"):
            self.assertIn(expected, row["module_ids"])
        self.assertNotIn("protocol", row["module_ids"])
        self.assertFalse(any(match["bucket"] == "client" for match in row["mapped_paths"]))
        self.assertEqual(row["unmapped_paths"], [])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")
        self.assertEqual(
            row["mapped_paths"],
            sorted(
                row["mapped_paths"],
                key=lambda match: (
                    match["path"],
                    match["module_id"],
                    match["bucket"],
                    match["pattern"],
                ),
            ),
        )

    def test_client_source_preserves_protocol_without_server_world_modules(self) -> None:
        row = self.candidate([
            "src/map/map.cpp",
            "src/game/zones/zone.cpp",
            "src/game/instance/instance_manager.cpp",
        ])
        map_candidate(row, self.registry, self.client_source)
        self.assertEqual(row["mapping_state"], "mapped")
        self.assertEqual(row["module_ids"], ["protocol"])
        self.assertTrue(all(match["bucket"] == "client" for match in row["mapped_paths"]))
        for invalid in ("instances", "world-map-runtime", "world-zones"):
            self.assertNotIn(invalid, row["module_ids"])
        self.assertEqual(row["unmapped_paths"], [])
        self.assertEqual(row["triage_status"], "needs-triage")
        self.assertEqual(row["decision_state"], "none")


if __name__ == "__main__":
    unittest.main()
