from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.e2e import cleanup_certification as cc


class CleanupCertificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.otclient = self.root / "otclient"
        self.artifacts = self.root / "artifacts"
        self.proc = self.root / "proc"
        for path in (self.repo, self.otclient, self.artifacts, self.proc):
            path.mkdir(parents=True)
        (self.otclient / "init.lua").write_text("init\n", encoding="utf-8")
        cc.capture_baseline(artifact_dir=self.artifacts, repo_root=self.repo, otclient_root=self.otclient)
        self._write_normal_artifacts("success")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_normal_artifacts(self, gameplay_status: str) -> None:
        (self.artifacts / "result.json").write_text(json.dumps({"status": gameplay_status}) + "\n", encoding="utf-8")
        manifest = {"scenario": {"fixture": {"character": "Paladin 15"}}}
        (self.artifacts / "scenario-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        for name, pid in (("otclient.pid", 101), ("canary.pid", 102), ("xvfb.pid", 103)):
            (self.artifacts / name).write_text(f"{pid}\n", encoding="utf-8")
        (self.artifacts / "otclient-exit-code.txt").write_text("0\n", encoding="utf-8")
        (self.artifacts / "canary.stdout.log").write_text("online\n", encoding="utf-8")
        (self.artifacts / "xvfb.log").write_text("started\n", encoding="utf-8")

    @staticmethod
    def _db_zero(command, query, env):
        return 0, "0", ""

    def _certify(self, *, db_runner=None, lifecycle_exit_code=0):
        return cc.certify(
            artifact_dir=self.artifacts,
            repo_root=self.repo,
            otclient_root=self.otclient,
            lifecycle_pid=90,
            lifecycle_pgid=90,
            lifecycle_exit_code=lifecycle_exit_code,
            db_command=["mariadb"],
            db_env={},
            proc_root=self.proc,
            db_runner=db_runner or self._db_zero,
        )

    def _add_proc(self, pid: int, pgrp: int) -> None:
        path = self.proc / str(pid)
        path.mkdir()
        (path / "stat").write_text(f"{pid} (test) S 1 {pgrp} 1 0\n", encoding="utf-8")

    def test_certifies_complete_cleanup_deterministically(self):
        first = self._certify()
        second = self._certify()
        self.assertTrue(first["cleanup_certified"])
        self.assertEqual(first, second)
        self.assertEqual("certified", first["status"])
        self.assertEqual(cc.CONTRACT, first["contract"])
        self.assertEqual(1, first["schema_version"])

    def test_invalid_pid_is_never_killed_and_fails_closed(self):
        (self.artifacts / "canary.pid").write_text("not-a-pid\n", encoding="utf-8")
        with mock.patch.object(cc.os, "kill") as kill:
            report = self._certify()
        kill.assert_not_called()
        self.assertFalse(report["cleanup_certified"])

    def test_outside_process_group_is_untouched(self):
        self._add_proc(500, 777)
        with mock.patch.object(cc.os, "kill") as kill:
            report = self._certify()
        kill.assert_not_called()
        check = next(item for item in report["checks"] if item["id"] == "runner_process_group_empty")
        self.assertEqual("pass", check["status"])
        self.assertTrue((self.proc / "500").exists())

    def test_runner_process_group_residue_fails(self):
        self._add_proc(501, 90)
        report = self._certify()
        self.assertFalse(report["cleanup_certified"])
        check = next(item for item in report["checks"] if item["id"] == "runner_process_group_empty")
        self.assertEqual([501], check["observed"])

    def test_missing_client_after_client_activity_fails(self):
        (self.artifacts / "otclient.pid").unlink()
        report = self._certify()
        check = next(item for item in report["checks"] if item["id"] == "process_stopped:primary_client")
        self.assertFalse(report["cleanup_certified"])
        self.assertEqual("fail", check["status"])

    def test_players_online_rows_fail_cleanup(self):
        def runner(command, query, env):
            return (0, "1", "") if query == "SELECT COUNT(*) FROM players_online" else (0, "0", "")

        report = self._certify(db_runner=runner)
        self.assertFalse(report["cleanup_certified"])
        self.assertEqual("partial", report["status"])

    def test_leftover_fault_marker_fails(self):
        (self.repo / ".agent-e2e-fault-injection").write_text("leftover\n", encoding="utf-8")
        report = self._certify()
        self.assertFalse(report["cleanup_certified"])

    def test_declared_secondary_requires_stop_and_exit_evidence(self):
        manifest = {"scenario": {"fixture": {"character": "Paladin 15"}, "multi_client": {"secondary": {"id": "secondary", "character": "Knight 20"}}}}
        (self.artifacts / "scenario-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        report = self._certify()
        self.assertFalse(report["cleanup_certified"])
        self.assertEqual("fail", next(item for item in report["checks"] if item["id"] == "secondary_client_stopped:secondary")["status"])

    def test_gameplay_success_does_not_mask_cleanup_failure(self):
        self._add_proc(600, 90)
        report = self._certify()
        self.assertEqual("success", report["gameplay_status"])
        self.assertFalse(report["cleanup_certified"])

    def test_gameplay_failure_does_not_block_cleanup(self):
        self._write_normal_artifacts("failure")
        report = self._certify(lifecycle_exit_code=1)
        self.assertEqual("failure", report["gameplay_status"])
        self.assertTrue(report["cleanup_certified"])

    def test_workspace_change_fails_and_partial_is_explicit(self):
        (self.otclient / "init.lua").write_text("changed\n", encoding="utf-8")
        report = self._certify()
        self.assertEqual("partial", report["status"])
        self.assertFalse(report["cleanup_certified"])

    def test_validate_rejects_certified_with_failed_required_check(self):
        report = self._certify()
        broken = copy.deepcopy(report)
        broken["checks"][0]["status"] = "fail"
        with self.assertRaises(cc.CleanupCertificationError):
            cc.validate_report(broken)

    def test_result_json_receives_cleanup_without_changing_gameplay_status(self):
        report = self._certify()
        result = json.loads((self.artifacts / "result.json").read_text(encoding="utf-8"))
        self.assertEqual("success", result["status"])
        self.assertEqual(report, result["cleanup_summary"])


if __name__ == "__main__":
    unittest.main()
