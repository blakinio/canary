from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from otbm_identifier_integrity import IdentifierIntegrityError
from otbm_identifier_integrity_tool import (
    _prepare_output,
    _stable_json,
    _validate_interaction_provenance,
    _write_json,
)


class IdentifierIntegrityOutputSafetyTests(unittest.TestCase):
    def test_create_new_refuses_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            output.write_text("existing\n", encoding="utf-8")
            with self.assertRaisesRegex(IdentifierIntegrityError, "already exists"):
                _prepare_output(output, [], overwrite=False)

    def test_output_cannot_alias_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "input.json"
            source.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(IdentifierIntegrityError, "must not be one of the input files"):
                _prepare_output(source, [source.resolve()], overwrite=True)

    def test_hard_link_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "input.json"
            output = root / "output.json"
            source.write_text("{}\n", encoding="utf-8")
            os.link(source, output)
            with self.assertRaisesRegex(IdentifierIntegrityError, "hard link"):
                _prepare_output(output, [source.resolve()], overwrite=True)

    def test_symlink_json_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.json"
            link = root / "link.json"
            source.write_text(json.dumps({"format": "canary-otbm-identifier-integrity-policy-v1"}), encoding="utf-8")
            try:
                link.symlink_to(source)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            with self.assertRaisesRegex(IdentifierIntegrityError, "must not be a symlink"):
                _stable_json(link, "policy", "canary-otbm-identifier-integrity-policy-v1")

    def test_interaction_registry_internal_provenance_must_match_evidence_set(self) -> None:
        registry = {
            "format": "canary-otbm-route-interactions-v1",
            "schemaVersion": 1,
            "registryStatus": "reviewed",
            "provenance": {
                "sourceMap": {"sha256": "f" * 64},
                "worldIndex": {"sha256": "b" * 64},
                "transitionManifest": None,
                "scriptResolution": None,
            },
            "entries": [],
        }
        with self.assertRaisesRegex(IdentifierIntegrityError, "provenance is incompatible"):
            _validate_interaction_provenance(
                registry,
                source_map_sha256="a" * 64,
                world_index_sha256="b" * 64,
                transition_manifest_sha256=None,
                script_resolution_sha256=None,
            )

    def test_create_new_writes_deterministic_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            _write_json(output, {"b": 2, "a": 1}, overwrite=False)
            self.assertEqual(output.read_text(encoding="utf-8"), '{\n  "a": 1,\n  "b": 2\n}\n')


if __name__ == "__main__":
    unittest.main()
