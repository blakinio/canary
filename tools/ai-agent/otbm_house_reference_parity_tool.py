from __future__ import annotations

import argparse
from pathlib import Path

from otbm_house_reference_parity import (
    DEFAULT_MAX_HOUSES,
    DEFAULT_MAX_JSON_BYTES,
    DEFAULT_MAX_MAPPINGS,
    HouseReferenceParityError,
    build_parity,
    derive_resolver,
    write_output,
)


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--client-manifest", type=Path, required=True)
    parser.add_argument("--staticdata-index", type=Path, required=True)
    parser.add_argument("--staticmapdata-index", type=Path, required=True)
    parser.add_argument("--world-index", type=Path, required=True)
    parser.add_argument("--world-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-json-bytes", type=int, default=DEFAULT_MAX_JSON_BYTES)
    parser.add_argument("--max-houses", type=int, default=DEFAULT_MAX_HOUSES)
    parser.add_argument("--overwrite", action="store_true")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic TCR-005 house-ID resolver and parity evidence.")
    sub = parser.add_subparsers(dest="command", required=True)
    resolver_parser = sub.add_parser(
        "derive-resolver",
        help="derive explicit one-to-one house-ID mappings from exact StaticData registry positions and World Index house tiles",
    )
    _common(resolver_parser)
    resolver_parser.add_argument("--review-id", required=True)
    resolver_parser.add_argument("--review-statement", required=True)

    parity_parser = sub.add_parser("parity", help="build canary-otbm-house-reference-parity-v1")
    _common(parity_parser)
    parity_parser.add_argument("--resolver", type=Path, required=True)
    parity_parser.add_argument("--max-mappings", type=int, default=DEFAULT_MAX_MAPPINGS)
    args = parser.parse_args()

    try:
        if args.command == "derive-resolver":
            payload, protected = derive_resolver(
                client_manifest_path=args.client_manifest,
                staticdata_index_path=args.staticdata_index,
                staticmapdata_index_path=args.staticmapdata_index,
                world_index_path=args.world_index,
                world_manifest_path=args.world_manifest,
                review_id=args.review_id,
                review_statement=args.review_statement,
                max_json_bytes=args.max_json_bytes,
                max_houses=args.max_houses,
            )
        else:
            payload, protected = build_parity(
                client_manifest_path=args.client_manifest,
                staticdata_index_path=args.staticdata_index,
                staticmapdata_index_path=args.staticmapdata_index,
                world_index_path=args.world_index,
                world_manifest_path=args.world_manifest,
                resolver_path=args.resolver,
                max_json_bytes=args.max_json_bytes,
                max_houses=args.max_houses,
                max_mappings=args.max_mappings,
            )
        write_output(args.output, payload, protected_inputs=protected, overwrite=args.overwrite)
    except (HouseReferenceParityError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
