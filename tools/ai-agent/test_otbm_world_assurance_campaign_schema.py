from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "ai-agent"


class WorldAssuranceCampaignSchemaTests(unittest.TestCase):
    def test_manifest_and_report_schemas_are_valid_json_schema_documents(self):
        for name in (
            "OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json",
            "OTBM_WORLD_ASSURANCE_CAMPAIGN.schema.json",
        ):
            schema = json.loads((DOCS / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertEqual(schema["type"], "object")
            self.assertIn("properties", schema)
            self.assertIn("required", schema)

    def test_reviewed_owa001_target_manifest_matches_required_schema_shape(self):
        schema = json.loads(
            (DOCS / "OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json").read_text(encoding="utf-8")
        )
        document = json.loads(
            (DOCS / "OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json").read_text(encoding="utf-8")
        )
        self.assertEqual(document["format"], schema["properties"]["format"]["const"])
        self.assertEqual(document["schemaVersion"], schema["properties"]["schemaVersion"]["const"])
        self.assertTrue(document["campaignId"])
        self.assertEqual(len(document["targets"]), 1)
        target = document["targets"][0]
        required = set(schema["$defs"]["target"]["required"])
        self.assertTrue(required.issubset(target))
        self.assertEqual(target["reviewedDefinition"]["reviewStatus"], "reviewed")
        self.assertEqual(target["class"], "landmark-route")


if __name__ == "__main__":
    unittest.main()
