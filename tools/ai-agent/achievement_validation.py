#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urljoin


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
REFERENCE_FORMAT = "canary-achievement-reference-catalog-v1"
AUDIT_FORMAT = "canary-achievement-audit-v2"
REVIEW_FORMAT = "canary-achievement-reviewed-evidence-v1"
ALLOWED_STATUSES = {
    "confirmed",
    "partially-confirmed",
    "definition-only",
    "handler-missing",
    "unresolved",
    "conflicting",
    "intentionally-unsupported",
}
REFERENCE_TABLE_HEADERS = [
    "Name",
    "ID",
    "Grade",
    "Secret?",
    "Premium",
    "Points",
    "Implemented",
    "Description",
    "Spoiler",
]
FANDOM_PAGE_URL = "https://tibia.fandom.com/wiki/Achievements"
FANDOM_BASE_URL = "https://tibia.fandom.com"


class _AchievementTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_target_table = False
        self.table_depth = 0
        self.current_row: list[dict[str, Any]] | None = None
        self.current_cell: dict[str, Any] | None = None
        self.current_link: dict[str, Any] | None = None
        self.rows: list[list[dict[str, Any]]] = []
        self.all_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "table":
            classes = set((attributes.get("class") or "").split())
            if not self.in_target_table and "achievements_title_table" in classes:
                self.in_target_table = True
                self.table_depth = 1
                return
            if self.in_target_table:
                self.table_depth += 1
        if not self.in_target_table:
            return
        if tag == "tr" and self.current_row is None:
            self.current_row = []
        elif tag in {"td", "th"} and self.current_row is not None and self.current_cell is None:
            self.current_cell = {"textParts": [], "links": []}
        elif tag == "a" and self.current_cell is not None:
            self.current_link = {
                "href": attributes.get("href") or "",
                "title": attributes.get("title") or "",
                "textParts": [],
            }
        elif tag == "br" and self.current_cell is not None:
            self.current_cell["textParts"].append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self.in_target_table:
            return
        if tag == "a" and self.current_link is not None and self.current_cell is not None:
            link = {
                "text": _normalize_space("".join(self.current_link["textParts"])),
                "title": _normalize_space(self.current_link["title"]),
                "url": _absolute_fandom_url(self.current_link["href"]),
            }
            if link["text"] or link["title"] or link["url"]:
                self.current_cell["links"].append(link)
            self.current_link = None
        elif tag in {"td", "th"} and self.current_cell is not None and self.current_row is not None:
            self.current_row.append(
                {
                    "text": _normalize_space("".join(self.current_cell["textParts"])),
                    "links": self.current_cell["links"],
                }
            )
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            if self.current_row:
                self.rows.append(self.current_row)
            self.current_row = None
        elif tag == "table":
            self.table_depth -= 1
            if self.table_depth <= 0:
                self.in_target_table = False
                self.table_depth = 0

    def handle_data(self, data: str) -> None:
        self.all_text.append(data)
        if self.current_cell is not None:
            self.current_cell["textParts"].append(data)
        if self.current_link is not None:
            self.current_link["textParts"].append(data)


def finding(severity: str, code: str, message: str, **evidence: Any) -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "evidence": evidence}


def _normalize_space(value: str) -> str:
    return " ".join(value.split())


def _absolute_fandom_url(href: str) -> str:
    if not href:
        return ""
    return urljoin(FANDOM_BASE_URL, href)


def _canonical_reference_name(value: str) -> str:
    return value.removesuffix(" (Achievement)")


def _parse_optional_int(value: str) -> int | None:
    stripped = value.strip()
    return int(stripped) if re.fullmatch(r"\d+", stripped) else None


def _parse_yes_no_unknown(value: str) -> bool | None:
    normalized = value.strip()
    if normalized == "✓":
        return True
    if normalized == "✗":
        return False
    if normalized in {"", "?"}:
        return None
    raise AchievementAuditError(f"unexpected yes/no value: {value!r}")


def _condition_kinds(text: str) -> list[str]:
    lowered = text.casefold()
    patterns = {
        "quest-or-task": r"\b(quest|task|mission|rank|faction|finish|finishing|complete|completing)\b",
        "combat": r"\b(kill|killing|slay|slaying|defeat|defeating|boss|battle|fight|fighting)\b",
        "collection": r"\b(collect|collecting|obtain|obtaining|find|finding|catch|catching|loot|pick up|picking up)\b",
        "item-or-interaction": r"\b(use|using|eat|eating|drink|drinking|play|playing|open|opening|cook|cooking|trigger|triggering)\b",
        "exploration": r"\b(discover|discovering|visit|visiting|enter|entering|travel|travelling|explore|exploring|map|marking)\b",
        "dialogue": r"\b(say|saying|speak|speaking|ask|asking|talk|talking)\b",
        "mount-taming": r"\b(tame|taming|mount)\b",
        "event-or-raid": r"\b(event|raid|world change)\b",
        "progress-threshold": r"\b(times|points|amount|number|consecutive|in a row)\b",
    }
    result = [kind for kind, pattern in patterns.items() if re.search(pattern, lowered)]
    return result or (["unresolved"] if not lowered else ["other"])


def _condition_numbers(text: str) -> list[str]:
    values: list[str] = []
    for match in re.finditer(r"(?<!\w)\d[\d,.]*(?!\w)", text):
        value = match.group(0).rstrip(".,")
        if value and value not in values:
            values.append(value)
    return values


def _condition_entities(links: list[dict[str, str]]) -> list[dict[str, str]]:
    entities: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for link in links:
        name = link.get("text") or link.get("title") or ""
        url = link.get("url") or ""
        key = (name, url)
        if not name or key in seen:
            continue
        seen.add(key)
        entities.append({"name": name, "url": url})
    return entities


def parse_reference_source_text(source_text: str, observed_at: str, source_url: str) -> dict[str, Any]:
    source_sha256 = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    page_id: int | None = None
    revision_id: int | None = None
    html = source_text
    stripped = source_text.lstrip()
    if stripped.startswith("{"):
        payload = json.loads(source_text)
        parsed = payload.get("parse")
        if not isinstance(parsed, dict) or not isinstance(parsed.get("text"), str):
            raise AchievementAuditError("MediaWiki parse payload must contain parse.text")
        html = parsed["text"]
        page_id = parsed.get("pageid") if isinstance(parsed.get("pageid"), int) else None
        revision_id = parsed.get("revid") if isinstance(parsed.get("revid"), int) else None

    parser = _AchievementTableParser()
    parser.feed(html)
    if not parser.rows:
        raise AchievementAuditError("achievement reference table was not found")
    headers = [cell["text"] for cell in parser.rows[0]]
    if headers != REFERENCE_TABLE_HEADERS:
        raise AchievementAuditError(f"unexpected achievement reference headers: {headers!r}")

    achievements: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    seen_names: set[str] = set()
    for row_index, cells in enumerate(parser.rows[1:], 1):
        if len(cells) != len(REFERENCE_TABLE_HEADERS):
            raise AchievementAuditError(f"reference row {row_index} has {len(cells)} cells")
        raw_name = cells[0]["text"]
        canonical_name = _canonical_reference_name(raw_name)
        achievement_id = _parse_optional_int(cells[1]["text"])
        grade = _parse_optional_int(cells[2]["text"])
        if achievement_id is None or grade is None:
            raise AchievementAuditError(f"reference row {row_index} has invalid ID/grade")
        if achievement_id in seen_ids:
            raise AchievementAuditError(f"duplicate reference ID {achievement_id}")
        if canonical_name in seen_names:
            raise AchievementAuditError(f"duplicate reference name {canonical_name!r}")
        seen_ids.add(achievement_id)
        seen_names.add(canonical_name)

        condition_text = cells[8]["text"]
        source_page = cells[0]["links"][0]["url"] if cells[0]["links"] else ""
        achievements.append(
            {
                "id": achievement_id,
                "name": canonical_name,
                "sourceTitle": raw_name,
                "grade": grade,
                "secret": _parse_yes_no_unknown(cells[3]["text"]),
                "premium": _parse_yes_no_unknown(cells[4]["text"]),
                "points": _parse_optional_int(cells[5]["text"]),
                "implemented": cells[6]["text"] or None,
                "sourcePage": source_page,
                "referenceRow": row_index,
                "condition": {
                    "available": bool(condition_text),
                    "kinds": _condition_kinds(condition_text),
                    "entities": _condition_entities(cells[8]["links"]),
                    "numbers": _condition_numbers(condition_text),
                    "sourceTextSha256": hashlib.sha256(condition_text.encode("utf-8")).hexdigest(),
                    "sourceTextLength": len(condition_text),
                    "evidence": "TibiaWiki/Fandom spoiler cell; prose intentionally not copied",
                },
                "descriptionSource": {
                    "sourceTextSha256": hashlib.sha256(cells[7]["text"].encode("utf-8")).hexdigest(),
                    "sourceTextLength": len(cells[7]["text"]),
                    "evidence": "TibiaWiki/Fandom description cell; prose intentionally not copied",
                },
            }
        )

    plain_text = _normalize_space(" ".join(parser.all_text))
    count_match = re.search(
        r"includes\s+(\d+)\s+common\s+and\s+(\d+)\s*/\s*(\d+)\s+secret\s+achievements\s*\(\s*(\d+)\s+out of\s+(\d+)\s+total",
        plain_text,
        re.IGNORECASE,
    )
    point_match = re.search(
        r"theoretical maximum points one can have is\s+(\d+).*?maximum is\s+(\d+)",
        plain_text,
        re.IGNORECASE,
    )
    heading_match = re.search(r"List of Achievements\s*\((\d+)\)", plain_text, re.IGNORECASE)
    page_summary = {
        "common": int(count_match.group(1)) if count_match else None,
        "secretDiscovered": int(count_match.group(2)) if count_match else None,
        "secretTotal": int(count_match.group(3)) if count_match else None,
        "listed": int(count_match.group(4)) if count_match else None,
        "total": int(count_match.group(5)) if count_match else None,
        "theoreticalPoints": int(point_match.group(1)) if point_match else None,
        "maximumExcludingCoinciding": int(point_match.group(2)) if point_match else None,
        "tableHeadingCount": int(heading_match.group(1)) if heading_match else None,
    }

    ids = [item["id"] for item in achievements]
    summary = {
        "rows": len(achievements),
        "minimumId": min(ids),
        "maximumId": max(ids),
        "gapCount": len(set(range(min(ids), max(ids) + 1)) - set(ids)),
        "common": sum(item["secret"] is False for item in achievements),
        "secret": sum(item["secret"] is True for item in achievements),
        "unknownSecret": sum(item["secret"] is None for item in achievements),
        "premiumYes": sum(item["premium"] is True for item in achievements),
        "premiumNo": sum(item["premium"] is False for item in achievements),
        "premiumUnknown": sum(item["premium"] is None for item in achievements),
        "knownPointTotal": sum(item["points"] or 0 for item in achievements),
        "unknownPointCount": sum(item["points"] is None for item in achievements),
        "conditionAvailableCount": sum(item["condition"]["available"] for item in achievements),
        "conditionUnavailableCount": sum(not item["condition"]["available"] for item in achievements),
    }

    conflicts: list[dict[str, Any]] = []
    comparisons = {
        "listed": (page_summary["listed"], summary["rows"]),
        "common": (page_summary["common"], summary["common"]),
        "secretDiscovered": (page_summary["secretDiscovered"], summary["secret"]),
        "tableHeadingCount": (page_summary["tableHeadingCount"], summary["rows"]),
    }
    for field, (stated, extracted) in comparisons.items():
        if stated is not None and stated != extracted:
            conflicts.append({"code": f"page-{field}-mismatch", "stated": stated, "extracted": extracted})
    stated_points = page_summary["theoreticalPoints"]
    if stated_points is not None and summary["knownPointTotal"] > stated_points:
        conflicts.append(
            {
                "code": "page-point-total-conflict",
                "stated": stated_points,
                "knownExtracted": summary["knownPointTotal"],
                "unknownPointRows": summary["unknownPointCount"],
            }
        )

    return {
        "format": REFERENCE_FORMAT,
        "source": {
            "name": "TibiaWiki/Fandom Achievements",
            "pageUrl": FANDOM_PAGE_URL,
            "retrievalUrl": source_url,
            "observedAt": observed_at,
            "pageId": page_id,
            "revisionId": revision_id,
            "sourceSha256": source_sha256,
            "sourceBytes": len(source_text.encode("utf-8")),
            "copyrightBoundary": "Factual metadata, links and hashes retained; description/spoiler prose is not copied.",
        },
        "pageSummary": page_summary,
        "summary": summary,
        "sourceConflicts": conflicts,
        "achievements": achievements,
    }


def validate_reference_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("format") != REFERENCE_FORMAT:
        raise AchievementAuditError(f"reference catalog format must be {REFERENCE_FORMAT}")
    achievements = catalog.get("achievements")
    if not isinstance(achievements, list) or not achievements:
        raise AchievementAuditError("reference catalog achievements must be a non-empty list")
    ids: set[int] = set()
    names: set[str] = set()
    for index, item in enumerate(achievements, 1):
        if not isinstance(item, dict):
            raise AchievementAuditError(f"reference catalog row {index} must be an object")
        achievement_id = item.get("id")
        name = item.get("name")
        if not isinstance(achievement_id, int) or not isinstance(name, str) or not name:
            raise AchievementAuditError(f"reference catalog row {index} requires integer id and non-empty name")
        if achievement_id in ids or name in names:
            raise AchievementAuditError(f"reference catalog duplicate at row {index}: {achievement_id} / {name}")
        ids.add(achievement_id)
        names.add(name)
        condition = item.get("condition")
        if not isinstance(condition, dict) or not isinstance(condition.get("available"), bool):
            raise AchievementAuditError(f"reference catalog row {index} requires condition evidence")
    summary = catalog.get("summary")
    if not isinstance(summary, dict) or summary.get("rows") != len(achievements):
        raise AchievementAuditError("reference catalog summary row count does not match achievements")


def load_reference_catalog(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict):
        raise AchievementAuditError("reference catalog must be an object")
    validate_reference_catalog(catalog)
    return catalog


def load_reviewed_evidence(path: Path | None) -> dict[int, dict[str, Any]]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format") != REVIEW_FORMAT:
        raise AchievementAuditError(f"reviewed evidence format must be {REVIEW_FORMAT}")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise AchievementAuditError("reviewed evidence entries must be a list")
    by_id: dict[int, dict[str, Any]] = {}
    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), int):
            raise AchievementAuditError(f"reviewed evidence row {index} requires integer id")
        status = entry.get("status")
        evidence = entry.get("evidence")
        if status not in ALLOWED_STATUSES:
            raise AchievementAuditError(f"reviewed evidence row {index} has invalid status {status!r}")
        if not isinstance(entry.get("reason"), str) or not entry["reason"]:
            raise AchievementAuditError(f"reviewed evidence row {index} requires a reason")
        if not isinstance(evidence, list) or not evidence:
            raise AchievementAuditError(f"reviewed evidence row {index} requires evidence")
        if entry["id"] in by_id:
            raise AchievementAuditError(f"duplicate reviewed evidence ID {entry['id']}")
        by_id[entry["id"]] = entry
    return by_id


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
        if points == 0 and (grade in GRADE_POINTS or grade == 0):
            findings.append(finding("info", "registry-zero-point-exception", f"ID {achievement_id} ({name}) has grade {grade} and zero points.", line=line_number))
        elif grade not in GRADE_POINTS or points not in GRADE_POINTS[grade]:
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
    expected["theoreticalPoints"] = baseline.get("points", {}).get("theoretical", baseline.get("points", {}).get("theoreticalKnown"))
    comparisons = {key: {"expected": value, "actual": actual[key], "matches": value == actual[key]} for key, value in expected.items() if value is not None}
    return {"source": baseline.get("source", {}), "comparisons": comparisons, "matches": all(item["matches"] for item in comparisons.values())}


def _line_evidence(text: str, path: str, needles: dict[str, str]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    lines = text.splitlines()
    for kind, needle in needles.items():
        for line_number, line in enumerate(lines, 1):
            if needle in line:
                evidence.append({"kind": kind, "path": path, "line": line_number, "excerpt": needle})
                break
    return evidence


def scan_persistence_evidence(root: Path, relative_path: str = "src/creatures/players/components/player_achievement.cpp") -> dict[str, Any]:
    path = root / relative_path
    if not path.is_file():
        return {"status": "unresolved", "evidence": [], "backfill": "unresolved"}
    text = path.read_text(encoding="utf-8")
    evidence = _line_evidence(
        text,
        relative_path,
        {
            "save-by-canonical-name": "getUnlockedKV()->set(achievement.name",
            "load-by-stored-name": "g_game().getAchievementByName(achievementName)",
            "point-persistence": 'scoped("achievements")->set("points"',
        },
    )
    status = "name-keyed-kv-confirmed" if len(evidence) == 3 else "unresolved"
    return {
        "status": status,
        "evidence": evidence,
        "backfill": "unresolved",
        "compatibilityRisk": "Renaming a canonical achievement can orphan name-keyed unlocked state without migration or aliasing.",
    }


def _metadata_mismatches(definition: AchievementDefinition, reference: dict[str, Any]) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    comparisons = {
        "name": (reference.get("name"), definition.name),
        "grade": (reference.get("grade"), definition.grade),
        "secret": (reference.get("secret"), definition.secret),
        "points": (reference.get("points"), definition.points),
    }
    for field, (expected, actual) in comparisons.items():
        if expected is not None and expected != actual:
            mismatches.append({"field": field, "reference": expected, "canary": actual})
    return mismatches


def _handler_evidence(refs: list[AchievementReference]) -> dict[str, Any]:
    gameplay = [ref for ref in refs if not ref.admin_only]
    kinds = {ref.kind for ref in gameplay}
    if "award" in kinds:
        status = "static-award-candidate"
    elif "progress" in kinds:
        status = "static-progress-candidate"
    elif gameplay:
        status = "reference-without-static-award"
    elif refs:
        status = "admin-only"
    else:
        status = "unresolved"
    return {"status": status, "references": [asdict(ref) for ref in refs]}


def _base_validation_status(definition_status: str, handler_status: str) -> str:
    if definition_status != "confirmed":
        return "conflicting"
    if handler_status in {"static-award-candidate", "static-progress-candidate"}:
        return "partially-confirmed"
    return "unresolved"


def build_reference_validation(
    definitions: list[AchievementDefinition],
    resolved: dict[int, list[AchievementReference]],
    catalog: dict[str, Any],
    registry_path: str,
    persistence: dict[str, Any],
    reviewed_evidence: dict[int, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {item.id: item for item in definitions}
    by_name = {item.name: item for item in definitions}
    rows: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for reference in sorted(catalog["achievements"], key=lambda item: item["id"]):
        definition_by_id = by_id.get(reference["id"])
        definition_by_name = by_name.get(reference["name"])
        definition = definition_by_id or definition_by_name
        mismatches: list[dict[str, Any]] = []
        if definition is None:
            definition_status = "missing"
        elif definition_by_id is not None and definition_by_name is not None and definition_by_id.id == definition_by_name.id:
            mismatches = _metadata_mismatches(definition, reference)
            definition_status = "conflicting" if mismatches else "confirmed"
        else:
            definition_status = "conflicting"
            mismatches.append(
                {
                    "field": "identity",
                    "referenceId": reference["id"],
                    "referenceName": reference["name"],
                    "canaryIdMatch": definition_by_id.name if definition_by_id else None,
                    "canaryNameMatch": definition_by_name.id if definition_by_name else None,
                }
            )

        refs = resolved.get(definition.id, []) if definition else []
        handler = _handler_evidence(refs)
        status = _base_validation_status(definition_status, handler["status"])
        review = reviewed_evidence.get(reference["id"])
        if review:
            status = review["status"]

        if definition_status == "missing":
            findings.append(
                finding(
                    "warning",
                    "reference-definition-missing",
                    f"Reference ID {reference['id']} ({reference['name']}) is absent from the Canary registry.",
                    id=reference["id"],
                    name=reference["name"],
                )
            )
        elif mismatches:
            findings.append(
                finding(
                    "warning",
                    "reference-definition-conflict",
                    f"Reference ID {reference['id']} ({reference['name']}) conflicts with Canary metadata.",
                    id=reference["id"],
                    name=reference["name"],
                    mismatches=mismatches,
                )
            )

        definition_evidence = None
        if definition:
            definition_evidence = {
                "id": definition.id,
                "name": definition.name,
                "grade": definition.grade,
                "secret": definition.secret,
                "points": definition.points,
                "path": registry_path,
                "line": definition.line,
            }
        new_player_status = (
            "partially-confirmed"
            if definition_status == "confirmed" and handler["status"] in {"static-award-candidate", "static-progress-candidate"}
            else "conflicting"
            if definition_status != "confirmed"
            else "unresolved"
        )
        rows.append(
            {
                "id": reference["id"],
                "name": reference["name"],
                "status": status,
                "reference": reference,
                "definition": {
                    "status": definition_status,
                    "evidence": definition_evidence,
                    "mismatches": mismatches,
                },
                "condition": {
                    "status": "reference-confirmed" if reference["condition"]["available"] else "unresolved",
                    **reference["condition"],
                },
                "handler": handler,
                "persistence": {
                    "unlockedState": persistence["status"] if definition_status == "confirmed" else "unavailable",
                    "backfill": review.get("persistenceBackfill", "unresolved") if review else "unresolved",
                    "evidence": persistence["evidence"] if definition_status == "confirmed" else [],
                    "compatibilityRisk": persistence.get("compatibilityRisk"),
                },
                "attainability": {
                    "newPlayers": review.get("newPlayerAttainability", new_player_status) if review else new_player_status,
                    "existingPlayers": review.get("existingPlayerAttainability", "unresolved") if review else "unresolved",
                    "reason": "A static API call is candidate handler evidence, not proof that the referenced gameplay condition is reachable.",
                },
                "runtimeRegistration": {
                    "status": "definition-source-confirmed" if definition_status == "confirmed" else "unavailable",
                    "runtimeE2EProven": review.get("runtimeE2EProven", False) if review else False,
                },
                "tests": {
                    "status": review.get("testStatus", "missing") if review else "missing",
                    "evidence": review.get("testEvidence", []) if review else [],
                },
                "reviewedEvidence": review,
            }
        )
    return rows, findings


def build_report(
    definitions: list[AchievementDefinition],
    registry_findings: list[dict[str, Any]],
    helper_findings: list[dict[str, Any]],
    references: list[AchievementReference],
    baseline: dict[str, Any] | None = None,
    reference_catalog: dict[str, Any] | None = None,
    reviewed_evidence: dict[int, dict[str, Any]] | None = None,
    registry_path: str = "data/scripts/lib/register_achievements.lua",
    persistence: dict[str, Any] | None = None,
) -> dict[str, Any]:
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
        rows.append({**asdict(definition), "disposition": disposition, "references": [asdict(ref) for ref in refs], "definitionEvidence": {"path": registry_path, "line": definition.line}})
    ids = sorted(by_id)
    gaps = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
    comparison = compare_baseline(definitions, baseline)
    if comparison and not comparison["matches"]:
        findings.append(finding("warning", "reference-baseline-mismatch", "Registry does not fully match the recorded external baseline.", comparison=comparison))

    reference_validation: list[dict[str, Any]] = []
    if reference_catalog is not None:
        reference_validation, reference_findings = build_reference_validation(
            definitions,
            resolved,
            reference_catalog,
            registry_path,
            persistence or {"status": "unresolved", "evidence": [], "backfill": "unresolved"},
            reviewed_evidence or {},
        )
        findings.extend(reference_findings)

    severities = Counter(item["severity"] for item in findings)
    status_counts = Counter(item["status"] for item in reference_validation)
    report = {
        "format": AUDIT_FORMAT if reference_catalog is not None else "canary-achievement-audit-v1",
        "ok": severities["error"] == 0,
        "complete": bool(reference_validation) and not any(item["status"] in {"unresolved", "conflicting", "definition-only", "handler-missing"} for item in reference_validation),
        "summary": {
            "registryCount": len(definitions),
            "minimumId": ids[0],
            "maximumId": ids[-1],
            "gapCount": len(gaps),
            "publicCount": sum(not item.secret for item in definitions),
            "secretCount": sum(item.secret for item in definitions),
            "pointTotal": sum(item.points for item in definitions),
            "referenceCount": len(references),
            "resolvedStaticReferenceCount": sum(map(len, resolved.values())),
            "unknownStaticReferenceCount": len(unknown),
            "dynamicReferenceCount": len(dynamic),
            "adminReferenceCount": sum(ref.admin_only for ref in references),
            "dispositions": dict(sorted(dispositions.items())),
            "validationStatuses": dict(sorted(status_counts.items())),
            "referenceCatalogCount": len(reference_validation),
            "findingsBySeverity": dict(sorted(severities.items())),
        },
        "baselineComparison": comparison,
        "referenceCatalogSource": reference_catalog.get("source") if reference_catalog else None,
        "referenceCatalogSummary": reference_catalog.get("summary") if reference_catalog else None,
        "referenceSourceConflicts": reference_catalog.get("sourceConflicts", []) if reference_catalog else [],
        "persistenceEvidence": persistence,
        "gaps": gaps,
        "findings": findings,
        "dynamicReferences": [asdict(ref) for ref in dynamic],
        "unknownStaticReferences": [asdict(ref) for ref in unknown],
        "achievements": rows,
        "referenceValidation": reference_validation,
    }
    return report


def audit_repository(
    repository_root: Path,
    registry: Path,
    script_roots: Iterable[str] | None = None,
    reference_baseline: Path | None = None,
    reference_catalog: Path | None = None,
    reviewed_evidence: Path | None = None,
    persistence_source: Path | None = None,
) -> dict[str, Any]:
    root = repository_root.resolve()
    registry = registry if registry.is_absolute() else root / registry
    text = registry.read_text(encoding="utf-8")
    definitions, registry_findings = parse_registry_text(text)
    baseline_path = reference_baseline if reference_baseline is None or reference_baseline.is_absolute() else root / reference_baseline
    catalog_path = reference_catalog if reference_catalog is None or reference_catalog.is_absolute() else root / reference_catalog
    review_path = reviewed_evidence if reviewed_evidence is None or reviewed_evidence.is_absolute() else root / reviewed_evidence
    persistence_relative = (persistence_source or Path("src/creatures/players/components/player_achievement.cpp")).as_posix()
    registry_relative = registry.resolve().relative_to(root).as_posix()
    return build_report(
        definitions,
        registry_findings,
        audit_registry_helpers(text),
        scan_references(root, tuple(script_roots or DEFAULT_ROOTS), registry),
        load_baseline(baseline_path),
        load_reference_catalog(catalog_path),
        load_reviewed_evidence(review_path),
        registry_relative,
        scan_persistence_evidence(root, persistence_relative),
    )


def _markdown_escape(value: Any) -> str:
    return str(value if value is not None else "?").replace("|", "\\|").replace("\n", " ")


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Canary achievement validation report",
        "",
        "## Decision",
        "",
        f"- audit: **{'pass' if report['ok'] else 'findings require follow-up'}**",
        f"- complete semantic/runtime validation: **{'yes' if report.get('complete') else 'no'}**",
        f"- definitions: **{summary['registryCount']}**, IDs **{summary['minimumId']}..{summary['maximumId']}**, gaps **{summary['gapCount']}**",
        f"- public / secret / points: **{summary['publicCount']} / {summary['secretCount']} / {summary['pointTotal']}**",
        f"- API references / dynamic / undefined static: **{summary['referenceCount']} / {summary['dynamicReferenceCount']} / {summary['unknownStaticReferenceCount']}**",
        "",
    ]
    if comparison := report.get("baselineComparison"):
        lines += ["## External baseline", ""] + [f"- {key}: expected `{item['expected']}`, actual `{item['actual']}` — **{'match' if item['matches'] else 'mismatch'}**" for key, item in comparison["comparisons"].items()] + [""]
    if report.get("referenceValidation"):
        lines += ["## Comprehensive status counts", ""]
        lines += [f"- {key}: {value}" for key, value in summary["validationStatuses"].items()]
        lines += ["", "## Per-achievement evidence table", ""]
        lines += [
            "| ID | Name | Status | Definition | Condition | Handler | Existing players | New players | Tests |",
            "|---:|---|---|---|---|---|---|---|---|",
        ]
        for row in report["referenceValidation"]:
            condition = ", ".join(row["condition"].get("kinds", []))
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row["id"]),
                        _markdown_escape(row["name"]),
                        row["status"],
                        row["definition"]["status"],
                        _markdown_escape(condition or "unresolved"),
                        row["handler"]["status"],
                        row["attainability"]["existingPlayers"],
                        row["attainability"]["newPlayers"],
                        row["tests"]["status"],
                    ]
                )
                + " |"
            )
        lines.append("")
    lines += ["## Findings", ""]
    lines += [f"- **{item['severity']} / {item['code']}** — {item['message']}" for item in report["findings"]] or ["No findings."]
    lines += ["", "## Trigger coverage", ""] + [f"- {key}: {value}" for key, value in summary["dispositions"].items()]
    lines += [
        "",
        "## Evidence boundary",
        "",
        "A reference condition, registry definition and static API call are separate evidence layers. A missing direct static call is not proof that an achievement is unobtainable. Dynamic tables, wrappers, quest state machines, engine-side paths, persistence/backfill and real runtime reachability remain unresolved until separately proven.",
        "",
    ]
    return "\n".join(lines)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Canary achievement definitions, reference catalogue and active Lua references")
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--registry", type=Path, default=Path("data/scripts/lib/register_achievements.lua"))
    parser.add_argument("--script-root", action="append", dest="script_roots")
    parser.add_argument("--reference-baseline", type=Path)
    parser.add_argument("--reference-catalog", type=Path)
    parser.add_argument("--reviewed-evidence", type=Path)
    parser.add_argument("--persistence-source", type=Path)
    parser.add_argument("--reference-source", type=Path)
    parser.add_argument("--reference-source-url", default="https://tibia.fandom.com/api.php?action=parse&page=Achievements&prop=text%7Crevid&format=json&formatversion=2")
    parser.add_argument("--reference-observed-at")
    parser.add_argument("--catalog-output", type=Path)
    parser.add_argument("--catalog-only", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args()
    try:
        catalog: dict[str, Any] | None = None
        if args.reference_source:
            if not args.catalog_output or not args.reference_observed_at:
                raise AchievementAuditError("--reference-source requires --catalog-output and --reference-observed-at")
            catalog = parse_reference_source_text(
                args.reference_source.read_text(encoding="utf-8"),
                args.reference_observed_at,
                args.reference_source_url,
            )
            write_json(args.catalog_output, catalog)
        if args.catalog_only:
            if catalog is None:
                raise AchievementAuditError("--catalog-only requires --reference-source")
            print(json.dumps({"catalog": str(args.catalog_output.resolve()), "summary": catalog["summary"], "sourceConflicts": catalog["sourceConflicts"]}, indent=2))
            return 0
        if args.output is None:
            raise AchievementAuditError("--output is required unless --catalog-only is used")
        report = audit_repository(
            args.repository_root,
            args.registry,
            args.script_roots,
            args.reference_baseline,
            args.reference_catalog,
            args.reviewed_evidence,
            args.persistence_source,
        )
        write_json(args.output, report)
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(render_markdown(report), encoding="utf-8")
    except (AchievementAuditError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    print(json.dumps({"ok": report["ok"], "complete": report["complete"], "summary": report["summary"], "output": str(args.output.resolve())}, indent=2))
    return 0 if report["ok"] or args.allow_findings else 2


if __name__ == "__main__":
    raise SystemExit(main())
