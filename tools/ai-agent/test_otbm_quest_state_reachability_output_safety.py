from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from otbm_quest_state_reachability import MANIFEST_FORMAT, QuestStateReachabilityError
from otbm_quest_state_reachability_tool import _load_stable_json, _prepare_output, _write_json


class QuestStateReachabilityOutputSafetyTests(unittest.TestCase):
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
            with self.assertRaisesRegex(QuestStateReachabilityError, "symlink"):
                _load_stable_json(link, "manifest", MANIFEST_FORMAT)

    def test_rejects_duplicate_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(QuestStateReachabilityError, "distinct"):
                _prepare_output(root / "out.json", [source.resolve(), source.resolve()], False)

    def test_rejects_output_input_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(QuestStateReachabilityError, "one of the input"):
                _prepare_output(source, [source.resolve()], True)

    def test_no_clobber_then_atomic_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            _write_json(output, {"value": 1}, overwrite=False)
            with self.assertRaisesRegex(QuestStateReachabilityError, "already exists"):
                _write_json(output, {"value": 2}, overwrite=False)
            _write_json(output, {"value": 3}, overwrite=True)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"value": 3})

    def test_stable_loader_pins_digest_and_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "manifest.json"
            source.write_text(json.dumps({"format": MANIFEST_FORMAT}), encoding="utf-8")
            payload, pin, resolved = _load_stable_json(source, "manifest", MANIFEST_FORMAT)
            self.assertEqual(payload["format"], MANIFEST_FORMAT)
            self.assertEqual(pin["format"], MANIFEST_FORMAT)
            self.assertEqual(len(pin["sha256"]), 64)
            self.assertEqual(resolved, source.resolve())


if __name__ == "__main__":
    unittest.main()
