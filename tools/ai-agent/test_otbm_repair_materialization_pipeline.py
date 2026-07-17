from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from otbm_area_materializer import APPROVAL_FORMAT, materialize_area_plan
from otbm_region_merge_planner import analyze_region_merge_plan
from otbm_repair_materialization_pipeline import (
    ATTRIBUTE_MODE,
    TILE_AREA_MODE,
    MutationExecution,
    RepairMaterializationPipelineError,
    execute_area_mutation,
    run_pipeline,
)
from otbm_semantic_diff_types import sha256_path
from otbm_world_index import build_world_index
from test_otbm_area_materializer import make_area_map


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _quality_components(
    root: Path,
    source_sha256: str,
    *,
    unresolved: bool = False,
    conflicting: bool = False,
) -> tuple[Path, Path, Path]:
    geometry = root / "geometry.json"
    reachability = root / "reachability.json"
    script_resolution = root / "script-resolution.json"
    _write_json(
        geometry,
        {
            "format": "canary-otbm-geometry-audit-v1",
            "ok": True,
            "complete": True,
            "provenance": {"source": {"sha256": source_sha256}},
            "scope": {"from": [512, 512, 7], "to": [767, 767, 7]},
            "summary": {"findings": {"bySeverity": {"error": 0, "warning": 0, "info": 0}, "truncated": False}},
            "findings": [],
        },
    )
    _write_json(
        reachability,
        {
            "format": "canary-otbm-reachability-v1",
            "ok": True,
            "provenance": {"worldIndexManifest": {"source": {"sha256": source_sha256}}},
            "region": {"from": [512, 512, 7], "to": [767, 767, 7]},
            "summary": {"findings": {"bySeverity": {"error": 0, "warning": 0, "info": 0}, "truncated": False}},
            "findings": [],
        },
    )
    placements: list[dict[str, object]] = []
    unresolved_count = 0
    conflict_count = 0
    if unresolved:
        placements.append({"index": 0, "itemId": 200, "position": [556, 600, 7], "status": "unresolved"})
        unresolved_count = 1
    if conflicting:
        placements.append({"index": len(placements), "itemId": 201, "position": [557, 600, 7], "status": "conflicting"})
        conflict_count = 1
    _write_json(
        script_resolution,
        {
            "format": "canary-otbm-script-resolution-v1",
            "ok": not conflicting,
            "sources": {"itemAudit": {"map": {"sha256": source_sha256}}},
            "summary": {
                "conflictingPlacements": conflict_count,
                "runtimeUnresolvedPlacements": unresolved_count,
                "unreviewedIdentifiers": 0,
                "unresolvedDynamicRegistrations": 0,
            },
            "placements": placements,
        },
    )
    return geometry, reachability, script_resolution


class PipelineCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.otbm"
        self.plan = self.root / "plan.json"
        self.source.write_bytes(b"source-map-bytes")
        _write_json(self.plan, {"format": "canary-otbm-bounded-patch-plan-v1", "reviewed": True})

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _attribute_executor(self, candidate_bytes: bytes):
        source_sha = sha256_path(self.source)

        def execute(candidate: Path, evidence: Path) -> MutationExecution:
            candidate.write_bytes(candidate_bytes)
            report_path = evidence / "sandbox-verification.json"
            _write_json(
                report_path,
                {
                    "format": "canary-otbm-repair-sandbox-verification-v1",
                    "ok": True,
                    "source": {"sha256": source_sha, "unchanged": True},
                    "patchedOutput": {
                        "sha256": _sha256_bytes(candidate_bytes),
                        "size": len(candidate_bytes),
                    },
                    "summary": {
                        "operations": 1,
                        "runtimeResolutionChangedOperations": 0,
                        "runtimeRegressionOperations": 0,
                        "runtimeUnresolvedAfter": 0,
                        "runtimeConflictingAfter": 0,
                    },
                    "review": {"unresolvedEvidencePreserved": True},
                    "policy": {
                        "sourceModifiedInPlace": False,
                        "phase8BoundedPatcherReused": True,
                        "phase8WorldIndexProofReused": True,
                        "phase8SemanticDiffProofReused": True,
                    },
                },
            )
            return MutationExecution(candidate_path=candidate, report_path=report_path)

        return execute

    def test_attribute_pipeline_publishes_only_after_exact_quality_identity(self) -> None:
        candidate = b"verified-patched-map"
        geometry, reachability, script_resolution = _quality_components(self.root, _sha256_bytes(candidate))
        source_before = self.source.read_bytes()
        result = run_pipeline(
            mode=ATTRIBUTE_MODE,
            artifact_root=self.root,
            source_map=self.source,
            output_map=Path("final.otbm"),
            evidence_dir=Path("pipeline-evidence"),
            geometry_report=geometry,
            reachability_report=reachability,
            script_resolution_report=script_resolution,
            direct_inputs={"sourceMap": self.source, "plan": self.plan},
            mutation_executor=self._attribute_executor(candidate),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["mode"], ATTRIBUTE_MODE)
        self.assertEqual((self.root / "final.otbm").read_bytes(), candidate)
        self.assertEqual(self.source.read_bytes(), source_before)
        self.assertTrue(result["output"]["byteIdenticalToVerifiedCandidate"])
        self.assertEqual(result["quality"]["sourceSha256"], _sha256_bytes(candidate))
        self.assertTrue((self.root / "pipeline-evidence" / "pipeline-result.json").is_file())

    def test_quality_source_mismatch_keeps_final_output_unpublished(self) -> None:
        candidate = b"verified-patched-map"
        wrong_sha = "1" * 64
        geometry, reachability, script_resolution = _quality_components(self.root, wrong_sha)
        with self.assertRaisesRegex(
            RepairMaterializationPipelineError,
            "does not prove the exact materialized candidate",
        ):
            run_pipeline(
                mode=ATTRIBUTE_MODE,
                artifact_root=self.root,
                source_map=self.source,
                output_map=Path("final.otbm"),
                evidence_dir=Path("pipeline-evidence"),
                geometry_report=geometry,
                reachability_report=reachability,
                script_resolution_report=script_resolution,
                direct_inputs={"sourceMap": self.source, "plan": self.plan},
                mutation_executor=self._attribute_executor(candidate),
            )
        self.assertFalse((self.root / "final.otbm").exists())
        self.assertTrue((self.root / "pipeline-evidence" / "candidate.otbm").is_file())
        self.assertTrue((self.root / "pipeline-evidence" / "map-quality.json").is_file())
        self.assertFalse((self.root / "pipeline-evidence" / "pipeline-result.json").exists())

    def test_unresolved_quality_evidence_is_preserved_without_automatic_promotion(self) -> None:
        candidate = b"verified-patched-map"
        geometry, reachability, script_resolution = _quality_components(
            self.root,
            _sha256_bytes(candidate),
            unresolved=True,
        )
        result = run_pipeline(
            mode=ATTRIBUTE_MODE,
            artifact_root=self.root,
            source_map=self.source,
            output_map=Path("final.otbm"),
            evidence_dir=Path("pipeline-evidence"),
            geometry_report=geometry,
            reachability_report=reachability,
            script_resolution_report=script_resolution,
            direct_inputs={"sourceMap": self.source, "plan": self.plan},
            mutation_executor=self._attribute_executor(candidate),
            fail_on_unresolved=False,
        )
        self.assertEqual(result["quality"]["outcomeCounts"]["unresolved"], 1)
        self.assertTrue(result["safety"]["unresolvedEvidencePreserved"])

    def test_fail_on_unresolved_blocks_final_publication(self) -> None:
        candidate = b"verified-patched-map"
        geometry, reachability, script_resolution = _quality_components(
            self.root,
            _sha256_bytes(candidate),
            unresolved=True,
        )
        with self.assertRaisesRegex(RepairMaterializationPipelineError, "Map Quality Gate rejected"):
            run_pipeline(
                mode=ATTRIBUTE_MODE,
                artifact_root=self.root,
                source_map=self.source,
                output_map=Path("final.otbm"),
                evidence_dir=Path("pipeline-evidence"),
                geometry_report=geometry,
                reachability_report=reachability,
                script_resolution_report=script_resolution,
                direct_inputs={"sourceMap": self.source, "plan": self.plan},
                mutation_executor=self._attribute_executor(candidate),
                fail_on_unresolved=True,
            )
        self.assertFalse((self.root / "final.otbm").exists())

    def test_rejects_symlink_source_input(self) -> None:
        target = self.root / "real-source.otbm"
        target.write_bytes(b"source")
        symlink = self.root / "source-link.otbm"
        symlink.symlink_to(target)
        candidate = b"candidate"
        geometry, reachability, script_resolution = _quality_components(self.root, _sha256_bytes(candidate))
        with self.assertRaisesRegex(RepairMaterializationPipelineError, "sourceMap must not be a symlink"):
            run_pipeline(
                mode=ATTRIBUTE_MODE,
                artifact_root=self.root,
                source_map=symlink,
                output_map=Path("final.otbm"),
                evidence_dir=Path("pipeline-evidence"),
                geometry_report=geometry,
                reachability_report=reachability,
                script_resolution_report=script_resolution,
                direct_inputs={"sourceMap": symlink, "plan": self.plan},
                mutation_executor=self._attribute_executor(candidate),
            )


class TileAreaPipelineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = shutil.which("c++") or shutil.which("g++")
        if compiler is None:
            raise unittest.SkipTest("A C++ compiler is required")
        cls.compiler_temp = tempfile.TemporaryDirectory()
        cls.scanner = Path(cls.compiler_temp.name) / "otbm_area_materializer_scan"
        source = Path(__file__).with_name("otbm_area_materializer_scan.cpp")
        completed = subprocess.run(
            [
                compiler,
                "-O2",
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                str(source),
                "-o",
                str(cls.scanner),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.compiler_temp.cleanup()

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.current = self.root / "current.otbm"
        self.donor = self.root / "donor.otbm"
        self.current_index = self.root / "current.widx"
        self.current_manifest = self.root / "current.widx.json"
        self.donor_index = self.root / "donor.widx"
        self.donor_manifest = self.root / "donor.widx.json"
        self.plan_path = self.root / "plan.json"
        self.approval_path = self.root / "approval.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _prepare_reviewed_area_inputs(self) -> tuple[Path, Path, Path, Path]:
        make_area_map(
            self.current,
            [
                {
                    "baseX": 512,
                    "baseY": 512,
                    "z": 7,
                    "tiles": [{"x": 556, "y": 600, "ground": 100, "items": [{"id": 200, "action": 1000}]}],
                }
            ],
        )
        make_area_map(
            self.donor,
            [
                {
                    "baseX": 512,
                    "baseY": 512,
                    "z": 7,
                    "tiles": [{"x": 556, "y": 600, "ground": 100, "items": [{"id": 201, "action": 1001}]}],
                }
            ],
        )
        current_before = self.current.read_bytes()
        build_world_index(
            map_path=self.current,
            scanner=self.scanner,
            output=self.current_index,
            manifest_output=self.current_manifest,
        )
        build_world_index(
            map_path=self.donor,
            scanner=self.scanner,
            output=self.donor_index,
            manifest_output=self.donor_manifest,
        )
        plan = analyze_region_merge_plan(
            artifact_root=self.root,
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            donor_from=(512, 512, 7),
            donor_to=(767, 767, 7),
            target_origin=(512, 512, 7),
            policy="replace-region",
            sample_limit=10_000,
        )
        _write_json(self.plan_path, plan)
        approval = {
            "format": APPROVAL_FORMAT,
            "schemaVersion": 1,
            "decision": "approved",
            "rationale": "Synthetic pipeline integration approval for one complete same-coordinate TILE_AREA.",
            "plan": {
                "format": "canary-otbm-region-merge-plan-v1",
                "sha256": sha256_path(self.plan_path),
            },
            "approvedAreaKeys": [{"baseX": 512, "baseY": 512, "z": 7}],
            "approvedConflictIds": [entry["id"] for entry in plan["conflicts"]],
        }
        _write_json(self.approval_path, approval)
        materialize_area_plan(
            artifact_root=self.root,
            current_map_path=self.current,
            donor_map_path=self.donor,
            scanner_path=self.scanner,
            plan_path=Path(self.plan_path.name),
            approval_path=Path(self.approval_path.name),
            current_index_path=Path(self.current_index.name),
            current_manifest_path=Path(self.current_manifest.name),
            donor_index_path=Path(self.donor_index.name),
            donor_manifest_path=Path(self.donor_manifest.name),
            output_map_path=Path("review-candidate.otbm"),
            evidence_dir=Path("review-materialization"),
        )
        self.assertEqual(self.current.read_bytes(), current_before)
        review_candidate = self.root / "review-candidate.otbm"
        geometry, reachability, script_resolution = _quality_components(self.root, sha256_path(review_candidate))
        return review_candidate, geometry, reachability, script_resolution

    def test_real_tile_area_pipeline_replays_reviewed_materialization_and_publishes_exact_final_copy(self) -> None:
        review_candidate, geometry, reachability, script_resolution = self._prepare_reviewed_area_inputs()
        current_before = self.current.read_bytes()

        def execute(candidate: Path, evidence: Path) -> MutationExecution:
            return execute_area_mutation(
                artifact_root=self.root,
                current_map=self.current,
                donor_map=self.donor,
                scanner=self.scanner,
                plan=self.plan_path,
                approval=self.approval_path,
                current_index=self.current_index,
                current_manifest=self.current_manifest,
                donor_index=self.donor_index,
                donor_manifest=self.donor_manifest,
                candidate_path=candidate,
                pipeline_evidence_dir=evidence,
            )

        result = run_pipeline(
            mode=TILE_AREA_MODE,
            artifact_root=self.root,
            source_map=self.current,
            output_map=Path("final.otbm"),
            evidence_dir=Path("pipeline-evidence"),
            geometry_report=geometry,
            reachability_report=reachability,
            script_resolution_report=script_resolution,
            direct_inputs={
                "sourceMap": self.current,
                "donorMap": self.donor,
                "scanner": self.scanner,
                "plan": self.plan_path,
                "approval": self.approval_path,
                "currentWorldIndex": self.current_index,
                "currentWorldIndexManifest": self.current_manifest,
                "donorWorldIndex": self.donor_index,
                "donorWorldIndexManifest": self.donor_manifest,
            },
            mutation_executor=execute,
        )
        final = self.root / "final.otbm"
        self.assertEqual(final.read_bytes(), review_candidate.read_bytes())
        self.assertEqual(result["output"]["sha256"], sha256_path(review_candidate))
        self.assertEqual(result["mutation"]["format"], "canary-otbm-area-materialization-result-v1")
        self.assertEqual(result["mutation"]["summary"]["selection"]["translation"], [0, 0, 0])
        self.assertEqual(self.current.read_bytes(), current_before)
        self.assertTrue((self.root / "pipeline-evidence" / "area-materialization" / "semantic-diff.json").is_file())
        self.assertTrue((self.root / "pipeline-evidence" / "map-quality.json").is_file())
        self.assertTrue((self.root / "pipeline-evidence" / "pipeline-result.json").is_file())


if __name__ == "__main__":
    unittest.main()
