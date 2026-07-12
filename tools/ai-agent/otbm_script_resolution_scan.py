from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

from otbm_script_resolution_parser import (
    DEFAULT_DATAPACKS,
    UNKNOWN,
    LoopFrame,
    LuaTable,
    Registration,
    _flatten,
    build_loop_frames,
    eval_expr,
    extract_environment,
    parse_table,
    split_top_level,
    strip_lua_comments,
)


def loop_environment(
    line_no: int,
    frames: list[LoopFrame],
    lines: list[str] | None = None,
    env: dict[str, Any] | None = None,
) -> dict[str, list[Any]]:
    result: dict[str, list[Any]] = {}
    for frame in frames:
        if not (frame.start < line_no < frame.end):
            continue
        values = dict(frame.values)
        if (not values or not any(values.values())) and lines is not None and env is not None:
            loop_line = lines[frame.start - 1]
            numeric = re.match(r"^\s*for\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s*,\s*(.+?)(?:\s*,\s*(.+?))?\s+do\s*$", loop_line)
            generic = re.match(r"^\s*for\s+(.+?)\s+in\s+(i?pairs)\s*\((.+)\)\s+do\s*$", loop_line)
            if numeric:
                variable, first_expr, last_expr, step_expr = numeric.groups()
                first = eval_expr(first_expr, env, result)
                last = eval_expr(last_expr, env, result)
                step = eval_expr(step_expr or "1", env, result)
                if all(isinstance(value, int) for value in (first, last, step)) and step != 0:
                    stop = last + (1 if step > 0 else -1)
                    values[variable] = list(range(first, stop, step))[:65536]
            elif generic:
                variables = [part.strip() for part in generic.group(1).split(",")]
                mode = generic.group(2)
                table_value = eval_expr(generic.group(3), env, result)
                if isinstance(table_value, LuaTable):
                    if mode == "ipairs":
                        keys = list(range(1, len(table_value.array) + 1))
                        vals = table_value.array
                    else:
                        keys = table_value.keys()
                        vals = table_value.values()
                    if variables:
                        values[variables[0]] = keys
                    if len(variables) > 1:
                        values[variables[1]] = vals
        result.update(values)
    return result


def _parse_call_arguments(args: str, env: dict[str, Any], loop_env: dict[str, list[Any]]) -> tuple[list[Any], bool]:
    values: list[Any] = []
    unresolved = False
    for raw in split_top_level(args):
        value = eval_expr(raw, env, loop_env)
        flattened = _flatten(value)
        if not flattened:
            unresolved = True
            continue
        for entry in flattened:
            if isinstance(entry, (int, tuple)) and not isinstance(entry, bool):
                values.append(entry)
            else:
                unresolved = True
    deduped: list[Any] = []
    seen: set[Any] = set()
    for value in values:
        key = tuple(value) if isinstance(value, tuple) else value
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped, unresolved


def _object_types(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"(?:^|\n)\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*(Action|MoveEvent|BossLever)\s*\(", text):
        result[match.group(1)] = {"Action": "action", "MoveEvent": "moveevent", "BossLever": "action"}[match.group(2)]
    return result


def _registered_objects(text: str) -> set[str]:
    return set(re.findall(r"^\s*([A-Za-z_]\w*)\s*:\s*register\s*\(\s*\)", text, flags=re.M))


def _event_types(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in re.finditer(r"^\s*([A-Za-z_]\w*)\s*:\s*type\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", text, flags=re.M):
        result[match.group(1)] = match.group(2).lower().replace("-", "")
    return result


def _registration_type(raw_args: str, values: list[Any], loop_env: dict[str, list[Any]]) -> str:
    if loop_env and any(re.search(rf"\b{re.escape(name)}\b", raw_args) for name in loop_env):
        return "loop"
    if len(values) > 1:
        sorted_ints = sorted(value for value in values if isinstance(value, int))
        if sorted_ints and sorted_ints == list(range(sorted_ints[0], sorted_ints[-1] + 1)):
            return "range"
        return "list"
    return "direct"


def _target_reference_registrations(
    text: str,
    path: str,
    env: dict[str, Any],
    object_types: dict[str, str],
    registered: set[str],
) -> list[Registration]:
    handlers = [(name, object_types.get(name, "action")) for name in sorted(registered)]
    if not handlers and path.endswith("scripts/lib/register_actions.lua"):
        handlers = [("legacy-global-action-library", "action")]
    if not handlers:
        return []
    registrations: list[Registration] = []
    lines = text.splitlines()
    namespaces = {
        "actionId": (r"(?:(?:item|target)(?:\.|:get)Action[Ii]d(?:\(\))?)", "actionId"),
        "uniqueId": (r"(?:(?:item|target)(?:\.|:get)Unique[Ii]d(?:\(\))?|(?:item|target)\.uid)", "uniqueId"),
    }
    for namespace, (reference_pattern, _) in namespaces.items():
        direct_pattern = re.compile(reference_pattern + r"\s*(?:==|~=|>=|<=|>|<)\s*(0x[0-9a-fA-F]+|\d+)", re.I)
        reverse_pattern = re.compile(r"(0x[0-9a-fA-F]+|\d+)\s*(?:==|~=|>=|<=|>|<)\s*" + reference_pattern, re.I)
        table_pattern = re.compile(r"([A-Za-z_]\w*)\s*\[\s*" + reference_pattern + r"\s*\]", re.I)
        found: set[int] = set()
        first_line = 1
        for line_no, line in enumerate(lines, start=1):
            for pattern in (direct_pattern, reverse_pattern):
                for match in pattern.finditer(line):
                    found.add(int(match.group(1), 0))
                    first_line = min(first_line or line_no, line_no)
            for match in table_pattern.finditer(line):
                table = env.get(match.group(1))
                if isinstance(table, LuaTable):
                    found.update(value for value in table.keys() if isinstance(value, int))
                    first_line = min(first_line or line_no, line_no)
        if found:
            name, kind = handlers[0]
            registrations.append(
                Registration(
                    handler_kind=kind,
                    event_type="use" if kind == "action" else "movement",
                    namespace=namespace,
                    values=sorted(found),
                    path=path,
                    line=first_line,
                    object_name=name,
                    registration_type="target-reference",
                    confidence="medium",
                    details="Identifier is inspected by an active registered handler in the same file.",
                )
            )
    return registrations


def scan_lua_file(path: Path, root: Path, shared_env: dict[str, Any] | None = None) -> tuple[list[Registration], list[dict[str, Any]]]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    text = strip_lua_comments(raw)
    env = extract_environment(text, shared_env)
    lines = text.splitlines()
    frames = build_loop_frames(lines, env)
    objects = _object_types(text)
    registered = _registered_objects(text)
    event_types: dict[str, str] = {}
    rel = path.relative_to(root).as_posix()
    registrations: list[Registration] = []
    dynamic: list[dict[str, Any]] = []
    call_pattern = re.compile(r"^\s*([A-Za-z_]\w*)\s*:\s*(aid|uid|id|position)\s*\((.*)\)\s*;?\s*$")
    sequential_env = dict(env)
    for line_no, line in enumerate(lines, start=1):
        type_call = re.match(r"^\s*([A-Za-z_]\w*)\s*:\s*type\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", line)
        if type_call:
            event_types[type_call.group(1)] = type_call.group(2).lower().replace("-", "")
        inline_table = re.match(r"^\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*(\{.*\})\s*$", line)
        if inline_table:
            sequential_env[inline_table.group(1)] = parse_table(inline_table.group(2), sequential_env)
        scalar_assignment = re.match(r"^\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*([^{}]+?)\s*$", line)
        if scalar_assignment and not any(marker in scalar_assignment.group(2) for marker in ("Action(", "MoveEvent(", "BossLever(", "function")):
            assigned = eval_expr(scalar_assignment.group(2), sequential_env, loop_environment(line_no, frames, lines, sequential_env))
            if assigned is not UNKNOWN:
                sequential_env[scalar_assignment.group(1)] = assigned
        inserted = re.match(r"^\s*table\.insert\s*\(\s*([A-Za-z_]\w*)\s*,\s*(.+)\)\s*$", line)
        if inserted:
            target = sequential_env.get(inserted.group(1))
            if isinstance(target, LuaTable):
                inserted_value = eval_expr(inserted.group(2), sequential_env, loop_environment(line_no, frames, lines, sequential_env))
                target.array.extend(_flatten(inserted_value))
        if re.match(r"^\s*function\s+", line):
            continue
        match = call_pattern.match(line)
        if not match:
            continue
        object_name, method, args = match.groups()
        if object_name not in registered:
            continue
        handler_kind = objects.get(object_name)
        if handler_kind is None:
            # Some scripts instantiate in loops or helper factories. Keep a conservative warning.
            handler_kind = "unknown"
        namespace = {"aid": "actionId", "uid": "uniqueId", "id": "itemId", "position": "position"}[method]
        loop_env = loop_environment(line_no, frames, lines, sequential_env)
        values, unresolved = _parse_call_arguments(args, sequential_env, loop_env)
        if values:
            registrations.append(
                Registration(
                    handler_kind=handler_kind,
                    event_type=("use" if handler_kind == "action" else event_types.get(object_name, "movement")),
                    namespace=namespace,
                    values=values,
                    path=rel,
                    line=line_no,
                    object_name=object_name,
                    registration_type=_registration_type(args, values, loop_env),
                    confidence="medium" if unresolved or handler_kind == "unknown" else "high",
                )
            )
        if unresolved:
            dynamic.append(
                {
                    "path": rel,
                    "line": line_no,
                    "object": object_name,
                    "method": method,
                    "arguments": args.strip(),
                    "reason": "Static evaluator could not resolve every registration argument.",
                }
            )
    registrations.extend(_target_reference_registrations(text, rel, sequential_env, objects, registered))
    return registrations, dynamic


def _int_attr(element: ET.Element, name: str) -> int | None:
    value = element.get(name)
    if value is None:
        return None
    try:
        return int(value, 0)
    except ValueError:
        return None


def scan_xml_file(path: Path, root: Path) -> list[Registration]:
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError):
        return []
    rel = path.relative_to(root).as_posix()
    registrations: list[Registration] = []
    for element in tree.iter():
        tag = element.tag.lower()
        if tag not in {"action", "moveevent"}:
            continue
        handler_kind = "action" if tag == "action" else "moveevent"
        event_type = element.get("event", "use" if handler_kind == "action" else "movement").lower().replace("-", "")
        definitions = (
            ("actionId", "actionid", "fromaid", "toaid"),
            ("uniqueId", "uniqueid", "fromuid", "touid"),
            ("itemId", "itemid", "fromid", "toid"),
        )
        for namespace, single_name, first_name, last_name in definitions:
            values: list[int] = []
            single = _int_attr(element, single_name)
            if single is not None:
                values.append(single)
            first = _int_attr(element, first_name)
            last = _int_attr(element, last_name)
            if first is not None and last is not None and first <= last:
                values.extend(range(first, last + 1))
            if values:
                registrations.append(
                    Registration(
                        handler_kind=handler_kind,
                        event_type=event_type,
                        namespace=namespace,
                        values=sorted(set(values)),
                        path=rel,
                        line=1,
                        object_name=element.get("script") or element.get("function") or tag,
                        registration_type="xml-range" if len(values) > 1 else "xml-direct",
                    )
                )
    return registrations


def scan_repository(root: Path, datapacks: Iterable[str] = DEFAULT_DATAPACKS) -> dict[str, Any]:
    root = root.resolve()
    registrations: list[Registration] = []
    dynamic: list[dict[str, Any]] = []
    files_scanned = 0
    shared_env: dict[str, Any] = {}
    shared_tables = root / "data" / "libs" / "tables"
    if shared_tables.is_dir():
        for shared_path in sorted(shared_tables.glob("*.lua")):
            shared_env.update(extract_environment(strip_lua_comments(shared_path.read_text(encoding="utf-8", errors="ignore")), shared_env))
    for datapack in datapacks:
        base = (root / datapack).resolve()
        if not base.is_dir() or root not in base.parents:
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".lua", ".xml"}:
                continue
            files_scanned += 1
            if path.suffix.lower() == ".lua":
                file_registrations, file_dynamic = scan_lua_file(path, root, shared_env)
                registrations.extend(file_registrations)
                dynamic.extend(file_dynamic)
            else:
                registrations.extend(scan_xml_file(path, root))
    return {
        "filesScanned": files_scanned,
        "registrations": [registration.to_json() for registration in registrations],
        "dynamicRegistrations": dynamic,
    }
