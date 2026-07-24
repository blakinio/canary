from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from tibia_proficiency_reference_correlation import (
    APPEARANCES_INDEX_FORMAT, CANARY_EVIDENCE_FORMAT, CORRELATION_FORMAT, RESOLVER_FORMAT,
    ProficiencyReferenceCorrelationError, _semantic_sha, build_canary_evidence, build_correlation,
    derive_resolver, deterministic_json, write_json,
)
from tibia_proficiency_reference_test_support import (
    SHA_A, SHA_B, SHA_C, SHA_D, appearances, canary_evidence,
    proficiency_index, resolved_fixture, source_entry,
)

class ProficiencyReferenceCorrelationTests(unittest.TestCase):

    def test_derives_reviewed_mapping_and_item_binding(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture(
                appearance=appearances([(100, 10, "A"), (101, 10, "B")])
            )
            self.assertEqual(resolver["format"], RESOLVER_FORMAT)
            self.assertEqual(resolver["summary"]["mappingCount"], 1)
            self.assertEqual([item["canaryItemId"] for item in resolver["mappings"][0]["items"]], [100, 101])
            self.assertFalse(resolver["policy"]["numericEqualityAloneAccepted"])

    def test_missing_appearance_binding_remains_unresolved(self) -> None:
            resolver = derive_resolver(
                proficiency_index=proficiency_index(),
                proficiency_index_sha256=SHA_A,
                appearances_index=appearances([]),
                appearances_index_sha256=SHA_B,
                canary_evidence=canary_evidence(),
                canary_evidence_sha256=SHA_C,
                review_id="review-1",
                review_statement="Reviewed.",
            )
            self.assertEqual(resolver["summary"]["mappingCount"], 0)
            self.assertEqual(resolver["findings"][0]["state"], "unresolved-id-space")
            self.assertIn("appearance-binding-missing", resolver["findings"][0]["reasons"])

    def test_semantic_mismatch_is_conflicting(self) -> None:
            mismatch = canary_evidence(
                [{"sourceOrdinal": 1, "proficiencyId": 10, "name": "Test Blade", "semanticSha256": SHA_D}]
            )
            resolver = derive_resolver(
                proficiency_index=proficiency_index(),
                proficiency_index_sha256=SHA_A,
                appearances_index=appearances(),
                appearances_index_sha256=SHA_B,
                canary_evidence=mismatch,
                canary_evidence_sha256=SHA_C,
                review_id="review-1",
                review_statement="Reviewed.",
            )
            self.assertEqual(resolver["findings"][0]["state"], "conflicting")
            self.assertIn("definition-semantics-mismatch", resolver["findings"][0]["reasons"])

    def test_duplicate_source_id_is_conflicting(self) -> None:
            source = proficiency_index([source_entry(10, "A", 1), source_entry(10, "B", 2)])
            resolver = derive_resolver(
                proficiency_index=source,
                proficiency_index_sha256=SHA_A,
                appearances_index=appearances(),
                appearances_index_sha256=SHA_B,
                canary_evidence=canary_evidence(),
                canary_evidence_sha256=SHA_C,
                review_id="review-1",
                review_statement="Reviewed.",
            )
            self.assertEqual(resolver["summary"]["mappingCount"], 0)
            self.assertTrue(all(item["state"] == "conflicting" for item in resolver["findings"]))

    def test_confirmed_correlation_keeps_proof_dimensions_separate(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture(
                evidence=canary_evidence(protocol="source-supported", automated="test-supported", physical="not-supplied")
            )
            report = build_correlation(
                proficiency_index=source,
                proficiency_index_sha256=SHA_A,
                appearances_index=appearance,
                appearances_index_sha256=SHA_B,
                canary_evidence=evidence,
                canary_evidence_sha256=SHA_C,
                resolver=resolver,
                resolver_sha256=SHA_D,
            )
            self.assertEqual(report["format"], CORRELATION_FORMAT)
            row = report["rows"][0]
            self.assertEqual(row["state"], "confirmed-reference")
            self.assertEqual(row["dimensions"]["protocolClient"], "source-supported")
            self.assertEqual(row["dimensions"]["automatedBehavior"], "test-supported")
            self.assertEqual(row["dimensions"]["physicalE2E"], "not-supplied")
            self.assertFalse(report["policy"]["gameplayConclusions"])

    def test_target_only_rows_are_explicit(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture(
                appearance=appearances([(100, 10, "A"), (200, 20, "Target only")]),
                evidence=canary_evidence(
                    [
                        {"sourceOrdinal": 1, "proficiencyId": 10, "name": "Test Blade", "semanticSha256": _semantic_sha(source_entry())},
                        {"sourceOrdinal": 2, "proficiencyId": 20, "name": "Target only", "semanticSha256": SHA_D},
                    ]
                ),
            )
            report = build_correlation(
                proficiency_index=source,
                proficiency_index_sha256=SHA_A,
                appearances_index=appearance,
                appearances_index_sha256=SHA_B,
                canary_evidence=evidence,
                canary_evidence_sha256=SHA_C,
                resolver=resolver,
                resolver_sha256=SHA_D,
            )
            target_rows = [row for row in report["rows"] if row["rowKind"] == "target-only"]
            self.assertEqual([row["targetProficiencyId"] for row in target_rows], [20])

    def test_missing_resolver_mapping_does_not_promote_numeric_equality(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture()
            resolver["mappings"] = []
            report = build_correlation(
                proficiency_index=source,
                proficiency_index_sha256=SHA_A,
                appearances_index=appearance,
                appearances_index_sha256=SHA_B,
                canary_evidence=evidence,
                canary_evidence_sha256=SHA_C,
                resolver=resolver,
                resolver_sha256=SHA_D,
            )
            self.assertEqual(report["rows"][0]["state"], "unresolved-id-space")

    def test_stale_resolver_provenance_fails_closed(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture()
            with self.assertRaisesRegex(ProficiencyReferenceCorrelationError, "provenance mismatch"):
                build_correlation(
                    proficiency_index=source,
                    proficiency_index_sha256=SHA_D,
                    appearances_index=appearance,
                    appearances_index_sha256=SHA_B,
                    canary_evidence=evidence,
                    canary_evidence_sha256=SHA_C,
                    resolver=resolver,
                    resolver_sha256=SHA_D,
                )


if __name__ == "__main__":
    unittest.main()
