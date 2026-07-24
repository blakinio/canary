from __future__ import annotations

import hashlib
import json
import lzma
import math
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

INDEX_FORMAT = "canary-tibia-proficiency-index-v1"
MANIFEST_FORMAT = "canary-tibia-client-reference-manifest-v1"
PROFICIENCY_ID_NAMESPACE = "client-reference.proficiency-id"
SCHEMA_VERSION = 1
DEFAULT_MAX_SOURCE_BYTES = 16 * 1024 * 1024
DEFAULT_MAX_DECOMPRESSED_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_MANIFEST_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_PROFICIENCIES = 100_000
DEFAULT_MAX_LEVELS = 1_000_000
DEFAULT_MAX_PERKS = 5_000_000
XZ_MAGIC = b"\xfd7zXZ\x00"
_SHA256_HEX_LEN = 64
_UINT32_MAX = (1 << 32) - 1
_UINT64_MAX = (1 << 64) - 1

_ENTRY_FIELDS = frozenset({"Levels", "Name", "ProficiencyId", "Version"})
_LEVEL_FIELDS = frozenset({"Perks", "XpRequired"})
_PERK_FIELDS = frozenset(
    {
        "AugmentType",
        "BestiaryId",
        "BestiaryName",
        "DamageType",
        "ElementId",
        "Range",
        "SkillId",
        "SpellId",
        "Type",
        "Value",
    }
)
_PERK_INTEGER_FIELDS = (
    ("AugmentType", "augmentType"),
    ("BestiaryId", "bestiaryId"),
    ("DamageType", "damageType"),
    ("ElementId", "elementId"),
    ("Range", "range"),
    ("SkillId", "skillId"),
    ("SpellId", "spellId"),
)


class ProficiencyReferenceError(RuntimeError):
    pass


def _reject_json_constant(value: str) -> object:
    raise ProficiencyReferenceError(f"non-finite JSON number is not supported: {value}")


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ProficiencyReferenceError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _strict_json_loads(text: str, *, label: str) -> object:
    try:
        return json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except ProficiencyReferenceError:
        raise
    except json.JSONDecodeError as exc:
        raise ProficiencyReferenceError(f"{label} must be valid JSON: {exc.msg}") from exc


def _stat_identity(stat: os.stat_result) -> tuple[int, int, int, int]:
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)


def _read_stable_file(path: Path, *, max_bytes: int, label: str) -> tuple[bytes, int, str, Path]:
    target = path.expanduser()
    if target.is_symlink():
        raise ProficiencyReferenceError(f"{label} must not be a symlink: {path}")
    try:
        resolved = target.resolve(strict=True)
    except OSError as exc:
        raise ProficiencyReferenceError(f"{label} does not exist: {path}") from exc
    if not resolved.is_file():
        raise ProficiencyReferenceError(f"{label} must be a regular file: {path}")
    before = resolved.stat()
    if before.st_size > max_bytes:
        raise ProficiencyReferenceError(f"{label} exceeds {max_bytes} bytes")
    try:
        with resolved.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            if _stat_identity(before) != _stat_identity(opened):
                raise ProficiencyReferenceError(f"{label} changed before read")
            data = stream.read(max_bytes + 1)
            after_open = os.fstat(stream.fileno())
    except OSError as exc:
        raise ProficiencyReferenceError(f"cannot read {label}: {exc}") from exc
    after = resolved.stat()
    if len(data) > max_bytes:
        raise ProficiencyReferenceError(f"{label} exceeds {max_bytes} bytes")
    identities = {_stat_identity(before), _stat_identity(opened), _stat_identity(after_open), _stat_identity(after)}
    if len(identities) != 1 or len(data) != after.st_size:
        raise ProficiencyReferenceError(f"{label} changed while reading")
    return data, len(data), hashlib.sha256(data).hexdigest(), resolved


def _bounded_decompress(data: bytes, *, fmt: int, max_bytes: int, label: str) -> bytes:
    try:
        decoder = lzma.LZMADecompressor(format=fmt)
        output = decoder.decompress(data, max_length=max_bytes + 1)
    except lzma.LZMAError as exc:
        raise ProficiencyReferenceError(f"{label} decompression failed") from exc
    if len(output) > max_bytes or not decoder.eof:
        if len(output) > max_bytes or not decoder.needs_input:
            raise ProficiencyReferenceError(f"{label} decompressed data exceeds {max_bytes} bytes")
        raise ProficiencyReferenceError(f"{label} stream is truncated or incomplete")
    if decoder.unused_data:
        raise ProficiencyReferenceError(f"{label} stream has trailing or concatenated data")
    return output


def _decode_source_bytes(data: bytes, *, max_decompressed_bytes: int) -> tuple[bytes, str]:
    if data.startswith(XZ_MAGIC):
        return (
            _bounded_decompress(data, fmt=lzma.FORMAT_XZ, max_bytes=max_decompressed_bytes, label="XZ"),
            "xz",
        )

    try:
        data.decode("utf-8")
        return data, "raw"
    except UnicodeDecodeError:
        pass

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
            decoded.decode("utf-8")
            return decoded, "lzma"
        except (ProficiencyReferenceError, UnicodeDecodeError):
            continue
    raise ProficiencyReferenceError("source must be UTF-8 JSON or a supported bounded XZ/LZMA stream")


def _load_manifest(path: Path, *, max_manifest_bytes: int) -> tuple[dict[str, object], str, Path]:
    data, _, sha256, resolved = _read_stable_file(path, max_bytes=max_manifest_bytes, label="manifest")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProficiencyReferenceError("manifest must be valid UTF-8 JSON") from exc
    payload = _strict_json_loads(text, label="manifest")
    if not isinstance(payload, dict) or payload.get("format") != MANIFEST_FORMAT:
        raise ProficiencyReferenceError(f"manifest format must be {MANIFEST_FORMAT}")
    if not isinstance(payload.get("referenceId"), str) or not payload["referenceId"]:
        raise ProficiencyReferenceError("manifest referenceId must be non-empty")
    if not isinstance(payload.get("selectedInputs"), list):
        raise ProficiencyReferenceError("manifest selectedInputs must be an array")
    return payload, sha256, resolved


def _manifest_input(manifest: Mapping[str, object], input_id: str) -> Mapping[str, object]:
    inputs = manifest["selectedInputs"]
    assert isinstance(inputs, list)
    entries = [entry for entry in inputs if isinstance(entry, dict) and entry.get("id") == input_id]
    if len(entries) != 1:
        raise ProficiencyReferenceError(f"manifest must contain exactly one selected input with id {input_id}")
    entry = entries[0]
    if not isinstance(entry.get("path"), str) or not entry["path"]:
        raise ProficiencyReferenceError("manifest selected input path must be non-empty")
    size = entry.get("sizeBytes")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        raise ProficiencyReferenceError("manifest selected input sizeBytes must be a non-negative integer")
    digest = entry.get("sha256")
    if not isinstance(digest, str) or len(digest) != _SHA256_HEX_LEN:
        raise ProficiencyReferenceError("manifest selected input sha256 must be 64 hexadecimal characters")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise ProficiencyReferenceError("manifest selected input sha256 must be hexadecimal") from exc
    return entry


def _require_object(value: object, *, path: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ProficiencyReferenceError(f"{path} must be an object")
    return value


def _require_array(value: object, *, path: str) -> list[object]:
    if not isinstance(value, list):
        raise ProficiencyReferenceError(f"{path} must be an array")
    return value


def _reject_unknown_fields(value: Mapping[str, object], allowed: frozenset[str], *, path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ProficiencyReferenceError(f"{path} contains unsupported field(s): {', '.join(unknown)}")


def _require_uint(value: object, *, path: str, maximum: int = _UINT32_MAX, positive: bool = False) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ProficiencyReferenceError(f"{path} must be an integer")
    minimum = 1 if positive else 0
    if value < minimum or value > maximum:
        raise ProficiencyReferenceError(f"{path} must be between {minimum} and {maximum}")
    return value


def _require_text(value: object, *, path: str, non_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise ProficiencyReferenceError(f"{path} must be a string")
    if non_empty and not value:
        raise ProficiencyReferenceError(f"{path} must be non-empty")
    return value


def _require_finite_number(value: object, *, path: str) -> int | float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ProficiencyReferenceError(f"{path} must be a number")
    try:
        finite_value = float(value)
    except OverflowError as exc:
        raise ProficiencyReferenceError(f"{path} must fit a finite double") from exc
    if not math.isfinite(finite_value):
        raise ProficiencyReferenceError(f"{path} must be finite")
    return value


def _parse_perk(value: object, *, path: str, source_ordinal: int) -> dict[str, object]:
    perk = _require_object(value, path=path)
    _reject_unknown_fields(perk, _PERK_FIELDS, path=path)
    if "Type" not in perk or "Value" not in perk:
        missing = [field for field in ("Type", "Value") if field not in perk]
        raise ProficiencyReferenceError(f"{path} is missing required field(s): {', '.join(missing)}")
    output: dict[str, object] = {
        "sourceOrdinal": source_ordinal,
        "type": _require_uint(perk["Type"], path=f"{path}.Type"),
        "value": _require_finite_number(perk["Value"], path=f"{path}.Value"),
    }
    for source_name, output_name in _PERK_INTEGER_FIELDS:
        if source_name in perk:
            output[output_name] = _require_uint(perk[source_name], path=f"{path}.{source_name}")
    if "BestiaryName" in perk:
        output["bestiaryName"] = _require_text(
            perk["BestiaryName"], path=f"{path}.BestiaryName", non_empty=False
        )
    return output


def _parse_proficiencies(
    payload: object,
    *,
    max_proficiencies: int,
    max_levels: int,
    max_perks: int,
) -> tuple[list[dict[str, object]], dict[str, object], dict[str, int]]:
    entries = _require_array(payload, path="source")
    if len(entries) > max_proficiencies:
        raise ProficiencyReferenceError(f"proficiency count exceeds {max_proficiencies}")

    proficiencies: list[dict[str, object]] = []
    id_ordinals: dict[int, list[int]] = defaultdict(list)
    name_ordinals: dict[str, list[int]] = defaultdict(list)
    total_levels = 0
    total_perks = 0
    xp_requirement_count = 0

    for proficiency_ordinal, raw_entry in enumerate(entries, start=1):
        path = f"proficiencies[{proficiency_ordinal}]"
        entry = _require_object(raw_entry, path=path)
        _reject_unknown_fields(entry, _ENTRY_FIELDS, path=path)
        missing = [field for field in ("Levels", "Name", "ProficiencyId") if field not in entry]
        if missing:
            raise ProficiencyReferenceError(f"{path} is missing required field(s): {', '.join(missing)}")

        proficiency_id = _require_uint(entry["ProficiencyId"], path=f"{path}.ProficiencyId", positive=True)
        name = _require_text(entry["Name"], path=f"{path}.Name")
        levels = _require_array(entry["Levels"], path=f"{path}.Levels")
        total_levels += len(levels)
        if total_levels > max_levels:
            raise ProficiencyReferenceError(f"level count exceeds {max_levels}")

        output_entry: dict[str, object] = {
            "sourceOrdinal": proficiency_ordinal,
            "proficiencyId": proficiency_id,
            "name": name,
            "levels": [],
        }
        if "Version" in entry:
            output_entry["version"] = _require_uint(entry["Version"], path=f"{path}.Version")

        output_levels: list[dict[str, object]] = []
        for level_ordinal, raw_level in enumerate(levels, start=1):
            level_path = f"{path}.Levels[{level_ordinal}]"
            level = _require_object(raw_level, path=level_path)
            _reject_unknown_fields(level, _LEVEL_FIELDS, path=level_path)
            if "Perks" not in level:
                raise ProficiencyReferenceError(f"{level_path} is missing required field: Perks")
            perks = _require_array(level["Perks"], path=f"{level_path}.Perks")
            total_perks += len(perks)
            if total_perks > max_perks:
                raise ProficiencyReferenceError(f"perk count exceeds {max_perks}")
            output_level: dict[str, object] = {
                "sourceOrdinal": level_ordinal,
                "perks": [
                    _parse_perk(
                        raw_perk,
                        path=f"{level_path}.Perks[{perk_ordinal}]",
                        source_ordinal=perk_ordinal,
                    )
                    for perk_ordinal, raw_perk in enumerate(perks, start=1)
                ],
            }
            if "XpRequired" in level:
                output_level["xpRequired"] = _require_uint(
                    level["XpRequired"],
                    path=f"{level_path}.XpRequired",
                    maximum=_UINT64_MAX,
                )
                xp_requirement_count += 1
            output_levels.append(output_level)
        output_entry["levels"] = output_levels
        proficiencies.append(output_entry)
        id_ordinals[proficiency_id].append(proficiency_ordinal)
        name_ordinals[name].append(proficiency_ordinal)

    duplicate_ids = [
        {"proficiencyId": proficiency_id, "sourceOrdinals": ordinals}
        for proficiency_id, ordinals in sorted(id_ordinals.items())
        if len(ordinals) > 1
    ]
    duplicate_names = [
        {"name": name, "sourceOrdinals": ordinals}
        for name, ordinals in sorted(name_ordinals.items())
        if len(ordinals) > 1
    ]
    findings: dict[str, object] = {
        "duplicateProficiencyIds": duplicate_ids,
        "duplicateNames": duplicate_names,
    }
    totals = {
        "proficiencyCount": len(proficiencies),
        "levelCount": total_levels,
        "perkCount": total_perks,
        "xpRequirementCount": xp_requirement_count,
    }
    return proficiencies, findings, totals


def build_index(
    *,
    manifest_path: Path,
    source_path: Path,
    input_id: str,
    max_source_bytes: int = DEFAULT_MAX_SOURCE_BYTES,
    max_decompressed_bytes: int = DEFAULT_MAX_DECOMPRESSED_BYTES,
    max_manifest_bytes: int = DEFAULT_MAX_MANIFEST_BYTES,
    max_proficiencies: int = DEFAULT_MAX_PROFICIENCIES,
    max_levels: int = DEFAULT_MAX_LEVELS,
    max_perks: int = DEFAULT_MAX_PERKS,
) -> tuple[dict[str, object], tuple[Path, Path]]:
    for value, label in (
        (max_source_bytes, "max_source_bytes"),
        (max_decompressed_bytes, "max_decompressed_bytes"),
        (max_manifest_bytes, "max_manifest_bytes"),
        (max_proficiencies, "max_proficiencies"),
        (max_levels, "max_levels"),
        (max_perks, "max_perks"),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ProficiencyReferenceError(f"{label} must be a positive integer")
    if not isinstance(input_id, str) or not input_id:
        raise ProficiencyReferenceError("input_id must be non-empty")

    manifest, manifest_sha256, manifest_resolved = _load_manifest(
        manifest_path, max_manifest_bytes=max_manifest_bytes
    )
    entry = _manifest_input(manifest, input_id)
    source_data, source_size, source_sha256, source_resolved = _read_stable_file(
        source_path, max_bytes=max_source_bytes, label="source"
    )
    if source_size != entry["sizeBytes"]:
        raise ProficiencyReferenceError("source size does not match manifest selected input")
    if source_sha256.lower() != str(entry["sha256"]).lower():
        raise ProficiencyReferenceError("source SHA-256 does not match manifest selected input")
    if os.path.samefile(manifest_resolved, source_resolved):
        raise ProficiencyReferenceError("manifest and source must be distinct files")

    decoded, encoding = _decode_source_bytes(source_data, max_decompressed_bytes=max_decompressed_bytes)
    try:
        source_text = decoded.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProficiencyReferenceError("decoded source must be valid UTF-8") from exc
    source_payload = _strict_json_loads(source_text, label="source")
    proficiencies, findings, totals = _parse_proficiencies(
        source_payload,
        max_proficiencies=max_proficiencies,
        max_levels=max_levels,
        max_perks=max_perks,
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
        "identifierNamespaces": {
            "proficiencyId": {
                "name": PROFICIENCY_ID_NAMESPACE,
                "resolution": "definition-only",
                "appearanceEquivalent": False,
                "canaryRuntimeEquivalent": False,
            }
        },
        "proficiencies": proficiencies,
        "findings": findings,
        "summary": {
            **totals,
            "duplicateProficiencyIdCount": len(findings["duplicateProficiencyIds"]),
            "duplicateNameCount": len(findings["duplicateNames"]),
        },
        "policy": {
            "definitionOnly": True,
            "appearanceParsing": False,
            "appearanceCorrelation": False,
            "runtimeCorrelation": False,
            "itemsXmlWriting": False,
            "gameplayConclusions": False,
            "maxSourceBytes": max_source_bytes,
            "maxDecompressedBytes": max_decompressed_bytes,
            "maxProficiencies": max_proficiencies,
            "maxLevels": max_levels,
            "maxPerks": max_perks,
        },
    }
    return payload, (manifest_resolved, source_resolved)


def deterministic_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def write_index(
    output: Path,
    payload: Mapping[str, object],
    *,
    protected_inputs: Iterable[Path],
    overwrite: bool = False,
) -> None:
    target_path = output.expanduser()
    if target_path.is_symlink():
        raise ProficiencyReferenceError(f"output must not be a symlink: {output}")
    target = target_path.resolve()
    protected = tuple(path.resolve() for path in protected_inputs)
    if any(target == source or (target.exists() and os.path.samefile(target, source)) for source in protected):
        raise ProficiencyReferenceError("output collides with a protected input")
    if target.exists() and not target.is_file():
        raise ProficiencyReferenceError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise ProficiencyReferenceError(f"output already exists: {target}; pass --overwrite")
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
