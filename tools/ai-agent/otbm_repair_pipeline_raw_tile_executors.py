from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from otbm_tile_deletion_materializer import materialize_tile_deletions
from otbm_tile_insertion_materializer import materialize_tile_insertions
from otbm_tile_materializer import materialize_tile_replacements
from otbm_tile_type_conversion_materializer import materialize_tile_type_conversions


@dataclass(frozen=True)
class RawTileMutationExecution:
    candidate_path: Path
    report_path: Path


def _relative(root: Path, path: Path, label: str) -> Path:
    try:
        return path.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} is outside the artifact root") from exc


def _result(candidate: Path, root: Path, evidence: Path) -> RawTileMutationExecution:
    return RawTileMutationExecution(candidate_path=candidate, report_path=root / evidence / "materialization-result.json")


def execute_tile_replacement_mutation(
    *, artifact_root: Path, current_map: Path, donor_map: Path, scanner: Path,
    approval: Path, current_index: Path, current_manifest: Path,
    donor_index: Path, donor_manifest: Path, candidate_path: Path,
    pipeline_evidence_dir: Path, timeout_seconds: int = 3600,
) -> RawTileMutationExecution:
    root = artifact_root.resolve(strict=True)
    candidate = _relative(root, candidate_path, "tile replacement candidate")
    evidence = _relative(root, pipeline_evidence_dir / "tile-replacement-materialization", "tile replacement evidence")
    materialize_tile_replacements(
        artifact_root=root, current_map_path=current_map, donor_map_path=donor_map,
        scanner_path=scanner, approval_path=approval, current_index_path=current_index,
        current_manifest_path=current_manifest, donor_index_path=donor_index,
        donor_manifest_path=donor_manifest, output_map_path=candidate,
        evidence_dir=evidence, timeout_seconds=timeout_seconds,
    )
    return _result(candidate_path, root, evidence)


def execute_tile_insertion_mutation(
    *, artifact_root: Path, current_map: Path, donor_map: Path, scanner: Path,
    approval: Path, current_index: Path, current_manifest: Path,
    donor_index: Path, donor_manifest: Path, candidate_path: Path,
    pipeline_evidence_dir: Path, timeout_seconds: int = 3600,
) -> RawTileMutationExecution:
    root = artifact_root.resolve(strict=True)
    candidate = _relative(root, candidate_path, "tile insertion candidate")
    evidence = _relative(root, pipeline_evidence_dir / "tile-insertion-materialization", "tile insertion evidence")
    materialize_tile_insertions(
        artifact_root=root, current_map_path=current_map, donor_map_path=donor_map,
        scanner_path=scanner, approval_path=approval, current_index_path=current_index,
        current_manifest_path=current_manifest, donor_index_path=donor_index,
        donor_manifest_path=donor_manifest, output_map_path=candidate,
        evidence_dir=evidence, timeout_seconds=timeout_seconds,
    )
    return _result(candidate_path, root, evidence)


def execute_tile_deletion_mutation(
    *, artifact_root: Path, current_map: Path, scanner: Path, approval: Path,
    current_index: Path, current_manifest: Path, candidate_path: Path,
    pipeline_evidence_dir: Path, timeout_seconds: int = 3600,
) -> RawTileMutationExecution:
    root = artifact_root.resolve(strict=True)
    candidate = _relative(root, candidate_path, "tile deletion candidate")
    evidence = _relative(root, pipeline_evidence_dir / "tile-deletion-materialization", "tile deletion evidence")
    materialize_tile_deletions(
        artifact_root=root, current_map_path=current_map, scanner_path=scanner,
        approval_path=approval, current_index_path=current_index,
        current_manifest_path=current_manifest, output_map_path=candidate,
        evidence_dir=evidence, timeout_seconds=timeout_seconds,
    )
    return _result(candidate_path, root, evidence)


def execute_tile_type_conversion_mutation(
    *, artifact_root: Path, current_map: Path, donor_map: Path, scanner: Path,
    approval: Path, current_index: Path, current_manifest: Path,
    donor_index: Path, donor_manifest: Path, candidate_path: Path,
    pipeline_evidence_dir: Path, timeout_seconds: int = 3600,
) -> RawTileMutationExecution:
    root = artifact_root.resolve(strict=True)
    candidate = _relative(root, candidate_path, "tile type conversion candidate")
    evidence = _relative(root, pipeline_evidence_dir / "tile-type-conversion-materialization", "tile type conversion evidence")
    materialize_tile_type_conversions(
        artifact_root=root, current_map_path=current_map, donor_map_path=donor_map,
        scanner_path=scanner, approval_path=approval, current_index_path=current_index,
        current_manifest_path=current_manifest, donor_index_path=donor_index,
        donor_manifest_path=donor_manifest, output_map_path=candidate,
        evidence_dir=evidence, timeout_seconds=timeout_seconds,
    )
    return _result(candidate_path, root, evidence)
