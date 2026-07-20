from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
RUNNER_SPEC = importlib.util.spec_from_file_location("run_agent_e2e_stdout_test", RUNNER_PATH)
assert RUNNER_SPEC and RUNNER_SPEC.loader
run_agent_e2e = importlib.util.module_from_spec(RUNNER_SPEC)
sys.modules[RUNNER_SPEC.name] = run_agent_e2e
RUNNER_SPEC.loader.exec_module(run_agent_e2e)


class ResolveStdoutPurityTests(unittest.TestCase):
    def test_pr_selection_diagnostic_stays_off_resolve_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            event_path = root / "event.json"
            event_path.write_text(
                json.dumps(
                    {
                        "repository": {"full_name": "blakinio/canary"},
                        "pull_request": {
                            "base": {"sha": "a" * 40},
                            "head": {
                                "sha": "b" * 40,
                                "repo": {"full_name": "blakinio/canary"},
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )

            selection = SimpleNamespace(
                suite="movement",
                scenario="physical-route",
                reason="single-changed-scenario-manifest",
                manifest="tests/e2e/scenarios/movement/physical-route.json",
            )
            selector = SimpleNamespace(
                SelectionError=ValueError,
                select_for_event=mock.Mock(return_value=selection),
            )
            scenario = SimpleNamespace()
            expected_manifest = {"id": "physical-route", "suite": "movement"}
            stdout = io.StringIO()
            stderr = io.StringIO()

            with mock.patch.dict(
                os.environ,
                {
                    "GITHUB_EVENT_NAME": "pull_request",
                    "GITHUB_EVENT_PATH": str(event_path),
                    "GITHUB_REPOSITORY": "blakinio/canary",
                },
                clear=False,
            ), mock.patch.object(
                run_agent_e2e,
                "_load_pr_scenario_selector",
                return_value=selector,
            ), mock.patch.object(
                run_agent_e2e,
                "discover",
                return_value=[scenario],
            ), mock.patch.object(
                run_agent_e2e,
                "select",
                return_value=scenario,
            ), mock.patch.object(
                run_agent_e2e,
                "normalized_manifest",
                return_value=expected_manifest,
            ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = run_agent_e2e.main(
                    [
                        "--root",
                        str(root),
                        "resolve",
                        "--suite",
                        "login",
                        "--scenario",
                        "relog",
                    ]
                )

            self.assertEqual(result, 0)
            self.assertEqual(json.loads(stdout.getvalue()), expected_manifest)
            self.assertNotIn("Pull-request scenario selection:", stdout.getvalue())
            self.assertIn("Pull-request scenario selection:", stderr.getvalue())
            selector.select_for_event.assert_called_once()


if __name__ == "__main__":
    unittest.main()
