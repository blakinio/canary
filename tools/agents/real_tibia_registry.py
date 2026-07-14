#!/usr/bin/env python3
"""CLI for the Real Tibia module registry."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_tibia_registry_lib import ROOT, Registry, RegistryError, ValidationResult, write_generated


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--root", type=Path, default=ROOT)
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("validate")
    generate = commands.add_parser("generate")
    generate.add_argument("--check", action="store_true")
    generate.add_argument("--as-of", type=parse_date)
    module = commands.add_parser("module")
    module.add_argument("module_id")
    module.add_argument("--json", action="store_true")
    lookup = commands.add_parser("lookup-path")
    lookup.add_argument("path")
    stale = commands.add_parser("stale")
    stale.add_argument("--as-of", type=parse_date)
    stale.add_argument("--only-stale", action="store_true")
    affected = commands.add_parser("affected")
    affected.add_argument("--base", required=True)
    affected.add_argument("--head", default="HEAD")
    return root


def print_validation(result: ValidationResult) -> int:
    for message in result.warnings:
        print(f"warning: {message}", file=sys.stderr)
    for message in result.errors:
        print(f"error: {message}", file=sys.stderr)
    if result.ok:
        print(f"registry valid ({len(result.warnings)} warning(s))")
        return 0
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        registry = Registry.load(args.root.resolve())
        if args.command == "validate":
            return print_validation(registry.validate())
        if args.command == "generate":
            status = print_validation(registry.validate())
            return status or write_generated(registry, args.check, args.as_of)
        if args.command == "module":
            module = registry.modules.get(args.module_id)
            if module is None:
                raise RegistryError(f"unknown module {args.module_id!r}")
            if args.json:
                print(json.dumps(module, indent=2, sort_keys=True, ensure_ascii=False))
            else:
                print(f"{module['name']} ({args.module_id})")
                print(f"category: {module['category']}")
                print(f"lifecycle: {module['lifecycle']['status']}")
                print(f"description: {module['description']}")
                print("depends_on: " + (", ".join(module["relationships"]["depends_on"]) or "none"))
                print("interacts_with: " + (", ".join(module["relationships"]["interacts_with"]) or "none"))
            return 0
        if args.command == "lookup-path":
            matches = registry.matched_modules(args.path)
            for module_id, bucket, pattern in matches:
                print(f"{module_id}\t{bucket}\t{pattern}")
            return 0 if matches else 1
        if args.command == "stale":
            rows = registry.stale_rows(args.as_of)
            for row in rows:
                if not args.only_stale or row["state"] != "current":
                    print(f"{row['module_id']}\t{row['state']}\t{row['age_days']}\t{row['last_inventory']}")
            return 0
        if args.command == "affected":
            command = ["git", "-C", str(registry.root), "diff", "--name-only", f"{args.base}...{args.head}", "--"]
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
            except (OSError, subprocess.CalledProcessError) as exc:
                raise RegistryError(f"cannot resolve affected files: {getattr(exc, 'stderr', '') or exc}") from exc
            for module_id in registry.affected_modules(line for line in result.stdout.splitlines() if line):
                print(module_id)
            return 0
    except RegistryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
