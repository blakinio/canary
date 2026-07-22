from __future__ import annotations

import unittest

from otbm_change_risk import ChangeRiskError, build_change_risk_report, normalize_policy


POLICY = {
    "format": "canary-otbm-change-risk-policy-v1",
    "weights": {
        "critical-infrastructure": 5,
        "identifier-semantics": 4,
        "quest-dependency": 3,
        "fragile-route": 4,
        "certification-invalidated": 3,
        "multi-region": 2,
        "unresolved-evidence": 4,
        "asset-walkability": 3,
    },
    "thresholds": {"low": 0, "medium": 3, "high": 7, "critical": 12},
}


def _ref(identifier: str) -> dict:
    return {"sourceFormat": "fixture-v1", "sha256": "c" * 64, "findingIds": [identifier]}


def _input(factors: list[dict]) -> dict:
    return {"format": "canary-otbm-change-risk-input-v1", "beforeMapSha256": "a" * 64, "afterMapSha256": "b" * 64, "factors": factors}


class ChangeRiskTests(unittest.TestCase):
    def test_explicit_contributions_drive_level(self) -> None:
        report = build_change_risk_report(POLICY, _input([
            {"factor": "critical-infrastructure", "status": "present", "evidence": [_ref("critical-1")]},
            {"factor": "identifier-semantics", "status": "present", "evidence": [_ref("id-1")]},
        ]))
        self.assertEqual(report["score"], 9)
        self.assertEqual(report["riskLevel"], "high")
        self.assertEqual(sum(item["contribution"] for item in report["contributions"]), 9)

    def test_unresolved_factor_fails_conservatively_into_score(self) -> None:
        report = build_change_risk_report(POLICY, _input([
            {"factor": "unresolved-evidence", "status": "unresolved", "evidence": [_ref("unresolved-1")]},
        ]))
        self.assertEqual(report["riskLevel"], "medium")
        self.assertEqual(report["unresolvedFactors"], ["unresolved-evidence"])

    def test_absent_factor_does_not_contribute(self) -> None:
        report = build_change_risk_report(POLICY, _input([]))
        self.assertEqual(report["score"], 0)
        self.assertEqual(report["riskLevel"], "low")

    def test_present_factor_requires_evidence(self) -> None:
        with self.assertRaises(ChangeRiskError):
            build_change_risk_report(POLICY, _input([{"factor": "multi-region", "status": "present", "evidence": []}]))

    def test_thresholds_must_be_strictly_increasing(self) -> None:
        policy = {**POLICY, "thresholds": {"low": 0, "medium": 3, "high": 3, "critical": 12}}
        with self.assertRaises(ChangeRiskError):
            normalize_policy(policy)

    def test_report_never_authorizes_merge(self) -> None:
        report = build_change_risk_report(POLICY, _input([]))
        self.assertFalse(report["policy"]["authorizesMerge"])
        self.assertFalse(report["policy"]["authorizesValidationSkip"])

    def test_hash_deterministic(self) -> None:
        self.assertEqual(build_change_risk_report(POLICY, _input([]))["reportSha256"], build_change_risk_report(POLICY, _input([]))["reportSha256"])


if __name__ == "__main__":
    unittest.main()
