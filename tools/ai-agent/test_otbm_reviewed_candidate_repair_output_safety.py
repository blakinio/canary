from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from otbm_reviewed_candidate_repair import APPROVAL_FORMAT, RECOMMENDATION_FORMAT, ReviewedCandidateRepairError
from otbm_reviewed_candidate_repair_tool import _load_stable_json, _prepare_output, _write_json


class ReviewedCandidateRepairOutputSafetyTests(unittest.TestCase):
    def test_stable_loader_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "recommendation.json"
            source.write_text(json.dumps({"format": RECOMMENDATION_FORMAT}), encoding="utf-8")
            link = root / "recommendation-link.json"
            try:
                link.symlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaises(ReviewedCandidateRepairError):
                _load_stable_json(link, "recommendation", RECOMMENDATION_FORMAT)

    def test_prepare_output_rejects_duplicate_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text("{}", encoding="utf-8")
            resolved = source.resolve()
            with self.assertRaises(ReviewedCandidateRepairError):
                _prepare_output(root / "output.json", [resolved, resolved], False)

    def test_prepare_output_rejects_input_collision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "approval.json"
            source.write_text(json.dumps({"format": APPROVAL_FORMAT}), encoding="utf-8")
            with self.assertRaises(ReviewedCandidateRepairError):
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
            with self.assertRaises(ReviewedCandidateRepairError):
                _prepare_output(output, [source.resolve()], True)

    def test_create_new_writer_does_not_clobber_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            with self.assertRaises(ReviewedCandidateRepairError):
                _write_json(output, {"format": "new"}, overwrite=False)
            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel")

    def test_overwrite_writer_replaces_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            _write_json(output, {"format": "new", "value": 1}, overwrite=True)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload, {"format": "new", "value": 1})


if __name__ == "__main__":
    unittest.main()
