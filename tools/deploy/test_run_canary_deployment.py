from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_canary_deployment
from health_check import HealthCheckResult
from manifest import DeploymentManifest


class CanaryDeploymentCliTests(unittest.TestCase):
    def _args(self, root: Path, **overrides: object) -> argparse.Namespace:
        repo = root / "repo"
        source = repo / "overlay"
        base = repo / "data-canary"
        binary = repo / "build" / "canary"
        releases = root / "deploy-root"
        workspace = root / "workspace"
        repo.mkdir()
        source.mkdir()
        base.mkdir()
        binary.parent.mkdir(parents=True)
        binary.write_text("binary", encoding="utf-8")
        releases.mkdir()

        values: dict[str, object] = {
            "source": Path("overlay"),
            "base_datapack": Path("data-canary"),
            "releases_root": releases,
            "release_id": "rel-test",
            "binary_path": Path("build/canary"),
            "repo_root": repo,
            "workspace_root": workspace,
            "environment": "staging",
            "confirm_production": False,
            "source_description": "unit test",
            "manifest_output": None,
            "dry_run": False,
            "keep_workspace": False,
            "map_name": "canary",
            "map_download_url": "",
            "map_cache_path": None,
            "db_host": "127.0.0.1",
            "db_port": 3306,
            "db_user": "root",
            "db_password": "root",
            "db_name": "canary_cli_test",
            "login_port": 7471,
            "game_port": 7472,
            "status_port": 7471,
            "startup_timeout_seconds": 30,
            "fail_on_warnings": True,
            "skip_database_init": True,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_production_requires_explicit_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._args(Path(tmp), environment="production")
            with mock.patch.object(run_canary_deployment, "parse_args", return_value=args):
                self.assertEqual(run_canary_deployment.main(), 2)

    def test_assembly_failure_writes_auditable_manifest_without_switching(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self._args(root)
            with (
                mock.patch.object(run_canary_deployment, "parse_args", return_value=args),
                mock.patch.object(
                    run_canary_deployment,
                    "assemble_staging_datapack",
                    side_effect=OSError("synthetic assembly failure"),
                ),
            ):
                self.assertEqual(run_canary_deployment.main(), 1)

            manifest_path = args.releases_root / "manifests" / "rel-test.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["preflightStatus"], "failed-assembly")
            self.assertEqual(manifest["outcome"], "failed-assembly")
            self.assertEqual(manifest["switchStatus"], "skipped")
            self.assertIn("synthetic assembly failure", manifest["preflightDetail"])
            self.assertFalse((args.releases_root / "active").exists())

    def test_failed_real_preflight_writes_manifest_and_does_not_deploy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self._args(root)
            assembled = root / "assembled"
            assembled.mkdir()
            with (
                mock.patch.object(run_canary_deployment, "parse_args", return_value=args),
                mock.patch.object(run_canary_deployment, "assemble_staging_datapack", return_value=assembled),
                mock.patch.object(
                    run_canary_deployment,
                    "run_canary_smoke",
                    return_value=HealthCheckResult(False, "Lua load failed"),
                ),
                mock.patch.object(run_canary_deployment, "deploy") as deploy_mock,
            ):
                self.assertEqual(run_canary_deployment.main(), 1)

            deploy_mock.assert_not_called()
            manifest_path = args.releases_root / "manifests" / "rel-test.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["preflightStatus"], "failed")
            self.assertEqual(manifest["outcome"], "failed-preflight")
            self.assertEqual(manifest["healthCheckStatus"], "skipped")

    def test_success_records_preflight_and_deployment_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = self._args(root)
            assembled = root / "assembled"
            assembled.mkdir()
            deployed = DeploymentManifest(
                schema_version="1.0",
                release_id="rel-test",
                created_at="2026-07-12T00:00:00+00:00",
                source_description="unit test",
                dry_run=False,
            )
            deployed.switch_status = "switched"
            deployed.health_check_status = "healthy"
            deployed.rollback_status = "not-needed"
            deployed.outcome = "deployed"

            with (
                mock.patch.object(run_canary_deployment, "parse_args", return_value=args),
                mock.patch.object(run_canary_deployment, "assemble_staging_datapack", return_value=assembled),
                mock.patch.object(
                    run_canary_deployment,
                    "run_canary_smoke",
                    return_value=HealthCheckResult(True, "preflight Canary runtime smoke passed"),
                ),
                mock.patch.object(run_canary_deployment, "deploy", return_value=deployed),
            ):
                self.assertEqual(run_canary_deployment.main(), 0)

            manifest_path = args.releases_root / "manifests" / "rel-test.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schemaVersion"], "1.1")
            self.assertEqual(manifest["preflightStatus"], "passed")
            self.assertEqual(manifest["healthCheckStatus"], "healthy")
            self.assertEqual(manifest["outcome"], "deployed")


if __name__ == "__main__":
    unittest.main()
