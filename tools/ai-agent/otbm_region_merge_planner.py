from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from otbm_script_resolution import REPORT_FORMAT as SCRIPT_RESOLUTION_FORMAT
from otbm_semantic_diff import (
    _load_json,
    _require_regular,
    _resolve_confined,
    _validate_manifest,
    _validate_pair,
)
from otbm_semantic_diff_types import (
    MAX_INDEX_BYTES,
    MAX_REPORT_INPUT_BYTES,
    canonical_json,
    normalize_bounds,
    normalize_position,
    sha256_path,
)
from otbm_world_index import WorldIndex

REPORT_FORMAT = "canary-otbm-region-merge-plan-v1"
SCHEMA_VERSION = 1
DEFAULT_SAMPLE_LIMIT = 500
MAX_SAMPLE_LIMIT = 10_000
POLICIES = {"overlay", "replace-region"}
UNRESOLVED_STATUSES = {"unresolved", "referenced-only", "partially-resolved"}

Position = tuple[int, int, int]
Bounds = tuple[Position, Position]


class RegionMergePlannerError(RuntimeError):
    pass


@dataclass
class SampleCollector:
    sample_limit: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.sample_limit, int)
            or isinstance(self.sample_limit, bool)
            or not 1 <= self.sample_limit <= MAX_SAMPLE_LIMIT
        ):
            raise RegionMergePlannerError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")
        self.total = 0
        self.samples: list[dict[str, Any]] = []
        self.by_kind: Counter[str] = Counter()
        self.by_severity: Counter[str] = Counter()

    def add(self, entry: dict[str, Any], *, kind: str, severity: str | None = None) -> None:
        self.total += 1
        self.by_kind[kind] += 1
        if severity is not None:
            self.by_severity[severity] += 1
        if len(self.samples) < self.sample_limit:
            self.samples.append(entry)

    def summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "total": self.total,
            "byKind": dict(sorted(self.by_kind.items())),
            "sampled": len(self.samples),
            "truncated": self.total > len(self.samples),
        }
        if self.by_severity:
            result["bySeverity"] = dict(sorted(self.by_severity.items()))
        return result


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256((prefix + "\n" + canonical_json(payload)).encode("utf-8")).hexdigest()
    return f"otbm-region-merge:{prefix}:{digest[:24]}"


def _in_bounds(position: Position, bounds: Bounds) -> bool:
    lower, upper = bounds
    return all(lower[index] <= position[index] <= upper[index] for index in range(3))


def _translate(position: Position, delta: Position, label: str) -> Position:
    translated = tuple(position[index] + delta[index] for index in range(3))
    if not (
        0 <= translated[0] <= 0xFFFF
        and 0 <= translated[1] <= 0xFFFF
        and 0 <= translated[2] <= 15
    ):
        raise RegionMergePlannerError(
            f"{label} translates outside the OTBM coordinate range: {position} + {delta} -> {translated}"
        )
    return translated  # type: ignore[return-value]


def _target_bounds(donor_bounds: Bounds, target_origin: Position) -> tuple[Bounds, Position]:
    donor_lower, donor_upper = donor_bounds
    target_origin = normalize_position(target_origin, "target origin")
    delta: Position = tuple(target_origin[index] - donor_lower[index] for index in range(3))  # type: ignore[assignment]
    target_upper = _translate(donor_upper, delta, "donor region upper bound")
    return (target_origin, target_upper), delta


def _placement_snapshot(
    placement: Mapping[str, Any],
    *,
    tile_placement_index: int,
    donor_bounds: Bounds | None = None,
    delta: Position | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "tilePlacementIndex": tile_placement_index,
        "itemId": int(placement["itemId"]),
        "itemDepth": int(placement.get("itemDepth", -1)),
        "source": str(placement.get("source", "")),
    }
    for field in ("actionId", "uniqueId", "houseDoorId"):
        value = placement.get(field)
        if isinstance(value, int):
            result[field] = value
    raw_destination = placement.get("teleportDestination")
    if isinstance(raw_destination, list) and len(raw_destination) == 3:
        destination = normalize_position(raw_destination, "teleport destination")
        if donor_bounds is not None and delta is not None and _in_bounds(destination, donor_bounds):
            result["teleportDestination"] = list(_translate(destination, delta, "internal teleport destination"))
            result["donorTeleportDestination"] = list(destination)
            result["teleportRemap"] = "translated-internal"
        else:
            result["teleportDestination"] = list(destination)
            if donor_bounds is not None and delta is not None:
                result["donorTeleportDestination"] = list(destination)
                result["teleportRemap"] = "preserved-external"
    return result


def _tile_snapshot(
    index: WorldIndex,
    tile_index: int,
    *,
    output_position: Position | None = None,
    donor_bounds: Bounds | None = None,
    delta: Position | None = None,
) -> dict[str, Any]:
    tile = index.tile(tile_index)
    position = output_position or (tile.x, tile.y, tile.z)
    placements = [
        _placement_snapshot(
            index.placement(ordinal),
            tile_placement_index=ordinal - tile.placement_start,
            donor_bounds=donor_bounds,
            delta=delta,
        )
        for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count)
    ]
    return {
        "position": list(position),
        "kind": tile.kind,
        "houseId": tile.house_id,
        "flags": tile.flags,
        "placementCount": len(placements),
        "placements": placements,
    }


def _region_snapshots(index: WorldIndex, bounds: Bounds) -> dict[Position, dict[str, Any]]:
    result: dict[Position, dict[str, Any]] = {}
    for tile_index, tile in index.iter_region_tiles(*bounds):
        position = (tile.x, tile.y, tile.z)
        result[position] = _tile_snapshot(index, tile_index)
    return result


def _translated_donor_snapshots(
    index: WorldIndex,
    donor_bounds: Bounds,
    delta: Position,
) -> tuple[dict[Position, dict[str, Any]], dict[Position, dict[str, Any]], dict[Position, Position]]:
    source: dict[Position, dict[str, Any]] = {}
    proposed: dict[Position, dict[str, Any]] = {}
    target_to_donor: dict[Position, Position] = {}
    for tile_index, tile in index.iter_region_tiles(*donor_bounds):
        donor_position = (tile.x, tile.y, tile.z)
        target_position = _translate(donor_position, delta, "donor tile")
        source[donor_position] = _tile_snapshot(index, tile_index)
        proposed[target_position] = _tile_snapshot(
            index,
            tile_index,
            output_position=target_position,
            donor_bounds=donor_bounds,
            delta=delta,
        )
        target_to_donor[target_position] = donor_position
    return source, proposed, target_to_donor


def _canonical_placement(placement: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in placement.items()
        if key not in {"donorTeleportDestination", "teleportRemap"}
    }


def _canonical_tile(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    placements = snapshot.get("placements", [])
    return {
        "position": snapshot.get("position"),
        "kind": snapshot.get("kind"),
        "houseId": snapshot.get("houseId"),
        "flags": snapshot.get("flags"),
        "placements": [
            _canonical_placement(entry)
            for entry in placements
            if isinstance(entry, dict)
        ],
    }


def _script_identifier_index(document: Mapping[str, Any] | None) -> dict[str, dict[int, dict[str, Any]]]:
    result: dict[str, dict[int, dict[str, Any]]] = {"actionId": {}, "uniqueId": {}}
    if document is None:
        return result
    raw_identifiers = document.get("identifiers")
    if not isinstance(raw_identifiers, dict):
        raise RegionMergePlannerError("Script-resolution report has no identifiers object")
    for namespace in ("actionId", "uniqueId"):
        entries = raw_identifiers.get(namespace)
        if not isinstance(entries, list):
            raise RegionMergePlannerError(f"Script-resolution report identifiers.{namespace} must be an array")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("value"), int):
                raise RegionMergePlannerError(f"Invalid script-resolution {namespace} identifier entry")
            result[namespace][int(entry["value"])] = entry
    return result


def _handler_signatures(entry: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if entry is None:
        return []
    handlers = entry.get("handlers")
    if not isinstance(handlers, list):
        return []
    signatures: list[dict[str, Any]] = []
    for handler in handlers:
        if not isinstance(handler, dict):
            continue
        source = handler.get("source") if isinstance(handler.get("source"), dict) else {}
        signatures.append(
            {
                "eventType": handler.get("eventType"),
                "handler": handler.get("handler"),
                "mode": handler.get("mode"),
                "generic": bool(handler.get("generic", False)),
                "origin": handler.get("origin"),
                "sourcePath": source.get("path"),
            }
        )
    signatures.sort(key=canonical_json)
    return signatures


def _compare_resolution(
    namespace: str,
    value: int,
    current_index: Mapping[str, Mapping[int, dict[str, Any]]],
    donor_index: Mapping[str, Mapping[int, dict[str, Any]]],
) -> dict[str, Any]:
    current = current_index.get(namespace, {}).get(value)
    donor = donor_index.get(namespace, {}).get(value)
    current_status = current.get("status") if isinstance(current, dict) else None
    donor_status = donor.get("status") if isinstance(donor, dict) else None
    current_handlers = _handler_signatures(current)
    donor_handlers = _handler_signatures(donor)
    if current is None or donor is None:
        comparison = "unavailable"
    elif current_status == "conflicting" or donor_status == "conflicting":
        comparison = "conflicting"
    elif current_status in UNRESOLVED_STATUSES or donor_status in UNRESOLVED_STATUSES:
        comparison = "unresolved"
    elif current_handlers and donor_handlers and current_handlers == donor_handlers:
        comparison = "same-handler"
    else:
        comparison = "different-handler"
    return {
        "comparison": comparison,
        "current": {"status": current_status, "handlers": current_handlers},
        "donor": {"status": donor_status, "handlers": donor_handlers},
    }


def _load_script_resolution(
    root: Path,
    path: Path | None,
    role: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if path is None:
        return None, None
    source = _resolve_confined(root, path, f"{role} script-resolution report")
    document = _load_json(source, f"{role} script-resolution report", maximum=MAX_REPORT_INPUT_BYTES)
    if document.get("format") != SCRIPT_RESOLUTION_FORMAT:
        raise RegionMergePlannerError(
            f"Unsupported {role} script-resolution format: {document.get('format')!r}"
        )
    return document, {
        "role": role,
        "path": source.relative_to(root).as_posix(),
        "size": source.stat().st_size,
        "sha256": sha256_path(source),
        "format": SCRIPT_RESOLUTION_FORMAT,
    }


def _global_mechanics(index: WorldIndex) -> dict[str, dict[Any, list[dict[str, Any]]]]:
    result: dict[str, dict[Any, list[dict[str, Any]]]] = {
        "actionId": defaultdict(list),
        "uniqueId": defaultdict(list),
        "houseDoor": defaultdict(list),
    }
    for mechanic_index in range(index.header.mechanic_count):
        ordinal, mechanic = index.mechanic_record(mechanic_index)
        placement = index.placement(ordinal)
        position = normalize_position(placement["position"], "current mechanic position")
        tile = index.tile(int(placement["tileIndex"]))
        evidence = {
            "position": list(position),
            "itemId": placement.get("itemId"),
            "itemDepth": placement.get("itemDepth"),
            "actionId": placement.get("actionId"),
            "uniqueId": placement.get("uniqueId"),
            "houseDoorId": placement.get("houseDoorId"),
            "houseId": tile.house_id,
        }
        if isinstance(mechanic.get("actionId"), int):
            result["actionId"][int(mechanic["actionId"])].append(evidence)
        if isinstance(mechanic.get("uniqueId"), int):
            result["uniqueId"][int(mechanic["uniqueId"])].append(evidence)
        if isinstance(mechanic.get("houseDoorId"), int) and tile.house_id is not None:
            result["houseDoor"][(tile.house_id, int(mechanic["houseDoorId"]))].append(evidence)
    return result


def _conflict_entry(
    *,
    kind: str,
    severity: str,
    position: Position,
    message: str,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    payload = {
        "kind": kind,
        "severity": severity,
        "position": list(position),
        "details": dict(details),
    }
    return {"id": _stable_id("conflict", payload), **payload, "message": message}


def _action_entry(
    *,
    kind: str,
    position: Position,
    donor_position: Position | None,
    current: Mapping[str, Any] | None,
    donor: Mapping[str, Any] | None,
    proposed: Mapping[str, Any] | None,
) -> dict[str, Any]:
    payload = {
        "kind": kind,
        "position": list(position),
        "donorPosition": list(donor_position) if donor_position is not None else None,
        "current": current,
        "donor": donor,
        "proposed": proposed,
    }
    return {"id": _stable_id("action", payload), **payload}


def analyze_region_merge_plan(
    *,
    artifact_root: Path,
    current_index_path: Path,
    current_manifest_path: Path,
    donor_index_path: Path,
    donor_manifest_path: Path,
    donor_from: Position,
    donor_to: Position,
    target_origin: Position,
    policy: str = "overlay",
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    current_script_resolution_path: Path | None = None,
    donor_script_resolution_path: Path | None = None,
) -> dict[str, Any]:
    if policy not in POLICIES:
        raise RegionMergePlannerError(f"policy must be one of {sorted(POLICIES)}")
    if not 1 <= sample_limit <= MAX_SAMPLE_LIMIT:
        raise RegionMergePlannerError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")

    root = artifact_root.expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)

    current_index_source = _resolve_confined(root, current_index_path, "current World Index")
    donor_index_source = _resolve_confined(root, donor_index_path, "donor World Index")
    current_manifest_source = _resolve_confined(root, current_manifest_path, "current World Index manifest")
    donor_manifest_source = _resolve_confined(root, donor_manifest_path, "donor World Index manifest")
    _require_regular(current_index_source, "current World Index", MAX_INDEX_BYTES)
    _require_regular(donor_index_source, "donor World Index", MAX_INDEX_BYTES)

    donor_bounds = normalize_bounds(donor_from, donor_to)
    target_region, delta = _target_bounds(donor_bounds, target_origin)
    current_script, current_script_provenance = _load_script_resolution(
        root, current_script_resolution_path, "current"
    )
    donor_script, donor_script_provenance = _load_script_resolution(
        root, donor_script_resolution_path, "donor"
    )
    current_script_index = _script_identifier_index(current_script)
    donor_script_index = _script_identifier_index(donor_script)

    action_collector = SampleCollector(sample_limit)
    conflict_collector = SampleCollector(sample_limit)
    action_kinds: dict[Position, str] = {}

    with WorldIndex(current_index_source) as current_index, WorldIndex(donor_index_source) as donor_index:
        current_provenance, current_manifest_provenance = _validate_manifest(
            role="current",
            root=root,
            index_path=current_index_source,
            manifest_path=current_manifest_source,
            index=current_index,
        )
        donor_provenance, donor_manifest_provenance = _validate_manifest(
            role="donor",
            root=root,
            index_path=donor_index_source,
            manifest_path=donor_manifest_source,
            index=donor_index,
        )
        compatibility = _validate_pair(current_provenance, donor_provenance)
        for role, provenance in (("current", current_provenance), ("donor", donor_provenance)):
            if int(provenance.summary.get("unknownAttributeTails", 0)) != 0:
                raise RegionMergePlannerError(
                    f"{role} World Index contains unknown attribute tails; region replacement planning is unsafe"
                )

        current_region = _region_snapshots(current_index, target_region)
        donor_source, donor_proposed, target_to_donor = _translated_donor_snapshots(
            donor_index, donor_bounds, delta
        )

        all_positions = sorted(
            set(current_region) | set(donor_proposed),
            key=lambda value: (value[2], value[1], value[0]),
        )
        for position in all_positions:
            current_snapshot = current_region.get(position)
            proposed_snapshot = donor_proposed.get(position)
            donor_position = target_to_donor.get(position)
            donor_snapshot = donor_source.get(donor_position) if donor_position is not None else None
            if proposed_snapshot is not None and current_snapshot is not None:
                kind = (
                    "unchanged"
                    if _canonical_tile(current_snapshot) == _canonical_tile(proposed_snapshot)
                    else "replace"
                )
            elif proposed_snapshot is not None:
                kind = "add"
            elif policy == "replace-region":
                kind = "delete-candidate"
            else:
                kind = "preserve-current-only"
            action_kinds[position] = kind
            action = _action_entry(
                kind=kind,
                position=position,
                donor_position=donor_position,
                current=current_snapshot,
                donor=donor_snapshot,
                proposed=proposed_snapshot,
            )
            action_collector.add(action, kind=kind)
            if kind == "replace":
                conflict = _conflict_entry(
                    kind="current-content-replacement",
                    severity="review",
                    position=position,
                    message="Donor content differs from existing target tile content; replacement requires explicit review.",
                    details={"actionId": action["id"]},
                )
                conflict_collector.add(conflict, kind=conflict["kind"], severity=conflict["severity"])
            elif kind == "delete-candidate":
                conflict = _conflict_entry(
                    kind="current-content-delete-candidate",
                    severity="review",
                    position=position,
                    message="replace-region policy would remove a current-only tile; deletion remains review-only.",
                    details={"actionId": action["id"]},
                )
                conflict_collector.add(conflict, kind=conflict["kind"], severity=conflict["severity"])

        removed_current_positions = {
            position
            for position, kind in action_kinds.items()
            if kind in {"replace", "delete-candidate"}
        }
        global_mechanics = _global_mechanics(current_index)

        for target_position, proposed_snapshot in sorted(
            donor_proposed.items(), key=lambda item: (item[0][2], item[0][1], item[0][0])
        ):
            if action_kinds[target_position] == "unchanged":
                continue
            donor_position = target_to_donor[target_position]
            donor_snapshot = donor_source[donor_position]
            house_id = proposed_snapshot.get("houseId")
            proposed_placements = proposed_snapshot.get("placements", [])
            donor_placements = donor_snapshot.get("placements", [])
            for placement_index, proposed_placement in enumerate(proposed_placements):
                donor_placement = donor_placements[placement_index]
                for namespace in ("actionId", "uniqueId"):
                    value = proposed_placement.get(namespace)
                    if not isinstance(value, int):
                        continue
                    collisions = [
                        entry
                        for entry in global_mechanics[namespace].get(value, [])
                        if normalize_position(entry["position"], "mechanic collision position")
                        not in removed_current_positions
                    ]
                    if not collisions:
                        continue
                    resolution = _compare_resolution(
                        namespace,
                        value,
                        current_script_index,
                        donor_script_index,
                    )
                    if namespace == "uniqueId":
                        kind = "unique-id-collision"
                        severity = "error"
                        message = "Donor uniqueId collides with a retained current-map uniqueId occurrence."
                    elif resolution["comparison"] == "same-handler":
                        kind = "action-id-reuse-same-handler"
                        severity = "review"
                        message = "Donor actionId already exists in retained current content with matching explicit handler evidence."
                    elif resolution["comparison"] in {"unavailable", "unresolved"}:
                        kind = "action-id-reuse-unresolved"
                        severity = "unresolved"
                        message = "Donor actionId already exists, but runtime compatibility is not proven by supplied script-resolution evidence."
                    else:
                        kind = "action-id-reuse-handler-conflict"
                        severity = "error"
                        message = "Donor actionId already exists with different or conflicting handler evidence."
                    conflict = _conflict_entry(
                        kind=kind,
                        severity=severity,
                        position=target_position,
                        message=message,
                        details={
                            "namespace": namespace,
                            "value": value,
                            "tilePlacementIndex": proposed_placement["tilePlacementIndex"],
                            "retainedCurrentOccurrences": collisions[:20],
                            "retainedCurrentOccurrenceCount": len(collisions),
                            "resolution": resolution,
                        },
                    )
                    conflict_collector.add(conflict, kind=kind, severity=severity)

                house_door_id = proposed_placement.get("houseDoorId")
                if isinstance(house_door_id, int):
                    if not isinstance(house_id, int):
                        conflict = _conflict_entry(
                            kind="house-door-without-house-id",
                            severity="error",
                            position=target_position,
                            message="Donor houseDoorId is attached to a tile without a houseId.",
                            details={
                                "houseDoorId": house_door_id,
                                "tilePlacementIndex": proposed_placement["tilePlacementIndex"],
                            },
                        )
                        conflict_collector.add(conflict, kind=conflict["kind"], severity=conflict["severity"])
                    else:
                        collisions = [
                            entry
                            for entry in global_mechanics["houseDoor"].get((house_id, house_door_id), [])
                            if normalize_position(entry["position"], "house-door collision position")
                            not in removed_current_positions
                        ]
                        if collisions:
                            conflict = _conflict_entry(
                                kind="house-door-id-reuse",
                                severity="error",
                                position=target_position,
                                message="Donor house-door identifier is already used by retained content in the same houseId.",
                                details={
                                    "houseId": house_id,
                                    "houseDoorId": house_door_id,
                                    "tilePlacementIndex": proposed_placement["tilePlacementIndex"],
                                    "retainedCurrentOccurrences": collisions[:20],
                                    "retainedCurrentOccurrenceCount": len(collisions),
                                },
                            )
                            conflict_collector.add(conflict, kind=conflict["kind"], severity=conflict["severity"])

                raw_destination = donor_placement.get("teleportDestination")
                if not isinstance(raw_destination, list):
                    continue
                donor_destination = normalize_position(raw_destination, "donor teleport destination")
                if _in_bounds(donor_destination, donor_bounds):
                    translated_destination = _translate(
                        donor_destination, delta, "internal teleport destination"
                    )
                    donor_destination_exists = donor_destination in donor_source
                    current_destination_exists = current_index.find_tile(translated_destination) is not None
                    effective_destination_exists = donor_destination_exists or (
                        policy == "overlay" and current_destination_exists
                    )
                    if not donor_destination_exists:
                        severity = "review" if effective_destination_exists else "error"
                        conflict = _conflict_entry(
                            kind="teleport-destination-missing-donor-tile",
                            severity=severity,
                            position=target_position,
                            message="Internal donor teleport destination has no donor tile in the selected donor region.",
                            details={
                                "donorDestination": list(donor_destination),
                                "translatedDestination": list(translated_destination),
                                "currentDestinationExists": current_destination_exists,
                                "effectiveDestinationExists": effective_destination_exists,
                            },
                        )
                        conflict_collector.add(conflict, kind=conflict["kind"], severity=severity)
                    if not effective_destination_exists:
                        conflict = _conflict_entry(
                            kind="teleport-destination-missing-after-plan",
                            severity="error",
                            position=target_position,
                            message="Translated internal teleport destination would not exist after the reviewed plan.",
                            details={
                                "donorDestination": list(donor_destination),
                                "translatedDestination": list(translated_destination),
                                "policy": policy,
                            },
                        )
                        conflict_collector.add(conflict, kind=conflict["kind"], severity=conflict["severity"])
                else:
                    current_destination_exists = current_index.find_tile(donor_destination) is not None
                    severity = "review" if current_destination_exists else "error"
                    kind = (
                        "external-teleport-destination-preserved"
                        if current_destination_exists
                        else "external-teleport-destination-missing-current"
                    )
                    conflict = _conflict_entry(
                        kind=kind,
                        severity=severity,
                        position=target_position,
                        message=(
                            "Teleport destination lies outside the selected donor region and is preserved without remapping; explicit review is required."
                            if current_destination_exists
                            else "Teleport destination lies outside the donor region and no matching current-map destination tile exists."
                        ),
                        details={
                            "donorDestination": list(donor_destination),
                            "remap": "none",
                            "currentDestinationExists": current_destination_exists,
                        },
                    )
                    conflict_collector.add(conflict, kind=kind, severity=severity)

        action_collector.samples.sort(
            key=lambda entry: (tuple(entry["position"]), entry["kind"], entry["id"])
        )
        conflict_collector.samples.sort(
            key=lambda entry: (tuple(entry["position"]), entry["kind"], entry["id"])
        )
        action_summary = action_collector.summary()
        conflict_summary = conflict_collector.summary()
        blocking = sum(
            conflict_summary.get("bySeverity", {}).get(severity, 0)
            for severity in ("error", "unresolved")
        )
        requires_review = (
            action_summary["byKind"].get("add", 0)
            + action_summary["byKind"].get("replace", 0)
            + action_summary["byKind"].get("delete-candidate", 0)
            + conflict_summary["total"]
        ) > 0

        return {
            "format": REPORT_FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "ok": blocking == 0,
            "analysisComplete": True,
            "writerReady": False,
            "requiresHumanReview": requires_review,
            "policy": policy,
            "translation": {
                "donorRegion": {"from": list(donor_bounds[0]), "to": list(donor_bounds[1])},
                "targetRegion": {"from": list(target_region[0]), "to": list(target_region[1])},
                "delta": list(delta),
            },
            "summary": {
                "donorTiles": len(donor_source),
                "currentTargetTiles": len(current_region),
                "actions": action_summary,
                "conflicts": conflict_summary,
                "blockingConflicts": blocking,
            },
            "actions": action_collector.samples,
            "conflicts": conflict_collector.samples,
            "provenance": {
                "compatibility": compatibility,
                "current": current_provenance.to_json(),
                "donor": donor_provenance.to_json(),
                "manifests": {
                    "current": current_manifest_provenance,
                    "donor": donor_manifest_provenance,
                },
                "scriptResolution": {
                    "current": current_script_provenance,
                    "donor": donor_script_provenance,
                },
            },
            "safety": {
                "readOnly": True,
                "writesOtbm": False,
                "heuristicAlignment": False,
                "phase8Expanded": False,
                "executableWriterInstructions": False,
                "unknownAttributeTailsAccepted": False,
            },
            "notes": [
                "This report is a review-only structural plan and does not modify either OTBM map.",
                "Only donor teleport destinations inside the selected donor region are translated. External destinations are preserved and reviewed explicitly.",
                "ActionId reuse is not automatically a conflict when explicit current and donor script-resolution evidence proves the same handler signature.",
                "UniqueId collisions remain blocking regardless of handler evidence.",
                "Current-only tiles are preserved by overlay and emitted as delete-candidate review actions by replace-region.",
                "No lower evidence level is promoted to gameplay correctness or executable region-import readiness.",
            ],
        }
