from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from health_check import HealthCheckResult
import release_manager
from release_manager import (
    ReleaseAlreadyExistsError,
    ReleaseNotFoundError,
    current_active_release_id,
    deploy,
    rollback,
    stage_release,
    switch_active,
)


def _healthy(_release_dir: Path) -> HealthCheckResult:
    return HealthCheckResult(healthy=True, detail="ok")


def _unhealthy(_release_dir: Path) -> HealthCheckResult:
    return HealthCheckResult(healthy=False, detail="simulated failure")


class ReleaseManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "deploy-root"
        self.root.mkdir()
        self.source = Path(self._tmp.name) / "source-v1"
        self.source.mkdir()
        (self.source / "npc").mkdir()
        (self.source / "npc" / "keeper.lua").write_text("return npc", encoding="utf-8")

    def _make_source(self, name: str, content: str = "return npc") -> Path:
        source = Path(self._tmp.name) / name
        source.mkdir()
        (source / "file.lua").write_text(content, encoding="utf-8")
        return source


class StageReleaseTests(ReleaseManagerTestCase):
    def test_stage_release_materializes_all_files_atomically(self) -> None:
        release_dir = stage_release(self.source, self.root, "rel-1")
        self.assertTrue((release_dir / "npc" / "keeper.lua").is_file())
        self.assertEqual((release_dir / "npc" / "keeper.lua").read_text(encoding="utf-8"), "return npc")
        # No leftover temp directories.
        leftovers = list((self.root / "releases").glob(".tmp-*"))
        self.assertEqual(leftovers, [])

    def test_staging_same_release_id_twice_fails(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        with self.assertRaises(ReleaseAlreadyExistsError):
            stage_release(self.source, self.root, "rel-1")

    def test_staging_failure_leaves_no_partial_release_visible(self) -> None:
        final_dir = self.root / "releases" / "rel-1"
        with mock.patch("release_manager.shutil.copy2", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                stage_release(self.source, self.root, "rel-1")
        self.assertFalse(final_dir.exists(), "a failed staging attempt must not leave a partial release at its final path")
        leftovers = list((self.root / "releases").glob(".tmp-*"))
        self.assertEqual(leftovers, [], "temp staging directory must be cleaned up on failure")

    def test_dry_run_stage_does_not_touch_filesystem(self) -> None:
        before = set(self.root.rglob("*"))
        release_dir = stage_release(self.source, self.root, "rel-1", dry_run=True)
        after = set(self.root.rglob("*"))
        self.assertEqual(before, after)
        self.assertFalse(release_dir.exists())

    def test_stage_rejects_source_path_escape(self) -> None:
        outside = Path(self._tmp.name) / "outside-secret"
        outside.mkdir()
        (outside / "secret.txt").write_text("nope", encoding="utf-8")
        escape_link = self.source / "escape"
        escape_link.symlink_to(outside, target_is_directory=True)

        with self.assertRaises(Exception):
            stage_release(self.source, self.root, "rel-escape")


class SwitchActiveTests(ReleaseManagerTestCase):
    def test_first_switch_has_no_previous_release(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        previous = switch_active(self.root, "rel-1")
        self.assertIsNone(previous)
        self.assertEqual(current_active_release_id(self.root), "rel-1")

    def test_switch_updates_previous_symlink(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        switch_active(self.root, "rel-1")
        stage_release(self._make_source("source-v2"), self.root, "rel-2")
        previous = switch_active(self.root, "rel-2")

        self.assertEqual(previous, "rel-1")
        self.assertEqual(current_active_release_id(self.root), "rel-2")
        self.assertTrue((self.root / "active" / "file.lua").exists(), "active must now serve rel-2's content")
        self.assertEqual(Path(os.readlink(self.root / "previous")).name, "rel-1")

        # rel-1 content is untouched and still fully present (retention).
        self.assertTrue((self.root / "releases" / "rel-1" / "npc" / "keeper.lua").is_file())

    def test_switch_to_unstaged_release_fails(self) -> None:
        with self.assertRaises(ReleaseNotFoundError):
            switch_active(self.root, "does-not-exist")

    def test_switch_never_partially_updates_active_on_failure(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        switch_active(self.root, "rel-1")

        with mock.patch("release_manager._atomic_symlink", side_effect=OSError("simulated failure mid-switch")):
            with self.assertRaises(OSError):
                switch_active(self.root, "rel-1")

        # active must still point at whatever it pointed at before the failed attempt.
        self.assertEqual(current_active_release_id(self.root), "rel-1")

    def test_dry_run_switch_does_not_touch_symlinks(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        switch_active(self.root, "rel-1", dry_run=True)
        self.assertIsNone(current_active_release_id(self.root))


class RollbackTests(ReleaseManagerTestCase):
    def test_rollback_restores_previous_release(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        switch_active(self.root, "rel-1")
        stage_release(self._make_source("source-v2"), self.root, "rel-2")
        switch_active(self.root, "rel-2")

        changed = rollback(self.root, "rel-1")
        self.assertTrue(changed)
        self.assertEqual(current_active_release_id(self.root), "rel-1")

    def test_rollback_is_idempotent(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        switch_active(self.root, "rel-1")
        stage_release(self._make_source("source-v2"), self.root, "rel-2")
        switch_active(self.root, "rel-2")

        first = rollback(self.root, "rel-1")
        second = rollback(self.root, "rel-1")
        self.assertTrue(first)
        self.assertFalse(second, "rolling back twice to the same target must be a reported no-op, not an error")
        self.assertEqual(current_active_release_id(self.root), "rel-1")

    def test_rollback_to_missing_release_fails(self) -> None:
        stage_release(self.source, self.root, "rel-1")
        switch_active(self.root, "rel-1")
        with self.assertRaises(ReleaseNotFoundError):
            rollback(self.root, "never-staged")


class DeployOrchestrationTests(ReleaseManagerTestCase):
    def test_successful_deploy_writes_manifest_with_checksums(self) -> None:
        manifest = deploy(self.source, self.root, "rel-1", _healthy, source_description="unit test")
        self.assertEqual(manifest.outcome, "deployed")
        self.assertEqual(manifest.switch_status, "switched")
        self.assertEqual(manifest.health_check_status, "healthy")
        self.assertEqual(manifest.rollback_status, "not-needed")
        self.assertEqual(len(manifest.files), 1)
        self.assertTrue(all(entry.sha256 for entry in manifest.files))
        self.assertEqual(current_active_release_id(self.root), "rel-1")

    def test_failed_health_check_triggers_rollback(self) -> None:
        deploy(self.source, self.root, "rel-1", _healthy)
        manifest = deploy(self._make_source("source-v2"), self.root, "rel-2", _unhealthy)

        self.assertEqual(manifest.outcome, "rolled-back")
        self.assertEqual(manifest.health_check_status, "unhealthy")
        self.assertEqual(manifest.rollback_status, "rolled-back")
        self.assertEqual(current_active_release_id(self.root), "rel-1", "a failed health check must restore the previous release")

    def test_failed_health_check_with_no_previous_release_cannot_roll_back(self) -> None:
        manifest = deploy(self.source, self.root, "rel-1", _unhealthy)
        self.assertEqual(manifest.outcome, "failed-health-check-no-rollback-target")
        self.assertEqual(manifest.rollback_status, "not-possible-no-previous-release")
        # The unhealthy release is still active - there was nothing to roll back to,
        # this is a visible failure state, not silently "fixed".
        self.assertEqual(current_active_release_id(self.root), "rel-1")

    def test_staging_failure_short_circuits_before_any_switch(self) -> None:
        with mock.patch("release_manager.shutil.copy2", side_effect=OSError("disk full")):
            manifest = deploy(self.source, self.root, "rel-1", _healthy)

        self.assertEqual(manifest.outcome, "failed-staging")
        self.assertEqual(manifest.switch_status, "skipped")
        self.assertIsNone(current_active_release_id(self.root))

    def test_switch_failure_short_circuits_before_health_check(self) -> None:
        with mock.patch("release_manager._atomic_symlink", side_effect=OSError("simulated switch failure")):
            manifest = deploy(self.source, self.root, "rel-1", _healthy)

        self.assertEqual(manifest.outcome, "failed-switch")
        self.assertEqual(manifest.health_check_status, "skipped")
        self.assertIsNone(current_active_release_id(self.root))

    def test_dry_run_deploy_touches_nothing(self) -> None:
        before = set(self.root.rglob("*"))
        manifest = deploy(self.source, self.root, "rel-1", _healthy, dry_run=True)
        after = set(self.root.rglob("*"))

        self.assertEqual(before, after)
        self.assertEqual(manifest.outcome, "dry-run-ok")
        self.assertIsNone(current_active_release_id(self.root))

    def test_redeploying_same_release_id_fails_cleanly(self) -> None:
        deploy(self.source, self.root, "rel-1", _healthy)
        manifest = deploy(self.source, self.root, "rel-1", _healthy)
        self.assertEqual(manifest.outcome, "failed-staging")


if __name__ == "__main__":
    unittest.main()
