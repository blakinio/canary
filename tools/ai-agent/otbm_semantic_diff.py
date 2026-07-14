from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from otbm_reachability_types import APPEARANCES_FORMAT, load_appearance_semantics
from otbm_world_index import WORLD_BUILD_FORMAT, WORLD_INDEX_FORMAT, SCHEMA_VERSION as WORLD_INDEX_SCHEMA_VERSION, WorldIndex

from otbm_semantic_diff_analysis import compare_worlds
from otbm_semantic_diff_types import (
    DEFAULT_SAMPLE_LIMIT,
    MAX_INDEX_BYTES,
    MAX_OUTPUT_BYTES,
    MAX_REPORT_INPUT_BYTES,
    REPORT_FORMAT,
    SCHEMA_VERSION,
    IndexProvenance,
    Position,
    SemanticDiffError,
    normalize_bounds,
    sha256_path,
)

ALLOWED_CORRELATION_FORMATS = {
    "quest-validation": {"canary-quest-map-validation-v1"},
    "script-resolution": {"canary-otbm-script-resolution-v1"},
    "reachability": {"canary-otbm-reachability-v1"},
    "spawn-npc": {
        "canary-otbm-spawn-npc-evidence-v1",
        "canary-otbm-spawn-npc-validation-v1",
    },
    "storage-graph": {"canary-otbm-storage-graph-v1"},
}


def _resolve_confined(root: Path, path: Path, label: str, *, must_exist: bool = True) -> Path:
    root = root.expanduser().resolve()
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise SemanticDiffError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=must_exist)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SemanticDiffError(f"{label} escapes artifact root {root}: {resolved}") from exc
    return resolved


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _require_regular(path: Path, label: str, maximum: int) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    size = path.stat().st_size
    if size > maximum:
        raise SemanticDiffError(f"{label} is {size} bytes; maximum is {maximum}")


def _load_json(path: Path, label: str, *, maximum: int = MAX_REPORT_INPUT_BYTES) -> dict[str, Any]:
    _require_regular(path, label, maximum)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SemanticDiffError(f"Cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SemanticDiffError(f"{label} must be a JSON object")
    return value


def _manifest_value(document: Mapping[str, Any], key: str, label: str) -> Mapping[str, Any]:
    value = document.get(key)
    if not isinstance(value, dict):
        raise SemanticDiffError(f"World Index manifest {label} must contain object {key}")
    return value


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise SemanticDiffError(f"{label} must be a lowercase SHA-256 hex digest")
    return value


def _validate_manifest(
    *,
    role: str,
    root: Path,
    index_path: Path,
    manifest_path: Path,
    index: WorldIndex,
) -> tuple[IndexProvenance, dict[str, Any]]:
    manifest = _load_json(manifest_path, f"{role} World Index manifest")
    if manifest.get("format") != WORLD_INDEX_FORMAT:
        raise SemanticDiffError(f"Unsupported {role} World Index manifest format: {manifest.get('format')!r}")
    if manifest.get("schemaVersion") != WORLD_INDEX_SCHEMA_VERSION:
        raise SemanticDiffError(f"Unsupported {role} World Index manifest schemaVersion: {manifest.get('schemaVersion')!r}")
    source = _manifest_value(manifest, "source", role)
    scanner = _manifest_value(manifest, "scanner", role)
    indexed = _manifest_value(manifest, "index", role)
    otbm = _manifest_value(manifest, "otbm", role)
    summary = _manifest_value(manifest, "summary", role)

    actual_size = index_path.stat().st_size
    actual_hash = sha256_path(index_path)
    expected_hash = _require_sha256(indexed.get("sha256"), f"{role} index.sha256")
    if expected_hash != actual_hash:
        raise SemanticDiffError(f"{role} World Index hash does not match its provenance manifest")
    if indexed.get("size") != actual_size or indexed.get("fileSize") != actual_size:
        raise SemanticDiffError(f"{role} World Index size does not match its provenance manifest")
    source_size = source.get("size")
    if source_size != index.header.source_map_size:
        raise SemanticDiffError(f"{role} source map size does not match the World Index header")
    source_hash = _require_sha256(source.get("sha256"), f"{role} source.sha256")
    scanner_hash = _require_sha256(scanner.get("sha256"), f"{role} scanner.sha256")
    if scanner.get("buildFormat") != WORLD_BUILD_FORMAT:
        raise SemanticDiffError(f"Unsupported {role} scanner build format: {scanner.get('buildFormat')!r}")

    header_json = index.header_json()
    if dict(otbm) != header_json["otbm"]:
        raise SemanticDiffError(f"{role} OTBM header provenance does not match the World Index")
    if dict(summary) != header_json["summary"]:
        raise SemanticDiffError(f"{role} logical summary does not match the World Index")
    binary = header_json["binary"]
    for key, value in binary.items():
        if indexed.get(key) != value:
            raise SemanticDiffError(f"{role} index.{key} does not match the World Index header")

    provenance = IndexProvenance(
        role=role,
        index_path=_relative(root, index_path),
        index_size=actual_size,
        index_sha256=actual_hash,
        format=WORLD_INDEX_FORMAT,
        schema_version=WORLD_INDEX_SCHEMA_VERSION,
        source_path=str(source.get("path", "")),
        source_size=int(source_size),
        source_sha256=source_hash,
        scanner_path=str(scanner.get("path", "")),
        scanner_sha256=scanner_hash,
        scanner_build_format=str(scanner.get("buildFormat")),
        otbm=dict(otbm),
        summary=dict(summary),
    )
    manifest_provenance = {
        "path": _relative(root, manifest_path),
        "size": manifest_path.stat().st_size,
        "sha256": sha256_path(manifest_path),
        "format": WORLD_INDEX_FORMAT,
    }
    return provenance, manifest_provenance


def _validate_pair(before: IndexProvenance, after: IndexProvenance) -> dict[str, Any]:
    incompatible: list[str] = []
    for key in ("version", "itemsMajor", "itemsMinor"):
        if before.otbm.get(key) != after.otbm.get(key):
            incompatible.append(key)
    if before.format != after.format or before.schema_version != after.schema_version:
        incompatible.append("worldIndexFormat")
    if before.scanner_build_format != after.scanner_build_format:
        incompatible.append("scannerBuildFormat")
    if incompatible:
        raise SemanticDiffError(f"World Index inputs are semantically incompatible: {sorted(set(incompatible))}")
    if (
        before.source_sha256 == after.source_sha256
        and before.scanner_sha256 == after.scanner_sha256
        and before.index_sha256 != after.index_sha256
    ):
        raise SemanticDiffError("The same source map and scanner produced different World Index bytes")
    return {
        "compatible": True,
        "worldIndexFormatEqual": before.format == after.format,
        "worldIndexSchemaVersionEqual": before.schema_version == after.schema_version,
        "scannerBuildFormatEqual": before.scanner_build_format == after.scanner_build_format,
        "scannerBinaryEqual": before.scanner_sha256 == after.scanner_sha256,
        "otbmVersionEqual": before.otbm.get("version") == after.otbm.get("version"),
        "itemsVersionEqual": (
            before.otbm.get("itemsMajor"),
            before.otbm.get("itemsMinor"),
        )
        == (
            after.otbm.get("itemsMajor"),
            after.otbm.get("itemsMinor"),
        ),
        "sourceMapEqual": before.source_sha256 == after.source_sha256,
        "worldIndexEqual": before.index_sha256 == after.index_sha256,
    }


def _load_optional_reports(root: Path, paths: Mapping[str, Path | None]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    documents: dict[str, dict[str, Any]] = {}
    provenance: list[dict[str, Any]] = []
    for role, path in sorted(paths.items()):
        if path is None:
            continue
        source = _resolve_confined(root, path, f"{role} report")
        document = _load_json(source, f"{role} report")
        allowed = ALLOWED_CORRELATION_FORMATS[role]
        if document.get("format") not in allowed:
            raise SemanticDiffError(
                f"Unsupported {role} report format {document.get('format')!r}; expected one of {sorted(allowed)}"
            )
        documents[role] = document
        provenance.append(
            {
                "role": role,
                "path": _relative(root, source),
                "size": source.stat().st_size,
                "sha256": sha256_path(source),
                "format": document["format"],
            }
        )
    return documents, provenance


def _verify_source_map(root: Path, path: Path | None, provenance: IndexProvenance, role: str) -> dict[str, Any] | None:
    if path is None:
        return None
    source = _resolve_confined(root, path, f"{role} source map")
    _require_regular(source, f"{role} source map", 16 * 1024 * 1024 * 1024)
    before_stat = source.stat()
    digest = sha256_path(source)
    after_stat = source.stat()
    if before_stat.st_size != after_stat.st_size or before_stat.st_mtime_ns != after_stat.st_mtime_ns:
        raise SemanticDiffError(f"{role} source map changed while its hash was being verified")
    if digest != provenance.source_sha256 or before_stat.st_size != provenance.source_size:
        raise SemanticDiffError(f"{role} source map does not match World Index provenance")
    return {
        "path": _relative(root, source),
        "size": before_stat.st_size,
        "sha256": digest,
        "verifiedUnchangedDuringRead": True,
    }


def analyze_index_paths(
    *,
    artifact_root: Path,
    before_index_path: Path,
    before_manifest_path: Path,
    after_index_path: Path,
    after_manifest_path: Path,
    appearances_path: Path | None = None,
    before_map_path: Path | None = None,
    after_map_path: Path | None = None,
    lower: Position | None = None,
    upper: Position | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    quest_validation_path: Path | None = None,
    script_resolution_path: Path | None = None,
    reachability_path: Path | None = None,
    spawn_npc_path: Path | None = None,
    storage_graph_path: Path | None = None,
) -> dict[str, Any]:
    root = artifact_root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    before_index_source = _resolve_confined(root, before_index_path, "before World Index")
    after_index_source = _resolve_confined(root, after_index_path, "after World Index")
    before_manifest_source = _resolve_confined(root, before_manifest_path, "before World Index manifest")
    after_manifest_source = _resolve_confined(root, after_manifest_path, "after World Index manifest")
    _require_regular(before_index_source, "before World Index", MAX_INDEX_BYTES)
    _require_regular(after_index_source, "after World Index", MAX_INDEX_BYTES)

    if (lower is None) != (upper is None):
        raise SemanticDiffError("A bounded comparison requires both lower and upper positions")
    bounds = normalize_bounds(lower, upper) if lower is not None and upper is not None else None

    appearances = None
    appearances_provenance = None
    if appearances_path is not None:
        appearance_source = _resolve_confined(root, appearances_path, "appearances evidence")
        appearances, raw_provenance = load_appearance_semantics(appearance_source)
        appearances_provenance = {
            **raw_provenance,
            "path": _relative(root, appearance_source),
        }

    documents, report_provenance = _load_optional_reports(
        root,
        {
            "quest-validation": quest_validation_path,
            "script-resolution": script_resolution_path,
            "reachability": reachability_path,
            "spawn-npc": spawn_npc_path,
            "storage-graph": storage_graph_path,
        },
    )

    with WorldIndex(before_index_source) as before_index, WorldIndex(after_index_source) as after_index:
        before_provenance, before_manifest_provenance = _validate_manifest(
            role="before",
            root=root,
            index_path=before_index_source,
            manifest_path=before_manifest_source,
            index=before_index,
        )
        after_provenance, after_manifest_provenance = _validate_manifest(
            role="after",
            root=root,
            index_path=after_index_source,
            manifest_path=after_manifest_source,
            index=after_index,
        )
        compatibility = _validate_pair(before_provenance, after_provenance)
        verified_before_map = _verify_source_map(root, before_map_path, before_provenance, "before")
        verified_after_map = _verify_source_map(root, after_map_path, after_provenance, "after")
        analysis = compare_worlds(
            before_index,
            after_index,
            appearances=appearances,
            bounds=bounds,
            sample_limit=sample_limit,
            correlation_documents=documents,
        )

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": True,
        "provenance": {
            "before": {
                **before_provenance.to_json(),
                "manifest": before_manifest_provenance,
                "verifiedSourceMap": verified_before_map,
            },
            "after": {
                **after_provenance.to_json(),
                "manifest": after_manifest_provenance,
                "verifiedSourceMap": verified_after_map,
            },
            "appearances": appearances_provenance,
            "correlationReports": report_provenance,
        },
        "compatibility": compatibility,
        "policy": {
            "dynamicLuaExecuted": False,
            "mapModified": False,
            "worldIndexReused": True,
            "nativeScannerReused": True,
            "walkabilityImplementation": "Phase 3 otbm_reachability_transition._classify_tile",
            "newParserCreated": False,
            "newPathfinderCreated": False,
            "newRendererCreated": False,
            "heuristicItemMatching": False,
            "itemAlignment": "deterministic-minimum-edit-over-exact-item-base; pure exact-multiset reorder is separate",
            "sampleLimit": sample_limit,
            "exactCountsPreserved": True,
            "correlationIsSelectedScopeOnly": True,
            "missingCorrelationMeansGloballyUnused": False,
        },
        **analysis,
    }


def write_report(path: Path, report: Mapping[str, Any], *, artifact_root: Path, overwrite: bool = False) -> None:
    root = artifact_root.expanduser().resolve()
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise SemanticDiffError(f"Output must not be a symlink: {candidate}")
    destination = candidate.resolve(strict=False)
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise SemanticDiffError(f"Output escapes artifact root {root}: {destination}") from exc
    if destination.exists() and not destination.is_file():
        raise SemanticDiffError(f"Output path exists but is not a regular file: {destination}")
    if destination.exists() and not overwrite:
        raise SemanticDiffError(f"Output already exists: {destination}; pass overwrite=True")
    encoded = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(encoded) > MAX_OUTPUT_BYTES:
        raise SemanticDiffError(f"Serialized report is {len(encoded)} bytes; maximum is {MAX_OUTPUT_BYTES}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.parent.is_symlink():
        raise SemanticDiffError(f"Output parent must not be a symlink: {destination.parent}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
