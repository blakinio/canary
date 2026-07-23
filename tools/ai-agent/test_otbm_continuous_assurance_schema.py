from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import jsonschema

MODULE_PATH = Path(__file__).with_name("otbm_continuous_assurance.py")
SPEC = importlib.util.spec_from_file_location("canary_otbm_continuous_assurance_schema", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

ROOT = Path(__file__).resolve().parents[2]

class ContinuousAssuranceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.execution_schema = json.loads(
            (ROOT / "docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE_EXECUTION.schema.json").read_text(encoding="utf-8")
        )
        cls.report_schema = json.loads(
            (ROOT / "docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.schema.json").read_text(encoding="utf-8")
        )

    def pin(self, fmt: str, char: str) -> dict:
        return {"fileName": f"{char}.json", "size": 1, "sha256": char * 64, "format": fmt}

    def test_generated_report_matches_schema(self) -> None:
        pins = {
            "executionLedger": self.pin(MODULE.EXECUTION_FORMAT, "a"),
            "regressionPlan": self.pin(MODULE.REGRESSION_FORMAT, "b"),
            "beforeWorldHealth": self.pin(MODULE.WORLD_HEALTH_FORMAT, "c"),
            "afterWorldHealth": self.pin(MODULE.WORLD_HEALTH_FORMAT, "d"),
            "beforeCertification": self.pin(MODULE.CERTIFICATION_FORMAT, "e"),
            "afterCertification": self.pin(MODULE.CERTIFICATION_FORMAT, "f"),
        }
        execution = {
            "format": MODULE.EXECUTION_FORMAT,
            "schemaVersion": 1,
            "inputs": {
                "regressionPlanSha256": pins["regressionPlan"]["sha256"],
                "beforeWorldHealthSha256": pins["beforeWorldHealth"]["sha256"],
                "afterWorldHealthSha256": pins["afterWorldHealth"]["sha256"],
                "beforeCertificationSha256": pins["beforeCertification"]["sha256"],
                "afterCertificationSha256": pins["afterCertification"]["sha256"],
            },
            "staticValidation": [{
                "validator": "otbm-map-quality",
                "status": "passed",
                "evidence": {"format": "canary-otbm-map-quality-v1", "sha256": "7" * 64},
            }],
            "physicalValidation": [{
                "suite": "quest",
                "id": "alpha",
                "status": "passed",
                "evidence": {"format": "universal-agent-e2e-result-v1", "sha256": "8" * 64},
            }],
        }
        regression = {
            "format": MODULE.REGRESSION_FORMAT,
            "schemaVersion": 1,
            "source": {
                "beforeMapSha256": "1" * 64, "afterMapSha256": "2" * 64,
                "beforeWorldIndexSha256": "3" * 64, "afterWorldIndexSha256": "4" * 64,
            },
            "staticValidation": {"failClosed": False, "selected": [{"validator": "otbm-map-quality"}], "skipped": []},
            "physicalValidation": {"manualSelectionRequired": False, "scenarios": [{"suite": "quest", "id": "alpha", "selected": True}]},
        }
        def health(before: bool) -> dict:
            return {
                "format": MODULE.WORLD_HEALTH_FORMAT, "schemaVersion": 1,
                "source": {"mapSha256": ("1" if before else "2") * 64, "worldIndexSha256": ("3" if before else "4") * 64},
                "summary": {key: 0 for key in MODULE.WORLD_HEALTH_KEYS},
            }
        def cert(before: bool) -> dict:
            return {
                "format": MODULE.CERTIFICATION_FORMAT, "schemaVersion": 1,
                "currentMap": {"mapSha256": ("1" if before else "2") * 64, "worldIndexSha256": ("3" if before else "4") * 64},
                "certifications": [{"targetId": "quest.alpha", "certificationLevel": "C4_STATIC_QUALITY_GREEN", "certificationState": "certified"}],
            }
        report = MODULE.build_continuous_assurance_report(
            execution_ledger=execution, regression_plan=regression,
            before_world_health=health(True), after_world_health=health(False),
            before_certification=cert(True), after_certification=cert(False),
            input_pins=pins,
        )
        jsonschema.Draft202012Validator(self.execution_schema).validate(execution)
        jsonschema.Draft202012Validator(self.report_schema).validate(report)

if __name__ == "__main__":
    unittest.main()
