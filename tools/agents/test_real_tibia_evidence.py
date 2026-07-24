from __future__ import annotations

from real_tibia_evidence_test_support import *


class RealTibiaEvidenceContractTests(EvidenceTestCase):
    def test_repository_contracts_and_generated_files_are_current(self) -> None:
        corpus = Corpus.load(self.repo)
        self.assertEqual(corpus.validate(AS_OF).errors, ())
        self.assertEqual(write_generated(corpus, check=True, as_of=AS_OF), 0)

    def test_valid_record_request_history_and_indexes(self) -> None:
        record = self.record()
        record["owner_request_refs"] = ["RTREQ-E2E-COMBAT-0001"]
        self.write_record(record)
        self.write_request(self.request())
        dump(self.root / "docs/agents/real-tibia/evidence/modules/combat/VERSION_HISTORY.yaml", history())
        self.refresh()
        corpus = Corpus.load(self.root)
        self.assertEqual(corpus.validate(AS_OF).errors, ())
        generated = corpus.generated_indexes(AS_OF)
        self.assertEqual(generated["evidence_by_module"], {"combat": ["RT-COMBAT-0001"]})
        self.assertEqual(generated["proof_maturity_by_dimension"]["combat"]["current-canary-behavior"]["proof_level"], "definition-found")

    def test_generation_is_filesystem_order_independent(self) -> None:
        first, second = self.record("RT-COMBAT-0001"), self.record("RT-COMBAT-0002")
        self.write_record(second); self.write_record(first)
        a = Corpus.load(self.root).generated_indexes(AS_OF)
        shutil.rmtree(self.root / "docs/agents/real-tibia/evidence/modules")
        self.write_record(first); self.write_record(second)
        self.assertEqual(a, Corpus.load(self.root).generated_indexes(AS_OF))

    def test_duplicate_json_and_record_ids_fail_closed(self) -> None:
        path = self.root / "docs/agents/real-tibia/evidence/modules/combat/records/RT-COMBAT-0001.yaml"
        path.parent.mkdir(parents=True)
        path.write_text('{"format":"a","format":"b"}\n')
        with self.assertRaisesRegex(EvidenceError, "duplicate JSON object key"):
            Corpus.load(self.root)
        path.unlink()
        record = self.record(); self.write_record(record); self.write_record(record, module_dir="protocol")
        request = self.request(); self.write_request(request); self.write_request(request, "feature")
        h = history(); h["events"].append(copy.deepcopy(h["events"][0]))
        dump(self.root / "docs/agents/real-tibia/evidence/modules/combat/VERSION_HISTORY.yaml", h)
        codes = self.codes()
        self.assertTrue({"RTEC-DUPLICATE-EVIDENCE-ID", "RTEC-DUPLICATE-REQUEST-ID", "RTEC-DUPLICATE-HISTORY-ID"} <= codes)

    def test_module_enum_id_and_path_rules(self) -> None:
        record = self.record("RT-PROTOCOL-0001", "missing")
        record["authority_dimension"] = "invented"
        self.write_record(record)
        codes = self.codes()
        self.assertTrue({"RTEC-MODULE-ID", "RTEC-ENUM", "RTEC-EVIDENCE-ID"} <= codes)

    def test_unsafe_paths_symlinks_and_unregistered_files_are_rejected(self) -> None:
        record = self.record(); record["sources"][0]["locator"]["repository_path"] = "../secret"
        self.write_record(record)
        self.assertIn("RTEC-UNSAFE-PATH", self.codes())
        shutil.rmtree(self.root / "docs/agents/real-tibia/evidence/modules")
        outside = self.root / "outside.yaml"; outside.write_text("{}\n")
        target = self.root / "docs/agents/real-tibia/evidence/modules/combat/records/RT-COMBAT-0001.yaml"
        target.parent.mkdir(parents=True)
        try:
            target.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        with self.assertRaisesRegex(EvidenceError, "symlink"):
            Corpus.load(self.root)
        target.unlink(); dump(self.root / "docs/agents/real-tibia/evidence/manual.json", {})
        with self.assertRaisesRegex(EvidenceError, "unregistered machine-readable"):
            Corpus.load(self.root)

    def test_empty_placeholder_module_tree_is_rejected(self) -> None:
        (self.root / "docs/agents/real-tibia/evidence/modules/combat").mkdir(parents=True)
        self.refresh()
        self.assertIn("RTEC-EMPTY-MODULE-DIRECTORY", self.codes(False))

    def test_malformed_hash_date_and_version_axis_are_rejected(self) -> None:
        record = self.record()
        record["sources"][0]["locator"]["commit_sha"] = "bad"
        record["freshness"]["observed_or_verified_at"] = "2026-99-99"
        record["current_canary_comparison"]["baseline"]["map_sha256"] = "bad"
        record["applicability"]["observed_in"] = [marker("EXACT", "RT-COMBAT-0001", datapack_revision="\ninvalid")]
        self.write_record(record)
        self.assertTrue({"RTEC-COMMIT-SHA", "RTEC-SHA256", "RTEC-DATE", "RTEC-VERSION-VALUE"} <= self.codes())

    def test_explicit_proof_boundaries_are_required(self) -> None:
        record = self.record(); record["proves"] = []; record["sources"][0]["does_not_prove"] = []
        self.write_record(record)
        self.assertIn("RTEC-PROOF-BOUNDARY", self.codes())

    def test_static_and_lower_proof_cannot_be_promoted(self) -> None:
        for level in ("gameplay-proven", "physical-client-proven"):
            with self.subTest(level=level):
                record = self.record(); record["proof_level"] = level
                record["sources"][0]["proof_level_reached"] = level
                self.write_record(record)
                codes = self.codes()
                self.assertIn("RTEC-PROOF-PROMOTION", codes)
                if level == "gameplay-proven": self.assertIn("RTEC-STATIC-PROMOTION", codes)

    def test_unknown_conflict_and_missing_references_remain_explicit(self) -> None:
        record = self.record(); record["uncertainty"] = []
        self.write_record(record); self.assertIn("RTEC-UNCERTAINTY", self.codes())
        record["evidence_state"] = "CONFLICT"; record["uncertainty"] = ["Sources disagree."]
        self.write_record(record); self.assertIn("RTEC-CONFLICT-REFS", self.codes())
        record["conflict_refs"] = ["RT-COMBAT-9999"]; record["owner_request_refs"] = ["RTREQ-E2E-COMBAT-9999"]
        self.write_record(record)
        codes = self.codes()
        self.assertTrue({"RTEC-MISSING-EVIDENCE-REF", "RTEC-MISSING-REQUEST-REF"} <= codes)

    def test_evidence_supersession_is_reciprocal_and_acyclic(self) -> None:
        old, new = self.record("RT-COMBAT-0001"), self.record("RT-COMBAT-0002")
        old.update(record_status="superseded", evidence_state="SUPERSEDED", superseded_by=["RT-COMBAT-0002"])
        new["supersedes"] = ["RT-COMBAT-0001"]
        self.write_record(old); self.write_record(new)
        self.assertNotIn("RTEC-SUPERSESSION-RECIPROCAL", self.codes())
        old["supersedes"] = ["RT-COMBAT-0002"]; new["superseded_by"] = ["RT-COMBAT-0001"]
        self.write_record(old); self.write_record(new)
        self.assertIn("RTEC-SUPERSESSION-CYCLE", self.codes())


if __name__ == "__main__":
    import unittest
    unittest.main()
