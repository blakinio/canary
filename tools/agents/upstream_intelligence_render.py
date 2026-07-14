#!/usr/bin/env python3
"""Bounded JSON and Markdown report rendering."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from real_tibia_registry_lib import load_json
from upstream_intelligence_common import SOURCE_CONFIG, UpstreamError

_GITHUB_URL = re.compile(r"^https://github\.com/[^\s<>]+$")


def _cell(value: object) -> str:
    """Escape untrusted external text for a Markdown table cell."""

    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("|", "\\|")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("`", "\\`")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .strip()
    )


def _candidate_link(title: object, url: object) -> str:
    safe_title = _cell(title)
    raw_url = str(url).strip()
    if not _GITHUB_URL.fullmatch(raw_url):
        return safe_title
    safe_url = raw_url.replace("(", "%28").replace(")", "%29")
    return f"[{safe_title}]({safe_url})"


def render_markdown(snapshot: Mapping[str, Any], *, max_rows: int | None = None) -> str:
    summary = snapshot["summary"]
    lines = [
        "# Upstream Intelligence — Current Drift Report",
        "",
        f"Generated: `{snapshot['generated_at']}`  ",
        f"Mode: `{snapshot['mode']}` · rolling window: **{snapshot['window_days']} days** · start: `{snapshot['window_start']}`",
        "",
        "> External activity is a candidate signal, not proof that the local fork is behind or defective.",
        "> No candidate is imported automatically.",
        "",
        "## Summary",
        "",
        f"- sources: **{summary['source_count']}**; source errors: **{summary['source_errors']}**",
        f"- candidates: **{summary['candidate_count']}**; unmapped PR candidates: **{summary['unmapped_candidates']}**",
        f"- priorities: `{json.dumps(summary['by_priority'], sort_keys=True)}`",
        f"- statuses: `{json.dumps(summary['by_status'], sort_keys=True)}`",
        "",
        "## Source heads",
        "",
        "| Source | Observed head | Baseline state | Candidates | Error |",
        "|---|---|---|---:|---|",
    ]
    for source in snapshot["sources"]:
        lines.append(
            f"| `{_cell(source['repository'])}` | `{_cell(source['observed_head_sha'] or 'unavailable')}` | "
            f"`{_cell(source['head_state'])}` | {source['candidate_count']} | {_cell(source['error'] or '—')} |"
        )
    lines += [
        "",
        "## Candidates",
        "",
        "| Priority | Status | Source | Kind | Candidate | Modules | Mapping | Local evidence | Flags |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    candidates = list(snapshot["candidates"])
    limit = len(candidates) if max_rows is None else max_rows
    for candidate in candidates[:limit]:
        modules = ", ".join(f"`{_cell(module)}`" for module in candidate["module_ids"]) or "—"
        flags = ", ".join(f"`{_cell(flag)}`" for flag in candidate["automation_flags"]) or "—"
        link = _candidate_link(candidate["title"], candidate["url"])
        lines.append(
            f"| `{_cell(candidate['priority'])}` | `{_cell(candidate['triage_status'])}` | "
            f"`{_cell(candidate['source_id'])}` | `{_cell(candidate['kind'])}` | {link} | {modules} | "
            f"`{_cell(candidate['mapping_state'])}` | `{_cell(candidate['local_reference']['state'])}` | {flags} |"
        )
    if len(candidates) > limit:
        lines += ["", f"Report truncated: showing **{limit}** of **{len(candidates)}** candidates."]
    if summary["by_module"]:
        lines += ["", "## Module drift counts", "", "| Module | Candidates |", "|---|---:|"]
        lines.extend(f"| `{_cell(module)}` | {count} |" for module, count in summary["by_module"].items())
    lines += [
        "",
        "## Required next step",
        "",
        "Review current-main behavior and authoritative evidence before creating any local task. Pin each durable decision to the exact candidate revision.",
        "",
    ]
    return "\n".join(lines)


def render_issue_body(snapshot: Mapping[str, Any], *, max_chars: int, max_rows: int) -> str:
    marker = "<!-- canary-upstream-intelligence-v1 -->\n"
    rows = min(max_rows, len(snapshot["candidates"]))
    while rows >= 0:
        body = marker + render_markdown(snapshot, max_rows=rows)
        if len(body) <= max_chars:
            return body
        if rows == 0:
            break
        rows //= 2
    raise UpstreamError("report metadata exceeds configured issue-body bound")


def write_outputs(
    snapshot: Mapping[str, Any],
    *,
    root: Path,
    output_json: Path,
    output_markdown: Path,
    issue_body: Path,
) -> None:
    config = load_json(root / SOURCE_CONFIG)
    for path in (output_json, output_markdown, issue_body):
        path.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output_markdown.write_text(render_markdown(snapshot), encoding="utf-8")
    issue_body.write_text(
        render_issue_body(
            snapshot,
            max_chars=int(config["report"]["max_issue_body_chars"]),
            max_rows=int(config["report"]["max_report_rows"]),
        ),
        encoding="utf-8",
    )
