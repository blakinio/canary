#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from otbm_world_index import (
    DEFAULT_LIMIT,
    WorldIndexError,
    build_world_index,
    index_summary,
    query_action,
    query_house_door,
    query_item,
    query_position,
    query_region,
    query_teleport_destination,
    query_unique,
)


def position(value: str) -> tuple[int, int, int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("position must use x,y,z")
    try:
        result = tuple(int(part.strip()) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("position must contain integers") from exc
    if not (0 <= result[0] <= 0xFFFF and 0 <= result[1] <= 0xFFFF and 0 <= result[2] <= 15):
        raise argparse.ArgumentTypeError("position is outside the OTBM coordinate range")
    return result  # type: ignore[return-value]


def locate_scanner(explicit: Path | None) -> Path:
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    environment = os.environ.get("OTBM_ITEM_AUDIT_SCANNER")
    if environment:
        candidates.append(Path(environment))
    module = Path(__file__).resolve().parent
    candidates.extend((module / "otbm_item_audit_scan", module / "otbm_item_audit_scan.exe"))
    for candidate in candidates:
        resolved = candidate.expanduser().resolve()
        if resolved.is_file():
            return resolved
    raise WorldIndexError("Native OTBM scanner was not found; compile otbm_item_audit_scan.cpp or pass --scanner")


def add_page(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--offset", type=int, default=0)


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Build and query a deterministic binary index of an OTBM world")
    commands = root.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="Build an index from an OTBM map")
    build.add_argument("map", type=Path)
    build.add_argument("--scanner", type=Path)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--manifest", type=Path)
    build.add_argument("--timeout", type=int, default=3600)
    build.add_argument("--overwrite", action="store_true")

    summary = commands.add_parser("summary")
    summary.add_argument("index", type=Path)
    summary.add_argument("--manifest", type=Path)

    item = commands.add_parser("item")
    item.add_argument("index", type=Path)
    item.add_argument("item_id", type=int)
    add_page(item)

    action = commands.add_parser("action")
    action.add_argument("index", type=Path)
    action.add_argument("action_id", type=int)
    add_page(action)

    unique = commands.add_parser("unique")
    unique.add_argument("index", type=Path)
    unique.add_argument("unique_id", type=int)
    add_page(unique)

    door = commands.add_parser("house-door")
    door.add_argument("index", type=Path)
    door.add_argument("house_door_id", type=int)
    add_page(door)

    teleport = commands.add_parser("teleport-destination")
    teleport.add_argument("index", type=Path)
    teleport.add_argument("destination", type=position)
    add_page(teleport)

    at = commands.add_parser("position")
    at.add_argument("index", type=Path)
    at.add_argument("position", type=position)

    region = commands.add_parser("region")
    region.add_argument("index", type=Path)
    region.add_argument("first", type=position)
    region.add_argument("second", type=position)
    add_page(region)
    region.add_argument("--tile-limit", type=int)
    region.add_argument("--tile-offset", type=int, default=0)
    return root


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "build":
            payload = build_world_index(
                map_path=args.map,
                scanner=locate_scanner(args.scanner),
                output=args.output,
                manifest_output=args.manifest,
                overwrite=args.overwrite,
                timeout_seconds=args.timeout,
            )
        elif args.command == "summary":
            payload = index_summary(args.index, args.manifest)
        elif args.command == "item":
            payload = query_item(args.index, args.item_id, limit=args.limit, offset=args.offset)
        elif args.command == "action":
            payload = query_action(args.index, args.action_id, limit=args.limit, offset=args.offset)
        elif args.command == "unique":
            payload = query_unique(args.index, args.unique_id, limit=args.limit, offset=args.offset)
        elif args.command == "house-door":
            payload = query_house_door(args.index, args.house_door_id, limit=args.limit, offset=args.offset)
        elif args.command == "teleport-destination":
            payload = query_teleport_destination(args.index, args.destination, limit=args.limit, offset=args.offset)
        elif args.command == "position":
            payload = query_position(args.index, args.position)
        elif args.command == "region":
            payload = query_region(
                args.index,
                args.first,
                args.second,
                limit=args.limit,
                offset=args.offset,
                tile_limit=args.tile_limit,
                tile_offset=args.tile_offset,
            )
        else:
            raise AssertionError(args.command)
    except (FileNotFoundError, OSError, ValueError, WorldIndexError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
