#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from otbm_script_resolution import DEFAULT_DATAPACKS, build_report, write_report


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve OTBM action/unique IDs to active Canary Lua/XML handlers")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Canary repository root")
    parser.add_argument("--item-scan", type=Path, required=True, help="Raw canary-otbm-item-scan-v1 JSON")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--datapack", action="append", dest="datapacks", help="Active datapack directory; repeatable")
    parser.add_argument("--map", type=Path, help="Optional source OTBM for SHA-256 provenance verification")
    parser.add_argument("--expected-map-sha256", help="Expected lowercase SHA-256; requires --map")
    parser.add_argument("--allow-unresolved", action="store_true", help="Return success when unresolved IDs remain")
    args = parser.parse_args()
    try:
        report = build_report(args.root.resolve(), args.item_scan.resolve(), args.datapacks or DEFAULT_DATAPACKS)
        if args.expected_map_sha256 and not args.map:
            raise ValueError("--expected-map-sha256 requires --map")
        if args.map:
            map_path = args.map.resolve()
            digest = sha256_path(map_path)
            if args.expected_map_sha256 and digest != args.expected_map_sha256.lower():
                raise ValueError(f"Map SHA-256 mismatch: expected {args.expected_map_sha256.lower()}, got {digest}")
            report["sources"]["map"].update(
                {
                    "path": str(map_path),
                    "size": map_path.stat().st_size,
                    "sha256": digest,
                }
            )
        write_report(args.output.resolve(), report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    print(json.dumps({"output": str(args.output.resolve()), "ok": report["ok"], "summary": report["summary"]}, indent=2))
    unresolved = report["summary"]["unresolvedIdentifiers"] + report["summary"]["partiallyResolvedIdentifiers"]
    return 0 if report["ok"] and (args.allow_unresolved or unresolved == 0) else 2


if __name__ == "__main__":
    raise SystemExit(main())
