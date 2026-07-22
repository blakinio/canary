from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from otbm_evidence_gateway import EvidenceGatewayError, build_evidence_bundle, normalize_manifest, resolve_pointer


class EvidenceGatewayTests(unittest.TestCase):
    def test_json_pointer_resolution(self) -> None:
        document = {"a": {"b": [10, {"x/y": "value"}]}}
        self.assertEqual(resolve_pointer(document, "/a/b/0"), 10)
        self.assertEqual(resolve_pointer(document, "/a/b/1/x~1y"), "value")

    def test_exact_source_extract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(json.dumps({"format": "fixture-v1", "summary": {"errors": 3}}), encoding="utf-8")
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            manifest_path = root / "manifest.json"
            manifest = normalize_manifest({
                "format": "canary-otbm-evidence-gateway-manifest-v1",
                "sources": [{"id": "quality", "path": "source.json", "sha256": sha, "format": "fixture-v1", "extracts": [{"id": "quality.errors", "pointer": "/summary/errors"}]}],
            })
            bundle = build_evidence_bundle(manifest_path, manifest)
            self.assertEqual(bundle["extracts"][0]["value"], 3)
            self.assertEqual(bundle["summary"], {"sourceCount": 1, "extractCount": 1})

    def test_hash_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.json").write_text(json.dumps({"format": "fixture-v1"}), encoding="utf-8")
            manifest = normalize_manifest({
                "format": "canary-otbm-evidence-gateway-manifest-v1",
                "sources": [{"id": "x", "path": "source.json", "sha256": "a" * 64, "format": "fixture-v1", "extracts": [{"id": "x.root", "pointer": ""}]}],
            })
            with self.assertRaises(EvidenceGatewayError):
                build_evidence_bundle(root / "manifest.json", manifest)

    def test_format_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(json.dumps({"format": "actual-v1"}), encoding="utf-8")
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            manifest = normalize_manifest({
                "format": "canary-otbm-evidence-gateway-manifest-v1",
                "sources": [{"id": "x", "path": "source.json", "sha256": sha, "format": "expected-v1", "extracts": [{"id": "x.root", "pointer": ""}]}],
            })
            with self.assertRaises(EvidenceGatewayError):
                build_evidence_bundle(root / "manifest.json", manifest)

    def test_unsafe_source_path_rejected(self) -> None:
        with self.assertRaises(EvidenceGatewayError):
            normalize_manifest({
                "format": "canary-otbm-evidence-gateway-manifest-v1",
                "sources": [{"id": "x", "path": "../source.json", "sha256": "a" * 64, "format": "x-v1", "extracts": [{"id": "x.root", "pointer": ""}]}],
            })

    def test_bundle_hash_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.json"
            source.write_text(json.dumps({"format": "fixture-v1", "value": 1}), encoding="utf-8")
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            manifest = normalize_manifest({"format": "canary-otbm-evidence-gateway-manifest-v1", "sources": [{"id": "x", "path": "source.json", "sha256": sha, "format": "fixture-v1", "extracts": [{"id": "x.value", "pointer": "/value"}]}]})
            first = build_evidence_bundle(root / "manifest.json", manifest)
            second = build_evidence_bundle(root / "manifest.json", manifest)
            self.assertEqual(first["bundleSha256"], second["bundleSha256"])


if __name__ == "__main__":
    unittest.main()
