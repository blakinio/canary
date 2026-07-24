#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping

_IMPL_PATH = Path(__file__).with_name("result_envelope_impl.py")
_SPEC = importlib.util.spec_from_file_location("canary_e2e_result_envelope_impl", _IMPL_PATH)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover
    raise ImportError(f"cannot load result envelope implementation from {_IMPL_PATH}")
_IMPL = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _IMPL
_SPEC.loader.exec_module(_IMPL)

CLEANUP_CONTRACT = "canary-universal-e2e-cleanup-certification-v1"
CLEANUP_SCHEMA_VERSION = 1
_GENERIC_CLEANUP_UNKNOWN = "Cleanup is observed only and is not QRI-006 certified."
_ORIGINAL_BUILD = _IMPL.build_envelope
_ORIGINAL_CLEANUP = _IMPL._cleanup_summary
_ORIGINAL_DIMENSIONS = _IMPL._quality_dimensions
_ORIGINAL_ARTIFACTS = _IMPL._artifact_references


def _safe_map_identity(artifacts: Path, scenario: Mapping[str, Any]) -> dict[str, Any]:
    parts = _IMPL._read_text(artifacts / "map.sha256").split(maxsplit=1)
    digest = parts[0] if parts else None
    if not isinstance(digest, str) or not _IMPL._SHA256_RE.fullmatch(digest):
        digest = None
    server = scenario.get("server") if isinstance(scenario, Mapping) else None
    return {
        "name": _IMPL.sanitize(server.get("map")) if isinstance(server, Mapping) else None,
        "sha256": digest,
    }


def _certified_cleanup(legacy: Mapping[str, Any]) -> Mapping[str, Any] | None:
    value = legacy.get("cleanup_summary")
    if not isinstance(value, Mapping):
        return None
    if value.get("contract") != CLEANUP_CONTRACT or value.get("schema_version") != CLEANUP_SCHEMA_VERSION:
        return None
    if not isinstance(value.get("cleanup_certified"), bool):
        return None
    return value


def _cleanup_summary(artifacts: Path, legacy: Mapping[str, Any]) -> dict[str, Any]:
    value = _certified_cleanup(legacy)
    return _IMPL.sanitize(dict(value)) if value is not None else _ORIGINAL_CLEANUP(artifacts, legacy)


def _quality_dimensions(legacy: Mapping[str, Any], status: str) -> dict[str, str]:
    dimensions = _ORIGINAL_DIMENSIONS(legacy, status)
    cleanup = _certified_cleanup(legacy)
    if cleanup is not None:
        dimensions["cleanup"] = "pass" if cleanup.get("cleanup_certified") is True else "fail"
    return dimensions


def _artifact_references(artifacts: Path, manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    references = _ORIGINAL_ARTIFACTS(artifacts, manifest)
    if any(item.get("path") == "cleanup-certification.json" for item in references):
        return references
    path = artifacts / "cleanup-certification.json"
    reference: dict[str, Any] = {
        "path": "cleanup-certification.json",
        "kind": "json",
        "exists": path.is_file(),
    }
    if path.is_file():
        reference["size_bytes"] = path.stat().st_size
        digest = _IMPL._sha256(path)
        if digest:
            reference["sha256"] = digest
    references.append(reference)
    return references


def build_envelope(*args: Any, **kwargs: Any) -> dict[str, Any]:
    envelope = _ORIGINAL_BUILD(*args, **kwargs)
    cleanup = envelope.get("cleanup_summary")
    if isinstance(cleanup, Mapping) and cleanup.get("contract") == CLEANUP_CONTRACT:
        unknowns = envelope.get("unknowns")
        if isinstance(unknowns, list):
            envelope["unknowns"] = [item for item in unknowns if item != _GENERIC_CLEANUP_UNKNOWN]
            for item in cleanup.get("unknowns", []):
                rendered = f"Cleanup certification: {item}"
                if rendered not in envelope["unknowns"]:
                    envelope["unknowns"].append(rendered)
        envelope["unknowns"] = sorted(envelope.get("unknowns", []))
        _IMPL.validate_envelope(envelope)
    return envelope


_IMPL._map_identity = _safe_map_identity
_IMPL._cleanup_summary = _cleanup_summary
_IMPL._quality_dimensions = _quality_dimensions
_IMPL._artifact_references = _artifact_references
_IMPL.build_envelope = build_envelope

CONTRACT = _IMPL.CONTRACT
SCHEMA_VERSION = _IMPL.SCHEMA_VERSION
EnvelopeError = _IMPL.EnvelopeError
sanitize = _IMPL.sanitize
validate_envelope = _IMPL.validate_envelope
serialize_envelope = _IMPL.serialize_envelope
write_envelope = _IMPL.write_envelope
build_parser = _IMPL.build_parser
main = _IMPL.main

__all__ = [
    "CONTRACT",
    "SCHEMA_VERSION",
    "EnvelopeError",
    "sanitize",
    "build_envelope",
    "validate_envelope",
    "serialize_envelope",
    "write_envelope",
    "build_parser",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())
