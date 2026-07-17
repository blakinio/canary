from __future__ import annotations

from typing import Any, Mapping, Sequence

TILE_REPLACEMENT_MODE = "tile-replacement"
TILE_INSERTION_MODE = "tile-insertion"
TILE_DELETION_MODE = "tile-deletion"
TILE_TYPE_CONVERSION_MODE = "tile-type-conversion"
RAW_TILE_MODES = {
    TILE_REPLACEMENT_MODE,
    TILE_INSERTION_MODE,
    TILE_DELETION_MODE,
    TILE_TYPE_CONVERSION_MODE,
}

REPORT_FORMATS = {
    TILE_REPLACEMENT_MODE: "canary-otbm-tile-materialization-result-v1",
    TILE_INSERTION_MODE: "canary-otbm-tile-insertion-result-v1",
    TILE_DELETION_MODE: "canary-otbm-tile-deletion-result-v1",
    TILE_TYPE_CONVERSION_MODE: "canary-otbm-tile-type-conversion-result-v1",
}
VERIFICATION_FIELDS = {
    TILE_REPLACEMENT_MODE: (
        "nativeReparse", "worldIndexRebuilt", "selectedTilesEqualDonor", "nonSelectedCurrentBytesExact"
    ),
    TILE_INSERTION_MODE: (
        "nativeReparse", "worldIndexRebuilt", "insertedTilesEqualDonor", "completeCurrentByteSequenceExact"
    ),
    TILE_DELETION_MODE: (
        "nativeReparse", "worldIndexRebuilt", "deletedTilesAbsent", "retainedCurrentByteSequenceExact", "parentTileAreasPreserved"
    ),
    TILE_TYPE_CONVERSION_MODE: (
        "nativeReparse", "worldIndexRebuilt", "selectedTilesEqualDonor", "nonSelectedCurrentBytesExact"
    ),
}
SAFETY_TRUE_FIELDS = {
    TILE_REPLACEMENT_MODE: (
        "rawCompleteTileSubtreesOnly", "sameCoordinateOnly", "sameParentTileAreaOnly", "sameNodeTypeOnly", "separateApprovalRequired"
    ),
    TILE_INSERTION_MODE: (
        "tileInsertion", "rawCompleteTileSubtreesOnly", "sameCoordinateOnly", "existingParentTileAreaOnly", "separateApprovalRequired"
    ),
    TILE_DELETION_MODE: (
        "tileDeletion", "rawCompleteTileSubtreesOnly", "sameCoordinateOnly", "parentTileAreaPreserved", "separateApprovalRequired"
    ),
    TILE_TYPE_CONVERSION_MODE: (
        "tileTypeConversion", "rawCompleteTileSubtreesOnly", "sameCoordinateOnly", "sameParentTileAreaOnly", "separateApprovalRequired"
    ),
}


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def validate_raw_tile_report(
    *,
    mode: str,
    report: Mapping[str, Any],
    source_sha256: str,
    candidate_sha256: str,
    candidate_size: int,
) -> dict[str, Any]:
    if mode not in RAW_TILE_MODES:
        raise ValueError(f"unsupported raw tile mutation mode: {mode}")
    if report.get("format") != REPORT_FORMATS[mode] or report.get("ok") is not True:
        raise ValueError(f"{mode} mutation did not produce a successful materialization report")
    if report.get("structuralVerificationComplete") is not True:
        raise ValueError(f"{mode} structural verification is incomplete")

    source = _mapping(report.get("source"), f"{mode} source")
    current = _mapping(source.get("current"), f"{mode} current source")
    output = _mapping(source.get("output"), f"{mode} output")
    if current.get("sha256") != source_sha256:
        raise ValueError(f"{mode} report does not reference the expected current source")
    if output.get("sha256") != candidate_sha256 or output.get("size") != candidate_size:
        raise ValueError(f"{mode} output pin does not match the pipeline candidate")

    verification = _mapping(report.get("verification"), f"{mode} verification")
    missing = [name for name in VERIFICATION_FIELDS[mode] if verification.get(name) is not True]
    if missing:
        raise ValueError(f"{mode} verification is incomplete: " + ", ".join(missing))

    safety = _mapping(report.get("safety"), f"{mode} safety")
    required_false: Sequence[str] = ("sourceInPlaceWrite", "fullMapSerializer", "arbitraryNodeSerialization")
    invalid_false = [name for name in required_false if safety.get(name) is not False]
    missing_true = [name for name in SAFETY_TRUE_FIELDS[mode] if safety.get(name) is not True]
    if invalid_false or missing_true:
        raise ValueError(f"{mode} safety boundary is incomplete: " + ", ".join(invalid_false + missing_true))

    return {
        "selection": dict(_mapping(report.get("selection"), f"{mode} selection")),
        "structuralVerificationComplete": True,
    }
