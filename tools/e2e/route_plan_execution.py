from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Mapping, Sequence

ROUTE_PLAN_FORMAT = "canary-otbm-e2e-route-plan-v1"
ROUTE_PLAN_SCHEMA_VERSION = 1
INTERACTION_RESOLUTION_FORMAT = "canary-otbm-route-interaction-resolution-v1"
MAX_ROUTE_POSITIONS = 10_000
MAX_ROUTE_EDGES = 9_999
SUPPORTED_ACTIVATIONS = frozenset({"step-on", "walk-direction", "use-map-item", "use-inventory-on-map"})
SUPPORTED_DIRECTIONS = frozenset(
    {"north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"}
)
ROUTE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RoutePlanExecutionError(ValueError):
    pass


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RoutePlanExecutionError(f"{label} must be an object")
    return value


def _position(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 3:
        raise RoutePlanExecutionError(f"{label} must be a three-element [x, y, z] array")
    limits = (65535, 65535, 15)
    result: list[int] = []
    for index, maximum in enumerate(limits):
        coordinate = value[index]
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate <= maximum:
            raise RoutePlanExecutionError(f"{label}[{index}] is outside the OTBM coordinate range")
        result.append(coordinate)
    return result


def _uint16(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 65535:
        raise RoutePlanExecutionError(f"{label} must be an integer in the range 0..65535")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise RoutePlanExecutionError(f"{label} must be a lowercase 64-character SHA-256")
    return value


def _hashed_evidence(value: Any, label: str) -> str:
    evidence = _mapping(value, label)
    return _sha256(evidence.get("sha256"), f"{label}.sha256")


def _canonical_json_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _verify_plan_hash(plan: Mapping[str, Any], route_id: str) -> str:
    plan_hash = _sha256(plan.get("planHashSha256"), f"route {route_id}.planHashSha256")
    unhashed = dict(plan)
    unhashed.pop("planHashSha256", None)
    actual = _canonical_json_hash(unhashed)
    if actual != plan_hash:
        raise RoutePlanExecutionError(
            f"route {route_id!r} planHashSha256 mismatch: declared={plan_hash} actual={actual}"
        )
    return plan_hash


def _canonical_route_path(artifact_dir: Path, route_id: str) -> Path:
    if not ROUTE_ID_RE.fullmatch(route_id):
        raise RoutePlanExecutionError(f"route id must match {ROUTE_ID_RE.pattern}")
    directory = artifact_dir.resolve()
    candidate = (directory / f"route-{route_id}.json").resolve()
    if candidate.parent != directory:
        raise RoutePlanExecutionError(f"route {route_id!r} escaped the canonical artifact directory")
    return candidate


def _target_item_id(*, query: Mapping[str, Any], edge: Mapping[str, Any], label: str) -> int:
    if "itemId" in query:
        return _uint16(query["itemId"], f"{label}.selectorQuery.itemId")
    evidence = edge.get("evidence")
    transition = evidence.get("transition") if isinstance(evidence, Mapping) else None
    if isinstance(transition, Mapping):
        item_id = transition.get("itemId")
        if isinstance(item_id, int) and not isinstance(item_id, bool):
            return _uint16(item_id, f"{label}.evidence.transition.itemId")
        expected = transition.get("expectedItemIds")
        if isinstance(expected, list) and len(expected) == 1:
            return _uint16(expected[0], f"{label}.evidence.transition.expectedItemIds[0]")
    raise RoutePlanExecutionError(f"{label} cannot resolve one exact target item id")


def _normalize_interaction(
    resolution_value: Any,
    *,
    edge: Mapping[str, Any],
    edge_kind: str,
    label: str,
) -> dict[str, Any]:
    resolution = _mapping(resolution_value, label)
    if resolution.get("format") != INTERACTION_RESOLUTION_FORMAT or resolution.get("schemaVersion") != 1:
        raise RoutePlanExecutionError(f"{label} has an unsupported interaction resolution contract")
    if resolution.get("executionStatus") != "executable":
        raise RoutePlanExecutionError(f"{label} is not executable")
    blockers = resolution.get("blockers")
    if not isinstance(blockers, list) or blockers:
        raise RoutePlanExecutionError(f"{label} contains interaction blockers")
    activation = _mapping(resolution.get("activation"), f"{label}.activation")
    kind = activation.get("kind")
    if kind not in SUPPORTED_ACTIVATIONS:
        raise RoutePlanExecutionError(f"{label}.activation.kind is unsupported: {kind!r}")
    if edge_kind == "movement" and kind not in {"use-map-item", "use-inventory-on-map"}:
        raise RoutePlanExecutionError(f"{label}.activation.kind {kind!r} is invalid for a movement edge")

    normalized: dict[str, Any] = {"kind": kind}
    if kind == "walk-direction":
        direction = activation.get("direction")
        if direction not in SUPPORTED_DIRECTIONS:
            raise RoutePlanExecutionError(f"{label}.activation.direction is unsupported: {direction!r}")
        normalized["direction"] = direction
        return normalized
    if kind == "step-on":
        return normalized

    target = activation.get("target")
    query = _mapping(resolution.get("selectorQuery"), f"{label}.selectorQuery")
    if target == "transition-source":
        target_position = _position(edge.get("from"), f"{label}.edge.from")
    elif target == "selector-position":
        target_position = _position(query.get("position"), f"{label}.selectorQuery.position")
    elif target == "explicit-position":
        target_position = _position(activation.get("targetPosition"), f"{label}.activation.targetPosition")
    else:
        raise RoutePlanExecutionError(f"{label}.activation.target is unsupported: {target!r}")

    normalized["target_position"] = target_position
    normalized["target_item_id"] = _target_item_id(query=query, edge=edge, label=label)
    if kind == "use-inventory-on-map":
        normalized["inventory_item_id"] = _uint16(
            activation.get("inventoryItemId"), f"{label}.activation.inventoryItemId"
        )
    return normalized


def validate_route_plan(document: Any, *, route_id: str) -> dict[str, Any]:
    plan = _mapping(document, f"route {route_id}")
    if plan.get("format") != ROUTE_PLAN_FORMAT:
        raise RoutePlanExecutionError(f"route {route_id!r} has unsupported format {plan.get('format')!r}")
    if plan.get("schemaVersion") != ROUTE_PLAN_SCHEMA_VERSION:
        raise RoutePlanExecutionError(f"route {route_id!r} has unsupported schemaVersion {plan.get('schemaVersion')!r}")
    plan_hash = _verify_plan_hash(plan, route_id)
    if plan.get("executionStatus") != "executable":
        raise RoutePlanExecutionError(f"route {route_id!r} executionStatus must be executable")
    routing_mode = plan.get("routingMode")
    if routing_mode not in {"strict", "executable"}:
        raise RoutePlanExecutionError(
            f"route {route_id!r} routingMode must be strict or executable; optimistic routes are not physically executable"
        )
    if plan.get("pathComplete") is not True:
        raise RoutePlanExecutionError(f"route {route_id!r} pathComplete must be true")
    blockers = plan.get("blockers")
    if not isinstance(blockers, list) or blockers:
        raise RoutePlanExecutionError(f"route {route_id!r} must contain no blockers")

    provenance = _mapping(plan.get("provenance"), f"route {route_id}.provenance")
    for key in ("map", "worldIndex", "appearances"):
        _hashed_evidence(provenance.get(key), f"route {route_id}.provenance.{key}")
    if routing_mode == "executable":
        _hashed_evidence(provenance.get("interactionRegistry"), f"route {route_id}.provenance.interactionRegistry")

    path = plan.get("path")
    edges = plan.get("edges")
    if not isinstance(path, list) or not 1 <= len(path) <= MAX_ROUTE_POSITIONS:
        raise RoutePlanExecutionError(f"route {route_id!r} path must contain 1..{MAX_ROUTE_POSITIONS} positions")
    if not isinstance(edges, list) or len(edges) > MAX_ROUTE_EDGES:
        raise RoutePlanExecutionError(f"route {route_id!r} edges must contain at most {MAX_ROUTE_EDGES} entries")
    distance = plan.get("distance")
    if not isinstance(distance, int) or isinstance(distance, bool) or distance != len(edges):
        raise RoutePlanExecutionError(f"route {route_id!r} distance must equal its executable edge count")
    positions = [_position(value, f"route {route_id}.path[{index}]") for index, value in enumerate(path)]
    origin = _position(plan.get("origin"), f"route {route_id}.origin")
    destination = _position(plan.get("destination"), f"route {route_id}.destination")
    if positions[0] != origin or positions[-1] != destination:
        raise RoutePlanExecutionError(f"route {route_id!r} path endpoints do not match origin/destination")
    if len(edges) != len(positions) - 1:
        raise RoutePlanExecutionError(f"route {route_id!r} edge count does not match its complete path")

    normalized_edges: list[dict[str, Any]] = []
    route_requires_interactions = False
    for index, edge_value in enumerate(edges):
        label = f"route {route_id}.edges[{index}]"
        edge = _mapping(edge_value, label)
        source = _position(edge.get("from"), f"{label}.from")
        target = _position(edge.get("to"), f"{label}.to")
        if source != positions[index] or target != positions[index + 1]:
            raise RoutePlanExecutionError(f"{label} does not match path continuity")
        edge_kind = edge.get("kind")
        if edge_kind not in {"movement", "transition"}:
            raise RoutePlanExecutionError(f"{label}.kind is unsupported: {edge_kind!r}")
        execution_blockers = edge.get("executionBlockers", [])
        if not isinstance(execution_blockers, list) or execution_blockers:
            raise RoutePlanExecutionError(f"{label} contains execution blockers")
        interactions_value = edge.get("interactions", [])
        if not isinstance(interactions_value, list):
            raise RoutePlanExecutionError(f"{label}.interactions must be an array")

        if edge_kind == "movement":
            if edge.get("isTransition") is not False or edge.get("transitionId") is not None:
                raise RoutePlanExecutionError(f"{label} has inconsistent movement edge metadata")
            if source[2] != target[2]:
                raise RoutePlanExecutionError(f"{label} movement edge changes floor")
            dx, dy = target[0] - source[0], target[1] - source[1]
            if (dx, dy) == (0, 0) or abs(dx) > 1 or abs(dy) > 1:
                raise RoutePlanExecutionError(f"{label} is not one adjacent movement edge")
        else:
            if edge.get("isTransition") is not True or not isinstance(edge.get("transitionId"), str) or not edge["transitionId"]:
                raise RoutePlanExecutionError(f"{label} has inconsistent transition edge metadata")
            if len(interactions_value) != 1:
                raise RoutePlanExecutionError(f"{label} must contain exactly one executable transition interaction")
            route_requires_interactions = True

        if interactions_value:
            route_requires_interactions = True
        interactions = [
            _normalize_interaction(
                value,
                edge=edge,
                edge_kind=edge_kind,
                label=f"{label}.interactions[{interaction_index}]",
            )
            for interaction_index, value in enumerate(interactions_value)
        ]
        normalized_edges.append(
            {
                "index": index + 1,
                "kind": edge_kind,
                "from": source,
                "to": target,
                "transition_id": edge.get("transitionId"),
                "interactions": interactions,
            }
        )

    if route_requires_interactions and routing_mode != "executable":
        raise RoutePlanExecutionError(f"route {route_id!r} contains interaction edges outside executable routing mode")
    return {
        "id": route_id,
        "plan_hash_sha256": plan_hash,
        "origin": origin,
        "destination": destination,
        "edges": normalized_edges,
    }


def load_route_plans(steps: Sequence[Mapping[str, Any]], artifact_dir: Path | None) -> dict[str, dict[str, Any]]:
    route_ids = sorted({str(step["route"]) for step in steps if step.get("action") == "follow_route"})
    if not route_ids:
        return {}
    if artifact_dir is None:
        raise RoutePlanExecutionError("follow_route materialization requires the canonical artifact directory")
    result: dict[str, dict[str, Any]] = {}
    for route_id in route_ids:
        path = _canonical_route_path(artifact_dir, route_id)
        if not path.is_file():
            raise RoutePlanExecutionError(f"canonical route artifact is missing for {route_id!r}: {path.name}")
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RoutePlanExecutionError(f"cannot read canonical route artifact {path.name}: {exc}") from exc
        result[route_id] = validate_route_plan(document, route_id=route_id)
    return result


def _lua_string(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return '"' + escaped + '"'


def _lua_value(value: Any, indent: int = 0) -> str:
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _lua_string(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        if not value:
            return "{}"
        child_indent = indent + 2
        entries = [" " * child_indent + _lua_value(item, child_indent) + "," for item in value]
        return "{\n" + "\n".join(entries) + "\n" + " " * indent + "}"
    if isinstance(value, Mapping):
        if not value:
            return "{}"
        child_indent = indent + 2
        entries = []
        for key in sorted(value):
            entries.append(
                " " * child_indent
                + f"[{_lua_string(str(key))}] = "
                + _lua_value(value[key], child_indent)
                + ","
            )
        return "{\n" + "\n".join(entries) + "\n" + " " * indent + "}"
    raise RoutePlanExecutionError(f"unsupported Lua route value type: {type(value).__name__}")


def render_routes_lua(routes: Mapping[str, Mapping[str, Any]], *, indent: int = 2) -> str:
    return _lua_value(routes, indent)


def materialize_client_executor(artifact_dir: Path) -> Path:
    source = Path(__file__).resolve().parent / "client" / "agent_e2e_route.lua"
    if not source.is_file():
        raise RoutePlanExecutionError(f"route executor source is missing: {source}")
    target = artifact_dir.resolve() / "agent-e2e-route.lua"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target
