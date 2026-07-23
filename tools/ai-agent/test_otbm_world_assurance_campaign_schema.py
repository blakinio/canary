from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "ai-agent"


class WorldAssuranceCampaignSchemaTests(unittest.TestCase):
    def test_manifest_and_report_schemas_are_valid_draft_2020_12(self):
        for name in (
            "OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json",
            "OTBM_WORLD_ASSURANCE_CAMPAIGN.schema.json",
        ):
            schema = json.loads((DOCS / name).read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_reviewed_owa001_target_manifest_matches_schema(self):
        schema = json.loads(
            (DOCS / "OTBM_WORLD_ASSURANCE_CAMPAIGN_MANIFEST.schema.json").read_text(encoding="utf-8")
        )
        document = json.loads(
            (DOCS / "OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator(schema).validate(document)


if __name__ == "__main__":
    unittest.main()
