from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_storage_graph import DEFAULT_SAMPLE_LIMIT, StorageGraphError, build_storage_graph, write_report


def _path(value: str) -> Path:
    return Path(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the deterministic read-only OTBM storage dependency graph from existing Phase 2 evidence."
    )
    parser.add_argument("--repository-root", type=_path, required=True, help="Repository root containing Phase 2 selected files")
    parser.add_argument("--quest-evidence", type=_path, required=True, help="canary-quest-map-evidence-v1 JSON")
    parser.add_argument("--quest-validation", type=_path, help="Optional canary-quest-map-validation-v1 JSON")
    parser.add_argument("--spawn-npc-evidence", type=_path, help="Optional canary-otbm-spawn-npc-evidence-v1 JSON")
    parser.add_argument("--spawn-npc-validation", type=_path, help="Optional canary-otbm-spawn-npc-validation-v1 JSON")
    parser.add_argument("--reachability", type=_path, help="Optional canary-otbm-reachability-v1 JSON")
    parser.add_argument("--sample-limit", type=int, default=DEFAULT_SAMPLE_LIMIT, help="Bound findings/unresolved samples")
    parser.add_argument("--output", type=_path, help="Write the report atomically instead of stdout")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing regular output file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = build_storage_graph(
            repository_root=args.repository_root,
            quest_evidence_path=args.quest_evidence,
            quest_validation_path=args.quest_validation,
            spawn_evidence_path=args.spawn_npc_evidence,
            spawn_validation_path=args.spawn_npc_validation,
            reachability_path=args.reachability,
            sample_limit=args.sample_limit,
        )
        if args.output:
            write_report(args.output, report, overwrite=args.overwrite)
        else:
            json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
            sys.stdout.write("\n")
    except (StorageGraphError, FileNotFoundError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
