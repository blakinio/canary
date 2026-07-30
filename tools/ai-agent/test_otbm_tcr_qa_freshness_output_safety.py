from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from otbm_tcr_qa_freshness import canonical_json
from otbm_tcr_qa_freshness_tool import run
from test_otbm_tcr_qa_freshness import make_manifest, make_provenance, make_routing


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TcrQaFreshnessOutputSafetyTests(unittest.TestCase):
    def write_inputs(self, root: Path) -> tuple[Path, Path, Path]:
        routing = make_routing()
        provenance = make_provenance()
        routing_path = root / "routing.json"
        provenance_path = root / "provenance.json"
        routing_path.write_text(canonical_json(routing) + "\n", encoding="utf-8")
        provenance_path.write_text(
            canonical_json(provenance) + "\n", encoding="utf-8"
        )
        manifest = make_manifest(
            routing,
            provenance,
            routing_file_sha=_file_sha256(routing_path),
            provenance_file_sha=_file_sha256(provenance_path),
        )
        manifest_path = root / "manifest.json"
        manifest_path.write_text(canonical_json(manifest) + "\n", encoding="utf-8")
        return routing_path, provenance_path, manifest_path

    def args(
        self,
        routing: Path,
        provenance: Path,
        manifest: Path,
        output: Path,
        *,
        overwrite: bool = False,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            routing_report=routing,
            release_provenance=provenance,
            manifest=manifest,
            output=output,
            overwrite=overwrite,
        )

    def test_create_new_then_overwrite_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            routing, provenance, manifest = self.write_inputs(root)
            output = root / "impact.json"
            first = run(self.args(routing, provenance, manifest, output))
            self.assertTrue(output.is_file())
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), first)
            with self.assertRaisesRegex(ValueError, "already exists"):
                run(self.args(routing, provenance, manifest, output))
            second = run(
                self.args(
                    routing,
                    provenance,
                    manifest,
                    output,
                    overwrite=True,
                )
            )
            self.assertEqual(second, first)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), first)

    def test_rejects_output_input_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            routing, provenance, manifest = self.write_inputs(root)
            with self.assertRaisesRegex(ValueError, "alias an input"):
                run(
                    self.args(
                        routing,
                        provenance,
                        manifest,
                        routing,
                        overwrite=True,
                    )
                )

    def test_rejects_symlink_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            routing, provenance, manifest = self.write_inputs(root)
            target = root / "target.json"
            target.write_text("{}\n", encoding="utf-8")
            output = root / "impact.json"
            try:
                os.symlink(target, output)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable in this environment")
            with self.assertRaisesRegex(ValueError, "must not be a symlink"):
                run(
                    self.args(
                        routing,
                        provenance,
                        manifest,
                        output,
                        overwrite=True,
                    )
                )

    def test_rejects_symlink_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            routing, provenance, manifest = self.write_inputs(root)
            routing_link = root / "routing-link.json"
            try:
                os.symlink(routing, routing_link)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable in this environment")
            with self.assertRaisesRegex(ValueError, "must not be a symlink"):
                run(
                    self.args(
                        routing_link,
                        provenance,
                        manifest,
                        root / "impact.json",
                    )
                )

    def test_rejects_duplicate_input_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            routing, provenance, _ = self.write_inputs(root)
            with self.assertRaisesRegex(ValueError, "inputs must be distinct"):
                run(
                    self.args(
                        routing,
                        provenance,
                        routing,
                        root / "impact.json",
                    )
                )


if __name__ == "__main__":
    unittest.main()
