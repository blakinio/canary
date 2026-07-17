from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "e2e" / "server_selection.py"
SPEC = importlib.util.spec_from_file_location("server_selection", MODULE_PATH)
assert SPEC and SPEC.loader
server_selection = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = server_selection
SPEC.loader.exec_module(server_selection)


class ServerSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "data-otservbr-global" / "world").mkdir(parents=True)
        (self.root / "data-canary" / "world").mkdir(parents=True)
        (self.root / "data-canary" / "world" / "canary.otbm").write_bytes(b"otbm-test")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_manifest(self, datapack: str, map_name: str) -> Path:
        path = self.root / "scenario-manifest.json"
        path.write_text(
            json.dumps({"scenario": {"server": {"datapack": datapack, "map": map_name}}}),
            encoding="utf-8",
        )
        return path

    def test_default_global_selection_allows_existing_download_fallback(self) -> None:
        selection = server_selection.resolve_server_selection(
            self.write_manifest("data-otservbr-global", "otservbr"), self.root
        )
        self.assertTrue(selection.allow_map_download)
        self.assertEqual(selection.datapack_path, (self.root / "data-otservbr-global").resolve())
        self.assertEqual(selection.map_path, (self.root / "data-otservbr-global" / "world" / "otservbr.otbm").resolve())

    def test_repository_local_non_default_map_must_exist(self) -> None:
        selection = server_selection.resolve_server_selection(self.write_manifest("data-canary", "canary"), self.root)
        self.assertFalse(selection.allow_map_download)
        self.assertEqual(selection.map_path, (self.root / "data-canary" / "world" / "canary.otbm").resolve())

    def test_missing_non_default_map_fails_closed(self) -> None:
        with self.assertRaisesRegex(server_selection.ServerSelectionError, "missing or empty"):
            server_selection.resolve_server_selection(self.write_manifest("data-canary", "missing"), self.root)

    def test_unsafe_datapack_and_map_segments_are_rejected(self) -> None:
        cases = [
            ("../data-canary", "canary"),
            ("data/canary", "canary"),
            ("data-canary", "../canary"),
            ("data-canary", "nested/canary"),
            ("data-canary", "."),
        ]
        for datapack, map_name in cases:
            with self.subTest(datapack=datapack, map_name=map_name):
                with self.assertRaisesRegex(server_selection.ServerSelectionError, "safe repository-local path segment"):
                    server_selection.resolve_server_selection(self.write_manifest(datapack, map_name), self.root)

    def test_symlinked_datapack_cannot_escape_repository_root(self) -> None:
        outside = Path(self.tempdir.name).parent / f"{self.root.name}-outside"
        outside.mkdir(exist_ok=True)
        link = self.root / "data-escape"
        try:
            link.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(server_selection.ServerSelectionError, "outside"):
                server_selection.resolve_server_selection(self.write_manifest("data-escape", "canary"), self.root)
        finally:
            if link.is_symlink():
                link.unlink()
            outside.rmdir()

    def test_symlinked_world_cannot_escape_selected_datapack(self) -> None:
        outside = Path(self.tempdir.name).parent / f"{self.root.name}-world-outside"
        outside.mkdir(exist_ok=True)
        (outside / "canary.otbm").write_bytes(b"outside")
        world = self.root / "data-canary" / "world"
        (world / "canary.otbm").unlink()
        world.rmdir()
        try:
            world.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(server_selection.ServerSelectionError, "outside"):
                server_selection.resolve_server_selection(self.write_manifest("data-canary", "canary"), self.root)
        finally:
            if world.is_symlink():
                world.unlink()
            (outside / "canary.otbm").unlink()
            outside.rmdir()

    def test_symlinked_map_cannot_escape_selected_world(self) -> None:
        outside = Path(self.tempdir.name).parent / f"{self.root.name}-outside-map.otbm"
        outside.write_bytes(b"outside")
        map_path = self.root / "data-canary" / "world" / "canary.otbm"
        map_path.unlink()
        try:
            map_path.symlink_to(outside)
            with self.assertRaisesRegex(server_selection.ServerSelectionError, "outside"):
                server_selection.resolve_server_selection(self.write_manifest("data-canary", "canary"), self.root)
        finally:
            if map_path.is_symlink():
                map_path.unlink()
            outside.unlink()

    def test_environment_contains_only_resolved_server_selection(self) -> None:
        selection = server_selection.resolve_server_selection(self.write_manifest("data-canary", "canary"), self.root)
        values = server_selection.github_environment(selection)
        self.assertEqual(
            values,
            {
                "AGENT_E2E_SERVER_DATAPACK": "data-canary",
                "AGENT_E2E_SERVER_MAP": "canary",
                "AGENT_E2E_SERVER_DATAPACK_PATH": str((self.root / "data-canary").resolve()),
                "AGENT_E2E_SERVER_MAP_PATH": str((self.root / "data-canary" / "world" / "canary.otbm").resolve()),
                "AGENT_E2E_SERVER_ALLOW_MAP_DOWNLOAD": "false",
            },
        )


if __name__ == "__main__":
    unittest.main()
