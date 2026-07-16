from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

REPORT_FORMAT = "canary-otbm-map-quality-v1"
SCHEMA_VERSION = 1
GEOMETRY_FORMAT = "canary-otbm-geometry-audit-v1"
REACHABILITY_FORMAT = "canary-otbm-reachability-v1"
SCRIPT_RESOLUTION_FORMAT = "canary-otbm-script-resolution-v1"
COMPONENT_ORDER = ("geometry", "reachability", "scriptResolution")
OUTCOMES = ("error", "warning", "unresolved", "info")
OUTCOME_ORDER = {name: index for index, name in enumerate(OUTCOMES)}
SCRIPT_UNRESOLVED_STATUSES = {"unresolved", "referenced-only", "partially-resolved"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DEFAULT_SAMPLE_LIMIT = 500
MAX_SAMPLE_LIMIT = 10_000


class MapQualityError(ValueError):
    """Raised when component evidence cannot be combined safely."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MapQualityError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise MapQualityError(f"{label} must be an array")
    return value


def _count(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MapQualityError(f"{label} must be a non-negative integer")
    return value


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise MapQualityError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _position(value: Any) -> list[int] | None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 3:
        return None
    if any(isinstance(entry, bool) or not isinstance(entry, int) for entry in value):
        return None
    x, y, z = (int(entry) for entry in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        return None
    return [x, y, z]


def _component_source_sha256(component: str, report: Mapping[str, Any]) -> str:
    if component == "geometry":
        if report.get("format") != GEOMETRY_FORMAT:
            raise MapQualityError(f"geometry report must use format {GEOMETRY_FORMAT}")
        provenance = _mapping(report.get("provenance"), "geometry.provenance")
        source = _mapping(provenance.get("source"), "geometry.provenance.source")
        return _sha256(source.get("sha256"), "geometry.provenance.source.sha256")

    if component == "reachability":
        if report.get("format") != REACHABILITY_FORMAT:
            raise MapQualityError(f"reachability report must use format {REACHABILITY_FORMAT}")
        provenance = _mapping(report.get("provenance"), "reachability.provenance")
        manifest = _mapping(
            provenance.get("worldIndexManifest"),
            "reachability.provenance.worldIndexManifest",
        )
        source = _mapping(manifest.get("source"), "reachability.provenance.worldIndexManifest.source")
        return _sha256(source.get("sha256"), "reachability.provenance.worldIndexManifest.source.sha256")

    if component == "scriptResolution":
        if report.get("format") != SCRIPT_RESOLUTION_FORMAT:
            raise MapQualityError(f"script-resolution report must use format {SCRIPT_RESOLUTION_FORMAT}")
        sources = _mapping(report.get("sources"), "scriptResolution.sources")
        item_audit = _mapping(sources.get("itemAudit"), "scriptResolution.sources.itemAudit")
        source = _mapping(item_audit.get("map"), "scriptResolution.sources.itemAudit.map")
        return _sha256(source.get("sha256"), "scriptResolution.sources.itemAudit.map.sha256")

    raise MapQualityError(f"unsupported quality component: {component}")


def _canonical_finding_id(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def _normalized_finding(
    *,
    component: str,
    outcome: str,
    kind: str,
    message: str,
    position: Any = None,
    source_id: str | None = None,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if outcome not in OUTCOMES:
        raise MapQualityError(f"unsupported normalized outcome: {outcome}")
    payload: dict[str, Any] = {
        "component": component,
        "outcome": outcome,
        "kind": str(kind),
        "message": str(message),
    }
    normalized_position = _position(position)
    if normalized_position is not None:
        payload["position"] = normalized_position
    if source_id:
        payload["sourceId"] = str(source_id)
    if evidence is not None:
        payload["evidence"] = dict(evidence)
    payload["id"] = _canonical_finding_id(payload)
    return payload


def _geometry_component(report: Mapping[str, Any]) -> tuple[dict[str, int], list[dict[str, Any]], dict[str, Any]]:
    summary = _mapping(report.get("summary"), "geometry.summary")
    finding_summary = _mapping(summary.get("findings"), "geometry.summary.findings")
    by_severity = _mapping(finding_summary.get("bySeverity"), "geometry.summary.findings.bySeverity")
    counts = {
        "error": _count(by_severity.get("error", 0), "geometry error count"),
        "warning": _count(by_severity.get("warning", 0), "geometry warning count"),
        "unresolved": 0,
        "info": _count(by_severity.get("info", 0), "geometry info count"),
    }
    samples: list[dict[str, Any]] = []
    for raw in _list(report.get("findings"), "geometry.findings"):
        finding = _mapping(raw, "geometry finding")
        severity = str(finding.get("severity", ""))
        if severity not in {"error", "warning", "info"}:
            raise MapQualityError(f"geometry finding has unsupported severity: {severity!r}")
        samples.append(
            _normalized_finding(
                component="geometry",
                outcome=severity,
                kind=str(finding.get("kind", "unknown")),
                message=str(finding.get("message", "")),
                position=finding.get("position"),
                source_id=str(finding.get("id")) if finding.get("id") is not None else None,
                evidence=finding,
            )
        )
    scope = _mapping(report.get("scope"), "geometry.scope")
    meta = {
        "inputOk": bool(report.get("ok")),
        "inputComplete": bool(report.get("complete")),
        "findingsTruncated": bool(finding_summary.get("truncated")),
        "scope": {"from": scope.get("from"), "to": scope.get("to")},
    }
    return counts, samples, meta


def _reachability_component(
    report: Mapping[str, Any],
) -> tuple[dict[str, int], list[dict[str, Any]], dict[str, Any]]:
    summary = _mapping(report.get("summary"), "reachability.summary")
    finding_summary = _mapping(summary.get("findings"), "reachability.summary.findings")
    by_severity = _mapping(finding_summary.get("bySeverity"), "reachability.summary.findings.bySeverity")
    counts = {
        "error": _count(by_severity.get("error", 0), "reachability error count"),
        "warning": _count(by_severity.get("warning", 0), "reachability warning count"),
        "unresolved": 0,
        "info": _count(by_severity.get("info", 0), "reachability info count"),
    }
    samples: list[dict[str, Any]] = []
    for raw in _list(report.get("findings"), "reachability.findings"):
        finding = _mapping(raw, "reachability finding")
        severity = str(finding.get("severity", ""))
        if severity not in {"error", "warning", "info"}:
            raise MapQualityError(f"reachability finding has unsupported severity: {severity!r}")
        position = finding.get("position")
        if position is None:
            position = finding.get("source")
        samples.append(
            _normalized_finding(
                component="reachability",
                outcome=severity,
                kind=str(finding.get("code", "unknown")),
                message=str(finding.get("message", "")),
                position=position,
                evidence=finding,
            )
        )
    region = _mapping(report.get("region"), "reachability.region")
    meta = {
        "inputOk": bool(report.get("ok")),
        "inputComplete": True,
        "findingsTruncated": bool(finding_summary.get("truncated")),
        "scope": {"from": region.get("from"), "to": region.get("to")},
    }
    return counts, samples, meta


def _script_component(report: Mapping[str, Any]) -> tuple[dict[str, int], list[dict[str, Any]], dict[str, Any]]:
    summary = _mapping(report.get("summary"), "scriptResolution.summary")
    counts = {
        "error": _count(summary.get("conflictingPlacements", 0), "script-resolution conflicting placement count"),
        "warning": 0,
        "unresolved": _count(
            summary.get("runtimeUnresolvedPlacements", 0),
            "script-resolution runtime unresolved placement count",
        ),
        "info": 0,
    }
    samples: list[dict[str, Any]] = []
    observed_errors = 0
    observed_unresolved = 0
    for raw in _list(report.get("placements"), "scriptResolution.placements"):
        placement = _mapping(raw, "script-resolution placement")
        status = str(placement.get("status", "unknown"))
        if status == "conflicting":
            observed_errors += 1
            samples.append(
                _normalized_finding(
                    component="scriptResolution",
                    outcome="error",
                    kind="conflicting-runtime-handlers",
                    message="Map mechanic placement has conflicting runtime handler evidence.",
                    position=placement.get("position"),
                    source_id=str(placement.get("index")) if placement.get("index") is not None else None,
                    evidence=placement,
                )
            )
        elif status in SCRIPT_UNRESOLVED_STATUSES:
            observed_unresolved += 1
            samples.append(
                _normalized_finding(
                    component="scriptResolution",
                    outcome="unresolved",
                    kind=f"runtime-{status}",
                    message=f"Map mechanic placement remains {status} in static runtime resolution evidence.",
                    position=placement.get("position"),
                    source_id=str(placement.get("index")) if placement.get("index") is not None else None,
                    evidence=placement,
                )
            )
    if observed_errors != counts["error"]:
        raise MapQualityError(
            "script-resolution conflicting placement summary does not match placement evidence: "
            f"summary={counts['error']}, placements={observed_errors}"
        )
    if observed_unresolved != counts["unresolved"]:
        raise MapQualityError(
            "script-resolution unresolved placement summary does not match placement evidence: "
            f"summary={counts['unresolved']}, placements={observed_unresolved}"
        )
    meta = {
        "inputOk": bool(report.get("ok")),
        "inputComplete": True,
        "findingsTruncated": False,
        "scope": None,
        "unreviewedIdentifiers": _count(
            summary.get("unreviewedIdentifiers", 0),
            "script-resolution unreviewed identifier count",
        ),
        "unresolvedDynamicRegistrations": _count(
            summary.get("unresolvedDynamicRegistrations", 0),
            "script-resolution unresolved dynamic registration count",
        ),
    }
    return counts, samples, meta


def _finding_sort_key(finding: Mapping[str, Any]) -> tuple[Any, ...]:
    position = _position(finding.get("position")) or [0x10000, 0x10000, 16]
    return (
        OUTCOME_ORDER[str(finding["outcome"])],
        COMPONENT_ORDER.index(str(finding["component"])),
        position[2],
        position[1],
        position[0],
        str(finding.get("kind", "")),
        str(finding.get("id", "")),
    )


def _severity_gate_failed(counts: Mapping[str, int], fail_on_severity: str) -> bool:
    if fail_on_severity == "none":
        return False
    if fail_on_severity == "error":
        return counts["error"] > 0
    if fail_on_severity == "warning":
        return counts["error"] > 0 or counts["warning"] > 0
    raise MapQualityError("fail_on_severity must be one of: none, error, warning")


def build_quality_report(
    *,
    geometry: Mapping[str, Any],
    reachability: Mapping[str, Any],
    script_resolution: Mapping[str, Any],
    input_pins: Mapping[str, Mapping[str, Any]],
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
    fail_on_severity: str = "error",
    fail_on_unresolved: bool = False,
) -> dict[str, Any]:
    if isinstance(sample_limit, bool) or not isinstance(sample_limit, int) or not 1 <= sample_limit <= MAX_SAMPLE_LIMIT:
        raise MapQualityError(f"sample_limit must be in 1..{MAX_SAMPLE_LIMIT}")
    if fail_on_severity not in {"none", "error", "warning"}:
        raise MapQualityError("fail_on_severity must be one of: none, error, warning")

    reports = {
        "geometry": geometry,
        "reachability": reachability,
        "scriptResolution": script_resolution,
    }
    source_hashes = {
        component: _component_source_sha256(component, report)
        for component, report in reports.items()
    }
    if len(set(source_hashes.values())) != 1:
        raise MapQualityError(
            "component reports do not prove the same source map SHA-256: "
            + ", ".join(f"{name}={value}" for name, value in source_hashes.items())
        )
    source_sha256 = next(iter(source_hashes.values()))

    missing_pins = [component for component in COMPONENT_ORDER if component not in input_pins]
    if missing_pins:
        raise MapQualityError(f"missing input report pins: {', '.join(missing_pins)}")

    component_builders = {
        "geometry": _geometry_component,
        "reachability": _reachability_component,
        "scriptResolution": _script_component,
    }
    total_counts = {outcome: 0 for outcome in OUTCOMES}
    all_samples: list[dict[str, Any]] = []
    components: dict[str, Any] = {}
    scopes: dict[str, Any] = {}

    for component in COMPONENT_ORDER:
        report = reports[component]
        counts, samples, meta = component_builders[component](report)
        for outcome in OUTCOMES:
            total_counts[outcome] += counts[outcome]
        all_samples.extend(samples)
        pin = _mapping(input_pins[component], f"{component} input pin")
        pin_format = pin.get("format")
        if pin_format != report.get("format"):
            raise MapQualityError(
                f"{component} input pin format {pin_format!r} does not match report format {report.get('format')!r}"
            )
        components[component] = {
            "format": report.get("format"),
            "sourceSha256": source_hashes[component],
            "input": dict(pin),
            "inputOk": meta["inputOk"],
            "inputComplete": meta["inputComplete"],
            "outcomeCounts": counts,
            "findingsAvailableForSampling": len(samples),
            "findingsTruncatedByComponent": meta["findingsTruncated"],
        }
        if component == "scriptResolution":
            components[component]["unreviewedIdentifiers"] = meta["unreviewedIdentifiers"]
            components[component]["unresolvedDynamicRegistrations"] = meta["unresolvedDynamicRegistrations"]
        if meta["scope"] is not None:
            scopes[component] = meta["scope"]

    all_samples.sort(key=_finding_sort_key)
    sampled = all_samples[:sample_limit]
    total = sum(total_counts.values())
    same_region = (
        scopes.get("geometry") == scopes.get("reachability")
        if "geometry" in scopes and "reachability" in scopes
        else False
    )
    severity_failed = _severity_gate_failed(total_counts, fail_on_severity)
    unresolved_failed = fail_on_unresolved and total_counts["unresolved"] > 0
    ok = not severity_failed and not unresolved_failed

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": ok,
        "source": {"sha256": source_sha256},
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "otbmParsedIndependently": False,
            "gameplayCorrectnessProven": False,
            "playerIntentProven": False,
            "crossComponentDeduplication": False,
            "failOnSeverity": fail_on_severity,
            "failOnUnresolved": bool(fail_on_unresolved),
            "sampleLimit": sample_limit,
        },
        "coverage": {
            "geometry": scopes.get("geometry"),
            "reachability": scopes.get("reachability"),
            "sameRegion": same_region,
            "globalCoverageProven": False,
        },
        "components": components,
        "summary": {
            "total": total,
            "outcomeCounts": total_counts,
            "sampled": len(sampled),
            "truncated": total > len(sampled),
            "availableForSampling": len(all_samples),
        },
        "findings": sampled,
        "notes": [
            "Counts are component evidence events; cross-component findings are not deduplicated into inferred defects.",
            "Unresolved runtime evidence remains unresolved even when a review disposition exists.",
            "A green quality gate is static evidence only and does not prove gameplay correctness or player intent.",
        ],
    }
