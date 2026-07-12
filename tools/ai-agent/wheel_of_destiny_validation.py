#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class WheelAuditError(ValueError):
    pass


@dataclass(frozen=True)
class SourceFile:
    key: str
    path: str


FILES = {
    "definitions": SourceFile("definitions", "src/creatures/players/components/wheel/wheel_definitions.hpp"),
    "player_header": SourceFile("player_header", "src/creatures/players/components/wheel/player_wheel.hpp"),
    "player": SourceFile("player", "src/creatures/players/components/wheel/player_wheel.cpp"),
    "gems": SourceFile("gems", "src/creatures/players/components/wheel/wheel_gems.cpp"),
    "enums": SourceFile("enums", "src/enums/player_wheel.hpp"),
    "io_header": SourceFile("io_header", "src/io/io_wheel.hpp"),
    "io": SourceFile("io", "src/io/io_wheel.cpp"),
    "config": SourceFile("config", "src/config/configmanager.cpp"),
}

WHEEL_CONFIG_KEYS = {
    "WHEEL_POINTS_PER_LEVEL": "pointsPerLevel",
    "WHEEL_MONK_QUEST_BONUS": "monkQuestBonus",
    "WHEEL_ATELIER_REVEAL_LESSER_COST": "revealLesser",
    "WHEEL_ATELIER_REVEAL_REGULAR_COST": "revealRegular",
    "WHEEL_ATELIER_REVEAL_GREATER_COST": "revealGreater",
    "WHEEL_ATELIER_ROTATE_LESSER_COST": "rotateLesser",
    "WHEEL_ATELIER_ROTATE_REGULAR_COST": "rotateRegular",
    "WHEEL_ATELIER_ROTATE_GREATER_COST": "rotateGreater",
}


def finding(severity: str, code: str, message: str, **evidence: Any) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "evidence": evidence}


def strip_cpp_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", text)


def safe_eval_int(expression: str) -> int:
    tree = ast.parse(expression.strip(), mode="eval")
    allowed = (
        ast.Expression,
        ast.Constant,
        ast.UnaryOp,
        ast.UAdd,
        ast.USub,
        ast.BinOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.FloorDiv,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.LShift,
        ast.RShift,
        ast.BitOr,
        ast.BitAnd,
    )
    if any(not isinstance(node, allowed) for node in ast.walk(tree)):
        raise WheelAuditError(f"unsupported integer expression: {expression!r}")
    value = eval(compile(tree, "<wheel-audit>", "eval"), {"__builtins__": {}}, {})
    if not isinstance(value, (int, float)) or int(value) != value:
        raise WheelAuditError(f"expression is not an integer: {expression!r}")
    return int(value)


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
    raise WheelAuditError("unbalanced braces")


def extract_block_after(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise WheelAuditError(f"pattern not found: {pattern}")
    opening = text.find("{", match.end() - 1)
    if opening < 0:
        raise WheelAuditError(f"opening brace not found after: {pattern}")
    closing = find_matching_brace(text, opening)
    return text[opening + 1 : closing]


def extract_function(text: str, name: str) -> str:
    pattern = rf"\b(?:[\w:<>,&*\s]+)\b(?:PlayerWheel|WheelModifierContext|IOWheel)::{re.escape(name)}\s*\([^;]*?\)\s*(?:const\s*)?\{{"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise WheelAuditError(f"function not found: {name}")
    opening = text.find("{", match.start())
    closing = find_matching_brace(text, opening)
    return text[opening + 1 : closing]


def parse_enum_values(text: str, enum_name: str) -> dict[str, int]:
    block = extract_block_after(
        strip_cpp_comments(text),
        rf"\benum(?:\s+class)?\s+{re.escape(enum_name)}\b[^{{]*\{{",
    )
    values: dict[str, int] = {}
    current = -1
    for raw in block.split(","):
        item = raw.strip()
        if not item:
            continue
        if "=" in item:
            name, expression = (part.strip() for part in item.split("=", 1))
            current = safe_eval_int(expression)
        else:
            name = item
            current += 1
        if not re.fullmatch(r"[A-Za-z_]\w*", name):
            raise WheelAuditError(f"invalid enum member in {enum_name}: {name!r}")
        values[name] = current
    return values


def parse_config_defaults(text: str) -> dict[str, int]:
    defaults: dict[str, int] = {}
    pattern = re.compile(
        r'loadIntConfig\s*\(\s*L\s*,\s*([A-Z0-9_]+)\s*,\s*"[^"]+"\s*,\s*([^)]+)\)\s*;'
    )
    for key, expression in pattern.findall(strip_cpp_comments(text)):
        if key in WHEEL_CONFIG_KEYS:
            defaults[WHEEL_CONFIG_KEYS[key]] = safe_eval_int(expression)
    return defaults


def parse_promotion_scrolls(text: str) -> list[dict[str, Any]]:
    block = extract_block_after(text, r"\bWheelOfDestinyPromotionScrolls\s*=\s*\{")
    rows = [
        {"itemId": int(item_id), "name": name, "points": int(points)}
        for item_id, name, points in re.findall(
            r'\{\s*(\d+)\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*\}', block
        )
    ]
    if not rows:
        raise WheelAuditError("no promotion scrolls parsed")
    return rows


def parse_grade_costs(text: str, function_name: str) -> dict[int, dict[str, int]]:
    body = extract_function(text, function_name)
    costs: dict[int, dict[str, int]] = {}
    for grade, gold, fragments in re.findall(
        r"case\s+(\d+)\s*:\s*return\s+std::make_tuple\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)",
        body,
        flags=re.DOTALL,
    ):
        costs[int(grade) + 1] = {"gold": int(gold), "fragments": int(fragments)}
    return costs


def parse_grade_multipliers(text: str) -> dict[int, float]:
    function = extract_function(text, "addStrategies")
    result = {1: 1.0}
    for internal_grade, multiplier in re.findall(
        r"grade\s*==\s*(\d+)\s*\)\s*\{\s*gradeMultiplier\s*=\s*([0-9.]+)",
        function,
        flags=re.DOTALL,
    ):
        result[int(internal_grade) + 1] = float(multiplier)
    return result


def duplicate_adjacency_checks(text: str) -> list[dict[str, Any]]:
    function = extract_function(text, "canPlayerSelectPointOnSlot")
    branch_re = re.compile(
        r"(?:if|else\s+if)\s*\(\s*slot\s*==\s*WheelSlots_t::(\w+)\s*\)\s*\{"
    )
    matches = list(branch_re.finditer(function))
    duplicates: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(function)
        body = function[start:end]
        neighbors = re.findall(r"canSelectSlotFullOrPartial\s*\(\s*WheelSlots_t::(\w+)", body)
        counts = Counter(neighbors)
        for neighbor, count in sorted(counts.items()):
            if count > 1:
                duplicates.append({"slot": match.group(1), "neighbor": neighbor, "count": count})
    return duplicates


def count_revelation_double_application(text: str) -> list[str]:
    supreme_start = text.find("void WheelModifierContext::addStrategies(WheelGemSupremeModifier_t")
    if supreme_start < 0:
        raise WheelAuditError("supreme addStrategies function not found")
    body = extract_function(text[supreme_start:], "addStrategies")
    case_re = re.compile(r"case\s+WheelGemSupremeModifier_t::(\w+)\s*:")
    matches = list(case_re.finditer(body))
    doubled: list[str] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        case_body = body[start:end]
        if "GemModifierRevelationStrategy" in case_body and "m_wheel.addRevelationBonus" in case_body:
            doubled.append(match.group(1))
    return doubled


def scan_wheel_files(root: Path, roots: Iterable[str] = ("src", "data", "data-otservbr-global")) -> list[str]:
    matched: list[str] = []
    pattern = re.compile(r"WheelOfDestiny|PlayerWheel|WheelGem|wheel-of-destiny|GemAtelier", re.IGNORECASE)
    for relative_root in roots:
        directory = root / relative_root
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.suffix.lower() not in {".cpp", ".hpp", ".h", ".lua", ".sql"} or not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if pattern.search(text):
                matched.append(path.relative_to(root).as_posix())
    return matched


def load_sources(root: Path) -> dict[str, str]:
    sources: dict[str, str] = {}
    for key, source in FILES.items():
        path = root / source.path
        if not path.is_file():
            raise FileNotFoundError(f"required Wheel source does not exist: {path}")
        sources[key] = path.read_text(encoding="utf-8")
    return sources


def load_baseline(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(baseline, dict) or "wheel" not in baseline or "atelier" not in baseline:
        raise WheelAuditError("reference baseline must contain wheel and atelier objects")
    return baseline


def compare_value(
    findings: list[dict[str, Any]],
    comparisons: dict[str, dict[str, Any]],
    key: str,
    expected: Any,
    actual: Any,
    severity: str = "error",
) -> None:
    matches = expected == actual
    comparisons[key] = {"expected": expected, "actual": actual, "matches": matches}
    if not matches:
        findings.append(
            finding(
                severity,
                "reference-baseline-mismatch",
                f"{key}: expected {expected!r}, actual {actual!r}.",
                key=key,
                expected=expected,
                actual=actual,
            )
        )


def audit_sources(sources: dict[str, str], baseline: dict[str, Any] | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    comparisons: dict[str, dict[str, Any]] = {}

    slots = parse_enum_values(sources["definitions"], "WheelSlots_t")
    thresholds_enum = parse_enum_values(sources["definitions"], "WheelStagePointsEnum_t")
    thresholds = [thresholds_enum[name] for name in ("ONE", "TWO", "THREE")]
    config = parse_config_defaults(sources["config"])
    scrolls = parse_promotion_scrolls(sources["player"])
    lesser_costs = parse_grade_costs(sources["player"], "getLesserGradeCost")
    greater_costs = parse_grade_costs(sources["player"], "getGreaterGradeCost")
    grade_multipliers = parse_grade_multipliers(sources["gems"])
    duplicates = duplicate_adjacency_checks(sources["player"])
    doubled_revelation = count_revelation_double_application(sources["gems"])

    if duplicates:
        findings.append(
            finding(
                "warning",
                "duplicate-adjacency-check",
                "At least one Wheel slot branch checks the same neighbour more than once; this can hide a missing edge.",
                duplicates=duplicates,
            )
        )

    if doubled_revelation:
        findings.append(
            finding(
                "error",
                "revelation-bonus-double-applied",
                "Revelation Mastery gem cases both enqueue GemModifierRevelationStrategy and call addRevelationBonus immediately; executeStrategies applies the queued value again.",
                modifiers=doubled_revelation,
                count=len(doubled_revelation),
            )
        )

    extra_points = extract_function(sources["player"], "getExtraPoints")
    slice_stage = extract_function(sources["player"], "getPlayerSliceStage")
    if "m_modsMaxGrade" not in extra_points:
        findings.append(
            finding(
                "error",
                "grade-iv-points-not-spendable",
                "Grade IV modifier count is not included in getExtraPoints(), so fully upgraded mods do not add spendable Promotion Points.",
            )
        )
    if "totalPoints += m_modsMaxGrade" in slice_stage:
        findings.append(
            finding(
                "error",
                "grade-iv-points-injected-into-every-domain",
                "The global Grade IV modifier count is added independently to every domain's Revelation threshold calculation.",
            )
        )
    if not re.search(r"task.*hunting|hunting.*task", extra_points, flags=re.IGNORECASE):
        findings.append(
            finding(
                "warning",
                "hunting-task-points-path-not-found",
                "getExtraPoints() has no visible Hunting Task Shop Promotion Point source.",
            )
        )

    reveal = extract_function(sources["player"], "revealGem")
    max_revealed = baseline.get("atelier", {}).get("maxRevealedGems") if baseline else 225
    if max_revealed and not (
        str(max_revealed) in reveal
        or re.search(r"m_revealedGems\.size\s*\(\s*\)\s*(?:>=|==|>)", reveal)
    ):
        findings.append(
            finding(
                "warning",
                "revealed-gem-cap-not-enforced-in-reveal",
                "revealGem() does not enforce the recorded maximum revealed-gem count; caller/protocol validation still requires review.",
                expectedMaximum=max_revealed,
            )
        )

    def ordered(body: str, first: str, second: str) -> bool:
        a, b = body.find(first), body.find(second)
        return a >= 0 and b >= 0 and a < b

    if ordered(reveal, "removeMoney", "removeItemCountById") and "addMoney" not in reveal:
        findings.append(
            finding(
                "warning",
                "reveal-operation-not-transactional",
                "revealGem() removes money before the gem item and contains no visible refund path if item removal fails.",
            )
        )

    improve = extract_function(sources["player"], "improveGemGrade")
    if ordered(improve, "removeMoney", "removeItemCountById") and "addMoney" not in improve:
        findings.append(
            finding(
                "warning",
                "grade-upgrade-not-transactional",
                "improveGemGrade() removes money before fragments and contains no visible refund path if fragment removal fails.",
            )
        )
    first_array_access = min(
        [position for position in (improve.find("m_basicGrades[pos]"), improve.find("m_supremeGrades[pos]")) if position >= 0],
        default=-1,
    )
    bounds_markers = [
        improve.find("m_basicGrades.size"),
        improve.find("m_supremeGrades.size"),
        improve.find("modsBasicPosition"),
        improve.find("modsSupremePosition"),
    ]
    first_bounds = min([position for position in bounds_markers if position >= 0], default=-1)
    if first_array_access >= 0 and (first_bounds < 0 or first_bounds > first_array_access):
        findings.append(
            finding(
                "warning",
                "grade-position-unvalidated",
                "improveGemGrade() indexes grade arrays with the client-supplied position before a visible bounds/membership check.",
            )
        )

    if baseline:
        wheel = baseline["wheel"]
        atelier = baseline["atelier"]
        compare_value(findings, comparisons, "wheel.sliceCount", wheel["sliceCount"], len(slots))
        compare_value(findings, comparisons, "wheel.revelationThresholds", wheel["revelationThresholds"], thresholds)
        compare_value(findings, comparisons, "wheel.pointsPerLevel", wheel["pointsPerLevel"], config.get("pointsPerLevel"))
        compare_value(findings, comparisons, "wheel.monkQuestBonus", wheel["monkQuestBonus"], config.get("monkQuestBonus"))
        compare_value(
            findings,
            comparisons,
            "wheel.promotionScrollPoints",
            wheel["promotionScrollPoints"],
            sum(row["points"] for row in scrolls),
        )
        expected_costs = atelier["costs"]
        actual_costs = {
            "reveal": {
                "lesser": config.get("revealLesser"),
                "regular": config.get("revealRegular"),
                "greater": config.get("revealGreater"),
            },
            "rotate": {
                "lesser": config.get("rotateLesser"),
                "regular": config.get("rotateRegular"),
                "greater": config.get("rotateGreater"),
            },
        }
        compare_value(findings, comparisons, "atelier.costs", expected_costs, actual_costs)
        compare_value(findings, comparisons, "atelier.basicGradeCosts", atelier["basicGradeCosts"], {str(k): v for k, v in lesser_costs.items()})
        compare_value(findings, comparisons, "atelier.supremeGradeCosts", atelier["supremeGradeCosts"], {str(k): v for k, v in greater_costs.items()})
        if expected_multipliers := atelier.get("gradeMultipliers"):
            actual_multipliers = {str(k): grade_multipliers.get(int(k)) for k in expected_multipliers}
            compare_value(
                findings,
                comparisons,
                "atelier.gradeMultipliers",
                expected_multipliers,
                actual_multipliers,
            )

    severities = Counter(item["severity"] for item in findings)
    return {
        "format": "canary-wheel-of-destiny-audit-v1",
        "ok": severities["error"] == 0,
        "summary": {
            "sliceCount": len(slots),
            "revelationThresholds": thresholds,
            "promotionScrollCount": len(scrolls),
            "promotionScrollPoints": sum(row["points"] for row in scrolls),
            "config": config,
            "doubledRevelationModifierCount": len(doubled_revelation),
            "duplicateAdjacencyCount": len(duplicates),
            "findingsBySeverity": dict(sorted(severities.items())),
        },
        "reference": baseline.get("source") if baseline else None,
        "comparisons": comparisons,
        "promotionScrolls": scrolls,
        "gradeCosts": {
            "basic": {str(k): v for k, v in lesser_costs.items()},
            "supreme": {str(k): v for k, v in greater_costs.items()},
        },
        "gradeMultipliers": {str(k): v for k, v in grade_multipliers.items()},
        "duplicateAdjacencyChecks": duplicates,
        "doubledRevelationModifiers": doubled_revelation,
        "findings": findings,
    }


def audit_repository(root: Path, baseline_path: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    baseline_file = baseline_path
    if baseline_file is not None and not baseline_file.is_absolute():
        baseline_file = root / baseline_file
    report = audit_sources(load_sources(root), load_baseline(baseline_file))
    report["sourceInventory"] = scan_wheel_files(root)
    report["summary"]["sourceFileCount"] = len(report["sourceInventory"])
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Canary Wheel of Destiny validation report",
        "",
        "## Decision",
        "",
        f"- static audit: **{'pass' if report['ok'] else 'findings require follow-up'}**",
        f"- slices / Revelation thresholds: **{summary['sliceCount']} / {summary['revelationThresholds']}**",
        f"- Promotion Scrolls: **{summary['promotionScrollCount']} items / {summary['promotionScrollPoints']} points**",
        f"- Wheel-related source files inventoried: **{summary.get('sourceFileCount', 'fixture-only')}**",
        "",
        "## External baseline",
        "",
    ]
    if report["comparisons"]:
        lines.extend(
            f"- {key}: expected `{item['expected']}`, actual `{item['actual']}` — **{'match' if item['matches'] else 'mismatch'}**"
            for key, item in report["comparisons"].items()
        )
    else:
        lines.append("No external baseline supplied.")
    lines += ["", "## Findings", ""]
    lines += [
        f"- **{item['severity']} / {item['code']}** — {item['message']}"
        for item in report["findings"]
    ] or ["No findings."]
    lines += [
        "",
        "## Evidence boundary",
        "",
        "This report is a deterministic static audit. A matching definition or value does not prove runtime behavior, persistence round-trip, client protocol compatibility, or correct interaction with combat and spell systems. Those require the runtime plan and focused integration tests.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Canary Wheel of Destiny and Gem Atelier implementation")
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--reference-baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args()
    try:
        report = audit_repository(args.repository_root, args.reference_baseline)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(render_markdown(report), encoding="utf-8")
    except (WheelAuditError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    print(json.dumps({"ok": report["ok"], "summary": report["summary"], "output": str(args.output.resolve())}, indent=2))
    return 0 if report["ok"] or args.allow_findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
