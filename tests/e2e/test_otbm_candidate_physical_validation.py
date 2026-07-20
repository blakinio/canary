from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

BRIDGE_PATH = Path(__file__).resolve().parents[2] / "tools" / "e2e" / "otbm_candidate_physical_validation.py"


def load_bridge():
    spec = importlib.util.spec_from_file_location("candidate_physical_validation_test_module", BRIDGE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


bridge = load_bridge()


class CandidatePhysicalValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.otbm"
        self.candidate = self.root / "candidate.otbm"
        self.source.write_bytes(b"source-map")
        self.candidate.write_bytes(b"candidate-map")
        self.source_sha = bridge.sha256_path(self.source)
        self.candidate_sha = bridge.sha256_path(self.candidate)
        self.before_index = "1" * 64
        self.after_index = "2" * 64
        self.pipeline = self.root / "pipeline.json"
        self.diff = self.root / "diff.json"
        self.selection = self.root / "selection.json"
        self.write_pipeline()
        self.write_diff()
        self.write_selection(selected=False)

    def tearDown(self):
        self.temp.cleanup()

    def write_pipeline(self):
        self.pipeline.write_text(json.dumps({
            "format": bridge.PIPELINE_FORMAT,
            "schemaVersion": 1,
            "ok": True,
            "source": {"sha256": self.source_sha, "unchanged": True},
            "output": {"sha256": self.candidate_sha, "createNew": True, "byteIdenticalToVerifiedCandidate": True},
            "quality": {"ok": True, "sourceSha256": self.candidate_sha},
            "safety": {
                "sourceModifiedInPlace": False,
                "silentOverwrite": False,
                "newOtbmParserCreated": False,
                "newOtbmWriterCreated": False,
                "existingMutationBoundaryReused": True,
                "existingMapQualityGateReused": True,
                "allDirectFileInputsPinned": True,
                "productionMapExecutionAuthorized": False,
            },
        }), encoding="utf-8")

    def write_diff(self, *, scope="full-index", truncated=False, findings=None):
        findings = [] if findings is None else findings
        self.diff.write_text(json.dumps({
            "format": bridge.DIFF_FORMAT,
            "schemaVersion": 1,
            "ok": True,
            "compatibility": {"compatible": True},
            "provenance": {
                "before": {"sourceMap": {"sha256": self.source_sha}, "worldIndex": {"sha256": self.before_index}},
                "after": {"sourceMap": {"sha256": self.candidate_sha}, "worldIndex": {"sha256": self.after_index}},
            },
            "scope": {"type": scope},
            "summary": {"findings": {"total": len(findings), "sampleCount": len(findings), "truncated": truncated}},
            "findings": findings,
        }), encoding="utf-8")

    def write_selection(self, *, selected: bool):
        self.selection.write_text(json.dumps({
            "format": bridge.SELECTION_FORMAT,
            "schemaVersion": 1,
            "ok": True,
            "semanticDiff": {
                "sha256": bridge.sha256_path(self.diff),
                "beforeMapSha256": self.source_sha,
                "afterMapSha256": self.candidate_sha,
                "beforeWorldIndexSha256": self.before_index,
                "afterWorldIndexSha256": self.after_index,
            },
            "summary": {
                "scenarioCount": 1,
                "selectedCount": 1 if selected else 0,
                "skippedCount": 0 if selected else 1,
                "failClosedCount": 0,
            },
            "scenarios": [{
                "suite": "route",
                "id": "example",
                "manifest": {"path": "ignored", "sha256": "3" * 64},
                "selected": selected,
                "decision": "selected" if selected else "skipped",
                "failClosed": False,
                "reasons": [{"code": "test"}],
                "impactedFindingIds": [],
                "routePlans": [],
            }],
        }), encoding="utf-8")

    def chain(self):
        return bridge.validate_evidence_chain(
            source_map_path=self.source,
            candidate_map_path=self.candidate,
            pipeline_result_path=self.pipeline,
            semantic_diff_path=self.diff,
            impacted_selection_path=self.selection,
        )

    def test_accepts_exact_evidence_chain(self):
        chain = self.chain()
        self.assertEqual(chain.source_sha256, self.source_sha)
        self.assertEqual(chain.candidate_sha256, self.candidate_sha)
        self.assertEqual(chain.before_world_index_sha256, self.before_index)
        self.assertEqual(chain.after_world_index_sha256, self.after_index)

    def test_rejects_pipeline_source_mismatch(self):
        document = json.loads(self.pipeline.read_text())
        document["source"]["sha256"] = "4" * 64
        self.pipeline.write_text(json.dumps(document))
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "pipeline source SHA"):
            self.chain()

    def test_rejects_pipeline_candidate_mismatch(self):
        document = json.loads(self.pipeline.read_text())
        document["output"]["sha256"] = "4" * 64
        self.pipeline.write_text(json.dumps(document))
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "pipeline output SHA"):
            self.chain()

    def test_rejects_failed_quality_gate(self):
        document = json.loads(self.pipeline.read_text())
        document["quality"]["ok"] = False
        self.pipeline.write_text(json.dumps(document))
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "pipeline quality ok"):
            self.chain()

    def test_rejects_in_place_source_policy(self):
        document = json.loads(self.pipeline.read_text())
        document["safety"]["sourceModifiedInPlace"] = True
        self.pipeline.write_text(json.dumps(document))
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "sourceModifiedInPlace"):
            self.chain()

    def test_rejects_diff_candidate_mismatch(self):
        document = json.loads(self.diff.read_text())
        document["provenance"]["after"]["sourceMap"]["sha256"] = "4" * 64
        self.diff.write_text(json.dumps(document))
        self.write_selection(selected=False)
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "after map SHA"):
            self.chain()

    def test_rejects_selection_bound_to_other_diff(self):
        document = json.loads(self.selection.read_text())
        document["semanticDiff"]["sha256"] = "4" * 64
        self.selection.write_text(json.dumps(document))
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "semanticDiff.sha256"):
            self.chain()

    def test_rejects_selection_summary_mismatch(self):
        document = json.loads(self.selection.read_text())
        document["summary"]["selectedCount"] = 1
        self.selection.write_text(json.dumps(document))
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "summary.selectedCount"):
            self.chain()

    def test_no_selected_scenarios_needs_no_repository_discovery(self):
        self.assertEqual(bridge.bind_selected_scenarios(self.root, self.chain()), [])

    def test_landmark_derivation_requires_full_index(self):
        self.write_diff(scope="bounded-region")
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "full-index"):
            bridge._exact_diff_positions(json.loads(self.diff.read_text()))

    def test_landmark_derivation_requires_complete_findings(self):
        self.write_diff()
        document = json.loads(self.diff.read_text())
        document["summary"]["findings"]["total"] = 1
        self.diff.write_text(json.dumps(document))
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "complete exact"):
            bridge._exact_diff_positions(json.loads(self.diff.read_text()))

    def test_runtime_repository_copy_is_disposable_and_candidate_exact(self):
        repo = self.root / "repo"
        datapack = repo / "data-otservbr-global"
        (datapack / "world").mkdir(parents=True)
        (datapack / "world" / "source-marker.txt").write_text("source")
        (repo / "tools" / "e2e").mkdir(parents=True)
        (repo / "tools" / "e2e" / "run_physical_e2e.sh").write_text("#!/usr/bin/env bash\n")
        (repo / "artifacts").mkdir()
        runtime_parent = repo / "artifacts" / "runtime-test"
        runtime_parent.mkdir(parents=True)
        runtime_repo, runtime_map = bridge._copy_runtime_repository(
            repo_root=repo,
            source_datapack="data-otservbr-global",
            map_name="otservbr",
            candidate_map_path=self.candidate,
            candidate_sha256=self.candidate_sha,
            runtime_parent=runtime_parent,
        )
        self.assertEqual(bridge.sha256_path(runtime_map), self.candidate_sha)
        self.assertTrue((runtime_repo / "data-otservbr-global" / "world" / "source-marker.txt").is_file())
        self.assertTrue((runtime_repo / "tools" / "e2e" / "run_physical_e2e.sh").is_file())
        self.assertFalse((datapack / "world" / "otservbr.otbm").exists())
        self.assertFalse((runtime_repo / "artifacts").exists())

    def test_runtime_repository_parent_is_artifact_confined(self):
        repo = self.root / "repo"
        (repo / "data-otservbr-global" / "world").mkdir(parents=True)
        with self.assertRaisesRegex(bridge.CandidatePhysicalValidationError, "under repository artifacts"):
            bridge._copy_runtime_repository(
                repo_root=repo,
                source_datapack="data-otservbr-global",
                map_name="otservbr",
                candidate_map_path=self.candidate,
                candidate_sha256=self.candidate_sha,
                runtime_parent=repo / "outside",
            )


if __name__ == "__main__":
    unittest.main()
