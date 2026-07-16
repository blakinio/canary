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

from otbm_map_quality import (
    DEFAULT_SAMPLE_LIMIT,
    MAX_SAMPLE_LIMIT,
    MapQualityError,
    build_quality_report,
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


def _load_stable_report(path: Path, label: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise MapQualityError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise MapQualityError(f"{label} must be an existing regular file")
    stat_before = resolved.stat()
    if stat_before.st_size > MAX_REPORT_BYTES:
        raise MapQualityError(f"{label} exceeds the {MAX_REPORT_BYTES}-byte input limit")
    sha_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MapQualityError(f"cannot read {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MapQualityError(f"{label} must contain one JSON object")
    stat_after = resolved.stat()
    sha_after = _sha256_file(resolved)
    if (
        stat_before.st_size != stat_after.st_size
        or stat_before.st_mtime_ns != stat_after.st_mtime_ns
        or sha_before != sha_after
    ):
        raise MapQualityError(f"{label} changed while it was being read")
    report_format = payload.get("format")
    if not isinstance(report_format, str) or not report_format:
        raise MapQualityError(f"{label} has no report format")
    pin = {
        "fileName": resolved.name,
        "size": stat_before.st_size,
        "sha256": sha_before,
        "format": report_format,
    }
    return payload, pin, resolved


def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise MapQualityError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    for source in inputs:
        if resolved == source:
            raise MapQualityError("output must not be one of the input reports")
    if candidate.exists():
        if not candidate.is_file():
            raise MapQualityError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise MapQualityError("output must not be a hard link to an input report")
            except OSError as exc:
                raise MapQualityError(f"cannot compare output with input report: {exc}") from exc
        if not overwrite:
            raise MapQualityError(f"output already exists: {candidate}; pass --overwrite to replace it")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def _write_json_atomic(path: Path, value: Any) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate existing OTBM geometry, reachability and script-resolution reports into one read-only static map quality gate."
        )
    )
    parser.add_argument("--geometry", type=_path, required=True, help="canary-otbm-geometry-audit-v1 report")
    parser.add_argument("--reachability", type=_path, required=True, help="canary-otbm-reachability-v1 report")
    parser.add_argument(
        "--script-resolution",
        type=_path,
        required=True,
        help="canary-otbm-script-resolution-v1 report",
    )
    parser.add_argument("--output", type=_path, required=True)
    parser.add_argument("--sample-limit", type=_positive_sample_limit, default=DEFAULT_SAMPLE_LIMIT)
    parser.add_argument("--fail-on-severity", choices=("none", "error", "warning"), default="error")
    parser.add_argument("--fail-on-unresolved", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        geometry, geometry_pin, geometry_path = _load_stable_report(args.geometry, "geometry report")
        reachability, reachability_pin, reachability_path = _load_stable_report(
            args.reachability,
            "reachability report",
        )
        script_resolution, script_pin, script_path = _load_stable_report(
            args.script_resolution,
            "script-resolution report",
        )
        output = _prepare_output(
            args.output,
            [geometry_path, reachability_path, script_path],
            args.overwrite,
        )
        report = build_quality_report(
            geometry=geometry,
            reachability=reachability,
            script_resolution=script_resolution,
            input_pins={
                "geometry": geometry_pin,
                "reachability": reachability_pin,
                "scriptResolution": script_pin,
            },
            sample_limit=args.sample_limit,
            fail_on_severity=args.fail_on_severity,
            fail_on_unresolved=args.fail_on_unresolved,
        )
        _write_json_atomic(output, report)
        summary = report["summary"]
        json.dump(
            {
                "ok": report["ok"],
                "sourceSha256": report["source"]["sha256"],
                "outcomeCounts": summary["outcomeCounts"],
                "sampled": summary["sampled"],
                "truncated": summary["truncated"],
                "output": str(output),
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if report["ok"] else 2
    except (FileNotFoundError, OSError, MapQualityError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
