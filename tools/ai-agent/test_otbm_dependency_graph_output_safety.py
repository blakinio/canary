from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from otbm_dependency_graph import MANIFEST_FORMAT, WORLD_HEALTH_FORMAT, DependencyGraphError
from otbm_dependency_graph_tool import _load_stable_json, _prepare_output, _write_json


class DependencyGraphOutputSafetyTests(unittest.TestCase):
    def test_rejects_input_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.json"
            source.write_text(json.dumps({"format": MANIFEST_FORMAT}), encoding="utf-8")
            link = root / "link.json"
            try:
                link.symlink_to(source)
            except OSError:
                self.skipTest("symlinks unavailable")
            with self.assertRaisesRegex(DependencyGraphError, "symlink"):
                _load_stable_json(link, "manifest", MANIFEST_FORMAT)

    def test_rejects_duplicate_input_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(DependencyGraphError, "distinct"):
                _prepare_output(root / "out.json", [source.resolve(), source.resolve()], False)

    def test_rejects_output_equal_to_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(DependencyGraphError, "one of the input"):
                _prepare_output(source, [source.resolve()], True)

    def test_no_clobber_and_atomic_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "report.json"
            _write_json(output, {"value": 1}, overwrite=False)
            with self.assertRaisesRegex(DependencyGraphError, "already exists"):
                _write_json(output, {"value": 2}, overwrite=False)
            _write_json(output, {"value": 3}, overwrite=True)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"value": 3})

    def test_load_stable_json_pins_exact_format_and_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "world.json"
            source.write_text(json.dumps({"format": WORLD_HEALTH_FORMAT}), encoding="utf-8")
            payload, pin, resolved = _load_stable_json(source, "World Health", WORLD_HEALTH_FORMAT)
            self.assertEqual(payload["format"], WORLD_HEALTH_FORMAT)
            self.assertEqual(pin["format"], WORLD_HEALTH_FORMAT)
            self.assertEqual(len(pin["sha256"]), 64)
            self.assertEqual(resolved, source.resolve())


if __name__ == "__main__":
    unittest.main()
