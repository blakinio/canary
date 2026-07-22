from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from otbm_evidence_gateway import EvidenceGatewayError
from otbm_evidence_gateway_tool import _write


class EvidenceGatewayOutputSafetyTests(unittest.TestCase):
    def test_create_new_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            output = root / "output.json"
            _write(output, {"value": 1}, overwrite=False, manifest_path=manifest)
            with self.assertRaises(EvidenceGatewayError):
                _write(output, {"value": 2}, overwrite=False, manifest_path=manifest)
            _write(output, {"value": 3}, overwrite=True, manifest_path=manifest)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"value": 3})

    def test_symlink_output_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(EvidenceGatewayError):
                _write(link, {}, overwrite=True, manifest_path=manifest)

    def test_manifest_collision_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            with self.assertRaises(EvidenceGatewayError):
                _write(manifest, {}, overwrite=True, manifest_path=manifest)


if __name__ == "__main__":
    unittest.main()
