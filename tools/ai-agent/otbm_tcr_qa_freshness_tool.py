#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from otbm_tcr_qa_freshness import (
    TcrQaFreshnessError,
    build_freshness_impact_report,
    canonical_json,
    load_json_file_with_sha256,
)


def _input_path(path: Path, label: str) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise TcrQaFreshnessError(f"{label} must not be a symlink: {path}")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise TcrQaFreshnessError(f"{label} must be a regular file: {resolved}")
    return resolved


def _output_path(path: Path) -> Path:
    candidate = path.expanduser().absolute()
    if candidate.is_symlink():
        raise TcrQaFreshnessError(f"output must not be a symlink: {path}")
    parent = candidate.parent.resolve(strict=True)
    if not parent.is_dir():
        raise TcrQaFreshnessError(f"output parent must be a directory: {parent}")
    return parent / candidate.name


def write_report(
    output: Path,
    report: dict[str, object],
    *,
    overwrite: bool,
    inputs: tuple[Path, ...],
) -> None:
    destination = _output_path(output)
    for source in inputs:
        if destination.resolve(strict=False) == source:
            raise TcrQaFreshnessError("output must not alias an input file")
    if destination.exists() and not overwrite:
        raise TcrQaFreshnessError(
            f"output already exists; pass --overwrite to replace it: {destination}"
        )
    payload = (canonical_json(report) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if overwrite:
            if destination.is_symlink():
                raise TcrQaFreshnessError(
                    f"output became a symlink before replacement: {destination}"
                )
            os.replace(temporary, destination)
        else:
            try:
                os.link(temporary, destination)
            except FileExistsError as exc:
                raise TcrQaFreshnessError(
                    f"output already exists: {destination}"
                ) from exc
            temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify exact reviewed TCR-011 route-to-QA-016 dependency mappings "
            "and emit bounded freshness impacts."
        )
    )
    parser.add_argument("--routing-report", type=Path, required=True)
    parser.add_argument("--release-provenance", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict[str, object]:
    routing_path = _input_path(args.routing_report, "routing report")
    provenance_path = _input_path(
        args.release_provenance, "release provenance report"
    )
    manifest_path = _input_path(args.manifest, "freshness manifest")
    inputs = (routing_path, provenance_path, manifest_path)
    if len(set(inputs)) != len(inputs):
        raise TcrQaFreshnessError("routing, provenance and manifest inputs must be distinct")

    routing, routing_file_sha256 = load_json_file_with_sha256(
        routing_path, label="routing report"
    )
    provenance, provenance_file_sha256 = load_json_file_with_sha256(
        provenance_path, label="release provenance report"
    )
    manifest, manifest_file_sha256 = load_json_file_with_sha256(
        manifest_path, label="freshness manifest"
    )
    report = build_freshness_impact_report(
        routing,
        provenance,
        manifest,
        routing_file_sha256=routing_file_sha256,
        provenance_file_sha256=provenance_file_sha256,
        manifest_file_sha256=manifest_file_sha256,
    )
    write_report(
        args.output,
        report,
        overwrite=bool(args.overwrite),
        inputs=inputs,
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except (TcrQaFreshnessError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
