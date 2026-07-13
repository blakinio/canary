from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_spawn_npc import (
    DEFAULT_SAMPLE_LIMIT,
    SpawnNpcValidationError,
    scan_active_datapack,
    validate_paths,
    write_json,
)


def _position(value: str) -> tuple[int, int, int]:
    try:
        parts = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("position must be x,y,z") from exc
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("position must be x,y,z")
    return parts  # type: ignore[return-value]


def _add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canary Phase 4 static spawn, boss and NPC validator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="scan one explicitly selected active datapack")
    scan.add_argument("--datapack-root", required=True, type=Path)
    scan.add_argument("--monster-spawn", action="append", dest="monster_spawns")
    scan.add_argument("--npc-spawn", action="append", dest="npc_spawns")
    scan.add_argument("--monster-definition-glob", action="append", dest="monster_definition_globs")
    scan.add_argument("--npc-definition-glob", action="append", dest="npc_definition_globs")
    scan.add_argument("--dynamic-glob", action="append", dest="dynamic_globs")
    _add_output(scan)

    validate = subparsers.add_parser("validate", help="correlate evidence with World Index and Phase 3 reachability")
    validate.add_argument("evidence", type=Path)
    validate.add_argument("--world-index", required=True, type=Path)
    validate.add_argument("--reachability", required=True, type=Path)
    validate.add_argument("--from", dest="lower", required=True, type=_position)
    validate.add_argument("--to", dest="upper", required=True, type=_position)
    _add_output(validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "scan":
            report = scan_active_datapack(
                datapack_root=args.datapack_root,
                monster_spawn_files=args.monster_spawns or ("world/otservbr-monster.xml",),
                npc_spawn_files=args.npc_spawns or ("world/otservbr-npc.xml",),
                monster_definition_globs=args.monster_definition_globs or ("monster/**/*.lua",),
                npc_definition_globs=args.npc_definition_globs or ("npc/**/*.lua",),
                dynamic_source_globs=args.dynamic_globs or ("scripts/**/*.lua",),
                sample_limit=args.sample_limit,
            )
        else:
            report = validate_paths(
                evidence_path=args.evidence,
                world_index_path=args.world_index,
                reachability_path=args.reachability,
                lower=args.lower,
                upper=args.upper,
                sample_limit=args.sample_limit,
            )
        write_json(args.output, report, overwrite=args.overwrite)
        print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, SpawnNpcValidationError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
