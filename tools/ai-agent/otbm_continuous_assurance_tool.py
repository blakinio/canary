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

from otbm_continuous_assurance import (
    CERTIFICATION_FORMAT,
    EXECUTION_FORMAT,
    REGRESSION_FORMAT,
    REPORT_FORMAT,
    WORLD_HEALTH_FORMAT,
    ContinuousAssuranceError,
    build_continuous_assurance_report,
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
        raise ContinuousAssuranceError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise ContinuousAssuranceError(f"{label} must be an existing regular file")
    stat_before = resolved.stat()
    if stat_before.st_size > MAX_REPORT_BYTES:
        raise ContinuousAssuranceError(f"{label} exceeds the {MAX_REPORT_BYTES}-byte input limit")
    sha_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContinuousAssuranceError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContinuousAssuranceError(f"{label} must contain one JSON object")
    if payload.get("format") != expected_format:
        raise ContinuousAssuranceError(f"{label} must use format {expected_format}")
    stat_after = resolved.stat()
    sha_after = _sha256_file(resolved)
    if stat_before.st_size != stat_after.st_size or stat_before.st_mtime_ns != stat_after.st_mtime_ns or sha_before != sha_after:
        raise ContinuousAssuranceError(f"{label} changed while it was being read")
    return payload, {
        "fileName": resolved.name,
        "size": stat_before.st_size,
        "sha256": sha_before,
        "format": expected_format,
    }, resolved

def _prepare_output(path: Path, inputs: list[Path], overwrite: bool) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise ContinuousAssuranceError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    if len(set(inputs)) != len(inputs):
        raise ContinuousAssuranceError("input reports must be distinct files")
    for source in inputs:
        if resolved == source:
            raise ContinuousAssuranceError("output must not be one of the input reports")
    if candidate.exists():
        if not candidate.is_file():
            raise ContinuousAssuranceError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise ContinuousAssuranceError("output must not be a hard link to an input report")
            except OSError as exc:
                raise ContinuousAssuranceError(f"cannot compare output with input report: {exc}") from exc
        if not overwrite:
            raise ContinuousAssuranceError(f"output already exists: {candidate}; pass --overwrite to replace it")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved

def _write_json(path: Path, value: Any, overwrite: bool) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if not overwrite:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        return
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

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compose a fail-closed OTBM continuous-assurance gate from exact regression, execution, health and certification evidence."
    )
    parser.add_argument("--execution-ledger", type=_path, required=True, help=f"required {EXECUTION_FORMAT}")
    parser.add_argument("--regression-plan", type=_path, required=True, help=f"required {REGRESSION_FORMAT}")
    parser.add_argument("--before-world-health", type=_path, required=True, help=f"required baseline {WORLD_HEALTH_FORMAT}")
    parser.add_argument("--after-world-health", type=_path, required=True, help=f"required current {WORLD_HEALTH_FORMAT}")
    parser.add_argument("--before-certification", type=_path, required=True, help=f"required baseline {CERTIFICATION_FORMAT}")
    parser.add_argument("--after-certification", type=_path, required=True, help=f"required current {CERTIFICATION_FORMAT}")
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT}")
    parser.add_argument("--overwrite", action="store_true")
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    specs = [
        ("executionLedger", args.execution_ledger, "execution ledger", EXECUTION_FORMAT),
        ("regressionPlan", args.regression_plan, "regression plan", REGRESSION_FORMAT),
        ("beforeWorldHealth", args.before_world_health, "before World Health", WORLD_HEALTH_FORMAT),
        ("afterWorldHealth", args.after_world_health, "after World Health", WORLD_HEALTH_FORMAT),
        ("beforeCertification", args.before_certification, "before Certification", CERTIFICATION_FORMAT),
        ("afterCertification", args.after_certification, "after Certification", CERTIFICATION_FORMAT),
    ]
    try:
        payloads: dict[str, dict[str, Any]] = {}
        pins: dict[str, dict[str, Any]] = {}
        paths: list[Path] = []
        for name, path, label, fmt in specs:
            payload, pin, resolved = _load_stable_json(path, label, fmt)
            payloads[name] = payload
            pins[name] = pin
            paths.append(resolved)
        output = _prepare_output(args.output, paths, args.overwrite)
        report = build_continuous_assurance_report(
            execution_ledger=payloads["executionLedger"],
            regression_plan=payloads["regressionPlan"],
            before_world_health=payloads["beforeWorldHealth"],
            after_world_health=payloads["afterWorldHealth"],
            before_certification=payloads["beforeCertification"],
            after_certification=payloads["afterCertification"],
            input_pins=pins,
        )
        _write_json(output, report, args.overwrite)
        json.dump(
            {"format": report["format"], "gate": report["gate"], "summary": report["summary"], "output": str(output)},
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0
    except (FileExistsError, FileNotFoundError, OSError, ContinuousAssuranceError) as exc:
        parser.error(str(exc))
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
