#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ACTIVE_STATUSES = {"planned", "implementing", "blocked", "review", "ready"}

@dataclass(frozen=True)
class Claim:
    task_id: str
    program_id: str
    agent: str
    branch: str
    mode: str
    path: str
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
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
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
            current_key, current_subkey = key.strip(), None
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

        if indent == 2 and stripped.endswith(":") and isinstance(data.get(current_key), dict):
            current_subkey = stripped[:-1].strip()
            casted = data[current_key]
            assert isinstance(casted, dict)
            casted[current_subkey] = []
            continue

        if stripped.startswith("- "):
            item = _scalar(stripped[2:].strip())
            target = data.get(current_key)
            if isinstance(target, list):
                target.append(item)
            elif isinstance(target, dict) and current_subkey:
                sub = target.setdefault(current_subkey, [])
                if not isinstance(sub, list):
                    raise ParseError(f"{path}: invalid list under {current_key}.{current_subkey}")
                sub.append(item)
            elif isinstance(target, dict) and not current_subkey:
                data[current_key] = [item]
            continue

    return data

def task_claims(path: Path) -> tuple[dict[str, object], list[Claim]]:
    data = parse_front_matter(path)
    task_id = str(data.get("task_id", "")).strip()
    if not task_id:
        raise ParseError(f"{path}: missing task_id")
    status = str(data.get("status", "")).strip()
    program_id = str(data.get("program_id", "")).strip()
    agent = str(data.get("agent", "")).strip()
    branch = str(data.get("branch", "")).strip()

    owned = data.get("owned_paths", [])
    modes: dict[str, list[str]]
    if isinstance(owned, list):
        modes = {"legacy_exclusive": [str(v) for v in owned]}
    elif isinstance(owned, dict):
        modes = {}
        for mode in ("exclusive", "shared", "read_only"):
            values = owned.get(mode, [])
            if values is None:
                values = []
            if not isinstance(values, list):
                raise ParseError(f"{path}: owned_paths.{mode} must be a list")
            modes[mode] = [str(v) for v in values]
    else:
        raise ParseError(f"{path}: owned_paths must be a list or mapping")

    claims = [
        Claim(task_id, program_id, agent, branch, mode, p.strip(), path)
        for mode, paths in modes.items()
        for p in paths
        if p.strip()
    ]
    return {"status": status, **data}, claims

def _normalize(pattern: str) -> str:
    while pattern.startswith("./"):
        pattern = pattern[2:]
    return pattern.rstrip("/")

def _literal_prefix(pattern: str) -> str:
    pattern = _normalize(pattern)
    first = len(pattern)
    for token in ("*", "?", "["):
        pos = pattern.find(token)
        if pos >= 0:
            first = min(first, pos)
    return pattern[:first].rstrip("/")

def patterns_overlap(a: str, b: str) -> bool:
    a, b = _normalize(a), _normalize(b)
    if a == b:
        return True
    if fnmatch.fnmatchcase(a, b) or fnmatch.fnmatchcase(b, a):
        return True

    pa, pb = _literal_prefix(a), _literal_prefix(b)
    if not pa or not pb:
        return True
    return pa == pb or pa.startswith(pb + "/") or pb.startswith(pa + "/")

def validate_tasks(paths: Iterable[Path]) -> list[str]:
    errors: list[str] = []
    active_claims: list[Claim] = []
    seen_task_ids: dict[str, Path] = {}

    for path in sorted(paths):
        try:
            data, claims = task_claims(path)
        except (OSError, ParseError) as exc:
            errors.append(str(exc))
            continue

        task_id = str(data.get("task_id", "")).strip()
        if task_id in seen_task_ids:
            errors.append(f"duplicate task_id {task_id}: {seen_task_ids[task_id]} and {path}")
        else:
            seen_task_ids[task_id] = path

        if str(data.get("status", "")).strip() not in ACTIVE_STATUSES:
            continue

        for required in ("agent", "branch"):
            if not str(data.get(required, "")).strip():
                errors.append(f"{path}: active task {task_id} missing {required}")

        active_claims.extend(claims)

    exclusive = [c for c in active_claims if c.mode == "exclusive"]
    for i, left in enumerate(exclusive):
        for right in exclusive[i + 1:]:
            if left.task_id == right.task_id:
                continue
            if patterns_overlap(left.path, right.path):
                errors.append(
                    "exclusive ownership conflict: "
                    f"{left.path!r} ({left.task_id}, {left.source}) overlaps "
                    f"{right.path!r} ({right.task_id}, {right.source})"
                )
    return errors

def render_index(paths: Iterable[Path]) -> str:
    claims: list[Claim] = []
    for path in sorted(paths):
        data, parsed = task_claims(path)
        if str(data.get("status", "")).strip() in ACTIVE_STATUSES:
            claims.extend(parsed)
    lines = [
        "# Active Task Ownership",
        "",
        "Generated from `docs/agents/tasks/active/**/*.md`. Do not edit manually.",
        "",
        "| Path | Mode | Program | Task | Agent | Branch |",
        "|---|---|---|---|---|---|",
    ]
    for claim in sorted(claims, key=lambda c: (c.path, c.mode, c.task_id)):
        lines.append(
            f"| `{claim.path}` | {claim.mode} | {claim.program_id or '—'} | "
            f"{claim.task_id} | {claim.agent or '—'} | `{claim.branch or '—'}` |"
        )
    lines.append("")
    return "\n".join(lines)

def _task_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.md"))

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate autonomous-agent task path ownership.")
    parser.add_argument("--tasks", type=Path, default=Path("docs/agents/tasks/active"))
    parser.add_argument("--write-index", type=Path)
    args = parser.parse_args(argv)
    paths = _task_files(args.tasks)
    errors = validate_tasks(paths)
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
