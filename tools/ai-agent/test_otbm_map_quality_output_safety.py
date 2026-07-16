from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from otbm_map_quality import MapQualityError
from otbm_map_quality_tool import _write_json


class OutputSafetyTests(unittest.TestCase):
    def test_create_new_writer_refuses_late_existing_output_without_replacing_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-quality-output-race-") as temporary:
            output = Path(temporary) / "quality.json"
            output.write_text("sentinel\n", encoding="utf-8")

            with self.assertRaisesRegex(MapQualityError, "output already exists"):
                _write_json(output, {"replacement": True}, overwrite=False)

            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel\n")

    def test_explicit_overwrite_replaces_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="otbm-map-quality-output-overwrite-") as temporary:
            output = Path(temporary) / "quality.json"
            output.write_text("sentinel\n", encoding="utf-8")

            _write_json(output, {"replacement": True}, overwrite=True)

            self.assertIn('"replacement": true', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
