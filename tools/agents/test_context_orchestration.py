from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import checkpoint
import context
import execution_mode
import resume


VALID_TASK = """---
task_id: CAN-TEST
program_id: CAN-PROGRAM-TEST
status: implementing
agent: test-agent
branch: feat/test
related_pr: "123"
owned_paths:
  exclusive:
    - tools/agents/context.py
---

# Goal

Test task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T16:00:00Z
head: 0123456789012345678901234567890123456789
branch: feat/test
pr: 123
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - tools/agents/context.py
proven:
  - ownership tooling exists
derived:
  - routing can reuse task state
unknown:
  - current head CI
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - full chat replay: unnecessary
changed_paths:
  - tools/agents/context.py
validation:
  - command: unit tests
    result: PASS
    evidence: local
blockers:
  - none
next_action: Run focused unit tests.
```
"""


def write_config(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "budget_policy": "minimize_agentic_usage",
                "limits": {
                    "max_required_reads": 8,
                    "max_search_first": 5,
                    "max_optional_reads": 4,
                    "max_proven": 4,
                    "max_unknown": 4,
                    "max_conflicts": 4,
                    "max_changed_paths": 4,
                    "max_validation": 4,
                    "max_blockers": 4,
                },
                "core_reads": [
                    "AGENTS.md",
                    "docs/agents/REPOSITORY_MAP.md",
                    "docs/agents/CONTEXT_ROUTING.md",
                ],
                "routes": {
                    "agent-governance": {
                        "path_globs": ["tools/agents/**", "docs/agents/**"],
                        "keywords": ["agent", "context"],
                        "required_reads": [
                            "docs/agents/CONTEXT_HANDOFF.md",
                            "docs/agents/EXECUTION_MODE_ROUTING.md",
                        ],
                        "search_first": ["docs/agents/MODULE_CATALOG.md"],
                        "optional_reads": [
                            "docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md"
                        ],
                    },
                    "cpp-runtime": {
                        "path_globs": ["src/**"],
                        "keywords": ["runtime"],
                        "required_reads": [],
                        "search_first": ["docs/agents/BUILD_TEST_MATRIX.md"],
                        "optional_reads": [],
                    },
                },
            }
        ),
        encoding="utf-8",
    )


class CheckpointTests(unittest.TestCase):
    def test_valid_checkpoint_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = Path(tmp) / "task.md"
            task.write_text(VALID_TASK, encoding="utf-8")
            self.assertEqual([], checkpoint.validate_task(task, require_checkpoint=True))

    def test_duplicate_next_action_is_rejected(self) -> None:
        block = """
checkpoint_version: 1
updated_at: now
head: UNKNOWN
branch: feat/test
pr: none
status: implementing
context_routes: []
owned_paths: []
proven: []
derived: []
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses: []
changed_paths: []
validation: []
blockers: []
next_action: first
next_action: second
"""
        with self.assertRaises(checkpoint.CheckpointError):
            checkpoint.parse_checkpoint_block(block)

    def test_evidence_fact_cannot_be_proven_and_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = Path(tmp) / "task.md"
            task.write_text(
                VALID_TASK.replace(
                    "unknown:\n  - current head CI",
                    "unknown:\n  - ownership tooling exists",
                ),
                encoding="utf-8",
            )
            errors = checkpoint.validate_task(task, require_checkpoint=True)
            self.assertTrue(any("both proven and unknown" in error for error in errors))


class ExecutionModeTests(unittest.TestCase):
    def test_chat_is_default_for_pr_ci_triage(self) -> None:
        recommendation = execution_mode.recommend_mode(
            task_text="Analyze PR and CI failure on GitHub",
            github_only=True,
        )
        self.assertEqual("CHAT", recommendation.mode)
        self.assertEqual("minimize_agentic_usage", recommendation.budget_policy)

    def test_codex_requires_execution_value(self) -> None:
        recommendation = execution_mode.recommend_mode(
            task_text="Fix runtime race and run tests",
            changed_paths=["src/game/game.cpp"],
            needs_local_execution=True,
        )
        self.assertEqual("CODEX", recommendation.mode)
        self.assertIn("Return to CHAT", recommendation.return_policy)

    def test_work_is_for_broad_research(self) -> None:
        recommendation = execution_mode.recommend_mode(
            task_text="Prepare a multi-source research report",
            broad_research=True,
            large_deliverable=True,
        )
        self.assertEqual("WORK", recommendation.mode)

    def test_runtime_path_alone_does_not_spend_agentic_budget(self) -> None:
        recommendation = execution_mode.recommend_mode(
            task_text="Analyze architecture around runtime ownership",
            changed_paths=["src/game/game.cpp"],
        )
        self.assertEqual("CHAT", recommendation.mode)


class ContextAndResumeTests(unittest.TestCase):
    def test_context_resolver_is_bounded_and_route_driven(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "task.md"
            config = root / "routes.json"
            task.write_text(VALID_TASK, encoding="utf-8")
            write_config(config)

            result = context.resolve_context(
                task_path=task,
                config_path=config,
                task_text="Review agent context handoff",
                github_only=True,
            )

            self.assertIn("agent-governance", result["routes"])
            self.assertLessEqual(len(result["required_reads"]), 8)
            self.assertIn(
                "docs/agents/CONTEXT_HANDOFF.md",
                result["required_reads"],
            )
            self.assertEqual("CHAT", result["execution_mode"]["mode"])
            self.assertEqual(
                ["ownership tooling exists"],
                result["evidence_bundle"]["proven"],
            )

    def test_resume_prompt_contains_compact_execution_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "task.md"
            config = root / "routes.json"
            task.write_text(VALID_TASK, encoding="utf-8")
            write_config(config)

            result = resume.build_resume_bundle(
                task_path=task,
                config_path=config,
                task_text="Fix runtime race and run tests",
                changed_paths=["src/game/game.cpp"],
                needs_local_execution=True,
            )
            prompt = resume.render_prompt(result)

            self.assertIn("RECOMMENDED_MODE: CODEX", prompt)
            self.assertIn("ownership tooling exists", prompt)
            self.assertIn("NEXT_ACTION: Run focused unit tests.", prompt)
            self.assertIn(
                "Return coordination to CHAT",
                prompt.replace("return coordination", "Return coordination"),
            )
            self.assertNotIn("full previous conversation", prompt)


if __name__ == "__main__":
    unittest.main()
