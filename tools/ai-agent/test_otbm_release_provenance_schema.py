from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_release_provenance import BOM_FORMAT, REPORT_FORMAT

ROOT = Path(__file__).resolve().parents[2]


class ReleaseProvenanceSchemaTests(unittest.TestCase):
    def test_bom_schema_contract(self) -> None:
        schema = json.loads((ROOT / "docs/ai-agent/OTBM_RELEASE_BOM.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], BOM_FORMAT)
        self.assertIn("dimensions", schema["required"])

    def test_report_schema_contract(self) -> None:
        schema = json.loads((ROOT / "docs/ai-agent/OTBM_RELEASE_PROVENANCE.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertIn("dimensionFreshness", schema["required"])

    def test_policy_rejects_timestamp_and_runtime_proof(self) -> None:
        source = (ROOT / "tools/ai-agent/otbm_release_provenance.py").read_text(encoding="utf-8")
        self.assertIn('"timestampsUsedAsFreshnessEvidence": False', source)
        self.assertIn('"runtimeCompatibilityProven": False', source)


if __name__ == "__main__":
    unittest.main()
