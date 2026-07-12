#!/usr/bin/env python3
"""Build a deterministic, read-only evidence report for Canary Cyclopedia."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
ACTIVE_MONSTER_ROOTS = ("data/monster", "data-otservbr-global/monster")
CHARM_REGISTRY = "data/scripts/systems/bestiary_charms.lua"
CHARM_HELPER = "data/scripts/lib/register_bestiary_charm.lua"
BESTIARY_CPP = "src/io/iobestiary.cpp"
BOSSTIARY_CPP = "src/io/io_bosstiary.cpp"
PLAYER_CYCLOPEDIA_CPP = "src/creatures/players/components/player_cyclopedia.cpp"
SCHEMA_SQL = "schema.sql"
SERVER_PROTOCOL = ("src/server/network/protocol/protocolgame.hpp", "src/server/network/protocol/protocolgame.cpp")
CLIENT_PROTOCOL = ("src/client/protocolgame.h", "src/client/protocolgameparse.cpp", "src/client/protocolgamesend.cpp")
DOMAIN_SOURCES = {
    "items": ("src/server/network/protocol/protocolgame.cpp", "src/items/items.cpp", "src/items/items.hpp"),
    "bestiary": (BESTIARY_CPP, "src/io/iobestiary.hpp", "src/creatures/monsters/monsters.cpp"),
    "charms": (CHARM_REGISTRY, CHARM_HELPER, BESTIARY_CPP),
    "bosstiary": (BOSSTIARY_CPP, "src/io/io_bosstiary.hpp", SCHEMA_SQL),
    "map": ("src/enums/player_cyclopedia.hpp", "src/server/network/protocol/protocolgame.cpp"),
    "character": (PLAYER_CYCLOPEDIA_CPP, "src/creatures/players/components/player_title.cpp", "src/creatures/players/components/player_title.hpp"),
    "houses": ("src/map/house/house.cpp", "src/map/house/house.hpp", "src/map/house/houses.cpp", "src/map/house/houses.hpp", SCHEMA_SQL),
}
CHARM_REQUIRED = ("name", "category", "type", "chance", "points")
BESTIARY_REQUIRED = ("class", "toKill", "FirstUnlock", "SecondUnlock", "CharmsPoints", "Stars", "Occurrence")
CHARM_CATEGORIES = {"CHARM_MAJOR", "CHARM_MINOR"}
CHARM_TYPES = {"CHARM_OFFENSIVE", "CHARM_DEFENSIVE", "CHARM_PASSIVE"}
BOSS_RARITIES = {"RARITY_BANE", "RARITY_ARCHFOE", "RARITY_NEMESIS"}
NUMBER = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)")


def git_head(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def read_text(root: Path, relative: str) -> str | None:
    try:
        return (root / relative).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def matching_brace(text: str, start: int) -> int:
    depth, index = 0, start
    quote: str | None = None
    escaped = comment = False
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if comment:
            comment = char != "\n"
        elif quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char == "-" and following == "-":
            comment = True
            index += 1
        elif char in {'"', "'"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise ValueError(f"unclosed brace at {start}")


def lua_table(text: str, name: str) -> tuple[str, int] | None:
    match = re.search(rf"(?im)^\s*{re.escape(name)}\s*=\s*\{{", text)
    if not match:
        return None
    opening = text.find("{", match.start(), match.end())
    try:
        closing = matching_brace(text, opening)
    except ValueError:
        return None
    return text[opening + 1 : closing], line_number(text, match.start())


def cpp_function(text: str, name: str) -> tuple[str, int] | None:
    match = re.search(rf"\b(?:[\w:<>,&*\s]+\s+)?{re.escape(name)}\s*\([^;{{]*\)\s*(?:const\s*)?\{{", text)
    if not match:
        return None
    opening = text.find("{", match.start(), match.end())
    try:
        closing = matching_brace(text, opening)
    except ValueError:
        return None
    return text[match.start() : closing + 1], line_number(text, match.start())


def scalar(body: str, field: str) -> str | int | float | None:
    string = re.search(rf"\b{re.escape(field)}\s*=\s*([\"'])(.*?)\1", body, re.S)
    if string:
        return string.group(2).replace("\\z", "").strip()
    token = re.search(rf"\b{re.escape(field)}\s*=\s*([A-Za-z_][A-Za-z0-9_]*|[-+]?(?:\d+(?:\.\d*)?|\.\d+))", body)
    if not token:
        return None
    value = token.group(1)
    if not NUMBER.fullmatch(value):
        return value
    number = float(value)
    return int(number) if number.is_integer() else number


def number_list(body: str, field: str) -> list[int | float] | None:
    match = re.search(rf"\b{re.escape(field)}\s*=\s*\{{([^}}]*)\}}", body, re.S)
    if not match:
        return None
    values: list[int | float] = []
    for raw in NUMBER.findall(match.group(1)):
        number = float(raw)
        values.append(int(number) if number.is_integer() else number)
    return values


def finding(fid: str, domain: str, severity: str, disposition: str, confidence: str, message: str, path: str | None = None, line: int | None = None, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"id": fid, "domain": domain, "severity": severity, "disposition": disposition, "confidence": confidence, "message": message}
    if path:
        result["path"] = path
    if line:
        result["line"] = line
    if evidence:
        result["evidence"] = evidence
    return result


def parse_charm_registry(text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for match in re.finditer(r"(?m)^\s*\[(\d+)\]\s*=\s*\{", text):
        lua_id = int(match.group(1))
        opening = text.find("{", match.start(), match.end())
        body = text[opening + 1 : matching_brace(text, opening)]
        entry: dict[str, Any] = {"luaId": lua_id, "internalId": lua_id - 1, "line": line_number(text, match.start())}
        for field in ("name", "category", "type", "damageType", "percent"):
            if (value := scalar(body, field)) is not None:
                entry[field] = value
        for field in ("chance", "points"):
            if (value := number_list(body, field)) is not None:
                entry[field] = value
        entries.append(entry)
    return entries


def validate_charms(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ids = [entry["luaId"] for entry in entries]
    for value, count in Counter(ids).items():
        if count > 1:
            out.append(finding(f"CHARM-DUPLICATE-ID-{value}", "charms", "error", "definition-invalid", "high", f"Charm Lua ID {value} is defined {count} times.", CHARM_REGISTRY))
    for value, count in Counter(entry.get("name") for entry in entries if entry.get("name")).items():
        if count > 1:
            out.append(finding("CHARM-DUPLICATE-NAME", "charms", "error", "definition-invalid", "high", f"Charm name {value!r} is defined {count} times.", CHARM_REGISTRY))
    if ids and sorted(set(ids)) != list(range(min(ids), max(ids) + 1)):
        out.append(finding("CHARM-SPARSE-LUA-IDS", "charms", "warning", "definition-needs-review", "high", "Charm Lua IDs are sparse; ipairs registration can stop before later entries.", CHARM_REGISTRY, evidence={"ids": sorted(set(ids))}))
    for entry in entries:
        missing = [field for field in CHARM_REQUIRED if field not in entry]
        if missing:
            out.append(finding(f"CHARM-{entry['luaId']}-MISSING-FIELDS", "charms", "error", "definition-invalid", "high", f"Missing fields: {', '.join(missing)}.", CHARM_REGISTRY, entry["line"]))
        if entry.get("category") not in CHARM_CATEGORIES:
            out.append(finding(f"CHARM-{entry['luaId']}-CATEGORY", "charms", "error", "definition-invalid", "high", f"Unsupported category {entry.get('category')!r}.", CHARM_REGISTRY, entry["line"]))
        if entry.get("type") not in CHARM_TYPES:
            out.append(finding(f"CHARM-{entry['luaId']}-TYPE", "charms", "error", "definition-invalid", "high", f"Unsupported type {entry.get('type')!r}.", CHARM_REGISTRY, entry["line"]))
        for field in ("chance", "points"):
            if (values := entry.get(field)) is not None and len(values) != 3:
                out.append(finding(f"CHARM-{entry['luaId']}-{field.upper()}-TIERS", "charms", "error", "definition-invalid", "high", f"Expected 3 {field} tiers, found {len(values)}.", CHARM_REGISTRY, entry["line"]))
    return out


def parse_monster_definition(text: str, path: str) -> dict[str, Any]:
    name = re.search(r"Game\.createMonsterType\s*\(\s*([\"'])(.*?)\1\s*\)", text, re.S)
    race = re.search(r"(?im)^\s*monster\.raceId\s*=\s*(\d+)\s*$", text)
    item: dict[str, Any] = {"path": path, "name": name.group(2).strip() if name else None, "raceId": int(race.group(1)) if race else None}
    if table := lua_table(text, "monster.Bestiary"):
        body, line = table
        data: dict[str, Any] = {"line": line}
        for field in BESTIARY_REQUIRED + ("race", "Locations"):
            if (value := scalar(body, field)) is not None:
                data[field] = value
        item["bestiary"] = data
    if table := lua_table(text, "monster.bosstiary"):
        body, line = table
        item["bosstiary"] = {"line": line, **{field: value for field in ("bossRaceId", "bossRace") if (value := scalar(body, field)) is not None}}
    return item


def collect_monsters(root: Path) -> dict[str, Any]:
    roots: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for relative in ACTIVE_MONSTER_ROOTS:
        directory = root / relative
        files = sorted(directory.rglob("*.lua")) if directory.is_dir() else []
        roots.append({"path": relative, "exists": directory.is_dir(), "files": len(files)})
        for path in files:
            try:
                item = parse_monster_definition(path.read_text(encoding="utf-8", errors="replace"), path.relative_to(root).as_posix())
            except OSError:
                continue
            if item.get("raceId") is not None or "bestiary" in item or "bosstiary" in item:
                records.append(item)
    bestiary = [item for item in records if "bestiary" in item]
    bosstiary = [item for item in records if "bosstiary" in item]
    return {"roots": roots, "records": records, "bestiaryEntries": bestiary, "bosstiaryEntries": bosstiary, "summary": {"scannedFiles": sum(item["files"] for item in roots), "records": len(records), "bestiaryEntries": len(bestiary), "bosstiaryEntries": len(bosstiary)}}


def validate_monsters(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not any(root["exists"] for root in inventory["roots"]):
        return [finding("ACTIVE-MONSTER-DATAPACK-MISSING", "bestiary", "error", "definition-invalid", "high", "Neither active monster datapack root exists.", evidence={"roots": list(ACTIVE_MONSTER_ROOTS)})]
    bestiary_ids: dict[int, list[str]] = defaultdict(list)
    boss_ids: dict[int, list[str]] = defaultdict(list)
    for item in inventory["bestiaryEntries"]:
        data, path, race_id = item["bestiary"], item["path"], item.get("raceId")
        if not isinstance(race_id, int) or race_id <= 0:
            out.append(finding("BESTIARY-MISSING-RACE-ID", "bestiary", "error", "definition-invalid", "high", "Bestiary table has no positive monster.raceId.", path, data["line"], {"name": item.get("name")}))
        else:
            bestiary_ids[race_id].append(path)
        missing = [field for field in BESTIARY_REQUIRED if field not in data]
        if missing:
            out.append(finding("BESTIARY-MISSING-FIELDS", "bestiary", "error", "definition-invalid", "high", f"Missing fields: {', '.join(missing)}.", path, data["line"], {"name": item.get("name"), "raceId": race_id}))
        if "race" not in data:
            out.append(finding("BESTIARY-MISSING-RACE-METADATA", "bestiary", "warning", "display-metadata-defect", "high", "Bestiary.race is absent; the loader leaves the numeric race as BESTY_RACE_NONE, so numeric race filters and unlocked counts can omit this entry.", path, data["line"], {"name": item.get("name"), "raceId": race_id}))
        values = [data.get("FirstUnlock"), data.get("SecondUnlock"), data.get("toKill")]
        if all(isinstance(value, (int, float)) for value in values):
            first, second, total = values
            if first < 0 or second < first or total < second or total <= 0:
                out.append(finding("BESTIARY-INVALID-THRESHOLDS", "bestiary", "error", "definition-invalid", "high", "Thresholds must satisfy 0 <= FirstUnlock <= SecondUnlock <= toKill and toKill > 0.", path, data["line"], {"raceId": race_id, "FirstUnlock": first, "SecondUnlock": second, "toKill": total}))
    for race_id, paths in sorted(bestiary_ids.items()):
        if len(paths) > 1:
            out.append(finding(f"BESTIARY-DUPLICATE-RACE-ID-{race_id}", "bestiary", "warning", "definition-needs-review", "high", f"Bestiary race ID {race_id} is used by {len(paths)} active definitions.", evidence={"paths": paths}))
    for item in inventory["bosstiaryEntries"]:
        data, path = item["bosstiary"], item["path"]
        boss_id, rarity = data.get("bossRaceId"), data.get("bossRace")
        if not isinstance(boss_id, int) or boss_id <= 0:
            out.append(finding("BOSSTIARY-MISSING-BOSS-RACE-ID", "bosstiary", "error", "definition-invalid", "high", "Bosstiary table has no positive bossRaceId.", path, data["line"], {"name": item.get("name")}))
        else:
            boss_ids[boss_id].append(path)
        if rarity not in BOSS_RARITIES:
            out.append(finding("BOSSTIARY-INVALID-RARITY", "bosstiary", "error", "definition-invalid", "high", f"Unsupported rarity {rarity!r}.", path, data["line"], {"bossRaceId": boss_id}))
    for boss_id, paths in sorted(boss_ids.items()):
        if len(paths) > 1:
            out.append(finding(f"BOSSTIARY-DUPLICATE-BOSS-RACE-ID-{boss_id}", "bosstiary", "warning", "definition-needs-review", "high", f"Bosstiary boss ID {boss_id} is used by {len(paths)} active definitions.", evidence={"paths": paths}))
    return out


def protocol_method(name: str) -> bool:
    lowered = name.lower()
    return any(word in lowered for word in ("cyclopedia", "bestiary", "bosstiary")) or lowered in {"sendhousesinfo", "senditemsprice", "senditeminspection", "parseinspectionobject", "sendcharmresourcesbalance", "sendcharmresourcebalance"}


def method_domain(name: str) -> str:
    lowered = name.lower()
    if "bosstiary" in lowered or "bossslot" in lowered:
        return "bosstiary"
    if "charm" in lowered:
        return "charms"
    if "bestiary" in lowered:
        return "bestiary"
    if "house" in lowered:
        return "houses"
    if any(word in lowered for word in ("character", "title", "badge")):
        return "character"
    if "map" in lowered:
        return "map"
    if "item" in lowered or "inspection" in lowered:
        return "items"
    return "unclassified"


def collect_protocol_methods(header: str | None, source: str | None) -> dict[str, Any]:
    declarations = sorted({m.group(1) for m in re.finditer(r"\bvoid\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", header or "") if protocol_method(m.group(1))})
    definitions = sorted({m.group(1) for m in re.finditer(r"\bvoid\s+ProtocolGame::([A-Za-z_][A-Za-z0-9_]*)\s*\(", source or "") if protocol_method(m.group(1))})
    by_domain: dict[str, dict[str, list[str]]] = defaultdict(lambda: {"declarations": [], "definitions": []})
    for name in declarations:
        by_domain[method_domain(name)]["declarations"].append(name)
    for name in definitions:
        by_domain[method_domain(name)]["definitions"].append(name)
    return {"declarations": declarations, "definitions": definitions, "missingDefinitions": sorted(set(declarations) - set(definitions)), "undeclaredDefinitions": sorted(set(definitions) - set(declarations)), "byDomain": dict(sorted(by_domain.items()))}


def known_patterns(root: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    helper = read_text(root, CHARM_HELPER) or ""
    if match := re.search(r"registerCharm\.category\s*=\s*function.*?if\s+mask\.type\s+then.*?charm:category\s*\(\s*mask\.category\s*\)", helper, re.S):
        out.append(finding("CHARM-CATEGORY-GUARD-USES-TYPE", "charms", "warning", "latent-helper-defect", "high", "Charm category registration is guarded by mask.type instead of mask.category.", CHARM_HELPER, line_number(helper, match.start())))
    bestiary = read_text(root, BESTIARY_CPP) or ""
    if match := re.search(r"resetAllCharmsCost\s*=\s*100000\s*\+\s*\(\s*playerLevel\s*>\s*100\s*\?\s*playerLevel\s*\*\s*11000", bestiary):
        out.append(finding("CHARM-RESET-ALL-LEVEL-FORMULA", "charms", "warning", "needs-evidence", "medium", "Full reset multiplies the entire level by 11,000 after level 100; verify whether only levels above 100 should count.", BESTIARY_CPP, line_number(bestiary, match.start()), {"boundaryTests": [100, 101, 102]}))
    if match := re.search(r"\bfloat(?:_t)?\s+chanceInPercent\s*=\s*chance\s*/\s*1000\s*;", bestiary):
        out.append(finding("BESTIARY-DIFFICULTY-INTEGER-DIVISION", "bestiary", "error", "confirmed-runtime-defect", "high", "Difficulty uses integer division before floating-point assignment, collapsing the fractional band.", BESTIARY_CPP, line_number(bestiary, match.start())))
    if function := cpp_function(bestiary, "IOBestiary::addBestiaryKill"):
        body, line = function
        if -1 < body.find("mtype->") < body.find("!mtype"):
            out.append(finding("BESTIARY-MTYPE-DEREFERENCE-BEFORE-GUARD", "bestiary", "warning", "latent-helper-defect", "high", "addBestiaryKill dereferences mtype before its explicit null guard.", BESTIARY_CPP, line))
    character = read_text(root, PLAYER_CYCLOPEDIA_CPP) or ""
    function = next((candidate for name in ("PlayerCyclopedia::loadRecentKills", "PlayerCyclopedia::loadRecentPvPKills") if (candidate := cpp_function(character, name))), None)
    if function:
        body, line = function
        start = re.search(r"\(\s*select\s+count\s*\(\s*\*\s*\)", body, re.I)
        count_query = None
        if start and (alias := re.search(r"\bas\s+`?entries`?", body[start.start() :], re.I)):
            count_query = body[start.start() : start.start() + alias.end()]
        if count_query and "INTERVAL 70 DAY" in body and "INTERVAL 70 DAY" not in count_query:
            out.append(finding("CHARACTER-RECENT-PVP-COUNT-WINDOW-MISMATCH", "character", "error", "confirmed-runtime-defect", "high", "Recent PvP rows use a 70-day window but the pagination count subquery does not.", PLAYER_CYCLOPEDIA_CPP, line + body.count("\n", 0, start.start())))
    bosstiary = read_text(root, BOSSTIARY_CPP) or ""
    if function := cpp_function(bosstiary, "IOBosstiary::loadBoostedBoss"):
        body, line = function
        guards = [m.start() for m in re.finditer(r"if\s*\(\s*!result\s*\)", body)]
        if len(guards) >= 2 and "return;" in body[guards[0] : guards[1]]:
            schema = read_text(root, SCHEMA_SQL) or ""
            seeded = bool(re.search(r"INSERT\s+INTO\s+`boosted_boss`.*?VALUES\s*\(\s*'default'", schema, re.I | re.S))
            out.append(finding("BOSSTIARY-EMPTY-RESULT-FALLBACK-UNREACHABLE", "bosstiary", "warning", "latent-helper-defect", "high", "loadBoostedBoss returns before a later empty-result fallback branch.", BOSSTIARY_CPP, line, {"cleanSchemaSeedsDefaultRow": seeded}))
    return out


_scan_known_patterns = known_patterns
validate_monster_definitions = validate_monsters


def source_record(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        return {"path": relative, "exists": False}
    return {"path": relative, "exists": True, "size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build_report(repository_root: Path, otclient_root: Path | None = None) -> dict[str, Any]:
    root = repository_root.resolve()
    required = (CHARM_REGISTRY, CHARM_HELPER, BESTIARY_CPP, BOSSTIARY_CPP, PLAYER_CYCLOPEDIA_CPP, *SERVER_PROTOCOL)
    source_paths = sorted({*required, SCHEMA_SQL, *(path for paths in DOMAIN_SOURCES.values() for path in paths)})
    sources = [source_record(root, path) for path in source_paths]
    charm_text = read_text(root, CHARM_REGISTRY)
    charms = parse_charm_registry(charm_text) if charm_text is not None else []
    monsters = collect_monsters(root)
    server = collect_protocol_methods(read_text(root, SERVER_PROTOCOL[0]), read_text(root, SERVER_PROTOCOL[1]))
    findings = [finding("SOURCE-MISSING", "infrastructure", "error", "definition-invalid", "high", f"Required source is missing: {path}.", path) for path in required if not (root / path).is_file()]
    findings += validate_charms(charms) + validate_monsters(monsters) + known_patterns(root)
    for name in server["missingDefinitions"]:
        findings.append(finding(f"PROTOCOL-SERVER-MISSING-DEFINITION-{name}", method_domain(name), "error", "missing-runtime-path", "high", f"ProtocolGame declares {name} but no definition was found.", SERVER_PROTOCOL[0]))
    client: dict[str, Any] = {"status": "not-provided", "root": None, "methods": collect_protocol_methods(None, None)}
    client_sources: list[dict[str, Any]] = []
    if otclient_root:
        client_root = otclient_root.resolve()
        client_sources = [source_record(client_root, path) for path in CLIENT_PROTOCOL]
        client = {"status": "scanned", "root": str(client_root), "methods": collect_protocol_methods(read_text(client_root, CLIENT_PROTOCOL[0]), "\n".join(filter(None, (read_text(client_root, path) for path in CLIENT_PROTOCOL[1:]))))}
    domains: dict[str, Any] = {}
    for domain, candidates in DOMAIN_SOURCES.items():
        domains[domain] = {"sourceCandidates": list(candidates), "existingSources": [path for path in candidates if (root / path).is_file()], "serverProtocol": server["byDomain"].get(domain, {"declarations": [], "definitions": []}), "clientProtocol": client["methods"]["byDomain"].get(domain, {"declarations": [], "definitions": []})}
    findings.sort(key=lambda item: ({"error": 0, "warning": 1, "info": 2}.get(item["severity"], 9), item["domain"], item["id"]))
    counts = lambda key: dict(sorted(Counter(item[key] for item in findings).items()))
    summary = {"domains": len(domains), "existingSourceCount": sum(item["exists"] for item in sources), "missingSourceCount": sum(not item["exists"] for item in sources), "charmCount": len(charms), "monsterFiles": monsters["summary"]["scannedFiles"], "bestiaryEntries": monsters["summary"]["bestiaryEntries"], "bosstiaryEntries": monsters["summary"]["bosstiaryEntries"], "findingCount": len(findings), "bySeverity": counts("severity"), "byDisposition": counts("disposition"), "byDomain": counts("domain")}
    return {"schemaVersion": SCHEMA_VERSION, "generatedAt": datetime.now(timezone.utc).isoformat(), "baseCommit": git_head(root), "repositoryRoot": str(root), "otclient": client, "sources": sources, "clientSources": client_sources, "domains": domains, "monsters": monsters, "charms": {"count": len(charms), "luaIds": [item["luaId"] for item in charms], "entries": charms}, "protocol": {"server": server, "client": client["methods"]}, "findings": findings, "summary": summary}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", "--root", dest="repository_root", type=Path, default=Path.cwd())
    parser.add_argument("--otclient-root", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts/CYCLOPEDIA_VALIDATION.json"))
    parser.add_argument("--fail-on", choices=("none", "error"), default="none")
    args = parser.parse_args()
    root = args.repository_root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    report = build_report(root, args.otclient_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "domains": report["summary"]["domains"], "charms": report["summary"]["charmCount"], "bestiaryEntries": report["summary"]["bestiaryEntries"], "bosstiaryEntries": report["summary"]["bosstiaryEntries"], "findings": report["summary"]["findingCount"], "bySeverity": report["summary"]["bySeverity"], "otclient": report["otclient"]["status"]}, indent=2))
    return 2 if args.fail_on == "error" and report["summary"]["bySeverity"].get("error", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
