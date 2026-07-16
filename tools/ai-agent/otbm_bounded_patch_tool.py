#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from otbm_bounded_patch import apply_bounded_patch
from otbm_bounded_patch_types import BoundedPatchError, load_plan


def _path(value: str) -> Path:
    return Path(value)


def _existing_scanner(candidate: Path, label: str) -> Path:
    expanded = candidate.expanduser()
    if not expanded.is_file():
        raise BoundedPatchError(f"{label} was not found: {expanded}")
    return expanded


def _locate_scanner(explicit: Path | None) -> Path:
    if explicit is not None:
        return _existing_scanner(explicit, "explicit native OTBM scanner")

    environment = os.environ.get("OTBM_ITEM_AUDIT_SCANNER")
    if environment:
        return _existing_scanner(Path(environment), "OTBM_ITEM_AUDIT_SCANNER")

    module = Path(__file__).resolve().parent
    for candidate in (module / "otbm_item_audit_scan", module / "otbm_item_audit_scan.exe"):
        if candidate.is_file():
            return candidate
    raise BoundedPatchError("native OTBM scanner was not found; compile otbm_item_audit_scan.cpp or pass --scanner")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply a manifest-pinned, fixed-width mechanic attribute patch to a distinct OTBM copy."
    )
    parser.add_argument("--plan", type=_path, required=True)
    parser.add_argument("--source", type=_path, required=True)
    parser.add_argument("--scanner", type=_path)
    parser.add_argument("--artifact-root", type=_path, required=True)
    parser.add_argument("--output", type=_path, required=True)
    parser.add_argument("--evidence-directory", type=_path, required=True)
    parser.add_argument("--result", type=_path, required=True)
    parser.add_argument("--timeout", type=int, default=3600)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = apply_bounded_patch(
            plan=load_plan(args.plan),
            source_path=args.source,
            scanner_path=_locate_scanner(args.scanner),
            artifact_root=args.artifact_root,
            output_path=args.output,
            evidence_directory=args.evidence_directory,
            result_path=args.result,
            timeout_seconds=args.timeout,
        )
    except (BoundedPatchError, FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
