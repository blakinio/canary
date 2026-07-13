from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

REPORT_FORMAT = "canary-otbm-storage-graph-v1"
SCHEMA_VERSION = 1
QUEST_EVIDENCE_FORMAT = "canary-quest-map-evidence-v1"
QUEST_VALIDATION_FORMAT = "canary-quest-map-validation-v1"
SPAWN_EVIDENCE_FORMAT = "canary-otbm-spawn-npc-evidence-v1"
SPAWN_VALIDATION_FORMAT = "canary-otbm-spawn-npc-validation-v1"
REACHABILITY_FORMAT = "canary-otbm-reachability-v1"

MAX_SOURCE_FILES = 10_000
MAX_SOURCE_BYTES = 128 * 1024 * 1024
MAX_OPERATIONS = 250_000
MAX_NODES = 100_000
MAX_TRANSITIONS = 250_000
MAX_UNRESOLVED = 250_000
MAX_SAMPLE_LIMIT = 10_000
DEFAULT_SAMPLE_LIMIT = 500

_NAMESPACE_ORDER = {
    "player-storage": 0,
    "account-storage": 1,
    "player-kv": 2,
    "account-kv": 3,
    "global-storage": 4,
    "global-kv": 5,
    "database": 6,
}


class StorageGraphError(RuntimeError):
    pass


@dataclass(frozen=True)
class SourceRef:
    path: str
    line: int
    context: str
    offset: int

    def json(self) -> dict[str, Any]:
        return {"path": self.path, "line": self.line, "context": self.context}


@dataclass(frozen=True)
class StorageRef:
    namespace: str
    key: int | str

    @property
    def canonical(self) -> str:
        if isinstance(self.key, int):
            key = f"int:{self.key}"
        else:
            key = f"str:{self.key}"
        return f"{self.namespace}|{key}"

    @property
    def node_id(self) -> str:
        return _short_hash(self.canonical)

    def json(self) -> dict[str, Any]:
        return {"namespace": self.namespace, "key": self.key, "nodeId": self.node_id}


@dataclass(frozen=True)
class Condition:
    ref: StorageRef
    operator: str
    value: int | str | bool | None
    exact: bool
    source: SourceRef

    def json(self) -> dict[str, Any]:
        return {
            **self.ref.json(),
            "operator": self.operator,
            "value": self.value,
            "exact": self.exact,
            "source": self.source.json(),
        }


@dataclass(frozen=True)
class BranchSpan:
    start: int
    end: int
    condition: str | None
    condition_offset: int


@dataclass
class _IfFrame:
    kind: str
    condition_start: int | None = None
    body_start: int | None = None
    condition_text: str | None = None
    condition_offset: int = 0
    branches: list[BranchSpan] | None = None

    def __post_init__(self) -> None:
        if self.branches is None:
            self.branches = []


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]


def _sha256_path(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _load_json(path: Path, expected: str) -> dict[str, Any]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StorageGraphError(f"Cannot read JSON {source}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("format") != expected:
        actual = payload.get("format") if isinstance(payload, dict) else type(payload).__name__
        raise StorageGraphError(f"Unsupported input format {actual!r}; expected {expected!r}: {source}")
    return payload


def _input_provenance(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    source = path.expanduser().resolve()
    return {
        "path": source.name,
        "sha256": _sha256_path(source),
        "format": payload.get("format"),
    }


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _context(lines: Sequence[str], line: int) -> str:
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()[:500]
    return ""


def _source_ref(rel: str, text: str, lines: Sequence[str], offset: int) -> SourceRef:
    line = _line_number(text, offset)
    return SourceRef(rel, line, _context(lines, line), offset)


def _mask_comments_and_strings(text: str) -> str:
    """Mask Lua comments and strings while preserving offsets/newlines."""
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
        char = text[index]
        if char in {"'", '"'}:
            quote = char
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


def _mask_comments_keep_strings(text: str) -> str:
    """Mask Lua comments only. Strings stay intact for literal KV keys."""
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
            index = cursor
            continue
        bracket = long_bracket(index)
        if bracket is not None:
            _, end = bracket
            index = end
            continue
        index += 1
    return "".join(result)


def _split_arguments(text: str) -> list[str]:
    args: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    index = 0
    while index < len(text):
        char = text[index]
        if quote is not None:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
        elif char in "({[":
            depth += 1
        elif char in ")} ]".replace(" ", ""):
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            args.append(text[start:index].strip())
            start = index + 1
        index += 1
    args.append(text[start:].strip())
    return args


def _balanced_call_argument(text: str, open_paren: int) -> tuple[str, int] | None:
    depth = 0
    quote: str | None = None
    index = open_paren
    while index < len(text):
        char = text[index]
        if quote is not None:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren + 1 : index], index + 1
        index += 1
    return None


def _literal_string(expression: str) -> str | None:
    value = expression.strip()
    if len(value) < 2 or value[0] not in {"'", '"'} or value[-1] != value[0]:
        return None
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return None
    return parsed if isinstance(parsed, str) else None


def _literal_value(expression: str, aliases: Mapping[str, int | str]) -> int | str | bool | None | object:
    value = expression.strip()
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    string = _literal_string(value)
    if string is not None:
        return string
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "nil":
        return None
    if value in aliases:
        return aliases[value]
    return _DYNAMIC


def _resolve_storage_key(expression: str, aliases: Mapping[str, int | str]) -> int | str | None:
    value = expression.strip()
    literal = _literal_value(value, aliases)
    if literal is not _DYNAMIC and not isinstance(literal, bool) and literal is not None:
        return literal  # type: ignore[return-value]
    if re.fullmatch(r"Storage(?:\.[A-Za-z_]\w*)+", value):
        return value
    match = re.fullmatch(r"(?P<alias>[A-Za-z_]\w*)(?P<suffix>(?:\.[A-Za-z_]\w*)+)", value)
    if match:
        root = aliases.get(match.group("alias"))
        if isinstance(root, str) and root.startswith("Storage."):
            return root + match.group("suffix")
    return None


_DYNAMIC = object()


_ASSIGN_LITERAL_RE = re.compile(
    r"(?m)^\s*(?:local\s+)?(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<value>-?\d+|true|false|nil|'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"|Storage(?:\.[A-Za-z_]\w*)+)\s*(?:[,;]|$)"
)


def _aliases(code: str) -> dict[str, int | str]:
    result: dict[str, int | str] = {}
    for match in _ASSIGN_LITERAL_RE.finditer(code):
        expression = match.group("value").strip()
        if re.fullmatch(r"Storage(?:\.[A-Za-z_]\w*)+", expression):
            result[match.group("name")] = expression
            continue
        parsed = _literal_value(expression, result)
        if parsed is _DYNAMIC or parsed is None or isinstance(parsed, bool):
            continue
        result[match.group("name")] = parsed  # type: ignore[assignment]
    alias_re = re.compile(
        r"(?m)^\s*(?:local\s+)?(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<base>[A-Za-z_]\w*)(?P<suffix>(?:\.[A-Za-z_]\w*)+)\s*(?:[,;]|$)"
    )
    changed = True
    while changed:
        changed = False
        for match in alias_re.finditer(code):
            if match.group("name") in result:
                continue
            root = result.get(match.group("base"))
            if isinstance(root, str) and root.startswith("Storage."):
                result[match.group("name")] = root + match.group("suffix")
                changed = True
    return result


_CALL_STARTS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(r"(?P<receiver>[A-Za-z_]\w*(?:(?:\.|:)\w+)*)\s*:\s*(?P<method>getStorageValue|setStorageValue|getAccountStorage|getUpdatedAccountStorage)\s*\(", re.I),
        "",
        "",
    ),
    (
        re.compile(r"(?P<receiver>[A-Za-z_]\w*(?:(?:\.|:)\w+)*)\s*:\s*kv\s*\(\s*\)\s*:\s*(?P<method>get|set|remove)\s*\(", re.I),
        "player-kv",
        "",
    ),
    (
        re.compile(r"(?P<receiver>[A-Za-z_]\w*(?:(?:\.|:)\w+)*)\s*:\s*accountKV\s*\(\s*\)\s*:\s*(?P<method>get|set|remove)\s*\(", re.I),
        "account-kv",
        "",
    ),
    (
        re.compile(r"Game\s*\.\s*(?P<method>getStorageValue|setStorageValue)\s*\(", re.I),
        "global-storage",
        "Game",
    ),
    (
        re.compile(r"(?:GlobalKV|KV)\s*[\.:]\s*(?P<method>get|set|remove)\s*\(", re.I),
        "global-kv",
        "GlobalKV",
    ),
)

_SCOPED_KV_START = re.compile(
    r"(?P<receiver>[A-Za-z_]\w*(?:(?:\.|:)\w+)*)\s*:\s*kv\s*\(\s*\)\s*:\s*scoped\s*\(", re.I
)
_DB_START = re.compile(r"db\s*\.\s*(?P<method>query|asyncQuery|storeQuery)\s*\(", re.I)


def _operation_kind(method: str) -> str:
    lower = method.lower()
    if lower.startswith("get") or lower == "storequery":
        return "read"
    if lower == "remove":
        return "delete"
    return "write"


def _namespace_from_method(method: str, explicit: str) -> str:
    if explicit:
        return explicit
    lower = method.lower()
    if lower in {"getaccountstorage", "getupdatedaccountstorage"}:
        return "account-storage"
    return "player-storage"


__all__ = [name for name in globals() if not name.startswith("__")]
