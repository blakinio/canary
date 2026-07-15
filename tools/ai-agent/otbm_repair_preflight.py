from __future__ import annotations

import copy
from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from otbm_bounded_patch_types import PatchPlan, SUPPORTED_OPERATIONS, encoded_width, value_bytes

REPORT_FORMAT = "canary-otbm-repair-preflight-v1"
PLAN_FORMAT = "canary-otbm-bounded-patch-plan-v1"
ANCHOR_FORMATS = {"canary-otbm-patch-anchors-native-v1", "canary-otbm-patch-anchors-v1"}
ITEM_AUDIT_FORMAT = "canary-otbm-item-audit-v1"
SCRIPT_RESOLUTION_FORMAT = "canary-otbm-script-resolution-v1"
MECHANIC_ATTRIBUTES = ("actionId", "uniqueId", "houseDoorId", "teleportDestination")
UNRESOLVED_STATUSES = {"unresolved", "referenced-only", "partially-resolved"}


class PreflightError(ValueError):
    """Raised when repair preflight input cannot be proven or correlated safely."""


def _integer(value: Any, label: str, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise PreflightError(f"{label} must be an integer in {lower}..{upper}")
    return value


def parse_position(value: Any, label: str = "position") -> tuple[int, int, int]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 3:
        raise PreflightError(f"{label} must contain exactly x,y,z")
    return (
        _integer(value[0], f"{label}[0]", 0, 0xFFFF),
        _integer(value[1], f"{label}[1]", 0, 0xFFFF),
        _integer(value[2], f"{label}[2]", 0, 15),
    )


def normalize_selector(selector: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {"position", "itemId", "actionId", "uniqueId", "houseDoorId", "teleportDestination"}
    unknown = sorted(set(selector) - allowed)
    if unknown:
        raise PreflightError(f"unsupported selector fields: {', '.join(unknown)}")
    normalized: dict[str, Any] = {}
    if selector.get("position") is not None:
        normalized["position"] = list(parse_position(selector["position"], "selector.position"))
    if selector.get("itemId") is not None:
        normalized["itemId"] = _integer(selector["itemId"], "selector.itemId", 0, 0xFFFF)
    if selector.get("actionId") is not None:
        normalized["actionId"] = _integer(selector["actionId"], "selector.actionId", 0, 0xFFFF)
    if selector.get("uniqueId") is not None:
        normalized["uniqueId"] = _integer(selector["uniqueId"], "selector.uniqueId", 0, 0xFFFF)
    if selector.get("houseDoorId") is not None:
        normalized["houseDoorId"] = _integer(selector["houseDoorId"], "selector.houseDoorId", 0, 0xFF)
    if selector.get("teleportDestination") is not None:
        normalized["teleportDestination"] = list(
            parse_position(selector["teleportDestination"], "selector.teleportDestination")
        )
    if not normalized:
        raise PreflightError("at least one repair selector is required")
    return normalized


def _require_documents(
    item_audit: Mapping[str, Any],
    anchor_report: Mapping[str, Any],
    script_resolution: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, dict[str, Any]]]:
    if item_audit.get("format") != ITEM_AUDIT_FORMAT:
        raise PreflightError(f"item audit format must be {ITEM_AUDIT_FORMAT}")
    if anchor_report.get("format") not in ANCHOR_FORMATS:
        raise PreflightError("unsupported patch-anchor report format")
    if script_resolution.get("format") != SCRIPT_RESOLUTION_FORMAT:
        raise PreflightError(f"script resolution format must be {SCRIPT_RESOLUTION_FORMAT}")
    mechanics = item_audit.get("mechanicPlacements")
    anchors = anchor_report.get("anchors")
    resolutions = script_resolution.get("placements")
    if not isinstance(mechanics, list) or not all(isinstance(row, dict) for row in mechanics):
        raise PreflightError("item audit mechanicPlacements must be an array of objects")
    if not isinstance(anchors, list) or not all(isinstance(row, dict) for row in anchors):
        raise PreflightError("patch-anchor report anchors must be an array of objects")
    if not isinstance(resolutions, list) or not all(isinstance(row, dict) for row in resolutions):
        raise PreflightError("script resolution placements must be an array of objects")
    resolution_by_index: dict[int, dict[str, Any]] = {}
    for row in resolutions:
        index = row.get("index")
        if not isinstance(index, int) or isinstance(index, bool):
            raise PreflightError("script-resolution placement index must be an integer")
        if index in resolution_by_index:
            raise PreflightError(f"duplicate script-resolution placement index {index}")
        resolution_by_index[index] = row
    expected_indexes = set(range(len(mechanics)))
    actual_indexes = set(resolution_by_index)
    if actual_indexes != expected_indexes:
        missing = sorted(expected_indexes - actual_indexes)
        extra = sorted(actual_indexes - expected_indexes)
        raise PreflightError(
            f"script-resolution placement indexes do not exactly cover item-audit mechanics; "
            f"missing={missing}, extra={extra}"
        )
    return list(mechanics), list(anchors), resolution_by_index


def _matches_selector(placement: Mapping[str, Any], selector: Mapping[str, Any]) -> bool:
    for key, expected in selector.items():
        actual = placement.get(key)
        if key in {"position", "teleportDestination"}:
            if not isinstance(actual, list) or actual != expected:
                return False
        elif actual != expected:
            return False
    return True


def _placement_expected_attributes(placement: Mapping[str, Any]) -> dict[str, Any]:
    return {key: placement[key] for key in MECHANIC_ATTRIBUTES if key in placement}


def _anchor_groups(
    placement: Mapping[str, Any],
    anchors: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    position = placement.get("position")
    item_id = placement.get("itemId")
    item_depth = placement.get("itemDepth", placement.get("depth"))
    expected = _placement_expected_attributes(placement)
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for anchor in anchors:
        if (
            anchor.get("position") != position
            or anchor.get("itemId") != item_id
            or anchor.get("itemDepth") != item_depth
        ):
            continue
        placement_index = anchor.get("tilePlacementIndex")
        if isinstance(placement_index, int) and not isinstance(placement_index, bool):
            grouped[placement_index].append(anchor)
    matches: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for placement_index, rows in sorted(grouped.items()):
        by_attribute: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_attribute[str(row.get("attribute"))].append(row)
        if not all(
            any(row.get("value") == value for row in by_attribute.get(attribute, []))
            for attribute, value in expected.items()
        ):
            continue
        group = {
            "tilePlacementIndex": placement_index,
            "anchors": sorted(rows, key=lambda row: str(row.get("attribute", ""))),
        }
        if any(len(by_attribute.get(attribute, [])) != 1 for attribute in expected):
            ambiguous.append(group)
        else:
            matches.append(group)
    return matches, ambiguous


def correlate_candidates(
    *,
    item_audit: Mapping[str, Any],
    anchor_report: Mapping[str, Any],
    script_resolution: Mapping[str, Any],
    selector: Mapping[str, Any],
) -> list[dict[str, Any]]:
    mechanics, anchors, resolution_by_index = _require_documents(item_audit, anchor_report, script_resolution)
    normalized_selector = normalize_selector(selector)
    candidates: list[dict[str, Any]] = []
    for audit_index, placement in enumerate(mechanics):
        if not _matches_selector(placement, normalized_selector):
            continue
        groups, ambiguous_groups = _anchor_groups(placement, anchors)
        if len(groups) == 1 and not ambiguous_groups:
            anchor_status = "exact"
            tile_placement_index = groups[0]["tilePlacementIndex"]
            exact_anchors = groups[0]["anchors"]
        elif groups or ambiguous_groups:
            anchor_status = "ambiguous"
            tile_placement_index = None
            exact_anchors = [
                anchor
                for group in [*groups, *ambiguous_groups]
                for anchor in group["anchors"]
            ]
        else:
            anchor_status = "missing"
            tile_placement_index = None
            exact_anchors = []
        script = resolution_by_index[audit_index]
        expected_depth = placement.get("itemDepth", placement.get("depth", 0))
        if (
            script.get("itemId") != placement.get("itemId")
            or script.get("position") != placement.get("position")
            or script.get("depth", 0) != expected_depth
        ):
            raise PreflightError(
                f"script-resolution placement {audit_index} identity does not match item-audit mechanic"
            )
        candidates.append(
            {
                "auditIndex": audit_index,
                "placement": dict(placement),
                "anchorStatus": anchor_status,
                "tilePlacementIndex": tile_placement_index,
                "anchors": exact_anchors,
                "scriptResolution": dict(script),
            }
        )
    return candidates


def normalize_replacement(kind: str, value: Any) -> int | tuple[int, int, int]:
    if kind not in SUPPORTED_OPERATIONS:
        raise PreflightError(f"unsupported Phase 8 operation kind: {kind}")
    if kind == "set-teleport-destination":
        return parse_position(value, "replacement")
    maximum = int(SUPPORTED_OPERATIONS[kind][1])
    return _integer(value, "replacement", 0, maximum)


def _ensure_escape_width_compatible(kind: str, expected: Any, replacement: Any) -> None:
    expected_bytes = value_bytes(kind, expected)
    replacement_bytes = value_bytes(kind, replacement)
    incompatible = [
        index
        for index, (old, new) in enumerate(zip(expected_bytes, replacement_bytes, strict=True))
        if encoded_width(old) != encoded_width(new)
    ]
    if incompatible:
        joined = ", ".join(str(index) for index in incompatible)
        raise PreflightError(f"replacement changes OTBM physical escape width at logical byte(s): {joined}")


def build_draft_plan(
    *,
    candidate: Mapping[str, Any],
    source: Mapping[str, Any],
    operation_kind: str,
    replacement: Any,
    operation_id: str,
) -> dict[str, Any]:
    if candidate.get("anchorStatus") != "exact":
        raise PreflightError("draft plan requires one exact patch-anchor placement")
    attribute = SUPPORTED_OPERATIONS.get(operation_kind, (None,))[0]
    if attribute is None:
        raise PreflightError(f"unsupported Phase 8 operation kind: {operation_kind}")
    anchors = candidate.get("anchors")
    if not isinstance(anchors, list):
        raise PreflightError("candidate has no anchor evidence")
    matching = [row for row in anchors if isinstance(row, Mapping) and row.get("attribute") == attribute]
    if len(matching) != 1:
        raise PreflightError(f"candidate does not contain exactly one existing {attribute} anchor")
    replacement_value = normalize_replacement(operation_kind, replacement)
    expected = matching[0].get("value")
    if operation_kind == "set-teleport-destination":
        expected_value: Any = parse_position(expected, "anchor.value")
        plan_expected: Any = list(expected_value)
        plan_replacement: Any = list(replacement_value)  # type: ignore[arg-type]
    else:
        maximum = int(SUPPORTED_OPERATIONS[operation_kind][1])
        expected_value = _integer(expected, "anchor.value", 0, maximum)
        plan_expected = expected_value
        plan_replacement = replacement_value
    if expected_value == replacement_value:
        raise PreflightError("replacement is identical to the existing attribute value")
    _ensure_escape_width_compatible(operation_kind, expected_value, replacement_value)

    required_source = ("fileName", "sha256", "size", "otbmVersion", "itemsMajor", "itemsMinor")
    missing = [key for key in required_source if source.get(key) is None]
    if missing:
        raise PreflightError(f"source pin is missing: {', '.join(missing)}")
    position = parse_position(candidate.get("placement", {}).get("position"), "candidate.position")
    operation = {
        "id": operation_id,
        "kind": operation_kind,
        "position": list(position),
        "tilePlacementIndex": _integer(
            candidate.get("tilePlacementIndex"),
            "candidate.tilePlacementIndex",
            0,
            0xFFFFFFFF,
        ),
        "itemId": _integer(candidate.get("placement", {}).get("itemId"), "candidate.itemId", 0, 0xFFFF),
        "itemDepth": _integer(
            candidate.get("placement", {}).get("itemDepth", candidate.get("placement", {}).get("depth")),
            "candidate.itemDepth",
            0,
            0x7FFF,
        ),
        "expected": plan_expected,
        "replacement": plan_replacement,
    }
    plan = {
        "format": PLAN_FORMAT,
        "source": {key: source[key] for key in required_source},
        "region": {"from": list(position), "to": list(position)},
        "operations": [operation],
    }
    try:
        PatchPlan.from_raw(plan)
    except (ValueError, TypeError) as exc:
        raise PreflightError(f"generated draft plan violates the existing Phase 8 plan contract: {exc}") from exc
    return plan


def build_hypothetical_item_audit(
    *,
    item_audit: Mapping[str, Any],
    audit_index: int,
    operation_kind: str,
    replacement: Any,
) -> dict[str, Any]:
    if item_audit.get("format") != ITEM_AUDIT_FORMAT:
        raise PreflightError(f"item audit format must be {ITEM_AUDIT_FORMAT}")
    mechanics = item_audit.get("mechanicPlacements")
    if not isinstance(mechanics, list) or not 0 <= audit_index < len(mechanics):
        raise PreflightError("hypothetical replacement audit index is out of range")
    attribute = SUPPORTED_OPERATIONS.get(operation_kind, (None,))[0]
    if attribute is None:
        raise PreflightError(f"unsupported Phase 8 operation kind: {operation_kind}")
    placement = mechanics[audit_index]
    if not isinstance(placement, Mapping) or attribute not in placement:
        raise PreflightError(f"hypothetical replacement requires existing {attribute} attribute")
    normalized = normalize_replacement(operation_kind, replacement)
    updated = copy.deepcopy(dict(item_audit))
    updated_placement = updated["mechanicPlacements"][audit_index]
    updated_placement[attribute] = list(normalized) if isinstance(normalized, tuple) else normalized
    return updated


def build_preflight_report(
    *,
    item_audit: Mapping[str, Any],
    anchor_report: Mapping[str, Any],
    script_resolution: Mapping[str, Any],
    selector: Mapping[str, Any],
    source: Mapping[str, Any],
    operation_kind: str | None = None,
    replacement: Any = None,
    operation_id: str = "repair-1",
) -> dict[str, Any]:
    normalized_selector = normalize_selector(selector)
    candidates = correlate_candidates(
        item_audit=item_audit,
        anchor_report=anchor_report,
        script_resolution=script_resolution,
        selector=normalized_selector,
    )
    anchor_counts = Counter(candidate["anchorStatus"] for candidate in candidates)
    script_counts = Counter(str(candidate["scriptResolution"].get("status", "unknown")) for candidate in candidates)
    unresolved = sum(count for status, count in script_counts.items() if status in UNRESOLVED_STATUSES)
    conflicts = script_counts.get("conflicting", 0)
    warnings: list[str] = []
    if not candidates:
        warnings.append("No mechanic placement matched all supplied selectors.")
    if anchor_counts.get("missing"):
        warnings.append("At least one matched mechanic placement has no exact Phase 8 patch-anchor correlation.")
    if anchor_counts.get("ambiguous"):
        warnings.append(
            "At least one matched mechanic placement has ambiguous Phase 8 patch-anchor correlation; do not guess."
        )
    if unresolved:
        warnings.append(
            "At least one matched placement remains runtime-unresolved or partially resolved; unresolved evidence is preserved."
        )
    if conflicts:
        warnings.append("At least one matched placement has conflicting runtime handlers.")

    draft_plan = None
    draft_error = None
    if operation_kind is not None:
        if len(candidates) != 1:
            draft_error = f"draft plan requires exactly one matched candidate; found {len(candidates)}"
        else:
            try:
                draft_plan = build_draft_plan(
                    candidate=candidates[0],
                    source=source,
                    operation_kind=operation_kind,
                    replacement=replacement,
                    operation_id=operation_id,
                )
            except PreflightError as exc:
                draft_error = str(exc)
        if draft_error:
            warnings.append(f"Draft plan not ready: {draft_error}")

    return {
        "format": REPORT_FORMAT,
        "ok": bool(candidates),
        "selector": normalized_selector,
        "source": dict(source),
        "summary": {
            "matchedCandidates": len(candidates),
            "anchorStatusCounts": dict(sorted(anchor_counts.items())),
            "scriptStatusCounts": dict(sorted(script_counts.items())),
            "runtimeUnresolvedCandidates": unresolved,
            "conflictingCandidates": conflicts,
            "draftPlanReady": draft_plan is not None,
        },
        "candidates": candidates,
        "draftPlan": draft_plan,
        "draftPlanError": draft_error,
        "warnings": warnings,
        "review": {
            "requiresHumanReview": True,
            "gameplayCorrectnessProven": False,
            "playerIntentProven": False,
            "unresolvedEvidencePreserved": True,
            "mapModified": False,
        },
    }
