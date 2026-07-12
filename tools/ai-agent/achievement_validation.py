#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


class AchievementAuditError(ValueError):
    pass


@dataclass(frozen=True)
class AchievementDefinition:
    id: int
    name: str
    description: str
    secret: bool
    grade: int
    points: int
    line: int


@dataclass(frozen=True)
class AchievementReference:
    path: str
    line: int
    method: str
    kind: str
    identifier_type: str
    identifier: str | int | None
    raw_argument: str
    admin_only: bool


ENTRY_RE = re.compile(r"^\s*\[(\d+)\]\s*=\s*\{(.*)\}\s*,?\s*$")
CALL_RE = re.compile(
    r"[A-Za-z_][\w:.]*\s*:\s*(addAchievementProgress|addAchievement|hasAchievement|"
    r"removeAchievement|addAllAchievements|removeAllAchievements)\s*\(([^)]*)\)",
    re.DOTALL,
)
METHOD_KIND = {
    "addAchievement": "award",
    "addAchievementProgress": "progress",
    "hasAchievement": "check",
    "removeAchievement": "removal",
    "addAllAchievements": "bulk-award",
    "removeAllAchievements": "bulk-removal",
}
GRADE_POINTS = {1: range(1, 4), 2: range(4, 7), 3: range(7, 10), 4: range(10, 11)}
DEFAULT_ROOTS = ("data", "data-otservbr-global")


def finding(severity: str, code: str, message: str, **evidence: Any) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "evidence": evidence}


def split_top_level(value: str) -> list[str]:
    parts: list[str] = []
    start = depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char in "({[":
            depth += 1
        elif char in ")}]":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    if tail := value[start:].strip():
        parts.append(tail)
    return parts


def parse_scalar(token: str) -> str | int | bool:
    token = token.strip()
    if token in {"true", "false"}:
        return token == "true"
    if re.fullmatch(r"-?\d+", token):
        return int(token)
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {"'", '"'}:
        try:
            value = ast.literal_eval(token)
        except (SyntaxError, ValueError) as exc:
            raise AchievementAuditError(f"invalid quoted Lua scalar: {token}") from exc
        if isinstance(value, str):
            return value
    raise AchievementAuditError(f"unsupported Lua scalar: {token}")


def parse_registry_text(text: str) -> tuple[list[AchievementDefinition], list[dict[str, Any]]]:
    definitions: list[AchievementDefinition] = []
    findings: list[dict[str, Any]] = []
    seen_ids: dict[int, int] = {}
    seen_names: dict[str, int] = {}
    previous = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("--") or not (match := ENTRY_RE.match(line)):
            continue
        achievement_id, body = int(match.group(1)), match.group(2)
        fields: dict[str, str | int | bool] = {}
        for part in split_top_level(body):
            if "=" not in part:
                raise AchievementAuditError(f"line {line_number}: malformed field {part!r}")
            key, raw = (piece.strip() for piece in part.split("=", 1))
            if key in fields:
                raise AchievementAuditError(f"line {line_number}: duplicate field {key}")
            fields[key] = parse_scalar(raw)
        missing = sorted({"name", "description"} - fields.keys())
        if missing:
            findings.append(finding("error", "registry-missing-required-field", f"ID {achievement_id} misses {', '.join(missing)}.", line=line_number))
            continue
        name, description = fields["name"], fields["description"]
        secret, grade, points = fields.get("secret", False), fields.get("grade", 0), fields.get("points", 0)
        if not isinstance(name, str) or not isinstance(description, str) or not isinstance(secret, bool) or not isinstance(grade, int) or not isinstance(points, int):
            raise AchievementAuditError(f"line {line_number}: invalid field types")
        if achievement_id in seen_ids:
            findings.append(finding("error", "registry-duplicate-id", f"Duplicate ID {achievement_id}.", line=line_number, firstLine=seen_ids[achievement_id]))
        if name in seen_names:
            findings.append(finding("error", "registry-duplicate-name", f"Duplicate name {name!r}.", line=line_number, firstLine=seen_names[name]))
        if previous and achievement_id < previous:
            findings.append(finding("warning", "registry-id-order", f"ID {achievement_id} appears after {previous}.", line=line_number))
        if grade not in GRADE_POINTS or points not in GRADE_POINTS[grade]:
            findings.append(finding("error", "registry-grade-points-mismatch", f"ID {achievement_id} ({name}) has grade {grade} and {points} points.", line=line_number))
        seen_ids.setdefault(achievement_id, line_number)
        seen_names.setdefault(name, line_number)
        previous = achievement_id
        definitions.append(AchievementDefinition(achievement_id, name, description, secret, grade, points, line_number))
    if not definitions:
        raise AchievementAuditError("no achievement definitions found")
    ids = sorted({item.id for item in definitions})
    gaps = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
    if gaps:
        findings.append(finding("info", "registry-sparse-id-space", f"Registry has {len(gaps)} ID gaps.", ids=gaps))
    return definitions, findings


def audit_registry_helpers(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    hash_lines = [number for number, line in enumerate(text.splitlines(), 1) if "#ACHIEVEMENTS" in line and not line.lstrip().startswith("--")]
    if hash_lines:
        findings.append(finding("error", "sparse-table-length-operator", "Sparse ACHIEVEMENTS is consumed through Lua's length operator, so IDs after a gap can be skipped.", lines=hash_lines))
    for number, line in enumerate(text.splitlines(), 1):
        if "return achievement.secret" in line:
            findings.append(finding("error", "secret-helper-returns-input", "Game.isAchievementSecret returns metadata from its input instead of foundAchievement.", line=number))
        if "Invalid achievement" in line and "ach)" in line:
            findings.append(finding("error", "secret-helper-undefined-error-variable", "Game.isAchievementSecret formats an error with undefined variable 'ach'.", line=number))
    return findings


def literal_identifier(raw: str) -> tuple[str, str | int | None]:
    if not (token := raw.strip()):
        return "none", None
    try:
        value = parse_scalar(token)
    except AchievementAuditError:
        return "dynamic", None
    if isinstance(value, bool):
        return "dynamic", None
    return ("id", value) if isinstance(value, int) else ("name", value)


def scan_reference_text(text: str, path: str) -> list[AchievementReference]:
    normalized = path.replace("\\", "/")
    admin = "/talkactions/god/" in f"/{normalized}"
    references: list[AchievementReference] = []
    for match in CALL_RE.finditer(text):
        method, arguments = match.group(1), match.group(2)
        parts = split_top_level(arguments)
        raw = parts[0] if parts else ""
        identifier_type, identifier = literal_identifier(raw)
        if method in {"addAllAchievements", "removeAllAchievements"}:
            identifier_type, identifier = "none", None
        references.append(AchievementReference(normalized, text.count("\n", 0, match.start()) + 1, method, METHOD_KIND[method], identifier_type, identifier, raw, admin))
    return references


def iter_scripts(root: Path, script_roots: Iterable[str]) -> Iterable[Path]:
    seen: set[Path] = set()
    for relative in script_roots:
        directory = (root / relative).resolve()
        if not directory.is_dir():
            raise FileNotFoundError(f"script root does not exist: {directory}")
        for path in sorted(directory.rglob("*.lua")):
            if path not in seen:
                seen.add(path)
                yield path


def scan_references(root: Path, script_roots: Iterable[str], registry: Path) -> list[AchievementReference]:
    references: list[AchievementReference] = []
    for path in iter_scripts(root, script_roots):
        if path.resolve() == registry.resolve():
            continue
        relative = path.resolve().relative_to(root.resolve()).as_posix()
        references.extend(scan_reference_text(path.read_text(encoding="utf-8"), relative))
    return references


def load_baseline(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(baseline, dict) or not isinstance(baseline.get("counts"), dict):
        raise AchievementAuditError("reference baseline must contain object field 'counts'")
    return baseline


def compare_baseline(definitions: list[AchievementDefinition], baseline: dict[str, Any] | None) -> dict[str, Any] | None:
    if baseline is None:
        return None
    actual = {
        "listed": len(definitions),
        "common": sum(not item.secret for item in definitions),
        "secretDiscovered": sum(item.secret for item in definitions),
        "theoreticalPoints": sum(item.points for item in definitions),
    }
    expected = {key: baseline["counts"].get(key) for key in ("listed", "common", "secretDiscovered")}
    expected["theoreticalPoints"] = baseline.get("points", {}).get("theoretical")
    comparisons = {key: {"expected": value, "actual": actual[key], "matches": value == actual[key]} for key, value in expected.items() if value is not None}
    return {"source": baseline.get("source", {}), "comparisons": comparisons, "matches": all(item["matches"] for item in comparisons.values())}


def build_report(definitions: list[AchievementDefinition], registry_findings: list[dict[str, Any]], helper_findings: list[dict[str, Any]], references: list[AchievementReference], baseline: dict[str, Any] | None = None) -> dict[str, Any]:
    by_id, by_name = {item.id: item for item in definitions}, {item.name: item for item in definitions}
    findings = [*registry_findings, *helper_findings]
    resolved: defaultdict[int, list[AchievementReference]] = defaultdict(list)
    dynamic: list[AchievementReference] = []
    unknown: list[AchievementReference] = []
    for reference in references:
        if reference.identifier_type == "dynamic":
            dynamic.append(reference)
            continue
        if reference.identifier_type == "none":
            continue
        target = by_id.get(reference.identifier) if reference.identifier_type == "id" else by_name.get(reference.identifier)
        if target is None:
            unknown.append(reference)
            findings.append(finding("error", "unknown-static-achievement-reference", f"{reference.path}:{reference.line} references undefined achievement {reference.identifier!r}.", path=reference.path, line=reference.line))
        else:
            resolved[target.id].append(reference)
    rows: list[dict[str, Any]] = []
    dispositions: Counter[str] = Counter()
    for definition in sorted(definitions, key=lambda item: item.id):
        refs = resolved.get(definition.id, [])
        kinds = {ref.kind for ref in refs if not ref.admin_only}
        disposition = "direct-static-award" if "award" in kinds else "static-progress-path" if "progress" in kinds else "referenced-without-static-award" if kinds else "admin-only-static-reference" if refs else "no-direct-static-reference"
        dispositions[disposition] += 1
        rows.append({**asdict(definition), "disposition": disposition, "references": [asdict(ref) for ref in refs]})
    ids = sorted(by_id)
    gaps = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
    comparison = compare_baseline(definitions, baseline)
    if comparison and not comparison["matches"]:
        findings.append(finding("warning", "reference-baseline-mismatch", "Registry does not fully match the recorded external baseline.", comparison=comparison))
    severities = Counter(item["severity"] for item in findings)
    return {
        "format": "canary-achievement-audit-v1",
        "ok": severities["error"] == 0,
        "summary": {
            "registryCount": len(definitions), "minimumId": ids[0], "maximumId": ids[-1], "gapCount": len(gaps),
            "publicCount": sum(not item.secret for item in definitions), "secretCount": sum(item.secret for item in definitions),
            "pointTotal": sum(item.points for item in definitions), "referenceCount": len(references),
            "resolvedStaticReferenceCount": sum(map(len, resolved.values())), "unknownStaticReferenceCount": len(unknown),
            "dynamicReferenceCount": len(dynamic), "adminReferenceCount": sum(ref.admin_only for ref in references),
            "dispositions": dict(sorted(dispositions.items())), "findingsBySeverity": dict(sorted(severities.items())),
        },
        "baselineComparison": comparison, "gaps": gaps, "findings": findings,
        "dynamicReferences": [asdict(ref) for ref in dynamic], "unknownStaticReferences": [asdict(ref) for ref in unknown],
        "achievements": rows,
    }


def audit_repository(repository_root: Path, registry: Path, script_roots: Iterable[str] | None = None, reference_baseline: Path | None = None) -> dict[str, Any]:
    root = repository_root.resolve()
    registry = registry if registry.is_absolute() else root / registry
    text = registry.read_text(encoding="utf-8")
    definitions, registry_findings = parse_registry_text(text)
    baseline_path = reference_baseline if reference_baseline is None or reference_baseline.is_absolute() else root / reference_baseline
    return build_report(definitions, registry_findings, audit_registry_helpers(text), scan_references(root, tuple(script_roots or DEFAULT_ROOTS), registry), load_baseline(baseline_path))


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Canary achievement validation report", "", "## Decision", "",
        f"- audit: **{'pass' if report['ok'] else 'findings require follow-up'}**",
        f"- definitions: **{summary['registryCount']}**, IDs **{summary['minimumId']}..{summary['maximumId']}**, gaps **{summary['gapCount']}**",
        f"- public / secret / points: **{summary['publicCount']} / {summary['secretCount']} / {summary['pointTotal']}**",
        f"- API references / dynamic / undefined static: **{summary['referenceCount']} / {summary['dynamicReferenceCount']} / {summary['unknownStaticReferenceCount']}**", "",
    ]
    if comparison := report.get("baselineComparison"):
        lines += ["## External baseline", ""] + [f"- {key}: expected `{item['expected']}`, actual `{item['actual']}` — **{'match' if item['matches'] else 'mismatch'}**" for key, item in comparison["comparisons"].items()] + [""]
    lines += ["## Findings", ""]
    lines += [f"- **{item['severity']} / {item['code']}** — {item['message']}" for item in report["findings"]] or ["No findings."]
    lines += ["", "## Trigger coverage", ""] + [f"- {key}: {value}" for key, value in summary["dispositions"].items()]
    lines += ["", "## Evidence boundary", "", "A missing direct static call is not proof that an achievement is unobtainable. Dynamic tables, wrappers, quest state machines and engine-side paths require semantic or runtime review. The JSON artifact retains those references.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Canary achievement definitions and active Lua references")
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--registry", type=Path, default=Path("data/scripts/lib/register_achievements.lua"))
    parser.add_argument("--script-root", action="append", dest="script_roots")
    parser.add_argument("--reference-baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args()
    try:
        report = audit_repository(args.repository_root, args.registry, args.script_roots, args.reference_baseline)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(render_markdown(report), encoding="utf-8")
    except (AchievementAuditError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    print(json.dumps({"ok": report["ok"], "summary": report["summary"], "output": str(args.output.resolve())}, indent=2))
    return 0 if report["ok"] or args.allow_findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
