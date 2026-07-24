from __future__ import annotations

import hashlib
import json
import lzma
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

INDEX_FORMAT = "canary-tibia-staticmapdata-index-v1"
MANIFEST_FORMAT = "canary-tibia-client-reference-manifest-v1"
OBJECT_ID_NAMESPACE = "staticmapdata.object_id"
SCHEMA_VERSION = 1
DEFAULT_MAX_SOURCE_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_DECOMPRESSED_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_MANIFEST_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_HOUSES = 100_000
DEFAULT_MAX_ROWS = 10_000_000
DEFAULT_MAX_TILE_RECORDS = 20_000_000
DEFAULT_MAX_DECLARED_CELLS = 20_000_000
MAX_NESTING_DEPTH = 10
XZ_MAGIC = b"\xfd7zXZ\x00"
_SHA256_HEX_LEN = 64


class StaticMapDataReferenceError(RuntimeError):
    pass


@dataclass(frozen=True)
class WireField:
    number: int
    wire_type: int
    value: int | bytes


@dataclass(frozen=True)
class FieldSpec:
    wire_type: int
    kind: str
    message: str | None = None
    repeated: bool = False


FIELD_SPECS: dict[str, dict[int, FieldSpec]] = {
    "staticmapdata": {1: FieldSpec(2, "message", "house_detail", repeated=True)},
    "house_detail": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "message", "house_layout"),
    },
    "house_layout": {
        1: FieldSpec(2, "message", "coordinate"),
        2: FieldSpec(2, "message", "area_size"),
        3: FieldSpec(2, "message", "house_tiles"),
    },
    "coordinate": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(0, "uint"),
        3: FieldSpec(0, "uint"),
    },
    "area_size": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(0, "uint"),
        3: FieldSpec(0, "uint"),
    },
    "house_tiles": {2: FieldSpec(2, "message", "house_floor_data")},
    "house_floor_data": {3: FieldSpec(2, "message", "house_tile_row", repeated=True)},
    "house_tile_row": {
        1: FieldSpec(2, "message", "house_tile", repeated=True),
        2: FieldSpec(0, "uint"),
    },
    "house_tile": {
        1: FieldSpec(0, "uint"),
        101: FieldSpec(2, "message", "house_tile_wall"),
        102: FieldSpec(2, "message", "house_tile_door"),
    },
    "house_tile_wall": {2: FieldSpec(0, "bool")},
    "house_tile_door": {2: FieldSpec(0, "bool")},
}


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise StaticMapDataReferenceError("truncated protobuf varint")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            if shift == 63 and byte > 1:
                raise StaticMapDataReferenceError("protobuf varint exceeds 64 bits")
            return value, offset
    raise StaticMapDataReferenceError("protobuf varint exceeds 10 bytes")


def _parse_wire_message(data: bytes) -> list[WireField]:
    fields: list[WireField] = []
    offset = 0
    while offset < len(data):
        key, offset = _read_varint(data, offset)
        number = key >> 3
        wire_type = key & 0x07
        if number <= 0:
            raise StaticMapDataReferenceError("protobuf field number must be positive")
        if wire_type == 0:
            value, offset = _read_varint(data, offset)
            fields.append(WireField(number, wire_type, value))
        elif wire_type == 1:
            end = offset + 8
            if end > len(data):
                raise StaticMapDataReferenceError("truncated protobuf fixed64 field")
            fields.append(WireField(number, wire_type, data[offset:end]))
            offset = end
        elif wire_type == 2:
            length, offset = _read_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise StaticMapDataReferenceError("truncated protobuf length-delimited field")
            fields.append(WireField(number, wire_type, data[offset:end]))
            offset = end
        elif wire_type == 5:
            end = offset + 4
            if end > len(data):
                raise StaticMapDataReferenceError("truncated protobuf fixed32 field")
            fields.append(WireField(number, wire_type, data[offset:end]))
            offset = end
        else:
            raise StaticMapDataReferenceError(f"unsupported protobuf wire type: {wire_type}")
    return fields


def _validate_message(fields: Sequence[WireField], message_type: str, *, depth: int = 0) -> None:
    if depth > MAX_NESTING_DEPTH:
        raise StaticMapDataReferenceError("protobuf nesting limit exceeded")
    specs = FIELD_SPECS[message_type]
    for field in fields:
        spec = specs.get(field.number)
        if spec is None:
            raise StaticMapDataReferenceError(f"unsupported field {field.number} in {message_type}")
        if field.wire_type != spec.wire_type:
            raise StaticMapDataReferenceError(
                f"wrong wire type for {message_type}.{field.number}: expected {spec.wire_type}, got {field.wire_type}"
            )
        if spec.kind == "bool":
            assert isinstance(field.value, int)
            if field.value not in (0, 1):
                raise StaticMapDataReferenceError(f"invalid bool value in {message_type}.{field.number}")
        elif spec.kind == "message":
            assert isinstance(field.value, bytes)
            nested = _parse_wire_message(field.value)
            _validate_message(nested, spec.message or "", depth=depth + 1)


def _validate_staticmapdata(data: bytes) -> list[WireField]:
    top_fields = _parse_wire_message(data)
    if not top_fields:
        raise StaticMapDataReferenceError("staticmapdata protobuf document is empty")
    _validate_message(top_fields, "staticmapdata")
    return top_fields


def _bounded_decompress(data: bytes, *, fmt: int, max_bytes: int, label: str) -> bytes:
    try:
        decoder = lzma.LZMADecompressor(format=fmt)
        output = decoder.decompress(data, max_length=max_bytes + 1)
    except lzma.LZMAError as exc:
        raise StaticMapDataReferenceError(f"{label} decompression failed") from exc
    if len(output) > max_bytes or not decoder.eof:
        if len(output) > max_bytes or not decoder.needs_input:
            raise StaticMapDataReferenceError(f"{label} decompressed data exceeds {max_bytes} bytes")
        raise StaticMapDataReferenceError(f"{label} stream is truncated or incomplete")
    if decoder.unused_data:
        raise StaticMapDataReferenceError(f"{label} stream has trailing or concatenated data")
    return output


def _decode_staticmapdata_bytes(data: bytes, *, max_decompressed_bytes: int) -> tuple[bytes, str, list[WireField]]:
    if data.startswith(XZ_MAGIC):
        decoded = _bounded_decompress(data, fmt=lzma.FORMAT_XZ, max_bytes=max_decompressed_bytes, label="XZ")
        return decoded, "xz", _validate_staticmapdata(decoded)

    raw_error: StaticMapDataReferenceError | None = None
    try:
        return data, "raw", _validate_staticmapdata(data)
    except StaticMapDataReferenceError as exc:
        raw_error = exc

    attempts: list[bytes] = []
    if len(data) >= 13:
        patched = bytearray(data)
        patched[5:13] = b"\xff" * 8
        attempts.append(bytes(patched))
    if not attempts or attempts[0] != data:
        attempts.append(data)

    for candidate in attempts:
        try:
            decoded = _bounded_decompress(
                candidate,
                fmt=lzma.FORMAT_ALONE,
                max_bytes=max_decompressed_bytes,
                label="LZMA",
            )
            return decoded, "lzma", _validate_staticmapdata(decoded)
        except StaticMapDataReferenceError:
            continue
    assert raw_error is not None
    raise raw_error


def _stat_identity(stat: os.stat_result) -> tuple[int, int, int, int]:
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)


def _read_stable_file(path: Path, *, max_bytes: int, label: str) -> tuple[bytes, int, str, Path]:
    target = path.expanduser()
    if target.is_symlink():
        raise StaticMapDataReferenceError(f"{label} must not be a symlink: {path}")
    try:
        resolved = target.resolve(strict=True)
    except OSError as exc:
        raise StaticMapDataReferenceError(f"{label} does not exist: {path}") from exc
    if not resolved.is_file():
        raise StaticMapDataReferenceError(f"{label} must be a regular file: {path}")
    before = resolved.stat()
    if before.st_size > max_bytes:
        raise StaticMapDataReferenceError(f"{label} exceeds {max_bytes} bytes")
    try:
        with resolved.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if _stat_identity(before) != _stat_identity(opened):
                raise StaticMapDataReferenceError(f"{label} changed before read")
            data = stream.read(max_bytes + 1)
            after_open = os.fstat(stream.fileno())
    except OSError as exc:
        raise StaticMapDataReferenceError(f"cannot read {label}: {exc}") from exc
    after = resolved.stat()
    if len(data) > max_bytes:
        raise StaticMapDataReferenceError(f"{label} exceeds {max_bytes} bytes")
    identities = {_stat_identity(before), _stat_identity(opened), _stat_identity(after_open), _stat_identity(after)}
    if len(identities) != 1 or len(data) != after.st_size:
        raise StaticMapDataReferenceError(f"{label} changed while reading")
    return data, len(data), hashlib.sha256(data).hexdigest(), resolved


def _load_manifest(path: Path, *, max_manifest_bytes: int) -> tuple[dict[str, object], str, Path]:
    data, _, sha256, resolved = _read_stable_file(path, max_bytes=max_manifest_bytes, label="manifest")
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StaticMapDataReferenceError("manifest must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict) or payload.get("format") != MANIFEST_FORMAT:
        raise StaticMapDataReferenceError(f"manifest format must be {MANIFEST_FORMAT}")
    if not isinstance(payload.get("referenceId"), str) or not payload["referenceId"]:
        raise StaticMapDataReferenceError("manifest referenceId must be non-empty")
    inputs = payload.get("selectedInputs")
    if not isinstance(inputs, list):
        raise StaticMapDataReferenceError("manifest selectedInputs must be an array")
    return payload, sha256, resolved


def _manifest_input(manifest: Mapping[str, object], input_id: str) -> Mapping[str, object]:
    inputs = manifest["selectedInputs"]
    assert isinstance(inputs, list)
    entries = [entry for entry in inputs if isinstance(entry, dict) and entry.get("id") == input_id]
    if len(entries) != 1:
        raise StaticMapDataReferenceError(f"manifest must contain exactly one selected input with id {input_id}")
    entry = entries[0]
    if not isinstance(entry.get("path"), str) or not entry["path"]:
        raise StaticMapDataReferenceError("manifest selected input path must be non-empty")
    size = entry.get("sizeBytes")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise StaticMapDataReferenceError("manifest selected input sizeBytes must be a non-negative integer")
    digest = entry.get("sha256")
    if not isinstance(digest, str) or len(digest) != _SHA256_HEX_LEN:
        raise StaticMapDataReferenceError("manifest selected input sha256 must be 64 hexadecimal characters")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise StaticMapDataReferenceError("manifest selected input sha256 must be hexadecimal") from exc
    return entry


def _group_fields(fields: Sequence[WireField]) -> dict[int, list[WireField]]:
    grouped: dict[int, list[WireField]] = defaultdict(list)
    for field in fields:
        grouped[field.number].append(field)
    return grouped


def _first_uint(grouped: Mapping[int, Sequence[WireField]], number: int) -> int | None:
    values = grouped.get(number, ())
    if not values:
        return None
    value = values[0].value
    assert isinstance(value, int)
    return value


def _first_bool(grouped: Mapping[int, Sequence[WireField]], number: int) -> bool | None:
    value = _first_uint(grouped, number)
    return None if value is None else bool(value)


def _first_message(grouped: Mapping[int, Sequence[WireField]], number: int) -> list[WireField] | None:
    values = grouped.get(number, ())
    if not values:
        return None
    value = values[0].value
    assert isinstance(value, bytes)
    return _parse_wire_message(value)


def _record_duplicate_singular_fields(
    grouped: Mapping[int, Sequence[WireField]],
    message_type: str,
    path: str,
    findings: list[dict[str, object]],
) -> None:
    specs = FIELD_SPECS[message_type]
    for number, occurrences in sorted(grouped.items()):
        spec = specs[number]
        if not spec.repeated and len(occurrences) > 1:
            findings.append(
                {
                    "path": path,
                    "messageType": message_type,
                    "fieldNumber": number,
                    "occurrences": len(occurrences),
                }
            )


def _required_uint(
    grouped: Mapping[int, Sequence[WireField]],
    number: int,
    *,
    path: str,
    field: str,
    missing: list[dict[str, object]],
) -> int | None:
    value = _first_uint(grouped, number)
    if value is None:
        missing.append({"path": path, "field": field})
    return value


def _required_message(
    grouped: Mapping[int, Sequence[WireField]],
    number: int,
    *,
    path: str,
    field: str,
    missing: list[dict[str, object]],
) -> list[WireField] | None:
    value = _first_message(grouped, number)
    if value is None:
        missing.append({"path": path, "field": field})
    return value


def _coordinate_document(
    fields: Sequence[WireField],
    *,
    path: str,
    missing: list[dict[str, object]],
    duplicates: list[dict[str, object]],
) -> dict[str, int]:
    grouped = _group_fields(fields)
    _record_duplicate_singular_fields(grouped, "coordinate", path, duplicates)
    result: dict[str, int] = {}
    for number, key in ((1, "x"), (2, "y"), (3, "z")):
        value = _required_uint(grouped, number, path=path, field=key, missing=missing)
        if value is not None:
            result[key] = value
    return result


def _size_document(
    fields: Sequence[WireField],
    *,
    path: str,
    missing: list[dict[str, object]],
    duplicates: list[dict[str, object]],
) -> dict[str, int]:
    grouped = _group_fields(fields)
    _record_duplicate_singular_fields(grouped, "area_size", path, duplicates)
    result: dict[str, int] = {}
    for number, key in ((1, "width"), (2, "height"), (3, "floors")):
        value = _required_uint(grouped, number, path=path, field=key, missing=missing)
        if value is not None:
            result[key] = value
    return result


def _tile_document(
    fields: Sequence[WireField],
    *,
    path: str,
    missing: list[dict[str, object]],
    duplicates: list[dict[str, object]],
) -> dict[str, object]:
    grouped = _group_fields(fields)
    _record_duplicate_singular_fields(grouped, "house_tile", path, duplicates)
    result: dict[str, object] = {}
    object_id = _required_uint(grouped, 1, path=path, field="objectId", missing=missing)
    if object_id is not None:
        result["objectId"] = object_id

    wall_fields = _first_message(grouped, 101)
    if wall_fields is not None:
        wall_grouped = _group_fields(wall_fields)
        _record_duplicate_singular_fields(wall_grouped, "house_tile_wall", f"{path}.wallInfo", duplicates)
        is_wall = _first_bool(wall_grouped, 2)
        wall_document: dict[str, bool] = {}
        if is_wall is None:
            missing.append({"path": f"{path}.wallInfo", "field": "isWall"})
        else:
            wall_document["isWall"] = is_wall
        result["wallInfo"] = wall_document

    door_fields = _first_message(grouped, 102)
    if door_fields is not None:
        door_grouped = _group_fields(door_fields)
        _record_duplicate_singular_fields(door_grouped, "house_tile_door", f"{path}.doorInfo", duplicates)
        is_door = _first_bool(door_grouped, 2)
        door_document: dict[str, bool] = {}
        if is_door is None:
            missing.append({"path": f"{path}.doorInfo", "field": "isDoor"})
        else:
            door_document["isDoor"] = is_door
        result["doorInfo"] = door_document
    return result


def _build_houses(
    top_fields: Sequence[WireField],
    *,
    max_houses: int,
    max_rows: int,
    max_tile_records: int,
    max_declared_cells: int,
) -> tuple[list[dict[str, object]], dict[str, object], dict[str, int]]:
    house_fields = [field for field in top_fields if field.number == 1]
    if len(house_fields) > max_houses:
        raise StaticMapDataReferenceError(f"staticmapdata house count exceeds {max_houses}")

    houses: list[dict[str, object]] = []
    missing: list[dict[str, object]] = []
    duplicates: list[dict[str, object]] = []
    dimension_mismatches: list[dict[str, object]] = []
    duplicate_house_ids: list[dict[str, object]] = []
    house_id_ordinals: dict[int, list[int]] = defaultdict(list)

    total_rows = 0
    total_tile_records = 0
    total_declared_cells = 0
    total_encoded_cell_span = 0

    for house_ordinal, field in enumerate(house_fields, start=1):
        assert isinstance(field.value, bytes)
        house_path = f"houses[{house_ordinal}]"
        house_grouped = _group_fields(_parse_wire_message(field.value))
        _record_duplicate_singular_fields(house_grouped, "house_detail", house_path, duplicates)
        house: dict[str, object] = {"sourceOrdinal": house_ordinal}

        house_id = _required_uint(house_grouped, 1, path=house_path, field="houseId", missing=missing)
        if house_id is not None:
            house["houseId"] = house_id
            house_id_ordinals[house_id].append(house_ordinal)

        layout_fields = _required_message(house_grouped, 2, path=house_path, field="layout", missing=missing)
        if layout_fields is None:
            houses.append(house)
            continue

        layout_path = f"{house_path}.layout"
        layout_grouped = _group_fields(layout_fields)
        _record_duplicate_singular_fields(layout_grouped, "house_layout", layout_path, duplicates)
        layout: dict[str, object] = {}

        position_fields = _required_message(layout_grouped, 1, path=layout_path, field="position", missing=missing)
        if position_fields is not None:
            layout["position"] = _coordinate_document(
                position_fields,
                path=f"{layout_path}.position",
                missing=missing,
                duplicates=duplicates,
            )

        size_fields = _required_message(layout_grouped, 2, path=layout_path, field="size", missing=missing)
        size: dict[str, int] = {}
        if size_fields is not None:
            size = _size_document(
                size_fields,
                path=f"{layout_path}.size",
                missing=missing,
                duplicates=duplicates,
            )
            layout["size"] = size

        tiles_fields = _required_message(layout_grouped, 3, path=layout_path, field="tiles", missing=missing)
        rows_document: list[dict[str, object]] = []
        row_flag_sum = 0
        if tiles_fields is not None:
            tiles_path = f"{layout_path}.tiles"
            tiles_grouped = _group_fields(tiles_fields)
            _record_duplicate_singular_fields(tiles_grouped, "house_tiles", tiles_path, duplicates)
            floor_fields = _required_message(
                tiles_grouped,
                2,
                path=tiles_path,
                field="floorData",
                missing=missing,
            )
            if floor_fields is not None:
                floor_path = f"{tiles_path}.floorData"
                floor_grouped = _group_fields(floor_fields)
                _record_duplicate_singular_fields(floor_grouped, "house_floor_data", floor_path, duplicates)
                row_fields = floor_grouped.get(3, ())
                total_rows += len(row_fields)
                if total_rows > max_rows:
                    raise StaticMapDataReferenceError(f"staticmapdata row count exceeds {max_rows}")
                for row_ordinal, row_field in enumerate(row_fields, start=1):
                    assert isinstance(row_field.value, bytes)
                    row_path = f"{floor_path}.rows[{row_ordinal}]"
                    row_grouped = _group_fields(_parse_wire_message(row_field.value))
                    _record_duplicate_singular_fields(row_grouped, "house_tile_row", row_path, duplicates)
                    row: dict[str, object] = {"sourceOrdinal": row_ordinal}
                    flags = _first_uint(row_grouped, 2)
                    if flags is not None:
                        row["flags"] = flags
                        row_flag_sum += flags
                    tile_documents: list[dict[str, object]] = []
                    for tile_ordinal, tile_field in enumerate(row_grouped.get(1, ()), start=1):
                        assert isinstance(tile_field.value, bytes)
                        tile_documents.append(
                            {
                                "sourceOrdinal": tile_ordinal,
                                **_tile_document(
                                    _parse_wire_message(tile_field.value),
                                    path=f"{row_path}.tiles[{tile_ordinal}]",
                                    missing=missing,
                                    duplicates=duplicates,
                                ),
                            }
                        )
                    total_tile_records += len(tile_documents)
                    if total_tile_records > max_tile_records:
                        raise StaticMapDataReferenceError(
                            f"staticmapdata tile record count exceeds {max_tile_records}"
                        )
                    row["tiles"] = tile_documents
                    rows_document.append(row)
                layout["tiles"] = {"floorData": {"rows": rows_document}}

        row_count = len(rows_document)
        encoded_cell_span = row_count + row_flag_sum
        total_encoded_cell_span += encoded_cell_span
        validation: dict[str, object] = {
            "rowCount": row_count,
            "rowFlagSum": row_flag_sum,
            "encodedCellSpan": encoded_cell_span,
        }
        if {"width", "height", "floors"}.issubset(size):
            width = size["width"]
            height = size["height"]
            floors = size["floors"]
            declared_cell_count = width * height * floors
            total_declared_cells += declared_cell_count
            if total_declared_cells > max_declared_cells:
                raise StaticMapDataReferenceError(
                    f"staticmapdata declared cell count exceeds {max_declared_cells}"
                )
            matches = width > 0 and height > 0 and floors > 0 and encoded_cell_span == declared_cell_count
            validation["declaredCellCount"] = declared_cell_count
            validation["matchesDeclaredDimensions"] = matches
            if not matches:
                reason = "non-positive-dimension" if min(width, height, floors) <= 0 else "encoded-cell-span-mismatch"
                finding: dict[str, object] = {
                    "houseSourceOrdinal": house_ordinal,
                    "width": width,
                    "height": height,
                    "floors": floors,
                    "declaredCellCount": declared_cell_count,
                    "rowCount": row_count,
                    "rowFlagSum": row_flag_sum,
                    "encodedCellSpan": encoded_cell_span,
                    "reason": reason,
                }
                if house_id is not None:
                    finding["houseId"] = house_id
                dimension_mismatches.append(finding)
        layout["validation"] = validation
        house["layout"] = layout
        houses.append(house)

    for house_id, ordinals in sorted(house_id_ordinals.items()):
        if len(ordinals) > 1:
            duplicate_house_ids.append({"houseId": house_id, "sourceOrdinals": ordinals})

    findings: dict[str, object] = {
        "duplicateHouseIds": duplicate_house_ids,
        "missingRequiredFields": missing,
        "duplicateSingularFields": duplicates,
        "dimensionMismatches": dimension_mismatches,
    }
    totals = {
        "houseCount": len(houses),
        "rowCount": total_rows,
        "tileRecordCount": total_tile_records,
        "declaredCellCount": total_declared_cells,
        "encodedCellSpan": total_encoded_cell_span,
    }
    return houses, findings, totals


def build_index(
    *,
    manifest_path: Path,
    source_path: Path,
    input_id: str,
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES,
    max_manifest_bytes: int = DEFAULT_MAX_MANIFEST_BYTES,
    max_houses: int = DEFAULT_MAX_HOUSES,
    max_rows: int = DEFAULT_MAX_ROWS,
    max_tile_records: int = DEFAULT_MAX_TILE_RECORDS,
    max_declared_cells: int = DEFAULT_MAX_DECLARED_CELLS,
) -> tuple[dict[str, object], tuple[Path, Path]]:
    for value, label in (
        (max_source_bytes, "max_source_bytes"),
        (max_decompressed_bytes, "max_decompressed_bytes"),
        (max_manifest_bytes, "max_manifest_bytes"),
        (max_houses, "max_houses"),
        (max_rows, "max_rows"),
        (max_tile_records, "max_tile_records"),
        (max_declared_cells, "max_declared_cells"),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise StaticMapDataReferenceError(f"{label} must be a positive integer")
    if not isinstance(input_id, str) or not input_id:
        raise StaticMapDataReferenceError("input_id must be non-empty")

    manifest, manifest_sha256, manifest_resolved = _load_manifest(
        manifest_path, max_manifest_bytes=max_manifest_bytes
    )
    entry = _manifest_input(manifest, input_id)
    source_data, source_size, source_sha256, source_resolved = _read_stable_file(
        source_path, max_bytes=max_source_bytes, label="source"
    )
    if source_size != entry["sizeBytes"]:
        raise StaticMapDataReferenceError("source size does not match manifest selected input")
    if source_sha256.lower() != str(entry["sha256"]).lower():
        raise StaticMapDataReferenceError("source SHA-256 does not match manifest selected input")
    if os.path.samefile(manifest_resolved, source_resolved):
        raise StaticMapDataReferenceError("manifest and source must be distinct files")

    decoded, encoding, top_fields = _decode_staticmapdata_bytes(
        source_data, max_decompressed_bytes=max_decompressed_bytes
    )
    houses, findings, totals = _build_houses(
        top_fields,
        max_houses=max_houses,
        max_rows=max_rows,
        max_tile_records=max_tile_records,
        max_declared_cells=max_declared_cells,
    )
    payload: dict[str, object] = {
        "format": INDEX_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "source": {
            "manifestFormat": MANIFEST_FORMAT,
            "manifestSha256": manifest_sha256,
            "referenceId": manifest["referenceId"],
            "inputId": input_id,
            "manifestPath": entry["path"],
            "sizeBytes": source_size,
            "sha256": source_sha256,
            "encoding": encoding,
            "decodedSizeBytes": len(decoded),
        },
        "objectIdNamespace": {
            "name": OBJECT_ID_NAMESPACE,
            "resolution": "unresolved",
            "otbmItemIdEquivalent": False,
        },
        "houses": houses,
        "findings": findings,
        "summary": {
            **totals,
            "duplicateHouseIdCount": len(findings["duplicateHouseIds"]),
            "missingRequiredFieldCount": len(findings["missingRequiredFields"]),
            "duplicateSingularFieldCount": len(findings["duplicateSingularFields"]),
            "dimensionMismatchCount": len(findings["dimensionMismatches"]),
        },
        "policy": {
            "gameplayConclusions": False,
            "otbmParsing": False,
            "otbmWriting": False,
            "objectIdMapping": "unresolved",
            "rowFlagSemantics": "unresolved-beyond-encoded-cell-span",
            "maxSourceBytes": max_source_bytes,
            "maxDecompressedBytes": max_decompressed_bytes,
            "maxHouses": max_houses,
            "maxRows": max_rows,
            "maxTileRecords": max_tile_records,
            "maxDeclaredCells": max_declared_cells,
        },
    }
    return payload, (manifest_resolved, source_resolved)


def deterministic_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_index(
    output: Path,
    payload: Mapping[str, object],
    *,
    protected_inputs: Iterable[Path],
    overwrite: bool = False,
) -> None:
    target_path = output.expanduser()
    if target_path.is_symlink():
        raise StaticMapDataReferenceError(f"output must not be a symlink: {output}")
    target = target_path.resolve()
    protected = tuple(path.resolve() for path in protected_inputs)
    if any(target == source or (target.exists() and os.path.samefile(target, source)) for source in protected):
        raise StaticMapDataReferenceError("output collides with a protected input")
    if target.exists() and not target.is_file():
        raise StaticMapDataReferenceError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise StaticMapDataReferenceError(f"output already exists: {target}; pass --overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = deterministic_json(payload)
    if not overwrite:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        return
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
