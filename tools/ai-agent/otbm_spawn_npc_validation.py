from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

EVIDENCE_FORMAT = "canary-otbm-spawn-npc-evidence-v1"
REPORT_FORMAT = "canary-otbm-spawn-npc-validation-v1"
REACHABILITY_FORMAT = "canary-otbm-reachability-v1"
SCHEMA_VERSION = 1

DEFAULT_SAMPLE_LIMIT = 500
MAX_SAMPLE_LIMIT = 10_000
MAX_SOURCE_FILES = 100_000
MAX_SPAWN_FILES = 1_000
MAX_DEFINITIONS = 100_000
MAX_PLACEMENTS = 1_000_000
MAX_DYNAMIC_CALLS = 200_000
MAX_FILE_SIZE = 64 * 1024 * 1024
MAX_XML_SIZE = 128 * 1024 * 1024
MAX_DYNAMIC_SNIPPET = 240

Position = tuple[int, int, int]
SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


class SpawnNpcValidationError(RuntimeError):
    pass


@dataclass
class FindingCollector:
    limit: int

    def __post_init__(self) -> None:
        if not isinstance(self.limit, int) or isinstance(self.limit, bool) or not 1 <= self.limit <= MAX_SAMPLE_LIMIT:
            raise SpawnNpcValidationError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")
        self.total = 0
        self.counts: Counter[str] = Counter()
        self.severity_counts: Counter[str] = Counter()
        self.samples: list[dict[str, Any]] = []

    def add(self, severity: str, code: str, message: str, **details: Any) -> None:
        if severity not in SEVERITY_ORDER:
            raise SpawnNpcValidationError(f"Unsupported finding severity: {severity}")
        self.total += 1
        self.counts[code] += 1
        self.severity_counts[severity] += 1
        if len(self.samples) < self.limit:
            self.samples.append({"severity": severity, "code": code, "message": message, **details})

    def finish(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        self.samples.sort(
            key=lambda entry: (
                SEVERITY_ORDER[entry["severity"]],
                entry["code"],
                entry.get("source", ""),
                entry.get("groupId", ""),
                tuple(entry.get("position", entry.get("center", []))),
                entry.get("name", ""),
            )
        )
        return self.samples, {
            "total": self.total,
            "bySeverity": {key: self.severity_counts.get(key, 0) for key in ("error", "warning", "info")},
            "byCode": dict(sorted(self.counts.items())),
            "truncated": self.total > len(self.samples),
        }


def _sha256(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _resolve_under(root: Path, value: Path | str, *, must_exist: bool = True, label: str = "path") -> Path:
    root = root.expanduser().resolve()
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    if candidate.is_symlink():
        raise SpawnNpcValidationError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=must_exist)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SpawnNpcValidationError(f"{label} escapes the active datapack root: {candidate}") from exc
    if must_exist and not resolved.is_file():
        raise FileNotFoundError(resolved)
    return resolved


def _glob_files(root: Path, patterns: Sequence[str], *, label: str) -> list[Path]:
    result: dict[str, Path] = {}
    for pattern in patterns:
        if not pattern or Path(pattern).is_absolute() or ".." in Path(pattern).parts:
            raise SpawnNpcValidationError(f"Invalid {label} glob: {pattern!r}")
        for candidate in root.glob(pattern):
            if candidate.is_dir():
                continue
            resolved = _resolve_under(root, candidate, label=label)
            if resolved.stat().st_size > MAX_FILE_SIZE:
                raise SpawnNpcValidationError(f"{label} file exceeds {MAX_FILE_SIZE} bytes: {resolved}")
            result[_relative(resolved, root)] = resolved
            if len(result) > MAX_SOURCE_FILES:
                raise SpawnNpcValidationError(f"More than {MAX_SOURCE_FILES} {label} files matched")
    return [result[key] for key in sorted(result)]


def _source_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": _relative(path, root),
        "size": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _int_attr(element: ET.Element, name: str, *, required: bool, default: int | None = None) -> int:
    raw = element.get(name)
    if raw is None:
        if required:
            raise SpawnNpcValidationError(f"Missing XML attribute {name}")
        if default is None:
            raise SpawnNpcValidationError(f"Missing XML attribute {name} and no default")
        return default
    try:
        return int(raw, 10)
    except ValueError as exc:
        raise SpawnNpcValidationError(f"Invalid integer XML attribute {name}={raw!r}") from exc


def _position(value: Sequence[Any], label: str) -> Position:
    if len(value) != 3 or any(not isinstance(part, int) or isinstance(part, bool) for part in value):
        raise SpawnNpcValidationError(f"{label} must contain three integers")
    x, y, z = (int(part) for part in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise SpawnNpcValidationError(f"{label} is outside the OTBM coordinate range: {(x, y, z)}")
    return x, y, z


def _in_bounds(position: Position, lower: Position, upper: Position) -> bool:
    return all(lower[index] <= position[index] <= upper[index] for index in range(3))


def normalize_bounds(first: Position, second: Position) -> tuple[Position, Position]:
    first = _position(first, "region start")
    second = _position(second, "region end")
    lower: Position = tuple(min(first[index], second[index]) for index in range(3))  # type: ignore[assignment]
    upper: Position = tuple(max(first[index], second[index]) for index in range(3))  # type: ignore[assignment]
    return lower, upper


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


_MONSTER_DEFINITION = re.compile(r"Game\s*\.\s*createMonsterType\s*\(\s*([\"'])(?P<name>.+?)\1\s*\)")
_NPC_DEFINITION_LITERAL = re.compile(r"Game\s*\.\s*createNpcType\s*\(\s*([\"'])(?P<name>.+?)\1\s*\)")
_LOCAL_STRING = re.compile(r"(?:local\s+)?(?P<variable>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*([\"'])(?P<value>.*?)\2")
_NPC_DEFINITION_VARIABLE = re.compile(r"Game\s*\.\s*createNpcType\s*\(\s*(?P<variable>[A-Za-z_][A-Za-z0-9_]*)\s*\)")
_REWARD_BOSS = re.compile(r"\brewardBoss\s*=\s*true\b")
_DYNAMIC_LITERAL_POSITION = re.compile(
    r"Game\s*\.\s*create(?P<kind>Monster|Npc)(?!Type)\s*\(\s*([\"'])(?P<name>.+?)\2\s*,\s*"
    r"Position\s*\(\s*(?P<x>\d+)\s*,\s*(?P<y>\d+)\s*,\s*(?P<z>\d+)\s*\)",
    re.MULTILINE,
)
_DYNAMIC_LITERAL_TABLE = re.compile(
    r"Game\s*\.\s*create(?P<kind>Monster|Npc)(?!Type)\s*\(\s*([\"'])(?P<name>.+?)\2\s*,\s*\{"
    r"(?=[^}]{0,300}\bx\s*=\s*(?P<x>\d+))(?=[^}]{0,300}\by\s*=\s*(?P<y>\d+))"
    r"(?=[^}]{0,300}\bz\s*=\s*(?P<z>\d+))[^}]{0,300}\}",
    re.MULTILINE | re.DOTALL,
)
_DYNAMIC_CALL = re.compile(r"Game\s*\.\s*create(?P<kind>Monster|Npc)(?!Type)\s*\(")


def _scan_definitions(
    root: Path,
    monster_files: Sequence[Path],
    npc_files: Sequence[Path],
    findings: FindingCollector,
) -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    for kind, files in (("monster", monster_files), ("npc", npc_files)):
        for path in files:
            text = _read_text(path)
            source = _relative(path, root)
            source_hash = _sha256(path)
            matches: list[tuple[str, int]] = []
            if kind == "monster":
                matches = [(match.group("name"), _line_number(text, match.start())) for match in _MONSTER_DEFINITION.finditer(text)]
            else:
                matches.extend(
                    (match.group("name"), _line_number(text, match.start())) for match in _NPC_DEFINITION_LITERAL.finditer(text)
                )
                variables: dict[str, str] = {}
                for match in _LOCAL_STRING.finditer(text):
                    variables.setdefault(match.group("variable"), match.group("value"))
                for match in _NPC_DEFINITION_VARIABLE.finditer(text):
                    variable = match.group("variable")
                    if variable in variables:
                        matches.append((variables[variable], _line_number(text, match.start())))
                    else:
                        findings.add(
                            "warning",
                            "npc_definition_name_dynamic",
                            "NPC type name is not a statically resolvable literal",
                            source=source,
                            line=_line_number(text, match.start()),
                            variable=variable,
                        )
            if not matches:
                findings.add(
                    "warning",
                    f"{kind}_definition_not_detected",
                    f"No static Game.create{kind.title()}Type definition was detected",
                    source=source,
                )
                continue
            for name, line in matches:
                if len(definitions) >= MAX_DEFINITIONS:
                    raise SpawnNpcValidationError(f"More than {MAX_DEFINITIONS} creature definitions were detected")
                definitions.append(
                    {
                        "kind": kind,
                        "name": name,
                        "canonicalName": name.casefold(),
                        "source": source,
                        "line": line,
                        "sourceSha256": source_hash,
                        "rewardBossLiteral": bool(_REWARD_BOSS.search(text)) if kind == "monster" else False,
                    }
                )
    definitions.sort(key=lambda entry: (entry["kind"], entry["canonicalName"], entry["source"], entry["line"]))
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in definitions:
        by_key[(entry["kind"], entry["canonicalName"])].append(entry)
    for (kind, canonical), entries in sorted(by_key.items()):
        if len(entries) > 1:
            findings.add(
                "error",
                "conflicting_creature_definition",
                "Multiple active definition files expose the same canonical creature name",
                kind=kind,
                canonicalName=canonical,
                sources=[entry["source"] for entry in entries],
            )
    return definitions


def _parse_spawn_file(
    *,
    root: Path,
    path: Path,
    kind: str,
    findings: FindingCollector,
    groups: list[dict[str, Any]],
    placements: list[dict[str, Any]],
) -> None:
    if kind not in {"monster", "npc"}:
        raise SpawnNpcValidationError(f"Unsupported spawn kind: {kind}")
    size = path.stat().st_size
    if size > MAX_XML_SIZE:
        raise SpawnNpcValidationError(f"Spawn XML exceeds {MAX_XML_SIZE} bytes: {path}")
    prefix = path.read_bytes()[:4096].upper()
    if b"<!DOCTYPE" in prefix or b"<!ENTITY" in prefix:
        raise SpawnNpcValidationError(f"DTD/entity declarations are not allowed in spawn XML: {path}")
    source = _relative(path, root)
    expected_root = "monsters" if kind == "monster" else "npcs"
    tag = kind
    try:
        iterator = ET.iterparse(path, events=("start", "end"))
        _, root_element = next(iterator)
        if root_element.tag != expected_root:
            raise SpawnNpcValidationError(
                f"Unexpected root <{root_element.tag}> in {source}; expected <{expected_root}>"
            )
        group_ordinal = 0
        for event, element in iterator:
            if event != "end" or element.tag != tag or element.get("centerx") is None:
                continue
            if len(groups) >= MAX_PLACEMENTS or len(placements) >= MAX_PLACEMENTS:
                raise SpawnNpcValidationError(f"More than {MAX_PLACEMENTS} spawn records were detected")
            group_ordinal += 1
            group_id = f"{kind}:{source}:{group_ordinal}"
            try:
                center = _position(
                    (
                        _int_attr(element, "centerx", required=True),
                        _int_attr(element, "centery", required=True),
                        _int_attr(element, "centerz", required=True),
                    ),
                    "spawn center",
                )
                radius = _int_attr(element, "radius", required=False, default=-1)
            except SpawnNpcValidationError as exc:
                findings.add(
                    "error",
                    "invalid_spawn_group",
                    str(exc),
                    source=source,
                    groupId=group_id,
                )
                element.clear()
                continue
            if radius < -1:
                findings.add(
                    "error",
                    "invalid_spawn_radius",
                    "Spawn radius must be -1 or a non-negative integer",
                    source=source,
                    groupId=group_id,
                    center=list(center),
                    radius=radius,
                )
            group: dict[str, Any] = {
                "id": group_id,
                "kind": kind,
                "source": source,
                "ordinal": group_ordinal,
                "center": list(center),
                "radius": radius,
                "placementCount": 0,
            }
            local_entries: list[dict[str, Any]] = []
            for child_ordinal, child in enumerate(list(element), start=1):
                if child.tag != tag:
                    findings.add(
                        "warning",
                        "unknown_spawn_child",
                        "Unknown child node inside spawn group",
                        source=source,
                        groupId=group_id,
                        childTag=child.tag,
                    )
                    continue
                name = child.get("name")
                if not name:
                    findings.add(
                        "error",
                        "missing_spawn_name",
                        "Spawn entry has no creature name",
                        source=source,
                        groupId=group_id,
                        childOrdinal=child_ordinal,
                    )
                    continue
                try:
                    x_offset = _int_attr(child, "x", required=False, default=0)
                    y_offset = _int_attr(child, "y", required=False, default=0)
                    position = _position((center[0] + x_offset, center[1] + y_offset, center[2]), "spawn position")
                except SpawnNpcValidationError as exc:
                    findings.add(
                        "error",
                        "invalid_spawn_position",
                        str(exc),
                        source=source,
                        groupId=group_id,
                        name=name,
                    )
                    continue
                child_z_raw = child.get("z")
                child_z: int | None = None
                if child_z_raw is not None:
                    try:
                        child_z = int(child_z_raw, 10)
                    except ValueError:
                        findings.add(
                            "warning",
                            "child_z_invalid_and_ignored",
                            "Child z is invalid and is ignored by the Canary spawn loader",
                            source=source,
                            groupId=group_id,
                            name=name,
                            childZ=child_z_raw,
                            centerZ=center[2],
                        )
                    else:
                        if child_z != center[2]:
                            findings.add(
                                "warning",
                                "child_z_ignored",
                                "Child z differs from centerz; Canary uses centerz for the runtime position",
                                source=source,
                                groupId=group_id,
                                name=name,
                                childZ=child_z,
                                centerZ=center[2],
                                position=list(position),
                            )
                if radius != -1 and (abs(x_offset) > radius or abs(y_offset) > radius):
                    findings.add(
                        "error",
                        "placement_outside_spawn_radius",
                        "Spawn offset is outside the square runtime spawn zone",
                        source=source,
                        groupId=group_id,
                        name=name,
                        position=list(position),
                        offset=[x_offset, y_offset],
                        radius=radius,
                    )
                spawn_time_raw = child.get("spawntime")
                spawn_time: int | None = None
                spawn_time_status = "explicit"
                if spawn_time_raw is None:
                    if kind == "monster":
                        spawn_time_status = "runtime-default"
                        findings.add(
                            "warning",
                            "monster_spawntime_defaulted",
                            "Monster spawntime is absent and Canary will use DEFAULT_RESPAWN_TIME",
                            source=source,
                            groupId=group_id,
                            name=name,
                            position=list(position),
                        )
                    else:
                        spawn_time_status = "runtime-rejected"
                        findings.add(
                            "error",
                            "npc_spawntime_missing",
                            "NPC spawntime is absent; the runtime interval becomes invalid and the entry is not added",
                            source=source,
                            groupId=group_id,
                            name=name,
                            position=list(position),
                        )
                else:
                    try:
                        spawn_time = int(spawn_time_raw, 10)
                    except ValueError:
                        spawn_time_status = "invalid"
                        findings.add(
                            "error",
                            "invalid_spawntime",
                            "Spawntime is not an integer",
                            source=source,
                            groupId=group_id,
                            name=name,
                            spawntime=spawn_time_raw,
                        )
                    else:
                        if kind == "monster" and spawn_time <= 0:
                            spawn_time_status = "runtime-default"
                            findings.add(
                                "warning",
                                "monster_spawntime_defaulted",
                                "Non-positive monster spawntime is replaced by DEFAULT_RESPAWN_TIME",
                                source=source,
                                groupId=group_id,
                                name=name,
                                position=list(position),
                                spawntime=spawn_time,
                            )
                        elif kind == "monster" and spawn_time > 86_400:
                            spawn_time_status = "runtime-clamped"
                            findings.add(
                                "warning",
                                "monster_spawntime_runtime_clamp",
                                "Monster spawntime exceeds the runtime one-day maximum before rate scaling",
                                source=source,
                                groupId=group_id,
                                name=name,
                                position=list(position),
                                spawntime=spawn_time,
                            )
                        elif kind == "npc" and not 1 <= spawn_time <= 86_400:
                            spawn_time_status = "runtime-rejected"
                            findings.add(
                                "error",
                                "npc_spawntime_runtime_rejected",
                                "NPC spawntime is outside the runtime 1..86400 second interval",
                                source=source,
                                groupId=group_id,
                                name=name,
                                position=list(position),
                                spawntime=spawn_time,
                            )
                entry = {
                    "id": f"{group_id}:{child_ordinal}",
                    "groupId": group_id,
                    "kind": kind,
                    "name": name,
                    "canonicalName": name.casefold(),
                    "source": source,
                    "childOrdinal": child_ordinal,
                    "center": list(center),
                    "radius": radius,
                    "offset": [x_offset, y_offset],
                    "position": list(position),
                    "childZ": child_z,
                    "spawntime": spawn_time,
                    "spawntimeStatus": spawn_time_status,
                    "direction": child.get("direction"),
                    "weight": child.get("weight") if kind == "monster" else None,
                }
                local_entries.append(entry)
                placements.append(entry)
            group["placementCount"] = len(local_entries)
            if not local_entries:
                findings.add(
                    "warning",
                    "empty_spawn_group",
                    "Spawn group contains no valid creature entries",
                    source=source,
                    groupId=group_id,
                    center=list(center),
                    radius=radius,
                )
            groups.append(group)
            element.clear()
    except ET.ParseError as exc:
        raise SpawnNpcValidationError(f"Cannot parse spawn XML {source}: {exc}") from exc


def _scan_dynamic_calls(root: Path, files: Sequence[Path], findings: FindingCollector) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for path in files:
        text = _read_text(path)
        source = _relative(path, root)
        source_hash = _sha256(path)
        matched_starts: set[int] = set()
        literal_matches = sorted(
            [*_DYNAMIC_LITERAL_POSITION.finditer(text), *_DYNAMIC_LITERAL_TABLE.finditer(text)],
            key=lambda match: match.start(),
        )
        for match in literal_matches:
            if match.start() in matched_starts:
                continue
            matched_starts.add(match.start())
            try:
                position = _position(
                    (int(match.group("x")), int(match.group("y")), int(match.group("z"))),
                    "dynamic creation position",
                )
            except SpawnNpcValidationError as exc:
                findings.add(
                    "error",
                    "dynamic_creation_position_invalid",
                    str(exc),
                    source=source,
                    line=_line_number(text, match.start()),
                )
                continue
            kind = match.group("kind").casefold()
            name = match.group("name")
            calls.append(
                {
                    "kind": kind,
                    "name": name,
                    "canonicalName": name.casefold(),
                    "source": source,
                    "line": _line_number(text, match.start()),
                    "sourceSha256": source_hash,
                    "position": list(position),
                    "status": "literal",
                    "questSource": "/quests/" in f"/{source.casefold()}",
                }
            )
            if len(calls) > MAX_DYNAMIC_CALLS:
                raise SpawnNpcValidationError(f"More than {MAX_DYNAMIC_CALLS} dynamic creation calls were detected")
        for match in _DYNAMIC_CALL.finditer(text):
            if match.start() in matched_starts:
                continue
            snippet = " ".join(text[match.start() : match.start() + MAX_DYNAMIC_SNIPPET].split())
            calls.append(
                {
                    "kind": match.group("kind").casefold(),
                    "name": None,
                    "canonicalName": None,
                    "source": source,
                    "line": _line_number(text, match.start()),
                    "sourceSha256": source_hash,
                    "position": None,
                    "status": "unresolved",
                    "questSource": "/quests/" in f"/{source.casefold()}",
                    "snippet": snippet,
                }
            )
            findings.add(
                "warning",
                "dynamic_creation_unresolved",
                "Dynamic creature creation has a non-literal name or position and remains unresolved",
                source=source,
                line=_line_number(text, match.start()),
                kind=match.group("kind").casefold(),
            )
            if len(calls) > MAX_DYNAMIC_CALLS:
                raise SpawnNpcValidationError(f"More than {MAX_DYNAMIC_CALLS} dynamic creation calls were detected")
    calls.sort(
        key=lambda entry: (
            entry["kind"],
            entry["source"],
            entry["line"],
            entry.get("canonicalName") or "",
            tuple(entry.get("position") or ()),
        )
    )
    return calls


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
    findings = FindingCollector(sample_limit)
    expanded_root = datapack_root.expanduser()
    if expanded_root.is_symlink():
        raise SpawnNpcValidationError(f"Active datapack root must not be a symlink: {expanded_root}")
    root = expanded_root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    if len(monster_spawn_files) + len(npc_spawn_files) > MAX_SPAWN_FILES:
        raise SpawnNpcValidationError(f"At most {MAX_SPAWN_FILES} spawn XML files may be scanned")
    monster_spawns = [_resolve_under(root, value, label="monster spawn XML") for value in monster_spawn_files]
    npc_spawns = [_resolve_under(root, value, label="NPC spawn XML") for value in npc_spawn_files]
    if not monster_spawns and not npc_spawns:
        raise SpawnNpcValidationError("At least one explicit active spawn XML file is required")
    monster_definition_files = _glob_files(root, monster_definition_globs, label="monster definition")
    npc_definition_files = _glob_files(root, npc_definition_globs, label="NPC definition")
    dynamic_files = _glob_files(root, dynamic_source_globs, label="dynamic source")

    definitions = _scan_definitions(root, monster_definition_files, npc_definition_files, findings)
    groups: list[dict[str, Any]] = []
    placements: list[dict[str, Any]] = []
    for path in monster_spawns:
        _parse_spawn_file(root=root, path=path, kind="monster", findings=findings, groups=groups, placements=placements)
    for path in npc_spawns:
        _parse_spawn_file(root=root, path=path, kind="npc", findings=findings, groups=groups, placements=placements)

    definition_lookup: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for definition in definitions:
        definition_lookup[(definition["kind"], definition["canonicalName"])].append(definition)
    for placement in placements:
        matches = definition_lookup.get((placement["kind"], placement["canonicalName"]), [])
        placement["definitionMatchCount"] = len(matches)
        placement["definitionSources"] = [entry["source"] for entry in matches]
        placement["rewardBossLiteral"] = any(entry.get("rewardBossLiteral") for entry in matches)
        if not matches:
            findings.add(
                "error",
                "spawn_definition_missing",
                "Static spawn name has no active matching creature definition",
                source=placement["source"],
                groupId=placement["groupId"],
                kind=placement["kind"],
                name=placement["name"],
                position=placement["position"],
            )
        elif len(matches) > 1:
            findings.add(
                "error",
                "spawn_definition_conflicting",
                "Static spawn name matches multiple active definition files",
                source=placement["source"],
                groupId=placement["groupId"],
                kind=placement["kind"],
                name=placement["name"],
                position=placement["position"],
                definitionSources=placement["definitionSources"],
            )

    by_exact: dict[tuple[str, str, tuple[int, ...]], list[dict[str, Any]]] = defaultdict(list)
    by_position: dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]] = defaultdict(list)
    by_group_position: dict[tuple[str, tuple[int, ...]], list[dict[str, Any]]] = defaultdict(list)
    for placement in placements:
        position = tuple(placement["position"])
        by_exact[(placement["kind"], placement["canonicalName"], position)].append(placement)
        by_position[(placement["kind"], position)].append(placement)
        by_group_position[(placement["groupId"], position)].append(placement)
    for (_, _, position), entries in sorted(by_exact.items()):
        if len(entries) > 1:
            findings.add(
                "warning",
                "duplicate_static_placement",
                "The same creature name is statically declared more than once at the same position",
                kind=entries[0]["kind"],
                name=entries[0]["name"],
                position=list(position),
                placementIds=[entry["id"] for entry in entries],
            )
    for (_, position), entries in sorted(by_position.items()):
        groups_here = sorted({entry["groupId"] for entry in entries})
        if len(groups_here) > 1:
            findings.add(
                "warning",
                "overlapping_spawn_groups",
                "Different spawn groups target the same runtime position",
                kind=entries[0]["kind"],
                position=list(position),
                groupIds=groups_here,
                names=sorted({entry["name"] for entry in entries}),
            )
    for (group_id, position), entries in sorted(by_group_position.items()):
        bosses = [entry for entry in entries if entry.get("rewardBossLiteral")]
        if bosses and len(entries) > 1:
            findings.add(
                "error",
                "boss_mixed_in_spawn_block",
                "A literal reward boss shares one runtime spawn position with another entry in the same group",
                groupId=group_id,
                position=list(position),
                names=[entry["name"] for entry in entries],
            )

    dynamic_calls = _scan_dynamic_calls(root, dynamic_files, findings)
    static_lookup: dict[tuple[str, str, tuple[int, ...]], list[str]] = defaultdict(list)
    for placement in placements:
        static_lookup[(placement["kind"], placement["canonicalName"], tuple(placement["position"]))].append(placement["id"])
    for call in dynamic_calls:
        if call["status"] != "literal":
            call["staticMatchCount"] = None
            call["staticPlacementIds"] = []
            call["correlation"] = "unresolved"
            continue
        key = (call["kind"], call["canonicalName"], tuple(call["position"]))
        matches = static_lookup.get(key, [])
        call["staticMatchCount"] = len(matches)
        call["staticPlacementIds"] = matches
        call["correlation"] = "static-and-dynamic" if matches else "dynamic-only"
        if matches:
            findings.add(
                "warning",
                "static_dynamic_overlap",
                "A literal dynamic creation call overlaps a static spawn of the same creature at the same position",
                source=call["source"],
                line=call["line"],
                kind=call["kind"],
                name=call["name"],
                position=call["position"],
                staticPlacementIds=matches,
            )

    groups.sort(key=lambda entry: (entry["kind"], entry["source"], entry["ordinal"]))
    placements.sort(
        key=lambda entry: (
            entry["kind"],
            tuple(entry["position"]),
            entry["canonicalName"],
            entry["source"],
            entry["childOrdinal"],
        )
    )
    source_records = {
        "monsterSpawnFiles": [_source_record(path, root) for path in monster_spawns],
        "npcSpawnFiles": [_source_record(path, root) for path in npc_spawns],
        "monsterDefinitionFiles": [_source_record(path, root) for path in monster_definition_files],
        "npcDefinitionFiles": [_source_record(path, root) for path in npc_definition_files],
        "dynamicSourceFiles": [_source_record(path, root) for path in dynamic_files],
    }
    source_manifest_sha256 = hashlib.sha256(
        json.dumps(source_records, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    findings_json, finding_summary = findings.finish()
    summary = {
        "spawnFiles": len(monster_spawns) + len(npc_spawns),
        "monsterSpawnFiles": len(monster_spawns),
        "npcSpawnFiles": len(npc_spawns),
        "definitionFiles": len(monster_definition_files) + len(npc_definition_files),
        "dynamicSourceFiles": len(dynamic_files),
        "definitions": len(definitions),
        "groups": len(groups),
        "placements": len(placements),
        "monsterPlacements": sum(1 for entry in placements if entry["kind"] == "monster"),
        "npcPlacements": sum(1 for entry in placements if entry["kind"] == "npc"),
        "dynamicCreations": len(dynamic_calls),
        "literalDynamicCreations": sum(1 for entry in dynamic_calls if entry["status"] == "literal"),
        "unresolvedDynamicCreations": sum(1 for entry in dynamic_calls if entry["status"] == "unresolved"),
        "findings": finding_summary,
    }
    return {
        "format": EVIDENCE_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": finding_summary["bySeverity"]["error"] == 0,
        "activeDatapack": {"rootName": root.name, "sourceManifestSha256": source_manifest_sha256},
        "policy": {
            "explicitSpawnFilesOnly": True,
            "activeDatapackConfined": True,
            "dynamicLuaExecuted": False,
            "childZRuntimeSource": "centerz",
            "radiusShape": "inclusive-square",
            "sampleLimit": sample_limit,
        },
        "sources": source_records,
        "summary": summary,
        "definitions": definitions,
        "spawnGroups": groups,
        "placements": placements,
        "dynamicCreations": dynamic_calls,
        "findings": findings_json,
    }


def _load_json(path: Path, expected_format: str, label: str) -> dict[str, Any]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpawnNpcValidationError(f"Cannot read {label} {source}: {exc}") from exc
    if not isinstance(document, dict) or document.get("format") != expected_format:
        raise SpawnNpcValidationError(f"Unsupported {label} format: {source}")
    return document


def _reachability_diagnostics(report: Mapping[str, Any]) -> dict[Position, dict[str, Any]]:
    diagnostics = report.get("tileDiagnostics")
    if not isinstance(diagnostics, list):
        raise SpawnNpcValidationError("Reachability report has no tileDiagnostics list")
    result: dict[Position, dict[str, Any]] = {}
    for entry in diagnostics:
        if not isinstance(entry, dict):
            continue
        position_value = entry.get("position")
        try:
            position = _position(position_value, "reachability diagnostic position")
        except (SpawnNpcValidationError, TypeError):
            continue
        if position in result:
            raise SpawnNpcValidationError(f"Duplicate reachability tile diagnostic: {position}")
        result[position] = entry
    return result


def _tile_evidence(index: Any, position: Position, diagnostics: Mapping[Position, Mapping[str, Any]], truncated: bool) -> dict[str, Any]:
    found = index.find_tile(position)
    if found is None:
        return {
            "status": "missing-tile",
            "tileExists": False,
            "strictWalkable": False,
            "optimisticWalkable": False,
            "issues": ["tile-missing"],
        }
    tile_index, tile = found
    diagnostic = diagnostics.get(position)
    if diagnostic is None:
        if truncated:
            return {
                "status": "unresolved",
                "tileExists": True,
                "tileIndex": tile_index,
                "strictWalkable": None,
                "optimisticWalkable": None,
                "issues": ["reachability-diagnostics-truncated"],
            }
        return {
            "status": "confirmed",
            "tileExists": True,
            "tileIndex": tile_index,
            "strictWalkable": True,
            "optimisticWalkable": True,
            "issues": [],
        }
    strict = bool(diagnostic.get("strictWalkable"))
    optimistic = bool(diagnostic.get("optimisticWalkable"))
    if strict:
        status = "confirmed"
    elif optimistic:
        status = "conditional"
    else:
        status = "blocked"
    issues: list[str] = []
    if not diagnostic.get("hasGround", False):
        issues.append("missing-ground")
    if diagnostic.get("staticBlockers"):
        issues.append("static-blocker")
    if diagnostic.get("conditionalBlockers"):
        issues.append("conditional-blocker")
    if diagnostic.get("unknownAppearances"):
        issues.append("unknown-appearance")
    issues.extend(str(value) for value in diagnostic.get("uncertainties", []) if isinstance(value, str))
    return {
        "status": status,
        "tileExists": True,
        "tileIndex": tile_index,
        "tileKind": getattr(tile, "kind", None),
        "strictWalkable": strict,
        "optimisticWalkable": optimistic,
        "issues": sorted(set(issues)),
        "diagnostic": dict(diagnostic),
    }


def validate_evidence(
    *,
    evidence: Mapping[str, Any],
    world_index: Any,
    reachability_report: Mapping[str, Any],
    lower: Position,
    upper: Position,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    findings = FindingCollector(sample_limit)
    if evidence.get("format") != EVIDENCE_FORMAT:
        raise SpawnNpcValidationError("Unsupported spawn/NPC evidence format")
    if reachability_report.get("format") != REACHABILITY_FORMAT:
        raise SpawnNpcValidationError("Unsupported reachability report format")
    lower, upper = normalize_bounds(lower, upper)
    region = reachability_report.get("region")
    if not isinstance(region, dict):
        raise SpawnNpcValidationError("Reachability report has no region")
    reach_lower = _position(region.get("from"), "reachability region start")
    reach_upper = _position(region.get("to"), "reachability region end")
    if any(lower[index] < reach_lower[index] or upper[index] > reach_upper[index] for index in range(3)):
        raise SpawnNpcValidationError("Validation region is not fully covered by the supplied Phase 3 reachability report")
    diagnostics_truncated = bool(reachability_report.get("tileDiagnosticsTruncated"))
    diagnostics = _reachability_diagnostics(reachability_report)
    if diagnostics_truncated:
        findings.add(
            "error",
            "reachability_diagnostics_truncated",
            "Phase 3 tile diagnostics are truncated; absent diagnostic entries cannot be assumed walkable",
        )

    definitions = evidence.get("definitions")
    placements = evidence.get("placements")
    groups = evidence.get("spawnGroups")
    dynamic_calls = evidence.get("dynamicCreations")
    if not all(isinstance(value, list) for value in (definitions, placements, groups, dynamic_calls)):
        raise SpawnNpcValidationError("Spawn/NPC evidence is missing required lists")

    definition_lookup: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for definition in definitions:
        if isinstance(definition, dict):
            definition_lookup[(str(definition.get("kind")), str(definition.get("canonicalName")))].append(definition)

    group_results: list[dict[str, Any]] = []
    group_status_counts: Counter[str] = Counter()
    for group in groups:
        if not isinstance(group, dict):
            continue
        center = _position(group.get("center"), "spawn group center")
        if not _in_bounds(center, lower, upper):
            continue
        tile = _tile_evidence(world_index, center, diagnostics, diagnostics_truncated)
        group_status_counts[tile["status"]] += 1
        if tile["status"] == "missing-tile":
            findings.add(
                "error",
                "spawn_center_missing_tile",
                "Spawn group center does not exist in the World Index",
                groupId=group.get("id"),
                source=group.get("source"),
                center=list(center),
            )
        elif tile["status"] == "blocked":
            findings.add(
                "warning",
                "spawn_center_blocked",
                "Spawn group center is not optimistically walkable in the Phase 3 evidence",
                groupId=group.get("id"),
                source=group.get("source"),
                center=list(center),
                issues=tile["issues"],
            )
        group_results.append({**group, "centerValidation": tile})

    placement_results: list[dict[str, Any]] = []
    placement_total = 0
    status_counts: Counter[str] = Counter()
    for placement in placements:
        if not isinstance(placement, dict):
            continue
        position = _position(placement.get("position"), "spawn placement position")
        if not _in_bounds(position, lower, upper):
            continue
        placement_total += 1
        kind = str(placement.get("kind"))
        canonical = str(placement.get("canonicalName"))
        matches = definition_lookup.get((kind, canonical), [])
        tile = _tile_evidence(world_index, position, diagnostics, diagnostics_truncated)
        issues = list(tile["issues"])
        if not matches:
            definition_status = "missing"
            issues.append("definition-missing")
        elif len(matches) > 1:
            definition_status = "conflicting"
            issues.append("definition-conflicting")
        else:
            definition_status = "confirmed"
        if definition_status == "missing":
            status = "missing-definition"
            findings.add(
                "error",
                "spawn_definition_missing",
                "Spawn placement has no active matching definition",
                source=placement.get("source"),
                groupId=placement.get("groupId"),
                kind=kind,
                name=placement.get("name"),
                position=list(position),
            )
        elif definition_status == "conflicting":
            status = "conflicting-definition"
            findings.add(
                "error",
                "spawn_definition_conflicting",
                "Spawn placement matches multiple active definitions",
                source=placement.get("source"),
                groupId=placement.get("groupId"),
                kind=kind,
                name=placement.get("name"),
                position=list(position),
                definitionSources=[entry.get("source") for entry in matches],
            )
        elif tile["status"] == "missing-tile":
            status = "missing-tile"
            findings.add(
                "error",
                "spawn_position_missing_tile",
                "Spawn placement position does not exist in the World Index",
                source=placement.get("source"),
                groupId=placement.get("groupId"),
                kind=kind,
                name=placement.get("name"),
                position=list(position),
            )
        elif tile["status"] == "blocked":
            status = "blocked"
            findings.add(
                "error",
                "spawn_position_blocked",
                "Spawn placement is not optimistically walkable in the Phase 3 evidence",
                source=placement.get("source"),
                groupId=placement.get("groupId"),
                kind=kind,
                name=placement.get("name"),
                position=list(position),
                issues=tile["issues"],
            )
        elif tile["status"] == "conditional":
            status = "conditional"
            findings.add(
                "warning",
                "spawn_position_conditional",
                "Spawn placement is walkable only under optimistic Phase 3 assumptions",
                source=placement.get("source"),
                groupId=placement.get("groupId"),
                kind=kind,
                name=placement.get("name"),
                position=list(position),
                issues=tile["issues"],
            )
        elif tile["status"] == "unresolved":
            status = "unresolved"
        else:
            status = "confirmed"
        status_counts[status] += 1
        if len(placement_results) < sample_limit:
            placement_results.append(
                {
                    **placement,
                    "definitionStatus": definition_status,
                    "definitionSources": [entry.get("source") for entry in matches],
                    "tileValidation": tile,
                    "status": status,
                    "issues": sorted(set(issues)),
                }
            )

    dynamic_results: list[dict[str, Any]] = []
    dynamic_counts: Counter[str] = Counter()
    for call in dynamic_calls:
        if not isinstance(call, dict):
            continue
        if call.get("status") != "literal" or call.get("position") is None:
            dynamic_counts["unresolved"] += 1
            if len(dynamic_results) < sample_limit:
                dynamic_results.append({**call, "validationStatus": "unresolved", "tileValidation": None})
            continue
        position = _position(call.get("position"), "dynamic creation position")
        if not _in_bounds(position, lower, upper):
            continue
        tile = _tile_evidence(world_index, position, diagnostics, diagnostics_truncated)
        if tile["status"] == "missing-tile":
            validation_status = "missing-tile"
            findings.add(
                "error",
                "dynamic_creation_missing_tile",
                "Literal dynamic creation targets a position absent from the World Index",
                source=call.get("source"),
                line=call.get("line"),
                kind=call.get("kind"),
                name=call.get("name"),
                position=list(position),
            )
        elif tile["status"] == "blocked":
            validation_status = "blocked"
            findings.add(
                "warning",
                "dynamic_creation_blocked",
                "Literal dynamic creation targets a position that is not optimistically walkable",
                source=call.get("source"),
                line=call.get("line"),
                kind=call.get("kind"),
                name=call.get("name"),
                position=list(position),
                issues=tile["issues"],
            )
        elif tile["status"] == "conditional":
            validation_status = "conditional"
        elif tile["status"] == "unresolved":
            validation_status = "unresolved"
        else:
            validation_status = "confirmed"
        dynamic_counts[validation_status] += 1
        if len(dynamic_results) < sample_limit:
            dynamic_results.append({**call, "validationStatus": validation_status, "tileValidation": tile})

    findings_json, finding_summary = findings.finish()
    coordinate_count = (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1) * (upper[2] - lower[2] + 1)
    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": finding_summary["bySeverity"]["error"] == 0,
        "provenance": dict(provenance or {}),
        "region": {"from": list(lower), "to": list(upper), "coordinateCount": coordinate_count},
        "policy": {
            "phase3ReachabilityConsumed": True,
            "dynamicLuaExecuted": False,
            "mapModified": False,
            "truncatedReachabilityDiagnosticsFailClosed": True,
            "sampleLimit": sample_limit,
        },
        "summary": {
            "groups": len(group_results),
            "groupStatusCounts": dict(sorted(group_status_counts.items())),
            "placements": placement_total,
            "placementStatusCounts": dict(sorted(status_counts.items())),
            "dynamicCreations": sum(dynamic_counts.values()),
            "dynamicStatusCounts": dict(sorted(dynamic_counts.items())),
            "findings": finding_summary,
        },
        "spawnGroups": group_results[:sample_limit],
        "spawnGroupsTruncated": len(group_results) > sample_limit,
        "placements": placement_results,
        "placementsTruncated": placement_total > len(placement_results),
        "dynamicCreations": dynamic_results,
        "dynamicCreationsTruncated": sum(dynamic_counts.values()) > len(dynamic_results),
        "findings": findings_json,
    }


def validate_paths(
    *,
    evidence_path: Path,
    world_index_path: Path,
    reachability_path: Path,
    lower: Position,
    upper: Position,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    evidence = _load_json(evidence_path, EVIDENCE_FORMAT, "spawn/NPC evidence")
    reachability = _load_json(reachability_path, REACHABILITY_FORMAT, "reachability report")
    world_index_path = world_index_path.expanduser().resolve()
    if not world_index_path.is_file():
        raise FileNotFoundError(world_index_path)
    try:
        from otbm_world_index import WorldIndex
    except ImportError as exc:
        raise SpawnNpcValidationError("otbm_world_index.py is required") from exc
    provenance = {
        "spawnEvidence": {
            "path": evidence_path.name,
            "size": evidence_path.stat().st_size,
            "sha256": _sha256(evidence_path),
            "format": EVIDENCE_FORMAT,
        },
        "worldIndex": {
            "path": world_index_path.name,
            "size": world_index_path.stat().st_size,
            "sha256": _sha256(world_index_path),
            "format": "canary-otbm-world-index-v1",
        },
        "reachability": {
            "path": reachability_path.name,
            "size": reachability_path.stat().st_size,
            "sha256": _sha256(reachability_path),
            "format": REACHABILITY_FORMAT,
        },
    }
    with WorldIndex(world_index_path) as index:
        return validate_evidence(
            evidence=evidence,
            world_index=index,
            reachability_report=reachability,
            lower=lower,
            upper=upper,
            sample_limit=sample_limit,
            provenance=provenance,
        )


def write_json(path: Path, document: Mapping[str, Any], *, overwrite: bool = False) -> None:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise SpawnNpcValidationError(f"Output must not be a symlink: {expanded}")
    destination = expanded.resolve()
    if destination.exists() and not destination.is_file():
        raise SpawnNpcValidationError(f"Output exists but is not a regular file: {destination}")
    if destination.exists() and not overwrite:
        raise SpawnNpcValidationError(f"Output already exists: {destination}; pass overwrite=True")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(document, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
