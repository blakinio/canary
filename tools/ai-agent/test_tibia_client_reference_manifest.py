from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from tibia_client_reference_manifest import (
    ClientReferenceManifestError,
    build_manifest,
    deterministic_json,
    write_manifest,
)

REVISION = "a" * 40
OBSERVED_AT = "2026-07-23T16:40:00+02:00"


def _build(root: Path, **overrides):
    values = {
        "package_root": root,
        "reference_id": "official-client-fixture",
        "package_root_label": "fixture package",
        "source_role": "official-client-reference",
        "observed_at": OBSERVED_AT,
        "client_build_evidence": "unknown",
        "client_build": None,
        "parser_revision": REVISION,
        "selected_inputs": [("staticdata", "data/staticdata.dat")],
    }
    values.update(overrides)
    return build_manifest(**values)


class ClientReferenceManifestTests(unittest.TestCase):
    def _root(self, directory: str) -> Path:
        root = Path(directory) / "client"
        (root / "data").mkdir(parents=True)
        (root / "data/staticdata.dat").write_bytes(b"fixture")
        return root

    def test_deterministic_manifest_and_no_absolute_root_leak(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            first, _ = _build(root)
            second, _ = _build(root)
            self.assertEqual(deterministic_json(first), deterministic_json(second))
            self.assertNotIn(str(root), deterministic_json(first))
            self.assertEqual(first["selectedInputs"][0]["path"], "data/staticdata.dat")
            self.assertEqual(first["summary"]["selectedInputBytes"], 7)
            self.assertEqual(first["policy"]["maxSelectedFileBytes"], 8 * 1024 * 1024 * 1024)

    def test_changed_content_changes_relevant_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            first, _ = _build(root)
            (root / "data/staticdata.dat").write_bytes(b"changed")
            second, _ = _build(root)
            self.assertNotEqual(first["selectedInputs"][0]["sha256"], second["selectedInputs"][0]["sha256"])

    def test_missing_and_unsafe_selected_inputs_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            for path in ("../outside.dat", "/tmp/outside.dat", "data/../staticdata.dat", "data\\staticdata.dat", "missing.dat"):
                with self.subTest(path=path), self.assertRaises(ClientReferenceManifestError):
                    _build(root, selected_inputs=[("x", path)])

    def test_duplicate_id_and_duplicate_file_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, selected_inputs=[("x", "data/staticdata.dat"), ("x", "data/staticdata.dat")])
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, selected_inputs=[("x", "data/staticdata.dat"), ("y", "data/staticdata.dat")])

    def test_hardlink_duplicate_file_fails_closed(self) -> None:
        if not hasattr(os, "link"):
            self.skipTest("hardlink unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            alias = root / "data/staticdata-alias.dat"
            try:
                os.link(root / "data/staticdata.dat", alias)
            except OSError as exc:
                self.skipTest(f"hardlink unavailable: {exc}")
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, selected_inputs=[("x", "data/staticdata.dat"), ("y", "data/staticdata-alias.dat")])

    def test_symlink_selected_input_and_symlink_root_fail_closed(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            outside = Path(directory) / "outside.dat"
            outside.write_bytes(b"outside")
            link = root / "data/link.dat"
            try:
                link.symlink_to(outside)
            except OSError as exc:
                self.skipTest(f"symlink unavailable: {exc}")
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, selected_inputs=[("x", "data/link.dat")])
            root_link = Path(directory) / "client-link"
            root_link.symlink_to(root, target_is_directory=True)
            with self.assertRaises(ClientReferenceManifestError):
                _build(root_link)

    def test_file_size_bound_is_checked_before_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, max_file_bytes=3)

    def test_client_build_evidence_rules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            declared, _ = _build(root, client_build_evidence="declared", client_build="15.25")
            self.assertEqual(declared["clientBuild"]["value"], "15.25")
            conflicting, _ = _build(
                root,
                client_build_evidence="conflicting",
                client_build=None,
                client_build_conflicts=["15.25", "15.24", "15.25"],
            )
            self.assertEqual(conflicting["clientBuild"]["conflictingValues"], ["15.24", "15.25"])
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, client_build_evidence="unknown", client_build="15.25")
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, client_build_evidence="conflicting", client_build=None, client_build_conflicts=["15.25"])

    def test_generated_indexes_and_metadata_are_sorted_and_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            manifest, _ = _build(
                root,
                generated_indexes=[("z", "b" * 64), ("a", "A" * 64)],
                package_metadata=[("channel", "stable"), ("source", "local")],
            )
            self.assertEqual([item["id"] for item in manifest["generatedIndexes"]], ["a", "z"])
            self.assertEqual(manifest["generatedIndexes"][0]["sha256"], "a" * 64)
            self.assertEqual(list(manifest["packageMetadata"]), ["channel", "source"])
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, generated_indexes=[("x", "bad")])

    def test_write_is_no_clobber_and_rejects_input_alias(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            manifest, selected = _build(root)
            output = Path(directory) / "manifest.json"
            write_manifest(output, manifest, selected_paths=selected)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["format"], "canary-tibia-client-reference-manifest-v1")
            with self.assertRaises(ClientReferenceManifestError):
                write_manifest(output, manifest, selected_paths=selected)
            with self.assertRaises(ClientReferenceManifestError):
                write_manifest(root / "data/staticdata.dat", manifest, selected_paths=selected, overwrite=True)

    def test_output_symlink_fails_closed(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unavailable")
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            manifest, selected = _build(root)
            target = Path(directory) / "target.json"
            target.write_text("{}\n", encoding="utf-8")
            output = Path(directory) / "manifest-link.json"
            try:
                output.symlink_to(target)
            except OSError as exc:
                self.skipTest(f"symlink unavailable: {exc}")
            with self.assertRaises(ClientReferenceManifestError):
                write_manifest(output, manifest, selected_paths=selected, overwrite=True)

    def test_regular_file_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory)
            (root / "data/subdir").mkdir()
            with self.assertRaises(ClientReferenceManifestError):
                _build(root, selected_inputs=[("x", "data/subdir")])


if __name__ == "__main__":
    unittest.main()
