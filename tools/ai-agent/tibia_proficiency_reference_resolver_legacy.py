from __future__ import annotations

from typing import Mapping

from tibia_proficiency_reference_common import (
    APPEARANCES_INDEX_FORMAT,
    DEFAULT_MAX_RECORDS,
    PROFICIENCY_INDEX_FORMAT,
    RESOLVER_FORMAT,
    SCHEMA_VERSION,
    ProficiencyReferenceCorrelationError,
    index_by_id,
    is_sha256,
    nonempty,
    semantic_sha,
    uint,
)
from tibia_proficiency_reference_inventory import validate_canary_evidence


def validate_proficiency_index(payload: Mapping[str, object], *, max_records: int) -> list[dict[str, object]]:
    if payload.get("format") != PROFICIENCY_INDEX_FORMAT:
        raise ProficiencyReferenceCorrelationError(f"proficiency index format must be {PROFICIENCY_INDEX_FORMAT}")
    if payload.get("schemaVersion") != 1:
        raise ProficiencyReferenceCorrelationError("proficiency index schemaVersion must be 1")
    source = payload.get("source")
    if not isinstance(source, dict):
        raise ProficiencyReferenceCorrelationError("proficiency index source must be an object")
    nonempty(source.get("referenceId"), "proficiency index source.referenceId")
    for key in ("manifestSha256", "sha256"):
        if not is_sha256(source.get(key)):
            raise ProficiencyReferenceCorrelationError(f"proficiency index source.{key} must be SHA-256")
    namespaces = payload.get("identifierNamespaces")
    if not isinstance(namespaces, dict):
        raise ProficiencyReferenceCorrelationError("proficiency index identifierNamespaces must be an object")
    proficiency_ns = namespaces.get("proficiencyId")
    if not isinstance(proficiency_ns, dict) or proficiency_ns.get("name") != "client-reference.proficiency-id":
        raise ProficiencyReferenceCorrelationError("proficiency index namespace must be client-reference.proficiency-id")
    records = payload.get("proficiencies")
    if not isinstance(records, list) or len(records) > max_records:
        raise ProficiencyReferenceCorrelationError("proficiency index proficiencies must be a bounded array")
    normalized: list[dict[str, object]] = []
    for ordinal, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ProficiencyReferenceCorrelationError(f"proficiency index record {ordinal} must be an object")
        item = dict(record)
        item["sourceOrdinal"] = uint(item.get("sourceOrdinal"), "sourceOrdinal", positive=True)
        item["proficiencyId"] = uint(item.get("proficiencyId"), "proficiencyId", positive=True)
        item["name"] = nonempty(item.get("name"), "proficiency name")
        if not isinstance(item.get("levels"), list):
            raise ProficiencyReferenceCorrelationError("proficiency levels must be an array")
        item["semanticSha256"] = semantic_sha(item)
        normalized.append(item)
    return normalized


def validate_appearances(payload: Mapping[str, object], *, max_records: int) -> list[dict[str, object]]:
    if payload.get("format") != APPEARANCES_INDEX_FORMAT:
        raise ProficiencyReferenceCorrelationError(f"appearances format must be {APPEARANCES_INDEX_FORMAT}")
    source = payload.get("source")
    if not isinstance(source, dict) or not is_sha256(source.get("sha256")):
        raise ProficiencyReferenceCorrelationError("appearances source.sha256 must be SHA-256")
    records = payload.get("appearances")
    if not isinstance(records, list) or len(records) > max_records:
        raise ProficiencyReferenceCorrelationError("appearances must be a bounded array")
    bindings: list[dict[str, object]] = []
    for ordinal, record in enumerate(records, start=1):
        if not isinstance(record, dict) or record.get("category") != "object":
            continue
        object_id = record.get("id")
        if not isinstance(object_id, int) or isinstance(object_id, bool) or object_id < 0:
            continue
        flags = record.get("flags")
        proficiency = flags.get("proficiency") if isinstance(flags, dict) else None
        proficiency_id = proficiency.get("id") if isinstance(proficiency, dict) else None
        if not isinstance(proficiency_id, int) or isinstance(proficiency_id, bool) or proficiency_id <= 0:
            continue
        bindings.append(
            {
                "sourceOrdinal": ordinal,
                "appearanceObjectId": object_id,
                "appearanceProficiencyId": proficiency_id,
                "name": record.get("name") if isinstance(record.get("name"), str) else "",
            }
        )
    return bindings


def derive_resolver(
    *,
    proficiency_index: Mapping[str, object],
    proficiency_index_sha256: str,
    appearances_index: Mapping[str, object],
    appearances_index_sha256: str,
    canary_evidence: Mapping[str, object],
    canary_evidence_sha256: str,
    review_id: str,
    review_statement: str,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> dict[str, object]:
    sources = validate_proficiency_index(proficiency_index, max_records=max_records)
    bindings = validate_appearances(appearances_index, max_records=max_records)
    runtime = validate_canary_evidence(canary_evidence, max_records=max_records)
    for digest, label in (
        (proficiency_index_sha256, "proficiency index SHA-256"),
        (appearances_index_sha256, "appearances index SHA-256"),
        (canary_evidence_sha256, "Canary evidence SHA-256"),
    ):
        if not is_sha256(digest):
            raise ProficiencyReferenceCorrelationError(f"{label} is invalid")
    review_id = nonempty(review_id, "reviewId")
    review_statement = nonempty(review_statement, "reviewStatement")
    source_by_id = index_by_id(sources, "proficiencyId")
    runtime_by_id = index_by_id(runtime, "proficiencyId")
    bindings_by_id = index_by_id(bindings, "appearanceProficiencyId")
    object_by_id = index_by_id(bindings, "appearanceObjectId")

    mappings: list[dict[str, object]] = []
    findings: list[dict[str, object]] = []
    for source in sources:
        source_id = int(source["proficiencyId"])
        source_ordinal = int(source["sourceOrdinal"])
        runtime_candidates = runtime_by_id.get(source_id, [])
        binding_candidates = bindings_by_id.get(source_id, [])
        reasons: list[str] = []
        if len(source_by_id[source_id]) != 1:
            reasons.append("duplicate-source-proficiency-id")
        if len(runtime_candidates) != 1:
            reasons.append("missing-or-duplicate-runtime-definition")
        elif runtime_candidates[0]["semanticSha256"] != source["semanticSha256"]:
            reasons.append("definition-semantics-mismatch")
        if not binding_candidates:
            reasons.append("appearance-binding-missing")
        if any(len(object_by_id[int(binding["appearanceObjectId"])]) != 1 for binding in binding_candidates):
            reasons.append("duplicate-appearance-object-id")
        if reasons:
            findings.append(
                {
                    "sourceOrdinal": source_ordinal,
                    "sourceProficiencyId": source_id,
                    "state": "conflicting"
                    if any("duplicate" in reason or "mismatch" in reason for reason in reasons)
                    else "unresolved-id-space",
                    "reasons": sorted(set(reasons)),
                }
            )
            continue
        items = [
            {
                "appearanceObjectId": int(binding["appearanceObjectId"]),
                "canaryItemId": int(binding["appearanceObjectId"]),
                "appearanceName": binding["name"],
                "method": "reviewed-canary-protobuf-loader-object-id",
            }
            for binding in sorted(
                binding_candidates,
                key=lambda item: (int(item["appearanceObjectId"]), int(item["sourceOrdinal"])),
            )
        ]
        mappings.append(
            {
                "sourceOrdinal": source_ordinal,
                "sourceProficiencyId": source_id,
                "appearanceProficiencyId": source_id,
                "runtimeProficiencyId": source_id,
                "method": "reviewed-exact-definition-and-loader-binding",
                "semanticSha256": source["semanticSha256"],
                "items": items,
            }
        )
    return {
        "format": RESOLVER_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "review": {"id": review_id, "statement": review_statement},
        "inputs": {
            "proficiencyIndexSha256": proficiency_index_sha256,
            "appearancesIndexSha256": appearances_index_sha256,
            "canaryEvidenceSha256": canary_evidence_sha256,
            "referenceId": proficiency_index["source"]["referenceId"],
            "repositoryHead": canary_evidence["repositoryHead"],
        },
        "identifierNamespaces": {
            "source": "client-reference.proficiency-id",
            "appearanceProficiency": "appearance.proficiency-id",
            "appearanceObject": "appearance.object-id",
            "runtimeProficiency": "canary.runtime-proficiency-id",
            "canaryItem": "canary.item-id",
        },
        "mappings": sorted(mappings, key=lambda item: (int(item["sourceProficiencyId"]), int(item["sourceOrdinal"]))),
        "findings": sorted(findings, key=lambda item: (int(item["sourceProficiencyId"]), int(item["sourceOrdinal"]))),
        "summary": {
            "sourceCount": len(sources),
            "mappingCount": len(mappings),
            "findingCount": len(findings),
            "appearanceBindingCount": len(bindings),
            "runtimeDefinitionCount": len(runtime),
        },
        "policy": {
            "numericEqualityAloneAccepted": False,
            "requiresReviewedResolver": True,
            "reparsesClientSource": False,
            "reparsesAppearances": False,
            "mutatesSources": False,
            "gameplayConclusions": False,
        },
    }


def validate_resolver(
    payload: Mapping[str, object],
    *,
    proficiency_index_sha256: str,
    appearances_index_sha256: str,
    canary_evidence_sha256: str,
    max_records: int,
) -> list[dict[str, object]]:
    if payload.get("format") != RESOLVER_FORMAT or payload.get("schemaVersion") != 1:
        raise ProficiencyReferenceCorrelationError(f"resolver format must be {RESOLVER_FORMAT} v1")
    inputs = payload.get("inputs")
    if not isinstance(inputs, dict):
        raise ProficiencyReferenceCorrelationError("resolver inputs must be an object")
    expected = {
        "proficiencyIndexSha256": proficiency_index_sha256,
        "appearancesIndexSha256": appearances_index_sha256,
        "canaryEvidenceSha256": canary_evidence_sha256,
    }
    for key, digest in expected.items():
        if inputs.get(key) != digest:
            raise ProficiencyReferenceCorrelationError(f"resolver {key} provenance mismatch")
    review = payload.get("review")
    if not isinstance(review, dict):
        raise ProficiencyReferenceCorrelationError("resolver review must be an object")
    nonempty(review.get("id"), "resolver review.id")
    nonempty(review.get("statement"), "resolver review.statement")
    records = payload.get("mappings")
    if not isinstance(records, list) or len(records) > max_records:
        raise ProficiencyReferenceCorrelationError("resolver mappings must be a bounded array")
    normalized: list[dict[str, object]] = []
    seen_ordinals: set[int] = set()
    for ordinal, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ProficiencyReferenceCorrelationError(f"resolver mapping {ordinal} must be an object")
        item = dict(record)
        source_ordinal = uint(item.get("sourceOrdinal"), "resolver sourceOrdinal", positive=True)
        if source_ordinal in seen_ordinals:
            raise ProficiencyReferenceCorrelationError(f"duplicate resolver sourceOrdinal {source_ordinal}")
        seen_ordinals.add(source_ordinal)
        source_id = uint(item.get("sourceProficiencyId"), "resolver sourceProficiencyId", positive=True)
        if item.get("appearanceProficiencyId") != source_id or item.get("runtimeProficiencyId") != source_id:
            raise ProficiencyReferenceCorrelationError("resolver proficiency IDs must match the reviewed source mapping")
        if item.get("method") != "reviewed-exact-definition-and-loader-binding":
            raise ProficiencyReferenceCorrelationError("resolver mapping method is unsupported")
        if not is_sha256(item.get("semanticSha256")):
            raise ProficiencyReferenceCorrelationError("resolver semanticSha256 must be SHA-256")
        items = item.get("items")
        if not isinstance(items, list):
            raise ProficiencyReferenceCorrelationError("resolver items must be an array")
        seen_items: set[int] = set()
        for mapped_item in items:
            if not isinstance(mapped_item, dict):
                raise ProficiencyReferenceCorrelationError("resolver item mapping must be an object")
            appearance_id = uint(mapped_item.get("appearanceObjectId"), "appearanceObjectId")
            canary_id = uint(mapped_item.get("canaryItemId"), "canaryItemId")
            if appearance_id != canary_id or mapped_item.get("method") != "reviewed-canary-protobuf-loader-object-id":
                raise ProficiencyReferenceCorrelationError("resolver item mapping is not loader-backed")
            if canary_id in seen_items:
                raise ProficiencyReferenceCorrelationError(f"duplicate resolver canary item ID {canary_id}")
            seen_items.add(canary_id)
        normalized.append(item)
    return normalized
