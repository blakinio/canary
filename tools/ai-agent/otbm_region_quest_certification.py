from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

MANIFEST_FORMAT = "canary-otbm-certification-targets-v1"
COVERAGE_FORMAT = "canary-otbm-coverage-dashboard-v1"
REPORT_FORMAT = "canary-otbm-region-quest-certification-v1"
SCHEMA_VERSION = 1

LEVELS = (
    "C0_NOT_EVALUATED",
    "C1_STATIC_INDEXED",
    "C2_STATIC_CORRELATED",
    "C3_STATIC_REACHABLE",
    "C4_STATIC_QUALITY_GREEN",
    "C5_PHYSICAL_ROUTE_PROVEN",
    "C6_FEATURE_OR_MECHANIC_PHYSICALLY_PROVEN",
    "C7_CANDIDATE_CHANGE_REVALIDATED",
)
LEVEL_INDEX = {level: index for index, level in enumerate(LEVELS)}
ALLOWED_KINDS = {"region", "landmark-route", "quest", "mechanic-set"}
MAX_LEVEL_BY_KIND = {
    "region": "C5_PHYSICAL_ROUTE_PROVEN",
    "landmark-route": "C5_PHYSICAL_ROUTE_PROVEN",
    "quest": "C7_CANDIDATE_CHANGE_REVALIDATED",
    "mechanic-set": "C7_CANDIDATE_CHANGE_REVALIDATED",
}

LEVEL_REQUIREMENTS = {
    1: (("indexedOnExactMap", {"proven"}),),
    2: (
        ("indexedOnExactMap", {"proven"}),
        ("sourceCorrelated", {"proven"}),
        ("scriptResolved", {"proven"}),
    ),
    3: (
        ("indexedOnExactMap", {"proven"}),
        ("sourceCorrelated", {"proven"}),
        ("scriptResolved", {"proven"}),
        ("staticallyReachable", {"proven"}),
        ("interactionResolved", {"proven", "not-applicable"}),
    ),
    4: (
        ("indexedOnExactMap", {"proven"}),
        ("sourceCorrelated", {"proven"}),
        ("scriptResolved", {"proven"}),
        ("staticallyReachable", {"proven"}),
        ("interactionResolved", {"proven", "not-applicable"}),
        ("staticQualityCompatible", {"proven"}),
    ),
    5: (
        ("indexedOnExactMap", {"proven"}),
        ("sourceCorrelated", {"proven"}),
        ("scriptResolved", {"proven"}),
        ("staticallyReachable", {"proven"}),
        ("interactionResolved", {"proven", "not-applicable"}),
        ("staticQualityCompatible", {"proven"}),
        ("executableRouteCovered", {"proven"}),
        ("physicallyRuntimeProven", {"proven"}),
    ),
    6: (
        ("indexedOnExactMap", {"proven"}),
        ("sourceCorrelated", {"proven"}),
        ("scriptResolved", {"proven"}),
        ("staticallyReachable", {"proven"}),
        ("interactionResolved", {"proven", "not-applicable"}),
        ("staticQualityCompatible", {"proven"}),
        ("executableRouteCovered", {"proven"}),
        ("physicallyRuntimeProven", {"proven"}),
    ),
    7: (
        ("indexedOnExactMap", {"proven"}),
        ("sourceCorrelated", {"proven"}),
        ("scriptResolved", {"proven"}),
        ("staticallyReachable", {"proven"}),
        ("interactionResolved", {"proven", "not-applicable"}),
        ("staticQualityCompatible", {"proven"}),
        ("executableRouteCovered", {"proven"}),
        ("physicallyRuntimeProven", {"proven"}),
        ("candidateMapValidated", {"proven"}),
    ),
}


class CertificationError(ValueError):
    """Raised when bounded certification evidence is malformed or incompatible."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_report_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CertificationError(f"{label} must be an object")
    return value


def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise CertificationError(f"{label} must be an array")
    return value


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CertificationError(f"{label} must be a non-empty string")
    return value.strip()


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise CertificationError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _input_pin(value: Any, expected_format: str, label: str) -> dict[str, Any]:
    pin = _mapping(value, label)
    size = pin.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise CertificationError(f"{label}.size must be a non-negative integer")
    if pin.get("format") != expected_format:
        raise CertificationError(f"{label}.format must be {expected_format}")
    return {
        "fileName": _non_empty_string(pin.get("fileName"), f"{label}.fileName"),
        "size": size,
        "sha256": _sha256(pin.get("sha256"), f"{label}.sha256"),
        "format": expected_format,
    }


def _normalize_manifest(manifest: Mapping[str, Any]) -> list[dict[str, str]]:
    if manifest.get("format") != MANIFEST_FORMAT or manifest.get("schemaVersion") != SCHEMA_VERSION:
        raise CertificationError(f"manifest must use {MANIFEST_FORMAT} schemaVersion {SCHEMA_VERSION}")
    entries = _array(manifest.get("targets"), "manifest.targets")
    if not entries:
        raise CertificationError("manifest.targets must not be empty")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(entries):
        entry = _mapping(raw, f"manifest.targets[{index}]")
        target_id = _non_empty_string(entry.get("targetId"), f"manifest.targets[{index}].targetId")
        if target_id in seen:
            raise CertificationError(f"duplicate certification target: {target_id}")
        seen.add(target_id)
        maximum_level = entry.get("maximumLevel")
        if maximum_level not in LEVEL_INDEX or maximum_level == LEVELS[0]:
            raise CertificationError(f"manifest.targets[{index}].maximumLevel must be C1..C7")
        reason = _non_empty_string(entry.get("reason"), f"manifest.targets[{index}].reason")
        result.append({"targetId": target_id, "maximumLevel": maximum_level, "reason": reason})
    return sorted(result, key=lambda item: item["targetId"])


def _coverage_targets(report: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], str, str]:
    if report.get("format") != COVERAGE_FORMAT or report.get("schemaVersion") != SCHEMA_VERSION:
        raise CertificationError(f"coverage dashboard must use {COVERAGE_FORMAT} schemaVersion {SCHEMA_VERSION}")
    policy = _mapping(report.get("policy"), "coverage.policy")
    if policy.get("formalCertificationAssigned") is not False:
        raise CertificationError("coverage dashboard must not pre-assign formal certification")
    current_map = _mapping(report.get("currentMap"), "coverage.currentMap")
    map_sha = _sha256(current_map.get("mapSha256"), "coverage.currentMap.mapSha256")
    world_sha = _sha256(current_map.get("worldIndexSha256"), "coverage.currentMap.worldIndexSha256")
    result: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(_array(report.get("targets"), "coverage.targets")):
        target = _mapping(raw, f"coverage.targets[{index}]")
        target_id = _non_empty_string(target.get("id"), f"coverage.targets[{index}].id")
        if target_id in result:
            raise CertificationError(f"duplicate coverage target id: {target_id}")
        if target.get("formalCertificationLevel") is not None:
            raise CertificationError(f"coverage target {target_id} already has a formal certification level")
        result[target_id] = target
    return result, map_sha, world_sha


def _dimension_state(target: Mapping[str, Any], key: str) -> tuple[str, list[str]]:
    dimensions = _mapping(target.get("dimensions"), f"target {target.get('id')}.dimensions")
    dimension = _mapping(dimensions.get(key), f"target {target.get('id')}.dimensions.{key}")
    state = dimension.get("state")
    if state not in {"proven", "blocked", "stale", "not-evaluated", "not-applicable"}:
        raise CertificationError(f"target {target.get('id')} dimension {key} has invalid state")
    blockers = []
    for raw in _array(dimension.get("blockers", []), f"target {target.get('id')}.dimensions.{key}.blockers"):
        blockers.append(_non_empty_string(raw, f"target {target.get('id')}.dimensions.{key}.blockers[]"))
    return str(state), sorted(set(blockers))


def _current_provenance(target: Mapping[str, Any]) -> tuple[str, list[str]]:
    stale = _mapping(target.get("staleAgainstCurrentMap"), f"target {target.get('id')}.staleAgainstCurrentMap")
    state = stale.get("state")
    if state not in {"current", "stale", "mixed", "not-evaluated"}:
        raise CertificationError(f"target {target.get('id')} has invalid current-map provenance state")
    blockers = [
        _non_empty_string(raw, f"target {target.get('id')}.staleAgainstCurrentMap.blockers[]")
        for raw in _array(stale.get("blockers", []), f"target {target.get('id')}.staleAgainstCurrentMap.blockers")
    ]
    return str(state), sorted(set(blockers))


def _level_evaluation(target: Mapping[str, Any], level_number: int) -> tuple[bool, list[str], list[dict[str, Any]]]:
    kind = target.get("kind")
    if level_number == 6 and kind not in {"quest", "mechanic-set"}:
        return False, ["C6_REQUIRES_QUEST_OR_MECHANIC_SET_TARGET"], []
    requirements: list[dict[str, Any]] = []
    blockers: list[str] = []
    for key, accepted_states in LEVEL_REQUIREMENTS[level_number]:
        state, dimension_blockers = _dimension_state(target, key)
        met = state in accepted_states
        requirements.append(
            {
                "dimension": key,
                "state": state,
                "acceptedStates": sorted(accepted_states),
                "met": met,
            }
        )
        if not met:
            blockers.append(f"{key.upper()}_{state.upper().replace('-', '_')}")
            blockers.extend(dimension_blockers)
    return not blockers, sorted(set(blockers)), requirements


def build_certification_report(
    *,
    manifest: Mapping[str, Any],
    coverage_dashboard: Mapping[str, Any],
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    manifest_pin = _input_pin(input_pins.get("manifest"), MANIFEST_FORMAT, "input_pins.manifest")
    coverage_pin = _input_pin(input_pins.get("coverageDashboard"), COVERAGE_FORMAT, "input_pins.coverageDashboard")
    selected = _normalize_manifest(manifest)
    coverage_targets, map_sha, world_sha = _coverage_targets(coverage_dashboard)

    certifications: list[dict[str, Any]] = []
    counts = {level: 0 for level in LEVELS}
    state_counts = {"certified": 0, "blocked": 0, "stale": 0, "not-evaluated": 0}

    for selection in selected:
        target = coverage_targets.get(selection["targetId"])
        if target is None:
            raise CertificationError(f"certification target {selection['targetId']} is missing from the coverage dashboard")
        kind = target.get("kind")
        if kind not in ALLOWED_KINDS:
            raise CertificationError(f"certification target {selection['targetId']} has unsupported bounded kind {kind!r}")
        allowed_max = MAX_LEVEL_BY_KIND[str(kind)]
        if LEVEL_INDEX[selection["maximumLevel"]] > LEVEL_INDEX[allowed_max]:
            raise CertificationError(
                f"certification target {selection['targetId']} kind {kind} cannot request above {allowed_max}"
            )

        provenance_state, provenance_blockers = _current_provenance(target)
        requested_max_index = LEVEL_INDEX[selection["maximumLevel"]]
        evaluated: list[dict[str, Any]] = []
        achieved = 0
        first_failure_blockers: list[str] = []

        for level_number in range(1, requested_max_index + 1):
            met, blockers, requirements = _level_evaluation(target, level_number)
            evaluated.append(
                {
                    "level": LEVELS[level_number],
                    "met": met,
                    "requirements": requirements,
                    "blockers": blockers,
                }
            )
            if not met:
                first_failure_blockers = blockers
                break
            achieved = level_number

        if provenance_state != "current":
            certification_level = LEVELS[0]
            certification_state = "stale" if provenance_state in {"stale", "mixed"} else "not-evaluated"
            blockers = sorted(set(provenance_blockers + ["CURRENT_MAP_PROVENANCE_NOT_CURRENT"]))
        else:
            certification_level = LEVELS[achieved]
            blockers = first_failure_blockers
            if achieved > 0:
                certification_state = "certified"
            else:
                first_states = {req["state"] for item in evaluated[:1] for req in item["requirements"]}
                certification_state = "blocked" if "blocked" in first_states else "not-evaluated"

        counts[certification_level] += 1
        state_counts[certification_state] += 1
        certifications.append(
            {
                "targetId": selection["targetId"],
                "kind": kind,
                "reason": selection["reason"],
                "requestedMaximumLevel": selection["maximumLevel"],
                "certificationLevel": certification_level,
                "certificationState": certification_state,
                "staleAgainstCurrentMap": provenance_state != "current",
                "coverageRequirementsSatisfied": bool(target.get("requirementsSatisfied")),
                "evaluatedLevels": evaluated,
                "blockers": sorted(set(blockers)),
                "evidence": {
                    "format": COVERAGE_FORMAT,
                    "reportSha256": coverage_pin["sha256"],
                    "sourceId": selection["targetId"],
                },
            }
        )

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "currentMap": {"mapSha256": map_sha, "worldIndexSha256": world_sha},
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "otbmParsedIndependently": False,
            "validatorsRecomputed": False,
            "physicalE2eExecuted": False,
            "candidateValidationExecuted": False,
            "strongestContiguousLevelOnly": True,
            "currentProvenanceRequired": True,
            "worldTargetsCertified": False,
            "opaqueScoreEmitted": False,
        },
        "provenance": {
            "manifest": manifest_pin,
            "coverageDashboard": coverage_pin,
        },
        "summary": {
            "targets": len(certifications),
            "byLevel": counts,
            "byState": state_counts,
        },
        "certifications": sorted(certifications, key=lambda item: item["targetId"]),
        "notes": [
            "Certification is bounded to explicitly selected non-world targets already defined by the factual Coverage Dashboard.",
            "A target receives only the strongest contiguous C0-C7 level supported by exact current evidence; stale or mixed current-map provenance collapses formal certification to C0.",
            "C6 is available only to reviewed quest or mechanic-set targets whose complete selected mechanic population is physically runtime-proven on the current map.",
            "This layer does not run validators, routes, Physical E2E or candidate validation and does not mutate maps or evidence.",
        ],
    }
