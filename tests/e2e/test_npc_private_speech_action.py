from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "tools" / "e2e" / "run_agent_e2e.py"
CLIENT_PATH = ROOT / "tools" / "e2e" / "client" / "agent_e2e_scenario.lua"


def load_runner():
    spec = importlib.util.spec_from_file_location("canary_e2e_run_agent_e2e_npc_private_test", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load E2E runner: {RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RUNNER = load_runner()


class NpcPrivateSpeechActionTests(unittest.TestCase):
    def test_talk_npc_validates_and_renders_receiver_and_text(self) -> None:
        step = {
            "id": "promotion-offer",
            "action": "talk_npc",
            "receiver": "Canary",
            "text": "promot",
        }
        self.assertEqual(RUNNER._validate_step(step, 0), step)

        scenario = RUNNER.Scenario(
            path=Path("tests/e2e/scenarios/npc/example.json"),
            data={
                "suite": "npc",
                "id": "example",
                "steps": [step],
                "assertions": {"persistence": []},
            },
        )
        route_execution = SimpleNamespace(
            load_route_plans=lambda steps, artifact_dir: {},
            render_routes_lua=lambda routes, indent: "{}",
            RoutePlanExecutionError=ValueError,
        )
        persistence = SimpleNamespace(validate_persistence_assertions=lambda assertions: [])
        with (
            mock.patch.object(RUNNER, "_load_route_plan_execution", return_value=route_execution),
            mock.patch.object(RUNNER, "_load_persistence_assertions", return_value=persistence),
        ):
            rendered = RUNNER.render_lua_plan(scenario)

        self.assertIn('action = "talk_npc"', rendered)
        self.assertIn('receiver = "Canary"', rendered)
        self.assertIn('text = "promot"', rendered)

    def test_talk_npc_requires_safe_receiver(self) -> None:
        with self.assertRaisesRegex(RUNNER.ScenarioError, r"receiver must be a non-empty string"):
            RUNNER._validate_step(
                {"id": "missing-receiver", "action": "talk_npc", "text": "yes"},
                0,
            )

        with self.assertRaisesRegex(RUNNER.ScenarioError, r"receiver must not contain control newlines or NUL"):
            RUNNER._validate_step(
                {
                    "id": "unsafe-receiver",
                    "action": "talk_npc",
                    "receiver": "Canary\nother",
                    "text": "yes",
                },
                0,
            )

    def test_talk_npc_rejects_arbitrary_message_mode(self) -> None:
        with self.assertRaisesRegex(RUNNER.ScenarioError, r"unknown field\(s\): mode"):
            RUNNER._validate_step(
                {
                    "id": "arbitrary-mode",
                    "action": "talk_npc",
                    "receiver": "Canary",
                    "text": "yes",
                    "mode": "NpcTo",
                },
                0,
            )

    def test_controlled_client_uses_fixed_npc_to_mode_and_preserves_public_talk(self) -> None:
        source = CLIENT_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "g_game.talkPrivate(MessageModes.NpcTo, step.receiver, step.text)",
            source,
        )
        self.assertIn("g_game.talk(step.text)", source)


if __name__ == "__main__":
    unittest.main()
