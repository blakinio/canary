from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

from otbm_script_resolution import ScriptAuditError, scan_lua_file, scan_xml_file
from otbm_world_index import WorldIndex, WorldIndexError, query_action, query_item, query_position, query_unique

EVIDENCE_FORMAT = "canary-quest-map-evidence-v1"
VALIDATION_FORMAT = "canary-quest-map-validation-v1"
SCRIPT_RESOLUTION_FORMAT = "canary-otbm-script-resolution-v1"
MAX_STATIC_RANGE = 4096
DEFAULT_SAMPLE_LIMIT = 20
MAX_SAMPLE_LIMIT = 1000
MAX_REGION_POSITIONS = 1_000_000

SUPPORTED_KINDS = {
    "actionId",
    "uniqueId",
    "itemId",
    "position",
    "teleportDestination",
    "storage",
}
CLASSIFICATIONS = {"confirmed", "map-only", "script-only", "unresolved", "conflicting"}


class QuestMapValidationError(RuntimeError):
    pass


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QuestMapValidationError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise QuestMapValidationError(f"JSON root must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    target = path.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        raise QuestMapValidationError(f"Refusing to replace symlink output: {target}")
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _line_context(lines: list[str], line: int) -> str:
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()[:500]
    return ""


def mask_lua_noncode(text: str) -> str:
    """Replace Lua comments and string bodies with spaces while preserving newlines."""

    result = list(text)
    length = len(text)
    index = 0

    def blank(start: int, end: int) -> None:
        for cursor in range(start, min(end, length)):
            if result[cursor] not in "\r\n":
                result[cursor] = " "

    def long_bracket(start: int) -> tuple[int, int] | None:
        if start >= length or text[start] != "[":
            return None
        cursor = start + 1
        while cursor < length and text[cursor] == "=":
            cursor += 1
        if cursor >= length or text[cursor] != "[":
            return None
        equals = cursor - start - 1
        close = "]" + ("=" * equals) + "]"
        end = text.find(close, cursor + 1)
        return cursor + 1, length if end < 0 else end + len(close)

    while index < length:
        if text.startswith("--", index):
            bracket = long_bracket(index + 2)
            if bracket is not None:
                _, end = bracket
                blank(index, end)
                index = end
                continue
            end = text.find("\n", index + 2)
            end = length if end < 0 else end
            blank(index, end)
            index = end
            continue
        if text[index] in {"'", '"'}:
            quote = text[index]
            cursor = index + 1
            while cursor < length:
                if text[cursor] == "\\":
                    cursor += 2
                    continue
                cursor += 1
                if cursor <= length and text[cursor - 1] == quote:
                    break
            blank(index, cursor)
            index = cursor
            continue
        bracket = long_bracket(index)
        if bracket is not None:
            _, end = bracket
            blank(index, end)
            index = end
            continue
        index += 1
    return "".join(result)


_NUMBER_ASSIGN_RE = re.compile(r"(?m)^\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*(\d+)\s*(?:[,;]|$)")
_POSITION_ASSIGN_RE = re.compile(
    r"(?m)^\s*(?:local\s+)?(?P<name>[A-Za-z_]\w*)\s*=\s*Position\s*\(\s*"
    r"(?P<x>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)\s*,\s*(?P<y>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)\s*,\s*(?P<z>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)\s*\)"
)
_TABLE_POSITION_ASSIGN_RE = re.compile(
    r"(?ms)^\s*(?:local\s+)?(?P<name>[A-Za-z_]\w*)\s*=\s*\{(?P<body>[^{}]{0,300})\}"
)
_POSITION_RE = re.compile(
    r"\bPosition\s*\(\s*(?P<x>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)\s*,\s*(?P<y>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)\s*,\s*(?P<z>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)\s*\)"
)
_TELEPORT_VARIABLE_RE = re.compile(
    r"\b(?:teleportTo|doTeleportThing)\s*\([^\n\)]*?\b(?P<name>[A-Za-z_]\w*)\s*\)", re.I
)
_STORAGE_RE = re.compile(
    r"\b(?P<method>getStorageValue|setStorageValue)\s*\(\s*(?P<arg>[^,\)\n]+)", re.I
)
_STORAGE_ALIAS_RE = re.compile(
    r"(?m)^\s*(?:local\s+)?(?P<name>[A-Za-z_]\w*)\s*=\s*"
    r"(?P<value>Storage(?:\.[A-Za-z_]\w*)+)\s*(?:[,;]|$)"
)
_ITEM_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(?:Game\s*\.\s*)?createItem\s*\(\s*(?P<value>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)", re.I), "item-create"),
    (re.compile(r"\bdoCreateItem\s*\(\s*(?P<value>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)", re.I), "item-create"),
    (re.compile(r"\b(?:addItem|addItemEx)\s*\(\s*(?P<value>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)", re.I), "item-reward"),
    (re.compile(r"\b(?:removeItem|removeItemOfType)\s*\(\s*(?P<value>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)", re.I), "item-consume"),
    (re.compile(r"\bItemType\s*\(\s*(?P<value>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)", re.I), "item-type"),
    (
        re.compile(
            r"\b(?:item|target)\s*\.\s*(?:itemid|itemId|id)\s*(?:==|~=)\s*(?P<value>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)",
            re.I,
        ),
        "item-condition",
    ),
)


def _resolve_int(expression: str, numbers: dict[str, int]) -> int | None:
    value = expression.strip()
    if value.isdigit():
        return int(value)
    return numbers.get(value)


def _resolve_position(
    x_expr: str,
    y_expr: str,
    z_expr: str,
    numbers: dict[str, int],
) -> tuple[int, int, int] | None:
    values = (_resolve_int(x_expr, numbers), _resolve_int(y_expr, numbers), _resolve_int(z_expr, numbers))
    if any(value is None for value in values):
        return None
    x, y, z = (int(value) for value in values)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        return None
    return x, y, z


def _source(path: str, line: int, lines: list[str]) -> dict[str, Any]:
    return {"path": path, "line": line, "context": _line_context(lines, line)}


def _canonical_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _evidence_id(kind: str, value: Any, role: str, source: dict[str, Any]) -> str:
    raw = "|".join((kind, _canonical_value(value), role, str(source["path"]), str(source["line"])))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _evidence(
    *,
    kind: str,
    value: Any,
    role: str,
    source: dict[str, Any],
    confidence: str = "high",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "id": _evidence_id(kind, value, role, source),
        "kind": kind,
        "value": value,
        "role": role,
        "confidence": confidence,
        "source": source,
    }
    if details:
        result["details"] = details
    return result


def _unresolved(*, kind: str, expression: str, source: dict[str, Any], reason: str) -> dict[str, Any]:
    raw = "|".join((kind, expression, str(source["path"]), str(source["line"]), reason))
    return {
        "id": hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20],
        "kind": kind,
        "expression": expression.strip()[:500],
        "source": source,
        "reason": reason,
    }


def _registration_evidence(path: Path, root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        scan = scan_lua_file(path, root) if path.suffix.lower() == ".lua" else scan_xml_file(path, root)
    except (OSError, ScriptAuditError) as exc:
        raise QuestMapValidationError(f"Cannot scan registrations in {path}: {exc}") from exc
    evidence: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for registration in scan.registrations:
        registration_json = registration.to_json()
        source = registration_json["source"]
        details = {
            "eventType": registration.event_type,
            "handler": registration.handler,
            "mode": registration.mode,
            "origin": registration.origin,
        }
        if registration.namespace == "position" and registration.position is not None:
            evidence.append(
                _evidence(kind="position", value=list(registration.position), role="registration", source=source, details=details)
            )
            continue
        if registration.namespace not in {"actionId", "uniqueId", "itemId"}:
            continue
        values = list(registration.values)
        if registration.range_start is not None and registration.range_end is not None:
            low, high = sorted((registration.range_start, registration.range_end))
            if high - low + 1 <= MAX_STATIC_RANGE:
                values.extend(range(low, high + 1))
            else:
                unresolved.append(
                    _unresolved(
                        kind=registration.namespace,
                        expression=f"{low}..{high}",
                        source=source,
                        reason="Static registration range exceeds the Quest Map Validator expansion limit",
                    )
                )
        for value in sorted(set(values)):
            evidence.append(
                _evidence(kind=registration.namespace, value=value, role="registration", source=source, details=details)
            )
    for reference in scan.references:
        evidence.append(
            _evidence(
                kind=reference.namespace,
                value=reference.value,
                role="comparison",
                source=asdict(reference.source),
                details={"origin": "otbm-script-resolution"},
            )
        )
    for entry in scan.unresolved_dynamic_registrations:
        source = entry.get("source") if isinstance(entry.get("source"), dict) else {"path": str(path), "line": 0, "context": ""}
        unresolved.append(
            _unresolved(
                kind=str(entry.get("namespace", "registration")),
                expression=_canonical_value(entry.get("arguments")),
                source=source,
                reason="Dynamic registration could not be resolved statically",
            )
        )
    return evidence, unresolved


def _lua_evidence(path: Path, root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    cleaned = mask_lua_noncode(text)
    lines = text.splitlines()
    rel = path.relative_to(root).as_posix()
    numbers = {match.group(1): int(match.group(2)) for match in _NUMBER_ASSIGN_RE.finditer(cleaned)}
    storage_aliases = {match.group("name"): match.group("value") for match in _STORAGE_ALIAS_RE.finditer(cleaned)}
    position_constants: dict[str, tuple[int, int, int]] = {}
    evidence, unresolved = _registration_evidence(path, root)

    for match in _POSITION_ASSIGN_RE.finditer(cleaned):
        position = _resolve_position(match.group("x"), match.group("y"), match.group("z"), numbers)
        if position is not None:
            position_constants[match.group("name")] = position

    for match in _TABLE_POSITION_ASSIGN_RE.finditer(cleaned):
        name = match.group("name")
        body = match.group("body")
        fields = {
            field.group("key").lower(): field.group("value")
            for field in re.finditer(r"(?P<key>x|y|z)\s*=\s*(?P<value>[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*|\d+)", body, re.I)
        }
        if set(fields) == {"x", "y", "z"} and re.search(r"(?:pos|position|dest|from|to)", name, re.I):
            position = _resolve_position(fields["x"], fields["y"], fields["z"], numbers)
            if position is not None:
                position_constants[name] = position

    for match in _POSITION_RE.finditer(cleaned):
        line = _line_number(cleaned, match.start())
        source = _source(rel, line, lines)
        position = _resolve_position(match.group("x"), match.group("y"), match.group("z"), numbers)
        if position is None:
            unresolved.append(
                _unresolved(
                    kind="position",
                    expression=match.group(0),
                    source=source,
                    reason="Position contains a dynamic or out-of-range coordinate",
                )
            )
            continue
        context_start = max(0, match.start() - 100)
        context = cleaned[context_start : match.end() + 50].lower()
        teleport_like = any(marker in context for marker in ("teleport", "destination", "destpos", "toposition"))
        kind = "teleportDestination" if teleport_like else "position"
        role = "teleport-destination" if teleport_like else "position-reference"
        evidence.append(_evidence(kind=kind, value=list(position), role=role, source=source))

    for match in _TELEPORT_VARIABLE_RE.finditer(cleaned):
        name = match.group("name")
        if name not in position_constants:
            continue
        line = _line_number(cleaned, match.start())
        evidence.append(
            _evidence(
                kind="teleportDestination",
                value=list(position_constants[name]),
                role="teleport-destination",
                source=_source(rel, line, lines),
                details={"viaConstant": name},
            )
        )

    for pattern, role in _ITEM_PATTERNS:
        for match in pattern.finditer(cleaned):
            line = _line_number(cleaned, match.start())
            source = _source(rel, line, lines)
            expression = match.group("value")
            value = _resolve_int(expression, numbers)
            if value is None or not 0 <= value <= 0xFFFF:
                unresolved.append(
                    _unresolved(
                        kind="itemId",
                        expression=expression,
                        source=source,
                        reason="Item ID expression is dynamic or outside uint16",
                    )
                )
                continue
            evidence.append(_evidence(kind="itemId", value=value, role=role, source=source))

    for match in _STORAGE_RE.finditer(cleaned):
        line = _line_number(cleaned, match.start())
        source = _source(rel, line, lines)
        expression = match.group("arg").strip()
        numeric = _resolve_int(expression, numbers)
        if numeric is not None:
            value: int | str = numeric
        elif re.fullmatch(r"Storage(?:\.[A-Za-z_]\w*)+", expression):
            value = expression
        else:
            alias_match = re.fullmatch(r"(?P<alias>[A-Za-z_]\w*)(?P<suffix>(?:\.[A-Za-z_]\w*)+)", expression)
            alias = storage_aliases.get(alias_match.group("alias")) if alias_match else None
            if alias is not None:
                value = alias + alias_match.group("suffix")
            else:
                unresolved.append(
                    _unresolved(
                        kind="storage",
                        expression=expression,
                        source=source,
                        reason="Storage key expression is dynamic",
                    )
                )
                continue
        role = "storage-read" if match.group("method").lower().startswith("get") else "storage-write"
        evidence.append(_evidence(kind="storage", value=value, role=role, source=source))

    return evidence, unresolved


def _iter_selected_files(
    root: Path,
    source_roots: Sequence[str | Path],
    includes: Sequence[str],
    excludes: Sequence[str],
) -> Iterator[Path]:
    if not includes:
        raise QuestMapValidationError("At least one --include glob is required")
    root = root.resolve()
    seen: set[Path] = set()
    for source_root in source_roots:
        candidate = Path(source_root)
        candidate = candidate if candidate.is_absolute() else root / candidate
        candidate = candidate.resolve()
        if not candidate.exists():
            continue
        paths = [candidate] if candidate.is_file() else candidate.rglob("*")
        for path in paths:
            if not path.is_file() or path.suffix.lower() not in {".lua", ".xml"}:
                continue
            resolved = path.resolve()
            try:
                rel = resolved.relative_to(root).as_posix()
            except ValueError as exc:
                raise QuestMapValidationError(f"Source path escapes repository root: {resolved}") from exc
            if not any(fnmatch.fnmatchcase(rel, pattern) for pattern in includes):
                continue
            if any(fnmatch.fnmatchcase(rel, pattern) for pattern in excludes):
                continue
            if resolved not in seen:
                seen.add(resolved)
                yield resolved


def _deduplicate(entries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    unique = {entry["id"]: entry for entry in entries}
    return sorted(
        unique.values(),
        key=lambda entry: (
            str(entry.get("kind")),
            _canonical_value(entry.get("value", entry.get("expression"))),
            str(entry.get("role", "")),
            str(entry.get("source", {}).get("path", "")),
            int(entry.get("source", {}).get("line", 0)),
        ),
    )


def scan_quest_sources(
    *,
    repository_root: Path,
    source_roots: Sequence[str | Path],
    includes: Sequence[str],
    excludes: Sequence[str] = (),
) -> dict[str, Any]:
    root = repository_root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    files = sorted(_iter_selected_files(root, source_roots, includes, excludes))
    evidence: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    file_entries: list[dict[str, Any]] = []
    for path in files:
        if path.suffix.lower() == ".lua":
            file_evidence, file_unresolved = _lua_evidence(path, root)
        else:
            file_evidence, file_unresolved = _registration_evidence(path, root)
        evidence.extend(file_evidence)
        unresolved.extend(file_unresolved)
        file_entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": _sha256_path(path),
                "evidenceCount": len(file_evidence),
                "unresolvedCount": len(file_unresolved),
            }
        )
    evidence = _deduplicate(evidence)
    unresolved = _deduplicate(unresolved)
    by_kind = Counter(entry["kind"] for entry in evidence)
    by_role = Counter(entry["role"] for entry in evidence)
    canonical = {
        "files": file_entries,
        "evidence": evidence,
        "unresolved": unresolved,
    }
    source_digest = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "format": EVIDENCE_FORMAT,
        "ok": bool(files),
        "selectors": {
            "repositoryRoot": ".",
            "sourceRoots": [str(entry) for entry in source_roots],
            "includes": list(includes),
            "excludes": list(excludes),
        },
        "sourceDigest": source_digest,
        "summary": {
            "filesScanned": len(files),
            "evidenceCount": len(evidence),
            "unresolvedCount": len(unresolved),
            "byKind": dict(sorted(by_kind.items())),
            "byRole": dict(sorted(by_role.items())),
        },
        "files": file_entries,
        "evidence": evidence,
        "unresolved": unresolved,
    }


def _script_status_index(payload: dict[str, Any] | None) -> dict[tuple[str, int], dict[str, Any]]:
    if payload is None:
        return {}
    if payload.get("format") != SCRIPT_RESOLUTION_FORMAT:
        raise QuestMapValidationError(f"Unsupported script-resolution format: {payload.get('format')!r}")
    result: dict[tuple[str, int], dict[str, Any]] = {}
    identifiers = payload.get("identifiers")
    if not isinstance(identifiers, dict):
        return result
    for namespace in ("actionId", "uniqueId"):
        entries = identifiers.get(namespace)
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("value"), int):
                continue
            result[(namespace, int(entry["value"]))] = entry
    return result


def _runtime_status(entry: dict[str, Any] | None) -> str | None:
    if entry is None:
        return None
    for key in ("runtimeStatus", "status", "resolutionStatus"):
        value = entry.get(key)
        if isinstance(value, str):
            return value
    return None


def _handled(status: str | None) -> bool:
    return bool(status and (status.startswith("handled-") or status == "handled-directly"))


def _sample_query_result(result: dict[str, Any], sample_limit: int) -> tuple[int, list[dict[str, Any]]]:
    total = int(result.get("totalCount", 0))
    placements = result.get("placements")
    return total, list(placements[:sample_limit]) if isinstance(placements, list) else []


def _correlate_one(
    entry: dict[str, Any],
    *,
    index_path: Path,
    script_statuses: dict[tuple[str, int], dict[str, Any]],
    sample_limit: int,
) -> dict[str, Any]:
    kind = entry["kind"]
    value = entry["value"]
    map_count = 0
    samples: list[dict[str, Any]] = []
    tile: dict[str, Any] | None = None
    script_entry: dict[str, Any] | None = None
    runtime_status: str | None = None
    reason: str | None = None

    if kind == "itemId":
        map_count, samples = _sample_query_result(query_item(index_path, int(value), limit=sample_limit), sample_limit)
        if map_count:
            classification = "confirmed"
            reason = "The item ID has at least one static placement in the indexed map; quest relevance still depends on source and region context"
        else:
            classification = "unresolved"
            reason = "Absence from the static map does not prove an item ID is invalid; rewards, inventory items and dynamically created items require item-registry/runtime evidence"
    elif kind == "actionId":
        map_count, samples = _sample_query_result(query_action(index_path, int(value), limit=sample_limit), sample_limit)
        script_entry = script_statuses.get((kind, int(value)))
        runtime_status = _runtime_status(script_entry)
        if runtime_status == "conflicting":
            classification = "conflicting"
        elif map_count == 0:
            classification = "script-only"
        elif _handled(runtime_status) or (runtime_status is None and entry.get("role") == "registration"):
            classification = "confirmed"
        else:
            classification = "map-only" if runtime_status in {"unresolved", "referenced-only", "partially-resolved"} else "unresolved"
    elif kind == "uniqueId":
        map_count, samples = _sample_query_result(query_unique(index_path, int(value), limit=sample_limit), sample_limit)
        script_entry = script_statuses.get((kind, int(value)))
        runtime_status = _runtime_status(script_entry)
        if runtime_status == "conflicting":
            classification = "conflicting"
        elif map_count == 0:
            classification = "script-only"
        elif _handled(runtime_status) or (runtime_status is None and entry.get("role") == "registration"):
            classification = "confirmed"
        else:
            classification = "map-only" if runtime_status in {"unresolved", "referenced-only", "partially-resolved"} else "unresolved"
    elif kind in {"position", "teleportDestination"}:
        position = tuple(int(component) for component in value)
        result = query_position(index_path, position)  # type: ignore[arg-type]
        tile = result.get("tile") if isinstance(result.get("tile"), dict) else None
        samples = list(result.get("placements", []))[:sample_limit]
        map_count = 1 if tile is not None else 0
        map_required = kind == "teleportDestination" or entry.get("role") == "registration"
        if tile is not None:
            classification = "confirmed"
        elif map_required:
            classification = "script-only"
        else:
            classification = "unresolved"
            reason = "A generic Position literal can be an area bound, center or transient coordinate; an absent tile is not enough to prove a broken quest requirement"
    elif kind == "storage":
        classification = "unresolved"
        reason = "Storage evidence is inventoried but map-independent; transition analysis is a later phase"
    else:
        raise QuestMapValidationError(f"Unsupported evidence kind: {kind}")

    result_entry = {
        "evidenceId": entry["id"],
        "kind": kind,
        "value": value,
        "role": entry["role"],
        "classification": classification,
        "source": entry["source"],
        "map": {"count": map_count, "samples": samples},
    }
    if tile is not None:
        result_entry["map"]["tile"] = tile
    if runtime_status is not None:
        result_entry["scriptResolution"] = {
            "status": runtime_status,
            "evidence": script_entry,
        }
    if reason is not None:
        result_entry["reason"] = reason
    return result_entry


def _region_volume(lower: tuple[int, int, int], upper: tuple[int, int, int]) -> int:
    return (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1) * (upper[2] - lower[2] + 1)


def _region_map_only(
    *,
    index_path: Path,
    lower: tuple[int, int, int],
    upper: tuple[int, int, int],
    evidence: list[dict[str, Any]],
    sample_limit: int,
) -> list[dict[str, Any]]:
    if _region_volume(lower, upper) > MAX_REGION_POSITIONS:
        raise QuestMapValidationError(f"Region contains more than {MAX_REGION_POSITIONS} coordinate positions")
    referenced: dict[str, set[Any]] = {
        "actionId": {entry["value"] for entry in evidence if entry["kind"] == "actionId"},
        "uniqueId": {entry["value"] for entry in evidence if entry["kind"] == "uniqueId"},
        "teleportDestination": {
            tuple(entry["value"]) for entry in evidence if entry["kind"] == "teleportDestination"
        },
        "position": {tuple(entry["value"]) for entry in evidence if entry["kind"] == "position"},
    }
    findings: dict[tuple[str, Any], dict[str, Any]] = {}
    with WorldIndex(index_path) as index:
        for _, tile in index.iter_region_tiles(lower, upper):
            position = (tile.x, tile.y, tile.z)
            for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count):
                placement = index.placement(ordinal)
                candidates: list[tuple[str, Any]] = []
                if "actionId" in placement:
                    candidates.append(("actionId", placement["actionId"]))
                if "uniqueId" in placement:
                    candidates.append(("uniqueId", placement["uniqueId"]))
                if "teleportDestination" in placement:
                    candidates.append(("teleportDestination", tuple(placement["teleportDestination"])))
                for kind, value in candidates:
                    if value in referenced[kind]:
                        continue
                    key = (kind, value)
                    finding = findings.setdefault(
                        key,
                        {
                            "kind": kind,
                            "value": list(value) if isinstance(value, tuple) else value,
                            "classification": "map-only",
                            "map": {"count": 0, "samples": []},
                            "reason": "Map mechanic exists inside the selected region but is not referenced by the selected source set",
                        },
                    )
                    finding["map"]["count"] += 1
                    if len(finding["map"]["samples"]) < sample_limit:
                        finding["map"]["samples"].append(placement)
            if position not in referenced["position"]:
                continue
    return sorted(findings.values(), key=lambda item: (item["kind"], _canonical_value(item["value"])))


def validate_quest_evidence(
    *,
    evidence_report: dict[str, Any],
    world_index: Path,
    script_resolution: dict[str, Any] | None = None,
    region: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    if evidence_report.get("format") != EVIDENCE_FORMAT:
        raise QuestMapValidationError(f"Unsupported evidence format: {evidence_report.get('format')!r}")
    if not isinstance(sample_limit, int) or isinstance(sample_limit, bool) or not 1 <= sample_limit <= MAX_SAMPLE_LIMIT:
        raise QuestMapValidationError(f"sample_limit must be between 1 and {MAX_SAMPLE_LIMIT}")
    raw_evidence = evidence_report.get("evidence")
    if not isinstance(raw_evidence, list):
        raise QuestMapValidationError("Evidence report has no evidence array")
    evidence = [entry for entry in raw_evidence if isinstance(entry, dict) and entry.get("kind") in SUPPORTED_KINDS]
    statuses = _script_status_index(script_resolution)
    findings = [
        _correlate_one(entry, index_path=world_index, script_statuses=statuses, sample_limit=sample_limit)
        for entry in evidence
    ]
    map_only: list[dict[str, Any]] = []
    normalized_region = None
    if region is not None:
        first, second = region
        lower = tuple(min(first[index], second[index]) for index in range(3))
        upper = tuple(max(first[index], second[index]) for index in range(3))
        if not (0 <= lower[0] <= upper[0] <= 0xFFFF and 0 <= lower[1] <= upper[1] <= 0xFFFF and 0 <= lower[2] <= upper[2] <= 15):
            raise QuestMapValidationError("Region is outside the OTBM coordinate range")
        normalized_region = {"from": list(lower), "to": list(upper)}
        map_only = _region_map_only(
            index_path=world_index,
            lower=lower,  # type: ignore[arg-type]
            upper=upper,  # type: ignore[arg-type]
            evidence=evidence,
            sample_limit=sample_limit,
        )
    counts = Counter(entry["classification"] for entry in [*findings, *map_only])
    by_kind = Counter(entry["kind"] for entry in findings)
    unresolved_source = evidence_report.get("unresolved")
    unresolved_count = len(unresolved_source) if isinstance(unresolved_source, list) else 0
    return {
        "format": VALIDATION_FORMAT,
        "ok": counts["conflicting"] == 0,
        "complete": sum(counts[name] for name in ("map-only", "script-only", "unresolved", "conflicting")) == 0
        and unresolved_count == 0,
        "sources": {
            "evidenceDigest": evidence_report.get("sourceDigest"),
            "worldIndex": {"path": world_index.name, "sha256": _sha256_path(world_index)},
            "scriptResolution": script_resolution.get("sources") if script_resolution else None,
        },
        "region": normalized_region,
        "summary": {
            "evidenceCount": len(evidence),
            "findingCount": len(findings) + len(map_only),
            "sourceUnresolvedCount": unresolved_count,
            "byClassification": {name: counts[name] for name in sorted(CLASSIFICATIONS)},
            "byKind": dict(sorted(by_kind.items())),
            "mapOnlyRegionMechanics": len(map_only),
        },
        "findings": findings,
        "mapOnlyRegionMechanics": map_only,
        "sourceUnresolved": unresolved_source if isinstance(unresolved_source, list) else [],
        "notes": [
            "confirmed means the selected source evidence and required map placement were both found; AID/UID handler confirmation uses script-resolution when supplied.",
            "map-only means the map placement exists but a confirmed selected handler/reference was not established.",
            "script-only means selected source evidence expects an identifier or position absent from the indexed map.",
            "Item-ID map counts are context only: absence from static OTBM is unresolved for rewards, inventory items and dynamic creation, not automatically script-only.",
            "Generic Position literals absent from the map remain unresolved unless they are explicit registrations or teleport destinations.",
            "Dynamic Lua and storage transition semantics remain unresolved rather than guessed.",
        ],
    }


def scan_to_file(
    output: Path,
    *,
    repository_root: Path,
    source_roots: Sequence[str | Path],
    includes: Sequence[str],
    excludes: Sequence[str] = (),
) -> dict[str, Any]:
    payload = scan_quest_sources(
        repository_root=repository_root,
        source_roots=source_roots,
        includes=includes,
        excludes=excludes,
    )
    _write_json(output, payload)
    return payload


def validate_to_file(
    output: Path,
    *,
    evidence_path: Path,
    world_index: Path,
    script_resolution_path: Path | None = None,
    region: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    evidence = _load_json(evidence_path)
    script = _load_json(script_resolution_path) if script_resolution_path is not None else None
    payload = validate_quest_evidence(
        evidence_report=evidence,
        world_index=world_index,
        script_resolution=script,
        region=region,
        sample_limit=sample_limit,
    )
    _write_json(output, payload)
    return payload
