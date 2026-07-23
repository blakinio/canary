from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from otbm_world_assurance_map import (
    WorldAssuranceMapError,
    build_world_assurance_map_plan,
    materialize_world_assurance_map,
    write_manifest,
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json_with_sha(path: Path) -> tuple[dict, str]:
    if path.is_symlink():
        raise WorldAssuranceMapError(f"campaign input must not be a symlink: {path}")
    raw = path.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise WorldAssuranceMapError("campaign input must be a JSON object")
    return payload, _sha256_bytes(raw)


def _confined_output(root: Path, path: Path, label: str) -> Path:
    root = root.expanduser().resolve()
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise WorldAssuranceMapError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorldAssuranceMapError(f"{label} escapes artifact root {root}: {resolved}") from exc
    return resolved


def _same_path(left: Path, right: Path) -> bool:
    return left.expanduser().resolve(strict=False) == right.expanduser().resolve(strict=False)


def _resolve_input(root: Path, path: Path, label: str) -> Path:
    candidate = path.expanduser()
    candidate = candidate if candidate.is_absolute() else root / candidate
    if candidate.is_symlink():
        raise WorldAssuranceMapError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorldAssuranceMapError(f"{label} escapes artifact root {root}: {resolved}") from exc
    return resolved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a factual, evidence-linked OWA certification/coverage visualization manifest and optional render artifacts."
    )
    parser.add_argument("--campaign", type=Path, required=True, help="OWA campaign report JSON")
    parser.add_argument("--artifact-root", type=Path, required=True, help="Root that confines map/assets/render outputs")
    parser.add_argument("--output-dir", type=Path, required=True, help="Render output directory, relative to artifact root unless absolute")
    parser.add_argument("--manifest", type=Path, required=True, help="Output visualization manifest JSON")
    parser.add_argument("--target-id", action="append", default=[], help="Campaign target ID to render; repeatable; defaults to all")
    parser.add_argument("--execute", action="store_true", help="Render the base PNG with the existing factual renderer and write SVG overlays")
    parser.add_argument("--map", dest="map_path", type=Path, help="Exact source OTBM; required with --execute")
    parser.add_argument("--assets", dest="assets_root", type=Path, help="Compatible client assets root; required with --execute")
    parser.add_argument("--overwrite", action="store_true", help="Atomically replace existing generated outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        campaign_path = args.campaign.expanduser().resolve(strict=True)
        raw_artifact_root = args.artifact_root.expanduser()
        if raw_artifact_root.is_symlink():
            raise WorldAssuranceMapError("artifact root must not be a symlink")
        artifact_root = raw_artifact_root.resolve()
        artifact_root.mkdir(parents=True, exist_ok=True)
        manifest_path = _confined_output(artifact_root, args.manifest, "manifest output")
        if _same_path(campaign_path, manifest_path):
            raise WorldAssuranceMapError("manifest output must not collide with campaign input")
        campaign, campaign_file_sha256 = _load_json_with_sha(campaign_path)
        plan = build_world_assurance_map_plan(
            campaign,
            campaign_file_sha256=campaign_file_sha256,
            target_ids=args.target_id,
        )
        report = plan
        if args.execute:
            if args.map_path is None or args.assets_root is None:
                raise WorldAssuranceMapError("--map and --assets are required with --execute")
            map_resolved = _resolve_input(artifact_root, args.map_path, "source map")
            assets_resolved = _resolve_input(artifact_root, args.assets_root, "assets root")
            if _same_path(map_resolved, manifest_path):
                raise WorldAssuranceMapError("manifest output must not collide with source map input")
            try:
                manifest_path.relative_to(assets_resolved)
            except ValueError:
                pass
            else:
                raise WorldAssuranceMapError("manifest output must not be inside the client assets root")
            report = materialize_world_assurance_map(
                plan,
                artifact_root=artifact_root,
                map_path=args.map_path,
                assets_root=args.assets_root,
                output_directory=args.output_dir,
                overwrite=args.overwrite,
            )
        write_manifest(manifest_path, report, overwrite=args.overwrite)
    except (OSError, UnicodeError, json.JSONDecodeError, WorldAssuranceMapError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"format": report["format"], "reportSha256": report["reportSha256"], "targets": len(report["targets"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
