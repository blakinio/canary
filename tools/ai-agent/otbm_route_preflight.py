#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from otbm_reachability import (
    _load_world_manifest,
    _manifest_source_sha256,
    export_route_plan_index_path,
    write_report,
)
from otbm_reachability_analysis import ROUTE_PLAN_FORMAT, ROUTE_PLAN_SCHEMA_VERSION
from otbm_reachability_types import ReachabilityError
from otbm_route_interactions import ACTIVATION_KINDS, FAIL_CLOSED_SCRIPT_STATUSES
from otbm_semantic_landmarks import SemanticLandmarkError, resolve_landmark_anchor
from otbm_world_index import sha256_path

PREFLIGHT_FORMAT = "canary-otbm-e2e-route-preflight-v1"
PREFLIGHT_SCHEMA_VERSION = 1
MAX_ROUTE_POSITIONS = 10_000
MAX_ROUTE_EDGES = 9_999
DEFAULT_MAX_FINDINGS = 200
MAX_FINDINGS = 10_000
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

_PROVENANCE_KEYS = (
    "map",
    "worldIndex",
    "appearances",
    "transitionManifest",
    "scriptResolution",
    "interactionRegistry",
)
_REQUIRED_PROVENANCE_KEYS = ("map", "worldIndex", "appearances")
_ROUTE_SIGNATURE_KEYS = (
    "origin",
    "destination",
    "routingBounds",
    "routingOptions",
    "routeStatus",
    "executionStatus",
    "routingMode",
    "distance",
    "strictDistance",
    "optimisticDistance",
    "executableDistance",
    "pathComplete",
    "path",
    "edges",
    "blockers",
)


class RoutePreflightError(ValueError):
    pass


class _Findings:
    def __init__(self, limit: int) -> None:
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_FINDINGS:
            raise RoutePreflightError(f"max_findings must be in 1..{MAX_FINDINGS}")
        self.limit = limit
        self.total = 0
        self.by_code: Counter[str] = Counter()
        self.samples: list[dict[str, Any]] = []
        self.first: dict[str, Any] | None = None

    def block(self, code: str, message: str, **details: Any) -> None:
        finding = {"severity": "error", "code": code, "message": message, **copy.deepcopy(details)}
        self.total += 1
        self.by_code[code] += 1
        if self.first is None:
            self.first = copy.deepcopy(finding)
        if len(self.samples) < self.limit:
            self.samples.append(finding)

    def finish(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "byCode": dict(sorted(self.by_code.items())),
            "truncated": self.total > len(self.samples),
        }


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RoutePreflightError(f"{label} must be an object")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise RoutePreflightError(f"{label} must be a lowercase 64-character SHA-256")
    return value


def _position(value: Any, label: str) -> tuple[int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise RoutePreflightError(f"{label} must be a three-element [x, y, z] array")
    limits = (0xFFFF, 0xFFFF, 15)
    result: list[int] = []
    for index, maximum in enumerate(limits):
        coordinate = value[index]
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate <= maximum:
            raise RoutePreflightError(f"{label}[{index}] is outside the OTBM coordinate range")
        result.append(coordinate)
    return result[0], result[1], result[2]


def _canonical_json_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _evidence_hash(provenance: Mapping[str, Any], key: str) -> str | None:
    value = provenance.get(key)
    if value is None:
        return None
    if not isinstance(value, Mapping):
        return None
    raw = value.get("sha256")
    return raw if isinstance(raw, str) and _SHA256_RE.fullmatch(raw) is not None else None


def _plan_signature(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(plan.get(key)) for key in _ROUTE_SIGNATURE_KEYS}


def _classify_landmark_error(exc: SemanticLandmarkError) -> str:
    message = str(exc).lower()
    if "unknown semantic landmark" in message or "has no" in message:
        return "LANDMARK_NOT_FOUND"
    if "ambiguous" in message:
        return "LANDMARK_AMBIGUOUS"
    if "sha-256" in message or "unbound" in message or "provenance" in message:
        return "LANDMARK_STALE"
    return "LANDMARK_STALE"


def _validate_landmark_request(
    *,
    plan: Mapping[str, Any],
    registry: Mapping[str, Any],
    request: Mapping[str, Any],
    map_sha256: str,
    world_index_sha256: str,
    findings: _Findings,
) -> dict[str, Any] | None:
    try:
        origin_request = _mapping(request.get("from"), "landmarkRequest.from")
        destination_request = _mapping(request.get("to"), "landmarkRequest.to")
        origin_id = origin_request.get("landmarkId")
        destination_id = destination_request.get("landmarkId")
        if not isinstance(origin_id, str) or not origin_id:
            raise RoutePreflightError("landmarkRequest.from.landmarkId must be a non-empty string")
        if not isinstance(destination_id, str) or not destination_id:
            raise RoutePreflightError("landmarkRequest.to.landmarkId must be a non-empty string")

        origin_anchor = origin_request.get("anchorId")
        destination_anchor = destination_request.get("anchorId")
        if origin_anchor is not None and (not isinstance(origin_anchor, str) or not origin_anchor):
            raise RoutePreflightError("landmarkRequest.from.anchorId must be a non-empty string when supplied")
        if destination_anchor is not None and (not isinstance(destination_anchor, str) or not destination_anchor):
            raise RoutePreflightError("landmarkRequest.to.anchorId must be a non-empty string when supplied")

        origin_resolution = resolve_landmark_anchor(
            registry,
            landmark_id=origin_id,
            anchor_id=origin_anchor,
            role=None if origin_anchor is not None else "route-origin",
            expected_source_map_sha256=map_sha256,
            expected_world_index_sha256=world_index_sha256,
        )
        destination_resolution = resolve_landmark_anchor(
            registry,
            landmark_id=destination_id,
            anchor_id=destination_anchor,
            role=None if destination_anchor is not None else "route-destination",
            expected_source_map_sha256=map_sha256,
            expected_world_index_sha256=world_index_sha256,
        )
    except SemanticLandmarkError as exc:
        findings.block(_classify_landmark_error(exc), "Semantic landmark request no longer resolves exactly", error=str(exc))
        return None
    except RoutePreflightError as exc:
        findings.block("LANDMARK_REQUEST_INVALID", "Semantic landmark request is invalid", error=str(exc))
        return None

    if origin_resolution["regionId"] != destination_resolution["regionId"]:
        findings.block(
            "ROUTING_REGION_INVALID",
            "Semantic route endpoints no longer resolve to one common routing region",
            originRegion=origin_resolution["regionId"],
            destinationRegion=destination_resolution["regionId"],
        )

    expected_bounds = origin_resolution["routingBounds"]
    if destination_resolution["routingBounds"] != expected_bounds:
        findings.block(
            "ROUTING_REGION_INVALID",
            "Semantic route endpoint resolutions disagree on routing bounds",
            originBounds=expected_bounds,
            destinationBounds=destination_resolution["routingBounds"],
        )
    if plan.get("routingBounds") != expected_bounds:
        findings.block(
            "ROUTING_REGION_INVALID",
            "Route-plan routing bounds no longer match the reviewed semantic region",
            expected=expected_bounds,
            actual=plan.get("routingBounds"),
        )

    origin_position = origin_resolution["anchor"]["position"]
    destination_position = destination_resolution["anchor"]["position"]
    if plan.get("origin") != origin_position:
        findings.block(
            "LANDMARK_STALE",
            "Route-plan origin no longer matches the reviewed semantic anchor",
            expected=origin_position,
            actual=plan.get("origin"),
        )
    if plan.get("destination") != destination_position:
        findings.block(
            "LANDMARK_STALE",
            "Route-plan destination no longer matches the reviewed semantic anchor",
            expected=destination_position,
            actual=plan.get("destination"),
        )

    return {
        "from": origin_resolution,
        "to": destination_resolution,
    }


def _validate_interaction(
    resolution_value: Any,
    *,
    edge_index: int,
    interaction_index: int,
    findings: _Findings,
) -> None:
    label = f"edges[{edge_index}].interactions[{interaction_index}]"
    if not isinstance(resolution_value, Mapping):
        findings.block("INTERACTION_STALE", "Route edge interaction resolution is not an object", location=label)
        return
    resolution = resolution_value
    if resolution.get("format") != "canary-otbm-route-interaction-resolution-v1" or resolution.get("schemaVersion") != 1:
        findings.block("INTERACTION_STALE", "Route edge interaction uses an unsupported resolution contract", location=label)
    if resolution.get("executionStatus") != "executable":
        findings.block("INTERACTION_STALE", "Route edge interaction is not executable", location=label)
    blockers = resolution.get("blockers")
    if not isinstance(blockers, list) or blockers:
        findings.block("INTERACTION_STALE", "Route edge interaction contains blockers", location=label, blockers=blockers)

    query = resolution.get("selectorQuery")
    if isinstance(query, Mapping):
        script_status = query.get("scriptStatus")
        if script_status in FAIL_CLOSED_SCRIPT_STATUSES:
            findings.block(
                "SCRIPT_RESOLUTION_BLOCKED",
                "Route edge interaction carries fail-closed Script Resolution evidence",
                location=label,
                status=script_status,
            )

    activation = resolution.get("activation")
    if not isinstance(activation, Mapping):
        findings.block("INTERACTION_UNSUPPORTED", "Executable route interaction is missing activation semantics", location=label)
        return
    activation_kind = activation.get("kind")
    if activation_kind not in ACTIVATION_KINDS:
        findings.block(
            "INTERACTION_UNSUPPORTED",
            "Route edge interaction activation is not supported by Universal E2E v1",
            location=label,
            activation=activation_kind,
        )


def _validate_plan_structure(plan: Mapping[str, Any], findings: _Findings) -> dict[str, Any] | None:
    if plan.get("format") != ROUTE_PLAN_FORMAT:
        findings.block("ROUTE_PLAN_INVALID", "Unsupported route-plan format", actual=plan.get("format"))
    if plan.get("schemaVersion") != ROUTE_PLAN_SCHEMA_VERSION:
        findings.block("ROUTE_PLAN_INVALID", "Unsupported route-plan schema version", actual=plan.get("schemaVersion"))

    declared_hash = plan.get("planHashSha256")
    if not isinstance(declared_hash, str) or _SHA256_RE.fullmatch(declared_hash) is None:
        findings.block("ROUTE_PLAN_HASH_MISMATCH", "Route plan has no valid planHashSha256")
    else:
        unhashed = dict(plan)
        unhashed.pop("planHashSha256", None)
        actual_hash = _canonical_json_hash(unhashed)
        if actual_hash != declared_hash:
            findings.block(
                "ROUTE_PLAN_HASH_MISMATCH",
                "Route plan canonical hash does not match planHashSha256",
                declared=declared_hash,
                actual=actual_hash,
            )

    if plan.get("executionStatus") != "executable":
        findings.block("ROUTE_INCOMPLETE", "Route plan executionStatus must be executable", actual=plan.get("executionStatus"))
    routing_mode = plan.get("routingMode")
    if routing_mode not in {"strict", "executable"}:
        findings.block(
            "ROUTE_INCOMPLETE",
            "Physical route preflight accepts only strict or interaction-aware executable routing",
            actual=routing_mode,
        )
    if plan.get("pathComplete") is not True:
        findings.block("ROUTE_TRUNCATED", "Executable route plan must contain a complete path")
    blockers = plan.get("blockers")
    if not isinstance(blockers, list) or blockers:
        findings.block("ROUTE_INCOMPLETE", "Executable route plan must contain no blockers", blockers=blockers)

    try:
        origin = _position(plan.get("origin"), "origin")
        destination = _position(plan.get("destination"), "destination")
    except RoutePreflightError as exc:
        findings.block("ROUTE_PLAN_INVALID", "Route plan has invalid endpoints", error=str(exc))
        return None

    path_value = plan.get("path")
    edges_value = plan.get("edges")
    if not isinstance(path_value, list) or not 1 <= len(path_value) <= MAX_ROUTE_POSITIONS:
        findings.block("ROUTE_INCOMPLETE", f"Route path must contain 1..{MAX_ROUTE_POSITIONS} positions")
        return None
    if not isinstance(edges_value, list) or len(edges_value) > MAX_ROUTE_EDGES:
        findings.block("ROUTE_INCOMPLETE", f"Route edges must contain at most {MAX_ROUTE_EDGES} entries")
        return None

    positions: list[tuple[int, int, int]] = []
    for index, value in enumerate(path_value):
        try:
            positions.append(_position(value, f"path[{index}]"))
        except RoutePreflightError as exc:
            findings.block("ROUTE_PLAN_INVALID", "Route path contains an invalid position", index=index, error=str(exc))
            return None

    if positions[0] != origin or positions[-1] != destination:
        findings.block(
            "ROUTE_INCOMPLETE",
            "Route path endpoints do not match origin and destination",
            origin=list(origin),
            destination=list(destination),
        )
    if len(edges_value) != len(positions) - 1:
        findings.block(
            "ROUTE_INCOMPLETE",
            "Route edge count does not match complete path length",
            pathPositions=len(positions),
            edgeCount=len(edges_value),
        )
    distance = plan.get("distance")
    if not isinstance(distance, int) or isinstance(distance, bool) or distance != len(edges_value):
        findings.block("ROUTE_INCOMPLETE", "Route distance must equal edge count", distance=distance, edgeCount=len(edges_value))

    routing_options = plan.get("routingOptions")
    if not isinstance(routing_options, Mapping):
        findings.block("ROUTE_PLAN_INVALID", "routingOptions must be an object")
        allow_diagonal = False
    else:
        allow_diagonal = routing_options.get("allowDiagonal") is True
        if routing_options.get("diagonalCornerCutting") is not False:
            findings.block("DIAGONAL_CORNER_BLOCKED", "Route plan must preserve no-corner-cutting semantics")

    route_requires_interactions = False
    for index, edge_value in enumerate(edges_value):
        if index + 1 >= len(positions):
            break
        if not isinstance(edge_value, Mapping):
            findings.block("ROUTE_PLAN_INVALID", "Route edge must be an object", edgeIndex=index)
            continue
        edge = edge_value
        try:
            source = _position(edge.get("from"), f"edges[{index}].from")
            target = _position(edge.get("to"), f"edges[{index}].to")
        except RoutePreflightError as exc:
            findings.block("ROUTE_PLAN_INVALID", "Route edge contains invalid coordinates", edgeIndex=index, error=str(exc))
            continue
        if source != positions[index] or target != positions[index + 1]:
            findings.block(
                "ROUTE_INCOMPLETE",
                "Route edge does not match path continuity",
                edgeIndex=index,
                expectedFrom=list(positions[index]),
                expectedTo=list(positions[index + 1]),
                actualFrom=list(source),
                actualTo=list(target),
            )

        execution_blockers = edge.get("executionBlockers", [])
        if not isinstance(execution_blockers, list) or execution_blockers:
            findings.block(
                "ROUTE_INCOMPLETE",
                "Route edge contains execution blockers",
                edgeIndex=index,
                blockers=execution_blockers,
            )
        interactions = edge.get("interactions", [])
        if not isinstance(interactions, list):
            findings.block("INTERACTION_STALE", "Route edge interactions must be an array", edgeIndex=index)
            interactions = []
        for interaction_index, resolution in enumerate(interactions):
            route_requires_interactions = True
            _validate_interaction(
                resolution,
                edge_index=index,
                interaction_index=interaction_index,
                findings=findings,
            )

        edge_kind = edge.get("kind")
        if edge_kind == "movement":
            if edge.get("isTransition") is not False or edge.get("transitionId") is not None:
                findings.block("MOVEMENT_EDGE_INVALID", "Movement edge has inconsistent transition metadata", edgeIndex=index)
            if source[2] != target[2]:
                findings.block("MOVEMENT_EDGE_INVALID", "Movement edge changes floor", edgeIndex=index)
            dx = target[0] - source[0]
            dy = target[1] - source[1]
            if (dx, dy) == (0, 0) or abs(dx) > 1 or abs(dy) > 1:
                findings.block("MOVEMENT_EDGE_INVALID", "Movement edge is not one adjacent tile", edgeIndex=index)
            elif abs(dx) == 1 and abs(dy) == 1 and not allow_diagonal:
                findings.block("DIAGONAL_NOT_ALLOWED", "Route contains a diagonal edge while allowDiagonal is false", edgeIndex=index)

            evidence = edge.get("evidence")
            if not isinstance(evidence, Mapping) or evidence.get("source") != "reachability-bfs-predecessor" or evidence.get("edgeSource") != "_movement_neighbors":
                findings.block("MOVEMENT_EDGE_INVALID", "Movement edge is not traceable to canonical Reachability neighbors", edgeIndex=index)
        elif edge_kind == "transition":
            transition_id = edge.get("transitionId")
            if edge.get("isTransition") is not True or not isinstance(transition_id, str) or not transition_id:
                findings.block("TRANSITION_STALE", "Transition edge has inconsistent transition metadata", edgeIndex=index)
            if len(interactions) != 1:
                findings.block(
                    "INTERACTION_UNSUPPORTED",
                    "Executable transition edge must contain exactly one reviewed executable interaction",
                    edgeIndex=index,
                    interactionCount=len(interactions),
                )
            route_requires_interactions = True
            evidence = edge.get("evidence")
            transition = evidence.get("transition") if isinstance(evidence, Mapping) else None
            if not isinstance(evidence, Mapping) or evidence.get("source") != "validated-transition-edge":
                findings.block("TRANSITION_STALE", "Transition edge is not traceable to validated transition evidence", edgeIndex=index)
            if not isinstance(transition, Mapping):
                findings.block("TRANSITION_STALE", "Transition edge is missing validated transition state", edgeIndex=index)
            else:
                if transition.get("id") != transition_id:
                    findings.block("TRANSITION_STALE", "Transition ID no longer matches embedded evidence", edgeIndex=index)
                if transition.get("source") != list(source) or transition.get("destination") != list(target):
                    findings.block(
                        "TRANSITION_STALE",
                        "Transition source/destination does not match the route edge",
                        edgeIndex=index,
                        transitionId=transition_id,
                    )
                if transition.get("valid") is not True:
                    findings.block("TRANSITION_STALE", "Transition is not valid in embedded evidence", edgeIndex=index, transitionId=transition_id)
                script_status = transition.get("scriptStatus")
                if script_status in FAIL_CLOSED_SCRIPT_STATUSES:
                    findings.block(
                        "SCRIPT_RESOLUTION_BLOCKED",
                        "Transition carries fail-closed Script Resolution evidence",
                        edgeIndex=index,
                        transitionId=transition_id,
                        status=script_status,
                    )
        else:
            findings.block("ROUTE_PLAN_INVALID", "Route edge kind is unsupported", edgeIndex=index, kind=edge_kind)

    if route_requires_interactions and routing_mode != "executable":
        findings.block("INTERACTION_UNSUPPORTED", "Route uses interactions outside interaction-aware executable routing mode")

    return {
        "origin": origin,
        "destination": destination,
        "path": positions,
        "edges": edges_value,
        "allowDiagonal": allow_diagonal,
    }


def _compare_current_plan(plan: Mapping[str, Any], current_plan: Mapping[str, Any], findings: _Findings) -> None:
    if current_plan.get("executionStatus") != "executable" or current_plan.get("pathComplete") is not True:
        findings.block(
            "ROUTE_NOT_CURRENTLY_EXECUTABLE",
            "Canonical Reachability no longer produces an executable complete route under current evidence",
            executionStatus=current_plan.get("executionStatus"),
            blockers=current_plan.get("blockers"),
        )

    if _plan_signature(plan) == _plan_signature(current_plan):
        return

    current_transitions = {
        edge.get("transitionId"): edge
        for edge in current_plan.get("edges", [])
        if isinstance(edge, Mapping) and edge.get("kind") == "transition" and isinstance(edge.get("transitionId"), str)
    }
    stale_transition = False
    for edge in plan.get("edges", []):
        if not isinstance(edge, Mapping) or edge.get("kind") != "transition":
            continue
        transition_id = edge.get("transitionId")
        current = current_transitions.get(transition_id)
        if current is None or current.get("from") != edge.get("from") or current.get("to") != edge.get("to"):
            findings.block(
                "TRANSITION_STALE",
                "Current canonical transition route no longer contains the planned transition edge",
                transitionId=transition_id,
                plannedFrom=edge.get("from"),
                plannedTo=edge.get("to"),
            )
            stale_transition = True
            continue
        planned_evidence = edge.get("evidence")
        current_evidence = current.get("evidence")
        planned_transition = planned_evidence.get("transition") if isinstance(planned_evidence, Mapping) else None
        current_transition = current_evidence.get("transition") if isinstance(current_evidence, Mapping) else None
        if planned_transition != current_transition:
            findings.block(
                "TRANSITION_STALE",
                "Current validated transition evidence differs from the route plan",
                transitionId=transition_id,
            )
            stale_transition = True

    if not stale_transition:
        findings.block(
            "ROUTE_CURRENT_EVIDENCE_MISMATCH",
            "Canonical Reachability regeneration differs from the supplied route plan",
            plannedPlanHash=plan.get("planHashSha256"),
            currentPlanHash=current_plan.get("planHashSha256"),
        )


def preflight_route_plan(
    document: Any,
    *,
    runtime_evidence: Mapping[str, str | None],
    current_plan: Mapping[str, Any] | None = None,
    current_plan_error: Mapping[str, Any] | None = None,
    landmark_registry: Mapping[str, Any] | None = None,
    landmark_request: Mapping[str, Any] | None = None,
    max_findings: int = DEFAULT_MAX_FINDINGS,
) -> dict[str, Any]:
    findings = _Findings(max_findings)
    plan = dict(document) if isinstance(document, Mapping) else {}
    if not isinstance(document, Mapping):
        findings.block("ROUTE_PLAN_INVALID", "Route plan must be a JSON object")

    normalized_runtime: dict[str, str | None] = {}
    for key in _PROVENANCE_KEYS:
        value = runtime_evidence.get(key)
        if value is None:
            normalized_runtime[key] = None
            continue
        try:
            normalized_runtime[key] = _sha256(value, f"runtimeEvidence.{key}")
        except RoutePreflightError as exc:
            findings.block("ROUTE_PROVENANCE_MISMATCH", "Runtime evidence hash is invalid", evidence=key, error=str(exc))
            normalized_runtime[key] = None
    landmark_registry_hash = runtime_evidence.get("landmarkRegistry")
    if landmark_registry_hash is not None:
        try:
            normalized_runtime["landmarkRegistry"] = _sha256(landmark_registry_hash, "runtimeEvidence.landmarkRegistry")
        except RoutePreflightError as exc:
            findings.block("LANDMARK_STALE", "Landmark registry hash is invalid", error=str(exc))
            normalized_runtime["landmarkRegistry"] = None

    structure = _validate_plan_structure(plan, findings)

    provenance_value = plan.get("provenance")
    if not isinstance(provenance_value, Mapping):
        findings.block("ROUTE_PROVENANCE_MISMATCH", "Route plan provenance must be an object")
        provenance: Mapping[str, Any] = {}
    else:
        provenance = provenance_value

    for key in _REQUIRED_PROVENANCE_KEYS:
        declared = _evidence_hash(provenance, key)
        if declared is None:
            findings.block("ROUTE_PROVENANCE_MISMATCH", "Executable route plan is missing required provenance", evidence=key)
    for key in _PROVENANCE_KEYS:
        declared = _evidence_hash(provenance, key)
        if declared is None:
            if provenance.get(key) is not None:
                findings.block("ROUTE_PROVENANCE_MISMATCH", "Route plan contains malformed provenance", evidence=key)
            continue
        actual = normalized_runtime.get(key)
        if actual is None:
            findings.block(
                "ROUTE_PROVENANCE_MISMATCH",
                "Route plan references evidence that was not supplied to preflight",
                evidence=key,
                expected=declared,
            )
        elif actual != declared:
            findings.block(
                "ROUTE_PROVENANCE_MISMATCH",
                "Route plan evidence hash does not match current runtime evidence",
                evidence=key,
                expected=declared,
                actual=actual,
            )

    landmark_resolution = None
    if landmark_request is not None:
        if landmark_registry is None:
            findings.block("LANDMARK_STALE", "Semantic landmark request requires the reviewed landmark registry")
        elif normalized_runtime.get("map") is not None and normalized_runtime.get("worldIndex") is not None:
            landmark_resolution = _validate_landmark_request(
                plan=plan,
                registry=landmark_registry,
                request=landmark_request,
                map_sha256=str(normalized_runtime["map"]),
                world_index_sha256=str(normalized_runtime["worldIndex"]),
                findings=findings,
            )

    if current_plan_error is not None:
        findings.block(
            str(current_plan_error.get("code", "ROUTE_CURRENT_EVIDENCE_MISMATCH")),
            str(current_plan_error.get("message", "Current exact-map evidence could not be validated")),
            **{key: value for key, value in current_plan_error.items() if key not in {"code", "message"}},
        )
    elif current_plan is not None and structure is not None:
        _compare_current_plan(plan, current_plan, findings)

    summary = findings.finish()
    status = "passed" if summary["total"] == 0 else "blocked"
    return {
        "format": PREFLIGHT_FORMAT,
        "schemaVersion": PREFLIGHT_SCHEMA_VERSION,
        "status": status,
        "ok": status == "passed",
        "staticEvidenceOnly": True,
        "planHashSha256": plan.get("planHashSha256") if isinstance(plan.get("planHashSha256"), str) else None,
        "runtimeEvidence": normalized_runtime,
        "landmarkResolution": landmark_resolution,
        "firstBlocker": findings.first,
        "findings": findings.samples,
        "summary": summary,
    }


def _load_json(path: Path, label: str) -> dict[str, Any]:
    candidate = path.expanduser().resolve()
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    try:
        document = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RoutePreflightError(f"Cannot read {label} {candidate}: {exc}") from exc
    if not isinstance(document, dict):
        raise RoutePreflightError(f"{label} must contain a JSON object")
    return document


def preflight_index_paths(
    *,
    route_plan_path: Path,
    runtime_map_path: Path,
    index_path: Path,
    appearances_path: Path,
    world_manifest_path: Path,
    transitions_path: Path | None = None,
    script_resolution_path: Path | None = None,
    interaction_registry_path: Path | None = None,
    landmark_registry_path: Path | None = None,
    landmark_request_path: Path | None = None,
    max_findings: int = DEFAULT_MAX_FINDINGS,
) -> dict[str, Any]:
    plan = _load_json(route_plan_path, "route plan")
    runtime_map = runtime_map_path.expanduser().resolve()
    world_index = index_path.expanduser().resolve()
    appearances = appearances_path.expanduser().resolve()
    if not runtime_map.is_file():
        raise FileNotFoundError(runtime_map)
    if not world_index.is_file():
        raise FileNotFoundError(world_index)
    if not appearances.is_file():
        raise FileNotFoundError(appearances)

    runtime_evidence: dict[str, str | None] = {
        "map": sha256_path(runtime_map),
        "worldIndex": sha256_path(world_index),
        "appearances": sha256_path(appearances),
        "transitionManifest": sha256_path(transitions_path.expanduser().resolve()) if transitions_path is not None else None,
        "scriptResolution": sha256_path(script_resolution_path.expanduser().resolve()) if script_resolution_path is not None else None,
        "interactionRegistry": sha256_path(interaction_registry_path.expanduser().resolve()) if interaction_registry_path is not None else None,
    }

    landmark_registry = _load_json(landmark_registry_path, "semantic landmark registry") if landmark_registry_path else None
    landmark_request = _load_json(landmark_request_path, "semantic landmark request") if landmark_request_path else None
    if landmark_registry_path is not None:
        runtime_evidence["landmarkRegistry"] = sha256_path(landmark_registry_path.expanduser().resolve())

    base_result = preflight_route_plan(
        plan,
        runtime_evidence=runtime_evidence,
        landmark_registry=landmark_registry,
        landmark_request=landmark_request,
        max_findings=max_findings,
    )
    if not base_result["ok"]:
        return base_result

    index_hash = str(runtime_evidence["worldIndex"])
    try:
        manifest = _load_world_manifest(world_index, world_manifest_path.expanduser().resolve(), index_hash)
    except (FileNotFoundError, OSError, ReachabilityError) as exc:
        return preflight_route_plan(
            plan,
            runtime_evidence=runtime_evidence,
            current_plan_error={
                "code": "WORLD_INDEX_MANIFEST_INVALID",
                "message": "World Index manifest is missing, invalid, or does not match the exact index",
                "error": str(exc),
            },
            landmark_registry=landmark_registry,
            landmark_request=landmark_request,
            max_findings=max_findings,
        )
    if manifest is None:
        return preflight_route_plan(
            plan,
            runtime_evidence=runtime_evidence,
            current_plan_error={
                "code": "WORLD_INDEX_MANIFEST_INVALID",
                "message": "Exact-map route preflight requires a World Index provenance manifest",
            },
            landmark_registry=landmark_registry,
            landmark_request=landmark_request,
            max_findings=max_findings,
        )
    manifest_map_hash = _manifest_source_sha256(manifest)
    if manifest_map_hash != runtime_evidence["map"]:
        return preflight_route_plan(
            plan,
            runtime_evidence=runtime_evidence,
            current_plan_error={
                "code": "ROUTE_PROVENANCE_MISMATCH",
                "message": "World Index manifest source-map SHA-256 does not match the exact runtime map",
                "manifestMapSha256": manifest_map_hash,
                "runtimeMapSha256": runtime_evidence["map"],
            },
            landmark_registry=landmark_registry,
            landmark_request=landmark_request,
            max_findings=max_findings,
        )

    try:
        bounds = _mapping(plan.get("routingBounds"), "routingBounds")
        lower = _position(bounds.get("from"), "routingBounds.from")
        upper = _position(bounds.get("to"), "routingBounds.to")
        origin = _position(plan.get("origin"), "origin")
        destination = _position(plan.get("destination"), "destination")
        options = _mapping(plan.get("routingOptions"), "routingOptions")
        allow_diagonal = options.get("allowDiagonal") is True
        max_positions = options.get("maxExecutablePositions")
        if not isinstance(max_positions, int) or isinstance(max_positions, bool) or not 1 <= max_positions <= MAX_ROUTE_POSITIONS:
            raise RoutePreflightError(f"routingOptions.maxExecutablePositions must be in 1..{MAX_ROUTE_POSITIONS}")

        provenance = _mapping(plan.get("provenance"), "provenance")
        current_plan = export_route_plan_index_path(
            index_path=world_index,
            appearances_path=appearances,
            lower=lower,
            upper=upper,
            origin=origin,
            destination=destination,
            transitions_path=(transitions_path if _evidence_hash(provenance, "transitionManifest") is not None else None),
            script_resolution_path=(
                script_resolution_path if _evidence_hash(provenance, "scriptResolution") is not None else None
            ),
            interaction_registry_path=(
                interaction_registry_path if _evidence_hash(provenance, "interactionRegistry") is not None else None
            ),
            world_manifest_path=world_manifest_path,
            allow_diagonal=allow_diagonal,
            max_positions=max_positions,
        )
    except (FileNotFoundError, OSError, ReachabilityError, RoutePreflightError) as exc:
        return preflight_route_plan(
            plan,
            runtime_evidence=runtime_evidence,
            current_plan_error={
                "code": "ROUTE_NOT_CURRENTLY_EXECUTABLE",
                "message": "Canonical Reachability could not regenerate the route under current exact-map evidence",
                "error": str(exc),
            },
            landmark_registry=landmark_registry,
            landmark_request=landmark_request,
            max_findings=max_findings,
        )

    return preflight_route_plan(
        plan,
        runtime_evidence=runtime_evidence,
        current_plan=current_plan,
        landmark_registry=landmark_registry,
        landmark_request=landmark_request,
        max_findings=max_findings,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fail-closed exact-map static preflight for executable OTBM E2E route plans")
    parser.add_argument("--route-plan", type=Path, required=True)
    parser.add_argument("--runtime-map", type=Path, required=True)
    parser.add_argument("--world-index", type=Path, required=True)
    parser.add_argument("--appearances", type=Path, required=True)
    parser.add_argument("--world-index-manifest", type=Path, required=True)
    parser.add_argument("--transitions", type=Path)
    parser.add_argument("--script-resolution", type=Path)
    parser.add_argument("--interaction-registry", type=Path)
    parser.add_argument("--landmark-registry", type=Path)
    parser.add_argument("--landmark-request", type=Path)
    parser.add_argument("--max-findings", type=int, default=DEFAULT_MAX_FINDINGS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    if (args.landmark_registry is None) != (args.landmark_request is None):
        sys.stderr.write("error: --landmark-registry and --landmark-request must be supplied together\n")
        return 2
    try:
        result = preflight_index_paths(
            route_plan_path=args.route_plan,
            runtime_map_path=args.runtime_map,
            index_path=args.world_index,
            appearances_path=args.appearances,
            world_manifest_path=args.world_index_manifest,
            transitions_path=args.transitions,
            script_resolution_path=args.script_resolution,
            interaction_registry_path=args.interaction_registry,
            landmark_registry_path=args.landmark_registry,
            landmark_request_path=args.landmark_request,
            max_findings=args.max_findings,
        )
        if args.output is not None:
            write_report(args.output, result, overwrite=args.overwrite)
        else:
            sys.stdout.write(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        return 0 if result["ok"] else 1
    except (FileNotFoundError, OSError, RoutePreflightError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
