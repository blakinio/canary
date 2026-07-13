from __future__ import annotations

from otbm_storage_graph_types import *  # noqa: F403


def _find_calls(
    code: str,
    original: str,
    rel: str,
    aliases: Mapping[str, int | str],
    unresolved: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    lines = original.splitlines()
    calls: list[dict[str, Any]] = []
    occupied: set[tuple[int, int]] = set()

    def add_unresolved(kind: str, expression: str, source: SourceRef, reason: str) -> None:
        unresolved.append(
            {
                "id": _short_hash(f"{kind}|{expression}|{source.path}|{source.line}|{reason}"),
                "kind": kind,
                "expression": expression.strip()[:1000],
                "source": source.json(),
                "reason": reason,
            }
        )

    for pattern, explicit_namespace, fixed_receiver in _CALL_STARTS:
        for match in pattern.finditer(code):
            open_paren = match.end() - 1
            parsed = _balanced_call_argument(code, open_paren)
            if parsed is None:
                continue
            args_text, call_end = parsed
            if any(start <= match.start() < end for start, end in occupied):
                continue
            args = _split_arguments(original[open_paren + 1 : call_end - 1])
            method = match.group("method")
            namespace = _namespace_from_method(method, explicit_namespace)
            receiver = fixed_receiver or match.groupdict().get("receiver") or ""
            source = _source_ref(rel, original, lines, match.start())
            if not args or not args[0]:
                add_unresolved("storage-key", args_text, source, "Storage operation is missing its key argument")
                continue
            key = _resolve_storage_key(args[0], aliases)
            if key is None:
                add_unresolved("storage-key", args[0], source, "Storage key expression is dynamic")
                continue
            operation = {
                "id": _short_hash(f"op|{namespace}|{key}|{method.lower()}|{rel}|{source.line}|{match.start()}"),
                "namespace": namespace,
                "key": key,
                "nodeId": StorageRef(namespace, key).node_id,
                "operation": _operation_kind(method),
                "method": method,
                "receiver": receiver,
                "source": source.json(),
                "offset": match.start(),
                "rawArguments": [arg[:500] for arg in args],
            }
            if method.lower() == "getupdatedaccountstorage":
                operation["uncertainties"] = ["composite-player-and-account-storage-read"]
            if operation["operation"] in {"write", "delete"}:
                if operation["operation"] == "delete":
                    operation["valueKind"] = "delete"
                    operation["value"] = None
                elif len(args) < 2:
                    add_unresolved("storage-value", args_text, source, "Storage write is missing its value argument")
                    operation["valueKind"] = "dynamic"
                    operation["valueExpression"] = ""
                else:
                    literal = _literal_value(args[1], aliases)
                    if literal is not _DYNAMIC:
                        operation["valueKind"] = "literal"
                        operation["value"] = literal
                    else:
                        operation["valueKind"] = "dynamic"
                        operation["valueExpression"] = args[1].strip()[:1000]
            calls.append(operation)
            occupied.add((match.start(), call_end))

    for match in _SCOPED_KV_START.finditer(code):
        first_open = match.end() - 1
        first = _balanced_call_argument(code, first_open)
        if first is None:
            continue
        _, scoped_end = first
        tail = code[scoped_end : scoped_end + 80]
        tail_match = re.match(r"\s*:\s*(?P<method>get|set|remove)\s*\(", tail, re.I)
        if not tail_match:
            continue
        second_open = scoped_end + tail_match.end() - 1
        second = _balanced_call_argument(code, second_open)
        if second is None:
            continue
        _, call_end = second
        args1 = _split_arguments(original[first_open + 1 : scoped_end - 1])
        args2 = _split_arguments(original[second_open + 1 : call_end - 1])
        source = _source_ref(rel, original, lines, match.start())
        scope = _resolve_storage_key(args1[0], aliases) if args1 else None
        key = _resolve_storage_key(args2[0], aliases) if args2 else None
        if scope is None or key is None:
            add_unresolved("storage-key", original[match.start() : call_end], source, "Scoped KV scope/key is dynamic")
            continue
        combined = f"{scope}/{key}"
        method = tail_match.group("method")
        operation = {
            "id": _short_hash(f"op|player-kv|{combined}|{method.lower()}|{rel}|{source.line}|{match.start()}"),
            "namespace": "player-kv",
            "key": combined,
            "nodeId": StorageRef("player-kv", combined).node_id,
            "operation": _operation_kind(method),
            "method": f"scoped:{method}",
            "receiver": match.group("receiver"),
            "source": source.json(),
            "offset": match.start(),
            "rawArguments": [arg[:500] for arg in args1 + args2],
        }
        if operation["operation"] == "delete":
            operation["valueKind"] = "delete"
            operation["value"] = None
        elif operation["operation"] == "write":
            if len(args2) < 2:
                operation["valueKind"] = "dynamic"
                operation["valueExpression"] = ""
            else:
                literal = _literal_value(args2[1], aliases)
                if literal is _DYNAMIC:
                    operation["valueKind"] = "dynamic"
                    operation["valueExpression"] = args2[1].strip()[:1000]
                else:
                    operation["valueKind"] = "literal"
                    operation["value"] = literal
        calls.append(operation)

    for match in _DB_START.finditer(code):
        open_paren = match.end() - 1
        parsed = _balanced_call_argument(code, open_paren)
        if parsed is None:
            continue
        _, call_end = parsed
        argument = original[open_paren + 1 : call_end - 1].strip()
        source = _source_ref(rel, original, lines, match.start())
        literal = _literal_string(argument)
        if literal is None:
            if "storage" in argument.lower():
                add_unresolved("database-storage", argument, source, "Database storage query is dynamically constructed")
            continue
        lower = literal.lower()
        if "storage" not in lower:
            continue
        table = "player_storage" if "player_storage" in lower else "storage"
        key_match = re.search(r"(?:`?key`?)\s*=\s*(-?\d+)", literal, re.I)
        key: int | str = int(key_match.group(1)) if key_match else f"sql:{_short_hash(literal)}"
        verb = re.match(r"\s*(select|insert|update|delete|replace)", lower)
        op = "read" if verb and verb.group(1) == "select" else "write"
        calls.append(
            {
                "id": _short_hash(f"op|database|{key}|{op}|{rel}|{source.line}|{match.start()}"),
                "namespace": "database",
                "key": key,
                "nodeId": StorageRef("database", key).node_id,
                "operation": op,
                "method": f"db.{match.group('method')}",
                "receiver": "db",
                "source": source.json(),
                "offset": match.start(),
                "rawArguments": [argument[:500]],
                "databaseTable": table,
                "valueKind": "dynamic" if op == "write" else None,
                "uncertainties": ["sql-storage-semantics-not-executed"],
            }
        )

    calls.sort(key=lambda entry: (entry["offset"], entry["id"]))
    if len(calls) > MAX_OPERATIONS:
        raise StorageGraphError(f"Selected sources contain more than {MAX_OPERATIONS} storage operations")
    return calls


__all__ = [name for name in globals() if not name.startswith("__")]
