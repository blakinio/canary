from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PERSISTENCE_PATH = ROOT / "tools" / "e2e" / "persistence_assertions.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


persistence = load_module("test_e2e_player_field_persistence_precision", PERSISTENCE_PATH)


class PlayerFieldPersistencePrecisionTests(unittest.TestCase):
    def test_accepts_exact_lua_safe_player_field_boundary(self) -> None:
        for field in ("level", "experience"):
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": field,
                        "type": "player_field",
                        "field": field,
                        "equals": persistence.MAX_SAFE_LUA_INTEGER,
                    }
                ],
            }

            with self.subTest(field=field):
                [query] = persistence.compile_persistence_assertions(raw, character="Knight 1")
                [client_check] = persistence.validate_persistence_assertions(raw)
                self.assertIn(str(persistence.MAX_SAFE_LUA_INTEGER), query)
                self.assertEqual(client_check["equals"], persistence.MAX_SAFE_LUA_INTEGER)

    def test_rejects_player_field_value_above_exact_lua_safe_boundary(self) -> None:
        for field in ("level", "experience"):
            raw = {
                "required": True,
                "checks": [
                    {
                        "id": field,
                        "type": "player_field",
                        "field": field,
                        "equals": persistence.MAX_SAFE_LUA_INTEGER + 1,
                    }
                ],
            }

            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    persistence.PersistenceAssertionError,
                    "exact Lua-safe non-negative integer",
                ):
                    persistence.compile_persistence_assertions(raw, character="Knight 1")


if __name__ == "__main__":
    unittest.main()
