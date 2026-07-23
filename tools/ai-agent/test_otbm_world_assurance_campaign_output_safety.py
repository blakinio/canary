from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from otbm_world_assurance_campaign import WorldAssuranceCampaignError
from otbm_world_assurance_campaign_tool import _write


class WorldAssuranceCampaignOutputSafetyTests(unittest.TestCase):
    def test_create_new_refuses_existing_output_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "report.json"
            output.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(WorldAssuranceCampaignError, "output already exists"):
                _write(output, {"ok": True}, overwrite=False, inputs=[])

    def test_output_must_not_replace_an_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "input.json"
            source.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(WorldAssuranceCampaignError, "output collides with input"):
                _write(source, {"ok": True}, overwrite=True, inputs=[source])

    def test_overwrite_is_atomic_for_regular_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "report.json"
            output.write_text('{"old": true}\n', encoding="utf-8")
            _write(output, {"new": True}, overwrite=True, inputs=[])
            self.assertIn('"new": true', output.read_text(encoding="utf-8"))
            self.assertFalse(any(path.suffix == ".tmp" for path in root.iterdir()))


if __name__ == "__main__":
    unittest.main()
