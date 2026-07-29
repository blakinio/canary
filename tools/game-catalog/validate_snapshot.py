#!/usr/bin/env python3
"""Validate an Oteryn Game Catalog snapshot without network or database access."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

CONTRACT_ID = "oteryn.game-catalog"
SCHEMA_SHA256_BY_VERSION = {
    "1.0.0": "099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b",
    "1.1.0": "323ff6ae849759c9190f2a0c342855194ed74645816adc45051b6d914e67c7ac",
}
MAX_DOCUMENT_BYTES = 67_108_864
MAX_FINDINGS = 200


@dataclass(frozen=True)
class Finding:
    code: str
    path: str
    message: str


class CatalogValidationError(Exception):
    def __init__(self, findings: list[Finding]) -> None:
        self.findings = findings
        super().__init__(findings[0].message if findings else "Game Catalog validation failed")


class SchemaSubsetValidator:
    """Draft 2020-12 keyword subset used by the pinned Game Catalog schema."""

    _SUPPORTED = {
        "$schema", "$id", "$defs", "$ref", "title", "description",
        "type", "additionalProperties", "required", "properties",
        "minProperties", "maxProperties", "items", "minItems", "maxItems",
        "minLength", "maxLength", "pattern", "format", "minimum", "maximum",
        "enum", "const", "oneOf", "allOf",
    }

    def __init__(self, root_schema: dict[str, Any], maximum_findings: int = MAX_FINDINGS) -> None:
        self.root_schema = root_schema
        self.maximum_findings = maximum_findings
        self.findings: list[Finding] = []

    def validate(self, value: Any) -> list[Finding]:
        self.findings = []
        self._validate(value, self.root_schema, "$")
        return self.findings

    def _validate(self, value: Any, schema: dict[str, Any], path: str) -> None:
        if len(self.findings) >= self.maximum_findings:
            return

        for keyword in schema:
            if keyword not in self._SUPPORTED:
                self._add("schema.unsupported_keyword", path, f"Unsupported schema keyword [{keyword}].")

        reference = schema.get("$ref")
        if reference is not None:
            resolved = self._resolve(reference)
            if resolved is None:
                self._add("schema.unresolved_ref", path, "Schema reference could not be resolved.")
                return
            self._validate(value, resolved, path)

        all_of = schema.get("allOf")
        if all_of is not None:
            if not isinstance(all_of, list) or not all(isinstance(entry, dict) for entry in all_of):
                self._add("schema.invalid_all_of", path, "allOf must contain schemas.")
            else:
                for entry in all_of:
                    self._validate(value, entry, path)

        one_of = schema.get("oneOf")
        if one_of is not None:
            if not isinstance(one_of, list) or not all(isinstance(entry, dict) for entry in one_of):
                self._add("schema.invalid_one_of", path, "oneOf must contain schemas.")
            else:
                matches = 0
                for entry in one_of:
                    nested = SchemaSubsetValidator(self.root_schema, self.maximum_findings)
                    nested._validate(value, entry, path)
                    if not nested.findings:
                        matches += 1
                if matches != 1:
                    self._add("schema.one_of", path, "Value must match exactly one oneOf schema.")

        if "const" in schema and value != schema["const"]:
            self._add("schema.const", path, "Value does not match the required constant.")
        if "enum" in schema and value not in schema["enum"]:
            self._add("schema.enum", path, "Value is not in the allowed enumeration.")

        declared_type = schema.get("type")
        if declared_type is not None and not self._matches_type(value, declared_type):
            self._add("schema.type", path, "Value does not match the declared JSON type.")
            return

        if isinstance(value, dict):
            self._validate_object(value, schema, path)
        elif isinstance(value, list):
            self._validate_array(value, schema, path)
        elif isinstance(value, str):
            self._validate_string(value, schema, path)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            self._validate_number(value, schema, path)

    def _validate_object(self, value: dict[str, Any], schema: dict[str, Any], path: str) -> None:
        if isinstance(schema.get("minProperties"), int) and len(value) < schema["minProperties"]:
            self._add("schema.min_properties", path, "Object contains fewer properties than allowed.")
        if isinstance(schema.get("maxProperties"), int) and len(value) > schema["maxProperties"]:
            self._add("schema.max_properties", path, "Object contains more properties than allowed.")

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            self._add("schema.invalid_properties", path, "properties must be an object.")
            properties = {}

        required = schema.get("required", [])
        if not isinstance(required, list) or not all(isinstance(entry, str) for entry in required):
            self._add("schema.invalid_required", path, "required must contain strings.")
        else:
            for name in required:
                if name not in value:
                    self._add("schema.required", f"{path}/{self._escape(name)}", f"Required property [{name}] is missing.")

        for name, child in value.items():
            child_path = f"{path}/{self._escape(name)}"
            child_schema = properties.get(name)
            if child_schema is not None:
                if not isinstance(child_schema, dict):
                    self._add("schema.invalid_property", child_path, "Property schema is invalid.")
                else:
                    self._validate(child, child_schema, child_path)
            elif schema.get("additionalProperties", True) is False:
                self._add("schema.additional_property", child_path, f"Unknown property [{name}] is not allowed.")

    def _validate_array(self, value: list[Any], schema: dict[str, Any], path: str) -> None:
        if isinstance(schema.get("minItems"), int) and len(value) < schema["minItems"]:
            self._add("schema.min_items", path, "Array contains fewer items than allowed.")
        if isinstance(schema.get("maxItems"), int) and len(value) > schema["maxItems"]:
            self._add("schema.max_items", path, "Array contains more items than allowed.")
        item_schema = schema.get("items")
        if item_schema is not None:
            if not isinstance(item_schema, dict):
                self._add("schema.invalid_items", path, "items must be a schema.")
            else:
                for index, child in enumerate(value):
                    self._validate(child, item_schema, f"{path}/{index}")

    def _validate_string(self, value: str, schema: dict[str, Any], path: str) -> None:
        if isinstance(schema.get("minLength"), int) and len(value) < schema["minLength"]:
            self._add("schema.min_length", path, "String is shorter than allowed.")
        if isinstance(schema.get("maxLength"), int) and len(value) > schema["maxLength"]:
            self._add("schema.max_length", path, "String is longer than allowed.")
        pattern = schema.get("pattern")
        if pattern is not None:
            if not isinstance(pattern, str):
                self._add("schema.invalid_pattern", path, "Schema pattern must be a string.")
            else:
                try:
                    if re.search(pattern, value) is None:
                        self._add("schema.pattern", path, "String does not match the required pattern.")
                except re.error:
                    self._add("schema.invalid_pattern", path, "Schema pattern is invalid.")
        if schema.get("format") == "date-time" and not self._is_datetime(value):
            self._add("schema.date_time", path, "String is not a valid RFC 3339 date-time.")

    def _validate_number(self, value: int | float, schema: dict[str, Any], path: str) -> None:
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            self._add("schema.minimum", path, "Number is below the allowed minimum.")
        if isinstance(maximum, (int, float)) and value > maximum:
            self._add("schema.maximum", path, "Number exceeds the allowed maximum.")

    def _matches_type(self, value: Any, declared: Any) -> bool:
        types = [declared] if isinstance(declared, str) else declared
        if not isinstance(types, list):
            return False
        for type_name in types:
            if type_name == "null" and value is None:
                return True
            if type_name == "boolean" and isinstance(value, bool):
                return True
            if type_name == "integer" and isinstance(value, int) and not isinstance(value, bool):
                return True
            if type_name == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
                return True
            if type_name == "string" and isinstance(value, str):
                return True
            if type_name == "array" and isinstance(value, list):
                return True
            if type_name == "object" and isinstance(value, dict):
                return True
        return False

    def _resolve(self, reference: Any) -> dict[str, Any] | None:
        if not isinstance(reference, str) or not reference.startswith("#/"):
            return None
        current: Any = self.root_schema
        for segment in reference[2:].split("/"):
            segment = segment.replace("~1", "/").replace("~0", "~")
            if not isinstance(current, dict) or segment not in current:
                return None
            current = current[segment]
        return current if isinstance(current, dict) else None

    @staticmethod
    def _is_datetime(value: str) -> bool:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value) is None:
            return False
        try:
            dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False

    @staticmethod
    def _escape(value: str) -> str:
        return value.replace("~", "~0").replace("/", "~1")

    def _add(self, code: str, path: str, message: str) -> None:
        if len(self.findings) < self.maximum_findings:
            self.findings.append(Finding(code, path, message))


def validate_semantics(document: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    releases = document.get("releases", [])
    entities = document.get("entities", [])
    relations = document.get("relations", [])
    snapshot = document.get("snapshot", {})

    release_orders: dict[str, int] = {}
    seen_orders: set[int] = set()
    release_sort_keys: list[tuple[int, str]] = []
    for index, release in enumerate(releases if isinstance(releases, list) else []):
        if not isinstance(release, dict):
            continue
        key = release.get("key")
        order = release.get("release_order")
        if not isinstance(key, str) or not isinstance(order, int) or isinstance(order, bool):
            continue
        if key in release_orders:
            findings.append(Finding("semantic.duplicate_release", f"$/releases/{index}/key", "Duplicate release key."))
        if order in seen_orders:
            findings.append(Finding("semantic.duplicate_release_order", f"$/releases/{index}/release_order", "Duplicate release_order."))
        release_orders[key] = order
        seen_orders.add(order)
        release_sort_keys.append((order, key))
    if release_sort_keys != sorted(release_sort_keys):
        findings.append(Finding("semantic.release_order", "$/releases", "Releases are not sorted by release_order and key."))

    if isinstance(snapshot, dict):
        if snapshot.get("entity_count") != len(entities):
            findings.append(Finding("semantic.entity_count", "$/snapshot/entity_count", "Declared entity count does not match the document."))
        if snapshot.get("relation_count") != len(relations):
            findings.append(Finding("semantic.relation_count", "$/snapshot/relation_count", "Declared relation count does not match the document."))
        for field in ("runtime_release", "content_target_release", "verified_content_through_release", "contains_content_through_release"):
            reference = snapshot.get(field)
            if reference is not None and reference not in release_orders:
                findings.append(Finding("semantic.unknown_release", f"$/snapshot/{field}", f"Snapshot field [{field}] references an unknown release."))

    entity_keys: set[str] = set()
    typed_entity_keys: set[tuple[str, str]] = set()
    entity_sort_keys: list[tuple[str, str]] = []
    for index, entity in enumerate(entities if isinstance(entities, list) else []):
        if not isinstance(entity, dict):
            continue
        entity_type = entity.get("type")
        key = entity.get("canonical_key")
        if isinstance(entity_type, str) and isinstance(key, str):
            identity = (entity_type, key)
            if identity in typed_entity_keys:
                findings.append(Finding("semantic.duplicate_entity", f"$/entities/{index}/canonical_key", "Duplicate entity canonical key for the same type."))
            typed_entity_keys.add(identity)
            entity_keys.add(key)
            entity_sort_keys.append(identity)
        _validate_range(entity, f"$/entities/{index}", release_orders, findings)
        _validate_identifiers(entity.get("identifiers"), f"$/entities/{index}/identifiers", findings)
        _validate_source_path(entity.get("source_path"), f"$/entities/{index}/source_path", findings)
    if entity_sort_keys != sorted(entity_sort_keys):
        findings.append(Finding("semantic.entity_order", "$/entities", "Entities are not sorted by type and canonical key."))

    relation_keys: set[str] = set()
    relation_sort_keys: list[tuple[str, str]] = []
    for index, relation in enumerate(relations if isinstance(relations, list) else []):
        if not isinstance(relation, dict):
            continue
        key = relation.get("canonical_key")
        relation_type = relation.get("type")
        if isinstance(key, str):
            if key in relation_keys:
                findings.append(Finding("semantic.duplicate_relation", f"$/relations/{index}/canonical_key", "Duplicate relation canonical key."))
            relation_keys.add(key)
            relation_sort_keys.append((relation_type if isinstance(relation_type, str) else "", key))
        for endpoint in ("source", "target"):
            endpoint_key = relation.get(endpoint)
            if not isinstance(endpoint_key, str) or endpoint_key not in entity_keys:
                findings.append(Finding("semantic.dangling_relation", f"$/relations/{index}/{endpoint}", f"Relation {endpoint} does not resolve to an entity."))
        _validate_range(relation, f"$/relations/{index}", release_orders, findings)
        _validate_source_path(relation.get("source_path"), f"$/relations/{index}/source_path", findings)
        data = relation.get("data")
        if isinstance(data, dict):
            numerator = data.get("chance_numerator")
            denominator = data.get("chance_denominator")
            if isinstance(numerator, int) and isinstance(denominator, int) and numerator > denominator:
                findings.append(Finding("semantic.invalid_probability", f"$/relations/{index}/data/chance_numerator", "Loot chance numerator exceeds its denominator."))
            minimum = data.get("minimum_count")
            maximum = data.get("maximum_count")
            if isinstance(minimum, int) and isinstance(maximum, int) and maximum < minimum:
                findings.append(Finding("semantic.invalid_count_range", f"$/relations/{index}/data/maximum_count", "Loot maximum count is lower than minimum count."))
    if relation_sort_keys != sorted(relation_sort_keys):
        findings.append(Finding("semantic.relation_order", "$/relations", "Relations are not sorted by type and canonical key."))

    return findings[:MAX_FINDINGS]


def _validate_range(record: dict[str, Any], path: str, releases: dict[str, int], findings: list[Finding]) -> None:
    introduced = record.get("introduced_in")
    removed = record.get("removed_in")
    for field, reference in (("introduced_in", introduced), ("removed_in", removed)):
        if reference is not None and reference not in releases:
            findings.append(Finding("semantic.unknown_release", f"{path}/{field}", f"Version range references unknown release [{field}]."))
    if isinstance(introduced, str) and isinstance(removed, str) and introduced in releases and removed in releases and releases[removed] <= releases[introduced]:
        findings.append(Finding("semantic.invalid_version_range", f"{path}/removed_in", "removed_in must be an exclusive release later than introduced_in."))


def _validate_identifiers(identifiers: Any, path: str, findings: list[Finding]) -> None:
    if not isinstance(identifiers, list):
        return
    seen: set[tuple[str, str]] = set()
    sort_keys: list[tuple[str, str]] = []
    for index, identifier in enumerate(identifiers):
        if not isinstance(identifier, dict):
            continue
        namespace = identifier.get("namespace")
        value = identifier.get("value")
        if not isinstance(namespace, str) or not isinstance(value, str):
            continue
        key = (namespace, value)
        if key in seen:
            findings.append(Finding("semantic.duplicate_identifier", f"{path}/{index}", "Duplicate namespaced identifier."))
        seen.add(key)
        sort_keys.append(key)
    if sort_keys != sorted(sort_keys):
        findings.append(Finding("semantic.identifier_order", path, "Identifiers are not sorted by namespace and value."))


def _validate_source_path(source_path: Any, path: str, findings: list[Finding]) -> None:
    if source_path is None:
        return
    if not isinstance(source_path, str):
        return
    pure = PurePosixPath(source_path)
    if not source_path or "\\" in source_path or pure.is_absolute() or ".." in pure.parts or re.match(r"^[A-Za-z]:", source_path):
        findings.append(Finding("semantic.unsafe_source_path", path, "Source path must be a non-empty portable repository-relative path."))


def load_and_validate(snapshot_path: Path, schema_path: Path, expected_hash: str | None = None) -> tuple[dict[str, Any], str, int]:
    if not snapshot_path.is_file() or snapshot_path.is_symlink():
        raise CatalogValidationError([Finding("file.invalid", "$", "Snapshot path must reference a regular file.")])
    size = snapshot_path.stat().st_size
    if size < 1 or size > MAX_DOCUMENT_BYTES:
        raise CatalogValidationError([Finding("file.size", "$", "Snapshot file size is outside the configured bounds.")])
    raw = snapshot_path.read_bytes()
    if len(raw) != size:
        raise CatalogValidationError([Finding("file.read", "$", "Snapshot file could not be read completely.")])
    content_hash = hashlib.sha256(raw).hexdigest()
    if expected_hash is not None and (re.fullmatch(r"[0-9a-f]{64}", expected_hash) is None or content_hash != expected_hash):
        raise CatalogValidationError([Finding("hash.mismatch", "$/sha256", "Snapshot SHA-256 does not match the expected value.")])

    sidecar = Path(f"{snapshot_path}.sha256")
    if sidecar.exists():
        if not sidecar.is_file() or sidecar.is_symlink():
            raise CatalogValidationError([Finding("hash.sidecar", "$/sha256", "SHA-256 sidecar is not a regular file.")])
        match = re.fullmatch(r"([0-9a-f]{64})(?:\s+[^\r\n]+)?\s*", sidecar.read_text(encoding="utf-8"))
        if match is None or match.group(1) != content_hash:
            raise CatalogValidationError([Finding("hash.sidecar", "$/sha256", "SHA-256 sidecar is invalid or mismatched.")])

    if not schema_path.is_file() or schema_path.is_symlink():
        raise CatalogValidationError([Finding("schema.unavailable", "$", "Pinned Game Catalog schema is unavailable.")])
    schema_raw = schema_path.read_bytes()
    schema_hash = hashlib.sha256(schema_raw).hexdigest()
    schema_version = next(
        (
            version
            for version, expected_schema_hash in SCHEMA_SHA256_BY_VERSION.items()
            if schema_hash == expected_schema_hash
        ),
        None,
    )
    if schema_version is None:
        raise CatalogValidationError([Finding("schema.hash", "$", "Pinned schema hash does not match the cross-repository contract.")])

    try:
        document = json.loads(raw.decode("utf-8"))
        schema = json.loads(schema_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CatalogValidationError([Finding("json.invalid", "$", f"Invalid UTF-8 or JSON: {error}")]) from error
    if not isinstance(document, dict) or not isinstance(schema, dict):
        raise CatalogValidationError([Finding("json.root", "$", "Snapshot and schema roots must be JSON objects.")])
    declared_schema_version = (
        schema.get("properties", {})
        .get("schema_version", {})
        .get("const")
    )
    if declared_schema_version != schema_version:
        raise CatalogValidationError([Finding("schema.version", "$schema", "Pinned schema hash and declared version do not match.")])

    schema_findings = SchemaSubsetValidator(schema).validate(document)
    if schema_findings:
        raise CatalogValidationError(schema_findings)
    semantic_findings = validate_semantics(document)
    if semantic_findings:
        raise CatalogValidationError(semantic_findings)

    return document, content_hash, size


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--schema", type=Path, default=Path("schemas/game-catalog/v1/game-catalog-snapshot.schema.json"))
    parser.add_argument("--expected-sha256")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        document, content_hash, size = load_and_validate(args.snapshot, args.schema, args.expected_sha256)
    except CatalogValidationError as error:
        for finding in error.findings:
            print(f"{finding.code}\t{finding.path}\t{finding.message}", file=sys.stderr)
        return 1
    print(json.dumps({
        "contract": CONTRACT_ID,
        "schema_version": document["schema_version"],
        "sha256": content_hash,
        "bytes": size,
        "entity_count": document["snapshot"]["entity_count"],
        "relation_count": document["snapshot"]["relation_count"],
    }, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
