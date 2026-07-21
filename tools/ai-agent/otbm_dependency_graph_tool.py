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

from otbm_dependency_graph import (
    COVERAGE_FORMAT,
    MANIFEST_FORMAT,
    REGRESSION_FORMAT,
    REPORT_FORMAT,
    WORLD_HEALTH_FORMAT,
    DependencyGraphError,
    build_dependency_graph_report,
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
        raise DependencyGraphError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise DependencyGraphError(f"{label} must be an existing regular file")
    stat_before = resolved.stat()
    if stat_before.st_size > MAX_REPORT_BYTES:
        raise DependencyGraphError(f"{label} exceeds the {MAX_REPORT_BYTES}-byte input limit")
    sha_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DependencyGraphError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DependencyGraphError(f"{label} must contain one JSON object")
    if payload.get("format") != expected_format:
        raise DependencyGraphError(f"{label} must use format {expected_format}")
    stat_after = resolved.stat()
    sha_after = _sha256_file(resolved)
    if (
        stat_before.st_size != stat_after.st_size
        or stat_before.st_mtime_ns != stat_after.st_mtime_ns
        or sha_before != sha_after
    ):
        raise DependencyGraphError(f"{label} changed while it was being read")
    pin = {
        "fileName": resolved.name,
        "size": stat_before.st_size,
        "sha256": sha_before,
        "format": expected_format,
    }
    return payload, pin, resolved


def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise DependencyGraphError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    seen_inputs: set[Path] = set()
    for source in inputs:
        if source in seen_inputs:
            raise DependencyGraphError("input reports must be distinct files")
        seen_inputs.add(source)
        if resolved == source:
            raise DependencyGraphError("output must not be one of the input reports")
    if candidate.exists():
        if not candidate.is_file():
            raise DependencyGraphError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise DependencyGraphError("output must not be a hard link to an input report")
            except OSError as exc:
                raise DependencyGraphError(f"cannot compare output with input report: {exc}") from exc
        if not overwrite:
            raise DependencyGraphError(f"output already exists: {candidate}; pass --overwrite to replace it")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def _encoded_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_json_create_new(path: Path, value: Any) -> None:
    encoded = _encoded_json(value)
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
        raise DependencyGraphError(f"output already exists: {path}; pass --overwrite to replace it") from exc
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            path.unlink(missing_ok=True)
        raise


def _write_json_overwrite_atomic(path: Path, value: Any) -> None:
    encoded = _encoded_json(value)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
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
            "Build an exact-evidence OTBM dependency/blast-radius report from a reviewed manifest, "
            "compatible World Health and Regression Guard evidence, and optional Coverage Dashboard evidence."
        )
    )
    parser.add_argument("--manifest", type=_path, required=True, help=f"required {MANIFEST_FORMAT} manifest")
    parser.add_argument("--world-health", type=_path, required=True, help=f"required {WORLD_HEALTH_FORMAT} report")
    parser.add_argument(
        "--regression-guard",
        type=_path,
        required=True,
        help=f"required {REGRESSION_FORMAT} report",
    )
    parser.add_argument(
        "--coverage-dashboard",
        type=_path,
        help=f"optional compatible {COVERAGE_FORMAT} report",
    )
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT} report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manifest, manifest_pin, manifest_path = _load_stable_json(args.manifest, "manifest", MANIFEST_FORMAT)
        world, world_pin, world_path = _load_stable_json(args.world_health, "World Health", WORLD_HEALTH_FORMAT)
        regression, regression_pin, regression_path = _load_stable_json(
            args.regression_guard,
            "Regression Guard",
            REGRESSION_FORMAT,
        )
        coverage = None
        coverage_pin = None
        coverage_path = None
        if args.coverage_dashboard is not None:
            coverage, coverage_pin, coverage_path = _load_stable_json(
                args.coverage_dashboard,
                "Coverage Dashboard",
                COVERAGE_FORMAT,
            )

        inputs = [manifest_path, world_path, regression_path]
        if coverage_path is not None:
            inputs.append(coverage_path)
        output = _prepare_output(args.output, inputs, args.overwrite)
        pins = {
            "manifest": manifest_pin,
            "worldHealth": world_pin,
            "regressionGuard": regression_pin,
        }
        if coverage_pin is not None:
            pins["coverageDashboard"] = coverage_pin

        report = build_dependency_graph_report(
            manifest=manifest,
            world_health=world,
            regression_guard=regression,
            coverage_dashboard=coverage,
            input_pins=pins,
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
    except (FileNotFoundError, OSError, DependencyGraphError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
