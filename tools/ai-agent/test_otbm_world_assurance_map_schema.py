from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_world_assurance_map import MAP_FORMAT, build_world_assurance_map_plan
from test_otbm_world_assurance_map import FILE_SHA, campaign


class WorldAssuranceMapSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema_path = Path(__file__).resolve().parents[2] / "docs" / "ai-agent" / "OTBM_WORLD_ASSURANCE_MAP.schema.json"
        cls.schema = json.loads(cls.schema_path.read_text(encoding="utf-8"))

    def test_schema_document_declares_expected_contract(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.schema["properties"]["format"]["const"], MAP_FORMAT)
        self.assertEqual(self.schema["properties"]["schemaVersion"]["const"], 1)
        self.assertFalse(self.schema["additionalProperties"])
        self.assertIn("reportSha256", self.schema["required"])
        target_schema = self.schema["properties"]["targets"]["items"]
        self.assertIn("baseRender", target_schema["required"])
        self.assertIn("overlay", target_schema["required"])
        overlay = target_schema["properties"]["overlay"]
        self.assertIn("annotations", overlay["required"])
        self.assertIn("panels", overlay["required"])
        refs = self.schema["$defs"]["evidenceRefs"]
        self.assertEqual(refs["minItems"], 1)
        self.assertIn("^campaign:", refs["items"]["pattern"])

    def test_generated_plan_satisfies_required_schema_shape(self):
        plan = build_world_assurance_map_plan(campaign(), campaign_file_sha256=FILE_SHA)
        for key in self.schema["required"]:
            self.assertIn(key, plan)
        self.assertEqual(plan["format"], MAP_FORMAT)
        self.assertEqual(plan["schemaVersion"], 1)
        target_required = self.schema["properties"]["targets"]["items"]["required"]
        for target in plan["targets"]:
            for key in target_required:
                self.assertIn(key, target)
            for annotation in target["overlay"]["annotations"]:
                self.assertTrue(annotation["evidenceRefs"])
            for panel in target["overlay"]["panels"]:
                self.assertTrue(panel["evidenceRefs"])


if __name__ == "__main__":
    unittest.main()
