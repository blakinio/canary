from __future__ import annotations

import datetime as dt
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("real_tibia_registry.py")
SPEC = importlib.util.spec_from_file_location("real_tibia_registry", MODULE_PATH)
assert SPEC and SPEC.loader
registry_tool = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = registry_tool
SPEC.loader.exec_module(registry_tool)

Registry = registry_tool.Registry
_write_generated = registry_tool.write_generated


class RealTibiaRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        source = self.repo_root / "docs/agents/real-tibia"
        target = self.root / "docs/agents/real-tibia"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def load(self) -> Registry:
        return Registry.load(self.root)

    def module_path(self, module_id: str) -> Path:
        return (
            self.root
            / "docs/agents/real-tibia/registry/modules"
            / f"{module_id}.yaml"
        )

    def read_module(self, module_id: str) -> dict:
        return json.loads(self.module_path(module_id).read_text(encoding="utf-8"))

    def write_module(self, module: dict) -> None:
        path = self.module_path(module["module_id"])
        path.write_text(
            json.dumps(module, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def test_real_registry_is_valid(self) -> None:
        result = Registry.load(self.repo_root).validate()
        self.assertEqual(result.errors, ())

    def test_generation_is_deterministic_and_checkable(self) -> None:
        registry = self.load()
        first = registry.generated_documents()
        second = registry.generated_documents()
        self.assertEqual(first, second)
        self.assertIn(
            "Evaluated as of **2026-07-14**", first["STALE_MODULES.md"]
        )
        self.assertEqual(
            _write_generated(registry, check=False, as_of=None), 0
        )
        self.assertEqual(
            _write_generated(registry, check=True, as_of=None), 0
        )

    def test_generated_drift_is_detected(self) -> None:
        registry = self.load()
        self.assertEqual(
            _write_generated(registry, check=False, as_of=None), 0
        )
        path = self.root / "docs/agents/real-tibia/generated/MODULE_INDEX.md"
        path.write_text("manual edit\n", encoding="utf-8")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(
                _write_generated(registry, check=True, as_of=None), 1
            )

    def test_unknown_dependency_is_rejected(self) -> None:
        module = self.read_module("wheel-of-destiny")
        module["relationships"]["depends_on"].append("does-not-exist")
        self.write_module(module)
        result = self.load().validate()
        self.assertTrue(
            any(
                "unknown module 'does-not-exist'" in error
                for error in result.errors
            )
        )

    def test_dependency_cycle_is_rejected(self) -> None:
        combat = self.read_module("combat")
        combat["relationships"]["depends_on"].append("wheel-of-destiny")
        self.write_module(combat)
        result = self.load().validate()
        self.assertTrue(
            any(
                error.startswith("dependency cycle:")
                for error in result.errors
            )
        )

    def test_path_traversal_is_rejected(self) -> None:
        module = self.read_module("market")
        module["paths"]["server"].append("../outside/**")
        self.write_module(module)
        result = self.load().validate()
        self.assertTrue(
            any(
                "unsafe paths.server entry" in error
                for error in result.errors
            )
        )

    def test_path_lookup_returns_all_matching_modules(self) -> None:
        matches = self.load().matched_modules(
            "src/server/network/protocol/protocolgame.cpp"
        )
        ids = {module_id for module_id, _, _ in matches}
        self.assertIn("protocol", ids)
        self.assertIn("wheel-of-destiny", ids)

    def test_decomposition_records_are_bounded(self) -> None:
        registry = self.load()
        self.assertEqual(len(registry.modules), 26)
        self.assertIn("engine-foundation", registry.categories)
        tsd_001 = {
            "configuration",
            "engine-runtime-lifecycle",
            "lua-runtime",
        }
        tsd_002a = {
            "build-system",
            "engine-scheduler",
            "engine-service-container",
            "lua-bindings",
        }
        actual = {
            module_id
            for module_id, module in registry.modules.items()
            if module["category"] == "engine-foundation"
        }
        self.assertEqual(actual, tsd_001 | tsd_002a)
        for module_id in tsd_001 | tsd_002a:
            module = registry.modules[module_id]
            self.assertEqual(module["lifecycle"]["status"], "inventory")
            self.assertEqual(module["maturity"]["implementation"], "inventory")
            self.assertEqual(module["maturity"]["evidence"], "inventory")
            self.assertEqual(module["maturity"]["persistence"], "not-assessed")
            self.assertEqual(module["maturity"]["runtime_validation"], "not-assessed")
        self.assertEqual(
            registry.modules["lua-bindings"]["relationships"]["depends_on"],
            ["lua-runtime"],
        )
        for module_id in (tsd_001 | tsd_002a) - {"lua-bindings"}:
            self.assertEqual(
                registry.modules[module_id]["relationships"]["depends_on"], []
            )
        self.assertNotIn("data-registries", registry.modules)
        self.assertNotIn("platform-compatibility", registry.modules)

    def test_tsd_002a_does_not_redefine_player_persistence(self) -> None:
        module = self.load().modules["player-persistence"]
        self.assertEqual(
            module["paths"]["server"],
            ["src/io/**", "src/database/**", "src/creatures/players/**"],
        )
        self.assertEqual(module["lifecycle"]["status"], "mapped")

    def test_decomposition_paths_map_to_narrow_modules(self) -> None:
        registry = self.load()
        cases = {
            "CMakeLists.txt": "build-system",
            "src/canary_server.cpp": "engine-runtime-lifecycle",
            "src/config/configmanager.cpp": "configuration",
            "src/game/scheduling/dispatcher.cpp": "engine-scheduler",
            "src/lib/di/container.hpp": "engine-service-container",
            "src/lua/functions/lua_functions_loader.cpp": "lua-bindings",
            "src/lua/scripts/lua_environment.hpp": "lua-runtime",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                matches = registry.matched_modules(path)
                ids = [module_id for module_id, _, _ in matches]
                self.assertIn(expected, ids)
                self.assertEqual(ids, sorted(ids))

    def test_freshness_thresholds_are_explicit(self) -> None:
        rows = {
            row["module_id"]: row
            for row in self.load().stale_rows(dt.date(2026, 8, 15))
        }
        self.assertEqual(rows["wheel-of-destiny"]["state"], "warning")
        self.assertEqual(rows["otbm-tooling"]["state"], "current")

    def test_unregistered_generated_file_is_rejected(self) -> None:
        path = self.root / "docs/agents/real-tibia/generated/manual.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("manual\n", encoding="utf-8")
        result = self.load().validate()
        self.assertTrue(
            any(
                "unregistered files: manual.md" in error
                for error in result.errors
            )
        )

    def test_affected_modules_are_sorted_and_deduplicated(self) -> None:
        affected = self.load().affected_modules(
            [
                "src/io/io_wheel.cpp",
                "src/server/network/protocol/protocolgame.cpp",
                "src/io/io_wheel.cpp",
            ]
        )
        self.assertEqual(affected, sorted(set(affected)))
        self.assertIn("wheel-of-destiny", affected)
        self.assertIn("protocol", affected)

    def test_decomposition_affected_keeps_sorted_overlapping_hints(self) -> None:
        affected = self.load().affected_modules(
            [
                "CMakeLists.txt",
                "src/lua/functions/lua_functions_loader.cpp",
                "src/game/scheduling/dispatcher.cpp",
                "src/lib/di/container.hpp",
                "src/lua/scripts/lua_environment.hpp",
                "src/canary_server.cpp",
                "src/config/configmanager.cpp",
                "src/canary_server.cpp",
            ]
        )
        self.assertEqual(affected, sorted(set(affected)))
        for expected in (
            "build-system",
            "configuration",
            "engine-runtime-lifecycle",
            "engine-scheduler",
            "engine-service-container",
            "lua-bindings",
            "lua-runtime",
        ):
            self.assertIn(expected, affected)
        self.assertIn("protocol", affected)


if __name__ == "__main__":
    unittest.main()
