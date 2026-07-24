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


# Keep the public contract in one canonical entrypoint while applying the
# fail-closed empty-map-identity regression fix to the retained implementation.
_IMPL._map_identity = _safe_map_identity

CONTRACT = _IMPL.CONTRACT
SCHEMA_VERSION = _IMPL.SCHEMA_VERSION
EnvelopeError = _IMPL.EnvelopeError
sanitize = _IMPL.sanitize
build_envelope = _IMPL.build_envelope
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
