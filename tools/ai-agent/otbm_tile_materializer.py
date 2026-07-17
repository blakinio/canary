from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from otbm_area_materializer import (
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
)
from otbm_semantic_diff import analyze_index_paths
from otbm_semantic_diff_types import canonical_json, sha256_path
from otbm_world_index import WORLD_INDEX_FORMAT, WorldIndex, build_world_index

NATIVE_TILE_SPAN_FORMAT = "canary-otbm-native-tile-spans-v1"
TILE_SPAN_FORMAT = "canary-otbm-tile-spans-v1"
APPROVAL_FORMAT = "canary-otbm-tile-materialization-approval-v1"
RESULT_FORMAT = "canary-otbm-tile-materialization-result-v1"
SCHEMA_VERSION = 1
MAX_REPORT_BYTES = 128 * 1024 * 1024
MAX_SELECTIONS = 4096
NODE_TYPES = {5: "tile", 14: "house"}

Position = tuple[int, int, int]
AreaKey = tuple[int, int, int]


class TileMaterializerError(RuntimeError):
    pass


def _pin_matches(path: Path, pin: Mapping[str, Any], label: str) -> None:
    if pin.get("size") != path.stat().st_size or pin.get("sha256") != sha256_path(path):
        raise TileMaterializerError(f"{label} does not match approval provenance pin")


def _position(value: Any, label: str) -> Position:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or any(isinstance(part, bool) or not isinstance(part, int) for part in value)
    ):
        raise TileMaterializerError(f"{label} must contain integer x,y,z")
    x, y, z = (int(part) for part in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise TileMaterializerError(f"{label} is outside the OTBM coordinate range")
    return x, y, z


def _area_key(value: Any, label: str) -> AreaKey:
    base_x, base_y, z = _position(value, label)
    if base_x % 256 != 0 or base_y % 256 != 0:
        raise TileMaterializerError(f"{label} must use 256-aligned x/y TILE_AREA coordinates")
    return base_x, base_y, z


def _run_tile_span_scan(
    *, map_path: Path, scanner: Path, output: Path, timeout_seconds: int
) -> dict[str, Any]:
    if timeout_seconds <= 0:
        raise TileMaterializerError("timeout_seconds must be positive")
    pin = _stat_pin(map_path)
    try:
        completed = subprocess.run(
            [str(scanner), "--tile-spans", str(map_path), str(output)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise TileMaterializerError(f"tile span scanner timed out after {timeout_seconds} seconds") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise TileMaterializerError(f"tile span scanner failed: {detail}")
    _assert_pin(map_path, pin, "map")
    document = _load_json(output, "native tile span report", maximum=MAX_REPORT_BYTES)
    if document.get("format") != NATIVE_TILE_SPAN_FORMAT:
        raise TileMaterializerError(f"unsupported native tile span format: {document.get('format')!r}")
    return document


def _normalize_tile_span_report(
    *, map_path: Path, scanner: Path, native: Mapping[str, Any]
) -> dict[str, Any]:
    source = native.get("source")
    raw_tiles = native.get("tiles")
    if not isinstance(source, dict) or not isinstance(raw_tiles, list):
        raise TileMaterializerError("native tile span report is incomplete")
    size = map_path.stat().st_size
    if source.get("path") != map_path.name or source.get("size") != size:
        raise TileMaterializerError("native tile span source identity mismatch")
    if source.get("unknownAttributeTails") != 0:
        raise TileMaterializerError("map contains unknown attribute tails; raw tile materialization is unsafe")

    tiles: list[dict[str, Any]] = []
    previous_end = -1
    for index, raw in enumerate(raw_tiles):
        if not isinstance(raw, dict):
            raise TileMaterializerError(f"native tile span {index} must be an object")
        names = (
            "areaBaseX",
            "areaBaseY",
            "areaZ",
            "x",
            "y",
            "z",
            "nodeType",
            "startOffset",
            "endOffsetExclusive",
        )
        values = [raw.get(name) for name in names]
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise TileMaterializerError(f"native tile span {index} contains invalid integers")
        base_x, base_y, area_z, x, y, z, node_type, start, end = (int(value) for value in values)
        if not (
            0 <= base_x <= 0xFFFF
            and 0 <= base_y <= 0xFFFF
            and 0 <= area_z <= 15
            and 0 <= x <= 0xFFFF
            and 0 <= y <= 0xFFFF
            and 0 <= z <= 15
        ):
            raise TileMaterializerError(f"native tile span {index} has invalid coordinates")
        if base_x % 256 != 0 or base_y % 256 != 0 or (base_x, base_y, area_z) != (x & 0xFF00, y & 0xFF00, z):
            raise TileMaterializerError(f"native tile span {index} has a non-canonical TILE_AREA parent key")
        if node_type not in NODE_TYPES:
            raise TileMaterializerError(f"native tile span {index} has unsupported node type {node_type}")
        if not 0 <= start < end <= size:
            raise TileMaterializerError(f"native tile span {index} has invalid physical offsets")
        if start < previous_end:
            raise TileMaterializerError("native tile physical spans overlap or are unsorted")
        previous_end = end
        tiles.append(
            {
                "areaBaseX": base_x,
                "areaBaseY": base_y,
                "areaZ": area_z,
                "x": x,
                "y": y,
                "z": z,
                "nodeType": node_type,
                "kind": NODE_TYPES[node_type],
                "startOffset": start,
                "endOffsetExclusive": end,
                "byteLength": end - start,
                "sha256": _hash_span(map_path, start, end),
            }
        )

    return {
        "format": TILE_SPAN_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "source": {
            "path": map_path.name,
            "size": size,
            "sha256": sha256_path(map_path),
            "otbmVersion": source.get("otbmVersion"),
            "width": source.get("width"),
            "height": source.get("height"),
            "itemsMajor": source.get("itemsMajor"),
            "itemsMinor": source.get("itemsMinor"),
            "unknownAttributeTails": source.get("unknownAttributeTails"),
        },
        "scanner": {"path": scanner.name, "sha256": sha256_path(scanner), "nativeFormat": NATIVE_TILE_SPAN_FORMAT},
        "tiles": tiles,
    }


def scan_tile_spans(
    *, map_path: Path, scanner: Path, workspace: Path, role: str, timeout_seconds: int = 3600
) -> dict[str, Any]:
    native_output = workspace / f"{role}-native-tile-spans.json"
    native = _run_tile_span_scan(
        map_path=map_path,
        scanner=scanner,
        output=native_output,
        timeout_seconds=timeout_seconds,
    )
    return _normalize_tile_span_report(map_path=map_path, scanner=scanner, native=native)


def _span_index(report: Mapping[str, Any]) -> dict[Position, list[dict[str, Any]]]:
    result: dict[Position, list[dict[str, Any]]] = {}
    raw_tiles = report.get("tiles")
    if not isinstance(raw_tiles, list):
        raise TileMaterializerError("tile span report contains no tiles array")
    for entry in raw_tiles:
        if not isinstance(entry, dict):
            raise TileMaterializerError("tile span report contains a non-object tile")
        key = int(entry["x"]), int(entry["y"]), int(entry["z"])
        result.setdefault(key, []).append(entry)
    return result


def _canonical_tile(index: WorldIndex, position: Position) -> tuple[str, dict[str, Any]]:
    found = index.find_tile(position)
    if found is None:
        raise TileMaterializerError(f"World Index has no tile at selected position {position}")
    _, tile = found
    placements: list[dict[str, Any]] = []
    for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count):
        placement = index.placement(ordinal)
        placements.append(
            {
                key: placement.get(key)
                for key in (
                    "itemId",
                    "itemDepth",
                    "source",
                    "actionId",
                    "uniqueId",
                    "houseDoorId",
                    "teleportDestination",
                )
                if placement.get(key) is not None
            }
        )
    value = {
        "position": [tile.x, tile.y, tile.z],
        "kind": tile.kind,
        "houseId": tile.house_id,
        "flags": tile.flags,
        "placements": placements,
    }
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest(), value


def _validate_manifest_bundle(
    *, role: str, map_path: Path, index_path: Path, manifest_path: Path, provenance: Mapping[str, Any]
) -> None:
    source_pin = provenance.get("sourceMap")
    index_pin = provenance.get("worldIndex")
    manifest_pin = provenance.get("manifest")
    if not isinstance(source_pin, dict) or not isinstance(index_pin, dict) or not isinstance(manifest_pin, dict):
        raise TileMaterializerError(f"approval {role} provenance is incomplete")
    _pin_matches(map_path, source_pin, f"{role} map")
    _pin_matches(index_path, index_pin, f"{role} World Index")
    _pin_matches(manifest_path, manifest_pin, f"{role} World Index manifest")

    manifest = _load_json(manifest_path, f"{role} World Index manifest")
    if manifest.get("format") != WORLD_INDEX_FORMAT or manifest.get("schemaVersion") != 1 or manifest.get("ok") is not True:
        raise TileMaterializerError(f"{role} World Index manifest is not a complete green v1 manifest")
    source = manifest.get("source")
    index = manifest.get("index")
    if not isinstance(source, dict) or not isinstance(index, dict):
        raise TileMaterializerError(f"{role} World Index manifest provenance is incomplete")
    if source.get("size") != map_path.stat().st_size or source.get("sha256") != sha256_path(map_path):
        raise TileMaterializerError(f"{role} World Index manifest does not pin the supplied map")
    if index.get("size") != index_path.stat().st_size or index.get("sha256") != sha256_path(index_path):
        raise TileMaterializerError(f"{role} World Index manifest does not pin the supplied index")
    with WorldIndex(index_path) as world_index:
        if world_index.header.source_map_size != map_path.stat().st_size:
            raise TileMaterializerError(f"{role} World Index source-map size does not match the supplied map")
        if world_index.header.unknown_attribute_tails != 0:
            raise TileMaterializerError(f"{role} World Index contains unknown attribute tails")


def _selection_side_matches(
    *, side: Mapping[str, Any], span: Mapping[str, Any], canonical_sha256: str, label: str
) -> None:
    if side.get("rawSha256") != span.get("sha256"):
        raise TileMaterializerError(f"{label} raw tile SHA-256 does not match approval")
    if side.get("rawByteLength") != span.get("byteLength"):
        raise TileMaterializerError(f"{label} raw tile byte length does not match approval")
    if side.get("nodeType") != span.get("nodeType"):
        raise TileMaterializerError(f"{label} node type does not match approval")
    if side.get("canonicalSha256") != canonical_sha256:
        raise TileMaterializerError(f"{label} canonical World Index tile SHA-256 does not match approval")


def _validate_approval(
    *,
    approval: Mapping[str, Any],
    current_report: Mapping[str, Any],
    donor_report: Mapping[str, Any],
    current_index_path: Path,
    donor_index_path: Path,
) -> list[Position]:
    if approval.get("format") != APPROVAL_FORMAT or approval.get("schemaVersion") != SCHEMA_VERSION:
        raise TileMaterializerError(f"approval must use {APPROVAL_FORMAT} schemaVersion {SCHEMA_VERSION}")
    if approval.get("decision") != "approved":
        raise TileMaterializerError("approval decision must be 'approved'")
    if not str(approval.get("rationale", "")).strip():
        raise TileMaterializerError("approval requires a non-empty rationale")
    raw_selections = approval.get("selections")
    if not isinstance(raw_selections, list) or not raw_selections:
        raise TileMaterializerError("approval selections must be a non-empty array")
    if len(raw_selections) > MAX_SELECTIONS:
        raise TileMaterializerError(f"approval exceeds the bounded selection limit of {MAX_SELECTIONS}")

    current_spans = _span_index(current_report)
    donor_spans = _span_index(donor_report)
    positions: list[Position] = []
    seen: set[Position] = set()
    with WorldIndex(current_index_path) as current_index, WorldIndex(donor_index_path) as donor_index:
        for selection_index, raw in enumerate(raw_selections):
            if not isinstance(raw, dict):
                raise TileMaterializerError(f"approval selections[{selection_index}] must be an object")
            position = _position(raw.get("position"), f"approval selections[{selection_index}].position")
            if position in seen:
                raise TileMaterializerError(f"approval contains duplicate selected position {position}")
            seen.add(position)
            expected_area = (position[0] & 0xFF00, position[1] & 0xFF00, position[2])
            approved_area = _area_key(raw.get("areaKey"), f"approval selections[{selection_index}].areaKey")
            if approved_area != expected_area:
                raise TileMaterializerError(f"approval selected position {position} does not match its canonical TILE_AREA key")

            current_matches = current_spans.get(position, [])
            donor_matches = donor_spans.get(position, [])
            if len(current_matches) != 1 or len(donor_matches) != 1:
                raise TileMaterializerError(
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
                raise TileMaterializerError(f"selected position {position} does not share the approved parent TILE_AREA key")
            if current_span.get("nodeType") != donor_span.get("nodeType"):
                raise TileMaterializerError(
                    f"tile materializer v1 requires the same current/donor node type at selected position {position}"
                )

            current_side = raw.get("current")
            donor_side = raw.get("donor")
            if not isinstance(current_side, dict) or not isinstance(donor_side, dict):
                raise TileMaterializerError(f"approval selection {position} is missing current/donor expected state")
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
    return positions


def _selected_spans(
    report: Mapping[str, Any], positions: Sequence[Position], role: str
) -> dict[Position, dict[str, Any]]:
    indexed = _span_index(report)
    result: dict[Position, dict[str, Any]] = {}
    for position in positions:
        matches = indexed.get(position, [])
        if len(matches) != 1:
            raise TileMaterializerError(f"{role} map must contain exactly one selected tile at {position}")
        result[position] = matches[0]
    return result


def _materialize_raw_tiles(
    *,
    current_map: Path,
    donor_map: Path,
    current_report: Mapping[str, Any],
    donor_report: Mapping[str, Any],
    positions: Sequence[Position],
    output: Path,
) -> dict[str, Any]:
    current_selected = _selected_spans(current_report, positions, "current")
    donor_selected = _selected_spans(donor_report, positions, "donor")
    operations = sorted(
        (
            int(current_selected[position]["startOffset"]),
            int(current_selected[position]["endOffsetExclusive"]),
            position,
            donor_selected[position],
        )
        for position in positions
    )
    cursor = 0
    output_cursor = 0
    current_excluded: list[tuple[int, int]] = []
    output_spans: dict[Position, tuple[int, int]] = {}
    with current_map.open("rb") as current_stream, donor_map.open("rb") as donor_stream, output.open("xb") as out:
        for start, end, position, donor_span in operations:
            if start < cursor or end <= start:
                raise TileMaterializerError("selected current tile spans overlap or are invalid")
            _copy_exact(current_stream, out, cursor, start)
            output_cursor += start - cursor
            current_excluded.append((start, end))
            donor_start = int(donor_span["startOffset"])
            donor_end = int(donor_span["endOffsetExclusive"])
            output_start = output_cursor
            _copy_exact(donor_stream, out, donor_start, donor_end)
            output_cursor += donor_end - donor_start
            output_spans[position] = (output_start, output_cursor)
            cursor = end
        _copy_exact(current_stream, out, cursor, current_map.stat().st_size)
        output_cursor += current_map.stat().st_size - cursor
        out.flush()
        os.fsync(out.fileno())

    current_retained_hash, current_retained_bytes = _hash_ranges_excluding(current_map, current_excluded)
    output_retained_hash, output_retained_bytes = _hash_ranges_excluding(output, list(output_spans.values()))
    if (current_retained_hash, current_retained_bytes) != (output_retained_hash, output_retained_bytes):
        raise TileMaterializerError("non-selected current OTBM bytes were not preserved exactly")
    for position, output_span in output_spans.items():
        if _hash_span(output, *output_span) != donor_selected[position]["sha256"]:
            raise TileMaterializerError(f"output raw tile bytes do not match donor subtree at {position}")

    return {
        "operations": {"replace": len(operations), "insert": 0, "delete": 0},
        "currentExcludedSpans": [list(value) for value in current_excluded],
        "outputSelectedSpans": {
            f"{position[0]},{position[1]},{position[2]}": list(value) for position, value in output_spans.items()
        },
        "retainedBytes": {
            "currentCount": current_retained_bytes,
            "outputCount": output_retained_bytes,
            "sha256": current_retained_hash,
            "exactlyPreserved": True,
        },
    }


def _verify_selected_world_index(
    *, donor_index_path: Path, output_index_path: Path, positions: Sequence[Position]
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    with WorldIndex(donor_index_path) as donor_index, WorldIndex(output_index_path) as output_index:
        for position in sorted(positions, key=lambda value: (value[2], value[1], value[0])):
            donor_hash, _ = _canonical_tile(donor_index, position)
            output_hash, _ = _canonical_tile(output_index, position)
            if output_hash != donor_hash:
                raise TileMaterializerError(f"output World Index tile {position} does not equal donor tile")
            evidence.append(
                {
                    "position": list(position),
                    "canonicalSha256": donor_hash,
                    "equalsDonor": True,
                }
            )
    return evidence


def materialize_tile_replacements(
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
    approval_source = _confined_existing(root, approval_path, "tile materialization approval")
    current_index = _confined_existing(root, current_index_path, "current World Index")
    current_manifest = _confined_existing(root, current_manifest_path, "current World Index manifest")
    donor_index = _confined_existing(root, donor_index_path, "donor World Index")
    donor_manifest = _confined_existing(root, donor_manifest_path, "donor World Index manifest")
    output = _new_confined_path(root, output_map_path, "output map")
    evidence_output = _new_confined_path(root, evidence_dir, "evidence directory", directory=True)
    if output == current_map or output == donor_map:
        raise TileMaterializerError("output map must be distinct from current and donor maps")
    try:
        output.relative_to(evidence_output)
    except ValueError:
        pass
    else:
        raise TileMaterializerError("output map must not be created inside the evidence directory")

    current_pin = _stat_pin(current_map)
    donor_pin = _stat_pin(donor_map)
    scanner_pin = _stat_pin(scanner)
    approval = _load_json(approval_source, "tile materialization approval")
    provenance = approval.get("provenance")
    if not isinstance(provenance, dict):
        raise TileMaterializerError("approval has no provenance object")
    current_provenance = provenance.get("current")
    donor_provenance = provenance.get("donor")
    if not isinstance(current_provenance, dict) or not isinstance(donor_provenance, dict):
        raise TileMaterializerError("approval current/donor provenance is incomplete")
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

    workspace = Path(tempfile.mkdtemp(prefix=".otbm-tile-materializer-", dir=root))
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
        positions = _validate_approval(
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
                raise TileMaterializerError(f"output raw tile subtree differs from donor at {position}")

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
                "current": {"path": current_map.name, "size": current_pin[0], "sha256": current_pin[2]},
                "donor": {"path": donor_map.name, "size": donor_pin[0], "sha256": donor_pin[2]},
                "output": {"path": _relative(root, output), "size": candidate.stat().st_size, "sha256": sha256_path(candidate)},
                "scanner": {"path": scanner.name, "size": scanner_pin[0], "sha256": scanner_pin[2]},
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
                "operation": "replace-existing-same-coordinate-tile",
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
                "action": f"Delete generated output copy {_relative(root, output)} to roll back this materialization artifact.",
            },
            "safety": {
                "sourceInPlaceWrite": False,
                "fullMapSerializer": False,
                "phase8Expanded": False,
                "translatedImport": False,
                "tileInsertion": False,
                "tileDeletion": False,
                "itemStackEditing": False,
                "arbitraryNodeSerialization": False,
                "rawCompleteTileSubtreesOnly": True,
                "sameCoordinateOnly": True,
                "sameParentTileAreaOnly": True,
                "sameNodeTypeOnly": True,
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
