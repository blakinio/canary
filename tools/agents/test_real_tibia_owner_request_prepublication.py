from __future__ import annotations

import datetime as dt

import real_tibia_owner_request as owner
from real_tibia_evidence import publication_view
from real_tibia_evidence_test_support import AS_OF, Corpus, EvidenceTestCase, write_generated


class RealTibiaOwnerRequestPrepublicationTests(EvidenceTestCase):
    def feature_request(self) -> dict[str, object]:
        request = self.request("RTREQ-FEATURE-COMBAT-0001")
        request.update(
            owner_kind="feature",
            requested_owner_program="CAN-PROGRAM-COMBAT-TEST",
            request_type="runtime-behavior-proof",
        )
        request["required_evidence"]["minimum_proof_level"] = "behavior-proven"
        return request

    def refresh_publication(self) -> None:
        write_generated(
            publication_view(Corpus.load(self.root)),
            check=False,
            as_of=AS_OF,
        )

    def test_review_needed_future_record_does_not_block_request_dry_run(self) -> None:
        future_date = AS_OF + dt.timedelta(days=1)
        self.write_record(self.record())
        request = self.feature_request()
        self.write_request(request, "feature")

        candidate = self.record("RT-COMBAT-0002")
        candidate["record_status"] = "review-needed"
        candidate["freshness"]["observed_or_verified_at"] = future_date.isoformat()
        candidate["review"].update(
            task_id="CAN-RTEC-PREPUBLICATION-TEST",
            pr=968,
            status="pending",
            reviewer=None,
            reviewed_at=None,
        )
        self.write_record(candidate)
        self.refresh_publication()

        self.assertEqual(owner._blocking_diagnostics(Corpus.load(self.root), AS_OF), [])

        def ready(value: dict[str, object], corpus: Corpus) -> dict[str, object]:
            del corpus
            return owner.transition_value(
                value,
                expected_status="draft",
                to_status="ready-for-owner-triage",
                at=f"{AS_OF.isoformat()}T10:00:00+02:00",
                actor="collector",
                actor_role="collector",
                actor_task="CAN-RTEC-PREPUBLICATION-TEST",
                actor_pr=968,
                reason="Exercise a request dry-run with an unpublished candidate present.",
            )

        result = owner.apply_candidate(
            root=self.root,
            request_id=request["request_id"],
            expected_status="draft",
            expected_document_sha256=None,
            as_of=AS_OF,
            write=False,
            mutation=ready,
        )
        self.assertEqual(result["status"], "ready-for-owner-triage")

    def test_accepted_future_record_still_blocks_request_validation(self) -> None:
        future_date = AS_OF + dt.timedelta(days=1)
        self.write_record(self.record())
        self.write_request(self.feature_request(), "feature")

        accepted = self.record("RT-COMBAT-0002")
        accepted["record_status"] = "accepted"
        accepted["freshness"]["observed_or_verified_at"] = future_date.isoformat()
        accepted["review"].update(
            task_id="CAN-RTEC-PREPUBLICATION-TEST",
            pr=968,
            status="accepted",
            reviewer="test-reviewer",
            reviewed_at=f"{future_date.isoformat()}T12:00:00+02:00",
        )
        self.write_record(accepted)
        self.refresh_publication()

        blocking = owner._blocking_diagnostics(Corpus.load(self.root), AS_OF)
        self.assertTrue(
            any("RTEC-FUTURE-EVIDENCE" in diagnostic for diagnostic in blocking),
            blocking,
        )
