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
    def test_nested_structured_exclusive_paths_conflict(self) -> None:
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

    def test_legacy_record_is_migration_safe_without_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(
                root,
                "legacy",
                task_id="OLD",
                owned="  - src/a.cpp",
                program_id="",
                agent="",
                branch="",
            )
            record = task_ownership.load_task_record(task)
            self.assertEqual("legacy", record.schema)
            self.assertEqual("legacy_exclusive", record.claims[0].mode)
            self.assertEqual([], task_ownership.validate_tasks([task]))

    def test_legacy_overlap_warns_but_does_not_fail_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = write_task(root, "legacy", task_id="OLD", owned="  - src/game/**")
            structured = write_task(
                root,
                "new",
                task_id="NEW",
                owned="  exclusive:\n    - src/game/player.cpp",
            )
            self.assertEqual([], task_ownership.validate_tasks([legacy, structured]))
            self.assertEqual(1, len(task_ownership.migration_warnings([legacy, structured])))

    def test_strict_legacy_mode_detects_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = write_task(root, "legacy", task_id="OLD", owned="  - src/game/**")
            structured = write_task(
                root,
                "new",
                task_id="NEW",
                owned="  exclusive:\n    - src/game/player.cpp",
            )
            errors = task_ownership.validate_tasks([legacy, structured], strict_legacy=True)
            self.assertTrue(any("exclusive ownership conflict" in error for error in errors))

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

    def test_structured_active_task_requires_identity_fields(self) -> None:
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

    def test_unknown_ownership_mode_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(
                root,
                "a",
                task_id="A",
                owned="  locked:\n    - src/a.cpp",
            )
            errors = task_ownership.validate_tasks([task])
            self.assertTrue(any("unsupported owned_paths mode" in error for error in errors))

    def test_repository_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(
                root,
                "a",
                task_id="A",
                owned="  exclusive:\n    - ../outside",
            )
            errors = task_ownership.validate_tasks([task])
            self.assertTrue(any("must not escape" in error for error in errors))

    def test_rendered_index_contains_source_and_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = write_task(
                root,
                "a",
                task_id="A",
                owned="  exclusive:\n    - src/a.cpp",
            )
            rendered = task_ownership.render_index([task])
            self.assertIn("| structured |", rendered)
            self.assertIn(task.as_posix(), rendered)


if __name__ == "__main__":
    unittest.main()
