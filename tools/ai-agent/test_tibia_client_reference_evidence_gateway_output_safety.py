from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tibia_client_reference_evidence_gateway import (
    BINDINGS_FORMAT,
    EXPECTED_FORMAT_BY_KIND,
    ClientReferenceEvidenceGatewayError,
    write_report,
)
from tibia_client_reference_evidence_gateway_tool import _safe_relative_output, main


class ClientReferenceEvidenceGatewayOutputSafetyTests(unittest.TestCase):
    def test_create_new_and_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.json"
            write_report(output, {"value": 1}, overwrite=False)
            with self.assertRaises(ClientReferenceEvidenceGatewayError):
                write_report(output, {"value": 2}, overwrite=False)
            write_report(output, {"value": 3}, overwrite=True)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")), {"value": 3}
            )

    def test_symlink_output_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaises(ClientReferenceEvidenceGatewayError):
                write_report(link, {}, overwrite=True)

    def test_relative_output_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaises(ClientReferenceEvidenceGatewayError):
                _safe_relative_output(root, Path("../output.json"))

    def test_cli_rejects_bindings_collision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(
                json.dumps(
                    {
                        "format": EXPECTED_FORMAT_BY_KIND["drift"],
                        "records": [{"id": "f1"}],
                    }
                ),
                encoding="utf-8",
            )
            bindings = root / "bindings.json"
            bindings.write_text(
                json.dumps(
                    {
                        "format": BINDINGS_FORMAT,
                        "schemaVersion": 1,
                        "bindings": [
                            {
                                "id": "drift.one",
                                "kind": "drift",
                                "sources": [
                                    {
                                        "id": "drift.one.source",
                                        "path": "source.json",
                                        "sha256": hashlib.sha256(
                                            source.read_bytes()
                                        ).hexdigest(),
                                        "format": EXPECTED_FORMAT_BY_KIND["drift"],
                                        "extracts": [
                                            {
                                                "id": "drift.one.record",
                                                "pointer": "/records/0",
                                            }
                                        ],
                                    }
                                ],
                                "contextReferences": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = main(
                [
                    "--bindings",
                    str(bindings),
                    "--binding-id",
                    "drift.one",
                    "--output",
                    "bindings.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(result, 2)

    def test_cli_rejects_source_collision(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(
                json.dumps(
                    {
                        "format": EXPECTED_FORMAT_BY_KIND["house"],
                        "records": [{"id": 1}],
                    }
                ),
                encoding="utf-8",
            )
            bindings = root / "bindings.json"
            bindings.write_text(
                json.dumps(
                    {
                        "format": BINDINGS_FORMAT,
                        "schemaVersion": 1,
                        "bindings": [
                            {
                                "id": "house.one",
                                "kind": "house",
                                "sources": [
                                    {
                                        "id": "house.one.source",
                                        "path": "source.json",
                                        "sha256": hashlib.sha256(
                                            source.read_bytes()
                                        ).hexdigest(),
                                        "format": EXPECTED_FORMAT_BY_KIND["house"],
                                        "extracts": [
                                            {
                                                "id": "house.one.record",
                                                "pointer": "/records/0",
                                            }
                                        ],
                                    }
                                ],
                                "contextReferences": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = main(
                [
                    "--bindings",
                    str(bindings),
                    "--binding-id",
                    "house.one",
                    "--output",
                    "source.json",
                    "--plan-only",
                ]
            )
            self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
