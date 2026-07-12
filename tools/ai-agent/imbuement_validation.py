#!/usr/bin/env python3
"""Deterministic, read-only audit of Canary's Imbuing registry and runtime wiring."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


WIKI_REFERENCE_URL = "https://tibia.fandom.com/wiki/Imbuing"
WIKI_OBSERVED_DATE = "2026-07-12"

EXPECTED_FAMILIES = (
    "Scorch", "Venom", "Frost", "Electrify", "Reap", "Vampirism", "Void", "Strike",
    "Lich Shroud", "Snake Skin", "Dragon Hide", "Quara Scale", "Cloud Fabric",
    "Demon Presence", "Swiftness", "Vibrancy", "Chop", "Slash", "Bash", "Precision",
    "Blockade", "Epiphany", "Punch", "Featherweight",
)

EXPECTED_CATEGORY_IDS = set(range(20))
EXPECTED_BASE_IDS = {1, 2, 3}
EXPECTED_WIKI_FIXED_FEES = {1: 7_500, 2: 60_000, 3: 250_000}
EXPECTED_REMOVE_COST = 15_000
EXPECTED_DURATION_SECONDS = 72_000

# Current TibiaWiki values observed on 2026-07-12.
EXPECTED_EFFECTS: dict[str, tuple[tuple[str, str | None, int, int | None], ...]] = {
    "Scorch": (("damage", "fire", 10, None), ("damage", "fire", 25, None), ("damage", "fire", 50, None)),
    "Venom": (("damage", "earth", 10, None), ("damage", "earth", 25, None), ("damage", "earth", 50, None)),
    "Frost": (("damage", "ice", 10, None), ("damage", "ice", 25, None), ("damage", "ice", 50, None)),
    "Electrify": (("damage", "energy", 10, None), ("damage", "energy", 25, None), ("damage", "energy", 50, None)),
    "Reap": (("damage", "death", 10, None), ("damage", "death", 25, None), ("damage", "death", 50, None)),
    "Vampirism": (("skill", "lifeleech", 500, None), ("skill", "lifeleech", 1000, None), ("skill", "lifeleech", 2500, None)),
    "Void": (("skill", "manaleech", 300, None), ("skill", "manaleech", 500, None), ("skill", "manaleech", 800, None)),
    "Strike": (("skill", "critical", 500, 500), ("skill", "critical", 1500, 500), ("skill", "critical", 4000, 500)),
    "Lich Shroud": (("reduction", "death", 2, None), ("reduction", "death", 5, None), ("reduction", "death", 10, None)),
    "Snake Skin": (("reduction", "earth", 3, None), ("reduction", "earth", 8, None), ("reduction", "earth", 15, None)),
    "Dragon Hide": (("reduction", "fire", 3, None), ("reduction", "fire", 8, None), ("reduction", "fire", 15, None)),
    "Quara Scale": (("reduction", "ice", 3, None), ("reduction", "ice", 8, None), ("reduction", "ice", 15, None)),
    "Cloud Fabric": (("reduction", "energy", 3, None), ("reduction", "energy", 8, None), ("reduction", "energy", 15, None)),
    "Demon Presence": (("reduction", "holy", 3, None), ("reduction", "holy", 8, None), ("reduction", "holy", 15, None)),
    "Swiftness": (("speed", None, 10, None), ("speed", None, 15, None), ("speed", None, 30, None)),
    "Vibrancy": (("paralysis", None, 15, 1), ("paralysis", None, 25, 1), ("paralysis", None, 50, 1)),
    "Chop": (("skill", "axe", 1, None), ("skill", "axe", 2, None), ("skill", "axe", 4, None)),
    "Slash": (("skill", "sword", 1, None), ("skill", "sword", 2, None), ("skill", "sword", 4, None)),
    "Bash": (("skill", "club", 1, None), ("skill", "club", 2, None), ("skill", "club", 4, None)),
    "Precision": (("skill", "distance", 1, None), ("skill", "distance", 2, None), ("skill", "distance", 4, None)),
    "Blockade": (("skill", "shield", 1, None), ("skill", "shield", 2, None), ("skill", "shield", 4, None)),
    "Epiphany": (("skill", "magicpoints", 1, None), ("skill", "magicpoints", 2, None), ("skill", "magicpoints", 4, None)),
    "Punch": (("skill", "fist", 1, None), ("skill", "fist", 2, None), ("skill", "fist", 4, None)),
    "Featherweight": (("capacity", None, 3, None), ("capacity", None, 8, None), ("capacity", None, 15, None)),
}

# Exact creature-product IDs/counts mapped from the active Canary item IDs to the
# current TibiaWiki tables. Each tier includes all sources consumed by that tier.
EXPECTED_MATERIALS: dict[str, tuple[tuple[tuple[int, int], ...], ...]] = {
    "Scorch": (((9636, 25),), ((9636, 25), (5920, 5)), ((9636, 25), (5920, 5), (5954, 5))),
    "Venom": (((9686, 25),), ((9686, 25), (9640, 20)), ((9686, 25), (9640, 20), (21194, 2))),
    "Frost": (((9661, 25),), ((9661, 25), (21801, 10)), ((9661, 25), (21801, 10), (9650, 5))),
    "Electrify": (((18993, 25),), ((18993, 25), (21975, 5)), ((18993, 25), (21975, 5), (23508, 1))),
    "Reap": (((11484, 25),), ((11484, 25), (9647, 20)), ((11484, 25), (9647, 20), (10420, 5))),
    "Vampirism": (((9685, 25),), ((9685, 25), (9633, 15)), ((9685, 25), (9633, 15), (9663, 5))),
    "Void": (((11492, 25),), ((11492, 25), (20200, 25)), ((11492, 25), (20200, 25), (22730, 5))),
    "Strike": (((11444, 20),), ((11444, 20), (10311, 25)), ((11444, 20), (10311, 25), (22728, 5))),
    "Lich Shroud": (((11466, 25),), ((11466, 25), (22007, 20)), ((11466, 25), (22007, 20), (9660, 5))),
    "Snake Skin": (((17823, 25),), ((17823, 25), (9694, 20)), ((17823, 25), (9694, 20), (11702, 10))),
    "Dragon Hide": (((5877, 20),), ((5877, 20), (16131, 10)), ((5877, 20), (16131, 10), (11658, 5))),
    "Quara Scale": (((10295, 25),), ((10295, 25), (10307, 15)), ((10295, 25), (10307, 15), (14012, 10))),
    "Cloud Fabric": (((9644, 20),), ((9644, 20), (14079, 15)), ((9644, 20), (14079, 15), (9665, 10))),
    "Demon Presence": (((9639, 25),), ((9639, 25), (9638, 25)), ((9639, 25), (9638, 25), (10304, 20))),
    "Swiftness": (((17458, 15),), ((17458, 15), (10302, 25)), ((17458, 15), (10302, 25), (14081, 20))),
    "Vibrancy": (((22053, 20),), ((22053, 20), (23507, 15)), ((22053, 20), (23507, 15), (28567, 5))),
    "Chop": (((10196, 20),), ((10196, 20), (11447, 25)), ((10196, 20), (11447, 25), (21200, 20))),
    "Slash": (((9691, 25),), ((9691, 25), (21202, 25)), ((9691, 25), (21202, 25), (9654, 5))),
    "Bash": (((9657, 20),), ((9657, 20), (22189, 15)), ((9657, 20), (22189, 15), (10405, 10))),
    "Precision": (((11464, 25),), ((11464, 25), (18994, 20)), ((11464, 25), (18994, 20), (10298, 10))),
    "Blockade": (((9641, 20),), ((9641, 20), (11703, 25)), ((9641, 20), (11703, 25), (20199, 25))),
    "Epiphany": (((9635, 25),), ((9635, 25), (11452, 15)), ((9635, 25), (11452, 15), (10309, 15))),
    "Punch": (((10281, 25),), ((10281, 25), (11489, 20)), ((10281, 25), (11489, 20), (40529, 15))),
    "Featherweight": (((25694, 20),), ((25694, 20), (25702, 10)), ((25694, 20), (25702, 10), (20205, 5))),
}

EXPECTED_SCROLLS: dict[str, tuple[int | None, int, int]] = {
    "Bash": (None, 51724, 51444),
    "Blockade": (None, 51725, 51445),
    "Chop": (None, 51726, 51446),
    "Cloud Fabric": (None, 51727, 51447),
    "Demon Presence": (None, 51728, 51448),
    "Dragon Hide": (None, 51729, 51449),
    "Electrify": (None, 51730, 51450),
    "Epiphany": (None, 51731, 51451),
    "Featherweight": (None, 51732, 51452),
    "Frost": (None, 51733, 51453),
    "Lich Shroud": (None, 51734, 51454),
    "Precision": (None, 51735, 51455),
    "Punch": (None, 51736, 51456),
    "Quara Scale": (None, 51737, 51457),
    "Reap": (None, 51738, 51458),
    "Scorch": (None, 51739, 51459),
    "Slash": (None, 51740, 51460),
    "Snake Skin": (None, 51741, 51461),
    "Strike": (None, 51742, 51462),
    "Swiftness": (None, 51743, 51463),
    "Vampirism": (None, 51744, 51464),
    "Venom": (None, 51745, 51465),
    "Vibrancy": (None, 51746, 51466),
    "Void": (None, 51747, 51467),
}

POWERFUL_REQUIRES_UNLOCK = set(EXPECTED_FAMILIES)

RUNTIME_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "src/creatures/players/imbuements/imbuements.cpp": (
        "loadFromXml", "ImbuementStoragePolicy::shouldHide", "getImbuementByScrollID",
        "canDecayImbuement", "checkImbuementDecay",
    ),
    "src/game/game.cpp": (
        "playerApplyImbuement", "playerClearImbuement",
    ),
    "src/creatures/players/player.hpp": (
        "applyImbuementScroll", "onApplyImbuement", "onClearImbuement",
        "clearAllImbuements", "openImbuementWindow",
    ),
    "data-otservbr-global/scripts/actions/object/imbuement_shrine.lua": (
        "TOGGLE_IMBUEMENT_SHRINE_STORAGE", "openImbuementWindow",
    ),
    "data-otservbr-global/scripts/actions/object/imbuement_scrolls.lua": (
        "applyImbuementScroll", "51444", "51467", "51724", "51747",
    ),
    "data-otservbr-global/scripts/actions/object/etcher.lua": (
        "clearAllImbuements", "51443",
    ),
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class BaseTier:
    id: int
    name: str
    price: int
    protection_price: int
    percent: int
    remove_cost: int
    duration: int


@dataclass(frozen=True)
class Entry:
    running_id: int
    name: str
    base: int
    category: int
    premium: bool
    storage: int
    icon_id: int
    description: str
    effect: Mapping[str, str]
    materials: tuple[tuple[int, int], ...]
    scroll: int | None


@dataclass(frozen=True)
class Registry:
    bases: Mapping[int, BaseTier]
    categories: Mapping[int, str]
    entries: tuple[Entry, ...]


def _integer(attrs: Mapping[str, str], key: str, *, default: int | None = None) -> int:
    value = attrs.get(key)
    if value is None:
        if default is None:
            raise ValueError(f"missing integer attribute {key}")
        return default
    return int(value)


def parse_registry(path: Path) -> Registry:
    root = ET.parse(path).getroot()
    if root.tag != "imbuements":
        raise ValueError(f"expected <imbuements>, got <{root.tag}>")

    bases: dict[int, BaseTier] = {}
    categories: dict[int, str] = {}
    entries: list[Entry] = []
    running_id = 0

    for node in root:
        if node.tag == "base":
            base = BaseTier(
                id=_integer(node.attrib, "id"),
                name=node.attrib.get("name", ""),
                price=_integer(node.attrib, "price"),
                protection_price=_integer(node.attrib, "protectionPrice"),
                percent=_integer(node.attrib, "percent"),
                remove_cost=_integer(node.attrib, "removecost"),
                duration=_integer(node.attrib, "duration"),
            )
            if base.id in bases:
                raise ValueError(f"duplicate base id {base.id}")
            bases[base.id] = base
            continue

        if node.tag == "category":
            category_id = _integer(node.attrib, "id")
            if category_id in categories:
                raise ValueError(f"duplicate category id {category_id}")
            categories[category_id] = node.attrib.get("name", "")
            continue

        if node.tag != "imbuement":
            continue

        running_id += 1
        descriptions: list[str] = []
        effects: list[Mapping[str, str]] = []
        materials: list[tuple[int, int]] = []
        scrolls: list[int] = []

        for child in node:
            if child.tag != "attribute":
                continue
            key = child.attrib.get("key")
            if key == "description":
                descriptions.append(child.attrib.get("value", ""))
            elif key == "effect":
                effects.append(dict(child.attrib))
            elif key == "item":
                materials.append((_integer(child.attrib, "value"), _integer(child.attrib, "count", default=1)))
            elif key == "scroll":
                scrolls.append(_integer(child.attrib, "value"))

        if len(descriptions) > 1 or len(effects) > 1 or len(scrolls) > 1:
            raise ValueError(f"duplicate singleton child attribute in {node.attrib.get('name', '<unnamed>')}")

        entries.append(
            Entry(
                running_id=running_id,
                name=node.attrib.get("name", ""),
                base=_integer(node.attrib, "base"),
                category=_integer(node.attrib, "category"),
                premium=node.attrib.get("premium", "0") in {"1", "true", "yes"},
                storage=_integer(node.attrib, "storage", default=0),
                icon_id=_integer(node.attrib, "iconid"),
                description=descriptions[0] if descriptions else "",
                effect=effects[0] if effects else {},
                materials=tuple(materials),
                scroll=scrolls[0] if scrolls else None,
            )
        )

    return Registry(bases=bases, categories=categories, entries=tuple(entries))


def _effect_signature(entry: Entry) -> tuple[str, str | None, int, int | None] | None:
    effect_type = entry.effect.get("type")
    if not effect_type:
        return None
    if effect_type in {"damage", "reduction"}:
        return effect_type, entry.effect.get("combat"), int(entry.effect.get("value", "0")), None
    if effect_type == "skill":
        secondary = int(entry.effect["chance"]) if entry.effect.get("value") == "critical" and "chance" in entry.effect else None
        return effect_type, entry.effect.get("value"), int(entry.effect.get("bonus", "0")), secondary
    if effect_type in {"speed", "capacity"}:
        return effect_type, None, int(entry.effect.get("value", "0")), None
    if effect_type in {"paralysis", "vibrancy"}:
        chance = int(entry.effect.get("chance", entry.effect.get("value", "0")))
        return "paralysis", None, chance, int(entry.effect.get("pvpDeflect", "0"))
    return effect_type, entry.effect.get("value"), 0, None


def _add(findings: list[Finding], severity: str, code: str, message: str, *evidence: str) -> None:
    findings.append(Finding(severity, code, message, tuple(evidence)))


def validate_registry(registry: Registry, repository_root: Path | None = None) -> list[Finding]:
    findings: list[Finding] = []

    if set(registry.bases) != EXPECTED_BASE_IDS:
        _add(findings, "error", "BASE_ID_SET", f"base IDs are {sorted(registry.bases)}, expected {sorted(EXPECTED_BASE_IDS)}")
    if set(registry.categories) != EXPECTED_CATEGORY_IDS:
        _add(findings, "error", "CATEGORY_ID_SET", f"category IDs are {sorted(registry.categories)}, expected 0..19")

    if len(registry.entries) != len(EXPECTED_FAMILIES) * 3:
        _add(findings, "error", "ENTRY_COUNT", f"registry has {len(registry.entries)} entries, expected 72")

    families: dict[str, dict[int, Entry]] = defaultdict(dict)
    scroll_counts: Counter[int] = Counter()
    for entry in registry.entries:
        if not entry.name:
            _add(findings, "error", "MISSING_NAME", f"entry {entry.running_id} has no name")
        if entry.base not in registry.bases:
            _add(findings, "error", "UNKNOWN_BASE", f"{entry.name} references base {entry.base}")
        if entry.category not in registry.categories:
            _add(findings, "error", "UNKNOWN_CATEGORY", f"{entry.name} references category {entry.category}")
        if entry.base in families[entry.name]:
            _add(findings, "error", "DUPLICATE_FAMILY_TIER", f"{entry.name} has duplicate base {entry.base}")
        families[entry.name][entry.base] = entry
        if not entry.description:
            _add(findings, "error", "MISSING_DESCRIPTION", f"{entry.name} tier {entry.base} has no description")
        if not entry.effect:
            _add(findings, "error", "MISSING_EFFECT", f"{entry.name} tier {entry.base} has no effect")
        if not entry.materials:
            _add(findings, "error", "MISSING_MATERIALS", f"{entry.name} tier {entry.base} has no materials")
        if any(item_id <= 0 or count <= 0 for item_id, count in entry.materials):
            _add(findings, "error", "INVALID_MATERIAL", f"{entry.name} tier {entry.base} has non-positive material data")
        if len({item_id for item_id, _ in entry.materials}) != len(entry.materials):
            _add(findings, "error", "DUPLICATE_MATERIAL", f"{entry.name} tier {entry.base} repeats a source item")
        if entry.scroll is not None:
            scroll_counts[entry.scroll] += 1

    actual_names = set(families)
    expected_names = set(EXPECTED_FAMILIES)
    if actual_names != expected_names:
        _add(
            findings, "error", "FAMILY_SET",
            f"family set differs; missing={sorted(expected_names - actual_names)}, extra={sorted(actual_names - expected_names)}",
        )

    for family, tiers in sorted(families.items()):
        if set(tiers) != EXPECTED_BASE_IDS:
            _add(findings, "error", "INCOMPLETE_FAMILY", f"{family} tiers are {sorted(tiers)}, expected [1, 2, 3]")
            continue
        categories = {entry.category for entry in tiers.values()}
        if len(categories) != 1:
            _add(findings, "error", "CATEGORY_DRIFT", f"{family} changes category across tiers: {sorted(categories)}")
        for tier, entry in tiers.items():
            expected_premium = tier > 1
            if entry.premium != expected_premium:
                _add(
                    findings, "warning", "PREMIUM_FLAG",
                    f"{family} tier {tier} premium={entry.premium}, expected {expected_premium}",
                )

    duplicates = sorted(scroll_id for scroll_id, count in scroll_counts.items() if count > 1)
    if duplicates:
        _add(findings, "error", "DUPLICATE_SCROLL_ID", f"duplicate scroll IDs: {duplicates}")

    # Current TibiaWiki comparison.
    for family in EXPECTED_FAMILIES:
        tiers = families.get(family)
        if not tiers or set(tiers) != EXPECTED_BASE_IDS:
            continue
        for tier in (1, 2, 3):
            entry = tiers[tier]
            expected_effect = EXPECTED_EFFECTS[family][tier - 1]
            actual_effect = _effect_signature(entry)
            if actual_effect != expected_effect:
                _add(
                    findings, "mismatch", "WIKI_EFFECT",
                    f"{family} tier {tier} effect {actual_effect} differs from TibiaWiki {expected_effect}",
                    WIKI_REFERENCE_URL,
                )
            expected_materials = EXPECTED_MATERIALS[family][tier - 1]
            if entry.materials != expected_materials:
                _add(
                    findings, "mismatch", "WIKI_MATERIALS",
                    f"{family} tier {tier} materials {entry.materials} differ from TibiaWiki {expected_materials}",
                    WIKI_REFERENCE_URL,
                )
            expected_scroll = EXPECTED_SCROLLS[family][tier - 1]
            if entry.scroll != expected_scroll:
                _add(
                    findings, "mismatch", "WIKI_SCROLL",
                    f"{family} tier {tier} scroll {entry.scroll} differs from TibiaWiki mapping {expected_scroll}",
                    WIKI_REFERENCE_URL,
                )

        powerful = tiers[3]
        if family in POWERFUL_REQUIRES_UNLOCK and powerful.storage == 0:
            _add(
                findings, "mismatch", "WIKI_POWERFUL_UNLOCK",
                f"Powerful {family} has storage=0 although TibiaWiki documents a quest/boss unlock",
                WIKI_REFERENCE_URL,
            )

    # Fee model comparison is explicit because the active XML models chance plus
    # optional protection, while the current reference lists one fixed fee.
    for tier_id, expected_fee in EXPECTED_WIKI_FIXED_FEES.items():
        base = registry.bases.get(tier_id)
        if not base:
            continue
        guaranteed_cost = base.price + base.protection_price
        if base.price != expected_fee or base.percent != 100 or base.protection_price != 0:
            _add(
                findings, "mismatch", "WIKI_FEE_MODEL",
                (
                    f"{base.name} uses price={base.price}, success={base.percent}%, "
                    f"protection={base.protection_price} (guaranteed total {guaranteed_cost}); "
                    f"TibiaWiki lists a fixed fee of {expected_fee}"
                ),
                WIKI_REFERENCE_URL,
            )
        if base.remove_cost != EXPECTED_REMOVE_COST:
            _add(
                findings, "mismatch", "WIKI_REMOVE_COST",
                f"{base.name} remove cost is {base.remove_cost}, expected {EXPECTED_REMOVE_COST}",
                WIKI_REFERENCE_URL,
            )
        if base.duration != EXPECTED_DURATION_SECONDS:
            _add(
                findings, "mismatch", "WIKI_DURATION",
                f"{base.name} duration is {base.duration}s, expected {EXPECTED_DURATION_SECONDS}s",
                WIKI_REFERENCE_URL,
            )

    if repository_root is not None:
        findings.extend(validate_runtime_wiring(repository_root, registry))

    return findings


def _registered_scroll_ids(lua_text: str) -> set[int]:
    result: set[int] = set()
    for start, end in re.findall(r"for\s+\w+\s*=\s*(\d+)\s*,\s*(\d+)\s+do", lua_text):
        result.update(range(int(start), int(end) + 1))
    for args in re.findall(r"imbuement:id\(([^)]*)\)", lua_text):
        for token in args.split(","):
            token = token.strip()
            if token.isdigit():
                result.add(int(token))
    return result


def validate_runtime_wiring(repository_root: Path, registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for relative_path, tokens in RUNTIME_REQUIREMENTS.items():
        path = repository_root / relative_path
        if not path.is_file():
            _add(findings, "error", "MISSING_RUNTIME_PATH", f"required runtime path is missing: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [token for token in tokens if token not in text]
        if missing:
            _add(
                findings, "error", "MISSING_RUNTIME_MARKER",
                f"{relative_path} is missing expected markers {missing}",
            )

    scroll_script = repository_root / "data-otservbr-global/scripts/actions/object/imbuement_scrolls.lua"
    if scroll_script.is_file():
        registered = _registered_scroll_ids(scroll_script.read_text(encoding="utf-8"))
        mapped = {entry.scroll for entry in registry.entries if entry.scroll is not None}
        orphaned = sorted(registered - mapped)
        unregistered = sorted(mapped - registered)
        if orphaned:
            _add(
                findings, "error", "ORPHAN_REGISTERED_SCROLL",
                f"Lua registers scroll IDs that XML cannot resolve: {orphaned}",
                str(scroll_script.relative_to(repository_root)),
                "data/XML/imbuements.xml",
            )
        if unregistered:
            _add(
                findings, "error", "UNREGISTERED_XML_SCROLL",
                f"XML maps scroll IDs that the active action does not register: {unregistered}",
            )

    return findings


def build_runtime_plan(registry: Registry, findings: Sequence[Finding]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "source": {
            "registry": "data/XML/imbuements.xml",
            "reference": WIKI_REFERENCE_URL,
            "reference_observed": WIKI_OBSERVED_DATE,
        },
        "baseline": {
            "base_tiers": len(registry.bases),
            "categories": len(registry.categories),
            "families": len({entry.name for entry in registry.entries}),
            "entries": len(registry.entries),
            "mapped_scrolls": len({entry.scroll for entry in registry.entries if entry.scroll is not None}),
        },
        "known_findings": [asdict(finding) for finding in findings],
        "scenarios": [
            {
                "id": "shrine-access-gate",
                "layer": "gameplay",
                "assertions": [
                    "locked player cannot open the shrine when storage filtering is enabled",
                    "unlocked player can open the shrine",
                ],
            },
            {
                "id": "tier-account-and-storage-policy",
                "layer": "gameplay",
                "assertions": [
                    "free account can apply Basic after the common unlock",
                    "premium account can apply Intricate after the common unlock",
                    "Powerful entries remain hidden until their documented unlock storage is set",
                ],
            },
            {
                "id": "application-cost-and-atomicity",
                "layer": "runtime",
                "assertions": [
                    "displayed fee, success policy and charged fee match the approved target model",
                    "missing gold or materials leaves all resources and item slots unchanged",
                    "successful application consumes each source exactly once",
                ],
            },
            {
                "id": "strike-effect",
                "layer": "gameplay",
                "assertions": [
                    "critical chance and damage match the approved Tibia reference for all three tiers",
                ],
            },
            {
                "id": "punch-materials",
                "layer": "gameplay",
                "assertions": [
                    "Basic, Intricate and Powerful Punch consume the current documented source chain",
                ],
            },
            {
                "id": "vibrancy-scrolls",
                "layer": "gameplay",
                "fixtures": {"scroll_ids": [51746, 51466]},
                "assertions": [
                    "each scroll resolves to Vibrancy",
                    "a valid boot receives the correct tier",
                    "the scroll is consumed only after successful application",
                ],
            },
            {
                "id": "duplicate-category-rejection",
                "layer": "gameplay",
                "assertions": [
                    "an item cannot receive two entries from the same category",
                    "rejection does not consume resources",
                ],
            },
            {
                "id": "clearing",
                "layer": "gameplay",
                "assertions": [
                    "single-slot shrine clearing charges 15000 gold",
                    "Etcher clears all active slots and is consumed only on success",
                ],
            },
            {
                "id": "duration-combat",
                "layer": "runtime",
                "assertions": [
                    "combat imbuements decay only while equipped and in combat outside protection zones",
                    "combat imbuements do not decay in backpack or while out of combat",
                ],
            },
            {
                "id": "duration-noncombat",
                "layer": "runtime",
                "assertions": [
                    "Swiftness and Featherweight decay while their item is directly equipped",
                    "they do not decay while stored in a container",
                ],
            },
            {
                "id": "persistence",
                "layer": "runtime",
                "assertions": [
                    "imbuement IDs and remaining duration survive save/logout/login",
                    "expired effects are removed exactly once",
                ],
            },
            {
                "id": "item-eligibility",
                "layer": "static-and-gameplay",
                "assertions": [
                    "only item-declared categories and tiers appear in the shrine",
                    "native conflicting bonuses are not offered",
                    "Legs are not imbuable under the approved Tibia rules",
                ],
            },
        ],
    }


def summarize(findings: Iterable[Finding]) -> dict[str, int]:
    counts = Counter(finding.severity for finding in findings)
    return dict(sorted(counts.items()))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--xml", type=Path, default=Path("data/XML/imbuements.xml"))
    parser.add_argument("--output", type=Path, help="write the complete audit as JSON")
    parser.add_argument("--runtime-plan", type=Path, help="write a machine-readable runtime test plan")
    parser.add_argument(
        "--fail-on",
        choices=("none", "error", "mismatch", "warning"),
        default="none",
        help="return non-zero when at least one selected severity exists",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.repository_root.resolve()
    xml_path = args.xml if args.xml.is_absolute() else root / args.xml
    try:
        registry = parse_registry(xml_path)
        findings = validate_registry(registry, root)
    except (OSError, ET.ParseError, ValueError) as exc:
        print(f"imbuement validation failed: {exc}", file=sys.stderr)
        return 2

    payload = {
        "schema_version": 1,
        "reference": {
            "url": WIKI_REFERENCE_URL,
            "observed": WIKI_OBSERVED_DATE,
        },
        "summary": {
            "base_tiers": len(registry.bases),
            "categories": len(registry.categories),
            "families": len({entry.name for entry in registry.entries}),
            "entries": len(registry.entries),
            "findings": summarize(findings),
        },
        "findings": [asdict(finding) for finding in findings],
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    if args.runtime_plan:
        args.runtime_plan.parent.mkdir(parents=True, exist_ok=True)
        args.runtime_plan.write_text(
            json.dumps(build_runtime_plan(registry, findings), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.fail_on == "none":
        return 0
    threshold = {"warning": 1, "mismatch": 2, "error": 3}
    selected = threshold[args.fail_on]
    return 1 if any(threshold.get(finding.severity, 0) >= selected for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
