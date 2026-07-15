from __future__ import annotations

import unittest

import efficiency_eval


def make_trace(
    *,
    run_id: str,
    cohort: str,
    files: list[str],
    tool_calls: int,
    first_action_second: int,
    context_expansions: int,
    optional_loads: int,
    handoff_attempted: bool,
    handoff_success: bool | None,
) -> dict[str, object]:
    events: list[dict[str, object]] = []
    second = 1
    for path in files:
        events.append(
            {
                "ts": f"2026-07-15T17:00:{second:02d}Z",
                "type": "file_read",
                "path": path,
            }
        )
        second += 1
    for index in range(tool_calls):
        events.append(
            {
                "ts": f"2026-07-15T17:00:{second:02d}Z",
                "type": "tool_call",
                "tool": f"tool-{index}",
            }
        )
        second += 1
    for _ in range(context_expansions):
        events.append(
            {
                "ts": f"2026-07-15T17:00:{second:02d}Z",
                "type": "context_expand",
            }
        )
        second += 1
    for _ in range(optional_loads):
        events.append(
            {
                "ts": f"2026-07-15T17:00:{second:02d}Z",
                "type": "optional_context_load",
            }
        )
        second += 1

    action_ts = f"2026-07-15T17:00:{first_action_second:02d}Z"
    events.append({"ts": action_ts, "type": "action", "name": "first_patch"})
    events.sort(key=lambda item: str(item["ts"]))

    return {
        "schema_version": 1,
        "run_id": run_id,
        "cohort": cohort,
        "mode": "CHAT",
        "started_at": "2026-07-15T17:00:00Z",
        "ended_at": "2026-07-15T17:01:00Z",
        "handoff_attempted": handoff_attempted,
        "handoff_success": handoff_success,
        "events": events,
    }


class ValidationTests(unittest.TestCase):
    def test_rejects_success_without_handoff_attempt(self) -> None:
        trace = make_trace(
            run_id="bad",
            cohort="routed",
            files=[],
            tool_calls=0,
            first_action_second=1,
            context_expansions=0,
            optional_loads=0,
            handoff_attempted=False,
            handoff_success=None,
        )
        trace["handoff_success"] = True
        with self.assertRaises(efficiency_eval.TraceError):
            efficiency_eval.validate_trace(trace)

    def test_rejects_out_of_order_events(self) -> None:
        trace = make_trace(
            run_id="bad-order",
            cohort="baseline",
            files=["a.md"],
            tool_calls=0,
            first_action_second=10,
            context_expansions=0,
            optional_loads=0,
            handoff_attempted=False,
            handoff_success=None,
        )
        trace["events"] = [
            {"ts": "2026-07-15T17:00:10Z", "type": "action", "name": "patch"},
            {"ts": "2026-07-15T17:00:05Z", "type": "file_read", "path": "a.md"},
        ]
        with self.assertRaises(efficiency_eval.TraceError):
            efficiency_eval.validate_trace(trace)


class MetricTests(unittest.TestCase):
    def test_counts_repeated_reads_and_first_action(self) -> None:
        trace = make_trace(
            run_id="routed-1",
            cohort="routed",
            files=["AGENTS.md", "AGENTS.md", "docs/agents/CONTEXT_ROUTING.md"],
            tool_calls=2,
            first_action_second=12,
            context_expansions=1,
            optional_loads=1,
            handoff_attempted=True,
            handoff_success=True,
        )
        metrics = efficiency_eval.compute_metrics(trace)
        self.assertEqual(3, metrics.files_read)
        self.assertEqual(2, metrics.unique_files)
        self.assertEqual(1, metrics.repeated_reads)
        self.assertAlmostEqual(1 / 3, metrics.repeat_read_ratio)
        self.assertEqual(2, metrics.tool_calls)
        self.assertEqual(12.0, metrics.time_to_first_action_seconds)
        self.assertEqual(1, metrics.context_expansions)
        self.assertEqual(1, metrics.optional_context_loads)
        self.assertTrue(metrics.handoff_success)

    def test_comparison_reports_routed_delta(self) -> None:
        baseline = efficiency_eval.compute_metrics(
            make_trace(
                run_id="baseline-1",
                cohort="baseline",
                files=["a", "a", "b", "c"],
                tool_calls=8,
                first_action_second=20,
                context_expansions=3,
                optional_loads=2,
                handoff_attempted=True,
                handoff_success=False,
            )
        )
        routed = efficiency_eval.compute_metrics(
            make_trace(
                run_id="routed-1",
                cohort="routed",
                files=["a", "b"],
                tool_calls=4,
                first_action_second=10,
                context_expansions=1,
                optional_loads=0,
                handoff_attempted=True,
                handoff_success=True,
            )
        )

        comparison = efficiency_eval.compare_cohorts([baseline, routed])
        delta = comparison["delta_routed_minus_baseline"]
        self.assertEqual(-2.0, delta["avg_files_read"]["absolute"])
        self.assertEqual(-4.0, delta["avg_tool_calls"]["absolute"])
        self.assertEqual(-10.0, delta["avg_time_to_first_action_seconds"]["absolute"])
        self.assertEqual(1.0, delta["handoff_success_rate"]["absolute"])

    def test_markdown_does_not_claim_token_usage(self) -> None:
        metrics = [
            efficiency_eval.compute_metrics(
                make_trace(
                    run_id="routed-1",
                    cohort="routed",
                    files=["a"],
                    tool_calls=1,
                    first_action_second=2,
                    context_expansions=0,
                    optional_loads=0,
                    handoff_attempted=False,
                    handoff_success=None,
                )
            )
        ]
        output = efficiency_eval.render_markdown(
            metrics,
            efficiency_eval.compare_cohorts(metrics),
        )
        self.assertIn("observable efficiency proxies", output)
        self.assertNotIn("tokens saved", output.casefold())


if __name__ == "__main__":
    unittest.main()
