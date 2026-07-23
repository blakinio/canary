from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/ai-agent/otbm_region_quest_certification_tool.py"

class CertificationOutputSafetyTests(unittest.TestCase):
    def write_inputs(self, directory: Path) -> tuple[Path, Path]:
        manifest = {
            "format": "canary-otbm-certification-targets-v1",
            "schemaVersion": 1,
            "targets": [{
                "targetId": "quest.alpha",
                "maximumLevel": "C1_STATIC_INDEXED",
                "reason": "bounded certification",
            }],
        }
        dim = {"state": "proven", "evidence": [], "memberIds": [], "blockers": []}
        target = {
            "id": "quest.alpha",
            "kind": "quest",
            "reason": "reviewed target",
            "formalCertificationLevel": None,
            "requirementsSatisfied": True,
            "dimensions": {
                "indexedOnExactMap": dim,
                "sourceCorrelated": dim,
                "scriptResolved": dim,
                "staticallyReachable": dim,
                "interactionResolved": {"state": "not-applicable", "evidence": [], "memberIds": [], "blockers": []},
                "staticQualityCompatible": dim,
                "executableRouteCovered": dim,
                "physicallyRuntimeProven": dim,
                "candidateMapValidated": dim,
            },
            "staleAgainstCurrentMap": {"state": "current", "evidence": [], "blockers": []},
        }
        coverage = {
            "format": "canary-otbm-coverage-dashboard-v1",
            "schemaVersion": 1,
            "policy": {"formalCertificationAssigned": False},
            "currentMap": {"mapSha256": "b" * 64, "worldIndexSha256": "c" * 64},
            "targets": [target],
        }
        manifest_path = directory / "manifest.json"
        coverage_path = directory / "coverage.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        coverage_path.write_text(json.dumps(coverage), encoding="utf-8")
        return manifest_path, coverage_path

    def run_tool(self, manifest: Path, coverage: Path, output: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(TOOL),
                "--manifest", str(manifest),
                "--coverage-dashboard", str(coverage),
                "--output", str(output),
                *extra,
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_create_new_refuses_existing_output_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            manifest, coverage = self.write_inputs(directory)
            output = directory / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            result = self.run_tool(manifest, coverage, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(encoding="utf-8"), "sentinel")

    def test_overwrite_replaces_regular_output_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            manifest, coverage = self.write_inputs(directory)
            output = directory / "report.json"
            output.write_text("sentinel", encoding="utf-8")
            result = self.run_tool(manifest, coverage, output, "--overwrite")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["format"], "canary-otbm-region-quest-certification-v1")

    def test_output_cannot_alias_an_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            manifest, coverage = self.write_inputs(directory)
            result = self.run_tool(manifest, coverage, manifest, "--overwrite")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["format"], "canary-otbm-certification-targets-v1")

if __name__ == "__main__":
    unittest.main()
