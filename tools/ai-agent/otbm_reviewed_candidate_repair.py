from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

APPROVAL_FORMAT = "canary-otbm-reviewed-candidate-repair-approval-v1"
REPORT_FORMAT = "canary-otbm-reviewed-candidate-repair-v1"
RECOMMENDATION_FORMAT = "canary-otbm-repair-recommendation-v1"
PIPELINE_FORMAT = "canary-otbm-repair-materialization-pipeline-v1"
SEMANTIC_DIFF_FORMAT = "canary-otbm-semantic-diff-v1"
IMPACTED_SELECTION_FORMAT = "canary-otbm-e2e-impacted-selection-v1"
PHYSICAL_VALIDATION_FORMAT = "canary-otbm-candidate-physical-validation-v1"
SCHEMA_VERSION = 1

SUPPORTED_RECOMMENDATION_STATES = {
    "supported-by-existing-attribute-path",
    "supported-by-existing-tile-area-path",
    "supported-by-existing-raw-tile-path",
}

ATTRIBUTE_OPERATIONS = {
    "set-action-id",
    "set-unique-id",
    "set-house-door-id",
    "set-teleport-destination",
}

RAW_TILE_CAPABILITY_BINDINGS = {
    "bounded-raw-tile-replacement": (
        "tile-replacement",
        "canary-otbm-tile-materialization-approval-v1",
        "raw-tile-replacement",
    ),
    "bounded-raw-tile-insertion": (
        "tile-insertion",
        "canary-otbm-tile-insertion-approval-v1",
        "raw-tile-insertion",
    ),
    "bounded-raw-tile-deletion": (
        "tile-deletion",
        "canary-otbm-tile-deletion-approval-v1",
        "raw-tile-deletion",
    ),
    "bounded-raw-tile-type-conversion": (
        "tile-type-conversion",
        "canary-otbm-tile-type-conversion-approval-v1",
        "raw-tile-type-conversion",
    ),
}

SELECTOR_KEYS = {
    "position",
    "itemId",
    "actionId",
    "uniqueId",
    "houseDoorId",
    "teleportDestination",
}


class ReviewedCandidateRepairError(ValueError):
    """Raised when reviewed-candidate repair evidence is malformed or incompatible."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_report_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReviewedCandidateRepairError(f"{label} must be an object")
    return value


def _sha256(value: Any, label: str) -> str:
    if not _is_sha256(value):
        raise ReviewedCandidateRepairError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReviewedCandidateRepairError(f"{label} must be a non-empty string")
    return value.strip()


def _input_pin(value: Any, expected_format: str, label: str) -> dict[str, Any]:
    pin = _mapping(value, f"{label} input pin")
    file_name = _non_empty_string(pin.get("fileName"), f"{label} input pin fileName")
    size = pin.get("size")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise ReviewedCandidateRepairError(f"{label} input pin size must be a non-negative integer")
    sha = _sha256(pin.get("sha256"), f"{label} input pin sha256")
    report_format = pin.get("format")
    if report_format != expected_format:
        raise ReviewedCandidateRepairError(f"{label} input pin format must be {expected_format}")
    return {"fileName": file_name, "size": size, "sha256": sha, "format": report_format}


def _position(value: Any, label: str) -> list[int]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(isinstance(part, bool) or not isinstance(part, int) for part in value)
    ):
        raise ReviewedCandidateRepairError(f"{label} must be an integer x,y,z array")
    x, y, z = value
    if not (0 <= x <= 65535 and 0 <= y <= 65535 and 0 <= z <= 15):
        raise ReviewedCandidateRepairError(f"{label} is outside the OTBM coordinate range")
    return [x, y, z]


def _selector(value: Any, label: str) -> dict[str, Any]:
    selector = _mapping(value, label)
    if not selector:
        raise ReviewedCandidateRepairError(f"{label} must be non-empty")
    unknown = set(selector) - SELECTOR_KEYS
    if unknown:
        raise ReviewedCandidateRepairError(f"{label} contains unsupported keys: {sorted(unknown)}")
    normalized: dict[str, Any] = {}
    for key in sorted(selector):
        raw = selector[key]
        if key in {"position", "teleportDestination"}:
            normalized[key] = _position(raw, f"{label}.{key}")
            continue
        maximum = 255 if key == "houseDoorId" else 65535
        if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= maximum:
            raise ReviewedCandidateRepairError(f"{label}.{key} must be an integer in 0..{maximum}")
        normalized[key] = raw
    return normalized


def _expected_binding(recommendation: Mapping[str, Any]) -> tuple[str, str]:
    state = recommendation.get("state")
    if state not in SUPPORTED_RECOMMENDATION_STATES:
        raise ReviewedCandidateRepairError("recommendation does not authorize a supported existing mutation path")

    capability = _mapping(recommendation.get("capability"), "recommendation.capability")
    if capability.get("technicalPathSupported") is not True:
        raise ReviewedCandidateRepairError("recommendation technical path is not supported")
    if capability.get("capabilityOnly") is not True:
        raise ReviewedCandidateRepairError("recommendation capability must remain capability-only before approval")

    mutation = _mapping(recommendation.get("mutation"), "recommendation.mutation")
    mutation_kind = mutation.get("kind")
    family = capability.get("family")
    mode = capability.get("mode")

    if state == "supported-by-existing-attribute-path":
        if family != "phase8-attribute" or mode not in ATTRIBUTE_OPERATIONS or mutation_kind != "attribute-replacement":
            raise ReviewedCandidateRepairError("attribute recommendation capability/mutation binding is incompatible")
        return "fixed-width-attribute", "canary-otbm-bounded-patch-plan-v1"

    if state == "supported-by-existing-tile-area-path":
        if (
            family != "tile-area"
            or mode != "complete-zero-translation-replace-region"
            or mutation_kind != "tile-area-materialization"
        ):
            raise ReviewedCandidateRepairError("TILE_AREA recommendation capability/mutation binding is incompatible")
        return "tile-area", "canary-otbm-area-materialization-approval-v1"

    if family != "raw-tile" or mode not in RAW_TILE_CAPABILITY_BINDINGS:
        raise ReviewedCandidateRepairError("raw-tile recommendation capability binding is incompatible")
    pipeline_mode, authorization_format, expected_mutation_kind = RAW_TILE_CAPABILITY_BINDINGS[mode]
    if mutation_kind != expected_mutation_kind:
        raise ReviewedCandidateRepairError("raw-tile recommendation mutation kind does not match capability mode")
    return pipeline_mode, authorization_format


def _validate_recommendation(recommendation: Mapping[str, Any]) -> tuple[dict[str, Any], str, str]:
    if recommendation.get("format") != RECOMMENDATION_FORMAT or recommendation.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewedCandidateRepairError(
            f"recommendation must use {RECOMMENDATION_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    if recommendation.get("blockers") not in ([], None):
        raise ReviewedCandidateRepairError("supported recommendation must not retain blockers")

    source = _mapping(recommendation.get("source"), "recommendation.source")
    source_sha = _sha256(source.get("mapSha256"), "recommendation.source.mapSha256")
    selector = _selector(recommendation.get("selector"), "recommendation.selector")
    mutation = _mapping(recommendation.get("mutation"), "recommendation.mutation")
    if "expectedOldState" not in mutation or "proposedTargetState" not in mutation:
        raise ReviewedCandidateRepairError("recommendation mutation old/target state is incomplete")

    pipeline_mode, authorization_format = _expected_binding(recommendation)
    return (
        {
            "state": recommendation["state"],
            "sourceMapSha256": source_sha,
            "selector": selector,
            "mutation": dict(mutation),
            "capability": dict(_mapping(recommendation["capability"], "recommendation.capability")),
        },
        pipeline_mode,
        authorization_format,
    )


def _validate_approval(
    approval: Mapping[str, Any],
    *,
    recommendation_summary: Mapping[str, Any],
    recommendation_pin: Mapping[str, Any],
    expected_pipeline_mode: str,
    expected_authorization_format: str,
) -> dict[str, Any]:
    if approval.get("format") != APPROVAL_FORMAT or approval.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewedCandidateRepairError(f"approval must use {APPROVAL_FORMAT} schemaVersion {SCHEMA_VERSION}")
    if approval.get("approved") is not True:
        raise ReviewedCandidateRepairError("approval.approved must be true")
    if approval.get("recommendationSha256") != recommendation_pin["sha256"]:
        raise ReviewedCandidateRepairError("approval recommendation SHA-256 does not match exact recommendation bytes")
    if approval.get("sourceMapSha256") != recommendation_summary["sourceMapSha256"]:
        raise ReviewedCandidateRepairError("approval source map SHA-256 does not match recommendation")

    selector = _selector(approval.get("selector"), "approval.selector")
    if selector != recommendation_summary["selector"]:
        raise ReviewedCandidateRepairError("approval selector does not exactly match recommendation")

    if "expectedOldState" not in approval or approval["expectedOldState"] != recommendation_summary["mutation"]["expectedOldState"]:
        raise ReviewedCandidateRepairError("approval expected old state does not exactly match recommendation")
    if "intendedTargetState" not in approval or approval["intendedTargetState"] != recommendation_summary["mutation"]["proposedTargetState"]:
        raise ReviewedCandidateRepairError("approval intended target state does not exactly match recommendation")
    if approval.get("pipelineMode") != expected_pipeline_mode:
        raise ReviewedCandidateRepairError("approval pipeline mode does not match recommendation capability")

    authorization = _mapping(approval.get("mutationAuthorization"), "approval.mutationAuthorization")
    authorization_format = authorization.get("format")
    authorization_sha = _sha256(authorization.get("sha256"), "approval.mutationAuthorization.sha256")
    if authorization_format != expected_authorization_format:
        raise ReviewedCandidateRepairError(
            f"approval mutation authorization format must be {expected_authorization_format}"
        )

    review = _mapping(approval.get("review"), "approval.review")
    reviewer = _non_empty_string(review.get("reviewer"), "approval.review.reviewer")
    rationale = _non_empty_string(review.get("rationale"), "approval.review.rationale")

    return {
        "pipelineMode": expected_pipeline_mode,
        "mutationAuthorization": {"format": authorization_format, "sha256": authorization_sha},
        "review": {"reviewer": reviewer, "rationale": rationale},
    }


def _validate_pipeline(
    pipeline: Mapping[str, Any],
    *,
    source_sha: str,
    expected_mode: str,
    authorization: Mapping[str, Any],
) -> dict[str, Any]:
    if pipeline.get("format") != PIPELINE_FORMAT or pipeline.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewedCandidateRepairError(f"pipeline result must use {PIPELINE_FORMAT} schemaVersion {SCHEMA_VERSION}")
    if pipeline.get("ok") is not True:
        raise ReviewedCandidateRepairError("pipeline result is not successful")
    if pipeline.get("mode") != expected_mode:
        raise ReviewedCandidateRepairError("pipeline mode does not match reviewed approval")

    source = _mapping(pipeline.get("source"), "pipeline.source")
    if source.get("sha256") != source_sha or source.get("unchanged") is not True:
        raise ReviewedCandidateRepairError("pipeline source identity/immutability does not match approved source")

    output = _mapping(pipeline.get("output"), "pipeline.output")
    candidate_sha = _sha256(output.get("sha256"), "pipeline.output.sha256")
    if output.get("createNew") is not True or output.get("byteIdenticalToVerifiedCandidate") is not True:
        raise ReviewedCandidateRepairError("pipeline output is not a verified create-new candidate")

    quality = _mapping(pipeline.get("quality"), "pipeline.quality")
    if quality.get("format") != "canary-otbm-map-quality-v1" or quality.get("ok") is not True:
        raise ReviewedCandidateRepairError("pipeline candidate Map Quality evidence is not successful")
    if quality.get("sourceSha256") != candidate_sha:
        raise ReviewedCandidateRepairError("pipeline Map Quality source SHA-256 does not match candidate")

    inputs = _mapping(pipeline.get("inputs"), "pipeline.inputs")
    authorization_matches = [
        pin
        for pin in inputs.values()
        if isinstance(pin, Mapping)
        and pin.get("sha256") == authorization["sha256"]
        and pin.get("format") == authorization["format"]
    ]
    if len(authorization_matches) != 1:
        raise ReviewedCandidateRepairError(
            "pipeline inputs must contain exactly one exact reviewed mutation authorization pin"
        )

    safety = _mapping(pipeline.get("safety"), "pipeline.safety")
    required_safety = {
        "sourceModifiedInPlace": False,
        "silentOverwrite": False,
        "existingMutationBoundaryReused": True,
        "existingMapQualityGateReused": True,
        "productionMapExecutionAuthorized": False,
    }
    for key, expected in required_safety.items():
        if safety.get(key) is not expected:
            raise ReviewedCandidateRepairError(f"pipeline safety.{key} is incompatible")

    return {"mode": expected_mode, "candidateSha256": candidate_sha, "qualitySourceSha256": quality["sourceSha256"]}


def _validate_semantic_diff(semantic_diff: Mapping[str, Any], *, source_sha: str, candidate_sha: str) -> dict[str, Any]:
    if semantic_diff.get("format") != SEMANTIC_DIFF_FORMAT or semantic_diff.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewedCandidateRepairError(
            f"semantic diff must use {SEMANTIC_DIFF_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    if semantic_diff.get("ok") is not True:
        raise ReviewedCandidateRepairError("semantic diff is not successful")
    provenance = _mapping(semantic_diff.get("provenance"), "semanticDiff.provenance")
    before = _mapping(provenance.get("before"), "semanticDiff.provenance.before")
    after = _mapping(provenance.get("after"), "semanticDiff.provenance.after")
    before_map = _mapping(before.get("sourceMap"), "semanticDiff.provenance.before.sourceMap")
    after_map = _mapping(after.get("sourceMap"), "semanticDiff.provenance.after.sourceMap")
    if before_map.get("sha256") != source_sha or after_map.get("sha256") != candidate_sha:
        raise ReviewedCandidateRepairError("semantic diff before/after map identity does not match source/candidate")
    before_index = _mapping(before.get("worldIndex"), "semanticDiff.provenance.before.worldIndex")
    after_index = _mapping(after.get("worldIndex"), "semanticDiff.provenance.after.worldIndex")
    before_index_sha = _sha256(before_index.get("sha256"), "semanticDiff before World Index SHA-256")
    after_index_sha = _sha256(after_index.get("sha256"), "semanticDiff after World Index SHA-256")
    scope = _mapping(semantic_diff.get("scope"), "semanticDiff.scope")
    if scope.get("type") not in {"full-index", "bounded-region"}:
        raise ReviewedCandidateRepairError("semantic diff scope type is invalid")
    summary = _mapping(semantic_diff.get("summary"), "semanticDiff.summary")
    findings = _mapping(summary.get("findings"), "semanticDiff.summary.findings")
    return {
        "beforeWorldIndexSha256": before_index_sha,
        "afterWorldIndexSha256": after_index_sha,
        "scopeType": scope["type"],
        "findingsTotal": findings.get("total"),
        "findingsTruncated": findings.get("truncated"),
    }


def _validate_impacted_selection(
    selection: Mapping[str, Any],
    *,
    semantic_diff_pin: Mapping[str, Any],
    source_sha: str,
    candidate_sha: str,
    diff_summary: Mapping[str, Any],
) -> dict[str, Any]:
    if selection.get("format") != IMPACTED_SELECTION_FORMAT or selection.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewedCandidateRepairError(
            f"impacted selection must use {IMPACTED_SELECTION_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    if selection.get("ok") is not True:
        raise ReviewedCandidateRepairError("impacted selection is not successful")
    diff_ref = _mapping(selection.get("semanticDiff"), "impactedSelection.semanticDiff")
    expected_values = {
        "sha256": semantic_diff_pin["sha256"],
        "beforeMapSha256": source_sha,
        "afterMapSha256": candidate_sha,
        "beforeWorldIndexSha256": diff_summary["beforeWorldIndexSha256"],
        "afterWorldIndexSha256": diff_summary["afterWorldIndexSha256"],
        "scopeType": diff_summary["scopeType"],
        "findingsTotal": diff_summary["findingsTotal"],
        "findingsTruncated": diff_summary["findingsTruncated"],
    }
    for key, expected in expected_values.items():
        if diff_ref.get(key) != expected:
            raise ReviewedCandidateRepairError(f"impacted selection semantic diff {key} is incompatible")

    summary = _mapping(selection.get("summary"), "impactedSelection.summary")
    scenarios = selection.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ReviewedCandidateRepairError("impacted selection scenarios must be a non-empty array")
    counts: dict[str, int] = {}
    for key in ("scenarioCount", "selectedCount", "skippedCount", "failClosedCount"):
        value = summary.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ReviewedCandidateRepairError(f"impacted selection {key} must be a non-negative integer")
        counts[key] = value
    if counts["scenarioCount"] != len(scenarios):
        raise ReviewedCandidateRepairError("impacted selection scenario count does not match scenario array")
    if counts["selectedCount"] + counts["skippedCount"] != counts["scenarioCount"]:
        raise ReviewedCandidateRepairError("impacted selection selected/skipped counts are inconsistent")
    actual_selected = sum(1 for scenario in scenarios if isinstance(scenario, Mapping) and scenario.get("selected") is True)
    if actual_selected != counts["selectedCount"]:
        raise ReviewedCandidateRepairError("impacted selection selected count does not match scenario decisions")
    return counts


def _validate_physical_validation(
    physical: Mapping[str, Any],
    *,
    source_sha: str,
    candidate_sha: str,
    pipeline_pin: Mapping[str, Any],
    semantic_diff_pin: Mapping[str, Any],
    impacted_selection_pin: Mapping[str, Any],
    selection_counts: Mapping[str, int],
) -> dict[str, Any]:
    if physical.get("format") != PHYSICAL_VALIDATION_FORMAT or physical.get("schemaVersion") != SCHEMA_VERSION:
        raise ReviewedCandidateRepairError(
            f"physical validation must use {PHYSICAL_VALIDATION_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    if physical.get("ok") is not True:
        raise ReviewedCandidateRepairError("candidate physical validation report is not successful")

    source = _mapping(physical.get("source"), "physicalValidation.source")
    candidate = _mapping(physical.get("candidate"), "physicalValidation.candidate")
    if source.get("sha256") != source_sha or source.get("unchanged") is not True:
        raise ReviewedCandidateRepairError("physical validation source identity is incompatible")
    if candidate.get("sha256") != candidate_sha or candidate.get("createNew") is not True:
        raise ReviewedCandidateRepairError("physical validation candidate identity is incompatible")

    evidence = _mapping(physical.get("evidence"), "physicalValidation.evidence")
    evidence_expectations = {
        "pipelineResult": pipeline_pin["sha256"],
        "semanticDiff": semantic_diff_pin["sha256"],
        "impactedSelection": impacted_selection_pin["sha256"],
    }
    for key, expected_sha in evidence_expectations.items():
        pin = _mapping(evidence.get(key), f"physicalValidation.evidence.{key}")
        if pin.get("sha256") != expected_sha:
            raise ReviewedCandidateRepairError(f"physical validation {key} pin does not match exact input bytes")

    selection = _mapping(physical.get("selection"), "physicalValidation.selection")
    for key in ("scenarioCount", "selectedCount", "skippedCount", "failClosedCount"):
        if selection.get(key) != selection_counts[key]:
            raise ReviewedCandidateRepairError(f"physical validation selection {key} is incompatible")
    selected_scenarios = selection.get("selectedScenarios")
    if not isinstance(selected_scenarios, list) or len(selected_scenarios) != selection_counts["selectedCount"]:
        raise ReviewedCandidateRepairError("physical validation selected scenario list is inconsistent")

    execution = _mapping(physical.get("execution"), "physicalValidation.execution")
    for key in ("requested", "required", "performed"):
        if not isinstance(execution.get(key), bool):
            raise ReviewedCandidateRepairError(f"physical validation execution.{key} must be boolean")
    if execution.get("runtimeWorkspaceRemoved") is not True:
        raise ReviewedCandidateRepairError("physical validation runtime workspace cleanup is not proven")
    scenarios = execution.get("scenarios")
    if not isinstance(scenarios, list):
        raise ReviewedCandidateRepairError("physical validation execution scenarios must be an array")

    selected_count = selection_counts["selectedCount"]
    blockers: list[str] = []
    if selected_count == 0:
        if execution.get("required") is not False:
            raise ReviewedCandidateRepairError("zero selected scenarios cannot require Physical E2E execution")
        status = "validated-no-physical-e2e-required"
        ok = True
    elif execution.get("required") is not True:
        raise ReviewedCandidateRepairError("selected scenarios must require Physical E2E execution")
    elif execution.get("performed") is not True:
        status = "physical-e2e-required"
        ok = False
        blockers.append("SELECTED_PHYSICAL_E2E_NOT_EXECUTED")
    else:
        if len(scenarios) != selected_count:
            raise ReviewedCandidateRepairError("performed Physical E2E scenario count does not match selected count")
        for index, scenario in enumerate(scenarios):
            scenario_map = _mapping(scenario, f"physicalValidation.execution.scenarios[{index}]")
            if scenario_map.get("executed") is not True or scenario_map.get("returnCode") != 0:
                raise ReviewedCandidateRepairError("performed Physical E2E contains a failed or unexecuted selected scenario")
            if scenario_map.get("runtimeMapSha256") != candidate_sha:
                raise ReviewedCandidateRepairError("performed Physical E2E runtime map SHA-256 does not match candidate")
        status = "physically-validated"
        ok = True

    return {
        "mode": physical.get("mode"),
        "required": execution["required"],
        "performed": execution["performed"],
        "status": status,
        "ok": ok,
        "blockers": blockers,
    }


def build_reviewed_candidate_repair_report(
    *,
    recommendation: Mapping[str, Any],
    approval: Mapping[str, Any],
    pipeline_result: Mapping[str, Any],
    semantic_diff: Mapping[str, Any],
    impacted_selection: Mapping[str, Any],
    physical_validation: Mapping[str, Any],
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    recommendation_pin = _input_pin(input_pins.get("recommendation"), RECOMMENDATION_FORMAT, "recommendation")
    approval_pin = _input_pin(input_pins.get("approval"), APPROVAL_FORMAT, "approval")
    pipeline_pin = _input_pin(input_pins.get("pipelineResult"), PIPELINE_FORMAT, "pipelineResult")
    semantic_diff_pin = _input_pin(input_pins.get("semanticDiff"), SEMANTIC_DIFF_FORMAT, "semanticDiff")
    impacted_selection_pin = _input_pin(
        input_pins.get("impactedSelection"), IMPACTED_SELECTION_FORMAT, "impactedSelection"
    )
    physical_validation_pin = _input_pin(
        input_pins.get("physicalValidation"), PHYSICAL_VALIDATION_FORMAT, "physicalValidation"
    )

    recommendation_summary, expected_mode, expected_authorization_format = _validate_recommendation(recommendation)
    approval_summary = _validate_approval(
        approval,
        recommendation_summary=recommendation_summary,
        recommendation_pin=recommendation_pin,
        expected_pipeline_mode=expected_mode,
        expected_authorization_format=expected_authorization_format,
    )
    pipeline_summary = _validate_pipeline(
        pipeline_result,
        source_sha=recommendation_summary["sourceMapSha256"],
        expected_mode=expected_mode,
        authorization=approval_summary["mutationAuthorization"],
    )
    diff_summary = _validate_semantic_diff(
        semantic_diff,
        source_sha=recommendation_summary["sourceMapSha256"],
        candidate_sha=pipeline_summary["candidateSha256"],
    )
    selection_counts = _validate_impacted_selection(
        impacted_selection,
        semantic_diff_pin=semantic_diff_pin,
        source_sha=recommendation_summary["sourceMapSha256"],
        candidate_sha=pipeline_summary["candidateSha256"],
        diff_summary=diff_summary,
    )
    physical_summary = _validate_physical_validation(
        physical_validation,
        source_sha=recommendation_summary["sourceMapSha256"],
        candidate_sha=pipeline_summary["candidateSha256"],
        pipeline_pin=pipeline_pin,
        semantic_diff_pin=semantic_diff_pin,
        impacted_selection_pin=impacted_selection_pin,
        selection_counts=selection_counts,
    )

    blockers = sorted(set(physical_summary["blockers"]))
    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "ok": physical_summary["ok"],
        "status": physical_summary["status"],
        "source": {"mapSha256": recommendation_summary["sourceMapSha256"], "unchanged": True},
        "candidate": {
            "mapSha256": pipeline_summary["candidateSha256"],
            "createNew": True,
            "qualitySourceSha256": pipeline_summary["qualitySourceSha256"],
        },
        "recommendation": {
            "state": recommendation_summary["state"],
            "capability": recommendation_summary["capability"],
            "selector": recommendation_summary["selector"],
            "mutation": recommendation_summary["mutation"],
        },
        "approval": {
            "pipelineMode": approval_summary["pipelineMode"],
            "mutationAuthorization": approval_summary["mutationAuthorization"],
            "review": approval_summary["review"],
        },
        "pipeline": {"mode": pipeline_summary["mode"], "ok": True},
        "semanticDiff": diff_summary,
        "selection": dict(selection_counts),
        "physicalValidation": {
            "mode": physical_summary["mode"],
            "required": physical_summary["required"],
            "performed": physical_summary["performed"],
        },
        "provenance": {
            "recommendation": recommendation_pin,
            "approval": approval_pin,
            "pipelineResult": pipeline_pin,
            "semanticDiff": semantic_diff_pin,
            "impactedSelection": impacted_selection_pin,
            "physicalValidation": physical_validation_pin,
        },
        "blockers": blockers,
        "safety": {
            "approvalGenerated": False,
            "mapModified": False,
            "pipelineExecutedByOrchestrator": False,
            "semanticDiffRecomputed": False,
            "impactedSelectionRecomputed": False,
            "physicalE2eExecutedByOrchestrator": False,
            "existingMutationBoundaryReused": True,
            "existingCandidateValidationReused": True,
            "productionMapDeployed": False,
            "globalGameplayCorrectnessProven": False,
        },
        "notes": [
            "Approval, mutation, static candidate validation and Physical E2E remain separate evidence stages.",
            "A physically validated result is limited to the exact represented selected OTBM-aware scenarios and candidate map provenance.",
            "This orchestrator validates an existing evidence chain and does not execute writers, materializers, Semantic Diff, impacted selection or Physical E2E.",
        ],
    }
