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

from otbm_coverage_dashboard import (
    CANDIDATE_REPAIR_FORMAT,
    COVERAGE_FORMAT,
    MAP_QUALITY_FORMAT,
    QUEST_VALIDATION_FORMAT,
    REPORT_FORMAT,
    ROUTE_PLAN_FORMAT,
    TARGETS_FORMAT,
    WORLD_HEALTH_FORMAT,
    CoverageDashboardError,
    build_coverage_dashboard_report,
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
        raise CoverageDashboardError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise CoverageDashboardError(f"{label} must be an existing regular file")
    stat_before = resolved.stat()
    if stat_before.st_size > MAX_REPORT_BYTES:
        raise CoverageDashboardError(f"{label} exceeds the {MAX_REPORT_BYTES}-byte input limit")
    sha_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CoverageDashboardError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CoverageDashboardError(f"{label} must contain one JSON object")
    if payload.get("format") != expected_format:
        raise CoverageDashboardError(f"{label} must use format {expected_format}")
    stat_after = resolved.stat()
    sha_after = _sha256_file(resolved)
    if (
        stat_before.st_size != stat_after.st_size
        or stat_before.st_mtime_ns != stat_after.st_mtime_ns
        or sha_before != sha_after
    ):
        raise CoverageDashboardError(f"{label} changed while it was being read")
    pin = {
        "fileName": resolved.name,
        "size": stat_before.st_size,
        "sha256": sha_before,
        "format": expected_format,
    }
    return payload, pin, resolved


def _load_optional(paths: list[Path], label: str, expected_format: str) -> tuple[list[dict[str, Any]], list[Path]]:
    entries: list[dict[str, Any]] = []
    resolved_paths: list[Path] = []
    for index, path in enumerate(paths):
        report, pin, resolved = _load_stable_json(path, f"{label}[{index}]", expected_format)
        entries.append({"report": report, "pin": pin})
        resolved_paths.append(resolved)
    return entries, resolved_paths


def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise CoverageDashboardError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    seen_inputs: set[Path] = set()
    for source in inputs:
        if source in seen_inputs:
            raise CoverageDashboardError("input reports must be distinct files")
        seen_inputs.add(source)
        if resolved == source:
            raise CoverageDashboardError("output must not be one of the input reports")
    if candidate.exists():
        if not candidate.is_file():
            raise CoverageDashboardError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise CoverageDashboardError("output must not be a hard link to an input report")
            except OSError as exc:
                raise CoverageDashboardError(f"cannot compare output with input report: {exc}") from exc
        if not overwrite:
            raise CoverageDashboardError(f"output already exists: {candidate}; pass --overwrite to replace it")
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
        raise CoverageDashboardError(f"output already exists: {path}; pass --overwrite to replace it") from exc
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
            "Build a factual OTBM coverage dashboard from reviewed targets and compatible existing coverage, "
            "quality, health, source-correlation, route and candidate evidence."
        )
    )
    parser.add_argument("--targets", type=_path, required=True, help=f"required {TARGETS_FORMAT} manifest")
    parser.add_argument("--coverage-matrix", type=_path, required=True, help=f"required {COVERAGE_FORMAT} report")
    parser.add_argument("--map-quality", type=_path, required=True, help=f"required {MAP_QUALITY_FORMAT} report")
    parser.add_argument("--world-health", type=_path, required=True, help=f"required {WORLD_HEALTH_FORMAT} report")
    parser.add_argument(
        "--quest-validation",
        type=_path,
        action="append",
        default=[],
        help=f"optional repeatable {QUEST_VALIDATION_FORMAT} report",
    )
    parser.add_argument(
        "--route-plan",
        type=_path,
        action="append",
        default=[],
        help=f"optional repeatable {ROUTE_PLAN_FORMAT} report",
    )
    parser.add_argument(
        "--candidate-repair",
        type=_path,
        action="append",
        default=[],
        help=f"optional repeatable {CANDIDATE_REPAIR_FORMAT} report",
    )
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT} report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        targets, targets_pin, targets_path = _load_stable_json(args.targets, "targets", TARGETS_FORMAT)
        coverage, coverage_pin, coverage_path = _load_stable_json(
            args.coverage_matrix, "coverage matrix", COVERAGE_FORMAT
        )
        map_quality, map_quality_pin, map_quality_path = _load_stable_json(
            args.map_quality, "Map Quality", MAP_QUALITY_FORMAT
        )
        world_health, world_health_pin, world_health_path = _load_stable_json(
            args.world_health, "World Health", WORLD_HEALTH_FORMAT
        )
        quest_entries, quest_paths = _load_optional(args.quest_validation, "quest validation", QUEST_VALIDATION_FORMAT)
        route_entries, route_paths = _load_optional(args.route_plan, "route plan", ROUTE_PLAN_FORMAT)
        candidate_entries, candidate_paths = _load_optional(
            args.candidate_repair, "candidate repair", CANDIDATE_REPAIR_FORMAT
        )
        input_paths = [targets_path, coverage_path, map_quality_path, world_health_path]
        input_paths.extend(quest_paths)
        input_paths.extend(route_paths)
        input_paths.extend(candidate_paths)
        output = _prepare_output(args.output, input_paths, args.overwrite)
        report = build_coverage_dashboard_report(
            targets_manifest=targets,
            coverage_matrix=coverage,
            map_quality=map_quality,
            world_health=world_health,
            quest_validations=quest_entries,
            route_plans=route_entries,
            candidate_repairs=candidate_entries,
            input_pins={
                "targets": targets_pin,
                "coverageMatrix": coverage_pin,
                "mapQuality": map_quality_pin,
                "worldHealth": world_health_pin,
            },
        )
        _write_json(output, report, overwrite=args.overwrite)
        json.dump(
            {
                "format": report["format"],
                "currentMap": report["currentMap"],
                "summary": report["summary"],
                "output": str(output),
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0
    except (FileNotFoundError, OSError, CoverageDashboardError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
