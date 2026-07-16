from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_area_materializer import AreaMaterializerError, materialize_area_plan


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize approved same-coordinate complete OTBM TILE_AREA subtrees into a new verified map copy."
    )
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--current-map", type=Path, required=True)
    parser.add_argument("--donor-map", type=Path, required=True)
    parser.add_argument("--scanner", type=Path, required=True, help="Compiled otbm_area_materializer_scan.cpp binary")
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--current-index", type=Path, required=True)
    parser.add_argument("--current-manifest", type=Path, required=True)
    parser.add_argument("--donor-index", type=Path, required=True)
    parser.add_argument("--donor-manifest", type=Path, required=True)
    parser.add_argument("--output-map", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = materialize_area_plan(
            artifact_root=args.artifact_root,
            current_map_path=args.current_map,
            donor_map_path=args.donor_map,
            scanner_path=args.scanner,
            plan_path=args.plan,
            approval_path=args.approval,
            current_index_path=args.current_index,
            current_manifest_path=args.current_manifest,
            donor_index_path=args.donor_index,
            donor_manifest_path=args.donor_manifest,
            output_map_path=args.output_map,
            evidence_dir=args.evidence_dir,
            timeout_seconds=args.timeout_seconds,
        )
    except (AreaMaterializerError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "format": result["format"],
                "ok": result["ok"],
                "output": result["source"]["output"],
                "areaCount": result["selection"]["areaCount"],
                "evidenceDir": str(args.evidence_dir),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
