from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from otbm_semantic_diff import analyze_index_paths, write_report
from otbm_semantic_diff_types import SemanticDiffError
from otbm_world_index import WorldIndexError, build_world_index

from otbm_bounded_patch_types import (
    ANCHOR_FORMAT,
    NATIVE_ANCHOR_FORMAT,
    PLAN_FORMAT,
    RESULT_FORMAT,
    BoundedPatchError,
    PatchOperation,
    PatchPlan,
    canonical_json,
    encoded_width,
    sha256_file,
    value_bytes,
)

MAX_OPERATIONS = 10_000
MAX_NATIVE_ANCHOR_BYTES = 512 * 1024 * 1024
BUFFER_SIZE = 8 * 1024 * 1024
MARKER_BYTES = {0xFD, 0xFE, 0xFF}
DIFF_KIND = {
    "set-action-id": "action-id-changed",
    "set-unique-id": "unique-id-changed",
    "set-house-door-id": "house-door-id-changed",
    "set-teleport-destination": "teleport-destination-changed",
}


def _resolve_existing_regular(path: Path, label: str, *, executable: bool = False) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise BoundedPatchError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file():
        raise BoundedPatchError(f"{label} must be a regular file: {resolved}")
    if executable and not os.access(resolved, os.X_OK):
        raise BoundedPatchError(f"{label} is not executable: {resolved}")
    return resolved


def _prepare_artifact_root(path: Path) -> Path:
    candidate = path.expanduser()
    if candidate.is_symlink():
        raise BoundedPatchError(f"artifact root must not be a symlink: {candidate}")
    candidate.mkdir(parents=True, exist_ok=True)
    resolved = candidate.resolve(strict=True)
    if not resolved.is_dir():
        raise BoundedPatchError(f"artifact root must be a directory: {resolved}")
    return resolved


def _check_ancestors(root: Path, path: Path, label: str) -> None:
    current = path.parent
    while True:
        if current.exists() and current.is_symlink():
            raise BoundedPatchError(f"{label} parent must not be a symlink: {current}")
        if current == root:
            return
        if root not in current.parents:
            raise BoundedPatchError(f"{label} escapes artifact root {root}: {path}")
        current = current.parent


def _new_confined_path(root: Path, path: Path, label: str) -> Path:
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise BoundedPatchError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BoundedPatchError(f"{label} escapes artifact root {root}: {resolved}") from exc
    _check_ancestors(root, resolved, label)
    if resolved.exists():
        raise BoundedPatchError(f"{label} already exists: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    _check_ancestors(root, resolved, label)
    return resolved


def _relative(root: Path, path: Path) -> str:
    return path.resolve(strict=False).relative_to(root).as_posix()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
        temporary.unlink()
        _fsync_directory(path.parent)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _run_scanner(scanner: Path, arguments: Sequence[str], *, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    if timeout_seconds <= 0:
        raise BoundedPatchError("timeout_seconds must be positive")
    try:
        completed = subprocess.run(
            [str(scanner), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise BoundedPatchError(f"native scanner timed out after {timeout_seconds} seconds") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
        raise BoundedPatchError(f"native scanner failed: {detail}")
    return completed


def _load_json(path: Path, label: str, *, maximum: int = MAX_NATIVE_ANCHOR_BYTES) -> dict[str, Any]:
    if not path.is_file():
        raise BoundedPatchError(f"{label} was not created: {path}")
    size = path.stat().st_size
    if size > maximum:
        raise BoundedPatchError(f"{label} is {size} bytes; maximum is {maximum}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BoundedPatchError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise BoundedPatchError(f"{label} must be a JSON object")
    return value


def _scan_anchors(
    *,
    source: Path,
    scanner: Path,
    native_output: Path,
    public_output: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    source_stat_before = source.stat()
    source_hash = sha256_file(source)
    scanner_hash = sha256_file(scanner)
    completed = _run_scanner(
        scanner,
        ["--patch-anchors", str(source), str(native_output)],
        timeout_seconds=timeout_seconds,
    )
    document = _load_json(native_output, "native patch-anchor report")
    if document.get("format") != NATIVE_ANCHOR_FORMAT:
        raise BoundedPatchError(f"unsupported native anchor format: {document.get('format')!r}")
    source_info = document.get("source")
    anchors = document.get("anchors")
    if not isinstance(source_info, dict) or not isinstance(anchors, list):
        raise BoundedPatchError("native anchor report must contain source object and anchors array")
    source_stat_after = source.stat()
    if (
        source_stat_before.st_size != source_stat_after.st_size
        or source_stat_before.st_mtime_ns != source_stat_after.st_mtime_ns
        or sha256_file(source) != source_hash
    ):
        raise BoundedPatchError("source map changed while native anchors were being generated")
    if source_info.get("path") != source.name or source_info.get("size") != source_stat_before.st_size:
        raise BoundedPatchError("native anchor source identity does not match the scanned map")
    expected_stdout = f"anchors={len(anchors)}"
    if completed.stdout.strip() != expected_stdout:
        raise BoundedPatchError(
            f"native anchor summary is {completed.stdout.strip()!r}; expected {expected_stdout!r}"
        )
    normalized = {
        "format": ANCHOR_FORMAT,
        "source": {
            "path": source.name,
            "size": source_stat_before.st_size,
            "sha256": source_hash,
            "otbmVersion": source_info.get("otbmVersion"),
            "width": source_info.get("width"),
            "height": source_info.get("height"),
            "itemsMajor": source_info.get("itemsMajor"),
            "itemsMinor": source_info.get("itemsMinor"),
        },
        "scanner": {"path": scanner.name, "sha256": scanner_hash},
        "anchors": anchors,
    }
    _write_json(public_output, normalized)
    return normalized


def _require_int(value: Any, label: str, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise BoundedPatchError(f"{label} must be an integer in {lower}..{upper}")
    return value


def _anchor_identity(anchor: Mapping[str, Any]) -> tuple[Any, ...]:
    position = anchor.get("position")
    if not isinstance(position, list) or len(position) != 3:
        raise BoundedPatchError("anchor.position must contain x,y,z")
    normalized_position = (
        _require_int(position[0], "anchor.position[0]", 0, 0xFFFF),
        _require_int(position[1], "anchor.position[1]", 0, 0xFFFF),
        _require_int(position[2], "anchor.position[2]", 0, 15),
    )
    attribute = anchor.get("attribute")
    if attribute not in {"actionId", "uniqueId", "houseDoorId", "teleportDestination"}:
        raise BoundedPatchError(f"unsupported anchor attribute: {attribute!r}")
    return (
        normalized_position,
        _require_int(anchor.get("tilePlacementIndex"), "anchor.tilePlacementIndex", 0, 0xFFFFFFFF),
        _require_int(anchor.get("itemId"), "anchor.itemId", 0, 0xFFFF),
        _require_int(anchor.get("itemDepth"), "anchor.itemDepth", 0, 0x7FFF),
        attribute,
    )


def _operation_expected_json(operation: PatchOperation) -> int | list[int]:
    return list(operation.expected) if isinstance(operation.expected, tuple) else operation.expected


def _operation_replacement_json(operation: PatchOperation) -> int | list[int]:
    return list(operation.replacement) if isinstance(operation.replacement, tuple) else operation.replacement


def _operation_identity(operation: PatchOperation) -> tuple[Any, ...]:
    return (
        operation.position,
        operation.tile_placement_index,
        operation.item_id,
        operation.item_depth,
        operation.attribute,
    )


def _validate_plan_source(plan: PatchPlan, source: Path, anchors: Mapping[str, Any]) -> None:
    info = anchors.get("source")
    if not isinstance(info, Mapping):
        raise BoundedPatchError("normalized anchor report has no source object")
    expected = {
        "fileName": plan.source.file_name,
        "sha256": plan.source.sha256,
        "size": plan.source.size,
        "otbmVersion": plan.source.otbm_version,
        "itemsMajor": plan.source.items_major,
        "itemsMinor": plan.source.items_minor,
    }
    actual = {
        "fileName": source.name,
        "sha256": info.get("sha256"),
        "size": info.get("size"),
        "otbmVersion": info.get("otbmVersion"),
        "itemsMajor": info.get("itemsMajor"),
        "itemsMinor": info.get("itemsMinor"),
    }
    mismatches = [key for key in expected if expected[key] != actual[key]]
    if mismatches:
        raise BoundedPatchError(f"source pin mismatch for: {', '.join(mismatches)}")


def _validate_anchor_bytes(
    source: Path,
    operation: PatchOperation,
    anchor: Mapping[str, Any],
) -> tuple[list[dict[str, int]], list[tuple[int, int]], tuple[int, ...]]:
    raw_bytes = anchor.get("bytes")
    if not isinstance(raw_bytes, list):
        raise BoundedPatchError(f"operation {operation.operation_id} anchor.bytes must be an array")
    expected_bytes = value_bytes(operation.kind, operation.expected)
    replacement_bytes = value_bytes(operation.kind, operation.replacement)
    if len(raw_bytes) != len(expected_bytes):
        raise BoundedPatchError(
            f"operation {operation.operation_id} anchor has {len(raw_bytes)} logical bytes; expected {len(expected_bytes)}"
        )
    normalized: list[dict[str, int]] = []
    spans: list[tuple[int, int]] = []
    size = source.stat().st_size
    with source.open("rb") as stream:
        for index, raw in enumerate(raw_bytes):
            if not isinstance(raw, Mapping):
                raise BoundedPatchError(f"operation {operation.operation_id} anchor byte {index} must be an object")
            offset = _require_int(raw.get("offset"), "anchor byte offset", 0, max(0, size - 1))
            encoded_size = _require_int(raw.get("encodedSize"), "anchor encodedSize", 1, 2)
            value = _require_int(raw.get("value"), "anchor byte value", 0, 0xFF)
            if value != expected_bytes[index]:
                raise BoundedPatchError(
                    f"operation {operation.operation_id} scanner byte {index} is {value}; expected {expected_bytes[index]}"
                )
            if encoded_size != encoded_width(value):
                raise BoundedPatchError(
                    f"operation {operation.operation_id} source uses non-canonical escape width for logical byte {index}"
                )
            if encoded_width(replacement_bytes[index]) != encoded_size:
                raise BoundedPatchError(
                    f"operation {operation.operation_id} replacement changes OTBM escape width at logical byte {index}"
                )
            if offset + encoded_size > size:
                raise BoundedPatchError(f"operation {operation.operation_id} byte span escapes the source file")
            stream.seek(offset)
            physical = stream.read(encoded_size)
            wanted = bytes((value,)) if encoded_size == 1 else bytes((0xFD, value))
            if physical != wanted:
                raise BoundedPatchError(
                    f"operation {operation.operation_id} source bytes disagree with scanner anchor at offset {offset}"
                )
            normalized.append({"offset": offset, "encodedSize": encoded_size, "value": value})
            spans.append((offset, offset + encoded_size))
    return normalized, spans, replacement_bytes


def _resolve_operations(
    *,
    plan: PatchPlan,
    source: Path,
    anchor_document: Mapping[str, Any],
) -> list[dict[str, Any]]:
    raw_anchors = anchor_document.get("anchors")
    if not isinstance(raw_anchors, list):
        raise BoundedPatchError("normalized anchor report has no anchors array")
    anchors: list[Mapping[str, Any]] = []
    identities: list[tuple[Any, ...]] = []
    for index, raw in enumerate(raw_anchors):
        if not isinstance(raw, Mapping):
            raise BoundedPatchError(f"anchors[{index}] must be an object")
        anchors.append(raw)
        identities.append(_anchor_identity(raw))

    resolved: list[dict[str, Any]] = []
    occupied: list[tuple[int, int, str]] = []
    for operation in plan.operations:
        identity = _operation_identity(operation)
        matching = [anchor for anchor, anchor_identity in zip(anchors, identities, strict=True) if anchor_identity == identity]
        if not matching:
            raise BoundedPatchError(f"operation {operation.operation_id} target anchor was not found")
        if len(matching) != 1:
            raise BoundedPatchError(f"operation {operation.operation_id} target anchor is ambiguous ({len(matching)} matches)")
        anchor = matching[0]
        expected_json = _operation_expected_json(operation)
        if anchor.get("value") != expected_json:
            raise BoundedPatchError(
                f"operation {operation.operation_id} old value is {anchor.get('value')!r}; expected {expected_json!r}"
            )
        normalized_bytes, spans, replacement_bytes = _validate_anchor_bytes(source, operation, anchor)
        for start, end in spans:
            for existing_start, existing_end, existing_id in occupied:
                if start < existing_end and existing_start < end:
                    raise BoundedPatchError(
                        f"operation {operation.operation_id} overlaps operation {existing_id} at physical bytes"
                    )
            occupied.append((start, end, operation.operation_id))
        resolved.append(
            {
                "id": operation.operation_id,
                "kind": operation.kind,
                "position": list(operation.position),
                "tilePlacementIndex": operation.tile_placement_index,
                "itemId": operation.item_id,
                "itemDepth": operation.item_depth,
                "attribute": operation.attribute,
                "expected": expected_json,
                "replacement": _operation_replacement_json(operation),
                "bytes": normalized_bytes,
                "replacementBytes": list(replacement_bytes),
                "spans": [{"offset": start, "size": end - start} for start, end in spans],
            }
        )
    return resolved


def _copy_and_patch(source: Path, destination: Path, operations: Sequence[Mapping[str, Any]]) -> None:
    with source.open("rb") as source_stream, destination.open("xb") as output_stream:
        shutil.copyfileobj(source_stream, output_stream, length=BUFFER_SIZE)
        output_stream.flush()
        os.fsync(output_stream.fileno())
    with destination.open("r+b", buffering=0) as stream:
        for operation in operations:
            replacement = operation["replacementBytes"]
            for byte, logical in zip(operation["bytes"], replacement, strict=True):
                payload_offset = int(byte["offset"]) + (1 if int(byte["encodedSize"]) == 2 else 0)
                stream.seek(payload_offset)
                stream.write(bytes((int(logical),)))
        os.fsync(stream.fileno())


def _compare_outside_spans(
    source: Path,
    output: Path,
    operations: Sequence[Mapping[str, Any]],
) -> list[int]:
    if source.stat().st_size != output.stat().st_size:
        raise BoundedPatchError("patched output length differs from source length")
    allowed: set[int] = set()
    for operation in operations:
        for span in operation["spans"]:
            start = int(span["offset"])
            allowed.update(range(start, start + int(span["size"])))
    changed: list[int] = []
    position = 0
    with source.open("rb") as before, output.open("rb") as after:
        while True:
            left = before.read(BUFFER_SIZE)
            right = after.read(BUFFER_SIZE)
            if not left and not right:
                break
            if len(left) != len(right):
                raise BoundedPatchError("patched output stream length differs from source")
            for index, (old, new) in enumerate(zip(left, right, strict=True)):
                if old == new:
                    continue
                offset = position + index
                if offset not in allowed:
                    raise BoundedPatchError(f"unplanned physical byte change at offset {offset}")
                changed.append(offset)
            position += len(left)
    if not changed:
        raise BoundedPatchError("patch produced no physical byte change")
    return changed


def _verify_after_anchors(
    plan: PatchPlan,
    before_operations: Sequence[Mapping[str, Any]],
    after_document: Mapping[str, Any],
) -> None:
    raw_anchors = after_document.get("anchors")
    if not isinstance(raw_anchors, list):
        raise BoundedPatchError("after anchor report has no anchors array")
    by_identity: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    for raw in raw_anchors:
        if not isinstance(raw, Mapping):
            raise BoundedPatchError("after anchor entry must be an object")
        by_identity.setdefault(_anchor_identity(raw), []).append(raw)
    before_by_id = {str(operation["id"]): operation for operation in before_operations}
    for operation in plan.operations:
        matching = by_identity.get(_operation_identity(operation), [])
        if len(matching) != 1:
            raise BoundedPatchError(
                f"operation {operation.operation_id} has {len(matching)} matching anchors after patch; expected 1"
            )
        anchor = matching[0]
        if anchor.get("value") != _operation_replacement_json(operation):
            raise BoundedPatchError(f"operation {operation.operation_id} replacement was not observed after full reparse")
        after_bytes = anchor.get("bytes")
        before_bytes = before_by_id[operation.operation_id]["bytes"]
        if not isinstance(after_bytes, list) or len(after_bytes) != len(before_bytes):
            raise BoundedPatchError(f"operation {operation.operation_id} byte-span shape changed after patch")
        for before_byte, after_byte in zip(before_bytes, after_bytes, strict=True):
            if not isinstance(after_byte, Mapping):
                raise BoundedPatchError("after anchor byte must be an object")
            if (
                after_byte.get("offset") != before_byte["offset"]
                or after_byte.get("encodedSize") != before_byte["encodedSize"]
            ):
                raise BoundedPatchError(f"operation {operation.operation_id} physical anchor moved after patch")


def _semantic_signature_from_operation(operation: PatchOperation) -> tuple[Any, ...]:
    return (
        DIFF_KIND[operation.kind],
        operation.position,
        operation.item_id,
        operation.tile_placement_index,
        canonical_json(_operation_expected_json(operation)),
        canonical_json(_operation_replacement_json(operation)),
    )


def _semantic_signature_from_finding(finding: Mapping[str, Any]) -> tuple[Any, ...]:
    position = finding.get("position")
    details = finding.get("details")
    if not isinstance(position, list) or len(position) != 3 or not isinstance(details, Mapping):
        raise BoundedPatchError("semantic diff finding lacks position/details")
    before_stack = details.get("beforeStackIndex")
    after_stack = details.get("afterStackIndex")
    if before_stack != after_stack:
        raise BoundedPatchError("semantic diff aligned stack index changed")
    return (
        finding.get("kind"),
        tuple(position),
        details.get("itemId"),
        before_stack,
        canonical_json(finding.get("before")),
        canonical_json(finding.get("after")),
    )


def _validate_semantic_diff(plan: PatchPlan, report: Mapping[str, Any]) -> None:
    if report.get("format") != "canary-otbm-semantic-diff-v1" or report.get("ok") is not True:
        raise BoundedPatchError("semantic diff did not return a successful v1 report")
    scope = report.get("scope")
    summary = report.get("summary")
    findings = report.get("findings")
    if not isinstance(scope, Mapping) or not isinstance(summary, Mapping) or not isinstance(findings, list):
        raise BoundedPatchError("semantic diff report is incomplete")
    if scope.get("type") != "bounded-region" or scope.get("from") != list(plan.region.lower) or scope.get("to") != list(plan.region.upper):
        raise BoundedPatchError("semantic diff scope does not match the patch region")
    finding_summary = summary.get("findings")
    if not isinstance(finding_summary, Mapping):
        raise BoundedPatchError("semantic diff finding summary is missing")
    if finding_summary.get("truncated") or finding_summary.get("total") != len(plan.operations):
        raise BoundedPatchError("semantic diff finding count does not exactly match planned operations")
    if summary.get("beforeTiles") != summary.get("afterTiles") or summary.get("beforePlacements") != summary.get("afterPlacements"):
        raise BoundedPatchError("semantic diff observed a tile or placement count change")
    expected = Counter(_semantic_signature_from_operation(operation) for operation in plan.operations)
    actual = Counter(_semantic_signature_from_finding(finding) for finding in findings if isinstance(finding, Mapping))
    if actual != expected:
        raise BoundedPatchError("semantic diff findings do not exactly match the planned mechanic changes")


def _render_request(plan: PatchPlan, source: Path, output: Path) -> dict[str, Any]:
    return {
        "format": "canary-otbm-bounded-patch-render-request-v1",
        "execute": False,
        "renderer": "tools/ai-agent/otbm_semantic_diff_tool.py render",
        "beforeMap": source.name,
        "afterMap": output.name,
        "region": {"from": list(plan.region.lower), "to": list(plan.region.upper)},
        "requiredExternalInput": "real client assets root",
        "policy": {
            "realAssetsOnly": True,
            "aiGeneratedImagery": False,
            "visualEvidenceIsSupplemental": True,
        },
    }


def apply_bounded_patch(
    *,
    plan: PatchPlan,
    source_path: Path,
    scanner_path: Path,
    artifact_root: Path,
    output_path: Path,
    evidence_directory: Path,
    result_path: Path,
    timeout_seconds: int = 3600,
) -> dict[str, Any]:
    if len(plan.operations) > MAX_OPERATIONS:
        raise BoundedPatchError(f"plan contains {len(plan.operations)} operations; limit is {MAX_OPERATIONS}")
    root = _prepare_artifact_root(artifact_root)
    source = _resolve_existing_regular(source_path, "source map")
    scanner = _resolve_existing_regular(scanner_path, "native scanner", executable=True)
    output = _new_confined_path(root, output_path, "patched output")
    evidence = _new_confined_path(root, evidence_directory, "evidence directory")
    result_destination = _new_confined_path(root, result_path, "result report")
    if source == output:
        raise BoundedPatchError("source and output paths must differ")
    if evidence == output or evidence in output.parents or output in evidence.parents:
        raise BoundedPatchError("patched output and evidence directory must be separate")
    if result_destination == output or evidence == result_destination or evidence in result_destination.parents:
        raise BoundedPatchError("result report must be separate from output and evidence directory")

    workspace = Path(tempfile.mkdtemp(prefix=".otbm-bounded-patch-", dir=root))
    published_output = False
    published_evidence = False
    try:
        before_native = workspace / "before-anchors.native.json"
        before_public = workspace / "before-anchors.json"
        before_anchors = _scan_anchors(
            source=source,
            scanner=scanner,
            native_output=before_native,
            public_output=before_public,
            timeout_seconds=timeout_seconds,
        )
        _validate_plan_source(plan, source, before_anchors)
        resolved_operations = _resolve_operations(plan=plan, source=source, anchor_document=before_anchors)

        temporary_output = workspace / output.name
        _copy_and_patch(source, temporary_output, resolved_operations)
        changed_offsets = _compare_outside_spans(source, temporary_output, resolved_operations)

        after_native = workspace / "after-anchors.native.json"
        after_public = workspace / "after-anchors.json"
        after_anchors = _scan_anchors(
            source=temporary_output,
            scanner=scanner,
            native_output=after_native,
            public_output=after_public,
            timeout_seconds=timeout_seconds,
        )
        _verify_after_anchors(plan, resolved_operations, after_anchors)

        after_scan = workspace / "after-full-scan.json"
        completed = _run_scanner(
            scanner,
            [str(temporary_output), str(after_scan)],
            timeout_seconds=timeout_seconds,
        )
        if not after_scan.is_file() or "tiles=" not in completed.stdout:
            raise BoundedPatchError("full post-patch scanner reparse did not produce its legacy evidence")

        before_index = workspace / "before.widx"
        before_manifest = workspace / "before.widx.json"
        after_index = workspace / "after.widx"
        after_manifest = workspace / "after.widx.json"
        build_world_index(
            map_path=source,
            scanner=scanner,
            output=before_index,
            manifest_output=before_manifest,
            timeout_seconds=timeout_seconds,
        )
        build_world_index(
            map_path=temporary_output,
            scanner=scanner,
            output=after_index,
            manifest_output=after_manifest,
            timeout_seconds=timeout_seconds,
        )
        semantic_report = analyze_index_paths(
            artifact_root=root,
            before_index_path=before_index,
            before_manifest_path=before_manifest,
            after_index_path=after_index,
            after_manifest_path=after_manifest,
            after_map_path=temporary_output,
            lower=plan.region.lower,
            upper=plan.region.upper,
            sample_limit=len(plan.operations),
        )
        _validate_semantic_diff(plan, semantic_report)
        semantic_path = workspace / "semantic-diff.json"
        write_report(semantic_path, semantic_report, artifact_root=root)

        source_hash_after = sha256_file(source)
        if source_hash_after != plan.source.sha256 or source.stat().st_size != plan.source.size:
            raise BoundedPatchError("source map changed during patch validation")
        output_hash = sha256_file(temporary_output)
        plan_hash = hashlib.sha256(canonical_json({
            "format": PLAN_FORMAT,
            "source": {
                "fileName": plan.source.file_name,
                "sha256": plan.source.sha256,
                "size": plan.source.size,
                "otbmVersion": plan.source.otbm_version,
                "itemsMajor": plan.source.items_major,
                "itemsMinor": plan.source.items_minor,
            },
            "region": {"from": list(plan.region.lower), "to": list(plan.region.upper)},
            "operations": [
                {
                    "id": operation.operation_id,
                    "kind": operation.kind,
                    "position": list(operation.position),
                    "tilePlacementIndex": operation.tile_placement_index,
                    "itemId": operation.item_id,
                    "itemDepth": operation.item_depth,
                    "expected": _operation_expected_json(operation),
                    "replacement": _operation_replacement_json(operation),
                }
                for operation in plan.operations
            ],
        }).encode("utf-8")).hexdigest()

        evidence_files = [
            path
            for path in sorted(workspace.iterdir(), key=lambda candidate: candidate.name)
            if path != temporary_output
        ]
        evidence_manifest = {
            "format": "canary-otbm-bounded-patch-evidence-v1",
            "files": [
                {
                    "path": path.name,
                    "size": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
                for path in evidence_files
                if path.is_file()
            ],
        }
        evidence_manifest_path = workspace / "evidence-manifest.json"
        _write_json(evidence_manifest_path, evidence_manifest)

        result = {
            "format": RESULT_FORMAT,
            "ok": True,
            "plan": {"format": PLAN_FORMAT, "sha256": plan_hash},
            "source": {
                "path": source.name,
                "size": plan.source.size,
                "sha256": plan.source.sha256,
                "unchanged": True,
            },
            "output": {
                "path": _relative(root, output),
                "size": temporary_output.stat().st_size,
                "sha256": output_hash,
                "atomicCopyOnly": True,
            },
            "region": {"from": list(plan.region.lower), "to": list(plan.region.upper)},
            "operations": resolved_operations,
            "proof": {
                "fileLengthPreserved": temporary_output.stat().st_size == plan.source.size,
                "outsideScannerSpansEqual": True,
                "changedPhysicalOffsets": changed_offsets,
                "fullScannerReparse": True,
                "worldIndexBeforeAfterBuilt": True,
                "boundedSemanticDiffExact": True,
            },
            "evidence": {
                "directory": _relative(root, evidence),
                "manifest": f"{_relative(root, evidence)}/evidence-manifest.json",
                "semanticDiff": f"{_relative(root, evidence)}/semantic-diff.json",
            },
            "renderRequest": _render_request(plan, source, output),
            "rollback": {
                "action": "delete-patched-copy",
                "path": _relative(root, output),
                "sourceRetained": source.name,
                "sourceSha256": plan.source.sha256,
            },
            "policy": {
                "sourceModifiedInPlace": False,
                "attributesInsertedOrRemoved": False,
                "itemsOrTilesInsertedOrRemoved": False,
                "newOtbmParserCreated": False,
                "existingNativeScannerReused": True,
                "existingWorldIndexReused": True,
                "existingSemanticDiffReused": True,
                "aiGeneratedImagery": False,
            },
        }

        os.link(temporary_output, output)
        published_output = True
        temporary_output.unlink()
        _fsync_directory(output.parent)
        os.rename(workspace, evidence)
        published_evidence = True
        _fsync_directory(evidence.parent)
        _write_json(result_destination, result)
        return result
    except (WorldIndexError, SemanticDiffError) as exc:
        raise BoundedPatchError(str(exc)) from exc
    except Exception:
        raise
    finally:
        if workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)
        if not result_destination.exists():
            if published_output:
                output.unlink(missing_ok=True)
            if published_evidence:
                shutil.rmtree(evidence, ignore_errors=True)
