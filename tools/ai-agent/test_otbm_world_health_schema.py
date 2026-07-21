from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_world_health import REPORT_FORMAT, SCHEMA_VERSION, build_world_health_report
from test_otbm_world_health import input_pins, map_quality_report


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "docs" / "ai-agent" / "OTBM_WORLD_HEALTH.schema.json"


class WorldHealthSchemaTests(unittest.TestCase):
    def test_schema_is_valid_json_and_tracks_public_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], SCHEMA_VERSION)
        self.assertEqual(
            set(schema["properties"]["dimensions"]["required"]),
            {"structural", "runtimeHandlers", "reachability", "staleEvidence", "missingPhysicalCoverage"},
        )
        self.assertEqual(
            set(schema["$defs"]["sample"]["properties"]["dimension"]["enum"]),
            {"structural", "runtimeHandlers", "reachability", "staleEvidence", "missingPhysicalCoverage"},
        )

    def test_generated_minimal_report_matches_schema_top_level_shape(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        report = build_world_health_report(
            map_quality=map_quality_report(),
            input_pins=input_pins(reachability_count=0, coverage_count=0),
        )

        self.assertEqual(set(report), set(schema["required"]))
        self.assertEqual(set(report["source"]), set(schema["properties"]["source"]["required"]))
        self.assertEqual(set(report["policy"]), set(schema["properties"]["policy"]["required"]))
        self.assertEqual(set(report["provenance"]), set(schema["properties"]["provenance"]["required"]))
        self.assertEqual(set(report["coverage"]), set(schema["properties"]["coverage"]["required"]))
        self.assertEqual(set(report["dimensions"]), set(schema["properties"]["dimensions"]["required"]))
        self.assertEqual(set(report["summary"]), set(schema["properties"]["summary"]["required"]))


if __name__ == "__main__":
    unittest.main()
