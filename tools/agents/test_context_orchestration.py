from __future__ import annotations

import json
import subprocess
import sys
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

LEGACY_TASK = """---
task_id: CAN-LEGACY
program_id: CAN-PROGRAM-E2E-PLATFORM
status: ready_for_merge
agent: legacy-agent
branch: fix/protocolgame-player-session-cleanup
base_branch: main
last_verified_commit: "41f8be155c80c29bc51c4c1ead6ad91e7e2159dc"
related_pr: "blakinio/canary#339"
owned_paths:
  exclusive:
    - src/server/network/protocol/protocolgame.cpp
---

# Goal

Legacy task without a context checkpoint.

# Handoff

Continue from old prose only.
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

    def test_task_template_checkpoint_skeleton_can_be_filled_and_validated(self) -> None:
        template_path = context.REPO_ROOT / "docs/agents/templates/TASK.md"
        block = checkpoint.extract_checkpoint_block(
            template_path.read_text(encoding="utf-8"),
            source=template_path,
        )
        self.assertIsNotNone(block)
        assert block is not None
        filled = block.replace(
            "status: investigating|implementing|validating|blocked|ready",
            "status: implementing",
        ).replace(
            "result: PASS|FAIL|BLOCKED|NOT_RUN",
            "result: NOT_RUN",
        )
        data = checkpoint.parse_checkpoint_block(filled, source=template_path)
        self.assertEqual([], checkpoint.validate_checkpoint(data, source=template_path))

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
            self.assertEqual("123", result["evidence_bundle"]["pr"])
            self.assertIn("PR #123", result["required_reads"])
            self.assertEqual([], result["warnings"])

    def test_checkpointless_legacy_task_uses_explicit_frontmatter_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "legacy-task.md"
            config = root / "routes.json"
            task.write_text(LEGACY_TASK, encoding="utf-8")
            write_config(config)

            result = context.resolve_context(
                task_path=task,
                config_path=config,
                task_text="Continue legacy task",
                github_only=True,
            )
            evidence = result["evidence_bundle"]

            self.assertFalse(result["checkpoint_present"])
            self.assertEqual(
                [context.CHECKPOINT_MISSING_WARNING],
                result["warnings"],
            )
            self.assertEqual(
                "41f8be155c80c29bc51c4c1ead6ad91e7e2159dc",
                evidence["head"],
            )
            self.assertEqual("fix/protocolgame-player-session-cleanup", evidence["branch"])
            self.assertEqual("339", evidence["pr"])
            self.assertEqual("ready_for_merge", evidence["status"])
            self.assertEqual([], evidence["proven"])
            self.assertEqual([], evidence["unknown"])
            self.assertEqual([], evidence["conflicts"])
            self.assertEqual(context.RECOVERY_NEXT_ACTION, evidence["next_action"])
            self.assertIn("PR #339", result["required_reads"])
            self.assertNotIn("PR #blakinio/canary#339", result["required_reads"])

            prompt = resume.render_prompt(result)
            self.assertIn(f"WARNING: {context.CHECKPOINT_MISSING_WARNING}", prompt)
            self.assertIn("PR: 339", prompt)
            self.assertIn(f"NEXT_ACTION: {context.RECOVERY_NEXT_ACTION}", prompt)

    def test_pr_reference_normalization(self) -> None:
        self.assertEqual("339", context.normalize_pr_reference("339"))
        self.assertEqual("339", context.normalize_pr_reference("#339"))
        self.assertEqual("339", context.normalize_pr_reference("blakinio/canary#339"))
        self.assertEqual(
            "339",
            context.normalize_pr_reference("https://github.com/blakinio/canary/pull/339"),
        )

    def test_resume_cli_resolves_repo_relative_paths_from_root_and_tools_directory(self) -> None:
        script = context.REPO_ROOT / "tools/agents/resume.py"
        args = [
            sys.executable,
            str(script),
            "--task",
            "docs/agents/templates/TASK.md",
            "--task-text",
            "Review context handoff",
            "--json",
        ]

        for cwd in (context.REPO_ROOT, context.REPO_ROOT / "tools/agents"):
            with self.subTest(cwd=cwd):
                completed = subprocess.run(
                    args,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertEqual(
                    "docs/agents/templates/TASK.md",
                    payload["task_path"],
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
