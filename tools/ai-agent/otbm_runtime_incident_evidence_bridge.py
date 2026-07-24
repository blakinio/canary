from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from otbm_evidence_gateway import (
    BUNDLE_FORMAT,
    MANIFEST_FORMAT,
    EvidenceGatewayError,
    build_evidence_bundle,
    normalize_manifest,
)

BINDINGS_FORMAT = "canary-otbm-runtime-incident-evidence-bindings-v1"
REPORT_FORMAT = "canary-otbm-runtime-incident-evidence-v1"
SCHEMA_VERSION = 1
MAX_BINDINGS = 256
SELECTOR_KINDS = {
    "position",
    "transition-id",
    "interaction-id",
    "landmark-id",
    "route-id",
    "preflight-reference",
}


class RuntimeIncidentEvidenceBridgeError(ValueError):
    pass


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
        raise RuntimeIncidentEvidenceBridgeError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise RuntimeIncidentEvidenceBridgeError(f"{label} must be an array")
    return value


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeIncidentEvidenceBridgeError(f"{label} must be a non-empty string")
    return value.strip()


def normalize_selector(document: Mapping[str, Any]) -> dict[str, Any]:
    selector = _object(document, "selector")
    if set(selector) != {"kind", "value"}:
        raise RuntimeIncidentEvidenceBridgeError("selector must contain exactly kind and value")
    kind = _nonempty_string(selector.get("kind"), "selector.kind")
    if kind not in SELECTOR_KINDS:
        raise RuntimeIncidentEvidenceBridgeError(f"unsupported selector kind: {kind}")
    value = selector.get("value")
    if kind == "position":
        if not isinstance(value, list) or len(value) != 3 or any(isinstance(item, bool) or not isinstance(item, int) for item in value):
            raise RuntimeIncidentEvidenceBridgeError("position selector value must be [x,y,z]")
        x, y, z = value
        if not (0 <= x <= 65535 and 0 <= y <= 65535 and 0 <= z <= 15):
            raise RuntimeIncidentEvidenceBridgeError("position selector value is outside OTBM coordinate range")
        return {"kind": kind, "value": [x, y, z]}
    return {"kind": kind, "value": _nonempty_string(value, "selector.value")}


def selector_key(selector: Mapping[str, Any]) -> str:
    return canonical_json(normalize_selector(selector))


def _normalize_context_references(value: Any, label: str) -> list[str]:
    if value is None:
        return []
    references = _array(value, label)
    normalized = sorted({_nonempty_string(item, f"{label}[]") for item in references})
    return normalized


def normalize_bindings(document: Mapping[str, Any]) -> dict[str, Any]:
    root = _object(document, "bindings document")
    if root.get("format") != BINDINGS_FORMAT or root.get("schemaVersion") != SCHEMA_VERSION:
        raise RuntimeIncidentEvidenceBridgeError(
            f"bindings document must use {BINDINGS_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    bindings = _array(root.get("bindings"), "bindings")
    if not 1 <= len(bindings) <= MAX_BINDINGS:
        raise RuntimeIncidentEvidenceBridgeError(f"bindings must contain 1..{MAX_BINDINGS} entries")

    binding_ids: set[str] = set()
    selector_keys: set[str] = set()
    normalized_bindings: list[dict[str, Any]] = []
    for index, raw_binding in enumerate(bindings):
        binding = _object(raw_binding, f"bindings[{index}]")
        binding_id = _nonempty_string(binding.get("id"), f"bindings[{index}].id")
        if binding_id in binding_ids:
            raise RuntimeIncidentEvidenceBridgeError(f"duplicate binding id: {binding_id}")
        selector = normalize_selector(_object(binding.get("selector"), f"bindings[{index}].selector"))
        key = canonical_json(selector)
        if key in selector_keys:
            raise RuntimeIncidentEvidenceBridgeError(f"duplicate/ambiguous selector binding: {key}")
        sources = binding.get("sources")
        try:
            gateway_manifest = normalize_manifest(
                {
                    "format": MANIFEST_FORMAT,
                    "schemaVersion": 1,
                    "sources": sources,
                }
            )
        except EvidenceGatewayError as exc:
            raise RuntimeIncidentEvidenceBridgeError(
                f"bindings[{index}] has invalid QA-018 source/extract specification: {exc}"
            ) from exc
        normalized_bindings.append(
            {
                "id": binding_id,
                "selector": selector,
                "sources": gateway_manifest["sources"],
                "contextReferences": _normalize_context_references(
                    binding.get("contextReferences"), f"bindings[{index}].contextReferences"
                ),
            }
        )
        binding_ids.add(binding_id)
        selector_keys.add(key)

    normalized_bindings.sort(key=lambda item: item["id"])
    return {
        "format": BINDINGS_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "bindings": normalized_bindings,
    }


def resolve_binding(bindings: Mapping[str, Any], selector: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_bindings(bindings)
    wanted = normalize_selector(selector)
    key = canonical_json(wanted)
    matches = [item for item in normalized["bindings"] if canonical_json(item["selector"]) == key]
    if not matches:
        raise RuntimeIncidentEvidenceBridgeError(f"no reviewed incident evidence binding matches selector {key}")
    if len(matches) != 1:
        raise RuntimeIncidentEvidenceBridgeError(f"ambiguous incident evidence binding for selector {key}")
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
        raise RuntimeIncidentEvidenceBridgeError(f"selected binding cannot produce a QA-018 manifest: {exc}") from exc


def build_incident_evidence_plan(
    bindings: Mapping[str, Any],
    selector: Mapping[str, Any],
    *,
    bindings_file_sha256: str,
) -> dict[str, Any]:
    normalized = normalize_bindings(bindings)
    selected = resolve_binding(normalized, selector)
    gateway_manifest = _gateway_manifest(selected)
    if not isinstance(bindings_file_sha256, str) or len(bindings_file_sha256) != 64 or any(
        char not in "0123456789abcdef" for char in bindings_file_sha256
    ):
        raise RuntimeIncidentEvidenceBridgeError("bindings_file_sha256 must be a lowercase SHA-256 digest")
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "mode": "plan",
        "bindings": {
            "format": BINDINGS_FORMAT,
            "fileSha256": bindings_file_sha256,
            "canonicalSha256": canonical_sha256(normalized),
        },
        "bindingId": selected["id"],
        "selector": selected["selector"],
        "contextReferences": selected["contextReferences"],
        "gatewayManifest": gateway_manifest,
        "evidenceBundle": None,
        "evidenceBundleSha256": None,
        "policy": {
            "reviewedSelectorsOnly": True,
            "parsesRuntimeLogs": False,
            "infersSelectors": False,
            "parsesOtbm": False,
            "rebuildsWorldIndex": False,
            "validatesSourceSemantics": False,
            "classifiesFailure": False,
            "diagnosesRootCause": False,
            "pathfinds": False,
            "regeneratesRouteOrPreflight": False,
            "runsE2e": False,
            "mutatesMapOrEvidence": False,
            "emitsNextAction": False,
            "qa018EvidenceGatewayReused": True,
        },
    }
    report["reportSha256"] = canonical_sha256(report)
    return report


def execute_incident_evidence_plan(
    bindings_path: Path,
    plan: Mapping[str, Any],
) -> dict[str, Any]:
    if plan.get("format") != REPORT_FORMAT or plan.get("schemaVersion") != SCHEMA_VERSION or plan.get("mode") != "plan":
        raise RuntimeIncidentEvidenceBridgeError(f"plan must use {REPORT_FORMAT} schemaVersion 1 in plan mode")
    provided_hash = plan.get("reportSha256")
    if not isinstance(provided_hash, str):
        raise RuntimeIncidentEvidenceBridgeError("plan.reportSha256 is required")
    unsigned_plan = dict(plan)
    unsigned_plan.pop("reportSha256", None)
    if canonical_sha256(unsigned_plan) != provided_hash:
        raise RuntimeIncidentEvidenceBridgeError("plan reportSha256 does not match canonical plan content")

    source = bindings_path.expanduser()
    if source.is_symlink():
        raise RuntimeIncidentEvidenceBridgeError(f"bindings input must not be a symlink: {bindings_path}")
    source = source.resolve(strict=True)
    expected_file_sha = plan.get("bindings", {}).get("fileSha256") if isinstance(plan.get("bindings"), Mapping) else None
    if sha256_path(source) != expected_file_sha:
        raise RuntimeIncidentEvidenceBridgeError("bindings file SHA-256 changed after plan creation")

    gateway_manifest = _object(plan.get("gatewayManifest"), "plan.gatewayManifest")
    try:
        bundle = build_evidence_bundle(source, dict(gateway_manifest))
    except EvidenceGatewayError as exc:
        raise RuntimeIncidentEvidenceBridgeError(f"QA-018 evidence extraction failed: {exc}") from exc
    if bundle.get("format") != BUNDLE_FORMAT or not isinstance(bundle.get("bundleSha256"), str):
        raise RuntimeIncidentEvidenceBridgeError("QA-018 returned an invalid evidence bundle contract")

    report = dict(plan)
    report.pop("reportSha256", None)
    report["mode"] = "executed"
    report["evidenceBundle"] = bundle
    report["evidenceBundleSha256"] = bundle["bundleSha256"]
    report["reportSha256"] = canonical_sha256(report)
    return report


def _atomic_write_text(path: Path, content: str, *, overwrite: bool) -> None:
    if path.is_symlink():
        raise RuntimeIncidentEvidenceBridgeError(f"output must not be a symlink: {path}")
    if path.exists() and not overwrite:
        raise RuntimeIncidentEvidenceBridgeError(f"output already exists: {path}; pass overwrite=True")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.is_symlink():
        raise RuntimeIncidentEvidenceBridgeError(f"temporary output must not be a symlink: {temporary}")
    temporary.unlink(missing_ok=True)
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_report(path: Path, report: Mapping[str, Any], *, overwrite: bool = False) -> None:
    _atomic_write_text(path, json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n", overwrite=overwrite)


def source_paths_for_plan(bindings_path: Path, plan: Mapping[str, Any]) -> list[Path]:
    root = bindings_path.expanduser().resolve(strict=True).parent
    manifest = _object(plan.get("gatewayManifest"), "plan.gatewayManifest")
    result: list[Path] = []
    for source in _array(manifest.get("sources"), "plan.gatewayManifest.sources"):
        source_spec = _object(source, "plan.gatewayManifest.sources[]")
        relative = Path(_nonempty_string(source_spec.get("path"), "source.path"))
        candidate = (root / relative).resolve(strict=False)
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise RuntimeIncidentEvidenceBridgeError(f"source path escapes bindings directory: {relative}") from exc
        result.append(candidate)
    return result
