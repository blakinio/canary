#!/usr/bin/env python3
"""Read-only Weapon Proficiency achievement audit for Canary.

The tool intentionally does not modify registry, C++ or datapack sources. It
collects evidence required before implementing achievements 564-567.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

FORMAT = "canary-weapon-proficiency-achievement-audit-v1"
TARGETS = {
    564: {"name": "The First of Many", "masteredWeapons": 1, "secret": False},
    565: {"name": "A Well-Honed Arsenal", "masteredWeapons": 10, "secret": False},
    566: {"name": "Arsenal of War", "masteredWeapons": 50, "secret": False},
    567: {"name": "The Forbidden Build", "masteredWeapons": None, "secret": True},
}
FORBIDDEN_BUILD_NAMES = (
    "Club of the Fury",
    "Glooth Blade",
    "Glutton's Mace",
    "Glooth Club",
    "Ice Rapier",
    "Incredible Mumpiz Slayer",
    "Musician's Bow",
    "Ornate Carving Rod",
    "Ornate Mayhem Wand",
    "Pointed Rabbitslayer",
    "Small Stone",
    "Snowball",
)
TEXT_SUFFIXES = {".cpp", ".hpp", ".h", ".lua", ".xml", ".json"}
REGISTRY_ENTRY_RE = re.compile(r"^\s*\[(\d+)]\s*=\s*\{(.*?)\}\s*,?\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"\b(name|grade|points|secret|description)\s*=\s*(\"(?:\\.|[^\"])*\"|'(?:\\.|[^'])*'|true|false|-?\d+)")
ITEM_OPEN_RE = re.compile(r'<item\s+id="(\d+)"[^>]*\bname="([^"]+)"[^>]*>', re.IGNORECASE)
PROFICIENCY_ATTRIBUTE_RE = re.compile(r'<attribute\s+key="proficiency"\s+value="(\d+)"\s*/?>', re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    evidence: dict[str, Any]


@dataclass(frozen=True)
class TextMatch:
    path: str
    line: int
    text: str


def _decode_lua_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw in {"true", "false"}:
        return raw == "true"
    if raw.startswith(("\"", "'")):
        return bytes(raw[1:-1], "utf-8").decode("unicode_escape")
    return int(raw)


def parse_registry(text: str) -> dict[int, dict[str, Any]]:
    entries: dict[int, dict[str, Any]] = {}
    for match in REGISTRY_ENTRY_RE.finditer(text):
        achievement_id = int(match.group(1))
        fields = {key: _decode_lua_scalar(value) for key, value in FIELD_RE.findall(match.group(2))}
        fields.setdefault("secret", False)
        fields.setdefault("grade", 0)
        fields.setdefault("points", 0)
        entries[achievement_id] = fields
    return entries


def extract_function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        character = text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1 : index]
    return ""


def line_matches(text: str, needle: str, path: str) -> list[TextMatch]:
    lowered = needle.casefold()
    matches: list[TextMatch] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if lowered in line.casefold():
            matches.append(TextMatch(path=path, line=line_number, text=line.strip()[:300]))
    return matches


def iter_text_files(root: Path, roots: Iterable[str]) -> Iterable[Path]:
    seen: set[Path] = set()
    for relative_root in roots:
        start = root / relative_root
        if not start.exists():
            continue
        if start.is_file():
            paths = (start,)
        else:
            paths = start.rglob("*")
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or path in seen:
                continue
            seen.add(path)
            yield path


def parse_items_xml_candidates(text: str, names: Iterable[str], valid_proficiency_ids: set[int]) -> dict[str, list[dict[str, Any]]]:
    requested = {name.casefold(): name for name in names}
    results = {name: [] for name in names}
    positions = list(ITEM_OPEN_RE.finditer(text))
    for index, match in enumerate(positions):
        item_id = int(match.group(1))
        item_name = match.group(2)
        canonical = requested.get(item_name.casefold())
        if canonical is None:
            continue
        block_end = positions[index + 1].start() if index + 1 < len(positions) else len(text)
        block = text[match.start() : block_end]
        proficiency_match = PROFICIENCY_ATTRIBUTE_RE.search(block)
        override = int(proficiency_match.group(1)) if proficiency_match else None
        results[canonical].append(
            {
                "itemId": item_id,
                "itemName": item_name,
                "xmlProficiencyOverride": override,
                "xmlOverrideValid": override in valid_proficiency_ids if override is not None else None,
                "resolvedEligibility": (
                    "explicit-valid-xml-override"
                    if override in valid_proficiency_ids
                    else "explicit-invalid-xml-override"
                    if override is not None
                    else "protobuf-or-runtime-resolution-required"
                ),
            }
        )
    return results


def load_proficiency_ids(path: Path) -> set[int]:
    if not path.exists():
        return set()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {int(entry["ProficiencyId"]) for entry in payload if isinstance(entry, dict) and "ProficiencyId" in entry}


def audit_repository(root: Path) -> dict[str, Any]:
    registry_path = root / "data/scripts/lib/register_achievements.lua"
    cpp_path = root / "src/creatures/players/components/weapon_proficiency.cpp"
    hpp_path = root / "src/creatures/players/components/weapon_proficiency.hpp"
    player_achievement_path = root / "src/creatures/players/components/player_achievement.hpp"
    proficiencies_path = root / "data/items/proficiencies.json"
    items_xml_path = root / "data/items/items.xml"

    required = (registry_path, cpp_path, hpp_path, player_achievement_path)
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required audit inputs: {', '.join(missing)}")

    registry_text = registry_path.read_text(encoding="utf-8")
    cpp_text = cpp_path.read_text(encoding="utf-8")
    hpp_text = hpp_path.read_text(encoding="utf-8")
    player_achievement_text = player_achievement_path.read_text(encoding="utf-8")
    registry = parse_registry(registry_text)

    findings: list[Finding] = []
    target_rows: list[dict[str, Any]] = []
    for achievement_id, reference in TARGETS.items():
        definition = registry.get(achievement_id)
        if definition is None:
            findings.append(
                Finding(
                    code="target-definition-missing",
                    severity="warning" if achievement_id == 567 else "error",
                    message=f"Achievement ID {achievement_id} is absent from the active registry.",
                    evidence={"id": achievement_id, "expectedName": reference["name"]},
                )
            )
        elif definition.get("name") != reference["name"]:
            findings.append(
                Finding(
                    code="target-name-mismatch",
                    severity="error",
                    message=f"Achievement ID {achievement_id} does not use the expected canonical name.",
                    evidence={"id": achievement_id, "actual": definition.get("name"), "expected": reference["name"]},
                )
            )
        target_rows.append({"id": achievement_id, "reference": reference, "registry": definition})

    add_experience = extract_function_body(cpp_text, "void WeaponProficiency::addExperience")
    load_body = extract_function_body(cpp_text, "void WeaponProficiency::load()")
    normalize_body = extract_function_body(cpp_text, "void WeaponProficiency::normalizeStoredState")

    existing_transition_sets_mastered = "mastered = true" in add_experience
    initial_creation_caps_experience = any(
        marker in add_experience
        for marker in (
            "try_emplace(weaponId, std::min(experience, maxExperience))",
            "try_emplace(weaponId, createInitialState(experience, maxExperience))",
        )
    )
    initial_creation_body = extract_function_body(add_experience, "if (!proficiency.contains(weaponId))")
    initial_state_body = extract_function_body(cpp_text, "WeaponProficiencyData WeaponProficiency::createInitialState")
    initial_creation_uses_state_factory = "createInitialState(experience, maxExperience)" in initial_creation_body
    initial_state_derives_mastered = bool(
        re.search(
            r"mastered\s*=\s*maxExperience\s*>\s*0\s*&&\s*state\.experience\s*>=\s*maxExperience",
            initial_state_body,
        )
    )
    initial_creation_sets_mastered = "mastered = true" in initial_creation_body or (
        initial_creation_uses_state_factory and initial_state_derives_mastered
    )
    load_normalizes = "normalizeStoredState(weaponId)" in load_body
    normalize_derives_mastered = bool(re.search(r"mastered\s*=\s*[^;]*experience\s*>=\s*maxExperience", normalize_body))
    component_has_achievement_hook = any(
        token in cpp_text
        for token in (
            ".addAchievement(",
            "achievement().add(",
            "getAchievement().add(",
            "m_playerAchievement.add(",
        )
    )
    mastered_count_api = bool(re.search(r"getMastered|countMastered|masteredWeapon", hpp_text, re.IGNORECASE))
    player_achievement_add_available = "bool add(uint16_t id" in player_achievement_text

    if not component_has_achievement_hook:
        findings.append(
            Finding(
                code="mastery-achievement-hook-missing",
                severity="error",
                message="WeaponProficiency contains no achievement award hook for mastery transitions.",
                evidence={"source": str(cpp_path.relative_to(root)), "targetIds": [564, 565, 566]},
            )
        )
    if initial_creation_caps_experience and not initial_creation_sets_mastered:
        findings.append(
            Finding(
                code="initial-mastery-flag-not-set",
                severity="error",
                message="The first stored XP gain can be capped at max experience and return without setting mastered=true.",
                evidence={"source": str(cpp_path.relative_to(root)), "function": "WeaponProficiency::addExperience"},
            )
        )
    if load_normalizes and normalize_derives_mastered:
        findings.append(
            Finding(
                code="load-normalization-can-identify-existing-mastery",
                severity="info",
                message="Load normalization derives mastered state from persisted experience and can support an explicit backfill decision.",
                evidence={"loadCallsNormalize": True, "normalizeDerivesMastered": True},
            )
        )
    if not mastered_count_api:
        findings.append(
            Finding(
                code="mastered-count-api-missing",
                severity="warning",
                message="WeaponProficiency exposes tracked IDs but no public mastered-weapon count/query API.",
                evidence={"source": str(hpp_path.relative_to(root))},
            )
        )

    source_roots = ("data", "data-otservbr-global", "src")
    all_matches: dict[str, list[dict[str, Any]]] = {}
    static_award_matches: dict[str, list[dict[str, Any]]] = {}
    target_names = [entry["name"] for entry in TARGETS.values()]
    file_cache: dict[Path, str] = {}
    for path in iter_text_files(root, source_roots):
        try:
            file_cache[path] = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    for name in target_names:
        matches: list[TextMatch] = []
        awards: list[TextMatch] = []
        for path, text in file_cache.items():
            relative = path.relative_to(root).as_posix()
            found = line_matches(text, name, relative)
            matches.extend(found)
            awards.extend(match for match in found if "addAchievement" in match.text or "achievement" in match.text and ".add(" in match.text)
        all_matches[name] = [asdict(match) for match in matches]
        static_award_matches[name] = [asdict(match) for match in awards]

    for achievement_id in (564, 565, 566):
        name = TARGETS[achievement_id]["name"]
        awards = [entry for entry in static_award_matches[name] if entry["path"] != registry_path.relative_to(root).as_posix()]
        if not awards:
            findings.append(
                Finding(
                    code="target-award-path-missing",
                    severity="error",
                    message=f"No active textual award path was found for {name}.",
                    evidence={"id": achievement_id, "name": name},
                )
            )

    valid_proficiency_ids = load_proficiency_ids(proficiencies_path)
    xml_candidates = (
        parse_items_xml_candidates(items_xml_path.read_text(encoding="utf-8", errors="replace"), FORBIDDEN_BUILD_NAMES, valid_proficiency_ids)
        if items_xml_path.exists()
        else {name: [] for name in FORBIDDEN_BUILD_NAMES}
    )
    secret_candidates: list[dict[str, Any]] = []
    for name in FORBIDDEN_BUILD_NAMES:
        matches: list[TextMatch] = []
        for path, text in file_cache.items():
            matches.extend(line_matches(text, name, path.relative_to(root).as_posix()))
        candidate = {
            "referenceName": name,
            "textMatches": [asdict(match) for match in matches],
            "itemsXmlDefinitions": xml_candidates[name],
            "serverNameFound": bool(matches or xml_candidates[name]),
            "eligibilityProven": any(
                item["resolvedEligibility"] == "explicit-valid-xml-override" for item in xml_candidates[name]
            ),
        }
        if candidate["serverNameFound"] and not candidate["eligibilityProven"]:
            candidate["disposition"] = "candidate-found-proficiency-resolution-required"
        elif candidate["eligibilityProven"]:
            candidate["disposition"] = "explicit-valid-xml-proficiency"
        else:
            candidate["disposition"] = "server-item-not-found-by-name"
        secret_candidates.append(candidate)

    summary = {
        "targetDefinitionCount": sum(1 for row in target_rows if row["registry"] is not None),
        "missingTargetIds": [row["id"] for row in target_rows if row["registry"] is None],
        "targetAwardPathCount": sum(
            1 for achievement_id in (564, 565, 566) if static_award_matches[TARGETS[achievement_id]["name"]]
        ),
        "forbiddenBuildReferenceNameCount": len(FORBIDDEN_BUILD_NAMES),
        "forbiddenBuildNamesFoundInServerText": sum(1 for row in secret_candidates if row["serverNameFound"]),
        "forbiddenBuildEligibilityProven": sum(1 for row in secret_candidates if row["eligibilityProven"]),
        "findingCounts": {
            severity: sum(1 for finding in findings if finding.severity == severity)
            for severity in ("error", "warning", "info")
        },
    }

    return {
        "format": FORMAT,
        "ok": not any(finding.severity == "error" for finding in findings),
        "summary": summary,
        "targets": target_rows,
        "runtimeEvidence": {
            "existingTransitionSetsMastered": existing_transition_sets_mastered,
            "initialCreationCapsExperience": initial_creation_caps_experience,
            "initialCreationSetsMastered": initial_creation_sets_mastered,
            "loadCallsNormalizeStoredState": load_normalizes,
            "normalizeDerivesMasteredFromExperience": normalize_derives_mastered,
            "achievementHookPresent": component_has_achievement_hook,
            "masteredCountApiPresent": mastered_count_api,
            "playerAchievementAddAvailable": player_achievement_add_available,
        },
        "nameOccurrences": all_matches,
        "staticAwardOccurrences": static_award_matches,
        "forbiddenBuildCandidates": secret_candidates,
        "findings": [asdict(finding) for finding in findings],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    runtime = report["runtimeEvidence"]
    lines = [
        "# Weapon Proficiency achievement audit",
        "",
        f"- status: `{'ok' if report['ok'] else 'findings'}`",
        f"- active target definitions: `{summary['targetDefinitionCount']}/4`",
        f"- missing target IDs: `{summary['missingTargetIds']}`",
        f"- detected target award paths: `{summary['targetAwardPathCount']}/3`",
        f"- secret-build names found in server text: `{summary['forbiddenBuildNamesFoundInServerText']}/{summary['forbiddenBuildReferenceNameCount']}`",
        f"- secret-build eligibility proven by explicit valid XML override: `{summary['forbiddenBuildEligibilityProven']}`",
        "",
        "## Runtime evidence",
        "",
        f"- existing-state mastery transition: `{runtime['existingTransitionSetsMastered']}`",
        f"- initial creation caps XP: `{runtime['initialCreationCapsExperience']}`",
        f"- initial creation sets mastered: `{runtime['initialCreationSetsMastered']}`",
        f"- load normalizes stored state: `{runtime['loadCallsNormalizeStoredState']}`",
        f"- normalization derives mastery from XP: `{runtime['normalizeDerivesMasteredFromExperience']}`",
        f"- achievement hook present: `{runtime['achievementHookPresent']}`",
        f"- mastered-count API present: `{runtime['masteredCountApiPresent']}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.append(f"- **{finding['severity']} / {finding['code']}** — {finding['message']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--allow-findings", action="store_true")
    args = parser.parse_args(argv)

    root = args.repository_root.resolve()
    try:
        report = audit_repository(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"weapon proficiency achievement audit failed: {exc}", file=sys.stderr)
        return 2

    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(report), encoding="utf-8")

    return 0 if report["ok"] or args.allow_findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
