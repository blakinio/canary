from __future__ import annotations

import hashlib
import json
import lzma
import os
import tempfile
import unittest
from pathlib import Path

from tibia_proficiency_reference_index import (
    INDEX_FORMAT,
    MANIFEST_FORMAT,
    PROFICIENCY_ID_NAMESPACE,
    ProficiencyReferenceError,
    build_index,
    deterministic_json,
    write_index,
)

REAL_FILE_SHA256 = "1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22"


def sample_document() -> list[dict[str, object]]:
    return [
        {
            "Levels": [
                {
                    "Perks": [
                        {"SkillId": 8, "Type": 3, "Value": 1},
                        {
                            "AugmentType": 16,
                            "SpellId": 105,
                            "Type": 5,
                            "Value": 0.1,
                        },
                        {
                            "BestiaryId": 77,
                            "BestiaryName": "Test Creature",
                            "DamageType": 4,
                            "ElementId": 3,
                            "Range": 2,
                            "Type": 9,
                            "Value": 1.5,
                        },
                    ],
                    "XpRequired": 1250,
                }
            ],
            "Name": "Reference Sword",
            "ProficiencyId": 6,
            "Version": 7,
        }
    ]


class ProficiencyReferenceIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_source(self, data: bytes, name: str = "proficiencies.json") -> Path:
        path = self.root / name
        path.write_bytes(data)
        return path

    def _json_bytes(self, payload: object | None = None) -> bytes:
        return json.dumps(payload if payload is not None else sample_document(), ensure_ascii=False).encode("utf-8")

    def _write_manifest(
        self,
        source: Path,
        *,
        input_id: str = "proficiency",
        digest: str | None = None,
        size: int | None = None,
        name: str = "manifest.json",
    ) -> Path:
        data = source.read_bytes()
        manifest = {
            "format": MANIFEST_FORMAT,
            "schemaVersion": 1,
            "referenceId": "reference-fixture",
            "selectedInputs": [
                {
                    "id": input_id,
                    "path": f"assets/{source.name}",
                    "sizeBytes": len(data) if size is None else size,
                    "sha256": hashlib.sha256(data).hexdigest() if digest is None else digest,
                }
            ],
        }
        path = self.root / name
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def _build(self, source: Path, **kwargs: int) -> dict[str, object]:
        manifest = self._write_manifest(source)
        payload, _ = build_index(
            manifest_path=manifest,
            source_path=source,
            input_id="proficiency",
            **kwargs,
        )
        return payload

    def test_builds_complete_definition_only_index(self) -> None:
        source = self._write_source(self._json_bytes())
        payload = self._build(source)
        self.assertEqual(payload["format"], INDEX_FORMAT)
        self.assertEqual(payload["source"]["encoding"], "raw")
        self.assertEqual(payload["identifierNamespaces"]["proficiencyId"]["name"], PROFICIENCY_ID_NAMESPACE)
        self.assertFalse(payload["identifierNamespaces"]["proficiencyId"]["appearanceEquivalent"])
        record = payload["proficiencies"][0]
        self.assertEqual(record["sourceOrdinal"], 1)
        self.assertEqual(record["proficiencyId"], 6)
        self.assertEqual(record["name"], "Reference Sword")
        self.assertEqual(record["version"], 7)
        level = record["levels"][0]
        self.assertEqual(level["xpRequired"], 1250)
        self.assertEqual(level["perks"][0]["skillId"], 8)
        self.assertEqual(level["perks"][1]["augmentType"], 16)
        self.assertEqual(level["perks"][2]["bestiaryName"], "Test Creature")
        self.assertEqual(payload["summary"]["proficiencyCount"], 1)
        self.assertEqual(payload["summary"]["levelCount"], 1)
        self.assertEqual(payload["summary"]["perkCount"], 3)
        self.assertEqual(payload["summary"]["xpRequirementCount"], 1)
        self.assertFalse(payload["policy"]["itemsXmlWriting"])
        self.assertFalse(payload["policy"]["gameplayConclusions"])

    def test_preserves_source_order_and_numeric_values_deterministically(self) -> None:
        document = sample_document() + [
            {
                "Levels": [{"Perks": [{"Type": 12, "Value": 0.25}]}],
                "Name": "Second",
                "ProficiencyId": 8,
            }
        ]
        source = self._write_source(self._json_bytes(document))
        first = self._build(source)
        second = self._build(source)
        self.assertEqual(deterministic_json(first), deterministic_json(second))
        self.assertEqual([row["proficiencyId"] for row in first["proficiencies"]], [6, 8])
        self.assertEqual(first["proficiencies"][1]["levels"][0]["perks"][0]["value"], 0.25)

    def test_reports_duplicate_ids_and_names_without_overwriting(self) -> None:
        document = sample_document() + sample_document()
        source = self._write_source(self._json_bytes(document))
        payload = self._build(source)
        self.assertEqual(len(payload["proficiencies"]), 2)
        self.assertEqual(
            payload["findings"]["duplicateProficiencyIds"],
            [{"proficiencyId": 6, "sourceOrdinals": [1, 2]}],
        )
        self.assertEqual(payload["summary"]["duplicateProficiencyIdCount"], 1)
        self.assertEqual(payload["summary"]["duplicateNameCount"], 1)

    def test_supports_bounded_xz_and_lzma_sources(self) -> None:
        raw = self._json_bytes()
        for name, data, expected in (
            ("proficiencies.json.xz", lzma.compress(raw, format=lzma.FORMAT_XZ), "xz"),
            ("proficiencies.json.lzma", lzma.compress(raw, format=lzma.FORMAT_ALONE), "lzma"),
        ):
            with self.subTest(name=name):
                source = self._write_source(data, name)
                payload = self._build(source)
                self.assertEqual(payload["source"]["encoding"], expected)
                self.assertEqual(payload["source"]["decodedSizeBytes"], len(raw))

    def test_rejects_manifest_size_and_hash_mismatch(self) -> None:
        source = self._write_source(self._json_bytes())
        for manifest in (
            self._write_manifest(source, size=source.stat().st_size + 1, name="size-manifest.json"),
            self._write_manifest(source, digest="0" * 64, name="hash-manifest.json"),
        ):
            with self.subTest(manifest=manifest.read_text()):
                with self.assertRaises(ProficiencyReferenceError):
                    build_index(manifest_path=manifest, source_path=source, input_id="proficiency")

    def test_rejects_duplicate_json_object_keys(self) -> None:
        source = self._write_source(
            b'[{"Levels":[],"Name":"A","ProficiencyId":6,"ProficiencyId":7}]'
        )
        with self.assertRaisesRegex(ProficiencyReferenceError, "duplicate JSON object key"):
            self._build(source)

    def test_rejects_unsupported_fields_at_every_level(self) -> None:
        cases = []
        entry = sample_document()
        entry[0]["Unexpected"] = True
        cases.append(entry)
        level = sample_document()
        level[0]["Levels"][0]["Unexpected"] = True
        cases.append(level)
        perk = sample_document()
        perk[0]["Levels"][0]["Perks"][0]["Unexpected"] = True
        cases.append(perk)
        for index, document in enumerate(cases):
            with self.subTest(index=index):
                source = self._write_source(self._json_bytes(document), f"unsupported-{index}.json")
                with self.assertRaisesRegex(ProficiencyReferenceError, "unsupported field"):
                    self._build(source)

    def test_rejects_missing_required_fields_and_invalid_types(self) -> None:
        cases = [
            [{}],
            [{"Levels": [], "Name": "A", "ProficiencyId": 0}],
            [{"Levels": "bad", "Name": "A", "ProficiencyId": 1}],
            [{"Levels": [{"Perks": [{"Type": True, "Value": 1}]}], "Name": "A", "ProficiencyId": 1}],
            [{"Levels": [{"Perks": [{"Type": 1, "Value": "bad"}]}], "Name": "A", "ProficiencyId": 1}],
        ]
        for index, document in enumerate(cases):
            with self.subTest(index=index):
                source = self._write_source(self._json_bytes(document), f"invalid-{index}.json")
                with self.assertRaises(ProficiencyReferenceError):
                    self._build(source)

    def test_rejects_non_finite_values(self) -> None:
        source = self._write_source(
            b'[{"Levels":[{"Perks":[{"Type":1,"Value":1e400}]}],"Name":"A","ProficiencyId":1}]'
        )
        with self.assertRaisesRegex(ProficiencyReferenceError, "finite"):
            self._build(source)
        source_nan = self._write_source(
            b'[{"Levels":[{"Perks":[{"Type":1,"Value":NaN}]}],"Name":"A","ProficiencyId":1}]',
            "nan.json",
        )
        with self.assertRaisesRegex(ProficiencyReferenceError, "non-finite"):
            self._build(source_nan)

    def test_enforces_source_decompressed_and_count_bounds(self) -> None:
        raw = self._json_bytes()
        source = self._write_source(raw)
        with self.assertRaisesRegex(ProficiencyReferenceError, "source exceeds"):
            self._build(source, max_source_bytes=len(raw) - 1)
        compressed = self._write_source(lzma.compress(raw, format=lzma.FORMAT_XZ), "bounded.xz")
        with self.assertRaisesRegex(ProficiencyReferenceError, "decompressed data exceeds"):
            self._build(compressed, max_decompressed_bytes=len(raw) - 1)
        for key, value in (("max_proficiencies", 0), ("max_levels", 0), ("max_perks", 0)):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ProficiencyReferenceError, "positive integer"):
                    self._build(source, **{key: value})

    def test_enforces_positive_count_limits_with_multi_record_fixture(self) -> None:
        source = self._write_source(self._json_bytes(sample_document() + sample_document()))
        with self.assertRaisesRegex(ProficiencyReferenceError, "proficiency count exceeds"):
            self._build(source, max_proficiencies=1)
        two_levels_document = sample_document()
        two_levels_document[0]["Levels"].append({"Perks": [{"Type": 1, "Value": 1}]})
        two_levels = self._write_source(self._json_bytes(two_levels_document), "two-levels.json")
        with self.assertRaisesRegex(ProficiencyReferenceError, "level count exceeds"):
            self._build(two_levels, max_levels=1)
        single = self._write_source(self._json_bytes(), "single.json")
        with self.assertRaisesRegex(ProficiencyReferenceError, "perk count exceeds"):
            self._build(single, max_perks=2)

    def test_output_is_create_new_and_protects_inputs(self) -> None:
        source = self._write_source(self._json_bytes())
        manifest = self._write_manifest(source)
        payload, protected = build_index(manifest_path=manifest, source_path=source, input_id="proficiency")
        output = self.root / "index.json"
        write_index(output, payload, protected_inputs=protected)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["format"], INDEX_FORMAT)
        with self.assertRaisesRegex(ProficiencyReferenceError, "already exists"):
            write_index(output, payload, protected_inputs=protected)
        write_index(output, payload, protected_inputs=protected, overwrite=True)
        with self.assertRaisesRegex(ProficiencyReferenceError, "collides"):
            write_index(source, payload, protected_inputs=protected, overwrite=True)

    def test_rejects_symlink_source_and_output(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        source = self._write_source(self._json_bytes())
        source_link = self.root / "source-link.json"
        source_link.symlink_to(source)
        manifest = self._write_manifest(source)
        with self.assertRaisesRegex(ProficiencyReferenceError, "must not be a symlink"):
            build_index(manifest_path=manifest, source_path=source_link, input_id="proficiency")
        payload, protected = build_index(manifest_path=manifest, source_path=source, input_id="proficiency")
        output_target = self.root / "target.json"
        output_target.write_text("{}", encoding="utf-8")
        output_link = self.root / "output-link.json"
        output_link.symlink_to(output_target)
        with self.assertRaisesRegex(ProficiencyReferenceError, "must not be a symlink"):
            write_index(output_link, payload, protected_inputs=protected, overwrite=True)

    def test_rejects_wrong_manifest_contract_and_missing_input(self) -> None:
        source = self._write_source(self._json_bytes())
        manifest = self._write_manifest(source)
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        payload["format"] = "wrong"
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(ProficiencyReferenceError, "manifest format"):
            build_index(manifest_path=manifest, source_path=source, input_id="proficiency")
        manifest = self._write_manifest(source)
        with self.assertRaisesRegex(ProficiencyReferenceError, "exactly one selected input"):
            build_index(manifest_path=manifest, source_path=source, input_id="missing")

    def test_opt_in_real_file(self) -> None:
        raw_path = os.environ.get("CANARY_TIBIA_PROFICIENCY_FILE")
        if not raw_path:
            self.skipTest("set CANARY_TIBIA_PROFICIENCY_FILE for exact external-file validation")
        source = Path(raw_path)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(digest, REAL_FILE_SHA256)
        manifest = self._write_manifest(source)
        payload, _ = build_index(manifest_path=manifest, source_path=source, input_id="proficiency")
        self.assertEqual(payload["summary"]["proficiencyCount"], 420)
        self.assertEqual(payload["summary"]["levelCount"], 2052)
        self.assertEqual(payload["summary"]["perkCount"], 3287)
        self.assertEqual(payload["summary"]["xpRequirementCount"], 0)
        self.assertEqual(payload["summary"]["duplicateProficiencyIdCount"], 0)
        self.assertEqual(payload["source"]["sha256"], REAL_FILE_SHA256)


if __name__ == "__main__":
    unittest.main()
