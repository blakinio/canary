from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import task_ownership


def write_task(
    root: Path,
    name: str,
    *,
    task_id: str,
    owned: str,
    status: str = "implementing",
    program_id: str = "CAN-PROGRAM-TEST",
    agent: str = "agent",
    branch: str = "feat/test",
) -> Path:
    path = root / f"{name}.md"
    path.write_text(
        f"""---
task_id: {task_id}
program_id: {program_id}
status: {status}
agent: {agent}
branch: {branch}
owned_paths:
{owned}
---
# Task
""",
        encoding="utf-8",
    )
    return path


class TaskOwnershipTests(unittest.TestCase):
    def test_nested_exclusive_paths_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = write_task(root, "a", task_id="A", owned="  exclusive:\n    - src/game/**")
            right = write_task(root, "b", task_id="B", owned="  exclusive:\n    - src/game/player.cpp")
            errors = task_ownership.validate_tasks([left, right])
            self.assertTrue(any("exclusive ownership conflict" in error for error in errors))

    def test_shared_and_read_only_do_not_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = write_task(
                root,
                "a",
                task_id="A",
                owned="  shared:\n    - docs/agents/MODULE_CATALOG.md",
            )
            right = write_task(
                root,
                "b",
                task_id="B",
                owned="  read_only:\n    - docs/agents/MODULE_CATALOG.md",
            )
            self.assertEqual([], task_ownership.validate_tasks([left, right]))

    def test_flat_owned_paths_remain_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(root, "a", task_id="A", owned="  - src/a.cpp")
            _, claims = task_ownership.task_claims(task)
            self.assertEqual("exclusive", claims[0].mode)

    def test_inactive_task_does_not_hold_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            left = write_task(
                root,
                "a",
                task_id="A",
                owned="  exclusive:\n    - src/a.cpp",
                status="done",
            )
            right = write_task(root, "b", task_id="B", owned="  exclusive:\n    - src/a.cpp")
            self.assertEqual([], task_ownership.validate_tasks([left, right]))

    def test_active_task_requires_identity_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(
                root,
                "a",
                task_id="A",
                owned="  exclusive:\n    - src/a.cpp",
                program_id="",
                agent="",
                branch="",
            )
            errors = task_ownership.validate_tasks([task])
            self.assertEqual(3, len(errors))


if __name__ == "__main__":
    unittest.main()
