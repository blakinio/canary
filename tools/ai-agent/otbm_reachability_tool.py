from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_reachability import (
    DEFAULT_EXECUTABLE_ROUTE_POSITIONS,
    DEFAULT_PATH_LIMIT,
    DEFAULT_SAMPLE_LIMIT,
    ReachabilityError,
    analyze_index_path,
    export_route_plan_index_path,
    write_report,
)


def parse_position(value: str) -> tuple[int, int, int]:
    try:
        parts = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("position must use x,y,z integers") from exc
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("position must use x,y,z")
    x, y, z = parts
    if not (0 <= x <= 65535 and 0 <= y <= 65535 and 0 <= z <= 15):
        raise argparse.ArgumentTypeError("position is outside the OTBM coordinate range")
    return x, y, z


def parse_route(value: str) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if ":" not in value:
        raise argparse.ArgumentTypeError("route must use startX,startY,startZ:goalX,goalY,goalZ")
    first, second = value.split(":", 1)
    return parse_position(first), parse_position(second)


def _add_common_inputs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("world_index", type=Path)
    parser.add_argument("--appearances", type=Path, required=True)
    parser.add_argument("--from", dest="lower", type=parse_position, required=True)
    parser.add_argument("--to", dest="upper", type=parse_position, required=True)
    parser.add_argument("--transitions", type=Path)
    parser.add_argument("--script-resolution", type=Path)
    parser.add_argument("--world-manifest", type=Path)
    parser.add_argument("--allow-diagonal", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate bounded OTBM teleport, floor-transition and reachability evidence")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze one explicit bounded region")
    _add_common_inputs(analyze)
    analyze.add_argument("--route", action="append", type=parse_route, default=[])
    analyze.add_argument("--origin", action="append", type=parse_position, default=[])
    analyze.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)
    analyze.add_argument("--path-limit", type=int, default=DEFAULT_PATH_LIMIT)
    analyze.add_argument("--fail-on", choices=("none", "warning", "error"), default="error")

    route_plan = subparsers.add_parser(
        "route-plan",
        help="Export one complete edge-aware route plan from the existing Reachability BFS",
    )
    _add_common_inputs(route_plan)
    route_plan.add_argument("--origin", type=parse_position, required=True)
    route_plan.add_argument("--destination", type=parse_position, required=True)
    route_plan.add_argument("--max-positions", type=int, default=DEFAULT_EXECUTABLE_ROUTE_POSITIONS)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "route-plan":
            plan = export_route_plan_index_path(
                index_path=args.world_index,
                appearances_path=args.appearances,
                lower=args.lower,
                upper=args.upper,
                origin=args.origin,
                destination=args.destination,
                transitions_path=args.transitions,
                script_resolution_path=args.script_resolution,
                world_manifest_path=args.world_manifest,
                allow_diagonal=args.allow_diagonal,
                max_positions=args.max_positions,
            )
            write_report(args.output, plan, overwrite=args.overwrite)
            print(
                json.dumps(
                    {
                        "format": plan["format"],
                        "routeStatus": plan["routeStatus"],
                        "executionStatus": plan["executionStatus"],
                        "distance": plan["distance"],
                        "output": str(args.output),
                    },
                    sort_keys=True,
                )
            )
            return 0

        report = analyze_index_path(
            index_path=args.world_index,
            appearances_path=args.appearances,
            lower=args.lower,
            upper=args.upper,
            routes=args.route,
            origins=args.origin,
            transitions_path=args.transitions,
            script_resolution_path=args.script_resolution,
            world_manifest_path=args.world_manifest,
            allow_diagonal=args.allow_diagonal,
            sample_limit=args.sample_limit,
            path_limit=args.path_limit,
        )
        write_report(args.output, report, overwrite=args.overwrite)
    except (FileNotFoundError, OSError, ReachabilityError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    counts = report["summary"]["findings"]["bySeverity"]
    print(
        json.dumps(
            {
                "format": report["format"],
                "ok": report["ok"],
                "routes": report["summary"]["routeStatusCounts"],
                "transitions": report["summary"]["transitionStatusCounts"],
                "findings": counts,
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    if args.fail_on == "error" and counts["error"]:
        return 1
    if args.fail_on == "warning" and (counts["error"] or counts["warning"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
