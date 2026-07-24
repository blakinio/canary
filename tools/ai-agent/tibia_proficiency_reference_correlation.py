from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Mapping

from tibia_proficiency_reference_common import (
    ALLOWED_STATES,
    APPEARANCES_INDEX_FORMAT,
    CANARY_EVIDENCE_FORMAT,
    CORRELATION_FORMAT,
    DEFAULT_MAX_JSON_BYTES,
    DEFAULT_MAX_RECORDS,
    PROFICIENCY_INDEX_FORMAT,
    RESOLVER_FORMAT,
    SCHEMA_VERSION,
    ProficiencyReferenceCorrelationError,
    deterministic_json,
    index_by_id,
    is_sha256,
    load_json,
    semantic_sha,
    write_json,
)
from tibia_proficiency_reference_inventory import build_canary_evidence, validate_canary_evidence
from tibia_proficiency_reference_resolver import (
    derive_resolver,
    validate_appearances,
    validate_proficiency_index,
    validate_resolver,
)

# Backward-compatible test/helper alias. It remains an internal implementation detail.
_semantic_sha = semantic_sha


def build_correlation(
    *,
    proficiency_index: Mapping[str, object],
    proficiency_index_sha256: str,
    appearances_index: Mapping[str, object],
    appearances_index_sha256: str,
    canary_evidence: Mapping[str, object],
    canary_evidence_sha256: str,
    resolver: Mapping[str, object],
    resolver_sha256: str,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> dict[str, object]:
    sources = validate_proficiency_index(proficiency_index, max_records=max_records)
    bindings = validate_appearances(appearances_index, max_records=max_records)
    runtime = validate_canary_evidence(canary_evidence, max_records=max_records)
    mappings = validate_resolver(
        resolver,
        proficiency_index_sha256=proficiency_index_sha256,
        appearances_index_sha256=appearances_index_sha256,
        canary_evidence_sha256=canary_evidence_sha256,
        max_records=max_records,
    )
    if not is_sha256(resolver_sha256):
        raise ProficiencyReferenceCorrelationError("resolver SHA-256 is invalid")

    source_by_id = index_by_id(sources, "proficiencyId")
    binding_by_id = index_by_id(bindings, "appearanceProficiencyId")
    runtime_by_id = index_by_id(runtime, "proficiencyId")
    mapping_by_ordinal = {int(mapping["sourceOrdinal"]): mapping for mapping in mappings}
    rows: list[dict[str, object]] = []
    mapped_proficiency_ids: set[int] = set()

    runtime_support = canary_evidence.get("runtimeSupport", {})
    optional = canary_evidence.get("optionalDimensions", {})
    if not isinstance(runtime_support, dict) or not isinstance(optional, dict):
        raise ProficiencyReferenceCorrelationError("Canary evidence dimensions must be objects")

    for source in sources:
        source_ordinal = int(source["sourceOrdinal"])
        source_id = int(source["proficiencyId"])
        mapping = mapping_by_ordinal.get(source_ordinal)
        source_duplicates = len(source_by_id[source_id]) > 1
        binding_candidates = binding_by_id.get(source_id, [])
        runtime_candidates = runtime_by_id.get(source_id, [])
        semantic_match = (
            len(runtime_candidates) == 1
            and runtime_candidates[0]["semanticSha256"] == source["semanticSha256"]
        )
        if source_duplicates or len(runtime_candidates) > 1:
            state = "conflicting"
        elif mapping is not None:
            state = "confirmed-reference" if semantic_match and binding_candidates else "partial"
            mapped_proficiency_ids.add(source_id)
        elif binding_candidates or runtime_candidates:
            state = "unresolved-id-space"
        else:
            state = "reference-only"
        if state not in ALLOWED_STATES:
            raise AssertionError(state)

        mapped_items = mapping.get("items", []) if isinstance(mapping, dict) else []
        rows.append(
            {
                "rowKind": "source",
                "sourceOrdinal": source_ordinal,
                "sourceProficiencyId": source_id,
                "sourceName": source["name"],
                "state": state,
                "dimensions": {
                    "definition": "present",
                    "appearanceBinding": (
                        "confirmed"
                        if mapping is not None and binding_candidates
                        else ("candidate" if binding_candidates else "missing")
                    ),
                    "canaryItemBinding": "confirmed" if mapped_items else ("candidate" if binding_candidates else "missing"),
                    "definitionSemantics": (
                        "confirmed"
                        if mapping is not None and semantic_match
                        else ("conflicting" if runtime_candidates and not semantic_match else "missing")
                    ),
                    "runtimeSupport": runtime_support.get("definitionLoading", "not-supplied"),
                    "persistence": runtime_support.get("persistence", "not-supplied"),
                    "protocolClient": optional.get("protocolClient", "not-supplied"),
                    "automatedBehavior": optional.get("automatedBehavior", "not-supplied"),
                    "physicalE2E": optional.get("physicalE2E", "not-supplied"),
                },
                "appearanceBindings": [
                    {
                        "appearanceObjectId": int(binding["appearanceObjectId"]),
                        "appearanceProficiencyId": int(binding["appearanceProficiencyId"]),
                        "name": binding["name"],
                    }
                    for binding in sorted(binding_candidates, key=lambda item: int(item["appearanceObjectId"]))
                ],
                "canaryItems": list(mapped_items),
                "runtimeDefinition": runtime_candidates[0] if len(runtime_candidates) == 1 else None,
            }
        )

    target_only: list[dict[str, object]] = []
    for target_id in sorted(set(binding_by_id) | set(runtime_by_id)):
        if target_id in mapped_proficiency_ids:
            continue
        target_only.append(
            {
                "rowKind": "target-only",
                "targetProficiencyId": target_id,
                "state": "target-only",
                "appearanceBindingCount": len(binding_by_id.get(target_id, [])),
                "runtimeDefinitionCount": len(runtime_by_id.get(target_id, [])),
            }
        )

    all_rows = rows + target_only
    state_counts = Counter(str(row["state"]) for row in all_rows)
    return {
        "format": CORRELATION_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "inputs": {
            "proficiencyIndexSha256": proficiency_index_sha256,
            "appearancesIndexSha256": appearances_index_sha256,
            "canaryEvidenceSha256": canary_evidence_sha256,
            "resolverSha256": resolver_sha256,
            "referenceId": proficiency_index["source"]["referenceId"],
            "repositoryHead": canary_evidence["repositoryHead"],
        },
        "rows": all_rows,
        "summary": {
            "sourceRowCount": len(rows),
            "targetOnlyRowCount": len(target_only),
            "rowCount": len(all_rows),
            "stateCounts": {state: state_counts.get(state, 0) for state in sorted(ALLOWED_STATES)},
            "appearanceBindingCount": len(bindings),
            "runtimeDefinitionCount": len(runtime),
        },
        "policy": {
            "definitionAppearanceItemRuntimeSeparated": True,
            "protocolAutomatedE2ESeparated": True,
            "numericEqualityAloneAccepted": False,
            "reparsesClientSource": False,
            "reparsesAppearances": False,
            "writesItemsXml": False,
            "mutatesRuntimeOrProtocol": False,
            "gameplayConclusions": False,
        },
    }


def load_inputs(
    *,
    proficiency_index_path: Path,
    appearances_index_path: Path,
    canary_evidence_path: Path,
    resolver_path: Path | None = None,
    max_json_bytes: int = DEFAULT_MAX_JSON_BYTES,
) -> tuple[
    dict[str, object],
    str,
    Path,
    dict[str, object],
    str,
    Path,
    dict[str, object],
    str,
    Path,
    tuple[dict[str, object], str, Path] | None,
]:
    proficiency, proficiency_sha, proficiency_resolved = load_json(
        proficiency_index_path, max_bytes=max_json_bytes, label="proficiency index"
    )
    appearances, appearances_sha, appearances_resolved = load_json(
        appearances_index_path, max_bytes=max_json_bytes, label="appearances index"
    )
    evidence, evidence_sha, evidence_resolved = load_json(
        canary_evidence_path, max_bytes=max_json_bytes, label="Canary evidence"
    )
    resolver_loaded = (
        load_json(resolver_path, max_bytes=max_json_bytes, label="resolver")
        if resolver_path is not None
        else None
    )
    return (
        proficiency,
        proficiency_sha,
        proficiency_resolved,
        appearances,
        appearances_sha,
        appearances_resolved,
        evidence,
        evidence_sha,
        evidence_resolved,
        resolver_loaded,
    )


__all__ = [
    "ALLOWED_STATES",
    "APPEARANCES_INDEX_FORMAT",
    "CANARY_EVIDENCE_FORMAT",
    "CORRELATION_FORMAT",
    "DEFAULT_MAX_JSON_BYTES",
    "DEFAULT_MAX_RECORDS",
    "PROFICIENCY_INDEX_FORMAT",
    "RESOLVER_FORMAT",
    "SCHEMA_VERSION",
    "ProficiencyReferenceCorrelationError",
    "_semantic_sha",
    "build_canary_evidence",
    "build_correlation",
    "derive_resolver",
    "deterministic_json",
    "load_inputs",
    "write_json",
]
