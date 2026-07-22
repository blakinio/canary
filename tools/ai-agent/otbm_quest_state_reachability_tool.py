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

from otbm_quest_state_reachability import (
    INTERACTION_REGISTRY_FORMAT,
    MANIFEST_FORMAT,
    REPORT_FORMAT,
    STORAGE_GRAPH_FORMAT,
    QuestStateReachabilityError,
    build_quest_state_reachability_report,
)

MAX_REPORT_BYTES = 256 * 1024 * 1024


def _path(value: str) -> Path:
    return Path(value)


def _sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _load_stable_json(path: Path, label: str, expected_format: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise QuestStateReachabilityError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise QuestStateReachabilityError(f"{label} must be an existing regular file")
    stat_before = resolved.stat()
    if stat_before.st_size > MAX_REPORT_BYTES:
        raise QuestStateReachabilityError(f"{label} exceeds the {MAX_REPORT_BYTES}-byte input limit")
    digest_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise QuestStateReachabilityError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise QuestStateReachabilityError(f"{label} must contain one JSON object")
    if payload.get("format") != expected_format:
        raise QuestStateReachabilityError(f"{label} must use format {expected_format}")
    stat_after = resolved.stat()
    digest_after = _sha256_file(resolved)
    if (
        stat_before.st_size != stat_after.st_size
        or stat_before.st_mtime_ns != stat_after.st_mtime_ns
        or digest_before != digest_after
    ):
        raise QuestStateReachabilityError(f"{label} changed while it was being read")
    return (
        payload,
        {
            "fileName": resolved.name,
            "size": stat_before.st_size,
            "sha256": digest_before,
            "format": expected_format,
        },
        resolved,
    )


def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise QuestStateReachabilityError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    if len(inputs) != len(set(inputs)):
        raise QuestStateReachabilityError("input reports must be distinct files")
    for source in inputs:
        if resolved == source:
            raise QuestStateReachabilityError("output must not be one of the input reports")
    if candidate.exists():
        if not candidate.is_file():
            raise QuestStateReachabilityError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise QuestStateReachabilityError("output must not be a hard link to an input report")
            except OSError as exc:
                raise QuestStateReachabilityError(f"cannot compare output with input report: {exc}") from exc
        if not overwrite:
            raise QuestStateReachabilityError(f"output already exists: {candidate}; pass --overwrite to replace it")
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
        raise QuestStateReachabilityError(f"output already exists: {path}; pass --overwrite to replace it") from exc
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
        description=(
            "Build a conservative selected-scope OTBM quest-state reachability report from an explicit reviewed manifest, "
            "canonical Storage Graph evidence and optional reviewed Route Interaction evidence."
        )
    )
    parser.add_argument("--manifest", type=_path, required=True, help=f"required {MANIFEST_FORMAT} manifest")
    parser.add_argument("--storage-graph", type=_path, required=True, help=f"required {STORAGE_GRAPH_FORMAT} report")
    parser.add_argument(
        "--route-interactions",
        type=_path,
        help=f"optional {INTERACTION_REGISTRY_FORMAT} registry; required by interaction-gated manifest transitions",
    )
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT} report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manifest, manifest_pin, manifest_path = _load_stable_json(args.manifest, "manifest", MANIFEST_FORMAT)
        storage_graph, storage_pin, storage_path = _load_stable_json(
            args.storage_graph,
            "Storage Graph",
            STORAGE_GRAPH_FORMAT,
        )
        route_interactions = None
        interaction_pin = None
        inputs = [manifest_path, storage_path]
        if args.route_interactions is not None:
            route_interactions, interaction_pin, interaction_path = _load_stable_json(
                args.route_interactions,
                "Route Interaction Registry",
                INTERACTION_REGISTRY_FORMAT,
            )
            inputs.append(interaction_path)
        output = _prepare_output(args.output, inputs, args.overwrite)
        report = build_quest_state_reachability_report(
            manifest=manifest,
            storage_graph=storage_graph,
            route_interactions=route_interactions,
            input_pins={
                "manifest": manifest_pin,
                "storageGraph": storage_pin,
                "routeInteractions": interaction_pin,
            },
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
    except (FileNotFoundError, OSError, QuestStateReachabilityError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
