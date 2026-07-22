from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MANIFEST_FORMAT = "canary-otbm-evidence-gateway-manifest-v1"
BUNDLE_FORMAT = "canary-otbm-evidence-bundle-v1"
SCHEMA_VERSION = 1
MAX_SOURCES = 32
MAX_EXTRACTS = 128
MAX_SERIALIZED_EXTRACT_BYTES = 256 * 1024


class EvidenceGatewayError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise EvidenceGatewayError(f"{label} must be a SHA-256 hex string")
    return value.lower()


def _decode_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def resolve_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise EvidenceGatewayError(f"JSON Pointer must be empty or start with '/': {pointer!r}")
    current = document
    for raw in pointer.split("/")[1:]:
        token = _decode_pointer_token(raw)
        if isinstance(current, dict):
            if token not in current:
                raise EvidenceGatewayError(f"JSON Pointer {pointer!r} is missing object key {token!r}")
            current = current[token]
        elif isinstance(current, list):
            if token == "-" or not token.isdigit():
                raise EvidenceGatewayError(f"JSON Pointer {pointer!r} contains invalid array index {token!r}")
            index = int(token)
            if index >= len(current):
                raise EvidenceGatewayError(f"JSON Pointer {pointer!r} array index {index} is out of range")
            current = current[index]
        else:
            raise EvidenceGatewayError(f"JSON Pointer {pointer!r} traverses a scalar value")
    return current


def normalize_manifest(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("format") != MANIFEST_FORMAT:
        raise EvidenceGatewayError(f"manifest.format must be {MANIFEST_FORMAT}")
    sources = document.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= MAX_SOURCES:
        raise EvidenceGatewayError(f"sources must contain 1..{MAX_SOURCES} entries")
    normalized: list[dict[str, Any]] = []
    source_ids: set[str] = set()
    extract_ids: set[str] = set()
    extract_total = 0
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise EvidenceGatewayError(f"sources[{index}] must be an object")
        identifier = source.get("id")
        path = source.get("path")
        expected_format = source.get("format")
        extracts = source.get("extracts")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in source_ids:
            raise EvidenceGatewayError(f"sources[{index}].id must be unique and non-empty")
        relative = Path(path) if isinstance(path, str) else Path()
        if not isinstance(path, str) or not path or relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
            raise EvidenceGatewayError(f"sources[{index}].path must be a safe non-empty relative path")
        if not isinstance(expected_format, str) or not expected_format.strip():
            raise EvidenceGatewayError(f"sources[{index}].format must be non-empty")
        if not isinstance(extracts, list) or not extracts:
            raise EvidenceGatewayError(f"sources[{index}].extracts must be a non-empty array")
        normalized_extracts: list[dict[str, str]] = []
        for extract_index, extract in enumerate(extracts):
            extract_total += 1
            if extract_total > MAX_EXTRACTS:
                raise EvidenceGatewayError(f"manifest contains more than {MAX_EXTRACTS} extracts")
            if not isinstance(extract, dict):
                raise EvidenceGatewayError(f"sources[{index}].extracts[{extract_index}] must be an object")
            extract_id = extract.get("id")
            pointer = extract.get("pointer")
            if not isinstance(extract_id, str) or not extract_id.strip() or extract_id in extract_ids:
                raise EvidenceGatewayError("extract ids must be globally unique and non-empty")
            if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
                raise EvidenceGatewayError(f"extract {extract_id} has invalid JSON Pointer")
            extract_ids.add(extract_id)
            normalized_extracts.append({"id": extract_id, "pointer": pointer})
        source_ids.add(identifier)
        normalized.append({"id": identifier, "path": relative.as_posix(), "sha256": _sha(source.get("sha256"), f"sources[{index}].sha256"), "format": expected_format, "extracts": normalized_extracts})
    return {"format": MANIFEST_FORMAT, "schemaVersion": SCHEMA_VERSION, "sources": normalized}


def load_manifest(path: Path) -> dict[str, Any]:
    source = path.expanduser().resolve()
    if path.is_symlink() or not source.is_file():
        raise EvidenceGatewayError(f"manifest must be an existing non-symlink file: {path}")
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceGatewayError(f"Cannot read manifest {source}: {exc}") from exc
    return normalize_manifest(document)


def build_evidence_bundle(manifest_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    manifest = normalize_manifest(manifest)
    root = manifest_path.expanduser().resolve().parent
    extracts: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for spec in manifest["sources"]:
        source_path = (root / spec["path"]).resolve()
        try:
            source_path.relative_to(root)
        except ValueError as exc:
            raise EvidenceGatewayError(f"source path escapes manifest directory: {spec['path']}") from exc
        if source_path.is_symlink() or not source_path.is_file():
            raise EvidenceGatewayError(f"source must be an existing non-symlink file: {spec['path']}")
        actual_sha = _sha256(source_path)
        if actual_sha != spec["sha256"]:
            raise EvidenceGatewayError(f"source {spec['id']} SHA-256 mismatch: expected {spec['sha256']}, got {actual_sha}")
        try:
            document = json.loads(source_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EvidenceGatewayError(f"Cannot read source {spec['id']}: {exc}") from exc
        if not isinstance(document, dict) or document.get("format") != spec["format"]:
            raise EvidenceGatewayError(f"source {spec['id']} format mismatch: expected {spec['format']}")
        sources.append({"id": spec["id"], "path": spec["path"], "sha256": actual_sha, "format": spec["format"]})
        for extract in spec["extracts"]:
            value = resolve_pointer(document, extract["pointer"])
            serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            if len(serialized) > MAX_SERIALIZED_EXTRACT_BYTES:
                raise EvidenceGatewayError(f"extract {extract['id']} exceeds {MAX_SERIALIZED_EXTRACT_BYTES} serialized bytes")
            extracts.append({"id": extract["id"], "sourceId": spec["id"], "pointer": extract["pointer"], "value": value, "valueSha256": hashlib.sha256(serialized).hexdigest()})
    extracts.sort(key=lambda value: value["id"])
    sources.sort(key=lambda value: value["id"])
    bundle: dict[str, Any] = {
        "format": BUNDLE_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "manifestSha256": _json_hash(manifest),
        "sources": sources,
        "extracts": extracts,
        "summary": {"sourceCount": len(sources), "extractCount": len(extracts)},
        "policy": {
            "readOnlyComposition": True,
            "parsesOtbm": False,
            "validatesSourceSemantics": False,
            "pathfinds": False,
            "runsE2e": False,
            "ownsDownstreamAcceptance": False,
        },
    }
    bundle["bundleSha256"] = _json_hash(bundle)
    return bundle
