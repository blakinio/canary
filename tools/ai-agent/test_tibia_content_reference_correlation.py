from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from tibia_content_reference_correlation import (
    CORRELATION_FORMAT,
    OWNER_INVENTORY_FORMAT,
    RESOLVER_FORMAT,
    ContentReferenceCorrelationError,
    build_correlation,
    derive_resolver,
    deterministic_json,
    write_output,
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ContentReferenceCorrelationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.staticdata = self.root / "staticdata.json"
        self.owner = self.root / "owner.json"
        self._write_staticdata()
        self._write_owner()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_json(self, path: Path, payload: object) -> None:
        path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True), encoding="utf-8")

    def _write_staticdata(self, *, newer: bool = False, duplicate: bool = False) -> None:
        categories: dict[str, object]
        if newer:
            categories = {
                "monsters": {
                    "sourceCategory": "monsters",
                    "sourceSchema": "newer",
                    "count": 1,
                    "records": [{"id": 1, "name": "Rat", "sourceOrdinal": 1}],
                },
                "monsterClasses": {
                    "sourceCategory": "monsterClasses",
                    "sourceSchema": "newer",
                    "count": 1,
                    "records": [{"id": 7, "name": "Vermin", "sourceOrdinal": 1}],
                },
                "achievements": {
                    "sourceCategory": "achievements",
                    "sourceSchema": "newer",
                    "count": 1,
                    "records": [{"id": 10, "name": "Hero", "grade": 1, "sourceOrdinal": 1}],
                },
                "bosses": {
                    "sourceCategory": "bosses",
                    "sourceSchema": "newer",
                    "count": 1,
                    "records": [{"id": 20, "name": "Boss", "sourceOrdinal": 1}],
                },
                "quests": {
                    "sourceCategory": "quests",
                    "sourceSchema": "newer",
                    "count": 1,
                    "records": [{"id": 30, "name": "Quest", "sourceOrdinal": 1}],
                },
                "houses": {
                    "sourceCategory": "houses",
                    "sourceSchema": "newer",
                    "houseFieldOrder": "newer",
                    "count": 1,
                    "records": [{"id": 99, "name": "House", "sourceOrdinal": 1}],
                },
            }
            family = "newer"
        else:
            creature_records = [
                {"id": 1, "name": "Rat", "sourceOrdinal": 1},
                {"id": 2, "name": "Butterfly", "sourceOrdinal": 2},
                {"id": 3, "name": "Missing Creature", "sourceOrdinal": 3},
            ]
            if duplicate:
                creature_records.append({"id": 1, "name": "Duplicate Rat", "sourceOrdinal": 4})
            categories = {
                "creatures": {
                    "sourceCategory": "creatures",
                    "sourceSchema": "legacy",
                    "count": len(creature_records),
                    "records": creature_records,
                },
                "titles": {
                    "sourceCategory": "titles",
                    "sourceSchema": "legacy",
                    "count": 2,
                    "records": [
                        {"id": 10, "name": "Hero", "grade": 1, "sourceOrdinal": 1},
                        {"id": 11, "name": "Wrong Title", "grade": 2, "sourceOrdinal": 2},
                    ],
                },
                "bosses": {
                    "sourceCategory": "bosses",
                    "sourceSchema": "legacy",
                    "count": 1,
                    "records": [{"id": 20, "name": "Boss", "sourceOrdinal": 1}],
                },
                "quests": {
                    "sourceCategory": "quests",
                    "sourceSchema": "legacy",
                    "count": 1,
                    "records": [{"id": 30, "name": "Quest", "sourceOrdinal": 1}],
                },
                "houses": {
                    "sourceCategory": "houses",
                    "sourceSchema": "legacy",
                    "houseFieldOrder": "newer",
                    "count": 1,
                    "records": [{"id": 99, "name": "House", "sourceOrdinal": 1}],
                },
            }
            family = "legacy"
        payload = {
            "format": "canary-tibia-staticdata-index-v1",
            "schemaVersion": 2,
            "source": {
                "manifestFormat": "canary-tibia-client-reference-manifest-v1",
                "manifestSha256": "1" * 64,
                "referenceId": "fixture-reference",
                "inputId": "staticdata",
                "manifestPath": "assets/staticdata.dat",
                "sizeBytes": 1,
                "sha256": "2" * 64,
                "encoding": "raw",
                "decodedSizeBytes": 1,
                "schemaFamily": family,
                "schemaEvidence": ["fixture"],
                "houseFieldOrder": "newer",
                "houseFieldOrderEvidence": {"state": "reviewed", "reviewId": "fixture", "statement": "fixture"},
            },
            "categories": categories,
            "findings": {
                "duplicateIds": [],
                "missingRequiredFields": [],
                "duplicateSingularFields": [],
                "unresolvedHouseFieldOrder": [],
            },
            "summary": {
                "categoryCounts": {key: value["count"] for key, value in categories.items()},
                "totalRecords": sum(value["count"] for value in categories.values()),
                "duplicateIdCount": 0,
                "missingRequiredFieldCount": 0,
                "duplicateSingularFieldCount": 0,
                "unresolvedHouseFieldOrderCount": 0,
            },
            "policy": {
                "gameplayConclusions": False,
                "questInventoryOnly": True,
                "schemaAmbiguityFailsClosed": True,
                "maxSourceBytes": 1,
                "maxDecompressedBytes": 1,
                "maxRecords": 100,
                "houseFieldOrderResolution": "newer",
                "houseFieldOrderHeuristics": False,
            },
        }
        self._write_json(self.staticdata, payload)

    def _write_owner(self, *, duplicate_achievement: bool = False, count_offset: int = 0) -> None:
        achievements = [
            {"id": 10, "name": "Hero", "grade": 1, "secret": False, "points": 1, "line": 10},
            {"id": 11, "name": "Different Title", "grade": 2, "secret": False, "points": 2, "line": 11},
            {"id": 12, "name": "Target Only", "grade": 1, "secret": False, "points": 1, "line": 12},
        ]
        if duplicate_achievement:
            achievements.append({"id": 10, "name": "Duplicate", "grade": 1, "secret": False, "points": 1, "line": 13})
        payload = {
            "format": OWNER_INVENTORY_FORMAT,
            "repositoryHead": "a" * 40,
            "achievement": {
                "ownerFormat": "canary-achievement-audit-v2",
                "sourcePath": "data/scripts/lib/register_achievements.lua",
                "sourceSha256": "3" * 64,
                "recordCount": len(achievements) + count_offset,
                "parserFindingCount": 0,
                "records": achievements,
            },
            "bestiary": {
                "owner": "Cyclopedia Validation",
                "recordCount": 3,
                "records": [
                    {"id": 1, "name": "Rat", "path": "monster/rat.lua", "class": "Vermin", "occurrence": "COMMON"},
                    {"id": 2, "name": "Blue Butterfly", "path": "monster/blue.lua", "class": "Vermin", "occurrence": "COMMON"},
                    {"id": 2, "name": "Red Butterfly", "path": "monster/red.lua", "class": "Vermin", "occurrence": "COMMON"},
                ],
            },
            "bosstiary": {
                "owner": "Cyclopedia Validation",
                "recordCount": 2,
                "records": [
                    {"id": 20, "name": "Boss", "path": "monster/boss.lua", "rarity": "RARITY_BANE"},
                    {"id": 21, "name": "Target Boss", "path": "monster/target_boss.lua", "rarity": "RARITY_BANE"},
                ],
            },
            "spawnBossDefinitions": {
                "ownerFormat": "canary-otbm-spawn-npc-evidence-v1",
                "summary": {},
                "recordCount": 4,
                "records": [
                    {"kind": "monster", "name": "Boss", "source": "monster/boss.lua", "rewardBoss": False, "spawnBossLiteral": True},
                    {"kind": "monster", "name": "Butterfly", "source": "monster/butterfly.lua", "rewardBoss": False, "spawnBossLiteral": False},
                    {"kind": "monster", "name": "Rat", "source": "monster/rat.lua", "rewardBoss": False, "spawnBossLiteral": False},
                    {"kind": "npc", "name": "Guide", "source": "npc/guide.lua", "rewardBoss": False, "spawnBossLiteral": False},
                ],
            },
            "quest": {
                "ownerFormat": "canary-quest-map-evidence-v1",
                "automaticClientQuestIdJoinSupported": False,
                "requiredReviewedInputs": ["explicit quest source globs"],
                "reason": "no shared ID",
            },
            "policy": {
                "clientInputsIncluded": False,
                "fullOwnerReportsIncluded": False,
                "nameOnlyMappingsConfirmed": False,
                "numericIdentityMappingsConfirmed": False,
            },
        }
        self._write_json(self.owner, payload)

    def _derive(self) -> tuple[dict[str, object], Path]:
        payload, _ = derive_resolver(
            staticdata_index_path=self.staticdata,
            owner_inventory_path=self.owner,
            review_id="fixture-review",
            review_statement="Fixture review approves only the explicit safe methods.",
        )
        path = self.root / "resolver.json"
        path.write_text(deterministic_json(payload), encoding="utf-8")
        return payload, path

    def test_derives_safe_mappings_and_preserves_legacy_vocabulary(self) -> None:
        resolver, resolver_path = self._derive()
        self.assertEqual(resolver["format"], RESOLVER_FORMAT)
        self.assertEqual(resolver["summary"]["identityMappingCount"], 3)
        self.assertEqual(resolver["summary"]["presenceMappingCount"], 3)
        self.assertEqual(resolver["summary"]["identityMappingsByCategory"], {"bosses": 1, "creatures": 1, "titles": 1})
        correlation, _ = build_correlation(
            staticdata_index_path=self.staticdata,
            owner_inventory_path=self.owner,
            resolver_path=resolver_path,
        )
        self.assertEqual(correlation["format"], CORRELATION_FORMAT)
        self.assertEqual(correlation["summary"]["sourceRecordCount"], 7)
        by_key = {(row["sourceCategory"], row["sourceId"]): row for row in correlation["records"]}
        self.assertEqual(by_key[("creatures", 1)]["state"], "confirmed-reference")
        self.assertEqual(by_key[("creatures", 2)]["state"], "partial")
        self.assertEqual(by_key[("creatures", 3)]["state"], "reference-only")
        self.assertEqual(by_key[("titles", 10)]["state"], "confirmed-reference")
        self.assertEqual(by_key[("titles", 11)]["state"], "unresolved-id-space")
        self.assertEqual(by_key[("quests", 30)]["state"], "unresolved-id-space")
        self.assertNotIn(("houses", 99), by_key)

    def test_shared_target_id_fails_closed(self) -> None:
        resolver, _ = self._derive()
        mappings = {(row["sourceCategory"], row["sourceId"]) for row in resolver["identityMappings"]}
        self.assertNotIn(("creatures", 2), mappings)
        finding = next(item for item in resolver["unresolved"] if item["sourceCategory"] == "creatures" and item["sourceId"] == 2 and item["dimension"] == "identity")
        self.assertEqual(finding["reason"], "target-id-not-unique")

    def test_title_grade_mismatch_is_not_mapped(self) -> None:
        resolver, _ = self._derive()
        title = next(item for item in resolver["unresolved"] if item["sourceCategory"] == "titles" and item["sourceId"] == 11)
        self.assertEqual(title["reason"], "target-evidence-mismatch")
        self.assertFalse(title["checks"]["nameEqual"])

    def test_quest_mapping_remains_unresolved(self) -> None:
        resolver, _ = self._derive()
        quest = next(item for item in resolver["unresolved"] if item["sourceCategory"] == "quests")
        self.assertEqual(quest["reason"], "reviewed-quest-source-selection-required")
        self.assertFalse(resolver["policy"]["questNameMapping"])

    def test_newer_vocabulary_is_preserved(self) -> None:
        self._write_staticdata(newer=True)
        resolver, resolver_path = self._derive()
        self.assertEqual(resolver["summary"]["identityMappingsByCategory"], {"achievements": 1, "bosses": 1, "monsters": 1})
        correlation, _ = build_correlation(
            staticdata_index_path=self.staticdata,
            owner_inventory_path=self.owner,
            resolver_path=resolver_path,
        )
        categories = {row["sourceCategory"] for row in correlation["records"]}
        self.assertIn("monsters", categories)
        self.assertIn("monsterClasses", categories)
        self.assertIn("achievements", categories)
        self.assertNotIn("creatures", categories)
        self.assertNotIn("titles", categories)

    def test_stale_staticdata_provenance_is_rejected(self) -> None:
        _, resolver_path = self._derive()
        payload = json.loads(self.staticdata.read_text(encoding="utf-8"))
        payload["source"]["referenceId"] = "changed"
        self._write_json(self.staticdata, payload)
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "stale for the StaticData index"):
            build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=resolver_path)

    def test_stale_owner_provenance_is_rejected(self) -> None:
        _, resolver_path = self._derive()
        payload = json.loads(self.owner.read_text(encoding="utf-8"))
        payload["repositoryHead"] = "b" * 40
        self._write_json(self.owner, payload)
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "stale for the owner inventory"):
            build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=resolver_path)

    def test_duplicate_source_ids_fail_closed(self) -> None:
        self._write_staticdata(duplicate=True)
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "duplicate StaticData creatures id 1"):
            self._derive()

    def test_duplicate_achievement_ids_fail_closed(self) -> None:
        self._write_owner(duplicate_achievement=True)
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "duplicate owner inventory achievement id 10"):
            self._derive()

    def test_owner_count_mismatch_fails_closed(self) -> None:
        self._write_owner(count_offset=1)
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "owner inventory achievement count mismatch"):
            self._derive()

    def test_tampered_target_pointer_fails_closed(self) -> None:
        resolver, resolver_path = self._derive()
        resolver["identityMappings"][0]["targetOrdinal"] = 999
        resolver_path.write_text(deterministic_json(resolver), encoding="utf-8")
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "target pointer is invalid"):
            build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=resolver_path)

    def test_tampered_unknown_source_fails_closed(self) -> None:
        resolver, resolver_path = self._derive()
        resolver["identityMappings"][0]["sourceId"] = 999
        resolver_path.write_text(deterministic_json(resolver), encoding="utf-8")
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "unknown source"):
            build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=resolver_path)

    def test_tampered_namespace_contract_fails_closed(self) -> None:
        resolver, resolver_path = self._derive()
        resolver["identityMappings"][0]["targetNamespace"] = "wrong-namespace"
        resolver_path.write_text(deterministic_json(resolver), encoding="utf-8")
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "identity contract mismatch"):
            build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=resolver_path)

    def test_missing_unresolved_coverage_fails_closed(self) -> None:
        resolver, resolver_path = self._derive()
        resolver["unresolved"] = [
            item for item in resolver["unresolved"]
            if not (item["sourceCategory"] == "quests" and item["sourceId"] == 30)
        ]
        resolver["summary"]["unresolvedCount"] -= 1
        resolver["summary"]["unresolvedByReason"]["reviewed-quest-source-selection-required"] -= 1
        resolver_path.write_text(deterministic_json(resolver), encoding="utf-8")
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "identity coverage must be exactly one"):
            build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=resolver_path)

    def test_duplicate_json_keys_fail_closed(self) -> None:
        self.staticdata.write_text('{"format":"a","format":"b"}', encoding="utf-8")
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "duplicate JSON object key"):
            self._derive()

    def test_deterministic_outputs(self) -> None:
        first, first_path = self._derive()
        second, _ = derive_resolver(
            staticdata_index_path=self.staticdata,
            owner_inventory_path=self.owner,
            review_id="fixture-review",
            review_statement="Fixture review approves only the explicit safe methods.",
        )
        self.assertEqual(deterministic_json(first), deterministic_json(second))
        first_correlation, _ = build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=first_path)
        second_correlation, _ = build_correlation(staticdata_index_path=self.staticdata, owner_inventory_path=self.owner, resolver_path=first_path)
        self.assertEqual(deterministic_json(first_correlation), deterministic_json(second_correlation))

    def test_output_no_clobber_and_input_protection(self) -> None:
        payload, protected = derive_resolver(
            staticdata_index_path=self.staticdata,
            owner_inventory_path=self.owner,
            review_id="fixture-review",
            review_statement="Fixture review approves only the explicit safe methods.",
        )
        output = self.root / "output.json"
        write_output(output, payload, protected_inputs=protected)
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "already exists"):
            write_output(output, payload, protected_inputs=protected)
        write_output(output, payload, protected_inputs=protected, overwrite=True)
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "collides with an input"):
            write_output(self.staticdata, payload, protected_inputs=protected, overwrite=True)

    def test_output_symlink_is_rejected(self) -> None:
        payload, protected = derive_resolver(
            staticdata_index_path=self.staticdata,
            owner_inventory_path=self.owner,
            review_id="fixture-review",
            review_statement="Fixture review approves only the explicit safe methods.",
        )
        target = self.root / "target.json"
        target.write_text("{}", encoding="utf-8")
        link = self.root / "link.json"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "must not be a symlink"):
            write_output(link, payload, protected_inputs=protected, overwrite=True)

    def test_record_bound_is_enforced(self) -> None:
        with self.assertRaisesRegex(ContentReferenceCorrelationError, "record count exceeds 1"):
            derive_resolver(
                staticdata_index_path=self.staticdata,
                owner_inventory_path=self.owner,
                review_id="fixture-review",
                review_statement="Fixture review approves only the explicit safe methods.",
                max_records=1,
            )

    def test_opt_in_exact_inputs(self) -> None:
        exact_dir = os.environ.get("CANARY_TCR006_EXACT_DIR")
        if not exact_dir:
            self.skipTest("set CANARY_TCR006_EXACT_DIR for exact-input validation")
        root = Path(exact_dir)
        resolver, _ = derive_resolver(
            staticdata_index_path=root / "staticdata-index.json",
            owner_inventory_path=root / "owner-inventory.json",
            review_id="tcr006-exact-20260724",
            review_statement="Exact reviewed comparison; safe unique mappings only.",
        )
        self.assertEqual(resolver["summary"]["identityMappingCount"], 1324)
        self.assertEqual(resolver["summary"]["presenceMappingCount"], 1094)
        resolver_path = root / "test-resolver.json"
        resolver_path.write_text(deterministic_json(resolver), encoding="utf-8")
        try:
            correlation, _ = build_correlation(
                staticdata_index_path=root / "staticdata-index.json",
                owner_inventory_path=root / "owner-inventory.json",
                resolver_path=resolver_path,
            )
            self.assertEqual(correlation["summary"]["stateCounts"]["confirmed-reference"], 1324)
            self.assertEqual(correlation["summary"]["stateCounts"]["partial"], 119)
            self.assertEqual(correlation["summary"]["stateCounts"]["reference-only"], 160)
            self.assertEqual(correlation["summary"]["stateCounts"]["unresolved-id-space"], 102)
        finally:
            resolver_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
