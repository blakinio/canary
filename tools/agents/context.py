#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import checkpoint
import execution_mode
import task_ownership

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "docs/agents/CONTEXT_ROUTES.json"
CHECKPOINT_MISSING_WARNING = (
    "CHECKPOINT_MISSING — evidence bundle partially derived from task frontmatter; "
    "verify live Git/PR state before continuing."
)
RECOVERY_NEXT_ACTION = (
    "Reconstruct and write a valid ## Context checkpoint from current Git, PR and task "
    "evidence before substantive implementation."
)


def _dedupe(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _bounded(values: Iterable[str], limit: int) -> list[str]:
    return _dedupe(values)[: max(0, limit)]


def _resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_pr_reference(value: object) -> str:
    raw = str(value or "").strip()
    if not raw or raw.casefold() in {"none", "unknown", "n/a"}:
        return ""

    if raw.isdigit():
        return raw
    if raw.startswith("#") and raw[1:].isdigit():
        return raw[1:]

    url_match = re.search(r"/pull/(\d+)/?$", raw)
    if url_match:
        return url_match.group(1)

    repo_match = re.search(r"#(\d+)$", raw)
    if repo_match:
        return repo_match.group(1)

    return raw


def _format_pr_required_read(pr_reference: str) -> str:
    if pr_reference.isdigit():
        return f"PR #{pr_reference}"
    return f"PR {pr_reference}"


def _matches_path(path: str, pattern: str) -> bool:
    normalized = path.replace("\\", "/").lstrip("./")
    return fnmatch.fnmatchcase(normalized, pattern)


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, object]:
    resolved = _resolve_repo_path(path)
    data = json.loads(resolved.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError(
            f"{resolved}: unsupported schema_version {data.get('schema_version')!r}"
        )
    if not isinstance(data.get("routes"), dict):
        raise ValueError(f"{resolved}: routes must be an object")
    if not isinstance(data.get("core_reads"), list):
        raise ValueError(f"{resolved}: core_reads must be a list")
    return data


def infer_routes(
    *,
    config: dict[str, object],
    explicit_routes: Iterable[str] = (),
    task_text: str = "",
    paths: Iterable[str] = (),
) -> tuple[list[str], list[str]]:
    routes = config.get("routes", {})
    assert isinstance(routes, dict)

    selected: list[str] = []
    unknown_explicit: list[str] = []

    for route in explicit_routes:
        if route in routes:
            selected.append(route)
        elif route:
            unknown_explicit.append(route)

    lowered = task_text.casefold()
    normalized_paths = [path.replace("\\", "/").lstrip("./") for path in paths if path]

    for route_name, raw in routes.items():
        if route_name in selected or not isinstance(raw, dict):
            continue
        keywords = raw.get("keywords", [])
        path_globs = raw.get("path_globs", [])
        keyword_match = any(
            str(keyword).casefold() in lowered for keyword in keywords if str(keyword).strip()
        )
        path_match = any(
            _matches_path(path, str(pattern))
            for path in normalized_paths
            for pattern in path_globs
            if str(pattern).strip()
        )
        if keyword_match or path_match:
            selected.append(route_name)

    return _dedupe(selected), _dedupe(unknown_explicit)


def _front_matter(task_path: Path) -> dict[str, object]:
    return task_ownership.parse_front_matter(task_path)


def _route_context(
    config: dict[str, object],
    selected_routes: Iterable[str],
) -> tuple[list[str], list[str], list[str]]:
    routes = config["routes"]
    assert isinstance(routes, dict)
    required: list[str] = []
    search_first: list[str] = []
    optional: list[str] = []

    for route_name in selected_routes:
        raw = routes.get(route_name)
        if not isinstance(raw, dict):
            continue
        required.extend(str(value) for value in raw.get("required_reads", []))
        search_first.extend(str(value) for value in raw.get("search_first", []))
        optional.extend(str(value) for value in raw.get("optional_reads", []))

    return _dedupe(required), _dedupe(search_first), _dedupe(optional)


def _limits(config: dict[str, object]) -> dict[str, int]:
    raw = config.get("limits", {})
    if not isinstance(raw, dict):
        return {}
    limits: dict[str, int] = {}
    for key, value in raw.items():
        try:
            limits[str(key)] = int(value)
        except (TypeError, ValueError):
            continue
    return limits


def build_evidence_bundle(
    checkpoint_data: dict[str, object],
    *,
    limits: dict[str, int],
) -> dict[str, object]:
    def list_value(key: str, limit_key: str, default_limit: int) -> list[str]:
        raw = checkpoint_data.get(key, [])
        if not isinstance(raw, list):
            return []
        return _bounded(
            (str(item) for item in raw),
            limits.get(limit_key, default_limit),
        )

    validation_raw = checkpoint_data.get("validation", [])
    validation: list[dict[str, str]] = []
    if isinstance(validation_raw, list):
        for item in validation_raw[: limits.get("max_validation", 8)]:
            if isinstance(item, dict):
                validation.append({str(k): str(v) for k, v in item.items()})

    first_failure = checkpoint_data.get("first_failure", {})
    if not isinstance(first_failure, dict):
        first_failure = {}

    return {
        "head": str(checkpoint_data.get("head", "UNKNOWN")),
        "branch": str(checkpoint_data.get("branch", "UNKNOWN")),
        "pr": normalize_pr_reference(checkpoint_data.get("pr", "")) or "none",
        "status": str(checkpoint_data.get("status", "UNKNOWN")),
        "proven": list_value("proven", "max_proven", 12),
        "unknown": list_value("unknown", "max_unknown", 8),
        "conflicts": list_value("conflicts", "max_conflicts", 6),
        "first_failure": {str(k): str(v) for k, v in first_failure.items()},
        "changed_paths": list_value("changed_paths", "max_changed_paths", 12),
        "validation": validation,
        "blockers": list_value("blockers", "max_blockers", 6),
        "next_action": str(checkpoint_data.get("next_action", "UNKNOWN")),
    }


def _legacy_evidence_fallback(
    evidence: dict[str, object],
    *,
    front_matter: dict[str, object],
    pr_reference: str,
) -> None:
    evidence["head"] = str(front_matter.get("last_verified_commit", "")).strip() or "UNKNOWN"
    evidence["branch"] = str(front_matter.get("branch", "")).strip() or "UNKNOWN"
    evidence["pr"] = pr_reference or "none"
    evidence["status"] = str(front_matter.get("status", "")).strip() or "UNKNOWN"
    evidence["next_action"] = RECOVERY_NEXT_ACTION


def resolve_context(
    *,
    task_path: Path,
    config_path: Path = DEFAULT_CONFIG,
    task_text: str = "",
    changed_paths: Iterable[str] = (),
    extra_routes: Iterable[str] = (),
    needs_local_execution: bool = False,
    broad_research: bool = False,
    large_deliverable: bool = False,
    parallel_workers: bool = False,
    github_only: bool = False,
    budget_policy: str | None = None,
) -> dict[str, object]:
    resolved_task_path = _resolve_repo_path(task_path)
    resolved_config_path = _resolve_repo_path(config_path)
    config = load_config(resolved_config_path)

    parsed_checkpoint = checkpoint.parse_task_checkpoint(resolved_task_path)
    checkpoint_present = parsed_checkpoint is not None
    cp = parsed_checkpoint.data if parsed_checkpoint is not None else {}
    front = _front_matter(resolved_task_path)

    cp_routes = cp.get("context_routes", [])
    if not isinstance(cp_routes, list):
        cp_routes = []
    cp_paths = cp.get("changed_paths", [])
    if not isinstance(cp_paths, list):
        cp_paths = []
    owned_paths = cp.get("owned_paths", [])
    if not isinstance(owned_paths, list):
        owned_paths = []

    all_paths = _dedupe(
        [str(value) for value in changed_paths]
        + [str(value) for value in cp_paths]
        + [str(value) for value in owned_paths]
    )
    explicit_routes = _dedupe(
        [str(value) for value in cp_routes] + [str(value) for value in extra_routes]
    )
    selected_routes, unknown_routes = infer_routes(
        config=config,
        explicit_routes=explicit_routes,
        task_text=task_text,
        paths=all_paths,
    )
    required, search_first, optional = _route_context(config, selected_routes)
    limits = _limits(config)

    checkpoint_pr = normalize_pr_reference(cp.get("pr", ""))
    frontmatter_pr = normalize_pr_reference(front.get("related_pr", ""))
    pr_reference = checkpoint_pr or frontmatter_pr

    core_reads = [str(value) for value in config.get("core_reads", [])]
    core_reads.append(_display_path(resolved_task_path))
    if pr_reference:
        core_reads.append(_format_pr_required_read(pr_reference))

    required_reads = _bounded(
        core_reads + required,
        limits.get("max_required_reads", 12),
    )
    search_first_reads = _bounded(
        search_first,
        limits.get("max_search_first", 10),
    )
    optional_reads = _bounded(
        optional,
        limits.get("max_optional_reads", 8),
    )

    selected_budget_policy = (
        budget_policy
        or str(config.get("budget_policy", execution_mode.DEFAULT_BUDGET_POLICY))
    )
    recommendation = execution_mode.recommend_mode(
        task_text=task_text,
        changed_paths=all_paths,
        needs_local_execution=needs_local_execution,
        broad_research=broad_research,
        large_deliverable=large_deliverable,
        parallel_workers=parallel_workers,
        github_only=github_only,
        budget_policy=selected_budget_policy,
    )

    evidence_bundle = build_evidence_bundle(cp, limits=limits)
    evidence_bundle["pr"] = pr_reference or "none"
    warnings: list[str] = []
    if not checkpoint_present:
        _legacy_evidence_fallback(
            evidence_bundle,
            front_matter=front,
            pr_reference=pr_reference,
        )
        warnings.append(CHECKPOINT_MISSING_WARNING)

    return {
        "task_id": str(front.get("task_id", "")),
        "program_id": str(front.get("program_id", "")),
        "task_path": _display_path(resolved_task_path),
        "checkpoint_present": checkpoint_present,
        "warnings": warnings,
        "routes": selected_routes,
        "unknown_explicit_routes": unknown_routes,
        "required_reads": required_reads,
        "search_first": search_first_reads,
        "optional_reads": optional_reads,
        "execution_mode": asdict(recommendation),
        "evidence_bundle": evidence_bundle,
        "anti_bloat": [
            "Do not load full chat history.",
            "Do not rediscover PROVEN facts unless current Git/PR evidence changed.",
            "Search search_first files before opening them in full.",
            "Do not preload optional_reads unless a concrete blocker requires them.",
            "For CODEX or WORK, pass only this bounded bundle plus exact source paths needed for execution.",
        ],
    }


def _render_text(result: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append(f"TASK: {result.get('task_id', '')}")
    lines.append(f"PROGRAM: {result.get('program_id', '')}")
    for warning in result.get("warnings", []):
        lines.append(f"WARNING: {warning}")
    lines.append(f"ROUTES: {', '.join(result.get('routes', [])) or 'none'}")

    mode = result.get("execution_mode", {})
    if isinstance(mode, dict):
        lines.append(f"MODE: {mode.get('mode', 'CHAT')}")
        lines.append(f"BUDGET_POLICY: {mode.get('budget_policy', '')}")
        lines.append(f"CONFIDENCE: {mode.get('confidence', '')}")
        for reason in mode.get("reasons", []):
            lines.append(f"MODE_REASON: {reason}")
        lines.append(f"MODE_ESCALATION: {mode.get('escalation_trigger', '')}")
        lines.append(f"MODE_RETURN: {mode.get('return_policy', '')}")

    for title, key in (
        ("REQUIRED_READS", "required_reads"),
        ("SEARCH_FIRST", "search_first"),
        ("OPTIONAL_READS", "optional_reads"),
    ):
        lines.append(title)
        for item in result.get(key, []):
            lines.append(f"- {item}")

    evidence = result.get("evidence_bundle", {})
    if isinstance(evidence, dict):
        lines.append("EVIDENCE_BUNDLE")
        for key in ("head", "branch", "pr", "status"):
            lines.append(f"{key.upper()}: {evidence.get(key, '')}")
        for key in ("proven", "unknown", "conflicts", "changed_paths", "blockers"):
            lines.append(key.upper())
            for item in evidence.get(key, []):
                lines.append(f"- {item}")
        first_failure = evidence.get("first_failure", {})
        if isinstance(first_failure, dict):
            lines.append(
                "FIRST_FAILURE: "
                f"{first_failure.get('marker', 'none')} | {first_failure.get('evidence', 'none')}"
            )
        lines.append(f"NEXT_ACTION: {evidence.get('next_action', 'UNKNOWN')}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve the smallest authoritative context for a Canary agent task."
    )
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
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
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = resolve_context(
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
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
