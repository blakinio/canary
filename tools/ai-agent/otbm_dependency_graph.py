from __future__ import annotations

import hashlib
import json
import re
from collections import deque
from typing import Any, Mapping, Sequence

MANIFEST_FORMAT = "canary-otbm-dependency-graph-manifest-v1"
REPORT_FORMAT = "canary-otbm-dependency-blast-radius-v1"
WORLD_HEALTH_FORMAT = "canary-otbm-world-health-v1"
REGRESSION_FORMAT = "canary-otbm-map-change-regression-v1"
COVERAGE_FORMAT = "canary-otbm-coverage-dashboard-v1"
SCHEMA_VERSION = 1

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
NODE_KINDS = {
    "tile",
    "item",
    "mechanic",
    "action-id",
    "unique-id",
    "house-door",
    "teleport",
    "transition",
    "script-handler",
    "storage",
    "landmark",
    "route",
    "quest",
    "coverage-target",
    "scenario",
}
RELATIONS = {
    "depends-on",
    "references",
    "guards",
    "routes-through",
    "activates",
    "produces",
    "consumes",
    "covers",
    "validates",
    "affected-by",
}
MAX_QUERY_DEPTH = 256


class DependencyGraphError(ValueError):
    """Raised when reviewed dependency evidence cannot be composed safely."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise DependencyGraphError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise DependencyGraphError(f"{label} must be an array")
    return value


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DependencyGraphError(f"{label} must be a non-empty string")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise DependencyGraphError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _pin(value: Any, label: str, expected_format: str) -> dict[str, Any]:
    pin = _mapping(value, label)
    if pin.get("format") != expected_format:
        raise DependencyGraphError(f"{label}.format must be {expected_format}")
    size = pin.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise DependencyGraphError(f"{label}.size must be a non-negative integer")
    return {
        "fileName": _nonempty_string(pin.get("fileName"), f"{label}.fileName"),
        "size": size,
        "sha256": _sha256(pin.get("sha256"), f"{label}.sha256"),
        "format": expected_format,
    }


def _world_health_identity(report: Mapping[str, Any]) -> tuple[str, str | None]:
    if report.get("format") != WORLD_HEALTH_FORMAT or report.get("schemaVersion") != 1:
        raise DependencyGraphError(f"World Health must use {WORLD_HEALTH_FORMAT} schemaVersion 1")
    source = _mapping(report.get("source"), "worldHealth.source")
    map_sha = _sha256(source.get("mapSha256"), "worldHealth.source.mapSha256")
    world_sha = source.get("worldIndexSha256")
    if world_sha is not None:
        world_sha = _sha256(world_sha, "worldHealth.source.worldIndexSha256")
    return map_sha, world_sha


def _regression_identity(report: Mapping[str, Any]) -> dict[str, str]:
    if report.get("format") != REGRESSION_FORMAT or report.get("schemaVersion") != 1:
        raise DependencyGraphError(f"Regression Guard must use {REGRESSION_FORMAT} schemaVersion 1")
    source = _mapping(report.get("source"), "regressionGuard.source")
    return {
        "beforeMapSha256": _sha256(source.get("beforeMapSha256"), "regressionGuard.source.beforeMapSha256"),
        "afterMapSha256": _sha256(source.get("afterMapSha256"), "regressionGuard.source.afterMapSha256"),
        "beforeWorldIndexSha256": _sha256(
            source.get("beforeWorldIndexSha256"),
            "regressionGuard.source.beforeWorldIndexSha256",
        ),
        "afterWorldIndexSha256": _sha256(
            source.get("afterWorldIndexSha256"),
            "regressionGuard.source.afterWorldIndexSha256",
        ),
    }


def _coverage_identity(report: Mapping[str, Any]) -> tuple[str, str]:
    if report.get("format") != COVERAGE_FORMAT or report.get("schemaVersion") != 1:
        raise DependencyGraphError(f"Coverage Dashboard must use {COVERAGE_FORMAT} schemaVersion 1")
    current = _mapping(report.get("currentMap"), "coverageDashboard.currentMap")
    return (
        _sha256(current.get("mapSha256"), "coverageDashboard.currentMap.mapSha256"),
        _sha256(current.get("worldIndexSha256"), "coverageDashboard.currentMap.worldIndexSha256"),
    )


def _unescape_pointer_token(token: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(token):
        char = token[index]
        if char != "~":
            result.append(char)
            index += 1
            continue
        if index + 1 >= len(token) or token[index + 1] not in {"0", "1"}:
            raise DependencyGraphError("JSON Pointer contains an invalid escape")
        result.append("~" if token[index + 1] == "0" else "/")
        index += 2
    return "".join(result)


def _resolve_pointer(document: Any, pointer: str) -> tuple[bool, Any, str | None]:
    if pointer == "":
        return True, document, None
    if not pointer.startswith("/"):
        return False, None, "EVIDENCE_POINTER_INVALID"
    current = document
    try:
        tokens = [_unescape_pointer_token(token) for token in pointer[1:].split("/")]
    except DependencyGraphError:
        return False, None, "EVIDENCE_POINTER_INVALID"
    for token in tokens:
        if isinstance(current, Mapping):
            if token not in current:
                return False, None, "EVIDENCE_POINTER_NOT_FOUND"
            current = current[token]
        elif isinstance(current, list):
            if token == "-" or not token.isdigit():
                return False, None, "EVIDENCE_POINTER_NOT_FOUND"
            index = int(token)
            if index >= len(current):
                return False, None, "EVIDENCE_POINTER_NOT_FOUND"
            current = current[index]
        else:
            return False, None, "EVIDENCE_POINTER_NOT_FOUND"
    return True, current, None


def _subset(actual: Any, expected: Any) -> bool:
    if isinstance(expected, Mapping):
        if not isinstance(actual, Mapping):
            return False
        return all(key in actual and _subset(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return actual == expected
    return actual == expected


def _evaluate_evidence_ref(
    value: Any,
    *,
    label: str,
    report_by_sha: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    ref = _mapping(value, label)
    report_sha = _sha256(ref.get("reportSha256"), f"{label}.reportSha256")
    pointer = ref.get("pointer")
    if not isinstance(pointer, str):
        raise DependencyGraphError(f"{label}.pointer must be a string")
    expectation = ref.get("expectation")
    normalized_expectation: dict[str, Any] | None = None
    if expectation is not None:
        expectation_object = _mapping(expectation, f"{label}.expectation")
        mode = expectation_object.get("mode")
        if mode not in {"equals", "subset"}:
            raise DependencyGraphError(f"{label}.expectation.mode must be equals or subset")
        if "value" not in expectation_object:
            raise DependencyGraphError(f"{label}.expectation.value is required")
        normalized_expectation = {"mode": mode, "value": expectation_object["value"]}

    if report_sha not in report_by_sha:
        return {
            "reportSha256": report_sha,
            "pointer": pointer,
            "expectation": normalized_expectation,
            "state": "unresolved",
            "blockers": ["EVIDENCE_REPORT_NOT_SUPPLIED"],
        }

    found, actual, pointer_error = _resolve_pointer(report_by_sha[report_sha], pointer)
    if not found:
        return {
            "reportSha256": report_sha,
            "pointer": pointer,
            "expectation": normalized_expectation,
            "state": "unresolved",
            "blockers": [pointer_error or "EVIDENCE_POINTER_NOT_FOUND"],
        }

    blockers: list[str] = []
    if normalized_expectation is not None:
        expected = normalized_expectation["value"]
        if normalized_expectation["mode"] == "equals":
            matched = actual == expected
        else:
            matched = _subset(actual, expected)
        if not matched:
            blockers.append("EVIDENCE_EXPECTATION_MISMATCH")

    return {
        "reportSha256": report_sha,
        "pointer": pointer,
        "expectation": normalized_expectation,
        "state": "proven" if not blockers else "unresolved",
        "blockers": blockers,
    }


def _normalize_manifest(
    manifest: Mapping[str, Any],
    *,
    current_map_sha: str,
    current_world_index_sha: str,
    report_by_sha: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if manifest.get("format") != MANIFEST_FORMAT or manifest.get("schemaVersion") != 1:
        raise DependencyGraphError(f"manifest must use {MANIFEST_FORMAT} schemaVersion 1")
    source = _mapping(manifest.get("source"), "manifest.source")
    if _sha256(source.get("mapSha256"), "manifest.source.mapSha256") != current_map_sha:
        raise DependencyGraphError("manifest source map does not match the current Regression Guard after-map")
    manifest_world = source.get("worldIndexSha256")
    if manifest_world is not None and _sha256(
        manifest_world,
        "manifest.source.worldIndexSha256",
    ) != current_world_index_sha:
        raise DependencyGraphError("manifest World Index does not match the current Regression Guard after-index")

    raw_nodes = _array(manifest.get("nodes"), "manifest.nodes")
    nodes: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    for index, raw_node in enumerate(raw_nodes):
        node = _mapping(raw_node, f"manifest.nodes[{index}]")
        node_id = _nonempty_string(node.get("id"), f"manifest.nodes[{index}].id")
        if node_id in node_ids:
            raise DependencyGraphError(f"duplicate dependency node id: {node_id}")
        node_ids.add(node_id)
        kind = node.get("kind")
        if kind not in NODE_KINDS:
            raise DependencyGraphError(f"manifest.nodes[{index}].kind is unsupported: {kind!r}")
        selector = _mapping(node.get("selector"), f"manifest.nodes[{index}].selector")
        review_state = node.get("reviewState", "reviewed")
        if review_state not in {"reviewed", "ambiguous"}:
            raise DependencyGraphError(f"manifest.nodes[{index}].reviewState must be reviewed or ambiguous")
        raw_refs = _array(node.get("evidence", []), f"manifest.nodes[{index}].evidence")
        refs = [
            _evaluate_evidence_ref(
                ref,
                label=f"manifest.nodes[{index}].evidence[{ref_index}]",
                report_by_sha=report_by_sha,
            )
            for ref_index, ref in enumerate(raw_refs)
        ]
        blockers: list[str] = []
        if review_state == "ambiguous":
            blockers.append("NODE_DECLARED_AMBIGUOUS")
        if not refs:
            blockers.append("NODE_EVIDENCE_MISSING")
        for ref in refs:
            blockers.extend(ref["blockers"])
        nodes.append(
            {
                "id": node_id,
                "kind": kind,
                "selector": dict(selector),
                "reviewState": review_state,
                "state": "proven" if not blockers else "unresolved",
                "blockers": sorted(set(blockers)),
                "evidence": refs,
            }
        )

    node_by_id = {node["id"]: node for node in nodes}
    raw_edges = _array(manifest.get("edges"), "manifest.edges")
    edges: list[dict[str, Any]] = []
    edge_ids: set[str] = set()
    for index, raw_edge in enumerate(raw_edges):
        edge = _mapping(raw_edge, f"manifest.edges[{index}]")
        edge_id = _nonempty_string(edge.get("id"), f"manifest.edges[{index}].id")
        if edge_id in edge_ids:
            raise DependencyGraphError(f"duplicate dependency edge id: {edge_id}")
        edge_ids.add(edge_id)
        source_id = _nonempty_string(edge.get("source"), f"manifest.edges[{index}].source")
        target_id = _nonempty_string(edge.get("target"), f"manifest.edges[{index}].target")
        if source_id not in node_by_id or target_id not in node_by_id:
            raise DependencyGraphError(f"manifest.edges[{index}] references an unknown node")
        relation = edge.get("relation")
        if relation not in RELATIONS:
            raise DependencyGraphError(f"manifest.edges[{index}].relation is unsupported: {relation!r}")
        review_state = edge.get("reviewState", "reviewed")
        if review_state not in {"reviewed", "ambiguous"}:
            raise DependencyGraphError(f"manifest.edges[{index}].reviewState must be reviewed or ambiguous")
        raw_refs = _array(edge.get("evidence", []), f"manifest.edges[{index}].evidence")
        refs = [
            _evaluate_evidence_ref(
                ref,
                label=f"manifest.edges[{index}].evidence[{ref_index}]",
                report_by_sha=report_by_sha,
            )
            for ref_index, ref in enumerate(raw_refs)
        ]
        blockers: list[str] = []
        if review_state == "ambiguous":
            blockers.append("EDGE_DECLARED_AMBIGUOUS")
        if node_by_id[source_id]["state"] != "proven":
            blockers.append("SOURCE_NODE_UNPROVEN")
        if node_by_id[target_id]["state"] != "proven":
            blockers.append("TARGET_NODE_UNPROVEN")
        if not refs:
            blockers.append("EDGE_EVIDENCE_MISSING")
        for ref in refs:
            blockers.extend(ref["blockers"])
        edges.append(
            {
                "id": edge_id,
                "source": source_id,
                "target": target_id,
                "relation": relation,
                "reviewState": review_state,
                "state": "proven" if not blockers else "unresolved",
                "blockers": sorted(set(blockers)),
                "evidence": refs,
            }
        )

    raw_queries = _array(manifest.get("queries"), "manifest.queries")
    queries: list[dict[str, Any]] = []
    query_ids: set[str] = set()
    for index, raw_query in enumerate(raw_queries):
        query = _mapping(raw_query, f"manifest.queries[{index}]")
        query_id = _nonempty_string(query.get("id"), f"manifest.queries[{index}].id")
        if query_id in query_ids:
            raise DependencyGraphError(f"duplicate dependency query id: {query_id}")
        query_ids.add(query_id)
        roots = _array(query.get("roots"), f"manifest.queries[{index}].roots")
        if not roots:
            raise DependencyGraphError(f"manifest.queries[{index}].roots must not be empty")
        normalized_roots: list[str] = []
        for root_index, root in enumerate(roots):
            root_id = _nonempty_string(root, f"manifest.queries[{index}].roots[{root_index}]")
            if root_id not in node_by_id:
                raise DependencyGraphError(f"manifest.queries[{index}] references unknown root node {root_id}")
            normalized_roots.append(root_id)
        if len(set(normalized_roots)) != len(normalized_roots):
            raise DependencyGraphError(f"manifest.queries[{index}].roots contains duplicates")
        max_depth = query.get("maxDepth", MAX_QUERY_DEPTH)
        if isinstance(max_depth, bool) or not isinstance(max_depth, int) or not 1 <= max_depth <= MAX_QUERY_DEPTH:
            raise DependencyGraphError(f"manifest.queries[{index}].maxDepth must be in 1..{MAX_QUERY_DEPTH}")
        queries.append({"id": query_id, "roots": sorted(normalized_roots), "maxDepth": max_depth})

    nodes.sort(key=lambda item: (item["kind"], item["id"]))
    edges.sort(key=lambda item: (item["source"], item["target"], item["relation"], item["id"]))
    queries.sort(key=lambda item: item["id"])
    return nodes, edges, queries


def _query_report(
    query: Mapping[str, Any],
    *,
    node_by_id: Mapping[str, Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    proven_adjacency: dict[str, list[Mapping[str, Any]]] = {}
    unresolved_outgoing: dict[str, list[Mapping[str, Any]]] = {}
    for edge in edges:
        target = proven_adjacency if edge["state"] == "proven" else unresolved_outgoing
        target.setdefault(str(edge["source"]), []).append(edge)
    for mapping in (proven_adjacency, unresolved_outgoing):
        for source in mapping:
            mapping[source] = sorted(mapping[source], key=lambda item: (item["target"], item["relation"], item["id"]))

    roots = list(query["roots"])
    proven_roots = [root for root in roots if node_by_id[root]["state"] == "proven"]
    unresolved_roots = [root for root in roots if node_by_id[root]["state"] != "proven"]
    max_depth = int(query["maxDepth"])

    best: dict[str, tuple[int, tuple[str, ...], tuple[str, ...]]] = {}
    queue: deque[tuple[str, int, tuple[str, ...], tuple[str, ...]]] = deque()
    for root in sorted(proven_roots):
        best[root] = (0, (root,), ())
        queue.append((root, 0, (root,), ()))

    while queue:
        current, depth, path_nodes, path_edges = queue.popleft()
        if depth >= max_depth:
            continue
        for edge in proven_adjacency.get(current, []):
            target = str(edge["target"])
            candidate_depth = depth + 1
            candidate_nodes = path_nodes + (target,)
            candidate_edges = path_edges + (str(edge["id"]),)
            existing = best.get(target)
            candidate_key = (candidate_depth, candidate_nodes, candidate_edges)
            if existing is None or candidate_key < existing:
                best[target] = candidate_key
                queue.append((target, candidate_depth, candidate_nodes, candidate_edges))

    root_set = set(roots)
    impacts: list[dict[str, Any]] = []
    for node_id, (depth, path_nodes, path_edges) in best.items():
        if node_id in root_set:
            continue
        impacts.append(
            {
                "nodeId": node_id,
                "nodeKind": node_by_id[node_id]["kind"],
                "depth": depth,
                "pathNodeIds": list(path_nodes),
                "pathEdgeIds": list(path_edges),
            }
        )
    impacts.sort(key=lambda item: (item["depth"], item["nodeKind"], item["nodeId"], item["pathEdgeIds"]))
    direct = [item for item in impacts if item["depth"] == 1]

    reachable_sources = set(best)
    boundaries: list[dict[str, Any]] = []
    for source in sorted(reachable_sources):
        for edge in unresolved_outgoing.get(source, []):
            boundaries.append(
                {
                    "edgeId": edge["id"],
                    "source": edge["source"],
                    "target": edge["target"],
                    "relation": edge["relation"],
                    "blockers": list(edge["blockers"]),
                }
            )
    boundaries.sort(key=lambda item: (item["source"], item["target"], item["relation"], item["edgeId"]))

    return {
        "id": query["id"],
        "roots": roots,
        "maxDepth": max_depth,
        "provenRootNodeIds": sorted(proven_roots),
        "unresolvedRootNodeIds": sorted(unresolved_roots),
        "directImpacts": direct,
        "transitiveImpacts": impacts,
        "unresolvedBoundaries": boundaries,
        "summary": {
            "rootCount": len(roots),
            "provenRootCount": len(proven_roots),
            "unresolvedRootCount": len(unresolved_roots),
            "directImpactCount": len(direct),
            "transitiveImpactCount": len(impacts),
            "unresolvedBoundaryCount": len(boundaries),
            "depthLimitReached": any(item["depth"] == max_depth for item in impacts)
            and any(proven_adjacency.get(item["nodeId"]) for item in impacts if item["depth"] == max_depth),
        },
    }


def build_dependency_graph_report(
    *,
    manifest: Mapping[str, Any],
    world_health: Mapping[str, Any],
    regression_guard: Mapping[str, Any],
    coverage_dashboard: Mapping[str, Any] | None = None,
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    pins = _mapping(input_pins, "input_pins")
    manifest_pin = _pin(pins.get("manifest"), "input_pins.manifest", MANIFEST_FORMAT)
    world_pin = _pin(pins.get("worldHealth"), "input_pins.worldHealth", WORLD_HEALTH_FORMAT)
    regression_pin = _pin(pins.get("regressionGuard"), "input_pins.regressionGuard", REGRESSION_FORMAT)
    coverage_pin: dict[str, Any] | None = None
    if coverage_dashboard is not None:
        coverage_pin = _pin(pins.get("coverageDashboard"), "input_pins.coverageDashboard", COVERAGE_FORMAT)
    elif pins.get("coverageDashboard") is not None:
        raise DependencyGraphError("coverage dashboard pin supplied without a coverage dashboard report")

    hashes = [manifest_pin["sha256"], world_pin["sha256"], regression_pin["sha256"]]
    if coverage_pin is not None:
        hashes.append(coverage_pin["sha256"])
    if len(hashes) != len(set(hashes)):
        raise DependencyGraphError("all dependency graph input SHA-256 pins must be distinct")

    world_object = _mapping(world_health, "world_health")
    regression_object = _mapping(regression_guard, "regression_guard")
    current_map_sha, world_index_sha = _world_health_identity(world_object)
    regression_identity = _regression_identity(regression_object)
    if regression_identity["afterMapSha256"] != current_map_sha:
        raise DependencyGraphError("World Health source map must equal Regression Guard after-map")
    current_world_index_sha = regression_identity["afterWorldIndexSha256"]
    if world_index_sha is not None and world_index_sha != current_world_index_sha:
        raise DependencyGraphError("World Health World Index must equal Regression Guard after-index when present")

    report_by_sha: dict[str, Mapping[str, Any]] = {
        world_pin["sha256"]: world_object,
        regression_pin["sha256"]: regression_object,
    }
    provenance: dict[str, Any] = {
        "manifest": manifest_pin,
        "worldHealth": world_pin,
        "regressionGuard": regression_pin,
        "coverageDashboard": None,
    }
    if coverage_dashboard is not None and coverage_pin is not None:
        coverage_object = _mapping(coverage_dashboard, "coverage_dashboard")
        coverage_map, coverage_world = _coverage_identity(coverage_object)
        if coverage_map != current_map_sha or coverage_world != current_world_index_sha:
            raise DependencyGraphError("Coverage Dashboard must prove the same current map and World Index")
        report_by_sha[coverage_pin["sha256"]] = coverage_object
        provenance["coverageDashboard"] = coverage_pin

    manifest_object = _mapping(manifest, "manifest")
    nodes, edges, queries = _normalize_manifest(
        manifest_object,
        current_map_sha=current_map_sha,
        current_world_index_sha=current_world_index_sha,
        report_by_sha=report_by_sha,
    )
    node_by_id = {node["id"]: node for node in nodes}
    query_reports = [_query_report(query, node_by_id=node_by_id, edges=edges) for query in queries]

    unresolved_nodes = [node for node in nodes if node["state"] != "proven"]
    unresolved_edges = [edge for edge in edges if edge["state"] != "proven"]
    all_boundaries = [
        {
            "edgeId": edge["id"],
            "source": edge["source"],
            "target": edge["target"],
            "relation": edge["relation"],
            "blockers": list(edge["blockers"]),
        }
        for edge in unresolved_edges
    ]

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "source": {
            "beforeMapSha256": regression_identity["beforeMapSha256"],
            "currentMapSha256": current_map_sha,
            "beforeWorldIndexSha256": regression_identity["beforeWorldIndexSha256"],
            "currentWorldIndexSha256": current_world_index_sha,
            "worldHealthWorldIndexPresent": world_index_sha is not None,
        },
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "otbmParsedIndependently": False,
            "scriptResolutionRecomputed": False,
            "storageGraphRecomputed": False,
            "pathfindingExecuted": False,
            "routePlanningExecuted": False,
            "physicalE2eSelectionRecomputed": False,
            "physicalE2eExecuted": False,
            "dependencyEdgesInferred": False,
            "unprovenEdgesTraversed": False,
            "selectedScopeAbsenceMeansGlobalAbsence": False,
            "scenarioPrioritizationDirected": False,
        },
        "provenance": provenance,
        "summary": {
            "nodeCount": len(nodes),
            "provenNodeCount": len(nodes) - len(unresolved_nodes),
            "unresolvedNodeCount": len(unresolved_nodes),
            "edgeCount": len(edges),
            "provenEdgeCount": len(edges) - len(unresolved_edges),
            "unresolvedEdgeCount": len(unresolved_edges),
            "queryCount": len(query_reports),
            "coverageDashboardPresent": coverage_dashboard is not None,
        },
        "nodes": nodes,
        "edges": edges,
        "unresolvedBoundaries": sorted(
            all_boundaries,
            key=lambda item: (item["source"], item["target"], item["relation"], item["edgeId"]),
        ),
        "queries": query_reports,
        "notes": [
            "Every dependency node and edge is explicitly reviewed in the manifest; this tool never infers domain relationships.",
            "Evidence references are resolved only against exact supplied report SHA-256 pins and JSON Pointers.",
            "Only proven directed edges contribute to direct or transitive blast radius; unresolved boundaries are surfaced separately.",
            "Transitive impacts use deterministic shortest proven paths and do not authorize E2E scenario prioritization, repair, mutation or certification.",
        ],
    }


def canonical_report_sha256(report: Mapping[str, Any]) -> str:
    encoded = json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
