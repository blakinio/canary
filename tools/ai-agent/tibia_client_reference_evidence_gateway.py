from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from otbm_evidence_gateway import (
    BUNDLE_FORMAT,
    MANIFEST_FORMAT,
    EvidenceGatewayError,
    build_evidence_bundle,
    normalize_manifest,
)

BINDINGS_FORMAT = "canary-tibia-client-reference-evidence-bindings-v1"
REPORT_FORMAT = "canary-tibia-client-reference-evidence-gateway-v1"
SCHEMA_VERSION = 1
MAX_BINDINGS = 128
MAX_BINDINGS_BYTES = 1024 * 1024
MAX_CONTEXT_REFERENCES = 32
MAX_EXTRACTS_PER_BINDING = 4
IDENTIFIER_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_FORMAT_BY_KIND = {
    "house": "canary-otbm-house-reference-parity-v1",
    "content": "canary-tibia-content-reference-correlation-v1",
    "proficiency": "canary-tibia-proficiency-reference-correlation-v1",
    "drift": "canary-tibia-client-reference-drift-v1",
}


class ClientReferenceEvidenceGatewayError(ValueError):
    pass


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ClientReferenceEvidenceGatewayError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _object(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ClientReferenceEvidenceGatewayError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ClientReferenceEvidenceGatewayError(f"{label} must be an array")
    return value


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise ClientReferenceEvidenceGatewayError(
            f"{label} must match {IDENTIFIER_RE.pattern}"
        )
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ClientReferenceEvidenceGatewayError(
            f"{label} must be an exact lowercase SHA-256"
        )
    return value


def _context_references(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    rows = _array(value, label)
    if len(rows) > MAX_CONTEXT_REFERENCES:
        raise ClientReferenceEvidenceGatewayError(
            f"{label} must contain at most {MAX_CONTEXT_REFERENCES} entries"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, str) or not row.strip() or row != row.strip():
            raise ClientReferenceEvidenceGatewayError(
                f"{label}[{index}] must be a non-empty trimmed string"
            )
        if row in seen:
            raise ClientReferenceEvidenceGatewayError(
                f"{label} contains duplicate value {row!r}"
            )
        seen.add(row)
        normalized.append(row)
    return sorted(normalized)


def load_bindings(path: Path) -> dict[str, Any]:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise ClientReferenceEvidenceGatewayError(
            f"bindings input must not be a symlink: {path}"
        )
    source = candidate.resolve(strict=True)
    if not source.is_file():
        raise ClientReferenceEvidenceGatewayError(
            f"bindings input must be a regular file: {source}"
        )
    before = source.stat()
    if before.st_size > MAX_BINDINGS_BYTES:
        raise ClientReferenceEvidenceGatewayError(
            f"bindings input exceeds {MAX_BINDINGS_BYTES} bytes"
        )
    try:
        data = source.read_bytes()
    except OSError as exc:
        raise ClientReferenceEvidenceGatewayError(
            f"cannot read bindings input {source}: {exc}"
        ) from exc
    after = source.stat()
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or len(data) != after.st_size:
        raise ClientReferenceEvidenceGatewayError(
            "bindings input changed while reading"
        )
    try:
        document = json.loads(
            data.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates
        )
    except UnicodeDecodeError as exc:
        raise ClientReferenceEvidenceGatewayError(
            "bindings input must be UTF-8"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ClientReferenceEvidenceGatewayError(
            f"bindings input is invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(document, dict):
        raise ClientReferenceEvidenceGatewayError(
            "bindings input must contain a JSON object"
        )
    return document


def normalize_bindings(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _object(document, "bindings document")
    required_root = {"format", "schemaVersion", "bindings"}
    if set(root) != required_root:
        raise ClientReferenceEvidenceGatewayError(
            "bindings document must contain exactly format, schemaVersion and bindings"
        )
    if root.get("format") != BINDINGS_FORMAT or root.get("schemaVersion") != SCHEMA_VERSION:
        raise ClientReferenceEvidenceGatewayError(
            f"bindings document must use {BINDINGS_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    bindings = _array(root.get("bindings"), "bindings")
    if not 1 <= len(bindings) <= MAX_BINDINGS:
        raise ClientReferenceEvidenceGatewayError(
            f"bindings must contain 1..{MAX_BINDINGS} entries"
        )

    binding_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw_binding in enumerate(bindings):
        binding = _object(raw_binding, f"bindings[{index}]")
        expected_keys = {"id", "kind", "sources", "contextReferences"}
        if set(binding) != expected_keys:
            raise ClientReferenceEvidenceGatewayError(
                f"bindings[{index}] must contain exactly id, kind, sources and contextReferences"
            )
        binding_id = _identifier(binding.get("id"), f"bindings[{index}].id")
        if binding_id in binding_ids:
            raise ClientReferenceEvidenceGatewayError(
                f"duplicate binding id {binding_id!r}"
            )
        kind = binding.get("kind")
        if kind not in EXPECTED_FORMAT_BY_KIND:
            raise ClientReferenceEvidenceGatewayError(
                f"bindings[{index}].kind must be one of {sorted(EXPECTED_FORMAT_BY_KIND)}"
            )
        sources = _array(binding.get("sources"), f"bindings[{index}].sources")
        if len(sources) != 1:
            raise ClientReferenceEvidenceGatewayError(
                f"bindings[{index}].sources must contain exactly one reviewed source"
            )
        try:
            gateway_manifest = normalize_manifest(
                {
                    "format": MANIFEST_FORMAT,
                    "schemaVersion": 1,
                    "sources": sources,
                }
            )
        except EvidenceGatewayError as exc:
            raise ClientReferenceEvidenceGatewayError(
                f"bindings[{index}] has an invalid QA-018 source/extract specification: {exc}"
            ) from exc
        source = gateway_manifest["sources"][0]
        expected_format = EXPECTED_FORMAT_BY_KIND[str(kind)]
        if source["format"] != expected_format:
            raise ClientReferenceEvidenceGatewayError(
                f"bindings[{index}] kind {kind!r} requires source format {expected_format!r}"
            )
        extracts = source["extracts"]
        if len(extracts) > MAX_EXTRACTS_PER_BINDING:
            raise ClientReferenceEvidenceGatewayError(
                f"bindings[{index}] must contain at most {MAX_EXTRACTS_PER_BINDING} reviewed extracts"
            )
        for extract in extracts:
            if extract["pointer"] == "":
                raise ClientReferenceEvidenceGatewayError(
                    f"binding {binding_id!r} must not extract an entire source document"
                )
            if not extract["id"].startswith(f"{binding_id}."):
                raise ClientReferenceEvidenceGatewayError(
                    f"extract id {extract['id']!r} must start with {binding_id + '.'!r}"
                )
        normalized.append(
            {
                "id": binding_id,
                "kind": kind,
                "sources": gateway_manifest["sources"],
                "contextReferences": _context_references(
                    binding.get("contextReferences"),
                    f"bindings[{index}].contextReferences",
                ),
            }
        )
        binding_ids.add(binding_id)

    normalized.sort(key=lambda row: row["id"])
    return {
        "format": BINDINGS_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "bindings": normalized,
    }


def resolve_binding(
    bindings: Mapping[str, Any], binding_id: str
) -> dict[str, Any]:
    normalized = normalize_bindings(bindings)
    wanted = _identifier(binding_id, "binding_id")
    matches = [row for row in normalized["bindings"] if row["id"] == wanted]
    if not matches:
        raise ClientReferenceEvidenceGatewayError(
            f"no reviewed client-reference evidence binding has id {wanted!r}"
        )
    if len(matches) != 1:
        raise ClientReferenceEvidenceGatewayError(
            f"ambiguous client-reference evidence binding id {wanted!r}"
        )
    return matches[0]


def _gateway_manifest(binding: Mapping[str, Any]) -> dict[str, Any]:
    try:
        return normalize_manifest(
            {
                "format": MANIFEST_FORMAT,
                "schemaVersion": 1,
                "sources": binding["sources"],
            }
        )
    except (KeyError, EvidenceGatewayError) as exc:
        raise ClientReferenceEvidenceGatewayError(
            f"selected binding cannot produce a QA-018 manifest: {exc}"
        ) from exc


def build_evidence_plan(
    bindings: Mapping[str, Any],
    binding_id: str,
    *,
    bindings_file_sha256: str,
) -> dict[str, Any]:
    normalized = normalize_bindings(bindings)
    selected = resolve_binding(normalized, binding_id)
    gateway_manifest = _gateway_manifest(selected)
    bindings_sha = _sha256(bindings_file_sha256, "bindings_file_sha256")
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "mode": "plan",
        "bindings": {
            "format": BINDINGS_FORMAT,
            "fileSha256": bindings_sha,
            "canonicalSha256": canonical_sha256(normalized),
        },
        "bindingId": selected["id"],
        "kind": selected["kind"],
        "contextReferences": selected["contextReferences"],
        "gatewayManifest": gateway_manifest,
        "evidenceBundle": None,
        "evidenceBundleSha256": None,
        "policy": {
            "reviewedBindingIdOnly": True,
            "parsesClientFiles": False,
            "parsesOtbm": False,
            "parsesSourceReports": False,
            "reinterpretsSourceSemantics": False,
            "infersIdentifiers": False,
            "fuzzySelection": False,
            "validatesSourceSemantics": False,
            "mutatesSourceOrGameState": False,
            "runsE2e": False,
            "ownsDownstreamAcceptance": False,
            "routesAdoption": False,
            "qa018EvidenceGatewayReused": True,
        },
    }
    report["reportSha256"] = canonical_sha256(report)
    return report


def execute_evidence_plan(
    bindings_path: Path, plan: Mapping[str, Any]
) -> dict[str, Any]:
    if (
        plan.get("format") != REPORT_FORMAT
        or plan.get("schemaVersion") != SCHEMA_VERSION
        or plan.get("mode") != "plan"
    ):
        raise ClientReferenceEvidenceGatewayError(
            f"plan must use {REPORT_FORMAT} schemaVersion {SCHEMA_VERSION} in plan mode"
        )
    provided_report_sha = plan.get("reportSha256")
    if not isinstance(provided_report_sha, str):
        raise ClientReferenceEvidenceGatewayError("plan.reportSha256 is required")
    unsigned = dict(plan)
    unsigned.pop("reportSha256", None)
    if canonical_sha256(unsigned) != provided_report_sha:
        raise ClientReferenceEvidenceGatewayError(
            "plan reportSha256 does not match canonical plan content"
        )

    candidate = bindings_path.expanduser()
    if candidate.is_symlink():
        raise ClientReferenceEvidenceGatewayError(
            f"bindings input must not be a symlink: {bindings_path}"
        )
    source = candidate.resolve(strict=True)
    bindings_meta = _object(plan.get("bindings"), "plan.bindings")
    expected_file_sha = _sha256(
        bindings_meta.get("fileSha256"), "plan.bindings.fileSha256"
    )
    if sha256_path(source) != expected_file_sha:
        raise ClientReferenceEvidenceGatewayError(
            "bindings file SHA-256 changed after plan creation"
        )

    raw_bindings = load_bindings(source)
    normalized = normalize_bindings(raw_bindings)
    if canonical_sha256(normalized) != bindings_meta.get("canonicalSha256"):
        raise ClientReferenceEvidenceGatewayError(
            "bindings canonical content changed after plan creation"
        )
    selected = resolve_binding(normalized, str(plan.get("bindingId")))
    expected_manifest = _gateway_manifest(selected)
    if plan.get("kind") != selected["kind"]:
        raise ClientReferenceEvidenceGatewayError(
            "plan kind does not match the reviewed binding"
        )
    if plan.get("contextReferences") != selected["contextReferences"]:
        raise ClientReferenceEvidenceGatewayError(
            "plan contextReferences do not match the reviewed binding"
        )
    if plan.get("gatewayManifest") != expected_manifest:
        raise ClientReferenceEvidenceGatewayError(
            "plan gatewayManifest does not match the reviewed binding"
        )

    try:
        bundle = build_evidence_bundle(source, expected_manifest)
    except EvidenceGatewayError as exc:
        raise ClientReferenceEvidenceGatewayError(
            f"QA-018 evidence extraction failed: {exc}"
        ) from exc
    if bundle.get("format") != BUNDLE_FORMAT or not isinstance(
        bundle.get("bundleSha256"), str
    ):
        raise ClientReferenceEvidenceGatewayError(
            "QA-018 returned an invalid evidence bundle contract"
        )

    report = dict(plan)
    report.pop("reportSha256", None)
    report["mode"] = "executed"
    report["evidenceBundle"] = bundle
    report["evidenceBundleSha256"] = bundle["bundleSha256"]
    report["reportSha256"] = canonical_sha256(report)
    return report


def source_paths_for_plan(
    bindings_path: Path, plan: Mapping[str, Any]
) -> list[Path]:
    root = bindings_path.expanduser().resolve(strict=True).parent
    manifest = _object(plan.get("gatewayManifest"), "plan.gatewayManifest")
    result: list[Path] = []
    for raw_source in _array(
        manifest.get("sources"), "plan.gatewayManifest.sources"
    ):
        source = _object(raw_source, "plan.gatewayManifest.sources[]")
        raw_path = source.get("path")
        if not isinstance(raw_path, str):
            raise ClientReferenceEvidenceGatewayError(
                "plan gateway source path must be a string"
            )
        relative = Path(raw_path)
        candidate = (root / relative).resolve(strict=False)
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ClientReferenceEvidenceGatewayError(
                f"source path escapes bindings directory: {relative}"
            ) from exc
        result.append(candidate)
    return result


def _atomic_write_text(path: Path, content: str, *, overwrite: bool) -> None:
    for parent in (path.parent, *path.parent.parents):
        if parent.is_symlink():
            raise ClientReferenceEvidenceGatewayError(
                f"output parent must not be a symlink: {parent}"
            )
        if parent.exists() and not parent.is_dir():
            raise ClientReferenceEvidenceGatewayError(
                f"output parent exists but is not a directory: {parent}"
            )
    if path.is_symlink():
        raise ClientReferenceEvidenceGatewayError(
            f"output must not be a symlink: {path}"
        )
    if path.exists() and not path.is_file():
        raise ClientReferenceEvidenceGatewayError(
            f"output exists but is not a regular file: {path}"
        )
    if path.exists() and not overwrite:
        raise ClientReferenceEvidenceGatewayError(
            f"output already exists: {path}; pass overwrite=True"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.is_symlink():
        raise ClientReferenceEvidenceGatewayError(
            f"temporary output must not be a symlink: {temporary}"
        )
    temporary.unlink(missing_ok=True)
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_report(
    path: Path, report: Mapping[str, Any], *, overwrite: bool = False
) -> None:
    _atomic_write_text(
        path,
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        overwrite=overwrite,
    )
