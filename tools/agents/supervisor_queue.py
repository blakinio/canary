#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import resume
import task_ownership

DEFAULT_BUDGET_POLICY = "minimize_agentic_usage"
VALID_TARGET_MODES = {"auto", "chat", "codex", "work"}
MAX_ITEMS = 64
MAX_PARALLEL = 16


class QueueError(ValueError):
    pass


@dataclass(frozen=True)
class PlannedItem:
    id: str
    task: str
    mode: str
    branch: str
    worktree: str | None
    dependencies: tuple[str, ...]
    dispatch: bool
    reason: str
    prompt: str


@dataclass(frozen=True)
class QueuePlan:
    queue_id: str
    budget_policy: str
    max_parallel: int
    completed: tuple[str, ...]
    coordinator_items: tuple[PlannedItem, ...]
    batches: tuple[tuple[PlannedItem, ...], ...]


def _repo_relative_path(value: str) -> Path:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    path = Path(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts:
        raise QueueError(f"task path must be repository-relative and confined: {value!r}")
    return path


def _list_of_strings(value: object, *, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise QueueError(f"{field} must be a list")
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if not text:
            raise QueueError(f"{field} must not contain empty values")
        if text in result:
            raise QueueError(f"{field} contains duplicate value {text!r}")
        result.append(text)
    return result


def load_queue(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise QueueError("queue root must be an object")
    return data


def validate_queue(data: dict[str, object], *, repo_root: Path = Path(".")) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    queue_id = str(data.get("queue_id", "")).strip()
    if not queue_id:
        errors.append("queue_id must not be empty")

    budget_policy = str(data.get("budget_policy", DEFAULT_BUDGET_POLICY)).strip()
    if budget_policy not in {"minimize_agentic_usage", "balanced", "capability_first"}:
        errors.append(f"unsupported budget_policy {budget_policy!r}")

    try:
        max_parallel = int(data.get("max_parallel", 1))
    except (TypeError, ValueError):
        max_parallel = 0
    if not 1 <= max_parallel <= MAX_PARALLEL:
        errors.append(f"max_parallel must be between 1 and {MAX_PARALLEL}")

    items = data.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
        return errors
    if len(items) > MAX_ITEMS:
        errors.append(f"items must contain at most {MAX_ITEMS} entries")

    try:
        completed = set(_list_of_strings(data.get("completed", []), field="completed"))
    except QueueError as exc:
        errors.append(str(exc))
        completed = set()

    ids: list[str] = []
    dependencies: dict[str, list[str]] = {}
    for index, raw in enumerate(items):
        prefix = f"items[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{prefix} must be an object")
            continue
        item_id = str(raw.get("id", "")).strip()
        if not item_id:
            errors.append(f"{prefix}.id must not be empty")
            continue
        if item_id in ids:
            errors.append(f"duplicate item id {item_id!r}")
        ids.append(item_id)

        mode = str(raw.get("target_mode", "auto")).strip().casefold()
        if mode not in VALID_TARGET_MODES:
            errors.append(f"{prefix}.target_mode has unsupported value {mode!r}")

        try:
            deps = _list_of_strings(raw.get("depends_on", []), field=f"{prefix}.depends_on")
        except QueueError as exc:
            errors.append(str(exc))
            deps = []
        dependencies[item_id] = deps

        task_value = str(raw.get("task", "")).strip()
        try:
            task_path = _repo_relative_path(task_value)
        except QueueError as exc:
            errors.append(f"{prefix}: {exc}")
            continue
        absolute = (repo_root / task_path).resolve()
        try:
            absolute.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"{prefix}.task escapes repository root")
            continue
        if not absolute.is_file():
            errors.append(f"{prefix}.task does not exist: {task_path.as_posix()}")
            continue
        try:
            record = task_ownership.load_task_record(absolute)
        except (OSError, task_ownership.ParseError) as exc:
            errors.append(f"{prefix}.task invalid: {exc}")
            continue
        if record.status not in task_ownership.ACTIVE_STATUSES:
            errors.append(
                f"{prefix}.task must reference an active task; "
                f"{record.task_id} has status {record.status!r}"
            )

    known = set(ids) | completed
    for item_id, deps in dependencies.items():
        for dep in deps:
            if dep not in known:
                errors.append(f"item {item_id!r} depends on unknown item {dep!r}")
            if dep == item_id:
                errors.append(f"item {item_id!r} cannot depend on itself")

    # Cycle detection ignores dependencies already listed as completed.
    graph = {item_id: [dep for dep in deps if dep in dependencies] for item_id, deps in dependencies.items()}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            raise QueueError(f"dependency cycle detected at {node!r}")
        visiting.add(node)
        for dep in graph.get(node, []):
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    try:
        for node in graph:
            visit(node)
    except QueueError as exc:
        errors.append(str(exc))

    return errors


def _write_claims(record: task_ownership.TaskRecord) -> tuple[str, ...]:
    return tuple(claim.path for claim in record.claims if claim.mode != "read_only")


def _items_conflict(
    left_record: task_ownership.TaskRecord,
    right_record: task_ownership.TaskRecord,
) -> bool:
    if left_record.branch and left_record.branch == right_record.branch:
        return True
    for left in _write_claims(left_record):
        for right in _write_claims(right_record):
            if task_ownership.patterns_overlap(left, right):
                return True
    return False


def _worktree_path(queue_id: str, item_id: str) -> str:
    safe_queue = "".join(char if char.isalnum() or char in "-_" else "-" for char in queue_id)
    safe_item = "".join(char if char.isalnum() or char in "-_" else "-" for char in item_id)
    return f".worktrees/{safe_queue}-{safe_item}"


def plan_queue(
    data: dict[str, object],
    *,
    repo_root: Path = Path("."),
    config_path: Path = resume.context_tool.DEFAULT_CONFIG,
) -> QueuePlan:
    errors = validate_queue(data, repo_root=repo_root)
    if errors:
        raise QueueError("; ".join(errors))

    queue_id = str(data["queue_id"])
    budget_policy = str(data.get("budget_policy", DEFAULT_BUDGET_POLICY))
    max_parallel = int(data.get("max_parallel", 1))
    completed = tuple(_list_of_strings(data.get("completed", []), field="completed"))
    completed_set = set(completed)
    raw_items = data["items"]
    assert isinstance(raw_items, list)

    entries: dict[str, tuple[dict[str, object], task_ownership.TaskRecord, PlannedItem]] = {}
    order: list[str] = []

    for raw in raw_items:
        assert isinstance(raw, dict)
        item_id = str(raw["id"])
        task_rel = _repo_relative_path(str(raw["task"]))
        task_path = (repo_root / task_rel).resolve()
        record = task_ownership.load_task_record(task_path)
        target_mode = str(raw.get("target_mode", "auto")).casefold()
        result = resume.build_resume_bundle(
            task_path=task_path,
            config_path=config_path,
            task_text=str(raw.get("task_text", "")),
            changed_paths=_list_of_strings(raw.get("changed_paths", []), field=f"{item_id}.changed_paths"),
            extra_routes=_list_of_strings(raw.get("extra_routes", []), field=f"{item_id}.extra_routes"),
            needs_local_execution=bool(raw.get("needs_local_execution", False)),
            broad_research=bool(raw.get("broad_research", False)),
            large_deliverable=bool(raw.get("large_deliverable", False)),
            parallel_workers=bool(raw.get("parallel_workers", False)),
            github_only=bool(raw.get("github_only", False)),
            budget_policy=budget_policy,
            target_mode=target_mode,
        )
        mode_data = result.get("execution_mode", {})
        mode = str(mode_data.get("mode", "CHAT")) if isinstance(mode_data, dict) else "CHAT"
        deps = tuple(_list_of_strings(raw.get("depends_on", []), field=f"{item_id}.depends_on"))
        dispatch = mode in {"CODEX", "WORK"}
        reason = (
            "bounded external worker candidate"
            if dispatch
            else "keep in CHAT coordinator; no scarce agentic worker is justified"
        )
        planned = PlannedItem(
            id=item_id,
            task=task_rel.as_posix(),
            mode=mode,
            branch=record.branch,
            worktree=_worktree_path(queue_id, item_id) if mode == "CODEX" else None,
            dependencies=deps,
            dispatch=dispatch,
            reason=reason,
            prompt=resume.render_prompt(result),
        )
        entries[item_id] = (raw, record, planned)
        order.append(item_id)

    coordinator = tuple(entries[item_id][2] for item_id in order if not entries[item_id][2].dispatch)
    remaining = [item_id for item_id in order if entries[item_id][2].dispatch]
    done = set(completed_set)
    # CHAT coordinator items are considered locally satisfiable prerequisites for queue planning.
    done.update(item.id for item in coordinator)
    batches: list[tuple[PlannedItem, ...]] = []

    while remaining:
        ready = [
            item_id
            for item_id in remaining
            if all(dep in done for dep in entries[item_id][2].dependencies)
        ]
        if not ready:
            blocked = ", ".join(remaining)
            raise QueueError(f"no dispatchable item is ready; unresolved dependencies for: {blocked}")

        batch_ids: list[str] = []
        for candidate in ready:
            candidate_record = entries[candidate][1]
            if any(
                _items_conflict(candidate_record, entries[selected][1])
                for selected in batch_ids
            ):
                continue
            batch_ids.append(candidate)
            if len(batch_ids) >= max_parallel:
                break

        if not batch_ids:
            batch_ids = [ready[0]]

        batch = tuple(entries[item_id][2] for item_id in batch_ids)
        batches.append(batch)
        for item_id in batch_ids:
            remaining.remove(item_id)
            done.add(item_id)

    return QueuePlan(
        queue_id=queue_id,
        budget_policy=budget_policy,
        max_parallel=max_parallel,
        completed=completed,
        coordinator_items=coordinator,
        batches=tuple(batches),
    )


def plan_to_dict(plan: QueuePlan) -> dict[str, object]:
    return {
        "queue_id": plan.queue_id,
        "budget_policy": plan.budget_policy,
        "max_parallel": plan.max_parallel,
        "completed": list(plan.completed),
        "coordinator_items": [asdict(item) for item in plan.coordinator_items],
        "batches": [[asdict(item) for item in batch] for batch in plan.batches],
    }


def render_markdown(plan: QueuePlan) -> str:
    lines = [
        f"# Supervisor Queue `{plan.queue_id}`",
        "",
        f"Budget policy: `{plan.budget_policy}`",
        f"Maximum parallel workers: {plan.max_parallel}",
        "",
        "## CHAT coordinator items",
    ]
    if not plan.coordinator_items:
        lines.append("- none")
    for item in plan.coordinator_items:
        lines.append(f"- `{item.id}` — {item.mode}: {item.reason}")

    lines.extend(["", "## Worker batches"])
    if not plan.batches:
        lines.append("- none")
    for index, batch in enumerate(plan.batches, start=1):
        lines.append(f"### Batch {index}")
        for item in batch:
            suffix = f"; worktree `{item.worktree}`" if item.worktree else ""
            lines.append(
                f"- `{item.id}` — {item.mode}; task `{item.task}`; branch `{item.branch}`{suffix}"
            )
    lines.extend(
        [
            "",
            "The plan does not spawn agents or create worktrees. An external/higher-license orchestrator may consume only the listed bounded worker prompts and must keep repository ownership, CI and branch protection in force.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and plan bounded CHAT/CODEX/WORK supervisor queues without spawning agents."
    )
    parser.add_argument("queue", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, default=resume.context_tool.DEFAULT_CONFIG)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        plan = plan_queue(
            load_queue(args.queue),
            repo_root=args.repo_root,
            config_path=args.config,
        )
    except (OSError, json.JSONDecodeError, QueueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.json:
        print(json.dumps(plan_to_dict(plan), indent=2))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
