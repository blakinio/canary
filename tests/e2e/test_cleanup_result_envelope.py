from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tools.e2e import cleanup_certification
from tools.e2e import result_envelope


class CleanupResultEnvelopeTests(unittest.TestCase):
    def write_json(self, root: Path, name: str, payload: object) -> None:
        (root / name).write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    def prepare(self, root: Path, *, cleanup_certified: bool) -> None:
        manifest = {
            "schema_version": 1,
            "key": "login/relog",
            "source": "tests/e2e/scenarios/login/relog.json",
            "scenario": {
                "schema_version": 1,
                "id": "relog",
                "suite": "login",
                "name": "Login and relog",
                "evidence_maturity": "M3",
                "client": {
                    "repository": "blakinio/otclient",
                    "ref": "b" * 40,
                },
                "server": {
                    "database_image": "mariadb:11.4",
                    "datapack": "data-otservbr-global",
                    "map": "otservbr",
                },
                "fixture": {
                    "account": "@test1",
                    "password_env": "AGENT_E2E_TEST_PASSWORD",
                    "character": "Knight 1",
                    "world": "Canary E2E",
                    "host": "127.0.0.1",
                    "game_port": 7172,
                },
                "assertions": {"required_markers": [], "sql": []},
                "artifacts": [
                    "result.json",
                    "cleanup-certification.json",
                ],
            },
        }
        cleanup = {
            "schema_version": 1,
            "contract": cleanup_certification.CONTRACT,
            "status": "certified" if cleanup_certified else "partial",
            "cleanup_certified": cleanup_certified,
            "gameplay_status": "success",
            "lifecycle_exit_code": 0,
            "lifecycle_process": {"pid": 1, "pgid": 1},
            "process_group_cleanup": {
                "pgid": 1,
                "members_before": [],
                "signals": [],
                "members_after": [],
                "errors": [],
            },
            "resource_scope": (
                "runner-owned-exact-process-group-and-fixed-disposable-database"
            ),
            "checks": [
                {
                    "id": "runner_process_group_empty",
                    "required": True,
                    "status": "pass" if cleanup_certified else "fail",
                    "expected": [],
                    "observed": [] if cleanup_certified else [2],
                    "evidence": {"pgid": 1},
                }
            ],
            "summary": {
                "required": 1,
                "passed": 1 if cleanup_certified else 0,
                "failed": 0 if cleanup_certified else 1,
            },
            "unknowns": [],
            "warnings": [],
        }
        legacy = {
            "schema_version": 2,
            "status": "success",
            "scenario": "login/relog",
            "canary_head": "a" * 40,
            "client_ref": "b" * 40,
            "checks": {},
            "missing_markers": [],
            "client_exit_code": 0,
            "after_online_count": 0,
            "events": [
                {
                    "timestamp": "1.0",
                    "key": "session_record",
                    "value": "/home/runner/work/canary/canary/artifacts/session-1.record",
                }
            ],
            "cleanup_summary": cleanup,
        }
        self.write_json(root, "scenario-manifest.json", manifest)
        self.write_json(root, "result.json", legacy)
        self.write_json(root, "cleanup-certification.json", cleanup)
        (root / "map.sha256").write_text("", encoding="utf-8")

    def build(self, root: Path) -> dict[str, object]:
        return result_envelope.build_envelope(
            root,
            current_phase="complete",
            shell_exit_code=0,
            execution_tier="pr-required",
            environment={
                "GITHUB_SHA": "a" * 40,
                "GITHUB_RUN_ID": "1",
                "GITHUB_RUN_ATTEMPT": "1",
            },
            started_at="2026-07-24T10:00:00.000Z",
            ended_at="2026-07-24T10:00:01.000Z",
            now=datetime(2026, 7, 24, 10, 0, 1, tzinfo=timezone.utc),
        )

    def test_certified_cleanup_promotes_only_cleanup_dimension(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, cleanup_certified=True)
            envelope = self.build(root)
        self.assertEqual("success", envelope["status"])
        self.assertEqual("pass", envelope["quality_dimensions"]["cleanup"])
        self.assertTrue(envelope["cleanup_summary"]["cleanup_certified"])
        self.assertFalse(
            any(
                "not QRI-006 certified" in item
                for item in envelope["unknowns"]
            )
        )
        self.assertTrue(
            any(
                item["path"] == "cleanup-certification.json"
                and item["exists"]
                for item in envelope["artifacts"]
            )
        )

    def test_failed_cleanup_does_not_reclassify_gameplay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, cleanup_certified=False)
            envelope = self.build(root)
        self.assertEqual("success", envelope["status"])
        self.assertEqual("fail", envelope["quality_dimensions"]["cleanup"])
        self.assertFalse(envelope["cleanup_summary"]["cleanup_certified"])

    def test_absolute_event_paths_are_reduced_to_artifact_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.prepare(root, cleanup_certified=True)
            envelope = self.build(root)
        expected = "session-1.record"
        self.assertEqual(expected, envelope["events"][0]["value"])
        self.assertEqual(
            expected,
            envelope["legacy_result"]["events"][0]["value"],
        )
        self.assertNotIn("/home/runner", json.dumps(envelope))


if __name__ == "__main__":
    unittest.main()
