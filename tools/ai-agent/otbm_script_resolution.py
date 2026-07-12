from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

REPORT_FORMAT = "canary-otbm-script-resolution-v1"
SUPPORTED_NAMESPACES = ("actionId", "uniqueId", "itemId", "position")
SCRIPT_EXTENSIONS = {".lua", ".xml"}
SKIP_DIRS = {".git", "build", "vcpkg_installed", "node_modules", ".cache", "artifacts"}
GENERIC_PATH_MARKERS = (
    "/actions/system/",
    "quest_system",
    "quest_reward_common",
    "teleport_item",
    "remove-create_item",
    "register_actions",
)
LUA_CONSTRUCTOR_RE = re.compile(
    r"(?:^|\n)\s*(?:local\s+)?(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<event>Action|MoveEvent)\s*\(",
    re.M,
)
LUA_REGISTER_RE = re.compile(r"\b(?P<name>[A-Za-z_]\w*)\s*:\s*register\s*\(")
LUA_TRIGGER_RE = re.compile(
    r"\b(?P<name>[A-Za-z_]\w*)\s*:\s*(?P<method>aid|uid|id|position)\s*\((?P<args>[^\n)]*(?:\([^\n)]*\)[^\n)]*)*)\)",
    re.M,
)
LUA_NUMBER_ASSIGN_RE = re.compile(r"(?:^|\n)\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*(\d+)\b", re.M)
LUA_TABLE_ASSIGN_RE = re.compile(r"(?:^|\n)\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*\{", re.M)
LUA_TABLE_INDEX_ASSIGN_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\[\s*(\d+)\s*\]\s*=")
LUA_ALIAS_RE = re.compile(r"\b(?:local\s+)?([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)\s*$")
DIRECT_NUMBER_LIST_RE = re.compile(r"^\s*\d+(?:\s*,\s*\d+)*\s*$")
REFERENCE_PATTERNS = {
    "actionId": [
        re.compile(r"(?:\b(?:actionid|actionId)\b|\bgetActionId\s*\(\s*\))\s*==\s*(\d+)", re.I),
        re.compile(r"(\d+)\s*==\s*(?:\b(?:actionid|actionId)\b|\bgetActionId\s*\(\s*\))", re.I),
    ],
    "uniqueId": [
        re.compile(r"(?:\b(?:uniqueid|uniqueId|uid)\b|\bgetUniqueId\s*\(\s*\))\s*==\s*(\d+)", re.I),
        re.compile(r"(\d+)\s*==\s*(?:\b(?:uniqueid|uniqueId|uid)\b|\bgetUniqueId\s*\(\s*\))", re.I),
    ],
}


class ScriptAuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class Source:
    path: str
    line: int
    context: str


@dataclass(frozen=True)
class Registration:
    namespace: str
    event_type: str
    handler: str
    mode: str
    source: Source
    values: tuple[int, ...] = ()
    range_start: int | None = None
    range_end: int | None = None
    position: tuple[int, int, int] | None = None
    generic: bool = False
    confidence: str = "high"
    origin: str = "lua"

    def matches(self, value: int | tuple[int, int, int]) -> bool:
        if self.namespace == "position":
            return isinstance(value, tuple) and self.position == value
        if not isinstance(value, int):
            return False
        if value in self.values:
            return True
        return (
            self.range_start is not None
            and self.range_end is not None
            and self.range_start <= value <= self.range_end
        )

    def key(self) -> tuple[Any, ...]:
        return (
            self.namespace,
            self.event_type,
            self.handler,
            self.mode,
            self.source.path,
            self.source.line,
            self.values,
            self.range_start,
            self.range_end,
            self.position,
            self.generic,
        )

    def to_json(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "namespace": self.namespace,
            "eventType": self.event_type,
            "handler": self.handler,
            "mode": self.mode,
            "source": asdict(self.source),
            "generic": self.generic,
            "confidence": self.confidence,
            "origin": self.origin,
        }
        if self.values:
            payload["values"] = list(self.values)
        if self.range_start is not None:
            payload["range"] = {"from": self.range_start, "to": self.range_end}
        if self.position is not None:
            payload["position"] = list(self.position)
        return payload


@dataclass(frozen=True)
class Reference:
    namespace: str
    value: int
    source: Source

    def to_json(self) -> dict[str, Any]:
        return {"namespace": self.namespace, "value": self.value, "source": asdict(self.source)}


@dataclass
class LuaTableInfo:
    keys: set[int] = field(default_factory=set)
    values: set[int] = field(default_factory=set)
    fields: dict[str, set[int]] = field(default_factory=lambda: defaultdict(set))
    entry_count: int = 0


@dataclass(frozen=True)
class LoopSpan:
    start_line: int
    end_line: int
    header: str
    kind: str
    variables: tuple[str, ...]
    table_name: str | None = None
    range_start: int | None = None
    range_end: int | None = None
    range_step: int = 1


@dataclass
class ScanResult:
    registrations: list[Registration] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)
    unresolved_dynamic_registrations: list[dict[str, Any]] = field(default_factory=list)
    inactive_registrations: list[dict[str, Any]] = field(default_factory=list)
    files_scanned: int = 0


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScriptAuditError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ScriptAuditError(f"JSON root must be an object: {path}")
    return payload


def iter_script_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SCRIPT_EXTENSIONS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def _mask_lua_comments(text: str) -> str:
    output = list(text)
    index = 0
    quote: str | None = None
    long_string = False
    while index < len(text):
        if long_string:
            if text.startswith("]]", index):
                index += 2
                long_string = False
            else:
                index += 1
            continue
        character = text[index]
        if quote:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = None
            index += 1
            continue
        if text.startswith("[[", index):
            long_string = True
            index += 2
            continue
        if character in {"'", '"'}:
            quote = character
            index += 1
            continue
        if text.startswith("--[[", index):
            end = text.find("]]", index + 4)
            if end < 0:
                end = len(text) - 2
            for cursor in range(index, min(len(text), end + 2)):
                if output[cursor] != "\n":
                    output[cursor] = " "
            index = end + 2
            continue
        if text.startswith("--", index):
            end = text.find("\n", index)
            if end < 0:
                end = len(text)
            for cursor in range(index, end):
                output[cursor] = " "
            index = end
            continue
        index += 1
    return "".join(output)


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _line_context(lines: list[str], line: int, radius: int = 1) -> str:
    start = max(1, line - radius)
    end = min(len(lines), line + radius)
    return "\n".join(f"{index}: {lines[index - 1].strip()}" for index in range(start, end + 1))


def _find_matching_brace(text: str, opening: int) -> int | None:
    depth = 0
    quote: str | None = None
    long_string = False
    index = opening
    while index < len(text):
        if long_string:
            if text.startswith("]]", index):
                long_string = False
                index += 2
            else:
                index += 1
            continue
        character = text[index]
        if quote:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = None
            index += 1
            continue
        if text.startswith("[[", index):
            long_string = True
            index += 2
            continue
        if character in {"'", '"'}:
            quote = character
            index += 1
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _parse_table_body(body: str) -> LuaTableInfo:
    info = LuaTableInfo()
    depth = 1
    index = 0
    quote: str | None = None
    long_string = False
    expect_entry = True
    while index < len(body):
        if long_string:
            if body.startswith("]]", index):
                long_string = False
                index += 2
            else:
                index += 1
            continue
        character = body[index]
        if quote:
            if character == "\\":
                index += 2
                continue
            if character == quote:
                quote = None
            index += 1
            continue
        if body.startswith("[[", index):
            long_string = True
            index += 2
            continue
        if character in {"'", '"'}:
            quote = character
            index += 1
            continue
        if character == "{":
            depth += 1
            index += 1
            continue
        if character == "}":
            depth -= 1
            index += 1
            continue
        if depth == 1 and character == ",":
            expect_entry = True
            index += 1
            continue
        if depth == 1 and expect_entry and character == "[":
            match = re.match(r"\[\s*(\d+)\s*\]\s*=", body[index:])
            if match:
                info.keys.add(int(match.group(1)))
                info.entry_count += 1
                expect_entry = False
                index += match.end()
                continue
        if depth == 1 and expect_entry:
            match = re.match(r"(\d+)\b", body[index:])
            if match:
                info.values.add(int(match.group(1)))
                info.entry_count += 1
                expect_entry = False
                index += match.end()
                continue
            if not character.isspace():
                info.entry_count += 1
                expect_entry = False
        field_match = re.match(r"([A-Za-z_]\w*)\s*=\s*(\d+)\b", body[index:])
        if field_match:
            info.fields[field_match.group(1)].add(int(field_match.group(2)))
            index += field_match.end()
            continue
        index += 1
    return info


def _parse_lua_tables(cleaned: str) -> dict[str, LuaTableInfo]:
    result: dict[str, LuaTableInfo] = {}
    for match in LUA_TABLE_ASSIGN_RE.finditer(cleaned):
        opening = cleaned.find("{", match.start(), match.end() + 1)
        if opening < 0:
            continue
        closing = _find_matching_brace(cleaned, opening)
        if closing is None:
            continue
        result[match.group(1)] = _parse_table_body(cleaned[opening + 1 : closing])
    for match in LUA_TABLE_INDEX_ASSIGN_RE.finditer(cleaned):
        table = result.setdefault(match.group(1), LuaTableInfo())
        table.keys.add(int(match.group(2)))
        table.entry_count = max(table.entry_count, len(table.keys))
    return result


def _block_open_kind(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    if re.match(r"^for\b.*\bdo\s*$", stripped):
        return "for"
    if re.match(r"^while\b.*\bdo\s*$", stripped):
        return "while"
    if re.match(r"^(?:local\s+)?function\b", stripped):
        return "function"
    if re.match(r"^if\b.*\bthen\s*$", stripped):
        return "if"
    if stripped == "do":
        return "do"
    if stripped == "repeat":
        return "repeat"
    return None


def _parse_loop_header(header: str, numbers: dict[str, int]) -> dict[str, Any] | None:
    numeric = re.match(
        r"\s*for\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*|\d+)\s*,\s*([A-Za-z_]\w*|\d+)(?:\s*,\s*(-?\d+))?\s+do\s*$",
        header,
    )
    if numeric:
        start_token, end_token = numeric.group(2), numeric.group(3)
        start = int(start_token) if start_token.isdigit() else numbers.get(start_token)
        end = int(end_token) if end_token.isdigit() else numbers.get(end_token)
        if start is None or end is None:
            return None
        return {
            "kind": "numeric",
            "variables": (numeric.group(1),),
            "start": start,
            "end": end,
            "step": int(numeric.group(4) or 1),
        }
    iterator = re.match(
        r"\s*for\s+(.+?)\s+in\s+(pairs|ipairs)\s*\(\s*([A-Za-z_]\w*)\s*\)\s+do\s*$",
        header,
    )
    if iterator:
        variables = tuple(part.strip() for part in iterator.group(1).split(","))
        return {
            "kind": iterator.group(2),
            "variables": variables,
            "table": iterator.group(3),
        }
    return None


def _parse_lua_loops(cleaned: str, numbers: dict[str, int]) -> list[LoopSpan]:
    lines = cleaned.splitlines()
    stack: list[dict[str, Any]] = []
    loops: list[LoopSpan] = []
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if re.match(r"^end\b", stripped):
            if stack:
                block = stack.pop()
                if block["kind"] == "for" and block.get("loop"):
                    loop = block["loop"]
                    loops.append(
                        LoopSpan(
                            start_line=block["line"],
                            end_line=line_no,
                            header=block["header"],
                            kind=loop["kind"],
                            variables=tuple(loop["variables"]),
                            table_name=loop.get("table"),
                            range_start=loop.get("start"),
                            range_end=loop.get("end"),
                            range_step=loop.get("step", 1),
                        )
                    )
            continue
        if re.match(r"^until\b", stripped):
            if stack and stack[-1]["kind"] == "repeat":
                stack.pop()
            continue
        kind = _block_open_kind(line)
        if kind:
            stack.append(
                {
                    "kind": kind,
                    "line": line_no,
                    "header": stripped,
                    "loop": _parse_loop_header(stripped, numbers) if kind == "for" else None,
                }
            )
    return loops


def _split_arguments(arguments: str) -> list[str]:
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    for index, character in enumerate(arguments):
        if quote:
            if character == quote and (index == 0 or arguments[index - 1] != "\\"):
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
        elif character in "({[":
            depth += 1
        elif character in ")}]":
            depth = max(0, depth - 1)
        elif character == "," and depth == 0:
            parts.append(arguments[start:index].strip())
            start = index + 1
    parts.append(arguments[start:].strip())
    return [part for part in parts if part]


def _position_from_expression(expression: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"\s*Position\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*", expression)
    if not match:
        return None
    return tuple(int(match.group(index)) for index in range(1, 4))  # type: ignore[return-value]


def _active_loop(loops: list[LoopSpan], line: int) -> LoopSpan | None:
    candidates = [loop for loop in loops if loop.start_line < line < loop.end_line]
    return max(candidates, key=lambda loop: loop.start_line, default=None)


def _aliases_for_loop(lines: list[str], loop: LoopSpan, line: int) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for raw in lines[loop.start_line: line - 1]:
        match = LUA_ALIAS_RE.search(raw.strip())
        if match:
            aliases[match.group(1)] = match.group(2)
    return aliases


def _resolve_expression(
    expression: str,
    *,
    numbers: dict[str, int],
    tables: dict[str, LuaTableInfo],
    loop: LoopSpan | None,
    aliases: dict[str, str],
) -> tuple[str, tuple[int, ...] | None, tuple[int, int] | None]:
    expression = expression.strip()
    seen: set[str] = set()
    while expression in aliases and expression not in seen:
        seen.add(expression)
        expression = aliases[expression]
    if expression.isdigit():
        return "literal", (int(expression),), None
    if expression in numbers:
        return "constant", (numbers[expression],), None
    if loop is None:
        return "dynamic", None, None
    if loop.kind == "numeric" and expression == loop.variables[0]:
        if loop.range_start is None or loop.range_end is None or loop.range_step != 1:
            values = tuple(range(loop.range_start or 0, (loop.range_end or -1) + (1 if loop.range_step > 0 else -1), loop.range_step))
            return "numeric-loop-values", values, None
        return "numeric-range", None, (min(loop.range_start, loop.range_end), max(loop.range_start, loop.range_end))
    table = tables.get(loop.table_name or "")
    if table is None:
        return "dynamic", None, None
    first = loop.variables[0] if loop.variables else ""
    second = loop.variables[1] if len(loop.variables) > 1 else ""
    if expression == first:
        if loop.kind == "pairs":
            return "table-key", tuple(sorted(table.keys)), None
        return "table-index", tuple(range(1, table.entry_count + 1)), None
    if expression == second:
        return "table-value", tuple(sorted(table.values)), None
    property_match = re.fullmatch(r"([A-Za-z_]\w*)\.([A-Za-z_]\w*)", expression)
    if property_match and property_match.group(1) == second:
        values = table.fields.get(property_match.group(2), set())
        return "table-field", tuple(sorted(values)), None
    return "dynamic", None, None


def _is_generic(path: str, mode: str, range_start: int | None, range_end: int | None) -> bool:
    lowered = path.lower()
    if any(marker in lowered for marker in GENERIC_PATH_MARKERS):
        return True
    return (
        mode == "numeric-range"
        and range_start is not None
        and range_end is not None
        and range_end - range_start + 1 >= 100
    )


def _namespace_for_method(method: str) -> str:
    return {"aid": "actionId", "uid": "uniqueId", "id": "itemId", "position": "position"}[method]


def _int_attribute(attributes: dict[str, str], name: str) -> int | None:
    value = attributes.get(name)
    if value is None or not re.fullmatch(r"\d+", value.strip()):
        return None
    return int(value)


def scan_xml_file(path: Path, root: Path) -> ScanResult:
    result = ScanResult(files_scanned=1)
    rel = path.relative_to(root).as_posix()
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError):
        return result
    for element in tree.iter():
        tag = element.tag.lower().split("}")[-1]
        if tag not in {"action", "movevent"}:
            continue
        event_type = "Action" if tag == "action" else "MoveEvent"
        attributes = {key.lower(): value for key, value in element.attrib.items()}
        line = int(getattr(element, "sourceline", 0) or 0)
        source = Source(rel, line, ET.tostring(element, encoding="unicode")[:300])
        handler = attributes.get("script") or attributes.get("function") or rel
        specs = (
            ("actionId", "actionid", "fromaid", "toaid"),
            ("uniqueId", "uniqueid", "fromuid", "touid"),
            ("itemId", "itemid", "fromid", "toid"),
        )
        for namespace, exact_name, from_name, to_name in specs:
            exact = _int_attribute(attributes, exact_name)
            start = _int_attribute(attributes, from_name)
            end = _int_attribute(attributes, to_name)
            if exact is not None:
                result.registrations.append(
                    Registration(namespace, event_type, handler, "xml-literal", source, values=(exact,), origin="xml")
                )
            if start is not None and end is not None:
                low, high = sorted((start, end))
                result.registrations.append(
                    Registration(
                        namespace,
                        event_type,
                        handler,
                        "xml-range",
                        source,
                        range_start=low,
                        range_end=high,
                        generic=(high - low + 1 >= 100),
                        origin="xml",
                    )
                )
    return result


def load_manual_rules(path: Path | None) -> list[Registration]:
    if path is None:
        return []
    payload = load_json(path)
    raw_rules = payload.get("rules")
    if not isinstance(raw_rules, list):
        raise ScriptAuditError("Manual rule document must contain a rules array")
    result: list[Registration] = []
    for index, raw in enumerate(raw_rules):
        if not isinstance(raw, dict):
            raise ScriptAuditError(f"Manual rule {index} must be an object")
        namespace = raw.get("namespace")
        if namespace not in SUPPORTED_NAMESPACES:
            raise ScriptAuditError(f"Manual rule {index} has invalid namespace")
        event_type = str(raw.get("eventType", "ManualRule"))
        handler = str(raw.get("handler", f"manual-rule-{index}"))
        reason = str(raw.get("reason", "manual rule"))
        source = Source(str(path), index + 1, reason)
        values_raw = raw.get("values", [])
        values = tuple(sorted({int(value) for value in values_raw})) if isinstance(values_raw, list) else ()
        range_raw = raw.get("range")
        start = end = None
        if isinstance(range_raw, dict):
            start = int(range_raw["from"])
            end = int(range_raw["to"])
        position_raw = raw.get("position")
        position = tuple(int(value) for value in position_raw) if isinstance(position_raw, list) and len(position_raw) == 3 else None
        result.append(
            Registration(
                namespace=namespace,
                event_type=event_type,
                handler=handler,
                mode="manual-rule",
                source=source,
                values=values,
                range_start=start,
                range_end=end,
                position=position,  # type: ignore[arg-type]
                generic=bool(raw.get("generic", True)),
                confidence="manual",
                origin="manual",
            )
        )
    return result


def _registration_index(registrations: Iterable[Registration]) -> tuple[dict[str, dict[int, list[Registration]]], dict[str, list[Registration]], dict[tuple[int, int, int], list[Registration]]]:
    exact: dict[str, dict[int, list[Registration]]] = {namespace: defaultdict(list) for namespace in SUPPORTED_NAMESPACES if namespace != "position"}
    ranges: dict[str, list[Registration]] = {namespace: [] for namespace in SUPPORTED_NAMESPACES if namespace != "position"}
    positions: dict[tuple[int, int, int], list[Registration]] = defaultdict(list)
    for registration in registrations:
        if registration.namespace == "position" and registration.position is not None:
            positions[registration.position].append(registration)
            continue
        for value in registration.values:
            exact[registration.namespace][value].append(registration)
        if registration.range_start is not None:
            ranges[registration.namespace].append(registration)
    return exact, ranges, positions


def _matches(
    namespace: str,
    value: int,
    exact: dict[str, dict[int, list[Registration]]],
    ranges: dict[str, list[Registration]],
) -> list[Registration]:
    return [*exact[namespace].get(value, []), *(entry for entry in ranges[namespace] if entry.matches(value))]


def _distinct_handlers(registrations: Iterable[Registration]) -> set[tuple[str, str, str]]:
    return {(entry.event_type, entry.handler, entry.source.path) for entry in registrations}


def _has_conflict(registrations: list[Registration]) -> bool:
    by_event: defaultdict[str, set[tuple[str, str]]] = defaultdict(set)
    for registration in registrations:
        by_event[registration.event_type].add((registration.handler, registration.source.path))
    return any(len(handlers) > 1 for event, handlers in by_event.items() if event not in {"ManualRule", "Unknown"})


def _selected_handlers_for_placement(
    placement: dict[str, Any],
    exact: dict[str, dict[int, list[Registration]]],
    ranges: dict[str, list[Registration]],
    positions: dict[tuple[int, int, int], list[Registration]],
) -> tuple[list[Registration], list[Registration], dict[str, str]]:
    available: dict[str, list[Registration]] = {}
    position_raw = placement.get("position")
    if isinstance(position_raw, list) and len(position_raw) == 3:
        position = tuple(int(value) for value in position_raw)
        available["position"] = positions.get(position, [])
    for namespace, key in (("uniqueId", "uniqueId"), ("actionId", "actionId"), ("itemId", "itemId")):
        value = placement.get(key)
        if isinstance(value, int):
            available[namespace] = _matches(namespace, value, exact, ranges)
    selected: list[Registration] = []
    shadowed: list[Registration] = []
    selected_by_event: dict[str, str] = {}
    event_types = {entry.event_type for entries in available.values() for entry in entries}
    precedence = ("position", "uniqueId", "actionId", "itemId")
    for event_type in sorted(event_types):
        chosen_namespace: str | None = None
        for namespace in precedence:
            candidates = [entry for entry in available.get(namespace, []) if entry.event_type == event_type]
            if candidates:
                selected.extend(candidates)
                chosen_namespace = namespace
                selected_by_event[event_type] = namespace
                break
        if chosen_namespace is not None:
            chosen_index = precedence.index(chosen_namespace)
            for namespace in precedence[chosen_index + 1 :]:
                shadowed.extend(entry for entry in available.get(namespace, []) if entry.event_type == event_type)
    return selected, shadowed, selected_by_event


def _reference_index(references: Iterable[Reference]) -> dict[str, dict[int, list[Reference]]]:
    result: dict[str, dict[int, list[Reference]]] = {"actionId": defaultdict(list), "uniqueId": defaultdict(list)}
    for reference in references:
        result[reference.namespace][reference.value].append(reference)
    return result


def _handled_status(selected: list[Registration], selected_by_event: dict[str, str]) -> str:
    if _has_conflict(selected):
        return "conflicting"
    if any(entry.generic for entry in selected):
        return "handled-generically"
    if any(entry.mode in {"numeric-range", "xml-range"} for entry in selected):
        return "handled-by-range"
    if selected and all(namespace == "itemId" for namespace in selected_by_event.values()):
        return "handled-by-item-id"
    if selected and all(namespace == "position" for namespace in selected_by_event.values()):
        return "handled-by-position"
    return "handled-directly"


# ---------------------------------------------------------------------------
# Production resolver (v1)
# ---------------------------------------------------------------------------

REFERENCE_PATTERNS = {
    "actionId": [
        re.compile(r"(?:\b(?:actionid|actionId)\b|\bgetActionId\s*\(\s*\))\s*(?:==|~=)\s*(\d+)", re.I),
        re.compile(r"(\d+)\s*(?:==|~=)\s*(?:\b(?:actionid|actionId)\b|\bgetActionId\s*\(\s*\))", re.I),
    ],
    "uniqueId": [
        re.compile(r"(?:\b(?:uniqueid|uniqueId|uid)\b|\bgetUniqueId\s*\(\s*\))\s*(?:==|~=)\s*(\d+)", re.I),
        re.compile(r"(\d+)\s*(?:==|~=)\s*(?:\b(?:uniqueid|uniqueId|uid)\b|\bgetUniqueId\s*\(\s*\))", re.I),
    ],
}

LUA_EVENT_TYPE_RE = re.compile(
    r"\b(?P<name>[A-Za-z_]\w*)\s*:\s*type\s*\(\s*[\"'](?P<type>[A-Za-z_-]+)[\"']\s*\)",
    re.I,
)
REVIEW_FORMAT = "canary-otbm-script-review-rules-v1"
ALLOWED_REVIEW_DISPOSITIONS = {
    "intentional-marker",
    "legacy-unused",
    "missing-script",
    "needs-manual-review",
    "preserve-until-reviewed",
}


def _event_types_for_handler(
    handler: str,
    constructors: dict[str, str],
    event_types: dict[str, set[str]],
) -> tuple[str, ...]:
    constructor = constructors.get(handler, "Unknown")
    if constructor == "Action":
        return ("Action:onUse",)
    if constructor == "MoveEvent":
        declared = sorted(event_types.get(handler, set()))
        if declared:
            return tuple(f"MoveEvent:{entry.lower()}" for entry in declared)
        return ("MoveEvent:unknown",)
    return (constructor,)


def scan_lua_file(path: Path, root: Path) -> ScanResult:  # type: ignore[no-redef]
    result = ScanResult(files_scanned=1)
    text = path.read_text(encoding="utf-8", errors="ignore")
    cleaned = _mask_lua_comments(text)
    lines = text.splitlines()
    cleaned_lines = cleaned.splitlines()
    rel = path.relative_to(root).as_posix()
    constructors = {match.group("name"): match.group("event") for match in LUA_CONSTRUCTOR_RE.finditer(cleaned)}
    registered = {match.group("name") for match in LUA_REGISTER_RE.finditer(cleaned)}
    event_types: dict[str, set[str]] = defaultdict(set)
    for match in LUA_EVENT_TYPE_RE.finditer(cleaned):
        event_types[match.group("name")].add(match.group("type"))
    numbers = {match.group(1): int(match.group(2)) for match in LUA_NUMBER_ASSIGN_RE.finditer(cleaned)}
    tables = _parse_lua_tables(cleaned)
    loops = _parse_lua_loops(cleaned, numbers)

    for match in LUA_TRIGGER_RE.finditer(cleaned):
        handler = match.group("name")
        method = match.group("method")
        namespace = _namespace_for_method(method)
        line = _line_number(cleaned, match.start())
        source = Source(rel, line, _line_context(lines, line))
        if handler not in registered:
            result.inactive_registrations.append(
                {
                    "namespace": namespace,
                    "handler": handler,
                    "arguments": match.group("args").strip(),
                    "source": asdict(source),
                }
            )
            continue
        handler_event_types = _event_types_for_handler(handler, constructors, event_types)
        arguments = _split_arguments(match.group("args"))
        if namespace == "position":
            position = _position_from_expression(match.group("args"))
            if position is not None:
                for event_type in handler_event_types:
                    result.registrations.append(
                        Registration(
                            namespace,
                            event_type,
                            handler,
                            "position-literal",
                            source,
                            position=position,
                            generic=False,
                        )
                    )
            else:
                result.unresolved_dynamic_registrations.append(
                    {
                        "namespace": namespace,
                        "eventTypes": list(handler_event_types),
                        "handler": handler,
                        "arguments": match.group("args").strip(),
                        "source": asdict(source),
                    }
                )
            continue

        active_loop = _active_loop(loops, line)
        aliases = _aliases_for_loop(cleaned_lines, active_loop, line) if active_loop else {}
        values: set[int] = set()
        ranges_found: list[tuple[int, int, str]] = []
        unresolved: list[str] = []
        modes: set[str] = set()
        for argument in arguments:
            mode, resolved_values, resolved_range = _resolve_expression(
                argument,
                numbers=numbers,
                tables=tables,
                loop=active_loop,
                aliases=aliases,
            )
            modes.add(mode)
            if resolved_values:
                values.update(resolved_values)
            elif resolved_range:
                ranges_found.append((resolved_range[0], resolved_range[1], mode))
            else:
                unresolved.append(argument)

        if values:
            mode = next(iter(modes)) if len(modes) == 1 else "mixed-static"
            for event_type in handler_event_types:
                result.registrations.append(
                    Registration(
                        namespace,
                        event_type,
                        handler,
                        mode,
                        source,
                        values=tuple(sorted(values)),
                        generic=_is_generic(rel, mode, None, None),
                        confidence="high" if mode in {"literal", "constant"} else "medium",
                    )
                )
        for start, end, mode in ranges_found:
            for event_type in handler_event_types:
                result.registrations.append(
                    Registration(
                        namespace,
                        event_type,
                        handler,
                        mode,
                        source,
                        range_start=start,
                        range_end=end,
                        generic=_is_generic(rel, mode, start, end),
                    )
                )
        if unresolved:
            result.unresolved_dynamic_registrations.append(
                {
                    "namespace": namespace,
                    "eventTypes": list(handler_event_types),
                    "handler": handler,
                    "arguments": unresolved,
                    "source": asdict(source),
                    "loop": asdict(active_loop) if active_loop else None,
                }
            )

    for namespace, patterns in REFERENCE_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(cleaned):
                line = _line_number(cleaned, match.start())
                result.references.append(
                    Reference(namespace, int(match.group(1)), Source(rel, line, _line_context(lines, line)))
                )

    table_target_re = re.compile(
        r"\b(?P<table>[A-Za-z_]\w*)\s*\[\s*target\.(?P<field>actionid|uid|uniqueid)\s*\]",
        re.I,
    )
    for match in table_target_re.finditer(cleaned):
        table = tables.get(match.group("table"))
        if table is None:
            continue
        namespace = "actionId" if match.group("field").lower() == "actionid" else "uniqueId"
        line = _line_number(cleaned, match.start())
        source = Source(rel, line, _line_context(lines, line))
        for value in sorted(table.keys):
            result.references.append(Reference(namespace, value, source))

    range_target_re = re.compile(
        r"target\.(?P<field>actionid|uid|uniqueid)\s*>=\s*(?P<start>\d+)"
        r"[^\n]*?target\.(?P=field)\s*<=\s*(?P<end>\d+)",
        re.I,
    )
    for match in range_target_re.finditer(cleaned):
        start, end = int(match.group("start")), int(match.group("end"))
        if abs(end - start) > 4096:
            continue
        namespace = "actionId" if match.group("field").lower() == "actionid" else "uniqueId"
        line = _line_number(cleaned, match.start())
        source = Source(rel, line, _line_context(lines, line))
        for value in range(min(start, end), max(start, end) + 1):
            result.references.append(Reference(namespace, value, source))
    return result


def scan_repository(
    root: Path,
    script_roots: Iterable[str | Path] | None = None,
) -> ScanResult:  # type: ignore[no-redef]
    """Scan only the active datapack roots.

    By default Canary loads ``data`` and ``data-otservbr-global``.  Alternative
    datapacks such as ``data-canary`` must be requested explicitly; mixing them
    produces duplicate registrations and false conflicts.
    """

    root = root.resolve()
    requested = tuple(script_roots or ("data", "data-otservbr-global"))
    combined = ScanResult()
    visited: set[Path] = set()
    for entry in requested:
        candidate = Path(entry)
        candidate = candidate if candidate.is_absolute() else root / candidate
        candidate = candidate.resolve()
        if not candidate.exists():
            continue
        paths = [candidate] if candidate.is_file() else list(iter_script_files(candidate))
        for path in paths:
            resolved = path.resolve()
            if resolved in visited:
                continue
            visited.add(resolved)
            partial = scan_lua_file(resolved, root) if resolved.suffix.lower() == ".lua" else scan_xml_file(resolved, root)
            combined.files_scanned += partial.files_scanned
            combined.registrations.extend(partial.registrations)
            combined.references.extend(partial.references)
            combined.unresolved_dynamic_registrations.extend(partial.unresolved_dynamic_registrations)
            combined.inactive_registrations.extend(partial.inactive_registrations)

    unique = {registration.key(): registration for registration in combined.registrations}
    combined.registrations = sorted(
        unique.values(),
        key=lambda item: (item.namespace, item.event_type, item.source.path, item.source.line, item.handler),
    )
    reference_unique = {
        (reference.namespace, reference.value, reference.source.path, reference.source.line): reference
        for reference in combined.references
    }
    combined.references = sorted(
        reference_unique.values(),
        key=lambda item: (item.namespace, item.value, item.source.path, item.source.line),
    )
    return combined


def _reference_is_registered_target(reference: Reference, registered_action_paths: set[str]) -> bool:
    context = reference.source.context.lower()
    target_like = any(
        marker in context
        for marker in (
            "target.actionid",
            "target.actionid",
            "target.uniqueid",
            "target.uid",
            "item.actionid",
            "item.uniqueid",
            "item.uid",
        )
    )
    if not target_like:
        return False
    path = reference.source.path.replace("\\", "/")
    return path in registered_action_paths or path.endswith("/scripts/lib/register_actions.lua")


def _registration_runtime_status(registrations: list[Registration]) -> str:
    if _has_conflict(registrations):
        return "conflicting"
    if any(entry.generic for entry in registrations):
        return "handled-generically"
    if any(entry.mode in {"numeric-range", "xml-range"} for entry in registrations):
        return "handled-by-range"
    return "handled-directly"


def _review_rule_matches(rule: dict[str, Any], namespace: str, value: int) -> bool:
    if rule.get("namespace") != namespace:
        return False
    values = rule.get("values")
    if isinstance(values, list) and value in {int(entry) for entry in values}:
        return True
    raw_range = rule.get("range")
    if isinstance(raw_range, dict):
        start = int(raw_range.get("from", -1))
        end = int(raw_range.get("to", -1))
        return min(start, end) <= value <= max(start, end)
    return False


def load_review_rules(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = load_json(path)
    if payload.get("format") != REVIEW_FORMAT:
        raise ScriptAuditError(f"Review rules must use format {REVIEW_FORMAT}")
    raw_rules = payload.get("rules")
    if not isinstance(raw_rules, list):
        raise ScriptAuditError("Review rule document must contain a rules array")
    result: list[dict[str, Any]] = []
    for index, rule in enumerate(raw_rules):
        if not isinstance(rule, dict):
            raise ScriptAuditError(f"Review rule {index} must be an object")
        namespace = rule.get("namespace")
        if namespace not in {"actionId", "uniqueId"}:
            raise ScriptAuditError(f"Review rule {index} has an invalid namespace")
        disposition = rule.get("disposition")
        if disposition not in ALLOWED_REVIEW_DISPOSITIONS:
            raise ScriptAuditError(f"Review rule {index} has an invalid disposition")
        if not isinstance(rule.get("values"), list) and not isinstance(rule.get("range"), dict):
            raise ScriptAuditError(f"Review rule {index} requires values or range")
        if not str(rule.get("reason", "")).strip():
            raise ScriptAuditError(f"Review rule {index} requires a reason")
        result.append(dict(rule))
    return result


def _review_for_identifier(
    rules: list[dict[str, Any]],
    namespace: str,
    value: int,
) -> dict[str, Any] | None:
    for rule in rules:
        if _review_rule_matches(rule, namespace, value):
            return {
                "disposition": rule["disposition"],
                "reason": rule["reason"],
                "source": rule.get("source"),
            }
    return None


def _resolution_status_for_namespace(
    *,
    namespace: str,
    value: int,
    placement: dict[str, Any],
    exact: dict[str, dict[int, list[Registration]]],
    ranges: dict[str, list[Registration]],
    selected: list[Registration],
    selected_by_event: dict[str, str],
    references: list[Reference],
    registered_action_paths: set[str],
) -> dict[str, Any]:
    direct = _matches(namespace, value, exact, ranges)
    if direct and _has_conflict(direct):
        return {"status": "conflicting", "handlers": [entry.to_json() for entry in direct]}

    direct_selected = [entry for entry in selected if entry.namespace == namespace and entry.matches(value)]
    if direct_selected:
        return {
            "status": _registration_runtime_status(direct_selected),
            "handlers": [entry.to_json() for entry in direct_selected],
        }

    selected_namespaces = set(selected_by_event.values())
    if namespace == "actionId" and "uniqueId" in selected_namespaces:
        handlers = [entry.to_json() for entry in selected if entry.namespace == "uniqueId"]
        return {"status": "handled-by-unique-id", "handlers": handlers}

    matching_references = [
        reference
        for reference in references
        if reference.namespace == namespace
        and reference.value == value
        and _reference_is_registered_target(reference, registered_action_paths)
    ]
    if matching_references:
        return {
            "status": "handled-as-target",
            "references": [
                {
                    **reference.to_json(),
                    "role": "target-condition",
                    "registered": True,
                    "eventType": "Action:onUse",
                }
                for reference in matching_references
            ],
        }

    if "position" in selected_namespaces:
        handlers = [entry.to_json() for entry in selected if entry.namespace == "position"]
        return {"status": "handled-by-position", "handlers": handlers}
    if "itemId" in selected_namespaces:
        handlers = [entry.to_json() for entry in selected if entry.namespace == "itemId"]
        return {"status": "handled-by-item-id", "handlers": handlers}

    if namespace == "uniqueId" and isinstance(placement.get("actionId"), int):
        action_value = int(placement["actionId"])
        action_handlers = _matches("actionId", action_value, exact, ranges)
        if action_handlers:
            status = "handled-by-fallback" if action_value == 2000 else "handled-by-action-id"
            evidence = (
                "Quest chest actionId 2000 consumes uniqueId as the reward/storage selector."
                if action_value == 2000
                else "Canary falls back from an unregistered uniqueId to the registered actionId handler on the same item."
            )
            return {
                "status": status,
                "handlers": [entry.to_json() for entry in action_handlers],
                "evidence": evidence,
            }

    item_info = placement.get("_itemInfo")
    items_xml = item_info.get("itemsXml") if isinstance(item_info, dict) else None
    item_type = items_xml.get("type") if isinstance(items_xml, dict) else None
    category = items_xml.get("category") if isinstance(items_xml, dict) else None
    if item_type in {"door", "key"} or category in {"door", "key"}:
        return {
            "status": "handled-by-item-id",
            "handler": "Generic door/key action registration",
            "evidence": "The item is classified as a door or key in items.xml and is registered through Canary's generated door/key item tables.",
        }

    all_references = [
        reference.to_json()
        for reference in references
        if reference.namespace == namespace and reference.value == value
    ]
    if all_references:
        return {"status": "referenced-only", "references": all_references}
    return {"status": "unresolved"}


def _overall_placement_status(resolutions: dict[str, dict[str, Any]]) -> str:
    statuses = [entry["status"] for entry in resolutions.values()]
    if not statuses:
        return "unresolved"
    if "conflicting" in statuses:
        return "conflicting"
    unresolved = {"unresolved", "referenced-only"}
    unresolved_count = sum(status in unresolved for status in statuses)
    if unresolved_count == len(statuses):
        return "referenced-only" if all(status == "referenced-only" for status in statuses) else "unresolved"
    if unresolved_count:
        return "partially-resolved"
    if len(statuses) > 1:
        return "handled-multiple"
    return statuses[0]


def build_script_audit(  # type: ignore[no-redef]
    *,
    item_audit: dict[str, Any],
    repository_root: Path,
    script_roots: Iterable[str | Path] | None = None,
    manual_rules: list[Registration] | None = None,
    review_rules: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    mechanics = item_audit.get("mechanicPlacements")
    if not isinstance(mechanics, list):
        raise ScriptAuditError("Item audit has no mechanicPlacements array")
    requested_roots = tuple(str(entry) for entry in (script_roots or ("data", "data-otservbr-global")))
    scan = scan_repository(repository_root, requested_roots)
    registrations = [*scan.registrations, *(manual_rules or [])]
    exact, ranges, positions = _registration_index(registrations)
    references_by_value = _reference_index(scan.references)
    registered_action_paths = {
        entry.source.path
        for entry in registrations
        if entry.event_type == "Action:onUse"
    }
    mechanic_item_index = {
        int(entry["id"]): entry
        for entry in item_audit.get("mapMechanicItems", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), int)
    }

    placement_results: list[dict[str, Any]] = []
    aggregate: dict[str, dict[int, list[dict[str, Any]]]] = {
        "actionId": defaultdict(list),
        "uniqueId": defaultdict(list),
    }
    placement_status_counts: Counter[str] = Counter()

    for index, raw_placement in enumerate(mechanics):
        if not isinstance(raw_placement, dict):
            raise ScriptAuditError(f"Invalid mechanic placement at index {index}")
        placement = dict(raw_placement)
        item_id = placement.get("itemId")
        if isinstance(item_id, int):
            placement["_itemInfo"] = mechanic_item_index.get(item_id)
        selected, shadowed, selected_by_event = _selected_handlers_for_placement(placement, exact, ranges, positions)
        resolutions: dict[str, dict[str, Any]] = {}

        if placement.get("teleportDestination") is not None:
            resolutions["teleportDestination"] = {
                "status": "handled-by-engine",
                "handler": "Item teleport destination",
                "evidence": "OTBM teleport destination is stored on the map item and executed by Canary item logic.",
            }
        if placement.get("houseDoorId") is not None:
            resolutions["houseDoorId"] = {
                "status": "handled-by-engine",
                "handler": "House door registry",
                "evidence": "OTBM house-door identifiers are consumed by Canary house-door logic.",
            }

        for namespace, key in (("actionId", "actionId"), ("uniqueId", "uniqueId")):
            value = placement.get(key)
            if not isinstance(value, int):
                continue
            references = references_by_value[namespace].get(value, [])
            resolutions[namespace] = _resolution_status_for_namespace(
                namespace=namespace,
                value=value,
                placement=placement,
                exact=exact,
                ranges=ranges,
                selected=selected,
                selected_by_event=selected_by_event,
                references=references,
                registered_action_paths=registered_action_paths,
            )

        status = _overall_placement_status(resolutions)
        placement_status_counts[status] += 1
        result_entry = {
            "index": index,
            "itemId": placement.get("itemId"),
            "position": placement.get("position"),
            "depth": placement.get("itemDepth", placement.get("depth")),
            "actionId": placement.get("actionId"),
            "uniqueId": placement.get("uniqueId"),
            "houseDoorId": placement.get("houseDoorId"),
            "teleportDestination": placement.get("teleportDestination"),
            "status": status,
            "resolutions": resolutions,
            "selectedByEvent": selected_by_event,
            "handlers": [entry.to_json() for entry in selected],
            "shadowedHandlers": [entry.to_json() for entry in shadowed],
            "references": [
                entry.to_json()
                for namespace, key in (("actionId", "actionId"), ("uniqueId", "uniqueId"))
                if isinstance(placement.get(key), int)
                for entry in references_by_value[namespace].get(int(placement[key]), [])
            ],
        }
        placement_results.append(result_entry)
        for namespace, key in (("actionId", "actionId"), ("uniqueId", "uniqueId")):
            value = placement.get(key)
            if isinstance(value, int):
                aggregate[namespace][value].append(result_entry)

    identifier_results: dict[str, list[dict[str, Any]]] = {"actionId": [], "uniqueId": []}
    identifier_status_counts: Counter[str] = Counter()
    review_disposition_counts: Counter[str] = Counter()
    unreviewed_identifiers = 0
    runtime_unresolved_identifiers = 0
    review_rules = review_rules or []

    for namespace in ("actionId", "uniqueId"):
        for value, placements in sorted(aggregate[namespace].items()):
            statuses = Counter(
                placement["resolutions"].get(namespace, {"status": "unresolved"})["status"]
                for placement in placements
            )
            if statuses["conflicting"]:
                status = "conflicting"
            elif statuses["unresolved"] or statuses["referenced-only"]:
                handled = sum(
                    count
                    for name, count in statuses.items()
                    if name.startswith("handled")
                )
                status = "partially-resolved" if handled else "unresolved"
            elif len(statuses) == 1:
                status = next(iter(statuses))
            else:
                status = "handled-multiple"
            identifier_status_counts[status] += 1

            review = None
            if status in {"unresolved", "partially-resolved", "referenced-only"}:
                runtime_unresolved_identifiers += 1
                review = _review_for_identifier(review_rules, namespace, value)
                if review is None:
                    unreviewed_identifiers += 1
                else:
                    review_disposition_counts[review["disposition"]] += 1

            handler_keys: dict[tuple[Any, ...], dict[str, Any]] = {}
            reference_keys: dict[tuple[Any, ...], dict[str, Any]] = {}
            for placement in placements:
                resolution = placement["resolutions"].get(namespace, {})
                for handler in resolution.get("handlers", []):
                    source = handler["source"]
                    key = (handler["eventType"], handler["handler"], source["path"], source["line"], handler["mode"])
                    handler_keys[key] = handler
                for reference in resolution.get("references", []):
                    source = reference["source"]
                    key = (source["path"], source["line"])
                    reference_keys[key] = reference

            entry = {
                "value": value,
                "placements": len(placements),
                "status": status,
                "placementStatuses": dict(sorted(statuses.items())),
                "handlers": list(handler_keys.values()),
                "references": list(reference_keys.values()),
                "samplePositions": [placement["position"] for placement in placements[:20]],
            }
            if review is not None:
                entry["review"] = review
            identifier_results[namespace].append(entry)

    unresolved_placements = [
        entry
        for entry in placement_results
        if entry["status"] in {"unresolved", "referenced-only", "partially-resolved"}
    ]
    conflict_placements = [entry for entry in placement_results if entry["status"] == "conflicting"]
    summary = {
        "filesScanned": scan.files_scanned,
        "registrations": len(registrations),
        "luaXmlRegistrations": len(scan.registrations),
        "manualRules": len(manual_rules or []),
        "reviewRules": len(review_rules),
        "references": len(scan.references),
        "mechanicPlacements": len(mechanics),
        "resolvedPlacements": len(mechanics) - len(unresolved_placements) - len(conflict_placements),
        "runtimeUnresolvedPlacements": len(unresolved_placements),
        "conflictingPlacements": len(conflict_placements),
        "identifierCounts": {namespace: len(entries) for namespace, entries in identifier_results.items()},
        "identifierStatusCounts": dict(sorted(identifier_status_counts.items())),
        "placementStatusCounts": dict(sorted(placement_status_counts.items())),
        "runtimeUnresolvedIdentifiers": runtime_unresolved_identifiers,
        "unreviewedIdentifiers": unreviewed_identifiers,
        "reviewDispositionCounts": dict(sorted(review_disposition_counts.items())),
        "unresolvedDynamicRegistrations": len(scan.unresolved_dynamic_registrations),
        "inactiveRegistrations": len(scan.inactive_registrations),
    }
    ok = summary["conflictingPlacements"] == 0 and summary["unreviewedIdentifiers"] == 0
    return {
        "format": REPORT_FORMAT,
        "ok": ok,
        "sources": {
            "itemAudit": item_audit.get("sources"),
            "repositoryRoot": str(repository_root.resolve()),
            "scriptRoots": list(requested_roots),
        },
        "summary": summary,
        "identifiers": identifier_results,
        "placements": placement_results,
        "registrations": [entry.to_json() for entry in registrations],
        "unresolvedDynamicRegistrations": scan.unresolved_dynamic_registrations,
        "inactiveRegistrations": scan.inactive_registrations,
        "notes": [
            "Runtime resolution and human review disposition are intentionally separate.",
            "A reviewed unresolved identifier is preserved and reported; it is not falsely labelled as handled.",
            "Position, uniqueId, actionId, and itemId precedence is evaluated independently for each event type.",
            "MoveEvent stepin, stepout, additem, removeitem, equip, and deequip registrations are distinct event types.",
            "Teleport destinations and house-door identifiers are classified as engine-handled map mechanics.",
            "Quest chest actionId 2000 may use uniqueId as a reward or storage selector.",
        ],
    }


def audit_from_files(  # type: ignore[no-redef]
    *,
    item_audit_path: Path,
    repository_root: Path,
    output: Path,
    script_roots: Iterable[str | Path] | None = None,
    rules_path: Path | None = None,
    review_rules_path: Path | None = None,
) -> dict[str, Any]:
    item_audit = load_json(item_audit_path)
    manual_rules = load_manual_rules(rules_path)
    review_rules = load_review_rules(review_rules_path)
    report = build_script_audit(
        item_audit=item_audit,
        repository_root=repository_root,
        script_roots=script_roots,
        manual_rules=manual_rules,
        review_rules=review_rules,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
