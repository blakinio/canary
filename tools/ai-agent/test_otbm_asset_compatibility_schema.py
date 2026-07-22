from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_asset_compatibility import MANIFEST_FORMAT, REPORT_FORMAT


ROOT = Path(__file__).resolve().parents[2]


class AssetCompatibilitySchemaTests(unittest.TestCase):
    def test_manifest_schema_contract(self) -> None:
        schema = json.loads((ROOT / "docs/ai-agent/OTBM_ASSET_COMPATIBILITY_MANIFEST.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], MANIFEST_FORMAT)
        self.assertIn("baselineAppearancesSha256", schema["properties"])

    def test_report_schema_contract(self) -> None:
        schema = json.loads((ROOT / "docs/ai-agent/OTBM_ASSET_COMPATIBILITY.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertIn("policy", schema["required"])

    def test_policy_keeps_static_runtime_boundary(self) -> None:
        source = (ROOT / "tools/ai-agent/otbm_asset_compatibility.py").read_text(encoding="utf-8")
        self.assertIn('"runtimeRenderingProven": False', source)
        self.assertIn('"mutatesMapOrAssets": False', source)
        self.assertIn("WorldIndex", source)


if __name__ == "__main__":
    unittest.main()
