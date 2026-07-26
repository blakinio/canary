from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "tools" / "e2e" / "pr_scenario_selection.py"
SPEC = importlib.util.spec_from_file_location(
    "canary_e2e_resolved_scenario_reuse", MODULE_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ResolvedScenarioReuseTest(unittest.TestCase):
    def call(self, *, suite: str = "login", scenario: str = "relog"):
        with tempfile.TemporaryDirectory() as temporary:
            return MODULE.select_for_event(
                event_name="pull_request",
                current_repository="blakinio/canary",
                pr_head_repository="blakinio/canary",
                requested_suite=suite,
                requested_scenario=scenario,
                base_sha="a" * 40,
                head_sha="b" * 40,
                repo_root=Path(temporary),
            )

    def test_physical_job_reuses_exact_workflow_resolved_identity(self) -> None:
        environment = {
            "GITHUB_JOB": "physical-client",
            "AGENT_E2E_SUITE": "login",
            "AGENT_E2E_SCENARIO_ID": "relog",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            with mock.patch.object(
                MODULE,
                "git_changed_paths",
                side_effect=AssertionError("PR delta must not be inspected twice"),
            ):
                selection = self.call()
        self.assertEqual("login", selection.suite)
        self.assertEqual("relog", selection.scenario)
        self.assertEqual("workflow-resolved-physical-job", selection.reason)

    def test_physical_job_rejects_missing_resolved_identity(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"GITHUB_JOB": "physical-client", "AGENT_E2E_SUITE": "login"},
            clear=True,
        ):
            with self.assertRaisesRegex(
                MODULE.SelectionError,
                "requires the workflow-resolved scenario identity",
            ):
                self.call()

    def test_physical_job_rejects_resolved_identity_mismatch(self) -> None:
        environment = {
            "GITHUB_JOB": "physical-client",
            "AGENT_E2E_SUITE": "login",
            "AGENT_E2E_SCENARIO_ID": "other",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(
                MODULE.SelectionError,
                "requested=login/relog resolved=login/other",
            ):
                self.call()

    def test_non_physical_non_pr_caller_keeps_existing_selection(self) -> None:
        with mock.patch.dict(os.environ, {"GITHUB_JOB": "resolve"}, clear=True):
            with tempfile.TemporaryDirectory() as temporary:
                selection = MODULE.select_for_event(
                    event_name="workflow_dispatch",
                    current_repository="blakinio/canary",
                    pr_head_repository="",
                    requested_suite="login",
                    requested_scenario="relog",
                    base_sha="",
                    head_sha="",
                    repo_root=Path(temporary),
                )
        self.assertEqual("explicit-or-canonical-non-pr", selection.reason)


if __name__ == "__main__":
    unittest.main()
