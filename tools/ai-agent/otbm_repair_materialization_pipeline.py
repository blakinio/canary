from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from otbm_area_materializer import materialize_area_plan
from otbm_map_quality import MapQualityError, REPORT_FORMAT as MAP_QUALITY_FORMAT, build_quality_report
from otbm_repair_pipeline_raw_tile_contracts import RAW_TILE_MODES, validate_raw_tile_report

PIPELINE_FORMAT = "canary-otbm-repair-materialization-pipeline-v1"
SCHEMA_VERSION = 1
ATTRIBUTE_MODE = "fixed-width-attribute"
TILE_AREA_MODE = "tile-area"
SUPPORTED_MODES = {ATTRIBUTE_MODE, TILE_AREA_MODE, *RAW_TILE_MODES}
ATTRIBUTE_REPORT_FORMAT = "canary-otbm-repair-sandbox-verification-v1"
AREA_REPORT_FORMAT = "canary-otbm-area-materialization-result-v1"


class RepairMaterializationPipelineError(RuntimeError):
    """Raised when the repair/materialization pipeline cannot prove a safe final artifact."""


@dataclass(frozen=True)
class StableFile:
    path: Path
    size: int
    mtime_ns: int
    sha256: str

    def evidence(self, *, include_format: str | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {"fileName": self.path.name, "size": self.size, "sha256": self.sha256}
        if include_format is not None:
            result["format"] = include_format
        return result


@dataclass(frozen=True)
class MutationExecution:
    candidate_path: Path
    report_path: Path


MutationExecutor = Callable[[Path, Path], MutationExecution]


def _sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def observe_stable_file(path: Path, label: str, *, executable: bool = False) -> StableFile:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise RepairMaterializationPipelineError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise RepairMaterializationPipelineError(f"{label} must be an existing regular file")
    if executable and not os.access(resolved, os.X_OK):
        raise RepairMaterializationPipelineError(f"{label} must be executable")
    before = resolved.stat()
    digest = _sha256_file(resolved)
    after = resolved.stat()
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
        raise RepairMaterializationPipelineError(f"{label} changed while it was being pinned")
    return StableFile(resolved, before.st_size, before.st_mtime_ns, digest)


def assert_stable_file(observed: StableFile, label: str) -> None:
    current = observed.path.stat()
    if current.st_size != observed.size or current.st_mtime_ns != observed.mtime_ns or _sha256_file(observed.path) != observed.sha256:
        raise RepairMaterializationPipelineError(f"{label} changed during pipeline execution")


def _prepare_artifact_root(path: Path) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise RepairMaterializationPipelineError("artifact root must not be a symlink")
    candidate.mkdir(parents=True, exist_ok=True)
    resolved = candidate.resolve(strict=True)
    if not resolved.is_dir():
        raise RepairMaterializationPipelineError("artifact root must be a directory")
    return resolved


def _check_existing_ancestors(root: Path, path: Path, label: str) -> None:
    current = path.parent
    while True:
        if current.is_symlink():
            raise RepairMaterializationPipelineError(f"{label} must not traverse symlink parents")
        if current == root:
            return
        if root not in current.parents:
            raise RepairMaterializationPipelineError(f"{label} escapes the artifact root")
        current = current.parent


def _new_confined_path(root: Path, relative: Path, label: str) -> Path:
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise RepairMaterializationPipelineError(f"{label} must be a relative path below the artifact root")
    lexical = Path(os.path.abspath(root / relative))
    try:
        lexical.relative_to(root)
    except ValueError as exc:
        raise RepairMaterializationPipelineError(f"{label} escapes the artifact root") from exc
    if lexical.is_symlink():
        raise RepairMaterializationPipelineError(f"{label} must not be a symlink")
    _check_existing_ancestors(root, lexical, label)
    resolved = lexical.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RepairMaterializationPipelineError(f"{label} resolves outside the artifact root") from exc
    if resolved.exists() or resolved.is_symlink():
        raise RepairMaterializationPipelineError(f"{label} already exists: {relative}")
    return resolved


def _artifact_relative(root: Path, path: Path, label: str) -> Path:
    try:
        return path.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise RepairMaterializationPipelineError(f"{label} is outside the artifact root") from exc


def _load_json_from_observed(observed: StableFile, label: str) -> dict[str, Any]:
    try:
        value = json.loads(observed.path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RepairMaterializationPipelineError(f"cannot read {label}: {exc}") from exc
    assert_stable_file(observed, label)
    if not isinstance(value, dict):
        raise RepairMaterializationPipelineError(f"{label} must contain one JSON object")
    return value


def _write_json_create_new(path: Path, value: Mapping[str, Any]) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(path, flags, 0o600)
        created = True
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise RepairMaterializationPipelineError(f"output already exists: {path}") from exc
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            path.unlink(missing_ok=True)
        raise


def _publish_exact_copy(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(output, flags, 0o600)
        created = True
        with source.open("rb") as input_stream, os.fdopen(descriptor, "wb") as output_stream:
            descriptor = None
            shutil.copyfileobj(input_stream, output_stream, length=8 * 1024 * 1024)
            output_stream.flush()
            os.fsync(output_stream.fileno())
    except FileExistsError as exc:
        raise RepairMaterializationPipelineError(f"final output already exists: {output}") from exc
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            output.unlink(missing_ok=True)
        raise


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RepairMaterializationPipelineError(f"{label} must be an object")
    return value


def _validate_mutation_report(*, mode: str, report: Mapping[str, Any], source: StableFile, candidate: StableFile) -> dict[str, Any]:
    if mode in RAW_TILE_MODES:
        try:
            return validate_raw_tile_report(
                mode=mode,
                report=report,
                source_sha256=source.sha256,
                candidate_sha256=candidate.sha256,
                candidate_size=candidate.size,
            )
        except ValueError as exc:
            raise RepairMaterializationPipelineError(str(exc)) from exc

    if mode == ATTRIBUTE_MODE:
        if report.get("format") != ATTRIBUTE_REPORT_FORMAT or report.get("ok") is not True:
            raise RepairMaterializationPipelineError("attribute mutation did not produce a successful repair sandbox report")
        report_source = _require_mapping(report.get("source"), "sandbox source")
        patched = _require_mapping(report.get("patchedOutput"), "sandbox patchedOutput")
        if report_source.get("sha256") != source.sha256 or report_source.get("unchanged") is not True:
            raise RepairMaterializationPipelineError("repair sandbox report does not prove the expected source remained unchanged")
        if patched.get("sha256") != candidate.sha256 or patched.get("size") != candidate.size:
            raise RepairMaterializationPipelineError("repair sandbox output pin does not match the pipeline candidate")
        review = _require_mapping(report.get("review"), "sandbox review")
        policy = _require_mapping(report.get("policy"), "sandbox policy")
        if review.get("unresolvedEvidencePreserved") is not True:
            raise RepairMaterializationPipelineError("repair sandbox did not preserve unresolved runtime evidence")
        if policy.get("phase8BoundedPatcherReused") is not True or policy.get("phase8WorldIndexProofReused") is not True or policy.get("phase8SemanticDiffProofReused") is not True or policy.get("sourceModifiedInPlace") is not False:
            raise RepairMaterializationPipelineError("repair sandbox proof boundary is incomplete")
        return {"summary": dict(_require_mapping(report.get("summary"), "sandbox summary")), "runtimeEvidencePreserved": True}

    if mode == TILE_AREA_MODE:
        if report.get("format") != AREA_REPORT_FORMAT or report.get("ok") is not True:
            raise RepairMaterializationPipelineError("tile-area mutation did not produce a successful materialization report")
        if report.get("structuralVerificationComplete") is not True:
            raise RepairMaterializationPipelineError("tile-area structural verification is incomplete")
        report_source = _require_mapping(report.get("source"), "area materialization source")
        current = _require_mapping(report_source.get("current"), "area materialization current source")
        output = _require_mapping(report_source.get("output"), "area materialization output")
        if current.get("sha256") != source.sha256:
            raise RepairMaterializationPipelineError("area materialization report does not reference the expected current source")
        if output.get("sha256") != candidate.sha256 or output.get("size") != candidate.size:
            raise RepairMaterializationPipelineError("area materialization output pin does not match the pipeline candidate")
        verification = _require_mapping(report.get("verification"), "area materialization verification")
        required = ("nativeReparse", "worldIndexRebuilt", "selectedAreasEqualDonor", "nonSelectedCurrentBytesExact")
        missing = [name for name in required if verification.get(name) is not True]
        if missing:
            raise RepairMaterializationPipelineError("area materialization verification is incomplete: " + ", ".join(missing))
        safety = _require_mapping(report.get("safety"), "area materialization safety")
        if safety.get("sourceInPlaceWrite") is not False or safety.get("fullMapSerializer") is not False or safety.get("phase8Expanded") is not False or safety.get("separateApprovalRequired") is not True:
            raise RepairMaterializationPipelineError("area materialization safety boundary is incomplete")
        selection = _require_mapping(report.get("selection"), "area materialization selection")
        return {"selection": {"from": selection.get("from"), "to": selection.get("to"), "areaCount": selection.get("areaCount"), "translation": selection.get("translation")}, "structuralVerificationComplete": True}

    raise RepairMaterializationPipelineError(f"unsupported mutation mode: {mode}")


def execute_attribute_mutation(
    *, artifact_root: Path, source_map: Path, plan: Path, scanner: Path,
    appearances_index: Path, items_xml: Path, repository_root: Path,
    script_roots: Sequence[str], candidate_path: Path, pipeline_evidence_dir: Path,
    rules: Path | None = None, review_rules: Path | None = None, timeout_seconds: int = 3600,
) -> MutationExecution:
    if timeout_seconds <= 0:
        raise RepairMaterializationPipelineError("timeout_seconds must be positive")
    root = artifact_root.resolve(strict=True)
    candidate_relative = _artifact_relative(root, candidate_path, "attribute candidate")
    evidence_relative = _artifact_relative(root, pipeline_evidence_dir, "pipeline evidence directory")
    phase8_evidence = evidence_relative / "phase8-evidence"
    phase8_result = evidence_relative / "phase8-result.json"
    sandbox_report = evidence_relative / "sandbox-verification.json"
    command = [
        sys.executable, str(Path(__file__).with_name("otbm_repair_sandbox_tool.py")), str(source_map), str(plan),
        "--scanner", str(scanner), "--artifact-root", str(root), "--appearances-index", str(appearances_index),
        "--items-xml", str(items_xml), "--repository-root", str(repository_root), "--patched-output", str(candidate_relative),
        "--phase8-evidence", str(phase8_evidence), "--phase8-result", str(phase8_result), "--output", str(sandbox_report),
        "--timeout", str(timeout_seconds),
    ]
    for script_root in script_roots:
        command.extend(("--script-root", script_root))
    if rules is not None:
        command.extend(("--rules", str(rules)))
    if review_rules is not None:
        command.extend(("--review-rules", str(review_rules)))
    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, shell=False, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        raise RepairMaterializationPipelineError(f"repair sandbox execution timed out after {timeout_seconds} seconds") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise RepairMaterializationPipelineError(f"repair sandbox execution failed: {detail}")
    return MutationExecution(candidate_path, root / sandbox_report)


def execute_area_mutation(
    *, artifact_root: Path, current_map: Path, donor_map: Path, scanner: Path, plan: Path,
    approval: Path, current_index: Path, current_manifest: Path, donor_index: Path,
    donor_manifest: Path, candidate_path: Path, pipeline_evidence_dir: Path,
    timeout_seconds: int = 3600,
) -> MutationExecution:
    root = artifact_root.resolve(strict=True)
    candidate_relative = _artifact_relative(root, candidate_path, "tile-area candidate")
    evidence = _artifact_relative(root, pipeline_evidence_dir / "area-materialization", "area materialization evidence")
    materialize_area_plan(
        artifact_root=root, current_map_path=current_map, donor_map_path=donor_map, scanner_path=scanner,
        plan_path=plan, approval_path=approval, current_index_path=current_index, current_manifest_path=current_manifest,
        donor_index_path=donor_index, donor_manifest_path=donor_manifest, output_map_path=candidate_relative,
        evidence_dir=evidence, timeout_seconds=timeout_seconds,
    )
    return MutationExecution(candidate_path, root / evidence / "materialization-result.json")


def run_pipeline(
    *, mode: str, artifact_root: Path, source_map: Path, output_map: Path, evidence_dir: Path,
    geometry_report: Path, reachability_report: Path, script_resolution_report: Path,
    direct_inputs: Mapping[str, Path], mutation_executor: MutationExecutor,
    fail_on_severity: str = "error", fail_on_unresolved: bool = False, sample_limit: int = 500,
) -> dict[str, Any]:
    if mode not in SUPPORTED_MODES:
        raise RepairMaterializationPipelineError(f"unsupported mutation mode: {mode}")
    if fail_on_severity not in {"error", "warning"}:
        raise RepairMaterializationPipelineError("pipeline fail_on_severity must be error or warning")

    root = _prepare_artifact_root(artifact_root)
    final_output = _new_confined_path(root, output_map, "final output map")
    pipeline_evidence = _new_confined_path(root, evidence_dir, "pipeline evidence directory")
    if final_output == pipeline_evidence or pipeline_evidence in final_output.parents:
        raise RepairMaterializationPipelineError("final output map must be outside the pipeline evidence directory")

    all_inputs = dict(direct_inputs)
    all_inputs.update({"geometryReport": geometry_report, "reachabilityReport": reachability_report, "scriptResolutionReport": script_resolution_report})
    all_inputs.setdefault("sourceMap", source_map)
    observed_inputs = {name: observe_stable_file(path, name) for name, path in sorted(all_inputs.items())}
    source = observe_stable_file(source_map, "source map")
    if observed_inputs["sourceMap"].path != source.path:
        raise RepairMaterializationPipelineError("direct sourceMap input does not match the explicit source map")

    pipeline_evidence.mkdir(parents=True, exist_ok=False)
    candidate_path = pipeline_evidence / "candidate.otbm"
    execution = mutation_executor(candidate_path, pipeline_evidence)
    if execution.candidate_path.resolve(strict=True) != candidate_path.resolve(strict=True):
        raise RepairMaterializationPipelineError("mutation executor published an unexpected candidate path")
    candidate = observe_stable_file(candidate_path, "mutation candidate")
    mutation_report_file = observe_stable_file(execution.report_path, "mutation verification report")
    mutation_report = _load_json_from_observed(mutation_report_file, "mutation verification report")
    mutation_summary = _validate_mutation_report(mode=mode, report=mutation_report, source=source, candidate=candidate)

    assert_stable_file(source, "source map")
    for name, observed in observed_inputs.items():
        assert_stable_file(observed, name)

    component_specs = (("geometry", observed_inputs["geometryReport"]), ("reachability", observed_inputs["reachabilityReport"]), ("scriptResolution", observed_inputs["scriptResolutionReport"]))
    component_reports: dict[str, dict[str, Any]] = {}
    component_pins: dict[str, dict[str, Any]] = {}
    for component, observed in component_specs:
        document = _load_json_from_observed(observed, f"{component} report")
        report_format = document.get("format")
        if not isinstance(report_format, str) or not report_format:
            raise RepairMaterializationPipelineError(f"{component} report has no format")
        component_reports[component] = document
        component_pins[component] = observed.evidence(include_format=report_format)

    try:
        quality_report = build_quality_report(
            geometry=component_reports["geometry"], reachability=component_reports["reachability"],
            script_resolution=component_reports["scriptResolution"], input_pins=component_pins,
            sample_limit=sample_limit, fail_on_severity=fail_on_severity, fail_on_unresolved=fail_on_unresolved,
        )
    except MapQualityError as exc:
        raise RepairMaterializationPipelineError(f"Map Quality Gate input failed: {exc}") from exc

    quality_path = pipeline_evidence / "map-quality.json"
    _write_json_create_new(quality_path, quality_report)
    quality_file = observe_stable_file(quality_path, "Map Quality Gate report")
    if quality_report.get("format") != MAP_QUALITY_FORMAT:
        raise RepairMaterializationPipelineError("Map Quality Gate returned an unsupported report format")
    quality_source = _require_mapping(quality_report.get("source"), "Map Quality Gate source")
    if quality_source.get("sha256") != candidate.sha256:
        raise RepairMaterializationPipelineError("Map Quality Gate component evidence does not prove the exact materialized candidate SHA-256")
    if quality_report.get("ok") is not True:
        raise RepairMaterializationPipelineError("Map Quality Gate rejected the materialized candidate")

    assert_stable_file(source, "source map")
    assert_stable_file(candidate, "mutation candidate")
    for name, observed in observed_inputs.items():
        assert_stable_file(observed, name)

    published = False
    try:
        _publish_exact_copy(candidate.path, final_output)
        published = True
        final = observe_stable_file(final_output, "final output map")
        if final.sha256 != candidate.sha256 or final.size != candidate.size:
            raise RepairMaterializationPipelineError("final output bytes differ from the verified mutation candidate")
        assert_stable_file(source, "source map")
        for name, observed in observed_inputs.items():
            assert_stable_file(observed, name)

        mutation_report_pin = mutation_report_file.evidence(include_format=str(mutation_report.get("format")))
        mutation_report_pin["path"] = _artifact_relative(root, mutation_report_file.path, "mutation report").as_posix()
        quality_pin = quality_file.evidence(include_format=MAP_QUALITY_FORMAT)
        quality_pin["path"] = _artifact_relative(root, quality_file.path, "quality report").as_posix()
        input_evidence = {name: observed.evidence() for name, observed in sorted(observed_inputs.items())}
        quality_summary = _require_mapping(quality_report.get("summary"), "Map Quality Gate summary")
        quality_policy = _require_mapping(quality_report.get("policy"), "Map Quality Gate policy")
        quality_coverage = _require_mapping(quality_report.get("coverage"), "Map Quality Gate coverage")
        result = {
            "format": PIPELINE_FORMAT, "schemaVersion": SCHEMA_VERSION, "ok": True, "mode": mode,
            "source": {**source.evidence(), "unchanged": True},
            "output": {"path": _artifact_relative(root, final.path, "final output map").as_posix(), "size": final.size, "sha256": final.sha256, "createNew": True, "byteIdenticalToVerifiedCandidate": True},
            "inputs": input_evidence,
            "mutation": {"format": mutation_report.get("format"), "report": mutation_report_pin, "summary": mutation_summary},
            "quality": {"format": MAP_QUALITY_FORMAT, "report": quality_pin, "sourceSha256": candidate.sha256, "ok": True, "policy": dict(quality_policy), "outcomeCounts": dict(_require_mapping(quality_summary.get("outcomeCounts"), "quality outcome counts")), "coverage": dict(quality_coverage), "components": component_pins},
            "evidence": {"directory": _artifact_relative(root, pipeline_evidence, "pipeline evidence directory").as_posix(), "candidateRetained": True},
            "rollback": {"action": "delete-final-output", "path": _artifact_relative(root, final.path, "final output map").as_posix(), "sourceRetained": source.path.name, "sourceSha256": source.sha256},
            "safety": {"sourceModifiedInPlace": False, "silentOverwrite": False, "newOtbmParserCreated": False, "newOtbmWriterCreated": False, "existingMutationBoundaryReused": True, "existingMapQualityGateReused": True, "allDirectFileInputsPinned": True, "unresolvedEvidencePreserved": True, "gameplayCorrectnessProven": False, "physicalClientE2EProven": False, "productionMapExecutionAuthorized": False},
        }
        _write_json_create_new(pipeline_evidence / "pipeline-result.json", result)
        return result
    except Exception:
        if published:
            final_output.unlink(missing_ok=True)
        raise
