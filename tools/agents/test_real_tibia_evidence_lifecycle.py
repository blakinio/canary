from __future__ import annotations

from real_tibia_evidence_test_support import *


class RealTibiaEvidenceLifecycleTests(EvidenceTestCase):
    def test_version_history_rejects_invented_exact_and_accepts_derived_range(self) -> None:
        record = self.record(); record["applicability"]["introduced_in"] = marker("EXACT", "RT-COMBAT-0001", official_tibia_release="15.25")
        self.write_record(record)
        self.assertIn("RTEC-INTRODUCTION-VERSION", self.codes())
        record["applicability"]["introduced_in"] = marker(); self.write_record(record)
        h = history(); event = h["events"][0]
        event.update(event_type="unknown-first-version", confidence="derived-range")
        event["version"] = {
            "mode": "DERIVED_RANGE", "exact": None,
            "lower_bound": axes(official_tibia_release="15.20"),
            "upper_bound": axes(official_tibia_release="15.25"),
            "evidence_refs": ["RT-COMBAT-0001"], "notes": ["First exact release is unknown."],
        }
        dump(self.root / "docs/agents/real-tibia/evidence/modules/combat/VERSION_HISTORY.yaml", h)
        self.assertEqual(self.codes(), set())

    def test_request_transitions_and_owner_evidence(self) -> None:
        self.write_record(self.record())
        request = self.request(); request["status"] = "active"
        request["history"].append({
            "at": "2026-07-24T22:00:00+02:00", "actor": "owner", "actor_role": "owner",
            "actor_task": "CAN-OWNER", "actor_pr": 1, "from_status": "draft", "to_status": "active",
            "reason": "Invalid jump.", "owner_evidence_ref": "owner-pr-1",
        })
        self.write_request(request); self.assertIn("RTEC-REQUEST-TRANSITION", self.codes())
        request = self.request(); request["status"] = "accepted-by-owner"
        request["history"] += [
            {"at":"2026-07-24T22:00:00+02:00","actor":"collector","actor_role":"collector","actor_task":"CAN-TEST","actor_pr":1,"from_status":"draft","to_status":"ready-for-owner-triage","reason":"Ready.","owner_evidence_ref":None},
            {"at":"2026-07-24T23:00:00+02:00","actor":"collector","actor_role":"collector","actor_task":"CAN-TEST","actor_pr":1,"from_status":"ready-for-owner-triage","to_status":"accepted-by-owner","reason":"Invalid actor.","owner_evidence_ref":None},
        ]
        self.write_request(request); self.assertIn("RTEC-OWNER-EVIDENCE", self.codes())
        request["history"][-1].update(actor="owner", actor_role="owner", actor_task="CAN-OWNER", actor_pr=2, owner_evidence_ref="owner-pr-2")
        self.write_request(request); self.assertEqual(self.codes(), set())

    def test_result_available_requires_complete_result_boundaries(self) -> None:
        self.write_record(self.record()); request = self.request(); request["status"] = "result-available"
        self.write_request(request)
        self.assertTrue({"RTEC-REQUEST-RESULT", "RTEC-REQUEST-TRANSITION"} <= self.codes())

    def test_external_artifacts_remain_outside_git_and_hashes_match(self) -> None:
        record = self.record(); source = record["sources"][0]
        source["source_id"] = "Bad Source"
        source["locator"]["artifact_sha256"] = "b" * 64
        source["external_artifact"] = {"retained_outside_git": False, "filename": "capture.bin", "byte_size": 10, "sha256": SHA256}
        self.write_record(record)
        self.assertTrue({"RTEC-SOURCE-ID", "RTEC-PROPRIETARY-ARTIFACT", "RTEC-ARTIFACT-HASH-MISMATCH"} <= self.codes())

    def test_stale_and_future_evidence_dates_are_factual(self) -> None:
        record = self.record(); record["freshness"]["observed_or_verified_at"] = "2026-01-01"
        self.write_record(record); self.refresh()
        row = Corpus.load(self.root).generated_indexes(AS_OF)["stale_evidence"][0]
        self.assertEqual((row["evidence_id"], row["reason"]), ("RT-COMBAT-0001", "freshness-window-expired"))
        record["freshness"]["observed_or_verified_at"] = "2026-07-25"; self.write_record(record)
        self.assertIn("RTEC-FUTURE-EVIDENCE", self.codes())

    def test_generated_drift_unexpected_indexes_and_atomic_repair(self) -> None:
        self.write_record(self.record()); self.refresh()
        global_path = self.root / "docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json"
        value = json.loads(global_path.read_text()); value["active_owner_requests"] = ["RTREQ-E2E-COMBAT-9999"]; dump(global_path, value)
        self.assertIn("RTEC-GENERATED-INDEX-DRIFT", self.codes(False))
        module_path = self.root / "docs/agents/real-tibia/evidence/modules/combat/EVIDENCE_INDEX.yaml"
        write_generated(Corpus.load(self.root), check=False, as_of=AS_OF)
        value = json.loads(module_path.read_text()); value["record_count"] = 999; dump(module_path, value)
        with self.assertRaisesRegex(EvidenceError, "stale, missing or unexpected"):
            write_generated(Corpus.load(self.root), check=True, as_of=AS_OF)
        write_generated(Corpus.load(self.root), check=False, as_of=AS_OF)
        self.assertEqual(Corpus.load(self.root).validate(AS_OF).errors, ())
        dump(self.root / "docs/agents/real-tibia/evidence/modules/protocol/EVIDENCE_INDEX.yaml", {"format": "bad"})
        with self.assertRaisesRegex(EvidenceError, "stale, missing or unexpected"):
            write_generated(Corpus.load(self.root), check=True, as_of=AS_OF)

    def test_all_owner_routes_and_active_request_index(self) -> None:
        self.write_record(self.record())
        cases = [
            ("e2e","RTREQ-E2E-COMBAT-0001","CAN-PROGRAM-E2E-PLATFORM","physical-gameplay-proof"),
            ("otbm","RTREQ-OTBM-COMBAT-0001","CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS","static-map-evidence"),
            ("tcr","RTREQ-TCR-COMBAT-0001","CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE","client-reference-evidence"),
            ("protocol","RTREQ-PROTOCOL-COMBAT-0001","CAN-PROGRAM-PROTOCOL-TEST","protocol-proof"),
            ("feature","RTREQ-FEATURE-COMBAT-0001","CAN-PROGRAM-COMBAT-TEST","implementation-audit"),
        ]
        for folder, request_id, program, kind in cases:
            req = self.request(request_id); req.update(owner_kind=folder, requested_owner_program=program, request_type=kind)
            self.write_request(req, folder)
        self.assertEqual(self.codes(), set())
        ready = self.request("RTREQ-E2E-COMBAT-0002"); ready["status"] = "ready-for-owner-triage"
        ready["history"].append({"at":"2026-07-24T22:00:00+02:00","actor":"collector","actor_role":"collector","actor_task":"CAN-TEST","actor_pr":1,"from_status":"draft","to_status":"ready-for-owner-triage","reason":"Ready.","owner_evidence_ref":None})
        self.write_request(ready); self.refresh()
        self.assertEqual(Corpus.load(self.root).generated_indexes(AS_OF)["active_owner_requests"], ["RTREQ-E2E-COMBAT-0002"])

    def test_request_and_history_supersession_are_reciprocal_and_acyclic(self) -> None:
        self.write_record(self.record())
        old, new = self.request("RTREQ-E2E-COMBAT-0001"), self.request("RTREQ-E2E-COMBAT-0002")
        old["status"] = "superseded"; old["superseded_by"] = [new["request_id"]]
        old["history"].append({"at":"2026-07-24T22:00:00+02:00","actor":"collector","actor_role":"collector","actor_task":"CAN-TEST","actor_pr":1,"from_status":"draft","to_status":"superseded","reason":"Replaced.","owner_evidence_ref":None})
        new["supersedes"] = [old["request_id"]]
        self.write_request(old); self.write_request(new)
        self.assertNotIn("RTEC-REQUEST-SUPERSESSION-RECIPROCAL", self.codes())
        old["supersedes"] = [new["request_id"]]; new["superseded_by"] = [old["request_id"]]
        self.write_request(old); self.write_request(new)
        self.assertIn("RTEC-REQUEST-SUPERSESSION-CYCLE", self.codes())
        shutil.rmtree(self.root / "docs/agents/real-tibia/evidence/requests")
        h = history(); first = h["events"][0]; second = copy.deepcopy(first); second["history_id"] = "RTVH-COMBAT-0002"
        first["superseded_by"] = [second["history_id"]]; second["supersedes"] = [first["history_id"]]; h["events"].append(second)
        dump(self.root / "docs/agents/real-tibia/evidence/modules/combat/VERSION_HISTORY.yaml", h)
        self.assertNotIn("RTEC-HISTORY-SUPERSESSION-RECIPROCAL", self.codes())
        first["supersedes"] = [second["history_id"]]; second["superseded_by"] = [first["history_id"]]
        dump(self.root / "docs/agents/real-tibia/evidence/modules/combat/VERSION_HISTORY.yaml", h)
        self.assertIn("RTEC-HISTORY-CYCLE", self.codes())

    def test_published_schemas_are_strict_and_accept_templates(self) -> None:
        try:
            import jsonschema
        except ModuleNotFoundError:
            self.skipTest("jsonschema is not installed")
        schema_dir = self.repo / "docs/agents/real-tibia/evidence/schemas"
        expected = {"evidence-record.schema.json","owner-request.schema.json","module-evidence-index.schema.json","version-history.schema.json","generated-indexes.schema.json"}
        self.assertEqual({path.name for path in schema_dir.glob("*.json")}, expected)
        for path in schema_dir.glob("*.json"):
            schema = json.loads(path.read_text())
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertFalse(schema["additionalProperties"])
        for schema_name, template_name in (("evidence-record.schema.json","REAL_TIBIA_EVIDENCE_RECORD.yaml"),("owner-request.schema.json","REAL_TIBIA_EVIDENCE_REQUEST.yaml")):
            schema = json.loads((schema_dir / schema_name).read_text())
            value = json.loads((self.repo / "docs/agents/templates" / template_name).read_text())
            jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(value)

    def test_missing_published_schema_fails_closed(self) -> None:
        (self.root / "docs/agents/real-tibia/evidence/schemas/evidence-record.schema.json").unlink()
        with self.assertRaises(EvidenceError):
            Corpus.load(self.root)


if __name__ == "__main__":
    import unittest
    unittest.main()
