from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "e2e" / "pr_scenario_selection.py"
SPEC = importlib.util.spec_from_file_location("pr_scenario_selection", MODULE_PATH)
assert SPEC and SPEC.loader
pr_scenario_selection = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pr_scenario_selection
SPEC.loader.exec_module(pr_scenario_selection)


class PullRequestScenarioSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.scenarios = self.root / "tests" / "e2e" / "scenarios"
        self.write_manifest("login", "scenario.json", "relog")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_manifest(self, suite: str, filename: str, scenario_id: object) -> Path:
        path = self.scenarios / suite / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"id": scenario_id}), encoding="utf-8")
        return path

    def select(self, changed_paths: list[str], **overrides: str):
        values = {
            "event_name": "pull_request",
            "current_repository": "blakinio/canary",
            "pr_head_repository": "blakinio/canary",
            "requested_suite": "login",
            "requested_scenario": "relog",
            "changed_paths": changed_paths,
            "repo_root": self.root,
        }
        values.update(overrides)
        return pr_scenario_selection.select_from_changed_paths(**values)

    def test_selects_exactly_one_existing_changed_manifest_and_declared_id(self) -> None:
        self.write_manifest("movement", "physical-movement.json", "physical-movement")
        selection = self.select(["tests/e2e/scenarios/movement/physical-movement.json"])
        self.assertEqual(selection.suite, "movement")
        self.assertEqual(selection.scenario, "physical-movement")
        self.assertEqual(selection.reason, "single-changed-scenario-manifest")
        self.assertEqual(selection.manifest, "tests/e2e/scenarios/movement/physical-movement.json")

    def test_manifest_filename_does_not_define_scenario_id(self) -> None:
        self.write_manifest("quests", "scenario.json", "quest-smoke")
        selection = self.select(["tests/e2e/scenarios/quests/scenario.json"])
        self.assertEqual((selection.suite, selection.scenario), ("quests", "quest-smoke"))

    def test_zero_changed_manifests_falls_back_to_canonical(self) -> None:
        selection = self.select(["docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md"])
        self.assertEqual((selection.suite, selection.scenario), ("login", "relog"))
        self.assertEqual(selection.reason, "canonical-fallback-existing-scenario-count-0")

    def test_multiple_existing_changed_manifests_fall_back_to_canonical(self) -> None:
        self.write_manifest("movement", "physical-movement.json", "physical-movement")
        self.write_manifest("quests", "quest.json", "quest-smoke")
        selection = self.select(
            [
                "tests/e2e/scenarios/movement/physical-movement.json",
                "tests/e2e/scenarios/quests/quest.json",
            ]
        )
        self.assertEqual((selection.suite, selection.scenario), ("login", "relog"))
        self.assertEqual(selection.reason, "canonical-fallback-existing-scenario-count-2")

    def test_deleted_only_manifest_falls_back_to_canonical(self) -> None:
        selection = self.select(["tests/e2e/scenarios/movement/deleted.json"])
        self.assertEqual((selection.suite, selection.scenario), ("login", "relog"))
        self.assertEqual(selection.reason, "canonical-fallback-existing-scenario-count-0")

    def test_fork_pull_request_falls_back_without_selecting_changed_manifest(self) -> None:
        self.write_manifest("movement", "physical-movement.json", "physical-movement")
        selection = self.select(
            ["tests/e2e/scenarios/movement/physical-movement.json"],
            pr_head_repository="someone/canary",
        )
        self.assertEqual((selection.suite, selection.scenario), ("login", "relog"))
        self.assertEqual(selection.reason, "canonical-fallback-non-same-repository-pr")

    def test_non_pr_event_preserves_explicit_dispatch_selection(self) -> None:
        selection = pr_scenario_selection.select_from_changed_paths(
            event_name="workflow_dispatch",
            current_repository="blakinio/canary",
            pr_head_repository="",
            requested_suite="movement",
            requested_scenario="physical-movement",
            changed_paths=[],
            repo_root=self.root,
        )
        self.assertEqual((selection.suite, selection.scenario), ("movement", "physical-movement"))
        self.assertEqual(selection.reason, "explicit-or-canonical-non-pr")

    def test_unique_invalid_json_manifest_fails_closed(self) -> None:
        path = self.scenarios / "movement" / "bad.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{bad", encoding="utf-8")
        with self.assertRaisesRegex(pr_scenario_selection.SelectionError, "cannot parse"):
            self.select(["tests/e2e/scenarios/movement/bad.json"])

    def test_unique_manifest_with_unsafe_id_fails_closed(self) -> None:
        self.write_manifest("movement", "bad-id.json", "../bad")
        with self.assertRaisesRegex(pr_scenario_selection.SelectionError, "safe non-empty string id"):
            self.select(["tests/e2e/scenarios/movement/bad-id.json"])

    def test_git_changed_paths_uses_exact_base_and_head(self) -> None:
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "e2e@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "E2E Test"], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "base"], check=True)
        base = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()

        self.write_manifest("movement", "physical-movement.json", "physical-movement")
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "head"], check=True)
        head = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()

        changed = pr_scenario_selection.git_changed_paths(self.root, base, head)
        self.assertEqual(changed, ["tests/e2e/scenarios/movement/physical-movement.json"])
        selection = pr_scenario_selection.select_for_event(
            event_name="pull_request",
            current_repository="blakinio/canary",
            pr_head_repository="blakinio/canary",
            requested_suite="login",
            requested_scenario="relog",
            base_sha=base,
            head_sha=head,
            repo_root=self.root,
        )
        self.assertEqual((selection.suite, selection.scenario), ("movement", "physical-movement"))

    def test_invalid_exact_sha_fails_closed(self) -> None:
        with self.assertRaisesRegex(pr_scenario_selection.SelectionError, "exact lowercase 40-character SHAs"):
            pr_scenario_selection.git_changed_paths(self.root, "main", "head")


if __name__ == "__main__":
    unittest.main()
