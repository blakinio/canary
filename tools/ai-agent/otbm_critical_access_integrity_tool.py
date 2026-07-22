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

from otbm_critical_access_integrity import (
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    CriticalAccessIntegrityError,
    build_critical_access_report,
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
        raise CriticalAccessIntegrityError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise CriticalAccessIntegrityError(f"{label} must be an existing regular file")
    before = resolved.stat()
    if before.st_size > MAX_JSON_BYTES:
        raise CriticalAccessIntegrityError(f"{label} exceeds the {MAX_JSON_BYTES}-byte input limit")
    before_hash = _sha256(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CriticalAccessIntegrityError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("format") != expected_format:
        raise CriticalAccessIntegrityError(f"{label} must use format {expected_format}")
    after = resolved.stat()
    after_hash = _sha256(resolved)
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns or before_hash != after_hash:
        raise CriticalAccessIntegrityError(f"{label} changed while it was being read")
    return payload, {
        "fileName": resolved.name,
        "size": before.st_size,
        "sha256": before_hash,
        "format": expected_format,
    }, resolved


def _stable_world_index(path: Path) -> tuple[dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise CriticalAccessIntegrityError("World Index must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise CriticalAccessIntegrityError("World Index must be an existing regular file")
    before = resolved.stat()
    if before.st_size > MAX_WORLD_INDEX_BYTES:
        raise CriticalAccessIntegrityError(f"World Index exceeds the {MAX_WORLD_INDEX_BYTES}-byte input limit")
    before_hash = _sha256(resolved)
    with WorldIndex(resolved) as index:
        index.header_json()
    after = resolved.stat()
    after_hash = _sha256(resolved)
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns or before_hash != after_hash:
        raise CriticalAccessIntegrityError("World Index changed while it was being read")
    return {
        "fileName": resolved.name,
        "size": before.st_size,
        "sha256": before_hash,
        "format": WORLD_INDEX_FORMAT,
    }, resolved


def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise CriticalAccessIntegrityError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    if len(inputs) != len(set(inputs)):
        raise CriticalAccessIntegrityError("input files must be distinct")
    if resolved in inputs:
        raise CriticalAccessIntegrityError("output must not be one of the input files")
    if candidate.exists():
        if not candidate.is_file():
            raise CriticalAccessIntegrityError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise CriticalAccessIntegrityError("output must not be a hard link to an input file")
            except OSError as exc:
                raise CriticalAccessIntegrityError(f"cannot compare output with input file: {exc}") from exc
        if not overwrite:
            raise CriticalAccessIntegrityError(f"output already exists: {candidate}; pass --overwrite to replace it")
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
        raise CriticalAccessIntegrityError(f"output already exists: {path}; pass --overwrite to replace it") from exc
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
        description="Compose reviewed OTBM critical-access integrity evidence without rescanning or pathfinding."
    )
    parser.add_argument("--targets", type=_path, required=True, help=f"reviewed {MANIFEST_FORMAT} manifest")
    parser.add_argument("--world-index", type=_path, required=True, help=f"canonical {WORLD_INDEX_FORMAT} file")
    parser.add_argument("--landmarks", type=_path, required=True, help="reviewed canary-otbm-semantic-landmarks-v1 registry")
    parser.add_argument("--connectivity", type=_path, required=True, help="canary-otbm-connectivity-resilience-v1 report")
    parser.add_argument("--geometry", type=_path, required=True, help="canary-otbm-geometry-audit-v1 report")
    parser.add_argument("--spawn-validation", type=_path, required=True, help="canary-otbm-spawn-npc-validation-v1 report")
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT} report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        targets, targets_pin, targets_path = _stable_json(args.targets, "critical-access targets", MANIFEST_FORMAT)
        landmarks, landmarks_pin, landmarks_path = _stable_json(
            args.landmarks, "Semantic Landmark Registry", "canary-otbm-semantic-landmarks-v1"
        )
        connectivity, connectivity_pin, connectivity_path = _stable_json(
            args.connectivity, "Connectivity Resilience report", "canary-otbm-connectivity-resilience-v1"
        )
        geometry, geometry_pin, geometry_path = _stable_json(
            args.geometry, "Geometry Audit report", "canary-otbm-geometry-audit-v1"
        )
        spawn_validation, spawn_pin, spawn_path = _stable_json(
            args.spawn_validation, "Spawn/NPC validation report", "canary-otbm-spawn-npc-validation-v1"
        )
        world_index_pin, world_index_path = _stable_world_index(args.world_index)
        input_paths = [
            targets_path,
            world_index_path,
            landmarks_path,
            connectivity_path,
            geometry_path,
            spawn_path,
        ]
        output = _prepare_output(args.output, input_paths, args.overwrite)
        with WorldIndex(world_index_path) as index:
            report = build_critical_access_report(
                manifest=targets,
                landmark_registry=landmarks,
                connectivity_report=connectivity,
                geometry_report=geometry,
                spawn_validation_report=spawn_validation,
                world_index=index,
                actual_world_index_sha256=world_index_pin["sha256"],
                input_pins={
                    "targets": targets_pin,
                    "worldIndex": world_index_pin,
                    "semanticLandmarks": landmarks_pin,
                    "connectivityResilience": connectivity_pin,
                    "geometryAudit": geometry_pin,
                    "spawnNpcValidation": spawn_pin,
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
    except (FileNotFoundError, OSError, CriticalAccessIntegrityError, WorldIndexError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
