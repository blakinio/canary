#!/usr/bin/env python3
"""Assemble, smoke-test, atomically deploy, and re-test a Canary datapack."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canary_staging import CanarySmokeSettings, assemble_staging_datapack, make_canary_smoke_health_check, run_canary_smoke
from manifest import DeploymentManifest
from release_manager import deploy


def _repo_path(repo_root: Path, value: Path) -> Path:
    return value if value.is_absolute() else repo_root / value


def parse_args() -> argparse.Namespace:
    default_repo_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Reviewed overlay. Relative paths are resolved from --repo-root.")
    parser.add_argument("--base-datapack", required=True, type=Path, help="Complete trusted datapack used as the staging base.")
    parser.add_argument("--releases-root", required=True, type=Path, help="Pre-provisioned atomic deployment root.")
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--binary-path", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--workspace-root", type=Path, help="Temporary assembly root. Defaults to <repo>/build/deployment-staging.")
    parser.add_argument("--environment", choices=["staging", "production"], default="staging")
    parser.add_argument("--confirm-production", action="store_true")
    parser.add_argument("--source-description", default="")
    parser.add_argument("--manifest-output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-workspace", action="store_true")

    parser.add_argument("--map-name", default="canary")
    parser.add_argument("--map-download-url", default="")
    parser.add_argument("--map-cache-path", type=Path)
    parser.add_argument("--db-host", default="127.0.0.1")
    parser.add_argument("--db-port", type=int, default=3306)
    parser.add_argument("--db-user", default="root")
    parser.add_argument("--db-password", default="root")
    parser.add_argument("--db-name", default="canary_deployment_smoke")
    parser.add_argument("--login-port", type=int, default=7471)
    parser.add_argument("--game-port", type=int, default=7472)
    parser.add_argument("--status-port", type=int, default=7471)
    parser.add_argument("--startup-timeout-seconds", type=int, default=420)
    parser.add_argument("--fail-on-warnings", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--skip-database-init", action="store_true")
    return parser.parse_args()


def _new_manifest(args: argparse.Namespace) -> DeploymentManifest:
    return DeploymentManifest(
        schema_version="1.1",
        release_id=args.release_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        source_description=args.source_description,
        dry_run=args.dry_run,
    )


def _write_manifest(args: argparse.Namespace, manifest: DeploymentManifest, releases_root: Path) -> None:
    if args.dry_run:
        return
    output = args.manifest_output or (releases_root / "manifests" / f"{args.release_id}.json")
    manifest.write(output)


def _failed_preflight_manifest(args: argparse.Namespace, status: str, detail: str) -> DeploymentManifest:
    manifest = _new_manifest(args)
    manifest.preflight_status = status
    manifest.preflight_detail = detail
    manifest.switch_status = "skipped"
    manifest.health_check_status = "skipped"
    manifest.rollback_status = "not-needed"
    manifest.outcome = "failed-preflight" if status == "failed" else "failed-assembly"
    return manifest


def main() -> int:
    args = parse_args()

    if args.environment == "production" and not args.confirm_production and not args.dry_run:
        print("refusing production deployment: pass --confirm-production explicitly", file=sys.stderr)
        return 2

    repo_root = args.repo_root.resolve(strict=True)
    source = _repo_path(repo_root, args.source).resolve(strict=True)
    base_datapack = _repo_path(repo_root, args.base_datapack).resolve(strict=True)
    releases_root = args.releases_root.resolve(strict=True)
    binary = _repo_path(repo_root, args.binary_path).resolve(strict=True)
    workspace_root = _repo_path(repo_root, args.workspace_root) if args.workspace_root else (repo_root / "build/deployment-staging")
    workspace_root.mkdir(parents=True, exist_ok=True)

    map_cache_path = None
    if args.map_cache_path:
        map_cache_path = _repo_path(repo_root, args.map_cache_path)

    smoke_settings = CanarySmokeSettings(
        repo_root=repo_root,
        binary_path=binary,
        map_name=args.map_name,
        map_download_url=args.map_download_url,
        map_cache_path=map_cache_path,
        db_host=args.db_host,
        db_port=args.db_port,
        db_user=args.db_user,
        db_password=args.db_password,
        db_name=f"{args.db_name}_preflight",
        login_port=args.login_port,
        game_port=args.game_port,
        status_port=args.status_port,
        startup_timeout_seconds=args.startup_timeout_seconds,
        fail_on_warnings=args.fail_on_warnings,
        skip_database_init=args.skip_database_init,
    )

    workspace = Path(tempfile.mkdtemp(prefix=f"{args.release_id}-", dir=workspace_root))
    try:
        try:
            assembled = assemble_staging_datapack(base_datapack, source, workspace / "datapack")
        except Exception as exc:
            detail = f"staging assembly failed: {type(exc).__name__}: {exc}"
            manifest = _failed_preflight_manifest(args, "failed-assembly", detail)
            _write_manifest(args, manifest, releases_root)
            print(json.dumps(manifest.to_json(), indent=2, ensure_ascii=False))
            return 1

        preflight = run_canary_smoke(assembled, smoke_settings, phase="preflight")
        if not preflight.healthy:
            manifest = _failed_preflight_manifest(args, "failed", preflight.detail)
            _write_manifest(args, manifest, releases_root)
            print(json.dumps(manifest.to_json(), indent=2, ensure_ascii=False))
            return 1

        post_switch_settings = replace(smoke_settings, db_name=f"{args.db_name}_post_switch")
        manifest = deploy(
            assembled,
            releases_root,
            args.release_id,
            make_canary_smoke_health_check(post_switch_settings, phase="post-switch"),
            source_description=args.source_description,
            dry_run=args.dry_run,
        )
        manifest.schema_version = "1.1"
        manifest.preflight_status = "passed"
        manifest.preflight_detail = preflight.detail
        _write_manifest(args, manifest, releases_root)
        print(json.dumps(manifest.to_json(), indent=2, ensure_ascii=False))
        return 0 if manifest.outcome in {"deployed", "dry-run-ok"} else 1
    finally:
        if args.keep_workspace:
            print(f"staging workspace retained at {workspace}")
        else:
            shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
