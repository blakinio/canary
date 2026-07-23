from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

EXECUTION_FORMAT = "canary-otbm-continuous-assurance-execution-v1"
REGRESSION_FORMAT = "canary-otbm-map-change-regression-v1"
WORLD_HEALTH_FORMAT = "canary-otbm-world-health-v1"
CERTIFICATION_FORMAT = "canary-otbm-region-quest-certification-v1"
REPORT_FORMAT = "canary-otbm-continuous-assurance-v1"
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
WORLD_HEALTH_KEYS = (
    "structuralFindings",
    "runtimeHandlerPlacementFindings",
    "attentionMechanics",
    "staleEvidenceTargets",
    "missingPhysicalScenarioTargets",
    "runtimeNotProvenOnCurrentMapTargets",
)

class ContinuousAssuranceError(ValueError):
    """Raised when continuous-assurance evidence is malformed or incompatible."""

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def canonical_report_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContinuousAssuranceError(f"{label} must be an object")
    return value

def _array(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContinuousAssuranceError(f"{label} must be an array")
    return value

def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContinuousAssuranceError(f"{label} must be a non-empty string")
    return value.strip()

def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ContinuousAssuranceError(f"{label} must be a lowercase SHA-256 digest")
    return value

def _count(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContinuousAssuranceError(f"{label} must be a non-negative integer")
    return value

def _pin(value: Any, expected_format: str, label: str) -> dict[str, Any]:
    pin = _mapping(value, label)
    if pin.get("format") != expected_format:
        raise ContinuousAssuranceError(f"{label}.format must be {expected_format}")
    return {
        "fileName": _string(pin.get("fileName"), f"{label}.fileName"),
        "size": _count(pin.get("size"), f"{label}.size"),
        "sha256": _sha256(pin.get("sha256"), f"{label}.sha256"),
        "format": expected_format,
    }

def _identity_from_regression(report: Mapping[str, Any]) -> dict[str, str]:
    if report.get("format") != REGRESSION_FORMAT or report.get("schemaVersion") != SCHEMA_VERSION:
        raise ContinuousAssuranceError(f"regression plan must use {REGRESSION_FORMAT} schemaVersion {SCHEMA_VERSION}")
    source = _mapping(report.get("source"), "regression.source")
    return {
        "beforeMapSha256": _sha256(source.get("beforeMapSha256"), "regression.source.beforeMapSha256"),
        "afterMapSha256": _sha256(source.get("afterMapSha256"), "regression.source.afterMapSha256"),
        "beforeWorldIndexSha256": _sha256(source.get("beforeWorldIndexSha256"), "regression.source.beforeWorldIndexSha256"),
        "afterWorldIndexSha256": _sha256(source.get("afterWorldIndexSha256"), "regression.source.afterWorldIndexSha256"),
    }

def _world_health_identity(report: Mapping[str, Any], label: str) -> tuple[str, str, dict[str, int]]:
    if report.get("format") != WORLD_HEALTH_FORMAT or report.get("schemaVersion") != SCHEMA_VERSION:
        raise ContinuousAssuranceError(f"{label} must use {WORLD_HEALTH_FORMAT} schemaVersion {SCHEMA_VERSION}")
    source = _mapping(report.get("source"), f"{label}.source")
    summary = _mapping(report.get("summary"), f"{label}.summary")
    counts = {key: _count(summary.get(key), f"{label}.summary.{key}") for key in WORLD_HEALTH_KEYS}
    return (
        _sha256(source.get("mapSha256"), f"{label}.source.mapSha256"),
        _sha256(source.get("worldIndexSha256"), f"{label}.source.worldIndexSha256"),
        counts,
    )

def _certification_identity(report: Mapping[str, Any], label: str) -> tuple[str, str, dict[str, Mapping[str, Any]]]:
    if report.get("format") != CERTIFICATION_FORMAT or report.get("schemaVersion") != SCHEMA_VERSION:
        raise ContinuousAssuranceError(f"{label} must use {CERTIFICATION_FORMAT} schemaVersion {SCHEMA_VERSION}")
    current_map = _mapping(report.get("currentMap"), f"{label}.currentMap")
    targets: dict[str, Mapping[str, Any]] = {}
    for index, raw in enumerate(_array(report.get("certifications"), f"{label}.certifications")):
        entry = _mapping(raw, f"{label}.certifications[{index}]")
        target_id = _string(entry.get("targetId"), f"{label}.certifications[{index}].targetId")
        if target_id in targets:
            raise ContinuousAssuranceError(f"{label} contains duplicate certification target {target_id}")
        level = entry.get("certificationLevel")
        if level not in LEVEL_INDEX:
            raise ContinuousAssuranceError(f"{label} target {target_id} has unsupported certificationLevel")
        state = entry.get("certificationState")
        if state not in {"certified", "blocked", "stale", "not-evaluated"}:
            raise ContinuousAssuranceError(f"{label} target {target_id} has unsupported certificationState")
        targets[target_id] = entry
    return (
        _sha256(current_map.get("mapSha256"), f"{label}.currentMap.mapSha256"),
        _sha256(current_map.get("worldIndexSha256"), f"{label}.currentMap.worldIndexSha256"),
        targets,
    )

def _verify_execution_pins(execution: Mapping[str, Any], pins: Mapping[str, Mapping[str, Any]]) -> None:
    if execution.get("format") != EXECUTION_FORMAT or execution.get("schemaVersion") != SCHEMA_VERSION:
        raise ContinuousAssuranceError(f"execution ledger must use {EXECUTION_FORMAT} schemaVersion {SCHEMA_VERSION}")
    expected = _mapping(execution.get("inputs"), "execution.inputs")
    bindings = {
        "regressionPlanSha256": "regressionPlan",
        "beforeWorldHealthSha256": "beforeWorldHealth",
        "afterWorldHealthSha256": "afterWorldHealth",
        "beforeCertificationSha256": "beforeCertification",
        "afterCertificationSha256": "afterCertification",
    }
    for field, pin_name in bindings.items():
        if _sha256(expected.get(field), f"execution.inputs.{field}") != pins[pin_name]["sha256"]:
            raise ContinuousAssuranceError(f"execution ledger {field} does not match supplied {pin_name} bytes")

def _result_evidence(value: Any, label: str) -> dict[str, str]:
    evidence = _mapping(value, label)
    return {
        "format": _string(evidence.get("format"), f"{label}.format"),
        "sha256": _sha256(evidence.get("sha256"), f"{label}.sha256"),
    }

def _static_results(execution: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(_array(execution.get("staticValidation"), "execution.staticValidation")):
        entry = _mapping(raw, f"execution.staticValidation[{index}]")
        validator = _string(entry.get("validator"), f"execution.staticValidation[{index}].validator")
        if validator in results:
            raise ContinuousAssuranceError(f"duplicate static validator result: {validator}")
        status = entry.get("status")
        if status not in {"passed", "failed", "not-run"}:
            raise ContinuousAssuranceError(f"static validator {validator} has unsupported status")
        results[validator] = {
            "validator": validator,
            "status": status,
            "evidence": _result_evidence(entry.get("evidence"), f"execution.staticValidation[{index}].evidence"),
        }
    return results

def _physical_results(execution: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    results: dict[tuple[str, str], dict[str, Any]] = {}
    for index, raw in enumerate(_array(execution.get("physicalValidation"), "execution.physicalValidation")):
        entry = _mapping(raw, f"execution.physicalValidation[{index}]")
        suite = _string(entry.get("suite"), f"execution.physicalValidation[{index}].suite")
        scenario_id = _string(entry.get("id"), f"execution.physicalValidation[{index}].id")
        key = (suite, scenario_id)
        if key in results:
            raise ContinuousAssuranceError(f"duplicate physical scenario result: {suite}/{scenario_id}")
        status = entry.get("status")
        if status not in {"passed", "failed", "not-run"}:
            raise ContinuousAssuranceError(f"physical scenario {suite}/{scenario_id} has unsupported status")
        results[key] = {
            "suite": suite,
            "id": scenario_id,
            "status": status,
            "evidence": _result_evidence(entry.get("evidence"), f"execution.physicalValidation[{index}].evidence"),
        }
    return results

def build_continuous_assurance_report(
    *,
    execution_ledger: Mapping[str, Any],
    regression_plan: Mapping[str, Any],
    before_world_health: Mapping[str, Any],
    after_world_health: Mapping[str, Any],
    before_certification: Mapping[str, Any],
    after_certification: Mapping[str, Any],
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    pins = {
        "executionLedger": _pin(input_pins.get("executionLedger"), EXECUTION_FORMAT, "input_pins.executionLedger"),
        "regressionPlan": _pin(input_pins.get("regressionPlan"), REGRESSION_FORMAT, "input_pins.regressionPlan"),
        "beforeWorldHealth": _pin(input_pins.get("beforeWorldHealth"), WORLD_HEALTH_FORMAT, "input_pins.beforeWorldHealth"),
        "afterWorldHealth": _pin(input_pins.get("afterWorldHealth"), WORLD_HEALTH_FORMAT, "input_pins.afterWorldHealth"),
        "beforeCertification": _pin(input_pins.get("beforeCertification"), CERTIFICATION_FORMAT, "input_pins.beforeCertification"),
        "afterCertification": _pin(input_pins.get("afterCertification"), CERTIFICATION_FORMAT, "input_pins.afterCertification"),
    }
    if len({pin["sha256"] for pin in pins.values()}) != len(pins):
        raise ContinuousAssuranceError("continuous-assurance input reports must have distinct SHA-256 pins")

    regression = _mapping(regression_plan, "regression_plan")
    identity = _identity_from_regression(regression)
    before_map, before_index, before_health = _world_health_identity(before_world_health, "beforeWorldHealth")
    after_map, after_index, after_health = _world_health_identity(after_world_health, "afterWorldHealth")
    before_cert_map, before_cert_index, before_certs = _certification_identity(before_certification, "beforeCertification")
    after_cert_map, after_cert_index, after_certs = _certification_identity(after_certification, "afterCertification")

    expected_identities = {
        "before World Health": (before_map, before_index, identity["beforeMapSha256"], identity["beforeWorldIndexSha256"]),
        "after World Health": (after_map, after_index, identity["afterMapSha256"], identity["afterWorldIndexSha256"]),
        "before Certification": (before_cert_map, before_cert_index, identity["beforeMapSha256"], identity["beforeWorldIndexSha256"]),
        "after Certification": (after_cert_map, after_cert_index, identity["afterMapSha256"], identity["afterWorldIndexSha256"]),
    }
    for label, (map_sha, index_sha, expected_map, expected_index) in expected_identities.items():
        if map_sha != expected_map or index_sha != expected_index:
            raise ContinuousAssuranceError(f"{label} provenance does not match regression-plan map/index identity")

    execution = _mapping(execution_ledger, "execution_ledger")
    _verify_execution_pins(execution, pins)

    blockers: list[str] = []
    static_plan = _mapping(regression.get("staticValidation"), "regression.staticValidation")
    selected_static = [
        _string(_mapping(raw, "regression.staticValidation.selected[]").get("validator"), "selected static validator")
        for raw in _array(static_plan.get("selected"), "regression.staticValidation.selected")
    ]
    if len(set(selected_static)) != len(selected_static):
        raise ContinuousAssuranceError("regression staticValidation.selected contains duplicate validators")
    static_results = _static_results(execution)
    if set(static_results) != set(selected_static):
        raise ContinuousAssuranceError("execution staticValidation results must exactly match regression selected validators")
    for validator in sorted(selected_static):
        if static_results[validator]["status"] != "passed":
            blockers.append(f"STATIC_VALIDATOR_NOT_PASSED:{validator}")
    if static_plan.get("failClosed") is True:
        blockers.append("REGRESSION_STATIC_SELECTION_FAIL_CLOSED")

    physical_plan = _mapping(regression.get("physicalValidation"), "regression.physicalValidation")
    if physical_plan.get("manualSelectionRequired") is True:
        blockers.append("MANUAL_PHYSICAL_SELECTION_REQUIRED")
    selected_physical: list[tuple[str, str]] = []
    for index, raw in enumerate(_array(physical_plan.get("scenarios"), "regression.physicalValidation.scenarios")):
        scenario = _mapping(raw, f"regression.physicalValidation.scenarios[{index}]")
        if scenario.get("selected") is True:
            selected_physical.append((
                _string(scenario.get("suite"), f"regression.physicalValidation.scenarios[{index}].suite"),
                _string(scenario.get("id"), f"regression.physicalValidation.scenarios[{index}].id"),
            ))
    if len(set(selected_physical)) != len(selected_physical):
        raise ContinuousAssuranceError("regression selected physical scenarios contain duplicates")
    physical_results = _physical_results(execution)
    if set(physical_results) != set(selected_physical):
        raise ContinuousAssuranceError("execution physicalValidation results must exactly match regression selected scenarios")
    for suite, scenario_id in sorted(selected_physical):
        if physical_results[(suite, scenario_id)]["status"] != "passed":
            blockers.append(f"PHYSICAL_SCENARIO_NOT_PASSED:{suite}/{scenario_id}")

    health_delta: list[dict[str, Any]] = []
    for key in WORLD_HEALTH_KEYS:
        before_value = before_health[key]
        after_value = after_health[key]
        delta = after_value - before_value
        regressed = delta > 0
        if regressed:
            blockers.append(f"WORLD_HEALTH_REGRESSION:{key}")
        health_delta.append({
            "dimension": key,
            "before": before_value,
            "after": after_value,
            "delta": delta,
            "regressed": regressed,
        })

    certification_delta: list[dict[str, Any]] = []
    for target_id in sorted(set(before_certs) | set(after_certs)):
        before_entry = before_certs.get(target_id)
        after_entry = after_certs.get(target_id)
        before_level = None if before_entry is None else str(before_entry["certificationLevel"])
        after_level = None if after_entry is None else str(after_entry["certificationLevel"])
        status = "new"
        delta = None
        regressed = False
        if before_entry is not None and after_entry is None:
            status = "missing-after"
            regressed = True
            blockers.append(f"CERTIFICATION_TARGET_MISSING_AFTER:{target_id}")
        elif before_entry is None and after_entry is not None:
            status = "new"
        else:
            assert before_entry is not None and after_entry is not None
            delta = LEVEL_INDEX[after_level] - LEVEL_INDEX[before_level]
            status = "improved" if delta > 0 else "unchanged" if delta == 0 else "regressed"
            regressed = delta < 0 or after_entry.get("certificationState") == "stale"
            if delta < 0:
                blockers.append(f"CERTIFICATION_LEVEL_REGRESSION:{target_id}")
            if after_entry.get("certificationState") == "stale":
                blockers.append(f"CERTIFICATION_STALE_AFTER:{target_id}")
        certification_delta.append({
            "targetId": target_id,
            "beforeLevel": before_level,
            "afterLevel": after_level,
            "delta": delta,
            "status": status,
            "regressed": regressed,
        })

    blockers = sorted(set(blockers))
    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "source": identity,
        "policy": {
            "readOnly": True,
            "mapModified": False,
            "semanticDiffRecomputed": False,
            "validatorsRecomputed": False,
            "physicalE2eExecuted": False,
            "certificationRecomputed": False,
            "selectedValidationMustPass": True,
            "worldHealthRegressionsFailClosed": True,
            "certificationRegressionsFailClosed": True,
            "uncertainRegressionSelectionFailsClosed": True,
            "unrelatedNonOtbmSuitesSuppressed": False,
            "deploymentAuthorized": False,
        },
        "provenance": pins,
        "validation": {
            "static": [static_results[key] for key in sorted(static_results)],
            "physical": [physical_results[key] for key in sorted(physical_results)],
        },
        "worldHealthDelta": health_delta,
        "certificationDelta": certification_delta,
        "gate": {
            "passed": not blockers,
            "blockers": blockers,
        },
        "summary": {
            "selectedStaticValidatorCount": len(selected_static),
            "selectedPhysicalScenarioCount": len(selected_physical),
            "worldHealthRegressionCount": sum(1 for item in health_delta if item["regressed"]),
            "certificationRegressionCount": sum(1 for item in certification_delta if item["regressed"]),
            "blockerCount": len(blockers),
        },
        "notes": [
            "This gate composes exact existing regression, world-health, certification and execution-ledger evidence; it does not rerun validators or Physical E2E.",
            "Selected validators and Physical E2E scenarios must have an exact corresponding execution-ledger result and must pass.",
            "Any positive problem-count delta in the explicit World Health dimensions fails closed.",
            "Missing, lower or stale after-certification evidence for a previously represented target fails closed.",
            "A passed gate is an auditable evidence result for the represented OTBM scope and does not authorize deployment or suppress unrelated non-OTBM validation.",
        ],
    }
