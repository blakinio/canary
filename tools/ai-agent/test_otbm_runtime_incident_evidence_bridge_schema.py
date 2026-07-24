from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_runtime_incident_evidence_bridge import BINDINGS_FORMAT, REPORT_FORMAT

ROOT = Path(__file__).resolve().parents[2]


class RuntimeIncidentEvidenceBridgeSchemaTests(unittest.TestCase):
    def test_formats_match_public_contracts(self) -> None:
        bindings = json.loads(
            (ROOT / "docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BINDINGS.schema.json").read_text(encoding="utf-8")
        )
        report = json.loads(
            (ROOT / "docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(bindings["properties"]["format"]["const"], BINDINGS_FORMAT)
        self.assertEqual(report["properties"]["format"]["const"], REPORT_FORMAT)

    def test_report_schema_preserves_qa018_delegation_and_no_diagnosis_boundary(self) -> None:
        report = json.loads(
            (ROOT / "docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.schema.json").read_text(encoding="utf-8")
        )
        policy = report["properties"]["policy"]["properties"]
        self.assertEqual(policy["qa018EvidenceGatewayReused"]["const"], True)
        self.assertEqual(policy["parsesRuntimeLogs"]["const"], False)
        self.assertEqual(policy["infersSelectors"]["const"], False)
        self.assertEqual(policy["classifiesFailure"]["const"], False)
        self.assertEqual(policy["diagnosesRootCause"]["const"], False)
        self.assertEqual(policy["pathfinds"]["const"], False)
        self.assertEqual(policy["runsE2e"]["const"], False)
        self.assertEqual(policy["emitsNextAction"]["const"], False)


if __name__ == "__main__":
    unittest.main()
