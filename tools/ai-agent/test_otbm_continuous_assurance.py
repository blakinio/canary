from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("otbm_continuous_assurance.py")
SPEC = importlib.util.spec_from_file_location("canary_otbm_continuous_assurance", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

class ContinuousAssuranceTests(unittest.TestCase):
    def pin(self, fmt: str, char: str) -> dict:
        return {"fileName": f"{char}.json", "size": 1, "sha256": char * 64, "format": fmt}

    def pins(self) -> dict:
        return {
            "executionLedger": self.pin(MODULE.EXECUTION_FORMAT, "a"),
            "regressionPlan": self.pin(MODULE.REGRESSION_FORMAT, "b"),
            "beforeWorldHealth": self.pin(MODULE.WORLD_HEALTH_FORMAT, "c"),
            "afterWorldHealth": self.pin(MODULE.WORLD_HEALTH_FORMAT, "d"),
            "beforeCertification": self.pin(MODULE.CERTIFICATION_FORMAT, "e"),
            "afterCertification": self.pin(MODULE.CERTIFICATION_FORMAT, "f"),
        }

    def regression(self, *, fail_closed: bool = False) -> dict:
        return {
            "format": MODULE.REGRESSION_FORMAT,
            "schemaVersion": 1,
            "source": {
                "beforeMapSha256": "1" * 64,
                "afterMapSha256": "2" * 64,
                "beforeWorldIndexSha256": "3" * 64,
                "afterWorldIndexSha256": "4" * 64,
            },
            "staticValidation": {
                "failClosed": fail_closed,
                "selected": [{"validator": "otbm-map-quality"}],
                "skipped": [],
            },
            "physicalValidation": {
                "manualSelectionRequired": False,
                "scenarios": [{
                    "suite": "quest",
                    "id": "alpha",
                    "selected": True,
                }],
            },
        }

    def health(self, before: bool, **overrides: int) -> dict:
        summary = {key: 0 for key in MODULE.WORLD_HEALTH_KEYS}
        summary.update(overrides)
        return {
            "format": MODULE.WORLD_HEALTH_FORMAT,
            "schemaVersion": 1,
            "source": {
                "mapSha256": ("1" if before else "2") * 64,
                "worldIndexSha256": ("3" if before else "4") * 64,
            },
            "summary": summary,
        }

    def certification(self, before: bool, level: str = "C4_STATIC_QUALITY_GREEN", state: str = "certified") -> dict:
        return {
            "format": MODULE.CERTIFICATION_FORMAT,
            "schemaVersion": 1,
            "currentMap": {
                "mapSha256": ("1" if before else "2") * 64,
                "worldIndexSha256": ("3" if before else "4") * 64,
            },
            "certifications": [{
                "targetId": "quest.alpha",
                "certificationLevel": level,
                "certificationState": state,
            }],
        }

    def execution(self, pins: dict, *, static_status: str = "passed", physical_status: str = "passed") -> dict:
        return {
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
                "status": static_status,
                "evidence": {"format": "canary-otbm-map-quality-v1", "sha256": "7" * 64},
            }],
            "physicalValidation": [{
                "suite": "quest",
                "id": "alpha",
                "status": physical_status,
                "evidence": {"format": "universal-agent-e2e-result-v1", "sha256": "8" * 64},
            }],
        }

    def build(self, **kwargs) -> dict:
        pins = kwargs.pop("pins", self.pins())
        return MODULE.build_continuous_assurance_report(
            execution_ledger=kwargs.pop("execution_ledger", self.execution(pins)),
            regression_plan=kwargs.pop("regression_plan", self.regression()),
            before_world_health=kwargs.pop("before_world_health", self.health(True)),
            after_world_health=kwargs.pop("after_world_health", self.health(False)),
            before_certification=kwargs.pop("before_certification", self.certification(True)),
            after_certification=kwargs.pop("after_certification", self.certification(False)),
            input_pins=pins,
        )

    def test_gate_passes_when_selected_validation_and_deltas_are_clean(self) -> None:
        report = self.build()
        self.assertTrue(report["gate"]["passed"])
        self.assertEqual(report["gate"]["blockers"], [])

    def test_selected_static_failure_blocks_gate(self) -> None:
        pins = self.pins()
        report = self.build(pins=pins, execution_ledger=self.execution(pins, static_status="failed"))
        self.assertFalse(report["gate"]["passed"])
        self.assertIn("STATIC_VALIDATOR_NOT_PASSED:otbm-map-quality", report["gate"]["blockers"])

    def test_world_health_regression_blocks_gate(self) -> None:
        report = self.build(after_world_health=self.health(False, structuralFindings=1))
        self.assertFalse(report["gate"]["passed"])
        self.assertIn("WORLD_HEALTH_REGRESSION:structuralFindings", report["gate"]["blockers"])

    def test_certification_regression_blocks_gate(self) -> None:
        report = self.build(after_certification=self.certification(False, level="C3_STATIC_REACHABLE"))
        self.assertFalse(report["gate"]["passed"])
        self.assertIn("CERTIFICATION_LEVEL_REGRESSION:quest.alpha", report["gate"]["blockers"])

    def test_fail_closed_regression_selection_blocks_gate_even_when_execution_passes(self) -> None:
        report = self.build(regression_plan=self.regression(fail_closed=True))
        self.assertFalse(report["gate"]["passed"])
        self.assertIn("REGRESSION_STATIC_SELECTION_FAIL_CLOSED", report["gate"]["blockers"])

    def test_execution_result_set_must_exactly_match_selected_validation(self) -> None:
        pins = self.pins()
        execution = self.execution(pins)
        execution["staticValidation"] = []
        with self.assertRaisesRegex(MODULE.ContinuousAssuranceError, "must exactly match"):
            self.build(pins=pins, execution_ledger=execution)

if __name__ == "__main__":
    unittest.main()
