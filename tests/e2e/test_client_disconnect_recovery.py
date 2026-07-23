from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "tests/e2e/scenarios/recovery/client-disconnect-recovery.json"
DRIVER_PATH = REPO_ROOT / "tools/e2e/client/agent_e2e_fault_recovery.lua"


class ClientDisconnectRecoveryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.driver = DRIVER_PATH.read_text(encoding="utf-8")

    def test_manifest_uses_bounded_existing_physical_runtime(self) -> None:
        self.assertEqual(self.manifest["suite"], "recovery")
        self.assertEqual(self.manifest["client"]["automation"], "tools/e2e/client/agent_e2e_fault_recovery.lua")
        self.assertEqual(self.manifest["fixture"]["password_env"], "AGENT_E2E_TEST_PASSWORD")
        self.assertNotIn("password", self.manifest["fixture"])
        self.assertEqual(self.manifest["fixture"]["host"], "127.0.0.1")
        self.assertEqual(self.manifest["server"]["database_image"], "mariadb:11.4")

    def test_manifest_requires_explicit_fault_and_recovery_markers(self) -> None:
        markers = set(self.manifest["assertions"]["required_markers"])
        self.assertTrue(
            {
                "fault_injection=client_force_logout",
                "fault_expected=client_disconnect",
                "fault_observed=client_disconnect",
                "fault_classification=expected_injected_failure",
                "recovery_login=success",
                "recovery_online=confirmed",
                "cleanup=safe_logout_complete",
                "e2e=success",
            }.issubset(markers)
        )

    def test_manifest_preserves_two_login_two_record_evidence_shape(self) -> None:
        artifacts = set(self.manifest["artifacts"])
        self.assertIn("session-1.record", artifacts)
        self.assertIn("session-2.record", artifacts)
        self.assertFalse(any(name.startswith("session-3") for name in artifacts))
        sql = self.manifest["assertions"]["sql"]
        self.assertEqual(len(sql), 2)
        self.assertTrue(any("lastlogin" in query for query in sql))
        self.assertTrue(any("lastlogout" in query for query in sql))

    def test_driver_injects_fault_only_after_stable_phase_one(self) -> None:
        injection = re.compile(
            r'if finished or phase ~= 1.*?appendEvent\("fault_injection", "client_force_logout"\).*?g_game\.forceLogout\(\)',
            re.DOTALL,
        )
        self.assertRegex(self.driver, injection)
        self.assertIn('appendEvent("online_stable_" .. phase, "confirmed")', self.driver)
        self.assertIn("scheduleEvent(injectClientDisconnect, 500)", self.driver)

    def test_driver_distinguishes_expected_fault_from_unexpected_disconnect(self) -> None:
        self.assertIn('appendEvent("fault_classification", "expected_injected_failure")', self.driver)
        self.assertIn('fail("unexpected disconnect in phase " .. tostring(phase))', self.driver)
        self.assertIn("if phase == 1 and injectedDisconnectPending then", self.driver)
        self.assertIn('appendEvent("recovery_login", "success")', self.driver)
        self.assertIn('appendEvent("cleanup", "safe_logout_complete")', self.driver)

    def test_driver_exposes_no_manifest_command_execution_surface(self) -> None:
        self.assertNotIn("os.execute", self.driver)
        self.assertNotIn("io.popen", self.driver)
        self.assertNotIn("AGENT_E2E_COMMAND", self.driver)
        self.assertNotIn("DB_HOST", self.driver)


if __name__ == "__main__":
    unittest.main()
