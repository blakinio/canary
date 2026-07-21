from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_repair_recommendation import REPORT_FORMAT, REQUEST_FORMAT, SCHEMA_VERSION, build_repair_recommendation
from test_otbm_repair_recommendation import pins, preflight, request


ROOT = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA_PATH = ROOT / "docs" / "ai-agent" / "OTBM_REPAIR_RECOMMENDATION_REQUEST.schema.json"
REPORT_SCHEMA_PATH = ROOT / "docs" / "ai-agent" / "OTBM_REPAIR_RECOMMENDATION.schema.json"


class RepairRecommendationSchemaTests(unittest.TestCase):
    def test_schemas_are_valid_json_and_track_public_formats(self) -> None:
        request_schema = json.loads(REQUEST_SCHEMA_PATH.read_text(encoding="utf-8"))
        report_schema = json.loads(REPORT_SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(request_schema["properties"]["format"]["const"], REQUEST_FORMAT)
        self.assertEqual(request_schema["properties"]["schemaVersion"]["const"], SCHEMA_VERSION)
        self.assertEqual(report_schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(report_schema["properties"]["schemaVersion"]["const"], SCHEMA_VERSION)
        self.assertEqual(
            set(report_schema["properties"]["state"]["enum"]),
            {
                "no-repair-evidence",
                "review-required",
                "supported-by-existing-attribute-path",
                "supported-by-existing-tile-area-path",
                "supported-by-existing-raw-tile-path",
                "unsupported-mutation-shape",
                "blocked-by-runtime-evidence",
                "ambiguous-target",
            },
        )

    def test_generated_report_matches_schema_top_level_shape(self) -> None:
        schema = json.loads(REPORT_SCHEMA_PATH.read_text(encoding="utf-8"))
        report = build_repair_recommendation(request=request(), repair_preflight=preflight(), input_pins=pins())

        self.assertEqual(set(report), set(schema["required"]))
        self.assertEqual(set(report["source"]), set(schema["properties"]["source"]["required"]))
        self.assertEqual(set(report["provenance"]), set(schema["properties"]["provenance"]["required"]))
        self.assertEqual(set(report["preflight"]), set(schema["properties"]["preflight"]["required"]))
        self.assertEqual(set(report["capability"]), set(schema["properties"]["capability"]["required"]))
        self.assertEqual(set(report["review"]), set(schema["properties"]["review"]["required"]))


if __name__ == "__main__":
    unittest.main()
