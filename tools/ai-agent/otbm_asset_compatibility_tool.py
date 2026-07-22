from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from otbm_asset_compatibility import AssetCompatibilityError, build_asset_compatibility_report, prepare_asset_compatibility_context


def _resolved_regular_input(path: Path, label: str) -> Path:
    source = path.expanduser().resolve()
    if path.is_symlink() or not source.is_file():
        raise AssetCompatibilityError(f"{label} must be an existing non-symlink regular file: {path}")
    return source


def _validate_distinct(inputs: list[Path], output: Path) -> None:
    output_resolved = output.expanduser().resolve()
    for source in inputs:
        if source == output_resolved:
            raise AssetCompatibilityError(f"output collides with input: {source}")
        if output.exists() and source.exists() and os.path.samefile(source, output_resolved):
            raise AssetCompatibilityError(f"output aliases input: {source}")


def _write_json(path: Path, payload: dict, *, overwrite: bool) -> None:
    target = path.expanduser().resolve()
    if path.is_symlink() or target.is_symlink():
        raise AssetCompatibilityError(f"output must not be a symlink: {path}")
    if target.exists() and not target.is_file():
        raise AssetCompatibilityError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise AssetCompatibilityError(f"output already exists: {target}; pass --overwrite")
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
    parser = argparse.ArgumentParser(description="Audit OTBM item/appearance/client-asset compatibility using existing canonical indexes.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--world-index", type=Path, required=True)
    parser.add_argument("--world-manifest", type=Path, required=True)
    parser.add_argument("--appearances", type=Path, required=True)
    parser.add_argument("--asset-index", type=Path, required=True)
    parser.add_argument("--baseline-appearances", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        manifest = _resolved_regular_input(args.manifest, "manifest")
        world_index = _resolved_regular_input(args.world_index, "world index")
        world_manifest = _resolved_regular_input(args.world_manifest, "world manifest")
        appearances = _resolved_regular_input(args.appearances, "appearances")
        asset_index = _resolved_regular_input(args.asset_index, "asset index")
        baseline = _resolved_regular_input(args.baseline_appearances, "baseline appearances") if args.baseline_appearances else None
        inputs = [manifest, world_index, world_manifest, appearances, asset_index] + ([baseline] if baseline else [])
        _validate_distinct(inputs, args.output)
        context = prepare_asset_compatibility_context(
            manifest_path=manifest,
            world_index_path=world_index,
            world_manifest_path=world_manifest,
            appearances_path=appearances,
            asset_index_path=asset_index,
            baseline_appearances_path=baseline,
        )
        report = build_asset_compatibility_report(context)
        _write_json(args.output, report, overwrite=args.overwrite)
    except (AssetCompatibilityError, FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
