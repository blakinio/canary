from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

from otbm_renderer import render_region

from otbm_semantic_diff_types import Position, SemanticDiffError, normalize_bounds, sha256_path

RENDER_MANIFEST_FORMAT = "canary-otbm-semantic-diff-render-v1"
MAX_RENDER_POSITIONS = 4096


def _confined(root: Path, path: Path, label: str, *, must_exist: bool) -> Path:
    root = root.expanduser().resolve()
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise SemanticDiffError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=must_exist)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise SemanticDiffError(f"{label} escapes artifact root {root}: {resolved}") from exc
    return resolved


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _expanded(lower: Position, upper: Position, padding: int, floor: int) -> tuple[Position, Position]:
    return (
        max(0, lower[0] - padding),
        max(0, lower[1] - padding),
        floor,
    ), (
        min(0xFFFF, upper[0] + padding),
        min(0xFFFF, upper[1] + padding),
        floor,
    )


def _position_count(bounds: tuple[Position, Position]) -> int:
    lower, upper = bounds
    return (upper[0] - lower[0] + 1) * (upper[1] - lower[1] + 1)


def build_render_manifest(
    *,
    artifact_root: Path,
    before_map_path: Path,
    after_map_path: Path,
    assets_root: Path,
    lower: Position,
    upper: Position,
    output_directory: Path,
    before_expected_sha256: str | None = None,
    after_expected_sha256: str | None = None,
    context_tiles: int = 4,
    execute: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    root = artifact_root.expanduser().resolve()
    before_map = _confined(root, before_map_path, "before map", must_exist=True)
    after_map = _confined(root, after_map_path, "after map", must_exist=True)
    assets = _confined(root, assets_root, "assets root", must_exist=True)
    if not before_map.is_file() or not after_map.is_file():
        raise SemanticDiffError("Render map inputs must be regular files")
    if not assets.is_dir():
        raise SemanticDiffError("Render assets root must be a directory")
    if not isinstance(context_tiles, int) or isinstance(context_tiles, bool) or not 0 <= context_tiles <= 32:
        raise SemanticDiffError("context_tiles must be in 0..32")
    normalized_lower, normalized_upper = normalize_bounds(lower, upper)
    before_hash = sha256_path(before_map)
    after_hash = sha256_path(after_map)
    if before_expected_sha256 is not None and before_hash != before_expected_sha256:
        raise SemanticDiffError("Before map does not match semantic-diff provenance")
    if after_expected_sha256 is not None and after_hash != after_expected_sha256:
        raise SemanticDiffError("After map does not match semantic-diff provenance")

    output = _confined(root, output_directory, "render output directory", must_exist=False)
    if output.exists() and not output.is_dir():
        raise SemanticDiffError("Render output path exists but is not a directory")
    output.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise SemanticDiffError("Render output directory must not be a symlink")

    requests: list[dict[str, Any]] = []
    for floor in range(normalized_lower[2], normalized_upper[2] + 1):
        exact = ((normalized_lower[0], normalized_lower[1], floor), (normalized_upper[0], normalized_upper[1], floor))
        context = _expanded(normalized_lower, normalized_upper, context_tiles, floor)
        for role, map_path, bounds, stem in (
            ("before", before_map, exact, f"before-z{floor}"),
            ("after", after_map, exact, f"after-z{floor}"),
            ("before-context", before_map, context, f"before-context-z{floor}"),
            ("after-context", after_map, context, f"after-context-z{floor}"),
        ):
            if _position_count(bounds) > MAX_RENDER_POSITIONS:
                raise SemanticDiffError(
                    f"Render request {role} floor {floor} contains {_position_count(bounds)} positions; maximum is {MAX_RENDER_POSITIONS}"
                )
            destination = output / f"{stem}.png"
            if destination.is_symlink():
                raise SemanticDiffError(f"Render output must not be a symlink: {destination}")
            if destination.exists() and not overwrite:
                raise SemanticDiffError(f"Render output already exists: {destination}; pass overwrite=True")
            request: dict[str, Any] = {
                "id": f"{role}:z{floor}",
                "role": role,
                "map": _relative(root, map_path),
                "assetsRoot": _relative(root, assets),
                "bounds": {"from": list(bounds[0]), "to": list(bounds[1])},
                "output": _relative(root, destination),
                "renderer": "tools/ai-agent/otbm_renderer.py:render_region",
                "command": [
                    "python",
                    "tools/ai-agent/otbm_render_tool.py",
                    _relative(root, map_path),
                    _relative(root, assets),
                    "--from",
                    ",".join(str(part) for part in bounds[0]),
                    "--to",
                    ",".join(str(part) for part in bounds[1]),
                    "--output",
                    _relative(root, destination),
                    "--padding-tiles",
                    "0",
                    "--max-tiles",
                    str(MAX_RENDER_POSITIONS),
                ],
                "executed": False,
                "report": None,
                "outputSha256": None,
            }
            if execute:
                temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
                if temporary.is_symlink():
                    raise SemanticDiffError(f"Temporary render output must not be a symlink: {temporary}")
                temporary.unlink(missing_ok=True)
                try:
                    report = render_region(
                        map_path,
                        assets,
                        bounds,
                        temporary,
                        padding_tiles=0,
                        max_tiles=MAX_RENDER_POSITIONS,
                    )
                    if not report.get("ok"):
                        raise SemanticDiffError(f"Existing factual renderer reported errors for {request['id']}: {report.get('errors')}")
                    os.replace(temporary, destination)
                except Exception:
                    temporary.unlink(missing_ok=True)
                    raise
                request["executed"] = True
                request["report"] = report
                request["outputSha256"] = sha256_path(destination)
            requests.append(request)

    before_after_hashes = (sha256_path(before_map), sha256_path(after_map))
    if before_after_hashes != (before_hash, after_hash):
        raise SemanticDiffError("A source map changed while factual render evidence was generated")
    return {
        "format": RENDER_MANIFEST_FORMAT,
        "schemaVersion": 1,
        "ok": True,
        "source": {
            "beforeMap": {"path": _relative(root, before_map), "sha256": before_hash, "size": before_map.stat().st_size},
            "afterMap": {"path": _relative(root, after_map), "sha256": after_hash, "size": after_map.stat().st_size},
            "assetsRoot": _relative(root, assets),
        },
        "policy": {
            "existingRendererReused": True,
            "aiImageGenerationUsed": False,
            "mapModified": False,
            "overlayGenerated": False,
            "manifestOnlyWhenNotExecuted": not execute,
            "contextTiles": context_tiles,
        },
        "region": {"from": list(normalized_lower), "to": list(normalized_upper)},
        "requests": requests,
        "diffManifest": {
            "before": [request["id"] for request in requests if request["role"] == "before"],
            "after": [request["id"] for request in requests if request["role"] == "after"],
            "context": [request["id"] for request in requests if request["role"].endswith("context")],
        },
    }
