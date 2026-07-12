#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


class TaskShopAuditError(ValueError):
    pass


def find_matching_brace(text: str, opening: int) -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise TaskShopAuditError("unbalanced braces")


def extract_cpp_function(text: str, owner: str, name: str) -> str:
    match = re.search(rf"\b{re.escape(owner)}::{re.escape(name)}\s*\([^;]*?\)\s*(?:const\s*)?\{{", text)
    if not match:
        raise TaskShopAuditError(f"function not found: {owner}::{name}")
    opening = text.find("{", match.start())
    return text[opening + 1 : find_matching_brace(text, opening)]


def extract_lua_function(text: str, name: str) -> str:
    match = re.search(rf"(?:local\s+)?function\s+{re.escape(name)}\s*\([^)]*\)", text)
    if not match:
        raise TaskShopAuditError(f"Lua function not found: {name}")
    start = match.end()
    next_function = re.search(r"\n(?:local\s+)?function\s+", text[start:])
    end = start + next_function.start() if next_function else len(text)
    return text[start:end]


def audit_sources(taskboard: str, player_wheel: str, maximum_points: int = 50) -> dict[str, Any]:
    shop = extract_lua_function(taskboard, "sendShopWindow")
    recv = extract_lua_function(taskboard, "onRecvbyte")
    extra = extract_cpp_function(player_wheel, "PlayerWheel", "getExtraPoints")

    empty_shop = bool(re.search(r"addByte\s*\(\s*0\s*\)\s*--\s*offer count", shop))
    shim_declared = "minimal official packet shim" in taskboard.lower() or "full\n-- task state, rewards, shop contents" in taskboard.lower()
    shop_buy_only_response = "ShopResponseActions[action]" in recv and not re.search(
        r"(?:wheel|promotion|extraPoints|removeTaskHuntingPoints|useTaskHuntingPoints)", recv,
        flags=re.IGNORECASE,
    )
    extra_points_path = bool(re.search(r"hunting.*task|task.*hunting", extra, flags=re.IGNORECASE))

    findings: list[dict[str, Any]] = []
    if empty_shop and shop_buy_only_response and not extra_points_path:
        findings.append(
            {
                "severity": "error",
                "code": "hunting-task-shop-wheel-points-missing",
                "message": "The official Taskboard shop exposes zero offers, ShopBuy has no purchase path, and PlayerWheel::getExtraPoints() has no Hunting Task source.",
                "evidence": {
                    "maximumReferencePoints": maximum_points,
                    "emptyOfferCount": True,
                    "shopBuyOnlyReturnsWindow": True,
                    "wheelExtraPointPath": False,
                    "shimDeclared": shim_declared,
                },
            }
        )

    return {
        "format": "canary-wheel-task-shop-audit-v1",
        "ok": not findings,
        "summary": {
            "maximumReferencePoints": maximum_points,
            "emptyOfferCount": empty_shop,
            "shopBuyOnlyReturnsWindow": shop_buy_only_response,
            "wheelExtraPointPath": extra_points_path,
            "findingCount": len(findings),
        },
        "findings": findings,
    }


def audit_repository(root: Path, maximum_points: int = 50) -> dict[str, Any]:
    taskboard = (root / "data/modules/scripts/taskboard/taskboard.lua").read_text(encoding="utf-8")
    player_wheel = (root / "src/creatures/players/components/wheel/player_wheel.cpp").read_text(encoding="utf-8")
    return audit_sources(taskboard, player_wheel, maximum_points)


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Wheel Hunting Task Shop audit",
        "",
        f"- reference maximum: **{summary['maximumReferencePoints']} Wheel points**",
        f"- empty shop: **{summary['emptyOfferCount']}**",
        f"- ShopBuy only returns window: **{summary['shopBuyOnlyReturnsWindow']}**",
        f"- Wheel extra-point path: **{summary['wheelExtraPointPath']}**",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- **{item['code']}** — {item['message']}" for item in report["findings"])
    if not report["findings"]:
        lines.append("No findings.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Hunting Task Shop Wheel Promotion Point availability")
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--maximum-points", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args()
    try:
        report = audit_repository(args.repository_root.resolve(), args.maximum_points)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(render_markdown(report), encoding="utf-8")
    except (TaskShopAuditError, FileNotFoundError, OSError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    print(json.dumps(report["summary"], indent=2))
    return 0 if report["ok"] or args.allow_findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
