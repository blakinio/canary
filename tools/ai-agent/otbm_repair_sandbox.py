from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from otbm_bounded_patch_types import PatchOperation, PatchPlan, RESULT_FORMAT, SUPPORTED_OPERATIONS
from otbm_repair_preflight import (
    MECHANIC_ATTRIBUTES,
    correlate_candidates,
    diff_script_resolution_placements,
    is_runtime_resolved_status,
)

REPORT_FORMAT = "canary-otbm-repair-sandbox-verification-v1"
REQUIRED_PHASE8_PROOFS = (
    "fileLengthPreserved",
    "outsideScannerSpansEqual",
    "fullScannerReparse",
    "worldIndexBeforeAfterBuilt",
    "boundedSemanticDiffExact",
)
UNRESOLVED_STATUSES = {"unresolved", "referenced-only", "partially-resolved"}


class RepairSandboxError(ValueError):
    """Raised when sandbox repair evidence cannot be proven exactly."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RepairSandboxError(f"{label} must be an object")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise RepairSandboxError(f"{label} must be an array")
    return value


def _json_value(value: Any) -> Any:
    return list(value) if isinstance(value, tuple) else value


def _operation_contract(operation: PatchOperation) -> dict[str, Any]:
    return {
        "id": operation.operation_id,
        "kind": operation.kind,
        "position": list(operation.position),
        "tilePlacementIndex": operation.tile_placement_index,
        "itemId": operation.item_id,
        "itemDepth": operation.item_depth,
        "attribute": operation.attribute,
        "expected": _json_value(operation.expected),
        "replacement": _json_value(operation.replacement),
    }


def validate_phase8_result(result: Mapping[str, Any], plan: PatchPlan) -> None:
    if result.get("format") != RESULT_FORMAT or result.get("ok") is not True:
        raise RepairSandboxError("Phase 8 bounded patch did not return a successful v1 result")
    result_plan = _mapping(result.get("plan"), "phase8.plan")
    if result_plan.get("format") != "canary-otbm-bounded-patch-plan-v1":
        raise RepairSandboxError("Phase 8 result does not reference the v1 patch-plan contract")

    source = _mapping(result.get("source"), "phase8.source")
    if (
        source.get("sha256") != plan.source.sha256
        or source.get("size") != plan.source.size
        or source.get("unchanged") is not True
    ):
        raise RepairSandboxError("Phase 8 result does not prove the expected source remained unchanged")

    output = _mapping(result.get("output"), "phase8.output")
    if output.get("atomicCopyOnly") is not True:
        raise RepairSandboxError("Phase 8 result does not prove copy-only output publication")

    proof = _mapping(result.get("proof"), "phase8.proof")
    missing_proofs = [name for name in REQUIRED_PHASE8_PROOFS if proof.get(name) is not True]
    if missing_proofs:
        raise RepairSandboxError(f"Phase 8 proof is incomplete: {', '.join(missing_proofs)}")

    policy = _mapping(result.get("policy"), "phase8.policy")
    if policy.get("sourceModifiedInPlace") is not False:
        raise RepairSandboxError("Phase 8 policy does not prove the source was never modified in place")
    if policy.get("newOtbmParserCreated") is not False:
        raise RepairSandboxError("Phase 8 result violates the existing-parser boundary")
    if policy.get("existingNativeScannerReused") is not True:
        raise RepairSandboxError("Phase 8 result does not prove native scanner reuse")
    if policy.get("existingWorldIndexReused") is not True or policy.get("existingSemanticDiffReused") is not True:
        raise RepairSandboxError("Phase 8 result does not prove World Index/Semantic Diff reuse")

    raw_operations = _list(result.get("operations"), "phase8.operations")
    expected = {operation.operation_id: _operation_contract(operation) for operation in plan.operations}
    if len(raw_operations) != len(expected):
        raise RepairSandboxError("Phase 8 result operation count does not match the patch plan")
    actual: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(raw_operations):
        row = dict(_mapping(raw, f"phase8.operations[{index}]"))
        operation_id = row.get("id")
        if not isinstance(operation_id, str) or operation_id in actual:
            raise RepairSandboxError("Phase 8 result operation IDs are missing or duplicated")
        actual[operation_id] = {
            key: row.get(key)
            for key in (
                "id",
                "kind",
                "position",
                "tilePlacementIndex",
                "itemId",
                "itemDepth",
                "attribute",
                "expected",
                "replacement",
            )
        }
    if actual != expected:
        raise RepairSandboxError("Phase 8 resolved operations do not exactly match the patch plan")


def _candidate_for_operation(
    *,
    operation: PatchOperation,
    expected_value: Any,
    item_audit: Mapping[str, Any],
    anchor_report: Mapping[str, Any],
    script_resolution: Mapping[str, Any],
    label: str,
) -> dict[str, Any]:
    selector = {
        "position": list(operation.position),
        "itemId": operation.item_id,
        operation.attribute: expected_value,
    }
    candidates = correlate_candidates(
        item_audit=item_audit,
        anchor_report=anchor_report,
        script_resolution=script_resolution,
        selector=selector,
    )
    exact = []
    for candidate in candidates:
        placement = _mapping(candidate.get("placement"), f"{label} candidate placement")
        depth = placement.get("itemDepth", placement.get("depth"))
        if (
            candidate.get("anchorStatus") == "exact"
            and candidate.get("tilePlacementIndex") == operation.tile_placement_index
            and placement.get("itemId") == operation.item_id
            and depth == operation.item_depth
        ):
            exact.append(candidate)
    if len(exact) != 1:
        raise RepairSandboxError(
            f"operation {operation.operation_id} requires exactly one {label} candidate at the planned tile placement; found {len(exact)}"
        )
    return dict(exact[0])


def _mechanic_snapshot(placement: Mapping[str, Any]) -> dict[str, Any]:
    result = {
        "itemId": placement.get("itemId"),
        "position": placement.get("position"),
        "itemDepth": placement.get("itemDepth", placement.get("depth")),
    }
    for attribute in MECHANIC_ATTRIBUTES:
        if attribute in placement:
            result[attribute] = placement[attribute]
    return result


def verify_operation(
    *,
    operation: PatchOperation,
    before_item_audit: Mapping[str, Any],
    after_item_audit: Mapping[str, Any],
    before_anchors: Mapping[str, Any],
    after_anchors: Mapping[str, Any],
    before_script_resolution: Mapping[str, Any],
    after_script_resolution: Mapping[str, Any],
) -> dict[str, Any]:
    expected = _json_value(operation.expected)
    replacement = _json_value(operation.replacement)
    before = _candidate_for_operation(
        operation=operation,
        expected_value=expected,
        item_audit=before_item_audit,
        anchor_report=before_anchors,
        script_resolution=before_script_resolution,
        label="before",
    )
    after = _candidate_for_operation(
        operation=operation,
        expected_value=replacement,
        item_audit=after_item_audit,
        anchor_report=after_anchors,
        script_resolution=after_script_resolution,
        label="after",
    )

    before_placement = _mapping(before.get("placement"), "before placement")
    after_placement = _mapping(after.get("placement"), "after placement")
    before_snapshot = _mechanic_snapshot(before_placement)
    after_snapshot = _mechanic_snapshot(after_placement)
    for key, wanted in (
        ("itemId", operation.item_id),
        ("position", list(operation.position)),
        ("itemDepth", operation.item_depth),
    ):
        if before_snapshot.get(key) != wanted or after_snapshot.get(key) != wanted:
            raise RepairSandboxError(f"operation {operation.operation_id} changed or lost placement identity field {key}")
    if before_snapshot.get(operation.attribute) != expected:
        raise RepairSandboxError(f"operation {operation.operation_id} before audit does not contain the planned expected value")
    if after_snapshot.get(operation.attribute) != replacement:
        raise RepairSandboxError(f"operation {operation.operation_id} after audit does not contain the planned replacement value")

    for attribute in MECHANIC_ATTRIBUTES:
        if attribute == operation.attribute:
            continue
        if before_snapshot.get(attribute) != after_snapshot.get(attribute):
            raise RepairSandboxError(
                f"operation {operation.operation_id} changed untargeted mechanic attribute {attribute}"
            )

    before_resolution = _mapping(before.get("scriptResolution"), "before script resolution")
    after_resolution = _mapping(after.get("scriptResolution"), "after script resolution")
    runtime_diff = diff_script_resolution_placements(before_resolution, after_resolution)
    before_status = str(before_resolution.get("status", "unknown"))
    after_status = str(after_resolution.get("status", "unknown"))
    runtime_regression = is_runtime_resolved_status(before_status) and not is_runtime_resolved_status(after_status)

    return {
        **_operation_contract(operation),
        "before": {
            "auditIndex": before.get("auditIndex"),
            "placement": before_snapshot,
            "runtimeStatus": before_status,
            "scriptResolution": dict(before_resolution),
        },
        "after": {
            "auditIndex": after.get("auditIndex"),
            "placement": after_snapshot,
            "runtimeStatus": after_status,
            "scriptResolution": dict(after_resolution),
        },
        "runtimeResolutionChanged": runtime_diff["changed"],
        "runtimeRegression": runtime_regression,
        "replacementRuntimeResolved": is_runtime_resolved_status(after_status),
        "runtimeDiff": runtime_diff,
    }


def build_verification_report(
    *,
    plan: PatchPlan,
    phase8_result: Mapping[str, Any],
    operation_results: list[Mapping[str, Any]],
    pins: Mapping[str, Any],
) -> dict[str, Any]:
    validate_phase8_result(phase8_result, plan)
    if len(operation_results) != len(plan.operations):
        raise RepairSandboxError("verified operation count does not match the patch plan")
    ids = [str(row.get("id")) for row in operation_results]
    if ids != [operation.operation_id for operation in plan.operations]:
        raise RepairSandboxError("verified operation order/identity does not match the patch plan")

    before_statuses = Counter(str(row.get("before", {}).get("runtimeStatus", "unknown")) for row in operation_results)
    after_statuses = Counter(str(row.get("after", {}).get("runtimeStatus", "unknown")) for row in operation_results)
    unresolved_after = sum(after_statuses.get(status, 0) for status in UNRESOLVED_STATUSES)
    conflicts_after = after_statuses.get("conflicting", 0)
    runtime_changed = sum(bool(row.get("runtimeResolutionChanged")) for row in operation_results)
    regressions = sum(bool(row.get("runtimeRegression")) for row in operation_results)

    return {
        "format": REPORT_FORMAT,
        "ok": True,
        "source": {
            "fileName": plan.source.file_name,
            "sha256": plan.source.sha256,
            "size": plan.source.size,
            "unchanged": True,
        },
        "patchedOutput": dict(_mapping(phase8_result.get("output"), "phase8.output")),
        "phase8": {
            "format": phase8_result.get("format"),
            "plan": dict(_mapping(phase8_result.get("plan"), "phase8.plan")),
            "proof": dict(_mapping(phase8_result.get("proof"), "phase8.proof")),
            "evidence": dict(_mapping(phase8_result.get("evidence"), "phase8.evidence")),
        },
        "inputs": dict(pins),
        "summary": {
            "operations": len(operation_results),
            "runtimeResolutionChangedOperations": runtime_changed,
            "runtimeRegressionOperations": regressions,
            "runtimeUnresolvedAfter": unresolved_after,
            "runtimeConflictingAfter": conflicts_after,
            "beforeStatusCounts": dict(sorted(before_statuses.items())),
            "afterStatusCounts": dict(sorted(after_statuses.items())),
        },
        "operations": [dict(row) for row in operation_results],
        "review": {
            "requiresHumanReview": True,
            "runtimeRegressionObserved": regressions > 0,
            "unresolvedEvidencePreserved": True,
            "gameplayCorrectnessProven": False,
            "playerIntentProven": False,
            "reachabilityProven": False,
            "physicalClientE2EProven": False,
        },
        "policy": {
            "sourceModifiedInPlace": False,
            "sandboxCopyOnly": True,
            "newOtbmParserCreated": False,
            "newOtbmWriterCreated": False,
            "phase8BoundedPatcherReused": True,
            "phase8WorldIndexProofReused": True,
            "phase8SemanticDiffProofReused": True,
            "mapQualityGateAutoGenerated": False,
        },
        "notes": [
            "A successful sandbox verification proves bounded mutation confinement and observed static before/after mechanic evidence only.",
            "Runtime unresolved or conflicting evidence is preserved and never promoted to handled by this verifier.",
            "Reachability and gameplay correctness require separate explicit evidence; no origins, routes or transitions are invented.",
        ],
    }
