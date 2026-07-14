#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_reachability_types import ReachabilityError
from otbm_scan import position_from_text
from otbm_world_index import WorldIndexError

from otbm_semantic_diff import analyze_index_paths, write_report
from otbm_semantic_diff_render import build_render_manifest
from otbm_semantic_diff_types import DEFAULT_SAMPLE_LIMIT, SemanticDiffError


def _path(value: str) -> Path:
    return Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare canonical World Index inputs without reparsing or modifying OTBM maps."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    diff = subparsers.add_parser("diff", help="Build canary-otbm-semantic-diff-v1")
    diff.add_argument("--artifact-root", type=_path, required=True)
    diff.add_argument("--before-index", type=_path, required=True)
    diff.add_argument("--before-manifest", type=_path, required=True)
    diff.add_argument("--after-index", type=_path, required=True)
    diff.add_argument("--after-manifest", type=_path, required=True)
    diff.add_argument("--appearances", type=_path, help="Optional Phase 3 appearances evidence for ground/walkability diff")
    diff.add_argument("--before-map", type=_path, help="Optional real map used only for provenance hash verification")
    diff.add_argument("--after-map", type=_path, help="Optional real map used only for provenance hash verification")
    diff.add_argument("--from", dest="lower", type=position_from_text)
    diff.add_argument("--to", dest="upper", type=position_from_text)
    diff.add_argument("--quest-validation", type=_path)
    diff.add_argument("--script-resolution", type=_path)
    diff.add_argument("--reachability", type=_path)
    diff.add_argument("--spawn-npc", type=_path)
    diff.add_argument("--storage-graph", type=_path)
    diff.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT)
    diff.add_argument("--output", type=_path)
    diff.add_argument("--overwrite", action="store_true")

    render = subparsers.add_parser("render", help="Build or execute factual before/after/context renderer requests")
    render.add_argument("--artifact-root", type=_path, required=True)
    render.add_argument("--before-map", type=_path, required=True)
    render.add_argument("--after-map", type=_path, required=True)
    render.add_argument("--assets", type=_path, required=True)
    render.add_argument("--from", dest="lower", type=position_from_text, required=True)
    render.add_argument("--to", dest="upper", type=position_from_text, required=True)
    render.add_argument("--output-directory", type=_path, required=True)
    render.add_argument("--before-sha256")
    render.add_argument("--after-sha256")
    render.add_argument("--context-tiles", type=int, default=4)
    render.add_argument("--execute", action="store_true")
    render.add_argument("--manifest", type=_path, required=True)
    render.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "diff":
            report = analyze_index_paths(
                artifact_root=args.artifact_root,
                before_index_path=args.before_index,
                before_manifest_path=args.before_manifest,
                after_index_path=args.after_index,
                after_manifest_path=args.after_manifest,
                appearances_path=args.appearances,
                before_map_path=args.before_map,
                after_map_path=args.after_map,
                lower=args.lower,
                upper=args.upper,
                sample_limit=args.sample_limit,
                quest_validation_path=args.quest_validation,
                script_resolution_path=args.script_resolution,
                reachability_path=args.reachability,
                spawn_npc_path=args.spawn_npc,
                storage_graph_path=args.storage_graph,
            )
            if args.output:
                write_report(args.output, report, artifact_root=args.artifact_root, overwrite=args.overwrite)
            else:
                json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
                sys.stdout.write("\n")
        else:
            manifest = build_render_manifest(
                artifact_root=args.artifact_root,
                before_map_path=args.before_map,
                after_map_path=args.after_map,
                assets_root=args.assets,
                lower=args.lower,
                upper=args.upper,
                output_directory=args.output_directory,
                before_expected_sha256=args.before_sha256,
                after_expected_sha256=args.after_sha256,
                context_tiles=args.context_tiles,
                execute=args.execute,
                overwrite=args.overwrite,
            )
            write_report(args.manifest, manifest, artifact_root=args.artifact_root, overwrite=args.overwrite)
    except (SemanticDiffError, WorldIndexError, ReachabilityError, FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
