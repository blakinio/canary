from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_static_hotspots import POLICY_FORMAT, REPORT_FORMAT

ROOT = Path(__file__).resolve().parents[2]


class StaticHotspotSchemaTests(unittest.TestCase):
    def test_policy_schema_contract(self) -> None:
        schema = json.loads((ROOT / "docs/ai-agent/OTBM_STATIC_HOTSPOT_POLICY.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], POLICY_FORMAT)
        self.assertIn("placementsPerArea", schema["properties"]["thresholds"]["properties"])

    def test_report_schema_contract(self) -> None:
        schema = json.loads((ROOT / "docs/ai-agent/OTBM_STATIC_HOTSPOTS.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertIn("policy", schema["required"])

    def test_runtime_claim_boundary_is_explicit(self) -> None:
        source = (ROOT / "tools/ai-agent/otbm_static_hotspots.py").read_text(encoding="utf-8")
        self.assertIn('"runtimePerformanceImpactProven": False', source)
        self.assertIn('"runsRuntimeProfiler": False', source)


if __name__ == "__main__":
    unittest.main()
