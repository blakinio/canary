from __future__ import annotations

import hashlib
import json
import lzma
import os
import tempfile
import unittest
from pathlib import Path

from tibia_staticdata_reference_index import (
    INDEX_FORMAT,
    StaticDataReferenceError,
    build_index,
    deterministic_json,
    select_schema,
    write_index,
)


def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _field(number: int, wire_type: int, value: int | bytes) -> bytes:
    key = _varint((number << 3) | wire_type)
    if wire_type == 0:
        return key + _varint(int(value))
    if wire_type == 2:
        payload = bytes(value)
        return key + _varint(len(payload)) + payload
    raise AssertionError(wire_type)


def _uint(number: int, value: int) -> bytes:
    return _field(number, 0, value)


def _string(number: int, value: str) -> bytes:
    return _field(number, 2, value.encode())


def _message(number: int, *parts: bytes) -> bytes:
    return _field(number, 2, b"".join(parts))


def _manifest(source: Path, *, input_id: str = "staticdata") -> dict[str, object]:
    data = source.read_bytes()
    return {
        "format": "canary-tibia-client-reference-manifest-v1",
        "referenceId": "fixture-reference",
        "selectedInputs": [
            {
                "id": input_id,
                "path": "client/staticdata.dat",
                "sizeBytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        ],
    }


def _legacy_document(*, duplicate_id: bool = False, missing_name: bool = False) -> bytes:
    creature_one = _message(
        1,
        _uint(1, 7),
        _string(2, "Rat"),
        _message(3, _uint(1, 21), _message(2, _uint(1, 1), _uint(2, 2), _uint(3, 3), _uint(4, 4))),
        _uint(4, 1),
        _uint(5, 2),
        _uint(6, 0),
        _uint(7, 1),
    )
    creature_two = b""
    if duplicate_id:
        creature_two = _message(1, _uint(1, 7), _string(2, "Cave Rat"))
    title_parts = [_uint(1, 10)]
    if not missing_name:
        title_parts.append(_string(2, "Explorer"))
    title_parts.extend((_string(3, "Fixture title"), _uint(4, 2)))
    title = _message(2, *title_parts)
    house = _message(
        3,
        _uint(1, 100),
        _string(2, "Legacy House"),
        _string(3, "Fixture house"),
        _uint(4, 5000),
        _uint(5, 42),
        _message(6, _uint(1, 32000), _uint(2, 32001), _uint(3, 7)),
        _uint(7, 2),
        _uint(8, 0),
        _string(9, "Thais"),
        _uint(10, 1),
    )
    boss = _message(4, _uint(1, 200), _string(2, "Boss"), _uint(4, 1))
    quest = _message(5, _uint(1, 300), _string(2, "Quest"))
    return creature_one + creature_two + title + house + boss + quest


def _newer_document() -> bytes:
    monster = _message(1, _uint(1, 8), _string(2, "Dragon"), _uint(6, 0), _uint(7, 1))
    monster_class = _message(2, _uint(1, 2), _string(2, "Dragonkin"))
    achievement = _message(3, _uint(1, 11), _string(2, "Hero"), _string(3, "Fixture achievement"), _uint(4, 3))
    house = _message(
        4,
        _uint(1, 101),
        _string(2, "New House"),
        _string(3, "Fixture newer house"),
        _uint(4, 6000),
        _uint(5, 3),
        _message(6, _uint(1, 32100), _uint(2, 32101), _uint(3, 6)),
        _uint(7, 55),
        _uint(8, 1),
        _string(9, "Carlin"),
        _uint(10, 0),
    )
    boss = _message(5, _uint(1, 201), _string(2, "Archboss"), _uint(4, 1))
    quest = _message(6, _uint(1, 301), _string(2, "New Quest"))
    return monster + monster_class + achievement + house + boss + quest


class StaticDataReferenceIndexTests(unittest.TestCase):
    def _build(self, source_bytes: bytes, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticdata.dat"
            source.write_bytes(source_bytes)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(_manifest(source), sort_keys=True), encoding="utf-8")
            payload, protected = build_index(
                manifest_path=manifest,
                source_path=source,
                input_id="staticdata",
                **kwargs,
            )
            return payload, tuple(protected)

    def test_legacy_schema_preserves_source_categories_and_house_field_order(self):
        payload, _ = self._build(_legacy_document())
        self.assertEqual(payload["format"], INDEX_FORMAT)
        self.assertEqual(payload["source"]["schemaFamily"], "legacy")
        self.assertEqual(set(payload["categories"]), {"creatures", "titles", "houses", "bosses", "quests"})
        house = payload["categories"]["houses"]["records"][0]
        self.assertEqual(house["size"], 42)
        self.assertEqual(house["beds"], 2)
        self.assertEqual(house["position"], {"x": 32000, "y": 32001, "z": 7})
        self.assertEqual(payload["categories"]["quests"]["records"][0], {"id": 300, "name": "Quest", "sourceOrdinal": 1})
        self.assertFalse(payload["policy"]["gameplayConclusions"])
        self.assertTrue(payload["policy"]["questInventoryOnly"])

    def test_newer_schema_preserves_achievement_and_monster_class_categories(self):
        payload, _ = self._build(_newer_document())
        self.assertEqual(payload["source"]["schemaFamily"], "newer")
        self.assertEqual(
            set(payload["categories"]),
            {"monsters", "monsterClasses", "achievements", "houses", "bosses", "quests"},
        )
        house = payload["categories"]["houses"]["records"][0]
        self.assertEqual(house["beds"], 3)
        self.assertEqual(house["size"], 55)
        self.assertEqual(payload["categories"]["monsterClasses"]["records"][0]["name"], "Dragonkin")
        self.assertEqual(payload["categories"]["achievements"]["records"][0]["grade"], 3)

    def test_ambiguous_schema_fails_closed(self):
        common_only = _message(1, _uint(1, 1), _string(2, "Common"))
        with self.assertRaisesRegex(StaticDataReferenceError, "ambiguous StaticData schema"):
            select_schema(common_only)

    def test_conflicting_schema_discriminators_fail_closed(self):
        conflicting = _message(2, _uint(1, 1), _string(2, "Title"), _string(3, "D"), _uint(4, 1)) + _message(
            6, _uint(1, 2), _string(2, "Quest")
        )
        with self.assertRaisesRegex(StaticDataReferenceError, "conflicting StaticData schema evidence"):
            select_schema(conflicting)

    def test_unknown_top_level_field_fails_closed(self):
        unsupported = _legacy_document() + _message(7, _uint(1, 1))
        with self.assertRaisesRegex(StaticDataReferenceError, "unsupported StaticData top-level"):
            select_schema(unsupported)

    def test_malformed_length_delimited_field_fails_closed(self):
        with self.assertRaisesRegex(StaticDataReferenceError, "truncated protobuf"):
            select_schema(b"\x0a\x05\x08")

    def test_duplicate_ids_are_explicit_findings(self):
        payload, _ = self._build(_legacy_document(duplicate_id=True))
        self.assertEqual(
            payload["findings"]["duplicateIds"],
            [{"category": "creatures", "id": 7, "sourceOrdinals": [1, 2]}],
        )
        self.assertEqual(payload["summary"]["duplicateIdCount"], 1)

    def test_missing_name_is_explicit_finding(self):
        payload, _ = self._build(_legacy_document(missing_name=True))
        self.assertIn(
            {"category": "titles", "field": "name", "sourceOrdinal": 1},
            payload["findings"]["missingRequiredFields"],
        )

    def test_xz_variant_is_supported_and_bounded(self):
        compressed = lzma.compress(_legacy_document(), format=lzma.FORMAT_XZ)
        payload, _ = self._build(compressed)
        self.assertEqual(payload["source"]["encoding"], "xz")
        self.assertEqual(payload["source"]["schemaFamily"], "legacy")

    def test_lzma_alone_variant_is_supported(self):
        compressed = lzma.compress(_newer_document(), format=lzma.FORMAT_ALONE)
        payload, _ = self._build(compressed)
        self.assertEqual(payload["source"]["encoding"], "lzma")
        self.assertEqual(payload["source"]["schemaFamily"], "newer")

    def test_tibia_lzma_unknown_size_header_patch_is_supported(self):
        compressed = bytearray(lzma.compress(_legacy_document(), format=lzma.FORMAT_ALONE))
        compressed[5:13] = (0).to_bytes(8, "little")
        payload, _ = self._build(bytes(compressed))
        self.assertEqual(payload["source"]["encoding"], "lzma")
        self.assertEqual(payload["source"]["schemaFamily"], "legacy")

    def test_decompressed_size_limit_fails_closed(self):
        compressed = lzma.compress(_legacy_document(), format=lzma.FORMAT_XZ)
        with self.assertRaisesRegex(StaticDataReferenceError, "decompressed data exceeds"):
            self._build(compressed, max_decompressed_bytes=16)

    def test_manifest_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticdata.dat"
            source.write_bytes(_legacy_document())
            manifest_payload = _manifest(source)
            manifest_payload["selectedInputs"][0]["sha256"] = "0" * 64
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
            with self.assertRaisesRegex(StaticDataReferenceError, "SHA-256 does not match"):
                build_index(manifest_path=manifest, source_path=source, input_id="staticdata")

    def test_manifest_size_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticdata.dat"
            source.write_bytes(_legacy_document())
            manifest_payload = _manifest(source)
            manifest_payload["selectedInputs"][0]["sizeBytes"] += 1
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
            with self.assertRaisesRegex(StaticDataReferenceError, "size does not match"):
                build_index(manifest_path=manifest, source_path=source, input_id="staticdata")

    def test_wrong_manifest_format_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticdata.dat"
            source.write_bytes(_legacy_document())
            manifest_payload = _manifest(source)
            manifest_payload["format"] = "wrong"
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
            with self.assertRaisesRegex(StaticDataReferenceError, "manifest format"):
                build_index(manifest_path=manifest, source_path=source, input_id="staticdata")

    def test_missing_input_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticdata.dat"
            source.write_bytes(_legacy_document())
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(_manifest(source)), encoding="utf-8")
            with self.assertRaisesRegex(StaticDataReferenceError, "exactly one selected input"):
                build_index(manifest_path=manifest, source_path=source, input_id="other")

    def test_deterministic_json_is_byte_stable(self):
        first, _ = self._build(_legacy_document())
        second, _ = self._build(_legacy_document())
        self.assertEqual(deterministic_json(first), deterministic_json(second))

    def test_write_index_is_no_clobber_and_protects_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticdata.dat"
            source.write_bytes(_legacy_document())
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(_manifest(source)), encoding="utf-8")
            payload, protected = build_index(manifest_path=manifest, source_path=source, input_id="staticdata")
            output = root / "index.json"
            write_index(output, payload, protected_inputs=protected)
            with self.assertRaisesRegex(StaticDataReferenceError, "already exists"):
                write_index(output, payload, protected_inputs=protected)
            with self.assertRaisesRegex(StaticDataReferenceError, "collides"):
                write_index(source, payload, protected_inputs=protected, overwrite=True)

    @unittest.skipUnless(
        os.environ.get("CANARY_TIBIA_STATICDATA_FILE"),
        "set CANARY_TIBIA_STATICDATA_FILE for opt-in real-file validation",
    )
    def test_opt_in_real_staticdata_file(self):
        source = Path(os.environ["CANARY_TIBIA_STATICDATA_FILE"])
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text(json.dumps(_manifest(source)), encoding="utf-8")
            payload, _ = build_index(manifest_path=manifest, source_path=source, input_id="staticdata")
        self.assertGreater(payload["summary"]["totalRecords"], 0)
        self.assertIn(payload["source"]["schemaFamily"], {"legacy", "newer"})


if __name__ == "__main__":
    unittest.main()
