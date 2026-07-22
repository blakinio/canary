from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from otbm_release_provenance import ReleaseProvenanceError, build_release_provenance_report, load_bom


def _input(path: Path, label: str) -> Path:
    source = path.expanduser().resolve()
    if path.is_symlink() or not source.is_file():
        raise ReleaseProvenanceError(f"{label} must be an existing non-symlink regular file: {path}")
    return source


def _write(path: Path, payload: dict, *, overwrite: bool, inputs: list[Path]) -> None:
    target = path.expanduser().resolve()
    if path.is_symlink() or target.is_symlink():
        raise ReleaseProvenanceError(f"output must not be a symlink: {path}")
    for source in inputs:
        if source == target or (target.exists() and os.path.samefile(source, target)):
            raise ReleaseProvenanceError(f"output collides with input: {source}")
    if target.exists() and not target.is_file():
        raise ReleaseProvenanceError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise ReleaseProvenanceError(f"output already exists: {target}; pass --overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if not overwrite:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        return
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare exact OTBM release BOMs and report dependency-scoped freshness.")
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        current_path = _input(args.current, "current BOM")
        previous_path = _input(args.previous, "previous BOM") if args.previous else None
        current = load_bom(current_path)
        previous = load_bom(previous_path) if previous_path else None
        report = build_release_provenance_report(current, previous)
        inputs = [current_path] + ([previous_path] if previous_path else [])
        _write(args.output, report, overwrite=args.overwrite, inputs=inputs)
    except (ReleaseProvenanceError, FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
