from __future__ import annotations

from tibia_proficiency_reference_correlation import (
    APPEARANCES_INDEX_FORMAT, CANARY_EVIDENCE_FORMAT, PROFICIENCY_INDEX_FORMAT,
    _semantic_sha, derive_resolver,
)

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64

def source_entry(proficiency_id: int = 10, name: str = "Test Blade", ordinal: int = 1) -> dict[str, object]:
    entry: dict[str, object] = {
        "sourceOrdinal": ordinal,
        "proficiencyId": proficiency_id,
        "name": name,
        "levels": [
            {
                "sourceOrdinal": 1,
                "perks": [{"sourceOrdinal": 1, "type": 1, "value": 2}],
            }
        ],
    }
    return entry

def proficiency_index(entries: list[dict[str, object]] | None = None) -> dict[str, object]:
    records = entries or [source_entry()]
    return {
        "format": PROFICIENCY_INDEX_FORMAT,
        "schemaVersion": 1,
        "source": {
            "referenceId": "ref-1",
            "manifestSha256": SHA_A,
            "sha256": SHA_B,
        },
        "identifierNamespaces": {
            "proficiencyId": {
                "name": "client-reference.proficiency-id",
                "resolution": "definition-only",
            }
        },
        "proficiencies": records,
    }

def appearances(bindings: list[tuple[int, int, str]] | None = None) -> dict[str, object]:
    rows = bindings if bindings is not None else [(100, 10, "Test Blade")]
    return {
        "format": APPEARANCES_INDEX_FORMAT,
        "source": {"sha256": SHA_C},
        "appearances": [
            {
                "category": "object",
                "id": item_id,
                "name": name,
                "flags": {"proficiency": {"id": proficiency_id}},
            }
            for item_id, proficiency_id, name in rows
        ],
    }

def canary_evidence(
    entries: list[dict[str, object]] | None = None,
    *,
    protocol: str = "not-supplied",
    automated: str = "not-supplied",
    physical: str = "not-supplied",
) -> dict[str, object]:
    source = source_entry()
    records = entries or [
        {
            "sourceOrdinal": 1,
            "proficiencyId": 10,
            "name": "Test Blade",
            "semanticSha256": _semantic_sha(source),
        }
    ]
    return {
        "format": CANARY_EVIDENCE_FORMAT,
        "schemaVersion": 1,
        "repositoryHead": "1" * 40,
        "runtimeDefinitions": {
            "source": {"path": "data/items/proficiencies.json", "sha256": SHA_D},
            "recordCount": len(records),
            "records": records,
        },
        "itemBindingContract": {
            "method": "reviewed-canary-protobuf-loader",
            "source": {"sha256": SHA_A, "supported": True},
            "objectIdAssignsItemId": True,
            "proficiencyFlagAssignsRuntimeBinding": True,
            "unknownRuntimeDefinitionsRejected": True,
        },
        "runtimeSupport": {
            "source": {"sha256": SHA_B, "supported": True},
            "definitionLoading": "source-supported",
            "persistence": "source-supported",
        },
        "optionalDimensions": {
            "protocolClient": protocol,
            "automatedBehavior": automated,
            "physicalE2E": physical,
        },
        "policy": {"clientInputsIncluded": False},
    }

def resolved_fixture(
    source: dict[str, object] | None = None,
    appearance: dict[str, object] | None = None,
    evidence: dict[str, object] | None = None,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    source = source or proficiency_index()
    appearance = appearance or appearances()
    evidence = evidence or canary_evidence()
    resolver = derive_resolver(
        proficiency_index=source,
        proficiency_index_sha256=SHA_A,
        appearances_index=appearance,
        appearances_index_sha256=SHA_B,
        canary_evidence=evidence,
        canary_evidence_sha256=SHA_C,
        review_id="review-1",
        review_statement="Exact reviewed fixture mapping.",
    )
    return source, appearance, evidence, resolver

