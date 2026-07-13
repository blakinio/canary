from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_reachability import (
    DEFAULT_MAX_NODES,
    DEFAULT_SAMPLE_LIMIT,
    Bounds,
    ReachabilityError,
    build_report,
    parse_position,
    tile_evidence,
    load_appearances,
    write_json_atomic,
)
from otbm_world_index import WorldIndex, WorldIndexError


def _position(value: str) -> tuple[int, int, int]:
    try:
        return parse_position(value)
    except ReachabilityError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("world_index", type=Path, help="Existing .widx file built by the OTBM World Index tool")
    parser.add_argument("appearances_index", type=Path, help="canary-appearances-index-v1 JSON")
    parser.add_argument("--movement-catalog", type=Path, help="Reviewed canary-otbm-movement-catalog-v1 JSON")
    parser.add_argument("--region-from", dest="region_from", type=_position)
    parser.add_argument("--region-to", dest="region_to", type=_position)
    parser.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)
    parser.add_argument("--max-nodes", type=int, default=DEFAULT_MAX_NODES)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate OTBM teleport destinations and bounded reachability")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Audit indexed teleports and reviewed relative transitions")
    _add_common(audit)

    route = subparsers.add_parser("route", help="Validate one explicitly bounded start/goal route")
    _add_common(route)
    route.add_argument("--start", required=True, type=_position)
    route.add_argument("--goal", required=True, type=_position)

    tile = subparsers.add_parser("tile", help="Inspect conservative movement evidence for one tile")
    tile.add_argument("world_index", type=Path)
    tile.add_argument("appearances_index", type=Path)
    tile.add_argument("position", type=_position)
    tile.add_argument("--output", type=Path)
    tile.add_argument("--overwrite", action="store_true")

    return parser


def _bounds(args: argparse.Namespace) -> Bounds | None:
    if (args.region_from is None) != (args.region_to is None):
        raise ReachabilityError("--region-from and --region-to must be provided together")
    if args.region_from is None:
        return None
    return Bounds(args.region_from, args.region_to)


def _emit(payload: dict, output: Path | None, overwrite: bool) -> None:
    if output is None:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        write_json_atomic(output, payload, overwrite=overwrite)
        print(output.expanduser().resolve())


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "tile":
            appearances, provenance = load_appearances(args.appearances_index)
            with WorldIndex(args.world_index) as index:
                payload = {
                    "format": "canary-otbm-tile-movement-evidence-v1",
                    "worldIndex": str(args.world_index.expanduser().resolve()),
                    "appearances": provenance,
                    "tile": tile_evidence(index, appearances, args.position),
                }
            _emit(payload, args.output, args.overwrite)
            return 0

        bounds = _bounds(args)
        if args.command == "route" and bounds is None:
            raise ReachabilityError("route requires --region-from and --region-to")
        payload = build_report(
            args.world_index,
            args.appearances_index,
            movement_catalog_path=args.movement_catalog,
            bounds=bounds,
            start=args.start if args.command == "route" else None,
            goal=args.goal if args.command == "route" else None,
            sample_limit=args.sample_limit,
            max_nodes=args.max_nodes,
        )
        _emit(payload, args.output, args.overwrite)
        return 0
    except (ReachabilityError, WorldIndexError, FileNotFoundError, FileExistsError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
