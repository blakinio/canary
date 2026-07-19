#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

REGISTRY_FORMAT = "canary-otbm-route-interactions-v1"
RESOLUTION_FORMAT = "canary-otbm-route-interaction-resolution-v1"
SCHEMA_VERSION = 1
MAX_ENTRIES = 4096
MAX_EVIDENCE_REFERENCES = 32

ACTIVATION_KINDS = frozenset({"step-on", "walk-direction", "use-map-item", "use-inventory-on-map"})
TRANSITION_KINDS = frozenset({"teleport", "stairs", "ladder", "hole", "rope", "floor-change", "custom"})
TRANSITION_EVIDENCE_SOURCES = frozenset({"worldIndex", "transitionManifest"})
DIRECTIONS = frozenset(
    {"north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"}
)
SAFE_SCRIPT_STATUSES = frozenset(
    {
        "handled-directly",
        "handled-by-range",
        "handled-generically",
        "handled-by-item-id",
        "handled-by-action-id",
        "handled-by-unique-id",
        "handled-by-position",
        "handled-as-target",
        "handled-by-fallback",
        "handled-by-engine",
        "handled-multiple",
    }
)
FAIL_CLOSED_SCRIPT_STATUSES = frozenset({"partially-resolved", "referenced-only", "unresolved", "conflicting"})
_MECHANIC_SELECTOR_FIELDS = ("itemId", "actionId", "uniqueId", "houseDoorId")
_IDENTIFIER_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RouteInteractionError(ValueError):
    pass


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RouteInteractionError(f"{label} must be an object")
    return value


def _exact_keys(
    value: Mapping[str, Any],
    *,
    label: str,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    optional = optional or set()
    keys = set(value)
    missing = required - keys
    unknown = keys - required - optional
    if missing:
        raise RouteInteractionError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        raise RouteInteractionError(f"{label} has unknown fields: {', '.join(sorted(unknown))}")


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 160 or _IDENTIFIER_RE.fullmatch(value) is None:
        raise RouteInteractionError(f"{label} must be a lowercase semantic identifier")
    return value


def _transition_id(value: Any, label: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 240:
        raise RouteInteractionError(f"{label} must be a non-empty string of at most 240 characters")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise RouteInteractionError(f"{label} must be a lowercase 64-character SHA-256")
    return value


def _uint16(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 0xFFFF:
        raise RouteInteractionError(f"{label} must be an integer in the range 0..65535")
    return value


def _position(value: Any, label: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise RouteInteractionError(f"{label} must be a three-element [x, y, z] array")
    limits = (0xFFFF, 0xFFFF, 15)
    result: list[int] = []
    for index, maximum in enumerate(limits):
        coordinate = value[index]
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate <= maximum:
            raise RouteInteractionError(f"{label}[{index}] is outside the OTBM coordinate range")
        result.append(coordinate)
    return result[0], result[1], result[2]


def _hash_evidence(value: Any, label: str) -> str:
    evidence = _mapping(value, label)
    _exact_keys(evidence, label=label, required={"sha256"})
    return _sha256(evidence["sha256"], f"{label}.sha256")


def _validate_provenance(value: Any) -> dict[str, str | None]:
    provenance = _mapping(value, "provenance")
    _exact_keys(
        provenance,
        label="provenance",
        required={"sourceMap", "worldIndex", "transitionManifest", "scriptResolution"},
    )
    result: dict[str, str | None] = {
        "sourceMap": _hash_evidence(provenance["sourceMap"], "provenance.sourceMap"),
        "worldIndex": _hash_evidence(provenance["worldIndex"], "provenance.worldIndex"),
        "transitionManifest": None,
        "scriptResolution": None,
    }
    if provenance["transitionManifest"] is not None:
        result["transitionManifest"] = _hash_evidence(
            provenance["transitionManifest"], "provenance.transitionManifest"
        )
    if provenance["scriptResolution"] is not None:
        result["scriptResolution"] = _hash_evidence(provenance["scriptResolution"], "provenance.scriptResolution")
    return result


def _validate_evidence(value: Any, label: str) -> None:
    evidence = _mapping(value, label)
    _exact_keys(evidence, label=label, required={"status", "references"}, optional={"note"})
    if evidence["status"] != "reviewed":
        raise RouteInteractionError(f"{label}.status must be reviewed")
    references = evidence["references"]
    if not isinstance(references, list) or not 1 <= len(references) <= MAX_EVIDENCE_REFERENCES:
        raise RouteInteractionError(
            f"{label}.references must contain 1..{MAX_EVIDENCE_REFERENCES} reviewed references"
        )
    seen: set[str] = set()
    for index, reference in enumerate(references):
        if not isinstance(reference, str) or not 1 <= len(reference) <= 512:
            raise RouteInteractionError(f"{label}.references[{index}] must be a non-empty string")
        if reference in seen:
            raise RouteInteractionError(f"{label}.references contains duplicate reference {reference!r}")
        seen.add(reference)
    note = evidence.get("note")
    if note is not None and (not isinstance(note, str) or len(note) > 2000):
        raise RouteInteractionError(f"{label}.note must be a string of at most 2000 characters")


def _selector_kind(selector: Mapping[str, Any], label: str) -> str:
    if "transitionId" in selector:
        _exact_keys(selector, label=label, required={"transitionId"})
        _transition_id(selector["transitionId"], f"{label}.transitionId")
        return "transition"

    _exact_keys(
        selector,
        label=label,
        required={"position"},
        optional=set(_MECHANIC_SELECTOR_FIELDS),
    )
    _position(selector["position"], f"{label}.position")
    present = [field for field in _MECHANIC_SELECTOR_FIELDS if field in selector]
    if not present:
        raise RouteInteractionError(
            f"{label} must include at least one of itemId, actionId, uniqueId or houseDoorId"
        )
    for field in present:
        _uint16(selector[field], f"{label}.{field}")
    return "mechanic"


def _validate_activation(value: Any, label: str, selector_kind: str) -> None:
    activation = _mapping(value, label)
    if "kind" not in activation:
        raise RouteInteractionError(f"{label} is missing required fields: kind")
    kind = activation["kind"]
    if kind not in ACTIVATION_KINDS:
        raise RouteInteractionError(f"{label}.kind is unsupported: {kind!r}")

    if kind == "step-on":
        _exact_keys(activation, label=label, required={"kind"})
        if selector_kind != "transition":
            raise RouteInteractionError("step-on activation requires a transitionId selector")
        return

    if kind == "walk-direction":
        _exact_keys(activation, label=label, required={"kind", "direction"})
        if selector_kind != "transition":
            raise RouteInteractionError("walk-direction activation requires a transitionId selector")
        if activation["direction"] not in DIRECTIONS:
            raise RouteInteractionError(f"{label}.direction is unsupported: {activation['direction']!r}")
        return

    optional = {"targetPosition"}
    required = {"kind", "target"}
    if kind == "use-inventory-on-map":
        required.add("inventoryItemId")
    _exact_keys(activation, label=label, required=required, optional=optional)
    target = activation["target"]
    if target not in {"transition-source", "selector-position", "explicit-position"}:
        raise RouteInteractionError(f"{label}.target is unsupported: {target!r}")
    if target == "transition-source" and selector_kind != "transition":
        raise RouteInteractionError("transition-source target requires a transitionId selector")
    if target == "selector-position" and selector_kind != "mechanic":
        raise RouteInteractionError("selector-position target requires an exact mechanic selector")
    if target == "explicit-position":
        if "targetPosition" not in activation:
            raise RouteInteractionError(f"{label}.targetPosition is required for explicit-position")
        _position(activation["targetPosition"], f"{label}.targetPosition")
    elif "targetPosition" in activation:
        raise RouteInteractionError(f"{label}.targetPosition is allowed only for explicit-position")
    if kind == "use-inventory-on-map":
        _uint16(activation["inventoryItemId"], f"{label}.inventoryItemId")


def _unique_enum_list(value: Any, label: str, allowed: frozenset[str]) -> list[str]:
    if not isinstance(value, list):
        raise RouteInteractionError(f"{label} must be an array")
    result: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if item not in allowed:
            raise RouteInteractionError(f"{label}[{index}] is unsupported: {item!r}")
        if item in seen:
            raise RouteInteractionError(f"{label} contains duplicate value {item!r}")
        seen.add(item)
        result.append(item)
    return result


def _validate_requirements(value: Any, label: str, selector_kind: str) -> tuple[list[str], list[str], bool]:
    requirements = _mapping(value, label)
    _exact_keys(
        requirements,
        label=label,
        required={"transitionKinds", "transitionEvidenceSources", "scriptResolution"},
    )
    transition_kinds = _unique_enum_list(
        requirements["transitionKinds"], f"{label}.transitionKinds", TRANSITION_KINDS
    )
    evidence_sources = _unique_enum_list(
        requirements["transitionEvidenceSources"],
        f"{label}.transitionEvidenceSources",
        TRANSITION_EVIDENCE_SOURCES,
    )

    if selector_kind == "transition":
        if not transition_kinds:
            raise RouteInteractionError(f"{label}.transitionKinds must not be empty for a transition selector")
        if not evidence_sources:
            raise RouteInteractionError(
                f"{label}.transitionEvidenceSources must not be empty for a transition selector"
            )
    elif transition_kinds or evidence_sources:
        raise RouteInteractionError(
            f"{label} transition constraints must be empty for an exact mechanic selector"
        )

    script_requirement = _mapping(requirements["scriptResolution"], f"{label}.scriptResolution")
    _exact_keys(
        script_requirement,
        label=f"{label}.scriptResolution",
        required={"required", "allowedStatuses"},
    )
    required = script_requirement["required"]
    if not isinstance(required, bool):
        raise RouteInteractionError(f"{label}.scriptResolution.required must be boolean")
    allowed_statuses = _unique_enum_list(
        script_requirement["allowedStatuses"],
        f"{label}.scriptResolution.allowedStatuses",
        SAFE_SCRIPT_STATUSES,
    )
    if required and not allowed_statuses:
        raise RouteInteractionError(
            f"{label}.scriptResolution.allowedStatuses must not be empty when script resolution is required"
        )
    if not required and allowed_statuses:
        raise RouteInteractionError(
            f"{label}.scriptResolution.allowedStatuses must be empty when script resolution is not required"
        )
    return transition_kinds, evidence_sources, required


def validate_registry(
    document: Any,
    *,
    expected_source_map_sha256: str | None = None,
    expected_world_index_sha256: str | None = None,
    expected_transition_manifest_sha256: str | None = None,
    expected_script_resolution_sha256: str | None = None,
    require_reviewed: bool = False,
) -> dict[str, Any]:
    root = _mapping(document, "registry")
    _exact_keys(
        root,
        label="registry",
        required={"format", "schemaVersion", "registryStatus", "provenance", "entries"},
    )
    if root["format"] != REGISTRY_FORMAT:
        raise RouteInteractionError(f"Unsupported route interaction registry format: {root['format']!r}")
    if root["schemaVersion"] != SCHEMA_VERSION:
        raise RouteInteractionError(f"Unsupported route interaction schema version: {root['schemaVersion']!r}")

    status = root["registryStatus"]
    if status not in {"unbound", "reviewed"}:
        raise RouteInteractionError("registryStatus must be unbound or reviewed")
    entries = root["entries"]
    if not isinstance(entries, list) or len(entries) > MAX_ENTRIES:
        raise RouteInteractionError(f"entries must be an array with at most {MAX_ENTRIES} entries")

    if status == "unbound":
        if require_reviewed:
            raise RouteInteractionError("Route interaction registry is unbound and cannot resolve executable interactions")
        if root["provenance"] is not None:
            raise RouteInteractionError("Unbound route interaction registry must use provenance=null")
        if entries:
            raise RouteInteractionError("Unbound route interaction registry must not contain entries")
        if any(
            value is not None
            for value in (
                expected_source_map_sha256,
                expected_world_index_sha256,
                expected_transition_manifest_sha256,
                expected_script_resolution_sha256,
            )
        ):
            raise RouteInteractionError("Unbound route interaction registry cannot satisfy exact provenance expectations")
        return copy.deepcopy(dict(root))

    provenance_hashes = _validate_provenance(root["provenance"])
    expectations = (
        ("sourceMap", expected_source_map_sha256, "source-map"),
        ("worldIndex", expected_world_index_sha256, "World Index"),
        ("transitionManifest", expected_transition_manifest_sha256, "transition-manifest"),
        ("scriptResolution", expected_script_resolution_sha256, "script-resolution"),
    )
    for key, expected_value, description in expectations:
        if expected_value is None:
            continue
        expected = _sha256(expected_value, f"expected_{key}_sha256")
        actual = provenance_hashes[key]
        if actual is None:
            raise RouteInteractionError(f"Route interaction registry has no {description} SHA-256 provenance")
        if actual != expected:
            raise RouteInteractionError(f"Route interaction registry {description} SHA-256 does not match runtime evidence")

    entry_ids: set[str] = set()
    canonical_selectors: set[str] = set()
    requires_script_resolution = False
    requires_transition_manifest = False

    for index, raw_entry in enumerate(entries):
        label = f"entries[{index}]"
        entry = _mapping(raw_entry, label)
        _exact_keys(
            entry,
            label=label,
            required={"id", "selector", "activation", "requirements", "evidence"},
        )
        entry_id = _identifier(entry["id"], f"{label}.id")
        if entry_id in entry_ids:
            raise RouteInteractionError(f"Duplicate route interaction entry ID: {entry_id}")
        entry_ids.add(entry_id)

        selector = _mapping(entry["selector"], f"{label}.selector")
        selector_kind = _selector_kind(selector, f"{label}.selector")
        canonical_selector = json.dumps(dict(selector), sort_keys=True, separators=(",", ":"))
        if canonical_selector in canonical_selectors:
            raise RouteInteractionError(f"Duplicate route interaction selector: {canonical_selector}")
        canonical_selectors.add(canonical_selector)

        _validate_activation(entry["activation"], f"{label}.activation", selector_kind)
        _, evidence_sources, script_required = _validate_requirements(
            entry["requirements"], f"{label}.requirements", selector_kind
        )
        _validate_evidence(entry["evidence"], f"{label}.evidence")
        requires_script_resolution = requires_script_resolution or script_required
        requires_transition_manifest = requires_transition_manifest or "transitionManifest" in evidence_sources

    if requires_script_resolution and provenance_hashes["scriptResolution"] is None:
        raise RouteInteractionError(
            "Reviewed route interaction registry requires scriptResolution provenance for handler-gated entries"
        )
    if requires_transition_manifest and provenance_hashes["transitionManifest"] is None:
        raise RouteInteractionError(
            "Reviewed route interaction registry requires transitionManifest provenance for reviewed transition entries"
        )

    return copy.deepcopy(dict(root))


def load_registry(
    path: Path,
    *,
    expected_source_map_sha256: str | None = None,
    expected_world_index_sha256: str | None = None,
    expected_transition_manifest_sha256: str | None = None,
    expected_script_resolution_sha256: str | None = None,
    require_reviewed: bool = False,
) -> dict[str, Any]:
    candidate = path.expanduser().resolve()
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    try:
        document = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RouteInteractionError(f"Cannot read route interaction registry {candidate}: {exc}") from exc
    return validate_registry(
        document,
        expected_source_map_sha256=expected_source_map_sha256,
        expected_world_index_sha256=expected_world_index_sha256,
        expected_transition_manifest_sha256=expected_transition_manifest_sha256,
        expected_script_resolution_sha256=expected_script_resolution_sha256,
        require_reviewed=require_reviewed,
    )


def _selector_matches(selector: Mapping[str, Any], query: Mapping[str, Any]) -> bool:
    if "transitionId" in selector:
        return query.get("transitionId") == selector["transitionId"]
    if query.get("position") != selector["position"]:
        return False
    return all(query.get(field) == selector[field] for field in _MECHANIC_SELECTOR_FIELDS if field in selector)


def _resolution(
    *,
    query: dict[str, Any],
    execution_status: str,
    blockers: list[dict[str, Any]],
    entry: Mapping[str, Any] | None = None,
    matched_entry_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "format": RESOLUTION_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "executionStatus": execution_status,
        "selectorQuery": copy.deepcopy(query),
        "matchedEntryId": entry["id"] if entry is not None else None,
        "matchedEntryIds": matched_entry_ids or ([] if entry is None else [entry["id"]]),
        "activation": copy.deepcopy(entry["activation"]) if entry is not None and execution_status == "executable" else None,
        "evidence": copy.deepcopy(entry["evidence"]) if entry is not None else None,
        "blockers": copy.deepcopy(blockers),
    }


def resolve_interaction(
    document: Any,
    *,
    expected_source_map_sha256: str,
    expected_world_index_sha256: str,
    transition_id: str | None = None,
    transition_kind: str | None = None,
    transition_evidence_source: str | None = None,
    position: list[int] | None = None,
    item_id: int | None = None,
    action_id: int | None = None,
    unique_id: int | None = None,
    house_door_id: int | None = None,
    script_status: str | None = None,
    expected_transition_manifest_sha256: str | None = None,
    expected_script_resolution_sha256: str | None = None,
) -> dict[str, Any]:
    registry = validate_registry(
        document,
        expected_source_map_sha256=expected_source_map_sha256,
        expected_world_index_sha256=expected_world_index_sha256,
        expected_transition_manifest_sha256=expected_transition_manifest_sha256,
        expected_script_resolution_sha256=expected_script_resolution_sha256,
        require_reviewed=True,
    )

    query: dict[str, Any] = {}
    if transition_id is not None:
        query["transitionId"] = _transition_id(transition_id, "transition_id")
    if transition_kind is not None:
        if transition_kind not in TRANSITION_KINDS:
            raise RouteInteractionError(f"Unsupported transition kind: {transition_kind!r}")
        query["transitionKind"] = transition_kind
    if transition_evidence_source is not None:
        if transition_evidence_source not in TRANSITION_EVIDENCE_SOURCES:
            raise RouteInteractionError(f"Unsupported transition evidence source: {transition_evidence_source!r}")
        query["transitionEvidenceSource"] = transition_evidence_source
    if position is not None:
        query["position"] = list(_position(position, "position"))
    for field, value in (
        ("itemId", item_id),
        ("actionId", action_id),
        ("uniqueId", unique_id),
        ("houseDoorId", house_door_id),
    ):
        if value is not None:
            query[field] = _uint16(value, field)
    if script_status is not None:
        if not isinstance(script_status, str) or not script_status:
            raise RouteInteractionError("script_status must be a non-empty string")
        query["scriptStatus"] = script_status

    if "transitionId" not in query and "position" not in query:
        raise RouteInteractionError("Interaction resolution requires transition_id or exact position evidence")

    matches = [entry for entry in registry["entries"] if _selector_matches(entry["selector"], query)]
    matches.sort(key=lambda entry: entry["id"])
    if not matches:
        return _resolution(
            query=query,
            execution_status="blocked",
            blockers=[{"code": "interaction-not-reviewed"}],
        )
    if len(matches) > 1:
        return _resolution(
            query=query,
            execution_status="blocked",
            blockers=[{"code": "interaction-selector-ambiguous", "entryIds": [entry["id"] for entry in matches]}],
            matched_entry_ids=[entry["id"] for entry in matches],
        )

    entry = matches[0]
    requirements = entry["requirements"]
    blockers: list[dict[str, Any]] = []

    if "transitionId" in entry["selector"]:
        allowed_kinds = requirements["transitionKinds"]
        if transition_kind is None:
            blockers.append({"code": "transition-kind-required"})
        elif transition_kind not in allowed_kinds:
            blockers.append(
                {"code": "transition-kind-not-allowed", "actual": transition_kind, "allowed": copy.deepcopy(allowed_kinds)}
            )

        allowed_sources = requirements["transitionEvidenceSources"]
        if transition_evidence_source is None:
            blockers.append({"code": "transition-evidence-source-required"})
        elif transition_evidence_source not in allowed_sources:
            blockers.append(
                {
                    "code": "transition-evidence-source-not-allowed",
                    "actual": transition_evidence_source,
                    "allowed": copy.deepcopy(allowed_sources),
                }
            )
        elif transition_evidence_source == "transitionManifest" and expected_transition_manifest_sha256 is None:
            blockers.append({"code": "transition-manifest-provenance-required"})

    script_requirement = requirements["scriptResolution"]
    if script_requirement["required"]:
        if expected_script_resolution_sha256 is None:
            blockers.append({"code": "script-resolution-provenance-required"})
        if script_status is None:
            blockers.append({"code": "script-status-required"})
        elif script_status in FAIL_CLOSED_SCRIPT_STATUSES:
            blockers.append({"code": "script-status-fail-closed", "status": script_status})
        elif script_status not in script_requirement["allowedStatuses"]:
            blockers.append(
                {
                    "code": "script-status-not-allowed",
                    "status": script_status,
                    "allowed": copy.deepcopy(script_requirement["allowedStatuses"]),
                }
            )

    if blockers:
        return _resolution(query=query, execution_status="blocked", blockers=blockers, entry=entry)
    return _resolution(query=query, execution_status="executable", blockers=[], entry=entry)


def _parse_position(value: str) -> list[int]:
    parts = value.split(",")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("position must use x,y,z")
    try:
        result = [int(part) for part in parts]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("position must use integer x,y,z") from exc
    try:
        return list(_position(result, "position"))
    except RouteInteractionError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and resolve reviewed OTBM route interaction registries")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="Validate a route interaction registry")
    validate.add_argument("registry", type=Path)
    validate.add_argument("--map-sha256")
    validate.add_argument("--world-index-sha256")
    validate.add_argument("--transition-manifest-sha256")
    validate.add_argument("--script-resolution-sha256")
    validate.add_argument("--require-reviewed", action="store_true")

    resolve = commands.add_parser("resolve", help="Resolve one reviewed physical interaction")
    resolve.add_argument("registry", type=Path)
    resolve.add_argument("--map-sha256", required=True)
    resolve.add_argument("--world-index-sha256", required=True)
    resolve.add_argument("--transition-manifest-sha256")
    resolve.add_argument("--script-resolution-sha256")
    resolve.add_argument("--transition-id")
    resolve.add_argument("--transition-kind", choices=sorted(TRANSITION_KINDS))
    resolve.add_argument("--transition-evidence-source", choices=sorted(TRANSITION_EVIDENCE_SOURCES))
    resolve.add_argument("--position", type=_parse_position)
    resolve.add_argument("--item-id", type=int)
    resolve.add_argument("--action-id", type=int)
    resolve.add_argument("--unique-id", type=int)
    resolve.add_argument("--house-door-id", type=int)
    resolve.add_argument("--script-status")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "validate":
            payload = load_registry(
                args.registry,
                expected_source_map_sha256=args.map_sha256,
                expected_world_index_sha256=args.world_index_sha256,
                expected_transition_manifest_sha256=args.transition_manifest_sha256,
                expected_script_resolution_sha256=args.script_resolution_sha256,
                require_reviewed=args.require_reviewed,
            )
        elif args.command == "resolve":
            registry = load_registry(args.registry)
            payload = resolve_interaction(
                registry,
                expected_source_map_sha256=args.map_sha256,
                expected_world_index_sha256=args.world_index_sha256,
                transition_id=args.transition_id,
                transition_kind=args.transition_kind,
                transition_evidence_source=args.transition_evidence_source,
                position=args.position,
                item_id=args.item_id,
                action_id=args.action_id,
                unique_id=args.unique_id,
                house_door_id=args.house_door_id,
                script_status=args.script_status,
                expected_transition_manifest_sha256=args.transition_manifest_sha256,
                expected_script_resolution_sha256=args.script_resolution_sha256,
            )
        else:
            raise AssertionError(args.command)
    except (FileNotFoundError, OSError, RouteInteractionError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
