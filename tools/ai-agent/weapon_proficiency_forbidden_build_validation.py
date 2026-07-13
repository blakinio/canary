#!/usr/bin/env python3
"""Validate the hashed asset baseline for Weapon Proficiency achievement 567."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

FORMAT = "canary-weapon-proficiency-forbidden-build-validation-v1"
EXPECTED_NAMES = (
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
ITEM_OPEN_RE = re.compile(r'<item\s+id="(\d+)"[^>]*\bname="([^"]+)"[^>]*>', re.IGNORECASE)


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    evidence: dict[str, Any]


def parse_items_xml(text: str) -> dict[int, str]:
    return {int(match.group(1)): match.group(2) for match in ITEM_OPEN_RE.finditer(text)}


def load_proficiency_ids(path: Path) -> set[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        int(entry["ProficiencyId"])
        for entry in payload
        if isinstance(entry, dict) and "ProficiencyId" in entry
    }


def validate(root: Path) -> dict[str, Any]:
    baseline_path = root / "docs/ai-agent/WEAPON_PROFICIENCY_FORBIDDEN_BUILD_BASELINE.json"
    items_path = root / "data/items/items.xml"
    proficiencies_path = root / "data/items/proficiencies.json"
    required = (baseline_path, items_path, proficiencies_path)
    missing = [path.relative_to(root).as_posix() for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required inputs: {', '.join(missing)}")

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    entries = baseline.get("items", [])
    by_name = {
        str(entry["referenceName"]): entry
        for entry in entries
        if isinstance(entry, dict) and "referenceName" in entry
    }
    active_items = parse_items_xml(items_path.read_text(encoding="utf-8", errors="replace"))
    active_proficiencies = load_proficiency_ids(proficiencies_path)

    findings: list[Finding] = []
    missing_names = [name for name in EXPECTED_NAMES if name not in by_name]
    extra_names = sorted(set(by_name) - set(EXPECTED_NAMES))
    if missing_names:
        findings.append(
            Finding(
                code="baseline-missing-reference-names",
                severity="error",
                message="The hashed asset baseline is incomplete.",
                evidence={"missingNames": missing_names},
            )
        )
    if extra_names:
        findings.append(
            Finding(
                code="baseline-extra-reference-names",
                severity="warning",
                message="The baseline contains names outside the reviewed secret set.",
                evidence={"extraNames": extra_names},
            )
        )

    rows: list[dict[str, Any]] = []
    seen_item_ids: dict[int, str] = {}
    for name in EXPECTED_NAMES:
        entry = by_name.get(name)
        if entry is None:
            rows.append({"referenceName": name, "status": "baseline-entry-missing"})
            continue
        item_id = int(entry["itemId"])
        proficiency_id = int(entry["proficiencyId"])
        active_name = active_items.get(item_id)
        name_matches = active_name is not None and active_name.casefold() == name.casefold()
        proficiency_exists = proficiency_id in active_proficiencies
        duplicate_owner = seen_item_ids.get(item_id)
        if duplicate_owner is None:
            seen_item_ids[item_id] = name
        else:
            findings.append(
                Finding(
                    code="baseline-duplicate-item-id",
                    severity="error",
                    message=f"Item ID {item_id} is assigned to multiple secret-set names.",
                    evidence={"itemId": item_id, "firstName": duplicate_owner, "secondName": name},
                )
            )
        if not name_matches:
            findings.append(
                Finding(
                    code="active-item-mismatch",
                    severity="error",
                    message=f"Active items.xml does not match the reviewed item metadata for {name}.",
                    evidence={"referenceName": name, "itemId": item_id, "activeName": active_name},
                )
            )
        if not proficiency_exists:
            findings.append(
                Finding(
                    code="active-proficiency-missing",
                    severity="error",
                    message=f"Proficiency ID {proficiency_id} for {name} is absent from active proficiencies.json.",
                    evidence={"referenceName": name, "itemId": item_id, "proficiencyId": proficiency_id},
                )
            )
        rows.append(
            {
                "referenceName": name,
                "itemId": item_id,
                "activeItemName": active_name,
                "proficiencyId": proficiency_id,
                "itemIdentityMatches": name_matches,
                "proficiencyDefinitionPresent": proficiency_exists,
                "eligibilityProven": name_matches and proficiency_exists,
                "status": "verified" if name_matches and proficiency_exists else "conflicting",
            }
        )

    verified = sum(1 for row in rows if row.get("eligibilityProven"))
    return {
        "format": FORMAT,
        "ok": not any(finding.severity == "error" for finding in findings),
        "source": baseline.get("source", {}),
        "summary": {
            "expectedEntryCount": len(EXPECTED_NAMES),
            "baselineEntryCount": len(entries),
            "verifiedEntryCount": verified,
            "activeProficiencyDefinitionCount": len(active_proficiencies),
            "findingCounts": {
                severity: sum(1 for finding in findings if finding.severity == severity)
                for severity in ("error", "warning", "info")
            },
        },
        "items": rows,
        "findings": [asdict(finding) for finding in findings],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# The Forbidden Build asset/server validation",
        "",
        f"- status: `{'verified' if report['ok'] else 'conflicting'}`",
        f"- verified item/proficiency mappings: `{summary['verifiedEntryCount']}/{summary['expectedEntryCount']}`",
        f"- active proficiency definitions: `{summary['activeProficiencyDefinitionCount']}`",
        "",
        "| Reference name | Item ID | Proficiency ID | Status |",
        "|---|---:|---:|---|",
    ]
    for row in report["items"]:
        lines.append(
            f"| {row['referenceName']} | {row.get('itemId', '')} | {row.get('proficiencyId', '')} | {row['status']} |"
        )
    if report["findings"]:
        lines.extend(("", "## Findings", ""))
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

    try:
        report = validate(args.repository_root.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"forbidden build validation failed: {exc}", file=sys.stderr)
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
