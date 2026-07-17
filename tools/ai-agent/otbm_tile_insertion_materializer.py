from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from otbm_area_materializer import (
    _area_index,
    _assert_pin,
    _check_ancestors,
    _confined_existing,
    _copy_exact,
    _hash_ranges_excluding,
    _hash_span,
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
    _verify_selected_world_index,
    scan_tile_spans,
)
from otbm_world_index import WorldIndex, build_world_index

APPROVAL_FORMAT = "canary-otbm-tile-insertion-approval-v1"
RESULT_FORMAT = "canary-otbm-tile-insertion-result-v1"
SCHEMA_VERSION = 1
NODE_END = 0xFF


class TileInsertionMaterializerError(TileMaterializerError):
    pass


def _validate_approval(
    *,
    approval: Mapping[str, Any],
    current_tiles: Mapping[str, Any],
    donor_tiles: Mapping[str, Any],
    current_areas: Mapping[str, Any],
    current_index_path: Path,
    donor_index_path: Path,
) -> list[Position]:
    if approval.get("format") != APPROVAL_FORMAT or approval.get("schemaVersion") != SCHEMA_VERSION:
        raise TileInsertionMaterializerError(f"approval must use {APPROVAL_FORMAT} schemaVersion 1")
    if approval.get("decision") != "approved" or not str(approval.get("rationale", "")).strip():
        raise TileInsertionMaterializerError("approval requires decision 'approved' and a non-empty rationale")
    selections = approval.get("selections")
    if not isinstance(selections, list) or not selections or len(selections) > MAX_SELECTIONS:
        raise TileInsertionMaterializerError(f"approval selections must contain 1..{MAX_SELECTIONS} entries")

    current_by_position = _span_index(current_tiles)
    donor_by_position = _span_index(donor_tiles)
    current_by_area = _area_index(current_areas)
    positions: list[Position] = []
    seen: set[Position] = set()
    with WorldIndex(current_index_path) as current_index, WorldIndex(donor_index_path) as donor_index:
        for index, raw in enumerate(selections):
            if not isinstance(raw, dict):
                raise TileInsertionMaterializerError(f"approval selections[{index}] must be an object")
            position = _position(raw.get("position"), f"approval selections[{index}].position")
            if position in seen:
                raise TileInsertionMaterializerError(f"approval contains duplicate selected position {position}")
            seen.add(position)
            expected_area = (position[0] & 0xFF00, position[1] & 0xFF00, position[2])
            area = _area_key(raw.get("areaKey"), f"approval selections[{index}].areaKey")
            if area != expected_area:
                raise TileInsertionMaterializerError(f"selected position {position} has the wrong canonical TILE_AREA key")
            if current_by_position.get(position) or current_index.find_tile(position) is not None:
                raise TileInsertionMaterializerError(f"selected insertion position {position} already exists in current map")
            donor_matches = donor_by_position.get(position, [])
            if len(donor_matches) != 1:
                raise TileInsertionMaterializerError(f"selected position {position} must exist exactly once in donor map")
            donor_span = donor_matches[0]
            donor_area = (int(donor_span["areaBaseX"]), int(donor_span["areaBaseY"]), int(donor_span["areaZ"]))
            if donor_area != area:
                raise TileInsertionMaterializerError(f"donor tile {position} does not use the approved TILE_AREA parent")
            area_matches = current_by_area.get(area, [])
            if len(area_matches) != 1:
                raise TileInsertionMaterializerError(f"target current TILE_AREA {area} must exist exactly once")
            area_span = area_matches[0]
            current_area = raw.get("currentArea")
            donor = raw.get("donor")
            if not isinstance(current_area, dict) or not isinstance(donor, dict):
                raise TileInsertionMaterializerError(f"approval selection {position} lacks currentArea/donor expected state")
            if current_area.get("rawSha256") != area_span.get("sha256"):
                raise TileInsertionMaterializerError(f"current TILE_AREA {area} raw SHA-256 does not match approval")
            if current_area.get("rawByteLength") != area_span.get("byteLength"):
                raise TileInsertionMaterializerError(f"current TILE_AREA {area} raw byte length does not match approval")
            donor_canonical, _ = _canonical_tile(donor_index, position)
            _selection_side_matches(
                side=donor,
                span=donor_span,
                canonical_sha256=donor_canonical,
                label=f"donor tile {position}",
            )
            positions.append(position)
    return positions


def _materialize(
    *,
    current_map: Path,
    donor_map: Path,
    current_areas: Mapping[str, Any],
    donor_tiles: Mapping[str, Any],
    positions: Sequence[Position],
    output: Path,
) -> dict[str, Any]:
    area_spans = _area_index(current_areas)
    donor_spans = _selected_spans(donor_tiles, positions, "donor")
    grouped: dict[tuple[int, int, int], list[Position]] = {}
    for position in positions:
        grouped.setdefault((position[0] & 0xFF00, position[1] & 0xFF00, position[2]), []).append(position)

    operations: list[tuple[int, list[Position]]] = []
    for area, selected in grouped.items():
        matches = area_spans.get(area, [])
        if len(matches) != 1:
            raise TileInsertionMaterializerError(f"target current TILE_AREA {area} must exist exactly once")
        insertion = int(matches[0]["endOffsetExclusive"]) - 1
        with current_map.open("rb") as stream:
            stream.seek(insertion)
            if stream.read(1) != bytes((NODE_END,)):
                raise TileInsertionMaterializerError(f"TILE_AREA {area} scanner boundary is not a NODE_END byte")
        operations.append((insertion, sorted(selected, key=lambda value: (value[2], value[1], value[0]))))
    operations.sort(key=lambda value: value[0])

    cursor = 0
    output_cursor = 0
    inserted: dict[Position, tuple[int, int]] = {}
    with current_map.open("rb") as current, donor_map.open("rb") as donor, output.open("xb") as out:
        for insertion, selected in operations:
            if insertion < cursor:
                raise TileInsertionMaterializerError("TILE_AREA insertion boundaries overlap or are unsorted")
            _copy_exact(current, out, cursor, insertion)
            output_cursor += insertion - cursor
            for position in selected:
                span = donor_spans[position]
                start = int(span["startOffset"])
                end = int(span["endOffsetExclusive"])
                output_start = output_cursor
                _copy_exact(donor, out, start, end)
                output_cursor += end - start
                inserted[position] = (output_start, output_cursor)
            cursor = insertion
        _copy_exact(current, out, cursor, current_map.stat().st_size)
        out.flush()
        os.fsync(out.fileno())

    retained_hash, retained_count = _hash_ranges_excluding(output, list(inserted.values()))
    if retained_count != current_map.stat().st_size or retained_hash != sha256_path(current_map):
        raise TileInsertionMaterializerError("output excluding inserted spans is not byte-identical to current map")
    for position, span in inserted.items():
        if _hash_span(output, *span) != donor_spans[position]["sha256"]:
            raise TileInsertionMaterializerError(f"inserted raw tile bytes differ from donor at {position}")
    return {
        "operations": {"replace": 0, "insert": len(positions), "delete": 0},
        "insertionPolicy": "before-existing-parent-tile-area-node-end",
        "outputInsertedSpans": {
            f"{position[0]},{position[1]},{position[2]}": list(span) for position, span in inserted.items()
        },
        "retainedBytes": {
            "currentCount": current_map.stat().st_size,
            "outputExcludingInsertedCount": retained_count,
            "sha256": retained_hash,
            "exactlyPreserved": True,
        },
    }


def materialize_tile_insertions(
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
    approval_source = _confined_existing(root, approval_path, "tile insertion approval")
    current_index = _confined_existing(root, current_index_path, "current World Index")
    current_manifest = _confined_existing(root, current_manifest_path, "current World Index manifest")
    donor_index = _confined_existing(root, donor_index_path, "donor World Index")
    donor_manifest = _confined_existing(root, donor_manifest_path, "donor World Index manifest")
    output = _new_confined_path(root, output_map_path, "output map")
    evidence_output = _new_confined_path(root, evidence_dir, "evidence directory", directory=True)
    if output in (current_map, donor_map):
        raise TileInsertionMaterializerError("output map must be distinct from current and donor maps")

    current_pin = _stat_pin(current_map)
    donor_pin = _stat_pin(donor_map)
    scanner_pin = _stat_pin(scanner)
    approval = _load_json(approval_source, "tile insertion approval")
    provenance = approval.get("provenance")
    if not isinstance(provenance, dict):
        raise TileInsertionMaterializerError("approval has no provenance object")
    for role, map_path, index_path, manifest_path in (
        ("current", current_map, current_index, current_manifest),
        ("donor", donor_map, donor_index, donor_manifest),
    ):
        role_provenance = provenance.get(role)
        if not isinstance(role_provenance, dict):
            raise TileInsertionMaterializerError(f"approval {role} provenance is incomplete")
        _validate_manifest_bundle(
            role=role,
            map_path=map_path,
            index_path=index_path,
            manifest_path=manifest_path,
            provenance=role_provenance,
        )

    workspace = Path(tempfile.mkdtemp(prefix=".otbm-tile-insertion-", dir=root))
    evidence_workspace = workspace / "evidence"
    evidence_workspace.mkdir()
    candidate = workspace / "candidate.otbm"
    published = False
    try:
        current_tiles = scan_tile_spans(map_path=current_map, scanner=scanner, workspace=workspace, role="current")
        donor_tiles = scan_tile_spans(map_path=donor_map, scanner=scanner, workspace=workspace, role="donor")
        current_areas = scan_tile_area_spans(map_path=current_map, scanner=scanner, workspace=workspace, role="current")
        _validate_header_compatibility(current_tiles, donor_tiles)
        positions = _validate_approval(
            approval=approval,
            current_tiles=current_tiles,
            donor_tiles=donor_tiles,
            current_areas=current_areas,
            current_index_path=current_index,
            donor_index_path=donor_index,
        )
        raw_proof = _materialize(
            current_map=current_map,
            donor_map=donor_map,
            current_areas=current_areas,
            donor_tiles=donor_tiles,
            positions=positions,
            output=candidate,
        )
        output_tiles = scan_tile_spans(map_path=candidate, scanner=scanner, workspace=workspace, role="output")
        output_areas = scan_tile_area_spans(map_path=candidate, scanner=scanner, workspace=workspace, role="output")
        _validate_header_compatibility(current_tiles, output_tiles)
        donor_selected = _selected_spans(donor_tiles, positions, "donor")
        output_selected = _selected_spans(output_tiles, positions, "output")
        for position in positions:
            donor_span = donor_selected[position]
            output_span = output_selected[position]
            if any(
                donor_span[key] != output_span[key]
                for key in ("sha256", "nodeType", "areaBaseX", "areaBaseY", "areaZ")
            ):
                raise TileInsertionMaterializerError(f"inserted output raw tile differs from donor at {position}")

        output_index = evidence_workspace / "output.widx"
        output_manifest = evidence_workspace / "output.widx.json"
        build_world_index(
            map_path=candidate,
            scanner=scanner,
            output=output_index,
            manifest_output=output_manifest,
            timeout_seconds=timeout_seconds,
        )
        inserted_world_index = _verify_selected_world_index(
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
        for name, document in (
            ("current-tile-spans.json", current_tiles),
            ("donor-tile-spans.json", donor_tiles),
            ("output-tile-spans.json", output_tiles),
            ("current-tile-area-spans.json", current_areas),
            ("output-tile-area-spans.json", output_areas),
        ):
            _write_json(evidence_workspace / name, document)

        _assert_pin(current_map, current_pin, "current map")
        _assert_pin(donor_map, donor_pin, "donor map")
        _assert_pin(scanner, scanner_pin, "extended native scanner")
        result = {
            "format": RESULT_FORMAT,
            "schemaVersion": 1,
            "ok": True,
            "structuralVerificationComplete": True,
            "source": {
                "current": {"path": current_map.name, "size": current_pin[0], "sha256": current_pin[2]},
                "donor": {"path": donor_map.name, "size": donor_pin[0], "sha256": donor_pin[2]},
                "output": {"path": _relative(root, output), "size": candidate.stat().st_size, "sha256": sha256_path(candidate)},
                "scanner": {"path": scanner.name, "size": scanner_pin[0], "sha256": scanner_pin[2]},
            },
            "approval": {"path": _relative(root, approval_source), "sha256": sha256_path(approval_source), "format": APPROVAL_FORMAT},
            "selection": {
                "positions": [list(position) for position in positions],
                "count": len(positions),
                "translation": [0, 0, 0],
                "operation": "insert-missing-same-coordinate-tile",
            },
            "rawConfinement": raw_proof,
            "insertedWorldIndex": inserted_world_index,
            "verification": {
                "nativeReparse": True,
                "worldIndexRebuilt": True,
                "insertedTilesEqualDonor": True,
                "completeCurrentByteSequenceExact": True,
                "semanticDiff": {
                    "path": "semantic-diff.json",
                    "sha256": sha256_path(semantic_path),
                    "format": semantic_diff.get("format"),
                    "summary": semantic_diff.get("summary"),
                },
            },
            "rollback": {"sourceMapsModified": False, "action": f"Delete generated output copy {_relative(root, output)}."},
            "safety": {
                "sourceInPlaceWrite": False,
                "fullMapSerializer": False,
                "translatedImport": False,
                "tileInsertion": True,
                "tileDeletion": False,
                "tileAreaCreation": False,
                "itemStackEditing": False,
                "arbitraryNodeSerialization": False,
                "rawCompleteTileSubtreesOnly": True,
                "sameCoordinateOnly": True,
                "existingParentTileAreaOnly": True,
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
