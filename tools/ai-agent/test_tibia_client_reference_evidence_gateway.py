from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from otbm_evidence_gateway import MAX_SERIALIZED_EXTRACT_BYTES

from tibia_client_reference_evidence_gateway import (
    BINDINGS_FORMAT,
    EXPECTED_FORMAT_BY_KIND,
    REPORT_FORMAT,
    ClientReferenceEvidenceGatewayError,
    build_evidence_plan,
    execute_evidence_plan,
    load_bindings,
    normalize_bindings,
    sha256_path,
)


def _source_spec(
    binding_id: str,
    kind: str,
    *,
    path: str = "source.json",
    sha256: str = "a" * 64,
    pointer: str = "/records/0",
) -> dict:
    return {
        "id": f"{binding_id}.source",
        "path": path,
        "sha256": sha256,
        "format": EXPECTED_FORMAT_BY_KIND[kind],
        "extracts": [
            {
                "id": f"{binding_id}.record",
                "pointer": pointer,
            }
        ],
    }


def _bindings(*rows: dict) -> dict:
    return {
        "format": BINDINGS_FORMAT,
        "schemaVersion": 1,
        "bindings": list(rows),
    }


def _binding(binding_id: str, kind: str, **source_overrides: object) -> dict:
    return {
        "id": binding_id,
        "kind": kind,
        "sources": [_source_spec(binding_id, kind, **source_overrides)],
        "contextReferences": [f"TCR-{kind}"],
    }


class ClientReferenceEvidenceGatewayTests(unittest.TestCase):
    def test_all_reviewed_kinds_normalize_deterministically(self) -> None:
        document = _bindings(
            _binding("z.drift", "drift"),
            _binding("a.house", "house"),
            _binding("m.content", "content"),
            _binding("n.proficiency", "proficiency"),
        )
        normalized = normalize_bindings(document)
        self.assertEqual(
            [row["id"] for row in normalized["bindings"]],
            ["a.house", "m.content", "n.proficiency", "z.drift"],
        )
        self.assertEqual(normalized, normalize_bindings(normalized))

    def test_duplicate_binding_id_fails_closed(self) -> None:
        document = _bindings(
            _binding("same", "house"),
            _binding("same", "drift"),
        )
        with self.assertRaisesRegex(
            ClientReferenceEvidenceGatewayError, "duplicate binding id"
        ):
            normalize_bindings(document)

    def test_kind_requires_exact_stable_source_format(self) -> None:
        row = _binding("house.one", "house")
        row["sources"][0]["format"] = EXPECTED_FORMAT_BY_KIND["content"]
        with self.assertRaisesRegex(
            ClientReferenceEvidenceGatewayError, "requires source format"
        ):
            normalize_bindings(_bindings(row))

    def test_entire_document_extract_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ClientReferenceEvidenceGatewayError, "must not extract an entire"
        ):
            normalize_bindings(
                _bindings(_binding("drift.one", "drift", pointer=""))
            )

    def test_execute_delegates_to_qa018_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "content.json"
            source.write_text(
                json.dumps(
                    {
                        "format": EXPECTED_FORMAT_BY_KIND["content"],
                        "records": [{"id": 7, "name": "Rat"}],
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            binding_id = "content.rat"
            bindings_path = root / "bindings.json"
            bindings_path.write_text(
                json.dumps(
                    _bindings(
                        _binding(
                            binding_id,
                            "content",
                            path="content.json",
                            sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        )
                    ),
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            normalized = normalize_bindings(load_bindings(bindings_path))
            plan = build_evidence_plan(
                normalized,
                binding_id,
                bindings_file_sha256=sha256_path(bindings_path),
            )
            first = execute_evidence_plan(bindings_path, plan)
            second = execute_evidence_plan(bindings_path, plan)
            self.assertEqual(first, second)
            self.assertEqual(first["format"], REPORT_FORMAT)
            self.assertEqual(first["mode"], "executed")
            self.assertEqual(
                first["evidenceBundle"]["extracts"][0]["value"],
                {"id": 7, "name": "Rat"},
            )
            self.assertTrue(first["policy"]["qa018EvidenceGatewayReused"])
            self.assertFalse(first["policy"]["parsesSourceReports"])

    def test_stale_bindings_file_fails_closed(self) -> None:
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
            bindings_path = root / "bindings.json"
            bindings_path.write_text(
                json.dumps(
                    _bindings(
                        _binding(
                            "drift.one",
                            "drift",
                            sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        )
                    )
                ),
                encoding="utf-8",
            )
            normalized = normalize_bindings(load_bindings(bindings_path))
            plan = build_evidence_plan(
                normalized,
                "drift.one",
                bindings_file_sha256=sha256_path(bindings_path),
            )
            bindings_path.write_text(
                bindings_path.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ClientReferenceEvidenceGatewayError,
                "bindings file SHA-256 changed",
            ):
                execute_evidence_plan(bindings_path, plan)

    def test_changed_source_hash_fails_closed_through_qa018(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(
                json.dumps(
                    {
                        "format": EXPECTED_FORMAT_BY_KIND["proficiency"],
                        "records": [{"id": 1}],
                    }
                ),
                encoding="utf-8",
            )
            expected_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            bindings_path = root / "bindings.json"
            bindings_path.write_text(
                json.dumps(
                    _bindings(
                        _binding(
                            "proficiency.one",
                            "proficiency",
                            sha256=expected_sha,
                        )
                    )
                ),
                encoding="utf-8",
            )
            plan = build_evidence_plan(
                normalize_bindings(load_bindings(bindings_path)),
                "proficiency.one",
                bindings_file_sha256=sha256_path(bindings_path),
            )
            source.write_text(
                json.dumps(
                    {
                        "format": EXPECTED_FORMAT_BY_KIND["proficiency"],
                        "records": [{"id": 2}],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ClientReferenceEvidenceGatewayError,
                "QA-018 evidence extraction failed.*SHA-256 mismatch",
            ):
                execute_evidence_plan(bindings_path, plan)

    def test_plan_tampering_fails_closed(self) -> None:
        document = normalize_bindings(
            _bindings(_binding("house.one", "house"))
        )
        plan = build_evidence_plan(
            document, "house.one", bindings_file_sha256="b" * 64
        )
        plan["kind"] = "drift"
        with tempfile.TemporaryDirectory() as directory:
            bindings_path = Path(directory) / "bindings.json"
            bindings_path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(
                ClientReferenceEvidenceGatewayError, "reportSha256"
            ):
                execute_evidence_plan(bindings_path, plan)

    def test_oversized_extract_fails_closed_through_qa018(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(
                json.dumps(
                    {
                        "format": EXPECTED_FORMAT_BY_KIND["house"],
                        "records": ["x" * (MAX_SERIALIZED_EXTRACT_BYTES + 1)],
                    }
                ),
                encoding="utf-8",
            )
            bindings_path = root / "bindings.json"
            bindings_path.write_text(
                json.dumps(
                    _bindings(
                        _binding(
                            "house.large",
                            "house",
                            sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                        )
                    )
                ),
                encoding="utf-8",
            )
            plan = build_evidence_plan(
                normalize_bindings(load_bindings(bindings_path)),
                "house.large",
                bindings_file_sha256=sha256_path(bindings_path),
            )
            with self.assertRaisesRegex(
                ClientReferenceEvidenceGatewayError,
                "QA-018 evidence extraction failed.*exceeds",
            ):
                execute_evidence_plan(bindings_path, plan)

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bindings.json"
            path.write_text(
                '{"format":"x","format":"y","schemaVersion":1,"bindings":[]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ClientReferenceEvidenceGatewayError, "duplicate JSON object key"
            ):
                load_bindings(path)


if __name__ == "__main__":
    unittest.main()
