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

from otbm_connectivity_resilience import (
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    ConnectivityResilienceError,
    build_connectivity_resilience_report,
    prepare_connectivity_context,
)
from otbm_reachability_types import APPEARANCES_FORMAT, TRANSITION_FORMAT, ReachabilityError
from otbm_route_interactions import REGISTRY_FORMAT as INTERACTION_REGISTRY_FORMAT

MAX_JSON_BYTES = 256 * 1024 * 1024


def _path(value: str) -> Path:
    return Path(value)


def _sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_json(path: Path, label: str, expected_format: str | None = None) -> tuple[dict[str, Any], dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise ConnectivityResilienceError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise ConnectivityResilienceError(f"{label} must be an existing regular file")
    before = resolved.stat()
    if before.st_size > MAX_JSON_BYTES:
        raise ConnectivityResilienceError(f"{label} exceeds the {MAX_JSON_BYTES}-byte input limit")
    digest_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConnectivityResilienceError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConnectivityResilienceError(f"{label} must contain one JSON object")
    if expected_format is not None and payload.get("format") != expected_format:
        raise ConnectivityResilienceError(f"{label} must use format {expected_format}")
    after = resolved.stat()
    digest_after = _sha256_file(resolved)
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns or digest_before != digest_after:
        raise ConnectivityResilienceError(f"{label} changed while it was being read")
    pin = {
        "fileName": resolved.name,
        "size": before.st_size,
        "sha256": digest_before,
        "format": payload.get("format"),
    }
    return payload, pin, resolved


def _stable_file_pin(path: Path, label: str, fmt: str) -> tuple[dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise ConnectivityResilienceError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise ConnectivityResilienceError(f"{label} must be an existing regular file")
    before = resolved.stat()
    digest_before = _sha256_file(resolved)
    after = resolved.stat()
    digest_after = _sha256_file(resolved)
    if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns or digest_before != digest_after:
        raise ConnectivityResilienceError(f"{label} changed while it was being read")
    return {
        "fileName": resolved.name,
        "size": before.st_size,
        "sha256": digest_before,
        "format": fmt,
    }, resolved


def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise ConnectivityResilienceError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    if len(inputs) != len(set(inputs)):
        raise ConnectivityResilienceError("input files must be distinct")
    for source in inputs:
        if resolved == source:
            raise ConnectivityResilienceError("output must not be one of the input files")
    if candidate.exists():
        if not candidate.is_file():
            raise ConnectivityResilienceError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise ConnectivityResilienceError("output must not be a hard link to an input file")
            except OSError as exc:
                raise ConnectivityResilienceError(f"cannot compare output with input file: {exc}") from exc
        if not overwrite:
            raise ConnectivityResilienceError(f"output already exists: {candidate}; pass --overwrite to replace it")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def _encoded_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_json_create_new(path: Path, value: Any) -> None:
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
        raise ConnectivityResilienceError(f"output already exists: {path}; pass --overwrite to replace it") from exc
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            path.unlink(missing_ok=True)
        raise


def _write_json_overwrite_atomic(path: Path, value: Any) -> None:
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
        _write_json_overwrite_atomic(path, value)
    else:
        _write_json_create_new(path, value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze reviewed OTBM connectivity resilience by reusing the canonical Reachability graph/BFS."
    )
    parser.add_argument("--manifest", type=_path, required=True, help=f"required {MANIFEST_FORMAT} manifest")
    parser.add_argument("--world-index", type=_path, required=True, help="canonical canary-otbm-world-index-v1 file")
    parser.add_argument("--world-manifest", type=_path, help="optional World Index manifest sidecar")
    parser.add_argument("--appearances", type=_path, required=True, help=f"{APPEARANCES_FORMAT} JSON or supported binary catalogue")
    parser.add_argument("--transitions", type=_path, help=f"optional {TRANSITION_FORMAT} reviewed transition manifest")
    parser.add_argument("--script-resolution", type=_path, help="optional canary-otbm-script-resolution-v1 report")
    parser.add_argument("--route-interactions", type=_path, help=f"optional reviewed {INTERACTION_REGISTRY_FORMAT} registry")
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT} report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manifest, manifest_pin, manifest_path = _stable_json(args.manifest, "manifest", MANIFEST_FORMAT)
        world_index_pin, world_index_path = _stable_file_pin(
            args.world_index,
            "World Index",
            "canary-otbm-world-index-v1",
        )
        inputs = [manifest_path, world_index_path]
        for optional_path, label, expected_format in (
            (args.world_manifest, "World Index manifest", None),
            (args.transitions, "transition manifest", TRANSITION_FORMAT),
            (args.script_resolution, "Script Resolution", "canary-otbm-script-resolution-v1"),
            (args.route_interactions, "Route Interaction Registry", INTERACTION_REGISTRY_FORMAT),
        ):
            if optional_path is None:
                continue
            if expected_format is None:
                _payload, _pin, resolved = _stable_json(optional_path, label, None)
            else:
                _payload, _pin, resolved = _stable_json(optional_path, label, expected_format)
            inputs.append(resolved)
        appearances_candidate = args.appearances.expanduser()
        if appearances_candidate.is_symlink():
            raise ConnectivityResilienceError("appearances must not be a symlink")
        appearances_resolved = appearances_candidate.resolve(strict=True)
        if not appearances_resolved.is_file():
            raise ConnectivityResilienceError("appearances must be an existing regular file")
        inputs.append(appearances_resolved)
        if len(inputs) != len(set(inputs)):
            raise ConnectivityResilienceError("input files must be distinct")

        output = _prepare_output(args.output, inputs, args.overwrite)
        context, canonical_pins = prepare_connectivity_context(
            index_path=world_index_path,
            appearances_path=appearances_resolved,
            manifest=manifest,
            world_manifest_path=args.world_manifest,
            transitions_path=args.transitions,
            script_resolution_path=args.script_resolution,
            interaction_registry_path=args.route_interactions,
        )
        report = build_connectivity_resilience_report(
            manifest=manifest,
            context=context,
            input_pins={"manifest": manifest_pin, "worldIndex": world_index_pin, **canonical_pins},
        )
        _write_json(output, report, overwrite=args.overwrite)
        json.dump(
            {
                "format": report["format"],
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
    except (FileNotFoundError, OSError, ReachabilityError, ConnectivityResilienceError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
