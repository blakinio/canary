from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

STATICDATA_FORMAT = "canary-tibia-staticdata-index-v1"
OWNER_INVENTORY_FORMAT = "canary-tcr006-owner-inventory-v1"
RESOLVER_FORMAT = "canary-tibia-content-reference-resolver-v1"
CORRELATION_FORMAT = "canary-tibia-content-reference-correlation-v1"
SCHEMA_VERSION = 1
DEFAULT_MAX_JSON_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_RECORDS = 2_000_000
_SHA256_LEN = 64
SOURCE_CATEGORIES = (
    "creatures",
    "monsters",
    "monsterClasses",
    "titles",
    "achievements",
    "bosses",
    "quests",
)
IDENTITY_TARGETS: dict[str, tuple[str, str, str]] = {
    "creatures": ("bestiary", "canary-bestiary-race-id", "reviewed-unique-id-name"),
    "monsters": ("bestiary", "canary-bestiary-race-id", "reviewed-unique-id-name"),
    "bosses": ("bosstiary", "canary-bosstiary-boss-race-id", "reviewed-unique-id-name"),
    "titles": ("achievement", "canary-achievement-id", "reviewed-unique-id-name-grade"),
    "achievements": ("achievement", "canary-achievement-id", "reviewed-unique-id-name-grade"),
}
PRESENCE_CATEGORIES = frozenset({"creatures", "monsters", "bosses"})
ALLOWED_STATES = frozenset(
    {
        "confirmed-reference",
        "reference-only",
        "target-only",
        "partial",
        "unresolved-id-space",
        "conflicting",
        "stale-evidence",
    }
)


class ContentReferenceCorrelationError(RuntimeError):
    pass


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ContentReferenceCorrelationError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _read_stable_file(path: Path, *, max_bytes: int, label: str) -> tuple[bytes, str, Path]:
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
        raise ContentReferenceCorrelationError(f"{label} max bytes must be positive")
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise ContentReferenceCorrelationError(f"{label} must not be a symlink")
    resolved = expanded.resolve(strict=True)
    before = resolved.stat()
    if before.st_size > max_bytes:
        raise ContentReferenceCorrelationError(f"{label} exceeds {max_bytes} bytes")
    data = resolved.read_bytes()
    after = resolved.stat()
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after or len(data) != after.st_size:
        raise ContentReferenceCorrelationError(f"{label} changed while reading")
    return data, hashlib.sha256(data).hexdigest(), resolved


def _load_json(path: Path, *, max_bytes: int, label: str) -> tuple[dict[str, object], str, Path]:
    data, digest, resolved = _read_stable_file(path, max_bytes=max_bytes, label=label)
    try:
        payload = json.loads(data.decode("utf-8"), object_pairs_hook=_object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContentReferenceCorrelationError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise ContentReferenceCorrelationError(f"{label} root must be an object")
    return payload, digest, resolved


def _is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != _SHA256_LEN:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContentReferenceCorrelationError(f"{label} must be a non-empty string")
    return value


def _uint(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ContentReferenceCorrelationError(f"{label} must be a non-negative integer")
    return value


def _normalize_name(value: str) -> str:
    return " ".join(value.casefold().replace("’", "'").split())


def _validate_staticdata(payload: Mapping[str, object], *, max_records: int) -> dict[str, list[dict[str, object]]]:
    if payload.get("format") != STATICDATA_FORMAT:
        raise ContentReferenceCorrelationError(f"StaticData format must be {STATICDATA_FORMAT}")
    version = payload.get("schemaVersion")
    if not isinstance(version, int) or isinstance(version, bool) or version < 2:
        raise ContentReferenceCorrelationError("StaticData schemaVersion must be at least 2")
    source = payload.get("source")
    if not isinstance(source, dict):
        raise ContentReferenceCorrelationError("StaticData source must be an object")
    _nonempty(source.get("referenceId"), "StaticData source.referenceId")
    if not _is_sha256(source.get("manifestSha256")) or not _is_sha256(source.get("sha256")):
        raise ContentReferenceCorrelationError("StaticData source hashes must be SHA-256")
    schema_family = source.get("schemaFamily")
    if schema_family not in {"legacy", "newer"}:
        raise ContentReferenceCorrelationError("StaticData source.schemaFamily must be legacy or newer")
    categories = payload.get("categories")
    if not isinstance(categories, dict):
        raise ContentReferenceCorrelationError("StaticData categories must be an object")
    result: dict[str, list[dict[str, object]]] = {}
    total = 0
    for category, document in categories.items():
        if not isinstance(category, str) or not isinstance(document, dict):
            raise ContentReferenceCorrelationError("StaticData category entries must be objects")
        if document.get("sourceCategory") not in {None, category}:
            raise ContentReferenceCorrelationError(f"StaticData category {category} sourceCategory mismatch")
        records = document.get("records")
        count = document.get("count")
        if not isinstance(records, list) or count != len(records):
            raise ContentReferenceCorrelationError(f"StaticData category {category} count mismatch")
        total += len(records)
        if total > max_records:
            raise ContentReferenceCorrelationError(f"StaticData record count exceeds {max_records}")
        seen_ids: set[int] = set()
        normalized: list[dict[str, object]] = []
        for ordinal, record in enumerate(records):
            if not isinstance(record, dict):
                raise ContentReferenceCorrelationError(f"StaticData {category} record {ordinal} must be an object")
            record_id = _uint(record.get("id"), f"StaticData {category} record id")
            name = _nonempty(record.get("name"), f"StaticData {category} record name")
            if record_id in seen_ids:
                raise ContentReferenceCorrelationError(f"duplicate StaticData {category} id {record_id}")
            seen_ids.add(record_id)
            normalized.append(dict(record, id=record_id, name=name))
        result[category] = normalized
    return result


def _validate_owner_section(
    payload: Mapping[str, object],
    key: str,
    *,
    allow_duplicate_ids: bool,
    max_records: int,
) -> list[dict[str, object]]:
    section = payload.get(key)
    if not isinstance(section, dict):
        raise ContentReferenceCorrelationError(f"owner inventory {key} must be an object")
    records = section.get("records")
    count = section.get("recordCount")
    if not isinstance(records, list) or count != len(records):
        raise ContentReferenceCorrelationError(f"owner inventory {key} count mismatch")
    if len(records) > max_records:
        raise ContentReferenceCorrelationError(f"owner inventory {key} exceeds {max_records} records")
    seen_ids: set[int] = set()
    normalized: list[dict[str, object]] = []
    for ordinal, record in enumerate(records):
        if not isinstance(record, dict):
            raise ContentReferenceCorrelationError(f"owner inventory {key} record {ordinal} must be an object")
        item = dict(record)
        if key != "spawnBossDefinitions":
            record_id = _uint(item.get("id"), f"owner inventory {key} id")
            if not allow_duplicate_ids and record_id in seen_ids:
                raise ContentReferenceCorrelationError(f"duplicate owner inventory {key} id {record_id}")
            seen_ids.add(record_id)
            item["id"] = record_id
        name = _nonempty(item.get("name"), f"owner inventory {key} name")
        item["name"] = name
        if key in {"bestiary", "bosstiary", "spawnBossDefinitions"}:
            item["path" if key != "spawnBossDefinitions" else "source"] = _nonempty(
                item.get("path" if key != "spawnBossDefinitions" else "source"),
                f"owner inventory {key} path",
            )
        normalized.append(item)
    return normalized


def _validate_owner_inventory(payload: Mapping[str, object], *, max_records: int) -> dict[str, list[dict[str, object]]]:
    if payload.get("format") != OWNER_INVENTORY_FORMAT:
        raise ContentReferenceCorrelationError(f"owner inventory format must be {OWNER_INVENTORY_FORMAT}")
    _nonempty(payload.get("repositoryHead"), "owner inventory repositoryHead")
    policy = payload.get("policy")
    if not isinstance(policy, dict) or policy.get("clientInputsIncluded") is not False:
        raise ContentReferenceCorrelationError("owner inventory must exclude client inputs")
    quest = payload.get("quest")
    if not isinstance(quest, dict) or quest.get("automaticClientQuestIdJoinSupported") is not False:
        raise ContentReferenceCorrelationError("owner inventory quest boundary must reject automatic client quest ID joins")
    return {
        "achievement": _validate_owner_section(payload, "achievement", allow_duplicate_ids=False, max_records=max_records),
        "bestiary": _validate_owner_section(payload, "bestiary", allow_duplicate_ids=True, max_records=max_records),
        "bosstiary": _validate_owner_section(payload, "bosstiary", allow_duplicate_ids=True, max_records=max_records),
        "spawnBossDefinitions": _validate_owner_section(
            payload, "spawnBossDefinitions", allow_duplicate_ids=True, max_records=max_records
        ),
    }


def _repo_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def build_owner_inventory(repository_root: Path) -> dict[str, object]:
    """Build a compact intermediate inventory by reusing existing subsystem-owner functions."""

    root = repository_root.expanduser().resolve(strict=True)
    try:
        from achievement_validation import parse_registry_text
        from cyclopedia_validation import collect_monsters
        from otbm_spawn_npc import scan_active_datapack
    except ImportError as exc:
        raise ContentReferenceCorrelationError(
            "existing Achievement, Cyclopedia and Spawn/Boss owner modules must be importable"
        ) from exc

    achievement_path = root / "data/scripts/lib/register_achievements.lua"
    definitions, achievement_findings = parse_registry_text(achievement_path.read_text(encoding="utf-8"))
    achievements = [
        {
            "id": item.id,
            "name": item.name,
            "grade": item.grade,
            "secret": item.secret,
            "points": item.points,
            "line": item.line,
        }
        for item in definitions
    ]
    cyclopedia = collect_monsters(root)
    bestiary = sorted(
        [
            {
                "id": item.get("raceId"),
                "name": item.get("name"),
                "path": item.get("path"),
                "class": item.get("bestiary", {}).get("class"),
                "occurrence": item.get("bestiary", {}).get("Occurrence"),
            }
            for item in cyclopedia["bestiaryEntries"]
        ],
        key=lambda item: (item["id"] is None, item["id"] or 0, item["name"] or "", item["path"]),
    )
    bosstiary = sorted(
        [
            {
                "id": item.get("bosstiary", {}).get("bossRaceId"),
                "name": item.get("name"),
                "path": item.get("path"),
                "rarity": item.get("bosstiary", {}).get("bossRace"),
            }
            for item in cyclopedia["bosstiaryEntries"]
        ],
        key=lambda item: (item["id"] is None, item["id"] or 0, item["name"] or "", item["path"]),
    )
    spawn = scan_active_datapack(
        datapack_root=root / "data-otservbr-global",
        monster_spawn_files=("world/otservbr-monster.xml",),
        npc_spawn_files=("world/otservbr-npc.xml",),
        monster_definition_globs=("monster/**/*.lua",),
        npc_definition_globs=("npc/**/*.lua",),
        dynamic_source_globs=(),
        sample_limit=1,
    )
    spawn_definitions = sorted(
        [
            {
                "kind": entry.get("kind"),
                "name": entry.get("name"),
                "source": entry.get("source"),
                "rewardBoss": entry.get("rewardBoss"),
                "spawnBossLiteral": entry.get("spawnBossLiteral"),
            }
            for entry in spawn.get("definitions", [])
        ],
        key=lambda item: (item["kind"] or "", item["name"] or "", item["source"] or ""),
    )
    return {
        "format": OWNER_INVENTORY_FORMAT,
        "repositoryHead": _repo_head(root),
        "achievement": {
            "ownerFormat": "canary-achievement-audit-v2",
            "sourcePath": achievement_path.relative_to(root).as_posix(),
            "sourceSha256": hashlib.sha256(achievement_path.read_bytes()).hexdigest(),
            "recordCount": len(achievements),
            "parserFindingCount": len(achievement_findings),
            "records": achievements,
        },
        "bestiary": {"owner": "Cyclopedia Validation", "recordCount": len(bestiary), "records": bestiary},
        "bosstiary": {"owner": "Cyclopedia Validation", "recordCount": len(bosstiary), "records": bosstiary},
        "spawnBossDefinitions": {
            "ownerFormat": spawn.get("format"),
            "summary": spawn.get("summary"),
            "recordCount": len(spawn_definitions),
            "records": spawn_definitions,
        },
        "quest": {
            "ownerFormat": "canary-quest-map-evidence-v1",
            "automaticClientQuestIdJoinSupported": False,
            "requiredReviewedInputs": [
                "explicit quest source globs",
                "selected source file SHA-256 values",
                "reviewed client quest ID to source-selection mapping",
            ],
            "reason": (
                "Quest Map Validator exposes selected source AID/UID/item/position/storage evidence "
                "and no shared client quest-ID namespace."
            ),
        },
        "policy": {
            "clientInputsIncluded": False,
            "fullOwnerReportsIncluded": False,
            "nameOnlyMappingsConfirmed": False,
            "numericIdentityMappingsConfirmed": False,
        },
    }


def _group_by_id(records: Sequence[Mapping[str, object]]) -> dict[int, list[tuple[int, Mapping[str, object]]]]:
    result: dict[int, list[tuple[int, Mapping[str, object]]]] = defaultdict(list)
    for ordinal, record in enumerate(records):
        record_id = record.get("id")
        if isinstance(record_id, int) and not isinstance(record_id, bool):
            result[record_id].append((ordinal, record))
    return result


def _group_by_name(records: Sequence[Mapping[str, object]]) -> dict[str, list[tuple[int, Mapping[str, object]]]]:
    result: dict[str, list[tuple[int, Mapping[str, object]]]] = defaultdict(list)
    for ordinal, record in enumerate(records):
        name = record.get("name")
        if isinstance(name, str):
            result[_normalize_name(name)].append((ordinal, record))
    return result


def _source_key(category: str, source_id: int) -> tuple[str, int]:
    return category, source_id


def derive_resolver(
    *,
    staticdata_index_path: Path,
    owner_inventory_path: Path,
    review_id: str,
    review_statement: str,
    max_json_bytes: int = DEFAULT_MAX_JSON_BYTES,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> tuple[dict[str, object], tuple[Path, ...]]:
    review_id = _nonempty(review_id, "review_id")
    review_statement = _nonempty(review_statement, "review_statement")
    staticdata, staticdata_sha, staticdata_resolved = _load_json(
        staticdata_index_path, max_bytes=max_json_bytes, label="StaticData index"
    )
    owner, owner_sha, owner_resolved = _load_json(
        owner_inventory_path, max_bytes=max_json_bytes, label="owner inventory"
    )
    if os.path.samefile(staticdata_resolved, owner_resolved):
        raise ContentReferenceCorrelationError("StaticData index and owner inventory must be distinct files")
    source_categories = _validate_staticdata(staticdata, max_records=max_records)
    owner_sections = _validate_owner_inventory(owner, max_records=max_records)

    identity_mappings: list[dict[str, object]] = []
    presence_mappings: list[dict[str, object]] = []
    unresolved: list[dict[str, object]] = []
    conflicts: list[dict[str, object]] = []

    for category in SOURCE_CATEGORIES:
        records = source_categories.get(category, [])
        target_spec = IDENTITY_TARGETS.get(category)
        if target_spec is None:
            reason = "unsupported-target-namespace" if category == "monsterClasses" else "reviewed-quest-source-selection-required"
            for record in records:
                unresolved.append(
                    {
                        "dimension": "identity",
                        "sourceCategory": category,
                        "sourceId": record["id"],
                        "sourceName": record["name"],
                        "reason": reason,
                    }
                )
        else:
            section, namespace, method = target_spec
            target_records = owner_sections[section]
            by_id = _group_by_id(target_records)
            for record in records:
                candidates = by_id.get(int(record["id"]), [])
                checks: dict[str, bool] = {
                    "uniqueTargetId": len(candidates) == 1,
                    "nameEqual": False,
                }
                if len(candidates) == 1:
                    target_ordinal, target = candidates[0]
                    checks["nameEqual"] = _normalize_name(str(record["name"])) == _normalize_name(str(target["name"]))
                    if category in {"titles", "achievements"}:
                        checks["gradeEqual"] = record.get("grade") == target.get("grade")
                    accepted = all(checks.values())
                    if accepted:
                        identity_mappings.append(
                            {
                                "sourceCategory": category,
                                "sourceId": record["id"],
                                "sourceName": record["name"],
                                "targetSection": section,
                                "targetOrdinal": target_ordinal,
                                "targetNamespace": namespace,
                                "targetId": target["id"],
                                "targetName": target["name"],
                                "method": method,
                                "checks": checks,
                            }
                        )
                    else:
                        unresolved.append(
                            {
                                "dimension": "identity",
                                "sourceCategory": category,
                                "sourceId": record["id"],
                                "sourceName": record["name"],
                                "reason": "target-evidence-mismatch",
                                "candidateTargetOrdinals": [target_ordinal],
                                "checks": checks,
                            }
                        )
                elif len(candidates) > 1:
                    unresolved.append(
                        {
                            "dimension": "identity",
                            "sourceCategory": category,
                            "sourceId": record["id"],
                            "sourceName": record["name"],
                            "reason": "target-id-not-unique",
                            "candidateTargetOrdinals": [ordinal for ordinal, _ in candidates],
                            "checks": checks,
                        }
                    )
                else:
                    unresolved.append(
                        {
                            "dimension": "identity",
                            "sourceCategory": category,
                            "sourceId": record["id"],
                            "sourceName": record["name"],
                            "reason": "target-id-not-found",
                            "candidateTargetOrdinals": [],
                            "checks": checks,
                        }
                    )

        if category in PRESENCE_CATEGORIES:
            by_name: dict[str, list[tuple[int, Mapping[str, object]]]] = defaultdict(list)
            for target_ordinal, entry in enumerate(owner_sections["spawnBossDefinitions"]):
                if entry.get("kind") == "monster":
                    by_name[_normalize_name(str(entry["name"]))].append((target_ordinal, entry))
            for record in records:
                candidates = by_name.get(_normalize_name(str(record["name"])), [])
                if len(candidates) == 1:
                    target_ordinal, target = candidates[0]
                    presence_mappings.append(
                        {
                            "sourceCategory": category,
                            "sourceId": record["id"],
                            "sourceName": record["name"],
                            "targetSection": "spawnBossDefinitions",
                            "targetOrdinal": target_ordinal,
                            "targetNamespace": "canary-monster-definition-path",
                            "targetName": target["name"],
                            "targetPath": target["source"],
                            "method": "reviewed-unique-normalized-name",
                            "checks": {"uniqueNormalizedName": True, "nameEqual": True},
                        }
                    )
                elif len(candidates) > 1:
                    unresolved.append(
                        {
                            "dimension": "definition-presence",
                            "sourceCategory": category,
                            "sourceId": record["id"],
                            "sourceName": record["name"],
                            "reason": "target-name-not-unique",
                            "candidateTargetOrdinals": [ordinal for ordinal, _ in candidates],
                        }
                    )
                else:
                    unresolved.append(
                        {
                            "dimension": "definition-presence",
                            "sourceCategory": category,
                            "sourceId": record["id"],
                            "sourceName": record["name"],
                            "reason": "target-name-not-found",
                            "candidateTargetOrdinals": [],
                        }
                    )

    identity_mappings.sort(key=lambda item: (str(item["sourceCategory"]), int(item["sourceId"])))
    presence_mappings.sort(key=lambda item: (str(item["sourceCategory"]), int(item["sourceId"])))
    unresolved.sort(
        key=lambda item: (
            str(item["sourceCategory"]),
            int(item["sourceId"]),
            str(item["dimension"]),
            str(item["reason"]),
        )
    )
    conflicts.sort(key=lambda item: deterministic_json(item))

    source = staticdata["source"]
    assert isinstance(source, dict)
    summary = {
        "sourceRecordCount": sum(len(source_categories.get(category, [])) for category in SOURCE_CATEGORIES),
        "identityMappingCount": len(identity_mappings),
        "presenceMappingCount": len(presence_mappings),
        "unresolvedCount": len(unresolved),
        "conflictCount": len(conflicts),
        "identityMappingsByCategory": dict(
            sorted(Counter(str(item["sourceCategory"]) for item in identity_mappings).items())
        ),
        "presenceMappingsByCategory": dict(
            sorted(Counter(str(item["sourceCategory"]) for item in presence_mappings).items())
        ),
        "unresolvedByReason": dict(sorted(Counter(str(item["reason"]) for item in unresolved).items())),
    }
    payload: dict[str, object] = {
        "format": RESOLVER_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "provenance": {
            "staticdataIndexSha256": staticdata_sha,
            "staticdataManifestSha256": source["manifestSha256"],
            "staticdataSourceSha256": source["sha256"],
            "referenceId": source["referenceId"],
            "schemaFamily": source["schemaFamily"],
            "ownerInventorySha256": owner_sha,
            "ownerInventoryFormat": OWNER_INVENTORY_FORMAT,
            "targetRepositoryHead": owner["repositoryHead"],
        },
        "review": {"reviewId": review_id, "statement": review_statement},
        "identityMappings": identity_mappings,
        "presenceMappings": presence_mappings,
        "unresolved": unresolved,
        "conflicts": conflicts,
        "summary": summary,
        "policy": {
            "sourceVocabularyPreserved": True,
            "housesExcluded": True,
            "numericIdentityHeuristics": False,
            "nameOnlyMappingsRequireReview": True,
            "sharedTargetIdsFailClosed": True,
            "questNameMapping": False,
            "gameplayConclusions": False,
            "mutation": False,
        },
    }
    return payload, (staticdata_resolved, owner_resolved)


def _validate_resolver(
    payload: Mapping[str, object],
    *,
    staticdata_sha: str,
    owner_sha: str,
    source_categories: Mapping[str, Sequence[Mapping[str, object]]],
    owner_sections: Mapping[str, Sequence[Mapping[str, object]]],
) -> tuple[dict[tuple[str, int], dict[str, object]], dict[tuple[str, int], dict[str, object]], list[dict[str, object]]]:
    if payload.get("format") != RESOLVER_FORMAT or payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ContentReferenceCorrelationError(f"resolver format must be {RESOLVER_FORMAT} schemaVersion {SCHEMA_VERSION}")
    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        raise ContentReferenceCorrelationError("resolver provenance must be an object")
    if provenance.get("staticdataIndexSha256") != staticdata_sha:
        raise ContentReferenceCorrelationError("resolver is stale for the StaticData index")
    if provenance.get("ownerInventorySha256") != owner_sha:
        raise ContentReferenceCorrelationError("resolver is stale for the owner inventory")
    review = payload.get("review")
    if not isinstance(review, dict):
        raise ContentReferenceCorrelationError("resolver review must be an object")
    _nonempty(review.get("reviewId"), "resolver reviewId")
    _nonempty(review.get("statement"), "resolver statement")

    source_by_key = {
        _source_key(category, int(record["id"])): record
        for category, records in source_categories.items()
        for record in records
        if category in SOURCE_CATEGORIES
    }
    identity_groups = {
        section: _group_by_id(owner_sections[section]) for section in ("achievement", "bestiary", "bosstiary")
    }
    presence_groups: dict[str, list[tuple[int, Mapping[str, object]]]] = defaultdict(list)
    for target_ordinal, target in enumerate(owner_sections["spawnBossDefinitions"]):
        if target.get("kind") == "monster":
            presence_groups[_normalize_name(str(target["name"]))].append((target_ordinal, target))

    def validate_mapping_list(key: str) -> dict[tuple[str, int], dict[str, object]]:
        rows = payload.get(key)
        if not isinstance(rows, list):
            raise ContentReferenceCorrelationError(f"resolver {key} must be an array")
        result: dict[tuple[str, int], dict[str, object]] = {}
        used_targets: set[tuple[str, int]] = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ContentReferenceCorrelationError(f"resolver {key} row {index} must be an object")
            category = _nonempty(row.get("sourceCategory"), f"resolver {key} sourceCategory")
            source_id = _uint(row.get("sourceId"), f"resolver {key} sourceId")
            source = source_by_key.get(_source_key(category, source_id))
            if source is None:
                raise ContentReferenceCorrelationError(f"resolver {key} references unknown source {category}:{source_id}")
            if row.get("sourceName") != source.get("name"):
                raise ContentReferenceCorrelationError(f"resolver {key} source name mismatch for {category}:{source_id}")
            source_key = _source_key(category, source_id)
            if source_key in result:
                raise ContentReferenceCorrelationError(f"duplicate resolver {key} source {category}:{source_id}")
            section = _nonempty(row.get("targetSection"), f"resolver {key} targetSection")
            ordinal = _uint(row.get("targetOrdinal"), f"resolver {key} targetOrdinal")
            target_records = owner_sections.get(section)
            if target_records is None or ordinal >= len(target_records):
                raise ContentReferenceCorrelationError(f"resolver {key} target pointer is invalid")
            target = target_records[ordinal]
            target_key = (section, ordinal)
            if key == "identityMappings" and target_key in used_targets:
                raise ContentReferenceCorrelationError(f"duplicate resolver identity target {section}:{ordinal}")
            used_targets.add(target_key)
            if row.get("targetName") != target.get("name"):
                raise ContentReferenceCorrelationError(f"resolver {key} target name mismatch for {section}:{ordinal}")
            checks = row.get("checks")
            if not isinstance(checks, dict) or not checks or any(value is not True for value in checks.values()):
                raise ContentReferenceCorrelationError(f"resolver {key} checks must all be true")

            if key == "identityMappings":
                expected = IDENTITY_TARGETS.get(category)
                if expected is None:
                    raise ContentReferenceCorrelationError(f"resolver identity mapping is unsupported for {category}")
                expected_section, expected_namespace, expected_method = expected
                if (section, row.get("targetNamespace"), row.get("method")) != (
                    expected_section,
                    expected_namespace,
                    expected_method,
                ):
                    raise ContentReferenceCorrelationError(f"resolver identity contract mismatch for {category}:{source_id}")
                if row.get("targetId") != target.get("id"):
                    raise ContentReferenceCorrelationError(f"resolver identity target id mismatch for {section}:{ordinal}")
                same_id = identity_groups[section].get(source_id, [])
                if len(same_id) != 1 or same_id[0][0] != ordinal:
                    raise ContentReferenceCorrelationError(f"resolver identity target id is not unique for {category}:{source_id}")
                if _normalize_name(str(source["name"])) != _normalize_name(str(target["name"])):
                    raise ContentReferenceCorrelationError(f"resolver identity name evidence mismatch for {category}:{source_id}")
                if category in {"titles", "achievements"} and source.get("grade") != target.get("grade"):
                    raise ContentReferenceCorrelationError(f"resolver identity grade evidence mismatch for {category}:{source_id}")
            else:
                if category not in PRESENCE_CATEGORIES:
                    raise ContentReferenceCorrelationError(f"resolver presence mapping is unsupported for {category}")
                if (
                    section != "spawnBossDefinitions"
                    or row.get("targetNamespace") != "canary-monster-definition-path"
                    or row.get("method") != "reviewed-unique-normalized-name"
                ):
                    raise ContentReferenceCorrelationError(f"resolver presence contract mismatch for {category}:{source_id}")
                if row.get("targetPath") != target.get("source"):
                    raise ContentReferenceCorrelationError(f"resolver presence target path mismatch for {section}:{ordinal}")
                same_name = presence_groups.get(_normalize_name(str(source["name"])), [])
                if len(same_name) != 1 or same_name[0][0] != ordinal:
                    raise ContentReferenceCorrelationError(f"resolver presence target name is not unique for {category}:{source_id}")
            result[source_key] = dict(row)
        return result

    identity = validate_mapping_list("identityMappings")
    presence = validate_mapping_list("presenceMappings")
    unresolved_rows = payload.get("unresolved")
    if not isinstance(unresolved_rows, list) or any(not isinstance(item, dict) for item in unresolved_rows):
        raise ContentReferenceCorrelationError("resolver unresolved must be an array of objects")
    unresolved: list[dict[str, object]] = []
    unresolved_dimensions: set[tuple[str, int, str]] = set()
    for index, raw in enumerate(unresolved_rows):
        item = dict(raw)
        category = _nonempty(item.get("sourceCategory"), f"resolver unresolved row {index} sourceCategory")
        source_id = _uint(item.get("sourceId"), f"resolver unresolved row {index} sourceId")
        dimension = _nonempty(item.get("dimension"), f"resolver unresolved row {index} dimension")
        if dimension not in {"identity", "definition-presence"}:
            raise ContentReferenceCorrelationError(f"resolver unresolved row {index} has invalid dimension")
        source = source_by_key.get(_source_key(category, source_id))
        if source is None:
            raise ContentReferenceCorrelationError(f"resolver unresolved references unknown source {category}:{source_id}")
        if item.get("sourceName") != source.get("name"):
            raise ContentReferenceCorrelationError(f"resolver unresolved source name mismatch for {category}:{source_id}")
        dimension_key = (category, source_id, dimension)
        if dimension_key in unresolved_dimensions:
            raise ContentReferenceCorrelationError(f"duplicate resolver unresolved dimension {category}:{source_id}:{dimension}")
        unresolved_dimensions.add(dimension_key)
        unresolved.append(item)

    for source_key in sorted(source_by_key):
        category, source_id = source_key
        has_identity = source_key in identity
        has_identity_unresolved = (category, source_id, "identity") in unresolved_dimensions
        if has_identity == has_identity_unresolved:
            raise ContentReferenceCorrelationError(f"resolver identity coverage must be exactly one for {category}:{source_id}")
        if category in PRESENCE_CATEGORIES:
            has_presence = source_key in presence
            has_presence_unresolved = (category, source_id, "definition-presence") in unresolved_dimensions
            if has_presence == has_presence_unresolved:
                raise ContentReferenceCorrelationError(f"resolver presence coverage must be exactly one for {category}:{source_id}")
        elif (category, source_id, "definition-presence") in unresolved_dimensions:
            raise ContentReferenceCorrelationError(f"resolver presence evidence is unsupported for {category}:{source_id}")

    conflicts = payload.get("conflicts")
    if not isinstance(conflicts, list):
        raise ContentReferenceCorrelationError("resolver conflicts must be an array")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise ContentReferenceCorrelationError("resolver summary must be an object")
    expected_summary = {
        "sourceRecordCount": len(source_by_key),
        "identityMappingCount": len(identity),
        "presenceMappingCount": len(presence),
        "unresolvedCount": len(unresolved),
        "conflictCount": len(conflicts),
        "identityMappingsByCategory": dict(sorted(Counter(key[0] for key in identity).items())),
        "presenceMappingsByCategory": dict(sorted(Counter(key[0] for key in presence).items())),
        "unresolvedByReason": dict(sorted(Counter(str(item.get("reason")) for item in unresolved).items())),
    }
    if summary != expected_summary:
        raise ContentReferenceCorrelationError("resolver summary does not match resolver rows")
    return identity, presence, unresolved


def build_correlation(
    *,
    staticdata_index_path: Path,
    owner_inventory_path: Path,
    resolver_path: Path,
    max_json_bytes: int = DEFAULT_MAX_JSON_BYTES,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> tuple[dict[str, object], tuple[Path, ...]]:
    staticdata, staticdata_sha, staticdata_resolved = _load_json(
        staticdata_index_path, max_bytes=max_json_bytes, label="StaticData index"
    )
    owner, owner_sha, owner_resolved = _load_json(
        owner_inventory_path, max_bytes=max_json_bytes, label="owner inventory"
    )
    resolver, resolver_sha, resolver_resolved = _load_json(
        resolver_path, max_bytes=max_json_bytes, label="content resolver"
    )
    resolved_paths = {staticdata_resolved, owner_resolved, resolver_resolved}
    if len(resolved_paths) != 3:
        raise ContentReferenceCorrelationError("StaticData index, owner inventory and resolver must be distinct files")
    source_categories = _validate_staticdata(staticdata, max_records=max_records)
    owner_sections = _validate_owner_inventory(owner, max_records=max_records)
    identity, presence, unresolved = _validate_resolver(
        resolver,
        staticdata_sha=staticdata_sha,
        owner_sha=owner_sha,
        source_categories=source_categories,
        owner_sections=owner_sections,
    )
    unresolved_by_key: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for item in unresolved:
        category = item.get("sourceCategory")
        source_id = item.get("sourceId")
        if isinstance(category, str) and isinstance(source_id, int) and not isinstance(source_id, bool):
            unresolved_by_key[_source_key(category, source_id)].append(item)

    rows: list[dict[str, object]] = []
    state_counts: Counter[str] = Counter()
    category_counts: dict[str, Counter[str]] = defaultdict(Counter)
    used_identity_targets: set[tuple[str, int]] = set()
    for category in SOURCE_CATEGORIES:
        for record in source_categories.get(category, []):
            key = _source_key(category, int(record["id"]))
            identity_row = identity.get(key)
            presence_row = presence.get(key)
            reasons = unresolved_by_key.get(key, [])
            if category in {"titles", "achievements"}:
                state = "confirmed-reference" if identity_row else (
                    "unresolved-id-space" if any(item.get("reason") != "target-id-not-found" for item in reasons) else "reference-only"
                )
            elif category in {"creatures", "monsters", "bosses"}:
                if identity_row and presence_row:
                    state = "confirmed-reference"
                elif identity_row or presence_row:
                    state = "partial"
                else:
                    state = "unresolved-id-space" if any(
                        item.get("reason") not in {"target-id-not-found", "target-name-not-found"} for item in reasons
                    ) else "reference-only"
            else:
                state = "unresolved-id-space"
            if state not in ALLOWED_STATES:
                raise AssertionError(state)
            if identity_row:
                used_identity_targets.add((str(identity_row["targetSection"]), int(identity_row["targetOrdinal"])))
            row = {
                "sourceCategory": category,
                "sourceId": record["id"],
                "sourceName": record["name"],
                "state": state,
                "identityResolution": identity_row,
                "definitionPresence": presence_row,
                "unresolvedEvidence": reasons,
            }
            rows.append(row)
            state_counts[state] += 1
            category_counts[category][state] += 1

    target_only: list[dict[str, object]] = []
    for section in ("achievement", "bestiary", "bosstiary"):
        for ordinal, record in enumerate(owner_sections[section]):
            if (section, ordinal) not in used_identity_targets:
                target_only.append(
                    {
                        "state": "target-only",
                        "targetSection": section,
                        "targetOrdinal": ordinal,
                        "targetId": record["id"],
                        "targetName": record["name"],
                        **({"targetPath": record.get("path")} if record.get("path") is not None else {}),
                    }
                )
    target_only.sort(
        key=lambda item: (str(item["targetSection"]), int(item["targetId"]), str(item["targetName"]), int(item["targetOrdinal"]))
    )
    rows.sort(key=lambda item: (str(item["sourceCategory"]), int(item["sourceId"]), str(item["sourceName"])))

    source = staticdata["source"]
    assert isinstance(source, dict)
    payload: dict[str, object] = {
        "format": CORRELATION_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "provenance": {
            "staticdataIndexSha256": staticdata_sha,
            "staticdataManifestSha256": source["manifestSha256"],
            "staticdataSourceSha256": source["sha256"],
            "referenceId": source["referenceId"],
            "schemaFamily": source["schemaFamily"],
            "ownerInventorySha256": owner_sha,
            "targetRepositoryHead": owner["repositoryHead"],
            "resolverSha256": resolver_sha,
        },
        "records": rows,
        "targetOnly": target_only,
        "findings": {
            "unresolved": unresolved,
            "targetOnly": target_only,
            "conflicts": resolver.get("conflicts", []),
        },
        "summary": {
            "sourceRecordCount": len(rows),
            "targetOnlyCount": len(target_only),
            "stateCounts": dict(sorted(state_counts.items())),
            "categoryStateCounts": {
                category: dict(sorted(counts.items())) for category, counts in sorted(category_counts.items())
            },
            "identityMappingCount": len(identity),
            "presenceMappingCount": len(presence),
            "unresolvedEvidenceCount": len(unresolved),
            "conflictCount": len(resolver.get("conflicts", [])) if isinstance(resolver.get("conflicts"), list) else 0,
        },
        "policy": {
            "sourceVocabularyPreserved": True,
            "housesExcluded": True,
            "existingSubsystemOwnersReused": True,
            "questNameMapping": False,
            "runtimeProof": False,
            "gameplayConclusions": False,
            "mutation": False,
        },
    }
    return payload, (staticdata_resolved, owner_resolved, resolver_resolved)


def deterministic_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def write_output(
    path: Path,
    payload: Mapping[str, object],
    *,
    protected_inputs: Iterable[Path],
    overwrite: bool = False,
) -> None:
    expanded_output = path.expanduser()
    if expanded_output.is_symlink():
        raise ContentReferenceCorrelationError("output must not be a symlink")
    output = expanded_output.resolve(strict=False)
    protected = {item.expanduser().resolve(strict=True) for item in protected_inputs}
    if output in protected:
        raise ContentReferenceCorrelationError("output collides with an input")
    if output.exists() and not overwrite:
        raise ContentReferenceCorrelationError("output already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    data = deterministic_json(payload)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{output.name}.", dir=output.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, output)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
