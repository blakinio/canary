from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from otbm_repair_materialization_pipeline import MutationExecution, RepairMaterializationPipelineError, run_pipeline
from otbm_repair_pipeline_raw_tile_contracts import (
    REPORT_FORMATS,
    SAFETY_TRUE_FIELDS,
    TILE_DELETION_MODE,
    TILE_INSERTION_MODE,
    TILE_REPLACEMENT_MODE,
    TILE_TYPE_CONVERSION_MODE,
    VERIFICATION_FIELDS,
)
from otbm_repair_materialization_pipeline_tool import build_parser
from test_otbm_repair_materialization_pipeline import _quality_components

RAW_MODES = (
    TILE_REPLACEMENT_MODE,
    TILE_INSERTION_MODE,
    TILE_DELETION_MODE,
    TILE_TYPE_CONVERSION_MODE,
)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class RawTilePipelineModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source.otbm"
        self.source.write_bytes(b"source-map")
        self.source_sha = _sha(self.source.read_bytes())

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _report(self, mode: str, candidate: bytes) -> dict[str, object]:
        safety = {
            "sourceInPlaceWrite": False,
            "fullMapSerializer": False,
            "arbitraryNodeSerialization": False,
        }
        safety.update({name: True for name in SAFETY_TRUE_FIELDS[mode]})
        return {
            "format": REPORT_FORMATS[mode],
            "schemaVersion": 1,
            "ok": True,
            "structuralVerificationComplete": True,
            "source": {
                "current": {"sha256": self.source_sha},
                "output": {"sha256": _sha(candidate), "size": len(candidate)},
            },
            "selection": {"positions": [[300, 600, 7]], "count": 1},
            "verification": {name: True for name in VERIFICATION_FIELDS[mode]},
            "safety": safety,
        }

    def _run(self, mode: str, report: dict[str, object], candidate: bytes) -> dict[str, object]:
        geometry, reachability, script_resolution = _quality_components(self.root, _sha(candidate))

        def executor(candidate_path: Path, evidence: Path) -> MutationExecution:
            candidate_path.write_bytes(candidate)
            report_path = evidence / "materialization-result.json"
            _write_json(report_path, report)
            return MutationExecution(candidate_path=candidate_path, report_path=report_path)

        return run_pipeline(
            mode=mode,
            artifact_root=self.root,
            source_map=self.source,
            output_map=Path("final.otbm"),
            evidence_dir=Path("pipeline-evidence"),
            geometry_report=geometry,
            reachability_report=reachability,
            script_resolution_report=script_resolution,
            direct_inputs={"sourceMap": self.source},
            mutation_executor=executor,
        )

    def test_all_raw_tile_modes_finalize_through_canonical_pipeline(self) -> None:
        for index, mode in enumerate(RAW_MODES):
            with self.subTest(mode=mode):
                case_root = self.root / f"case-{index}"
                case_root.mkdir()
                original_root = self.root
                original_source = self.source
                self.root = case_root
                self.source = case_root / "source.otbm"
                self.source.write_bytes(original_source.read_bytes())
                self.source_sha = _sha(self.source.read_bytes())
                candidate = f"candidate-{mode}".encode()
                result = self._run(mode, self._report(mode, candidate), candidate)
                self.assertTrue(result["ok"])
                self.assertEqual(result["mode"], mode)
                self.assertEqual(result["mutation"]["format"], REPORT_FORMATS[mode])
                self.assertTrue(result["mutation"]["summary"]["structuralVerificationComplete"])
                self.assertEqual((case_root / "final.otbm").read_bytes(), candidate)
                self.root = original_root
                self.source = original_source
                self.source_sha = _sha(original_source.read_bytes())

    def test_each_raw_tile_mode_fails_closed_when_required_verification_is_missing(self) -> None:
        for index, mode in enumerate(RAW_MODES):
            with self.subTest(mode=mode):
                case_root = self.root / f"reject-{index}"
                case_root.mkdir()
                original_root = self.root
                original_source = self.source
                self.root = case_root
                self.source = case_root / "source.otbm"
                self.source.write_bytes(original_source.read_bytes())
                self.source_sha = _sha(self.source.read_bytes())
                candidate = f"candidate-{mode}".encode()
                report = self._report(mode, candidate)
                report["verification"][VERIFICATION_FIELDS[mode][0]] = False  # type: ignore[index]
                with self.assertRaisesRegex(RepairMaterializationPipelineError, "verification is incomplete"):
                    self._run(mode, report, candidate)
                self.assertFalse((case_root / "final.otbm").exists())
                self.root = original_root
                self.source = original_source
                self.source_sha = _sha(original_source.read_bytes())

    def test_public_cli_registers_all_raw_tile_subcommands(self) -> None:
        choices = build_parser()._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
        for mode in RAW_MODES:
            self.assertIn(mode, choices)


if __name__ == "__main__":
    unittest.main()
