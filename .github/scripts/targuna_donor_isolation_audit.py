from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path.cwd()
ARTIFACT_ROOT = ROOT / "audit"
OUTPUT = ARTIFACT_ROOT / "output"
CRYSTAL = ROOT / "external/crystalserver/data-global"
BASELINE_INDEX = ARTIFACT_ROOT / "index/baseline.widx"
CRYSTAL_INDEX = ARTIFACT_ROOT / "index/crystal.widx"
BASELINE_MANIFEST = ARTIFACT_ROOT / "output/baseline.widx.json"
CRYSTAL_MANIFEST = ARTIFACT_ROOT / "output/crystal.widx.json"
BASELINE_MAP = ARTIFACT_ROOT / "maps/baseline.otbm"
CRYSTAL_MAP = ARTIFACT_ROOT / "maps/crystal.otbm"
SPAWN_EVIDENCE = OUTPUT / "crystal-spawn-npc-evidence.json"
CRYSTAL_COMMIT = os.environ["CRYSTAL_SHA"]
CANARY_COMMIT = os.environ["CANARY_SHA"]

sys.path.insert(0, str((ROOT / "tools/ai-agent").resolve()))
from otbm_world_index import WorldIndex  # noqa: E402

POSITION_PATTERNS = (
    re.compile(r"Position\s*\(\s*(\d{3,5})\s*,\s*(\d{3,5})\s*,\s*(\d{1,2})\s*\)"),
    re.compile(
        r"\{[^{}\n]{0,120}?\bx\s*=\s*(\d{3,5})\s*,\s*\by\s*=\s*(\d{3,5})\s*,\s*\bz\s*=\s*(\d{1,2})[^{}\n]{0,120}?\}",
        re.I,
    ),
)
STORAGE_RE = re.compile(r"\bStorage(?:\.[A-Za-z_][A-Za-z0-9_]*)+")
MONSTER_NAME_RE = re.compile(r"Game\.createMonsterType\s*\(\s*[\"']([^\"']+)[\"']")
NPC_NAME_RE = re.compile(r"(?:local\s+)?internalNpcName\s*=\s*[\"']([^\"']+)[\"']")
API_RE = re.compile(r"\b(?:Game|player|creature|monster|npc|item|target|tile|Tile|Position)[:.]([A-Za-z_][A-Za-z0-9_]*)\s*\(")
ITEM_PATTERNS = (
    re.compile(r"\b(?:createItem|addItem|removeItem|getItemCount|ItemType|Item)\s*\(\s*(\d{2,5})"),
    re.compile(r"\b(?:itemId|itemid|id)\s*[=~!<>]+\s*(\d{2,5})", re.I),
    re.compile(r":id\s*\(\s*(\d{2,5})(?:\s*,|\s*\))"),
)
REGISTRATION_PATTERNS = {
    "actionId": re.compile(r":aid\s*\(([^\n)]*)\)"),
    "uniqueId": re.compile(r":uid\s*\(([^\n)]*)\)"),
    "itemId": re.compile(r":id\s*\(([^\n)]*)\)"),
    "position": re.compile(r":position\s*\(([^\n)]*)\)"),
}
NUMBER_RE = re.compile(r"\b\d+\b")


@dataclass(frozen=True)
class Anchor:
    x: int
    y: int
    z: int
    role: str
    source: str
    label: str

    @property
    def position(self) -> tuple[int, int, int]:
        return self.x, self.y, self.z

    @property
    def cell(self) -> tuple[int, int]:
        return self.x // 256, self.y // 256

    def to_json(self) -> dict[str, Any]:
        return {
            "position": [self.x, self.y, self.z],
            "role": self.role,
            "source": self.source,
            "label": self.label,
        }


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def label_for_path(path: str) -> str:
    value = path.lower()
    if "aragonia" in value:
        return "aragonia"
    if "crimson" in value:
        return "crimson-court"
    if "hidden_lizard" in value or "lizard_temple" in value:
        return "hidden-lizard-temple"
    if "main_continent" in value:
        return "main-continent-dependency"
    if "herald" in value:
        return "herald-of-fire"
    if "sandcastle" in value:
        return "targuna-sandcastles"
    return "targuna"


def read_sources() -> tuple[list[dict[str, Any]], set[str], set[str], list[Anchor], dict[str, Any]]:
    quest_files = sorted((CRYSTAL / "scripts/quests/targuna").glob("*.lua"))
    monster_files = sorted((CRYSTAL / "monster/targuna").rglob("*.lua"))
    npc_files: list[Path] = []
    for path in sorted((CRYSTAL / "npc").glob("*.lua")):
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        if "u15_24.targuna" in lowered or "targuna" in lowered:
            npc_files.append(path)

    all_files = sorted(set(quest_files + monster_files + npc_files))
    anchors: list[Anchor] = []
    monster_names: set[str] = set()
    npc_names: set[str] = set()
    storage_counts: Counter[str] = Counter()
    item_counts: Counter[int] = Counter()
    api_counts: Counter[str] = Counter()
    registrations: dict[str, set[int | str]] = defaultdict(set)
    files_json: list[dict[str, Any]] = []

    for path in all_files:
        relative = path.relative_to(CRYSTAL).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        label = label_for_path(relative)
        roles: list[str] = []
        if path in quest_files:
            roles.append("quest")
        if path in monster_files:
            roles.append("monster-definition")
        if path in npc_files:
            roles.append("npc-definition")

        for match in MONSTER_NAME_RE.finditer(text):
            monster_names.add(match.group(1))
        for match in NPC_NAME_RE.finditer(text):
            npc_names.add(match.group(1))
        for match in STORAGE_RE.finditer(text):
            storage_counts[match.group(0)] += 1
        for pattern in ITEM_PATTERNS:
            for match in pattern.finditer(text):
                value = int(match.group(1))
                if 1 <= value <= 65535:
                    item_counts[value] += 1
        for match in API_RE.finditer(text):
            api_counts[match.group(1)] += 1
        for namespace, pattern in REGISTRATION_PATTERNS.items():
            for match in pattern.finditer(text):
                raw = match.group(1)
                if namespace == "position":
                    registrations[namespace].add(raw.strip())
                else:
                    for number in NUMBER_RE.findall(raw):
                        registrations[namespace].add(int(number))
        for pattern in POSITION_PATTERNS:
            for match in pattern.finditer(text):
                x, y, z = (int(part) for part in match.groups())
                if not (0 <= z <= 15):
                    continue
                anchors.append(
                    Anchor(
                        x=x,
                        y=y,
                        z=z,
                        role="literal-source-position",
                        source=f"{relative}:{line_number(text, match.start())}",
                        label=label,
                    )
                )

        files_json.append(
            {
                "path": relative,
                "roles": roles,
                "label": label,
                "size": path.stat().st_size,
                "sha256": sha256_path(path),
            }
        )

    return (
        files_json,
        monster_names,
        npc_names,
        anchors,
        {
            "storages": [
                {"name": name, "references": count}
                for name, count in sorted(storage_counts.items())
            ],
            "itemIds": [
                {"itemId": item_id, "references": count}
                for item_id, count in sorted(item_counts.items())
            ],
            "apiCalls": [
                {"name": name, "references": count}
                for name, count in sorted(api_counts.items())
            ],
            "registrations": {
                namespace: sorted(values, key=lambda value: str(value))
                for namespace, values in sorted(registrations.items())
            },
        },
    )


def selected_spawn_evidence(
    monster_names: set[str],
    npc_names: set[str],
) -> tuple[dict[str, Any], list[Anchor]]:
    evidence = json.loads(SPAWN_EVIDENCE.read_text(encoding="utf-8"))
    selected_names = {name.casefold() for name in monster_names | npc_names}
    selected_definitions = [
        row
        for row in evidence.get("definitions", [])
        if str(row.get("canonicalName", "")).casefold() in selected_names
        or str(row.get("name", "")).casefold() in selected_names
        or str(row.get("source", "")).lower().startswith("monster/targuna/")
    ]
    canonical_selected = {
        str(row.get("canonicalName", row.get("name", ""))).casefold()
        for row in selected_definitions
    }
    selected_placements = [
        row
        for row in evidence.get("placements", [])
        if str(row.get("canonicalName", row.get("name", ""))).casefold()
        in canonical_selected
    ]
    selected_groups = {
        row.get("groupId") for row in selected_placements if row.get("groupId")
    }
    groups = [
        row for row in evidence.get("spawnGroups", []) if row.get("id") in selected_groups
    ]
    selected_dynamic = [
        row
        for row in evidence.get("dynamicCreations", [])
        if str(row.get("canonicalName", row.get("name", ""))).casefold()
        in canonical_selected
    ]
    selected_findings = [
        row
        for row in evidence.get("findings", [])
        if any(
            str(row.get(key, "")).casefold() in canonical_selected
            for key in ("canonicalName", "name", "actor")
        )
    ]

    anchors: list[Anchor] = []
    for row in selected_placements:
        position = row.get("position")
        if not (isinstance(position, list) and len(position) == 3):
            continue
        source = f"{row.get('source', 'spawn-sidecar')}#{row.get('id', '?')}"
        definition_source = ""
        canonical = str(row.get("canonicalName", row.get("name", ""))).casefold()
        for definition in selected_definitions:
            if str(definition.get("canonicalName", definition.get("name", ""))).casefold() == canonical:
                definition_source = str(definition.get("source", ""))
                break
        label = label_for_path(definition_source or source)
        anchors.append(
            Anchor(
                x=int(position[0]),
                y=int(position[1]),
                z=int(position[2]),
                role=f"{row.get('kind', 'actor')}-spawn",
                source=source,
                label=label,
            )
        )
    for row in selected_dynamic:
        position = row.get("position")
        if not (isinstance(position, list) and len(position) == 3):
            continue
        anchors.append(
            Anchor(
                x=int(position[0]),
                y=int(position[1]),
                z=int(position[2]),
                role=f"dynamic-{row.get('kind', 'actor')}",
                source=str(row.get("source", "dynamic-creation")),
                label=label_for_path(str(row.get("source", ""))),
            )
        )

    return (
        {
            "scannerSummary": evidence.get("summary", {}),
            "definitions": selected_definitions,
            "spawnGroups": groups,
            "placements": selected_placements,
            "dynamicCreations": selected_dynamic,
            "findings": selected_findings,
        },
        anchors,
    )


def house_anchors() -> tuple[list[dict[str, Any]], list[Anchor]]:
    import xml.etree.ElementTree as ET

    path = CRYSTAL / "world/world-house.xml"
    houses: list[dict[str, Any]] = []
    anchors: list[Anchor] = []
    for node in ET.parse(path).getroot().findall(".//house"):
        if node.attrib.get("houseid") not in {"3701", "3702"}:
            continue
        row = dict(sorted(node.attrib.items()))
        houses.append(row)
        anchors.append(
            Anchor(
                x=int(row["entryx"]),
                y=int(row["entryy"]),
                z=int(row["entryz"]),
                role="targuna-house-entry",
                source=f"world/world-house.xml#house-{row['houseid']}",
                label="targuna-island",
            )
        )
    return houses, anchors


def cluster_anchors(anchors: Iterable[Anchor]) -> list[dict[str, Any]]:
    unique = sorted(
        {anchor for anchor in anchors},
        key=lambda anchor: (anchor.x, anchor.y, anchor.z, anchor.role, anchor.source),
    )
    cells = sorted({anchor.cell for anchor in unique})
    parent = {cell: cell for cell in cells}

    def find(cell: tuple[int, int]) -> tuple[int, int]:
        while parent[cell] != cell:
            parent[cell] = parent[parent[cell]]
            cell = parent[cell]
        return cell

    def union(left: tuple[int, int], right: tuple[int, int]) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    cell_set = set(cells)
    for cell in cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                other = (cell[0] + dx, cell[1] + dy)
                if other in cell_set:
                    union(cell, other)

    grouped_cells: dict[tuple[int, int], set[tuple[int, int]]] = defaultdict(set)
    for cell in cells:
        grouped_cells[find(cell)].add(cell)

    results: list[dict[str, Any]] = []
    for ordinal, component_cells in enumerate(
        sorted(grouped_cells.values(), key=lambda values: min(values)), start=1
    ):
        selected = [anchor for anchor in unique if anchor.cell in component_cells]
        min_cell_x = min(cell[0] for cell in component_cells)
        max_cell_x = max(cell[0] for cell in component_cells)
        min_cell_y = min(cell[1] for cell in component_cells)
        max_cell_y = max(cell[1] for cell in component_cells)
        lower = [max(0, (min_cell_x - 1) * 256), max(0, (min_cell_y - 1) * 256), max(0, min(a.z for a in selected) - 1)]
        upper = [min(65535, (max_cell_x + 2) * 256 - 1), min(65535, (max_cell_y + 2) * 256 - 1), min(15, max(a.z for a in selected) + 1)]
        labels = Counter(anchor.label for anchor in selected)
        result = {
            "id": f"cluster-{ordinal:02d}",
            "labels": [
                {"label": label, "anchors": count}
                for label, count in sorted(labels.items(), key=lambda row: (-row[1], row[0]))
            ],
            "cells": [list(cell) for cell in sorted(component_cells)],
            "anchorCount": len(selected),
            "anchorBounds": {
                "from": [min(a.x for a in selected), min(a.y for a in selected), min(a.z for a in selected)],
                "to": [max(a.x for a in selected), max(a.y for a in selected), max(a.z for a in selected)],
            },
            "auditBounds": {"from": lower, "to": upper},
            "anchors": [anchor.to_json() for anchor in selected],
        }
        results.append(result)
    return results


def run_semantic_diff(cluster: dict[str, Any]) -> dict[str, Any]:
    cluster_id = cluster["id"]
    lower = ",".join(str(value) for value in cluster["auditBounds"]["from"])
    upper = ",".join(str(value) for value in cluster["auditBounds"]["to"])
    output_name = f"output/{cluster_id}-semantic-diff.json"
    command = [
        sys.executable,
        "tools/ai-agent/otbm_semantic_diff_tool.py",
        "diff",
        "--artifact-root",
        "audit",
        "--before-index",
        "index/baseline.widx",
        "--before-manifest",
        "output/baseline.widx.json",
        "--after-index",
        "index/crystal.widx",
        "--after-manifest",
        "output/crystal.widx.json",
        "--before-map",
        "maps/baseline.otbm",
        "--after-map",
        "maps/crystal.otbm",
        "--from",
        lower,
        "--to",
        upper,
        "--sample-limit",
        "500",
        "--output",
        output_name,
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    report = json.loads((ARTIFACT_ROOT / output_name).read_text(encoding="utf-8"))
    return {
        "reportPath": output_name,
        "format": report.get("format"),
        "scope": report.get("scope"),
        "summary": report.get("summary", {}),
        "findings": report.get("findings", [])[:100],
    }


def mechanics_in_region(index_path: Path, lower: list[int], upper: list[int]) -> dict[str, Any]:
    placements: list[dict[str, Any]] = []
    with WorldIndex(index_path) as index:
        for _tile_index, tile in index.iter_region_tiles(tuple(lower), tuple(upper)):
            for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count):
                placement = index.placement(ordinal)
                if any(
                    key in placement
                    for key in ("actionId", "uniqueId", "houseDoorId", "teleportDestination")
                ):
                    placements.append(placement)
    action_ids = Counter(row["actionId"] for row in placements if "actionId" in row)
    unique_ids = Counter(row["uniqueId"] for row in placements if "uniqueId" in row)
    house_doors = Counter(row["houseDoorId"] for row in placements if "houseDoorId" in row)
    teleports = [row for row in placements if "teleportDestination" in row]
    return {
        "placementCount": len(placements),
        "actionIds": [{"value": value, "placements": count} for value, count in sorted(action_ids.items())],
        "uniqueIds": [{"value": value, "placements": count} for value, count in sorted(unique_ids.items())],
        "houseDoorIds": [{"value": value, "placements": count} for value, count in sorted(house_doors.items())],
        "teleportCount": len(teleports),
        "placements": placements[:500],
        "truncated": len(placements) > 500,
    }


def compact_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(summary))


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Real Tibia Targuna donor isolation audit",
        "",
        f"- Canary commit: `{report['sources']['canaryCommit']}`",
        f"- CrystalServer commit: `{report['sources']['crystalCommit']}`",
        f"- Baseline map: `{report['sources']['baselineMapSha256']}`",
        f"- Crystal logical map: `{report['sources']['crystalMapSha256']}`",
        "",
        "## Source inventory",
        "",
        f"- Targuna source files: **{len(report['sourceFiles'])}**",
        f"- Monster definitions: **{len(report['actors']['monsterNames'])}**",
        f"- NPC definitions/references: **{len(report['actors']['npcNames'])}**",
        f"- Selected static actor placements: **{len(report['spawnNpcEvidence']['placements'])}**",
        f"- Literal/source/actor/house anchors: **{report['anchorCount']}**",
        "",
        "## Spatial clusters",
        "",
        "| Cluster | Labels | Anchors | Audit bounds | Semantic findings | Crystal mechanics |",
        "|---|---|---:|---|---:|---:|",
    ]
    for cluster in report["clusters"]:
        summary = cluster.get("semanticDiff", {}).get("summary", {})
        findings = summary.get("findings", {})
        total_findings = findings.get("total", summary.get("findingCount", 0))
        labels = ", ".join(row["label"] for row in cluster["labels"][:4])
        bounds = f"{cluster['auditBounds']['from']} → {cluster['auditBounds']['to']}"
        lines.append(
            f"| `{cluster['id']}` | {labels} | {cluster['anchorCount']} | `{bounds}` | "
            f"{total_findings} | {cluster['crystalMechanics']['placementCount']} |"
        )
    lines.extend(
        [
            "",
            "## Import boundary",
            "",
            "This audit identifies bounded donor candidates and dependencies. It does not write an OTBM, "
            "does not prove live Real Tibia parity, and does not authorize copying every tile inside a coarse "
            "cluster bound. Each cluster must be reviewed independently with exact findings, mechanics, actors, "
            "items, storages, transitions and runtime scenarios before any map-writing proposal.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    source_files, monster_names, npc_names, source_anchors, dependencies = read_sources()
    spawn_evidence, actor_anchors = selected_spawn_evidence(monster_names, npc_names)
    houses, house_points = house_anchors()
    anchors = source_anchors + actor_anchors + house_points
    clusters = cluster_anchors(anchors)
    for cluster in clusters:
        cluster["semanticDiff"] = run_semantic_diff(cluster)
        lower = cluster["auditBounds"]["from"]
        upper = cluster["auditBounds"]["to"]
        cluster["baselineMechanics"] = mechanics_in_region(BASELINE_INDEX, lower, upper)
        cluster["crystalMechanics"] = mechanics_in_region(CRYSTAL_INDEX, lower, upper)

    report = {
        "format": "canary-real-tibia-targuna-donor-audit-v1",
        "sources": {
            "canaryCommit": CANARY_COMMIT,
            "crystalCommit": CRYSTAL_COMMIT,
            "baselineMapSha256": sha256_path(BASELINE_MAP),
            "crystalMapSha256": sha256_path(CRYSTAL_MAP),
            "baselineIndexSha256": sha256_path(BASELINE_INDEX),
            "crystalIndexSha256": sha256_path(CRYSTAL_INDEX),
        },
        "sourceFiles": source_files,
        "dependencies": dependencies,
        "actors": {
            "monsterNames": sorted(monster_names, key=str.casefold),
            "npcNames": sorted(npc_names, key=str.casefold),
        },
        "spawnNpcEvidence": spawn_evidence,
        "houses": houses,
        "anchorCount": len(anchors),
        "clusters": clusters,
        "limitations": [
            "Cluster construction uses deterministic 256x256 source-anchor cell connectivity and one-cell context padding.",
            "A cluster bound is a review scope, not an authorization to import every changed tile inside it.",
            "Literal source extraction does not execute Lua and dynamic positions remain unresolved.",
            "Semantic map findings are static evidence and do not prove runtime or gameplay parity.",
        ],
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT / "real-tibia-targuna-donor-audit.json"
    md_path = OUTPUT / "real-tibia-targuna-donor-audit.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown(report), encoding="utf-8")
    print("=== REAL_TIBIA_TARGUNA_DONOR_AUDIT ===")
    print(md_path.read_text(encoding="utf-8"))
    print("=== END_REAL_TIBIA_TARGUNA_DONOR_AUDIT ===")


if __name__ == "__main__":
    main()
