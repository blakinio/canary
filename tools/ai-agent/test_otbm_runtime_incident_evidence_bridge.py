from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from otbm_runtime_incident_evidence_bridge import (
    BINDINGS_FORMAT,
    REPORT_FORMAT,
    RuntimeIncidentEvidenceBridgeError,
    build_incident_evidence_plan,
    canonical_sha256,
    execute_incident_evidence_plan,
    normalize_bindings,
    normalize_selector,
    resolve_binding,
    sha256_path,
)

SOURCE_FORMAT = "synthetic-otbm-evidence-v1"


def _source_spec(*, sha256: str, path: str = "source.json", pointer: str = "/payload") -> dict:
    return {
        "id": "source",
        "path": path,
        "sha256": sha256,
        "format": SOURCE_FORMAT,
        "extracts": [{"id": "payload", "pointer": pointer}],
    }


def bindings_document(selector: dict, *, sha256: str = "a" * 64, context_references=None, source=None) -> dict:
    return {
        "format": BINDINGS_FORMAT,
        "schemaVersion": 1,
        "bindings": [
            {
                "id": "binding-1",
                "selector": selector,
                "sources": [source or _source_spec(sha256=sha256)],
                "contextReferences": context_references or [],
            }
        ],
    }


class RuntimeIncidentEvidenceBridgeTests(unittest.TestCase):
    def test_supported_selector_kinds_normalize_exactly(self):
        cases = [
            ({"kind": "position", "value": [32369, 32241, 7]}, {"kind": "position", "value": [32369, 32241, 7]}),
            ({"kind": "transition-id", "value": " transition-1 "}, {"kind": "transition-id", "value": "transition-1"}),
            ({"kind": "interaction-id", "value": "interaction-1"}, {"kind": "interaction-id", "value": "interaction-1"}),
            ({"kind": "landmark-id", "value": "thais.temple"}, {"kind": "landmark-id", "value": "thais.temple"}),
            ({"kind": "route-id", "value": "thais-temple-depot"}, {"kind": "route-id", "value": "thais-temple-depot"}),
            ({"kind": "preflight-reference", "value": "preflight:thais"}, {"kind": "preflight-reference", "value": "preflight:thais"}),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(normalize_selector(raw), expected)

    def test_unsupported_selector_kind_fails_closed(self):
        with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "unsupported selector kind"):
            normalize_selector({"kind": "log-line", "value": "timeout"})

    def test_invalid_position_fails_closed(self):
        with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "outside OTBM coordinate range"):
            normalize_selector({"kind": "position", "value": [1, 2, 16]})

    def test_duplicate_selector_binding_is_rejected_as_ambiguous(self):
        document = bindings_document({"kind": "route-id", "value": "route-1"})
        duplicate = dict(document["bindings"][0])
        duplicate["id"] = "binding-2"
        document["bindings"].append(duplicate)
        with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "duplicate/ambiguous selector"):
            normalize_bindings(document)

    def test_missing_selector_binding_fails_closed(self):
        document = bindings_document({"kind": "route-id", "value": "route-1"})
        with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "no reviewed incident evidence binding"):
            resolve_binding(document, {"kind": "route-id", "value": "route-2"})

    def test_binding_normalization_delegates_qa018_manifest_validation(self):
        document = bindings_document(
            {"kind": "route-id", "value": "route-1"},
            source={
                "id": "source",
                "path": "../escape.json",
                "sha256": "a" * 64,
                "format": SOURCE_FORMAT,
                "extracts": [{"id": "payload", "pointer": "/payload"}],
            },
        )
        with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "invalid QA-018"):
            normalize_bindings(document)

    def test_plan_is_deterministic_and_does_not_read_evidence_sources(self):
        document = bindings_document(
            {"kind": "route-id", "value": "route-1"},
            sha256="f" * 64,
            context_references=["triage:artifact/result.json", "triage:artifact/result.json"],
        )
        first = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256="b" * 64)
        second = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256="b" * 64)
        self.assertEqual(first, second)
        self.assertEqual(first["format"], REPORT_FORMAT)
        self.assertEqual(first["mode"], "plan")
        self.assertIsNone(first["evidenceBundle"])
        self.assertIsNone(first["evidenceBundleSha256"])
        self.assertEqual(first["contextReferences"], ["triage:artifact/result.json"])
        self.assertFalse(first["policy"]["parsesRuntimeLogs"])
        self.assertFalse(first["policy"]["classifiesFailure"])
        self.assertFalse(first["policy"]["diagnosesRootCause"])
        self.assertFalse(first["policy"]["emitsNextAction"])
        self.assertTrue(first["policy"]["qa018EvidenceGatewayReused"])

    def test_execution_embeds_exact_qa018_bundle_and_hash(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.json"
            source.write_text(json.dumps({"format": SOURCE_FORMAT, "payload": {"route": "route-1", "distance": 59}}), encoding="utf-8")
            document = bindings_document({"kind": "route-id", "value": "route-1"}, sha256=sha256_path(source))
            bindings_path = root / "bindings.json"
            bindings_path.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")
            plan = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256=sha256_path(bindings_path))
            report = execute_incident_evidence_plan(bindings_path, plan)
            self.assertEqual(report["mode"], "executed")
            self.assertEqual(report["bindingId"], "binding-1")
            self.assertEqual(report["selector"], {"kind": "route-id", "value": "route-1"})
            self.assertEqual(report["evidenceBundle"]["format"], "canary-otbm-evidence-bundle-v1")
            self.assertEqual(report["evidenceBundleSha256"], report["evidenceBundle"]["bundleSha256"])
            self.assertEqual(report["evidenceBundle"]["extracts"][0]["value"], {"route": "route-1", "distance": 59})
            unsigned = dict(report)
            supplied = unsigned.pop("reportSha256")
            self.assertEqual(supplied, canonical_sha256(unsigned))

    def test_qa018_sha_mismatch_remains_fail_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.json"
            source.write_text(json.dumps({"format": SOURCE_FORMAT, "payload": 1}), encoding="utf-8")
            document = bindings_document({"kind": "route-id", "value": "route-1"}, sha256="0" * 64)
            bindings_path = root / "bindings.json"
            bindings_path.write_text(json.dumps(document), encoding="utf-8")
            plan = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256=sha256_path(bindings_path))
            with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "QA-018 evidence extraction failed.*SHA-256 mismatch"):
                execute_incident_evidence_plan(bindings_path, plan)

    def test_qa018_format_mismatch_remains_fail_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.json"
            source.write_text(json.dumps({"format": "wrong-format", "payload": 1}), encoding="utf-8")
            document = bindings_document({"kind": "route-id", "value": "route-1"}, sha256=sha256_path(source))
            bindings_path = root / "bindings.json"
            bindings_path.write_text(json.dumps(document), encoding="utf-8")
            plan = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256=sha256_path(bindings_path))
            with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "QA-018 evidence extraction failed.*format mismatch"):
                execute_incident_evidence_plan(bindings_path, plan)

    def test_qa018_missing_pointer_remains_fail_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.json"
            source.write_text(json.dumps({"format": SOURCE_FORMAT, "payload": 1}), encoding="utf-8")
            document = bindings_document(
                {"kind": "route-id", "value": "route-1"},
                sha256=sha256_path(source),
                source=_source_spec(sha256=sha256_path(source), pointer="/missing"),
            )
            bindings_path = root / "bindings.json"
            bindings_path.write_text(json.dumps(document), encoding="utf-8")
            plan = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256=sha256_path(bindings_path))
            with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "QA-018 evidence extraction failed.*missing object key"):
                execute_incident_evidence_plan(bindings_path, plan)

    def test_bindings_file_change_between_plan_and_execution_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "source.json"
            source.write_text(json.dumps({"format": SOURCE_FORMAT, "payload": 1}), encoding="utf-8")
            document = bindings_document({"kind": "route-id", "value": "route-1"}, sha256=sha256_path(source))
            bindings_path = root / "bindings.json"
            bindings_path.write_text(json.dumps(document), encoding="utf-8")
            plan = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256=sha256_path(bindings_path))
            bindings_path.write_text(json.dumps(document, indent=2), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "bindings file SHA-256 changed"):
                execute_incident_evidence_plan(bindings_path, plan)

    def test_tampered_plan_is_rejected(self):
        document = bindings_document({"kind": "route-id", "value": "route-1"})
        plan = build_incident_evidence_plan(document, {"kind": "route-id", "value": "route-1"}, bindings_file_sha256="b" * 64)
        plan["bindingId"] = "tampered"
        with tempfile.TemporaryDirectory() as raw:
            bindings_path = Path(raw) / "bindings.json"
            bindings_path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeIncidentEvidenceBridgeError, "plan reportSha256"):
                execute_incident_evidence_plan(bindings_path, plan)


if __name__ == "__main__":
    unittest.main()
