#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

CHECKPOINT_HEADING = "## Context checkpoint"
ALLOWED_STATUSES = {"investigating", "implementing", "validating", "blocked", "ready"}
ALLOWED_VALIDATION_RESULTS = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}

SCALAR_KEYS = {
    "checkpoint_version",
    "updated_at",
    "head",
    "branch",
    "pr",
    "status",
    "next_action",
}
LIST_KEYS = {
    "context_routes",
    "owned_paths",
    "proven",
    "derived",
    "unknown",
    "conflicts",
    "rejected_hypotheses",
    "changed_paths",
    "blockers",
}
MAP_KEYS = {"first_failure"}
LIST_OF_MAP_KEYS = {"validation"}
REQUIRED_KEYS = SCALAR_KEYS | LIST_KEYS | MAP_KEYS | LIST_OF_MAP_KEYS


class CheckpointError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedCheckpoint:
    data: dict[str, object]
    block: str
    source: Path


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def extract_checkpoint_block(text: str, *, source: Path | None = None) -> str | None:
    heading_index = text.find(CHECKPOINT_HEADING)
    if heading_index < 0:
        return None

    remainder = text[heading_index + len(CHECKPOINT_HEADING) :]
    fence = re.search(r"```(?:yaml|yml)?\s*\n", remainder, flags=re.IGNORECASE)
    if fence is None:
        location = str(source) if source else "<text>"
        raise CheckpointError(f"{location}: context checkpoint heading has no fenced YAML block")

    block_start = fence.end()
    block_end = remainder.find("```", block_start)
    if block_end < 0:
        location = str(source) if source else "<text>"
        raise CheckpointError(f"{location}: context checkpoint fenced block is not closed")
    return remainder[block_start:block_end].strip("\n")


def parse_checkpoint_block(block: str, *, source: Path | None = None) -> dict[str, object]:
    data: dict[str, object] = {}
    seen_top_level: set[str] = set()
    current_key: str | None = None
    current_validation: dict[str, str] | None = None
    location = str(source) if source else "<checkpoint>"

    for lineno, raw in enumerate(block.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if indent == 0:
            if ":" not in stripped:
                raise CheckpointError(f"{location}:{lineno}: invalid top-level checkpoint line")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in seen_top_level:
                raise CheckpointError(f"{location}:{lineno}: duplicate top-level key {key!r}")
            seen_top_level.add(key)
            current_key = key
            current_validation = None

            if key in LIST_KEYS:
                if value not in {"", "[]"}:
                    raise CheckpointError(f"{location}:{lineno}: {key} must be a YAML list")
                data[key] = []
            elif key in MAP_KEYS:
                if value:
                    raise CheckpointError(f"{location}:{lineno}: {key} must be a YAML mapping")
                data[key] = {}
            elif key in LIST_OF_MAP_KEYS:
                if value not in {"", "[]"}:
                    raise CheckpointError(f"{location}:{lineno}: {key} must be a YAML list")
                data[key] = []
            else:
                data[key] = _scalar(value)
            continue

        if current_key is None:
            raise CheckpointError(f"{location}:{lineno}: nested checkpoint value has no parent key")

        if current_key in LIST_KEYS:
            if indent != 2 or not stripped.startswith("- "):
                raise CheckpointError(f"{location}:{lineno}: invalid list item under {current_key}")
            values = data[current_key]
            assert isinstance(values, list)
            values.append(_scalar(stripped[2:].strip()))
            continue

        if current_key in MAP_KEYS:
            if indent != 2 or ":" not in stripped:
                raise CheckpointError(f"{location}:{lineno}: invalid mapping item under {current_key}")
            key, value = stripped.split(":", 1)
            mapping = data[current_key]
            assert isinstance(mapping, dict)
            if key.strip() in mapping:
                raise CheckpointError(
                    f"{location}:{lineno}: duplicate key {current_key}.{key.strip()}"
                )
            mapping[key.strip()] = _scalar(value)
            continue

        if current_key in LIST_OF_MAP_KEYS:
            items = data[current_key]
            assert isinstance(items, list)
            if indent == 2 and stripped.startswith("- "):
                item_text = stripped[2:].strip()
                if ":" not in item_text:
                    raise CheckpointError(
                        f"{location}:{lineno}: validation item must start with a key/value pair"
                    )
                key, value = item_text.split(":", 1)
                current_validation = {key.strip(): _scalar(value)}
                items.append(current_validation)
                continue
            if indent == 4 and current_validation is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                key = key.strip()
                if key in current_validation:
                    raise CheckpointError(
                        f"{location}:{lineno}: duplicate validation field {key!r}"
                    )
                current_validation[key] = _scalar(value)
                continue
            raise CheckpointError(f"{location}:{lineno}: invalid validation entry")

        raise CheckpointError(
            f"{location}:{lineno}: scalar key {current_key!r} cannot have nested values"
        )

    return data


def parse_task_checkpoint(path: Path) -> ParsedCheckpoint | None:
    text = path.read_text(encoding="utf-8")
    block = extract_checkpoint_block(text, source=path)
    if block is None:
        return None
    return ParsedCheckpoint(
        data=parse_checkpoint_block(block, source=path),
        block=block,
        source=path,
    )


def _normalized_fact(value: str) -> str:
    return " ".join(value.casefold().split())


def validate_checkpoint(data: dict[str, object], *, source: Path | None = None) -> list[str]:
    location = str(source) if source else "<checkpoint>"
    errors: list[str] = []

    missing = sorted(REQUIRED_KEYS - set(data))
    for key in missing:
        errors.append(f"{location}: missing checkpoint field {key}")

    if str(data.get("checkpoint_version", "")).strip() != "1":
        errors.append(f"{location}: checkpoint_version must be 1")

    status = str(data.get("status", "")).strip()
    if status and status not in ALLOWED_STATUSES:
        errors.append(
            f"{location}: unsupported checkpoint status {status!r}; "
            f"expected one of {', '.join(sorted(ALLOWED_STATUSES))}"
        )

    for key in ("updated_at", "head", "branch", "pr", "next_action"):
        if key in data and not str(data.get(key, "")).strip():
            errors.append(f"{location}: checkpoint field {key} must not be empty")

    next_action = str(data.get("next_action", "")).strip()
    if next_action.casefold() in {"none", "unknown", "pending", "n/a"}:
        errors.append(f"{location}: next_action must be one concrete next step")

    first_failure = data.get("first_failure")
    if isinstance(first_failure, dict):
        for key in ("marker", "evidence"):
            if not str(first_failure.get(key, "")).strip():
                errors.append(f"{location}: first_failure.{key} must not be empty")
    elif "first_failure" in data:
        errors.append(f"{location}: first_failure must be a mapping")

    validation = data.get("validation")
    if isinstance(validation, list):
        for index, item in enumerate(validation, start=1):
            if not isinstance(item, dict):
                errors.append(f"{location}: validation item {index} must be a mapping")
                continue
            for key in ("command", "result", "evidence"):
                if not str(item.get(key, "")).strip():
                    errors.append(f"{location}: validation item {index} missing {key}")
            result = str(item.get("result", "")).strip()
            if result and result not in ALLOWED_VALIDATION_RESULTS:
                errors.append(
                    f"{location}: validation item {index} has unsupported result {result!r}"
                )
    elif "validation" in data:
        errors.append(f"{location}: validation must be a list")

    evidence_lists: dict[str, set[str]] = {}
    for key in ("proven", "derived", "unknown", "conflicts"):
        raw = data.get(key, [])
        if not isinstance(raw, list):
            errors.append(f"{location}: {key} must be a list")
            continue
        values = {_normalized_fact(str(item)) for item in raw if str(item).strip()}
        evidence_lists[key] = values

    keys = list(evidence_lists)
    for index, left in enumerate(keys):
        for right in keys[index + 1 :]:
            overlap = evidence_lists[left] & evidence_lists[right]
            for fact in sorted(overlap):
                errors.append(
                    f"{location}: evidence fact appears in both {left} and {right}: {fact!r}"
                )

    return errors


def validate_task(path: Path, *, require_checkpoint: bool = False) -> list[str]:
    try:
        parsed = parse_task_checkpoint(path)
    except (OSError, CheckpointError) as exc:
        return [str(exc)]

    if parsed is None:
        if require_checkpoint:
            return [f"{path}: missing {CHECKPOINT_HEADING} section"]
        return []
    return validate_checkpoint(parsed.data, source=path)


def _task_files(root: Path) -> Iterable[Path]:
    return sorted(
        path for path in root.rglob("*.md") if path.name.casefold() != "readme.md"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate compact autonomous-agent context checkpoints."
    )
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--tasks", type=Path)
    parser.add_argument(
        "--require-checkpoint",
        action="store_true",
        help="Fail when a selected task has no Context checkpoint section.",
    )
    args = parser.parse_args(argv)

    paths = list(args.paths)
    if args.tasks:
        paths.extend(_task_files(args.tasks))
    if not paths:
        parser.error("provide at least one task path or --tasks directory")

    errors: list[str] = []
    for path in paths:
        errors.extend(validate_task(path, require_checkpoint=args.require_checkpoint))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(paths)} task checkpoint(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
