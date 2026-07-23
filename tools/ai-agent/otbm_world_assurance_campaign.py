from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Mapping, Sequence

MANIFEST_FORMAT = "canary-otbm-world-assurance-campaign-manifest-v1"
REPORT_FORMAT = "canary-otbm-world-assurance-campaign-v1"
COVERAGE_FORMAT = "canary-otbm-coverage-dashboard-v1"
CERTIFICATION_FORMAT = "canary-otbm-region-quest-certification-v1"
FRESHNESS_FORMAT = "canary-otbm-release-provenance-v1"
EVIDENCE_BUNDLE_FORMAT = "canary-otbm-evidence-bundle-v1"
SCHEMA_VERSION = 1

TARGET_CLASSES = {"region", "landmark-route", "quest", "mechanic-set"}
DIMENSIONS = (
    "indexedOnExactMap", "sourceCorrelated", "scriptResolved", "staticallyReachable",
    "interactionResolved", "staticQualityCompatible", "executableRouteCovered",
    "physicallyRuntimeProven", "candidateMapValidated",
)
LEVELS = (
    "C0_NOT_EVALUATED", "C1_STATIC_INDEXED", "C2_STATIC_CORRELATED",
    "C3_STATIC_REACHABLE", "C4_STATIC_QUALITY_GREEN", "C5_PHYSICAL_ROUTE_PROVEN",
    "C6_FEATURE_OR_MECHANIC_PHYSICALLY_PROVEN", "C7_CANDIDATE_CHANGE_REVALIDATED",
)
MAX_LEVEL = {
    "region": "C5_PHYSICAL_ROUTE_PROVEN",
    "landmark-route": "C5_PHYSICAL_ROUTE_PROVEN",
    "quest": "C7_CANDIDATE_CHANGE_REVALIDATED",
    "mechanic-set": "C7_CANDIDATE_CHANGE_REVALIDATED",
}


class WorldAssuranceCampaignError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def _obj(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WorldAssuranceCampaignError(f"{label} must be an object")
    return value


def _arr(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise WorldAssuranceCampaignError(f"{label} must be an array")
    return value


def _str(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorldAssuranceCampaignError(f"{label} must be a non-empty string")
    return value.strip()


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise WorldAssuranceCampaignError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _pos(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 3 or any(isinstance(v, bool) or not isinstance(v, int) for v in value):
        raise WorldAssuranceCampaignError(f"{label} must be [x,y,z]")
    if not (0 <= value[0] <= 65535 and 0 <= value[1] <= 65535 and 0 <= value[2] <= 15):
        raise WorldAssuranceCampaignError(f"{label} is outside OTBM coordinate range")
    return list(value)


def _strings(value: Any, label: str) -> list[str]:
    return sorted({_str(v, f"{label}[]") for v in _arr(value, label)})


def _pin(value: Any, expected_format: str, label: str) -> dict[str, Any]:
    value = _obj(value, label)
    size = value.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise WorldAssuranceCampaignError(f"{label}.size must be a non-negative integer")
    if value.get("format") != expected_format:
        raise WorldAssuranceCampaignError(f"{label}.format must be {expected_format}")
    return {"fileName": _str(value.get("fileName"), f"{label}.fileName"), "size": size,
            "sha256": _sha(value.get("sha256"), f"{label}.sha256"), "format": expected_format}


def _artifact_pin(value: Any, label: str) -> dict[str, Any]:
    value = _obj(value, label)
    size = value.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise WorldAssuranceCampaignError(f"{label}.size must be a non-negative integer")
    return {"fileName": _str(value.get("fileName"), f"{label}.fileName"), "size": size,
            "sha256": _sha(value.get("sha256"), f"{label}.sha256")}


def _normalize_target(raw: Any, index: int) -> dict[str, Any]:
    target = _obj(raw, f"targets[{index}]")
    target_id = _str(target.get("id"), f"targets[{index}].id")
    target_class = target.get("class")
    if target_class not in TARGET_CLASSES:
        raise WorldAssuranceCampaignError(f"target {target_id} has unsupported class")
    reviewed = _obj(target.get("reviewedDefinition"), f"target {target_id}.reviewedDefinition")
    if reviewed.get("reviewStatus") != "reviewed":
        raise WorldAssuranceCampaignError(f"target {target_id} must be reviewed")
    bounds = _obj(reviewed.get("routingBounds"), f"target {target_id}.routingBounds")
    start, end = _pos(bounds.get("from"), "routingBounds.from"), _pos(bounds.get("to"), "routingBounds.to")
    if any(start[i] > end[i] for i in range(3)):
        raise WorldAssuranceCampaignError(f"target {target_id} routing bounds are invalid")
    reviewed_norm = {
        "reviewStatus": "reviewed", "fromLandmarkId": _str(reviewed.get("fromLandmarkId"), "fromLandmarkId"),
        "toLandmarkId": _str(reviewed.get("toLandmarkId"), "toLandmarkId"),
        "regionId": _str(reviewed.get("regionId"), "regionId"), "origin": _pos(reviewed.get("origin"), "origin"),
        "destination": _pos(reviewed.get("destination"), "destination"),
        "routingBounds": {"from": start, "to": end}, "references": _strings(reviewed.get("references"), "references"),
    }
    provenance = _obj(target.get("provenance"), f"target {target_id}.provenance")
    provenance_norm = {"sourceMapSha256": _sha(provenance.get("sourceMapSha256"), "sourceMapSha256"),
                       "worldIndexSha256": _sha(provenance.get("worldIndexSha256"), "worldIndexSha256")}
    qa005 = _obj(target.get("qa005"), f"target {target_id}.qa005")
    qa006 = _obj(target.get("qa006"), f"target {target_id}.qa006")
    for name, binding in (("qa005", qa005), ("qa006", qa006)):
        if binding.get("bindingState") not in {"bound", "unavailable"}:
            raise WorldAssuranceCampaignError(f"target {target_id}.{name}.bindingState is invalid")
        if binding.get("bindingState") == "unavailable" and not binding.get("blockers"):
            raise WorldAssuranceCampaignError(f"target {target_id}.{name} unavailable binding requires blockers")
    if qa006.get("bindingState") == "bound" and qa005.get("bindingState") != "bound":
        raise WorldAssuranceCampaignError(f"target {target_id} cannot bind QA-006 without QA-005")
    maximum = qa006.get("maximumLevel")
    if maximum not in LEVELS[1:] or LEVELS.index(maximum) > LEVELS.index(MAX_LEVEL[target_class]):
        raise WorldAssuranceCampaignError(f"target {target_id} requests an invalid maximum certification level")
    qa016 = _obj(target.get("qa016"), f"target {target_id}.qa016")
    freshness_ids = _strings(qa016.get("freshnessDimensionIds"), "freshnessDimensionIds")
    if not freshness_ids:
        raise WorldAssuranceCampaignError(f"target {target_id} requires QA-016 freshness dimensions")
    qa018 = _obj(target.get("qa018"), f"target {target_id}.qa018")
    extracts = []
    for e in _arr(qa018.get("requiredExtracts"), "requiredExtracts"):
        e = _obj(e, "requiredExtract")
        extracts.append({"id": _str(e.get("id"), "requiredExtract.id"),
                         "sourceSha256": _sha(e.get("sourceSha256"), "requiredExtract.sourceSha256"),
                         "valueSha256": _sha(e.get("valueSha256"), "requiredExtract.valueSha256")})
    physical = _obj(target.get("physicalE2e"), f"target {target_id}.physicalE2e")
    if physical.get("status") not in {"retained-success", "missing"}:
        raise WorldAssuranceCampaignError(f"target {target_id}.physicalE2e.status is invalid")
    physical_norm = dict(physical)
    if physical["status"] == "retained-success":
        physical_norm["artifactDigestSha256"] = _sha(physical.get("artifactDigestSha256"), "artifactDigestSha256")
        physical_norm["runtimeMapSha256"] = _sha(physical.get("runtimeMapSha256"), "runtimeMapSha256")
        physical_norm["resultFileSha256"] = _sha(physical.get("resultFileSha256"), "resultFileSha256")
        physical_norm["scenarioManifestFileSha256"] = _sha(physical.get("scenarioManifestFileSha256"), "scenarioManifestFileSha256")
        physical_norm["evidenceExtractIds"] = _strings(physical.get("evidenceExtractIds", []), "evidenceExtractIds")
        if physical_norm["runtimeMapSha256"] != provenance_norm["sourceMapSha256"]:
            raise WorldAssuranceCampaignError(f"target {target_id} Physical E2E runtime map provenance mismatch")
    return {
        "id": target_id, "class": target_class, "reviewedDefinition": reviewed_norm, "provenance": provenance_norm,
        "qa005": {"bindingState": qa005["bindingState"], "targetId": qa005.get("targetId"),
                  "blockers": _strings(qa005.get("blockers", []), "qa005.blockers")},
        "qa006": {"bindingState": qa006["bindingState"], "targetId": qa006.get("targetId"),
                  "maximumLevel": maximum, "blockers": _strings(qa006.get("blockers", []), "qa006.blockers")},
        "qa016": {"freshnessDimensionIds": freshness_ids}, "qa018": {"requiredExtracts": extracts},
        "routeEvidence": dict(_obj(target.get("routeEvidence"), "routeEvidence")), "physicalE2e": physical_norm,
        "unresolvedEvidence": _strings(target.get("unresolvedEvidence", []), "unresolvedEvidence"),
        "conflictingEvidence": _strings(target.get("conflictingEvidence", []), "conflictingEvidence"),
        "blockers": _strings(target.get("blockers", []), "blockers"),
    }


def normalize_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if manifest.get("format") != MANIFEST_FORMAT or manifest.get("schemaVersion") != 1:
        raise WorldAssuranceCampaignError(f"manifest must use {MANIFEST_FORMAT} schemaVersion 1")
    targets = [_normalize_target(raw, i) for i, raw in enumerate(_arr(manifest.get("targets"), "targets"))]
    if not targets:
        raise WorldAssuranceCampaignError("targets must not be empty")
    ids = [t["id"] for t in targets]
    if len(ids) != len(set(ids)):
        raise WorldAssuranceCampaignError("campaign target ids must be unique")
    return {"format": MANIFEST_FORMAT, "schemaVersion": 1,
            "campaignId": _str(manifest.get("campaignId"), "campaignId"),
            "targets": sorted(targets, key=lambda t: t["id"])}


def _report_map(report: Mapping[str, Any], expected_format: str, label: str) -> dict[str, str]:
    if report.get("format") != expected_format or report.get("schemaVersion") != 1:
        raise WorldAssuranceCampaignError(f"{label} must use {expected_format} schemaVersion 1")
    current = _obj(report.get("currentMap"), f"{label}.currentMap")
    return {"sourceMapSha256": _sha(current.get("mapSha256"), f"{label}.mapSha256"),
            "worldIndexSha256": _sha(current.get("worldIndexSha256"), f"{label}.worldIndexSha256")}


def _coverage(target: dict[str, Any], report: Mapping[str, Any] | None) -> tuple[dict[str, Any], list[str]]:
    binding = target["qa005"]
    if binding["bindingState"] == "unavailable":
        blockers = binding["blockers"]
        dims = {name: {"state": "not-evaluated", "evidence": [], "memberIds": [], "blockers": blockers} for name in DIMENSIONS}
        return {"sourceReportPresent": False, "targetId": None, "dimensions": dims,
                "currentMapProvenance": {"state": "not-evaluated", "evidence": [], "blockers": blockers},
                "requirementsSatisfied": False}, blockers
    if report is None:
        raise WorldAssuranceCampaignError(f"target {target['id']} binds QA-005 but no report was supplied")
    if _report_map(report, COVERAGE_FORMAT, "QA-005") != target["provenance"]:
        raise WorldAssuranceCampaignError(f"target {target['id']} QA-005 map/World Index provenance mismatch")
    found = next((v for v in _arr(report.get("targets"), "QA-005.targets") if v.get("id") == binding["targetId"]), None)
    if found is None:
        raise WorldAssuranceCampaignError(f"target {target['id']} references missing QA-005 target")
    if found.get("kind") != target["class"]:
        raise WorldAssuranceCampaignError(f"target {target['id']} QA-005 target class mismatch")
    dims = _obj(found.get("dimensions"), "QA-005 target dimensions")
    normalized = {}
    for name in DIMENSIONS:
        d = _obj(dims.get(name), f"QA-005.{name}")
        state = d.get("state")
        if state not in {"proven", "blocked", "stale", "not-evaluated", "not-applicable"}:
            raise WorldAssuranceCampaignError(f"QA-005 dimension {name} has invalid state")
        normalized[name] = dict(d)
    provenance = _obj(found.get("staleAgainstCurrentMap"), "QA-005.staleAgainstCurrentMap")
    return {"sourceReportPresent": True, "targetId": binding["targetId"], "dimensions": normalized,
            "currentMapProvenance": dict(provenance), "requirementsSatisfied": bool(found.get("requirementsSatisfied"))}, []


def _certification(target: dict[str, Any], report: Mapping[str, Any] | None, coverage_pin: Mapping[str, Any] | None) -> tuple[dict[str, Any], list[str]]:
    binding = target["qa006"]
    if binding["bindingState"] == "unavailable":
        blockers = binding["blockers"]
        return {"sourceReportPresent": False, "targetId": None, "certificationLevel": LEVELS[0],
                "certificationState": "not-evaluated", "requestedMaximumLevel": binding["maximumLevel"],
                "blockers": blockers}, blockers
    if report is None:
        raise WorldAssuranceCampaignError(f"target {target['id']} binds QA-006 but no report was supplied")
    if _report_map(report, CERTIFICATION_FORMAT, "QA-006") != target["provenance"]:
        raise WorldAssuranceCampaignError(f"target {target['id']} QA-006 map/World Index provenance mismatch")
    entry = next((v for v in _arr(report.get("certifications"), "QA-006.certifications") if v.get("targetId") == binding["targetId"]), None)
    if entry is None:
        raise WorldAssuranceCampaignError(f"target {target['id']} references missing QA-006 target")
    if entry.get("kind") != target["class"]:
        raise WorldAssuranceCampaignError(f"target {target['id']} QA-006 target class mismatch")
    level = entry.get("certificationLevel")
    if level not in LEVELS or LEVELS.index(level) > LEVELS.index(binding["maximumLevel"]):
        raise WorldAssuranceCampaignError(f"target {target['id']} QA-006 level exceeds reviewed maximum")
    if coverage_pin is None:
        raise WorldAssuranceCampaignError(f"target {target['id']} QA-006 requires supplied QA-005 pin")
    evidence = _obj(entry.get("evidence"), "QA-006.evidence")
    if evidence.get("format") != COVERAGE_FORMAT or evidence.get("reportSha256") != coverage_pin.get("sha256"):
        raise WorldAssuranceCampaignError(f"target {target['id']} QA-006 evidence does not pin supplied QA-005 report")
    return {"sourceReportPresent": True, "targetId": binding["targetId"], "certificationLevel": level,
            "certificationState": entry.get("certificationState"), "requestedMaximumLevel": binding["maximumLevel"],
            "blockers": list(entry.get("blockers", []))}, list(entry.get("blockers", []))


def _freshness(target: dict[str, Any], report: Mapping[str, Any] | None) -> tuple[dict[str, Any], list[str]]:
    if report is None:
        blockers = ["QA016_FRESHNESS_REPORT_MISSING"]
        return {"state": "not-evaluated", "dimensions": [], "blockers": blockers}, blockers
    if report.get("format") != FRESHNESS_FORMAT or report.get("schemaVersion") != 1:
        raise WorldAssuranceCampaignError(f"freshness report must use {FRESHNESS_FORMAT} schemaVersion 1")
    index = {v.get("dimensionId"): v for v in _arr(report.get("dimensionFreshness"), "dimensionFreshness")}
    dims, blockers, states = [], [], []
    for dimension_id in target["qa016"]["freshnessDimensionIds"]:
        item = index.get(dimension_id)
        if item is None:
            blockers.append(f"QA016_DIMENSION_MISSING:{dimension_id}")
            states.append("not-evaluated")
            continue
        status = item.get("status")
        if status not in {"current", "stale", "not-compared"}:
            raise WorldAssuranceCampaignError(f"invalid QA-016 freshness status for {dimension_id}")
        dims.append(dict(item)); states.append(status)
        if status == "stale":
            blockers.append(f"QA016_DIMENSION_STALE:{dimension_id}")
    if "stale" in states:
        state = "stale"
    elif states and all(s == "current" for s in states):
        state = "current"
    else:
        state = "not-evaluated"
        blockers.append("QA016_FRESHNESS_NOT_CURRENT")
    return {"state": state, "dimensions": sorted(dims, key=lambda d: d["dimensionId"]), "blockers": sorted(set(blockers))}, blockers


def _evidence(target: dict[str, Any], bundles: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], list[str], set[str]]:
    sources, extracts = {}, {}
    for bundle in bundles:
        if bundle.get("format") != EVIDENCE_BUNDLE_FORMAT or bundle.get("schemaVersion") != 1:
            raise WorldAssuranceCampaignError(f"evidence bundle must use {EVIDENCE_BUNDLE_FORMAT} schemaVersion 1")
        local_sources = {s.get("id"): s for s in _arr(bundle.get("sources"), "bundle.sources")}
        for e in _arr(bundle.get("extracts"), "bundle.extracts"):
            extracts[e.get("id")] = e
            source = local_sources.get(e.get("sourceId"))
            if source:
                sources[e.get("id")] = source
    verified, blockers = [], []
    for required in target["qa018"]["requiredExtracts"]:
        e = extracts.get(required["id"]); s = sources.get(required["id"])
        if e is None or s is None:
            blockers.append(f"QA018_EXTRACT_MISSING:{required['id']}"); continue
        if s.get("sha256") != required["sourceSha256"]:
            blockers.append(f"QA018_SOURCE_SHA_MISMATCH:{required['id']}"); continue
        if e.get("valueSha256") != required["valueSha256"]:
            blockers.append(f"QA018_VALUE_SHA_MISMATCH:{required['id']}"); continue
        verified.append(required["id"])
    return {"state": "proven" if not blockers else "blocked", "verifiedExtractIds": sorted(verified),
            "blockers": sorted(blockers)}, blockers, set(verified)


def build_campaign_report(*, manifest: Mapping[str, Any], coverage_dashboard: Mapping[str, Any] | None = None,
                          certification_report: Mapping[str, Any] | None = None,
                          freshness_report: Mapping[str, Any] | None = None,
                          evidence_bundles: Sequence[Mapping[str, Any]] = (),
                          input_pins: Mapping[str, Any]) -> dict[str, Any]:
    normalized = normalize_manifest(manifest)
    manifest_pin = _pin(input_pins.get("manifest"), MANIFEST_FORMAT, "manifest pin")
    coverage_pin = _pin(input_pins.get("coverageDashboard"), COVERAGE_FORMAT, "coverage pin") if coverage_dashboard is not None else None
    cert_pin = _pin(input_pins.get("certification"), CERTIFICATION_FORMAT, "certification pin") if certification_report is not None else None
    freshness_pin = _pin(input_pins.get("freshness"), FRESHNESS_FORMAT, "freshness pin") if freshness_report is not None else None
    bundle_pins = [_pin(v, EVIDENCE_BUNDLE_FORMAT, f"evidenceBundles[{i}]") for i, v in enumerate(_arr(input_pins.get("evidenceBundles", []), "evidenceBundles"))]
    if len(bundle_pins) != len(evidence_bundles):
        raise WorldAssuranceCampaignError("evidence bundle pin count mismatch")
    physical_pins = [_artifact_pin(v, f"physicalArtifacts[{i}]") for i, v in enumerate(_arr(input_pins.get("physicalArtifacts", []), "physicalArtifacts"))]
    physical_digests = {p["sha256"] for p in physical_pins}

    targets, level_counts, freshness_counts, status_counts, physical_counts = [], Counter(), Counter(), Counter(), Counter()
    for target in normalized["targets"]:
        blockers = set(target["blockers"])
        coverage, b = _coverage(target, coverage_dashboard); blockers.update(b)
        certification, b = _certification(target, certification_report, coverage_pin); blockers.update(b)
        freshness, b = _freshness(target, freshness_report); blockers.update(b)
        evidence, b, verified = _evidence(target, evidence_bundles); blockers.update(b)
        physical = target["physicalE2e"]
        physical_blockers = []
        if physical["status"] == "missing":
            physical_state = "missing"; physical_blockers.append("PHYSICAL_E2E_PROOF_MISSING")
        elif physical["artifactDigestSha256"] not in physical_digests:
            physical_state = "missing"; physical_blockers.append("PHYSICAL_E2E_ARTIFACT_DIGEST_NOT_SUPPLIED")
        elif set(physical.get("evidenceExtractIds", [])) - verified:
            physical_state = "blocked"; physical_blockers.append("PHYSICAL_E2E_REQUIRED_EVIDENCE_NOT_VERIFIED")
        elif freshness["state"] == "stale":
            physical_state = "stale"; physical_blockers.append("PHYSICAL_E2E_FRESHNESS_STALE")
        elif freshness["state"] != "current":
            physical_state = "not-evaluated"; physical_blockers.append("PHYSICAL_E2E_FRESHNESS_NOT_CURRENT")
        else:
            physical_state = "proven"
        blockers.update(physical_blockers)
        if target["unresolvedEvidence"]: blockers.add("UNRESOLVED_EVIDENCE_PRESENT")
        if target["conflictingEvidence"]: blockers.add("CONFLICTING_EVIDENCE_PRESENT")
        level = certification["certificationLevel"]
        status = "stale" if freshness["state"] == "stale" else ("certified" if level != LEVELS[0] and not blockers else "blocked")
        targets.append({
            "id": target["id"], "class": target["class"], "reviewedDefinition": target["reviewedDefinition"],
            "exactProvenance": target["provenance"], "qa005Coverage": coverage, "qa006Certification": certification,
            "qa016Freshness": freshness, "qa018Evidence": evidence, "routeEvidence": target["routeEvidence"],
            "physicalE2e": {**physical, "state": physical_state, "blockers": sorted(physical_blockers),
                            "proofBoundary": "route-level Physical E2E only; not QA-005 mechanic proof and not candidate-change revalidation"},
            "unresolvedEvidence": target["unresolvedEvidence"], "conflictingEvidence": target["conflictingEvidence"],
            "blockers": sorted(blockers), "status": status,
        })
        level_counts[level] += 1; freshness_counts[freshness["state"]] += 1; status_counts[status] += 1; physical_counts[physical_state] += 1
    report = {
        "format": REPORT_FORMAT, "schemaVersion": 1, "campaignId": normalized["campaignId"],
        "provenance": {"manifest": manifest_pin, "coverageDashboard": coverage_pin, "certification": cert_pin,
                       "freshness": freshness_pin, "evidenceBundles": bundle_pins, "physicalArtifacts": physical_pins},
        "targets": sorted(targets, key=lambda t: t["id"]),
        "summary": {"targets": len(targets), "byCertificationLevel": dict(sorted(level_counts.items())),
                    "byFreshness": dict(sorted(freshness_counts.items())), "byStatus": dict(sorted(status_counts.items())),
                    "byPhysicalE2e": dict(sorted(physical_counts.items()))},
        "policy": {"readOnlyComposition": True, "parsesOtbm": False, "buildsWorldIndex": False,
                   "resolvesScripts": False, "pathfinds": False, "rerunsCoverageValidators": False,
                   "assignsCertificationIndependently": False, "runsPhysicalE2e": False,
                   "runsCandidateValidation": False, "mutatesMap": False, "timestampsUsedAsFreshnessEvidence": False,
                   "staticEvidenceEqualsPhysicalProof": False, "physicalProofEqualsCandidateRevalidation": False},
        "notes": [
            "QA-005 and QA-006 states are copied only from supplied canonical reports when reviewed bindings exist; unavailable bindings stay fail-closed and formally C0.",
            "QA-016 freshness is preserved per declared dimension and never inferred from timestamps.",
            "QA-018 verifies only exact reviewed evidence extracts by source and canonical value SHA-256.",
            "Route-level retained Physical E2E remains separate from QA-005 mechanic proof and cannot independently raise QA-006 certification.",
        ],
    }
    report["reportSha256"] = canonical_sha256(report)
    return report
