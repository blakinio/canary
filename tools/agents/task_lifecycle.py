#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import checkpoint
import task_ownership

DEFAULT_ACTIVE_ROOT = Path("docs/agents/tasks/active")
DEFAULT_ARCHIVE_ROOT = Path("docs/agents/tasks/archive")
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
STATUS_COMPATIBILITY = {
    "planned": {"investigating", "implementing"},
    "implementing": {"investigating", "implementing", "validating", "blocked"},
    "blocked": {"blocked"},
    "review": {"validating", "ready"},
    "ready": {"validating", "ready"},
}


class LifecycleError(ValueError):
    pass


@dataclass(frozen=True)
class ArchiveResult:
    task_id: str
    source: Path
    destination: Path
    related_pr: str


def _task_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path for path in root.rglob("*.md") if path.name.casefold() != "readme.md"
    )


def _resolved_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _normalize_repo_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def changed_active_task_paths(
    changed_paths: Iterable[str],
    *,
    repo_root: Path = Path("."),
    active_root: Path = DEFAULT_ACTIVE_ROOT,
) -> list[Path]:
    repo_root = repo_root.resolve()
    absolute_active = (repo_root / active_root).resolve()
    selected: list[Path] = []

    for raw in changed_paths:
        normalized = _normalize_repo_path(raw)
        if not normalized or not normalized.endswith(".md"):
            continue
        candidate = (repo_root / normalized).resolve()
        if not _resolved_under(candidate, absolute_active):
            continue
        if candidate.name.casefold() == "readme.md" or not candidate.is_file():
            continue
        selected.append(candidate)

    return sorted(dict.fromkeys(selected))


def _all_claim_paths(front: dict[str, object]) -> set[str]:
    owned = front.get("owned_paths", {})
    result: set[str] = set()
    if isinstance(owned, list):
        result.update(_normalize_repo_path(str(item)) for item in owned)
    elif isinstance(owned, dict):
        for values in owned.values():
            if isinstance(values, list):
                result.update(_normalize_repo_path(str(item)) for item in values)
    return {item for item in result if item}


def validate_changed_task(path: Path, *, current_pr: int | None = None) -> list[str]:
    errors = checkpoint.validate_task(path, require_checkpoint=True)
    if errors:
        return errors

    try:
        front = task_ownership.parse_front_matter(path)
        parsed = checkpoint.parse_task_checkpoint(path)
    except (OSError, task_ownership.ParseError, checkpoint.CheckpointError) as exc:
        return [str(exc)]

    if parsed is None:
        return [f"{path}: missing context checkpoint"]

    data = parsed.data
    task_id = str(front.get("task_id", "")).strip()
    task_status = str(front.get("status", "")).strip()
    task_branch = str(front.get("branch", "")).strip()
    related_pr = str(front.get("related_pr", "")).strip()
    cp_status = str(data.get("status", "")).strip()
    cp_branch = str(data.get("branch", "")).strip()
    cp_pr = str(data.get("pr", "")).strip()
    cp_head = str(data.get("head", "")).strip()

    if task_status not in task_ownership.ACTIVE_STATUSES:
        errors.append(
            f"{path}: record under tasks/active has non-active status {task_status!r}"
        )

    compatible = STATUS_COMPATIBILITY.get(task_status)
    if compatible is not None and cp_status not in compatible:
        errors.append(
            f"{path}: task status {task_status!r} is inconsistent with checkpoint status {cp_status!r}"
        )

    if task_branch and cp_branch != task_branch:
        errors.append(
            f"{path}: checkpoint branch {cp_branch!r} does not match frontmatter branch {task_branch!r}"
        )

    if current_pr is not None and related_pr != str(current_pr):
        errors.append(
            f"{path}: changed active task related_pr {related_pr!r} must match current PR {current_pr}"
        )

    if related_pr and cp_pr != related_pr:
        errors.append(
            f"{path}: checkpoint pr {cp_pr!r} does not match frontmatter related_pr {related_pr!r}"
        )

    if related_pr and cp_head.casefold() == "unknown":
        errors.append(
            f"{path}: checkpoint head must be a concrete 40-hex commit once related_pr is known"
        )
    elif cp_head.casefold() != "unknown" and not SHA40.fullmatch(cp_head):
        errors.append(f"{path}: checkpoint head must be UNKNOWN or a 40-hex commit SHA")

    checkpoint_owned = data.get("owned_paths", [])
    if isinstance(checkpoint_owned, list):
        claims = _all_claim_paths(front)
        for value in checkpoint_owned:
            normalized = _normalize_repo_path(str(value))
            if normalized and normalized not in claims:
                errors.append(
                    f"{path}: checkpoint owned path {normalized!r} is not declared in frontmatter owned_paths"
                )

    if not task_id:
        errors.append(f"{path}: missing task_id")

    return errors


def validate_changed_tasks(
    changed_paths: Iterable[str],
    *,
    repo_root: Path = Path("."),
    active_root: Path = DEFAULT_ACTIVE_ROOT,
    current_pr: int | None = None,
) -> tuple[list[Path], list[str]]:
    selected = changed_active_task_paths(
        changed_paths,
        repo_root=repo_root,
        active_root=active_root,
    )
    errors: list[str] = []
    for path in selected:
        errors.extend(validate_changed_task(path, current_pr=current_pr))
    return selected, errors


def tasks_for_pr(active_root: Path, pr_number: int) -> list[Path]:
    wanted = str(pr_number)
    matches: list[Path] = []
    for path in _task_files(active_root):
        try:
            front = task_ownership.parse_front_matter(path)
        except (OSError, task_ownership.ParseError) as exc:
            raise LifecycleError(str(exc)) from exc
        if str(front.get("related_pr", "")).strip() == wanted:
            matches.append(path)
    return matches


def _replace_frontmatter_scalars(
    text: str,
    *,
    status: str,
    completed: str,
    updated: str,
    last_verified_commit: str,
) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise LifecycleError("task record is missing opening frontmatter delimiter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise LifecycleError("task record is missing closing frontmatter delimiter") from exc

    replacements = {
        "status": status,
        "completed": completed,
        "updated": updated,
        "last_verified_commit": last_verified_commit,
    }
    seen: set[str] = set()
    output = list(lines)

    for index in range(1, end):
        raw = lines[index]
        if raw.startswith(" ") or ":" not in raw:
            continue
        key = raw.split(":", 1)[0].strip()
        if key in replacements:
            output[index] = f"{key}: {replacements[key]}"
            seen.add(key)

    inserts = [
        f"{key}: {value}"
        for key, value in replacements.items()
        if key not in seen
    ]
    if inserts:
        output[end:end] = inserts

    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def archive_task(
    path: Path,
    *,
    active_root: Path,
    archive_root: Path,
    pr_number: int,
    merge_commit: str,
    merged_at: str,
    feature_head: str,
    write: bool,
) -> ArchiveResult:
    if not SHA40.fullmatch(merge_commit):
        raise LifecycleError("merge_commit must be a 40-hex commit SHA")
    if not SHA40.fullmatch(feature_head):
        raise LifecycleError("feature_head must be a 40-hex commit SHA")
    if not merged_at.strip():
        raise LifecycleError("merged_at must not be empty")
    if not _resolved_under(path, active_root):
        raise LifecycleError(f"task path escapes active root: {path}")

    front = task_ownership.parse_front_matter(path)
    related_pr = str(front.get("related_pr", "")).strip()
    if related_pr != str(pr_number):
        raise LifecycleError(
            f"{path}: related_pr {related_pr!r} does not match requested PR {pr_number}"
        )

    relative = path.resolve().relative_to(active_root.resolve())
    destination = archive_root.resolve() / relative
    if not _resolved_under(destination, archive_root):
        raise LifecycleError(f"archive destination escapes archive root: {destination}")
    if destination.exists():
        raise LifecycleError(f"archive destination already exists: {destination}")

    text = path.read_text(encoding="utf-8")
    updated = _replace_frontmatter_scalars(
        text,
        status="completed",
        completed=merged_at,
        updated=merged_at,
        last_verified_commit=f'"{merge_commit}"',
    )
    completion = (
        "\n\n## Automated lifecycle completion\n\n"
        f"- Feature PR: #{pr_number}.\n"
        f"- Feature head: `{feature_head}`.\n"
        f"- Merge commit: `{merge_commit}`.\n"
        f"- Merged at: `{merged_at}`.\n"
        "- This record was moved from `tasks/active` by the post-merge lifecycle automation.\n"
    )
    if "## Automated lifecycle completion" not in updated:
        updated = updated.rstrip() + completion

    result = ArchiveResult(
        task_id=str(front.get("task_id", "")).strip(),
        source=path,
        destination=destination,
        related_pr=related_pr,
    )

    if write:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(updated, encoding="utf-8")
        path.unlink()

    return result


def archive_tasks_for_pr(
    *,
    active_root: Path,
    archive_root: Path,
    pr_number: int,
    merge_commit: str,
    merged_at: str,
    feature_head: str,
    write: bool,
) -> list[ArchiveResult]:
    matches = tasks_for_pr(active_root, pr_number)
    results: list[ArchiveResult] = []
    for path in matches:
        results.append(
            archive_task(
                path,
                active_root=active_root,
                archive_root=archive_root,
                pr_number=pr_number,
                merge_commit=merge_commit,
                merged_at=merged_at,
                feature_head=feature_head,
                write=write,
            )
        )
    return results


def _read_changed_file(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate changed agent tasks and archive exact-PR task records after merge."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-changed")
    validate.add_argument("--changed-files-file", type=Path, required=True)
    validate.add_argument("--repo-root", type=Path, default=Path("."))
    validate.add_argument("--active-root", type=Path, default=DEFAULT_ACTIVE_ROOT)
    validate.add_argument("--current-pr", type=int)

    archive = subparsers.add_parser("archive-pr")
    archive.add_argument("--active-root", type=Path, default=DEFAULT_ACTIVE_ROOT)
    archive.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE_ROOT)
    archive.add_argument("--pr-number", type=int, required=True)
    archive.add_argument("--merge-commit", required=True)
    archive.add_argument("--merged-at", required=True)
    archive.add_argument("--feature-head", required=True)
    archive.add_argument("--write", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "validate-changed":
        changed = _read_changed_file(args.changed_files_file)
        selected, errors = validate_changed_tasks(
            changed,
            repo_root=args.repo_root,
            active_root=args.active_root,
            current_pr=args.current_pr,
        )
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Validated {len(selected)} changed active task checkpoint(s).")
        return 0

    results = archive_tasks_for_pr(
        active_root=args.active_root,
        archive_root=args.archive_root,
        pr_number=args.pr_number,
        merge_commit=args.merge_commit,
        merged_at=args.merged_at,
        feature_head=args.feature_head,
        write=args.write,
    )
    for result in results:
        print(
            f"ARCHIVE: {result.task_id} PR#{result.related_pr} "
            f"{result.source.as_posix()} -> {result.destination.as_posix()}"
        )
    print(f"ARCHIVED_COUNT={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
