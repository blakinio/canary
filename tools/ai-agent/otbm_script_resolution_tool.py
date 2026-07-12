#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_script_resolution import ScriptAuditError, audit_from_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve OTBM actionId/uniqueId mechanics against active Canary Lua/XML handlers"
    )
    parser.add_argument("item_audit", type=Path, help="OTBM item-audit JSON containing mechanicPlacements")
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument(
        "--script-root",
        action="append",
        dest="script_roots",
        help="Active script root relative to the repository; repeatable (default: data and data-otservbr-global)",
    )
    parser.add_argument("--rules", type=Path, help="Optional manual runtime registration rules")
    parser.add_argument("--review-rules", type=Path, help="Optional review dispositions for unresolved identifiers")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--strict-runtime",
        action="store_true",
        help="Return an error while any runtime identifier remains unresolved, even if reviewed",
    )
    parser.add_argument("--allow-findings", action="store_true", help="Always return zero after writing a valid report")
    args = parser.parse_args()

    try:
        report = audit_from_files(
            item_audit_path=args.item_audit,
            repository_root=args.repository_root,
            script_roots=args.script_roots,
            output=args.output,
            rules_path=args.rules,
            review_rules_path=args.review_rules,
        )
    except (FileNotFoundError, OSError, ValueError, ScriptAuditError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2

    summary = report["summary"]
    sys.stdout.write(
        json.dumps(
            {
                "ok": report["ok"],
                "strictRuntimeOk": summary["runtimeUnresolvedIdentifiers"] == 0,
                "summary": summary,
                "output": str(args.output.resolve()),
            },
            indent=2,
        )
        + "\n"
    )
    if args.allow_findings:
        return 0
    if not report["ok"]:
        return 2
    if args.strict_runtime and summary["runtimeUnresolvedIdentifiers"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
