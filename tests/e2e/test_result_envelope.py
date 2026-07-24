from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "e2e" / "result_envelope.py"
SPEC = importlib.util.spec_from_file_location("canary_e2e_result_envelope", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
result_envelope = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = result_envelope
SPEC.loader.exec_module(result_envelope)


FIXED_NOW = datetime(2026, 7, 24, 6, 0, 5, tzinfo=timezone.utc)
FIXED_ENV = {
    "GITHUB_REPOSITORY": "blakinio/canary",
    "GITHUB_SHA": "a" * 40,
    "GITHUB_RUN_ID": "30000000000",
    "GITHUB_RUN_ATTEMPT": "2",
}


class ResultEnvelopeTest(unittest.TestCase):
    def write_json(self, root: Path, name: str, payload: object) -> None:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def manifest(self, *, maturity: str | None = "M3") -> dict[str, object]:
        scenario: dict[str, object] = {
            "schema_version": 1,
            "id": "relog",
            "suite": "login",
            "name": "Login and relog",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "client": {
                "repository": "blakinio/otclient",
                "ref": "b" * 40,
                "automation": "tools/e2e/client/agent_e2e.lua",
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
            "assertions": {
                "required_markers": ["login_1=success", "logout_2=complete"],
                "persistence": {
                    "required": True,
                    "checks": [{"id": "last-login", "type": "player_scalar"}],
                },
                "sql": ["SELECT 1"],
            },
            "artifacts": [
                "result.json",
                "scenario-manifest.json",
                "client-events.tsv",
                "canary.stdout.log",
            ],
        }
        if maturity is not None:
            scenario["evidence_maturity"] = maturity
        return {
            "schema_version": 1,
            "key": "login/relog",
            "source": "tests/e2e/scenarios/login/relog.json",
            "scenario": scenario,
        }

    def successful_legacy_result(self) -> dict[str, object]:
        return {
            "schema_version": 2,
            "status": "success",
            "scenario": "login/relog",
            "canary_head": "a" * 40,
            "client_repository": "blakinio/otclient",
            "client_ref": "b" * 40,
            "checks": {
                "required_markers": True,
                "client_exit_zero": True,
                "two_server_logins_observed": True,
                "two_packet_records_present": True,
                "lastlogin_persisted": True,
                "lastlogout_persisted": True,
                "scenario_sql_assertions": True,
                "no_fatal_runtime_log": True,
            },
            "missing_markers": [],
            "client_exit_code": 0,
            "server_login_count": 2,
            "session_record_count": 2,
            "lastlogin_set": 1,
            "lastlogout_set": 1,
            "sql_assertions_passed": 1,
            "sql_assertions": {
                "schema_version": 1,
                "all_passed": True,
                "assertions": [
                    {
                        "index": 1,
                        "executed": True,
                        "returncode": 0,
                        "stdout": "1",
                        "stderr": "",
                        "passed": True,
                    }
                ],
            },
            "players_online_snapshot": 1,
            "players_online_snapshot_is_diagnostic_only": True,
            "after_online_count": 0,
            "fatal_log_hits": [],
            "events": [
                {"timestamp": "1.0", "key": "login_1", "value": "success"},
                {"timestamp": "2.0", "key": "logout_2", "value": "complete"},
            ],
        }

    def build(
        self,
        artifacts: Path,
        *,
        phase: str = "complete",
        shell_exit_code: int = 0,
        environment: dict[str, str] | None = None,
    ) -> dict[str, object]:
        return result_envelope.build_envelope(
            artifacts,
            current_phase=phase,
            shell_exit_code=shell_exit_code,
            execution_tier="pr-required",
            environment=environment or FIXED_ENV,
            started_at="2026-07-24T06:00:00.000Z",
            ended_at="2026-07-24T06:00:05.000Z",
            now=FIXED_NOW,
        )

    def prepare_success(self, root: Path, *, maturity: str | None = "M3") -> None:
        self.write_json(root, "scenario-manifest.json", self.manifest(maturity=maturity))
        self.write_json(root, "result.json", self.successful_legacy_result())
        (root / "client-events.tsv").write_text(
            "timestamp\tkey\tvalue\n1.0\tlogin_1\tsuccess\n2.0\tlogout_2\tcomplete\n",
            encoding="utf-8",
        )
        (root / "canary.stdout.log").write_text("server online!\n", encoding="utf-8")
        (root / "otclient-exit-code.txt").write_text("0\n", encoding="utf-8")
        (root / "database-after-online-count.txt").write_text("0\n", encoding="utf-8")
        (root / "map.sha256").write_text(f"{'c' * 64}  otservbr.otbm\n", encoding="utf-8")

    def test_success_contract_is_a_legacy_compatible_superset(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.prepare_success(artifacts)

            envelope = self.build(artifacts)

            self.assertEqual(result_envelope.CONTRACT, envelope["contract"])
            self.assertEqual(result_envelope.SCHEMA_VERSION, envelope["schema_version"])
            self.assertEqual("success", envelope["status"])
            self.assertEqual("login", envelope["suite"])
            self.assertEqual("relog", envelope["scenario_id"])
            self.assertEqual("login/relog", envelope["scenario"])
            self.assertEqual("M3", envelope["evidence_maturity"])
            self.assertEqual("pass", envelope["quality_dimensions"]["diagnostics"])
            self.assertEqual("not-evaluated", envelope["quality_dimensions"]["cleanup"])
            self.assertEqual("a" * 40, envelope["server"]["revision"])
            self.assertEqual("b" * 40, envelope["client"]["revision"])
            self.assertEqual("c" * 64, envelope["server"]["map"]["sha256"])
            self.assertEqual(5000, envelope["duration_ms"])
            self.assertIsNone(envelope["failure"])
            self.assertIsNone(envelope["first_failed_step"])
            self.assertFalse(envelope["cleanup_summary"]["cleanup_certified"])
            self.assertEqual(0, envelope["cleanup_summary"]["observations"]["players_online_after"])
            self.assertEqual(2, envelope["legacy_result"]["schema_version"])
            self.assertEqual(2, envelope["server_login_count"])
            self.assertEqual(1, len(envelope["attempt_history"]))
            result_envelope.validate_envelope(envelope)

    def test_serialization_is_deterministic_for_fixed_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.prepare_success(artifacts)

            first = result_envelope.serialize_envelope(self.build(artifacts))
            second = result_envelope.serialize_envelope(self.build(artifacts))

            self.assertEqual(first, second)
            self.assertTrue(first.endswith("\n"))

    def test_validation_rejects_invalid_version_status_and_dimension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.prepare_success(artifacts)
            valid = self.build(artifacts)

            invalid_version = json.loads(json.dumps(valid))
            invalid_version["schema_version"] = 999
            with self.assertRaisesRegex(result_envelope.EnvelopeError, "schema_version"):
                result_envelope.validate_envelope(invalid_version)

            invalid_status = json.loads(json.dumps(valid))
            invalid_status["status"] = "green"
            with self.assertRaisesRegex(result_envelope.EnvelopeError, "invalid status"):
                result_envelope.validate_envelope(invalid_status)

            invalid_dimension = json.loads(json.dumps(valid))
            invalid_dimension["quality_dimensions"]["diagnostics"] = "proven"
            with self.assertRaisesRegex(result_envelope.EnvelopeError, "quality dimension"):
                result_envelope.validate_envelope(invalid_dimension)

    def test_sanitization_removes_secrets_and_connection_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.prepare_success(artifacts)
            legacy = self.successful_legacy_result()
            legacy["token"] = "top-secret-token"
            legacy["diagnostic"] = "mysql://root:root@127.0.0.1/db password=root"
            legacy["nested"] = {"private_key": "PEM-DATA", "safe": "retained"}
            self.write_json(artifacts, "result.json", legacy)

            envelope = self.build(artifacts)
            serialized = result_envelope.serialize_envelope(envelope)

            self.assertEqual("[REDACTED]", envelope["token"])
            self.assertEqual("[REDACTED]", envelope["nested"]["private_key"])
            self.assertEqual("retained", envelope["nested"]["safe"])
            self.assertNotIn("top-secret-token", serialized)
            self.assertNotIn("root:root@", serialized)
            self.assertNotIn("password=root", serialized)
            self.assertIn("AGENT_E2E_TEST_PASSWORD", serialized)

    def test_first_failure_selects_missing_route_marker_and_last_successful_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.write_json(artifacts, "scenario-manifest.json", self.manifest(maturity="M1"))
            legacy = self.successful_legacy_result()
            legacy.update(
                {
                    "status": "failure",
                    "checks": {
                        "client_exit_zero": True,
                        "required_markers": False,
                        "scenario_sql_assertions": False,
                    },
                    "missing_markers": ["route_position_expected=32369,32241,7"],
                    "sql_assertions_passed": 0,
                }
            )
            self.write_json(artifacts, "result.json", legacy)

            envelope = self.build(artifacts, phase="evidence-evaluation", shell_exit_code=1)

            self.assertEqual("failure", envelope["status"])
            self.assertEqual("route_execution", envelope["failure"]["classification"])
            self.assertEqual("gameplay", envelope["failure"]["category"])
            self.assertEqual("check:required_markers", envelope["first_failed_step"]["id"])
            self.assertIsNone(envelope["last_successful_step"])
            self.assertEqual(
                ["route_position_expected=32369,32241,7"],
                envelope["failure"]["observed"]["missing_markers"],
            )
            self.assertEqual("route_execution", envelope["attempt_history"][-1]["failure_classification"])

    def test_multiple_attempt_history_preserves_previous_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.prepare_success(artifacts)
            legacy = self.successful_legacy_result()
            legacy["attempt_history"] = [
                {
                    "run_id": "github-29999999999-1-login-relog",
                    "attempt": 1,
                    "status": "failure",
                    "started_at": "2026-07-24T05:00:00.000Z",
                    "ended_at": "2026-07-24T05:00:04.000Z",
                    "duration_ms": 4000,
                    "failure_classification": "assertion",
                }
            ]
            self.write_json(artifacts, "result.json", legacy)

            envelope = self.build(artifacts)

            self.assertEqual(2, len(envelope["attempt_history"]))
            self.assertEqual("failure", envelope["attempt_history"][0]["status"])
            self.assertEqual("success", envelope["attempt_history"][1]["status"])
            self.assertEqual(2, envelope["attempt_history"][1]["attempt"])

    def test_bootstrap_failure_is_classified_as_infrastructure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.write_json(
                artifacts,
                "result.json",
                {
                    "schema_version": 1,
                    "status": "failure",
                    "scenario": "login/relog",
                    "phase": "bootstrap",
                    "shell_exit_code": 127,
                    "checks": {},
                },
            )

            envelope = self.build(artifacts, phase="bootstrap", shell_exit_code=127)

            self.assertEqual("failure", envelope["status"])
            self.assertEqual("infrastructure", envelope["failure"]["classification"])
            self.assertEqual("infrastructure", envelope["failure"]["category"])
            self.assertEqual(127, envelope["failure"]["observed"])
            self.assertEqual("infrastructure", envelope["infrastructure_failure"]["classification"])
            self.assertTrue(envelope["warnings"])
            result_envelope.validate_envelope(envelope)

    def test_unknown_maturity_and_cleanup_remain_explicitly_unproven(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            self.prepare_success(artifacts, maturity=None)

            envelope = self.build(artifacts)

            self.assertEqual("unknown", envelope["evidence_maturity"])
            self.assertEqual("not-evaluated", envelope["quality_dimensions"]["cleanup"])
            self.assertEqual("not-certified", envelope["cleanup_summary"]["status"])
            self.assertTrue(any("maturity" in item.lower() for item in envelope["unknowns"]))
            self.assertTrue(any("QRI-006" in item for item in envelope["unknowns"]))


if __name__ == "__main__":
    unittest.main()
