from __future__ import annotations

import hashlib
import json
import lzma
import os
import tempfile
import unittest
from pathlib import Path

from tibia_staticmapdata_reference_index import (
    INDEX_FORMAT,
    OBJECT_ID_NAMESPACE,
    StaticMapDataReferenceError,
    build_index,
    deterministic_json,
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


def _message(number: int, *parts: bytes) -> bytes:
    return _field(number, 2, b"".join(parts))


def _manifest(source: Path, *, input_id: str = "staticmapdata") -> dict[str, object]:
    data = source.read_bytes()
    return {
        "format": "canary-tibia-client-reference-manifest-v1",
        "referenceId": "fixture-reference",
        "selectedInputs": [
            {
                "id": input_id,
                "path": "client/staticmapdata.dat",
                "sizeBytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        ],
    }


def _tile(object_id: int, *, wall: bool | None = None, door: bool | None = None) -> bytes:
    parts = [_uint(1, object_id)]
    if wall is not None:
        parts.append(_message(101, _uint(2, int(wall))))
    if door is not None:
        parts.append(_message(102, _uint(2, int(door))))
    return b"".join(parts)


def _row(*tiles: bytes, flags: int | None = None) -> bytes:
    parts = [_message(1, tile) for tile in tiles]
    if flags is not None:
        parts.append(_uint(2, flags))
    return b"".join(parts)


def _house(
    house_id: int,
    *,
    width: int = 2,
    height: int = 2,
    floors: int = 1,
    rows: tuple[bytes, ...] | None = None,
    duplicate_width: bool = False,
) -> bytes:
    if rows is None:
        rows = (
            _row(_tile(100, wall=True), _tile(101), flags=1),
            _row(_tile(200, door=False), flags=1),
        )
    size_parts = [_uint(1, width)]
    if duplicate_width:
        size_parts.append(_uint(1, width + 1))
    size_parts.extend((_uint(2, height), _uint(3, floors)))
    layout = b"".join(
        (
            _message(1, _uint(1, 32000), _uint(2, 32001), _uint(3, 7)),
            _message(2, *size_parts),
            _message(3, _message(2, *(_message(3, row) for row in rows))),
        )
    )
    return _message(1, _uint(1, house_id), _message(2, layout))


class StaticMapDataReferenceIndexTests(unittest.TestCase):
    def _build(self, source_bytes: bytes, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticmapdata.dat"
            source.write_bytes(source_bytes)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(_manifest(source), sort_keys=True), encoding="utf-8")
            payload, protected = build_index(
                manifest_path=manifest,
                source_path=source,
                input_id="staticmapdata",
                **kwargs,
            )
            return payload, tuple(protected)

    def test_preserves_house_layout_rows_tiles_and_namespace(self):
        payload, _ = self._build(_house(101))
        self.assertEqual(payload["format"], INDEX_FORMAT)
        self.assertEqual(
            payload["objectIdNamespace"],
            {
                "name": OBJECT_ID_NAMESPACE,
                "resolution": "unresolved",
                "otbmItemIdEquivalent": False,
            },
        )
        house = payload["houses"][0]
        self.assertEqual(house["houseId"], 101)
        self.assertEqual(house["layout"]["position"], {"x": 32000, "y": 32001, "z": 7})
        self.assertEqual(house["layout"]["size"], {"width": 2, "height": 2, "floors": 1})
        rows = house["layout"]["tiles"]["floorData"]["rows"]
        self.assertEqual([row["sourceOrdinal"] for row in rows], [1, 2])
        self.assertEqual(rows[0]["flags"], 1)
        self.assertEqual(rows[0]["tiles"][0]["objectId"], 100)
        self.assertEqual(rows[0]["tiles"][0]["wallInfo"], {"isWall": True})
        self.assertEqual(rows[1]["tiles"][0]["doorInfo"], {"isDoor": False})
        self.assertEqual(
            house["layout"]["validation"],
            {
                "rowCount": 2,
                "rowFlagSum": 2,
                "encodedCellSpan": 4,
                "declaredCellCount": 4,
                "matchesDeclaredDimensions": True,
            },
        )
        self.assertEqual(payload["summary"]["houseCount"], 1)
        self.assertEqual(payload["summary"]["rowCount"], 2)
        self.assertEqual(payload["summary"]["tileRecordCount"], 3)
        self.assertFalse(payload["policy"]["otbmParsing"])
        self.assertFalse(payload["policy"]["otbmWriting"])
        self.assertEqual(payload["policy"]["objectIdMapping"], "unresolved")

    def test_duplicate_house_ids_are_findings(self):
        payload, _ = self._build(_house(101) + _house(101))
        self.assertEqual(
            payload["findings"]["duplicateHouseIds"],
            [{"houseId": 101, "sourceOrdinals": [1, 2]}],
        )
        self.assertEqual(payload["summary"]["duplicateHouseIdCount"], 1)

    def test_missing_required_fields_are_findings(self):
        payload, _ = self._build(_message(1, _uint(1, 101)))
        self.assertIn(
            {"path": "houses[1]", "field": "layout"},
            payload["findings"]["missingRequiredFields"],
        )

    def test_duplicate_singular_fields_are_findings(self):
        payload, _ = self._build(_house(101, duplicate_width=True))
        self.assertEqual(payload["summary"]["duplicateSingularFieldCount"], 1)
        self.assertEqual(payload["findings"]["duplicateSingularFields"][0]["fieldNumber"], 1)

    def test_encoded_cell_span_mismatch_is_explicit(self):
        rows = (_row(_tile(100)), _row(_tile(200)))
        payload, _ = self._build(_house(101, rows=rows))
        finding = payload["findings"]["dimensionMismatches"][0]
        self.assertEqual(finding["reason"], "encoded-cell-span-mismatch")
        self.assertEqual(finding["declaredCellCount"], 4)
        self.assertEqual(finding["encodedCellSpan"], 2)
        self.assertEqual(payload["summary"]["dimensionMismatchCount"], 1)

    def test_zero_dimension_is_explicit(self):
        payload, _ = self._build(_house(101, width=0, height=1, floors=1, rows=()))
        self.assertEqual(
            payload["findings"]["dimensionMismatches"][0]["reason"],
            "non-positive-dimension",
        )

    def test_unknown_field_fails_closed(self):
        malformed = _house(101) + _message(2, _uint(1, 1))
        with self.assertRaisesRegex(StaticMapDataReferenceError, "unsupported field 2 in staticmapdata"):
            self._build(malformed)

    def test_invalid_nested_bool_fails_closed(self):
        bad_row = _row(_uint(1, 100) + _message(101, _uint(2, 2)), flags=3)
        with self.assertRaisesRegex(StaticMapDataReferenceError, "invalid bool"):
            self._build(_house(101, rows=(bad_row,)))

    def test_malformed_length_delimited_field_fails_closed(self):
        with self.assertRaisesRegex(StaticMapDataReferenceError, "truncated protobuf"):
            self._build(b"\x0a\x05\x08")

    def test_xz_variant_is_supported_and_bounded(self):
        payload, _ = self._build(lzma.compress(_house(101), format=lzma.FORMAT_XZ))
        self.assertEqual(payload["source"]["encoding"], "xz")
        with self.assertRaisesRegex(StaticMapDataReferenceError, "decompressed data exceeds"):
            self._build(lzma.compress(_house(101), format=lzma.FORMAT_XZ), max_decompressed_bytes=16)

    def test_lzma_alone_and_tibia_header_variants_are_supported(self):
        compressed = lzma.compress(_house(101), format=lzma.FORMAT_ALONE)
        payload, _ = self._build(compressed)
        self.assertEqual(payload["source"]["encoding"], "lzma")
        patched = bytearray(compressed)
        patched[5:13] = (0).to_bytes(8, "little")
        payload, _ = self._build(bytes(patched))
        self.assertEqual(payload["source"]["encoding"], "lzma")

    def test_manifest_hash_and_size_mismatch_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticmapdata.dat"
            source.write_bytes(_house(101))
            manifest_payload = _manifest(source)
            manifest_payload["selectedInputs"][0]["sha256"] = "0" * 64
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
            with self.assertRaisesRegex(StaticMapDataReferenceError, "SHA-256 does not match"):
                build_index(manifest_path=manifest, source_path=source, input_id="staticmapdata")
            manifest_payload = _manifest(source)
            manifest_payload["selectedInputs"][0]["sizeBytes"] += 1
            manifest.write_text(json.dumps(manifest_payload), encoding="utf-8")
            with self.assertRaisesRegex(StaticMapDataReferenceError, "size does not match"):
                build_index(manifest_path=manifest, source_path=source, input_id="staticmapdata")

    def test_record_bounds_fail_closed(self):
        with self.assertRaisesRegex(StaticMapDataReferenceError, "house count exceeds"):
            self._build(_house(101) + _house(102), max_houses=1)
        with self.assertRaisesRegex(StaticMapDataReferenceError, "row count exceeds"):
            self._build(_house(101), max_rows=1)
        with self.assertRaisesRegex(StaticMapDataReferenceError, "tile record count exceeds"):
            self._build(_house(101), max_tile_records=2)
        with self.assertRaisesRegex(StaticMapDataReferenceError, "declared cell count exceeds"):
            self._build(_house(101), max_declared_cells=3)

    def test_deterministic_json_is_byte_stable(self):
        first, _ = self._build(_house(101))
        second, _ = self._build(_house(101))
        self.assertEqual(deterministic_json(first), deterministic_json(second))

    def test_write_index_is_no_clobber_and_protects_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "staticmapdata.dat"
            source.write_bytes(_house(101))
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(_manifest(source)), encoding="utf-8")
            payload, protected = build_index(
                manifest_path=manifest,
                source_path=source,
                input_id="staticmapdata",
            )
            output = root / "index.json"
            write_index(output, payload, protected_inputs=protected)
            with self.assertRaisesRegex(StaticMapDataReferenceError, "already exists"):
                write_index(output, payload, protected_inputs=protected)
            with self.assertRaisesRegex(StaticMapDataReferenceError, "collides"):
                write_index(source, payload, protected_inputs=protected, overwrite=True)

    @unittest.skipUnless(
        os.environ.get("CANARY_TIBIA_STATICMAPDATA_FILE"),
        "set CANARY_TIBIA_STATICMAPDATA_FILE for opt-in real-file validation",
    )
    def test_opt_in_real_staticmapdata_file(self):
        source = Path(os.environ["CANARY_TIBIA_STATICMAPDATA_FILE"])
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text(json.dumps(_manifest(source)), encoding="utf-8")
            payload, _ = build_index(
                manifest_path=manifest,
                source_path=source,
                input_id="staticmapdata",
            )
        self.assertGreater(payload["summary"]["houseCount"], 0)
        self.assertEqual(payload["objectIdNamespace"]["name"], OBJECT_ID_NAMESPACE)
        self.assertEqual(payload["summary"]["dimensionMismatchCount"], 0)


if __name__ == "__main__":
    unittest.main()
