#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quest_map_validation import (
    DEFAULT_SAMPLE_LIMIT,
    QuestMapValidationError,
    scan_to_file,
    validate_to_file,
)
from otbm_world_index_tool import position_from_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract and correlate static quest/map evidence")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Generate map-independent quest source evidence")
    scan.add_argument("--repository-root", type=Path, default=Path("."))
    scan.add_argument("--source-root", action="append", default=[])
    scan.add_argument("--include", action="append", required=True)
    scan.add_argument("--exclude", action="append", default=[])
    scan.add_argument("--output", type=Path, required=True)
    scan.add_argument("--allow-empty", action="store_true")

    validate = subparsers.add_parser("validate", help="Correlate evidence with an OTBM world index")
    validate.add_argument("evidence", type=Path)
    validate.add_argument("--world-index", type=Path, required=True)
    validate.add_argument("--script-resolution", type=Path)
    validate.add_argument("--region-from", type=position_from_text)
    validate.add_argument("--region-to", type=position_from_text)
    validate.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)
    validate.add_argument("--output", type=Path, required=True)
    validate.add_argument("--fail-on", choices=("none", "conflicting", "finding", "incomplete"), default="conflicting")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "scan":
            roots = args.source_root or ["data", "data-otservbr-global"]
            payload = scan_to_file(
                args.output,
                repository_root=args.repository_root,
                source_roots=roots,
                includes=args.include,
                excludes=args.exclude,
            )
            if not payload["ok"] and not args.allow_empty:
                raise QuestMapValidationError("No selected Lua/XML files were found")
            summary = payload["summary"]
            sys.stdout.write(json.dumps({"ok": payload["ok"], "summary": summary, "output": str(args.output.resolve())}, indent=2) + "\n")
            return 0

        if bool(args.region_from) != bool(args.region_to):
            raise QuestMapValidationError("--region-from and --region-to must be supplied together")
        region = (args.region_from, args.region_to) if args.region_from else None
        payload = validate_to_file(
            args.output,
            evidence_path=args.evidence,
            world_index=args.world_index,
            script_resolution_path=args.script_resolution,
            region=region,
            sample_limit=args.sample_limit,
        )
        summary = payload["summary"]
        sys.stdout.write(json.dumps({"ok": payload["ok"], "complete": payload["complete"], "summary": summary, "output": str(args.output.resolve())}, indent=2) + "\n")
        if args.fail_on == "none":
            return 0
        if args.fail_on == "conflicting":
            return 2 if summary["byClassification"]["conflicting"] else 0
        if args.fail_on == "finding":
            return 2 if any(summary["byClassification"][name] for name in ("map-only", "script-only", "conflicting")) else 0
        return 2 if not payload["complete"] else 0
    except (FileNotFoundError, OSError, ValueError, QuestMapValidationError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
