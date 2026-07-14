#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry, load_json
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceDecompositionTests(unittest.TestCase):
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

    def test_multi_module_mapping_is_sorted_and_remains_discovery_only(self) -> None:
        candidate = {
            "paths": [
                "src/lua/scripts/lua_environment.hpp",
                "src/canary_server.cpp",
                "src/config/configmanager.cpp",
            ],
            "module_ids": [],
            "mapped_paths": [],
            "unmapped_paths": [],
            "triage_status": "needs-triage",
            "decision_state": "none",
        }

        map_candidate(candidate, self.registry, self.server_source)

        self.assertEqual(candidate["mapping_state"], "mapped")
        self.assertEqual(candidate["module_ids"], sorted(candidate["module_ids"]))
        self.assertIn("engine-runtime-lifecycle", candidate["module_ids"])
        self.assertIn("configuration", candidate["module_ids"])
        self.assertIn("lua-runtime", candidate["module_ids"])
        self.assertNotIn("protocol", candidate["module_ids"])
        self.assertFalse(
            any(row["bucket"] == "client" for row in candidate["mapped_paths"])
        )
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
        self.assertEqual(candidate["triage_status"], "needs-triage")
        self.assertEqual(candidate["decision_state"], "none")


if __name__ == "__main__":
    unittest.main()
