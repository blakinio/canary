from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping

from otbm_area_materializer import (
    _assert_pin,
    _check_ancestors,
    _confined_existing,
    _load_json,
    _new_confined_path,
    _prepare_artifact_root,
    _publish_directory_no_overwrite,
    _relative,
    _resolve_existing_regular,
    _stat_pin,
    _validate_header_compatibility,
    _write_json,
)
from otbm_semantic_diff import analyze_index_paths
from otbm_semantic_diff_types import sha256_path
from otbm_tile_materializer import (
    MAX_SELECTIONS,
    SCHEMA_VERSION,
    Position,
    TileMaterializerError,
    _area_key,
    _canonical_tile,
    _materialize_raw_tiles,
    _position,
    _selected_spans,
    _selection_side_matches,
    _span_index,
    _validate_manifest_bundle,
    _verify_selected_world_index,
    scan_tile_spans,
)
from otbm_world_index import WorldIndex, build_world_index

APPROVAL_FORMAT = "canary-otbm-tile-type-conversion-approval-v1"
RESULT_FORMAT = "canary-otbm-tile-type-conversion-result-v1"
SUPPORTED_NODE_TYPES = {5, 14}


class TileTypeConversionMaterializerError(TileMaterializerError):
    pass


def _validate_conversion_approval(
    *,
    approval: Mapping[str, Any],
    current_report: Mapping[str, Any],
    donor_report: Mapping[str, Any],
    current_index_path: Path,
    donor_index_path: Path,
) -> tuple[list[Position], list[dict[str, Any]]]:
    if approval.get("format") != APPROVAL_FORMAT or approval.get("schemaVersion") != SCHEMA_VERSION:
        raise TileTypeConversionMaterializerError(
            f"approval must use {APPROVAL_FORMAT} schemaVersion {SCHEMA_VERSION}"
        )
    if approval.get("decision") != "approved":
        raise TileTypeConversionMaterializerError("approval decision must be 'approved'")
    if not str(approval.get("rationale", "")).strip():
        raise TileTypeConversionMaterializerError("approval requires a non-empty rationale")

    raw_selections = approval.get("selections")
    if not isinstance(raw_selections, list) or not raw_selections:
        raise TileTypeConversionMaterializerError("approval selections must be a non-empty array")
    if len(raw_selections) > MAX_SELECTIONS:
        raise TileTypeConversionMaterializerError(
            f"approval exceeds the bounded selection limit of {MAX_SELECTIONS}"
        )

    current_spans = _span_index(current_report)
    donor_spans = _span_index(donor_report)
    positions: list[Position] = []
    conversions: list[dict[str, Any]] = []
    seen: set[Position] = set()

    with WorldIndex(current_index_path) as current_index, WorldIndex(donor_index_path) as donor_index:
        for selection_index, raw in enumerate(raw_selections):
            if not isinstance(raw, dict):
                raise TileTypeConversionMaterializerError(
                    f"approval selections[{selection_index}] must be an object"
                )
            position = _position(
                raw.get("position"), f"approval selections[{selection_index}].position"
            )
            if position in seen:
                raise TileTypeConversionMaterializerError(
                    f"approval contains duplicate selected position {position}"
                )
            seen.add(position)

            expected_area = (position[0] & 0xFF00, position[1] & 0xFF00, position[2])
            approved_area = _area_key(
                raw.get("areaKey"), f"approval selections[{selection_index}].areaKey"
            )
            if approved_area != expected_area:
                raise TileTypeConversionMaterializerError(
                    f"approval selected position {position} does not match its canonical TILE_AREA key"
                )

            current_matches = current_spans.get(position, [])
            donor_matches = donor_spans.get(position, [])
            if len(current_matches) != 1 or len(donor_matches) != 1:
                raise TileTypeConversionMaterializerError(
                    f"selected position {position} must exist exactly once in both current and donor maps"
                )

            current_span = current_matches[0]
            donor_span = donor_matches[0]
            current_area = (
                int(current_span["areaBaseX"]),
                int(current_span["areaBaseY"]),
                int(current_span["areaZ"]),
            )
            donor_area = (
                int(donor_span["areaBaseX"]),
                int(donor_span["areaBaseY"]),
                int(donor_span["areaZ"]),
            )
            if current_area != approved_area or donor_area != approved_area:
                raise TileTypeConversionMaterializerError(
                    f"selected position {position} does not share the approved parent TILE_AREA key"
                )

            current_node_type = int(current_span["nodeType"])
            donor_node_type = int(donor_span["nodeType"])
            if current_node_type not in SUPPORTED_NODE_TYPES or donor_node_type not in SUPPORTED_NODE_TYPES:
                raise TileTypeConversionMaterializerError(
                    f"selected position {position} uses an unsupported tile node type"
                )
            if current_node_type == donor_node_type:
                raise TileTypeConversionMaterializerError(
                    f"tile type conversion requires different current/donor node types at selected position {position}"
                )

            current_side = raw.get("current")
            donor_side = raw.get("donor")
            if not isinstance(current_side, dict) or not isinstance(donor_side, dict):
                raise TileTypeConversionMaterializerError(
                    f"approval selection {position} is missing current/donor expected state"
                )

            current_canonical, _ = _canonical_tile(current_index, position)
            donor_canonical, _ = _canonical_tile(donor_index, position)
            _selection_side_matches(
                side=current_side,
                span=current_span,
                canonical_sha256=current_canonical,
                label=f"current tile {position}",
            )
            _selection_side_matches(
                side=donor_side,
                span=donor_span,
                canonical_sha256=donor_canonical,
                label=f"donor tile {position}",
            )

            positions.append(position)
            conversions.append(
                {
                    "position": list(position),
                    "areaKey": list(approved_area),
                    "fromNodeType": current_node_type,
                    "toNodeType": donor_node_type,
                    "fromKind": current_span.get("kind"),
                    "toKind": donor_span.get("kind"),
                }
            )

    return positions, conversions


def materialize_tile_type_conversions(
    *,
    artifact_root: Path,
    current_map_path: Path,
    donor_map_path: Path,
    scanner_path: Path,
    approval_path: Path,
    current_index_path: Path,
    current_manifest_path: Path,
    donor_index_path: Path,
    donor_manifest_path: Path,
    output_map_path: Path,
    evidence_dir: Path,
    timeout_seconds: int = 3600,
) -> dict[str, Any]:
    root = _prepare_artifact_root(artifact_root)
    current_map = _resolve_existing_regular(current_map_path, "current map")
    donor_map = _resolve_existing_regular(donor_map_path, "donor map")
    scanner = _resolve_existing_regular(scanner_path, "extended native scanner", executable=True)
    approval_source = _confined_existing(root, approval_path, "tile type conversion approval")
    current_index = _confined_existing(root, current_index_path, "current World Index")
    current_manifest = _confined_existing(root, current_manifest_path, "current World Index manifest")
    donor_index = _confined_existing(root, donor_index_path, "donor World Index")
    donor_manifest = _confined_existing(root, donor_manifest_path, "donor World Index manifest")
    output = _new_confined_path(root, output_map_path, "output map")
    evidence_output = _new_confined_path(root, evidence_dir, "evidence directory", directory=True)

    if output == current_map or output == donor_map:
        raise TileTypeConversionMaterializerError(
            "output map must be distinct from current and donor maps"
        )
    try:
        output.relative_to(evidence_output)
    except ValueError:
        pass
    else:
        raise TileTypeConversionMaterializerError(
            "output map must not be created inside the evidence directory"
        )

    current_pin = _stat_pin(current_map)
    donor_pin = _stat_pin(donor_map)
    scanner_pin = _stat_pin(scanner)
    approval = _load_json(approval_source, "tile type conversion approval")
    provenance = approval.get("provenance")
    if not isinstance(provenance, dict):
        raise TileTypeConversionMaterializerError("approval has no provenance object")
    current_provenance = provenance.get("current")
    donor_provenance = provenance.get("donor")
    if not isinstance(current_provenance, dict) or not isinstance(donor_provenance, dict):
        raise TileTypeConversionMaterializerError(
            "approval current/donor provenance is incomplete"
        )

    _validate_manifest_bundle(
        role="current",
        map_path=current_map,
        index_path=current_index,
        manifest_path=current_manifest,
        provenance=current_provenance,
    )
    _validate_manifest_bundle(
        role="donor",
        map_path=donor_map,
        index_path=donor_index,
        manifest_path=donor_manifest,
        provenance=donor_provenance,
    )

    workspace = Path(tempfile.mkdtemp(prefix=".otbm-tile-type-conversion-", dir=root))
    evidence_workspace = workspace / "evidence"
    evidence_workspace.mkdir()
    candidate = workspace / "candidate.otbm"
    published_output = False

    try:
        current_spans = scan_tile_spans(
            map_path=current_map,
            scanner=scanner,
            workspace=workspace,
            role="current",
            timeout_seconds=timeout_seconds,
        )
        donor_spans = scan_tile_spans(
            map_path=donor_map,
            scanner=scanner,
            workspace=workspace,
            role="donor",
            timeout_seconds=timeout_seconds,
        )
        _validate_header_compatibility(current_spans, donor_spans)

        positions, conversions = _validate_conversion_approval(
            approval=approval,
            current_report=current_spans,
            donor_report=donor_spans,
            current_index_path=current_index,
            donor_index_path=donor_index,
        )

        raw_proof = _materialize_raw_tiles(
            current_map=current_map,
            donor_map=donor_map,
            current_report=current_spans,
            donor_report=donor_spans,
            positions=positions,
            output=candidate,
        )
        raw_proof["operations"] = {
            "replace": 0,
            "convert": len(positions),
            "insert": 0,
            "delete": 0,
        }

        output_spans = scan_tile_spans(
            map_path=candidate,
            scanner=scanner,
            workspace=workspace,
            role="output",
            timeout_seconds=timeout_seconds,
        )
        _validate_header_compatibility(current_spans, output_spans)

        donor_selected = _selected_spans(donor_spans, positions, "donor")
        output_selected = _selected_spans(output_spans, positions, "output")
        for position in positions:
            donor_span = donor_selected[position]
            output_span = output_selected[position]
            if (
                donor_span["sha256"] != output_span["sha256"]
                or donor_span["nodeType"] != output_span["nodeType"]
                or donor_span["areaBaseX"] != output_span["areaBaseX"]
                or donor_span["areaBaseY"] != output_span["areaBaseY"]
                or donor_span["areaZ"] != output_span["areaZ"]
            ):
                raise TileTypeConversionMaterializerError(
                    f"output raw tile subtree differs from donor at {position}"
                )

        output_index = evidence_workspace / "output.widx"
        output_manifest = evidence_workspace / "output.widx.json"
        build_world_index(
            map_path=candidate,
            scanner=scanner,
            output=output_index,
            manifest_output=output_manifest,
            timeout_seconds=timeout_seconds,
        )
        selected_world_index = _verify_selected_world_index(
            donor_index_path=donor_index,
            output_index_path=output_index,
            positions=positions,
        )

        lower = tuple(min(position[index] for position in positions) for index in range(3))
        upper = tuple(max(position[index] for position in positions) for index in range(3))
        semantic_diff = analyze_index_paths(
            artifact_root=root,
            before_index_path=Path(_relative(root, current_index)),
            before_manifest_path=Path(_relative(root, current_manifest)),
            after_index_path=Path(_relative(root, output_index)),
            after_manifest_path=Path(_relative(root, output_manifest)),
            lower=lower,  # type: ignore[arg-type]
            upper=upper,  # type: ignore[arg-type]
            sample_limit=10_000,
        )
        semantic_path = evidence_workspace / "semantic-diff.json"
        _write_json(semantic_path, semantic_diff)

        current_spans_path = evidence_workspace / "current-tile-spans.json"
        donor_spans_path = evidence_workspace / "donor-tile-spans.json"
        output_spans_path = evidence_workspace / "output-tile-spans.json"
        _write_json(current_spans_path, current_spans)
        _write_json(donor_spans_path, donor_spans)
        _write_json(output_spans_path, output_spans)

        _assert_pin(current_map, current_pin, "current map")
        _assert_pin(donor_map, donor_pin, "donor map")
        _assert_pin(scanner, scanner_pin, "extended native scanner")

        result = {
            "format": RESULT_FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "ok": True,
            "structuralVerificationComplete": True,
            "source": {
                "current": {
                    "path": current_map.name,
                    "size": current_pin[0],
                    "sha256": current_pin[2],
                },
                "donor": {
                    "path": donor_map.name,
                    "size": donor_pin[0],
                    "sha256": donor_pin[2],
                },
                "output": {
                    "path": _relative(root, output),
                    "size": candidate.stat().st_size,
                    "sha256": sha256_path(candidate),
                },
                "scanner": {
                    "path": scanner.name,
                    "size": scanner_pin[0],
                    "sha256": scanner_pin[2],
                },
            },
            "approval": {
                "path": _relative(root, approval_source),
                "sha256": sha256_path(approval_source),
                "format": APPROVAL_FORMAT,
                "decision": approval["decision"],
            },
            "selection": {
                "positions": [list(position) for position in positions],
                "count": len(positions),
                "translation": [0, 0, 0],
                "operation": "convert-existing-same-coordinate-tile-type",
                "conversions": conversions,
            },
            "rawConfinement": raw_proof,
            "selectedWorldIndex": selected_world_index,
            "verification": {
                "nativeReparse": True,
                "worldIndexRebuilt": True,
                "selectedTilesEqualDonor": True,
                "nonSelectedCurrentBytesExact": True,
                "semanticDiff": {
                    "path": "semantic-diff.json",
                    "sha256": sha256_path(semantic_path),
                    "format": semantic_diff.get("format"),
                    "summary": semantic_diff.get("summary"),
                },
            },
            "rollback": {
                "sourceMapsModified": False,
                "action": (
                    f"Delete generated output copy {_relative(root, output)} to roll back this "
                    "materialization artifact."
                ),
            },
            "safety": {
                "sourceInPlaceWrite": False,
                "fullMapSerializer": False,
                "phase8Expanded": False,
                "translatedImport": False,
                "tileInsertion": False,
                "tileDeletion": False,
                "tileTypeConversion": True,
                "itemStackEditing": False,
                "arbitraryNodeSerialization": False,
                "rawCompleteTileSubtreesOnly": True,
                "sameCoordinateOnly": True,
                "sameParentTileAreaOnly": True,
                "sameNodeTypeOnly": False,
                "separateApprovalRequired": True,
                "gameplayCorrectnessProven": False,
                "physicalClientE2EProven": False,
            },
        }
        result_path = evidence_workspace / "materialization-result.json"
        _write_json(result_path, result)

        output.parent.mkdir(parents=True, exist_ok=True)
        _check_ancestors(root, output, "output map")
        os.link(candidate, output)
        published_output = True
        candidate.unlink()
        evidence_output.parent.mkdir(parents=True, exist_ok=True)
        _check_ancestors(root, evidence_output, "evidence directory")
        _publish_directory_no_overwrite(evidence_workspace, evidence_output)
        return result
    except Exception:
        if published_output:
            output.unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
