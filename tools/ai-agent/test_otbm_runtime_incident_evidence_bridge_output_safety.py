from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from otbm_runtime_incident_evidence_bridge import sha256_path
from otbm_runtime_incident_evidence_bridge_tool import main as tool_main
from test_otbm_runtime_incident_evidence_bridge import SOURCE_FORMAT, bindings_document


class RuntimeIncidentEvidenceBridgeOutputSafetyTests(unittest.TestCase):
    def _write_bindings(self, root: Path, *, source_sha: str = "f" * 64) -> Path:
        bindings_path = root / "bindings.json"
        bindings_path.write_text(
            json.dumps(bindings_document({"kind": "route-id", "value": "route-1"}, sha256=source_sha), sort_keys=True),
            encoding="utf-8",
        )
        return bindings_path

    def test_plan_only_does_not_require_evidence_source_file(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bindings_path = self._write_bindings(root)
            rc = tool_main(
                [
                    "--bindings", str(bindings_path),
                    "--route-id", "route-1",
                    "--output", "plan.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(rc, 0)
            report = json.loads((root / "plan.json").read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "plan")
            self.assertIsNone(report["evidenceBundle"])

    def test_execute_uses_exact_source_and_writes_bundle(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.json"
            source.write_text(json.dumps({"format": SOURCE_FORMAT, "payload": {"ok": True}}), encoding="utf-8")
            bindings_path = self._write_bindings(root, source_sha=sha256_path(source))
            rc = tool_main(
                [
                    "--bindings", str(bindings_path),
                    "--route-id", "route-1",
                    "--output", "report.json",
                ]
            )
            self.assertEqual(rc, 0)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "executed")
            self.assertEqual(report["evidenceBundleSha256"], report["evidenceBundle"]["bundleSha256"])

    def test_no_clobber_default_and_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bindings_path = self._write_bindings(root)
            args = [
                "--bindings", str(bindings_path),
                "--route-id", "route-1",
                "--output", "plan.json",
                "--plan-only",
            ]
            self.assertEqual(tool_main(args), 0)
            first = (root / "plan.json").read_bytes()
            self.assertEqual(tool_main(args), 2)
            self.assertEqual((root / "plan.json").read_bytes(), first)
            self.assertEqual(tool_main(args + ["--overwrite"]), 0)
            self.assertEqual((root / "plan.json").read_bytes(), first)

    def test_output_must_not_collide_with_bindings_input(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bindings_path = self._write_bindings(root)
            original = bindings_path.read_bytes()
            rc = tool_main(
                [
                    "--bindings", str(bindings_path),
                    "--route-id", "route-1",
                    "--output", "bindings.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(rc, 2)
            self.assertEqual(bindings_path.read_bytes(), original)

    def test_output_must_not_collide_with_selected_source(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.json"
            source.write_text(json.dumps({"format": SOURCE_FORMAT, "payload": 1}), encoding="utf-8")
            bindings_path = self._write_bindings(root, source_sha=sha256_path(source))
            original = source.read_bytes()
            rc = tool_main(
                [
                    "--bindings", str(bindings_path),
                    "--route-id", "route-1",
                    "--output", "source.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(rc, 2)
            self.assertEqual(source.read_bytes(), original)

    def test_output_path_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bindings_path = self._write_bindings(root)
            rc = tool_main(
                [
                    "--bindings", str(bindings_path),
                    "--route-id", "route-1",
                    "--output", "../escape.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(rc, 2)
            self.assertFalse((root.parent / "escape.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_bindings_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            real = self._write_bindings(root)
            link = root / "bindings-link.json"
            link.symlink_to(real)
            rc = tool_main(
                [
                    "--bindings", str(link),
                    "--route-id", "route-1",
                    "--output", "plan.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(rc, 2)
            self.assertFalse((root / "plan.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_output_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bindings_path = self._write_bindings(root)
            target = root / "target.json"
            target.write_text("preserve", encoding="utf-8")
            link = root / "plan.json"
            link.symlink_to(target)
            rc = tool_main(
                [
                    "--bindings", str(bindings_path),
                    "--route-id", "route-1",
                    "--output", "plan.json",
                    "--plan-only",
                    "--overwrite",
                ]
            )
            self.assertEqual(rc, 2)
            self.assertEqual(target.read_text(encoding="utf-8"), "preserve")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_output_parent_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bindings_path = self._write_bindings(root)
            real_dir = root / "real"
            real_dir.mkdir()
            link_dir = root / "link"
            link_dir.symlink_to(real_dir, target_is_directory=True)
            rc = tool_main(
                [
                    "--bindings", str(bindings_path),
                    "--route-id", "route-1",
                    "--output", "link/plan.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(rc, 2)
            self.assertFalse((real_dir / "plan.json").exists())


if __name__ == "__main__":
    unittest.main()
