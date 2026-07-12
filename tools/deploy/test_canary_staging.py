from __future__ import annotations

import argparse
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canary_staging import CanarySmokeSettings, _staging_smoke_executor, assemble_staging_datapack, run_canary_smoke
from path_policy import PathEscapesRootError


class CanaryStagingTests(unittest.TestCase):
    def test_assemble_staging_datapack_copies_base_and_applies_overlay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base"
            overlay = root / "overlay"
            destination = root / "workspace" / "datapack"
            (base / "scripts").mkdir(parents=True)
            (base / "world").mkdir(parents=True)
            (overlay / "scripts").mkdir(parents=True)
            (overlay / "new").mkdir(parents=True)
            (base / "scripts" / "existing.lua").write_text("base", encoding="utf-8")
            (base / "world" / "canary.otbm").write_bytes(b"map")
            (overlay / "scripts" / "existing.lua").write_text("overlay", encoding="utf-8")
            (overlay / "new" / "content.lua").write_text("new", encoding="utf-8")

            assembled = assemble_staging_datapack(base, overlay, destination)

            self.assertEqual((assembled / "scripts" / "existing.lua").read_text(encoding="utf-8"), "overlay")
            self.assertEqual((assembled / "new" / "content.lua").read_text(encoding="utf-8"), "new")
            self.assertEqual((assembled / "world" / "canary.otbm").read_bytes(), b"map")
            self.assertEqual((base / "scripts" / "existing.lua").read_text(encoding="utf-8"), "base")

    def test_assemble_refuses_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base"
            overlay = root / "overlay"
            destination = root / "destination"
            base.mkdir()
            overlay.mkdir()
            destination.mkdir()

            with self.assertRaises(FileExistsError):
                assemble_staging_datapack(base, overlay, destination)

    def test_assemble_rejects_overlay_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base"
            overlay = root / "overlay"
            base.mkdir()
            overlay.mkdir()
            outside = root / "outside.lua"
            outside.write_text("outside", encoding="utf-8")
            link = overlay / "escape.lua"
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlinks are unavailable: {exc}")

            with self.assertRaises(PathEscapesRootError):
                assemble_staging_datapack(base, overlay, root / "destination")

    def test_assemble_cleans_partial_destination_when_base_copy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base"
            overlay = root / "overlay"
            destination = root / "destination"
            base.mkdir()
            overlay.mkdir()

            def fail_after_partial_copy(_source: Path, target: Path, **_kwargs: object) -> None:
                target_path = Path(target)
                target_path.mkdir(parents=True)
                (target_path / "partial.lua").write_text("partial", encoding="utf-8")
                raise OSError("synthetic base copy failure")

            with mock.patch("canary_staging.shutil.copytree", side_effect=fail_after_partial_copy):
                with self.assertRaisesRegex(OSError, "synthetic base copy failure"):
                    assemble_staging_datapack(base, overlay, destination)

            self.assertFalse(destination.exists())

    def test_assemble_cleans_destination_when_overlay_application_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base"
            overlay = root / "overlay"
            destination = root / "destination"
            (base / "conflict.lua").mkdir(parents=True)
            overlay.mkdir()
            (overlay / "conflict.lua").write_text("file", encoding="utf-8")

            with self.assertRaises(IsADirectoryError):
                assemble_staging_datapack(base, overlay, destination)

            self.assertFalse(destination.exists())

    def _smoke_fixture(self, root: Path) -> tuple[Path, CanarySmokeSettings]:
        repo = root / "repo"
        datapack = root / "datapack"
        binary = repo / "build" / "canary"
        repo.mkdir()
        datapack.mkdir()
        binary.parent.mkdir(parents=True)
        binary.write_text("binary", encoding="utf-8")
        settings = CanarySmokeSettings(repo_root=repo, binary_path=binary)
        return datapack, settings

    def test_staging_executor_enables_any_datapack_only_in_generated_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            config_path = repo / "config.lua"
            observed: list[str] = []

            def standard_write(_args: argparse.Namespace) -> None:
                config_path.write_text("useAnyDatapackFolder = false\n", encoding="utf-8")

            def set_lua_value(content: str, name: str, value: str) -> str:
                self.assertEqual(name, "useAnyDatapackFolder")
                return content.replace("useAnyDatapackFolder = false", f"useAnyDatapackFolder = {value}")

            def run_smoke(_args: argparse.Namespace) -> None:
                observed.append(config_path.read_text(encoding="utf-8"))

            fake_module = SimpleNamespace(
                write_smoke_config=standard_write,
                set_lua_value=set_lua_value,
                run_smoke=run_smoke,
            )
            with mock.patch("canary_staging._load_smoke_module", return_value=fake_module):
                executor = _staging_smoke_executor(repo)
                executor(argparse.Namespace())

            self.assertEqual(observed, ["useAnyDatapackFolder = true\n"])

    def test_run_canary_smoke_uses_short_alias_and_cleans_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            datapack, settings = self._smoke_fixture(root)
            seen_alias: list[Path] = []

            def executor(args: argparse.Namespace) -> None:
                self.assertNotIn(os.sep, args.data_pack)
                alias = settings.repo_root / args.data_pack
                self.assertTrue(alias.is_symlink())
                self.assertEqual(alias.resolve(), datapack.resolve())
                seen_alias.append(alias)

            result = run_canary_smoke(datapack, settings, phase="preflight", executor=executor)

            self.assertTrue(result.healthy)
            self.assertEqual(len(seen_alias), 1)
            self.assertFalse(seen_alias[0].exists())
            self.assertFalse(seen_alias[0].is_symlink())

    def test_run_canary_smoke_returns_unhealthy_and_cleans_alias_on_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            datapack, settings = self._smoke_fixture(root)
            seen_alias: list[Path] = []

            def executor(args: argparse.Namespace) -> None:
                alias = settings.repo_root / args.data_pack
                seen_alias.append(alias)
                raise RuntimeError("synthetic smoke failure")

            result = run_canary_smoke(datapack, settings, phase="post-switch", executor=executor)

            self.assertFalse(result.healthy)
            self.assertIn("synthetic smoke failure", result.detail)
            self.assertEqual(len(seen_alias), 1)
            self.assertFalse(seen_alias[0].exists())
            self.assertFalse(seen_alias[0].is_symlink())


if __name__ == "__main__":
    unittest.main()
