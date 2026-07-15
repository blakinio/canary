from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import task_lifecycle


MERGE_SHA = "a" * 40
FEATURE_SHA = "b" * 40


def write_task(
    root: Path,
    *,
    name: str = "CAN-TEST.md",
    related_pr: str = "391",
    branch: str = "feat/test",
    checkpoint_branch: str | None = None,
    checkpoint_pr: str | None = None,
    checkpoint_head: str = FEATURE_SHA,
    include_checkpoint: bool = True,
) -> Path:
    active = root / "docs/agents/tasks/active"
    active.mkdir(parents=True, exist_ok=True)
    path = active / name
    cp_branch = checkpoint_branch if checkpoint_branch is not None else branch
    cp_pr = checkpoint_pr if checkpoint_pr is not None else (related_pr or "none")
    checkpoint_text = ""
    if include_checkpoint:
        checkpoint_text = f"""
## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T16:00:00Z
head: {checkpoint_head}
branch: {cp_branch}
pr: {cp_pr}
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - tools/agents/task_lifecycle.py
proven:
  - deterministic task record exists
derived:
  - lifecycle validation can inspect it
unknown:
  - final CI
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - none
changed_paths:
  - tools/agents/task_lifecycle.py
validation:
  - command: unit test
    result: PASS
    evidence: fixture
blockers:
  - none
next_action: Run the next bounded validation step.
```
"""
    path.write_text(
        f"""---
task_id: CAN-TEST
program_id: CAN-PROGRAM-TEST
status: implementing
agent: test-agent
branch: {branch}
base_branch: main
created: 2026-07-15T16:00:00Z
updated: 2026-07-15T16:00:00Z
last_verified_commit: \"{FEATURE_SHA}\"
related_pr: \"{related_pr}\"
owned_paths:
  exclusive:
    - tools/agents/task_lifecycle.py
---

# Goal

Test lifecycle.
{checkpoint_text}
""",
        encoding="utf-8",
    )
    return path


class ChangedTaskValidationTests(unittest.TestCase):
    def test_only_changed_active_tasks_are_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(root)
            selected, errors = task_lifecycle.validate_changed_tasks(
                [
                    "README.md",
                    "docs/agents/tasks/archive/OLD.md",
                    task.relative_to(root).as_posix(),
                ],
                repo_root=root,
            )
            self.assertEqual([], errors)
            self.assertEqual([task.resolve()], selected)

    def test_changed_active_task_requires_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(root, include_checkpoint=False)
            _, errors = task_lifecycle.validate_changed_tasks(
                [task.relative_to(root).as_posix()],
                repo_root=root,
            )
            self.assertTrue(any("missing ## Context checkpoint" in error for error in errors))

    def test_frontmatter_and_checkpoint_branch_must_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(root, checkpoint_branch="feat/other")
            _, errors = task_lifecycle.validate_changed_tasks(
                [task.relative_to(root).as_posix()],
                repo_root=root,
            )
            self.assertTrue(any("does not match frontmatter branch" in error for error in errors))

    def test_known_related_pr_requires_matching_checkpoint_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(root, related_pr="391", checkpoint_pr="999")
            _, errors = task_lifecycle.validate_changed_tasks(
                [task.relative_to(root).as_posix()],
                repo_root=root,
            )
            self.assertTrue(any("does not match frontmatter related_pr" in error for error in errors))

    def test_pull_request_changed_task_must_claim_current_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(root, related_pr="390")
            _, errors = task_lifecycle.validate_changed_tasks(
                [task.relative_to(root).as_posix()],
                repo_root=root,
                current_pr=391,
            )
            self.assertTrue(any("must match current PR 391" in error for error in errors))

    def test_known_related_pr_requires_concrete_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(root, checkpoint_head="UNKNOWN")
            _, errors = task_lifecycle.validate_changed_tasks(
                [task.relative_to(root).as_posix()],
                repo_root=root,
            )
            self.assertTrue(any("concrete 40-hex commit" in error for error in errors))


class ArchiveTests(unittest.TestCase):
    def test_tasks_for_pr_matches_exact_related_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "docs/agents/tasks/active"
            matching = write_task(root, name="match.md", related_pr="391")
            write_task(root, name="other.md", related_pr="1391")
            self.assertEqual([matching], task_lifecycle.tasks_for_pr(active, 391))

    def test_archive_moves_exact_task_and_updates_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "docs/agents/tasks/active"
            archive = root / "docs/agents/tasks/archive"
            task = write_task(root, related_pr="391")

            results = task_lifecycle.archive_tasks_for_pr(
                active_root=active,
                archive_root=archive,
                pr_number=391,
                merge_commit=MERGE_SHA,
                merged_at="2026-07-15T17:00:00Z",
                feature_head=FEATURE_SHA,
                write=True,
            )

            self.assertEqual(1, len(results))
            self.assertFalse(task.exists())
            destination = archive / task.name
            self.assertTrue(destination.exists())
            text = destination.read_text(encoding="utf-8")
            self.assertIn("status: completed", text)
            self.assertIn("completed: 2026-07-15T17:00:00Z", text)
            self.assertIn(f'last_verified_commit: "{MERGE_SHA}"', text)
            self.assertIn("## Automated lifecycle completion", text)
            self.assertIn("Feature PR: #391", text)

    def test_no_matching_pr_is_a_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "docs/agents/tasks/active"
            archive = root / "docs/agents/tasks/archive"
            task = write_task(root, related_pr="391")
            results = task_lifecycle.archive_tasks_for_pr(
                active_root=active,
                archive_root=archive,
                pr_number=392,
                merge_commit=MERGE_SHA,
                merged_at="2026-07-15T17:00:00Z",
                feature_head=FEATURE_SHA,
                write=True,
            )
            self.assertEqual([], results)
            self.assertTrue(task.exists())

    def test_archive_rejects_source_outside_active_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "docs/agents/tasks/active"
            archive = root / "docs/agents/tasks/archive"
            outside = root / "outside.md"
            outside.write_text("---\ntask_id: X\nrelated_pr: \"391\"\n---\n", encoding="utf-8")
            with self.assertRaises(task_lifecycle.LifecycleError):
                task_lifecycle.archive_task(
                    outside,
                    active_root=active,
                    archive_root=archive,
                    pr_number=391,
                    merge_commit=MERGE_SHA,
                    merged_at="2026-07-15T17:00:00Z",
                    feature_head=FEATURE_SHA,
                    write=False,
                )


if __name__ == "__main__":
    unittest.main()
