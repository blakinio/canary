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

from otbm_reviewed_candidate_repair import (
    APPROVAL_FORMAT,
    IMPACTED_SELECTION_FORMAT,
    PHYSICAL_VALIDATION_FORMAT,
    PIPELINE_FORMAT,
    RECOMMENDATION_FORMAT,
    REPORT_FORMAT,
    SEMANTIC_DIFF_FORMAT,
    ReviewedCandidateRepairError,
    build_reviewed_candidate_repair_report,
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
        raise ReviewedCandidateRepairError(f"{label} must not be a symlink")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise ReviewedCandidateRepairError(f"{label} must be an existing regular file")
    stat_before = resolved.stat()
    if stat_before.st_size > MAX_REPORT_BYTES:
        raise ReviewedCandidateRepairError(f"{label} exceeds the {MAX_REPORT_BYTES}-byte input limit")
    sha_before = _sha256_file(resolved)
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewedCandidateRepairError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReviewedCandidateRepairError(f"{label} must contain one JSON object")
    if payload.get("format") != expected_format:
        raise ReviewedCandidateRepairError(f"{label} must use format {expected_format}")
    stat_after = resolved.stat()
    sha_after = _sha256_file(resolved)
    if (
        stat_before.st_size != stat_after.st_size
        or stat_before.st_mtime_ns != stat_after.st_mtime_ns
        or sha_before != sha_after
    ):
        raise ReviewedCandidateRepairError(f"{label} changed while it was being read")
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
        raise ReviewedCandidateRepairError("output must not be a symlink")
    resolved = candidate.resolve(strict=False)
    seen_inputs: set[Path] = set()
    for source in inputs:
        if source in seen_inputs:
            raise ReviewedCandidateRepairError("input reports must be distinct files")
        seen_inputs.add(source)
        if resolved == source:
            raise ReviewedCandidateRepairError("output must not be one of the input reports")
    if candidate.exists():
        if not candidate.is_file():
            raise ReviewedCandidateRepairError("output exists but is not a regular file")
        for source in inputs:
            try:
                if os.path.samefile(candidate, source):
                    raise ReviewedCandidateRepairError("output must not be a hard link to an input report")
            except OSError as exc:
                raise ReviewedCandidateRepairError(f"cannot compare output with input report: {exc}") from exc
        if not overwrite:
            raise ReviewedCandidateRepairError(f"output already exists: {candidate}; pass --overwrite to replace it")
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
        raise ReviewedCandidateRepairError(f"output already exists: {path}; pass --overwrite to replace it") from exc
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
            "Validate one explicitly approved OTBM repair evidence chain across the existing repair/materialization "
            "pipeline, Semantic Diff, impacted Physical E2E selection and OTBM-E2E-009 result."
        )
    )
    parser.add_argument("--recommendation", type=_path, required=True, help=f"required {RECOMMENDATION_FORMAT} report")
    parser.add_argument("--approval", type=_path, required=True, help=f"required {APPROVAL_FORMAT} approval")
    parser.add_argument("--pipeline-result", type=_path, required=True, help=f"required {PIPELINE_FORMAT} report")
    parser.add_argument("--semantic-diff", type=_path, required=True, help=f"required {SEMANTIC_DIFF_FORMAT} report")
    parser.add_argument(
        "--impacted-selection", type=_path, required=True, help=f"required {IMPACTED_SELECTION_FORMAT} report"
    )
    parser.add_argument(
        "--physical-validation", type=_path, required=True, help=f"required {PHYSICAL_VALIDATION_FORMAT} report"
    )
    parser.add_argument("--output", type=_path, required=True, help=f"create {REPORT_FORMAT} report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        recommendation, recommendation_pin, recommendation_path = _load_stable_json(
            args.recommendation, "recommendation", RECOMMENDATION_FORMAT
        )
        approval, approval_pin, approval_path = _load_stable_json(args.approval, "approval", APPROVAL_FORMAT)
        pipeline, pipeline_pin, pipeline_path = _load_stable_json(
            args.pipeline_result, "pipeline result", PIPELINE_FORMAT
        )
        semantic_diff, semantic_diff_pin, semantic_diff_path = _load_stable_json(
            args.semantic_diff, "semantic diff", SEMANTIC_DIFF_FORMAT
        )
        impacted_selection, impacted_selection_pin, impacted_selection_path = _load_stable_json(
            args.impacted_selection, "impacted selection", IMPACTED_SELECTION_FORMAT
        )
        physical_validation, physical_validation_pin, physical_validation_path = _load_stable_json(
            args.physical_validation, "physical validation", PHYSICAL_VALIDATION_FORMAT
        )
        paths = [
            recommendation_path,
            approval_path,
            pipeline_path,
            semantic_diff_path,
            impacted_selection_path,
            physical_validation_path,
        ]
        output = _prepare_output(args.output, paths, args.overwrite)
        report = build_reviewed_candidate_repair_report(
            recommendation=recommendation,
            approval=approval,
            pipeline_result=pipeline,
            semantic_diff=semantic_diff,
            impacted_selection=impacted_selection,
            physical_validation=physical_validation,
            input_pins={
                "recommendation": recommendation_pin,
                "approval": approval_pin,
                "pipelineResult": pipeline_pin,
                "semanticDiff": semantic_diff_pin,
                "impactedSelection": impacted_selection_pin,
                "physicalValidation": physical_validation_pin,
            },
        )
        _write_json(output, report, overwrite=args.overwrite)
        json.dump(
            {
                "format": report["format"],
                "ok": report["ok"],
                "status": report["status"],
                "source": report["source"],
                "candidate": report["candidate"],
                "selection": report["selection"],
                "output": str(output),
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if report["ok"] else 3
    except (FileNotFoundError, OSError, ReviewedCandidateRepairError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
