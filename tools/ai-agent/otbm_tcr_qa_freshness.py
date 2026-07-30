from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

MANIFEST_FORMAT = "canary-otbm-tcr-qa-freshness-manifest-v1"
REPORT_FORMAT = "canary-otbm-tcr-qa-freshness-impact-v1"
ROUTING_FORMAT = "canary-tibia-reference-adoption-routing-v1"
PROVENANCE_FORMAT = "canary-otbm-release-provenance-v1"
SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_ROUTES = 32
MAX_MAPPINGS = 128
MAX_IDS_PER_MAPPING = 32
MAX_CONTEXT_REFERENCES = 64
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class TcrQaFreshnessError(ValueError):
    pass


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TcrQaFreshnessError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise TcrQaFreshnessError("value is not canonical JSON") from exc


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TcrQaFreshnessError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise TcrQaFreshnessError(f"{label} must be an array")
    return value


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise TcrQaFreshnessError(f"{label} must match {IDENTIFIER_RE.pattern}")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise TcrQaFreshnessError(f"{label} must be an exact lowercase SHA-256")
    return value


def _trimmed(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise TcrQaFreshnessError(f"{label} must be a non-empty trimmed string")
    return value


def _identifier_list(
    value: Any,
    label: str,
    *,
    min_items: int = 0,
    max_items: int = MAX_IDS_PER_MAPPING,
) -> list[str]:
    rows = _array(value, label)
    if not min_items <= len(rows) <= max_items:
        raise TcrQaFreshnessError(
            f"{label} must contain {min_items}..{max_items} entries"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        item = _identifier(row, f"{label}[{index}]")
        if item in seen:
            raise TcrQaFreshnessError(f"{label} contains duplicate value {item!r}")
        seen.add(item)
        normalized.append(item)
    return sorted(normalized)


def _context_references(value: Any, label: str) -> list[str]:
    rows = _array(value, label)
    if len(rows) > MAX_CONTEXT_REFERENCES:
        raise TcrQaFreshnessError(
            f"{label} must contain at most {MAX_CONTEXT_REFERENCES} entries"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        item = _trimmed(row, f"{label}[{index}]")
        if item in seen:
            raise TcrQaFreshnessError(f"{label} contains duplicate value {item!r}")
        seen.add(item)
        normalized.append(item)
    return sorted(normalized)


def load_json_file_with_sha256(
    path: Path, *, label: str
) -> tuple[dict[str, Any], str]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise TcrQaFreshnessError(f"{label} must not be a symlink: {path}")
    source = candidate.resolve(strict=True)
    if not source.is_file():
        raise TcrQaFreshnessError(f"{label} must be a regular file: {source}")
    before = source.stat()
    if before.st_size > MAX_INPUT_BYTES:
        raise TcrQaFreshnessError(f"{label} exceeds {MAX_INPUT_BYTES} bytes")
    data = source.read_bytes()
    after = source.stat()
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or len(data) != after.st_size:
        raise TcrQaFreshnessError(f"{label} changed while reading")
    try:
        document = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                TcrQaFreshnessError(
                    f"{label} contains non-finite number {token}"
                )
            ),
        )
    except UnicodeDecodeError as exc:
        raise TcrQaFreshnessError(f"{label} must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise TcrQaFreshnessError(
            f"{label} is invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(document, dict):
        raise TcrQaFreshnessError(f"{label} must contain a JSON object")
    return document, hashlib.sha256(data).hexdigest()


def _validate_signed_document(
    document: Mapping[str, Any], *, hash_field: str, label: str
) -> str:
    provided = _sha256(document.get(hash_field), f"{label}.{hash_field}")
    unsigned = dict(document)
    unsigned.pop(hash_field, None)
    if canonical_sha256(unsigned) != provided:
        raise TcrQaFreshnessError(
            f"{label}.{hash_field} does not match canonical document content"
        )
    return provided


def _normalize_target(value: Any, label: str) -> dict[str, str]:
    target = _object(value, label)
    if set(target) != {"owner", "capability"}:
        raise TcrQaFreshnessError(
            f"{label} must contain exactly owner and capability"
        )
    return {
        "owner": _identifier(target.get("owner"), f"{label}.owner"),
        "capability": _identifier(
            target.get("capability"), f"{label}.capability"
        ),
    }


def _target_key(target: Mapping[str, str]) -> tuple[str, str]:
    return (target["owner"], target["capability"])


def validate_routing_report(document: Mapping[str, Any]) -> dict[str, Any]:
    report = _object(document, "routing report")
    if report.get("format") != ROUTING_FORMAT or report.get("schemaVersion") != 1:
        raise TcrQaFreshnessError(
            f"routing report must use {ROUTING_FORMAT} schemaVersion 1"
        )
    report_sha = _validate_signed_document(
        report, hash_field="reportSha256", label="routing report"
    )
    routes = _array(report.get("routes"), "routing report.routes")
    if not 1 <= len(routes) <= MAX_ROUTES:
        raise TcrQaFreshnessError(
            f"routing report.routes must contain 1..{MAX_ROUTES} entries"
        )
    normalized_routes: list[dict[str, Any]] = []
    route_ids: set[str] = set()
    extract_ids: set[str] = set()
    for index, raw_route in enumerate(routes):
        route = _object(raw_route, f"routing report.routes[{index}]")
        expected = {
            "id",
            "extract",
            "disposition",
            "targets",
            "reasonCode",
            "contextReferences",
        }
        if set(route) != expected:
            raise TcrQaFreshnessError(
                f"routing report.routes[{index}] has an unexpected field set"
            )
        route_id = _identifier(route.get("id"), f"routing report.routes[{index}].id")
        if route_id in route_ids:
            raise TcrQaFreshnessError(f"duplicate routing route id {route_id!r}")
        extract = _object(
            route.get("extract"), f"routing report.routes[{index}].extract"
        )
        if set(extract) != {"id", "sourceId", "pointer", "valueSha256"}:
            raise TcrQaFreshnessError(
                f"routing report.routes[{index}].extract has an unexpected field set"
            )
        extract_id = _identifier(
            extract.get("id"), f"routing report.routes[{index}].extract.id"
        )
        if extract_id in extract_ids:
            raise TcrQaFreshnessError(
                f"routing extract {extract_id!r} appears more than once"
            )
        pointer = extract.get("pointer")
        if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
            raise TcrQaFreshnessError(
                f"routing report.routes[{index}].extract.pointer must be a non-root JSON Pointer"
            )
        normalized_extract = {
            "id": extract_id,
            "sourceId": _identifier(
                extract.get("sourceId"),
                f"routing report.routes[{index}].extract.sourceId",
            ),
            "pointer": pointer,
            "valueSha256": _sha256(
                extract.get("valueSha256"),
                f"routing report.routes[{index}].extract.valueSha256",
            ),
        }
        disposition = route.get("disposition")
        if disposition not in {"routed", "unsupported", "blocked"}:
            raise TcrQaFreshnessError(
                f"routing report.routes[{index}].disposition is unsupported"
            )
        targets = _array(
            route.get("targets"), f"routing report.routes[{index}].targets"
        )
        normalized_targets: list[dict[str, str]] = []
        seen_targets: set[tuple[str, str]] = set()
        for target_index, raw_target in enumerate(targets):
            target = _normalize_target(
                raw_target,
                f"routing report.routes[{index}].targets[{target_index}]",
            )
            key = _target_key(target)
            if key in seen_targets:
                raise TcrQaFreshnessError(
                    f"routing report route {route_id!r} contains duplicate target {key!r}"
                )
            seen_targets.add(key)
            normalized_targets.append(target)
        if disposition == "routed" and not normalized_targets:
            raise TcrQaFreshnessError(
                f"routed route {route_id!r} must contain at least one target"
            )
        if disposition != "routed" and normalized_targets:
            raise TcrQaFreshnessError(
                f"non-routed route {route_id!r} must not contain targets"
            )
        normalized_targets.sort(key=_target_key)
        normalized_routes.append(
            {
                "id": route_id,
                "extract": normalized_extract,
                "disposition": disposition,
                "targets": normalized_targets,
                "reasonCode": _identifier(
                    route.get("reasonCode"),
                    f"routing report.routes[{index}].reasonCode",
                ),
                "contextReferences": _context_references(
                    route.get("contextReferences"),
                    f"routing report.routes[{index}].contextReferences",
                ),
            }
        )
        route_ids.add(route_id)
        extract_ids.add(extract_id)
    normalized_routes.sort(key=lambda row: row["id"])
    return {
        "reportSha256": report_sha,
        "gateway": _object(report.get("gateway"), "routing report.gateway"),
        "request": _object(report.get("request"), "routing report.request"),
        "routes": normalized_routes,
    }


def validate_release_provenance(document: Mapping[str, Any]) -> dict[str, Any]:
    report = _object(document, "release provenance report")
    if report.get("format") != PROVENANCE_FORMAT or report.get("schemaVersion") != 1:
        raise TcrQaFreshnessError(
            f"release provenance report must use {PROVENANCE_FORMAT} schemaVersion 1"
        )
    report_sha = _validate_signed_document(
        report, hash_field="reportSha256", label="release provenance report"
    )
    current_bom_sha = _sha256(
        report.get("currentBomSha256"),
        "release provenance report.currentBomSha256",
    )
    previous_bom_raw = report.get("previousBomSha256")
    previous_bom_sha = (
        None
        if previous_bom_raw is None
        else _sha256(
            previous_bom_raw,
            "release provenance report.previousBomSha256",
        )
    )
    changes = _array(
        report.get("componentChanges"),
        "release provenance report.componentChanges",
    )
    normalized_changes: list[dict[str, str]] = []
    change_ids: set[str] = set()
    for index, raw_change in enumerate(changes):
        change = _object(
            raw_change, f"release provenance report.componentChanges[{index}]"
        )
        component_id = _identifier(
            change.get("componentId"),
            f"release provenance report.componentChanges[{index}].componentId",
        )
        if component_id in change_ids:
            raise TcrQaFreshnessError(
                f"duplicate release provenance component change {component_id!r}"
            )
        status = change.get("status")
        if status not in {"added", "removed", "changed"}:
            raise TcrQaFreshnessError(
                f"release provenance component {component_id!r} has unsupported status"
            )
        normalized_changes.append({"componentId": component_id, "status": status})
        change_ids.add(component_id)
    freshness_rows = _array(
        report.get("dimensionFreshness"),
        "release provenance report.dimensionFreshness",
    )
    normalized_freshness: list[dict[str, Any]] = []
    dimension_ids: set[str] = set()
    for index, raw_row in enumerate(freshness_rows):
        row = _object(
            raw_row, f"release provenance report.dimensionFreshness[{index}]"
        )
        dimension_id = _identifier(
            row.get("dimensionId"),
            f"release provenance report.dimensionFreshness[{index}].dimensionId",
        )
        if dimension_id in dimension_ids:
            raise TcrQaFreshnessError(
                f"duplicate release provenance dimension {dimension_id!r}"
            )
        status = row.get("status")
        if status not in {"stale", "current", "not-compared"}:
            raise TcrQaFreshnessError(
                f"release provenance dimension {dimension_id!r} has unsupported status"
            )
        changed_dependencies = _identifier_list(
            row.get("changedDependencies"),
            f"release provenance report.dimensionFreshness[{index}].changedDependencies",
            max_items=MAX_MAPPINGS,
        )
        if status == "stale" and not changed_dependencies:
            raise TcrQaFreshnessError(
                f"stale dimension {dimension_id!r} must contain changed dependencies"
            )
        if status != "stale" and changed_dependencies:
            raise TcrQaFreshnessError(
                f"non-stale dimension {dimension_id!r} must not contain changed dependencies"
            )
        normalized_freshness.append(
            {
                "dimensionId": dimension_id,
                "status": status,
                "changedDependencies": changed_dependencies,
            }
        )
        dimension_ids.add(dimension_id)
    removed_dimensions = _identifier_list(
        report.get("removedDimensions"),
        "release provenance report.removedDimensions",
        max_items=MAX_MAPPINGS,
    )
    overlap = sorted(set(removed_dimensions).intersection(dimension_ids))
    if overlap:
        raise TcrQaFreshnessError(
            f"release provenance dimensions cannot be both current and removed: {overlap}"
        )
    normalized_changes.sort(key=lambda row: row["componentId"])
    normalized_freshness.sort(key=lambda row: row["dimensionId"])
    return {
        "reportSha256": report_sha,
        "currentBomSha256": current_bom_sha,
        "previousBomSha256": previous_bom_sha,
        "componentChanges": normalized_changes,
        "dimensionFreshness": normalized_freshness,
        "removedDimensions": removed_dimensions,
    }


def normalize_manifest(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _object(document, "freshness manifest")
    expected_root = {
        "format",
        "schemaVersion",
        "routing",
        "releaseProvenance",
        "review",
        "mappings",
    }
    if set(root) != expected_root:
        raise TcrQaFreshnessError(
            "freshness manifest has an unexpected top-level field set"
        )
    if root.get("format") != MANIFEST_FORMAT or root.get("schemaVersion") != 1:
        raise TcrQaFreshnessError(
            f"freshness manifest must use {MANIFEST_FORMAT} schemaVersion 1"
        )
    routing = _object(root.get("routing"), "freshness manifest.routing")
    if set(routing) != {"fileSha256", "reportSha256"}:
        raise TcrQaFreshnessError(
            "freshness manifest.routing must contain exactly fileSha256 and reportSha256"
        )
    normalized_routing = {
        "fileSha256": _sha256(
            routing.get("fileSha256"), "freshness manifest.routing.fileSha256"
        ),
        "reportSha256": _sha256(
            routing.get("reportSha256"),
            "freshness manifest.routing.reportSha256",
        ),
    }
    provenance = _object(
        root.get("releaseProvenance"),
        "freshness manifest.releaseProvenance",
    )
    if set(provenance) != {
        "fileSha256",
        "reportSha256",
        "currentBomSha256",
        "previousBomSha256",
    }:
        raise TcrQaFreshnessError(
            "freshness manifest.releaseProvenance has an unexpected field set"
        )
    previous_bom_raw = provenance.get("previousBomSha256")
    normalized_provenance = {
        "fileSha256": _sha256(
            provenance.get("fileSha256"),
            "freshness manifest.releaseProvenance.fileSha256",
        ),
        "reportSha256": _sha256(
            provenance.get("reportSha256"),
            "freshness manifest.releaseProvenance.reportSha256",
        ),
        "currentBomSha256": _sha256(
            provenance.get("currentBomSha256"),
            "freshness manifest.releaseProvenance.currentBomSha256",
        ),
        "previousBomSha256": (
            None
            if previous_bom_raw is None
            else _sha256(
                previous_bom_raw,
                "freshness manifest.releaseProvenance.previousBomSha256",
            )
        ),
    }
    review = _object(root.get("review"), "freshness manifest.review")
    if set(review) != {"reviewId", "statement"}:
        raise TcrQaFreshnessError(
            "freshness manifest.review must contain exactly reviewId and statement"
        )
    normalized_review = {
        "reviewId": _identifier(
            review.get("reviewId"), "freshness manifest.review.reviewId"
        ),
        "statement": _trimmed(
            review.get("statement"), "freshness manifest.review.statement"
        ),
    }
    mappings = _array(root.get("mappings"), "freshness manifest.mappings")
    if not 1 <= len(mappings) <= MAX_MAPPINGS:
        raise TcrQaFreshnessError(
            f"freshness manifest.mappings must contain 1..{MAX_MAPPINGS} entries"
        )
    normalized_mappings: list[dict[str, Any]] = []
    mapping_ids: set[str] = set()
    route_target_keys: set[tuple[str, str | None, str | None]] = set()
    for index, raw_mapping in enumerate(mappings):
        mapping = _object(raw_mapping, f"freshness manifest.mappings[{index}]")
        expected_mapping = {
            "id",
            "routeId",
            "extract",
            "target",
            "componentIds",
            "dimensionIds",
            "contextReferences",
        }
        if set(mapping) != expected_mapping:
            raise TcrQaFreshnessError(
                f"freshness manifest.mappings[{index}] has an unexpected field set"
            )
        mapping_id = _identifier(
            mapping.get("id"), f"freshness manifest.mappings[{index}].id"
        )
        if mapping_id in mapping_ids:
            raise TcrQaFreshnessError(f"duplicate freshness mapping id {mapping_id!r}")
        route_id = _identifier(
            mapping.get("routeId"),
            f"freshness manifest.mappings[{index}].routeId",
        )
        extract = _object(
            mapping.get("extract"),
            f"freshness manifest.mappings[{index}].extract",
        )
        if set(extract) != {"id", "sourceId", "pointer", "valueSha256"}:
            raise TcrQaFreshnessError(
                f"freshness manifest.mappings[{index}].extract has an unexpected field set"
            )
        pointer = extract.get("pointer")
        if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
            raise TcrQaFreshnessError(
                f"freshness manifest.mappings[{index}].extract.pointer must be a non-root JSON Pointer"
            )
        normalized_extract = {
            "id": _identifier(
                extract.get("id"),
                f"freshness manifest.mappings[{index}].extract.id",
            ),
            "sourceId": _identifier(
                extract.get("sourceId"),
                f"freshness manifest.mappings[{index}].extract.sourceId",
            ),
            "pointer": pointer,
            "valueSha256": _sha256(
                extract.get("valueSha256"),
                f"freshness manifest.mappings[{index}].extract.valueSha256",
            ),
        }
        target_raw = mapping.get("target")
        target = (
            None
            if target_raw is None
            else _normalize_target(
                target_raw,
                f"freshness manifest.mappings[{index}].target",
            )
        )
        key = (
            route_id,
            None if target is None else target["owner"],
            None if target is None else target["capability"],
        )
        if key in route_target_keys:
            raise TcrQaFreshnessError(
                f"duplicate route/target freshness mapping {key!r}"
            )
        component_ids = _identifier_list(
            mapping.get("componentIds"),
            f"freshness manifest.mappings[{index}].componentIds",
        )
        dimension_ids = _identifier_list(
            mapping.get("dimensionIds"),
            f"freshness manifest.mappings[{index}].dimensionIds",
        )
        if target is None and (component_ids or dimension_ids):
            raise TcrQaFreshnessError(
                f"targetless mapping {mapping_id!r} must not declare QA dependencies"
            )
        if target is not None and (not component_ids or not dimension_ids):
            raise TcrQaFreshnessError(
                f"routed mapping {mapping_id!r} requires componentIds and dimensionIds"
            )
        normalized_mappings.append(
            {
                "id": mapping_id,
                "routeId": route_id,
                "extract": normalized_extract,
                "target": target,
                "componentIds": component_ids,
                "dimensionIds": dimension_ids,
                "contextReferences": _context_references(
                    mapping.get("contextReferences"),
                    f"freshness manifest.mappings[{index}].contextReferences",
                ),
            }
        )
        mapping_ids.add(mapping_id)
        route_target_keys.add(key)
    normalized_mappings.sort(
        key=lambda row: (
            row["routeId"],
            "" if row["target"] is None else row["target"]["owner"],
            "" if row["target"] is None else row["target"]["capability"],
            row["id"],
        )
    )
    return {
        "format": MANIFEST_FORMAT,
        "schemaVersion": 1,
        "routing": normalized_routing,
        "releaseProvenance": normalized_provenance,
        "review": normalized_review,
        "mappings": normalized_mappings,
    }


def build_freshness_impact_report(
    routing_document: Mapping[str, Any],
    provenance_document: Mapping[str, Any],
    manifest_document: Mapping[str, Any],
    *,
    routing_file_sha256: str,
    provenance_file_sha256: str,
    manifest_file_sha256: str,
) -> dict[str, Any]:
    routing = validate_routing_report(routing_document)
    provenance = validate_release_provenance(provenance_document)
    manifest = normalize_manifest(manifest_document)
    actual_routing_file_sha = _sha256(
        routing_file_sha256, "routing_file_sha256"
    )
    actual_provenance_file_sha = _sha256(
        provenance_file_sha256, "provenance_file_sha256"
    )
    actual_manifest_file_sha = _sha256(
        manifest_file_sha256, "manifest_file_sha256"
    )
    if manifest["routing"] != {
        "fileSha256": actual_routing_file_sha,
        "reportSha256": routing["reportSha256"],
    }:
        raise TcrQaFreshnessError(
            "freshness manifest routing identity does not match the exact TCR-011 report"
        )
    if manifest["releaseProvenance"] != {
        "fileSha256": actual_provenance_file_sha,
        "reportSha256": provenance["reportSha256"],
        "currentBomSha256": provenance["currentBomSha256"],
        "previousBomSha256": provenance["previousBomSha256"],
    }:
        raise TcrQaFreshnessError(
            "freshness manifest releaseProvenance identity does not match the exact QA-016 report"
        )
    routes_by_id = {route["id"]: route for route in routing["routes"]}
    mappings_by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for mapping in manifest["mappings"]:
        if mapping["routeId"] not in routes_by_id:
            raise TcrQaFreshnessError(
                f"freshness mapping {mapping['id']!r} references unknown route {mapping['routeId']!r}"
            )
        mappings_by_route[mapping["routeId"]].append(mapping)
    missing_routes = sorted(set(routes_by_id) - set(mappings_by_route))
    if missing_routes:
        raise TcrQaFreshnessError(
            f"freshness manifest must cover every routing route; missing={missing_routes}"
        )
    changes_by_id = {
        row["componentId"]: row for row in provenance["componentChanges"]
    }
    freshness_by_id = {
        row["dimensionId"]: row for row in provenance["dimensionFreshness"]
    }
    removed_dimensions = set(provenance["removedDimensions"])
    aggregate_components_by_dimension: dict[str, set[str]] = defaultdict(set)
    impact_rows: list[dict[str, Any]] = []
    for route_id in sorted(routes_by_id):
        route = routes_by_id[route_id]
        route_mappings = mappings_by_route[route_id]
        expected_extract = route["extract"]
        for mapping in route_mappings:
            if mapping["extract"] != expected_extract:
                raise TcrQaFreshnessError(
                    f"freshness mapping {mapping['id']!r} does not pin the exact route extract"
                )
        expected_targets = {_target_key(target) for target in route["targets"]}
        actual_target_rows = [
            mapping for mapping in route_mappings if mapping["target"] is not None
        ]
        actual_targets = {
            _target_key(mapping["target"]) for mapping in actual_target_rows
        }
        targetless_rows = [
            mapping for mapping in route_mappings if mapping["target"] is None
        ]
        if route["disposition"] == "routed":
            if targetless_rows or actual_targets != expected_targets:
                raise TcrQaFreshnessError(
                    f"routed route {route_id!r} must map every exact target once"
                )
        else:
            if actual_target_rows or len(targetless_rows) != 1:
                raise TcrQaFreshnessError(
                    f"non-routed route {route_id!r} requires exactly one targetless mapping"
                )
        if route["disposition"] != "routed":
            mapping = targetless_rows[0]
            impact_rows.append(
                {
                    "mappingId": mapping["id"],
                    "routeId": route_id,
                    "extract": expected_extract,
                    "disposition": route["disposition"],
                    "reasonCode": route["reasonCode"],
                    "target": None,
                    "componentIds": [],
                    "dimensionIds": [],
                    "freshnessStatus": "not-mapped",
                    "reviewRequired": True,
                    "downstreamEvidence": {
                        "qa008": "not-evaluated",
                        "qa002": "not-evaluated",
                        "qa007": "not-evaluated",
                        "qa006": "not-refreshed",
                    },
                    "contextReferences": mapping["contextReferences"],
                }
            )
            continue
        for mapping in actual_target_rows:
            for component_id in mapping["componentIds"]:
                change = changes_by_id.get(component_id)
                if change is None:
                    raise TcrQaFreshnessError(
                        f"freshness mapping {mapping['id']!r} references unchanged or unknown component {component_id!r}"
                    )
                if change["status"] == "removed":
                    raise TcrQaFreshnessError(
                        f"freshness mapping {mapping['id']!r} cannot bind removed component {component_id!r} to a current dimension"
                    )
            for dimension_id in mapping["dimensionIds"]:
                if dimension_id in removed_dimensions:
                    raise TcrQaFreshnessError(
                        f"freshness mapping {mapping['id']!r} references removed dimension {dimension_id!r}"
                    )
                freshness = freshness_by_id.get(dimension_id)
                if freshness is None:
                    raise TcrQaFreshnessError(
                        f"freshness mapping {mapping['id']!r} references unknown dimension {dimension_id!r}"
                    )
                if freshness["status"] != "stale":
                    raise TcrQaFreshnessError(
                        f"freshness mapping {mapping['id']!r} references non-stale dimension {dimension_id!r}"
                    )
                aggregate_components_by_dimension[dimension_id].update(
                    mapping["componentIds"]
                )
            impact_rows.append(
                {
                    "mappingId": mapping["id"],
                    "routeId": route_id,
                    "extract": expected_extract,
                    "disposition": "routed",
                    "reasonCode": route["reasonCode"],
                    "target": mapping["target"],
                    "componentIds": mapping["componentIds"],
                    "dimensionIds": mapping["dimensionIds"],
                    "freshnessStatus": "stale",
                    "reviewRequired": True,
                    "downstreamEvidence": {
                        "qa008": "not-evaluated",
                        "qa002": "not-evaluated",
                        "qa007": "not-evaluated",
                        "qa006": "not-refreshed",
                    },
                    "contextReferences": mapping["contextReferences"],
                }
            )
    for dimension_id, mapped_components in sorted(
        aggregate_components_by_dimension.items()
    ):
        actual_dependencies = set(
            freshness_by_id[dimension_id]["changedDependencies"]
        )
        if mapped_components != actual_dependencies:
            raise TcrQaFreshnessError(
                f"mapped components for dimension {dimension_id!r} do not exactly equal QA-016 changedDependencies; mapped={sorted(mapped_components)}, actual={sorted(actual_dependencies)}"
            )
    impact_rows.sort(
        key=lambda row: (
            row["routeId"],
            "" if row["target"] is None else row["target"]["owner"],
            "" if row["target"] is None else row["target"]["capability"],
            row["mappingId"],
        )
    )
    disposition_counts = Counter(row["disposition"] for row in impact_rows)
    mapped_component_ids = sorted(
        {component for row in impact_rows for component in row["componentIds"]}
    )
    mapped_dimension_ids = sorted(
        {dimension for row in impact_rows for dimension in row["dimensionIds"]}
    )
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": 1,
        "routing": {
            "format": ROUTING_FORMAT,
            "fileSha256": actual_routing_file_sha,
            "reportSha256": routing["reportSha256"],
        },
        "releaseProvenance": {
            "format": PROVENANCE_FORMAT,
            "fileSha256": actual_provenance_file_sha,
            "reportSha256": provenance["reportSha256"],
            "currentBomSha256": provenance["currentBomSha256"],
            "previousBomSha256": provenance["previousBomSha256"],
        },
        "manifest": {
            "format": MANIFEST_FORMAT,
            "fileSha256": actual_manifest_file_sha,
            "canonicalSha256": canonical_sha256(manifest),
            "review": manifest["review"],
        },
        "impacts": impact_rows,
        "summary": {
            "routeCount": len(routes_by_id),
            "mappingCount": len(impact_rows),
            "routedImpactCount": disposition_counts.get("routed", 0),
            "unsupportedImpactCount": disposition_counts.get("unsupported", 0),
            "blockedImpactCount": disposition_counts.get("blocked", 0),
            "mappedChangedComponentCount": len(mapped_component_ids),
            "mappedStaleDimensionCount": len(mapped_dimension_ids),
            "mappedChangedComponentIds": mapped_component_ids,
            "mappedStaleDimensionIds": mapped_dimension_ids,
        },
        "policy": {
            "readOnlyComposition": True,
            "stableTcrRoutingRequired": True,
            "existingQa016Required": True,
            "reviewedDependencyMappingRequired": True,
            "exactRouteTargetCoverageRequired": True,
            "exactChangedDependencyEqualityRequired": True,
            "parsesClientInputs": False,
            "parsesOtbm": False,
            "guessesIdentifierMappings": False,
            "discoversDependencyEdges": False,
            "rerunsQa016": False,
            "invokesQa008": False,
            "selectsQa002Validators": False,
            "createsQa007ExecutionEvidence": False,
            "runsPhysicalE2e": False,
            "refreshesQa006Certification": False,
            "mutatesEvidenceOrGameState": False,
            "authorizesDeployment": False,
            "claimsGameplayParity": False,
            "unsupportedAndBlockedPreserved": True,
        },
    }
    report["reportSha256"] = canonical_sha256(report)
    return report
