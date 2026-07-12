from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

REPORT_FORMAT = "canary-otbm-script-resolution-v1"
DEFAULT_DATAPACKS = ("data", "data-otservbr-global")
ENGINE_GENERIC_ACTION_IDS = {2000: "generic quest chest"}
UNKNOWN = object()


@dataclass
class LuaTable:
    array: list[Any] = field(default_factory=list)
    fields: dict[Any, Any] = field(default_factory=dict)

    def keys(self) -> list[Any]:
        return list(range(1, len(self.array) + 1)) + list(self.fields)

    def values(self) -> list[Any]:
        return list(self.array) + list(self.fields.values())

    def get(self, key: Any) -> Any:
        if isinstance(key, int) and 1 <= key <= len(self.array):
            return self.array[key - 1]
        return self.fields.get(key, UNKNOWN)


@dataclass
class LoopFrame:
    start: int
    end: int
    values: dict[str, list[Any]]


@dataclass
class Registration:
    handler_kind: str
    event_type: str
    namespace: str
    values: list[Any]
    path: str
    line: int
    object_name: str
    registration_type: str
    confidence: str = "high"
    details: str | None = None

    def to_json(self) -> dict[str, Any]:
        payload = {
            "handlerKind": self.handler_kind,
            "eventType": self.event_type,
            "namespace": self.namespace,
            "values": self.values,
            "path": self.path,
            "line": self.line,
            "object": self.object_name,
            "registrationType": self.registration_type,
            "confidence": self.confidence,
        }
        if self.details:
            payload["details"] = self.details
        return payload


def strip_lua_comments(text: str) -> str:
    """Remove Lua comments while preserving line numbers and string contents."""
    out: list[str] = []
    index = 0
    quote: str | None = None
    long_comment = False
    while index < len(text):
        if long_comment:
            end = text.find("]]", index)
            if end < 0:
                out.extend("\n" if ch == "\n" else " " for ch in text[index:])
                break
            out.extend("\n" if ch == "\n" else " " for ch in text[index : end + 2])
            index = end + 2
            long_comment = False
            continue
        ch = text[index]
        if quote:
            out.append(ch)
            if ch == "\\" and index + 1 < len(text):
                out.append(text[index + 1])
                index += 2
                continue
            if ch == quote:
                quote = None
            index += 1
            continue
        if ch in ('"', "'"):
            quote = ch
            out.append(ch)
            index += 1
            continue
        if text.startswith("--[[", index):
            long_comment = True
            out.extend(" " * 4)
            index += 4
            continue
        if text.startswith("--", index):
            end = text.find("\n", index)
            if end < 0:
                out.extend(" " * (len(text) - index))
                break
            out.extend(" " * (end - index))
            out.append("\n")
            index = end + 1
            continue
        out.append(ch)
        index += 1
    return "".join(out)


def split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    depths = {"(": 0, "[": 0, "{": 0}
    pairs = {")": "(", "]": "[", "}": "{"}
    quote: str | None = None
    index = 0
    while index < len(text):
        ch = text[index]
        if quote:
            if ch == "\\":
                index += 2
                continue
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
        elif ch in depths:
            depths[ch] += 1
        elif ch in pairs:
            opener = pairs[ch]
            depths[opener] = max(0, depths[opener] - 1)
        elif ch == delimiter and not any(depths.values()):
            parts.append(text[start:index].strip())
            start = index + 1
        index += 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def capture_balanced(text: str, start: int, opening: str = "{", closing: str = "}") -> tuple[str, int] | None:
    if start >= len(text) or text[start] != opening:
        return None
    depth = 0
    quote: str | None = None
    index = start
    while index < len(text):
        ch = text[index]
        if quote:
            if ch == "\\":
                index += 2
                continue
            if ch == quote:
                quote = None
        elif ch in ('"', "'"):
            quote = ch
        elif ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1], index + 1
        index += 1
    return None


def _safe_numeric(expr: str, env: dict[str, Any]) -> Any:
    candidate = expr.strip()
    for name, value in sorted(env.items(), key=lambda item: -len(item[0])):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            candidate = re.sub(rf"\b{re.escape(name)}\b", str(value), candidate)
    if not re.fullmatch(r"[0-9a-fA-FxX\s()+\-*/%]+", candidate):
        return UNKNOWN
    try:
        value = eval(candidate, {"__builtins__": {}}, {})  # noqa: S307 - restricted grammar above
    except Exception:
        return UNKNOWN
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value)
    return UNKNOWN


def parse_table(text: str, env: dict[str, Any]) -> LuaTable:
    inner = text.strip()[1:-1]
    table = LuaTable()
    for raw_field in split_top_level(inner):
        if not raw_field:
            continue
        match = re.match(r"^\[(.+)\]\s*=\s*(.+)$", raw_field, flags=re.S)
        if match:
            key = eval_expr(match.group(1), env, {})
            value = eval_expr(match.group(2), env, {})
            if key is not UNKNOWN:
                try:
                    hash(key)
                except TypeError:
                    pass
                else:
                    table.fields[key] = value
            continue
        match = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+)$", raw_field, flags=re.S)
        if match:
            table.fields[match.group(1)] = eval_expr(match.group(2), env, {})
            continue
        value = eval_expr(raw_field, env, {})
        table.array.append(value)
    return table


def _flatten(value: Any) -> list[Any]:
    if value is UNKNOWN or value is None:
        return []
    if isinstance(value, list):
        result: list[Any] = []
        for entry in value:
            result.extend(_flatten(entry))
        return result
    return [value]


def _resolve_path(expr: str, env: dict[str, Any], loop_env: dict[str, list[Any]]) -> Any:
    match = re.match(r"^([A-Za-z_]\w*)", expr)
    if not match:
        return UNKNOWN
    name = match.group(1)
    values: list[Any]
    if name in loop_env:
        values = loop_env[name]
    elif name in env:
        values = [env[name]]
    else:
        return UNKNOWN
    rest = expr[match.end() :]
    token_re = re.compile(r"^\s*(?:\.([A-Za-z_]\w*)|\[([^\]]+)\])")
    while rest.strip():
        token = token_re.match(rest)
        if not token:
            return UNKNOWN
        key: Any
        if token.group(1):
            key = token.group(1)
        else:
            key = eval_expr(token.group(2), env, loop_env)
            key_values = _flatten(key)
            if len(key_values) != 1:
                return UNKNOWN
            key = key_values[0]
        next_values: list[Any] = []
        for value in values:
            if isinstance(value, LuaTable):
                resolved = value.get(key)
            elif isinstance(value, dict):
                resolved = value.get(key, UNKNOWN)
            else:
                resolved = UNKNOWN
            next_values.extend(_flatten(resolved))
        values = next_values
        rest = rest[token.end() :]
    return values if len(values) != 1 else values[0]


def eval_expr(expr: str, env: dict[str, Any], loop_env: dict[str, list[Any]]) -> Any:
    expr = expr.strip().rstrip(";")
    if not expr:
        return UNKNOWN
    if expr.startswith("{"):
        captured = capture_balanced(expr, 0)
        if captured and captured[1] == len(expr):
            return parse_table(captured[0], env)
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]
    if expr in ("true", "false"):
        return expr == "true"
    if expr == "nil":
        return None
    position = re.match(r"^(?:Position\s*\()?\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)?$", expr)
    if position:
        return tuple(int(position.group(i)) for i in range(1, 4))
    unpack = re.match(r"^(?:table\.)?unpack\s*\((.+)\)$", expr, flags=re.S)
    if unpack:
        value = eval_expr(unpack.group(1), env, loop_env)
        if isinstance(value, LuaTable):
            return value.array
        return value
    numeric = _safe_numeric(expr, {**env, **{k: v[0] for k, v in loop_env.items() if len(v) == 1}})
    if numeric is not UNKNOWN:
        return numeric
    if re.fullmatch(r"[A-Za-z_]\w*(?:\s*(?:\.[A-Za-z_]\w*|\[[^\]]+\]))*", expr):
        return _resolve_path(expr, env, loop_env)
    return UNKNOWN


def extract_environment(text: str, base_env: dict[str, Any] | None = None) -> dict[str, Any]:
    env: dict[str, Any] = dict(base_env or {})
    lines = text.splitlines()
    # Repeat to resolve constants that depend on earlier constants.
    for _ in range(3):
        for line in lines:
            match = re.match(r"^\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*([^{}\n]+?)\s*$", line)
            if not match:
                continue
            name, expr = match.groups()
            if any(marker in expr for marker in ("function", "Action(", "MoveEvent(", "BossLever(")):
                continue
            value = eval_expr(expr, env, {})
            if value is not UNKNOWN:
                env[name] = value
    assignment = re.compile(r"(?:^|\n)\s*(?:local\s+)?([A-Za-z_]\w*)\s*=\s*\{")
    for match in assignment.finditer(text):
        brace = text.find("{", match.start())
        captured = capture_balanced(text, brace)
        if not captured:
            continue
        env[match.group(1)] = parse_table(captured[0], env)
    return env


def _line_block_starts(line: str) -> list[str]:
    code = line.strip()
    starts: list[str] = []
    if re.search(r"\bfor\b.+\bdo\b", code):
        starts.append("for")
    elif re.search(r"\bwhile\b.+\bdo\b", code):
        starts.append("while")
    elif re.search(r"\bif\b.+\bthen\b", code):
        starts.append("if")
    if re.search(r"\bfunction\b", code):
        starts.append("function")
    if re.match(r"^\s*repeat\b", code):
        starts.append("repeat")
    if re.match(r"^\s*do\s*$", code):
        starts.append("do")
    return starts


def build_loop_frames(lines: list[str], env: dict[str, Any]) -> list[LoopFrame]:
    stack: list[tuple[str, int, dict[str, list[Any]]]] = []
    frames: list[LoopFrame] = []
    for line_no, line in enumerate(lines, start=1):
        numeric = re.match(r"^\s*for\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s*,\s*(.+?)(?:\s*,\s*(.+?))?\s+do\s*$", line)
        generic = re.match(r"^\s*for\s+(.+?)\s+in\s+(i?pairs)\s*\((.+)\)\s+do\s*$", line)
        starts = _line_block_starts(line)
        for kind in starts:
            values: dict[str, list[Any]] = {}
            if kind == "for" and numeric:
                variable, first_expr, last_expr, step_expr = numeric.groups()
                first = eval_expr(first_expr, env, {})
                last = eval_expr(last_expr, env, {})
                step = eval_expr(step_expr or "1", env, {})
                if all(isinstance(value, int) for value in (first, last, step)) and step != 0:
                    stop = last + (1 if step > 0 else -1)
                    values[variable] = list(range(first, stop, step))[:65536]
            elif kind == "for" and generic:
                variables = [part.strip() for part in generic.group(1).split(",")]
                mode = generic.group(2)
                table_value = eval_expr(generic.group(3), env, {})
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
            stack.append((kind, line_no, values))
        close_count = len(re.findall(r"\bend\b", line))
        if re.search(r"^\s*until\b", line):
            close_count += 1
        # Open/close on one line: remove newly opened frames first as Lua does.
        for _ in range(close_count):
            if not stack:
                break
            kind, start, values = stack.pop()
            if kind == "for":
                frames.append(LoopFrame(start=start, end=line_no, values=values))
    return frames
