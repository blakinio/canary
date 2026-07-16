from __future__ import annotations

import unittest

import ci_incremental_validation as civ


class PathProfileTests(unittest.TestCase):
    def test_ci_treats_agent_task_docs_as_non_impacting(self) -> None:
        self.assertFalse(
            civ.path_impacts_profile(
                "docs/agents/tasks/active/CAN-20260716-example.md", "ci"
            )
        )

    def test_ci_treats_runtime_and_workflow_changes_as_impacting(self) -> None:
        self.assertTrue(civ.path_impacts_profile("src/game/game.cpp", "ci"))
        self.assertTrue(civ.path_impacts_profile(".github/workflows/ci.yml", "ci"))

    def test_normalize_path_preserves_dotfile_prefix(self) -> None:
        self.assertEqual(civ.normalize_path("./.github/workflows/ci.yml"), ".github/workflows/ci.yml")
        self.assertTrue(civ.path_impacts_profile("./.github/workflows/ci.yml", "ci"))

    def test_e2e_excludes_load_only_tests(self) -> None:
        self.assertFalse(
            civ.path_impacts_profile("tests/e2e/load/status-smoke.json", "universal-e2e")
        )
        self.assertFalse(
            civ.path_impacts_profile("tests/e2e/test_load_runner.py", "universal-e2e")
        )

    def test_e2e_keeps_runtime_and_physical_scenario_changes_impacting(self) -> None:
        self.assertTrue(
            civ.path_impacts_profile("src/server/network/protocol/protocollogin.cpp", "universal-e2e")
        )
        self.assertTrue(
            civ.path_impacts_profile("tests/e2e/scenarios/login/relog.yaml", "universal-e2e")
        )

    def test_helper_change_forces_e2e_and_load_validation(self) -> None:
        helper = "tools/agents/ci_incremental_validation.py"
        self.assertTrue(civ.path_impacts_profile(helper, "universal-e2e"))
        self.assertTrue(civ.path_impacts_profile(helper, "universal-load"))

    def test_load_keeps_runtime_and_load_paths_impacting(self) -> None:
        self.assertTrue(
            civ.path_impacts_profile("src/server/network/protocol/protocolstatus.cpp", "universal-load")
        )
        self.assertTrue(
            civ.path_impacts_profile("tests/e2e/load/status-smoke.json", "universal-load")
        )
        self.assertFalse(
            civ.path_impacts_profile("docs/agents/CHANGELOG.md", "universal-load")
        )


class FinalGateLabelTests(unittest.TestCase):
    def test_exact_final_gate_label_is_detected(self) -> None:
        payload = {
            "pull_request": {
                "labels": [
                    {"name": "documentation"},
                    {"name": civ.FINAL_GATE_LABEL},
                ]
            }
        }
        self.assertTrue(civ.event_has_final_gate_label(payload))

    def test_other_or_malformed_labels_do_not_force_final_gate(self) -> None:
        self.assertFalse(
            civ.event_has_final_gate_label(
                {"pull_request": {"labels": [{"name": "documentation"}]}}
            )
        )
        self.assertFalse(civ.event_has_final_gate_label({}))
        self.assertFalse(civ.event_has_final_gate_label({"pull_request": {"labels": "bad"}}))


class ParentWorkflowEvidenceTests(unittest.TestCase):
    def test_latest_same_workflow_run_wins(self) -> None:
        runs = [
            {
                "name": "Universal Agent E2E",
                "run_number": 10,
                "run_attempt": 1,
                "created_at": "2026-07-16T01:00:00Z",
                "status": "completed",
                "conclusion": "success",
            },
            {
                "name": "Universal Agent E2E",
                "run_number": 11,
                "run_attempt": 1,
                "created_at": "2026-07-16T02:00:00Z",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "name": "CI",
                "run_number": 999,
                "status": "completed",
                "conclusion": "success",
            },
        ]
        latest = civ.latest_same_workflow_run(runs, "Universal Agent E2E")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["run_number"], 11)
        ok, _ = civ.parent_has_successful_workflow_run(runs, "Universal Agent E2E")
        self.assertFalse(ok)

    def test_completed_success_is_reusable_parent_evidence(self) -> None:
        ok, reason = civ.parent_has_successful_workflow_run(
            [
                {
                    "name": "CI",
                    "run_number": 20,
                    "status": "completed",
                    "conclusion": "success",
                }
            ],
            "CI",
        )
        self.assertTrue(ok)
        self.assertIn("completed successfully", reason)

    def test_missing_or_in_progress_parent_evidence_fails_closed(self) -> None:
        missing, _ = civ.parent_has_successful_workflow_run([], "CI")
        pending, _ = civ.parent_has_successful_workflow_run(
            [
                {
                    "name": "CI",
                    "run_number": 21,
                    "status": "in_progress",
                    "conclusion": None,
                }
            ],
            "CI",
        )
        self.assertFalse(missing)
        self.assertFalse(pending)


class DecisionTests(unittest.TestCase):
    SUCCESSFUL_PARENT = [
        {
            "name": "CI",
            "run_number": 100,
            "status": "completed",
            "conclusion": "success",
        }
    ]

    def test_non_impacting_synchronize_reuses_successful_immediate_parent(self) -> None:
        decision = civ.decide_reuse(
            profile="ci",
            workflow_name="CI",
            event_name="pull_request",
            event_action="synchronize",
            force_full=False,
            changed_paths=["docs/agents/tasks/active/CAN-20260716-example.md"],
            parent_sha="abc123",
            parent_runs=self.SUCCESSFUL_PARENT,
        )
        self.assertTrue(decision.reuse_parent)
        self.assertFalse(decision.run_heavy)

    def test_impacting_delta_forces_heavy_even_with_successful_parent(self) -> None:
        decision = civ.decide_reuse(
            profile="ci",
            workflow_name="CI",
            event_name="pull_request",
            event_action="synchronize",
            force_full=False,
            changed_paths=["src/game/game.cpp"],
            parent_sha="abc123",
            parent_runs=self.SUCCESSFUL_PARENT,
        )
        self.assertFalse(decision.reuse_parent)
        self.assertTrue(decision.run_heavy)
        self.assertIn("affects validation profile", decision.reason)

    def test_final_gate_always_forces_heavy(self) -> None:
        decision = civ.decide_reuse(
            profile="ci",
            workflow_name="CI",
            event_name="pull_request",
            event_action="labeled",
            force_full=True,
            changed_paths=["docs/agents/CHANGELOG.md"],
            parent_sha="abc123",
            parent_runs=self.SUCCESSFUL_PARENT,
        )
        self.assertFalse(decision.reuse_parent)
        self.assertTrue(decision.run_heavy)
        self.assertIn("final gate", decision.reason)

    def test_non_synchronize_event_forces_heavy(self) -> None:
        decision = civ.decide_reuse(
            profile="ci",
            workflow_name="CI",
            event_name="pull_request",
            event_action="opened",
            force_full=False,
            changed_paths=["docs/agents/CHANGELOG.md"],
            parent_sha="abc123",
            parent_runs=self.SUCCESSFUL_PARENT,
        )
        self.assertFalse(decision.reuse_parent)
        self.assertTrue(decision.run_heavy)

    def test_missing_parent_run_fails_closed(self) -> None:
        decision = civ.decide_reuse(
            profile="ci",
            workflow_name="CI",
            event_name="pull_request",
            event_action="synchronize",
            force_full=False,
            changed_paths=["docs/agents/CHANGELOG.md"],
            parent_sha="abc123",
            parent_runs=[],
        )
        self.assertFalse(decision.reuse_parent)
        self.assertTrue(decision.run_heavy)
        self.assertIn("no same-workflow", decision.reason)

    def test_empty_delta_fails_closed(self) -> None:
        decision = civ.decide_reuse(
            profile="ci",
            workflow_name="CI",
            event_name="pull_request",
            event_action="synchronize",
            force_full=False,
            changed_paths=[],
            parent_sha="abc123",
            parent_runs=self.SUCCESSFUL_PARENT,
        )
        self.assertFalse(decision.reuse_parent)
        self.assertTrue(decision.run_heavy)


if __name__ == "__main__":
    unittest.main()