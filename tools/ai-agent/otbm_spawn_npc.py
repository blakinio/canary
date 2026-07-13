from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import otbm_spawn_npc_validation as _engine
from otbm_spawn_npc_validation import (
    DEFAULT_SAMPLE_LIMIT,
    EVIDENCE_FORMAT,
    MAX_SAMPLE_LIMIT,
    REPORT_FORMAT,
    REACHABILITY_FORMAT,
    SCHEMA_VERSION,
    SpawnNpcValidationError,
    normalize_bounds,
    validate_evidence as _validate_evidence,
    validate_paths as _validate_paths,
    write_json,
)

_BOSSTIARY_BLOCK = re.compile(
    r"\b[A-Za-z_][A-Za-z0-9_]*\s*\.\s*Bosstiary\s*=\s*\{(?P<body>.*?)\}",
    re.DOTALL,
)
_BOSSTIARY_CLASS = re.compile(r"\bclass\s*=\s*([\"'])(?P<value>.*?)\1", re.DOTALL)


def _literal_spawn_boss(text: str) -> bool:
    """Match the current MonsterType::isBoss() contract conservatively.

    Canary's runtime spawn exclusivity uses a non-empty bosstiaryClass, not
    rewardBoss. Only a literal non-empty class inside a literal Bosstiary table
    is promoted to confirmed source evidence.
    """

    for block in _BOSSTIARY_BLOCK.finditer(text):
        class_match = _BOSSTIARY_CLASS.search(block.group("body"))
        if class_match and class_match.group("value").strip():
            return True
    return False


def _finding_sort_key(entry: Mapping[str, Any]) -> tuple[Any, ...]:
    severity_order = {"error": 0, "warning": 1, "info": 2}
    return (
        severity_order.get(str(entry.get("severity")), 99),
        str(entry.get("code", "")),
        str(entry.get("source", "")),
        str(entry.get("groupId", "")),
        tuple(entry.get("position", entry.get("center", [])) or []),
        str(entry.get("name", "")),
    )


def _harden_runtime_semantics(report: dict[str, Any], datapack_root: Path) -> dict[str, Any]:
    root = datapack_root.expanduser().resolve()
    definitions = report.get("definitions", [])
    source_flags: dict[str, bool] = {}
    for definition in definitions:
        if not isinstance(definition, dict):
            continue
        is_spawn_boss = False
        if definition.get("kind") == "monster":
            source = definition.get("source")
            if isinstance(source, str):
                if source not in source_flags:
                    path = _engine._resolve_under(root, source, label="monster definition")
                    source_flags[source] = _literal_spawn_boss(_engine._read_text(path))
                is_spawn_boss = source_flags[source]
        definition["spawnBossLiteral"] = is_spawn_boss

    definition_by_source = {
        str(entry.get("source")): bool(entry.get("spawnBossLiteral"))
        for entry in definitions
        if isinstance(entry, dict)
    }
    placements = [entry for entry in report.get("placements", []) if isinstance(entry, dict)]
    for placement in placements:
        placement["spawnBossLiteral"] = any(
            definition_by_source.get(str(source), False)
            for source in placement.get("definitionSources", [])
        )
        if placement.get("spawntimeStatus") == "runtime-clamped":
            placement["spawntimeStatus"] = "rate-dependent"

    findings = [entry for entry in report.get("findings", []) if isinstance(entry, dict)]
    finding_summary = report["summary"]["findings"]
    by_code = finding_summary["byCode"]
    by_severity = finding_summary["bySeverity"]

    clamp_count = int(by_code.pop("monster_spawntime_runtime_clamp", 0))
    if clamp_count:
        by_code["monster_spawntime_rate_dependent"] = (
            int(by_code.get("monster_spawntime_rate_dependent", 0)) + clamp_count
        )
    for finding in findings:
        if finding.get("code") == "monster_spawntime_runtime_clamp":
            finding["code"] = "monster_spawntime_rate_dependent"
            finding["message"] = (
                "Monster spawntime exceeds one day before runtime rate scaling; "
                "the final interval may or may not be clamped"
            )

    old_boss_count = int(by_code.pop("boss_mixed_in_spawn_block", 0))
    findings = [entry for entry in findings if entry.get("code") != "boss_mixed_in_spawn_block"]

    by_group_position: dict[tuple[str, tuple[int, int, int]], list[dict[str, Any]]] = defaultdict(list)
    for placement in placements:
        position_value = placement.get("position")
        if not isinstance(position_value, list) or len(position_value) != 3:
            continue
        position = tuple(int(value) for value in position_value)
        by_group_position[(str(placement.get("groupId")), position)].append(placement)

    boss_findings: list[dict[str, Any]] = []
    for (group_id, position), entries in sorted(by_group_position.items()):
        if len(entries) > 1 and any(entry.get("spawnBossLiteral") for entry in entries):
            boss_findings.append(
                {
                    "severity": "error",
                    "code": "boss_mixed_in_spawn_block",
                    "message": (
                        "A literal Bosstiary boss shares one runtime spawn position "
                        "with another entry in the same group"
                    ),
                    "groupId": group_id,
                    "position": list(position),
                    "names": [entry.get("name") for entry in entries],
                }
            )

    new_boss_count = len(boss_findings)
    if new_boss_count:
        by_code["boss_mixed_in_spawn_block"] = new_boss_count
    delta = new_boss_count - old_boss_count
    finding_summary["total"] = int(finding_summary["total"]) + delta
    by_severity["error"] = int(by_severity.get("error", 0)) + delta

    sample_limit = int(report.get("policy", {}).get("sampleLimit", DEFAULT_SAMPLE_LIMIT))
    findings.extend(boss_findings)
    findings.sort(key=_finding_sort_key)
    report["findings"] = findings[:sample_limit]
    finding_summary["truncated"] = int(finding_summary["total"]) > len(report["findings"])
    finding_summary["byCode"] = dict(sorted(by_code.items()))
    report["ok"] = int(by_severity.get("error", 0)) == 0
    report.setdefault("policy", {})["runtimeBossEvidence"] = "literal-nonempty-bosstiary-class"
    report["policy"]["rewardBossKeptSeparate"] = True
    report["policy"]["monsterSpawntimeAboveOneDay"] = "rate-dependent"
    return report


def _harden_validation_semantics(report: dict[str, Any]) -> dict[str, Any]:
    """Make the bounded/global split for unresolved dynamic calls explicit."""

    dynamic = report.get("dynamicCreations", [])
    unpositioned = sum(
        1
        for entry in dynamic
        if isinstance(entry, dict)
        and entry.get("validationStatus") == "unresolved"
        and entry.get("position") is None
    )
    report.setdefault("summary", {})["unpositionedDynamicCreations"] = unpositioned
    report.setdefault("policy", {})["unpositionedDynamicEvidenceScope"] = (
        "selected-active-datapack-global"
    )
    report["policy"]["boundedDynamicPositionsOnly"] = True
    return report


def scan_active_datapack(
    *,
    datapack_root: Path,
    monster_spawn_files: Sequence[Path | str],
    npc_spawn_files: Sequence[Path | str],
    monster_definition_globs: Sequence[str] = ("monster/**/*.lua",),
    npc_definition_globs: Sequence[str] = ("npc/**/*.lua",),
    dynamic_source_globs: Sequence[str] = ("scripts/**/*.lua",),
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    report = _engine.scan_active_datapack(
        datapack_root=datapack_root,
        monster_spawn_files=monster_spawn_files,
        npc_spawn_files=npc_spawn_files,
        monster_definition_globs=monster_definition_globs,
        npc_definition_globs=npc_definition_globs,
        dynamic_source_globs=dynamic_source_globs,
        sample_limit=sample_limit,
    )
    return _harden_runtime_semantics(report, datapack_root)


def validate_evidence(**kwargs: Any) -> dict[str, Any]:
    return _harden_validation_semantics(_validate_evidence(**kwargs))


def validate_paths(**kwargs: Any) -> dict[str, Any]:
    return _harden_validation_semantics(_validate_paths(**kwargs))


__all__ = [
    "DEFAULT_SAMPLE_LIMIT",
    "EVIDENCE_FORMAT",
    "MAX_SAMPLE_LIMIT",
    "REPORT_FORMAT",
    "REACHABILITY_FORMAT",
    "SCHEMA_VERSION",
    "SpawnNpcValidationError",
    "normalize_bounds",
    "scan_active_datapack",
    "validate_evidence",
    "validate_paths",
    "write_json",
]
