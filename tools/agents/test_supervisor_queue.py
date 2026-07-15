from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import supervisor_queue


TASK_TEMPLATE = """---
task_id: {task_id}
program_id: CAN-PROGRAM-TEST
status: implementing
agent: test-agent
branch: {branch}
related_pr: "999"
owned_paths:
  exclusive:
{exclusive}
  shared:
{shared}
  read_only: []
---

# Goal

Test task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T18:40:00Z
head: 0123456789012345678901234567890123456789
branch: {branch}
pr: 999
status: implementing
context_routes:
  - agent-governance
owned_paths:
{checkpoint_paths}
proven:
  - bounded test evidence exists
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
next_action: Execute the bounded test task.
```
"""


def _yaml_paths(paths: list[str], indent: int) -> str:
    prefix = " " * indent
    if not paths:
        return f"{prefix}[]"
    return "\n".join(f"{prefix}- {path}" for path in paths)


def write_task(root: Path, name: str, branch: str, exclusive: list[str], shared: list[str] | None = None) -> Path:
    shared = shared or []
    path = root / "docs" / "agents" / "tasks" / "active" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_paths = exclusive + shared
    path.write_text(
        TASK_TEMPLATE.format(
            task_id=name,
            branch=branch,
            exclusive=_yaml_paths(exclusive, 4),
            shared=_yaml_paths(shared, 4),
            checkpoint_paths=_yaml_paths(checkpoint_paths, 2),
        ),
        encoding="utf-8",
    )
    return path


def write_config(root: Path) -> Path:
    path = root / "routes.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "budget_policy": "minimize_agentic_usage",
                "limits": {
                    "max_required_reads": 8,
                    "max_search_first": 4,
                    "max_optional_reads": 3,
                    "max_proven": 4,
                    "max_unknown": 4,
                    "max_conflicts": 4,
                    "max_changed_paths": 4,
                    "max_validation": 4,
                    "max_blockers": 4,
                },
                "core_reads": ["AGENTS.md"],
                "routes": {
                    "agent-governance": {
                        "path_globs": ["tools/agents/**"],
                        "keywords": ["agent"],
                        "required_reads": [],
                        "search_first": [],
                        "optional_reads": [],
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return path


class SupervisorQueueTests(unittest.TestCase):
    def test_non_overlapping_codex_and_work_can_share_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = write_config(root)
            codex = write_task(root, "CAN-CODEX", "feat/codex", ["src/a/**"])
            work = write_task(root, "CAN-WORK", "docs/work", ["docs/report/**"])
            data = {
                "schema_version": 1,
                "queue_id": "CAN-QUEUE-TEST",
                "budget_policy": "minimize_agentic_usage",
                "max_parallel": 2,
                "items": [
                    {
                        "id": "codex",
                        "task": codex.relative_to(root).as_posix(),
                        "task_text": "Implement and run tests",
                        "needs_local_execution": True,
                    },
                    {
                        "id": "work",
                        "task": work.relative_to(root).as_posix(),
                        "task_text": "Prepare broad multi-source research report",
                        "broad_research": True,
                        "large_deliverable": True,
                    },
                ],
            }
            plan = supervisor_queue.plan_queue(data, repo_root=root, config_path=config)
            self.assertEqual(1, len(plan.batches))
            self.assertEqual({"codex", "work"}, {item.id for item in plan.batches[0]})
            self.assertEqual({"CODEX", "WORK"}, {item.mode for item in plan.batches[0]})

    def test_overlapping_write_claims_serialize(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = write_config(root)
            first = write_task(root, "CAN-ONE", "feat/one", ["src/game/**"])
            second = write_task(root, "CAN-TWO", "feat/two", ["src/game/game.cpp"])
            data = {
                "schema_version": 1,
                "queue_id": "CAN-QUEUE-CONFLICT",
                "budget_policy": "minimize_agentic_usage",
                "max_parallel": 2,
                "items": [
                    {"id": "one", "task": first.relative_to(root).as_posix(), "needs_local_execution": True},
                    {"id": "two", "task": second.relative_to(root).as_posix(), "needs_local_execution": True},
                ],
            }
            plan = supervisor_queue.plan_queue(data, repo_root=root, config_path=config)
            self.assertEqual(2, len(plan.batches))
            self.assertEqual(["one"], [item.id for item in plan.batches[0]])
            self.assertEqual(["two"], [item.id for item in plan.batches[1]])

    def test_dependency_orders_batches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = write_config(root)
            first = write_task(root, "CAN-A", "feat/a", ["src/a/**"])
            second = write_task(root, "CAN-B", "feat/b", ["src/b/**"])
            data = {
                "schema_version": 1,
                "queue_id": "CAN-QUEUE-DEPS",
                "budget_policy": "minimize_agentic_usage",
                "max_parallel": 2,
                "items": [
                    {"id": "a", "task": first.relative_to(root).as_posix(), "needs_local_execution": True},
                    {"id": "b", "task": second.relative_to(root).as_posix(), "needs_local_execution": True, "depends_on": ["a"]},
                ],
            }
            plan = supervisor_queue.plan_queue(data, repo_root=root, config_path=config)
            self.assertEqual([["a"], ["b"]], [[item.id for item in batch] for batch in plan.batches])

    def test_chat_item_stays_coordinator_side(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = write_config(root)
            task = write_task(root, "CAN-CHAT", "docs/chat", ["docs/plan.md"])
            data = {
                "schema_version": 1,
                "queue_id": "CAN-QUEUE-CHAT",
                "budget_policy": "minimize_agentic_usage",
                "max_parallel": 2,
                "items": [
                    {
                        "id": "chat",
                        "task": task.relative_to(root).as_posix(),
                        "task_text": "Analyze PR and CI on GitHub",
                        "github_only": True,
                    }
                ],
            }
            plan = supervisor_queue.plan_queue(data, repo_root=root, config_path=config)
            self.assertEqual("CHAT", plan.coordinator_items[0].mode)
            self.assertFalse(plan.coordinator_items[0].dispatch)
            self.assertEqual((), plan.batches)

    def test_cycle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            first = write_task(root, "CAN-A", "feat/a", ["src/a/**"])
            second = write_task(root, "CAN-B", "feat/b", ["src/b/**"])
            data = {
                "schema_version": 1,
                "queue_id": "CAN-QUEUE-CYCLE",
                "budget_policy": "minimize_agentic_usage",
                "max_parallel": 2,
                "items": [
                    {"id": "a", "task": first.relative_to(root).as_posix(), "depends_on": ["b"]},
                    {"id": "b", "task": second.relative_to(root).as_posix(), "depends_on": ["a"]},
                ],
            }
            errors = supervisor_queue.validate_queue(data, repo_root=root)
            self.assertTrue(any("cycle" in error for error in errors))

    def test_same_branch_serializes_workers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = write_config(root)
            first = write_task(root, "CAN-A", "feat/shared", ["src/a/**"])
            second = write_task(root, "CAN-B", "feat/shared", ["src/b/**"])
            data = {
                "schema_version": 1,
                "queue_id": "CAN-QUEUE-BRANCH",
                "budget_policy": "minimize_agentic_usage",
                "max_parallel": 2,
                "items": [
                    {"id": "a", "task": first.relative_to(root).as_posix(), "needs_local_execution": True},
                    {"id": "b", "task": second.relative_to(root).as_posix(), "needs_local_execution": True},
                ],
            }
            plan = supervisor_queue.plan_queue(data, repo_root=root, config_path=config)
            self.assertEqual(2, len(plan.batches))

    def test_worker_prompt_is_bounded_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = write_config(root)
            task = write_task(root, "CAN-CODEX", "feat/codex", ["src/a/**"])
            data = {
                "schema_version": 1,
                "queue_id": "CAN-QUEUE-PROMPT",
                "budget_policy": "minimize_agentic_usage",
                "max_parallel": 1,
                "items": [
                    {"id": "codex", "task": task.relative_to(root).as_posix(), "needs_local_execution": True}
                ],
            }
            plan = supervisor_queue.plan_queue(data, repo_root=root, config_path=config)
            prompt = plan.batches[0][0].prompt
            self.assertIn("Continue task CAN-CODEX", prompt)
            self.assertIn("Do not rely on previous chat history", prompt)
            self.assertIn("bounded test evidence exists", prompt)
            self.assertNotIn("full previous conversation", prompt)


if __name__ == "__main__":
    unittest.main()
