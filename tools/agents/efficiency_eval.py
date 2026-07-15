#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ALLOWED_COHORTS = {"baseline", "routed", "custom"}
ALLOWED_MODES = {"CHAT", "CODEX", "WORK"}
ALLOWED_EVENT_TYPES = {
    "file_read",
    "tool_call",
    "action",
    "context_expand",
    "optional_context_load",
    "handoff",
}
MAX_EVENTS = 10_000


class TraceError(ValueError):
    pass


@dataclass(frozen=True)
class RunMetrics:
    run_id: str
    cohort: str
    mode: str
    duration_seconds: float
    files_read: int
    unique_files: int
    repeated_reads: int
    repeat_read_ratio: float
    tool_calls: int
    time_to_first_action_seconds: float | None
    context_expansions: int
    optional_context_loads: int
    handoff_attempted: bool
    handoff_success: bool | None


def _parse_ts(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise TraceError(f"{field} must be a non-empty ISO-8601 string")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise TraceError(f"{field} is not valid ISO-8601: {value!r}") from exc
    if parsed.tzinfo is None:
        raise TraceError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate_trace(trace: object) -> dict[str, object]:
    if not isinstance(trace, dict):
        raise TraceError("trace must be a JSON object")

    required = {
        "schema_version",
        "run_id",
        "cohort",
        "mode",
        "started_at",
        "ended_at",
        "handoff_attempted",
        "handoff_success",
        "events",
    }
    missing = sorted(required - set(trace))
    if missing:
        raise TraceError(f"missing required fields: {', '.join(missing)}")

    if trace.get("schema_version") != 1:
        raise TraceError("schema_version must be 1")

    run_id = trace.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip() or len(run_id) > 128:
        raise TraceError("run_id must be a non-empty string no longer than 128 characters")

    cohort = trace.get("cohort")
    if cohort not in ALLOWED_COHORTS:
        raise TraceError(f"cohort must be one of {', '.join(sorted(ALLOWED_COHORTS))}")

    mode = trace.get("mode")
    if mode not in ALLOWED_MODES:
        raise TraceError(f"mode must be one of {', '.join(sorted(ALLOWED_MODES))}")

    started = _parse_ts(trace.get("started_at"), field="started_at")
    ended = _parse_ts(trace.get("ended_at"), field="ended_at")
    if ended < started:
        raise TraceError("ended_at must not be earlier than started_at")

    attempted = trace.get("handoff_attempted")
    success = trace.get("handoff_success")
    if not isinstance(attempted, bool):
        raise TraceError("handoff_attempted must be boolean")
    if success is not None and not isinstance(success, bool):
        raise TraceError("handoff_success must be boolean or null")
    if not attempted and success is not None:
        raise TraceError("handoff_success must be null when handoff_attempted is false")

    events = trace.get("events")
    if not isinstance(events, list):
        raise TraceError("events must be a list")
    if len(events) > MAX_EVENTS:
        raise TraceError(f"events exceeds maximum of {MAX_EVENTS}")

    previous_ts = started
    normalized_events: list[dict[str, object]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise TraceError(f"events[{index}] must be an object")
        event_type = event.get("type")
        if event_type not in ALLOWED_EVENT_TYPES:
            raise TraceError(
                f"events[{index}].type must be one of {', '.join(sorted(ALLOWED_EVENT_TYPES))}"
            )
        event_ts = _parse_ts(event.get("ts"), field=f"events[{index}].ts")
        if event_ts < started or event_ts > ended:
            raise TraceError(f"events[{index}].ts must be within run bounds")
        if event_ts < previous_ts:
            raise TraceError("events must be ordered by non-decreasing timestamp")
        previous_ts = event_ts

        if event_type == "file_read":
            path = event.get("path")
            if not isinstance(path, str) or not path.strip():
                raise TraceError(f"events[{index}].path is required for file_read")
        if event_type == "tool_call":
            tool = event.get("tool")
            if not isinstance(tool, str) or not tool.strip():
                raise TraceError(f"events[{index}].tool is required for tool_call")
        if event_type == "action":
            name = event.get("name")
            if not isinstance(name, str) or not name.strip():
                raise TraceError(f"events[{index}].name is required for action")

        normalized_events.append(dict(event))

    normalized = dict(trace)
    normalized["run_id"] = run_id.strip()
    normalized["events"] = normalized_events
    return normalized


def compute_metrics(trace: dict[str, object]) -> RunMetrics:
    trace = validate_trace(trace)
    started = _parse_ts(trace["started_at"], field="started_at")
    ended = _parse_ts(trace["ended_at"], field="ended_at")
    events = trace["events"]
    assert isinstance(events, list)

    read_paths: list[str] = []
    tool_calls = 0
    context_expansions = 0
    optional_context_loads = 0
    first_action: datetime | None = None

    for event in events:
        assert isinstance(event, dict)
        event_type = event["type"]
        if event_type == "file_read":
            read_paths.append(str(event["path"]))
        elif event_type == "tool_call":
            tool_calls += 1
        elif event_type == "context_expand":
            context_expansions += 1
        elif event_type == "optional_context_load":
            optional_context_loads += 1
        elif event_type == "action" and first_action is None:
            first_action = _parse_ts(event["ts"], field="action.ts")

    unique_files = len(set(read_paths))
    repeated_reads = len(read_paths) - unique_files
    repeat_ratio = repeated_reads / len(read_paths) if read_paths else 0.0
    first_action_seconds = (
        (first_action - started).total_seconds() if first_action is not None else None
    )

    return RunMetrics(
        run_id=str(trace["run_id"]),
        cohort=str(trace["cohort"]),
        mode=str(trace["mode"]),
        duration_seconds=(ended - started).total_seconds(),
        files_read=len(read_paths),
        unique_files=unique_files,
        repeated_reads=repeated_reads,
        repeat_read_ratio=repeat_ratio,
        tool_calls=tool_calls,
        time_to_first_action_seconds=first_action_seconds,
        context_expansions=context_expansions,
        optional_context_loads=optional_context_loads,
        handoff_attempted=bool(trace["handoff_attempted"]),
        handoff_success=trace["handoff_success"],
    )


def _mean(values: Iterable[float | int]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else 0.0


def summarize_cohort(metrics: Iterable[RunMetrics]) -> dict[str, object]:
    rows = list(metrics)
    attempted = [row for row in rows if row.handoff_attempted]
    successful = [row for row in attempted if row.handoff_success is True]
    first_actions = [
        row.time_to_first_action_seconds
        for row in rows
        if row.time_to_first_action_seconds is not None
    ]

    return {
        "runs": len(rows),
        "avg_files_read": _mean(row.files_read for row in rows),
        "avg_unique_files": _mean(row.unique_files for row in rows),
        "avg_repeated_reads": _mean(row.repeated_reads for row in rows),
        "avg_repeat_read_ratio": _mean(row.repeat_read_ratio for row in rows),
        "avg_tool_calls": _mean(row.tool_calls for row in rows),
        "avg_time_to_first_action_seconds": _mean(first_actions) if first_actions else None,
        "avg_context_expansions": _mean(row.context_expansions for row in rows),
        "avg_optional_context_loads": _mean(row.optional_context_loads for row in rows),
        "handoff_attempts": len(attempted),
        "handoff_success_rate": (len(successful) / len(attempted)) if attempted else None,
    }


def compare_cohorts(metrics: Iterable[RunMetrics]) -> dict[str, object]:
    rows = list(metrics)
    baseline = summarize_cohort(row for row in rows if row.cohort == "baseline")
    routed = summarize_cohort(row for row in rows if row.cohort == "routed")

    numeric_fields = (
        "avg_files_read",
        "avg_unique_files",
        "avg_repeated_reads",
        "avg_repeat_read_ratio",
        "avg_tool_calls",
        "avg_time_to_first_action_seconds",
        "avg_context_expansions",
        "avg_optional_context_loads",
        "handoff_success_rate",
    )
    deltas: dict[str, object] = {}
    for field in numeric_fields:
        base_value = baseline.get(field)
        routed_value = routed.get(field)
        if base_value is None or routed_value is None:
            deltas[field] = {"absolute": None, "percent": None}
            continue
        base_float = float(base_value)
        routed_float = float(routed_value)
        absolute = routed_float - base_float
        percent = (absolute / base_float * 100.0) if base_float != 0 else None
        deltas[field] = {"absolute": absolute, "percent": percent}

    return {
        "baseline": baseline,
        "routed": routed,
        "delta_routed_minus_baseline": deltas,
        "interpretation": {
            "lower_is_better": [
                "avg_files_read",
                "avg_repeated_reads",
                "avg_repeat_read_ratio",
                "avg_tool_calls",
                "avg_time_to_first_action_seconds",
                "avg_context_expansions",
                "avg_optional_context_loads",
            ],
            "higher_is_better": ["handoff_success_rate"],
            "note": "These are observable efficiency proxies. Exact platform token or credit usage is not inferred.",
        },
    }


def load_traces(paths: Iterable[Path]) -> list[dict[str, object]]:
    traces: list[dict[str, object]] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            traces.extend(validate_trace(item) for item in payload)
        else:
            traces.append(validate_trace(payload))
    return traces


def render_markdown(metrics: list[RunMetrics], comparison: dict[str, object]) -> str:
    lines = [
        "# Agent Efficiency Evaluation",
        "",
        "Exact platform token/credit usage is not inferred. Metrics below are observable efficiency proxies.",
        "",
        "## Runs",
        "",
        "| Run | Cohort | Mode | Files read | Repeated reads | Tool calls | First action (s) | Context expansions | Optional loads | Handoff |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in metrics:
        first_action = (
            f"{row.time_to_first_action_seconds:.3f}"
            if row.time_to_first_action_seconds is not None
            else "n/a"
        )
        handoff = (
            "n/a"
            if not row.handoff_attempted
            else "success"
            if row.handoff_success is True
            else "failure"
            if row.handoff_success is False
            else "unknown"
        )
        lines.append(
            f"| {row.run_id} | {row.cohort} | {row.mode} | {row.files_read} | "
            f"{row.repeated_reads} | {row.tool_calls} | {first_action} | "
            f"{row.context_expansions} | {row.optional_context_loads} | {handoff} |"
        )

    lines.extend(["", "## Cohort comparison", ""])
    baseline = comparison["baseline"]
    routed = comparison["routed"]
    assert isinstance(baseline, dict)
    assert isinstance(routed, dict)
    lines.append("| Metric | Baseline | Routed |")
    lines.append("|---|---:|---:|")
    for field in (
        "runs",
        "avg_files_read",
        "avg_repeated_reads",
        "avg_repeat_read_ratio",
        "avg_tool_calls",
        "avg_time_to_first_action_seconds",
        "avg_context_expansions",
        "avg_optional_context_loads",
        "handoff_success_rate",
    ):
        lines.append(f"| {field} | {baseline.get(field)} | {routed.get(field)} |")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate bounded agent-efficiency traces without collecting full chat history."
    )
    parser.add_argument("traces", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    traces = load_traces(args.traces)
    metrics = [compute_metrics(trace) for trace in traces]
    comparison = compare_cohorts(metrics)

    if args.json:
        print(
            json.dumps(
                {
                    "runs": [asdict(row) for row in metrics],
                    "comparison": comparison,
                },
                indent=2,
            )
        )
    else:
        print(render_markdown(metrics, comparison), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
