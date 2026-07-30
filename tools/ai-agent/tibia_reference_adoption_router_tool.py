#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from tibia_reference_adoption_router import (
    AdoptionRoutingError,
    build_routing_report,
    canonical_json,
    load_json_file_with_sha256,
)


def _input_path(path: Path, label: str) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise AdoptionRoutingError(f"{label} must not be a symlink: {path}")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise AdoptionRoutingError(f"{label} must be a regular file: {resolved}")
    return resolved


def _output_path(path: Path) -> Path:
    candidate = path.expanduser().absolute()
    if candidate.is_symlink():
        raise AdoptionRoutingError(f"output must not be a symlink: {path}")
    parent = candidate.parent.resolve(strict=True)
    if not parent.is_dir():
        raise AdoptionRoutingError(f"output parent must be a directory: {parent}")
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
            raise AdoptionRoutingError("output must not alias an input file")
    if destination.exists() and not overwrite:
        raise AdoptionRoutingError(
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
                raise AdoptionRoutingError(
                    f"output became a symlink before replacement: {destination}"
                )
            os.replace(temporary, destination)
        else:
            try:
                os.link(temporary, destination)
            except FileExistsError as exc:
                raise AdoptionRoutingError(
                    f"output already exists: {destination}"
                ) from exc
            temporary.unlink()
    finally:
        if temporary.exists():
            temporary.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Route exact reviewed TCR-010 extracts to existing Canary owners/capabilities."
    )
    parser.add_argument("--gateway-report", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def run(args: argparse.Namespace) -> dict[str, object]:
    gateway_path = _input_path(args.gateway_report, "gateway report")
    request_path = _input_path(args.request, "routing request")
    if gateway_path == request_path:
        raise AdoptionRoutingError("gateway report and routing request must be distinct")
    gateway, gateway_file_sha256 = load_json_file_with_sha256(
        gateway_path, label="gateway report"
    )
    request, request_file_sha256 = load_json_file_with_sha256(
        request_path, label="routing request"
    )
    report = build_routing_report(
        gateway,
        request,
        gateway_file_sha256=gateway_file_sha256,
        request_file_sha256=request_file_sha256,
    )
    write_report(
        args.output,
        report,
        overwrite=bool(args.overwrite),
        inputs=(gateway_path, request_path),
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except (AdoptionRoutingError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
