#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Iterable

DEFAULT_BUDGET_POLICY = "minimize_agentic_usage"
VALID_BUDGET_POLICIES = {"minimize_agentic_usage", "balanced", "capability_first"}
VALID_MODES = {"CHAT", "CODEX", "WORK"}

CHAT_KEYWORDS = {
    "analyze",
    "analysis",
    "triage",
    "plan",
    "planning",
    "review pr",
    "pull request",
    "github",
    "ci",
    "workflow failure",
    "inspect",
    "compare options",
    "architecture",
    "prompt",
    "policy",
    "documentation",
}
CODEX_KEYWORDS = {
    "build",
    "compile",
    "run tests",
    "test locally",
    "local runtime",
    "physical client",
    "edit build test",
    "debug executable",
    "cmake",
    "gdb",
    "lldb",
    "valgrind",
    "sanitizer",
    "worktree",
}
WORK_KEYWORDS = {
    "broad research",
    "many sources",
    "multi-source",
    "research report",
    "literature review",
    "large report",
    "large deliverable",
    "spreadsheet",
    "presentation",
    "slide deck",
}

CODEX_PATH_PREFIXES = (
    "src/",
    "tests/",
    "cmake/",
    "vcproj/",
)
CODEX_PATH_NAMES = {"CMakeLists.txt", "CMakePresets.json", "vcpkg.json"}


@dataclass(frozen=True)
class ModeRecommendation:
    mode: str
    budget_policy: str
    confidence: str
    reasons: tuple[str, ...]
    escalation_trigger: str
    return_policy: str
    context_policy: str


def _normalize_paths(paths: Iterable[str]) -> tuple[str, ...]:
    normalized: list[str] = []
    for path in paths:
        value = path.strip().replace("\\", "/")
        while value.startswith("./"):
            value = value[2:]
        if value:
            normalized.append(value)
    return tuple(dict.fromkeys(normalized))


def _contains_any(text: str, needles: set[str]) -> bool:
    lowered = text.casefold()
    return any(needle in lowered for needle in needles)


def _looks_like_code_implementation(task_text: str) -> bool:
    lowered = task_text.casefold()
    return any(
        token in lowered
        for token in (
            "fix ",
            "implement",
            "modify code",
            "change c++",
            "patch",
            "debug",
            "repair runtime",
        )
    )


def _has_runtime_paths(paths: Iterable[str]) -> bool:
    for path in _normalize_paths(paths):
        if path in CODEX_PATH_NAMES:
            return True
        if any(path.startswith(prefix) for prefix in CODEX_PATH_PREFIXES):
            return True
        if PurePosixPath(path).suffix in {".cpp", ".hpp", ".cc", ".cxx"}:
            return True
    return False


def recommend_mode(
    *,
    task_text: str = "",
    changed_paths: Iterable[str] = (),
    needs_local_execution: bool = False,
    broad_research: bool = False,
    large_deliverable: bool = False,
    parallel_workers: bool = False,
    github_only: bool = False,
    budget_policy: str = DEFAULT_BUDGET_POLICY,
) -> ModeRecommendation:
    if budget_policy not in VALID_BUDGET_POLICIES:
        raise ValueError(
            f"unsupported budget policy {budget_policy!r}; "
            f"expected one of {', '.join(sorted(VALID_BUDGET_POLICIES))}"
        )

    paths = _normalize_paths(changed_paths)
    scores = {"CHAT": 0, "CODEX": 0, "WORK": 0}
    reasons: dict[str, list[str]] = {mode: [] for mode in VALID_MODES}

    if budget_policy == "minimize_agentic_usage":
        scores["CHAT"] += 4
        reasons["CHAT"].append("budget policy prefers Chat before consuming scarce agentic usage")
    elif budget_policy == "balanced":
        scores["CHAT"] += 2
    else:
        scores["CODEX"] += 1
        scores["WORK"] += 1

    if github_only or _contains_any(task_text, CHAT_KEYWORDS):
        scores["CHAT"] += 4
        reasons["CHAT"].append("task is primarily analysis, planning, GitHub, PR or CI work")

    runtime_paths = _has_runtime_paths(paths)
    implementation_intent = _looks_like_code_implementation(task_text)

    if needs_local_execution:
        scores["CODEX"] += 8
        reasons["CODEX"].append("task explicitly requires local edit/build/test/runtime execution")
    if _contains_any(task_text, CODEX_KEYWORDS):
        scores["CODEX"] += 5
        reasons["CODEX"].append("task text contains local execution or iterative debugging signals")
    if runtime_paths and implementation_intent:
        scores["CODEX"] += 4
        reasons["CODEX"].append("implementation intent targets runtime/build/test code paths")
    elif runtime_paths:
        scores["CODEX"] += 1
        reasons["CODEX"].append("runtime-oriented paths are present, but local execution is not yet proven necessary")
    if parallel_workers:
        scores["CODEX"] += 3
        reasons["CODEX"].append("parallel isolated coding workers may reduce wall-clock time")

    if broad_research:
        scores["WORK"] += 8
        reasons["WORK"].append("task explicitly requires broad multi-source research")
    if large_deliverable:
        scores["WORK"] += 5
        reasons["WORK"].append("task explicitly requires a large final deliverable")
    if _contains_any(task_text, WORK_KEYWORDS):
        scores["WORK"] += 5
        reasons["WORK"].append("task text contains broad research or large-deliverable signals")

    mode = max(scores, key=lambda item: (scores[item], item == "CHAT"))

    if budget_policy == "minimize_agentic_usage" and mode in {"CODEX", "WORK"}:
        if scores[mode] < scores["CHAT"] + 2:
            mode = "CHAT"
            reasons["CHAT"].append(
                "agentic-mode advantage was too small to justify scarce Codex/Work usage"
            )

    if mode == "CHAT":
        confidence = "high" if scores["CHAT"] >= max(scores["CODEX"], scores["WORK"]) + 3 else "medium"
        escalation_trigger = (
            "Escalate to CODEX only when local edit/build/test/runtime execution becomes necessary; "
            "escalate to WORK only when broad multi-source research or a large deliverable becomes necessary."
        )
        return_policy = "Stay in CHAT while connector-based analysis, planning, PR and CI work is sufficient."
    elif mode == "CODEX":
        confidence = "high" if needs_local_execution or scores["CODEX"] >= scores["CHAT"] + 4 else "medium"
        escalation_trigger = (
            "Use CODEX only for the bounded executable step. Do not preload unrelated repository context."
        )
        return_policy = (
            "Return to CHAT after the bounded edit/build/test/runtime loop completes or a blocker needs analysis."
        )
    else:
        confidence = "high" if broad_research or scores["WORK"] >= scores["CHAT"] + 4 else "medium"
        escalation_trigger = (
            "Use WORK only for the bounded research/deliverable package. Do not use it for ordinary code iteration."
        )
        return_policy = (
            "Return to CHAT after the research/deliverable package is produced for review, PR and CI coordination."
        )

    context_policy = (
        "Pass only task identity, current head/PR, routed required reads, PROVEN facts, UNKNOWN/CONFLICT items, "
        "first failure, changed paths, validation evidence and one next_action. Never pass full chat history or "
        "whole-repository dumps by default."
    )

    selected_reasons = tuple(reasons[mode]) or ("selected by deterministic score",)
    return ModeRecommendation(
        mode=mode,
        budget_policy=budget_policy,
        confidence=confidence,
        reasons=selected_reasons,
        escalation_trigger=escalation_trigger,
        return_policy=return_policy,
        context_policy=context_policy,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recommend CHAT, CODEX or WORK while minimizing scarce agentic usage."
    )
    parser.add_argument("--task-text", default="")
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--needs-local-execution", action="store_true")
    parser.add_argument("--broad-research", action="store_true")
    parser.add_argument("--large-deliverable", action="store_true")
    parser.add_argument("--parallel-workers", action="store_true")
    parser.add_argument("--github-only", action="store_true")
    parser.add_argument(
        "--budget-policy",
        choices=sorted(VALID_BUDGET_POLICIES),
        default=DEFAULT_BUDGET_POLICY,
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    recommendation = recommend_mode(
        task_text=args.task_text,
        changed_paths=args.changed_path,
        needs_local_execution=args.needs_local_execution,
        broad_research=args.broad_research,
        large_deliverable=args.large_deliverable,
        parallel_workers=args.parallel_workers,
        github_only=args.github_only,
        budget_policy=args.budget_policy,
    )

    if args.json:
        print(json.dumps(asdict(recommendation), indent=2))
    else:
        print(f"MODE: {recommendation.mode}")
        print(f"BUDGET_POLICY: {recommendation.budget_policy}")
        print(f"CONFIDENCE: {recommendation.confidence}")
        for reason in recommendation.reasons:
            print(f"REASON: {reason}")
        print(f"ESCALATION: {recommendation.escalation_trigger}")
        print(f"RETURN: {recommendation.return_policy}")
        print(f"CONTEXT: {recommendation.context_policy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
