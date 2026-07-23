from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "tests/e2e/scenarios/recovery/canary-restart-recovery.json"
DRIVER_PATH = REPO_ROOT / "tools/e2e/client/agent_e2e_canary_restart_recovery.lua"
RUNNER_PATH = REPO_ROOT / "tools/e2e/run_physical_e2e.sh"
RESTART_SEAM_PATH = REPO_ROOT / "tools/e2e/disposable_canary_restart.sh"


class CanaryRestartRecoveryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.driver = DRIVER_PATH.read_text(encoding="utf-8")
        cls.runner = RUNNER_PATH.read_text(encoding="utf-8")
        cls.restart_seam = RESTART_SEAM_PATH.read_text(encoding="utf-8")

    def test_manifest_uses_existing_disposable_physical_runtime(self) -> None:
        self.assertEqual(self.manifest["suite"], "recovery")
        self.assertEqual(
            self.manifest["client"]["automation"],
            "tools/e2e/client/agent_e2e_canary_restart_recovery.lua",
        )
        self.assertEqual(self.manifest["fixture"]["host"], "127.0.0.1")
        self.assertEqual(self.manifest["fixture"]["character"], "Paladin 15")
        self.assertEqual(self.manifest["server"]["database_image"], "mariadb:11.4")
        self.assertEqual(self.manifest["server"]["datapack"], "data-canary")
        self.assertEqual(self.manifest["server"]["map"], "canary")
        self.assertNotIn("password", self.manifest["fixture"])

    def test_manifest_uses_typed_balance_persistence_before_final_sql(self) -> None:
        persistence = self.manifest["assertions"]["persistence"]
        self.assertTrue(persistence["required"])
        self.assertEqual(
            persistence["checks"],
            [{"id": "balance", "type": "player_balance", "equals": 12345}],
        )
        markers = set(self.manifest["assertions"]["required_markers"])
        self.assertTrue(
            {
                "mutation_request=bank_balance_12345",
                "save_request=fixed_server_save",
                "restart_request=disposable_canary",
                "fault_observed=server_disconnect",
                "recovery_server_ready=confirmed",
                "recovery_login=success",
                "recovery_online=confirmed",
                "persistence_check_balance=success",
                "persistence_check_balance_detail=12345",
                "cleanup=safe_logout_complete",
                "e2e=success",
            }.issubset(markers)
        )
        self.assertNotIn("pre_restart_persistence_check=success", markers)
        self.assertIn("database-restart-pre-balance.txt", set(self.manifest["artifacts"]))

    def test_driver_mutates_saves_and_requests_restart_without_stale_cache_gate(self) -> None:
        mutation = re.compile(
            r"local function mutatePersistentState\(\)"
            r'.*?appendEvent\("mutation_request", "bank_balance_12345"\)'
            r'.*?g_game\.talk\("/addmoney " \.\. CHARACTER \.\. ", 12345"\)'
            r".*?scheduleEvent\(saveAndRequestRestart, 500\)",
            re.DOTALL,
        )
        save_callback = re.compile(
            r"local function saveAndRequestRestart\(\)"
            r'.*?appendEvent\("save_request", "fixed_server_save"\)'
            r'.*?g_game\.talk\("/save"\)'
            r".*?scheduleEvent\(requestRestart, 1000\)",
            re.DOTALL,
        )
        restart_callback = re.compile(
            r"local function requestRestart\(\)"
            r".*?restartRequested = true"
            r'.*?appendEvent\("restart_request", "disposable_canary"\)',
            re.DOTALL,
        )
        self.assertRegex(self.driver, mutation)
        self.assertRegex(self.driver, save_callback)
        self.assertRegex(self.driver, restart_callback)
        self.assertNotIn('waitForBalance(EXPECTED_BALANCE, "pre_restart_persistence_check"', self.driver)
        self.assertIn('waitForBalance(EXPECTED_BALANCE, "persistence_check_balance"', self.driver)

    def test_restart_seam_proves_exact_persisted_balance_before_sigterm(self) -> None:
        persistence_check = re.compile(
            r'wait_for_restart_client_marker "mutation_request" "bank_balance_12345"'
            r'.*?wait_for_restart_client_marker "save_request" "fixed_server_save"'
            r'.*?wait_for_restart_client_marker "restart_request" "disposable_canary"'
            r".*?wait_for_persisted_restart_balance"
            r'.*?record_restart_phase "pre-restart-gameplay" "success"',
            re.DOTALL,
        )
        self.assertRegex(self.restart_seam, persistence_check)
        self.assertIn('DISPOSABLE_CANARY_RESTART_EXPECTED_BALANCE="12345"', self.restart_seam)
        self.assertIn("SELECT balance FROM players WHERE name='${DISPOSABLE_CANARY_RESTART_CHARACTER}' LIMIT 1;", self.restart_seam)
        self.assertIn('DISPOSABLE_CANARY_RESTART_PRE_BALANCE_FILE="${ARTIFACT_DIR}/database-restart-pre-balance.txt"', self.restart_seam)
        self.assertIn('"pre_restart_balance_persisted": pre_restart_balance == 12345', self.restart_seam)

    def test_driver_requires_real_disconnect_before_relogin(self) -> None:
        self.assertIn('appendEvent("fault_expected", "server_disconnect")', self.driver)
        self.assertIn('appendEvent("fault_observed", "server_disconnect")', self.driver)
        self.assertIn('appendEvent("fault_classification", "expected_injected_failure")', self.driver)
        self.assertIn('appendEvent("recovery_server_ready", "confirmed")', self.driver)
        self.assertIn('appendEvent("recovery_login", "success")', self.driver)
        self.assertIn('appendEvent("cleanup", "safe_logout_complete")', self.driver)
        self.assertNotIn("os.execute", self.driver)
        self.assertNotIn("io.popen", self.driver)

    def test_restart_seam_is_exact_scenario_gated_and_has_no_arbitrary_target_input(self) -> None:
        self.assertIn(
            'DISPOSABLE_CANARY_RESTART_SCENARIO_KEY="recovery/canary-restart-recovery"',
            self.restart_seam,
        )
        self.assertIn('local lifecycle_pid="${CANARY_PID}"', self.restart_seam)
        self.assertIn('resolve_exact_runner_owned_canary_pid "${lifecycle_pid}"', self.restart_seam)
        self.assertIn('/proc/${lifecycle_pid}/task/${lifecycle_pid}/children', self.restart_seam)
        self.assertIn('kill -TERM "${pid}"', self.restart_seam)
        self.assertIn('readlink -f "/proc/${pid}/exe"', self.restart_seam)
        self.assertIn('readlink -f "${CANARY_BIN}"', self.restart_seam)
        self.assertIn('exec "${CANARY_BIN}" >> "${ARTIFACT_DIR}/canary.stdout.log"', self.restart_seam)
        self.assertIn('CANARY_PID=$!', self.restart_seam)
        self.assertIn('CANARY_PID=""', self.restart_seam)
        for forbidden in (
            "AGENT_E2E_RESTART_PID",
            "AGENT_E2E_RESTART_HOST",
            "AGENT_E2E_RESTART_COMMAND",
            "run_command",
            "kill_pid",
            "restart_host",
        ):
            self.assertNotIn(forbidden, self.restart_seam)
        self.assertNotIn("recovery", self.manifest)

    def test_restart_evidence_covers_required_failure_phases_and_cleanup(self) -> None:
        for phase in (
            "pre-restart-gameplay",
            "restart-request",
            "process-termination",
            "server-startup",
            "readiness",
            "reconnect",
            "relog",
            "persistence-assertion",
            "cleanup",
        ):
            self.assertIn(f'record_restart_phase "{phase}"', self.restart_seam)
        artifacts = set(self.manifest["artifacts"])
        self.assertIn("canary-restart-evidence.json", artifacts)
        self.assertIn("database-restart-pre-balance.txt", artifacts)
        self.assertIn("database-restart-pre-relogin-online-count.txt", artifacts)
        self.assertIn("canary-old.pid", artifacts)
        self.assertIn("canary-restarted.pid", artifacts)

    def test_canonical_lifecycle_invokes_one_sourced_restart_seam(self) -> None:
        self.assertIn('source "${REPO_ROOT}/tools/e2e/disposable_canary_restart.sh"', self.runner)
        self.assertIn("initialize_disposable_canary_restart", self.runner)
        self.assertIn("validate_disposable_canary_restart_contract", self.runner)
        self.assertIn("restart_disposable_canary", self.runner)
        self.assertIn("finalize_disposable_canary_restart", self.runner)
        self.assertIn("write_disposable_canary_restart_evidence", self.runner)
        self.assertIn("augment_disposable_canary_restart_result", self.runner)
        self.assertNotIn("run_physical_e2e_core.sh", self.runner)
        self.assertIn('CURRENT_PHASE="database-initialization"', self.runner)
        self.assertIn('CURRENT_PHASE="server-startup"', self.runner)
        self.assertIn('CURRENT_PHASE="physical-client"', self.runner)
        self.assertIn('CURRENT_PHASE="database-final-state"', self.runner)
        self.assertIn('CURRENT_PHASE="evidence-evaluation"', self.runner)


if __name__ == "__main__":
    unittest.main()
