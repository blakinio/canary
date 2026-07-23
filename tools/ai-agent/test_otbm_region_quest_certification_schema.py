from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("otbm_region_quest_certification.py")
SPEC = importlib.util.spec_from_file_location("canary_otbm_region_quest_certification_schema", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

ROOT = Path(__file__).resolve().parents[2]

class CertificationSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_schema = json.loads(
            (ROOT / "docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION_MANIFEST.schema.json").read_text(encoding="utf-8")
        )
        cls.report_schema = json.loads(
            (ROOT / "docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.schema.json").read_text(encoding="utf-8")
        )

    def pin(self, fmt: str, char: str) -> dict:
        return {"fileName": f"{char}.json", "size": 1, "sha256": char * 64, "format": fmt}

    def dimension(self, state: str) -> dict:
        return {"state": state, "evidence": [], "memberIds": [], "blockers": []}

    def test_schema_contracts_track_public_formats_and_generated_shape(self) -> None:
        manifest = {
            "format": MODULE.MANIFEST_FORMAT,
            "schemaVersion": 1,
            "targets": [{
                "targetId": "quest.alpha",
                "maximumLevel": "C7_CANDIDATE_CHANGE_REVALIDATED",
                "reason": "reviewed certification target",
            }],
        }
        target = {
            "id": "quest.alpha",
            "kind": "quest",
            "reason": "reviewed target",
            "formalCertificationLevel": None,
            "requirementsSatisfied": True,
            "dimensions": {
                "indexedOnExactMap": self.dimension("proven"),
                "sourceCorrelated": self.dimension("proven"),
                "scriptResolved": self.dimension("proven"),
                "staticallyReachable": self.dimension("proven"),
                "interactionResolved": self.dimension("not-applicable"),
                "staticQualityCompatible": self.dimension("proven"),
                "executableRouteCovered": self.dimension("proven"),
                "physicallyRuntimeProven": self.dimension("proven"),
                "candidateMapValidated": self.dimension("proven"),
            },
            "staleAgainstCurrentMap": {"state": "current", "evidence": [], "blockers": []},
        }
        coverage = {
            "format": MODULE.COVERAGE_FORMAT,
            "schemaVersion": 1,
            "policy": {"formalCertificationAssigned": False},
            "currentMap": {"mapSha256": "b" * 64, "worldIndexSha256": "c" * 64},
            "targets": [target],
        }
        report = MODULE.build_certification_report(
            manifest=manifest,
            coverage_dashboard=coverage,
            input_pins={
                "manifest": self.pin(MODULE.MANIFEST_FORMAT, "a"),
                "coverageDashboard": self.pin(MODULE.COVERAGE_FORMAT, "d"),
            },
        )
        self.assertEqual(self.manifest_schema["properties"]["format"]["const"], MODULE.MANIFEST_FORMAT)
        self.assertEqual(self.report_schema["properties"]["format"]["const"], MODULE.REPORT_FORMAT)
        self.assertTrue(set(self.manifest_schema["required"]).issubset(manifest))
        self.assertTrue(set(self.report_schema["required"]).issubset(report))
        self.assertEqual(report["certifications"][0]["certificationLevel"], "C7_CANDIDATE_CHANGE_REVALIDATED")

if __name__ == "__main__":
    unittest.main()
