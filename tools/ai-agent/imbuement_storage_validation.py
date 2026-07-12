#!/usr/bin/env python3
"""Audit Canary imbuement unlock storage IDs against active Lua storage declarations."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
IMBUEMENT_VALIDATION_PATH = SCRIPT_DIR / "imbuement_validation.py"
STORAGE_REGISTRY_PATH = Path("data-otservbr-global/lib/core/storages.lua")
CONFIG_PATH = Path("config.lua.dist")
BOSS_UNLOCK_PATH = Path(
    "data-otservbr-global/scripts/quests/forgotten_knowledge/creaturescripts_bosses_kill.lua"
)

EXPECTED_STALE_STORAGE_IDS = {50488, 50490, 50492, 50494, 50496, 50498, 50501}
CURRENT_FORGOTTEN_KNOWLEDGE_STORAGE_IDS = {
    45489,
    45490,
    45491,
    45492,
    45493,
    45494,
    45495,
}


@dataclass(frozen=True)
class StorageFinding:
    severity: str
    code: str
    message: str
    evidence: tuple[str, ...] = ()


def _load_registry_parser():
    spec = importlib.util.spec_from_file_location(
        "imbuement_validation_for_storage_audit", IMBUEMENT_VALIDATION_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {IMBUEMENT_VALIDATION_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def declared_storage_ids(lua_text: str) -> set[int]:
    """Return numeric values assigned to named Lua storage fields."""
    return {
        int(value)
        for value in re.findall(
            r"^\s*[A-Za-z_][A-Za-z0-9_]*\s*=\s*(\d+)\s*,",
            lua_text,
            re.MULTILINE,
        )
    }


def config_boolean(lua_text: str, key: str) -> bool | None:
    match = re.search(
        rf"^\s*{re.escape(key)}\s*=\s*(true|false)\s*$",
        lua_text,
        re.MULTILINE,
    )
    if match is None:
        return None
    return match.group(1) == "true"


def validate(repository_root: Path) -> tuple[dict[str, object], list[StorageFinding]]:
    parser_module = _load_registry_parser()
    registry = parser_module.parse_registry(repository_root / "data/XML/imbuements.xml")

    storage_path = repository_root / STORAGE_REGISTRY_PATH
    config_path = repository_root / CONFIG_PATH
    boss_path = repository_root / BOSS_UNLOCK_PATH
    for path in (storage_path, config_path, boss_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    declared = declared_storage_ids(storage_path.read_text(encoding="utf-8"))
    configured = {entry.storage for entry in registry.entries if entry.storage != 0}
    undeclared = sorted(configured - declared)
    affected_families = sorted(
        {entry.name for entry in registry.entries if entry.storage in set(undeclared)}
    )
    powerful_zero_storage = sorted(
        entry.name for entry in registry.entries if entry.base == 3 and entry.storage == 0
    )
    filtering_default = config_boolean(
        config_path.read_text(encoding="utf-8"), "toggleImbuementShrineStorage"
    )
    boss_text = boss_path.read_text(encoding="utf-8")
    current_fk_ids_present = sorted(
        storage_id
        for storage_id in CURRENT_FORGOTTEN_KNOWLEDGE_STORAGE_IDS
        if storage_id in declared
    )
    boss_uses_named_storages = all(
        token in boss_text
        for token in (
            "LadyTenebrisKilled",
            "LloydKilled",
            "ThornKnightKilled",
            "DragonkingKilled",
            "HorrorKilled",
            "TimeGuardianKilled",
            "LastLoreKilled",
        )
    )

    findings: list[StorageFinding] = []
    if undeclared:
        findings.append(
            StorageFinding(
                severity="error",
                code="UNDECLARED_IMBUEMENT_STORAGE",
                message=(
                    "XML uses unlock storage IDs absent from the active storage registry: "
                    f"{undeclared}; affected Powerful families: {affected_families}"
                ),
                evidence=(str(STORAGE_REGISTRY_PATH), "data/XML/imbuements.xml"),
            )
        )
    if powerful_zero_storage:
        findings.append(
            StorageFinding(
                severity="mismatch",
                code="POWERFUL_UNLOCK_BYPASS",
                message=(
                    "Powerful entries with storage=0 bypass family-specific storage filtering: "
                    f"{powerful_zero_storage}"
                ),
                evidence=("data/XML/imbuements.xml",),
            )
        )
    if filtering_default is not False:
        findings.append(
            StorageFinding(
                severity="warning",
                code="STORAGE_FILTER_DEFAULT",
                message=(
                    "toggleImbuementShrineStorage default could not be confirmed as false; "
                    f"parsed value: {filtering_default}"
                ),
                evidence=(str(CONFIG_PATH),),
            )
        )
    if not boss_uses_named_storages:
        findings.append(
            StorageFinding(
                severity="error",
                code="BOSS_UNLOCK_WIRING",
                message="Forgotten Knowledge boss deaths do not reference the expected named storages",
                evidence=(str(BOSS_UNLOCK_PATH),),
            )
        )

    baseline = {
        "configured_nonzero_storage_ids": sorted(configured),
        "undeclared_storage_ids": undeclared,
        "expected_stale_storage_ids": sorted(EXPECTED_STALE_STORAGE_IDS),
        "affected_powerful_families": affected_families,
        "powerful_with_nonzero_storage": len(affected_families),
        "powerful_with_zero_storage": powerful_zero_storage,
        "storage_filter_default": filtering_default,
        "current_forgotten_knowledge_storage_ids": current_fk_ids_present,
        "boss_script_uses_named_storages": boss_uses_named_storages,
    }
    return baseline, findings


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        baseline, findings = validate(args.repository_root.resolve())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"imbuement storage validation failed: {exc}", file=sys.stderr)
        return 2

    payload = {
        "schema_version": 1,
        "baseline": baseline,
        "findings": [asdict(finding) for finding in findings],
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    return 1 if args.strict and any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
