from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("otbm_region_quest_certification.py")
SPEC = importlib.util.spec_from_file_location("canary_otbm_region_quest_certification", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

class CertificationTests(unittest.TestCase):
    def pin(self, fmt: str, char: str) -> dict:
        return {"fileName": f"{char}.json", "size": 1, "sha256": char * 64, "format": fmt}

    def dimension(self, state: str, blockers: list[str] | None = None) -> dict:
        return {"state": state, "evidence": [], "memberIds": [], "blockers": blockers or []}

    def target(self, target_id: str = "quest.alpha", kind: str = "quest") -> dict:
        keys = [
            "indexedOnExactMap", "sourceCorrelated", "scriptResolved", "staticallyReachable",
            "interactionResolved", "staticQualityCompatible", "executableRouteCovered",
            "physicallyRuntimeProven", "candidateMapValidated",
        ]
        dimensions = {key: self.dimension("proven") for key in keys}
        dimensions["interactionResolved"] = self.dimension("not-applicable")
        return {
            "id": target_id,
            "kind": kind,
            "reason": "reviewed target",
            "formalCertificationLevel": None,
            "requirementsSatisfied": True,
            "dimensions": dimensions,
            "staleAgainstCurrentMap": {"state": "current", "evidence": [], "blockers": []},
        }

    def coverage(self, target: dict) -> dict:
        return {
            "format": MODULE.COVERAGE_FORMAT,
            "schemaVersion": 1,
            "policy": {"formalCertificationAssigned": False},
            "currentMap": {"mapSha256": "b" * 64, "worldIndexSha256": "c" * 64},
            "targets": [target],
        }

    def manifest(self, target_id: str, maximum_level: str) -> dict:
        return {
            "format": MODULE.MANIFEST_FORMAT,
            "schemaVersion": 1,
            "targets": [{"targetId": target_id, "maximumLevel": maximum_level, "reason": "bounded certification"}],
        }

    def build(self, target: dict, maximum_level: str) -> dict:
        return MODULE.build_certification_report(
            manifest=self.manifest(target["id"], maximum_level),
            coverage_dashboard=self.coverage(target),
            input_pins={
                "manifest": self.pin(MODULE.MANIFEST_FORMAT, "a"),
                "coverageDashboard": self.pin(MODULE.COVERAGE_FORMAT, "d"),
            },
        )

    def test_quest_with_complete_current_evidence_reaches_c7(self) -> None:
        report = self.build(self.target(), "C7_CANDIDATE_CHANGE_REVALIDATED")
        certification = report["certifications"][0]
        self.assertEqual(certification["certificationLevel"], "C7_CANDIDATE_CHANGE_REVALIDATED")
        self.assertEqual(certification["certificationState"], "certified")
        self.assertFalse(certification["staleAgainstCurrentMap"])

    def test_levels_are_contiguous_and_stop_at_first_gap(self) -> None:
        target = self.target()
        target["dimensions"]["staticQualityCompatible"] = self.dimension("blocked", ["QUALITY_RED"])
        report = self.build(target, "C7_CANDIDATE_CHANGE_REVALIDATED")
        certification = report["certifications"][0]
        self.assertEqual(certification["certificationLevel"], "C3_STATIC_REACHABLE")
        self.assertEqual(certification["certificationState"], "certified")
        self.assertIn("QUALITY_RED", certification["blockers"])
        self.assertEqual(certification["evaluatedLevels"][-1]["level"], "C4_STATIC_QUALITY_GREEN")

    def test_stale_current_map_provenance_collapses_formal_level_to_c0(self) -> None:
        target = self.target()
        target["staleAgainstCurrentMap"] = {
            "state": "stale",
            "evidence": [],
            "blockers": ["CURRENT_MAP_PROVENANCE_NOT_FULLY_PROVEN"],
        }
        report = self.build(target, "C7_CANDIDATE_CHANGE_REVALIDATED")
        certification = report["certifications"][0]
        self.assertEqual(certification["certificationLevel"], "C0_NOT_EVALUATED")
        self.assertEqual(certification["certificationState"], "stale")
        self.assertTrue(certification["staleAgainstCurrentMap"])

    def test_region_cannot_request_feature_level(self) -> None:
        target = self.target(target_id="thais.region", kind="region")
        with self.assertRaisesRegex(MODULE.CertificationError, "cannot request above"):
            self.build(target, "C6_FEATURE_OR_MECHANIC_PHYSICALLY_PROVEN")

    def test_world_target_is_rejected(self) -> None:
        target = self.target(target_id="world", kind="world")
        with self.assertRaisesRegex(MODULE.CertificationError, "unsupported bounded kind"):
            self.build(target, "C5_PHYSICAL_ROUTE_PROVEN")

    def test_missing_coverage_target_fails_closed(self) -> None:
        manifest = self.manifest("quest.missing", "C1_STATIC_INDEXED")
        with self.assertRaisesRegex(MODULE.CertificationError, "missing from the coverage dashboard"):
            MODULE.build_certification_report(
                manifest=manifest,
                coverage_dashboard=self.coverage(self.target()),
                input_pins={
                    "manifest": self.pin(MODULE.MANIFEST_FORMAT, "a"),
                    "coverageDashboard": self.pin(MODULE.COVERAGE_FORMAT, "d"),
                },
            )

if __name__ == "__main__":
    unittest.main()
