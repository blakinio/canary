from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.security import runtime_adapter as ra  # noqa: E402


class RuntimeAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "tests/security/runtime_adapters").mkdir(parents=True)
        (self.root / "tests/e2e/scenarios/login").mkdir(parents=True)
        (self.root / ".github/workflows").mkdir(parents=True)
        (self.root / "tools/e2e/client").mkdir(parents=True)

        (self.root / ".github/workflows/universal-agent-e2e.yml").write_text(
            "name: Universal Agent E2E\n", encoding="utf-8"
        )
        (self.root / "tools/e2e/run_agent_e2e.py").write_text("# resolver\n", encoding="utf-8")
        (self.root / "tools/e2e/run_physical_e2e.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        (self.root / "tools/e2e/client/agent_e2e.lua").write_text("-- automation\n", encoding="utf-8")
        self.write_e2e_scenario()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def adapter_data(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "id": "canary-universal-e2e",
            "target_adapter": "canary-runtime",
            "component": "server",
            "authorization": {"scope": "repository", "repository": "blakinio/canary"},
            "delegate": {"provider": "universal-e2e", "suite": "login", "scenario": "relog"},
            "confinement": {"network": "literal-loopback-only"},
        }

    def e2e_data(self, *, host: str = "127.0.0.1", client_repository: str = "blakinio/otclient") -> dict[str, object]:
        return {
            "schema_version": 1,
            "id": "relog",
            "suite": "login",
            "name": "Login relog baseline",
            "program_id": "CAN-PROGRAM-E2E-PLATFORM",
            "description": "Deterministic login and relog baseline.",
            "client": {
                "repository": client_repository,
                "ref": "main",
                "automation": "tools/e2e/client/agent_e2e.lua",
            },
            "server": {
                "datapack": "data-otservbr-global",
                "map": "otservbr",
                "database_image": "mariadb:11.4",
            },
            "fixture": {
                "account": "security@example.invalid",
                "password_env": "AGENT_E2E_TEST_PASSWORD",
                "character": "Knight 1",
                "world": "Canary",
                "host": host,
                "game_port": 7172,
            },
            "timing": {
                "global_timeout_seconds": 120,
                "session_hold_ms": 1000,
                "relog_delay_ms": 1000,
            },
            "assertions": {
                "required_markers": ["online_stable_1=confirmed"],
                "sql": ["SELECT 1"],
            },
            "artifacts": ["result.json"],
        }

    def write_adapter(self, data: dict[str, object] | None = None, name: str = "canary.json") -> Path:
        path = self.root / "tests/security/runtime_adapters" / name
        path.write_text(json.dumps(data or self.adapter_data()), encoding="utf-8")
        return path

    def write_e2e_scenario(self, data: dict[str, object] | None = None) -> Path:
        path = self.root / "tests/e2e/scenarios/login/relog.json"
        path.write_text(json.dumps(data or self.e2e_data()), encoding="utf-8")
        return path

    def test_valid_adapter_resolves_deterministic_delegation_evidence(self) -> None:
        adapter = ra.validate_adapter(self.write_adapter(), self.root)
        first = ra.resolve_adapter(adapter, self.root, "blakinio/canary")
        second = ra.resolve_adapter(adapter, self.root, "blakinio/canary")
        self.assertEqual(first, second)
        self.assertEqual(first["schema"], ra.REPORT_SCHEMA)
        self.assertEqual(first["result"], "pass")
        self.assertEqual(first["delegate"]["scenario_key"], "login/relog")
        self.assertEqual(first["confinement"]["host"], "127.0.0.1")
        self.assertTrue(first["confinement"]["host_is_loopback"])
        self.assertEqual(first["confinement"]["host_ip_version"], 4)
        for evidence in first["delegate"]["provider_files"].values():
            self.assertEqual(len(evidence["sha256"]), 64)

    def test_unknown_manifest_field_is_rejected(self) -> None:
        data = self.adapter_data()
        data["command"] = "bash arbitrary.sh"
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "unsupported field"):
            ra.validate_adapter(self.write_adapter(data), self.root)

    def test_unsupported_provider_is_rejected(self) -> None:
        data = self.adapter_data()
        data["delegate"]["provider"] = "custom-shell"  # type: ignore[index]
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "provider must be one of"):
            ra.validate_adapter(self.write_adapter(data), self.root)

    def test_repository_authorization_mismatch_is_rejected(self) -> None:
        adapter = ra.validate_adapter(self.write_adapter(), self.root)
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "authorized for blakinio/canary"):
            ra.resolve_adapter(adapter, self.root, "example/other")

    def test_hostname_is_rejected_even_when_it_resolves_to_loopback(self) -> None:
        self.write_e2e_scenario(self.e2e_data(host="localhost"))
        adapter = ra.validate_adapter(self.write_adapter(), self.root)
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "literal loopback IP address"):
            ra.resolve_adapter(adapter, self.root, "blakinio/canary")

    def test_non_loopback_literal_ip_is_rejected(self) -> None:
        self.write_e2e_scenario(self.e2e_data(host="192.0.2.10"))
        adapter = ra.validate_adapter(self.write_adapter(), self.root)
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "must be loopback"):
            ra.resolve_adapter(adapter, self.root, "blakinio/canary")

    def test_unapproved_controlled_client_repository_is_rejected(self) -> None:
        self.write_e2e_scenario(self.e2e_data(client_repository="example/other-client"))
        adapter = ra.validate_adapter(self.write_adapter(), self.root)
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "client repository is not approved"):
            ra.resolve_adapter(adapter, self.root, "blakinio/canary")

    def test_missing_delegated_scenario_is_rejected(self) -> None:
        data = self.adapter_data()
        data["delegate"]["scenario"] = "missing"  # type: ignore[index]
        adapter = ra.validate_adapter(self.write_adapter(data), self.root)
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "delegated Universal E2E scenario is invalid"):
            ra.resolve_adapter(adapter, self.root, "blakinio/canary")

    def test_provider_symlink_is_rejected(self) -> None:
        provider = self.root / "tools/e2e/run_physical_e2e.sh"
        target = self.root / "tools/e2e/real_runner.sh"
        target.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
        provider.unlink()
        try:
            os.symlink(target, provider)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "must not traverse a symlink"):
            ra.validate_adapter(self.write_adapter(), self.root)

    def test_duplicate_adapter_ids_are_rejected(self) -> None:
        self.write_adapter(name="one.json")
        self.write_adapter(name="two.json")
        with self.assertRaisesRegex(ra.RuntimeAdapterError, "duplicate runtime adapter id"):
            ra.discover(self.root)

    def test_write_report_is_atomic_and_stable(self) -> None:
        adapter = ra.validate_adapter(self.write_adapter(), self.root)
        report = ra.resolve_adapter(adapter, self.root, "blakinio/canary")
        output = self.root / "artifacts/runtime-delegation.json"
        ra.write_report(output, report)
        self.assertEqual(output.read_text(encoding="utf-8"), ra.render_report(report))
        self.assertFalse(output.with_name("runtime-delegation.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
