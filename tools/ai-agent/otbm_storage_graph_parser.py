from __future__ import annotations

from otbm_storage_graph_calls import *  # noqa: F403

_KEYWORD_RE = re.compile(r"\b(if|then|elseif|else|end|function|for|while|repeat|until|do)\b")


def _if_branches(masked: str, original: str) -> list[BranchSpan]:
    stack: list[_IfFrame] = []
    completed: list[BranchSpan] = []
    pending_loop: set[int] = set()
    tokens = list(_KEYWORD_RE.finditer(masked))
    for token in tokens:
        word = token.group(1)
        if word == "if":
            stack.append(_IfFrame(kind="if", condition_start=token.end(), condition_offset=token.start()))
        elif word == "then":
            if stack and stack[-1].kind == "if" and stack[-1].condition_start is not None:
                frame = stack[-1]
                frame.condition_text = original[frame.condition_start : token.start()].strip()
                frame.condition_offset = frame.condition_start
                frame.body_start = token.end()
                frame.condition_start = None
        elif word == "elseif":
            if stack and stack[-1].kind == "if":
                frame = stack[-1]
                if frame.body_start is not None:
                    frame.branches.append(
                        BranchSpan(frame.body_start, token.start(), frame.condition_text, frame.condition_offset)
                    )
                frame.condition_start = token.end()
                frame.condition_offset = token.start()
                frame.body_start = None
                frame.condition_text = None
        elif word == "else":
            if stack and stack[-1].kind == "if":
                frame = stack[-1]
                if frame.body_start is not None:
                    frame.branches.append(
                        BranchSpan(frame.body_start, token.start(), frame.condition_text, frame.condition_offset)
                    )
                frame.condition_start = None
                frame.condition_text = None
                frame.condition_offset = token.start()
                frame.body_start = token.end()
        elif word == "function":
            stack.append(_IfFrame(kind="generic"))
        elif word in {"for", "while"}:
            stack.append(_IfFrame(kind="loop"))
            pending_loop.add(id(stack[-1]))
        elif word == "do":
            if stack and stack[-1].kind == "loop" and id(stack[-1]) in pending_loop:
                pending_loop.discard(id(stack[-1]))
            else:
                stack.append(_IfFrame(kind="generic"))
        elif word == "repeat":
            stack.append(_IfFrame(kind="repeat"))
        elif word == "until":
            for cursor in range(len(stack) - 1, -1, -1):
                if stack[cursor].kind == "repeat":
                    del stack[cursor:]
                    break
        elif word == "end":
            if not stack:
                continue
            frame = stack.pop()
            pending_loop.discard(id(frame))
            if frame.kind == "if":
                if frame.body_start is not None:
                    frame.branches.append(
                        BranchSpan(frame.body_start, token.start(), frame.condition_text, frame.condition_offset)
                    )
                completed.extend(frame.branches or [])
    return sorted(completed, key=lambda span: (span.start, span.end, span.condition_offset))


_DIRECT_COMPARE_RE = re.compile(
    r"(?P<call>(?:[A-Za-z_]\w*(?:(?:\.|:)\w+)*\s*:\s*(?:getStorageValue|getAccountStorage|getUpdatedAccountStorage)\s*\([^\n\)]{1,500}\)|Game\s*\.\s*getStorageValue\s*\([^\n\)]{1,500}\)|[A-Za-z_]\w*(?:(?:\.|:)\w+)*\s*:\s*kv\s*\(\s*\)\s*:\s*get\s*\([^\n\)]{1,500}\)))\s*(?P<op>==|~=|<=|>=|<|>)\s*(?P<value>[^\s\)\]\},]+)",
    re.I,
)
_REVERSE_COMPARE_RE = re.compile(
    r"(?P<value>-?\d+|true|false|nil|'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"|[A-Za-z_]\w*)\s*(?P<op>==|~=|<=|>=|<|>)\s*(?P<call>(?:[A-Za-z_]\w*(?:(?:\.|:)\w+)*\s*:\s*(?:getStorageValue|getAccountStorage|getUpdatedAccountStorage)\s*\([^\n\)]{1,500}\)|Game\s*\.\s*getStorageValue\s*\([^\n\)]{1,500}\)|[A-Za-z_]\w*(?:(?:\.|:)\w+)*\s*:\s*kv\s*\(\s*\)\s*:\s*get\s*\([^\n\)]{1,500}\)))",
    re.I,
)
_VARIABLE_COMPARE_RE = re.compile(
    r"\b(?P<name>[A-Za-z_]\w*)\s*(?P<op>==|~=|<=|>=|<|>)\s*(?P<value>-?\d+|true|false|nil|'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"|[A-Za-z_]\w*)"
)
_VARIABLE_REVERSE_COMPARE_RE = re.compile(
    r"(?P<value>-?\d+|true|false|nil|'(?:\\.|[^'])*'|\"(?:\\.|[^\"])*\"|[A-Za-z_]\w*)\s*(?P<op>==|~=|<=|>=|<|>)\s*\b(?P<name>[A-Za-z_]\w*)"
)


def _invert_operator(operator: str) -> str:
    return {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "==": "==", "~=": "~="}[operator]


def _call_to_ref(call: str, aliases: Mapping[str, int | str]) -> StorageRef | None:
    game = re.match(r"\s*Game\s*\.\s*getStorageValue\s*\((?P<key>.*)\)\s*$", call, re.I | re.S)
    if game:
        key = _resolve_storage_key(game.group("key"), aliases)
        return StorageRef("global-storage", key) if key is not None else None
    kv = re.match(
        r"\s*(?P<receiver>[A-Za-z_]\w*(?:(?:\.|:)\w+)*)\s*:\s*kv\s*\(\s*\)\s*:\s*get\s*\((?P<key>.*)\)\s*$",
        call,
        re.I | re.S,
    )
    if kv:
        key = _resolve_storage_key(kv.group("key"), aliases)
        return StorageRef("player-kv", key) if key is not None else None
    method = re.match(
        r"\s*(?P<receiver>[A-Za-z_]\w*(?:(?:\.|:)\w+)*)\s*:\s*(?P<method>getStorageValue|getAccountStorage|getUpdatedAccountStorage)\s*\((?P<key>.*)\)\s*$",
        call,
        re.I | re.S,
    )
    if method:
        key = _resolve_storage_key(method.group("key"), aliases)
        if key is None:
            return None
        namespace = "account-storage" if "account" in method.group("method").lower() else "player-storage"
        return StorageRef(namespace, key)
    return None


def _read_variable_refs(code: str, aliases: Mapping[str, int | str]) -> dict[str, StorageRef]:
    result: dict[str, StorageRef] = {}
    conflicts: set[str] = set()
    pattern = re.compile(
        r"(?m)^\s*(?:local\s+)?(?P<name>[A-Za-z_]\w*)\s*=\s*(?P<call>(?:[A-Za-z_]\w*(?:(?:\.|:)\w+)*\s*:\s*(?:getStorageValue|getAccountStorage|getUpdatedAccountStorage)\s*\([^\n\)]{1,500}\)|Game\s*\.\s*getStorageValue\s*\([^\n\)]{1,500}\)|[A-Za-z_]\w*(?:(?:\.|:)\w+)*\s*:\s*kv\s*\(\s*\)\s*:\s*get\s*\([^\n\)]{1,500}\)))"
    )
    for match in pattern.finditer(code):
        ref = _call_to_ref(match.group("call"), aliases)
        if ref is None:
            continue
        name = match.group("name")
        if name in result and result[name] != ref:
            conflicts.add(name)
        else:
            result[name] = ref
    for name in conflicts:
        result.pop(name, None)
    return result


def _conditions_from_text(
    condition_text: str,
    *,
    condition_offset: int,
    original: str,
    rel: str,
    lines: Sequence[str],
    aliases: Mapping[str, int | str],
    read_variables: Mapping[str, StorageRef],
) -> list[Condition]:
    conditions: list[Condition] = []
    source = _source_ref(rel, original, lines, condition_offset)

    def add(ref: StorageRef | None, operator: str, value_expr: str, reverse: bool = False) -> None:
        if ref is None:
            return
        value = _literal_value(value_expr, aliases)
        if value is _DYNAMIC:
            return
        op = _invert_operator(operator) if reverse else operator
        conditions.append(Condition(ref, op, value, op == "==", source))

    for match in _DIRECT_COMPARE_RE.finditer(condition_text):
        add(_call_to_ref(match.group("call"), aliases), match.group("op"), match.group("value"))
    for match in _REVERSE_COMPARE_RE.finditer(condition_text):
        add(_call_to_ref(match.group("call"), aliases), match.group("op"), match.group("value"), reverse=True)
    for match in _VARIABLE_COMPARE_RE.finditer(condition_text):
        add(read_variables.get(match.group("name")), match.group("op"), match.group("value"))
    for match in _VARIABLE_REVERSE_COMPARE_RE.finditer(condition_text):
        add(read_variables.get(match.group("name")), match.group("op"), match.group("value"), reverse=True)

    unique = {(condition.ref.canonical, condition.operator, _canonical_json(condition.value)): condition for condition in conditions}
    return sorted(unique.values(), key=lambda item: (item.ref.canonical, item.operator, _canonical_json(item.value)))


def _detect_delta(
    expression: str,
    target: StorageRef,
    aliases: Mapping[str, int | str],
    read_variables: Mapping[str, StorageRef],
) -> int | None:
    value = expression.strip()
    call_delta = re.fullmatch(r"(?P<call>.+)\s*(?P<op>[+-])\s*(?P<delta>\d+)", value)
    if call_delta:
        ref = _call_to_ref(call_delta.group("call"), aliases)
        if ref == target:
            delta = int(call_delta.group("delta"))
            return delta if call_delta.group("op") == "+" else -delta
    variable_delta = re.fullmatch(r"(?P<name>[A-Za-z_]\w*)\s*(?P<op>[+-])\s*(?P<delta>\d+)", value)
    if variable_delta and read_variables.get(variable_delta.group("name")) == target:
        delta = int(variable_delta.group("delta"))
        return delta if variable_delta.group("op") == "+" else -delta
    return None


def _file_contexts(
    quest_evidence: Mapping[str, Any],
    quest_validation: Mapping[str, Any] | None,
    spawn_evidence: Mapping[str, Any] | None,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    handlers: dict[str, list[dict[str, Any]]] = defaultdict(list)
    map_context: dict[str, list[dict[str, Any]]] = defaultdict(list)
    validation_by_id: dict[str, dict[str, Any]] = {}
    if quest_validation is not None:
        for finding in quest_validation.get("findings", []):
            if isinstance(finding, dict) and isinstance(finding.get("evidenceId"), str):
                validation_by_id[finding["evidenceId"]] = finding
    for evidence in quest_evidence.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        source = evidence.get("source")
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            continue
        path = source["path"]
        details = evidence.get("details") if isinstance(evidence.get("details"), dict) else {}
        if evidence.get("role") == "registration":
            handlers[path].append(
                {
                    "evidenceId": evidence.get("id"),
                    "kind": evidence.get("kind"),
                    "value": evidence.get("value"),
                    "eventType": details.get("eventType"),
                    "handler": details.get("handler"),
                    "classification": validation_by_id.get(str(evidence.get("id")), {}).get("classification"),
                }
            )
        if evidence.get("kind") in {"position", "teleportDestination", "actionId", "uniqueId"}:
            finding = validation_by_id.get(str(evidence.get("id")))
            map_context[path].append(
                {
                    "evidenceId": evidence.get("id"),
                    "kind": evidence.get("kind"),
                    "value": evidence.get("value"),
                    "role": evidence.get("role"),
                    "classification": finding.get("classification") if finding else None,
                }
            )
    actors: dict[str, dict[str, Any]] = {}
    if spawn_evidence is not None:
        by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for definition in spawn_evidence.get("definitions", []):
            if not isinstance(definition, dict) or not isinstance(definition.get("source"), str):
                continue
            by_source[definition["source"]].append(
                {
                    "kind": definition.get("kind"),
                    "name": definition.get("name"),
                    "canonicalName": definition.get("canonicalName"),
                    "line": definition.get("line"),
                }
            )
        for path, values in by_source.items():
            actors[path] = {
                "scope": "source-file",
                "definitions": sorted(
                    values,
                    key=lambda value: (
                        str(value.get("kind")),
                        str(value.get("canonicalName")),
                        int(value.get("line") or 0),
                    ),
                ),
            }
    for values in handlers.values():
        values.sort(key=lambda value: (str(value.get("kind")), _canonical_json(value.get("value")), str(value.get("handler"))))
    for values in map_context.values():
        values.sort(key=lambda value: (str(value.get("kind")), _canonical_json(value.get("value")), str(value.get("role"))))
    return handlers, map_context, actors


def _validate_selected_files(repository_root: Path, quest_evidence: Mapping[str, Any]) -> list[tuple[Path, dict[str, Any]]]:
    root = repository_root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    files = quest_evidence.get("files")
    if not isinstance(files, list) or len(files) > MAX_SOURCE_FILES:
        raise StorageGraphError(f"Quest evidence must contain at most {MAX_SOURCE_FILES} source files")
    selected: list[tuple[Path, dict[str, Any]]] = []
    total_bytes = 0
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise StorageGraphError("Quest evidence contains an invalid source-file entry")
        rel = entry["path"]
        if rel in seen:
            raise StorageGraphError(f"Quest evidence contains a duplicate source path: {rel}")
        seen.add(rel)
        unresolved_candidate = root / rel
        if unresolved_candidate.is_symlink():
            raise StorageGraphError(f"Selected source is missing, non-regular or a symlink: {rel}")
        candidate = unresolved_candidate.resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise StorageGraphError(f"Selected source escapes repository root: {rel}") from exc
        if not candidate.is_file():
            raise StorageGraphError(f"Selected source is missing, non-regular or a symlink: {rel}")
        expected = entry.get("sha256")
        actual = _sha256_path(candidate)
        if not isinstance(expected, str) or expected != actual:
            raise StorageGraphError(f"Selected source hash mismatch: {rel}")
        total_bytes += candidate.stat().st_size
        if total_bytes > MAX_SOURCE_BYTES:
            raise StorageGraphError(f"Selected sources exceed {MAX_SOURCE_BYTES} bytes")
        selected.append((candidate, entry))
    return sorted(selected, key=lambda item: item[1]["path"])


__all__ = [name for name in globals() if not name.startswith("__")]
