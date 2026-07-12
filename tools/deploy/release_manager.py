"""Atomic release/deployment engine.

Layout under a configured ``releases_root``::

    releases_root/
      releases/
        <release_id>/          # fully-populated release, only ever appears atomically
      active   -> releases/<release_id>   # symlink, atomically repointed
      previous -> releases/<old_release_id>  # symlink, updated just before active moves

Two separate atomic primitives do the real work:

* **staging** a release builds its full content under a hidden temp
  directory inside ``releases_root/releases/`` and only then
  ``os.replace()``s it into its final ``<release_id>`` name - an atomic
  rename on the same filesystem, so the final path either doesn't exist yet
  or is fully populated. There is no state in between.
* **switching** which release is active swaps the ``active`` symlink by
  creating a new symlink under a temp name and ``os.replace()``-ing it onto
  ``active`` - again a single atomic rename, this time of a directory entry
  that happens to be a symlink.

Nothing here ever copies into ``active`` directly, and nothing ever deletes
a previous release: retention is "don't delete", not a separate mechanism.
"""

from __future__ import annotations

import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from health_check import HealthChecker, HealthCheckResult
from manifest import DeploymentManifest, build_file_entries
from path_policy import PathEscapesRootError, resolve_within_root


class ReleaseError(RuntimeError):
    pass


class ReleaseAlreadyExistsError(ReleaseError):
    pass


class ReleaseNotFoundError(ReleaseError):
    pass


def _atomic_symlink(target: str, link_path: Path) -> None:
    tmp_link = link_path.with_name(f"{link_path.name}.tmp-{uuid.uuid4().hex[:8]}")
    if tmp_link.is_symlink() or tmp_link.exists():
        tmp_link.unlink()
    tmp_link.symlink_to(target, target_is_directory=True)
    os.replace(tmp_link, link_path)


def _collect_source_files(source_resolved: Path) -> list[Path]:
    """List every regular file under ``source_resolved``, rejecting any symlink outright.

    ``Path.rglob`` lists a symlinked directory as a single entry but does not
    recurse into it, so relying on "does each *file* resolve back inside the
    root" alone would silently skip a symlinked directory's contents instead
    of catching the escape attempt. Source content for deployment is plain
    generated/reviewed files - reject any symlink, anywhere in the tree,
    rather than trying to tell "safe" ones from unsafe ones.
    """
    files: list[Path] = []
    for entry in sorted(source_resolved.rglob("*")):
        if entry.is_symlink():
            raise PathEscapesRootError(f"source content must not contain symlinks: {entry}")
        if entry.is_file():
            resolve_within_root(entry, source_resolved)
            files.append(entry)
    return files


def current_active_release_id(releases_root: str | Path, *, active_name: str = "active") -> str | None:
    active_path = Path(releases_root) / active_name
    if not active_path.is_symlink():
        return None
    target = os.readlink(active_path)
    return Path(target).name


def stage_release(source_dir: str | Path, releases_root: str | Path, release_id: str, *, dry_run: bool = False) -> Path:
    """Build ``release_id`` under ``releases_root`` from the contents of ``source_dir``.

    Every source file path is validated against ``source_dir``'s own
    boundary before being copied, so a maliciously or accidentally crafted
    entry can't smuggle a path outside of it. The release only becomes
    visible at its final path in a single atomic rename once every file has
    been copied successfully.
    """
    releases_root_resolved = Path(releases_root).resolve(strict=True)
    source_resolved = Path(source_dir).resolve(strict=True)
    releases_dir = releases_root_resolved / "releases"
    final_dir = releases_dir / release_id

    source_files = _collect_source_files(source_resolved)

    if dry_run:
        return final_dir

    if final_dir.exists():
        raise ReleaseAlreadyExistsError(f"release already exists: {release_id}")

    releases_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = releases_dir / f".tmp-{release_id}-{uuid.uuid4().hex[:8]}"
    tmp_dir.mkdir(parents=True, exist_ok=False)
    try:
        for src_path in source_files:
            relative = src_path.relative_to(source_resolved)
            dest_path = tmp_dir / relative
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)

        if final_dir.exists():
            raise ReleaseAlreadyExistsError(f"release already exists: {release_id}")
        os.replace(tmp_dir, final_dir)
    except BaseException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise

    return final_dir


def switch_active(releases_root: str | Path, release_id: str, *, active_name: str = "active", previous_name: str = "previous", dry_run: bool = False) -> str | None:
    """Atomically point ``active_name`` at ``release_id``. Returns the release id that was active before (or None)."""
    releases_root_resolved = Path(releases_root).resolve(strict=True)
    previous_release_id = current_active_release_id(releases_root_resolved, active_name=active_name)

    if dry_run:
        # A dry run never actually staged anything on disk, so there is
        # nothing to check for existence - report what *would* happen only.
        return previous_release_id

    release_dir = releases_root_resolved / "releases" / release_id
    if not release_dir.is_dir():
        raise ReleaseNotFoundError(f"release not staged: {release_id}")

    active_path = releases_root_resolved / active_name
    if active_path.is_symlink() or active_path.exists():
        current_target = os.readlink(active_path)
        _atomic_symlink(current_target, releases_root_resolved / previous_name)

    _atomic_symlink(str(Path("releases") / release_id), active_path)
    return previous_release_id


def rollback(releases_root: str | Path, target_release_id: str, *, active_name: str = "active", dry_run: bool = False) -> bool:
    """Idempotently point ``active_name`` back at ``target_release_id``.

    Returns whether a change was actually made - calling this again after a
    successful rollback (or when nothing needs rolling back) is a safe,
    reported no-op rather than an error.
    """
    releases_root_resolved = Path(releases_root).resolve(strict=True)
    release_dir = releases_root_resolved / "releases" / target_release_id
    if not release_dir.is_dir():
        raise ReleaseNotFoundError(f"cannot roll back to missing release: {target_release_id}")

    if current_active_release_id(releases_root_resolved, active_name=active_name) == target_release_id:
        return False

    if dry_run:
        return True

    _atomic_symlink(str(Path("releases") / target_release_id), releases_root_resolved / active_name)
    return True


def deploy(
    source_dir: str | Path,
    releases_root: str | Path,
    release_id: str,
    health_checker: HealthChecker,
    *,
    source_description: str = "",
    dry_run: bool = False,
) -> DeploymentManifest:
    """Stage, switch, health-check, and (on failure) roll back a release. Always returns a manifest."""
    manifest = DeploymentManifest(
        schema_version="1.0",
        release_id=release_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        source_description=source_description,
        dry_run=dry_run,
    )

    try:
        release_dir = stage_release(source_dir, releases_root, release_id, dry_run=dry_run)
    except Exception as exc:
        manifest.outcome = "failed-staging"
        manifest.switch_status = "skipped"
        manifest.health_check_status = "skipped"
        manifest.rollback_status = "not-needed"
        manifest.health_check_detail = str(exc)
        return manifest

    if not dry_run:
        manifest.files = build_file_entries(release_dir)

    try:
        previous_release_id = switch_active(releases_root, release_id, dry_run=dry_run)
        manifest.previous_release_id = previous_release_id
        manifest.switch_status = "dry-run" if dry_run else "switched"
    except Exception as exc:
        manifest.outcome = "failed-switch"
        manifest.switch_status = "failed"
        manifest.health_check_status = "skipped"
        manifest.rollback_status = "not-needed"
        manifest.health_check_detail = str(exc)
        return manifest

    if dry_run:
        manifest.health_check_status = "skipped-dry-run"
        manifest.rollback_status = "not-needed"
        manifest.outcome = "dry-run-ok"
        return manifest

    result: HealthCheckResult = health_checker(release_dir)
    manifest.health_check_detail = result.detail
    if result.healthy:
        manifest.health_check_status = "healthy"
        manifest.rollback_status = "not-needed"
        manifest.outcome = "deployed"
        return manifest

    manifest.health_check_status = "unhealthy"
    if previous_release_id is None:
        manifest.rollback_status = "not-possible-no-previous-release"
        manifest.outcome = "failed-health-check-no-rollback-target"
        return manifest

    try:
        rolled_back = rollback(releases_root, previous_release_id)
        manifest.rollback_status = "rolled-back" if rolled_back else "already-active"
        manifest.outcome = "rolled-back"
    except Exception as exc:
        manifest.rollback_status = f"rollback-failed: {exc}"
        manifest.outcome = "failed-health-check-rollback-failed"

    return manifest
