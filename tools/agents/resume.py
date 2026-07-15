#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import context as context_tool
import execution_mode

MODE_NAMES = {"auto", "chat", "codex", "work"}


def _override_mode(result: dict[str, object], target_mode: str) -> None:
    if target_mode == "auto":
        return
    mode = result.get("execution_mode")
    if not isinstance(mode, dict):
        return
    mode["mode"] = target_mode.upper()
    mode["confidence"] = "user-selected"
    mode["reasons"] = (
        f"target mode explicitly selected as {target_mode.upper()}",
    )


def build_resume_bundle(
    *,
    task_path: Path,
    config_path: Path = context_tool.DEFAULT_CONFIG,
    task_text: str = "",
    changed_paths: list[str] | None = None,
    extra_routes: list[str] | None = None,
    needs_local_execution: bool = False,
    broad_research: bool = False,
    large_deliverable: bool = False,
    parallel_workers: bool = False,
    github_only: bool = False,
    budget_policy: str | None = None,
    target_mode: str = "auto",
) -> dict[str, object]:
    if target_mode not in MODE_NAMES:
        raise ValueError(f"unsupported target_mode {target_mode!r}")

    result = context_tool.resolve_context(
        task_path=task_path,
        config_path=config_path,
        task_text=task_text,
        changed_paths=changed_paths or [],
        extra_routes=extra_routes or [],
        needs_local_execution=needs_local_execution,
        broad_research=broad_research,
        large_deliverable=large_deliverable,
        parallel_workers=parallel_workers,
        github_only=github_only,
        budget_policy=budget_policy,
    )
    _override_mode(result, target_mode)
    return result


def render_prompt(result: dict[str, object]) -> str:
    task_id = str(result.get("task_id", ""))
    program_id = str(result.get("program_id", ""))
    routes = result.get("routes", [])
    required_reads = result.get("required_reads", [])
    search_first = result.get("search_first", [])
    optional_reads = result.get("optional_reads", [])
    warnings = result.get("warnings", [])
    mode = result.get("execution_mode", {})
    evidence = result.get("evidence_bundle", {})

    if not isinstance(mode, dict):
        mode = {}
    if not isinstance(evidence, dict):
        evidence = {}

    lines: list[str] = [
        f"Continue task {task_id} from repository state.",
        "Repository writes are allowed only in blakinio/canary.",
        "Do not rely on previous chat history.",
    ]
    for warning in warnings:
        lines.append(f"WARNING: {warning}")
    lines.extend(
        [
            "",
            f"PROGRAM: {program_id or 'none'}",
            f"RECOMMENDED_MODE: {mode.get('mode', 'CHAT')}",
            f"BUDGET_POLICY: {mode.get('budget_policy', execution_mode.DEFAULT_BUDGET_POLICY)}",
            f"MODE_CONFIDENCE: {mode.get('confidence', '')}",
        ]
    )

    for reason in mode.get("reasons", []):
        lines.append(f"MODE_REASON: {reason}")
    lines.extend(
        [
            f"MODE_ESCALATION: {mode.get('escalation_trigger', '')}",
            f"MODE_RETURN: {mode.get('return_policy', '')}",
            "",
            f"CONTEXT_ROUTES: {', '.join(str(item) for item in routes) or 'none'}",
            "REQUIRED_READS:",
        ]
    )
    for item in required_reads:
        lines.append(f"- {item}")

    lines.append("SEARCH_FIRST:")
    for item in search_first:
        lines.append(f"- {item}")

    lines.append("OPTIONAL_READS_ONLY_IF_BLOCKED:")
    for item in optional_reads:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "EVIDENCE_BUNDLE:",
            f"HEAD: {evidence.get('head', 'UNKNOWN')}",
            f"BRANCH: {evidence.get('branch', 'UNKNOWN')}",
            f"PR: {evidence.get('pr', 'none')}",
            f"STATUS: {evidence.get('status', 'UNKNOWN')}",
            "PROVEN:",
        ]
    )
    for item in evidence.get("proven", []):
        lines.append(f"- {item}")

    lines.append("UNKNOWN:")
    for item in evidence.get("unknown", []):
        lines.append(f"- {item}")

    lines.append("CONFLICTS:")
    for item in evidence.get("conflicts", []):
        lines.append(f"- {item}")

    first_failure = evidence.get("first_failure", {})
    if isinstance(first_failure, dict):
        lines.append(f"FIRST_FAILURE_MARKER: {first_failure.get('marker', 'none')}")
        lines.append(f"FIRST_FAILURE_EVIDENCE: {first_failure.get('evidence', 'none')}")

    lines.append("CHANGED_PATHS:")
    for item in evidence.get("changed_paths", []):
        lines.append(f"- {item}")

    lines.append("VALIDATION:")
    for item in evidence.get("validation", []):
        if isinstance(item, dict):
            lines.append(
                "- "
                f"{item.get('command', '')}: {item.get('result', '')}; "
                f"evidence={item.get('evidence', '')}"
            )

    lines.append("BLOCKERS:")
    for item in evidence.get("blockers", []):
        lines.append(f"- {item}")

    lines.extend(
        [
            f"NEXT_ACTION: {evidence.get('next_action', 'UNKNOWN')}",
            "",
            "OPERATING_RULES:",
            "- Verify current head, PR, CI and ownership before making changes.",
            "- Do not rediscover PROVEN facts unless live repository evidence changed.",
            "- Search SEARCH_FIRST paths before opening them in full.",
            "- Do not load OPTIONAL_READS unless a concrete blocker requires them.",
            "- Do not paste full logs, diffs, source trees or old chat history into context.",
            "- For CODEX: execute only the bounded edit/build/test/runtime loop, checkpoint results, then return coordination to CHAT.",
            "- For WORK: execute only the bounded multi-source research/deliverable package, checkpoint results, then return coordination to CHAT.",
            "- Preserve UNKNOWN and CONFLICT explicitly; never convert them into assumptions.",
            "- Leave exactly one concrete next_action before ending or handing off.",
        ]
    )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a compact continuation/evidence bundle for Chat, Codex or Work."
    )
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=context_tool.DEFAULT_CONFIG)
    parser.add_argument("--task-text", default="")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--route", action="append", default=[])
    parser.add_argument("--needs-local-execution", action="store_true")
    parser.add_argument("--broad-research", action="store_true")
    parser.add_argument("--large-deliverable", action="store_true")
    parser.add_argument("--parallel-workers", action="store_true")
    parser.add_argument("--github-only", action="store_true")
    parser.add_argument(
        "--budget-policy",
        choices=sorted(execution_mode.VALID_BUDGET_POLICIES),
    )
    parser.add_argument("--target-mode", choices=sorted(MODE_NAMES), default="auto")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = build_resume_bundle(
        task_path=args.task,
        config_path=args.config,
        task_text=args.task_text,
        changed_paths=args.changed_path,
        extra_routes=args.route,
        needs_local_execution=args.needs_local_execution,
        broad_research=args.broad_research,
        large_deliverable=args.large_deliverable,
        parallel_workers=args.parallel_workers,
        github_only=args.github_only,
        budget_policy=args.budget_policy,
        target_mode=args.target_mode,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_prompt(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
