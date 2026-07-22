from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from otbm_asset_compatibility import AssetCompatibilityError
from otbm_asset_compatibility_tool import _validate_distinct, _write_json


class AssetCompatibilityOutputSafetyTests(unittest.TestCase):
    def test_create_new_refuses_existing_output_and_overwrite_replaces(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            output.write_text("old", encoding="utf-8")
            with self.assertRaises(AssetCompatibilityError):
                _write_json(output, {"value": 1}, overwrite=False)
            _write_json(output, {"value": 2}, overwrite=True)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"value": 2})

    def test_symlink_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(AssetCompatibilityError):
                _write_json(link, {"value": 1}, overwrite=True)

    def test_input_output_collision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaises(AssetCompatibilityError):
                _validate_distinct([source.resolve()], source)


if __name__ == "__main__":
    unittest.main()
