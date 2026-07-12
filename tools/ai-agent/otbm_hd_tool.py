#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_binary import OTBMError
from otbm_hd import (
    HDPipelineError,
    compare_renders,
    export_region_sprites,
    render_region_hd,
    upscale_export,
    validate_override_pack,
)
from otbm_scan import position_from_text
from otbm_sprites import SpriteSheetError


def _add_bounds(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--from", dest="from_position", type=position_from_text, required=True)
    parser.add_argument("--to", dest="to_position", type=position_from_text, required=True)
    parser.add_argument("--max-tiles", type=int, default=4096)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export, upscale, validate and render bounded OTBM sprite sets")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    export = subparsers.add_parser("export", help="Export sprites used by a bounded OTBM region")
    export.add_argument("map", type=Path)
    export.add_argument("assets", type=Path)
    export.add_argument("--output", type=Path, required=True)
    _add_bounds(export)

    upscale = subparsers.add_parser("upscale", help="Create an HD override pack from an export manifest")
    upscale.add_argument("export", type=Path, help="Export directory containing manifest.json and original/")
    upscale.add_argument("--output", type=Path, required=True)
    upscale.add_argument("--scale", type=int, default=2)
    upscale.add_argument("--padding", type=int, default=4)
    upscale.add_argument("--backend", choices=("nearest", "external"), default="nearest")
    upscale.add_argument(
        "--command",
        help="External command template using {input}, {output}, {scale} and optionally {sprite_id}; no shell is used",
    )
    upscale.add_argument("--timeout", type=int, default=120)
    upscale.add_argument("--keep-work", action="store_true")

    validate = subparsers.add_parser("validate", help="Validate an HD override pack against its source export")
    validate.add_argument("overrides", type=Path)
    validate.add_argument("--export", type=Path)
    validate.add_argument("--report", type=Path)

    render = subparsers.add_parser("render", help="Render a bounded OTBM region using validated HD overrides")
    render.add_argument("map", type=Path)
    render.add_argument("assets", type=Path)
    render.add_argument("overrides", type=Path)
    render.add_argument("--output", type=Path, required=True)
    render.add_argument("--export", type=Path, help="Source export directory; overrides the path recorded in the pack")
    render.add_argument("--report", type=Path)
    render.add_argument("--padding-tiles", type=int, default=4)
    _add_bounds(render)

    compare = subparsers.add_parser("compare", help="Place a nearest-scaled original beside an HD render")
    compare.add_argument("original", type=Path)
    compare.add_argument("hd", type=Path)
    compare.add_argument("--output", type=Path, required=True)
    compare.add_argument("--report", type=Path)
    compare.add_argument("--gap", type=int, default=16)
    return parser


def _emit(payload: dict, report_path: Path | None = None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if report_path is None:
        sys.stdout.write(text)
    else:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(text, encoding="utf-8")
        sys.stdout.write(text)


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command_name == "export":
            payload = export_region_sprites(
                args.map,
                args.assets,
                (args.from_position, args.to_position),
                args.output,
                max_tiles=args.max_tiles,
            )
            _emit(payload)
        elif args.command_name == "upscale":
            payload = upscale_export(
                args.export,
                args.output,
                scale=args.scale,
                padding=args.padding,
                backend=args.backend,
                command=args.command,
                timeout_seconds=args.timeout,
                keep_work=args.keep_work,
            )
            _emit(payload)
        elif args.command_name == "validate":
            payload = validate_override_pack(args.overrides, export_root=args.export)
            _emit(payload, args.report)
        elif args.command_name == "render":
            payload = render_region_hd(
                args.map,
                args.assets,
                (args.from_position, args.to_position),
                args.overrides,
                args.output,
                export_root=args.export,
                padding_tiles=args.padding_tiles,
                max_tiles=args.max_tiles,
            )
            _emit(payload, args.report)
        else:
            payload = compare_renders(args.original, args.hd, args.output, gap=args.gap)
            _emit(payload, args.report)
    except (FileNotFoundError, OSError, ValueError, OTBMError, SpriteSheetError, HDPipelineError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
