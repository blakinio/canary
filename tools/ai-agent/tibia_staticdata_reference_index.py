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

INDEX_FORMAT = "canary-tibia-staticdata-index-v1"
MANIFEST_FORMAT = "canary-tibia-client-reference-manifest-v1"
SCHEMA_VERSION = 1
DEFAULT_MAX_SOURCE_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_DECOMPRESSED_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_MANIFEST_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_RECORDS = 2_000_000
MAX_NESTING_DEPTH = 8
XZ_MAGIC = b"\xfd7zXZ\x00"
_SHA256_HEX_LEN = 64


class StaticDataReferenceError(RuntimeError):
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


@dataclass(frozen=True)
class SchemaSpec:
    family: str
    top_categories: Mapping[int, tuple[str, str]]


FIELD_SPECS: dict[str, dict[int, FieldSpec]] = {
    "outfit_colors": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(0, "uint"),
        3: FieldSpec(0, "uint"),
        4: FieldSpec(0, "uint"),
    },
    "outfit": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "message", "outfit_colors"),
        3: FieldSpec(0, "uint"),
        4: FieldSpec(0, "uint"),
    },
    "coordinate": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(0, "uint"),
        3: FieldSpec(0, "uint"),
    },
    "creature": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
        3: FieldSpec(2, "message", "outfit"),
        4: FieldSpec(0, "uint"),
        5: FieldSpec(0, "uint"),
        6: FieldSpec(0, "bool"),
        7: FieldSpec(0, "bool"),
    },
    "monster": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
        3: FieldSpec(2, "message", "outfit"),
        4: FieldSpec(0, "uint"),
        5: FieldSpec(0, "uint"),
        6: FieldSpec(0, "bool"),
        7: FieldSpec(0, "bool"),
    },
    "title": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
        3: FieldSpec(2, "string"),
        4: FieldSpec(0, "uint"),
    },
    "achievement": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
        3: FieldSpec(2, "string"),
        4: FieldSpec(0, "uint"),
    },
    "monster_class": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
    },
    "house_legacy": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
        3: FieldSpec(2, "string"),
        4: FieldSpec(0, "uint"),
        5: FieldSpec(0, "uint"),
        6: FieldSpec(2, "message", "coordinate"),
        7: FieldSpec(0, "uint"),
        8: FieldSpec(0, "bool"),
        9: FieldSpec(2, "string"),
        10: FieldSpec(0, "bool"),
    },
    "house_newer": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
        3: FieldSpec(2, "string"),
        4: FieldSpec(0, "uint"),
        5: FieldSpec(0, "uint"),
        6: FieldSpec(2, "message", "coordinate"),
        7: FieldSpec(0, "uint"),
        8: FieldSpec(0, "bool"),
        9: FieldSpec(2, "string"),
        10: FieldSpec(0, "bool"),
    },
    "boss": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
        3: FieldSpec(2, "message", "outfit"),
        4: FieldSpec(0, "bool"),
    },
    "quest": {
        1: FieldSpec(0, "uint"),
        2: FieldSpec(2, "string"),
    },
}

LEGACY_SCHEMA = SchemaSpec(
    family="legacy",
    top_categories={
        1: ("creatures", "creature"),
        2: ("titles", "title"),
        3: ("houses", "house_legacy"),
        4: ("bosses", "boss"),
        5: ("quests", "quest"),
    },
)
NEWER_SCHEMA = SchemaSpec(
    family="newer",
    top_categories={
        1: ("monsters", "monster"),
        2: ("monsterClasses", "monster_class"),
        3: ("achievements", "achievement"),
        4: ("houses", "house_newer"),
        5: ("bosses", "boss"),
        6: ("quests", "quest"),
    },
)


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise StaticDataReferenceError("truncated protobuf varint")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            if shift == 63 and byte > 1:
                raise StaticDataReferenceError("protobuf varint exceeds 64 bits")
            return value, offset
    raise StaticDataReferenceError("protobuf varint exceeds 10 bytes")


def _parse_wire_message(data: bytes) -> list[WireField]:
    fields: list[WireField] = []
    offset = 0
    while offset < len(data):
        key, offset = _read_varint(data, offset)
        number = key >> 3
        wire_type = key & 0x07
        if number <= 0:
            raise StaticDataReferenceError("protobuf field number must be positive")
        if wire_type == 0:
            value, offset = _read_varint(data, offset)
            fields.append(WireField(number, wire_type, value))
        elif wire_type == 1:
            end = offset + 8
            if end > len(data):
                raise StaticDataReferenceError("truncated protobuf fixed64 field")
            fields.append(WireField(number, wire_type, data[offset:end]))
            offset = end
        elif wire_type == 2:
            length, offset = _read_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise StaticDataReferenceError("truncated protobuf length-delimited field")
            fields.append(WireField(number, wire_type, data[offset:end]))
            offset = end
        elif wire_type == 5:
            end = offset + 4
            if end > len(data):
                raise StaticDataReferenceError("truncated protobuf fixed32 field")
            fields.append(WireField(number, wire_type, data[offset:end]))
            offset = end
        else:
            raise StaticDataReferenceError(f"unsupported protobuf wire type: {wire_type}")
    return fields


def _decode_utf8(value: bytes, label: str) -> str:
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise StaticDataReferenceError(f"{label} is not valid UTF-8") from exc


def _validate_message(fields: Sequence[WireField], message_type: str, *, depth: int = 0) -> None:
    if depth > MAX_NESTING_DEPTH:
        raise StaticDataReferenceError("protobuf nesting limit exceeded")
    specs = FIELD_SPECS[message_type]
    for field in fields:
        spec = specs.get(field.number)
        if spec is None:
            raise StaticDataReferenceError(f"unsupported field {field.number} in {message_type}")
        if field.wire_type != spec.wire_type:
            raise StaticDataReferenceError(
                f"wrong wire type for {message_type}.{field.number}: expected {spec.wire_type}, got {field.wire_type}"
            )
        if spec.kind == "string":
            assert isinstance(field.value, bytes)
            _decode_utf8(field.value, f"{message_type}.{field.number}")
        elif spec.kind == "bool":
            assert isinstance(field.value, int)
            if field.value not in (0, 1):
                raise StaticDataReferenceError(f"invalid bool value in {message_type}.{field.number}")
        elif spec.kind == "message":
            assert isinstance(field.value, bytes)
            nested = _parse_wire_message(field.value)
            _validate_message(nested, spec.message or "", depth=depth + 1)


def _candidate_valid(top_fields: Sequence[WireField], schema: SchemaSpec) -> bool:
    try:
        for field in top_fields:
            category = schema.top_categories.get(field.number)
            if category is None or field.wire_type != 2 or not isinstance(field.value, bytes):
                return False
            nested = _parse_wire_message(field.value)
            _validate_message(nested, category[1])
        return bool(top_fields)
    except StaticDataReferenceError:
        return False


def _field_numbers(message: bytes) -> set[int]:
    return {field.number for field in _parse_wire_message(message)}


def _schema_evidence(top_fields: Sequence[WireField]) -> tuple[set[str], list[str]]:
    evidence: set[str] = set()
    reasons: list[str] = []
    for field in top_fields:
        if field.wire_type != 2 or not isinstance(field.value, bytes):
            continue
        nested_numbers = _field_numbers(field.value)
        if field.number == 6:
            evidence.add("newer")
            reasons.append("top-level field 6 is newer-schema quests")
        elif field.number == 2 and nested_numbers.intersection({3, 4}):
            evidence.add("legacy")
            reasons.append("top-level field 2 contains title-only fields 3/4")
        elif field.number == 3 and nested_numbers.intersection({5, 6, 7, 8, 9, 10}):
            evidence.add("legacy")
            reasons.append("top-level field 3 contains legacy-house fields 5..10")
        elif field.number == 4 and nested_numbers.intersection({5, 6, 7, 8, 9, 10}):
            evidence.add("newer")
            reasons.append("top-level field 4 contains newer-house fields 5..10")
        elif field.number == 5 and nested_numbers.intersection({3, 4}):
            evidence.add("newer")
            reasons.append("top-level field 5 contains newer-boss fields 3/4")
    return evidence, sorted(set(reasons))


def select_schema(data: bytes) -> tuple[SchemaSpec, list[WireField], list[str]]:
    top_fields = _parse_wire_message(data)
    if not top_fields:
        raise StaticDataReferenceError("staticdata protobuf document is empty")
    unsupported_top = sorted({field.number for field in top_fields if field.number not in {1, 2, 3, 4, 5, 6}})
    if unsupported_top:
        raise StaticDataReferenceError(f"unsupported StaticData top-level fields: {unsupported_top}")
    legacy_valid = _candidate_valid(top_fields, LEGACY_SCHEMA)
    newer_valid = _candidate_valid(top_fields, NEWER_SCHEMA)
    evidence, reasons = _schema_evidence(top_fields)
    if evidence == {"legacy", "newer"}:
        raise StaticDataReferenceError("conflicting StaticData schema evidence")
    if evidence == {"legacy"}:
        if not legacy_valid:
            raise StaticDataReferenceError("legacy StaticData discriminator conflicts with record structure")
        return LEGACY_SCHEMA, top_fields, reasons
    if evidence == {"newer"}:
        if not newer_valid:
            raise StaticDataReferenceError("newer StaticData discriminator conflicts with record structure")
        return NEWER_SCHEMA, top_fields, reasons
    if legacy_valid and not newer_valid:
        return LEGACY_SCHEMA, top_fields, ["only legacy schema validates structurally"]
    if newer_valid and not legacy_valid:
        return NEWER_SCHEMA, top_fields, ["only newer schema validates structurally"]
    if legacy_valid and newer_valid:
        raise StaticDataReferenceError("ambiguous StaticData schema: both known schemas validate without discriminator evidence")
    raise StaticDataReferenceError("unsupported or malformed StaticData schema")


def _bounded_decompress(data: bytes, *, fmt: int, max_bytes: int, label: str) -> bytes:
    try:
        decoder = lzma.LZMADecompressor(format=fmt)
        output = decoder.decompress(data, max_length=max_bytes + 1)
    except lzma.LZMAError as exc:
        raise StaticDataReferenceError(f"{label} decompression failed") from exc
    if len(output) > max_bytes or not decoder.eof:
        if len(output) > max_bytes or not decoder.needs_input:
            raise StaticDataReferenceError(f"{label} decompressed data exceeds {max_bytes} bytes")
        raise StaticDataReferenceError(f"{label} stream is truncated or incomplete")
    if decoder.unused_data:
        raise StaticDataReferenceError(f"{label} stream has trailing or concatenated data")
    return output


def _decode_staticdata_bytes(
    data: bytes, *, max_decompressed_bytes: int
) -> tuple[bytes, str, SchemaSpec, list[WireField], list[str]]:
    if data.startswith(XZ_MAGIC):
        decoded = _bounded_decompress(data, fmt=lzma.FORMAT_XZ, max_bytes=max_decompressed_bytes, label="XZ")
        schema, fields, reasons = select_schema(decoded)
        return decoded, "xz", schema, fields, reasons

    raw_error: StaticDataReferenceError | None = None
    try:
        schema, fields, reasons = select_schema(data)
        return data, "raw", schema, fields, reasons
    except StaticDataReferenceError as exc:
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
            schema, fields, reasons = select_schema(decoded)
            return decoded, "lzma", schema, fields, reasons
        except StaticDataReferenceError:
            continue
    assert raw_error is not None
    raise raw_error


def _stat_identity(stat: os.stat_result) -> tuple[int, int, int, int]:
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)


def _read_stable_file(path: Path, *, max_bytes: int, label: str) -> tuple[bytes, int, str, Path]:
    target = path.expanduser()
    if target.is_symlink():
        raise StaticDataReferenceError(f"{label} must not be a symlink: {path}")
    try:
        resolved = target.resolve(strict=True)
    except OSError as exc:
        raise StaticDataReferenceError(f"{label} does not exist: {path}") from exc
    if not resolved.is_file():
        raise StaticDataReferenceError(f"{label} must be a regular file: {path}")
    before = resolved.stat()
    if before.st_size > max_bytes:
        raise StaticDataReferenceError(f"{label} exceeds {max_bytes} bytes")
    try:
        with resolved.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if _stat_identity(before) != _stat_identity(opened):
                raise StaticDataReferenceError(f"{label} changed before read")
            data = stream.read(max_bytes + 1)
            after_open = os.fstat(stream.fileno())
    except OSError as exc:
        raise StaticDataReferenceError(f"cannot read {label}: {exc}") from exc
    after = resolved.stat()
    if len(data) > max_bytes:
        raise StaticDataReferenceError(f"{label} exceeds {max_bytes} bytes")
    identities = {_stat_identity(before), _stat_identity(opened), _stat_identity(after_open), _stat_identity(after)}
    if len(identities) != 1 or len(data) != after.st_size:
        raise StaticDataReferenceError(f"{label} changed while reading")
    return data, len(data), hashlib.sha256(data).hexdigest(), resolved


def _load_manifest(path: Path, *, max_manifest_bytes: int) -> tuple[dict[str, object], str, Path]:
    data, _, sha256, resolved = _read_stable_file(path, max_bytes=max_manifest_bytes, label="manifest")
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StaticDataReferenceError("manifest must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict) or payload.get("format") != MANIFEST_FORMAT:
        raise StaticDataReferenceError(f"manifest format must be {MANIFEST_FORMAT}")
    if not isinstance(payload.get("referenceId"), str) or not payload["referenceId"]:
        raise StaticDataReferenceError("manifest referenceId must be non-empty")
    inputs = payload.get("selectedInputs")
    if not isinstance(inputs, list):
        raise StaticDataReferenceError("manifest selectedInputs must be an array")
    return payload, sha256, resolved


def _manifest_input(manifest: Mapping[str, object], input_id: str) -> Mapping[str, object]:
    entries = [entry for entry in manifest["selectedInputs"] if isinstance(entry, dict) and entry.get("id") == input_id]
    if len(entries) != 1:
        raise StaticDataReferenceError(f"manifest must contain exactly one selected input with id {input_id}")
    entry = entries[0]
    if not isinstance(entry.get("path"), str) or not entry["path"]:
        raise StaticDataReferenceError("manifest selected input path must be non-empty")
    size = entry.get("sizeBytes")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise StaticDataReferenceError("manifest selected input sizeBytes must be a non-negative integer")
    digest = entry.get("sha256")
    if not isinstance(digest, str) or len(digest) != _SHA256_HEX_LEN:
        raise StaticDataReferenceError("manifest selected input sha256 must be 64 hexadecimal characters")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise StaticDataReferenceError("manifest selected input sha256 must be hexadecimal") from exc
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


def _first_string(grouped: Mapping[int, Sequence[WireField]], number: int, label: str) -> str | None:
    values = grouped.get(number, ())
    if not values:
        return None
    value = values[0].value
    assert isinstance(value, bytes)
    return _decode_utf8(value, label)


def _first_message(grouped: Mapping[int, Sequence[WireField]], number: int) -> list[WireField] | None:
    values = grouped.get(number, ())
    if not values:
        return None
    value = values[0].value
    assert isinstance(value, bytes)
    return _parse_wire_message(value)


def _outfit_document(fields: Sequence[WireField]) -> dict[str, object]:
    grouped = _group_fields(fields)
    document: dict[str, object] = {}
    for number, key in ((1, "looktype"), (3, "addons"), (4, "mount")):
        value = _first_uint(grouped, number)
        if value is not None:
            document[key] = value
    colors = _first_message(grouped, 2)
    if colors is not None:
        color_grouped = _group_fields(colors)
        color_document: dict[str, int] = {}
        for number, key in ((1, "head"), (2, "body"), (3, "legs"), (4, "feet")):
            value = _first_uint(color_grouped, number)
            if value is not None:
                color_document[key] = value
        document["colors"] = color_document
    return document


def _coordinate_document(fields: Sequence[WireField]) -> dict[str, int]:
    grouped = _group_fields(fields)
    document: dict[str, int] = {}
    for number, key in ((1, "x"), (2, "y"), (3, "z")):
        value = _first_uint(grouped, number)
        if value is not None:
            document[key] = value
    return document


def _record_document(message_type: str, fields: Sequence[WireField], ordinal: int) -> dict[str, object]:
    grouped = _group_fields(fields)
    record: dict[str, object] = {"sourceOrdinal": ordinal}
    record_id = _first_uint(grouped, 1)
    name = _first_string(grouped, 2, f"{message_type}.name")
    if record_id is not None:
        record["id"] = record_id
    if name is not None:
        record["name"] = name

    if message_type in {"creature", "monster"}:
        outfit = _first_message(grouped, 3)
        if outfit is not None:
            record["outfit"] = _outfit_document(outfit)
        for number, key in ((4, "difficulty"), (5, "occurrence")):
            value = _first_uint(grouped, number)
            if value is not None:
                record[key] = value
        for number, key in ((6, "isNpc"), (7, "isHostile")):
            value = _first_bool(grouped, number)
            if value is not None:
                record[key] = value
    elif message_type in {"title", "achievement"}:
        description = _first_string(grouped, 3, f"{message_type}.description")
        grade = _first_uint(grouped, 4)
        if description is not None:
            record["description"] = description
        if grade is not None:
            record["grade"] = grade
    elif message_type in {"house_legacy", "house_newer"}:
        description = _first_string(grouped, 3, f"{message_type}.description")
        rent = _first_uint(grouped, 4)
        position = _first_message(grouped, 6)
        if description is not None:
            record["description"] = description
        if rent is not None:
            record["rent"] = rent
        if message_type == "house_legacy":
            size = _first_uint(grouped, 5)
            beds = _first_uint(grouped, 7)
        else:
            beds = _first_uint(grouped, 5)
            size = _first_uint(grouped, 7)
        if beds is not None:
            record["beds"] = beds
        if size is not None:
            record["size"] = size
        if position is not None:
            record["position"] = _coordinate_document(position)
        guildhall = _first_bool(grouped, 8)
        town = _first_string(grouped, 9, f"{message_type}.town")
        premium = _first_bool(grouped, 10)
        if guildhall is not None:
            record["guildhall"] = guildhall
        if town is not None:
            record["town"] = town
        if premium is not None:
            record["isPremium"] = premium
    elif message_type == "boss":
        outfit = _first_message(grouped, 3)
        if outfit is not None:
            record["outfit"] = _outfit_document(outfit)
        archfoe = _first_bool(grouped, 4)
        if archfoe is not None:
            record["isArchfoe"] = archfoe
    return record


def _record_sort_key(record: Mapping[str, object]) -> tuple[bool, int, str, int]:
    record_id = record.get("id")
    return (
        record_id is None,
        int(record_id) if isinstance(record_id, int) else 0,
        str(record.get("name", "")),
        int(record["sourceOrdinal"]),
    )


def _build_categories(
    top_fields: Sequence[WireField],
    schema: SchemaSpec,
    *,
    max_records: int,
) -> tuple[dict[str, object], dict[str, object], int]:
    by_top: dict[int, list[WireField]] = defaultdict(list)
    for field in top_fields:
        by_top[field.number].append(field)
    total_records = len(top_fields)
    if total_records > max_records:
        raise StaticDataReferenceError(f"staticdata record count exceeds {max_records}")

    categories: dict[str, object] = {}
    duplicate_ids: list[dict[str, object]] = []
    missing_fields: list[dict[str, object]] = []
    duplicate_fields: list[dict[str, object]] = []

    for top_number, (category_name, message_type) in schema.top_categories.items():
        records: list[dict[str, object]] = []
        id_ordinals: dict[int, list[int]] = defaultdict(list)
        for ordinal, field in enumerate(by_top.get(top_number, ()), start=1):
            assert isinstance(field.value, bytes)
            nested = _parse_wire_message(field.value)
            grouped = _group_fields(nested)
            for field_number, occurrences in sorted(grouped.items()):
                if len(occurrences) > 1:
                    duplicate_fields.append(
                        {
                            "category": category_name,
                            "fieldNumber": field_number,
                            "sourceOrdinal": ordinal,
                            "occurrences": len(occurrences),
                        }
                    )
            record = _record_document(message_type, nested, ordinal)
            if "id" not in record:
                missing_fields.append({"category": category_name, "field": "id", "sourceOrdinal": ordinal})
            else:
                id_ordinals[int(record["id"])].append(ordinal)
            if "name" not in record or record.get("name") == "":
                missing_fields.append({"category": category_name, "field": "name", "sourceOrdinal": ordinal})
            records.append(record)
        for duplicate_id, ordinals in sorted(id_ordinals.items()):
            if len(ordinals) > 1:
                duplicate_ids.append(
                    {
                        "category": category_name,
                        "id": duplicate_id,
                        "sourceOrdinals": ordinals,
                    }
                )
        records.sort(key=_record_sort_key)
        categories[category_name] = {
            "sourceCategory": category_name,
            "sourceSchema": schema.family,
            "count": len(records),
            "records": records,
        }

    findings = {
        "duplicateIds": duplicate_ids,
        "missingRequiredFields": missing_fields,
        "duplicateSingularFields": duplicate_fields,
    }
    return categories, findings, total_records


def build_index(
    *,
    manifest_path: Path,
    source_path: Path,
    input_id: str,
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES,
    max_manifest_bytes: int = DEFAULT_MAX_MANIFEST_BYTES,
    max_records: int = DEFAULT_MAX_RECORDS,
) -> tuple[dict[str, object], tuple[Path, Path]]:
    for value, label in (
        (max_source_bytes, "max_source_bytes"),
        (max_decompressed_bytes, "max_decompressed_bytes"),
        (max_manifest_bytes, "max_manifest_bytes"),
        (max_records, "max_records"),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise StaticDataReferenceError(f"{label} must be a positive integer")
    if not isinstance(input_id, str) or not input_id:
        raise StaticDataReferenceError("input_id must be non-empty")

    manifest, manifest_sha256, manifest_resolved = _load_manifest(
        manifest_path, max_manifest_bytes=max_manifest_bytes
    )
    entry = _manifest_input(manifest, input_id)
    source_data, source_size, source_sha256, source_resolved = _read_stable_file(
        source_path, max_bytes=max_source_bytes, label="source"
    )
    if source_size != entry["sizeBytes"]:
        raise StaticDataReferenceError("source size does not match manifest selected input")
    if source_sha256.lower() != str(entry["sha256"]).lower():
        raise StaticDataReferenceError("source SHA-256 does not match manifest selected input")
    if os.path.samefile(manifest_resolved, source_resolved):
        raise StaticDataReferenceError("manifest and source must be distinct files")

    decoded, encoding, schema, top_fields, schema_reasons = _decode_staticdata_bytes(
        source_data, max_decompressed_bytes=max_decompressed_bytes
    )
    categories, findings, total_records = _build_categories(top_fields, schema, max_records=max_records)
    category_counts = {name: int(document["count"]) for name, document in categories.items()}
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
            "schemaFamily": schema.family,
            "schemaEvidence": schema_reasons,
        },
        "categories": categories,
        "findings": findings,
        "summary": {
            "categoryCounts": category_counts,
            "totalRecords": total_records,
            "duplicateIdCount": len(findings["duplicateIds"]),
            "missingRequiredFieldCount": len(findings["missingRequiredFields"]),
            "duplicateSingularFieldCount": len(findings["duplicateSingularFields"]),
        },
        "policy": {
            "gameplayConclusions": False,
            "questInventoryOnly": True,
            "schemaAmbiguityFailsClosed": True,
            "maxSourceBytes": max_source_bytes,
            "maxDecompressedBytes": max_decompressed_bytes,
            "maxRecords": max_records,
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
        raise StaticDataReferenceError(f"output must not be a symlink: {output}")
    target = target_path.resolve()
    protected = tuple(path.resolve() for path in protected_inputs)
    if any(target == source or (target.exists() and os.path.samefile(target, source)) for source in protected):
        raise StaticDataReferenceError("output collides with a protected input")
    if target.exists() and not target.is_file():
        raise StaticDataReferenceError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise StaticDataReferenceError(f"output already exists: {target}; pass --overwrite")
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
