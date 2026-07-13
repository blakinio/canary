#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ACTIVE_STATUSES = {"planned", "implementing", "blocked", "review", "ready"}
OWNERSHIP_MODES = {"exclusive", "shared", "read_only"}


@dataclass(frozen=True)
class Claim:
    task_id: str
    program_id: str
    agent: str
    branch: str
    status: str
    schema: str
    mode: str
    path: str
    source: Path


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    program_id: str
    agent: str
    branch: str
    status: str
    schema: str
    claims: tuple[Claim, ...]
    source: Path


class ParseError(ValueError):
    pass


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_front_matter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ParseError(f"{path}: missing opening front matter delimiter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise ParseError(f"{path}: missing closing front matter delimiter") from exc

    data: dict[str, object] = {}
    current_key: str | None = None
    current_subkey: str | None = None

    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_key = key.strip()
            current_subkey = None
            value = value.strip()
            if value == "[]":
                data[current_key] = []
            elif value:
                data[current_key] = _scalar(value)
            else:
                data[current_key] = {} if current_key == "owned_paths" else ""
            continue

        if current_key is None:
            continue

        target = data.get(current_key)
        if indent == 2 and stripped.endswith(":") and isinstance(target, dict):
            current_subkey = stripped[:-1].strip()
            target[current_subkey] = []
            continue

        if stripped.startswith("- "):
            item = _scalar(stripped[2:].strip())
            if isinstance(target, list):
                target.append(item)
            elif isinstance(target, dict) and current_subkey:
                values = target.setdefault(current_subkey, [])
                if not isinstance(values, list):
                    raise ParseError(f"{path}: invalid list under {current_key}.{current_subkey}")
                values.append(item)
            elif isinstance(target, dict):
                data[current_key] = [item]

    return data


def _normalize_claim_path(path: str, source: Path) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.rstrip("/")

    if not normalized:
        raise ParseError(f"{source}: ownership claim must not be empty")
    if normalized.startswith("/"):
        raise ParseError(f"{source}: ownership claim must be repository-relative: {path!r}")
    if any(part == ".." for part in normalized.split("/")):
        raise ParseError(f"{source}: ownership claim must not escape the repository: {path!r}")
    return normalized


def load_task_record(path: Path) -> TaskRecord:
    data = parse_front_matter(path)
    task_id = str(data.get("task_id", "")).strip()
    if not task_id:
        raise ParseError(f"{path}: missing task_id")

    program_id = str(data.get("program_id", "")).strip()
    agent = str(data.get("agent", "")).strip()
    branch = str(data.get("branch", "")).strip()
    status = str(data.get("status", "")).strip()
    owned = data.get("owned_paths", [])

    if isinstance(owned, list):
        schema = "legacy"
        modes = {"legacy_exclusive": [str(value) for value in owned]}
    elif isinstance(owned, dict):
        schema = "structured"
        unknown = sorted(set(owned) - OWNERSHIP_MODES)
        if unknown:
            raise ParseError(f"{path}: unsupported owned_paths mode(s): {', '.join(unknown)}")
        modes: dict[str, list[str]] = {}
        for mode in sorted(OWNERSHIP_MODES):
            values = owned.get(mode, [])
            if values is None:
                values = []
            if not isinstance(values, list):
                raise ParseError(f"{path}: owned_paths.{mode} must be a list")
            modes[mode] = [str(value) for value in values]
    else:
        raise ParseError(f"{path}: owned_paths must be a list or mapping")

    claims = tuple(
        Claim(
            task_id=task_id,
            program_id=program_id,
            agent=agent,
            branch=branch,
            status=status,
            schema=schema,
            mode=mode,
            path=_normalize_claim_path(claimed_path, path),
            source=path,
        )
        for mode, claimed_paths in modes.items()
        for claimed_path in claimed_paths
        if claimed_path.strip()
    )

    return TaskRecord(
        task_id=task_id,
        program_id=program_id,
        agent=agent,
        branch=branch,
        status=status,
        schema=schema,
        claims=claims,
        source=path,
    )


def _literal_prefix(pattern: str) -> str:
    first = len(pattern)
    for token in ("*", "?", "["):
        position = pattern.find(token)
        if position >= 0:
            first = min(first, position)
    return pattern[:first].rstrip("/")


def patterns_overlap(left: str, right: str) -> bool:
    if left == right:
        return True
    if fnmatch.fnmatchcase(left, right) or fnmatch.fnmatchcase(right, left):
        return True

    left_prefix = _literal_prefix(left)
    right_prefix = _literal_prefix(right)
    if not left_prefix or not right_prefix:
        return True
    return (
        left_prefix == right_prefix
        or left_prefix.startswith(right_prefix + "/")
        or right_prefix.startswith(left_prefix + "/")
    )


def read_records(paths: Iterable[Path]) -> tuple[list[TaskRecord], list[str]]:
    records: list[TaskRecord] = []
    errors: list[str] = []
    for path in sorted(paths):
        try:
            records.append(load_task_record(path))
        except (OSError, ParseError) as exc:
            errors.append(str(exc))
    return records, errors


def validate_tasks(paths: Iterable[Path], *, strict_legacy: bool = False) -> list[str]:
    records, errors = read_records(paths)
    seen_task_ids: dict[str, Path] = {}

    for record in records:
        previous = seen_task_ids.get(record.task_id)
        if previous is not None:
            errors.append(f"duplicate task_id {record.task_id}: {previous} and {record.source}")
        else:
            seen_task_ids[record.task_id] = record.source

        if record.status not in ACTIVE_STATUSES:
            continue

        if record.schema == "structured":
            for field, value in (
                ("program_id", record.program_id),
                ("agent", record.agent),
                ("branch", record.branch),
            ):
                if not value:
                    errors.append(f"{record.source}: active structured task {record.task_id} missing {field}")
            if not record.claims:
                errors.append(f"{record.source}: active structured task {record.task_id} has no ownership claims")

    active_claims = [
        claim
        for record in records
        if record.status in ACTIVE_STATUSES
        for claim in record.claims
        if claim.mode == "exclusive" or (strict_legacy and claim.mode == "legacy_exclusive")
    ]

    for index, left in enumerate(active_claims):
        for right in active_claims[index + 1 :]:
            if left.task_id == right.task_id:
                continue
            if patterns_overlap(left.path, right.path):
                errors.append(
                    "exclusive ownership conflict: "
                    f"{left.path!r} ({left.task_id}, {left.source}) overlaps "
                    f"{right.path!r} ({right.task_id}, {right.source})"
                )

    return errors


def migration_warnings(paths: Iterable[Path]) -> list[str]:
    records, _ = read_records(paths)
    legacy = [
        claim
        for record in records
        if record.status in ACTIVE_STATUSES
        for claim in record.claims
        if claim.mode == "legacy_exclusive"
    ]
    structured = [
        claim
        for record in records
        if record.status in ACTIVE_STATUSES
        for claim in record.claims
        if claim.mode == "exclusive"
    ]

    warnings: list[str] = []
    for old in legacy:
        for new in structured:
            if old.task_id != new.task_id and patterns_overlap(old.path, new.path):
                warnings.append(
                    "legacy ownership overlap (migration warning only): "
                    f"{old.path!r} ({old.task_id}) overlaps {new.path!r} ({new.task_id})"
                )
    return warnings


def render_index(paths: Iterable[Path]) -> str:
    records, errors = read_records(paths)
    if errors:
        raise ParseError("; ".join(errors))

    claims = [
        claim
        for record in records
        if record.status in ACTIVE_STATUSES
        for claim in record.claims
    ]
    lines = [
        "# Active Task Ownership",
        "",
        "Generated from `docs/agents/tasks/active/**/*.md`. Do not edit manually.",
        "",
        "| Path | Mode | Schema | Program | Task | Agent | Branch | Record |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for claim in sorted(claims, key=lambda item: (item.path, item.mode, item.task_id)):
        lines.append(
            f"| `{claim.path}` | {claim.mode} | {claim.schema} | "
            f"{claim.program_id or '—'} | {claim.task_id} | {claim.agent or '—'} | "
            f"`{claim.branch or '—'}` | `{claim.source.as_posix()}` |"
        )
    lines.append("")
    return "\n".join(lines)


def _task_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.name.casefold() != "readme.md"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate autonomous-agent task path ownership.")
    parser.add_argument("--tasks", type=Path, default=Path("docs/agents/tasks/active"))
    parser.add_argument(
        "--strict-legacy",
        action="store_true",
        help="Treat legacy flat owned_paths lists as enforced exclusive locks.",
    )
    parser.add_argument("--write-index", type=Path)
    args = parser.parse_args(argv)

    paths = _task_files(args.tasks)
    errors = validate_tasks(paths, strict_legacy=args.strict_legacy)
    for warning in migration_warnings(paths):
        print(f"WARNING: {warning}", file=sys.stderr)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.write_index:
        args.write_index.parent.mkdir(parents=True, exist_ok=True)
        args.write_index.write_text(render_index(paths), encoding="utf-8")

    print(f"Validated {len(paths)} active task record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
