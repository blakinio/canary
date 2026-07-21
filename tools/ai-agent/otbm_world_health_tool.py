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

from otbm_world_health import (
    COVERAGE_FORMAT,
    DEFAULT_SAMPLE_LIMIT,
    MAP_QUALITY_FORMAT,
    MAX_SAMPLE_LIMIT,
    REACHABILITY_FORMAT,
    WorldHealthError,
    build_world_health_report,
)

MAX_REPORT_BYTES = 256 * 1024 * 1024


def _path(value: str) -> Path:
    return Path(value)


def _positive_sample_limit(value: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("sample limit must be an integer") from exc
    if not 1 <= result <= MAX_SAMPLE_LIMIT:
        raise argparse.ArgumentTypeError(f"sample limit must be in 1..{MAX_SAMPLE_LIMIT}")
    return result


def _sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _load_stable_report(
    path: Path,
    label: str,
    expected_format: str,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise WorldHealthError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise WorldHealthError(f"{label} must be an existing regular file")
    stat_before = resolved.stat()
    if stat_before.st_size > MAX_REPORT_BYTES:
        raise WorldHealthError(f"{label} exceeds the {MAX_REPORT_BYTES}-byte input limit")
    sha_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldHealthError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorldHealthError(f"{label} must contain one JSON object")
    if payload.get("format") != expected_format:
        raise WorldHealthError(f"{label} must use format {expected_format}")
    stat_after = resolved.stat()
    sha_after = _sha256_file(resolved)
    if (
        stat_before.st_size != stat_after.st_size
        or stat_before.st_mtime_ns != stat_after.st_mtime_ns
        or sha_before != sha_after
    ):
        raise WorldHealthError(f"{label} changed while it was being read")
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
        raise WorldHealthError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    seen_inputs: set[Path] = set()
    for source in inputs:
        if source in seen_inputs:
            raise WorldHealthError("input reports must be distinct files")
        seen_inputs.add(source)
        if resolved == source:
            raise WorldHealthError("output must not be one of the input reports")
    if candidate.exists():
        if not candidate.is_file():
            raise WorldHealthError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise WorldHealthError("output must not be a hard link to an input report")
            except OSError as exc:
                raise WorldHealthError(f"cannot compare output with input report: {exc}") from exc
        if not overwrite:
            raise WorldHealthError(f"output already exists: {candidate}; pass --overwrite to replace it")
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
        raise WorldHealthError(f"output already exists: {path}; pass --overwrite to replace it") from exc
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
            "Aggregate compatible existing OTBM Map Quality, Reachability and Physical E2E coverage evidence "
            "into one deterministic read-only world-health report."
        )
    )
    parser.add_argument("--map-quality", type=_path, required=True, help=f"required {MAP_QUALITY_FORMAT} report")
    parser.add_argument(
        "--reachability",
        type=_path,
        action="append",
        default=[],
        help=f"optional {REACHABILITY_FORMAT} report; repeat for multiple bounded regions",
    )
    parser.add_argument(
        "--coverage-matrix",
        type=_path,
        action="append",
        default=[],
        help=f"optional {COVERAGE_FORMAT} report; repeat for multiple reviewed target sets",
    )
    parser.add_argument("--output", type=_path, required=True)
    parser.add_argument("--sample-limit", type=_positive_sample_limit, default=DEFAULT_SAMPLE_LIMIT)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        map_quality, map_quality_pin, map_quality_path = _load_stable_report(
            args.map_quality,
            "map-quality report",
            MAP_QUALITY_FORMAT,
        )
        reachability_reports: list[dict[str, Any]] = []
        reachability_pins: list[dict[str, Any]] = []
        input_paths = [map_quality_path]
        for index, path in enumerate(args.reachability):
            report, pin, resolved = _load_stable_report(
                path,
                f"reachability report #{index + 1}",
                REACHABILITY_FORMAT,
            )
            reachability_reports.append(report)
            reachability_pins.append(pin)
            input_paths.append(resolved)
        coverage_matrices: list[dict[str, Any]] = []
        coverage_pins: list[dict[str, Any]] = []
        for index, path in enumerate(args.coverage_matrix):
            report, pin, resolved = _load_stable_report(
                path,
                f"coverage matrix #{index + 1}",
                COVERAGE_FORMAT,
            )
            coverage_matrices.append(report)
            coverage_pins.append(pin)
            input_paths.append(resolved)

        output = _prepare_output(args.output, input_paths, args.overwrite)
        report = build_world_health_report(
            map_quality=map_quality,
            reachability_reports=reachability_reports,
            coverage_matrices=coverage_matrices,
            input_pins={
                "mapQuality": map_quality_pin,
                "reachability": reachability_pins,
                "coverageMatrices": coverage_pins,
            },
            sample_limit=args.sample_limit,
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
    except (FileNotFoundError, OSError, WorldHealthError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
