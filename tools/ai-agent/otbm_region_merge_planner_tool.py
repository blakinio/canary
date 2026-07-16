#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from otbm_scan import position_from_text
from otbm_semantic_diff_types import MAX_OUTPUT_BYTES, SemanticDiffError
from otbm_world_index import WorldIndexError

from otbm_region_merge_planner import (
    DEFAULT_SAMPLE_LIMIT,
    POLICIES,
    RegionMergePlannerError,
    analyze_region_merge_plan,
)


def _path(value: str) -> Path:
    return Path(value)


def _resolve_output(root: Path, path: Path) -> Path:
    root = root.expanduser().resolve()
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise RegionMergePlannerError(f"Output must not be a symlink: {candidate}")
    resolved_parent = candidate.parent.resolve(strict=True)
    try:
        resolved_parent.relative_to(root)
    except ValueError as exc:
        raise RegionMergePlannerError(f"Output escapes artifact root {root}: {candidate}") from exc
    return resolved_parent / candidate.name


def _encode_report(report: dict[str, object]) -> bytes:
    payload = (json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > MAX_OUTPUT_BYTES:
        raise RegionMergePlannerError(
            f"Region merge report is {len(payload)} bytes; maximum is {MAX_OUTPUT_BYTES}"
        )
    return payload


def _write_report(path: Path, report: dict[str, object], *, artifact_root: Path, overwrite: bool) -> None:
    target = _resolve_output(artifact_root, path)
    payload = _encode_report(report)
    if target.exists() and not target.is_file():
        raise RegionMergePlannerError(f"Output exists but is not a regular file: {target}")
    if target.exists() and target.is_symlink():
        raise RegionMergePlannerError(f"Output must not be a symlink: {target}")

    if not overwrite:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(target, flags, 0o644)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
        finally:
            os.close(descriptor)
        return

    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise RegionMergePlannerError(f"Temporary output already exists: {temporary}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(temporary, flags, 0o644)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    finally:
        os.close(descriptor)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a read-only translated donor-region merge review plan from canonical World Index inputs."
    )
    parser.add_argument("--artifact-root", type=_path, required=True)
    parser.add_argument("--current-index", type=_path, required=True)
    parser.add_argument("--current-manifest", type=_path, required=True)
    parser.add_argument("--donor-index", type=_path, required=True)
    parser.add_argument("--donor-manifest", type=_path, required=True)
    parser.add_argument("--donor-from", type=position_from_text, required=True)
    parser.add_argument("--donor-to", type=position_from_text, required=True)
    parser.add_argument("--target-origin", type=position_from_text, required=True)
    parser.add_argument("--policy", choices=sorted(POLICIES), default="overlay")
    parser.add_argument("--current-script-resolution", type=_path)
    parser.add_argument("--donor-script-resolution", type=_path)
    parser.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)
    parser.add_argument("--output", type=_path)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = analyze_region_merge_plan(
            artifact_root=args.artifact_root,
            current_index_path=args.current_index,
            current_manifest_path=args.current_manifest,
            donor_index_path=args.donor_index,
            donor_manifest_path=args.donor_manifest,
            donor_from=args.donor_from,
            donor_to=args.donor_to,
            target_origin=args.target_origin,
            policy=args.policy,
            sample_limit=args.sample_limit,
            current_script_resolution_path=args.current_script_resolution,
            donor_script_resolution_path=args.donor_script_resolution,
        )
        if args.output is None:
            json.dump(report, sys.stdout, indent=2, ensure_ascii=False, sort_keys=True)
            sys.stdout.write("\n")
        else:
            _write_report(
                args.output,
                report,
                artifact_root=args.artifact_root,
                overwrite=args.overwrite,
            )
    except (
        RegionMergePlannerError,
        SemanticDiffError,
        WorldIndexError,
        FileNotFoundError,
        OSError,
        ValueError,
    ) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
