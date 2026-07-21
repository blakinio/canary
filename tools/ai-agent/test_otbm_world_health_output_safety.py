from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from otbm_world_health import WorldHealthError
from otbm_world_health_tool import _prepare_output, _write_json


class OutputSafetyTests(unittest.TestCase):
    def test_create_new_writer_refuses_late_existing_output_without_replacing_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-world-health-output-race-") as temporary:
            output = Path(temporary) / "health.json"
            output.write_text("sentinel\n", encoding="utf-8")

            with self.assertRaisesRegex(WorldHealthError, "output already exists"):
                _write_json(output, {"replacement": True}, overwrite=False)

            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel\n")

    def test_explicit_overwrite_replaces_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-world-health-output-overwrite-") as temporary:
            output = Path(temporary) / "health.json"
            output.write_text("sentinel\n", encoding="utf-8")

            _write_json(output, {"replacement": True}, overwrite=True)

            self.assertIn('"replacement": true', output.read_text(encoding="utf-8"))

    def test_prepare_output_rejects_direct_input_collision(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-world-health-output-collision-") as temporary:
            source = Path(temporary) / "quality.json"
            source.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(WorldHealthError, "output must not be one of the input reports"):
                _prepare_output(source, [source.resolve()], overwrite=True)

    def test_prepare_output_rejects_duplicate_input_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-world-health-duplicate-input-") as temporary:
            source = Path(temporary) / "quality.json"
            output = Path(temporary) / "health.json"
            source.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(WorldHealthError, "input reports must be distinct files"):
                _prepare_output(output, [source.resolve(), source.resolve()], overwrite=False)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are not supported")
    def test_prepare_output_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-world-health-output-symlink-") as temporary:
            target = Path(temporary) / "target.json"
            output = Path(temporary) / "health.json"
            target.write_text("sentinel\n", encoding="utf-8")
            try:
                output.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"cannot create symlink on this platform: {exc}")

            with self.assertRaisesRegex(WorldHealthError, "output must not be a symlink"):
                _prepare_output(output, [], overwrite=True)


if __name__ == "__main__":
    unittest.main()
