#!/usr/bin/env python3
"""Materialize a manually approved promotion handoff into a deployment overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath


class OverlayMaterializationError(ValueError):
    pass


def _safe_relative(value: str, *, label: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise OverlayMaterializationError(f"unsafe {label}: {value}")
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_file(generated_root: Path, relative: PurePosixPath) -> Path:
    cursor = generated_root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise OverlayMaterializationError(f"preview source must not contain symlinks: {relative.as_posix()}")

    resolved = cursor.resolve(strict=True)
    try:
        resolved.relative_to(generated_root)
    except ValueError as exc:
        raise OverlayMaterializationError(f"preview source escapes generated root: {relative.as_posix()}") from exc
    if not resolved.is_file():
        raise OverlayMaterializationError(f"preview source is not a regular file: {relative.as_posix()}")
    return resolved


def _overlay_relative(target_datapack: PurePosixPath, target_path: PurePosixPath) -> PurePosixPath:
    prefix = target_datapack.parts
    if target_path.parts[: len(prefix)] != prefix:
        raise OverlayMaterializationError(
            f"target path '{target_path.as_posix()}' is outside target datapack '{target_datapack.as_posix()}'"
        )
    remainder = target_path.parts[len(prefix) :]
    if not remainder:
        raise OverlayMaterializationError(f"target path points at datapack root: {target_path.as_posix()}")
    return PurePosixPath(*remainder)


def validate_handoff(handoff: dict, *, confirm_reviewed: bool) -> tuple[PurePosixPath, list[dict]]:
    if not confirm_reviewed:
        raise OverlayMaterializationError("manual review confirmation is required")
    if handoff.get("handoffStatus") != "ready-for-manual-review":
        raise OverlayMaterializationError(f"handoff is not ready for review: {handoff.get('handoffStatus')}")
    if handoff.get("automaticApplyAllowed") is not False:
        raise OverlayMaterializationError("handoff must explicitly forbid automatic apply")
    if handoff.get("manualApprovalRequired") is not True:
        raise OverlayMaterializationError("handoff must explicitly require manual approval")
    if handoff.get("blockers"):
        raise OverlayMaterializationError("handoff still contains blockers")

    target_datapack = _safe_relative(str(handoff.get("targetDatapack", "")), label="target datapack")
    files = handoff.get("files")
    if not isinstance(files, list) or not files:
        raise OverlayMaterializationError("handoff contains no files")
    return target_datapack, files


def materialize(
    handoff: dict,
    generated_root: Path,
    output_dir: Path,
    *,
    confirm_reviewed: bool,
) -> dict:
    target_datapack, files = validate_handoff(handoff, confirm_reviewed=confirm_reviewed)
    generated_root = generated_root.resolve(strict=True)
    if not generated_root.is_dir():
        raise OverlayMaterializationError(f"generated root is not a directory: {generated_root}")

    output_dir = output_dir.absolute()
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"overlay output already exists: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    mappings: list[dict] = []
    seen_targets: set[str] = set()
    for item in files:
        if not isinstance(item, dict):
            raise OverlayMaterializationError("handoff file entry must be an object")
        preview = _safe_relative(str(item.get("previewPath", "")), label="preview path")
        target = _safe_relative(str(item.get("targetPath", "")), label="target path")
        relative = _overlay_relative(target_datapack, target)
        relative_text = relative.as_posix()
        if relative_text in seen_targets:
            raise OverlayMaterializationError(f"duplicate overlay target: {relative_text}")
        seen_targets.add(relative_text)

        expected = str(item.get("sha256", "")).lower()
        if len(expected) != 64 or any(character not in "0123456789abcdef" for character in expected):
            raise OverlayMaterializationError(f"invalid SHA-256 for {preview.as_posix()}")
        source = _source_file(generated_root, preview)
        actual = _sha256(source)
        if actual != expected:
            raise OverlayMaterializationError(f"checksum mismatch for {preview.as_posix()}")
        if item.get("operation") != "manual-copy-after-review":
            raise OverlayMaterializationError(f"unexpected handoff operation for {preview.as_posix()}")

        mappings.append(
            {
                "previewPath": preview.as_posix(),
                "overlayPath": relative_text,
                "targetPath": target.as_posix(),
                "sha256": actual,
                "source": source,
            }
        )

    mappings.sort(key=lambda item: item["overlayPath"])
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=output_dir.parent))
    try:
        for mapping in mappings:
            destination = temporary / mapping["overlayPath"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(mapping["source"], destination)
            if _sha256(destination) != mapping["sha256"]:
                raise OverlayMaterializationError(f"copied overlay checksum mismatch: {mapping['overlayPath']}")
        os.replace(temporary, output_dir)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    return {
        "schemaVersion": "1.0",
        "taskId": handoff.get("taskId"),
        "targetDatapack": target_datapack.as_posix(),
        "manualReviewConfirmed": True,
        "fileCount": len(mappings),
        "files": [
            {
                "previewPath": item["previewPath"],
                "overlayPath": item["overlayPath"],
                "targetPath": item["targetPath"],
                "sha256": item["sha256"],
            }
            for item in mappings
        ],
    }


def _write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff", required=True, type=Path)
    parser.add_argument("--generated-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manifest-output", required=True, type=Path)
    parser.add_argument("--confirm-reviewed", action="store_true")
    args = parser.parse_args()

    try:
        handoff = json.loads(args.handoff.read_text(encoding="utf-8"))
        result = materialize(
            handoff,
            args.generated_root,
            args.output_dir,
            confirm_reviewed=args.confirm_reviewed,
        )
        _write_json_atomic(args.manifest_output, result)
    except Exception as exc:
        print(f"overlay materialization failed: {exc}", file=os.sys.stderr)
        return 1

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
