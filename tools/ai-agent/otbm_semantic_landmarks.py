#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

REGISTRY_FORMAT = "canary-otbm-semantic-landmarks-v1"
RESOLUTION_FORMAT = "canary-otbm-semantic-landmark-resolution-v1"
SCHEMA_VERSION = 1
MAX_REGIONS = 1024
MAX_LANDMARKS = 4096
MAX_ANCHORS_PER_LANDMARK = 64
MAX_EVIDENCE_REFERENCES = 32
ANCHOR_ROLES = frozenset(
    {
        "route-origin",
        "route-destination",
        "entrance",
        "exit",
        "interaction",
    }
)
_IDENTIFIER_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SemanticLandmarkError(ValueError):
    pass


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SemanticLandmarkError(f"{label} must be an object")
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
        raise SemanticLandmarkError(f"{label} is missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        raise SemanticLandmarkError(f"{label} has unknown fields: {', '.join(sorted(unknown))}")


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= 160 or _IDENTIFIER_RE.fullmatch(value) is None:
        raise SemanticLandmarkError(f"{label} must be a lowercase semantic identifier")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise SemanticLandmarkError(f"{label} must be a lowercase 64-character SHA-256")
    return value


def _position(value: Any, label: str) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise SemanticLandmarkError(f"{label} must be a three-element [x, y, z] array")
    result: list[int] = []
    limits = (0xFFFF, 0xFFFF, 15)
    for index, maximum in enumerate(limits):
        coordinate = value[index]
        if not isinstance(coordinate, int) or isinstance(coordinate, bool) or not 0 <= coordinate <= maximum:
            raise SemanticLandmarkError(f"{label}[{index}] is outside the OTBM coordinate range")
        result.append(coordinate)
    return result[0], result[1], result[2]


def _validate_provenance(value: Any) -> tuple[str, str]:
    provenance = _mapping(value, "provenance")
    _exact_keys(provenance, label="provenance", required={"sourceMap", "worldIndex"})

    source_map = _mapping(provenance["sourceMap"], "provenance.sourceMap")
    _exact_keys(source_map, label="provenance.sourceMap", required={"sha256"})
    source_map_sha256 = _sha256(source_map["sha256"], "provenance.sourceMap.sha256")

    world_index = _mapping(provenance["worldIndex"], "provenance.worldIndex")
    _exact_keys(world_index, label="provenance.worldIndex", required={"sha256"})
    world_index_sha256 = _sha256(world_index["sha256"], "provenance.worldIndex.sha256")
    return source_map_sha256, world_index_sha256


def _validate_anchor_evidence(value: Any, label: str) -> None:
    evidence = _mapping(value, label)
    _exact_keys(evidence, label=label, required={"status", "references"}, optional={"note"})
    if evidence["status"] != "reviewed":
        raise SemanticLandmarkError(f"{label}.status must be reviewed")
    references = evidence["references"]
    if not isinstance(references, list) or not 1 <= len(references) <= MAX_EVIDENCE_REFERENCES:
        raise SemanticLandmarkError(
            f"{label}.references must contain 1..{MAX_EVIDENCE_REFERENCES} reviewed references"
        )
    seen: set[str] = set()
    for index, reference in enumerate(references):
        if not isinstance(reference, str) or not 1 <= len(reference) <= 512:
            raise SemanticLandmarkError(f"{label}.references[{index}] must be a non-empty string")
        if reference in seen:
            raise SemanticLandmarkError(f"{label}.references contains duplicate reference {reference!r}")
        seen.add(reference)
    note = evidence.get("note")
    if note is not None and (not isinstance(note, str) or len(note) > 2000):
        raise SemanticLandmarkError(f"{label}.note must be a string of at most 2000 characters")


def _contains(lower: tuple[int, int, int], upper: tuple[int, int, int], position: tuple[int, int, int]) -> bool:
    return all(lower[index] <= position[index] <= upper[index] for index in range(3))


def validate_registry(
    document: Any,
    *,
    expected_source_map_sha256: str | None = None,
    expected_world_index_sha256: str | None = None,
    require_reviewed: bool = False,
) -> dict[str, Any]:
    root = _mapping(document, "registry")
    _exact_keys(
        root,
        label="registry",
        required={"format", "schemaVersion", "registryStatus", "provenance", "regions", "landmarks"},
    )
    if root["format"] != REGISTRY_FORMAT:
        raise SemanticLandmarkError(f"Unsupported semantic landmark registry format: {root['format']!r}")
    if root["schemaVersion"] != SCHEMA_VERSION:
        raise SemanticLandmarkError(f"Unsupported semantic landmark schema version: {root['schemaVersion']!r}")

    status = root["registryStatus"]
    if status not in {"unbound", "reviewed"}:
        raise SemanticLandmarkError("registryStatus must be unbound or reviewed")
    regions = root["regions"]
    landmarks = root["landmarks"]
    if not isinstance(regions, list) or len(regions) > MAX_REGIONS:
        raise SemanticLandmarkError(f"regions must be an array with at most {MAX_REGIONS} entries")
    if not isinstance(landmarks, list) or len(landmarks) > MAX_LANDMARKS:
        raise SemanticLandmarkError(f"landmarks must be an array with at most {MAX_LANDMARKS} entries")

    if status == "unbound":
        if require_reviewed:
            raise SemanticLandmarkError("Semantic landmark registry is unbound and cannot resolve executable route anchors")
        if root["provenance"] is not None:
            raise SemanticLandmarkError("Unbound semantic landmark registry must use provenance=null")
        if regions or landmarks:
            raise SemanticLandmarkError("Unbound semantic landmark registry must not contain regions or landmarks")
        if expected_source_map_sha256 is not None or expected_world_index_sha256 is not None:
            raise SemanticLandmarkError("Unbound semantic landmark registry cannot satisfy exact provenance expectations")
        return copy.deepcopy(dict(root))

    source_map_sha256, world_index_sha256 = _validate_provenance(root["provenance"])
    if expected_source_map_sha256 is not None:
        expected = _sha256(expected_source_map_sha256, "expected_source_map_sha256")
        if source_map_sha256 != expected:
            raise SemanticLandmarkError("Semantic landmark registry source-map SHA-256 does not match runtime evidence")
    if expected_world_index_sha256 is not None:
        expected = _sha256(expected_world_index_sha256, "expected_world_index_sha256")
        if world_index_sha256 != expected:
            raise SemanticLandmarkError("Semantic landmark registry World Index SHA-256 does not match runtime evidence")

    region_by_id: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {}
    for index, raw_region in enumerate(regions):
        region = _mapping(raw_region, f"regions[{index}]")
        _exact_keys(region, label=f"regions[{index}]", required={"id", "bounds"})
        region_id = _identifier(region["id"], f"regions[{index}].id")
        if region_id in region_by_id:
            raise SemanticLandmarkError(f"Duplicate semantic landmark region ID: {region_id}")
        bounds = _mapping(region["bounds"], f"regions[{index}].bounds")
        _exact_keys(bounds, label=f"regions[{index}].bounds", required={"from", "to"})
        lower = _position(bounds["from"], f"regions[{index}].bounds.from")
        upper = _position(bounds["to"], f"regions[{index}].bounds.to")
        if any(lower[axis] > upper[axis] for axis in range(3)):
            raise SemanticLandmarkError(f"Region {region_id} bounds must be inclusive lower-to-upper coordinates")
        region_by_id[region_id] = (lower, upper)

    landmark_ids: set[str] = set()
    for index, raw_landmark in enumerate(landmarks):
        landmark = _mapping(raw_landmark, f"landmarks[{index}]")
        _exact_keys(landmark, label=f"landmarks[{index}]", required={"id", "regionId", "anchors"})
        landmark_id = _identifier(landmark["id"], f"landmarks[{index}].id")
        if landmark_id in landmark_ids:
            raise SemanticLandmarkError(f"Duplicate semantic landmark ID: {landmark_id}")
        landmark_ids.add(landmark_id)
        region_id = _identifier(landmark["regionId"], f"landmarks[{index}].regionId")
        if region_id not in region_by_id:
            raise SemanticLandmarkError(f"Landmark {landmark_id} references unknown region {region_id}")
        anchors = landmark["anchors"]
        if not isinstance(anchors, list) or not 1 <= len(anchors) <= MAX_ANCHORS_PER_LANDMARK:
            raise SemanticLandmarkError(
                f"Landmark {landmark_id} anchors must contain 1..{MAX_ANCHORS_PER_LANDMARK} entries"
            )
        anchor_ids: set[str] = set()
        lower, upper = region_by_id[region_id]
        for anchor_index, raw_anchor in enumerate(anchors):
            label = f"landmarks[{index}].anchors[{anchor_index}]"
            anchor = _mapping(raw_anchor, label)
            _exact_keys(anchor, label=label, required={"id", "role", "position", "evidence"})
            anchor_id = _identifier(anchor["id"], f"{label}.id")
            if anchor_id in anchor_ids:
                raise SemanticLandmarkError(f"Landmark {landmark_id} contains duplicate anchor ID {anchor_id}")
            anchor_ids.add(anchor_id)
            role = anchor["role"]
            if role not in ANCHOR_ROLES:
                raise SemanticLandmarkError(f"{label}.role is unsupported: {role!r}")
            position = _position(anchor["position"], f"{label}.position")
            if not _contains(lower, upper, position):
                raise SemanticLandmarkError(
                    f"Landmark {landmark_id} anchor {anchor_id} at {list(position)} is outside region {region_id}"
                )
            _validate_anchor_evidence(anchor["evidence"], f"{label}.evidence")

    return copy.deepcopy(dict(root))


def load_registry(
    path: Path,
    *,
    expected_source_map_sha256: str | None = None,
    expected_world_index_sha256: str | None = None,
    require_reviewed: bool = False,
) -> dict[str, Any]:
    candidate = path.expanduser().resolve()
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    try:
        document = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SemanticLandmarkError(f"Cannot read semantic landmark registry {candidate}: {exc}") from exc
    return validate_registry(
        document,
        expected_source_map_sha256=expected_source_map_sha256,
        expected_world_index_sha256=expected_world_index_sha256,
        require_reviewed=require_reviewed,
    )


def resolve_landmark_anchor(
    document: Any,
    *,
    landmark_id: str,
    expected_source_map_sha256: str,
    expected_world_index_sha256: str,
    anchor_id: str | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    if (anchor_id is None) == (role is None):
        raise SemanticLandmarkError("Exactly one of anchor_id or role must be provided")
    landmark_id = _identifier(landmark_id, "landmark_id")
    if anchor_id is not None:
        anchor_id = _identifier(anchor_id, "anchor_id")
    if role is not None and role not in ANCHOR_ROLES:
        raise SemanticLandmarkError(f"Unsupported anchor role: {role!r}")

    registry = validate_registry(
        document,
        expected_source_map_sha256=expected_source_map_sha256,
        expected_world_index_sha256=expected_world_index_sha256,
        require_reviewed=True,
    )
    landmark = next((entry for entry in registry["landmarks"] if entry["id"] == landmark_id), None)
    if landmark is None:
        raise SemanticLandmarkError(f"Unknown semantic landmark ID: {landmark_id}")

    if anchor_id is not None:
        candidates = [anchor for anchor in landmark["anchors"] if anchor["id"] == anchor_id]
        selector = f"anchor {anchor_id}"
    else:
        candidates = [anchor for anchor in landmark["anchors"] if anchor["role"] == role]
        selector = f"role {role}"
    if not candidates:
        raise SemanticLandmarkError(f"Landmark {landmark_id} has no {selector}")
    if len(candidates) != 1:
        raise SemanticLandmarkError(f"Landmark {landmark_id} has ambiguous {selector}; select an exact anchor ID")

    region = next(entry for entry in registry["regions"] if entry["id"] == landmark["regionId"])
    return {
        "format": RESOLUTION_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "provenance": copy.deepcopy(registry["provenance"]),
        "landmarkId": landmark_id,
        "regionId": landmark["regionId"],
        "routingBounds": copy.deepcopy(region["bounds"]),
        "anchor": copy.deepcopy(candidates[0]),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and resolve reviewed OTBM semantic landmark registries")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="Validate a semantic landmark registry")
    validate.add_argument("registry", type=Path)
    validate.add_argument("--map-sha256")
    validate.add_argument("--world-index-sha256")
    validate.add_argument("--require-reviewed", action="store_true")

    resolve = commands.add_parser("resolve", help="Resolve one exact landmark anchor")
    resolve.add_argument("registry", type=Path)
    resolve.add_argument("--landmark", required=True)
    selector = resolve.add_mutually_exclusive_group(required=True)
    selector.add_argument("--anchor")
    selector.add_argument("--role", choices=sorted(ANCHOR_ROLES))
    resolve.add_argument("--map-sha256", required=True)
    resolve.add_argument("--world-index-sha256", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "validate":
            payload = load_registry(
                args.registry,
                expected_source_map_sha256=args.map_sha256,
                expected_world_index_sha256=args.world_index_sha256,
                require_reviewed=args.require_reviewed,
            )
        elif args.command == "resolve":
            registry = load_registry(args.registry)
            payload = resolve_landmark_anchor(
                registry,
                landmark_id=args.landmark,
                anchor_id=args.anchor,
                role=args.role,
                expected_source_map_sha256=args.map_sha256,
                expected_world_index_sha256=args.world_index_sha256,
            )
        else:
            raise AssertionError(args.command)
    except (FileNotFoundError, OSError, SemanticLandmarkError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
