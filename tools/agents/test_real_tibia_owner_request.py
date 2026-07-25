from __future__ import annotations

import hashlib
import json
from unittest import mock

import real_tibia_owner_request as owner
from real_tibia_evidence_test_support import *


RESULT_REF = f"repo-file:blakinio/canary@{COMMIT}:reports/owner-result.json"
OWNER_REF = "github-pr:blakinio/canary#123"
ROUTES = {
    "e2e": ("RTREQ-E2E-COMBAT-0001", "CAN-PROGRAM-E2E-PLATFORM", "physical-gameplay-proof", "physical-e2e-result", "physical-client-proven"),
    "otbm": ("RTREQ-OTBM-COMBAT-0001", "CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS", "static-map-evidence", "otbm-owner-result", "behavior-proven"),
    "tcr": ("RTREQ-TCR-COMBAT-0001", "CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE", "client-reference-evidence", "tcr-owner-result", "protocol-proven"),
    "protocol": ("RTREQ-PROTOCOL-COMBAT-0001", "CAN-PROGRAM-PROTOCOL-TEST", "protocol-proof", "packet-capture", "protocol-proven"),
    "feature": ("RTREQ-FEATURE-COMBAT-0001", "CAN-PROGRAM-COMBAT-TEST", "runtime-behavior-proof", "feature-owner-result", "behavior-proven"),
}


class RealTibiaOwnerRequestLifecycleTests(EvidenceTestCase):
    def route_request(self, route: str) -> dict[str, object]:
        request_id, program, request_type, _, proof_level = ROUTES[route]
        request = self.request(request_id)
        request.update(owner_kind=route, requested_owner_program=program, request_type=request_type)
        request["required_evidence"]["minimum_proof_level"] = proof_level
        request["required_evidence"]["minimum_e2e_maturity"] = "M5" if route == "e2e" else None
        return request

    def advance_to_active(self, request: dict[str, object]) -> dict[str, object]:
        request = owner.transition_value(
            request,
            expected_status="draft",
            to_status="ready-for-owner-triage",
            at="2026-07-25T10:00:00+02:00",
            actor="collector",
            actor_role="collector",
            actor_task="CAN-COLLECTOR",
            actor_pr=10,
            reason="Ready for bounded owner triage.",
        )
        request = owner.transition_value(
            request,
            expected_status="ready-for-owner-triage",
            to_status="accepted-by-owner",
            at="2026-07-25T10:10:00+02:00",
            actor="owner",
            actor_role="owner",
            actor_task="CAN-OWNER",
            actor_pr=11,
            owner_evidence_ref=OWNER_REF,
            reason="Owner accepted the exact bounded request.",
        )
        request = owner.transition_value(
            request,
            expected_status="accepted-by-owner",
            to_status="planned",
            at="2026-07-25T10:20:00+02:00",
            actor="owner-planner",
            actor_role="owner",
            actor_task="CAN-OWNER",
            actor_pr=11,
            reason="Owner scheduled the bounded work.",
        )
        return owner.transition_value(
            request,
            expected_status="planned",
            to_status="active",
            at="2026-07-25T10:30:00+02:00",
            actor="owner",
            actor_role="owner",
            actor_task="CAN-OWNER",
            actor_pr=11,
            owner_evidence_ref=OWNER_REF,
            reason="Owner began the bounded work.",
        )

    def result_available(self, request: dict[str, object], route: str) -> dict[str, object]:
        proof_level = ROUTES[route][4]
        return owner.record_result_value(
            self.advance_to_active(request),
            expected_status="active",
            at="2026-07-25T11:00:00+02:00",
            actor="owner",
            actor_task="CAN-OWNER",
            actor_pr=11,
            reason="Stable owner result is retained.",
            owner_evidence_ref=OWNER_REF,
            owner_task="CAN-OWNER",
            owner_pr=11,
            result_refs=[RESULT_REF],
            proof_level=proof_level,
            proves=["The bounded owner observation completed."],
            does_not_prove=["No broader module or whole-game parity is proven."],
            blockers=[],
        )

    def owner_record(self, route: str, request_id: str) -> dict[str, object]:
        _, _, _, source_type, proof_level = ROUTES[route]
        record = self.record("RT-COMBAT-0002")
        record.update(
            record_status="accepted",
            evidence_state="PROVEN",
            proof_level=proof_level,
            confidence="HIGH",
            uncertainty=[],
            owner_request_refs=[request_id],
        )
        source = record["sources"][0]
        source.update(
            source_id=f"{route}-owner-result",
            source_type=source_type,
            proof_level_reached=proof_level,
            observation_date="2026-07-25",
            proves=["The retained owner result proves the bounded observation."],
            does_not_prove=["The result does not prove unrelated behavior."],
            limitations=[],
            external_artifact=None,
        )
        source["locator"] = {
            "url": None,
            "repository": "blakinio/canary",
            "repository_path": "reports/owner-result.json",
            "commit_sha": COMMIT,
            "build": None,
            "report_id": None,
            "artifact_sha256": None,
        }
        source["selected"] = {
            "sections": [],
            "symbols": [],
            "files": ["reports/owner-result.json"],
            "observations": ["Bounded owner result."],
        }
        return record

    def consume(self, request: dict[str, object], record: dict[str, object]) -> dict[str, object]:
        self.write_record(record)
        return owner.consume_result_value(
            request,
            expected_status="result-available",
            at="2026-07-25T11:10:00+02:00",
            actor="collector",
            actor_role="collector",
            actor_task="CAN-COLLECTOR",
            actor_pr=10,
            reason="Collector consumed the exact stable owner result.",
            evidence_ids=[record["evidence_id"]],
            evidence_documents=Corpus.load(self.root).evidence_documents,
        )

    def test_stable_result_reference_contract(self) -> None:
        valid = [
            OWNER_REF,
            f"github-commit:blakinio/canary@{COMMIT}",
            "github-actions-run:blakinio/canary#123",
            "github-actions-job:blakinio/canary#456",
            f"github-actions-artifact:blakinio/canary#789@sha256:{SHA256}",
            RESULT_REF,
            f"external-report:sha256:{SHA256}",
        ]
        self.assertEqual([owner.parse_stable_result_ref(value).raw for value in valid], valid)
        for invalid in (
            "https://github.com/blakinio/canary/actions/runs/latest",
            "github-pr:blakinio/canary#0",
            "github-commit:blakinio/canary@main",
            f"repo-file:blakinio/canary@{COMMIT}:../secret",
            "external-report:sha256:bad",
        ):
            with self.subTest(invalid=invalid), self.assertRaises(owner.RequestLifecycleError):
                owner.parse_stable_result_ref(invalid)

    def test_expected_status_and_document_digest_reject_stale_writer(self) -> None:
        request = self.route_request("e2e")
        self.write_record(self.record())
        self.write_request(request)
        self.refresh()
        document = next(item for item in Corpus.load(self.root).request_documents if item.value["request_id"] == request["request_id"])
        with self.assertRaisesRegex(owner.RequestLifecycleError, "stale request state"):
            owner.apply_candidate(
                root=self.root,
                request_id=request["request_id"],
                expected_status="planned",
                expected_document_sha256=None,
                as_of=AS_OF,
                write=False,
                mutation=lambda value, corpus: value,
            )
        with self.assertRaisesRegex(owner.RequestLifecycleError, "stale request document"):
            owner.apply_candidate(
                root=self.root,
                request_id=request["request_id"],
                expected_status="draft",
                expected_document_sha256="f" * 64,
                as_of=AS_OF,
                write=False,
                mutation=lambda value, corpus: value,
            )
        self.assertEqual(len(document.sha256), 64)

    def test_owner_states_dedicated_result_commands_and_actor_pr_fail_closed(self) -> None:
        request = self.route_request("feature")
        ready = owner.transition_value(
            request,
            expected_status="draft",
            to_status="ready-for-owner-triage",
            at="2026-07-25T10:00:00+02:00",
            actor="collector",
            actor_role="collector",
            actor_task="CAN-COLLECTOR",
            actor_pr=10,
            reason="Ready.",
        )
        with self.assertRaisesRegex(owner.RequestLifecycleError, "requires owner actor"):
            owner.transition_value(
                ready,
                expected_status="ready-for-owner-triage",
                to_status="accepted-by-owner",
                at="2026-07-25T10:10:00+02:00",
                actor="collector",
                actor_role="collector",
                actor_task="CAN-COLLECTOR",
                actor_pr=10,
                owner_evidence_ref=OWNER_REF,
                reason="Invalid self acceptance.",
            )
        active = self.advance_to_active(request)
        with self.assertRaisesRegex(owner.RequestLifecycleError, "dedicated command"):
            owner.transition_value(
                active,
                expected_status="active",
                to_status="result-available",
                at="2026-07-25T11:00:00+02:00",
                actor="owner",
                actor_role="owner",
                actor_task="CAN-OWNER",
                actor_pr=11,
                owner_evidence_ref=OWNER_REF,
                reason="Wrong command.",
            )
        with self.assertRaisesRegex(owner.RequestLifecycleError, "positive actor PR"):
            owner.record_result_value(
                active,
                expected_status="active",
                at="2026-07-25T11:00:00+02:00",
                actor="owner",
                actor_task="CAN-OWNER",
                actor_pr=None,
                reason="Missing PR.",
                owner_evidence_ref=OWNER_REF,
                owner_task="CAN-OWNER",
                owner_pr=None,
                result_refs=[RESULT_REF],
                proof_level="behavior-proven",
                proves=["Bounded result."],
                does_not_prove=["No broader claim."],
                blockers=[],
            )

    def test_all_owner_routes_reach_consumed_with_matching_evidence(self) -> None:
        for route in ROUTES:
            with self.subTest(route=route):
                request = self.result_available(self.route_request(route), route)
                consumed = self.consume(request, self.owner_record(route, request["request_id"]))
                self.assertEqual(consumed["status"], "consumed")
                self.assertEqual(consumed["result"]["consumed_by_evidence_records"], ["RT-COMBAT-0002"])
                (self.root / "docs/agents/real-tibia/evidence/modules/combat/records/RT-COMBAT-0002.yaml").unlink()

    def test_consumption_rejects_missing_link_route_ref_and_proof_promotion(self) -> None:
        request = self.result_available(self.route_request("feature"), "feature")
        record = self.owner_record("feature", request["request_id"])
        record["owner_request_refs"] = []
        with self.assertRaisesRegex(owner.RequestLifecycleError, "must link owner request"):
            self.consume(request, record)
        record = self.owner_record("feature", request["request_id"])
        record["sources"][0]["source_type"] = "tcr-owner-result"
        with self.assertRaisesRegex(owner.RequestLifecycleError, "lacks a feature owner-result source"):
            self.consume(request, record)
        record = self.owner_record("feature", request["request_id"])
        record["sources"][0]["locator"]["repository_path"] = "reports/other.json"
        record["sources"][0]["selected"]["files"] = ["reports/other.json"]
        with self.assertRaisesRegex(owner.RequestLifecycleError, "matching a stable result reference"):
            self.consume(request, record)
        record = self.owner_record("feature", request["request_id"])
        record["proof_level"] = "physical-client-proven"
        with self.assertRaisesRegex(owner.RequestLifecycleError, "exceeds owner result proof"):
            self.consume(request, record)

    def test_dry_run_write_and_rollback_are_transactional(self) -> None:
        request = self.route_request("feature")
        self.write_record(self.record())
        self.write_request(request, "feature")
        self.refresh()
        request_path = self.root / f"docs/agents/real-tibia/evidence/requests/feature/{request['request_id']}.yaml"
        before = request_path.read_bytes()

        def ready(value: dict[str, object], corpus: Corpus) -> dict[str, object]:
            return owner.transition_value(
                value,
                expected_status="draft",
                to_status="ready-for-owner-triage",
                at="2026-07-25T10:00:00+02:00",
                actor="collector",
                actor_role="collector",
                actor_task="CAN-COLLECTOR",
                actor_pr=10,
                reason="Ready.",
            )

        candidate = owner.apply_candidate(
            root=self.root,
            request_id=request["request_id"],
            expected_status="draft",
            expected_document_sha256=hashlib.sha256(before).hexdigest(),
            as_of=AS_OF,
            write=False,
            mutation=ready,
        )
        self.assertEqual(candidate["status"], "ready-for-owner-triage")
        self.assertEqual(request_path.read_bytes(), before)
        owner.apply_candidate(
            root=self.root,
            request_id=request["request_id"],
            expected_status="draft",
            expected_document_sha256=hashlib.sha256(before).hexdigest(),
            as_of=AS_OF,
            write=True,
            mutation=ready,
        )
        self.assertEqual(json.loads(request_path.read_text())["status"], "ready-for-owner-triage")
        self.assertEqual(Corpus.load(self.root).validate(AS_OF).errors, ())

        rollback_before = request_path.read_bytes()

        def reject(value: dict[str, object], corpus: Corpus) -> dict[str, object]:
            return owner.transition_value(
                value,
                expected_status="ready-for-owner-triage",
                to_status="rejected",
                at="2026-07-25T10:30:00+02:00",
                actor="owner",
                actor_role="owner",
                actor_task="CAN-OWNER",
                actor_pr=11,
                reason="Owner rejected the request.",
            )

        with mock.patch.object(owner, "write_generated", side_effect=owner.EvidenceError("forced failure")):
            with self.assertRaisesRegex(owner.EvidenceError, "forced failure"):
                owner.apply_candidate(
                    root=self.root,
                    request_id=request["request_id"],
                    expected_status="ready-for-owner-triage",
                    expected_document_sha256=hashlib.sha256(rollback_before).hexdigest(),
                    as_of=AS_OF,
                    write=True,
                    mutation=reject,
                )
        self.assertEqual(request_path.read_bytes(), rollback_before)
        self.assertEqual(Corpus.load(self.root).validate(AS_OF).errors, ())

    def test_repository_vocations_request_remains_unclaimed(self) -> None:
        path = self.repo / "docs/agents/real-tibia/evidence/requests/feature/RTREQ-FEATURE-VOCATIONS-0001.yaml"
        value = json.loads(path.read_text())
        self.assertEqual(value["status"], "ready-for-owner-triage")
        self.assertIsNone(value["coordination"]["owner_task"])
        self.assertIsNone(value["coordination"]["owner_pr"])
        self.assertFalse(value["result"]["available"])
        self.assertEqual(value["result"]["result_refs"], [])


if __name__ == "__main__":
    import unittest

    unittest.main()
