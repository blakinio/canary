from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from otbm_map_change_regression import RegressionGuardError
from otbm_map_change_regression_tool import _prepare_output, _write_json


class OutputSafetyTests(unittest.TestCase):
    def test_create_new_writer_refuses_late_existing_output_without_replacing_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-change-regression-output-race-") as temporary:
            output = Path(temporary) / "regression.json"
            output.write_text("sentinel\n", encoding="utf-8")

            with self.assertRaisesRegex(RegressionGuardError, "output already exists"):
                _write_json(output, {"replacement": True}, overwrite=False)

            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel\n")

    def test_explicit_overwrite_replaces_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-change-regression-output-overwrite-") as temporary:
            output = Path(temporary) / "regression.json"
            output.write_text("sentinel\n", encoding="utf-8")

            _write_json(output, {"replacement": True}, overwrite=True)

            self.assertIn('"replacement": true', output.read_text(encoding="utf-8"))

    def test_prepare_output_rejects_direct_input_collision(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-change-regression-output-collision-") as temporary:
            source = Path(temporary) / "semantic-diff.json"
            source.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(RegressionGuardError, "output must not be one of the input reports"):
                _prepare_output(source, [source.resolve()], overwrite=True)

    def test_prepare_output_rejects_duplicate_input_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-change-regression-duplicate-input-") as temporary:
            source = Path(temporary) / "semantic-diff.json"
            output = Path(temporary) / "regression.json"
            source.write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(RegressionGuardError, "input reports must be distinct files"):
                _prepare_output(output, [source.resolve(), source.resolve()], overwrite=False)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are not supported")
    def test_prepare_output_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-change-regression-output-symlink-") as temporary:
            target = Path(temporary) / "target.json"
            output = Path(temporary) / "regression.json"
            target.write_text("sentinel\n", encoding="utf-8")
            try:
                output.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"cannot create symlink on this platform: {exc}")

            with self.assertRaisesRegex(RegressionGuardError, "output must not be a symlink"):
                _prepare_output(output, [], overwrite=True)


if __name__ == "__main__":
    unittest.main()
