from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from otbm_world_index import WORLD_INDEX_FORMAT, WorldIndex, WorldIndexError, sha256_path

PARITY_FORMAT = "canary-otbm-house-reference-parity-v1"
RESOLVER_FORMAT = "canary-otbm-house-id-resolver-v1"
CLIENT_MANIFEST_FORMAT = "canary-tibia-client-reference-manifest-v1"
STATICDATA_FORMAT = "canary-tibia-staticdata-index-v1"
STATICMAPDATA_FORMAT = "canary-tibia-staticmapdata-index-v1"
SCHEMA_VERSION = 1
CLIENT_HOUSE_NAMESPACE = "client-reference.house-id"
OTBM_HOUSE_NAMESPACE = "otbm.house-id"
STATICMAP_OBJECT_NAMESPACE = "staticmapdata.object_id"
DEFAULT_MAX_JSON_BYTES = 512 * 1024 * 1024
DEFAULT_MAX_HOUSES = 100_000
DEFAULT_MAX_MAPPINGS = 100_000
_SHA256_LENGTH = 64
_ALLOWED_RESOLVER_METHODS = frozenset({"exact-identity", "one-to-one-mapped"})
_ALLOWED_HOUSE_FIELD_ORDERS = frozenset({"unresolved", "legacy", "newer"})
_ALLOWED_STATES = frozenset(
    {
        "conforming",
        "reference-only",
        "otbm-only",
        "mismatch",
        "partial",
        "unresolved-id-space",
        "conflicting",
        "stale-evidence",
    }
)


class HouseReferenceParityError(RuntimeError):
    pass


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise HouseReferenceParityError(f"duplicate JSON object key: {key}")
        output[key] = value
    return output


def _reject_constant(value: str) -> object:
    raise HouseReferenceParityError(f"non-finite JSON number is not supported: {value}")


def _stat_identity(stat: os.stat_result) -> tuple[int, int, int, int]:
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def _read_stable(path: Path, *, max_bytes: int, label: str) -> tuple[bytes, str, Path]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise HouseReferenceParityError(f"{label} must not be a symlink: {path}")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise HouseReferenceParityError(f"{label} does not exist: {path}") from exc
    if not resolved.is_file():
        raise HouseReferenceParityError(f"{label} must be a regular file: {path}")
    before = resolved.stat()
    if before.st_size > max_bytes:
        raise HouseReferenceParityError(f"{label} exceeds {max_bytes} bytes")
    with resolved.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if _stat_identity(before) != _stat_identity(opened):
            raise HouseReferenceParityError(f"{label} changed before read")
        data = stream.read(max_bytes + 1)
        after_open = os.fstat(stream.fileno())
    after = resolved.stat()
    if len(data) > max_bytes:
        raise HouseReferenceParityError(f"{label} exceeds {max_bytes} bytes")
    identities = {_stat_identity(before), _stat_identity(opened), _stat_identity(after_open), _stat_identity(after)}
    if len(identities) != 1 or len(data) != after.st_size:
        raise HouseReferenceParityError(f"{label} changed while reading")
    return data, hashlib.sha256(data).hexdigest(), resolved


def _load_json(path: Path, *, max_bytes: int, label: str) -> tuple[dict[str, object], str, Path]:
    data, digest, resolved = _read_stable(path, max_bytes=max_bytes, label=label)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HouseReferenceParityError(f"{label} must be UTF-8 JSON") from exc
    try:
        payload = json.loads(text, object_pairs_hook=_strict_object, parse_constant=_reject_constant)
    except HouseReferenceParityError:
        raise
    except json.JSONDecodeError as exc:
        raise HouseReferenceParityError(f"{label} must be valid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise HouseReferenceParityError(f"{label} must be a JSON object")
    return payload, digest, resolved


def _require_format(payload: Mapping[str, object], expected: str, label: str) -> None:
    if payload.get("format") != expected:
        raise HouseReferenceParityError(f"{label} format must be {expected}")


def _require_nonempty_text(value: object, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise HouseReferenceParityError(f"{path} must be a non-empty string")
    return value


def _require_sha(value: object, path: str) -> str:
    digest = _require_nonempty_text(value, path).lower()
    if len(digest) != _SHA256_LENGTH:
        raise HouseReferenceParityError(f"{path} must be 64 hexadecimal characters")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise HouseReferenceParityError(f"{path} must be hexadecimal") from exc
    return digest


def _require_uint(value: object, path: str, *, positive: bool = False, maximum: int = 0xFFFFFFFF) -> int:
    minimum = 1 if positive else 0
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise HouseReferenceParityError(f"{path} must be an integer between {minimum} and {maximum}")
    return value


def _require_dict(value: object, path: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise HouseReferenceParityError(f"{path} must be an object")
    return value


def _require_list(value: object, path: str) -> list[object]:
    if not isinstance(value, list):
        raise HouseReferenceParityError(f"{path} must be an array")
    return value


def _selected_input(manifest: Mapping[str, object], input_id: str) -> Mapping[str, object]:
    selected = _require_list(manifest.get("selectedInputs"), "manifest.selectedInputs")
    matches = [row for row in selected if isinstance(row, dict) and row.get("id") == input_id]
    if len(matches) != 1:
        raise HouseReferenceParityError(f"manifest must contain exactly one selected input with id {input_id}")
    entry = matches[0]
    _require_nonempty_text(entry.get("path"), f"manifest.selectedInputs[{input_id}].path")
    _require_uint(entry.get("sizeBytes"), f"manifest.selectedInputs[{input_id}].sizeBytes")
    _require_sha(entry.get("sha256"), f"manifest.selectedInputs[{input_id}].sha256")
    return entry


def _validate_reference_index(
    index: Mapping[str, object],
    *,
    expected_format: str,
    label: str,
    manifest_sha256: str,
    reference_id: str,
    manifest: Mapping[str, object],
) -> None:
    _require_format(index, expected_format, label)
    source = _require_dict(index.get("source"), f"{label}.source")
    if _require_sha(source.get("manifestSha256"), f"{label}.source.manifestSha256") != manifest_sha256:
        raise HouseReferenceParityError(f"{label} is stale: manifest SHA-256 does not match")
    if _require_nonempty_text(source.get("referenceId"), f"{label}.source.referenceId") != reference_id:
        raise HouseReferenceParityError(f"{label} is stale: referenceId does not match")
    input_id = _require_nonempty_text(source.get("inputId"), f"{label}.source.inputId")
    manifest_entry = _selected_input(manifest, input_id)
    if _require_sha(source.get("sha256"), f"{label}.source.sha256") != str(manifest_entry["sha256"]).lower():
        raise HouseReferenceParityError(f"{label} source SHA-256 does not match client manifest")
    if _require_uint(source.get("sizeBytes"), f"{label}.source.sizeBytes") != manifest_entry["sizeBytes"]:
        raise HouseReferenceParityError(f"{label} source size does not match client manifest")
    if _require_nonempty_text(source.get("manifestPath"), f"{label}.source.manifestPath") != manifest_entry["path"]:
        raise HouseReferenceParityError(f"{label} source path does not match client manifest")


def _validate_world_manifest(
    payload: Mapping[str, object],
    *,
    manifest_sha256: str,
    index_path: Path,
) -> dict[str, object]:
    _require_format(payload, WORLD_INDEX_FORMAT, "world manifest")
    index_meta = _require_dict(payload.get("index"), "world manifest.index")
    source_meta = _require_dict(payload.get("source"), "world manifest.source")
    expected_index_sha = _require_sha(index_meta.get("sha256"), "world manifest.index.sha256")
    expected_index_size = _require_uint(index_meta.get("size"), "world manifest.index.size")
    source_map_sha = _require_sha(source_meta.get("sha256"), "world manifest.source.sha256")
    source_map_size = _require_uint(source_meta.get("size"), "world manifest.source.size")

    candidate = index_path.expanduser()
    if candidate.is_symlink():
        raise HouseReferenceParityError(f"world index must not be a symlink: {index_path}")
    resolved = candidate.resolve(strict=True)
    before = resolved.stat()
    if before.st_size != expected_index_size:
        raise HouseReferenceParityError("world index size does not match its manifest")
    actual_sha = sha256_path(resolved)
    after = resolved.stat()
    if _stat_identity(before) != _stat_identity(after):
        raise HouseReferenceParityError("world index changed while hashing")
    if actual_sha != expected_index_sha:
        raise HouseReferenceParityError("world index SHA-256 does not match its manifest")

    try:
        with WorldIndex(resolved) as world:
            header = world.header_json()
    except (OSError, WorldIndexError) as exc:
        raise HouseReferenceParityError(f"world index validation failed: {exc}") from exc
    if header["binary"]["fileSize"] != expected_index_size:
        raise HouseReferenceParityError("world index binary size disagrees with its manifest")
    if header["sourceMapSize"] != source_map_size:
        raise HouseReferenceParityError("world index source-map size disagrees with its manifest")
    if payload.get("summary") != header["summary"]:
        raise HouseReferenceParityError("world index summary disagrees with its manifest")
    if payload.get("otbm") != header["otbm"]:
        raise HouseReferenceParityError("world index OTBM header disagrees with its manifest")
    return {
        "manifestSha256": manifest_sha256,
        "indexSha256": actual_sha,
        "indexSizeBytes": expected_index_size,
        "sourceMapSha256": source_map_sha,
        "sourceMapSizeBytes": source_map_size,
        "summary": header["summary"],
        "otbm": header["otbm"],
    }


def _validate_staticdata_house_contract(index: Mapping[str, object]) -> dict[str, object]:
    schema_version = _require_uint(index.get("schemaVersion"), "StaticData index.schemaVersion", positive=True)
    if schema_version < 2:
        raise HouseReferenceParityError(
            "StaticData index schemaVersion must be at least 2 so HouseData field order is explicit"
        )
    source = _require_dict(index.get("source"), "StaticData index.source")
    categories = _require_dict(index.get("categories"), "StaticData index.categories")
    houses = _require_dict(categories.get("houses"), "StaticData index.categories.houses")
    policy = _require_dict(index.get("policy"), "StaticData index.policy")
    source_order = _require_nonempty_text(source.get("houseFieldOrder"), "StaticData index.source.houseFieldOrder")
    category_order = _require_nonempty_text(
        houses.get("houseFieldOrder"), "StaticData index.categories.houses.houseFieldOrder"
    )
    policy_order = _require_nonempty_text(
        policy.get("houseFieldOrderResolution"), "StaticData index.policy.houseFieldOrderResolution"
    )
    if source_order not in _ALLOWED_HOUSE_FIELD_ORDERS:
        raise HouseReferenceParityError(f"unsupported StaticData houseFieldOrder: {source_order}")
    if source_order != category_order or source_order != policy_order:
        raise HouseReferenceParityError("StaticData houseFieldOrder declarations disagree")
    evidence = _require_dict(source.get("houseFieldOrderEvidence"), "StaticData index.source.houseFieldOrderEvidence")
    if source_order == "unresolved":
        if evidence.get("state") != "unresolved":
            raise HouseReferenceParityError("unresolved StaticData house field order requires unresolved evidence")
    else:
        if evidence.get("state") != "reviewed":
            raise HouseReferenceParityError("resolved StaticData house field order requires reviewed evidence")
        _require_nonempty_text(evidence.get("reviewId"), "StaticData index.source.houseFieldOrderEvidence.reviewId")
        _require_nonempty_text(evidence.get("statement"), "StaticData index.source.houseFieldOrderEvidence.statement")
    return {
        "schemaVersion": schema_version,
        "schemaFamily": _require_nonempty_text(source.get("schemaFamily"), "StaticData index.source.schemaFamily"),
        "houseFieldOrder": source_order,
        "houseFieldOrderEvidence": evidence,
    }


def _load_inputs(
    *,
    client_manifest_path: Path,
    staticdata_index_path: Path,
    staticmapdata_index_path: Path,
    world_index_path: Path,
    world_manifest_path: Path,
    max_json_bytes: int,
) -> dict[str, object]:
    if not isinstance(max_json_bytes, int) or isinstance(max_json_bytes, bool) or max_json_bytes <= 0:
        raise HouseReferenceParityError("max_json_bytes must be positive")
    manifest, manifest_sha, manifest_resolved = _load_json(
        client_manifest_path, max_bytes=max_json_bytes, label="client manifest"
    )
    staticdata, staticdata_sha, staticdata_resolved = _load_json(
        staticdata_index_path, max_bytes=max_json_bytes, label="StaticData index"
    )
    staticmap, staticmap_sha, staticmap_resolved = _load_json(
        staticmapdata_index_path, max_bytes=max_json_bytes, label="StaticMapData index"
    )
    world_manifest, world_manifest_sha, world_manifest_resolved = _load_json(
        world_manifest_path, max_bytes=max_json_bytes, label="world manifest"
    )
    paths = [manifest_resolved, staticdata_resolved, staticmap_resolved, world_manifest_resolved, world_index_path.resolve()]
    if len(set(paths)) != len(paths):
        raise HouseReferenceParityError("required input files must be distinct")
    _require_format(manifest, CLIENT_MANIFEST_FORMAT, "client manifest")
    reference_id = _require_nonempty_text(manifest.get("referenceId"), "manifest.referenceId")
    _validate_reference_index(
        staticdata,
        expected_format=STATICDATA_FORMAT,
        label="StaticData index",
        manifest_sha256=manifest_sha,
        reference_id=reference_id,
        manifest=manifest,
    )
    _validate_reference_index(
        staticmap,
        expected_format=STATICMAPDATA_FORMAT,
        label="StaticMapData index",
        manifest_sha256=manifest_sha,
        reference_id=reference_id,
        manifest=manifest,
    )
    staticdata_house_contract = _validate_staticdata_house_contract(staticdata)
    object_namespace = _require_dict(staticmap.get("objectIdNamespace"), "StaticMapData index.objectIdNamespace")
    if object_namespace.get("name") != STATICMAP_OBJECT_NAMESPACE:
        raise HouseReferenceParityError("StaticMapData object-ID namespace is unsupported")
    if object_namespace.get("resolution") != "unresolved" or object_namespace.get("otbmItemIdEquivalent") is not False:
        raise HouseReferenceParityError("StaticMapData object-ID namespace must remain unresolved")
    world = _validate_world_manifest(
        world_manifest, manifest_sha256=world_manifest_sha, index_path=world_index_path
    )
    return {
        "manifest": manifest,
        "manifestSha256": manifest_sha,
        "referenceId": reference_id,
        "staticdata": staticdata,
        "staticdataSha256": staticdata_sha,
        "staticdataHouseContract": staticdata_house_contract,
        "staticmap": staticmap,
        "staticmapSha256": staticmap_sha,
        "worldManifest": world_manifest,
        "worldManifestSha256": world_manifest_sha,
        "world": world,
        "worldIndexPath": world_index_path.expanduser().resolve(),
    }


def _house_records_staticdata(index: Mapping[str, object], *, max_houses: int) -> tuple[dict[int, dict[str, object]], set[int]]:
    categories = _require_dict(index.get("categories"), "StaticData index.categories")
    houses = _require_dict(categories.get("houses"), "StaticData index.categories.houses")
    records = _require_list(houses.get("records"), "StaticData index.categories.houses.records")
    if len(records) > max_houses:
        raise HouseReferenceParityError(f"StaticData house count exceeds {max_houses}")
    output: dict[int, dict[str, object]] = {}
    conflicts: set[int] = set()
    for ordinal, raw in enumerate(records, start=1):
        record = _require_dict(raw, f"StaticData houses[{ordinal}]")
        if "id" not in record:
            continue
        house_id = _require_uint(record["id"], f"StaticData houses[{ordinal}].id", positive=True)
        if house_id in output:
            conflicts.add(house_id)
        else:
            output[house_id] = record
    return output, conflicts


def _house_records_staticmap(index: Mapping[str, object], *, max_houses: int) -> tuple[dict[int, dict[str, object]], set[int]]:
    records = _require_list(index.get("houses"), "StaticMapData index.houses")
    if len(records) > max_houses:
        raise HouseReferenceParityError(f"StaticMapData house count exceeds {max_houses}")
    output: dict[int, dict[str, object]] = {}
    conflicts: set[int] = set()
    for ordinal, raw in enumerate(records, start=1):
        record = _require_dict(raw, f"StaticMapData houses[{ordinal}]")
        if "houseId" not in record:
            continue
        house_id = _require_uint(record["houseId"], f"StaticMapData houses[{ordinal}].houseId", positive=True)
        if house_id in output:
            conflicts.add(house_id)
        else:
            output[house_id] = record
    return output, conflicts


def _position(record: Mapping[str, object], path: str) -> tuple[int, int, int] | None:
    raw = record.get("position")
    if raw is None:
        return None
    value = _require_dict(raw, path)
    if not {"x", "y", "z"}.issubset(value):
        return None
    return (
        _require_uint(value["x"], f"{path}.x", maximum=0xFFFF),
        _require_uint(value["y"], f"{path}.y", maximum=0xFFFF),
        _require_uint(value["z"], f"{path}.z", maximum=15),
    )


def _provenance(inputs: Mapping[str, object]) -> dict[str, object]:
    world = inputs["world"]
    assert isinstance(world, dict)
    return {
        "clientReferenceId": inputs["referenceId"],
        "clientManifestSha256": inputs["manifestSha256"],
        "staticdataIndexSha256": inputs["staticdataSha256"],
        "staticdataHouseFieldOrder": inputs["staticdataHouseContract"]["houseFieldOrder"],
        "staticdataHouseFieldOrderEvidence": inputs["staticdataHouseContract"]["houseFieldOrderEvidence"],
        "staticmapdataIndexSha256": inputs["staticmapSha256"],
        "worldIndexManifestSha256": inputs["worldManifestSha256"],
        "worldIndexSha256": world["indexSha256"],
        "sourceMapSha256": world["sourceMapSha256"],
    }


def derive_resolver(
    *,
    client_manifest_path: Path,
    staticdata_index_path: Path,
    staticmapdata_index_path: Path,
    world_index_path: Path,
    world_manifest_path: Path,
    review_id: str,
    review_statement: str,
    max_json_bytes: int = DEFAULT_MAX_JSON_BYTES,
    max_houses: int = DEFAULT_MAX_HOUSES,
) -> tuple[dict[str, object], tuple[Path, ...]]:
    review_id = _require_nonempty_text(review_id, "review_id")
    review_statement = _require_nonempty_text(review_statement, "review_statement")
    inputs = _load_inputs(
        client_manifest_path=client_manifest_path,
        staticdata_index_path=staticdata_index_path,
        staticmapdata_index_path=staticmapdata_index_path,
        world_index_path=world_index_path,
        world_manifest_path=world_manifest_path,
        max_json_bytes=max_json_bytes,
    )
    staticdata = inputs["staticdata"]
    staticmap = inputs["staticmap"]
    assert isinstance(staticdata, dict) and isinstance(staticmap, dict)
    registry, registry_conflicts = _house_records_staticdata(staticdata, max_houses=max_houses)
    layouts, layout_conflicts = _house_records_staticmap(staticmap, max_houses=max_houses)
    client_ids = sorted(set(registry) | set(layouts))
    if len(client_ids) > max_houses:
        raise HouseReferenceParityError(f"combined client house count exceeds {max_houses}")

    mappings: list[dict[str, object]] = []
    unresolved: list[dict[str, object]] = []
    conflicts: list[dict[str, object]] = []
    reverse: dict[int, int] = {}
    with WorldIndex(inputs["worldIndexPath"]) as world:
        for client_id in client_ids:
            if client_id in registry_conflicts or client_id in layout_conflicts:
                conflicts.append(
                    {
                        "clientHouseId": client_id,
                        "reason": "duplicate-client-house-id",
                        "staticdataDuplicate": client_id in registry_conflicts,
                        "staticmapdataDuplicate": client_id in layout_conflicts,
                    }
                )
                continue
            registry_record = registry.get(client_id)
            if registry_record is None:
                unresolved.append({"clientHouseId": client_id, "reason": "missing-staticdata-registry-record"})
                continue
            position = _position(registry_record, f"StaticData house {client_id}.position")
            if position is None:
                unresolved.append({"clientHouseId": client_id, "reason": "missing-registry-position"})
                continue
            found = world.find_tile(position)
            if found is None:
                unresolved.append(
                    {"clientHouseId": client_id, "reason": "registry-position-has-no-otbm-tile", "position": list(position)}
                )
                continue
            _, tile = found
            if tile.house_id is None:
                unresolved.append(
                    {
                        "clientHouseId": client_id,
                        "reason": "registry-position-is-not-an-otbm-house-tile",
                        "position": list(position),
                    }
                )
                continue
            previous = reverse.get(tile.house_id)
            if previous is not None and previous != client_id:
                conflicts.append(
                    {
                        "clientHouseId": client_id,
                        "otbmHouseId": tile.house_id,
                        "reason": "multiple-client-house-ids-map-to-one-otbm-house-id",
                        "otherClientHouseId": previous,
                        "position": list(position),
                    }
                )
                continue
            reverse[tile.house_id] = client_id
            mappings.append(
                {
                    "clientHouseId": client_id,
                    "otbmHouseId": tile.house_id,
                    "method": "exact-registry-position-house-tile",
                    "position": list(position),
                }
            )
    mappings.sort(key=lambda row: (int(row["clientHouseId"]), int(row["otbmHouseId"])))
    unresolved.sort(key=lambda row: int(row["clientHouseId"]))
    conflicts.sort(key=lambda row: (int(row["clientHouseId"]), int(row.get("otbmHouseId", 0))))
    payload: dict[str, object] = {
        "format": RESOLVER_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "provenance": _provenance(inputs),
        "namespaces": {"source": CLIENT_HOUSE_NAMESPACE, "target": OTBM_HOUSE_NAMESPACE},
        "method": "one-to-one-mapped",
        "review": {"state": "reviewed", "reviewId": review_id, "statement": review_statement},
        "mappings": mappings,
        "findings": {"unresolved": unresolved, "conflicts": conflicts},
        "summary": {
            "clientHouseCount": len(client_ids),
            "mappingCount": len(mappings),
            "unresolvedCount": len(unresolved),
            "conflictCount": len(conflicts),
        },
        "policy": {
            "exactRegistryPositionOnly": True,
            "nameMapping": False,
            "proximityMapping": False,
            "numericIdentityInference": False,
            "staticdataHouseFieldOrder": inputs["staticdataHouseContract"]["houseFieldOrder"],
            "declaredSizeComparison": "enabled-only-when-reviewed-size-is-present",
            "objectIdMapping": False,
            "requiresExactProvenance": True,
        },
    }
    protected = (
        client_manifest_path.resolve(),
        staticdata_index_path.resolve(),
        staticmapdata_index_path.resolve(),
        world_index_path.resolve(),
        world_manifest_path.resolve(),
    )
    return payload, protected


def _validate_resolver(
    resolver: Mapping[str, object],
    *,
    resolver_sha256: str,
    expected_provenance: Mapping[str, object],
    client_ids: set[int],
    otbm_ids: set[int],
    max_mappings: int,
) -> tuple[dict[int, int], dict[str, object]]:
    _require_format(resolver, RESOLVER_FORMAT, "resolver")
    namespaces = _require_dict(resolver.get("namespaces"), "resolver.namespaces")
    if namespaces.get("source") != CLIENT_HOUSE_NAMESPACE or namespaces.get("target") != OTBM_HOUSE_NAMESPACE:
        raise HouseReferenceParityError("resolver namespaces are unsupported")
    provenance = _require_dict(resolver.get("provenance"), "resolver.provenance")
    for key, expected in expected_provenance.items():
        actual = provenance.get(key)
        if key.endswith("Sha256"):
            actual = _require_sha(actual, f"resolver.provenance.{key}")
        elif key.endswith("Id"):
            actual = _require_nonempty_text(actual, f"resolver.provenance.{key}")
        if actual != expected:
            raise HouseReferenceParityError(f"resolver is stale: provenance {key} does not match")
    review = _require_dict(resolver.get("review"), "resolver.review")
    if review.get("state") != "reviewed":
        raise HouseReferenceParityError("resolver review.state must be reviewed")
    _require_nonempty_text(review.get("reviewId"), "resolver.review.reviewId")
    _require_nonempty_text(review.get("statement"), "resolver.review.statement")
    method = _require_nonempty_text(resolver.get("method"), "resolver.method")
    if method not in _ALLOWED_RESOLVER_METHODS:
        raise HouseReferenceParityError(f"unsupported resolver method: {method}")

    mapping: dict[int, int] = {}
    reverse: dict[int, int] = {}
    if method == "exact-identity":
        rows = _require_list(resolver.get("mappings", []), "resolver.mappings")
        if rows:
            raise HouseReferenceParityError("exact-identity resolver must not contain mappings")
        if client_ids != otbm_ids:
            raise HouseReferenceParityError("exact-identity resolver requires identical client and OTBM house-ID sets")
        for house_id in sorted(client_ids):
            mapping[house_id] = house_id
            reverse[house_id] = house_id
    else:
        rows = _require_list(resolver.get("mappings"), "resolver.mappings")
        if len(rows) > max_mappings:
            raise HouseReferenceParityError(f"resolver mapping count exceeds {max_mappings}")
        for ordinal, raw in enumerate(rows, start=1):
            row = _require_dict(raw, f"resolver.mappings[{ordinal}]")
            client_id = _require_uint(row.get("clientHouseId"), f"resolver.mappings[{ordinal}].clientHouseId", positive=True)
            otbm_id = _require_uint(row.get("otbmHouseId"), f"resolver.mappings[{ordinal}].otbmHouseId", positive=True)
            if client_id not in client_ids:
                raise HouseReferenceParityError(f"resolver references unknown client house ID {client_id}")
            if otbm_id not in otbm_ids:
                raise HouseReferenceParityError(f"resolver references unknown OTBM house ID {otbm_id}")
            row_method = _require_nonempty_text(row.get("method"), f"resolver.mappings[{ordinal}].method")
            if row_method != "exact-registry-position-house-tile":
                raise HouseReferenceParityError(f"unsupported resolver mapping method: {row_method}")
            position = _require_list(row.get("position"), f"resolver.mappings[{ordinal}].position")
            if len(position) != 3:
                raise HouseReferenceParityError(f"resolver.mappings[{ordinal}].position must contain x, y and z")
            _require_uint(position[0], f"resolver.mappings[{ordinal}].position[0]", maximum=0xFFFF)
            _require_uint(position[1], f"resolver.mappings[{ordinal}].position[1]", maximum=0xFFFF)
            _require_uint(position[2], f"resolver.mappings[{ordinal}].position[2]", maximum=15)
            if client_id in mapping:
                raise HouseReferenceParityError(f"resolver contains duplicate client house ID {client_id}")
            if otbm_id in reverse:
                raise HouseReferenceParityError(f"resolver contains duplicate OTBM house ID {otbm_id}")
            mapping[client_id] = otbm_id
            reverse[otbm_id] = client_id
    return mapping, {
        "sha256": resolver_sha256,
        "method": method,
        "review": review,
        "mappingCount": len(mapping),
    }


def _layout_summary(record: Mapping[str, object]) -> dict[str, object]:
    layout = _require_dict(record.get("layout"), "StaticMapData house.layout")
    result: dict[str, object] = {}
    position = _position(layout, "StaticMapData house.layout.position")
    if position is not None:
        result["origin"] = list(position)
    raw_size = layout.get("size")
    if isinstance(raw_size, dict):
        size: dict[str, int] = {}
        for key in ("width", "height", "floors"):
            if key in raw_size:
                size[key] = _require_uint(raw_size[key], f"StaticMapData house.layout.size.{key}")
        result["dimensions"] = size
    validation = layout.get("validation")
    if isinstance(validation, dict):
        result["validation"] = validation
    row_count = 0
    tile_record_count = 0
    wall_true = 0
    door_true = 0
    tiles = layout.get("tiles")
    if isinstance(tiles, dict):
        floor_data = tiles.get("floorData")
        if isinstance(floor_data, dict):
            rows = floor_data.get("rows")
            if isinstance(rows, list):
                row_count = len(rows)
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    row_tiles = row.get("tiles")
                    if not isinstance(row_tiles, list):
                        continue
                    tile_record_count += len(row_tiles)
                    for tile in row_tiles:
                        if not isinstance(tile, dict):
                            continue
                        wall = tile.get("wallInfo")
                        door = tile.get("doorInfo")
                        if isinstance(wall, dict) and wall.get("isWall") is True:
                            wall_true += 1
                        if isinstance(door, dict) and door.get("isDoor") is True:
                            door_true += 1
    result["rowCount"] = row_count
    result["tileRecordCount"] = tile_record_count
    result["wallFlagTrueCount"] = wall_true
    result["doorFlagTrueCount"] = door_true
    return result


def _world_house_evidence(index_path: Path, *, max_houses: int) -> tuple[dict[int, dict[str, object]], list[dict[str, object]]]:
    houses: dict[int, dict[str, object]] = {}
    doors: defaultdict[int | None, list[dict[str, object]]] = defaultdict(list)
    with WorldIndex(index_path) as world:
        for tile_index in range(world.header.tile_count):
            tile = world.tile(tile_index)
            if tile.house_id is None:
                continue
            evidence = houses.get(tile.house_id)
            if evidence is None:
                if len(houses) >= max_houses:
                    raise HouseReferenceParityError(f"OTBM house count exceeds {max_houses}")
                evidence = {
                    "houseTileCount": 0,
                    "placementCount": 0,
                    "minX": tile.x,
                    "maxX": tile.x,
                    "minY": tile.y,
                    "maxY": tile.y,
                    "minZ": tile.z,
                    "maxZ": tile.z,
                    "floors": set(),
                }
                houses[tile.house_id] = evidence
            evidence["houseTileCount"] = int(evidence["houseTileCount"]) + 1
            evidence["placementCount"] = int(evidence["placementCount"]) + tile.placement_count
            evidence["minX"] = min(int(evidence["minX"]), tile.x)
            evidence["maxX"] = max(int(evidence["maxX"]), tile.x)
            evidence["minY"] = min(int(evidence["minY"]), tile.y)
            evidence["maxY"] = max(int(evidence["maxY"]), tile.y)
            evidence["minZ"] = min(int(evidence["minZ"]), tile.z)
            evidence["maxZ"] = max(int(evidence["maxZ"]), tile.z)
            floors = evidence["floors"]
            assert isinstance(floors, set)
            floors.add(tile.z)
        for mechanic_index in range(world.header.mechanic_count):
            placement_ordinal, mechanic = world.mechanic_record(mechanic_index)
            if "houseDoorId" not in mechanic:
                continue
            placement = world.placement(placement_ordinal)
            found = world.find_tile(tuple(placement["position"]))
            house_id = None if found is None else found[1].house_id
            doors[house_id].append(
                {
                    "houseDoorId": mechanic["houseDoorId"],
                    "position": placement["position"],
                    "itemId": placement["itemId"],
                    "placementOrdinal": placement_ordinal,
                }
            )
    for house_id, evidence in houses.items():
        floors = sorted(evidence.pop("floors"))
        evidence["floors"] = floors
        evidence["bounds"] = {
            "min": [evidence.pop("minX"), evidence.pop("minY"), evidence.pop("minZ")],
            "max": [evidence.pop("maxX"), evidence.pop("maxY"), evidence.pop("maxZ")],
        }
        minimum = evidence["bounds"]["min"]
        maximum = evidence["bounds"]["max"]
        evidence["boundingDimensions"] = {
            "width": maximum[0] - minimum[0] + 1,
            "height": maximum[1] - minimum[1] + 1,
            "floors": len(floors),
            "floorSpan": maximum[2] - minimum[2] + 1,
        }
        evidence["houseDoors"] = sorted(
            doors.pop(house_id, []),
            key=lambda row: (row["position"][2], row["position"][1], row["position"][0], row["placementOrdinal"]),
        )
        evidence["houseDoorPlacementCount"] = len(evidence["houseDoors"])
    orphan_doors = sorted(
        doors.pop(None, []),
        key=lambda row: (row["position"][2], row["position"][1], row["position"][0], row["placementOrdinal"]),
    )
    for remaining in doors.values():
        orphan_doors.extend(remaining)
    return houses, orphan_doors


def _comparison(
    registry: Mapping[str, object] | None,
    layout: Mapping[str, object] | None,
    otbm: Mapping[str, object] | None,
    *,
    resolved_otbm_id: int | None,
) -> tuple[dict[str, object], list[str]]:
    comparisons: dict[str, object] = {}
    mismatches: list[str] = []
    if registry is not None and resolved_otbm_id is not None:
        registry_position = _position(registry, "registry.position")
        if registry_position is not None and otbm is not None:
            bounds = otbm["bounds"]
            assert isinstance(bounds, dict)
            minimum = bounds["min"]
            maximum = bounds["max"]
            in_bounds = (
                minimum[0] <= registry_position[0] <= maximum[0]
                and minimum[1] <= registry_position[1] <= maximum[1]
                and registry_position[2] in otbm["floors"]
            )
            comparisons["registryPosition"] = {
                "position": list(registry_position),
                "insideObservedHouseBounds": in_bounds,
                "resolvedOtbmHouseId": resolved_otbm_id,
            }
        if "size" in registry and otbm is not None:
            declared_size = _require_uint(registry["size"], "registry.size")
            observed = int(otbm["houseTileCount"])
            matches = declared_size == observed
            comparisons["registrySizeVsOtbmHouseTiles"] = {
                "declaredSize": declared_size,
                "observedHouseTileCount": observed,
                "matches": matches,
                "semantics": "review-only-direct-numeric-comparison",
            }
            if not matches:
                mismatches.append("registry-size-vs-otbm-house-tile-count")
    if layout is not None and otbm is not None:
        origin = layout.get("origin")
        dimensions = layout.get("dimensions")
        bounds = otbm["bounds"]
        observed_dimensions = otbm["boundingDimensions"]
        if isinstance(origin, list) and len(origin) == 3:
            origin_matches = origin == bounds["min"]
            comparisons["layoutOriginVsOtbmBounds"] = {
                "layoutOrigin": origin,
                "otbmMinimum": bounds["min"],
                "matches": origin_matches,
                "semantics": "review-only-direct-coordinate-comparison",
            }
            if not origin_matches:
                mismatches.append("layout-origin-vs-otbm-bounds")
        if isinstance(dimensions, dict):
            keys = [key for key in ("width", "height", "floors") if key in dimensions]
            matches_by_key = {key: dimensions[key] == observed_dimensions[key] for key in keys}
            comparisons["layoutDimensionsVsOtbmBounds"] = {
                "layoutDimensions": dimensions,
                "otbmBoundingDimensions": observed_dimensions,
                "matches": matches_by_key,
                "semantics": "review-only-direct-dimension-comparison",
            }
            if any(not value for value in matches_by_key.values()):
                mismatches.append("layout-dimensions-vs-otbm-bounds")
        comparisons["referenceTopologyVsOtbmHouseDoors"] = {
            "staticmapWallFlagTrueCount": layout.get("wallFlagTrueCount", 0),
            "staticmapDoorFlagTrueCount": layout.get("doorFlagTrueCount", 0),
            "otbmHouseDoorPlacementCount": otbm["houseDoorPlacementCount"],
            "semantics": "reference-only-counts-no-object-id-join",
        }
    return comparisons, mismatches


def build_parity(
    *,
    client_manifest_path: Path,
    staticdata_index_path: Path,
    staticmapdata_index_path: Path,
    world_index_path: Path,
    world_manifest_path: Path,
    resolver_path: Path,
    max_json_bytes: int = DEFAULT_MAX_JSON_BYTES,
    max_houses: int = DEFAULT_MAX_HOUSES,
    max_mappings: int = DEFAULT_MAX_MAPPINGS,
) -> tuple[dict[str, object], tuple[Path, ...]]:
    for value, label in ((max_houses, "max_houses"), (max_mappings, "max_mappings")):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise HouseReferenceParityError(f"{label} must be positive")
    inputs = _load_inputs(
        client_manifest_path=client_manifest_path,
        staticdata_index_path=staticdata_index_path,
        staticmapdata_index_path=staticmapdata_index_path,
        world_index_path=world_index_path,
        world_manifest_path=world_manifest_path,
        max_json_bytes=max_json_bytes,
    )
    resolver, resolver_sha, resolver_resolved = _load_json(
        resolver_path, max_bytes=max_json_bytes, label="house-ID resolver"
    )
    staticdata = inputs["staticdata"]
    staticmap = inputs["staticmap"]
    assert isinstance(staticdata, dict) and isinstance(staticmap, dict)
    registry, registry_conflicts = _house_records_staticdata(staticdata, max_houses=max_houses)
    layouts, layout_conflicts = _house_records_staticmap(staticmap, max_houses=max_houses)
    otbm, orphan_doors = _world_house_evidence(inputs["worldIndexPath"], max_houses=max_houses)
    mapping, resolver_summary = _validate_resolver(
        resolver,
        resolver_sha256=resolver_sha,
        expected_provenance=_provenance(inputs),
        client_ids=set(registry) | set(layouts),
        otbm_ids=set(otbm),
        max_mappings=max_mappings,
    )

    rows: list[dict[str, object]] = []
    findings: list[dict[str, object]] = []
    covered_client: set[int] = set()
    covered_otbm: set[int] = set()
    for client_id, otbm_id in sorted(mapping.items()):
        covered_client.add(client_id)
        covered_otbm.add(otbm_id)
        registry_record = registry.get(client_id)
        layout_record = layouts.get(client_id)
        otbm_record = otbm.get(otbm_id)
        row: dict[str, object] = {"clientHouseId": client_id, "otbmHouseId": otbm_id}
        if registry_record is not None:
            row["registry"] = registry_record
        layout_summary = None
        if layout_record is not None and "layout" in layout_record:
            layout_summary = _layout_summary(layout_record)
            row["layout"] = layout_summary
        if otbm_record is not None:
            row["otbm"] = otbm_record
        if client_id in registry_conflicts or client_id in layout_conflicts:
            state = "conflicting"
            dimensions = ["duplicate-client-house-id"]
        elif registry_record is None and layout_record is None and otbm_record is not None:
            state = "otbm-only"
            dimensions = ["client-house-presence"]
        elif otbm_record is None and (registry_record is not None or layout_record is not None):
            state = "reference-only"
            dimensions = ["otbm-house-presence"]
        elif registry_record is None or layout_record is None or otbm_record is None:
            state = "partial"
            dimensions = [
                name
                for name, value in (
                    ("staticdata-registry", registry_record),
                    ("staticmapdata-layout", layout_record),
                    ("otbm-house", otbm_record),
                )
                if value is None
            ]
        else:
            comparisons, dimensions = _comparison(
                registry_record,
                layout_summary,
                otbm_record,
                resolved_otbm_id=otbm_id,
            )
            row["comparisons"] = comparisons
            state = "mismatch" if dimensions else "conforming"
        if state not in _ALLOWED_STATES:
            raise AssertionError(state)
        row["state"] = state
        if dimensions:
            finding = {
                "state": state,
                "clientHouseId": client_id,
                "otbmHouseId": otbm_id,
                "dimensions": dimensions,
            }
            findings.append(finding)
            row["findingDimensions"] = dimensions
        rows.append(row)

    for client_id in sorted((set(registry) | set(layouts)) - covered_client):
        state = "conflicting" if client_id in registry_conflicts or client_id in layout_conflicts else "unresolved-id-space"
        row = {"clientHouseId": client_id, "state": state}
        if client_id in registry:
            row["registry"] = registry[client_id]
        if client_id in layouts and "layout" in layouts[client_id]:
            row["layout"] = _layout_summary(layouts[client_id])
        rows.append(row)
        findings.append({"state": state, "clientHouseId": client_id, "dimensions": ["house-id-resolution"]})
    for otbm_id in sorted(set(otbm) - covered_otbm):
        rows.append({"otbmHouseId": otbm_id, "state": "unresolved-id-space", "otbm": otbm[otbm_id]})
        findings.append({"state": "unresolved-id-space", "otbmHouseId": otbm_id, "dimensions": ["house-id-resolution"]})

    rows.sort(key=lambda row: (int(row.get("clientHouseId", 0xFFFFFFFF)), int(row.get("otbmHouseId", 0xFFFFFFFF))))
    findings.sort(
        key=lambda row: (
            str(row["state"]),
            int(row.get("clientHouseId", 0xFFFFFFFF)),
            int(row.get("otbmHouseId", 0xFFFFFFFF)),
        )
    )
    state_counts = Counter(str(row["state"]) for row in rows)
    payload: dict[str, object] = {
        "format": PARITY_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "provenance": {
            **_provenance(inputs),
            "resolverSha256": resolver_sha,
        },
        "namespaces": {
            "clientHouseId": CLIENT_HOUSE_NAMESPACE,
            "otbmHouseId": OTBM_HOUSE_NAMESPACE,
            "staticmapObjectId": {
                "name": STATICMAP_OBJECT_NAMESPACE,
                "resolution": "unresolved",
                "otbmItemIdEquivalent": False,
            },
        },
        "resolver": resolver_summary,
        "houses": rows,
        "findings": findings,
        "orphanHouseDoorPlacements": orphan_doors,
        "summary": {
            "staticdataHouseCount": len(registry),
            "staticdataHouseFieldOrder": inputs["staticdataHouseContract"]["houseFieldOrder"],
            "staticmapdataHouseCount": len(layouts),
            "otbmHouseCount": len(otbm),
            "houseRecordCount": len(rows),
            "findingCount": len(findings),
            "orphanHouseDoorPlacementCount": len(orphan_doors),
            "stateCounts": {state: state_counts.get(state, 0) for state in sorted(_ALLOWED_STATES)},
        },
        "policy": {
            "reviewFindingsOnly": True,
            "otbmParsing": False,
            "otbmWriting": False,
            "pathfinding": False,
            "geometryRecomputation": False,
            "nameMapping": False,
            "proximityMapping": False,
            "numericIdentityInference": False,
            "staticdataHouseFieldOrder": inputs["staticdataHouseContract"]["houseFieldOrder"],
            "declaredSizeComparison": "enabled-only-when-reviewed-size-is-present",
            "objectIdMapping": False,
            "gameplayConclusions": False,
            "maxJsonBytes": max_json_bytes,
            "maxHouses": max_houses,
            "maxMappings": max_mappings,
        },
    }
    protected = (
        client_manifest_path.resolve(),
        staticdata_index_path.resolve(),
        staticmapdata_index_path.resolve(),
        world_index_path.resolve(),
        world_manifest_path.resolve(),
        resolver_resolved,
    )
    return payload, protected


def deterministic_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def write_output(
    output: Path,
    payload: Mapping[str, object],
    *,
    protected_inputs: Iterable[Path],
    overwrite: bool = False,
) -> None:
    candidate = output.expanduser()
    if candidate.is_symlink():
        raise HouseReferenceParityError(f"output must not be a symlink: {output}")
    target = candidate.resolve()
    protected = tuple(path.resolve() for path in protected_inputs)
    if target in protected or any(target.exists() and os.path.samefile(target, source) for source in protected):
        raise HouseReferenceParityError("output collides with a protected input")
    if target.exists() and not target.is_file():
        raise HouseReferenceParityError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise HouseReferenceParityError(f"output already exists: {target}; pass --overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = deterministic_json(payload)
    if not overwrite:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        return
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
