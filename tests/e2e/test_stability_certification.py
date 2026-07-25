from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "e2e" / "stability_certification.py"
SPEC = importlib.util.spec_from_file_location(
    "canary_e2e_stability_certification", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
stability = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stability
SPEC.loader.exec_module(stability)

AS_OF = datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


class StabilityCertificationTest(unittest.TestCase):
    def provenance(self, **overrides: str | None) -> dict[str, str | None]:
        value: dict[str, str | None] = {
            "server_revision": "a" * 40,
            "client_revision": "b" * 40,
            "datapack": "data-otservbr-global",
            "execution_tier": "scheduled",
        }
        value.update(overrides)
        return value

    def cleanup(
        self, *, certified: bool, contract_valid: bool = True
    ) -> dict[str, object]:
        return {
            "status": (
                "certified"
                if certified and contract_valid
                else "partial"
                if contract_valid
                else "unknown"
            ),
            "cleanup_certified": certified,
            "contract_valid": contract_valid,
        }

    def attempt(
        self,
        index: int,
        *,
        status: str = "success",
        cleanup_certified: bool = True,
        outcome: str | None = None,
        duration_ms: int | None = None,
        run_id: str | None = None,
        attempt_number: int = 1,
        source_path: str | None = None,
    ) -> dict[str, object]:
        run = run_id or f"run-{index:02d}"
        cleanup = self.cleanup(certified=cleanup_certified)
        if outcome is None:
            outcome = (
                "clean-pass"
                if status == "success" and cleanup_certified
                else "failed"
            )
        failure_classification = None
        failure_category = None
        first_divergence = None
        if outcome != "clean-pass":
            if status == "success":
                failure_classification = "cleanup"
                failure_category = "test-contract"
                first_divergence = "cleanup/cleanup-certification"
            else:
                failure_classification = (
                    status if status in {"cancelled", "timeout"} else "assertion"
                )
                failure_category = (
                    status if status in {"cancelled", "timeout"} else "test-contract"
                )
                first_divergence = "evidence-evaluation/check:required_markers"
        return {
            "identity": f"{run}#{attempt_number}",
            "run_id": run,
            "attempt": attempt_number,
            "status": status,
            "outcome": outcome,
            "clean_pass": outcome == "clean-pass",
            "started_at": f"2026-07-25T06:{index:02d}:00.000Z",
            "ended_at": f"2026-07-25T06:{index:02d}:01.000Z",
            "ended_at_epoch": 0.0 + index,
            "duration_ms": duration_ms if duration_ms is not None else index * 100,
            "failure_classification": failure_classification,
            "failure_category": failure_category,
            "first_divergence": first_divergence,
            "cleanup": cleanup,
            "source": {
                "root_id": "evidence-1",
                "path": source_path or f"run-{index:02d}/result.json",
                "attempt_history_index": 0,
            },
        }

    def envelope(
        self,
        attempts: list[dict[str, object]],
        *,
        scenario: str = "login/relog",
        provenance: dict[str, str | None] | None = None,
        missing: list[str] | None = None,
        source_path: str = "bundle/result.json",
    ) -> dict[str, object]:
        return {
            "scenario": scenario,
            "provenance": provenance or self.provenance(),
            "missing_provenance": missing or [],
            "attempts": attempts,
            "warnings": [],
            "unknowns": [],
            "source": {"root_id": "evidence-1", "path": source_path},
        }

    def build(
        self,
        envelopes: list[dict[str, object]],
        *,
        minimum_runs: int = 10,
        as_of: datetime = AS_OF,
        invalid: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        return stability.build_report(
            envelopes=envelopes,
            invalid_evidence=invalid or [],
            evidence_roots=[{"id": "evidence-1", "result_files": len(envelopes)}],
            as_of=as_of,
            minimum_runs=minimum_runs,
        )

    def test_all_clean_attempts_pass_only_after_explicit_minimum(self) -> None:
        attempts = [self.attempt(index) for index in range(1, 11)]
        cell = self.build([self.envelope(attempts)])["certifications"][0]
        self.assertEqual("pass", cell["state"])
        self.assertEqual("complete-clean-pass-set", cell["reason"])
        self.assertEqual(10, cell["clean_pass_count"])
        self.assertEqual(1.0, cell["success_ratio"])

    def test_nine_of_ten_is_unstable_and_preserves_failure(self) -> None:
        attempts = [self.attempt(index) for index in range(1, 10)]
        attempts.append(self.attempt(10, status="failure"))
        cell = self.build([self.envelope(attempts)])["certifications"][0]
        self.assertEqual("unstable", cell["state"])
        self.assertEqual("mixed-outcomes", cell["reason"])
        self.assertEqual(0.9, cell["success_ratio"])
        self.assertEqual({"assertion": 1}, cell["failure_class_distribution"])
        self.assertEqual(
            {"evidence-evaluation/check:required_markers": 1},
            cell["first_divergence_distribution"],
        )
        self.assertEqual("failed", cell["attempts"][-1]["outcome"])

    def test_all_failures_are_fail_after_minimum(self) -> None:
        attempts = [
            self.attempt(index, status="failure") for index in range(1, 4)
        ]
        cell = self.build(
            [self.envelope(attempts)], minimum_runs=3
        )["certifications"][0]
        self.assertEqual("fail", cell["state"])
        self.assertEqual("all-attempts-failed", cell["reason"])
        self.assertEqual(0.0, cell["success_ratio"])

    def test_insufficient_runs_are_not_evaluated(self) -> None:
        attempts = [self.attempt(index) for index in range(1, 4)]
        cell = self.build(
            [self.envelope(attempts)], minimum_runs=10
        )["certifications"][0]
        self.assertEqual("not-evaluated", cell["state"])
        self.assertEqual("insufficient-runs", cell["reason"])

    def test_missing_provenance_blocks_certification(self) -> None:
        attempts = [self.attempt(index) for index in range(1, 3)]
        envelope = self.envelope(
            attempts,
            provenance=self.provenance(client_revision="unknown"),
            missing=["client_revision"],
        )
        cell = self.build([envelope], minimum_runs=2)["certifications"][0]
        self.assertEqual("blocked", cell["state"])
        self.assertEqual("incomplete-provenance", cell["reason"])
        self.assertEqual(["client_revision"], cell["missing_provenance"])

    def test_cleanup_failure_prevents_clean_pass(self) -> None:
        attempts = [self.attempt(1), self.attempt(2, cleanup_certified=False)]
        cell = self.build(
            [self.envelope(attempts)], minimum_runs=2
        )["certifications"][0]
        self.assertEqual("unstable", cell["state"])
        self.assertEqual(1, cell["cleanup_failure_count"])
        self.assertEqual({"cleanup": 1}, cell["failure_class_distribution"])

    def test_duplicate_attempt_identity_fails_closed_and_remains_visible(self) -> None:
        first = self.attempt(1, run_id="duplicate", source_path="a/result.json")
        second = self.attempt(2, run_id="duplicate", source_path="b/result.json")
        second["attempt"] = 1
        second["identity"] = "duplicate#1"
        report = self.build(
            [
                self.envelope([first], source_path="a/result.json"),
                self.envelope([second], source_path="b/result.json"),
            ],
            minimum_runs=2,
        )
        cell = report["certifications"][0]
        self.assertEqual("blocked", cell["state"])
        self.assertEqual("duplicate-attempt-identity", cell["reason"])
        self.assertEqual(["duplicate#1"], cell["duplicate_attempt_identities"])
        self.assertEqual(1, report["summary"]["duplicate_attempt_identity_count"])
        self.assertEqual(2, len(report["duplicate_attempt_identities"][0]["occurrences"]))

    def test_historical_success_without_cleanup_is_blocked(self) -> None:
        blocked = self.attempt(1, outcome="blocked")
        blocked["cleanup"] = self.cleanup(
            certified=False, contract_valid=False
        )
        blocked["failure_classification"] = "cleanup-unknown"
        blocked["failure_category"] = "unknown"
        blocked["first_divergence"] = "cleanup/unknown-historical-attempt"
        clean = self.attempt(2)
        cell = self.build(
            [self.envelope([blocked, clean])], minimum_runs=2
        )["certifications"][0]
        self.assertEqual("blocked", cell["state"])
        self.assertEqual("incomplete-attempt-evidence", cell["reason"])
        self.assertEqual(1, cell["blocked_attempt_count"])
        self.assertEqual(1, cell["cleanup_unknown_count"])

    def test_duration_distribution_uses_deterministic_nearest_rank(self) -> None:
        values = [100, 200, 300, 400, 1000]
        attempts = [
            self.attempt(index, duration_ms=value)
            for index, value in enumerate(values, start=1)
        ]
        cell = self.build(
            [self.envelope(attempts)], minimum_runs=5
        )["certifications"][0]
        self.assertEqual(
            {
                "count": 5,
                "min_ms": 100,
                "p50_ms": 300,
                "p95_ms": 1000,
                "max_ms": 1000,
            },
            cell["duration_ms"],
        )

    def test_future_attempt_is_rejected_against_explicit_as_of(self) -> None:
        attempt = self.attempt(1)
        attempt["started_at"] = "2026-07-25T09:00:00.000Z"
        attempt["ended_at"] = "2026-07-25T09:00:01.000Z"
        with self.assertRaisesRegex(
            stability.StabilityCertificationError, "ends after as_of"
        ):
            self.build([self.envelope([attempt])])

    def test_serialization_and_markdown_are_deterministic(self) -> None:
        attempts = [self.attempt(1), self.attempt(2, status="failure")]
        report = self.build([self.envelope(attempts)], minimum_runs=2)
        self.assertEqual(
            stability.serialize_report(report),
            stability.serialize_report(report),
        )
        markdown = stability.render_markdown(report)
        self.assertEqual(markdown, stability.render_markdown(report))
        self.assertIn("Mixed evidence is `unstable`", markdown)
        self.assertIn("No opaque stability score is calculated", markdown)
        self.assertNotIn(str(ROOT), markdown)

    def test_validation_rejects_tampered_success_ratio(self) -> None:
        report = self.build(
            [self.envelope([self.attempt(1), self.attempt(2)])],
            minimum_runs=2,
        )
        report["certifications"][0]["success_ratio"] = 0.5
        with self.assertRaisesRegex(
            stability.StabilityCertificationError, "success_ratio is inconsistent"
        ):
            stability.validate_report(report)

    def test_normalize_envelope_reuses_coverage_normalization(self) -> None:
        calls: list[tuple[str, str]] = []

        def normalize_result(
            payload: dict[str, object], *, root_id: str, relative_path: str
        ) -> dict[str, object]:
            calls.append((root_id, relative_path))
            return {
                "scenario": "login/relog",
                "run_id": "current",
                "status": "success",
                "started_at": "2026-07-25T06:00:00.000Z",
                "ended_at": "2026-07-25T06:00:01.000Z",
                "duration_ms": 1000,
                "execution_tier": "scheduled",
                "server_revision": "a" * 40,
                "client_revision": "b" * 40,
                "datapack": "data-otservbr-global",
                "cleanup": self.cleanup(certified=True),
                "warnings": [],
                "unknowns": [],
                "source": {"root_id": root_id, "path": relative_path},
            }

        previous = stability._COVERAGE_DASHBOARD
        stability._COVERAGE_DASHBOARD = SimpleNamespace(
            normalize_result=normalize_result
        )
        try:
            envelope = stability.normalize_envelope(
                {
                    "attempt_history": [
                        {
                            "run_id": "current",
                            "attempt": 1,
                            "status": "success",
                        }
                    ],
                    "failure": None,
                    "first_failed_step": None,
                },
                root_id="evidence-1",
                relative_path="current/result.json",
            )
        finally:
            stability._COVERAGE_DASHBOARD = previous
        self.assertEqual(
            [("evidence-1", "current/result.json")], calls
        )
        self.assertEqual("clean-pass", envelope["attempts"][0]["outcome"])

    def test_canonical_normalization_preserves_prior_failure_and_current_success(
        self,
    ) -> None:
        payload = self.canonical_envelope(
            run_id="current",
            attempt_history=[
                {
                    "run_id": "previous",
                    "attempt": 1,
                    "status": "failure",
                    "started_at": "2026-07-25T05:00:00.000Z",
                    "ended_at": "2026-07-25T05:00:01.000Z",
                    "duration_ms": 1000,
                    "first_failed_step": {
                        "id": "check:required_markers",
                        "phase": "evidence-evaluation",
                    },
                    "failure_classification": "assertion",
                },
                {
                    "run_id": "current",
                    "attempt": 2,
                    "status": "success",
                },
            ],
        )
        previous = stability._COVERAGE_DASHBOARD
        stability._COVERAGE_DASHBOARD = None
        try:
            normalized = stability.normalize_envelope(
                payload,
                root_id="evidence-1",
                relative_path="run/result.json",
            )
        finally:
            stability._COVERAGE_DASHBOARD = previous
        report = self.build([normalized], minimum_runs=2)
        cell = report["certifications"][0]
        self.assertEqual("unstable", cell["state"])
        self.assertEqual(2, cell["run_count"])
        self.assertEqual("failed", cell["attempts"][0]["outcome"])
        self.assertEqual("clean-pass", cell["attempts"][1]["outcome"])

    def canonical_cleanup_summary(self, certified: bool = True) -> dict[str, object]:
        return {
            "schema_version": 1,
            "contract": "canary-universal-e2e-cleanup-certification-v1",
            "status": "certified" if certified else "partial",
            "cleanup_certified": certified,
            "process_group_cleanup": {
                "members_before": [],
                "members_after": [],
            },
            "checks": [
                {
                    "id": "runner-owned-workspace-restored",
                    "status": "pass" if certified else "fail",
                    "required": True,
                }
            ],
        }

    def canonical_envelope(
        self,
        *,
        run_id: str,
        attempt_history: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        dimensions = {
            name: "not-evaluated"
            for name in (
                "determinism",
                "stability",
                "resilience",
                "exactly_once",
                "concurrency",
                "cleanup",
                "performance",
                "compatibility",
                "diagnostics",
            )
        }
        dimensions["cleanup"] = "pass"
        dimensions["diagnostics"] = "pass"
        return {
            "schema_version": 3,
            "contract": "canary-universal-e2e-result-envelope-v1",
            "run_id": run_id,
            "scenario_id": "relog",
            "suite": "login",
            "scenario": "login/relog",
            "status": "success",
            "evidence_maturity": "M3",
            "quality_dimensions": dimensions,
            "server": {
                "revision": "a" * 40,
                "datapack": "data-otservbr-global",
            },
            "client": {"revision": "b" * 40},
            "started_at": "2026-07-25T06:00:00.000Z",
            "ended_at": "2026-07-25T06:00:01.000Z",
            "duration_ms": 1000,
            "execution_tier": "scheduled",
            "actors": [],
            "phases": [],
            "steps": [],
            "failure": None,
            "first_failed_step": None,
            "attempt_history": attempt_history
            or [{"run_id": run_id, "attempt": 1, "status": "success"}],
            "cleanup_summary": self.canonical_cleanup_summary(),
            "warnings": [],
            "unknowns": [],
        }


if __name__ == "__main__":
    unittest.main()
