from __future__ import annotations

import json
import unittest
from pathlib import Path

from otbm_map_change_regression import REPORT_FORMAT, SCHEMA_VERSION, build_regression_plan
from test_otbm_map_change_regression import input_pins, semantic_diff


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "docs" / "ai-agent" / "OTBM_MAP_CHANGE_REGRESSION.schema.json"


class RegressionGuardSchemaTests(unittest.TestCase):
    def test_schema_is_valid_json_and_tracks_public_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(schema["properties"]["format"]["const"], REPORT_FORMAT)
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], SCHEMA_VERSION)
        self.assertEqual(
            set(schema["$defs"]["staticValidator"]["enum"]),
            {
                "otbm-geometry-audit",
                "otbm-reachability",
                "otbm-script-resolution",
                "quest-map-validation",
                "otbm-spawn-npc-validation",
                "otbm-storage-dependency-graph",
                "otbm-map-quality",
            },
        )

    def test_generated_minimal_report_matches_schema_top_level_shape(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        report = build_regression_plan(
            semantic_diff=semantic_diff(),
            input_pins=input_pins(),
        )

        self.assertEqual(set(report), set(schema["required"]))
        self.assertEqual(set(report["source"]), set(schema["$defs"]["sourceIdentity"]["required"]))
        self.assertEqual(set(report["policy"]), set(schema["properties"]["policy"]["required"]))
        self.assertEqual(set(report["provenance"]), set(schema["properties"]["provenance"]["required"]))
        self.assertEqual(set(report["semanticDiff"]), set(schema["properties"]["semanticDiff"]["required"]))
        self.assertEqual(set(report["impactEvidence"]), set(schema["properties"]["impactEvidence"]["required"]))
        self.assertEqual(set(report["staticValidation"]), set(schema["properties"]["staticValidation"]["required"]))
        self.assertEqual(set(report["physicalValidation"]), set(schema["properties"]["physicalValidation"]["required"]))
        self.assertEqual(set(report["summary"]), set(schema["properties"]["summary"]["required"]))


if __name__ == "__main__":
    unittest.main()
