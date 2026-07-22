from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from otbm_release_provenance import ReleaseProvenanceError
from otbm_release_provenance_tool import _write


class ReleaseProvenanceOutputSafetyTests(unittest.TestCase):
    def test_create_new_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            _write(output, {"value": 1}, overwrite=False, inputs=[])
            with self.assertRaises(ReleaseProvenanceError):
                _write(output, {"value": 2}, overwrite=False, inputs=[])
            _write(output, {"value": 3}, overwrite=True, inputs=[])
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"value": 3})

    def test_symlink_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(ReleaseProvenanceError):
                _write(link, {}, overwrite=True, inputs=[])

    def test_input_collision_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaises(ReleaseProvenanceError):
                _write(source, {}, overwrite=True, inputs=[source.resolve()])


if __name__ == "__main__":
    unittest.main()
