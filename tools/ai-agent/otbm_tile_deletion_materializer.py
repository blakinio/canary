from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from otbm_area_materializer import (
    _assert_pin,
    _check_ancestors,
    _confined_existing,
    _copy_exact,
    _hash_ranges_excluding,
    _load_json,
    _new_confined_path,
    _prepare_artifact_root,
    _publish_directory_no_overwrite,
    _relative,
    _resolve_existing_regular,
    _stat_pin,
    _validate_header_compatibility,
    _write_json,
    scan_tile_area_spans,
)
from otbm_semantic_diff import analyze_index_paths
from otbm_semantic_diff_types import sha256_path
from otbm_tile_materializer import (
    MAX_SELECTIONS,
    Position,
    TileMaterializerError,
    _area_key,
    _canonical_tile,
    _position,
    _selected_spans,
    _selection_side_matches,
    _span_index,
    _validate_manifest_bundle,
    scan_tile_spans,
)
from otbm_world_index import WorldIndex, build_world_index

APPROVAL_FORMAT = "canary-otbm-tile-deletion-approval-v1"
RESULT_FORMAT = "canary-otbm-tile-deletion-result-v1"
SCHEMA_VERSION = 1


class TileDeletionMaterializerError(TileMaterializerError):
    pass


def _validate_approval(
    *,
    approval: Mapping[str, Any],
    current_tiles: Mapping[str, Any],
    current_index_path: Path,
) -> list[Position]:
    if approval.get("format") != APPROVAL_FORMAT or approval.get("schemaVersion") != SCHEMA_VERSION:
        raise TileDeletionMaterializerError(f"approval must use {APPROVAL_FORMAT} schemaVersion 1")
    if approval.get("decision") != "approved" or not str(approval.get("rationale", "")).strip():
        raise TileDeletionMaterializerError("approval requires decision 'approved' and a non-empty rationale")
    selections = approval.get("selections")
    if not isinstance(selections, list) or not selections or len(selections) > MAX_SELECTIONS:
        raise TileDeletionMaterializerError(f"approval selections must contain 1..{MAX_SELECTIONS} entries")

    current_by_position = _span_index(current_tiles)
    positions: list[Position] = []
    seen: set[Position] = set()
    with WorldIndex(current_index_path) as current_index:
        for index, raw in enumerate(selections):
            if not isinstance(raw, dict):
                raise TileDeletionMaterializerError(f"approval selections[{index}] must be an object")
            position = _position(raw.get("position"), f"approval selections[{index}].position")
            if position in seen:
                raise TileDeletionMaterializerError(f"approval contains duplicate selected position {position}")
            seen.add(position)
            expected_area = (position[0] & 0xFF00, position[1] & 0xFF00, position[2])
            area = _area_key(raw.get("areaKey"), f"approval selections[{index}].areaKey")
            if area != expected_area:
                raise TileDeletionMaterializerError(f"selected position {position} has the wrong canonical TILE_AREA key")
            matches = current_by_position.get(position, [])
            if len(matches) != 1:
                raise TileDeletionMaterializerError(f"selected deletion position {position} must exist exactly once in current map")
            span = matches[0]
            span_area = (int(span["areaBaseX"]), int(span["areaBaseY"]), int(span["areaZ"]))
            if span_area != area:
                raise TileDeletionMaterializerError(f"current tile {position} does not use the approved TILE_AREA parent")
            current_side = raw.get("current")
            if not isinstance(current_side, dict):
                raise TileDeletionMaterializerError(f"approval selection {position} lacks current expected state")
            canonical_sha256, _ = _canonical_tile(current_index, position)
            _selection_side_matches(
                side=current_side,
                span=span,
                canonical_sha256=canonical_sha256,
                label=f"current tile {position}",
            )
            positions.append(position)
    return positions


def _materialize(
    *,
    current_map: Path,
    current_tiles: Mapping[str, Any],
    positions: Sequence[Position],
    output: Path,
) -> dict[str, Any]:
    selected = _selected_spans(current_tiles, positions, "current")
    ordered: list[tuple[int, int, Position]] = []
    for position, span in selected.items():
        ordered.append((int(span["startOffset"]), int(span["endOffsetExclusive"]), position))
    ordered.sort(key=lambda value: value[0])
    previous_end = -1
    for start, end, position in ordered:
        if start < previous_end or end <= start:
            raise TileDeletionMaterializerError(f"selected deletion tile spans overlap or are invalid near {position}")
        previous_end = end

    excluded = [(start, end) for start, end, _position_value in ordered]
    retained_hash, retained_count = _hash_ranges_excluding(current_map, excluded)
    cursor = 0
    with current_map.open("rb") as current, output.open("xb") as out:
        for start, end, _position_value in ordered:
            _copy_exact(current, out, cursor, start)
            cursor = end
        _copy_exact(current, out, cursor, current_map.stat().st_size)
        out.flush()
        os.fsync(out.fileno())

    if output.stat().st_size != retained_count or sha256_path(output) != retained_hash:
        raise TileDeletionMaterializerError(
            "output is not byte-for-byte equal to current map with exactly selected tile spans removed"
        )
    return {
        "operations": {"replace": 0, "insert": 0, "delete": len(positions)},
        "deletedRawSpans": {
            f"{position[0]},{position[1]},{position[2]}": [start, end]
            for start, end, position in ordered
        },
        "retainedBytes": {
            "currentCount": current_map.stat().st_size,
            "deletedCount": current_map.stat().st_size - retained_count,
            "outputCount": retained_count,
            "sha256": retained_hash,
            "exactlyPreserved": True,
        },
    }


def _verify_deleted_world_index(
    *,
    current_index_path: Path,
    output_index_path: Path,
    positions: Sequence[Position],
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    with WorldIndex(current_index_path) as current_index, WorldIndex(output_index_path) as output_index:
        for position in sorted(positions, key=lambda value: (value[2], value[1], value[0])):
            current_hash, _ = _canonical_tile(current_index, position)
            if output_index.find_tile(position) is not None:
                raise TileDeletionMaterializerError(f"output World Index still contains deleted tile {position}")
            evidence.append(
                {
                    "position": list(position),
                    "deletedCanonicalSha256": current_hash,
                    "absentFromOutput": True,
                }
            )
    return evidence


def materialize_tile_deletions(
    *,
    artifact_root: Path,
    current_map_path: Path,
    scanner_path: Path,
    approval_path: Path,
    current_index_path: Path,
    current_manifest_path: Path,
    output_map_path: Path,
    evidence_dir: Path,
    timeout_seconds: int = 3600,
) -> dict[str, Any]:
    root = _prepare_artifact_root(artifact_root)
    current_map = _resolve_existing_regular(current_map_path, "current map")
    scanner = _resolve_existing_regular(scanner_path, "extended native scanner", executable=True)
    approval_source = _confined_existing(root, approval_path, "tile deletion approval")
    current_index = _confined_existing(root, current_index_path, "current World Index")
    current_manifest = _confined_existing(root, current_manifest_path, "current World Index manifest")
    output = _new_confined_path(root, output_map_path, "output map")
    evidence_output = _new_confined_path(root, evidence_dir, "evidence directory", directory=True)
    if output == current_map:
        raise TileDeletionMaterializerError("output map must be distinct from current map")

    current_pin = _stat_pin(current_map)
    scanner_pin = _stat_pin(scanner)
    approval = _load_json(approval_source, "tile deletion approval")
    provenance = approval.get("provenance")
    if not isinstance(provenance, dict) or not isinstance(provenance.get("current"), dict):
        raise TileDeletionMaterializerError("approval current provenance is incomplete")
    _validate_manifest_bundle(
        role="current",
        map_path=current_map,
        index_path=current_index,
        manifest_path=current_manifest,
        provenance=provenance["current"],
    )

    workspace = Path(tempfile.mkdtemp(prefix=".otbm-tile-deletion-", dir=root))
    evidence_workspace = workspace / "evidence"
    evidence_workspace.mkdir()
    candidate = workspace / "candidate.otbm"
    published = False
    try:
        current_tiles = scan_tile_spans(
            map_path=current_map,
            scanner=scanner,
            workspace=workspace,
            role="current",
            timeout_seconds=timeout_seconds,
        )
        current_areas = scan_tile_area_spans(
            map_path=current_map,
            scanner=scanner,
            workspace=workspace,
            role="current",
            timeout_seconds=timeout_seconds,
        )
        positions = _validate_approval(
            approval=approval,
            current_tiles=current_tiles,
            current_index_path=current_index,
        )
        raw_proof = _materialize(
            current_map=current_map,
            current_tiles=current_tiles,
            positions=positions,
            output=candidate,
        )

        output_tiles = scan_tile_spans(
            map_path=candidate,
            scanner=scanner,
            workspace=workspace,
            role="output",
            timeout_seconds=timeout_seconds,
        )
        output_areas = scan_tile_area_spans(
            map_path=candidate,
            scanner=scanner,
            workspace=workspace,
            role="output",
            timeout_seconds=timeout_seconds,
        )
        _validate_header_compatibility(current_tiles, output_tiles)
        output_by_position = _span_index(output_tiles)
        for position in positions:
            if output_by_position.get(position):
                raise TileDeletionMaterializerError(f"output raw scan still contains deleted tile {position}")

        output_index = evidence_workspace / "output.widx"
        output_manifest = evidence_workspace / "output.widx.json"
        build_world_index(
            map_path=candidate,
            scanner=scanner,
            output=output_index,
            manifest_output=output_manifest,
            timeout_seconds=timeout_seconds,
        )
        deleted_world_index = _verify_deleted_world_index(
            current_index_path=current_index,
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
        for name, document in (
            ("current-tile-spans.json", current_tiles),
            ("output-tile-spans.json", output_tiles),
            ("current-tile-area-spans.json", current_areas),
            ("output-tile-area-spans.json", output_areas),
        ):
            _write_json(evidence_workspace / name, document)

        _assert_pin(current_map, current_pin, "current map")
        _assert_pin(scanner, scanner_pin, "extended native scanner")
        result = {
            "format": RESULT_FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "ok": True,
            "structuralVerificationComplete": True,
            "source": {
                "current": {"path": current_map.name, "size": current_pin[0], "sha256": current_pin[2]},
                "output": {"path": _relative(root, output), "size": candidate.stat().st_size, "sha256": sha256_path(candidate)},
                "scanner": {"path": scanner.name, "size": scanner_pin[0], "sha256": scanner_pin[2]},
            },
            "approval": {
                "path": _relative(root, approval_source),
                "sha256": sha256_path(approval_source),
                "format": APPROVAL_FORMAT,
            },
            "selection": {
                "positions": [list(position) for position in positions],
                "count": len(positions),
                "translation": [0, 0, 0],
                "operation": "delete-existing-same-coordinate-tile",
            },
            "rawConfinement": raw_proof,
            "deletedWorldIndex": deleted_world_index,
            "verification": {
                "nativeReparse": True,
                "worldIndexRebuilt": True,
                "deletedTilesAbsent": True,
                "retainedCurrentByteSequenceExact": True,
                "parentTileAreasPreserved": True,
                "semanticDiff": {
                    "path": "semantic-diff.json",
                    "sha256": sha256_path(semantic_path),
                    "format": semantic_diff.get("format"),
                    "summary": semantic_diff.get("summary"),
                },
            },
            "rollback": {
                "sourceMapModified": False,
                "action": f"Delete generated output copy {_relative(root, output)}.",
            },
            "safety": {
                "sourceInPlaceWrite": False,
                "fullMapSerializer": False,
                "translatedImport": False,
                "tileInsertion": False,
                "tileReplacement": False,
                "tileDeletion": True,
                "tileAreaDeletion": False,
                "itemStackEditing": False,
                "arbitraryNodeSerialization": False,
                "rawCompleteTileSubtreesOnly": True,
                "sameCoordinateOnly": True,
                "parentTileAreaPreserved": True,
                "separateApprovalRequired": True,
                "gameplayCorrectnessProven": False,
                "physicalClientE2EProven": False,
            },
        }
        _write_json(evidence_workspace / "materialization-result.json", result)
        output.parent.mkdir(parents=True, exist_ok=True)
        _check_ancestors(root, output, "output map")
        os.link(candidate, output)
        published = True
        candidate.unlink()
        evidence_output.parent.mkdir(parents=True, exist_ok=True)
        _check_ancestors(root, evidence_output, "evidence directory")
        _publish_directory_no_overwrite(evidence_workspace, evidence_output)
        return result
    except Exception:
        if published:
            output.unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
