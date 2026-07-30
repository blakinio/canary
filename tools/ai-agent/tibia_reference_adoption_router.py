from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

REQUEST_FORMAT = "canary-tibia-reference-adoption-routing-request-v1"
REPORT_FORMAT = "canary-tibia-reference-adoption-routing-v1"
GATEWAY_FORMAT = "canary-tibia-client-reference-evidence-gateway-v1"
BUNDLE_FORMAT = "canary-otbm-evidence-bundle-v1"
SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_ROUTES = 4
MAX_TARGETS_PER_ROUTE = 4
MAX_CONTEXT_REFERENCES = 32
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

TARGET_OTBM_REPAIR = (
    "otbm-repair-recommendation",
    "canary-otbm-repair-recommendation-v1",
)
TARGET_ACHIEVEMENT = (
    "achievement-validation",
    "canary-achievement-audit-v2",
)
TARGET_CYCLOPEDIA = (
    "cyclopedia-validation",
    "module-catalog:cyclopedia-validation",
)
TARGET_SPAWN_NPC = (
    "otbm-spawn-npc-validation",
    "canary-otbm-spawn-npc-validation-v1",
)
TARGET_QUEST_MAP = (
    "quest-map-validation",
    "canary-quest-map-evidence-v1",
)
TARGET_STORAGE_GRAPH = (
    "otbm-storage-graph",
    "canary-otbm-storage-graph-v1",
)
TARGET_WEAPON_PROFICIENCY = (
    "weapon-proficiency",
    "module-catalog:weapon-proficiency",
)
TARGET_TCR_MANIFEST = (
    "tcr-client-manifest",
    "canary-tibia-client-reference-manifest-v1",
)
TARGET_TCR_HOUSE = (
    "tcr-house-parity",
    "canary-otbm-house-reference-parity-v1",
)
TARGET_TCR_CONTENT = (
    "tcr-content-correlation",
    "canary-tibia-content-reference-correlation-v1",
)
TARGET_TCR_PROFICIENCY = (
    "tcr-proficiency-correlation",
    "canary-tibia-proficiency-reference-correlation-v1",
)

ALL_TARGETS = {
    TARGET_OTBM_REPAIR,
    TARGET_ACHIEVEMENT,
    TARGET_CYCLOPEDIA,
    TARGET_SPAWN_NPC,
    TARGET_QUEST_MAP,
    TARGET_STORAGE_GRAPH,
    TARGET_WEAPON_PROFICIENCY,
    TARGET_TCR_MANIFEST,
    TARGET_TCR_HOUSE,
    TARGET_TCR_CONTENT,
    TARGET_TCR_PROFICIENCY,
}

UNSUPPORTED_REASONS = {
    "unsupported-map-change-shape",
    "unsupported-existing-capability",
    "unsupported-fragment-shape",
}
BLOCKED_REASONS = {
    "conflicting-evidence",
    "stale-evidence",
    "unresolved-id-space",
    "missing-downstream-evidence",
}
ROUTED_REASON = "reviewed-existing-owner-capability"


class AdoptionRoutingError(ValueError):
    pass


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AdoptionRoutingError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AdoptionRoutingError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise AdoptionRoutingError(f"{label} must be an array")
    return value


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise AdoptionRoutingError(f"{label} must match {IDENTIFIER_RE.pattern}")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise AdoptionRoutingError(f"{label} must be an exact lowercase SHA-256")
    return value


def _trimmed(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise AdoptionRoutingError(f"{label} must be a non-empty trimmed string")
    return value


def _context_references(value: Any, label: str) -> list[str]:
    rows = _array(value, label)
    if len(rows) > MAX_CONTEXT_REFERENCES:
        raise AdoptionRoutingError(
            f"{label} must contain at most {MAX_CONTEXT_REFERENCES} entries"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        item = _trimmed(row, f"{label}[{index}]")
        if item in seen:
            raise AdoptionRoutingError(f"{label} contains duplicate value {item!r}")
        seen.add(item)
        normalized.append(item)
    return sorted(normalized)


def load_json_file(path: Path, *, label: str) -> dict[str, Any]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise AdoptionRoutingError(f"{label} must not be a symlink: {path}")
    source = candidate.resolve(strict=True)
    if not source.is_file():
        raise AdoptionRoutingError(f"{label} must be a regular file: {source}")
    before = source.stat()
    if before.st_size > MAX_INPUT_BYTES:
        raise AdoptionRoutingError(f"{label} exceeds {MAX_INPUT_BYTES} bytes")
    data = source.read_bytes()
    after = source.stat()
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or len(data) != after.st_size:
        raise AdoptionRoutingError(f"{label} changed while reading")
    try:
        document = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except UnicodeDecodeError as exc:
        raise AdoptionRoutingError(f"{label} must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise AdoptionRoutingError(
            f"{label} is invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(document, dict):
        raise AdoptionRoutingError(f"{label} must contain a JSON object")
    return document


def _validate_signed_document(
    document: Mapping[str, Any], *, hash_field: str, label: str
) -> str:
    provided = _sha256(document.get(hash_field), f"{label}.{hash_field}")
    unsigned = dict(document)
    unsigned.pop(hash_field, None)
    if canonical_sha256(unsigned) != provided:
        raise AdoptionRoutingError(
            f"{label}.{hash_field} does not match canonical document content"
        )
    return provided


def validate_gateway_report(document: Mapping[str, Any]) -> dict[str, Any]:
    report = _object(document, "gateway report")
    if (
        report.get("format") != GATEWAY_FORMAT
        or report.get("schemaVersion") != SCHEMA_VERSION
        or report.get("mode") != "executed"
    ):
        raise AdoptionRoutingError(
            f"gateway report must use {GATEWAY_FORMAT} schemaVersion {SCHEMA_VERSION} in executed mode"
        )
    report_sha = _validate_signed_document(
        report, hash_field="reportSha256", label="gateway report"
    )
    binding_id = _identifier(report.get("bindingId"), "gateway report.bindingId")
    kind = report.get("kind")
    if kind not in {"house", "content", "proficiency", "drift"}:
        raise AdoptionRoutingError("gateway report.kind is unsupported")
    bundle = _object(report.get("evidenceBundle"), "gateway report.evidenceBundle")
    if bundle.get("format") != BUNDLE_FORMAT or bundle.get("schemaVersion") != 1:
        raise AdoptionRoutingError(
            f"gateway report.evidenceBundle must use {BUNDLE_FORMAT} schemaVersion 1"
        )
    bundle_sha = _validate_signed_document(
        bundle, hash_field="bundleSha256", label="gateway report.evidenceBundle"
    )
    if report.get("evidenceBundleSha256") != bundle_sha:
        raise AdoptionRoutingError(
            "gateway report.evidenceBundleSha256 does not match evidenceBundle.bundleSha256"
        )
    extracts = _array(bundle.get("extracts"), "gateway report.evidenceBundle.extracts")
    if not 1 <= len(extracts) <= MAX_ROUTES:
        raise AdoptionRoutingError(
            f"gateway report must contain 1..{MAX_ROUTES} reviewed extracts"
        )
    normalized_extracts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw_extract in enumerate(extracts):
        extract = _object(raw_extract, f"gateway extract[{index}]")
        extract_id = _identifier(extract.get("id"), f"gateway extract[{index}].id")
        if extract_id in seen_ids:
            raise AdoptionRoutingError(f"duplicate gateway extract id {extract_id!r}")
        source_id = _identifier(
            extract.get("sourceId"), f"gateway extract[{index}].sourceId"
        )
        pointer = extract.get("pointer")
        if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
            raise AdoptionRoutingError(
                f"gateway extract[{index}].pointer must be a non-root JSON Pointer"
            )
        value_sha = _sha256(
            extract.get("valueSha256"), f"gateway extract[{index}].valueSha256"
        )
        value = extract.get("value")
        if canonical_sha256(value) != value_sha:
            raise AdoptionRoutingError(
                f"gateway extract[{index}].valueSha256 does not match canonical value"
            )
        normalized_extracts.append(
            {
                "id": extract_id,
                "sourceId": source_id,
                "pointer": pointer,
                "value": value,
                "valueSha256": value_sha,
            }
        )
        seen_ids.add(extract_id)
    normalized_extracts.sort(key=lambda row: row["id"])
    return {
        "reportSha256": report_sha,
        "evidenceBundleSha256": bundle_sha,
        "bindingId": binding_id,
        "kind": kind,
        "contextReferences": _context_references(
            report.get("contextReferences", []), "gateway report.contextReferences"
        ),
        "extracts": normalized_extracts,
    }


def normalize_request(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _object(document, "routing request")
    expected_root = {"format", "schemaVersion", "gateway", "review", "routes"}
    if set(root) != expected_root:
        raise AdoptionRoutingError(
            "routing request must contain exactly format, schemaVersion, gateway, review and routes"
        )
    if root.get("format") != REQUEST_FORMAT or root.get("schemaVersion") != 1:
        raise AdoptionRoutingError(
            f"routing request must use {REQUEST_FORMAT} schemaVersion 1"
        )
    gateway = _object(root.get("gateway"), "routing request.gateway")
    expected_gateway = {
        "fileSha256",
        "reportSha256",
        "evidenceBundleSha256",
        "bindingId",
        "kind",
    }
    if set(gateway) != expected_gateway:
        raise AdoptionRoutingError(
            "routing request.gateway must contain exactly fileSha256, reportSha256, evidenceBundleSha256, bindingId and kind"
        )
    kind = gateway.get("kind")
    if kind not in {"house", "content", "proficiency", "drift"}:
        raise AdoptionRoutingError("routing request.gateway.kind is unsupported")
    normalized_gateway = {
        "fileSha256": _sha256(
            gateway.get("fileSha256"), "routing request.gateway.fileSha256"
        ),
        "reportSha256": _sha256(
            gateway.get("reportSha256"), "routing request.gateway.reportSha256"
        ),
        "evidenceBundleSha256": _sha256(
            gateway.get("evidenceBundleSha256"),
            "routing request.gateway.evidenceBundleSha256",
        ),
        "bindingId": _identifier(
            gateway.get("bindingId"), "routing request.gateway.bindingId"
        ),
        "kind": kind,
    }
    review = _object(root.get("review"), "routing request.review")
    if set(review) != {"reviewId", "statement"}:
        raise AdoptionRoutingError(
            "routing request.review must contain exactly reviewId and statement"
        )
    normalized_review = {
        "reviewId": _identifier(
            review.get("reviewId"), "routing request.review.reviewId"
        ),
        "statement": _trimmed(
            review.get("statement"), "routing request.review.statement"
        ),
    }
    routes = _array(root.get("routes"), "routing request.routes")
    if not 1 <= len(routes) <= MAX_ROUTES:
        raise AdoptionRoutingError(
            f"routing request.routes must contain 1..{MAX_ROUTES} entries"
        )
    normalized_routes: list[dict[str, Any]] = []
    route_ids: set[str] = set()
    extract_ids: set[str] = set()
    for index, raw_route in enumerate(routes):
        route = _object(raw_route, f"routing request.routes[{index}]")
        expected_route = {
            "id",
            "extract",
            "disposition",
            "targets",
            "reasonCode",
            "contextReferences",
        }
        if set(route) != expected_route:
            raise AdoptionRoutingError(
                f"routing request.routes[{index}] has an unexpected field set"
            )
        route_id = _identifier(route.get("id"), f"routing request.routes[{index}].id")
        if route_id in route_ids:
            raise AdoptionRoutingError(f"duplicate route id {route_id!r}")
        extract = _object(
            route.get("extract"), f"routing request.routes[{index}].extract"
        )
        if set(extract) != {"id", "sourceId", "pointer", "valueSha256"}:
            raise AdoptionRoutingError(
                f"routing request.routes[{index}].extract has an unexpected field set"
            )
        extract_id = _identifier(
            extract.get("id"), f"routing request.routes[{index}].extract.id"
        )
        if extract_id in extract_ids:
            raise AdoptionRoutingError(
                f"gateway extract {extract_id!r} is routed more than once"
            )
        pointer = extract.get("pointer")
        if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
            raise AdoptionRoutingError(
                f"routing request.routes[{index}].extract.pointer must be a non-root JSON Pointer"
            )
        normalized_extract = {
            "id": extract_id,
            "sourceId": _identifier(
                extract.get("sourceId"),
                f"routing request.routes[{index}].extract.sourceId",
            ),
            "pointer": pointer,
            "valueSha256": _sha256(
                extract.get("valueSha256"),
                f"routing request.routes[{index}].extract.valueSha256",
            ),
        }
        disposition = route.get("disposition")
        if disposition not in {"routed", "unsupported", "blocked"}:
            raise AdoptionRoutingError(
                f"routing request.routes[{index}].disposition is unsupported"
            )
        reason_code = route.get("reasonCode")
        targets = _array(
            route.get("targets"), f"routing request.routes[{index}].targets"
        )
        normalized_targets: list[dict[str, str]] = []
        target_pairs: set[tuple[str, str]] = set()
        for target_index, raw_target in enumerate(targets):
            target = _object(
                raw_target,
                f"routing request.routes[{index}].targets[{target_index}]",
            )
            if set(target) != {"owner", "capability"}:
                raise AdoptionRoutingError(
                    f"routing request.routes[{index}].targets[{target_index}] has an unexpected field set"
                )
            pair = (
                _identifier(
                    target.get("owner"),
                    f"routing request.routes[{index}].targets[{target_index}].owner",
                ),
                _identifier(
                    target.get("capability"),
                    f"routing request.routes[{index}].targets[{target_index}].capability",
                ),
            )
            if pair not in ALL_TARGETS:
                raise AdoptionRoutingError(
                    f"routing request routes to unknown owner/capability pair {pair!r}"
                )
            if pair in target_pairs:
                raise AdoptionRoutingError(
                    f"routing request.routes[{index}] contains duplicate target {pair!r}"
                )
            target_pairs.add(pair)
            normalized_targets.append({"owner": pair[0], "capability": pair[1]})
        if len(normalized_targets) > MAX_TARGETS_PER_ROUTE:
            raise AdoptionRoutingError(
                f"routing request.routes[{index}] exceeds {MAX_TARGETS_PER_ROUTE} targets"
            )
        if disposition == "routed":
            if not normalized_targets or reason_code != ROUTED_REASON:
                raise AdoptionRoutingError(
                    f"routed route {route_id!r} requires targets and reasonCode {ROUTED_REASON!r}"
                )
        elif disposition == "unsupported":
            if normalized_targets or reason_code not in UNSUPPORTED_REASONS:
                raise AdoptionRoutingError(
                    f"unsupported route {route_id!r} must have no targets and a supported unsupported reason"
                )
        else:
            if normalized_targets or reason_code not in BLOCKED_REASONS:
                raise AdoptionRoutingError(
                    f"blocked route {route_id!r} must have no targets and a supported blocked reason"
                )
        normalized_targets.sort(key=lambda row: (row["owner"], row["capability"]))
        normalized_routes.append(
            {
                "id": route_id,
                "extract": normalized_extract,
                "disposition": disposition,
                "targets": normalized_targets,
                "reasonCode": reason_code,
                "contextReferences": _context_references(
                    route.get("contextReferences"),
                    f"routing request.routes[{index}].contextReferences",
                ),
            }
        )
        route_ids.add(route_id)
        extract_ids.add(extract_id)
    normalized_routes.sort(key=lambda row: row["id"])
    return {
        "format": REQUEST_FORMAT,
        "schemaVersion": 1,
        "gateway": normalized_gateway,
        "review": normalized_review,
        "routes": normalized_routes,
    }


def allowed_targets_for_fragment(kind: str, value: Any) -> set[tuple[str, str]]:
    if kind == "house":
        return {TARGET_OTBM_REPAIR}
    if kind == "proficiency":
        return {TARGET_WEAPON_PROFICIENCY}
    if not isinstance(value, Mapping):
        return set()
    if kind == "content":
        category = value.get("sourceCategory")
        if category in {"creatures", "monsters", "monsterClasses"}:
            return {TARGET_CYCLOPEDIA, TARGET_SPAWN_NPC}
        if category == "bosses":
            return {TARGET_CYCLOPEDIA, TARGET_SPAWN_NPC}
        if category in {"titles", "achievements"}:
            return {TARGET_ACHIEVEMENT}
        if category == "quests":
            return {TARGET_QUEST_MAP, TARGET_STORAGE_GRAPH}
        return set()
    if kind == "drift":
        component = value.get("component")
        family = value.get("family")
        if component == "package-metadata":
            return {TARGET_TCR_MANIFEST}
        if component == "staticmapdata":
            return {TARGET_TCR_HOUSE}
        if component == "proficiencies":
            return {TARGET_TCR_PROFICIENCY}
        if component == "staticdata":
            if family == "houses":
                return {TARGET_TCR_HOUSE}
            if family in {
                "creatures",
                "monsters",
                "monsterClasses",
                "titles",
                "achievements",
                "bosses",
                "quests",
            }:
                return {TARGET_TCR_CONTENT}
        return set()
    return set()


def build_routing_report(
    gateway_document: Mapping[str, Any],
    request_document: Mapping[str, Any],
    *,
    gateway_file_sha256: str,
    request_file_sha256: str,
) -> dict[str, Any]:
    gateway = validate_gateway_report(gateway_document)
    request = normalize_request(request_document)
    actual_gateway_file_sha = _sha256(
        gateway_file_sha256, "gateway_file_sha256"
    )
    actual_request_file_sha = _sha256(request_file_sha256, "request_file_sha256")
    expected_gateway = request["gateway"]
    exact_gateway_identity = {
        "fileSha256": actual_gateway_file_sha,
        "reportSha256": gateway["reportSha256"],
        "evidenceBundleSha256": gateway["evidenceBundleSha256"],
        "bindingId": gateway["bindingId"],
        "kind": gateway["kind"],
    }
    if expected_gateway != exact_gateway_identity:
        raise AdoptionRoutingError(
            "routing request gateway identity does not match the exact executed TCR-010 report"
        )
    extracts_by_id = {row["id"]: row for row in gateway["extracts"]}
    request_extract_ids = {row["extract"]["id"] for row in request["routes"]}
    if request_extract_ids != set(extracts_by_id):
        missing = sorted(set(extracts_by_id) - request_extract_ids)
        extra = sorted(request_extract_ids - set(extracts_by_id))
        raise AdoptionRoutingError(
            f"routing request must cover every gateway extract exactly once; missing={missing}, extra={extra}"
        )
    normalized_routes: list[dict[str, Any]] = []
    for route in request["routes"]:
        actual_extract = extracts_by_id[route["extract"]["id"]]
        actual_identity = {
            "id": actual_extract["id"],
            "sourceId": actual_extract["sourceId"],
            "pointer": actual_extract["pointer"],
            "valueSha256": actual_extract["valueSha256"],
        }
        if route["extract"] != actual_identity:
            raise AdoptionRoutingError(
                f"route {route['id']!r} does not pin the exact gateway extract identity"
            )
        if route["disposition"] == "routed":
            allowed = allowed_targets_for_fragment(gateway["kind"], actual_extract["value"])
            selected = {
                (target["owner"], target["capability"])
                for target in route["targets"]
            }
            if not allowed or not selected.issubset(allowed):
                raise AdoptionRoutingError(
                    f"route {route['id']!r} selects an owner/capability not supported by the exact {gateway['kind']} fragment"
                )
        if (
            gateway["kind"] == "house"
            and route["disposition"] == "unsupported"
            and route["reasonCode"] != "unsupported-map-change-shape"
        ):
            raise AdoptionRoutingError(
                "unsupported house routing must preserve unsupported-map-change-shape"
            )
        normalized_routes.append(route)
    normalized_routes.sort(key=lambda row: row["id"])
    disposition_counts = Counter(row["disposition"] for row in normalized_routes)
    owner_counts: Counter[str] = Counter()
    capability_counts: Counter[str] = Counter()
    target_count = 0
    for route in normalized_routes:
        for target in route["targets"]:
            owner_counts[target["owner"]] += 1
            capability_counts[target["capability"]] += 1
            target_count += 1
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": 1,
        "gateway": {
            "format": GATEWAY_FORMAT,
            **exact_gateway_identity,
            "contextReferences": gateway["contextReferences"],
        },
        "request": {
            "format": REQUEST_FORMAT,
            "fileSha256": actual_request_file_sha,
            "canonicalSha256": canonical_sha256(request),
            "review": request["review"],
        },
        "routes": normalized_routes,
        "summary": {
            "extractCount": len(normalized_routes),
            "routedCount": disposition_counts.get("routed", 0),
            "unsupportedCount": disposition_counts.get("unsupported", 0),
            "blockedCount": disposition_counts.get("blocked", 0),
            "targetCount": target_count,
            "ownerCounts": dict(sorted(owner_counts.items())),
            "capabilityCounts": dict(sorted(capability_counts.items())),
        },
        "policy": {
            "readOnlyRouting": True,
            "reviewedRequestRequired": True,
            "exactFindingReferencesRequired": True,
            "infersMutationTarget": False,
            "expandsWriters": False,
            "generatesApproval": False,
            "executesWriterOrMaterializer": False,
            "mutatesMapOrGameState": False,
            "deploys": False,
            "runsE2e": False,
            "claimsGameplayParity": False,
            "mapChangesRouteThroughQa003": True,
            "unsupportedOutcomesPreserved": True,
        },
    }
    report["reportSha256"] = canonical_sha256(report)
    return report
