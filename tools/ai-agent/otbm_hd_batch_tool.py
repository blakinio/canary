#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_hd import HDPipelineError
from otbm_hd_batch import run_batch_external


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one external AI process for a complete OTBM HD sprite export")
    parser.add_argument("export", type=Path, help="Export directory containing manifest.json and original/")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--command",
        required=True,
        help="Command template using {input_dir}, {output_dir}, {manifest}, {scale}, and optionally {work_dir}",
    )
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument("--padding", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = run_batch_external(
            args.export,
            args.output,
            command=args.command,
            scale=args.scale,
            padding=args.padding,
            timeout_seconds=args.timeout,
            keep_work=args.keep_work,
            overwrite=args.overwrite,
        )
    except (FileNotFoundError, OSError, ValueError, HDPipelineError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
