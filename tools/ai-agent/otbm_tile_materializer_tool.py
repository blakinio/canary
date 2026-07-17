from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_tile_materializer import materialize_tile_replacements


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replace reviewed complete raw OTBM tile subtrees at exact same coordinates in a create-new map copy."
    )
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--current-map", type=Path, required=True)
    parser.add_argument("--donor-map", type=Path, required=True)
    parser.add_argument("--scanner", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--current-index", type=Path, required=True)
    parser.add_argument("--current-manifest", type=Path, required=True)
    parser.add_argument("--donor-index", type=Path, required=True)
    parser.add_argument("--donor-manifest", type=Path, required=True)
    parser.add_argument("--output-map", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = materialize_tile_replacements(
            artifact_root=args.artifact_root,
            current_map_path=args.current_map,
            donor_map_path=args.donor_map,
            scanner_path=args.scanner,
            approval_path=args.approval,
            current_index_path=args.current_index,
            current_manifest_path=args.current_manifest,
            donor_index_path=args.donor_index,
            donor_manifest_path=args.donor_manifest,
            output_map_path=args.output_map,
            evidence_dir=args.evidence_dir,
            timeout_seconds=args.timeout_seconds,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
