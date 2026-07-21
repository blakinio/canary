from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_coverage_dashboard import REPORT_FORMAT, TARGETS_FORMAT

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGETS_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_COVERAGE_DASHBOARD_TARGETS.schema.json"
REPORT_SCHEMA = REPO_ROOT / "docs/ai-agent/OTBM_COVERAGE_DASHBOARD.schema.json"


class CoverageDashboardSchemaTests(unittest.TestCase):
    def test_targets_schema_supports_exact_reviewed_target_kinds_and_dimensions(self) -> None:
        schema = json.loads(TARGETS_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], TARGETS_FORMAT)
        target = schema["$defs"]["target"]
        self.assertEqual(
            set(target["properties"]["kind"]["enum"]),
            {"world", "region", "landmark-route", "quest", "mechanic-set"},
        )
        dimensions = set(schema["$defs"]["requiredDimension"]["enum"])
        self.assertEqual(
            dimensions,
            {
                "indexed-on-exact-map",
                "source-correlated",
                "script-resolved",
                "statically-reachable",
                "interaction-resolved",
                "static-quality-compatible",
                "executable-route-covered",
                "physically-runtime-proven",
                "candidate-map-validated",
                "current-map-provenance",
            },
        )
        self.assertIn("reportSha256", schema["$defs"]["sourceCorrelation"]["required"])
        self.assertIn("evidenceIds", schema["$defs"]["sourceCorrelation"]["required"])
        self.assertIn("interactionRequired", schema["$defs"]["routePlan"]["required"])

    def test_report_schema_keeps_dimensions_independent_and_certification_unassigned(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        dimensions = schema["$defs"]["dimensions"]
        self.assertEqual(
            set(dimensions["required"]),
            {
                "indexedOnExactMap",
                "sourceCorrelated",
                "scriptResolved",
                "staticallyReachable",
                "interactionResolved",
                "staticQualityCompatible",
                "executableRouteCovered",
                "physicallyRuntimeProven",
                "candidateMapValidated",
            },
        )
        self.assertEqual(
            set(schema["$defs"]["dimensionState"]["enum"]),
            {"proven", "blocked", "stale", "not-evaluated", "not-applicable"},
        )
        self.assertEqual(schema["$defs"]["target"]["properties"]["formalCertificationLevel"]["type"], "null")

    def test_report_policy_forbids_opaque_scores_and_execution_ownership(self) -> None:
        schema = json.loads(REPORT_SCHEMA.read_text(encoding="utf-8"))
        policy = schema["properties"]["policy"]["properties"]
        self.assertTrue(policy["readOnly"]["const"])
        self.assertFalse(policy["mapModified"]["const"])
        self.assertFalse(policy["otbmParsedIndependently"]["const"])
        self.assertFalse(policy["validatorsRecomputed"]["const"])
        self.assertFalse(policy["routeGenerated"]["const"])
        self.assertFalse(policy["physicalE2eExecuted"]["const"])
        self.assertFalse(policy["candidateValidationExecuted"]["const"])
        self.assertFalse(policy["formalCertificationAssigned"]["const"])
        self.assertFalse(policy["opaqueScoreEmitted"]["const"])
        self.assertFalse(policy["missingEvidenceMeansGlobalAbsence"]["const"])
        self.assertFalse(policy["downstreamScenarioPrioritizationDirected"]["const"])


if __name__ == "__main__":
    unittest.main()
