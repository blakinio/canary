#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from otbm_identifier_integrity import (
    POLICY_FORMAT,
    REPORT_FORMAT,
    IdentifierIntegrityError,
    build_identifier_integrity_report,
)
from otbm_world_index import WORLD_INDEX_FORMAT, WorldIndex, WorldIndexError

MAX_JSON_BYTES = 256 * 1024 * 1024
MAX_WORLD_INDEX_BYTES = 4 * 1024 * 1024 * 1024


def _path(value: str) -> Path:
    return Path(value)


def _sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_json(path: Path, label: str, expected_format: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise IdentifierIntegrityError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise IdentifierIntegrityError(f"{label} must be an existing regular file")
    before = resolved.stat()
    if before.st_size > MAX_JSON_BYTES:
        raise IdentifierIntegrityError(f"{label} exceeds the {MAX_JSON_BYTES}-byte input limit")
    before_hash = _sha256(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentifierIntegrityError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("format") != expected_format:
        raise IdentifierIntegrityError(f"{label} must use format {expected_format}")
    after = resolved.stat()
    after_hash = _sha256(resolved)
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns or before_hash != after_hash:
        raise IdentifierIntegrityError(f"{label} changed while it was being read")
    return payload, {
        "fileName": resolved.name,
        "size": before.st_size,
        "sha256": before_hash,
        "format": expected_format,
    }, resolved


def _stable_optional_json(
    path: Path | None, label: str, expected_format: str
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, Path | None]:
    if path is None:
        return None, None, None
    return _stable_json(path, label, expected_format)


def _stable_world_index(path: Path) -> tuple[dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise IdentifierIntegrityError("World Index must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise IdentifierIntegrityError("World Index must be an existing regular file")
    before = resolved.stat()
    if before.st_size > MAX_WORLD_INDEX_BYTES:
        raise IdentifierIntegrityError(f"World Index exceeds the {MAX_WORLD_INDEX_BYTES}-byte input limit")
    before_hash = _sha256(resolved)
    with WorldIndex(resolved) as index:
        index.header_json()
    after = resolved.stat()
    after_hash = _sha256(resolved)
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns or before_hash != after_hash:
        raise IdentifierIntegrityError("World Index changed while it was being read")
    return {
        "fileName": resolved.name,
        "size": before.st_size,
        "sha256": before_hash,
        "format": WORLD_INDEX_FORMAT,
    }, resolved


def _world_manifest_source_and_index(document: dict[str, Any]) -> tuple[str, str]:
    source = document.get("source")
    index = document.get("index")
    if not isinstance(source, dict) or not isinstance(index, dict):
        raise IdentifierIntegrityError("World Index manifest must contain source and index provenance objects")
    source_hash = source.get("sha256")
    index_hash = index.get("sha256")
    if not isinstance(source_hash, str) or len(source_hash) != 64:
        raise IdentifierIntegrityError("World Index manifest has no exact source-map SHA-256")
    if not isinstance(index_hash, str) or len(index_hash) != 64:
        raise IdentifierIntegrityError("World Index manifest has no exact index SHA-256")
    return source_hash, index_hash


def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise IdentifierIntegrityError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    if len(inputs) != len(set(inputs)):
        raise IdentifierIntegrityError("input files must be distinct")
    if resolved in inputs:
        raise IdentifierIntegrityError("output must not be one of the input files")
    if candidate.exists():
        if not candidate.is_file():
            raise IdentifierIntegrityError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise IdentifierIntegrityError("output must not be a hard link to an input file")
            except OSError as exc:
                raise IdentifierIntegrityError(f"cannot compare output with input file: {exc}") from exc
        if not overwrite:
            raise IdentifierIntegrityError(f"output already exists: {candidate}; pass --overwrite to replace it")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def _encoded_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_create_new(path: Path, value: Any) -> None:
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
            stream.write(_encoded_json(value))
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise IdentifierIntegrityError(f"output already exists: {path}; pass --overwrite to replace it") from exc
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            path.unlink(missing_ok=True)
        raise


def _write_overwrite_atomic(path: Path, value: Any) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(_encoded_json(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _write_json(path: Path, value: Any, *, overwrite: bool) -> None:
    if overwrite:
        _write_overwrite_atomic(path, value)
    else:
        _write_create_new(path, value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compose OTBM identifier/selector integrity evidence without rescanning, resolving scripts or pathfinding."
    )
    parser.add_argument("--policy", type=_path, required=True, help=f"reviewed {POLICY_FORMAT} policy")
    parser.add_argument("--world-index", type=_path, required=True, help=f"canonical {WORLD_INDEX_FORMAT} file")
    parser.add_argument(
        "--world-index-manifest",
        type=_path,
        required=True,
        help=f"{WORLD_INDEX_FORMAT} provenance manifest with exact source/index SHA-256",
    )
    parser.add_argument("--script-resolution", type=_path, help="optional canary-otbm-script-resolution-v1 report")
    parser.add_argument("--transitions", type=_path, help="optional canary-otbm-transition-manifest-v1 document")
    parser.add_argument("--interactions", type=_path, help="optional reviewed canary-otbm-route-interactions-v1 registry")
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT} report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        policy, policy_pin, policy_path = _stable_json(args.policy, "identifier-integrity policy", POLICY_FORMAT)
        world_manifest, world_manifest_pin, world_manifest_path = _stable_json(
            args.world_index_manifest, "World Index manifest", WORLD_INDEX_FORMAT
        )
        world_index_pin, world_index_path = _stable_world_index(args.world_index)
        source_map_sha, manifest_index_sha = _world_manifest_source_and_index(world_manifest)
        if manifest_index_sha != world_index_pin["sha256"]:
            raise IdentifierIntegrityError("World Index file SHA-256 does not match its provenance manifest")

        script_resolution, script_pin, script_path = _stable_optional_json(
            args.script_resolution, "Script Resolution report", "canary-otbm-script-resolution-v1"
        )
        transitions, transition_pin, transition_path = _stable_optional_json(
            args.transitions, "transition manifest", "canary-otbm-transition-manifest-v1"
        )
        interactions, interaction_pin, interaction_path = _stable_optional_json(
            args.interactions, "Route Interaction Registry", "canary-otbm-route-interactions-v1"
        )
        input_paths = [policy_path, world_index_path, world_manifest_path]
        input_paths.extend(path for path in (script_path, transition_path, interaction_path) if path is not None)
        output = _prepare_output(args.output, input_paths, args.overwrite)

        with WorldIndex(world_index_path) as index:
            report = build_identifier_integrity_report(
                policy=policy,
                world_index=index,
                source_map_sha256=source_map_sha,
                actual_world_index_sha256=world_index_pin["sha256"],
                script_resolution=script_resolution,
                script_resolution_sha256=script_pin["sha256"] if script_pin is not None else None,
                transition_manifest=transitions,
                transition_manifest_sha256=transition_pin["sha256"] if transition_pin is not None else None,
                interaction_registry=interactions,
                interaction_registry_sha256=interaction_pin["sha256"] if interaction_pin is not None else None,
                input_pins={
                    "policy": policy_pin,
                    "worldIndex": world_index_pin,
                    "worldIndexManifest": world_manifest_pin,
                    "scriptResolution": script_pin,
                    "transitionManifest": transition_pin,
                    "interactionRegistry": interaction_pin,
                },
            )
        _write_json(output, report, overwrite=args.overwrite)
        json.dump(
            {
                "format": report["format"],
                "ok": report["ok"],
                "source": report["source"],
                "summary": report["summary"],
                "output": str(output),
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0
    except (FileNotFoundError, OSError, IdentifierIntegrityError, WorldIndexError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
