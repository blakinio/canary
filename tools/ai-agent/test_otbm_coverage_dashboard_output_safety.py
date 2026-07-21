from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from otbm_coverage_dashboard import TARGETS_FORMAT, CoverageDashboardError
from otbm_coverage_dashboard_tool import _load_stable_json, _prepare_output, _write_json


class CoverageDashboardOutputSafetyTests(unittest.TestCase):
    def test_stable_loader_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "targets.json"
            source.write_text(json.dumps({"format": TARGETS_FORMAT}), encoding="utf-8")
            link = root / "targets-link.json"
            try:
                link.symlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(CoverageDashboardError):
                _load_stable_json(link, "targets", TARGETS_FORMAT)

    def test_prepare_output_rejects_duplicate_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            resolved = source.resolve()
            with self.assertRaises(CoverageDashboardError):
                _prepare_output(root / "output.json", [resolved, resolved], False)

    def test_prepare_output_rejects_input_collision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "targets.json"
            source.write_text(json.dumps({"format": TARGETS_FORMAT}), encoding="utf-8")
            with self.assertRaises(CoverageDashboardError):
                _prepare_output(source, [source.resolve()], False)

    def test_prepare_output_rejects_hard_link_collision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            output = root / "output.json"
            try:
                os.link(source, output)
            except OSError:
                self.skipTest("hard links are unavailable")
            with self.assertRaises(CoverageDashboardError):
                _prepare_output(output, [source.resolve()], True)

    def test_create_new_writer_does_not_clobber_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            with self.assertRaises(CoverageDashboardError):
                _write_json(output, {"format": "new"}, overwrite=False)
            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel")

    def test_overwrite_writer_replaces_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            _write_json(output, {"format": "new", "value": 1}, overwrite=True)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"format": "new", "value": 1})


if __name__ == "__main__":
    unittest.main()
