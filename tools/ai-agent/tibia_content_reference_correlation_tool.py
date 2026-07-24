from __future__ import annotations

import argparse
from pathlib import Path

from tibia_content_reference_correlation import (
    DEFAULT_MAX_JSON_BYTES,
    DEFAULT_MAX_RECORDS,
    ContentReferenceCorrelationError,
    build_correlation,
    build_owner_inventory,
    derive_resolver,
    write_output,
)


def _bounds(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--max-json-bytes", type=int, default=DEFAULT_MAX_JSON_BYTES)
    parser.add_argument("--max-records", type=int, default=DEFAULT_MAX_RECORDS)
    parser.add_argument("--overwrite", action="store_true")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic TCR-006 content-reference evidence")
    sub = parser.add_subparsers(dest="command", required=True)

    inventory = sub.add_parser("inventory", help="build a compact intermediate inventory through existing owner modules")
    inventory.add_argument("--repository-root", type=Path, default=Path("."))
    inventory.add_argument("--output", type=Path, required=True)
    inventory.add_argument("--overwrite", action="store_true")

    resolver = sub.add_parser("derive-resolver", help="derive reviewed safe mappings from exact source and owner evidence")
    resolver.add_argument("--staticdata-index", type=Path, required=True)
    resolver.add_argument("--owner-inventory", type=Path, required=True)
    resolver.add_argument("--review-id", required=True)
    resolver.add_argument("--review-statement", required=True)
    resolver.add_argument("--output", type=Path, required=True)
    _bounds(resolver)

    correlation = sub.add_parser("correlate", help="build canary-tibia-content-reference-correlation-v1")
    correlation.add_argument("--staticdata-index", type=Path, required=True)
    correlation.add_argument("--owner-inventory", type=Path, required=True)
    correlation.add_argument("--resolver", type=Path, required=True)
    correlation.add_argument("--output", type=Path, required=True)
    _bounds(correlation)

    args = parser.parse_args()
    try:
        if args.command == "inventory":
            payload = build_owner_inventory(args.repository_root)
            write_output(args.output, payload, protected_inputs=(), overwrite=args.overwrite)
        elif args.command == "derive-resolver":
            payload, protected = derive_resolver(
                staticdata_index_path=args.staticdata_index,
                owner_inventory_path=args.owner_inventory,
                review_id=args.review_id,
                review_statement=args.review_statement,
                max_json_bytes=args.max_json_bytes,
                max_records=args.max_records,
            )
            write_output(args.output, payload, protected_inputs=protected, overwrite=args.overwrite)
        else:
            payload, protected = build_correlation(
                staticdata_index_path=args.staticdata_index,
                owner_inventory_path=args.owner_inventory,
                resolver_path=args.resolver,
                max_json_bytes=args.max_json_bytes,
                max_records=args.max_records,
            )
            write_output(args.output, payload, protected_inputs=protected, overwrite=args.overwrite)
    except (ContentReferenceCorrelationError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
