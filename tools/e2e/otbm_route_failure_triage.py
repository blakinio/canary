#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

FORMAT = "canary-otbm-e2e-failure-triage-v1"
SCHEMA_VERSION = 1
DEFAULT_OUTPUT = "otbm-route-failure-triage.json"

FAILURE_CATEGORIES = frozenset(
    {
        "ROUTE_RESOLUTION_FAILURE",
        "ROUTE_PREFLIGHT_FAILURE",
        "PLAN_LOAD_FAILURE",
        "INITIAL_POSITION_MISMATCH",
        "MOVEMENT_DIVERGENCE",
        "BLOCKED_TILE",
        "INTERACTION_UNSUPPORTED",
        "INTERACTION_TIMEOUT",
        "TELEPORT_NOT_TRIGGERED",
        "WRONG_TRANSITION_DESTINATION",
        "WRONG_FLOOR_DELTA",
        "SERVER_DISCONNECT",
        "PERSISTENCE_FAILURE",
        "RELOG_FAILURE",
    }
)

ROUTE_MARKER_RE = re.compile(
    r"^route_(?P<step>.+)_edge_(?P<edge>[1-9][0-9]*)(?:_interaction_[1-9][0-9]*)?$"
)
POSITION_PAIR_RE = re.compile(
    r"actual=(?P<actual>-?[0-9]+,-?[0-9]+,-?[0-9]+)\s+"
    r"expected=(?P<expected>-?[0-9]+,-?[0-9]+,-?[0-9]+)"
)


class TriageError(ValueError):
    pass


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _read_events(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    events: list[dict[str, str]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        if line_number == 1 and line == "timestamp\tkey\tvalue":
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        timestamp, key, value = parts
        events.append(
            {
                "line": str(line_number),
                "timestamp": timestamp,
                "key": key,
                "value": value,
            }
        )
    return events


def _route_steps(manifest: Mapping[str, Any]) -> list[dict[str, str]]:
    scenario = manifest.get("scenario")
    if not isinstance(scenario, Mapping):
        return []
    steps = scenario.get("steps")
    if not isinstance(steps, list):
        return []
    result: list[dict[str, str]] = []
    for step in steps:
        if not isinstance(step, Mapping) or step.get("action") != "follow_route":
            continue
        step_id = step.get("id")
        route_id = step.get("route")
        if isinstance(step_id, str) and isinstance(route_id, str):
            result.append({"stepId": step_id, "routeId": route_id})
    return result


def _event_index(events: Sequence[Mapping[str, str]], key: str, value: str | None = None) -> int | None:
    for index, event in enumerate(events):
        if event.get("key") != key:
            continue
        if value is not None and event.get("value") != value:
            continue
        return index
    return None


def _first_event(events: Sequence[Mapping[str, str]], key: str) -> dict[str, str] | None:
    index = _event_index(events, key)
    return dict(events[index]) if index is not None else None


def _has_event(events: Sequence[Mapping[str, str]], key: str, value: str | None = None) -> bool:
    return _event_index(events, key, value) is not None


def _active_route_marker(
    events: Sequence[Mapping[str, str]], error_index: int | None
) -> tuple[str, int, dict[str, str]] | None:
    if error_index is None:
        return None
    active: dict[str, tuple[int, dict[str, str]]] = {}
    for event in events[:error_index]:
        key = event.get("key", "")
        match = ROUTE_MARKER_RE.fullmatch(key)
        if not match:
            continue
        if event.get("value") == "start":
            active[key] = (int(match.group("edge")), dict(event))
        elif event.get("value") in {"success", "failure"}:
            active.pop(key, None)
    if not active:
        return None
    key, (edge_index, event) = next(reversed(active.items()))
    return key, edge_index, event


def _route_context(
    artifacts: Path,
    route_steps: Sequence[Mapping[str, str]],
    events: Sequence[Mapping[str, str]],
    error_index: int | None,
) -> dict[str, Any]:
    active = _active_route_marker(events, error_index)
    if active is None:
        return {}
    marker, edge_index, marker_event = active
    match = ROUTE_MARKER_RE.fullmatch(marker)
    if match is None:
        return {}
    step_id = match.group("step")
    route_id = next(
        (step["routeId"] for step in route_steps if step.get("stepId") == step_id),
        None,
    )
    context: dict[str, Any] = {
        "stepId": step_id,
        "edgeIndex": edge_index,
        "marker": marker,
        "markerEvent": marker_event,
    }
    if route_id is None:
        return context
    context["routeId"] = route_id
    plan_path = artifacts / f"route-{route_id}.json"
    plan = _read_json(plan_path)
    if plan is None:
        return context
    edges = plan.get("edges")
    if isinstance(edges, list) and 1 <= edge_index <= len(edges):
        edge = edges[edge_index - 1]
        if isinstance(edge, Mapping):
            context["edge"] = dict(edge)
    return context


def _position(value: str) -> tuple[int, int, int] | None:
    parts = value.split(",")
    if len(parts) != 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None


def _wrong_transition_category(error: str, context: Mapping[str, Any]) -> str:
    match = POSITION_PAIR_RE.search(error)
    if match is None:
        return "WRONG_TRANSITION_DESTINATION"
    actual = _position(match.group("actual"))
    expected = _position(match.group("expected"))
    edge = context.get("edge")
    if actual is None or expected is None or not isinstance(edge, Mapping):
        return "WRONG_TRANSITION_DESTINATION"
    source = edge.get("from")
    destination = edge.get("to")
    if not (
        isinstance(source, list)
        and len(source) == 3
        and isinstance(destination, list)
        and len(destination) == 3
    ):
        return "WRONG_TRANSITION_DESTINATION"
    try:
        floor_changes = int(source[2]) != int(destination[2])
    except (TypeError, ValueError):
        return "WRONG_TRANSITION_DESTINATION"
    if floor_changes and actual[:2] == expected[:2] and actual[2] != expected[2]:
        return "WRONG_FLOOR_DELTA"
    return "WRONG_TRANSITION_DESTINATION"


def _transition_not_triggered_category(context: Mapping[str, Any]) -> str:
    edge = context.get("edge")
    if isinstance(edge, Mapping):
        transition_kind = edge.get("transitionKind", edge.get("transition_kind"))
        if transition_kind == "teleport":
            return "TELEPORT_NOT_TRIGGERED"
    return "INTERACTION_TIMEOUT"


def _client_error_category(error: str, context: Mapping[str, Any]) -> str | None:
    if "INITIAL_POSITION_MISMATCH:" in error:
        return "INITIAL_POSITION_MISMATCH"
    if "MOVEMENT_DIVERGENCE:" in error or "FINAL_POSITION_MISMATCH:" in error:
        return "MOVEMENT_DIVERGENCE"
    if "MOVEMENT_TIMEOUT:" in error:
        return "BLOCKED_TILE"
    if "INTERACTION_TIMEOUT:" in error:
        return "INTERACTION_TIMEOUT"
    if "TRANSITION_NOT_TRIGGERED:" in error:
        return _transition_not_triggered_category(context)
    if "WRONG_TRANSITION_DESTINATION:" in error:
        return _wrong_transition_category(error, context)
    if "INTERACTION_FAILED:" in error:
        lowered = error.lower()
        unsupported_markers = (
            "unsupported use interaction kind",
            "unsupported movement interaction kind",
            "unsupported transition interaction kind",
            "invalid exact map target contract",
            "transition requires exactly one interaction",
        )
        if any(marker in lowered for marker in unsupported_markers):
            return "INTERACTION_UNSUPPORTED"
        return None
    lowered = error.lower()
    if any(
        marker in lowered
        for marker in (
            "scenario plan is unavailable",
            "invalid scenario plan contract",
            "invalid route plan contract",
            "route executor unavailable",
            "invalid route executor contract",
            "route plan unavailable for logical id",
            "failed to open scenario plan",
            "failed to compile scenario plan",
            "failed to execute scenario plan",
            "failed to open route executor",
            "failed to compile route executor",
            "failed to execute route executor",
        )
    ):
        return "PLAN_LOAD_FAILURE"
    if "persistence check " in lowered or "persistence plan is unavailable" in lowered:
        return "PERSISTENCE_FAILURE"
    if "login error in phase 2" in lowered or "connection error in phase 2" in lowered:
        return "RELOG_FAILURE"
    if "game ended before phase 2 entered the world" in lowered:
        return "RELOG_FAILURE"
    if "unexpected disconnect before safe logout" in lowered:
        return "SERVER_DISCONNECT"
    if "connection error in phase 1" in lowered:
        return "SERVER_DISCONNECT"
    return None


def _preflight_failure(artifacts: Path, route_steps: Sequence[Mapping[str, str]]) -> tuple[Path, dict[str, Any]] | None:
    ordered_paths: list[Path] = []
    seen: set[Path] = set()
    for step in route_steps:
        path = artifacts / f"route-{step['routeId']}-preflight.json"
        if path not in seen:
            ordered_paths.append(path)
            seen.add(path)
    for path in sorted(artifacts.glob("route-*-preflight.json")):
        if path not in seen:
            ordered_paths.append(path)
            seen.add(path)
    for path in ordered_paths:
        report = _read_json(path)
        if report is None:
            continue
        if report.get("ok") is False or report.get("status") in {"blocked", "failed", "failure"}:
            return path, report
    return None


def _failure_result(
    category: str,
    *,
    evidence: Sequence[str],
    first_failure: Mapping[str, Any],
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if category not in FAILURE_CATEGORIES:
        raise TriageError(f"unsupported failure category: {category}")
    result: dict[str, Any] = {
        "format": FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "status": "failure",
        "routeAware": True,
        "failureCategory": category,
        "firstFailure": dict(first_failure),
        "evidence": sorted(set(evidence)),
    }
    if context:
        result["routeContext"] = dict(context)
    return result


def classify_artifacts(artifact_dir: Path) -> dict[str, Any]:
    artifacts = artifact_dir.expanduser().resolve()
    manifest_path = artifacts / "scenario-manifest.json"
    manifest = _read_json(manifest_path)
    if manifest is None:
        return {
            "format": FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "status": "unclassified",
            "routeAware": None,
            "failureCategory": None,
            "firstFailure": None,
            "evidence": [],
            "unclassifiedReason": "scenario manifest is missing or invalid",
        }

    route_steps = _route_steps(manifest)
    if not route_steps:
        return {
            "format": FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "status": "not-applicable",
            "routeAware": False,
            "failureCategory": None,
            "firstFailure": None,
            "evidence": [manifest_path.name],
        }

    preflight_failure = _preflight_failure(artifacts, route_steps)
    if preflight_failure is not None:
        path, report = preflight_failure
        first_blocker = report.get("firstBlocker")
        findings = report.get("findings")
        first_failure: dict[str, Any] = {
            "source": path.name,
            "kind": "exact-map-preflight",
            "firstBlocker": first_blocker,
        }
        if isinstance(findings, list) and findings:
            first_failure["firstFinding"] = findings[0]
        return _failure_result(
            "ROUTE_PREFLIGHT_FAILURE",
            evidence=[manifest_path.name, path.name],
            first_failure=first_failure,
        )

    route_preparation_path = artifacts / "route-preparation.json"
    preparation = _read_json(route_preparation_path)
    if preparation is None or preparation.get("status") != "passed":
        preparer_hash_path = artifacts / "route-preparer.sha256"
        if preparer_hash_path.is_file():
            return _failure_result(
                "ROUTE_RESOLUTION_FAILURE",
                evidence=[manifest_path.name, preparer_hash_path.name],
                first_failure={
                    "source": "route-preparation",
                    "kind": "route-resolution",
                    "detail": "route preparer was invoked but no passed route-preparation summary was retained",
                },
            )
        return {
            "format": FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "status": "unclassified",
            "routeAware": True,
            "failureCategory": None,
            "firstFailure": None,
            "evidence": [manifest_path.name],
            "unclassifiedReason": "route preparation did not pass and route preparer invocation evidence is absent",
        }

    events_path = artifacts / "client-events.tsv"
    events = _read_events(events_path)
    error_index = _event_index(events, "error")
    error_event = dict(events[error_index]) if error_index is not None else None
    context = _route_context(artifacts, route_steps, events, error_index)
    if error_event is not None:
        category = _client_error_category(error_event["value"], context)
        if category is not None:
            return _failure_result(
                category,
                evidence=[manifest_path.name, route_preparation_path.name, events_path.name],
                first_failure={
                    "source": events_path.name,
                    "kind": "client-error-event",
                    "line": int(error_event["line"]),
                    "timestamp": error_event["timestamp"],
                    "key": error_event["key"],
                    "value": error_event["value"],
                },
                context=context,
            )

    result_path = artifacts / "result.json"
    result = _read_json(result_path)
    if result is not None:
        if result.get("status") == "success":
            return {
                "format": FORMAT,
                "schemaVersion": SCHEMA_VERSION,
                "status": "success",
                "routeAware": True,
                "failureCategory": None,
                "firstFailure": None,
                "evidence": sorted(
                    {
                        manifest_path.name,
                        route_preparation_path.name,
                        result_path.name,
                        *([events_path.name] if events_path.is_file() else []),
                    }
                ),
            }
        if result.get("schema_version") == 1 and result.get("phase") == "scenario-resolution":
            return _failure_result(
                "PLAN_LOAD_FAILURE",
                evidence=[manifest_path.name, route_preparation_path.name, result_path.name],
                first_failure={
                    "source": result_path.name,
                    "kind": "runner-phase",
                    "phase": result.get("phase"),
                    "shellExitCode": result.get("shell_exit_code"),
                },
            )
        checks = result.get("checks")
        if isinstance(checks, Mapping):
            if checks.get("scenario_sql_assertions") is False or checks.get("lastlogout_persisted") is False:
                return _failure_result(
                    "PERSISTENCE_FAILURE",
                    evidence=[manifest_path.name, route_preparation_path.name, result_path.name],
                    first_failure={
                        "source": result_path.name,
                        "kind": "result-checks",
                        "checks": dict(checks),
                    },
                )
            if checks.get("two_server_logins_observed") is False:
                persistence_confirmed = _has_event(events, "server_persistence_1", "confirmed")
                login_two = _has_event(events, "login_2", "success")
                if persistence_confirmed and not login_two:
                    return _failure_result(
                        "RELOG_FAILURE",
                        evidence=[
                            manifest_path.name,
                            route_preparation_path.name,
                            result_path.name,
                            events_path.name,
                        ],
                        first_failure={
                            "source": result_path.name,
                            "kind": "lifecycle-incomplete",
                            "detail": "server persistence was confirmed but second login was not observed",
                        },
                    )

    if error_event is not None:
        return {
            "format": FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "status": "unclassified",
            "routeAware": True,
            "failureCategory": None,
            "firstFailure": {
                "source": events_path.name,
                "kind": "client-error-event",
                "line": int(error_event["line"]),
                "timestamp": error_event["timestamp"],
                "key": error_event["key"],
                "value": error_event["value"],
            },
            "evidence": [manifest_path.name, route_preparation_path.name, events_path.name],
            "routeContext": context,
            "unclassifiedReason": "explicit client error did not map deterministically to a supported programme category",
        }

    return {
        "format": FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "status": "unclassified",
        "routeAware": True,
        "failureCategory": None,
        "firstFailure": None,
        "evidence": sorted(
            {
                manifest_path.name,
                route_preparation_path.name,
                *([result_path.name] if result_path.is_file() else []),
                *([events_path.name] if events_path.is_file() else []),
            }
        ),
        "unclassifiedReason": "retained route-aware evidence does not deterministically identify a supported first-failure category",
    }


def write_triage(artifact_dir: Path, output: Path | None = None) -> dict[str, Any]:
    artifacts = artifact_dir.expanduser().resolve()
    result = classify_artifacts(artifacts)
    destination = output.expanduser().resolve() if output is not None else artifacts / DEFAULT_OUTPUT
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify the first deterministic OTBM-aware Universal Physical E2E failure"
    )
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = write_triage(args.artifact_dir, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
