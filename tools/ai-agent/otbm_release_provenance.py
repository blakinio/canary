from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

BOM_FORMAT = "canary-otbm-release-bom-v1"
REPORT_FORMAT = "canary-otbm-release-provenance-v1"
SCHEMA_VERSION = 1
ALLOWED_KINDS = {
    "source-map", "world-index", "scanner", "items", "appearances", "asset-index", "datapack",
    "script-resolution", "transition-manifest", "landmark-registry", "interaction-registry",
    "quality-evidence", "coverage-evidence", "certification-evidence", "other",
}


class ReleaseProvenanceError(RuntimeError):
    pass


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise ReleaseProvenanceError(f"{label} must be a SHA-256 hex string")
    return value.lower()


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_bom(path: Path) -> dict[str, Any]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        document = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseProvenanceError(f"Cannot read BOM {source}: {exc}") from exc
    return normalize_bom(document)


def normalize_bom(document: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(document, dict) or document.get("format") != BOM_FORMAT:
        raise ReleaseProvenanceError(f"BOM format must be {BOM_FORMAT}")
    release_id = document.get("releaseId")
    if not isinstance(release_id, str) or not release_id.strip():
        raise ReleaseProvenanceError("releaseId must be a non-empty string")
    raw_components = document.get("components")
    raw_dimensions = document.get("dimensions")
    if not isinstance(raw_components, list) or not isinstance(raw_dimensions, list):
        raise ReleaseProvenanceError("components and dimensions must be arrays")
    components: list[dict[str, Any]] = []
    component_ids: set[str] = set()
    for index, entry in enumerate(raw_components):
        if not isinstance(entry, dict):
            raise ReleaseProvenanceError(f"components[{index}] must be an object")
        identifier = entry.get("id")
        kind = entry.get("kind")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in component_ids:
            raise ReleaseProvenanceError(f"components[{index}].id must be unique and non-empty")
        if kind not in ALLOWED_KINDS:
            raise ReleaseProvenanceError(f"components[{index}].kind is unsupported: {kind!r}")
        component_ids.add(identifier)
        normalized = {"id": identifier, "kind": kind, "sha256": _sha(entry.get("sha256"), f"components[{index}].sha256")}
        if isinstance(entry.get("format"), str) and entry["format"].strip():
            normalized["format"] = entry["format"]
        components.append(normalized)
    dimensions: list[dict[str, Any]] = []
    dimension_ids: set[str] = set()
    for index, entry in enumerate(raw_dimensions):
        if not isinstance(entry, dict):
            raise ReleaseProvenanceError(f"dimensions[{index}] must be an object")
        identifier = entry.get("id")
        depends = entry.get("dependsOn")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in dimension_ids:
            raise ReleaseProvenanceError(f"dimensions[{index}].id must be unique and non-empty")
        if not isinstance(depends, list) or not depends or any(not isinstance(value, str) for value in depends):
            raise ReleaseProvenanceError(f"dimensions[{index}].dependsOn must be a non-empty string array")
        unknown = sorted(set(depends) - component_ids)
        if unknown:
            raise ReleaseProvenanceError(f"dimensions[{index}] references unknown components: {unknown}")
        dimension_ids.add(identifier)
        dimensions.append({"id": identifier, "dependsOn": sorted(set(depends))})
    components.sort(key=lambda value: value["id"])
    dimensions.sort(key=lambda value: value["id"])
    return {"format": BOM_FORMAT, "schemaVersion": SCHEMA_VERSION, "releaseId": release_id, "components": components, "dimensions": dimensions}


def build_release_provenance_report(current: dict[str, Any], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    current = normalize_bom(current)
    previous = normalize_bom(previous) if previous is not None else None
    current_components = {entry["id"]: entry for entry in current["components"]}
    previous_components = {entry["id"]: entry for entry in previous["components"]} if previous is not None else {}
    changes: list[dict[str, Any]] = []
    changed_ids: set[str] = set()
    if previous is not None:
        for identifier in sorted(set(current_components) | set(previous_components)):
            before = previous_components.get(identifier)
            after = current_components.get(identifier)
            if before is None:
                status = "added"
            elif after is None:
                status = "removed"
            elif before["sha256"] != after["sha256"] or before.get("format") != after.get("format") or before["kind"] != after["kind"]:
                status = "changed"
            else:
                continue
            changed_ids.add(identifier)
            changes.append({"componentId": identifier, "status": status, "before": before, "after": after})
    stale: list[dict[str, Any]] = []
    for dimension in current["dimensions"]:
        impacted = sorted(changed_ids.intersection(dimension["dependsOn"]))
        if impacted:
            stale.append({"dimensionId": dimension["id"], "status": "stale", "changedDependencies": impacted})
        else:
            stale.append({"dimensionId": dimension["id"], "status": "current" if previous is not None else "not-compared", "changedDependencies": []})
    missing_previous_dimensions: list[str] = []
    if previous is not None:
        current_dimension_ids = {entry["id"] for entry in current["dimensions"]}
        missing_previous_dimensions = sorted(entry["id"] for entry in previous["dimensions"] if entry["id"] not in current_dimension_ids)
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "currentReleaseId": current["releaseId"],
        "previousReleaseId": previous["releaseId"] if previous is not None else None,
        "currentBomSha256": _json_hash(current),
        "previousBomSha256": _json_hash(previous) if previous is not None else None,
        "componentChanges": changes,
        "dimensionFreshness": stale,
        "removedDimensions": missing_previous_dimensions,
        "summary": {
            "componentCount": len(current_components),
            "changedComponentCount": len(changes),
            "staleDimensionCount": sum(1 for entry in stale if entry["status"] == "stale"),
            "comparisonPerformed": previous is not None,
        },
        "policy": {
            "timestampsUsedAsFreshnessEvidence": False,
            "rerunsValidators": False,
            "rerunsSemanticDiff": False,
            "rerunsPhysicalE2e": False,
            "mutatesEvidenceOrCertification": False,
            "runtimeCompatibilityProven": False,
        },
    }
    report["reportSha256"] = _json_hash(report)
    return report
