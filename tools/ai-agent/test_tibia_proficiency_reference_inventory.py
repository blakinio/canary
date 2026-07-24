from __future__ import annotations

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

from tibia_proficiency_reference_correlation import (
    APPEARANCES_INDEX_FORMAT, CANARY_EVIDENCE_FORMAT, CORRELATION_FORMAT, RESOLVER_FORMAT,
    ProficiencyReferenceCorrelationError, _semantic_sha, build_canary_evidence, build_correlation,
    derive_resolver, deterministic_json, write_json,
)
from tibia_proficiency_reference_test_support import (
    SHA_A, SHA_B, SHA_C, SHA_D, appearances, canary_evidence,
    proficiency_index, resolved_fixture, source_entry,
)

class ProficiencyReferenceCorrelationTests(unittest.TestCase):

    def test_duplicate_resolver_source_ordinal_fails_closed(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture()
            resolver["mappings"].append(dict(resolver["mappings"][0]))
            with self.assertRaisesRegex(ProficiencyReferenceCorrelationError, "duplicate resolver sourceOrdinal"):
                build_correlation(
                    proficiency_index=source,
                    proficiency_index_sha256=SHA_A,
                    appearances_index=appearance,
                    appearances_index_sha256=SHA_B,
                    canary_evidence=evidence,
                    canary_evidence_sha256=SHA_C,
                    resolver=resolver,
                    resolver_sha256=SHA_D,
                )

    def test_invalid_appearance_format_fails_closed(self) -> None:
            bad = appearances()
            bad["format"] = "wrong"
            with self.assertRaisesRegex(ProficiencyReferenceCorrelationError, "appearances format"):
                derive_resolver(
                    proficiency_index=proficiency_index(),
                    proficiency_index_sha256=SHA_A,
                    appearances_index=bad,
                    appearances_index_sha256=SHA_B,
                    canary_evidence=canary_evidence(),
                    canary_evidence_sha256=SHA_C,
                    review_id="review-1",
                    review_statement="Reviewed.",
                )

    def test_unproven_loader_contract_fails_closed(self) -> None:
            evidence = canary_evidence()
            evidence["itemBindingContract"]["objectIdAssignsItemId"] = False
            with self.assertRaisesRegex(ProficiencyReferenceCorrelationError, "unresolved"):
                derive_resolver(
                    proficiency_index=proficiency_index(),
                    proficiency_index_sha256=SHA_A,
                    appearances_index=appearances(),
                    appearances_index_sha256=SHA_B,
                    canary_evidence=evidence,
                    canary_evidence_sha256=SHA_C,
                    review_id="review-1",
                    review_statement="Reviewed.",
                )

    def test_deterministic_json_is_stable(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture()
            report = build_correlation(
                proficiency_index=source,
                proficiency_index_sha256=SHA_A,
                appearances_index=appearance,
                appearances_index_sha256=SHA_B,
                canary_evidence=evidence,
                canary_evidence_sha256=SHA_C,
                resolver=resolver,
                resolver_sha256=SHA_D,
            )
            self.assertEqual(deterministic_json(report), deterministic_json(report))
            self.assertTrue(deterministic_json(report).endswith("\n"))

    def test_write_json_is_create_new_by_default(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                output = Path(directory) / "report.json"
                write_json(output, {"format": "fixture"})
                with self.assertRaisesRegex(ProficiencyReferenceCorrelationError, "already exists"):
                    write_json(output, {"format": "fixture"})
                write_json(output, {"format": "replacement"}, overwrite=True)
                self.assertEqual(json.loads(output.read_text())["format"], "replacement")

    def test_write_json_rejects_protected_input(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "input.json"
                source.write_text("{}\n", encoding="utf-8")
                with self.assertRaisesRegex(ProficiencyReferenceCorrelationError, "collides"):
                    write_json(source, {"format": "fixture"}, protected_inputs=[source], overwrite=True)

    def test_inventory_reuses_tcr004_parser_and_proves_source_markers(self) -> None:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "data/items").mkdir(parents=True)
                (root / "src/items").mkdir(parents=True)
                (root / "src/creatures/players/components").mkdir(parents=True)
                raw = [{"ProficiencyId": 10, "Name": "Test Blade", "Levels": [{"Perks": [{"Type": 1, "Value": 2}]}]}]
                (root / "data/items/proficiencies.json").write_text(json.dumps(raw), encoding="utf-8")
                (root / "src/items/items.cpp").write_text(
                    "\n".join(
                        [
                            "ItemType &iType = items[object.id()]",
                            "iType.id = static_cast<uint16_t>(object.id())",
                            "object.flags().has_proficiency()",
                            "iType.proficiencyId = proficiencyId",
                            "WeaponProficiency::getProficiencies()",
                        ]
                    ),
                    encoding="utf-8",
                )
                (root / "src/creatures/players/components/weapon_proficiency.cpp").write_text(
                    "\n".join(
                        [
                            'fmt::format("{}/items/proficiencies.json", coreFolder)',
                            'proficiency.id = proficiencyJson["ProficiencyId"].get<uint16_t>()',
                            'm_player.kv()->scoped("weapon-proficiency")',
                            "Item::items[weaponId].proficiencyId == 0",
                        ]
                    ),
                    encoding="utf-8",
                )
                stub = types.ModuleType("tibia_proficiency_reference_index")

                def parse(payload, **_: object):
                    entry = source_entry()
                    return [entry], {"duplicateProficiencyIds": [], "duplicateNames": []}, {}

                stub._parse_proficiencies = parse
                previous = sys.modules.get("tibia_proficiency_reference_index")
                sys.modules["tibia_proficiency_reference_index"] = stub
                try:
                    report = build_canary_evidence(root)
                finally:
                    if previous is None:
                        del sys.modules["tibia_proficiency_reference_index"]
                    else:
                        sys.modules["tibia_proficiency_reference_index"] = previous
                self.assertEqual(report["format"], CANARY_EVIDENCE_FORMAT)
                self.assertEqual(report["runtimeDefinitions"]["recordCount"], 1)
                self.assertTrue(report["itemBindingContract"]["objectIdAssignsItemId"])
                self.assertEqual(report["runtimeSupport"]["persistence"], "source-supported")

    def test_report_counts_all_allowed_states(self) -> None:
            source, appearance, evidence, resolver = resolved_fixture()
            report = build_correlation(
                proficiency_index=source,
                proficiency_index_sha256=SHA_A,
                appearances_index=appearance,
                appearances_index_sha256=SHA_B,
                canary_evidence=evidence,
                canary_evidence_sha256=SHA_C,
                resolver=resolver,
                resolver_sha256=SHA_D,
            )
            self.assertEqual(set(report["summary"]["stateCounts"]), {
                "confirmed-reference", "conflicting", "partial", "reference-only", "stale-evidence", "target-only", "unresolved-id-space"
            })


if __name__ == "__main__":
    unittest.main()
