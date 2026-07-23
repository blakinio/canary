from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Iterable

MANIFEST_FORMAT = "canary-tibia-client-reference-manifest-v1"
SCHEMA_VERSION = 1
DEFAULT_MAX_FILE_BYTES = 8 * 1024 * 1024 * 1024
MAX_SELECTED_INPUTS = 128
BUILD_EVIDENCE_STATES = frozenset({"proven", "declared", "unknown", "conflicting"})
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_REVISION_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


class ClientReferenceManifestError(RuntimeError):
    pass


def _validate_id(value: str, label: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ClientReferenceManifestError(f"{label} must match {_ID_RE.pattern}")
    return value


def _validate_sha256(value: str, label: str) -> str:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        raise ClientReferenceManifestError(f"{label} must be a SHA-256 hex string")
    return value.lower()


def _validate_revision(value: str) -> str:
    if not isinstance(value, str) or not _REVISION_RE.fullmatch(value):
        raise ClientReferenceManifestError("parser revision must be an exact 40- or 64-character hexadecimal commit id")
    return value.lower()


def _validate_observed_at(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ClientReferenceManifestError("observedAt must be a non-empty timezone-aware ISO-8601 value")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ClientReferenceManifestError("observedAt must be a timezone-aware ISO-8601 value") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ClientReferenceManifestError("observedAt must include a timezone offset")
    return value


def _safe_relative_path(value: str, label: str) -> tuple[str, tuple[str, ...]]:
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise ClientReferenceManifestError(f"{label} must be a non-empty POSIX-style relative path")
    if PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute():
        raise ClientReferenceManifestError(f"{label} must be relative")
    parts = tuple(value.split("/"))
    if any(part in {"", ".", ".."} for part in parts):
        raise ClientReferenceManifestError(f"{label} must not contain empty, '.' or '..' segments")
    return PurePosixPath(*parts).as_posix(), parts


def _resolve_package_root(package_root: Path) -> Path:
    expanded = package_root.expanduser()
    lexical = Path(os.path.abspath(expanded))
    cursor = Path(lexical.anchor)
    for part in lexical.parts[1:]:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ClientReferenceManifestError(f"package root path contains a symlink: {package_root}")
    try:
        root = lexical.resolve(strict=True)
    except OSError as exc:
        raise ClientReferenceManifestError(f"package root does not exist: {package_root}") from exc
    if not root.is_dir():
        raise ClientReferenceManifestError(f"package root must be a directory: {package_root}")
    return root


def _resolve_selected_file(root: Path, relative_value: str, *, max_file_bytes: int) -> tuple[str, Path, int, str]:
    if not isinstance(max_file_bytes, int) or isinstance(max_file_bytes, bool) or max_file_bytes <= 0:
        raise ClientReferenceManifestError("max_file_bytes must be a positive integer")
    relative, parts = _safe_relative_path(relative_value, "selected input path")
    cursor = root
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ClientReferenceManifestError(f"selected input path contains a symlink: {relative}")
    try:
        source = cursor.resolve(strict=True)
        source.relative_to(root)
    except (OSError, ValueError) as exc:
        raise ClientReferenceManifestError(f"selected input escapes package root or is missing: {relative}") from exc
    if not source.is_file():
        raise ClientReferenceManifestError(f"selected input must be a regular file: {relative}")
    before = source.stat()
    if before.st_size > max_file_bytes:
        raise ClientReferenceManifestError(
            f"selected input exceeds max file size {max_file_bytes} bytes: {relative} ({before.st_size} bytes)"
        )
    digest = hashlib.sha256()
    try:
        with source.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if opened.st_size > max_file_bytes:
                raise ClientReferenceManifestError(
                    f"selected input exceeds max file size {max_file_bytes} bytes: {relative} ({opened.st_size} bytes)"
                )
            if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                raise ClientReferenceManifestError(f"selected input changed before hashing: {relative}")
            while chunk := stream.read(4 * 1024 * 1024):
                digest.update(chunk)
            after_open = os.fstat(stream.fileno())
    except OSError as exc:
        raise ClientReferenceManifestError(f"cannot hash selected input {relative}: {exc}") from exc
    after = source.stat()
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    opened_identity = (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
    after_open_identity = (after_open.st_dev, after_open.st_ino, after_open.st_size, after_open.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if len({before_identity, opened_identity, after_open_identity, after_identity}) != 1:
        raise ClientReferenceManifestError(f"selected input changed while hashing: {relative}")
    return relative, source, after.st_size, digest.hexdigest()


def _normalize_client_build(
    evidence: str,
    value: str | None,
    conflicting_values: Iterable[str] = (),
) -> dict[str, object]:
    if evidence not in BUILD_EVIDENCE_STATES:
        raise ClientReferenceManifestError(
            f"client build evidence must be one of {sorted(BUILD_EVIDENCE_STATES)}"
        )
    normalized_conflicts = sorted({item.strip() for item in conflicting_values if isinstance(item, str) and item.strip()})
    normalized_value = value.strip() if isinstance(value, str) and value.strip() else None
    if evidence in {"proven", "declared"}:
        if normalized_value is None:
            raise ClientReferenceManifestError(f"client build value is required when evidence is {evidence}")
        if normalized_conflicts:
            raise ClientReferenceManifestError("conflicting client build values are allowed only for conflicting evidence")
    elif evidence == "unknown":
        if normalized_value is not None or normalized_conflicts:
            raise ClientReferenceManifestError("unknown client build evidence must not carry a value or conflicts")
    else:
        if normalized_value is not None:
            raise ClientReferenceManifestError("conflicting client build evidence must not carry a single value")
        if len(normalized_conflicts) < 2:
            raise ClientReferenceManifestError("conflicting client build evidence requires at least two distinct values")
    return {"evidence": evidence, "value": normalized_value, "conflictingValues": normalized_conflicts}


def _normalize_key_values(entries: Iterable[tuple[str, str]], label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in entries:
        key = _validate_id(key, f"{label} id")
        if key in result:
            raise ClientReferenceManifestError(f"duplicate {label} id: {key}")
        if not isinstance(value, str) or not value:
            raise ClientReferenceManifestError(f"{label} value for {key} must be non-empty")
        result[key] = value
    return dict(sorted(result.items()))


def build_manifest(
    *,
    package_root: Path,
    reference_id: str,
    package_root_label: str,
    source_role: str,
    observed_at: str,
    client_build_evidence: str,
    client_build: str | None,
    client_build_conflicts: Iterable[str] = (),
    parser_revision: str,
    selected_inputs: Iterable[tuple[str, str]],
    generated_indexes: Iterable[tuple[str, str]] = (),
    package_metadata: Iterable[tuple[str, str]] = (),
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> tuple[dict[str, object], tuple[Path, ...]]:
    root = _resolve_package_root(package_root)
    reference_id = _validate_id(reference_id, "referenceId")
    source_role = _validate_id(source_role, "sourceRole")
    if not isinstance(package_root_label, str) or not package_root_label.strip():
        raise ClientReferenceManifestError("package root label must be non-empty")
    observed_at = _validate_observed_at(observed_at)
    parser_revision = _validate_revision(parser_revision)
    client_build_document = _normalize_client_build(
        client_build_evidence, client_build, client_build_conflicts
    )

    selected_specs = list(selected_inputs)
    if not 1 <= len(selected_specs) <= MAX_SELECTED_INPUTS:
        raise ClientReferenceManifestError(
            f"selected inputs must contain 1..{MAX_SELECTED_INPUTS} entries"
        )

    seen_ids: set[str] = set()
    seen_sources: set[Path] = set()
    inputs: list[dict[str, object]] = []
    selected_paths: list[Path] = []
    for input_id, relative_path in selected_specs:
        input_id = _validate_id(input_id, "selected input id")
        if input_id in seen_ids:
            raise ClientReferenceManifestError(f"duplicate selected input id: {input_id}")
        relative, source, size_bytes, sha256 = _resolve_selected_file(
            root, relative_path, max_file_bytes=max_file_bytes
        )
        if source in seen_sources or any(os.path.samefile(source, existing) for existing in seen_sources):
            raise ClientReferenceManifestError(f"selected input resolves to a duplicate file: {relative}")
        seen_ids.add(input_id)
        seen_sources.add(source)
        selected_paths.append(source)
        inputs.append(
            {
                "id": input_id,
                "path": relative,
                "sizeBytes": size_bytes,
                "sha256": sha256,
            }
        )
    inputs.sort(key=lambda item: item["id"])

    generated: list[dict[str, str]] = []
    generated_ids: set[str] = set()
    for index_id, sha256 in generated_indexes:
        index_id = _validate_id(index_id, "generated index id")
        if index_id in generated_ids:
            raise ClientReferenceManifestError(f"duplicate generated index id: {index_id}")
        generated_ids.add(index_id)
        generated.append({"id": index_id, "sha256": _validate_sha256(sha256, f"generated index {index_id} sha256")})
    generated.sort(key=lambda item: item["id"])

    metadata = _normalize_key_values(package_metadata, "package metadata")
    manifest: dict[str, object] = {
        "format": MANIFEST_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "referenceId": reference_id,
        "packageRootLabel": package_root_label.strip(),
        "sourceRole": source_role,
        "observedAt": observed_at,
        "clientBuild": client_build_document,
        "parserRevision": parser_revision,
        "selectedInputs": inputs,
        "generatedIndexes": generated,
        "packageMetadata": metadata,
        "summary": {
            "selectedInputCount": len(inputs),
            "selectedInputBytes": sum(int(item["sizeBytes"]) for item in inputs),
            "generatedIndexCount": len(generated),
        },
        "policy": {
            "explicitSelectionOnly": True,
            "recursiveDiscovery": False,
            "executesSelectedContent": False,
            "packageRootTrustedAsVersionProof": False,
            "maxSelectedFileBytes": max_file_bytes,
        },
    }
    return manifest, tuple(selected_paths)


def deterministic_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_manifest(
    output: Path,
    payload: dict[str, object],
    *,
    selected_paths: Iterable[Path],
    overwrite: bool = False,
) -> None:
    target_path = output.expanduser()
    if target_path.is_symlink():
        raise ClientReferenceManifestError(f"output must not be a symlink: {output}")
    target = target_path.resolve()
    selected = tuple(path.resolve() for path in selected_paths)
    if any(target == source or (target.exists() and os.path.samefile(target, source)) for source in selected):
        raise ClientReferenceManifestError("output collides with a selected input")
    if target.exists() and not target.is_file():
        raise ClientReferenceManifestError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise ClientReferenceManifestError(f"output already exists: {target}; pass --overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = deterministic_json(payload)
    if not overwrite:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        return
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
