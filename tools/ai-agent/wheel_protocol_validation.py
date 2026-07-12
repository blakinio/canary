#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


class ProtocolAuditError(ValueError):
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
    raise ProtocolAuditError("unbalanced braces")


def extract_function(text: str, owner: str, name: str) -> str:
    match = re.search(
        rf"\b{re.escape(owner)}::{re.escape(name)}\s*\([^;]*?\)\s*(?:const\s*)?\{{",
        text,
        flags=re.MULTILINE,
    )
    if not match:
        raise ProtocolAuditError(f"function not found: {owner}::{name}")
    opening = text.find("{", match.start())
    return text[opening + 1 : find_matching_brace(text, opening)]


def parse_uint8_array_size(text: str, member: str) -> int:
    match = re.search(
        rf"std::array\s*<\s*uint8_t\s*,\s*(\d+)\s*>\s*{re.escape(member)}\b",
        text,
    )
    if not match:
        raise ProtocolAuditError(f"array not found: {member}")
    return int(match.group(1))


def has_bounds_check(body: str, variable: str) -> bool:
    return bool(
        re.search(rf"\b{re.escape(variable)}\b\s*(?:>=|>|<|<=)\s*[^;]+", body)
        or re.search(rf"[^;]+\s*(?:>=|>|<|<=)\s*\b{re.escape(variable)}\b", body)
        or re.search(rf"(?:validate|isValid)[A-Za-z0-9_]*\s*\([^)]*\b{re.escape(variable)}\b", body)
    )


def has_revealed_cap(body: str, maximum: int) -> bool:
    return str(maximum) in body or bool(
        re.search(r"(?:m_revealedGems|revealedGems|getRevealedGems)[^;]*(?:>=|>|==)", body)
    )


def finding(code: str, message: str, **evidence: Any) -> dict[str, Any]:
    return {"severity": "error", "code": code, "message": message, "evidence": evidence}


def audit_sources(
    protocolgame: str,
    game: str,
    player_cpp: str,
    player_hpp: str,
    maximum_revealed: int = 225,
) -> dict[str, Any]:
    current = extract_function(protocolgame, "ProtocolGame", "parseWheelGemAction")
    legacy = extract_function(game, "Game", "playerWheelGemAction")
    reveal = extract_function(player_cpp, "PlayerWheel", "revealGem")
    improve = extract_function(player_cpp, "PlayerWheel", "improveGemGrade")

    profiles = {"current": (current, "position"), "legacy": (legacy, "pos")}
    cap_guards = {name: has_revealed_cap(body, maximum_revealed) for name, (body, _) in profiles.items()}
    runtime_cap = has_revealed_cap(reveal, maximum_revealed)

    basic_size = parse_uint8_array_size(player_hpp, "m_basicGrades")
    supreme_size = parse_uint8_array_size(player_hpp, "m_supremeGrades")
    runtime_indexes_before_check = min(
        (position for position in (improve.find("m_basicGrades[pos]"), improve.find("m_supremeGrades[pos]")) if position >= 0),
        default=-1,
    ) >= 0 and not has_bounds_check(improve, "pos")
    position_guards = {
        name: has_bounds_check(body, variable)
        for name, (body, variable) in profiles.items()
        if "improveGemGrade" in body
    }

    findings: list[dict[str, Any]] = []
    unguarded_cap = sorted(name for name, guarded in cap_guards.items() if not guarded)
    if not runtime_cap and unguarded_cap:
        findings.append(
            finding(
                "revealed-gem-cap-unenforced-all-profiles",
                "Neither PlayerWheel::revealGem() nor all supported Gem Atelier protocol profiles enforce the revealed-gem maximum.",
                maximum=maximum_revealed,
                unguardedProfiles=unguarded_cap,
            )
        )

    unguarded_position = sorted(name for name, guarded in position_guards.items() if not guarded)
    if runtime_indexes_before_check and unguarded_position:
        findings.append(
            finding(
                "grade-position-unvalidated-all-profiles",
                "Both supported Gem Atelier protocol profiles can forward an arbitrary byte to fixed Grade arrays before runtime bounds validation.",
                unguardedProfiles=unguarded_position,
                inputMaximum=255,
                basicArraySize=basic_size,
                supremeArraySize=supreme_size,
            )
        )

    return {
        "format": "canary-wheel-protocol-audit-v1",
        "ok": not findings,
        "summary": {
            "profiles": sorted(profiles),
            "maximumRevealedGems": maximum_revealed,
            "basicGradeArraySize": basic_size,
            "supremeGradeArraySize": supreme_size,
            "findingCount": len(findings),
        },
        "guards": {
            "runtimeRevealCap": runtime_cap,
            "protocolRevealCap": cap_guards,
            "runtimeGradeBoundsBeforeRead": not runtime_indexes_before_check,
            "protocolGradePosition": position_guards,
        },
        "findings": findings,
    }


def audit_repository(root: Path, maximum_revealed: int = 225) -> dict[str, Any]:
    def read(relative: str) -> str:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        return path.read_text(encoding="utf-8")

    return audit_sources(
        read("src/server/network/protocol/protocolgame.cpp"),
        read("src/game/game.cpp"),
        read("src/creatures/players/components/wheel/player_wheel.cpp"),
        read("src/creatures/players/components/wheel/player_wheel.hpp"),
        maximum_revealed,
    )


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Wheel Gem Atelier protocol boundary audit",
        "",
        f"- profiles: **{', '.join(summary['profiles'])}**",
        f"- revealed-gem maximum: **{summary['maximumRevealedGems']}**",
        f"- Grade arrays: **{summary['basicGradeArraySize']} / {summary['supremeGradeArraySize']}**",
        f"- findings: **{summary['findingCount']}**",
        "",
        "## Findings",
        "",
    ]
    lines.extend(f"- **{item['code']}** — {item['message']}" for item in report["findings"])
    if not report["findings"]:
        lines.append("No findings.")
    lines.extend(["", "Static caller-boundary evidence does not replace malformed-packet runtime testing.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit current and legacy Wheel Gem Atelier protocol boundaries")
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--maximum-revealed", type=int, default=225)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args()
    try:
        report = audit_repository(args.repository_root.resolve(), args.maximum_revealed)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(render_markdown(report), encoding="utf-8")
    except (ProtocolAuditError, FileNotFoundError, OSError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    print(json.dumps(report["summary"], indent=2))
    return 0 if report["ok"] or args.allow_findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
