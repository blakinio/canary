from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "e2e" / "coverage_dashboard.py"
SPEC = importlib.util.spec_from_file_location("canary_e2e_coverage_dashboard", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
coverage_dashboard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = coverage_dashboard
SPEC.loader.exec_module(coverage_dashboard)
AS_OF = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)


class CoverageDashboardTest(unittest.TestCase):
    def dimensions(self, **overrides: str) -> dict[str, str]:
        values = {name: "not-evaluated" for name in coverage_dashboard.QUALITY_DIMENSIONS}
        values.update(overrides)
        return values

    def cleanup_summary(self, certified: bool) -> dict[str, object]:
        return {
            "schema_version": coverage_dashboard.CLEANUP_SCHEMA_VERSION,
            "contract": coverage_dashboard.CLEANUP_CONTRACT,
            "status": "certified" if certified else "partial",
            "cleanup_certified": certified,
            "process_group_cleanup": {"members_before": [], "members_after": []},
            "checks": [{
                "id": "runner-owned-workspace-restored",
                "status": "pass" if certified else "fail",
                "required": True,
            }],
        }

    def envelope(
        self,
        *,
        run_id: str,
        scenario: str = "login/relog",
        status: str = "success",
        maturity: str = "M3",
        started_at: str = "2026-07-24T09:59:55.000Z",
        ended_at: str = "2026-07-24T10:00:00.000Z",
        dimensions: dict[str, str] | None = None,
        cleanup_certified: bool | None = True,
        warnings: list[str] | None = None,
        unknowns: list[str] | None = None,
    ) -> dict[str, object]:
        suite, scenario_id = scenario.split("/", 1)
        quality = dimensions or self.dimensions(diagnostics="pass")
        if cleanup_certified is not None:
            quality["cleanup"] = "pass" if cleanup_certified else "fail"
            cleanup_summary: dict[str, object] = self.cleanup_summary(cleanup_certified)
        else:
            cleanup_summary = {
                "contract": None,
                "status": "not-certified",
                "cleanup_certified": False,
            }
        failure = None if status == "success" else {
            "classification": "assertion",
            "category": "test-contract",
            "phase": "evidence-evaluation",
        }
        return {
            "schema_version": coverage_dashboard.RESULT_SCHEMA_VERSION,
            "contract": coverage_dashboard.RESULT_CONTRACT,
            "run_id": run_id,
            "scenario_id": scenario_id,
            "suite": suite,
            "scenario": scenario,
            "status": status,
            "evidence_maturity": maturity,
            "quality_dimensions": quality,
            "server": {"revision": "a" * 40, "datapack": "data-otservbr-global"},
            "client": {"revision": "b" * 40},
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_ms": 5000,
            "execution_tier": "pr-required",
            "actors": [],
            "phases": [],
            "steps": [],
            "failure": failure,
            "attempt_history": [{"run_id": run_id, "attempt": 1, "status": status}],
            "cleanup_summary": cleanup_summary,
            "warnings": warnings or [],
            "unknowns": unknowns or [],
        }

    def normalize(self, payload: dict[str, object], path: str = "run/result.json") -> dict[str, object]:
        return coverage_dashboard.normalize_result(payload, root_id="evidence-1", relative_path=path)

    def build(
        self,
        *,
        registered: list[dict[str, str]],
        evidence: list[dict[str, object]],
        invalid: list[dict[str, object]] | None = None,
        stale_after_days: int | None = None,
        as_of: datetime = AS_OF,
    ) -> dict[str, object]:
        return coverage_dashboard.build_report(
            registered_scenarios=registered,
            evidence=evidence,
            invalid_evidence=invalid or [],
            evidence_roots=[{"id": "evidence-1", "result_files": len(evidence)}],
            as_of=as_of,
            stale_after_days=stale_after_days,
        )

    def registered(self, scenario: str = "login/relog") -> list[dict[str, str]]:
        return [{"scenario": scenario, "source": f"tests/e2e/scenarios/{scenario}.json"}]

    def test_failed_declared_m5_does_not_promote_successful_m3(self) -> None:
        success = self.normalize(self.envelope(
            run_id="success-m3", maturity="M3",
            dimensions=self.dimensions(diagnostics="pass", resilience="pass", cleanup="pass"),
        ), "success/result.json")
        failure = self.normalize(self.envelope(
            run_id="failed-m5", status="failure", maturity="M5",
            ended_at="2026-07-24T11:00:00.000Z",
            dimensions=self.dimensions(diagnostics="pass", resilience="fail", cleanup="pass"),
        ), "failure/result.json")
        row = self.build(registered=self.registered(), evidence=[success, failure], stale_after_days=1)["scenarios"][0]
        self.assertEqual("M3", row["strongest_proven_maturity"]["level"])
        self.assertEqual("success-m3", row["last_success"]["run_id"])
        self.assertEqual("failed-m5", row["last_failure"]["run_id"])
        self.assertEqual("failed-m5", row["latest_run"]["run_id"])
        self.assertEqual("fail", row["quality_dimensions"]["resilience"]["state"])
        self.assertEqual("pass", row["quality_dimensions"]["cleanup"]["state"])

    def test_registration_without_evidence_stays_missing_and_not_proven(self) -> None:
        row = self.build(registered=self.registered("combat/physical-combat"), evidence=[])["scenarios"][0]
        codes = {item["code"] for item in row["coverage_gaps"]}
        self.assertTrue(row["registered"])
        self.assertEqual("missing", row["freshness"]["status"])
        self.assertEqual("not-proven", row["strongest_proven_maturity"]["level"])
        self.assertTrue({"missing-result-evidence", "maturity-not-proven"} <= codes)
        self.assertEqual("not-evaluated", row["quality_dimensions"]["diagnostics"]["state"])

    def test_evidence_for_removed_scenario_is_retained_as_unregistered(self) -> None:
        evidence = self.normalize(self.envelope(run_id="old-run", scenario="legacy/removed"))
        row = self.build(registered=[], evidence=[evidence])["scenarios"][0]
        self.assertFalse(row["registered"])
        self.assertIn("unregistered-scenario-evidence", {item["code"] for item in row["coverage_gaps"]})

    def test_freshness_requires_an_explicit_threshold(self) -> None:
        evidence = self.normalize(self.envelope(
            run_id="old-run",
            started_at="2026-07-01T09:59:55.000Z",
            ended_at="2026-07-01T10:00:00.000Z",
        ))
        without = self.build(registered=self.registered(), evidence=[evidence])
        with_policy = self.build(registered=self.registered(), evidence=[evidence], stale_after_days=7)
        self.assertEqual("not-evaluated", without["scenarios"][0]["freshness"]["status"])
        self.assertEqual("stale", with_policy["scenarios"][0]["freshness"]["status"])

    def test_future_evidence_is_rejected_against_explicit_as_of(self) -> None:
        evidence = self.normalize(self.envelope(
            run_id="future-run",
            started_at="2026-07-24T12:59:55.000Z",
            ended_at="2026-07-24T13:00:00.000Z",
        ))
        with self.assertRaisesRegex(coverage_dashboard.CoverageDashboardError, "ends after as_of"):
            self.build(registered=[], evidence=[evidence])

    def test_naive_as_of_is_rejected(self) -> None:
        with self.assertRaisesRegex(coverage_dashboard.CoverageDashboardError, "timezone-aware"):
            self.build(registered=[], evidence=[], as_of=datetime(2026, 7, 24, 12, 0))

    def test_cleanup_contract_must_match_cleanup_dimension(self) -> None:
        payload = self.envelope(run_id="bad-cleanup", cleanup_certified=True)
        payload["quality_dimensions"]["cleanup"] = "fail"
        with self.assertRaisesRegex(coverage_dashboard.CoverageDashboardError, "disagrees"):
            self.normalize(payload)

    def test_exact_cleanup_header_without_schema_body_is_rejected(self) -> None:
        payload = self.envelope(run_id="truncated-cleanup")
        payload["cleanup_summary"] = {
            "schema_version": coverage_dashboard.CLEANUP_SCHEMA_VERSION,
            "contract": coverage_dashboard.CLEANUP_CONTRACT,
            "status": "certified",
            "cleanup_certified": True,
        }
        with self.assertRaisesRegex(coverage_dashboard.CoverageDashboardError, "invalid cleanup certification"):
            self.normalize(payload)

    def test_discovery_preserves_invalid_results_without_counting_them(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            good, bad = root / "good/result.json", root / "bad/result.json"
            good.parent.mkdir(parents=True)
            bad.parent.mkdir(parents=True)
            good.write_text(json.dumps(self.envelope(run_id="good-run")) + "\n", encoding="utf-8")
            bad.write_text('{"schema_version": 999}\n', encoding="utf-8")
            valid, invalid, roots = coverage_dashboard.discover_result_evidence([root])
        self.assertEqual("good-run", valid[0]["run_id"])
        self.assertEqual("bad/result.json", invalid[0]["source"]["path"])
        self.assertEqual([{"id": "evidence-1", "result_files": 2}], roots)

    @unittest.skipIf(os.name == "nt", "symlink behavior is platform-specific")
    def test_discovery_rejects_result_symlink_outside_evidence_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root, outside = base / "evidence", base / "outside"
            root.mkdir()
            outside.mkdir()
            target = outside / "result.json"
            target.write_text(json.dumps(self.envelope(run_id="outside-run")) + "\n", encoding="utf-8")
            link = root / "linked/result.json"
            link.parent.mkdir()
            link.symlink_to(target)
            valid, invalid, _ = coverage_dashboard.discover_result_evidence([root])
        self.assertEqual([], valid)
        self.assertEqual("linked/result.json", invalid[0]["source"]["path"])
        self.assertEqual("result.json resolves outside the evidence root", invalid[0]["error"])
        self.assertNotIn(directory, json.dumps(invalid))

    def test_absolute_or_parent_source_paths_are_rejected(self) -> None:
        payload = self.envelope(run_id="unsafe-source")
        for path in ("/tmp/result.json", "../result.json", "a/../result.json"):
            with self.subTest(path=path), self.assertRaisesRegex(
                coverage_dashboard.CoverageDashboardError, "safe POSIX relative path"
            ):
                self.normalize(payload, path)

    def test_scenario_discovery_reuses_existing_runner_and_emits_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / "tests/e2e/scenarios/login/relog.json"
            path.parent.mkdir(parents=True)
            path.write_text("{}\n", encoding="utf-8")
            previous = coverage_dashboard._SCENARIO_RUNNER
            coverage_dashboard._SCENARIO_RUNNER = SimpleNamespace(
                discover=lambda _: [SimpleNamespace(key="login/relog", path=path)]
            )
            try:
                registered = coverage_dashboard.discover_registered_scenarios(root)
            finally:
                coverage_dashboard._SCENARIO_RUNNER = previous
        self.assertEqual(self.registered(), registered)

    def test_serialization_and_markdown_are_deterministic_and_path_safe(self) -> None:
        evidence = self.normalize(self.envelope(
            run_id="stable-run", warnings=["warning retained"], unknowns=["unknown retained"]
        ))
        report = self.build(registered=self.registered(), evidence=[evidence])
        first_json, second_json = coverage_dashboard.serialize_report(report), coverage_dashboard.serialize_report(report)
        first_md, second_md = coverage_dashboard.render_markdown(report), coverage_dashboard.render_markdown(report)
        self.assertEqual(first_json, second_json)
        self.assertEqual(first_md, second_md)
        self.assertNotIn(str(ROOT), first_json + first_md)
        self.assertIn("warning retained", first_md)
        self.assertIn("unknown retained", first_md)
        self.assertIn("No score is calculated", first_md)

    def test_report_validation_rejects_unsorted_rows(self) -> None:
        report = self.build(
            registered=self.registered("zeta/one") + self.registered("alpha/one"), evidence=[]
        )
        report["scenarios"].reverse()
        with self.assertRaisesRegex(coverage_dashboard.CoverageDashboardError, "unique and sorted"):
            coverage_dashboard.validate_report(report)

    def test_report_validation_rejects_unproven_maturity_with_evidence(self) -> None:
        report = self.build(registered=[], evidence=[self.normalize(self.envelope(run_id="success-run"))])
        report["scenarios"][0]["strongest_proven_maturity"]["level"] = "not-proven"
        with self.assertRaisesRegex(coverage_dashboard.CoverageDashboardError, "must not cite evidence"):
            coverage_dashboard.validate_report(report)


if __name__ == "__main__":
    unittest.main()
