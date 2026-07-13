from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from otbm_reachability_analysis import analyze_world
from otbm_reachability_types import (
    APPEARANCES_FORMAT,
    DEFAULT_PATH_LIMIT,
    DEFAULT_SAMPLE_LIMIT,
    MAX_PATH_LIMIT,
    MAX_REGION_COORDINATES,
    MAX_SAMPLE_LIMIT,
    REPORT_FORMAT,
    SCHEMA_VERSION,
    TRANSITION_FORMAT,
    AppearanceSemantics,
    Position,
    ReachabilityError,
    _sha256,
    load_appearance_semantics,
    load_script_resolution,
    load_transition_manifest,
    normalize_bounds,
)


def _load_world_manifest(index_path: Path, manifest_path: Path | None, actual_hash: str) -> dict[str, Any] | None:
    candidate = manifest_path or index_path.with_suffix(index_path.suffix + ".json")
    if not candidate.is_file():
        return None
    try:
        document = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReachabilityError(f"Cannot read world-index manifest {candidate}: {exc}") from exc
    if not isinstance(document, dict) or document.get("format") != "canary-otbm-world-index-v1":
        raise ReachabilityError(f"Unsupported world-index manifest: {candidate}")
    expected = document.get("index", {}).get("sha256") if isinstance(document.get("index"), dict) else None
    if expected is not None and expected != actual_hash:
        raise ReachabilityError("World-index hash does not match its provenance manifest")
    return document


def analyze_index_path(
    *,
    index_path: Path,
    appearances_path: Path,
    lower: Position,
    upper: Position,
    routes: Sequence[tuple[Position, Position]],
    origins: Sequence[Position],
    transitions_path: Path | None = None,
    script_resolution_path: Path | None = None,
    world_manifest_path: Path | None = None,
    allow_diagonal: bool = False,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    path_limit: int = DEFAULT_PATH_LIMIT,
) -> dict[str, Any]:
    index_path = index_path.expanduser().resolve()
    if not index_path.is_file():
        raise FileNotFoundError(index_path)
    try:
        from otbm_world_index import WorldIndex
    except ImportError as exc:
        raise ReachabilityError("otbm_world_index.py is required") from exc
    appearances, appearances_provenance = load_appearance_semantics(appearances_path)
    transition_entries, transition_provenance = load_transition_manifest(transitions_path)
    script_resolution, script_provenance = load_script_resolution(script_resolution_path)
    index_hash = _sha256(index_path)
    world_manifest = _load_world_manifest(index_path, world_manifest_path, index_hash)
    provenance: dict[str, Any] = {
        "worldIndex": {
            "path": index_path.name,
            "size": index_path.stat().st_size,
            "sha256": index_hash,
            "format": "canary-otbm-world-index-v1",
        },
        "appearances": appearances_provenance,
        "transitionManifest": transition_provenance,
        "scriptResolution": script_provenance,
    }
    if world_manifest is not None:
        provenance["worldIndexManifest"] = {
            "source": world_manifest.get("source"),
            "index": world_manifest.get("index"),
        }
    with WorldIndex(index_path) as index:
        return analyze_world(
            index,
            appearances=appearances,
            lower=lower,
            upper=upper,
            routes=routes,
            origins=origins,
            transition_entries=transition_entries,
            script_resolution=script_resolution,
            allow_diagonal=allow_diagonal,
            sample_limit=sample_limit,
            path_limit=path_limit,
            provenance=provenance,
        )


def write_report(path: Path, report: Mapping[str, Any], *, overwrite: bool = False) -> None:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise ReachabilityError(f"Output must not be a symlink: {expanded}")
    destination = expanded.resolve()
    if destination.exists() and not destination.is_file():
        raise ReachabilityError(f"Output path exists but is not a regular file: {destination}")
    if destination.exists() and not overwrite:
        raise ReachabilityError(f"Output already exists: {destination}; pass overwrite=True")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
