#!/usr/bin/env python3
"""Validate and generate Real Tibia evidence contracts and factual indexes."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_tibia_evidence_lib import Corpus, EvidenceError, ROOT, write_generated


def parse_date(value: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    return parsed


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--root", type=Path, default=ROOT)
    commands = root.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--as-of", type=parse_date)
    generate = commands.add_parser("generate")
    generate.add_argument("--check", action="store_true")
    generate.add_argument("--as-of", type=parse_date)
    show = commands.add_parser("show-index")
    show.add_argument("--as-of", type=parse_date, required=True)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        corpus = Corpus.load(args.root)
        if args.command == "validate":
            result = corpus.validate(args.as_of)
            for diagnostic in result.warnings:
                print(f"warning: {diagnostic.render()}", file=sys.stderr)
            for diagnostic in result.errors:
                print(f"error: {diagnostic.render()}", file=sys.stderr)
            if not result.ok:
                return 1
            print(
                "evidence corpus valid "
                f"({len(corpus.evidence_documents)} evidence, "
                f"{len(corpus.request_documents)} requests, "
                f"{sum(len(doc.value.get('entries', [])) for doc in corpus.history_documents)} history records)"
            )
            return 0
        if args.command == "generate":
            result = corpus.validate(args.as_of)
            # Missing/drift diagnostics are expected to be repaired by generation,
            # but all source-contract errors remain fail-closed.
            repairable = {
                "RTEC-GENERATED-INDEX-MISSING",
                "RTEC-GENERATED-INDEX-DRIFT",
                "RTEC-MODULE-INDEX-MISSING",
                "RTEC-MODULE-INDEX-DRIFT",
            }
            blocking = [item for item in result.errors if item.code not in repairable]
            if blocking:
                for diagnostic in blocking:
                    print(f"error: {diagnostic.render()}", file=sys.stderr)
                return 1
            return write_generated(corpus, check=args.check, as_of=args.as_of)
        if args.command == "show-index":
            result = corpus.validate(args.as_of)
            blocking = [item for item in result.errors if item.code not in {"RTEC-GENERATED-INDEX-MISSING", "RTEC-GENERATED-INDEX-DRIFT", "RTEC-MODULE-INDEX-MISSING", "RTEC-MODULE-INDEX-DRIFT"}]
            if blocking:
                for diagnostic in blocking:
                    print(f"error: {diagnostic.render()}", file=sys.stderr)
                return 1
            print(json.dumps(corpus.generated_indexes(args.as_of), indent=2, sort_keys=True, ensure_ascii=False))
            return 0
    except EvidenceError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
