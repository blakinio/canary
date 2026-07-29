from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from tibia_proficiency_reference_index import (
    INDEX_FORMAT,
    MANIFEST_FORMAT,
    ProficiencyReferenceError,
    build_index,
    deterministic_json,
)
from tibia_proficiency_reference_resolver import validate_proficiency_index

CURRENT_FILE_SHA256 = "97e59f4c247c6a64884ecbbfcceb2ba6dbad82f4fe52749f035b6b3d01c84ee1"


def _document(perk: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "Levels": [{"Perks": [perk]}],
            "Name": "Reference projectile",
            "ProficiencyId": 422,
            "Version": 1,
        }
    ]


class ProficiencyReferenceIndexSchemaV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _build(self, payload: object) -> dict[str, object]:
        source = self.root / "proficiencies.json"
        source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        data = source.read_bytes()
        manifest = self.root / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "format": MANIFEST_FORMAT,
                    "schemaVersion": 1,
                    "referenceId": "schema-v2-fixture",
                    "selectedInputs": [
                        {
                            "id": "proficiency",
                            "path": "assets/proficiencies.json",
                            "sizeBytes": len(data),
                            "sha256": hashlib.sha256(data).hexdigest(),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        result, _ = build_index(
            manifest_path=manifest,
            source_path=source,
            input_id="proficiency",
        )
        return result

    def test_preserves_reviewed_projectile_probability_perk_without_inventing_value(self) -> None:
        payload = self._build(
            _document(
                {
                    "ElementId": 3,
                    "MissileId": 42,
                    "Multiplier": 2.0,
                    "Probability": 0.01,
                    "Type": 32,
                }
            )
        )
        self.assertEqual(payload["format"], INDEX_FORMAT)
        self.assertEqual(payload["schemaVersion"], 2)
        perk = payload["proficiencies"][0]["levels"][0]["perks"][0]
        self.assertEqual(
            perk,
            {
                "sourceOrdinal": 1,
                "type": 32,
                "elementId": 3,
                "missileId": 42,
                "multiplier": 2.0,
                "probability": 0.01,
            },
        )
        self.assertNotIn("value", perk)

    def test_preserves_legacy_value_perks(self) -> None:
        payload = self._build(_document({"SkillId": 8, "Type": 3, "Value": 1}))
        perk = payload["proficiencies"][0]["levels"][0]["perks"][0]
        self.assertEqual(perk["value"], 1)
        self.assertEqual(perk["skillId"], 8)

    def test_requires_type_and_one_finite_numeric_effect_field(self) -> None:
        for perk in (
            {"ElementId": 3},
            {"ElementId": 3, "Type": 32},
            {"Multiplier": "2", "Type": 32},
            {"Probability": float("inf"), "Type": 32},
        ):
            with self.subTest(perk=perk), self.assertRaises(ProficiencyReferenceError):
                self._build(_document(perk))

    def test_is_deterministic_and_tcr007_accepts_schema_versions_one_and_two(self) -> None:
        first = self._build(_document({"Multiplier": 3, "Probability": 0.25, "Type": 32}))
        second = self._build(_document({"Multiplier": 3, "Probability": 0.25, "Type": 32}))
        self.assertEqual(deterministic_json(first), deterministic_json(second))
        normalized = validate_proficiency_index(first, max_records=10)
        self.assertEqual(normalized[0]["proficiencyId"], 422)
        legacy = dict(first)
        legacy["schemaVersion"] = 1
        self.assertEqual(validate_proficiency_index(legacy, max_records=10)[0]["proficiencyId"], 422)
        incompatible = dict(first)
        incompatible["schemaVersion"] = 3
        with self.assertRaisesRegex(Exception, "schemaVersion"):
            validate_proficiency_index(incompatible, max_records=10)

    def test_opt_in_current_real_file(self) -> None:
        raw_path = os.environ.get("CANARY_TIBIA_PROFICIENCY_CURRENT_FILE")
        if not raw_path:
            self.skipTest("set CANARY_TIBIA_PROFICIENCY_CURRENT_FILE for exact external-file validation")
        source = Path(raw_path)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), CURRENT_FILE_SHA256)
        data = source.read_bytes()
        manifest = self.root / "current-manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "format": MANIFEST_FORMAT,
                    "schemaVersion": 1,
                    "referenceId": "current-real-file",
                    "selectedInputs": [
                        {
                            "id": "proficiency",
                            "path": source.name,
                            "sizeBytes": len(data),
                            "sha256": CURRENT_FILE_SHA256,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        payload, _ = build_index(manifest_path=manifest, source_path=source, input_id="proficiency")
        self.assertEqual(payload["schemaVersion"], 2)
        self.assertEqual(payload["summary"]["proficiencyCount"], 443)
        self.assertEqual(payload["summary"]["levelCount"], 2211)
        self.assertEqual(payload["summary"]["perkCount"], 3671)
        projectile = [
            perk
            for proficiency in payload["proficiencies"]
            for level in proficiency["levels"]
            for perk in level["perks"]
            if perk["type"] == 32
        ]
        self.assertEqual(len(projectile), 22)
        self.assertTrue(all("value" not in perk for perk in projectile))


if __name__ == "__main__":
    unittest.main()
