#!/usr/bin/env python3
"""CLI for Canary upstream intelligence and drift tracking."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from upstream_intelligence_lib import (
    ROOT,
    UpstreamError,
    render_markdown,
    scan,
    validate_repository,
    validate_snapshot,
    write_outputs,
)


def _print_validation(result: object) -> int:
    for warning in getattr(result, "warnings", ()):
        print(f"warning: {warning}", file=sys.stderr)
    for error in getattr(result, "errors", ()):
        print(f"error: {error}", file=sys.stderr)
    return 0 if getattr(result, "ok", False) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="validate source and reviewed-decision records")

    scan_parser = sub.add_parser("scan", help="scan watched GitHub repositories")
    scan_parser.add_argument("--mode", choices=("daily", "deep"), default="daily")
    scan_parser.add_argument("--days", type=int, default=30)
    scan_parser.add_argument("--token-env", default="GITHUB_TOKEN")
    scan_parser.add_argument("--output-json", type=Path, required=True)
    scan_parser.add_argument("--output-markdown", type=Path, required=True)
    scan_parser.add_argument("--issue-body", type=Path, required=True)

    render_parser = sub.add_parser("render", help="render Markdown from a saved snapshot")
    render_parser.add_argument("--input", type=Path, required=True)
    render_parser.add_argument("--output", type=Path, required=True)

    snapshot_parser = sub.add_parser("validate-snapshot", help="validate a saved scan snapshot")
    snapshot_parser.add_argument("--input", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "validate":
            return _print_validation(validate_repository(root))
        if args.command == "scan":
            token = os.environ.get(args.token_env)
            snapshot = scan(root=root, token=token, days=args.days, mode=args.mode)
            validation = validate_snapshot(snapshot, root)
            if not validation.ok:
                return _print_validation(validation)
            write_outputs(
                snapshot,
                root=root,
                output_json=args.output_json,
                output_markdown=args.output_markdown,
                issue_body=args.issue_body,
            )
            print(
                f"wrote {snapshot['summary']['candidate_count']} candidates from "
                f"{snapshot['summary']['source_count']} sources"
            )
            return 0
        if args.command == "render":
            snapshot = json.loads(args.input.read_text(encoding="utf-8"))
            validation = validate_snapshot(snapshot, root)
            if not validation.ok:
                return _print_validation(validation)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(render_markdown(snapshot), encoding="utf-8")
            return 0
        if args.command == "validate-snapshot":
            snapshot = json.loads(args.input.read_text(encoding="utf-8"))
            return _print_validation(validate_snapshot(snapshot, root))
    except (OSError, json.JSONDecodeError, UpstreamError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
