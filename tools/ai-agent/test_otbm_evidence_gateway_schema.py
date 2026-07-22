from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_evidence_gateway import BUNDLE_FORMAT, MANIFEST_FORMAT

ROOT = Path(__file__).resolve().parents[2]


class EvidenceGatewaySchemaTests(unittest.TestCase):
    def test_formats(self) -> None:
        manifest = json.loads((ROOT / "docs/ai-agent/OTBM_EVIDENCE_GATEWAY_MANIFEST.schema.json").read_text(encoding="utf-8"))
        bundle = json.loads((ROOT / "docs/ai-agent/OTBM_EVIDENCE_GATEWAY.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertEqual(bundle["properties"]["format"]["const"], BUNDLE_FORMAT)

    def test_gateway_ownership_boundary(self) -> None:
        source = (ROOT / "tools/ai-agent/otbm_evidence_gateway.py").read_text(encoding="utf-8")
        self.assertIn('"parsesOtbm": False', source)
        self.assertIn('"validatesSourceSemantics": False', source)
        self.assertIn('"pathfinds": False', source)
        self.assertIn('"runsE2e": False', source)
        self.assertIn('"ownsDownstreamAcceptance": False', source)


if __name__ == "__main__":
    unittest.main()
