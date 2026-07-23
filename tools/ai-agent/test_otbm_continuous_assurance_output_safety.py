from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/ai-agent/otbm_continuous_assurance_tool.py"

class ContinuousAssuranceOutputSafetyTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> str:
        path.write_text(json.dumps(value), encoding="utf-8")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_inputs(self, directory: Path) -> dict[str, Path]:
        paths = {name: directory / f"{name}.json" for name in (
            "execution", "regression", "before_health", "after_health", "before_cert", "after_cert"
        )}
        regression = {
            "format": "canary-otbm-map-change-regression-v1",
            "schemaVersion": 1,
            "source": {
                "beforeMapSha256": "1" * 64, "afterMapSha256": "2" * 64,
                "beforeWorldIndexSha256": "3" * 64, "afterWorldIndexSha256": "4" * 64,
            },
            "staticValidation": {"failClosed": False, "selected": [], "skipped": []},
            "physicalValidation": {"manualSelectionRequired": False, "scenarios": []},
        }
        health_summary = {
            "structuralFindings": 0, "runtimeHandlerPlacementFindings": 0, "attentionMechanics": 0,
            "staleEvidenceTargets": 0, "missingPhysicalScenarioTargets": 0, "runtimeNotProvenOnCurrentMapTargets": 0,
        }
        before_health = {
            "format": "canary-otbm-world-health-v1", "schemaVersion": 1,
            "source": {"mapSha256": "1" * 64, "worldIndexSha256": "3" * 64}, "summary": health_summary,
        }
        after_health = {
            "format": "canary-otbm-world-health-v1", "schemaVersion": 1,
            "source": {"mapSha256": "2" * 64, "worldIndexSha256": "4" * 64}, "summary": health_summary,
        }
        before_cert = {
            "format": "canary-otbm-region-quest-certification-v1", "schemaVersion": 1,
            "currentMap": {"mapSha256": "1" * 64, "worldIndexSha256": "3" * 64}, "certifications": [],
        }
        after_cert = {
            "format": "canary-otbm-region-quest-certification-v1", "schemaVersion": 1,
            "currentMap": {"mapSha256": "2" * 64, "worldIndexSha256": "4" * 64}, "certifications": [],
        }
        hashes = {
            "regression": self.write_json(paths["regression"], regression),
            "before_health": self.write_json(paths["before_health"], before_health),
            "after_health": self.write_json(paths["after_health"], after_health),
            "before_cert": self.write_json(paths["before_cert"], before_cert),
            "after_cert": self.write_json(paths["after_cert"], after_cert),
        }
        execution = {
            "format": "canary-otbm-continuous-assurance-execution-v1", "schemaVersion": 1,
            "inputs": {
                "regressionPlanSha256": hashes["regression"],
                "beforeWorldHealthSha256": hashes["before_health"],
                "afterWorldHealthSha256": hashes["after_health"],
                "beforeCertificationSha256": hashes["before_cert"],
                "afterCertificationSha256": hashes["after_cert"],
            },
            "staticValidation": [], "physicalValidation": [],
        }
        self.write_json(paths["execution"], execution)
        return paths

    def run_tool(self, paths: dict[str, Path], output: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable, str(TOOL),
                "--execution-ledger", str(paths["execution"]),
                "--regression-plan", str(paths["regression"]),
                "--before-world-health", str(paths["before_health"]),
                "--after-world-health", str(paths["after_health"]),
                "--before-certification", str(paths["before_cert"]),
                "--after-certification", str(paths["after_cert"]),
                "--output", str(output), *extra,
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )

    def test_create_new_refuses_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            paths = self.write_inputs(directory)
            output = directory / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            result = self.run_tool(paths, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel")

    def test_overwrite_is_explicit_and_successful(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            paths = self.write_inputs(directory)
            output = directory / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            result = self.run_tool(paths, output, "--overwrite")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(report["gate"]["passed"])

    def test_output_cannot_alias_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            paths = self.write_inputs(directory)
            result = self.run_tool(paths, paths["regression"], "--overwrite")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(paths["regression"].read_text(encoding="utf-8"))["format"], "canary-otbm-map-change-regression-v1")

if __name__ == "__main__":
    unittest.main()
