from __future__ import annotations

import copy
from collections import Counter
from typing import Any, Mapping, Sequence

from otbm_semantic_landmarks import SemanticLandmarkError, resolve_landmark_anchor

MANIFEST_FORMAT = "canary-otbm-critical-access-targets-v1"
REPORT_FORMAT = "canary-otbm-critical-access-integrity-v1"
SCHEMA_VERSION = 1
MAX_TARGETS_PER_KIND = 4096
MAX_REVIEW_REFERENCES = 32

CRITICALITY_KINDS = frozenset(
    {
        "temple-recovery",
        "depot",
        "bank",
        "transport-hub",
        "city-entrance",
        "quest-hub",
        "other-reviewed-critical",
    }
)
ENTITY_ROLES = frozenset({"monster", "npc", "boss"})
ACCESS_EXPECTATIONS = frozenset({"reviewed-context", "public"})
CLASSIFICATIONS = frozenset(
    {
        "confirmed",
        "conditional",
        "unreachable-in-reviewed-context",
        "review-required",
        "unresolved",
        "conflicting",
    }
)


class CriticalAccessIntegrityError(ValueError):
    pass


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CriticalAccessIntegrityError(f"{label} must be an object")
    return value


def _exact_keys(
    value: Mapping[str, Any],
    *,
    label: str,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    missing = required - set(value)
    unknown = set(value) - required - optional
    if missing:
        raise CriticalAccessIntegrityError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        raise CriticalAccessIntegrityError(f"{label} has unknown fields: {', '.join(sorted(unknown))}")


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 240:
        raise CriticalAccessIntegrityError(f"{label} must be a non-empty string of at most 240 characters")
    return value


def _hash64(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise CriticalAccessIntegrityError(f"{label} must be a lowercase 64-character SHA-256")
    return value


def _position(value: Any, label: str) -> tuple[int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise CriticalAccessIntegrityError(f"{label} must contain exactly [x, y, z]")
    result: list[int] = []
    for index, maximum in enumerate((0xFFFF, 0xFFFF, 15)):
        coordinate = value[index]
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate <= maximum:
            raise CriticalAccessIntegrityError(f"{label}[{index}] is outside the OTBM coordinate range")
        result.append(int(coordinate))
    return result[0], result[1], result[2]


def _positive_int(value: Any, label: str, maximum: int = 0xFFFFFFFF) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= maximum:
        raise CriticalAccessIntegrityError(f"{label} must be an integer in 1..{maximum}")
    return value


def _uint8(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 0xFF:
        raise CriticalAccessIntegrityError(f"{label} must be an integer in 0..255")
    return value


def _review(value: Any, label: str) -> None:
    review = _mapping(value, label)
    _exact_keys(review, label=label, required={"status", "references"}, optional={"note"})
    if review["status"] != "reviewed":
        raise CriticalAccessIntegrityError(f"{label}.status must be reviewed")
    references = review["references"]
    if not isinstance(references, list) or not 1 <= len(references) <= MAX_REVIEW_REFERENCES:
        raise CriticalAccessIntegrityError(f"{label}.references must contain 1..{MAX_REVIEW_REFERENCES} entries")
    seen: set[str] = set()
    for index, reference in enumerate(references):
        if not isinstance(reference, str) or not 1 <= len(reference) <= 512:
            raise CriticalAccessIntegrityError(f"{label}.references[{index}] must be a non-empty string")
        if reference in seen:
            raise CriticalAccessIntegrityError(f"{label}.references contains duplicate reference {reference!r}")
        seen.add(reference)
    note = review.get("note")
    if note is not None and (not isinstance(note, str) or len(note) > 2000):
        raise CriticalAccessIntegrityError(f"{label}.note must be a string of at most 2000 characters")


def validate_target_manifest(document: Any) -> dict[str, Any]:
    root = _mapping(document, "manifest")
    _exact_keys(
        root,
        label="manifest",
        required={"format", "schemaVersion", "provenance", "targets"},
    )
    if root["format"] != MANIFEST_FORMAT:
        raise CriticalAccessIntegrityError(f"Unsupported critical-access target format: {root['format']!r}")
    if root["schemaVersion"] != SCHEMA_VERSION:
        raise CriticalAccessIntegrityError(f"Unsupported critical-access schema version: {root['schemaVersion']!r}")

    provenance = _mapping(root["provenance"], "provenance")
    _exact_keys(provenance, label="provenance", required={"sourceMap", "worldIndex"})
    for key, label in (("sourceMap", "source map"), ("worldIndex", "World Index")):
        record = _mapping(provenance[key], f"provenance.{key}")
        _exact_keys(record, label=f"provenance.{key}", required={"sha256"})
        _hash64(record["sha256"], f"provenance.{key}.sha256")

    targets = _mapping(root["targets"], "targets")
    _exact_keys(targets, label="targets", required={"criticalLandmarks", "houses", "spawnAccess"})
    seen_ids: set[str] = set()

    critical_landmarks = targets["criticalLandmarks"]
    houses = targets["houses"]
    spawn_access = targets["spawnAccess"]
    for name, entries in (("criticalLandmarks", critical_landmarks), ("houses", houses), ("spawnAccess", spawn_access)):
        if not isinstance(entries, list) or len(entries) > MAX_TARGETS_PER_KIND:
            raise CriticalAccessIntegrityError(f"targets.{name} must be an array with at most {MAX_TARGETS_PER_KIND} entries")

    for index, value in enumerate(critical_landmarks):
        label = f"targets.criticalLandmarks[{index}]"
        entry = _mapping(value, label)
        _exact_keys(
            entry,
            label=label,
            required={"id", "criticality", "landmarkId", "anchorId", "routeId", "review"},
        )
        target_id = _identifier(entry["id"], f"{label}.id")
        if target_id in seen_ids:
            raise CriticalAccessIntegrityError(f"Duplicate target ID: {target_id}")
        seen_ids.add(target_id)
        if entry["criticality"] not in CRITICALITY_KINDS:
            raise CriticalAccessIntegrityError(f"{label}.criticality is unsupported: {entry['criticality']!r}")
        _identifier(entry["landmarkId"], f"{label}.landmarkId")
        _identifier(entry["anchorId"], f"{label}.anchorId")
        _identifier(entry["routeId"], f"{label}.routeId")
        _review(entry["review"], f"{label}.review")

    for index, value in enumerate(houses):
        label = f"targets.houses[{index}]"
        entry = _mapping(value, label)
        _exact_keys(
            entry,
            label=label,
            required={"id", "houseId", "houseDoorId", "doorPosition", "interiorPosition", "routeId", "review"},
        )
        target_id = _identifier(entry["id"], f"{label}.id")
        if target_id in seen_ids:
            raise CriticalAccessIntegrityError(f"Duplicate target ID: {target_id}")
        seen_ids.add(target_id)
        _positive_int(entry["houseId"], f"{label}.houseId")
        _uint8(entry["houseDoorId"], f"{label}.houseDoorId")
        _position(entry["doorPosition"], f"{label}.doorPosition")
        _position(entry["interiorPosition"], f"{label}.interiorPosition")
        _identifier(entry["routeId"], f"{label}.routeId")
        _review(entry["review"], f"{label}.review")

    for index, value in enumerate(spawn_access):
        label = f"targets.spawnAccess[{index}]"
        entry = _mapping(value, label)
        _exact_keys(
            entry,
            label=label,
            required={"id", "entityRole", "placementId", "position", "routeId", "accessExpectation", "review"},
        )
        target_id = _identifier(entry["id"], f"{label}.id")
        if target_id in seen_ids:
            raise CriticalAccessIntegrityError(f"Duplicate target ID: {target_id}")
        seen_ids.add(target_id)
        if entry["entityRole"] not in ENTITY_ROLES:
            raise CriticalAccessIntegrityError(f"{label}.entityRole is unsupported: {entry['entityRole']!r}")
        _identifier(entry["placementId"], f"{label}.placementId")
        _position(entry["position"], f"{label}.position")
        _identifier(entry["routeId"], f"{label}.routeId")
        if entry["accessExpectation"] not in ACCESS_EXPECTATIONS:
            raise CriticalAccessIntegrityError(
                f"{label}.accessExpectation is unsupported: {entry['accessExpectation']!r}"
            )
        _review(entry["review"], f"{label}.review")

    return copy.deepcopy(dict(root))


def _nested_sha(document: Mapping[str, Any], path: Sequence[str], label: str) -> str:
    current: Any = document
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            raise CriticalAccessIntegrityError(f"{label} is missing SHA-256 provenance")
        current = current[key]
    return _hash64(current, label)


def _validate_inputs(
    manifest: Mapping[str, Any],
    landmark_registry: Mapping[str, Any],
    connectivity: Mapping[str, Any],
    geometry: Mapping[str, Any],
    spawn_validation: Mapping[str, Any],
    *,
    actual_world_index_sha256: str,
) -> tuple[str, str]:
    map_sha = _nested_sha(manifest, ("provenance", "sourceMap", "sha256"), "target source-map SHA-256")
    index_sha = _nested_sha(manifest, ("provenance", "worldIndex", "sha256"), "target World Index SHA-256")
    if _hash64(actual_world_index_sha256, "actual_world_index_sha256") != index_sha:
        raise CriticalAccessIntegrityError("World Index file SHA-256 does not match the reviewed target manifest")

    if landmark_registry.get("format") != "canary-otbm-semantic-landmarks-v1":
        raise CriticalAccessIntegrityError("Unsupported Semantic Landmark Registry format")
    if connectivity.get("format") != "canary-otbm-connectivity-resilience-v1":
        raise CriticalAccessIntegrityError("Unsupported Connectivity Resilience report format")
    if geometry.get("format") != "canary-otbm-geometry-audit-v1":
        raise CriticalAccessIntegrityError("Unsupported Geometry Audit report format")
    if spawn_validation.get("format") != "canary-otbm-spawn-npc-validation-v1":
        raise CriticalAccessIntegrityError("Unsupported Spawn/NPC validation report format")

    if _nested_sha(landmark_registry, ("provenance", "sourceMap", "sha256"), "landmark source-map SHA-256") != map_sha:
        raise CriticalAccessIntegrityError("Semantic Landmark Registry source-map provenance does not match targets")
    if _nested_sha(landmark_registry, ("provenance", "worldIndex", "sha256"), "landmark World Index SHA-256") != index_sha:
        raise CriticalAccessIntegrityError("Semantic Landmark Registry World Index provenance does not match targets")
    if _nested_sha(connectivity, ("source", "mapSha256"), "connectivity source-map SHA-256") != map_sha:
        raise CriticalAccessIntegrityError("Connectivity source-map provenance does not match targets")
    if _nested_sha(connectivity, ("source", "worldIndexSha256"), "connectivity World Index SHA-256") != index_sha:
        raise CriticalAccessIntegrityError("Connectivity World Index provenance does not match targets")
    if _nested_sha(geometry, ("provenance", "source", "sha256"), "geometry source-map SHA-256") != map_sha:
        raise CriticalAccessIntegrityError("Geometry source-map provenance does not match targets")
    if _nested_sha(geometry, ("provenance", "index", "sha256"), "geometry World Index SHA-256") != index_sha:
        raise CriticalAccessIntegrityError("Geometry World Index provenance does not match targets")
    if _nested_sha(spawn_validation, ("provenance", "worldIndex", "sha256"), "spawn World Index SHA-256") != index_sha:
        raise CriticalAccessIntegrityError("Spawn/NPC validation World Index provenance does not match targets")
    if geometry.get("complete") is not True:
        raise CriticalAccessIntegrityError("Geometry Audit must be complete")
    return map_sha, index_sha


def _unique_by_id(entries: Any, label: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(entries, list):
        raise CriticalAccessIntegrityError(f"{label} must be an array")
    result: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            continue
        if entry_id in result:
            raise CriticalAccessIntegrityError(f"{label} contains duplicate ID {entry_id!r}")
        result[entry_id] = entry
    return result


def _route_result(
    route: Mapping[str, Any] | None,
    *,
    expected_goal: tuple[int, int, int],
    required_position: tuple[int, int, int] | None = None,
) -> dict[str, Any]:
    if route is None:
        return {"status": "unresolved", "reason": "route-id-missing", "mode": None, "route": None}
    try:
        goal = _position(route.get("goal"), "route.goal")
    except CriticalAccessIntegrityError:
        return {
            "status": "conflicting",
            "reason": "route-goal-invalid",
            "mode": route.get("mode"),
            "route": dict(route),
        }
    if goal != expected_goal:
        return {
            "status": "conflicting",
            "reason": "route-goal-mismatch",
            "mode": route.get("mode"),
            "route": dict(route),
        }
    if not bool(route.get("reachable")):
        return {
            "status": "unreachable-in-reviewed-context",
            "reason": "reviewed-route-unreachable",
            "mode": route.get("mode"),
            "route": dict(route),
        }
    if required_position is not None:
        path = route.get("baselinePath")
        if not isinstance(path, list):
            return {
                "status": "unresolved",
                "reason": "route-baseline-path-missing",
                "mode": route.get("mode"),
                "route": dict(route),
            }
        try:
            normalized = {_position(value, "route.baselinePath position") for value in path}
        except CriticalAccessIntegrityError:
            return {
                "status": "conflicting",
                "reason": "route-baseline-path-invalid",
                "mode": route.get("mode"),
                "route": dict(route),
            }
        if required_position not in normalized:
            return {
                "status": "conflicting",
                "reason": "required-position-not-on-proven-route",
                "mode": route.get("mode"),
                "route": dict(route),
            }
    mode = route.get("mode")
    if mode == "optimistic" or bool(route.get("conditionalOnly")):
        status = "conditional"
    elif mode in {"strict", "executable"}:
        status = "confirmed"
    else:
        status = "unresolved"
    return {"status": status, "reason": "route-evidence", "mode": mode, "route": dict(route)}


def _house_door_evidence(
    index: Any,
    *,
    position: tuple[int, int, int],
    house_id: int,
    house_door_id: int,
) -> dict[str, Any]:
    found = index.find_tile(position)
    if found is None:
        return {"status": "unresolved", "reason": "door-tile-missing", "matches": []}
    tile_index, tile = found
    if getattr(tile, "kind", None) != "house" or getattr(tile, "house_id", None) != house_id:
        return {
            "status": "conflicting",
            "reason": "door-tile-house-id-mismatch",
            "tileIndex": tile_index,
            "actualHouseId": getattr(tile, "house_id", None),
            "matches": [],
        }
    placements = [
        index.placement(ordinal)
        for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count)
    ]
    door_placements = [entry for entry in placements if entry.get("houseDoorId") is not None]
    matches = [entry for entry in door_placements if entry.get("houseDoorId") == house_door_id]
    if len(matches) == 1:
        return {
            "status": "confirmed",
            "reason": "exact-house-door-placement",
            "tileIndex": tile_index,
            "matches": matches,
        }
    if len(matches) > 1:
        return {
            "status": "conflicting",
            "reason": "house-door-selector-ambiguous",
            "tileIndex": tile_index,
            "matches": matches,
        }
    if door_placements:
        return {
            "status": "conflicting",
            "reason": "house-door-id-mismatch",
            "tileIndex": tile_index,
            "availableHouseDoorIds": sorted({entry.get("houseDoorId") for entry in door_placements}),
            "matches": [],
        }
    return {
        "status": "unresolved",
        "reason": "house-door-placement-missing",
        "tileIndex": tile_index,
        "matches": [],
    }


def _geometry_house_evidence(geometry: Mapping[str, Any], house_id: int) -> dict[str, Any]:
    findings = geometry.get("findings")
    if not isinstance(findings, list):
        raise CriticalAccessIntegrityError("Geometry Audit findings must be an array")
    relevant = [
        dict(entry)
        for entry in findings
        if isinstance(entry, Mapping)
        and entry.get("houseId") == house_id
        and entry.get("kind") in {"house-disconnected-components", "house-component-mixed-pz"}
    ]
    relevant.sort(key=lambda entry: (str(entry.get("kind")), str(entry.get("id"))))
    summary = geometry.get("summary")
    truncated = False
    if isinstance(summary, Mapping) and isinstance(summary.get("findings"), Mapping):
        truncated = bool(summary["findings"].get("truncated"))
    if relevant:
        status = "review-required"
    elif truncated:
        status = "unresolved"
    else:
        status = "confirmed"
    return {"status": status, "findingsTruncated": truncated, "findings": relevant}


def _spawn_role_matches(target_role: str, placement: Mapping[str, Any]) -> bool:
    kind = placement.get("kind")
    if target_role == "npc":
        return kind == "npc"
    if target_role == "monster":
        return kind == "monster"
    return kind == "monster" and placement.get("rewardBossLiteral") is True


def _combine_statuses(statuses: Sequence[str]) -> str:
    ranking = {
        "conflicting": 5,
        "unresolved": 4,
        "unreachable-in-reviewed-context": 3,
        "review-required": 2,
        "conditional": 1,
        "confirmed": 0,
    }
    return max(statuses, key=lambda value: ranking.get(value, 99)) if statuses else "unresolved"


def _finding(code: str, target_id: str, classification: str, severity: str, message: str) -> dict[str, Any]:
    return {
        "code": code,
        "targetId": target_id,
        "classification": classification,
        "severity": severity,
        "message": message,
    }


def build_critical_access_report(
    *,
    manifest: Mapping[str, Any],
    landmark_registry: Mapping[str, Any],
    connectivity_report: Mapping[str, Any],
    geometry_report: Mapping[str, Any],
    spawn_validation_report: Mapping[str, Any],
    world_index: Any,
    actual_world_index_sha256: str,
    input_pins: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    targets = validate_target_manifest(manifest)
    map_sha, index_sha = _validate_inputs(
        targets,
        landmark_registry,
        connectivity_report,
        geometry_report,
        spawn_validation_report,
        actual_world_index_sha256=actual_world_index_sha256,
    )
    routes = _unique_by_id(connectivity_report.get("routes"), "Connectivity routes")
    placements = _unique_by_id(spawn_validation_report.get("placements"), "Spawn/NPC placements")
    placements_truncated = bool(spawn_validation_report.get("placementsTruncated"))

    landmark_results: list[dict[str, Any]] = []
    house_results: list[dict[str, Any]] = []
    spawn_results: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    for target in targets["targets"]["criticalLandmarks"]:
        target_id = target["id"]
        try:
            resolution = resolve_landmark_anchor(
                landmark_registry,
                landmark_id=target["landmarkId"],
                anchor_id=target["anchorId"],
                expected_source_map_sha256=map_sha,
                expected_world_index_sha256=index_sha,
            )
        except SemanticLandmarkError as exc:
            classification = "unresolved"
            route_evidence = {
                "status": "unresolved",
                "reason": "landmark-resolution-failed",
                "mode": None,
                "route": None,
            }
            position = None
            resolution_payload = None
            findings.append(
                _finding("CRITICAL_LANDMARK_UNRESOLVED", target_id, classification, "error", str(exc))
            )
        else:
            position = _position(resolution["anchor"]["position"], "resolved landmark anchor position")
            route_evidence = _route_result(routes.get(target["routeId"]), expected_goal=position)
            classification = route_evidence["status"]
            resolution_payload = resolution
            if classification != "confirmed":
                severity = "warning" if classification in {"conditional", "unreachable-in-reviewed-context"} else "error"
                findings.append(
                    _finding(
                        "CRITICAL_LANDMARK_ACCESS_NOT_CONFIRMED",
                        target_id,
                        classification,
                        severity,
                        route_evidence["reason"],
                    )
                )
        landmark_results.append(
            {
                "id": target_id,
                "criticality": target["criticality"],
                "landmarkId": target["landmarkId"],
                "anchorId": target["anchorId"],
                "position": None if position is None else list(position),
                "routeId": target["routeId"],
                "routeEvidence": route_evidence,
                "landmarkResolution": resolution_payload,
                "classification": classification,
                "runtimeAccessProven": False,
                "review": copy.deepcopy(target["review"]),
            }
        )

    for target in targets["targets"]["houses"]:
        target_id = target["id"]
        door_position = _position(target["doorPosition"], "house door position")
        interior_position = _position(target["interiorPosition"], "house interior position")
        door = _house_door_evidence(
            world_index,
            position=door_position,
            house_id=target["houseId"],
            house_door_id=target["houseDoorId"],
        )
        geometry = _geometry_house_evidence(geometry_report, target["houseId"])
        route = _route_result(
            routes.get(target["routeId"]),
            expected_goal=interior_position,
            required_position=door_position,
        )
        classification = _combine_statuses((door["status"], geometry["status"], route["status"]))
        if classification != "confirmed":
            severity = (
                "warning"
                if classification in {"conditional", "unreachable-in-reviewed-context", "review-required"}
                else "error"
            )
            findings.append(
                _finding(
                    "HOUSE_ACCESS_INTEGRITY_NOT_CONFIRMED",
                    target_id,
                    classification,
                    severity,
                    f"door={door['status']}; geometry={geometry['status']}; route={route['status']}",
                )
            )
        house_results.append(
            {
                "id": target_id,
                "houseId": target["houseId"],
                "houseDoorId": target["houseDoorId"],
                "doorPosition": list(door_position),
                "interiorPosition": list(interior_position),
                "routeId": target["routeId"],
                "doorEvidence": door,
                "geometryEvidence": geometry,
                "routeEvidence": route,
                "classification": classification,
                "runtimeAccessProven": False,
                "review": copy.deepcopy(target["review"]),
            }
        )

    for target in targets["targets"]["spawnAccess"]:
        target_id = target["id"]
        expected_position = _position(target["position"], "spawn access position")
        placement = placements.get(target["placementId"])
        if placement is None:
            placement_status = "unresolved"
            placement_reason = (
                "placement-id-not-visible-in-truncated-report"
                if placements_truncated
                else "placement-id-missing"
            )
            placement_payload = None
        else:
            placement_payload = dict(placement)
            try:
                actual_position = _position(placement.get("position"), "spawn placement position")
            except CriticalAccessIntegrityError:
                placement_status = "conflicting"
                placement_reason = "placement-position-invalid"
            else:
                if actual_position != expected_position:
                    placement_status = "conflicting"
                    placement_reason = "placement-position-mismatch"
                elif not _spawn_role_matches(target["entityRole"], placement):
                    placement_status = "conflicting"
                    placement_reason = "placement-role-mismatch"
                else:
                    source_status = placement.get("status")
                    if source_status == "confirmed":
                        placement_status = "confirmed"
                    elif source_status == "conditional":
                        placement_status = "conditional"
                    elif source_status in {
                        "blocked",
                        "missing-tile",
                        "missing-definition",
                        "conflicting-definition",
                    }:
                        placement_status = "review-required"
                    else:
                        placement_status = "unresolved"
                    placement_reason = f"spawn-validation-{source_status}"
        route = _route_result(routes.get(target["routeId"]), expected_goal=expected_position)
        classification = _combine_statuses((placement_status, route["status"]))
        if classification != "confirmed":
            severity = (
                "warning"
                if classification in {"conditional", "unreachable-in-reviewed-context", "review-required"}
                else "error"
            )
            findings.append(
                _finding(
                    "SPAWN_ACCESS_INTEGRITY_NOT_CONFIRMED",
                    target_id,
                    classification,
                    severity,
                    f"placement={placement_status} ({placement_reason}); route={route['status']}",
                )
            )
        spawn_results.append(
            {
                "id": target_id,
                "entityRole": target["entityRole"],
                "placementId": target["placementId"],
                "position": list(expected_position),
                "routeId": target["routeId"],
                "accessExpectation": target["accessExpectation"],
                "placementEvidence": {
                    "status": placement_status,
                    "reason": placement_reason,
                    "placement": placement_payload,
                    "sourceReportTruncated": placements_truncated,
                },
                "routeEvidence": route,
                "classification": classification,
                "intendedPublicAccessibilityDeclared": target["accessExpectation"] == "public",
                "intendedPublicAccessibilityProven": False,
                "runtimeAccessProven": False,
                "review": copy.deepcopy(target["review"]),
            }
        )

    findings.sort(key=lambda entry: (entry["severity"], entry["code"], entry["targetId"]))
    counts = Counter(
        entry["classification"]
        for entry in [*landmark_results, *house_results, *spawn_results]
    )
    severity_counts = Counter(entry["severity"] for entry in findings)
    report = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": severity_counts.get("error", 0) == 0,
        "source": {"mapSha256": map_sha, "worldIndexSha256": index_sha},
        "inputs": copy.deepcopy(dict(input_pins or {})),
        "policy": {
            "readOnly": True,
            "criticalityInferred": False,
            "semanticLandmarkResolverReused": True,
            "worldIndexReused": True,
            "connectivityReportConsumed": True,
            "pathfindingPerformed": False,
            "geometryRecomputed": False,
            "spawnNpcRescanned": False,
            "dynamicLuaExecuted": False,
            "runtimeAccessClaimed": False,
            "publicAccessibilityInferred": False,
            "mapModified": False,
            "physicalE2EExecuted": False,
            "changeBypassSeverClaimed": False,
        },
        "summary": {
            "criticalLandmarkTargets": len(landmark_results),
            "houseTargets": len(house_results),
            "spawnAccessTargets": len(spawn_results),
            "classifications": {key: counts.get(key, 0) for key in sorted(CLASSIFICATIONS)},
            "findings": len(findings),
            "errors": severity_counts.get("error", 0),
            "warnings": severity_counts.get("warning", 0),
        },
        "criticalLandmarks": landmark_results,
        "houses": house_results,
        "spawnAccess": spawn_results,
        "findings": findings,
    }
    return report


__all__ = [
    "ACCESS_EXPECTATIONS",
    "CLASSIFICATIONS",
    "CRITICALITY_KINDS",
    "CriticalAccessIntegrityError",
    "ENTITY_ROLES",
    "MANIFEST_FORMAT",
    "REPORT_FORMAT",
    "SCHEMA_VERSION",
    "build_critical_access_report",
    "validate_target_manifest",
]
