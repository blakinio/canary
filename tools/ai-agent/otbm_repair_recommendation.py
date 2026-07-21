from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

REQUEST_FORMAT = "canary-otbm-repair-recommendation-request-v1"
REPORT_FORMAT = "canary-otbm-repair-recommendation-v1"
PREFLIGHT_FORMAT = "canary-otbm-repair-preflight-v1"
PATCH_PLAN_FORMAT = "canary-otbm-bounded-patch-plan-v1"
SCHEMA_VERSION = 1

RECOMMENDATION_STATES = {
    "no-repair-evidence",
    "review-required",
    "supported-by-existing-attribute-path",
    "supported-by-existing-tile-area-path",
    "supported-by-existing-raw-tile-path",
    "unsupported-mutation-shape",
    "blocked-by-runtime-evidence",
    "ambiguous-target",
}

ATTRIBUTE_OPERATIONS = {
    "set-action-id",
    "set-unique-id",
    "set-house-door-id",
    "set-teleport-destination",
}
RAW_TILE_MODES = {
    "raw-tile-replacement": "bounded-raw-tile-replacement",
    "raw-tile-insertion": "bounded-raw-tile-insertion",
    "raw-tile-deletion": "bounded-raw-tile-deletion",
    "raw-tile-type-conversion": "bounded-raw-tile-type-conversion",
}
BLOCKING_RUNTIME_STATUSES = {
    "unresolved",
    "partially-resolved",
    "referenced-only",
    "conflicting",
    "conflict",
    "unknown",
}
SELECTOR_KEYS = {
    "position",
    "itemId",
    "actionId",
    "uniqueId",
    "houseDoorId",
    "teleportDestination",
}


class RepairRecommendationError(ValueError):
    """Raised when recommendation evidence is malformed or incompatible."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_report_sha256(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _position(value: Any, label: str) -> list[int]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(isinstance(part, bool) or not isinstance(part, int) for part in value)
    ):
        raise RepairRecommendationError(f"{label} must be an integer x,y,z array")
    x, y, z = value
    if not (0 <= x <= 65535 and 0 <= y <= 65535 and 0 <= z <= 15):
        raise RepairRecommendationError(f"{label} is outside the OTBM coordinate range")
    return [x, y, z]


def _selector(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not value:
        raise RepairRecommendationError(f"{label} must be a non-empty object")
    unknown = set(value) - SELECTOR_KEYS
    if unknown:
        raise RepairRecommendationError(f"{label} contains unsupported keys: {sorted(unknown)}")
    result: dict[str, Any] = {}
    for key in sorted(value):
        raw = value[key]
        if key in {"position", "teleportDestination"}:
            result[key] = _position(raw, f"{label}.{key}")
            continue
        maximum = 255 if key == "houseDoorId" else 65535
        if isinstance(raw, bool) or not isinstance(raw, int) or not 0 <= raw <= maximum:
            raise RepairRecommendationError(f"{label}.{key} must be an integer in 0..{maximum}")
        result[key] = raw
    return result


def _input_pin(value: Any, expected_format: str, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RepairRecommendationError(f"{label} input pin must be an object")
    file_name = value.get("fileName")
    size = value.get("size")
    sha256 = value.get("sha256")
    report_format = value.get("format")
    if not isinstance(file_name, str) or not file_name:
        raise RepairRecommendationError(f"{label} input pin fileName must be non-empty")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise RepairRecommendationError(f"{label} input pin size must be a non-negative integer")
    if not _is_sha256(sha256):
        raise RepairRecommendationError(f"{label} input pin sha256 is invalid")
    if report_format != expected_format:
        raise RepairRecommendationError(f"{label} input pin format must be {expected_format}")
    return {"fileName": file_name, "size": size, "sha256": sha256, "format": report_format}


def _validate_request(request: Mapping[str, Any]) -> dict[str, Any]:
    if request.get("format") != REQUEST_FORMAT or request.get("schemaVersion") != SCHEMA_VERSION:
        raise RepairRecommendationError(f"request must use {REQUEST_FORMAT} schemaVersion {SCHEMA_VERSION}")

    finding = request.get("finding")
    if not isinstance(finding, dict):
        raise RepairRecommendationError("request.finding must be an object")
    report_format = finding.get("reportFormat")
    report_sha = finding.get("reportSha256")
    finding_id = finding.get("id")
    if not isinstance(report_format, str) or not report_format:
        raise RepairRecommendationError("request.finding.reportFormat must be non-empty")
    if not _is_sha256(report_sha):
        raise RepairRecommendationError("request.finding.reportSha256 must be a lowercase SHA-256 digest")
    if not isinstance(finding_id, str) or not finding_id:
        raise RepairRecommendationError("request.finding.id must be non-empty")

    source_map_sha = request.get("sourceMapSha256")
    if not _is_sha256(source_map_sha):
        raise RepairRecommendationError("request.sourceMapSha256 must be a lowercase SHA-256 digest")

    selector = _selector(request.get("selector"), "request.selector")
    mutation = request.get("mutation")
    if not isinstance(mutation, dict):
        raise RepairRecommendationError("request.mutation must be an object")
    kind = mutation.get("kind")
    allowed_kinds = {"none", "attribute-replacement", "tile-area-materialization", *RAW_TILE_MODES, "unsupported"}
    if kind not in allowed_kinds:
        raise RepairRecommendationError(f"request.mutation.kind is unsupported: {kind!r}")
    if "expectedOldState" not in mutation:
        raise RepairRecommendationError("request.mutation.expectedOldState is required")
    if "proposedTargetState" not in mutation:
        raise RepairRecommendationError("request.mutation.proposedTargetState is required")

    normalized_mutation: dict[str, Any] = {
        "kind": kind,
        "expectedOldState": mutation["expectedOldState"],
        "proposedTargetState": mutation["proposedTargetState"],
    }
    operation_kind = mutation.get("operationKind")
    if operation_kind is not None:
        if not isinstance(operation_kind, str) or not operation_kind:
            raise RepairRecommendationError("request.mutation.operationKind must be non-empty when present")
        normalized_mutation["operationKind"] = operation_kind

    position = mutation.get("position")
    if position is not None:
        normalized_mutation["position"] = _position(position, "request.mutation.position")

    region = mutation.get("region")
    if region is not None:
        if not isinstance(region, dict):
            raise RepairRecommendationError("request.mutation.region must be an object")
        normalized_mutation["region"] = {
            "policy": region.get("policy"),
            "from": _position(region.get("from"), "request.mutation.region.from"),
            "to": _position(region.get("to"), "request.mutation.region.to"),
            "translationDelta": _position(region.get("translationDelta"), "request.mutation.region.translationDelta"),
        }

    runtime_required = request.get("runtimeHandlingRequired")
    if not isinstance(runtime_required, bool):
        raise RepairRecommendationError("request.runtimeHandlingRequired must be boolean")
    rationale = request.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise RepairRecommendationError("request.rationale must be non-empty")

    return {
        "finding": {
            "reportFormat": report_format,
            "reportSha256": report_sha,
            "id": finding_id,
        },
        "sourceMapSha256": source_map_sha,
        "selector": selector,
        "mutation": normalized_mutation,
        "runtimeHandlingRequired": runtime_required,
        "rationale": rationale.strip(),
    }


def _preflight_summary(preflight: Mapping[str, Any]) -> dict[str, Any]:
    if preflight.get("format") != PREFLIGHT_FORMAT:
        raise RepairRecommendationError(f"repair preflight must use {PREFLIGHT_FORMAT}")
    source = preflight.get("source")
    if not isinstance(source, dict) or not _is_sha256(source.get("sha256")):
        raise RepairRecommendationError("repair preflight source SHA-256 is missing or invalid")
    selector = _selector(preflight.get("selector"), "repairPreflight.selector")
    summary = preflight.get("summary")
    candidates = preflight.get("candidates")
    if not isinstance(summary, dict) or not isinstance(candidates, list):
        raise RepairRecommendationError("repair preflight summary/candidates are malformed")
    matched = summary.get("matchedCandidates")
    if isinstance(matched, bool) or not isinstance(matched, int) or matched < 0:
        raise RepairRecommendationError("repair preflight matchedCandidates must be non-negative")
    if matched != len(candidates):
        raise RepairRecommendationError("repair preflight matchedCandidates does not match candidate count")

    readiness = summary.get("readiness")
    if readiness is None:
        readiness = {
            "matched": matched > 0,
            "correlated": matched == 1 and candidates[0].get("anchorStatus") == "exact" if matched == 1 else False,
            "runtimeResolved": False,
            "runtimeStatus": "unknown",
            "patchable": bool(summary.get("draftPlanReady")),
            "reviewReady": bool(summary.get("draftPlanReady")),
        }
    if not isinstance(readiness, dict):
        raise RepairRecommendationError("repair preflight summary.readiness must be an object")
    required_readiness = {"matched", "correlated", "runtimeResolved", "runtimeStatus", "patchable", "reviewReady"}
    if not required_readiness.issubset(readiness):
        raise RepairRecommendationError("repair preflight summary.readiness is incomplete")

    anchor_statuses: list[str] = []
    candidate_runtime_statuses: list[str] = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise RepairRecommendationError(f"repair preflight candidate {index} must be an object")
        anchor_status = candidate.get("anchorStatus")
        if anchor_status not in {"exact", "missing", "ambiguous"}:
            raise RepairRecommendationError(f"repair preflight candidate {index} anchorStatus is invalid")
        anchor_statuses.append(anchor_status)
        resolution = candidate.get("scriptResolution")
        if isinstance(resolution, dict):
            status = resolution.get("status")
            if isinstance(status, str) and status:
                candidate_runtime_statuses.append(status)

    runtime_status = readiness.get("runtimeStatus")
    if not isinstance(runtime_status, str) or not runtime_status:
        raise RepairRecommendationError("repair preflight runtimeStatus must be non-empty")
    runtime_resolved = readiness.get("runtimeResolved")
    patchable = readiness.get("patchable")
    review_ready = readiness.get("reviewReady")
    correlated = readiness.get("correlated")
    for label, value in (
        ("runtimeResolved", runtime_resolved),
        ("patchable", patchable),
        ("reviewReady", review_ready),
        ("correlated", correlated),
    ):
        if not isinstance(value, bool):
            raise RepairRecommendationError(f"repair preflight readiness.{label} must be boolean")

    draft_plan = preflight.get("draftPlan")
    if draft_plan is not None and not isinstance(draft_plan, dict):
        raise RepairRecommendationError("repair preflight draftPlan must be object or null")

    return {
        "sourceMapSha256": source["sha256"],
        "selector": selector,
        "matchedCandidates": matched,
        "anchorStatuses": sorted(anchor_statuses),
        "candidateRuntimeStatuses": sorted(set(candidate_runtime_statuses)),
        "runtimeStatus": runtime_status,
        "runtimeResolved": runtime_resolved,
        "correlated": correlated,
        "patchable": patchable,
        "reviewReady": review_ready,
        "draftPlan": draft_plan,
        "runtimeUnresolvedCandidates": int(summary.get("runtimeUnresolvedCandidates", 0)),
        "conflictingCandidates": int(summary.get("conflictingCandidates", 0)),
    }


def _area_shape_supported(mutation: Mapping[str, Any]) -> tuple[bool, list[str]]:
    region = mutation.get("region")
    if not isinstance(region, dict):
        return False, ["TILE_AREA_REGION_EVIDENCE_MISSING"]
    if region.get("policy") != "replace-region":
        return False, ["TILE_AREA_POLICY_UNSUPPORTED"]
    if region.get("translationDelta") != [0, 0, 0]:
        return False, ["TILE_AREA_TRANSLATION_UNSUPPORTED"]
    lower = region.get("from")
    upper = region.get("to")
    if not isinstance(lower, list) or not isinstance(upper, list):
        return False, ["TILE_AREA_REGION_EVIDENCE_MISSING"]
    if lower[0] % 256 != 0 or lower[1] % 256 != 0 or upper[0] % 256 != 255 or upper[1] % 256 != 255:
        return False, ["TILE_AREA_PARTIAL_REGION_UNSUPPORTED"]
    if any(upper[index] < lower[index] for index in range(3)):
        return False, ["TILE_AREA_REGION_BOUNDS_REVERSED"]
    return True, []


def _raw_tile_shape_supported(request: Mapping[str, Any]) -> tuple[bool, list[str]]:
    mutation = request["mutation"]
    position = mutation.get("position")
    selector_position = request["selector"].get("position")
    if not isinstance(position, list):
        return False, ["RAW_TILE_POSITION_MISSING"]
    if selector_position is None:
        return False, ["RAW_TILE_SELECTOR_POSITION_MISSING"]
    if position != selector_position:
        return False, ["RAW_TILE_POSITION_SELECTOR_MISMATCH"]
    kind = mutation["kind"]
    old_state = mutation["expectedOldState"]
    target_state = mutation["proposedTargetState"]
    if kind == "raw-tile-insertion" and old_state is not None:
        return False, ["RAW_TILE_INSERTION_EXPECTS_ABSENT_OLD_STATE"]
    if kind == "raw-tile-deletion" and target_state is not None:
        return False, ["RAW_TILE_DELETION_EXPECTS_ABSENT_TARGET_STATE"]
    if kind in {"raw-tile-replacement", "raw-tile-type-conversion"} and (old_state is None or target_state is None):
        return False, ["RAW_TILE_REPLACEMENT_STATE_INCOMPLETE"]
    if kind == "raw-tile-type-conversion":
        if not isinstance(old_state, dict) or not isinstance(target_state, dict):
            return False, ["RAW_TILE_TYPE_CONVERSION_NODE_TYPE_MISSING"]
        old_type = old_state.get("nodeType")
        target_type = target_state.get("nodeType")
        if {old_type, target_type} != {5, 14} or old_type == target_type:
            return False, ["RAW_TILE_TYPE_CONVERSION_NODE_TYPES_UNSUPPORTED"]
    return True, []


def build_repair_recommendation(
    *,
    request: Mapping[str, Any],
    repair_preflight: Mapping[str, Any],
    input_pins: Mapping[str, Any],
) -> dict[str, Any]:
    normalized_request = _validate_request(request)
    preflight = _preflight_summary(repair_preflight)
    request_pin = _input_pin(input_pins.get("request"), REQUEST_FORMAT, "request")
    preflight_pin = _input_pin(input_pins.get("repairPreflight"), PREFLIGHT_FORMAT, "repairPreflight")

    if normalized_request["sourceMapSha256"] != preflight["sourceMapSha256"]:
        raise RepairRecommendationError("request source map SHA-256 does not match repair preflight")
    if normalized_request["selector"] != preflight["selector"]:
        raise RepairRecommendationError("request selector does not exactly match repair preflight selector")

    blockers: list[str] = []
    state = "review-required"
    capability_family: str | None = None
    capability_mode: str | None = None
    technical_path_supported = False

    if preflight["matchedCandidates"] == 0:
        state = "no-repair-evidence"
        blockers.append("NO_MATCHED_REPAIR_TARGET")
    elif preflight["matchedCandidates"] > 1 or "ambiguous" in preflight["anchorStatuses"]:
        state = "ambiguous-target"
        blockers.append("AMBIGUOUS_REPAIR_TARGET")
    elif not preflight["correlated"] or preflight["anchorStatuses"] != ["exact"]:
        state = "review-required"
        blockers.append("EXACT_PATCH_ANCHOR_NOT_PROVEN")
    else:
        runtime_status = preflight["runtimeStatus"]
        runtime_blocked = (
            normalized_request["runtimeHandlingRequired"]
            and (
                not preflight["runtimeResolved"]
                or runtime_status in BLOCKING_RUNTIME_STATUSES
                or preflight["runtimeUnresolvedCandidates"] > 0
                or preflight["conflictingCandidates"] > 0
            )
        )
        if runtime_blocked:
            state = "blocked-by-runtime-evidence"
            blockers.append("RUNTIME_EVIDENCE_NOT_RESOLVED")
        else:
            kind = normalized_request["mutation"]["kind"]
            if kind == "none":
                state = "review-required"
                blockers.append("NO_MUTATION_SHAPE_REQUESTED")
            elif kind == "unsupported":
                state = "unsupported-mutation-shape"
                blockers.append("MUTATION_SHAPE_NOT_IN_EXISTING_CAPABILITY_INVENTORY")
            elif kind == "attribute-replacement":
                operation_kind = normalized_request["mutation"].get("operationKind")
                draft_plan = preflight["draftPlan"]
                if operation_kind not in ATTRIBUTE_OPERATIONS:
                    state = "unsupported-mutation-shape"
                    blockers.append("PHASE8_ATTRIBUTE_OPERATION_UNSUPPORTED")
                elif (
                    not preflight["patchable"]
                    or not preflight["reviewReady"]
                    or not isinstance(draft_plan, dict)
                    or draft_plan.get("format") != PATCH_PLAN_FORMAT
                ):
                    state = "review-required"
                    blockers.append("PHASE8_REVIEW_READY_DRAFT_PLAN_MISSING")
                else:
                    state = "supported-by-existing-attribute-path"
                    capability_family = "phase8-attribute"
                    capability_mode = operation_kind
                    technical_path_supported = True
            elif kind == "tile-area-materialization":
                supported, shape_blockers = _area_shape_supported(normalized_request["mutation"])
                blockers.extend(shape_blockers)
                if supported:
                    state = "supported-by-existing-tile-area-path"
                    capability_family = "tile-area"
                    capability_mode = "complete-zero-translation-replace-region"
                    technical_path_supported = True
                else:
                    state = "unsupported-mutation-shape"
            elif kind in RAW_TILE_MODES:
                supported, shape_blockers = _raw_tile_shape_supported(normalized_request)
                blockers.extend(shape_blockers)
                if supported:
                    state = "supported-by-existing-raw-tile-path"
                    capability_family = "raw-tile"
                    capability_mode = RAW_TILE_MODES[kind]
                    technical_path_supported = True
                else:
                    state = "unsupported-mutation-shape"
            else:
                raise RepairRecommendationError(f"unhandled mutation kind: {kind}")

    if state not in RECOMMENDATION_STATES:
        raise AssertionError(f"invalid recommendation state {state}")

    downstream_requirements = ["human-review-required"]
    if technical_path_supported:
        downstream_requirements.extend(
            [
                "exact-current-state-revalidation-required",
                "writer-specific-evidence-required",
                "explicit-approval-required",
                "create-new-candidate-only",
                "post-mutation-native-reparse-required",
                "post-mutation-world-index-required",
                "post-mutation-semantic-diff-required",
            ]
        )
        if capability_family in {"tile-area", "raw-tile"}:
            downstream_requirements.append("materializer-specific-span-index-provenance-gates-required")
        if capability_family == "tile-area":
            downstream_requirements.append("reviewed-region-merge-plan-required")
        if capability_family == "raw-tile":
            downstream_requirements.append("exact-raw-span-and-canonical-tile-evidence-required")

    return {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "state": state,
        "source": {
            "mapSha256": normalized_request["sourceMapSha256"],
            "finding": normalized_request["finding"],
        },
        "selector": normalized_request["selector"],
        "mutation": normalized_request["mutation"],
        "provenance": {
            "request": request_pin,
            "repairPreflight": preflight_pin,
        },
        "preflight": {
            "matchedCandidates": preflight["matchedCandidates"],
            "anchorStatuses": preflight["anchorStatuses"],
            "runtimeStatus": preflight["runtimeStatus"],
            "runtimeResolved": preflight["runtimeResolved"],
            "correlated": preflight["correlated"],
            "patchable": preflight["patchable"],
            "reviewReady": preflight["reviewReady"],
        },
        "capability": {
            "family": capability_family,
            "mode": capability_mode,
            "technicalPathSupported": technical_path_supported,
            "capabilityOnly": technical_path_supported,
        },
        "blockers": sorted(set(blockers)),
        "downstreamRequirements": sorted(set(downstream_requirements)),
        "review": {
            "requiresHumanReview": True,
            "approvalGenerated": False,
            "mapModified": False,
            "gameplayCorrectnessProven": False,
            "playerIntentProven": False,
            "supportedPathMeansRepairCorrect": False,
        },
        "rationale": normalized_request["rationale"],
        "notes": [
            "This report classifies existing technical mutation capability only and never approves a repair.",
            "All writer/materializer-specific provenance, confinement, approval and post-write gates remain authoritative downstream.",
        ],
    }
