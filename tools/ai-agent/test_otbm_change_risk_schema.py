from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_change_risk import INPUT_FORMAT, POLICY_FORMAT, REPORT_FORMAT

ROOT = Path(__file__).resolve().parents[2]


class ChangeRiskSchemaTests(unittest.TestCase):
    def test_formats(self) -> None:
        policy = json.loads((ROOT / "docs/ai-agent/OTBM_CHANGE_RISK_POLICY.schema.json").read_text(encoding="utf-8"))
        risk_input = json.loads((ROOT / "docs/ai-agent/OTBM_CHANGE_RISK_INPUT.schema.json").read_text(encoding="utf-8"))
        report = json.loads((ROOT / "docs/ai-agent/OTBM_CHANGE_RISK.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["properties"]["format"]["const"], POLICY_FORMAT)
        self.assertEqual(risk_input["properties"]["format"]["const"], INPUT_FORMAT)
        self.assertEqual(report["properties"]["format"]["const"], REPORT_FORMAT)

    def test_no_authorization_boundary(self) -> None:
        source = (ROOT / "tools/ai-agent/otbm_change_risk.py").read_text(encoding="utf-8")
        self.assertIn('"opaqueAiScore": False', source)
        self.assertIn('"authorizesMerge": False', source)
        self.assertIn('"authorizesValidationSkip": False', source)


if __name__ == "__main__":
    unittest.main()
