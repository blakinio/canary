from __future__ import annotations

from otbm_storage_graph_parser import *  # noqa: F403


def build_storage_graph(
    *,
    repository_root: Path,
    quest_evidence_path: Path,
    quest_validation_path: Path | None = None,
    spawn_evidence_path: Path | None = None,
    spawn_validation_path: Path | None = None,
    reachability_path: Path | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    if not isinstance(sample_limit, int) or isinstance(sample_limit, bool) or not 1 <= sample_limit <= MAX_SAMPLE_LIMIT:
        raise StorageGraphError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")
    quest_evidence = _load_json(quest_evidence_path, QUEST_EVIDENCE_FORMAT)
    quest_validation = _load_json(quest_validation_path, QUEST_VALIDATION_FORMAT) if quest_validation_path else None
    spawn_evidence = _load_json(spawn_evidence_path, SPAWN_EVIDENCE_FORMAT) if spawn_evidence_path else None
    spawn_validation = _load_json(spawn_validation_path, SPAWN_VALIDATION_FORMAT) if spawn_validation_path else None
    reachability = _load_json(reachability_path, REACHABILITY_FORMAT) if reachability_path else None
    if quest_validation is not None:
        sources = quest_validation.get("sources")
        evidence_digest = sources.get("evidenceDigest") if isinstance(sources, dict) else None
        if evidence_digest is not None and evidence_digest != quest_evidence.get("sourceDigest"):
            raise StorageGraphError("Quest validation evidence digest does not match Quest Map evidence")

    selected = _validate_selected_files(repository_root, quest_evidence)
    handlers, map_context, actors = _file_contexts(quest_evidence, quest_validation, spawn_evidence)

    operations: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    files: list[dict[str, Any]] = []
    branch_conditions_by_file: dict[str, list[tuple[BranchSpan, list[Condition]]]] = {}
    read_variables_by_file: dict[str, dict[str, StorageRef]] = {}
    aliases_by_file: dict[str, dict[str, int | str]] = {}

    for path, evidence_entry in selected:
        rel = evidence_entry["path"]
        if path.suffix.lower() != ".lua":
            files.append({"path": rel, "sha256": evidence_entry["sha256"], "operations": 0, "unresolved": 0, "language": path.suffix.lower().lstrip(".")})
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        code = _mask_comments_keep_strings(text)
        masked = _mask_comments_and_strings(text)
        aliases = _aliases(code)
        read_variables = _read_variable_refs(code, aliases)
        aliases_by_file[rel] = aliases
        read_variables_by_file[rel] = read_variables
        before_unresolved = len(unresolved)
        file_operations = _find_calls(code, text, rel, aliases, unresolved)
        branches = _if_branches(masked, text)
        lines = text.splitlines()
        branch_conditions: list[tuple[BranchSpan, list[Condition]]] = []
        for branch in branches:
            if branch.condition is None:
                branch_conditions.append((branch, []))
                continue
            parsed_conditions = _conditions_from_text(
                branch.condition,
                condition_offset=branch.condition_offset,
                original=text,
                rel=rel,
                lines=lines,
                aliases=aliases,
                read_variables=read_variables,
            )
            branch_conditions.append((branch, parsed_conditions))
        branch_conditions_by_file[rel] = branch_conditions
        operations.extend(file_operations)
        files.append(
            {
                "path": rel,
                "sha256": evidence_entry["sha256"],
                "operations": len(file_operations),
                "unresolved": len(unresolved) - before_unresolved,
                "language": "lua",
                "handlerContextCount": len(handlers.get(rel, [])),
                "mapContextCount": len(map_context.get(rel, [])),
                "actorContext": actors.get(rel),
            }
        )

    if len(operations) > MAX_OPERATIONS:
        raise StorageGraphError(f"Selected sources contain more than {MAX_OPERATIONS} storage operations")
    if len(unresolved) > MAX_UNRESOLVED:
        raise StorageGraphError(f"Selected sources contain more than {MAX_UNRESOLVED} unresolved expressions")

    for operation in operations:
        rel = operation["source"]["path"]
        offset = int(operation.pop("offset"))
        active_conditions: list[Condition] = []
        for branch, conditions in branch_conditions_by_file.get(rel, []):
            if branch.start <= offset < branch.end:
                active_conditions.extend(conditions)
        unique_conditions = {
            (condition.ref.canonical, condition.operator, _canonical_json(condition.value)): condition
            for condition in active_conditions
        }
        operation["conditions"] = [
            condition.json()
            for condition in sorted(
                unique_conditions.values(),
                key=lambda item: (item.ref.canonical, item.operator, _canonical_json(item.value)),
            )
        ]
        operation["handlerContext"] = handlers.get(rel, [])[:sample_limit]
        operation["handlerContextTruncated"] = len(handlers.get(rel, [])) > sample_limit
        operation["mapContext"] = map_context.get(rel, [])[:sample_limit]
        operation["mapContextTruncated"] = len(map_context.get(rel, [])) > sample_limit
        if rel in actors:
            operation["actorContext"] = actors[rel]
        if operation["operation"] == "write" and operation.get("valueKind") == "dynamic":
            target = StorageRef(operation["namespace"], operation["key"])
            expression = str(operation.get("valueExpression", ""))
            delta = _detect_delta(
                expression,
                target,
                aliases_by_file.get(rel, {}),
                read_variables_by_file.get(rel, {}),
            )
            if delta is not None:
                operation["operation"] = "increment" if delta > 0 else "decrement"
                operation["valueKind"] = "delta"
                operation["delta"] = delta
                operation.pop("valueExpression", None)
            else:
                source = operation["source"]
                unresolved.append(
                    {
                        "id": _short_hash(f"storage-value|{expression}|{source['path']}|{source['line']}"),
                        "kind": "storage-value",
                        "expression": expression[:1000],
                        "source": source,
                        "reason": "Storage value expression is dynamic",
                    }
                )

    for entry in quest_evidence.get("unresolved", []):
        if isinstance(entry, dict) and entry.get("kind") == "storage":
            unresolved.append(
                {
                    "id": f"phase2-{entry.get('id')}",
                    "kind": "storage-key",
                    "expression": str(entry.get("expression", ""))[:1000],
                    "source": entry.get("source"),
                    "reason": f"Phase 2: {entry.get('reason', 'unresolved storage expression')}",
                }
            )

    unresolved_by_id = {entry["id"]: entry for entry in unresolved if isinstance(entry.get("id"), str)}
    unresolved = sorted(
        unresolved_by_id.values(),
        key=lambda entry: (
            str(entry.get("kind")),
            str(entry.get("source", {}).get("path", "")),
            int(entry.get("source", {}).get("line", 0)),
            str(entry.get("expression", "")),
        ),
    )
    if len(unresolved) > MAX_UNRESOLVED:
        raise StorageGraphError(f"Selected sources contain more than {MAX_UNRESOLVED} unresolved expressions")

    operations.sort(
        key=lambda entry: (
            _NAMESPACE_ORDER.get(entry["namespace"], 99),
            _canonical_json(entry["key"]),
            str(entry["source"]["path"]),
            int(entry["source"]["line"]),
            entry["id"],
        )
    )

    node_operations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    refs: dict[str, StorageRef] = {}
    for operation in operations:
        ref = StorageRef(operation["namespace"], operation["key"])
        refs[ref.canonical] = ref
        node_operations[ref.canonical].append(operation)
    if len(refs) > MAX_NODES:
        raise StorageGraphError(f"Storage graph contains more than {MAX_NODES} nodes")

    transitions: list[dict[str, Any]] = []
    for operation in operations:
        if operation["operation"] not in {"write", "increment", "decrement", "delete"}:
            continue
        ref = StorageRef(operation["namespace"], operation["key"])
        exact_same = [
            condition
            for condition in operation.get("conditions", [])
            if condition.get("namespace") == ref.namespace
            and condition.get("key") == ref.key
            and condition.get("operator") == "=="
            and condition.get("exact") is True
        ]
        if len(exact_same) != 1:
            continue
        prerequisite = exact_same[0]["value"]
        result_kind = operation.get("valueKind")
        result_value: Any = operation.get("value")
        if result_kind == "delta":
            if not isinstance(prerequisite, int) or isinstance(prerequisite, bool):
                continue
            result_value = prerequisite + int(operation["delta"])
        elif result_kind not in {"literal", "delete"}:
            continue
        transition_id = _short_hash(
            f"transition|{ref.canonical}|{_canonical_json(prerequisite)}|{_canonical_json(result_value)}|{operation['id']}"
        )
        issues: list[str] = []
        if isinstance(prerequisite, int) and isinstance(result_value, int) and result_value < prerequisite:
            issues.append("backward-literal-transition")
        transitions.append(
            {
                "id": transition_id,
                **ref.json(),
                "prerequisite": {"operator": "==", "value": prerequisite},
                "result": {
                    "kind": "delete" if result_kind == "delete" else ("delta" if result_kind == "delta" else "literal"),
                    "value": result_value,
                    **({"delta": operation["delta"]} if result_kind == "delta" else {}),
                },
                "operationId": operation["id"],
                "source": operation["source"],
                "handlerContext": operation.get("handlerContext", []),
                "actorContext": operation.get("actorContext"),
                "mapContext": operation.get("mapContext", []),
                "confidence": "high",
                "issues": issues,
            }
        )
    if len(transitions) > MAX_TRANSITIONS:
        raise StorageGraphError(f"Storage graph contains more than {MAX_TRANSITIONS} transitions")
    transitions.sort(
        key=lambda edge: (
            edge["namespace"],
            _canonical_json(edge["key"]),
            _canonical_json(edge["prerequisite"]),
            _canonical_json(edge["result"]),
            edge["id"],
        )
    )

    findings: list[dict[str, Any]] = []
    finding_counts: Counter[str] = Counter()

    def finding(severity: str, code: str, message: str, **details: Any) -> None:
        finding_counts[code] += 1
        findings.append(
            {
                "id": _short_hash(f"finding|{code}|{_canonical_json(details)}"),
                "severity": severity,
                "code": code,
                "message": message,
                **details,
            }
        )

    nodes: list[dict[str, Any]] = []
    transition_by_ref: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in transitions:
        transition_by_ref[StorageRef(edge["namespace"], edge["key"]).canonical].append(edge)

    for canonical, ref in sorted(
        refs.items(),
        key=lambda item: (_NAMESPACE_ORDER.get(item[1].namespace, 99), _canonical_json(item[1].key)),
    ):
        values = node_operations[canonical]
        counts = Counter(operation["operation"] for operation in values)
        read_count = counts["read"]
        write_count = counts["write"] + counts["increment"] + counts["decrement"] + counts["delete"]
        status: list[str] = []
        if read_count and not write_count:
            status.append("external-or-unproven-writer")
            finding(
                "info",
                "storage_read_without_selected_writer",
                "Storage is read in the selected Phase 2 source set but no selected-scope writer was proven",
                namespace=ref.namespace,
                key=ref.key,
                nodeId=ref.node_id,
            )
        if write_count and not read_count:
            status.append("write-only-in-selected-scope")
            finding(
                "info",
                "storage_write_without_selected_read",
                "Storage is written in the selected Phase 2 source set but no selected-scope read was proven",
                namespace=ref.namespace,
                key=ref.key,
                nodeId=ref.node_id,
            )
        edges = transition_by_ref.get(canonical, [])
        prerequisites = {edge["prerequisite"]["value"] for edge in edges}
        produced = {edge["result"]["value"] for edge in edges}
        for prerequisite in sorted(prerequisites, key=_canonical_json):
            if prerequisite not in produced:
                finding(
                    "info",
                    "storage_prerequisite_unproven_in_selected_scope",
                    "An exact prerequisite value is consumed but not produced by another selected-scope explicit transition",
                    namespace=ref.namespace,
                    key=ref.key,
                    nodeId=ref.node_id,
                    value=prerequisite,
                )
        by_prerequisite: dict[str, set[str]] = defaultdict(set)
        for edge in edges:
            prerequisite_json = _canonical_json(edge["prerequisite"]["value"])
            result_json = _canonical_json(edge["result"]["value"])
            by_prerequisite[prerequisite_json].add(result_json)
            if "backward-literal-transition" in edge["issues"]:
                finding(
                    "warning",
                    "storage_backward_literal_transition",
                    "An explicit same-key transition writes a lower literal value",
                    namespace=ref.namespace,
                    key=ref.key,
                    nodeId=ref.node_id,
                    transitionId=edge["id"],
                    prerequisite=edge["prerequisite"]["value"],
                    result=edge["result"]["value"],
                    source=edge["source"],
                )
        for prerequisite, outputs in sorted(by_prerequisite.items()):
            if len(outputs) > 1:
                finding(
                    "warning",
                    "storage_conflicting_literal_writers",
                    "The same exact prerequisite has multiple incompatible literal outputs in selected sources",
                    namespace=ref.namespace,
                    key=ref.key,
                    nodeId=ref.node_id,
                    prerequisite=json.loads(prerequisite),
                    outputs=[json.loads(value) for value in sorted(outputs)],
                )
        nodes.append(
            {
                **ref.json(),
                "operationCounts": dict(sorted(counts.items())),
                "operationCount": len(values),
                "transitionCount": len(edges),
                "statuses": status,
                "sourceFiles": sorted({operation["source"]["path"] for operation in values}),
                "operationIds": [operation["id"] for operation in values],
                "transitionIds": [edge["id"] for edge in edges],
            }
        )

    for entry in unresolved:
        finding(
            "info",
            "storage_expression_unresolved",
            "A storage key or value expression could not be resolved statically",
            unresolvedId=entry["id"],
            kind=entry["kind"],
            source=entry.get("source"),
        )

    severity_order = {"error": 0, "warning": 1, "info": 2}
    findings.sort(
        key=lambda entry: (
            severity_order.get(entry["severity"], 99),
            entry["code"],
            str(entry.get("namespace", "")),
            _canonical_json(entry.get("key")),
            entry["id"],
        )
    )
    severity_counts = Counter(entry["severity"] for entry in findings)

    by_namespace = Counter(operation["namespace"] for operation in operations)
    by_operation = Counter(operation["operation"] for operation in operations)
    inputs: dict[str, Any] = {
        "questEvidence": _input_provenance(quest_evidence_path, quest_evidence),
        "questValidation": _input_provenance(quest_validation_path, quest_validation) if quest_validation_path and quest_validation else None,
        "spawnNpcEvidence": _input_provenance(spawn_evidence_path, spawn_evidence) if spawn_evidence_path and spawn_evidence else None,
        "spawnNpcValidation": _input_provenance(spawn_validation_path, spawn_validation) if spawn_validation_path and spawn_validation else None,
        "reachability": _input_provenance(reachability_path, reachability) if reachability_path and reachability else None,
    }
    source_digest = hashlib.sha256(
        _canonical_json(
            {
                "questSourceDigest": quest_evidence.get("sourceDigest"),
                "files": [{"path": entry["path"], "sha256": entry["sha256"]} for entry in files],
                "operations": [
                    {
                        key: value
                        for key, value in entry.items()
                        if key not in {"handlerContext", "mapContext", "actorContext"}
                    }
                    for entry in operations
                ],
                "transitions": transitions,
                "unresolved": unresolved,
            }
        ).encode("utf-8")
    ).hexdigest()

    report = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": severity_counts["error"] == 0,
        "complete": len(unresolved) == 0,
        "inputs": inputs,
        "sourceDigest": source_digest,
        "policy": {
            "dynamicLuaExecuted": False,
            "executionOrderInferred": False,
            "sourceSelectionExpanded": False,
            "selectedFilesHashVerified": True,
            "mapModified": False,
            "sampleLimit": sample_limit,
            "readWithoutWriterMeans": "external-or-unproven",
            "writeWithoutReadMeans": "write-only-in-selected-scope",
        },
        "summary": {
            "files": len(files),
            "operations": len(operations),
            "nodes": len(nodes),
            "transitions": len(transitions),
            "unresolved": len(unresolved),
            "findings": len(findings),
            "byNamespace": dict(
                sorted(by_namespace.items(), key=lambda item: (_NAMESPACE_ORDER.get(item[0], 99), item[0]))
            ),
            "byOperation": dict(sorted(by_operation.items())),
            "findingsBySeverity": {key: severity_counts.get(key, 0) for key in ("error", "warning", "info")},
            "findingsByCode": dict(sorted(finding_counts.items())),
        },
        "files": files,
        "nodes": nodes,
        "operations": operations,
        "transitions": transitions,
        "unresolved": unresolved[:sample_limit],
        "unresolvedTruncated": len(unresolved) > sample_limit,
        "findings": findings[:sample_limit],
        "findingsTruncated": len(findings) > sample_limit,
        "correlation": {
            "questValidationProvided": quest_validation is not None,
            "spawnNpcEvidenceProvided": spawn_evidence is not None,
            "spawnNpcValidationProvided": spawn_validation is not None,
            "reachabilityProvided": reachability is not None,
            "reachabilitySummary": reachability.get("summary") if reachability is not None else None,
            "spawnNpcValidationSummary": spawn_validation.get("summary") if spawn_validation is not None else None,
        },
        "notes": [
            "Explicit transition edges require one exact same-key equality prerequisite enclosing one literal/delete/delta write.",
            "Lexical order, nearby lines and source-file order are never treated as runtime execution order.",
            "Read-only/write-only and unproven prerequisite findings are selected-scope evidence, not automatic gameplay defects.",
            "Dynamic Lua, callbacks, database state and live player/account state are not executed or simulated.",
        ],
    }
    return report


def write_report(path: Path, report: Mapping[str, Any], *, overwrite: bool = False) -> None:
    target = path.expanduser()
    if target.is_symlink():
        raise StorageGraphError(f"Output must not be a symlink: {target}")
    destination = target.resolve()
    if destination.exists() and not destination.is_file():
        raise StorageGraphError(f"Output exists but is not a regular file: {destination}")
    if destination.exists() and not overwrite:
        raise StorageGraphError(f"Output already exists: {destination}; pass overwrite=True")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


__all__ = [name for name in globals() if not name.startswith("__")]
