from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from otbm_geometry_audit_analysis import analyze_geometry
from otbm_geometry_audit_types import (
    DEFAULT_ORPHAN_MAX_TILES,
    DEFAULT_SAMPLE_LIMIT,
    GeometryAuditError,
    Position,
    resolve_artifact_path,
    write_json_atomic,
)

__all__ = [
    "GeometryAuditError",
    "analyze_index_paths",
    "write_report",
]


def analyze_index_paths(
    *,
    artifact_root: Path,
    index_path: Path,
    manifest_path: Path,
    appearances_path: Path,
    lower: Position,
    upper: Position,
    rules_path: Path | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    orphan_max_tiles: int = DEFAULT_ORPHAN_MAX_TILES,
) -> dict[str, Any]:
    return analyze_geometry(
        artifact_root=artifact_root,
        index_path=index_path,
        manifest_path=manifest_path,
        appearances_path=appearances_path,
        lower=lower,
        upper=upper,
        rules_path=rules_path,
        sample_limit=sample_limit,
        orphan_max_tiles=orphan_max_tiles,
    )


def write_report(
    report: Mapping[str, Any],
    *,
    artifact_root: Path,
    output_path: Path,
    overwrite: bool = False,
) -> Path:
    output = resolve_artifact_path(
        artifact_root,
        output_path,
        label="geometry audit output",
        require_file=False,
    )
    write_json_atomic(report, output, overwrite=overwrite)
    return output
