from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Mapping, Sequence

from otbm_region_merge_planner import REPORT_FORMAT as REGION_PLAN_FORMAT
from otbm_semantic_diff import analyze_index_paths
from otbm_semantic_diff_types import canonical_json, sha256_path
from otbm_world_index import WorldIndex, build_world_index

NATIVE_SPAN_FORMAT = "canary-otbm-native-tile-area-spans-v1"
SPAN_FORMAT = "canary-otbm-tile-area-spans-v1"
APPROVAL_FORMAT = "canary-otbm-area-materialization-approval-v1"
RESULT_FORMAT = "canary-otbm-area-materialization-result-v1"
SCHEMA_VERSION = 1
MAX_REPORT_BYTES = 128 * 1024 * 1024
BUFFER_SIZE = 8 * 1024 * 1024

AreaKey = tuple[int, int, int]
Position = tuple[int, int, int]


class AreaMaterializerError(RuntimeError):
    pass


def _load_json(path: Path, label: str, *, maximum: int = MAX_REPORT_BYTES) -> dict[str, Any]:
    if not path.is_file():
        raise AreaMaterializerError(f"{label} is not a regular file: {path}")
    if path.stat().st_size > maximum:
        raise AreaMaterializerError(f"{label} exceeds {maximum} bytes: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AreaMaterializerError(f"Cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise AreaMaterializerError(f"{label} root must be an object")
    return value


def _resolve_existing_regular(path: Path, label: str, *, executable: bool = False) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise AreaMaterializerError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise AreaMaterializerError(f"{label} must be a regular file: {resolved}")
    if executable and not os.access(resolved, os.X_OK):
        raise AreaMaterializerError(f"{label} is not executable: {resolved}")
    return resolved


def _prepare_artifact_root(path: Path) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise AreaMaterializerError(f"artifact root must not be a symlink: {candidate}")
    candidate.mkdir(parents=True, exist_ok=True)
    resolved = candidate.resolve(strict=True)
    if not resolved.is_dir():
        raise AreaMaterializerError(f"artifact root must be a directory: {resolved}")
    return resolved


def _check_ancestors(root: Path, path: Path, label: str) -> None:
    current = path.parent
    while True:
        if current.is_symlink():
            raise AreaMaterializerError(f"{label} parent must not be a symlink: {current}")
        if current == root:
            return
        if root not in current.parents:
            raise AreaMaterializerError(f"{label} escapes artifact root {root}: {path}")
        current = current.parent


def _confined_existing(root: Path, path: Path, label: str) -> Path:
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    lexical = Path(os.path.abspath(candidate))
    try:
        lexical.relative_to(root)
    except ValueError as exc:
        raise AreaMaterializerError(f"{label} escapes artifact root {root}: {lexical}") from exc
    if lexical.is_symlink():
        raise AreaMaterializerError(f"{label} must not be a symlink: {lexical}")
    _check_ancestors(root, lexical, label)
    resolved = lexical.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AreaMaterializerError(f"{label} resolves outside artifact root {root}: {resolved}") from exc
    if not resolved.is_file():
        raise AreaMaterializerError(f"{label} must be a regular file: {resolved}")
    return resolved


def _new_confined_path(root: Path, path: Path, label: str, *, directory: bool = False) -> Path:
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    lexical = Path(os.path.abspath(candidate))
    try:
        lexical.relative_to(root)
    except ValueError as exc:
        raise AreaMaterializerError(f"{label} escapes artifact root {root}: {lexical}") from exc
    if lexical.is_symlink():
        raise AreaMaterializerError(f"{label} must not be a symlink: {lexical}")
    _check_ancestors(root, lexical, label)
    resolved = lexical.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise AreaMaterializerError(f"{label} resolves outside artifact root {root}: {resolved}") from exc
    if resolved.exists() or resolved.is_symlink():
        raise AreaMaterializerError(f"{label} already exists: {resolved}")
    if directory and resolved.suffix:
        # A suffix is legal for directories, but catching accidental JSON/map path swaps is useful.
        pass
    return resolved


def _relative(root: Path, path: Path) -> str:
    return path.resolve(strict=False).relative_to(root).as_posix()


def _stat_pin(path: Path) -> tuple[int, int, str]:
    stat = path.stat()
    return stat.st_size, stat.st_mtime_ns, sha256_path(path)


def _assert_pin(path: Path, pin: tuple[int, int, str], label: str) -> None:
    stat = path.stat()
    if stat.st_size != pin[0] or stat.st_mtime_ns != pin[1] or sha256_path(path) != pin[2]:
        raise AreaMaterializerError(f"{label} changed during materialization: {path}")


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _copy_exact(source: BinaryIO, destination: BinaryIO, start: int, end: int) -> None:
    if end < start:
        raise AreaMaterializerError("invalid byte range")
    source.seek(start)
    remaining = end - start
    while remaining:
        chunk = source.read(min(BUFFER_SIZE, remaining))
        if not chunk:
            raise AreaMaterializerError("unexpected EOF while copying OTBM byte range")
        destination.write(chunk)
        remaining -= len(chunk)


def _hash_ranges_excluding(path: Path, excluded: Sequence[tuple[int, int]]) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    cursor = 0
    size = path.stat().st_size
    with path.open("rb") as stream:
        for start, end in sorted(excluded):
            if start < cursor or end < start or end > size:
                raise AreaMaterializerError("overlapping or invalid excluded physical spans")
            stream.seek(cursor)
            remaining = start - cursor
            while remaining:
                chunk = stream.read(min(BUFFER_SIZE, remaining))
                if not chunk:
                    raise AreaMaterializerError("unexpected EOF while hashing retained OTBM bytes")
                digest.update(chunk)
                total += len(chunk)
                remaining -= len(chunk)
            cursor = end
        stream.seek(cursor)
        while True:
            chunk = stream.read(BUFFER_SIZE)
            if not chunk:
                break
            digest.update(chunk)
            total += len(chunk)
    return digest.hexdigest(), total


def _hash_span(path: Path, start: int, end: int) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        stream.seek(start)
        remaining = end - start
        while remaining:
            chunk = stream.read(min(BUFFER_SIZE, remaining))
            if not chunk:
                raise AreaMaterializerError("unexpected EOF while hashing TILE_AREA span")
            digest.update(chunk)
            remaining -= len(chunk)
    return digest.hexdigest()


def _run_span_scan(
    *, map_path: Path, scanner: Path, output: Path, timeout_seconds: int
) -> dict[str, Any]:
    if timeout_seconds <= 0:
        raise AreaMaterializerError("timeout_seconds must be positive")
    pin = _stat_pin(map_path)
    try:
        completed = subprocess.run(
            [str(scanner), "--tile-area-spans", str(map_path), str(output)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AreaMaterializerError(f"tile-area span scanner timed out after {timeout_seconds} seconds") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise AreaMaterializerError(f"tile-area span scanner failed: {detail}")
    _assert_pin(map_path, pin, "map")
    document = _load_json(output, "native tile-area span report")
    if document.get("format") != NATIVE_SPAN_FORMAT:
        raise AreaMaterializerError(f"unsupported native tile-area span format: {document.get('format')!r}")
    return document


def _normalize_span_report(
    *, map_path: Path, scanner: Path, native: Mapping[str, Any]
) -> dict[str, Any]:
    source = native.get("source")
    map_data = native.get("mapData")
    raw_areas = native.get("areas")
    if not isinstance(source, dict) or not isinstance(map_data, dict) or not isinstance(raw_areas, list):
        raise AreaMaterializerError("native tile-area span report is incomplete")
    size = map_path.stat().st_size
    if source.get("path") != map_path.name or source.get("size") != size:
        raise AreaMaterializerError("native tile-area span source identity mismatch")
    if source.get("unknownAttributeTails") != 0:
        raise AreaMaterializerError("map contains unknown attribute tails; raw structural materialization is unsafe")
    if map_data.get("tileAreaSectionContiguous") is not True:
        raise AreaMaterializerError("direct MAP_DATA tile-area children are interleaved with other node types")
    insertion = map_data.get("insertionOffset")
    map_data_end = map_data.get("endOffset")
    if not isinstance(insertion, int) or not isinstance(map_data_end, int) or not 0 < insertion <= map_data_end < size:
        raise AreaMaterializerError("native tile-area insertion boundary is invalid")

    areas: list[dict[str, Any]] = []
    previous_end = -1
    for index, raw in enumerate(raw_areas):
        if not isinstance(raw, dict):
            raise AreaMaterializerError(f"native tile-area span {index} must be an object")
        values = [raw.get("baseX"), raw.get("baseY"), raw.get("z"), raw.get("startOffset"), raw.get("endOffsetExclusive")]
        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            raise AreaMaterializerError(f"native tile-area span {index} contains invalid integers")
        base_x, base_y, z, start, end = (int(value) for value in values)
        if not (0 <= base_x <= 0xFFFF and 0 <= base_y <= 0xFFFF and 0 <= z <= 15):
            raise AreaMaterializerError(f"native tile-area span {index} has invalid coordinates")
        if not 0 <= start < end <= size:
            raise AreaMaterializerError(f"native tile-area span {index} has invalid physical offsets")
        if start < previous_end:
            raise AreaMaterializerError("native tile-area physical spans overlap or are unsorted")
        previous_end = end
        areas.append(
            {
                "baseX": base_x,
                "baseY": base_y,
                "z": z,
                "startOffset": start,
                "endOffsetExclusive": end,
                "byteLength": end - start,
                "sha256": _hash_span(map_path, start, end),
            }
        )

    return {
        "format": SPAN_FORMAT,
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
        "scanner": {"path": scanner.name, "sha256": sha256_path(scanner), "nativeFormat": NATIVE_SPAN_FORMAT},
        "mapData": dict(map_data),
        "areas": areas,
    }


def scan_tile_area_spans(
    *, map_path: Path, scanner: Path, workspace: Path, role: str, timeout_seconds: int = 3600
) -> dict[str, Any]:
    native_output = workspace / f"{role}-native-area-spans.json"
    native = _run_span_scan(map_path=map_path, scanner=scanner, output=native_output, timeout_seconds=timeout_seconds)
    return _normalize_span_report(map_path=map_path, scanner=scanner, native=native)


def _area_key(entry: Mapping[str, Any]) -> AreaKey:
    return int(entry["baseX"]), int(entry["baseY"]), int(entry["z"])


def _area_index(report: Mapping[str, Any]) -> dict[AreaKey, list[dict[str, Any]]]:
    result: dict[AreaKey, list[dict[str, Any]]] = {}
    for entry in report.get("areas", []):
        if not isinstance(entry, dict):
            raise AreaMaterializerError("tile-area span report contains a non-object area")
        result.setdefault(_area_key(entry), []).append(entry)
    return result


def _position(value: Any, label: str) -> Position:
    if not isinstance(value, list) or len(value) != 3 or any(isinstance(part, bool) or not isinstance(part, int) for part in value):
        raise AreaMaterializerError(f"{label} must contain integer x,y,z")
    x, y, z = (int(part) for part in value)
    if not (0 <= x <= 0xFFFF and 0 <= y <= 0xFFFF and 0 <= z <= 15):
        raise AreaMaterializerError(f"{label} is outside the OTBM coordinate range")
    return x, y, z


def _expected_area_keys(plan: Mapping[str, Any]) -> tuple[list[AreaKey], Position, Position]:
    if plan.get("format") != REGION_PLAN_FORMAT or plan.get("schemaVersion") != 1:
        raise AreaMaterializerError("merge plan must use canary-otbm-region-merge-plan-v1 schemaVersion 1")
    if plan.get("analysisComplete") is not True or plan.get("policy") != "replace-region":
        raise AreaMaterializerError("materializer v1 requires a complete replace-region plan")
    translation = plan.get("translation")
    if not isinstance(translation, dict):
        raise AreaMaterializerError("merge plan has no translation object")
    delta = _position(translation.get("delta"), "translation.delta")
    # normalize_position cannot represent negative deltas, but v1 requires literal zero anyway.
    if delta != (0, 0, 0):
        raise AreaMaterializerError("materializer v1 requires zero donor-to-target translation")
    donor_region = translation.get("donorRegion")
    target_region = translation.get("targetRegion")
    if not isinstance(donor_region, dict) or not isinstance(target_region, dict):
        raise AreaMaterializerError("merge plan regions are incomplete")
    lower = _position(donor_region.get("from"), "donorRegion.from")
    upper = _position(donor_region.get("to"), "donorRegion.to")
    target_lower = _position(target_region.get("from"), "targetRegion.from")
    target_upper = _position(target_region.get("to"), "targetRegion.to")
    if (lower, upper) != (target_lower, target_upper):
        raise AreaMaterializerError("zero-translation materialization requires identical donor and target regions")
    if lower[0] % 256 != 0 or lower[1] % 256 != 0 or upper[0] % 256 != 255 or upper[1] % 256 != 255:
        raise AreaMaterializerError("materializer v1 requires complete 256x256 tile-area aligned x/y bounds")
    if upper[0] < lower[0] or upper[1] < lower[1] or upper[2] < lower[2]:
        raise AreaMaterializerError("merge plan donor region bounds are reversed")
    keys = [
        (base_x, base_y, z)
        for z in range(lower[2], upper[2] + 1)
        for base_y in range(lower[1], upper[1] + 1, 256)
        for base_x in range(lower[0], upper[0] + 1, 256)
    ]
    return keys, lower, upper


def _pin_matches(path: Path, pin: Mapping[str, Any], label: str) -> None:
    if pin.get("size") != path.stat().st_size or pin.get("sha256") != sha256_path(path):
        raise AreaMaterializerError(f"{label} does not match the merge-plan provenance pin")


def _validate_plan_provenance(
    *,
    plan: Mapping[str, Any],
    current_map: Path,
    donor_map: Path,
    current_index: Path,
    current_manifest: Path,
    donor_index: Path,
    donor_manifest: Path,
) -> None:
    provenance = plan.get("provenance")
    if not isinstance(provenance, dict):
        raise AreaMaterializerError("merge plan has no provenance object")
    manifests = provenance.get("manifests")
    if not isinstance(manifests, dict):
        raise AreaMaterializerError("merge plan has no manifest provenance")
    for role, map_path, index_path, manifest_path in (
        ("current", current_map, current_index, current_manifest),
        ("donor", donor_map, donor_index, donor_manifest),
    ):
        role_provenance = provenance.get(role)
        if not isinstance(role_provenance, dict):
            raise AreaMaterializerError(f"merge plan has no {role} provenance")
        source_pin = role_provenance.get("sourceMap")
        index_pin = role_provenance.get("worldIndex")
        manifest_pin = manifests.get(role)
        if not isinstance(source_pin, dict) or not isinstance(index_pin, dict) or not isinstance(manifest_pin, dict):
            raise AreaMaterializerError(f"merge plan {role} provenance is incomplete")
        _pin_matches(map_path, source_pin, f"{role} map")
        _pin_matches(index_path, index_pin, f"{role} World Index")
        _pin_matches(manifest_path, manifest_pin, f"{role} World Index manifest")


def _validate_approval(
    *, plan_path: Path, plan: Mapping[str, Any], approval: Mapping[str, Any], expected_keys: Sequence[AreaKey]
) -> None:
    if approval.get("format") != APPROVAL_FORMAT or approval.get("schemaVersion") != SCHEMA_VERSION:
        raise AreaMaterializerError(f"approval must use {APPROVAL_FORMAT} schemaVersion {SCHEMA_VERSION}")
    if approval.get("decision") != "approved":
        raise AreaMaterializerError("approval decision must be 'approved'")
    if not str(approval.get("rationale", "")).strip():
        raise AreaMaterializerError("approval requires a non-empty rationale")
    plan_pin = approval.get("plan")
    if not isinstance(plan_pin, dict) or plan_pin.get("format") != REGION_PLAN_FORMAT:
        raise AreaMaterializerError("approval must pin the region merge plan format")
    if plan_pin.get("sha256") != sha256_path(plan_path):
        raise AreaMaterializerError("approval plan SHA-256 does not match the supplied merge plan")
    if plan.get("ok") is not True or plan.get("summary", {}).get("blockingConflicts") != 0:
        raise AreaMaterializerError("merge plan contains blocking conflicts")

    summary = plan.get("summary")
    raw_conflicts = plan.get("conflicts")
    if not isinstance(summary, dict) or not isinstance(raw_conflicts, list):
        raise AreaMaterializerError("merge plan conflict evidence is incomplete")
    conflict_summary = summary.get("conflicts")
    if not isinstance(conflict_summary, dict):
        raise AreaMaterializerError("merge plan conflict summary is missing")
    if conflict_summary.get("truncated") is True or conflict_summary.get("total") != len(raw_conflicts):
        raise AreaMaterializerError("merge plan conflict evidence is truncated; rerun a narrower plan before approval")
    conflict_ids: set[str] = set()
    for entry in raw_conflicts:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise AreaMaterializerError("merge plan contains invalid conflict evidence")
        if entry.get("severity") in {"error", "unresolved"}:
            raise AreaMaterializerError("approval cannot override blocking error/unresolved conflict evidence")
        conflict_ids.add(entry["id"])
    approved_conflicts = approval.get("approvedConflictIds")
    if not isinstance(approved_conflicts, list) or any(not isinstance(value, str) for value in approved_conflicts):
        raise AreaMaterializerError("approval approvedConflictIds must be an array of strings")
    if set(approved_conflicts) != conflict_ids or len(approved_conflicts) != len(conflict_ids):
        raise AreaMaterializerError("approval must explicitly cover every non-blocking merge-plan conflict exactly once")

    raw_keys = approval.get("approvedAreaKeys")
    if not isinstance(raw_keys, list):
        raise AreaMaterializerError("approval approvedAreaKeys must be an array")
    approved_keys: list[AreaKey] = []
    for index, raw in enumerate(raw_keys):
        if not isinstance(raw, dict):
            raise AreaMaterializerError(f"approvedAreaKeys[{index}] must be an object")
        try:
            key = int(raw["baseX"]), int(raw["baseY"]), int(raw["z"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AreaMaterializerError(f"approvedAreaKeys[{index}] is invalid") from exc
        approved_keys.append(key)
    if sorted(approved_keys) != sorted(expected_keys) or len(approved_keys) != len(set(approved_keys)):
        raise AreaMaterializerError("approval area keys must exactly match every tile area covered by the aligned merge plan")


def _validate_header_compatibility(current: Mapping[str, Any], donor: Mapping[str, Any]) -> None:
    current_source = current.get("source")
    donor_source = donor.get("source")
    if not isinstance(current_source, dict) or not isinstance(donor_source, dict):
        raise AreaMaterializerError("tile-area span source evidence is missing")
    mismatches = [
        key
        for key in ("otbmVersion", "width", "height", "itemsMajor", "itemsMinor")
        if current_source.get(key) != donor_source.get(key)
    ]
    if mismatches:
        raise AreaMaterializerError(f"current/donor OTBM headers are incompatible for raw subtree materialization: {mismatches}")


def _selected_spans(
    report: Mapping[str, Any], keys: Sequence[AreaKey], role: str
) -> dict[AreaKey, dict[str, Any] | None]:
    indexed = _area_index(report)
    result: dict[AreaKey, dict[str, Any] | None] = {}
    for key in keys:
        matches = indexed.get(key, [])
        if len(matches) > 1:
            raise AreaMaterializerError(f"{role} map has duplicate raw TILE_AREA nodes for selected key {key}")
        result[key] = matches[0] if matches else None
    return result


def _materialize_raw(
    *,
    current_map: Path,
    donor_map: Path,
    current_report: Mapping[str, Any],
    donor_report: Mapping[str, Any],
    keys: Sequence[AreaKey],
    output: Path,
) -> dict[str, Any]:
    current_selected = _selected_spans(current_report, keys, "current")
    donor_selected = _selected_spans(donor_report, keys, "donor")
    insertion_offset = int(current_report["mapData"]["insertionOffset"])

    operations: list[dict[str, Any]] = []
    inserted: list[tuple[AreaKey, dict[str, Any]]] = []
    for key in sorted(keys, key=lambda value: (value[2], value[1], value[0])):
        current_span = current_selected[key]
        donor_span = donor_selected[key]
        if current_span is not None:
            operations.append(
                {
                    "start": int(current_span["startOffset"]),
                    "end": int(current_span["endOffsetExclusive"]),
                    "donor": [(key, donor_span)] if donor_span is not None else [],
                    "kind": "replace" if donor_span is not None else "delete",
                }
            )
        elif donor_span is not None:
            inserted.append((key, donor_span))
    if inserted:
        operations.append({"start": insertion_offset, "end": insertion_offset, "donor": inserted, "kind": "insert"})

    operations.sort(key=lambda entry: (entry["start"], -(entry["end"] - entry["start"])))
    cursor = 0
    output_cursor = 0
    output_spans: dict[AreaKey, tuple[int, int]] = {}
    current_excluded: list[tuple[int, int]] = []
    with current_map.open("rb") as current_stream, donor_map.open("rb") as donor_stream, output.open("xb") as out:
        for operation in operations:
            start = int(operation["start"])
            end = int(operation["end"])
            if start < cursor or end < start:
                raise AreaMaterializerError("selected current TILE_AREA operations overlap")
            _copy_exact(current_stream, out, cursor, start)
            output_cursor += start - cursor
            if end > start:
                current_excluded.append((start, end))
            for key, donor_span in operation["donor"]:
                if donor_span is None:
                    continue
                donor_start = int(donor_span["startOffset"])
                donor_end = int(donor_span["endOffsetExclusive"])
                span_output_start = output_cursor
                _copy_exact(donor_stream, out, donor_start, donor_end)
                output_cursor += donor_end - donor_start
                output_spans[key] = (span_output_start, output_cursor)
            cursor = end
        _copy_exact(current_stream, out, cursor, current_map.stat().st_size)
        output_cursor += current_map.stat().st_size - cursor
        out.flush()
        os.fsync(out.fileno())

    current_retained_hash, current_retained_bytes = _hash_ranges_excluding(current_map, current_excluded)
    output_retained_hash, output_retained_bytes = _hash_ranges_excluding(output, list(output_spans.values()))
    if (current_retained_hash, current_retained_bytes) != (output_retained_hash, output_retained_bytes):
        raise AreaMaterializerError("non-selected current OTBM bytes were not preserved exactly")

    donor_index = _area_index(donor_report)
    for key, output_span in output_spans.items():
        donor_span = donor_index[key][0]
        if _hash_span(output, *output_span) != donor_span["sha256"]:
            raise AreaMaterializerError(f"output TILE_AREA bytes do not match donor subtree for {key}")

    return {
        "operations": {
            "replace": sum(entry["kind"] == "replace" for entry in operations),
            "delete": sum(entry["kind"] == "delete" for entry in operations),
            "insert": len(inserted),
        },
        "currentExcludedSpans": current_excluded,
        "outputSelectedSpans": {f"{key[0]},{key[1]},{key[2]}": list(value) for key, value in output_spans.items()},
        "retainedBytes": {
            "currentCount": current_retained_bytes,
            "outputCount": output_retained_bytes,
            "sha256": current_retained_hash,
            "exactlyPreserved": True,
        },
    }


def _canonical_area(index: WorldIndex, key: AreaKey) -> tuple[str, int]:
    base_x, base_y, z = key
    tiles: list[dict[str, Any]] = []
    for _, tile in index.iter_region_tiles((base_x, base_y, z), (base_x + 255, base_y + 255, z)):
        placements: list[dict[str, Any]] = []
        for ordinal in range(tile.placement_start, tile.placement_start + tile.placement_count):
            placement = index.placement(ordinal)
            placements.append(
                {
                    key_name: placement.get(key_name)
                    for key_name in (
                        "itemId",
                        "itemDepth",
                        "source",
                        "actionId",
                        "uniqueId",
                        "houseDoorId",
                        "teleportDestination",
                    )
                    if placement.get(key_name) is not None
                }
            )
        tiles.append(
            {
                "position": [tile.x, tile.y, tile.z],
                "kind": tile.kind,
                "houseId": tile.house_id,
                "flags": tile.flags,
                "placements": placements,
            }
        )
    encoded = canonical_json(tiles).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), len(tiles)


def _verify_selected_world_index(
    *, donor_index_path: Path, output_index_path: Path, keys: Sequence[AreaKey]
) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    with WorldIndex(donor_index_path) as donor_index, WorldIndex(output_index_path) as output_index:
        for key in sorted(keys, key=lambda value: (value[2], value[1], value[0])):
            donor_hash, donor_tiles = _canonical_area(donor_index, key)
            output_hash, output_tiles = _canonical_area(output_index, key)
            if (donor_hash, donor_tiles) != (output_hash, output_tiles):
                raise AreaMaterializerError(f"output World Index area {key} does not equal donor area")
            evidence.append(
                {
                    "baseX": key[0],
                    "baseY": key[1],
                    "z": key[2],
                    "tileCount": donor_tiles,
                    "canonicalSha256": donor_hash,
                    "equalsDonor": True,
                }
            )
    return evidence


def _publish_directory_no_overwrite(source: Path, destination: Path) -> None:
    destination.mkdir(mode=0o700)
    try:
        for child in sorted(source.iterdir(), key=lambda candidate: candidate.name):
            if child.is_symlink() or not child.is_file():
                raise AreaMaterializerError(f"evidence workspace contains a non-regular entry: {child}")
            published = destination / child.name
            os.link(child, published)
            child.unlink()
        source.rmdir()
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def materialize_area_plan(
    *,
    artifact_root: Path,
    current_map_path: Path,
    donor_map_path: Path,
    scanner_path: Path,
    plan_path: Path,
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
    plan_source = _confined_existing(root, plan_path, "region merge plan")
    approval_source = _confined_existing(root, approval_path, "area materialization approval")
    current_index = _confined_existing(root, current_index_path, "current World Index")
    current_manifest = _confined_existing(root, current_manifest_path, "current World Index manifest")
    donor_index = _confined_existing(root, donor_index_path, "donor World Index")
    donor_manifest = _confined_existing(root, donor_manifest_path, "donor World Index manifest")
    output = _new_confined_path(root, output_map_path, "output map")
    evidence_output = _new_confined_path(root, evidence_dir, "evidence directory", directory=True)
    if output == current_map or output == donor_map:
        raise AreaMaterializerError("output map must be distinct from current and donor maps")
    try:
        output.relative_to(evidence_output)
    except ValueError:
        pass
    else:
        raise AreaMaterializerError("output map must not be created inside the evidence directory")

    current_pin = _stat_pin(current_map)
    donor_pin = _stat_pin(donor_map)
    scanner_pin = _stat_pin(scanner)
    plan = _load_json(plan_source, "region merge plan")
    approval = _load_json(approval_source, "area materialization approval")
    keys, lower, upper = _expected_area_keys(plan)
    _validate_approval(plan_path=plan_source, plan=plan, approval=approval, expected_keys=keys)
    _validate_plan_provenance(
        plan=plan,
        current_map=current_map,
        donor_map=donor_map,
        current_index=current_index,
        current_manifest=current_manifest,
        donor_index=donor_index,
        donor_manifest=donor_manifest,
    )

    workspace = Path(tempfile.mkdtemp(prefix=".otbm-area-materializer-", dir=root))
    evidence_workspace = workspace / "evidence"
    evidence_workspace.mkdir()
    candidate = workspace / "candidate.otbm"
    published_output = False
    try:
        current_spans = scan_tile_area_spans(
            map_path=current_map, scanner=scanner, workspace=workspace, role="current", timeout_seconds=timeout_seconds
        )
        donor_spans = scan_tile_area_spans(
            map_path=donor_map, scanner=scanner, workspace=workspace, role="donor", timeout_seconds=timeout_seconds
        )
        _validate_header_compatibility(current_spans, donor_spans)
        raw_proof = _materialize_raw(
            current_map=current_map,
            donor_map=donor_map,
            current_report=current_spans,
            donor_report=donor_spans,
            keys=keys,
            output=candidate,
        )
        output_spans = scan_tile_area_spans(
            map_path=candidate, scanner=scanner, workspace=workspace, role="output", timeout_seconds=timeout_seconds
        )
        _validate_header_compatibility(current_spans, output_spans)

        donor_selected = _selected_spans(donor_spans, keys, "donor")
        output_selected = _selected_spans(output_spans, keys, "output")
        for key in keys:
            donor_span = donor_selected[key]
            output_span = output_selected[key]
            if donor_span is None:
                if output_span is not None:
                    raise AreaMaterializerError(f"output retained a TILE_AREA that donor omits for selected key {key}")
            elif output_span is None or donor_span["sha256"] != output_span["sha256"]:
                raise AreaMaterializerError(f"output raw TILE_AREA subtree differs from donor for selected key {key}")

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
            donor_index_path=donor_index, output_index_path=output_index, keys=keys
        )
        semantic_diff = analyze_index_paths(
            artifact_root=root,
            before_index_path=Path(_relative(root, current_index)),
            before_manifest_path=Path(_relative(root, current_manifest)),
            after_index_path=Path(_relative(root, output_index)),
            after_manifest_path=Path(_relative(root, output_manifest)),
            lower=lower,
            upper=upper,
            sample_limit=10_000,
        )
        semantic_path = evidence_workspace / "semantic-diff.json"
        _write_json(semantic_path, semantic_diff)
        current_spans_path = evidence_workspace / "current-area-spans.json"
        donor_spans_path = evidence_workspace / "donor-area-spans.json"
        output_spans_path = evidence_workspace / "output-area-spans.json"
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
            "plan": {
                "path": _relative(root, plan_source),
                "sha256": sha256_path(plan_source),
                "format": REGION_PLAN_FORMAT,
                "policy": plan["policy"],
                "writerReadyFromPlanner": plan.get("writerReady"),
            },
            "approval": {
                "path": _relative(root, approval_source),
                "sha256": sha256_path(approval_source),
                "format": APPROVAL_FORMAT,
                "decision": approval["decision"],
            },
            "selection": {
                "from": list(lower),
                "to": list(upper),
                "areaKeys": [{"baseX": key[0], "baseY": key[1], "z": key[2]} for key in keys],
                "areaCount": len(keys),
                "translation": [0, 0, 0],
            },
            "rawConfinement": raw_proof,
            "selectedWorldIndex": selected_world_index,
            "verification": {
                "nativeReparse": True,
                "worldIndexRebuilt": True,
                "selectedAreasEqualDonor": True,
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
                "tileLevelOverlay": False,
                "rawCompleteTileAreaSubtreesOnly": True,
                "plannerReportExecutedDirectly": False,
                "separateApprovalRequired": True,
                "gameplayCorrectnessProven": False,
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
