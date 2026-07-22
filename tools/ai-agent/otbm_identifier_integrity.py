from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from otbm_reachability_transition import _transition_from_manifest
from otbm_reachability_types import ReachabilityError
from otbm_route_interactions import RouteInteractionError, validate_registry

POLICY_FORMAT = "canary-otbm-identifier-integrity-policy-v1"
REPORT_FORMAT = "canary-otbm-identifier-integrity-v1"
SCHEMA_VERSION = 1
MAX_EXPECTATIONS = 4096
MAX_ROLE_BINDINGS = 8192
MAX_REVIEW_REFERENCES = 32

NAMESPACES = frozenset({"actionId", "uniqueId", "houseDoorId"})
EXPECTATIONS = frozenset({"unique", "reviewed-reuse"})
SCRIPT_BLOCKING_STATUSES = frozenset({"conflicting"})
SCRIPT_UNRESOLVED_STATUSES = frozenset({"unresolved", "partially-resolved", "referenced-only"})
_MECHANIC_SELECTOR_FIELDS = ("itemId", "actionId", "uniqueId", "houseDoorId")


class IdentifierIntegrityError(ValueError):
    pass


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise IdentifierIntegrityError(f"{label} must be an object")
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
        raise IdentifierIntegrityError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        raise IdentifierIntegrityError(f"{label} has unknown fields: {', '.join(sorted(unknown))}")


def _identifier(value: Any, label: str, maximum: int = 240) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= maximum:
        raise IdentifierIntegrityError(f"{label} must be a non-empty string of at most {maximum} characters")
    return value


def _hash64(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise IdentifierIntegrityError(f"{label} must be a lowercase 64-character SHA-256")
    return value


def _uint(value: Any, label: str, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= maximum:
        raise IdentifierIntegrityError(f"{label} must be an integer in 0..{maximum}")
    return value


def _review(value: Any, label: str) -> None:
    review = _mapping(value, label)
    _exact_keys(review, label=label, required={"status", "references"}, optional={"note"})
    if review["status"] != "reviewed":
        raise IdentifierIntegrityError(f"{label}.status must be reviewed")
    references = review["references"]
    if not isinstance(references, list) or not 1 <= len(references) <= MAX_REVIEW_REFERENCES:
        raise IdentifierIntegrityError(f"{label}.references must contain 1..{MAX_REVIEW_REFERENCES} entries")
    seen: set[str] = set()
    for index, reference in enumerate(references):
        if not isinstance(reference, str) or not 1 <= len(reference) <= 512:
            raise IdentifierIntegrityError(f"{label}.references[{index}] must be a non-empty bounded string")
        if reference in seen:
            raise IdentifierIntegrityError(f"{label}.references contains duplicate reference {reference!r}")
        seen.add(reference)
    note = review.get("note")
    if note is not None and (not isinstance(note, str) or len(note) > 2000):
        raise IdentifierIntegrityError(f"{label}.note must be a string of at most 2000 characters")


def _provenance_pin(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None:
        if nullable:
            return None
        raise IdentifierIntegrityError(f"{label} must not be null")
    record = _mapping(value, label)
    _exact_keys(record, label=label, required={"sha256"})
    return _hash64(record["sha256"], f"{label}.sha256")


def _validate_scope(value: Any, label: str, namespace: str) -> dict[str, Any]:
    scope = _mapping(value, label)
    kind = scope.get("kind")
    if kind == "world":
        _exact_keys(scope, label=label, required={"kind"})
        return {"kind": "world"}
    if kind == "house":
        _exact_keys(scope, label=label, required={"kind", "houseId"})
        house_id = _uint(scope["houseId"], f"{label}.houseId", 0xFFFFFFFF)
        return {"kind": "house", "houseId": house_id}
    raise IdentifierIntegrityError(f"{label}.kind must be world or house")


def validate_policy(document: Any) -> dict[str, Any]:
    root = _mapping(document, "policy")
    _exact_keys(
        root,
        label="policy",
        required={"format", "schemaVersion", "provenance", "expectations", "placementRoles"},
    )
    if root["format"] != POLICY_FORMAT:
        raise IdentifierIntegrityError(f"Unsupported identifier-integrity policy format: {root['format']!r}")
    if root["schemaVersion"] != SCHEMA_VERSION:
        raise IdentifierIntegrityError(f"Unsupported identifier-integrity schema version: {root['schemaVersion']!r}")

    provenance = _mapping(root["provenance"], "policy.provenance")
    _exact_keys(
        provenance,
        label="policy.provenance",
        required={"sourceMap", "worldIndex", "scriptResolution", "transitionManifest", "interactionRegistry"},
    )
    _provenance_pin(provenance["sourceMap"], "policy.provenance.sourceMap")
    _provenance_pin(provenance["worldIndex"], "policy.provenance.worldIndex")
    _provenance_pin(provenance["scriptResolution"], "policy.provenance.scriptResolution", nullable=True)
    _provenance_pin(provenance["transitionManifest"], "policy.provenance.transitionManifest", nullable=True)
    _provenance_pin(provenance["interactionRegistry"], "policy.provenance.interactionRegistry", nullable=True)

    expectations = root["expectations"]
    roles = root["placementRoles"]
    if not isinstance(expectations, list) or len(expectations) > MAX_EXPECTATIONS:
        raise IdentifierIntegrityError(f"policy.expectations must contain at most {MAX_EXPECTATIONS} entries")
    if not isinstance(roles, list) or len(roles) > MAX_ROLE_BINDINGS:
        raise IdentifierIntegrityError(f"policy.placementRoles must contain at most {MAX_ROLE_BINDINGS} entries")

    seen_ids: set[str] = set()
    seen_expectations: set[str] = set()
    for index, raw in enumerate(expectations):
        label = f"policy.expectations[{index}]"
        entry = _mapping(raw, label)
        _exact_keys(
            entry,
            label=label,
            required={"id", "namespace", "value", "scope", "expectation", "evidence"},
        )
        entry_id = _identifier(entry["id"], f"{label}.id")
        if entry_id in seen_ids:
            raise IdentifierIntegrityError(f"Duplicate policy entry ID: {entry_id}")
        seen_ids.add(entry_id)
        namespace = entry["namespace"]
        if namespace not in NAMESPACES:
            raise IdentifierIntegrityError(f"{label}.namespace is unsupported: {namespace!r}")
        maximum = 0xFF if namespace == "houseDoorId" else 0xFFFF
        _uint(entry["value"], f"{label}.value", maximum)
        scope = _validate_scope(entry["scope"], f"{label}.scope", namespace)
        if namespace == "houseDoorId" and scope["kind"] != "house":
            raise IdentifierIntegrityError(f"{label}.scope must be house for houseDoorId expectations")
        if entry["expectation"] not in EXPECTATIONS:
            raise IdentifierIntegrityError(f"{label}.expectation is unsupported: {entry['expectation']!r}")
        _review(entry["evidence"], f"{label}.evidence")
        canonical = json.dumps(
            {"namespace": namespace, "value": entry["value"], "scope": scope},
            sort_keys=True,
            separators=(",", ":"),
        )
        if canonical in seen_expectations:
            raise IdentifierIntegrityError(f"Duplicate policy expectation selector: {canonical}")
        seen_expectations.add(canonical)

    seen_role_ordinals: set[int] = set()
    for index, raw in enumerate(roles):
        label = f"policy.placementRoles[{index}]"
        entry = _mapping(raw, label)
        _exact_keys(
            entry,
            label=label,
            required={"id", "placementOrdinal", "namespace", "value", "role", "compatibilityClass", "evidence"},
        )
        entry_id = _identifier(entry["id"], f"{label}.id")
        if entry_id in seen_ids:
            raise IdentifierIntegrityError(f"Duplicate policy entry ID: {entry_id}")
        seen_ids.add(entry_id)
        ordinal = _uint(entry["placementOrdinal"], f"{label}.placementOrdinal", 0xFFFFFFFF)
        if ordinal in seen_role_ordinals:
            raise IdentifierIntegrityError(f"Duplicate reviewed placement role for placementOrdinal {ordinal}")
        seen_role_ordinals.add(ordinal)
        namespace = entry["namespace"]
        if namespace not in NAMESPACES:
            raise IdentifierIntegrityError(f"{label}.namespace is unsupported: {namespace!r}")
        maximum = 0xFF if namespace == "houseDoorId" else 0xFFFF
        _uint(entry["value"], f"{label}.value", maximum)
        _identifier(entry["role"], f"{label}.role", 160)
        _identifier(entry["compatibilityClass"], f"{label}.compatibilityClass", 160)
        _review(entry["evidence"], f"{label}.evidence")

    return copy.deepcopy(dict(root))


def _pin(policy: Mapping[str, Any], key: str) -> str | None:
    value = policy["provenance"][key]
    return None if value is None else str(value["sha256"])


def _require_optional_pin(policy: Mapping[str, Any], key: str, actual: str | None, label: str) -> None:
    expected = _pin(policy, key)
    if (expected is None) != (actual is None):
        raise IdentifierIntegrityError(f"{label} presence does not match reviewed policy provenance")
    if expected is not None and expected != actual:
        raise IdentifierIntegrityError(f"{label} SHA-256 does not match reviewed policy provenance")


def _inventory(index: Any) -> tuple[list[dict[str, Any]], dict[str, dict[int, list[dict[str, Any]]]]]:
    placements: list[dict[str, Any]] = []
    by_namespace: dict[str, dict[int, list[dict[str, Any]]]] = {
        namespace: defaultdict(list) for namespace in NAMESPACES
    }
    for mechanic_index in range(int(index.header.mechanic_count)):
        ordinal, _ = index.mechanic_record(mechanic_index)
        placement = dict(index.placement(ordinal))
        tile = index.tile(int(placement["tileIndex"]))
        placement["houseId"] = getattr(tile, "house_id", None)
        placements.append(placement)
        for namespace in NAMESPACES:
            value = placement.get(namespace)
            if isinstance(value, int) and not isinstance(value, bool):
                by_namespace[namespace][value].append(placement)
    placements.sort(key=lambda entry: int(entry["placementOrdinal"]))
    for namespace in NAMESPACES:
        for value in by_namespace[namespace]:
            by_namespace[namespace][value].sort(key=lambda entry: int(entry["placementOrdinal"]))
    return placements, by_namespace


def _scope_matches(placement: Mapping[str, Any], scope: Mapping[str, Any]) -> bool:
    return scope["kind"] == "world" or placement.get("houseId") == scope.get("houseId")


def _placement_sample(placement: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "placementOrdinal": placement.get("placementOrdinal"),
        "itemId": placement.get("itemId"),
        "position": placement.get("position"),
        "houseId": placement.get("houseId"),
        "actionId": placement.get("actionId"),
        "uniqueId": placement.get("uniqueId"),
        "houseDoorId": placement.get("houseDoorId"),
    }


def _unreviewed_reuse(by_namespace: Mapping[str, Mapping[int, Sequence[Mapping[str, Any]]]], policy: Mapping[str, Any]) -> list[dict[str, Any]]:
    reviewed: set[tuple[str, int, str, int | None]] = set()
    for entry in policy["expectations"]:
        scope = entry["scope"]
        reviewed.add((entry["namespace"], int(entry["value"]), scope["kind"], scope.get("houseId")))

    results: list[dict[str, Any]] = []
    for namespace in ("actionId", "uniqueId"):
        for value, placements in sorted(by_namespace[namespace].items()):
            if len(placements) <= 1 or (namespace, value, "world", None) in reviewed:
                continue
            results.append(
                {
                    "namespace": namespace,
                    "value": value,
                    "scope": {"kind": "world"},
                    "placementCount": len(placements),
                    "classification": "review-required",
                    "samplePlacements": [_placement_sample(entry) for entry in placements[:20]],
                    "reason": "repetition-alone-does-not-prove-conflict-or-intentional-reuse",
                }
            )
    for value, placements in sorted(by_namespace["houseDoorId"].items()):
        by_house: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
        for placement in placements:
            house_id = placement.get("houseId")
            if isinstance(house_id, int):
                by_house[house_id].append(placement)
        for house_id, house_placements in sorted(by_house.items()):
            if len(house_placements) <= 1 or ("houseDoorId", value, "house", house_id) in reviewed:
                continue
            results.append(
                {
                    "namespace": "houseDoorId",
                    "value": value,
                    "scope": {"kind": "house", "houseId": house_id},
                    "placementCount": len(house_placements),
                    "classification": "review-required",
                    "samplePlacements": [_placement_sample(entry) for entry in house_placements[:20]],
                    "reason": "same-house-door-id-repetition-requires-reviewed-uniqueness-or-reuse-intent",
                }
            )
    return results


def _expectation_results(policy: Mapping[str, Any], by_namespace: Mapping[str, Mapping[int, Sequence[Mapping[str, Any]]]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for expectation in policy["expectations"]:
        namespace = expectation["namespace"]
        value = int(expectation["value"])
        scope = expectation["scope"]
        matches = [entry for entry in by_namespace[namespace].get(value, []) if _scope_matches(entry, scope)]
        wanted = expectation["expectation"]
        if wanted == "unique" and len(matches) > 1:
            classification = "conflicting"
            reason = "reviewed-unique-expectation-has-multiple-placements"
        elif wanted == "reviewed-reuse":
            classification = "reviewed-reuse"
            reason = "repeated-selector-is-explicitly-reviewed-for-reuse"
        else:
            classification = "confirmed"
            reason = "reviewed-unique-expectation-not-violated"
        results.append(
            {
                "expectationId": expectation["id"],
                "namespace": namespace,
                "value": value,
                "scope": copy.deepcopy(scope),
                "expectation": wanted,
                "placementCount": len(matches),
                "classification": classification,
                "reason": reason,
                "evidence": copy.deepcopy(expectation["evidence"]),
                "samplePlacements": [_placement_sample(entry) for entry in matches[:20]],
            }
        )
    return results


def _script_evidence(report: Mapping[str, Any] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if report is None:
        return [], []
    if report.get("format") != "canary-otbm-script-resolution-v1":
        raise IdentifierIntegrityError("Unsupported Script Resolution report format")
    identifiers = report.get("identifiers")
    if not isinstance(identifiers, Mapping):
        raise IdentifierIntegrityError("Script Resolution report is missing identifiers")
    conflicts: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for namespace in ("actionId", "uniqueId"):
        entries = identifiers.get(namespace)
        if not isinstance(entries, list):
            raise IdentifierIntegrityError(f"Script Resolution identifiers.{namespace} must be an array")
        for entry in entries:
            if not isinstance(entry, Mapping):
                continue
            status = entry.get("status")
            payload = {
                "namespace": namespace,
                "value": entry.get("value"),
                "status": status,
                "placements": entry.get("placements"),
                "handlers": copy.deepcopy(entry.get("handlers", [])),
                "samplePositions": copy.deepcopy(entry.get("samplePositions", [])),
            }
            if status in SCRIPT_BLOCKING_STATUSES:
                payload["reason"] = "script-resolution-conflicting"
                conflicts.append(payload)
            elif status in SCRIPT_UNRESOLVED_STATUSES:
                payload["reason"] = "script-resolution-not-fully-resolved"
                unresolved.append(payload)
    return conflicts, unresolved


def _transition_conflicts(document: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if document is None:
        return []
    if document.get("format") != "canary-otbm-transition-manifest-v1":
        raise IdentifierIntegrityError("Unsupported transition manifest format")
    transitions = document.get("transitions")
    if not isinstance(transitions, list):
        raise IdentifierIntegrityError("Transition manifest is missing transitions")
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for index, raw in enumerate(transitions):
        if not isinstance(raw, Mapping):
            raise IdentifierIntegrityError(f"Transition manifest entry {index} must be an object")
        transition_id = raw.get("id")
        if not isinstance(transition_id, str) or not transition_id:
            raise IdentifierIntegrityError(f"Transition manifest entry {index} has invalid id")
        grouped[transition_id].append(raw)

    conflicts: list[dict[str, Any]] = []
    for transition_id, entries in sorted(grouped.items()):
        if len(entries) <= 1:
            continue
        canonical = {json.dumps(dict(entry), sort_keys=True, separators=(",", ":")) for entry in entries}
        conflicts.append(
            {
                "transitionId": transition_id,
                "occurrences": len(entries),
                "classification": "conflicting",
                "reason": "duplicate-transition-id-incompatible" if len(canonical) > 1 else "duplicate-transition-id-identical",
                "definitions": [copy.deepcopy(dict(entry)) for entry in entries[:20]],
            }
        )

    seen_ids: set[str] = set()
    for raw in transitions:
        transition_id = str(raw["id"])
        if len(grouped[transition_id]) > 1:
            if transition_id in seen_ids:
                continue
            # Validate one representative through the canonical parser contract; duplicate ID evidence is reported above.
        try:
            _transition_from_manifest(dict(raw), seen_ids)
        except ReachabilityError as exc:
            if "Duplicate transition id" in str(exc) and len(grouped[transition_id]) > 1:
                continue
            raise IdentifierIntegrityError(f"Invalid transition manifest evidence: {exc}") from exc
    return conflicts


def _selector_overlap(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any] | None:
    if "transitionId" in left or "transitionId" in right:
        if left.get("transitionId") is not None and left.get("transitionId") == right.get("transitionId"):
            return {"transitionId": left["transitionId"]}
        return None
    if left.get("position") != right.get("position"):
        return None
    witness: dict[str, Any] = {"position": copy.deepcopy(left.get("position"))}
    for field in _MECHANIC_SELECTOR_FIELDS:
        left_value = left.get(field)
        right_value = right.get(field)
        if left_value is not None and right_value is not None and left_value != right_value:
            return None
        value = left_value if left_value is not None else right_value
        if value is not None:
            witness[field] = value
    return witness


def _interaction_ambiguities(document: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if document is None:
        return []
    try:
        registry = validate_registry(document, require_reviewed=True)
    except RouteInteractionError as exc:
        raise IdentifierIntegrityError(f"Invalid reviewed Route Interaction Registry: {exc}") from exc
    entries = registry["entries"]
    results: list[dict[str, Any]] = []
    for left_index, left in enumerate(entries):
        for right in entries[left_index + 1 :]:
            witness = _selector_overlap(left["selector"], right["selector"])
            if witness is None:
                continue
            results.append(
                {
                    "entryIds": sorted([left["id"], right["id"]]),
                    "classification": "conflicting",
                    "reason": "overlapping-reviewed-route-interaction-selectors",
                    "witnessQuery": witness,
                    "selectors": [copy.deepcopy(left["selector"]), copy.deepcopy(right["selector"])],
                }
            )
    results.sort(key=lambda entry: tuple(entry["entryIds"]))
    return results


def _role_conflicts(policy: Mapping[str, Any], placements_by_ordinal: Mapping[int, Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for role in policy["placementRoles"]:
        ordinal = int(role["placementOrdinal"])
        placement = placements_by_ordinal.get(ordinal)
        if placement is None:
            raise IdentifierIntegrityError(f"Reviewed placement role references unknown placementOrdinal {ordinal}")
        namespace = role["namespace"]
        value = int(role["value"])
        if placement.get(namespace) != value:
            raise IdentifierIntegrityError(
                f"Reviewed placement role {role['id']} selector does not match placementOrdinal {ordinal}"
            )
        groups[(namespace, value)].append(dict(role))

    results: list[dict[str, Any]] = []
    for (namespace, value), roles in sorted(groups.items()):
        classes = sorted({entry["compatibilityClass"] for entry in roles})
        if len(classes) <= 1:
            continue
        results.append(
            {
                "namespace": namespace,
                "value": value,
                "classification": "conflicting",
                "reason": "reviewed-incompatible-mechanic-roles",
                "compatibilityClasses": classes,
                "roles": [copy.deepcopy(entry) for entry in sorted(roles, key=lambda item: item["id"])],
            }
        )
    return results


def build_identifier_integrity_report(
    *,
    policy: Mapping[str, Any],
    world_index: Any,
    source_map_sha256: str,
    actual_world_index_sha256: str,
    script_resolution: Mapping[str, Any] | None = None,
    script_resolution_sha256: str | None = None,
    transition_manifest: Mapping[str, Any] | None = None,
    transition_manifest_sha256: str | None = None,
    interaction_registry: Mapping[str, Any] | None = None,
    interaction_registry_sha256: str | None = None,
    input_pins: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    validated_policy = validate_policy(policy)
    source_map_sha256 = _hash64(source_map_sha256, "source_map_sha256")
    actual_world_index_sha256 = _hash64(actual_world_index_sha256, "actual_world_index_sha256")
    if _pin(validated_policy, "sourceMap") != source_map_sha256:
        raise IdentifierIntegrityError("Source-map SHA-256 does not match reviewed policy provenance")
    if _pin(validated_policy, "worldIndex") != actual_world_index_sha256:
        raise IdentifierIntegrityError("World Index SHA-256 does not match reviewed policy provenance")
    _require_optional_pin(validated_policy, "scriptResolution", script_resolution_sha256, "Script Resolution")
    _require_optional_pin(validated_policy, "transitionManifest", transition_manifest_sha256, "transition manifest")
    _require_optional_pin(validated_policy, "interactionRegistry", interaction_registry_sha256, "Route Interaction Registry")
    if (script_resolution is None) != (script_resolution_sha256 is None):
        raise IdentifierIntegrityError("Script Resolution document and SHA-256 must be supplied together")
    if (transition_manifest is None) != (transition_manifest_sha256 is None):
        raise IdentifierIntegrityError("Transition manifest document and SHA-256 must be supplied together")
    if (interaction_registry is None) != (interaction_registry_sha256 is None):
        raise IdentifierIntegrityError("Route Interaction Registry document and SHA-256 must be supplied together")

    placements, by_namespace = _inventory(world_index)
    placements_by_ordinal = {int(entry["placementOrdinal"]): entry for entry in placements}
    expectations = _expectation_results(validated_policy, by_namespace)
    review_required = _unreviewed_reuse(by_namespace, validated_policy)
    script_conflicts, script_unresolved = _script_evidence(script_resolution)
    transition_conflicts = _transition_conflicts(transition_manifest)
    selector_ambiguities = _interaction_ambiguities(interaction_registry)
    role_conflicts = _role_conflicts(validated_policy, placements_by_ordinal)

    conflicts: list[dict[str, Any]] = []
    conflicts.extend(
        {"kind": "identifier-expectation", **copy.deepcopy(entry)}
        for entry in expectations
        if entry["classification"] == "conflicting"
    )
    conflicts.extend({"kind": "script-resolution", **copy.deepcopy(entry)} for entry in script_conflicts)
    conflicts.extend({"kind": "transition-id", **copy.deepcopy(entry)} for entry in transition_conflicts)
    conflicts.extend({"kind": "route-interaction-selector", **copy.deepcopy(entry)} for entry in selector_ambiguities)
    conflicts.extend({"kind": "reviewed-role", **copy.deepcopy(entry)} for entry in role_conflicts)
    conflicts.sort(
        key=lambda entry: (
            entry["kind"],
            str(entry.get("namespace", "")),
            str(entry.get("value", "")),
            str(entry.get("transitionId", "")),
            json.dumps(entry.get("entryIds", []), sort_keys=True),
        )
    )

    repeated_counts = Counter()
    for namespace in NAMESPACES:
        repeated_counts[namespace] = sum(1 for entries in by_namespace[namespace].values() if len(entries) > 1)

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": not conflicts,
        "source": {
            "mapSha256": source_map_sha256,
            "worldIndexSha256": actual_world_index_sha256,
        },
        "policy": {
            "format": POLICY_FORMAT,
            "expectationCount": len(validated_policy["expectations"]),
            "placementRoleCount": len(validated_policy["placementRoles"]),
        },
        "summary": {
            "mechanicPlacements": len(placements),
            "identifierValues": {namespace: len(by_namespace[namespace]) for namespace in sorted(NAMESPACES)},
            "repeatedIdentifierValues": dict(sorted(repeated_counts.items())),
            "reviewedExpectations": len(expectations),
            "reviewedReuse": sum(entry["classification"] == "reviewed-reuse" for entry in expectations),
            "reviewRequired": len(review_required),
            "scriptConflicts": len(script_conflicts),
            "scriptUnresolved": len(script_unresolved),
            "transitionConflicts": len(transition_conflicts),
            "selectorAmbiguities": len(selector_ambiguities),
            "roleConflicts": len(role_conflicts),
            "conflicts": len(conflicts),
        },
        "expectations": expectations,
        "reviewRequired": review_required,
        "scriptConflicts": script_conflicts,
        "scriptUnresolved": script_unresolved,
        "transitionConflicts": transition_conflicts,
        "selectorAmbiguities": selector_ambiguities,
        "roleConflicts": role_conflicts,
        "conflicts": conflicts,
        "inputPins": copy.deepcopy(dict(input_pins or {})),
        "notes": [
            "Repeated action IDs, unique IDs or item IDs are not automatically defects; unreviewed repetition remains review-required unless exact conflict evidence closes the question.",
            "House-door repetition is scoped by exact houseId plus houseDoorId when evaluating reviewed uniqueness intent.",
            "Script Resolution unresolved/partially-resolved/referenced-only states remain unresolved evidence and are not promoted to conflicts by repetition alone.",
            "The report is static evidence only and does not prove runtime behavior, player intent or authorize map repair or identifier renumbering.",
        ],
    }
