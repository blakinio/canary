#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry
from upstream_intelligence_candidates import map_candidate


class UpstreamIntelligenceDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.registry = Registry.load(cls.root)

    def test_multi_module_mapping_is_sorted_and_remains_discovery_only(self) -> None:
        candidate = {
            "paths": [
                "src/lua/scripts/lua_environment.hpp",
                "src/canary_server.cpp",
            ],
            "module_ids": [],
            "mapped_paths": [],
            "unmapped_paths": [],
            "triage_status": "needs-triage",
        }

        map_candidate(candidate, self.registry)

        self.assertEqual(candidate["mapping_state"], "mapped")
        self.assertEqual(candidate["module_ids"], sorted(candidate["module_ids"]))
        self.assertIn("engine-runtime-lifecycle", candidate["module_ids"])
        self.assertIn("lua-runtime", candidate["module_ids"])
        self.assertIn("protocol", candidate["module_ids"])
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


if __name__ == "__main__":
    unittest.main()
