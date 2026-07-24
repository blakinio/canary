from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

from tibia_proficiency_reference_common import (
    CANARY_EVIDENCE_FORMAT,
    DEFAULT_MAX_JSON_BYTES,
    DEFAULT_MAX_RECORDS,
    SCHEMA_VERSION,
    ProficiencyReferenceCorrelationError,
    is_sha256,
    load_json_array,
    nonempty,
    repo_head,
    semantic_sha,
    source_evidence,
    uint,
)


def normalize_runtime_definitions(payload: Sequence[object], *, max_records: int) -> list[dict[str, object]]:
    if len(payload) > max_records:
        raise ProficiencyReferenceCorrelationError(f"runtime proficiency count exceeds {max_records}")
    try:
        from tibia_proficiency_reference_index import _parse_proficiencies
    except ImportError as exc:
        raise ProficiencyReferenceCorrelationError("TCR-004 proficiency parser must be importable") from exc
    try:
        normalized, findings, _ = _parse_proficiencies(
            list(payload),
            max_proficiencies=max_records,
            max_levels=max_records * 100,
            max_perks=max_records * 1000,
        )
    except Exception as exc:
        raise ProficiencyReferenceCorrelationError(f"Canary proficiency definitions are invalid: {exc}") from exc
    if not isinstance(findings.get("duplicateProficiencyIds", []), list):
        raise ProficiencyReferenceCorrelationError("reused TCR-004 findings are malformed")
    return [
        {
            "sourceOrdinal": entry["sourceOrdinal"],
            "proficiencyId": entry["proficiencyId"],
            "name": entry["name"],
            "semanticSha256": semantic_sha(entry),
        }
        for entry in normalized
    ]


def build_canary_evidence(repository_root: Path, *, max_records: int = DEFAULT_MAX_RECORDS) -> dict[str, object]:
    root = repository_root.expanduser().resolve(strict=True)
    runtime_payload, runtime_sha, runtime_path = load_json_array(
        root / "data/items/proficiencies.json",
        max_bytes=DEFAULT_MAX_JSON_BYTES,
        label="Canary proficiency definitions",
    )
    runtime_definitions = normalize_runtime_definitions(runtime_payload, max_records=max_records)
    items_loader = source_evidence(
        root / "src/items/items.cpp",
        required_markers=(
            "ItemType &iType = items[object.id()]",
            "iType.id = static_cast<uint16_t>(object.id())",
            "object.flags().has_proficiency()",
            "iType.proficiencyId = proficiencyId",
            "WeaponProficiency::getProficiencies()",
        ),
        label="Canary item loader source",
    )
    items_loader["path"] = "src/items/items.cpp"
    runtime_source = source_evidence(
        root / "src/creatures/players/components/weapon_proficiency.cpp",
        required_markers=(
            'fmt::format("{}/items/proficiencies.json", coreFolder)',
            'proficiency.id = proficiencyJson["ProficiencyId"].get<uint16_t>()',
            'm_player.kv()->scoped("weapon-proficiency")',
            "Item::items[weaponId].proficiencyId == 0",
        ),
        label="Weapon Proficiency runtime source",
    )
    runtime_source["path"] = "src/creatures/players/components/weapon_proficiency.cpp"
    return {
        "format": CANARY_EVIDENCE_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "repositoryHead": repo_head(root),
        "runtimeDefinitions": {
            "source": {"path": runtime_path.relative_to(root).as_posix(), "sha256": runtime_sha},
            "recordCount": len(runtime_definitions),
            "records": runtime_definitions,
        },
        "itemBindingContract": {
            "appearanceObjectIdNamespace": "appearance.object-id",
            "canaryItemIdNamespace": "canary.item-id",
            "appearanceProficiencyIdNamespace": "appearance.proficiency-id",
            "runtimeProficiencyIdNamespace": "canary.runtime-proficiency-id",
            "method": "reviewed-canary-protobuf-loader",
            "source": items_loader,
            "objectIdAssignsItemId": bool(items_loader["supported"]),
            "proficiencyFlagAssignsRuntimeBinding": bool(items_loader["supported"]),
            "unknownRuntimeDefinitionsRejected": bool(items_loader["supported"]),
        },
        "runtimeSupport": {
            "method": "reviewed-weapon-proficiency-source",
            "source": runtime_source,
            "definitionLoading": "source-supported" if runtime_source["supported"] else "unresolved",
            "persistence": "source-supported" if runtime_source["supported"] else "unresolved",
        },
        "optionalDimensions": {
            "protocolClient": "not-supplied",
            "automatedBehavior": "not-supplied",
            "physicalE2E": "not-supplied",
        },
        "policy": {
            "clientInputsIncluded": False,
            "appearanceParsing": False,
            "runtimeExecution": False,
            "itemsXmlWriting": False,
            "runtimeMutation": False,
            "protocolMutation": False,
            "gameplayConclusions": False,
        },
    }


def validate_canary_evidence(payload: Mapping[str, object], *, max_records: int) -> list[dict[str, object]]:
    if payload.get("format") != CANARY_EVIDENCE_FORMAT or payload.get("schemaVersion") != 1:
        raise ProficiencyReferenceCorrelationError(f"Canary evidence format must be {CANARY_EVIDENCE_FORMAT} v1")
    nonempty(payload.get("repositoryHead"), "Canary evidence repositoryHead")
    policy = payload.get("policy")
    if not isinstance(policy, dict) or policy.get("clientInputsIncluded") is not False:
        raise ProficiencyReferenceCorrelationError("Canary evidence must exclude client inputs")
    contract = payload.get("itemBindingContract")
    if not isinstance(contract, dict) or contract.get("method") != "reviewed-canary-protobuf-loader":
        raise ProficiencyReferenceCorrelationError("Canary item binding contract is missing")
    required = ("objectIdAssignsItemId", "proficiencyFlagAssignsRuntimeBinding", "unknownRuntimeDefinitionsRejected")
    if not all(contract.get(key) is True for key in required):
        raise ProficiencyReferenceCorrelationError("Canary item binding contract is unresolved")
    source = contract.get("source")
    if not isinstance(source, dict) or not is_sha256(source.get("sha256")) or source.get("supported") is not True:
        raise ProficiencyReferenceCorrelationError("Canary item binding source evidence is unresolved")
    runtime = payload.get("runtimeDefinitions")
    if not isinstance(runtime, dict):
        raise ProficiencyReferenceCorrelationError("Canary runtimeDefinitions must be an object")
    runtime_source = runtime.get("source")
    if not isinstance(runtime_source, dict) or not is_sha256(runtime_source.get("sha256")):
        raise ProficiencyReferenceCorrelationError("Canary runtime definition source hash must be SHA-256")
    records = runtime.get("records")
    if not isinstance(records, list) or runtime.get("recordCount") != len(records) or len(records) > max_records:
        raise ProficiencyReferenceCorrelationError("Canary runtime definition count mismatch")
    normalized: list[dict[str, object]] = []
    for ordinal, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ProficiencyReferenceCorrelationError(f"Canary runtime definition {ordinal} must be an object")
        item = dict(record)
        item["sourceOrdinal"] = uint(item.get("sourceOrdinal"), "runtime sourceOrdinal", positive=True)
        item["proficiencyId"] = uint(item.get("proficiencyId"), "runtime proficiencyId", positive=True)
        item["name"] = nonempty(item.get("name"), "runtime proficiency name")
        if not is_sha256(item.get("semanticSha256")):
            raise ProficiencyReferenceCorrelationError("runtime semanticSha256 must be SHA-256")
        normalized.append(item)
    support = payload.get("runtimeSupport")
    if not isinstance(support, dict):
        raise ProficiencyReferenceCorrelationError("Canary runtimeSupport must be an object")
    support_source = support.get("source")
    if not isinstance(support_source, dict) or not is_sha256(support_source.get("sha256")):
        raise ProficiencyReferenceCorrelationError("Canary runtime support source hash must be SHA-256")
    return normalized
