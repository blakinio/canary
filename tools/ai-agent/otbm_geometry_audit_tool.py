#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_geometry_audit import GeometryAuditError, analyze_index_paths, write_report
from otbm_geometry_audit_render import build_render_manifest
from otbm_geometry_audit_types import resolve_artifact_path, write_json_atomic


def position_from_text(value: str) -> tuple[int, int, int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("position must be x,y,z")
    try:
        position = tuple(int(part.strip()) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("position must contain integers") from exc
    if not (0 <= position[0] <= 0xFFFF and 0 <= position[1] <= 0xFFFF and 0 <= position[2] <= 15):
        raise argparse.ArgumentTypeError("position is outside the OTBM coordinate range")
    return position  # type: ignore[return-value]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit bounded OTBM geometry using canonical World Index evidence")
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--appearances", type=Path, required=True)
    parser.add_argument("--from", dest="lower", type=position_from_text, required=True)
    parser.add_argument("--to", dest="upper", type=position_from_text, required=True)
    parser.add_argument("--rules", type=Path)
    parser.add_argument("--sample-limit", type=int, default=500)
    parser.add_argument("--orphan-max-tiles", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--render-manifest", type=Path)
    parser.add_argument("--map", type=Path)
    parser.add_argument("--assets", type=Path)
    parser.add_argument("--render-output-dir", type=Path)
    parser.add_argument("--render-radius", type=int, default=8)
    parser.add_argument("--max-render-requests", type=int, default=100)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = analyze_index_paths(
            artifact_root=args.artifact_root,
            index_path=args.index,
            manifest_path=args.manifest,
            appearances_path=args.appearances,
            lower=args.lower,
            upper=args.upper,
            rules_path=args.rules,
            sample_limit=args.sample_limit,
            orphan_max_tiles=args.orphan_max_tiles,
        )
        output = write_report(
            report,
            artifact_root=args.artifact_root,
            output_path=args.output,
            overwrite=args.overwrite,
        )
        render_output: str | None = None
        if args.render_manifest is not None:
            if args.map is None or args.assets is None or args.render_output_dir is None:
                raise GeometryAuditError(
                    "--render-manifest requires --map, --assets and --render-output-dir"
                )
            manifest = build_render_manifest(
                report,
                map_path=args.map,
                assets_path=args.assets,
                output_dir=args.render_output_dir,
                radius=args.render_radius,
                max_requests=args.max_render_requests,
            )
            render_path = resolve_artifact_path(
                args.artifact_root,
                args.render_manifest,
                label="geometry render manifest output",
                require_file=False,
            )
            write_json_atomic(manifest, render_path, overwrite=args.overwrite)
            render_output = str(render_path)
    except (FileNotFoundError, OSError, ValueError, GeometryAuditError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    summary = {
        "ok": report["ok"],
        "complete": report["complete"],
        "tiles": report["summary"]["tiles"],
        "placements": report["summary"]["placements"],
        "findings": report["summary"]["findings"]["total"],
        "output": str(output),
        "renderManifest": render_output,
    }
    sys.stdout.write(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
