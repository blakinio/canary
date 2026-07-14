#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from real_tibia_registry_lib import Registry
from upstream_intelligence_candidates import map_candidate


class TibiaSystemDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = Registry.load(ROOT)

    def test_bootstrap_registry_is_valid_and_bounded(self) -> None:
        result = self.registry.validate()
        self.assertEqual(result.errors, ())
        self.assertEqual(len(self.registry.modules), 22)
        self.assertIn("engine-foundation", self.registry.categories)
        self.assertEqual(
            {
                "configuration",
                "engine-runtime-lifecycle",
                "lua-runtime",
            },
            {
                module_id
                for module_id in self.registry.modules
                if self.registry.modules[module_id]["category"] == "engine-foundation"
            },
        )
        for module_id in (
            "configuration",
            "engine-runtime-lifecycle",
            "lua-runtime",
        ):
            module = self.registry.modules[module_id]
            self.assertEqual(module["lifecycle"]["status"], "inventory")
            self.assertEqual(module["maturity"]["implementation"], "inventory")
            self.assertEqual(module["maturity"]["evidence"], "inventory")
            self.assertEqual(module["relationships"]["depends_on"], [])

    def test_representative_paths_map_to_narrow_modules(self) -> None:
        cases = {
            "src/canary_server.cpp": "engine-runtime-lifecycle",
            "src/config/configmanager.cpp": "configuration",
            "src/lua/scripts/lua_environment.hpp": "lua-runtime",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                matches = self.registry.matched_modules(path)
                module_ids = [module_id for module_id, _, _ in matches]
                self.assertIn(expected, module_ids)
                self.assertEqual(module_ids, sorted(module_ids))

    def test_affected_is_sorted_deduplicated_and_keeps_umbrella_matches(self) -> None:
        affected = self.registry.affected_modules(
            [
                "src/lua/scripts/lua_environment.hpp",
                "src/canary_server.cpp",
                "src/config/configmanager.cpp",
                "src/canary_server.cpp",
            ]
        )
        self.assertEqual(affected, sorted(set(affected)))
        self.assertIn("configuration", affected)
        self.assertIn("engine-runtime-lifecycle", affected)
        self.assertIn("lua-runtime", affected)
        self.assertIn("protocol", affected)

    def test_upstream_mapping_remains_sorted_discovery_only(self) -> None:
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

    def test_generated_documents_include_bootstrap_records(self) -> None:
        generated = self.registry.generated_documents()
        self.assertIn("Total modules: **22**.", generated["MODULE_INDEX.md"])
        self.assertIn(
            "| `src/canary_server.*` | `engine-runtime-lifecycle` | `server` |",
            generated["MODULE_PATH_INDEX.md"],
        )
        self.assertIn(
            "| `configuration` | — | `engine-runtime-lifecycle`, `lua-runtime`, `protocol` |",
            generated["MODULE_DEPENDENCIES.md"],
        )


if __name__ == "__main__":
    unittest.main()
