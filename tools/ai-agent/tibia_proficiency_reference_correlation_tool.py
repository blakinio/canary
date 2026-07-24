#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tibia_proficiency_reference_correlation import (
    DEFAULT_MAX_JSON_BYTES,
    ProficiencyReferenceCorrelationError,
    build_canary_evidence,
    build_correlation,
    derive_resolver,
    load_inputs,
    write_json,
)


def _add_common_inputs(parser: argparse.ArgumentParser, *, resolver: bool = False) -> None:
    parser.add_argument("--proficiency-index", type=Path, required=True)
    parser.add_argument("--appearances-index", type=Path, required=True)
    parser.add_argument("--canary-evidence", type=Path, required=True)
    if resolver:
        parser.add_argument("--resolver", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-json-bytes", type=int, default=DEFAULT_MAX_JSON_BYTES)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build deterministic TCR-007 proficiency reference evidence.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser("inventory", help="Build compact Canary proficiency evidence.")
    inventory.add_argument("--repository-root", type=Path, default=Path.cwd())
    inventory.add_argument("--output", type=Path, required=True)
    inventory.add_argument("--overwrite", action="store_true")

    resolver_parser = subparsers.add_parser("derive-resolver", help="Derive reviewed exact proficiency mappings.")
    _add_common_inputs(resolver_parser)
    resolver_parser.add_argument("--review-id", required=True)
    resolver_parser.add_argument("--review-statement", required=True)

    correlation_parser = subparsers.add_parser("correlate", help="Build the read-only proficiency correlation report.")
    _add_common_inputs(correlation_parser, resolver=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            report = build_canary_evidence(args.repository_root)
            write_json(args.output, report, overwrite=args.overwrite)
            return 0

        loaded = load_inputs(
            proficiency_index_path=args.proficiency_index,
            appearances_index_path=args.appearances_index,
            canary_evidence_path=args.canary_evidence,
            resolver_path=getattr(args, "resolver", None),
            max_json_bytes=args.max_json_bytes,
        )
        (
            proficiency,
            proficiency_sha,
            proficiency_path,
            appearances,
            appearances_sha,
            appearances_path,
            evidence,
            evidence_sha,
            evidence_path,
            resolver_loaded,
        ) = loaded
        protected = [proficiency_path, appearances_path, evidence_path]
        if args.command == "derive-resolver":
            report = derive_resolver(
                proficiency_index=proficiency,
                proficiency_index_sha256=proficiency_sha,
                appearances_index=appearances,
                appearances_index_sha256=appearances_sha,
                canary_evidence=evidence,
                canary_evidence_sha256=evidence_sha,
                review_id=args.review_id,
                review_statement=args.review_statement,
            )
        else:
            assert resolver_loaded is not None
            resolver, resolver_sha, resolver_path = resolver_loaded
            protected.append(resolver_path)
            report = build_correlation(
                proficiency_index=proficiency,
                proficiency_index_sha256=proficiency_sha,
                appearances_index=appearances,
                appearances_index_sha256=appearances_sha,
                canary_evidence=evidence,
                canary_evidence_sha256=evidence_sha,
                resolver=resolver,
                resolver_sha256=resolver_sha,
            )
        write_json(args.output, report, protected_inputs=protected, overwrite=args.overwrite)
        return 0
    except (OSError, ValueError, ProficiencyReferenceCorrelationError) as exc:
        print(f"TCR-007 proficiency reference correlation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
