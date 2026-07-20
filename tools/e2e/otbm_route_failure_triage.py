#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

FORMAT = "canary-otbm-e2e-failure-triage-v1"
SCHEMA_VERSION = 1

FAILURE_CATEGORIES = (
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
)
ROUTE_CODE_RE = re.compile(
    r"\b(INITIAL_POSITION_MISMATCH|MOVEMENT_DIVERGENCE|MOVEMENT_TIMEOUT|"
    r"INTERACTION_FAILED|INTERACTION_TIMEOUT|TRANSITION_NOT_TRIGGERED|"
    r"WRONG_TRANSITION_DESTINATION|FINAL_POSITION_MISMATCH):\s*(.*)$"
)
EDGE_MARKER_RE = re.compile(
    r"^route_(?P<step>.+)_edge_(?P<edge>[1-9][0-9]*)(?:_interaction_[1-9][0-9]*)?$"
)
POSITION_PAIR_RE = re.compile(
    r"actual=(?P<actual>-?\d+,-?\d+,-?\d+)\s+expected=(?P<expected>-?\d+,-?\d+,-?\d+)"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _read_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events = []
    for line_no, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines()[1:], start=1
    ):
        parts = line.split("\t", 2)
        if len(parts) == 3:
            events.append(
                {"line": line_no, "timestamp": parts[0], "key": parts[1], "value": parts[2]}
            )
    return events


def _route_steps(manifest: Mapping[str, Any] | None) -> list[dict[str, str]]:
    if not isinstance(manifest, Mapping):
        return []
    scenario = manifest.get("scenario")
    steps = scenario.get("steps") if isinstance(scenario, Mapping) else None
    if not isinstance(steps, list):
        return []
    result = []
    for step in steps:
        if not isinstance(step, Mapping) or step.get("action") != "follow_route":
            continue
        step_id, route_id = step.get("id"), step.get("route")
        if isinstance(step_id, str) and step_id and isinstance(route_id, str) and route_id:
            result.append({"stepId": step_id, "routeId": route_id})
    return result


def _has_event(events: Iterable[Mapping[str, Any]], key: str, value: str | None = None) -> bool:
    return any(
        event.get("key") == key and (value is None or event.get("value") == value)
        for event in events
    )


def _first_error(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((event for event in events if event["key"] == "error"), None)


def _route_context(
    artifacts: Path,
    route_steps: list[dict[str, str]],
    events: list[dict[str, Any]],
    error_event: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if error_event is None:
        return {}

    active: tuple[str, int, str] | None = None
    failed: tuple[str, int, str] | None = None
    for event in events:
        if int(event["line"]) >= int(error_event["line"]):
            break
        match = EDGE_MARKER_RE.fullmatch(str(event["key"]))
        if not match:
            continue
        marker = str(event["key"])
        candidate = (match.group("step"), int(match.group("edge")), marker)
        if event["value"] == "start":
            active = candidate
            continue
        if event["value"] == "success":
            if active and active[2] == marker:
                active = None
            continue
        if event["value"] == "failure":
            failed = candidate
            if active and active[2] == marker:
                active = None

    selected = failed or active
    if selected is None:
        return {}
    step_id, edge_index, marker = selected
    route_id = next(
        (step["routeId"] for step in route_steps if step["stepId"] == step_id), None
    )
    context: dict[str, Any] = {
        "routeStepId": step_id,
        "edgeIndex": edge_index,
        "eventMarker": marker,
    }
    if route_id is not None:
        context["routeId"] = route_id
    else:
        return context

    plan = _read_json(artifacts / f"route-{route_id}.json")
    edges = plan.get("edges") if isinstance(plan, Mapping) else None
    if isinstance(edges, list) and 1 <= edge_index <= len(edges):
        edge = edges[edge_index - 1]
        if isinstance(edge, Mapping):
            context["edge"] = dict(edge)
    return context


def _transition_kind(context: Mapping[str, Any]) -> str | None:
    edge = context.get("edge")
    if not isinstance(edge, Mapping):
        return None
    value = edge.get("transitionKind", edge.get("transition_kind"))
    return value if isinstance(value, str) else None


def _position(raw: str) -> tuple[int, int, int] | None:
    try:
        values = tuple(int(part) for part in raw.split(","))
    except ValueError:
        return None
    return values if len(values) == 3 else None


def _wrong_transition_category(detail: str, context: Mapping[str, Any]) -> str:
    edge = context.get("edge")
    if not isinstance(edge, Mapping):
        return "WRONG_TRANSITION_DESTINATION"
    source, destination = edge.get("from"), edge.get("to")
    if not (
        isinstance(source, list)
        and len(source) == 3
        and isinstance(destination, list)
        and len(destination) == 3
        and source[2] != destination[2]
    ):
        return "WRONG_TRANSITION_DESTINATION"
    match = POSITION_PAIR_RE.search(detail)
    if not match:
        return "WRONG_TRANSITION_DESTINATION"
    actual, expected = _position(match.group("actual")), _position(match.group("expected"))
    if actual and expected and actual[:2] == expected[:2] and actual[2] != expected[2]:
        return "WRONG_FLOOR_DELTA"
    return "WRONG_TRANSITION_DESTINATION"


def _client_category(
    message: str, context: Mapping[str, Any], events: list[dict[str, Any]]
) -> tuple[str | None, str | None, str]:
    lower = message.lower()
    if "login error in phase 2" in lower or "connection error in phase 2" in lower:
        return "RELOG_FAILURE", "CLIENT_LIFECYCLE", message
    if "game ended before phase 2 entered the world" in lower:
        return "RELOG_FAILURE", "CLIENT_LIFECYCLE", message
    if "unexpected disconnect before safe logout" in lower or "connection error in phase 1" in lower:
        return "SERVER_DISCONNECT", "CLIENT_LIFECYCLE", message
    if "persistence check " in lower or "persistence plan" in lower:
        return "PERSISTENCE_FAILURE", "CLIENT_LIFECYCLE", message
    if any(
        fragment in lower
        for fragment in (
            "scenario plan is unavailable",
            "failed to open scenario plan",
            "failed to compile scenario plan",
            "failed to execute scenario plan",
            "invalid scenario plan contract",
            "invalid route plan contract",
            "route plan unavailable for logical id",
            "failed to open route executor",
            "failed to compile route executor",
            "failed to execute route executor",
            "invalid route executor contract",
            "route executor unavailable",
        )
    ):
        return "PLAN_LOAD_FAILURE", "PLAN_LOAD", message
    if "global timeout" in lower:
        if _has_event(events, "server_persistence_1", "waiting") and not _has_event(
            events, "server_persistence_1", "confirmed"
        ):
            return "PERSISTENCE_FAILURE", "CLIENT_LIFECYCLE", message
        if _has_event(events, "server_persistence_1", "confirmed") and not _has_event(
            events, "login_2", "success"
        ):
            return "RELOG_FAILURE", "CLIENT_LIFECYCLE", message

    match = ROUTE_CODE_RE.search(message)
    if not match:
        return None, None, message
    code, detail = match.group(1), match.group(2)
    if code == "INITIAL_POSITION_MISMATCH":
        return "INITIAL_POSITION_MISMATCH", code, detail
    if code in {"MOVEMENT_DIVERGENCE", "FINAL_POSITION_MISMATCH"}:
        return "MOVEMENT_DIVERGENCE", code, detail
    if code == "MOVEMENT_TIMEOUT":
        return "BLOCKED_TILE", code, detail
    if code == "INTERACTION_TIMEOUT":
        return "INTERACTION_TIMEOUT", code, detail
    if code == "TRANSITION_NOT_TRIGGERED":
        return (
            "TELEPORT_NOT_TRIGGERED" if _transition_kind(context) == "teleport" else "INTERACTION_TIMEOUT"
        ), code, detail
    if code == "WRONG_TRANSITION_DESTINATION":
        return _wrong_transition_category(detail, context), code, detail
    if code == "INTERACTION_FAILED":
        return (
            ("INTERACTION_UNSUPPORTED", code, detail)
            if "unsupported" in detail.lower()
            else (None, code, detail)
        )
    return None, code, detail


def _preflight_failure(
    artifacts: Path, route_steps: list[dict[str, str]]
) -> tuple[str, dict[str, Any]] | None:
    route_ids = [step["routeId"] for step in route_steps]
    for path in sorted(artifacts.glob("route-*-preflight.json")):
        route_id = path.name[len("route-") : -len("-preflight.json")]
        if route_id not in route_ids:
            route_ids.append(route_id)
    for route_id in dict.fromkeys(route_ids):
        path = artifacts / f"route-{route_id}-preflight.json"
        document = _read_json(path)
        if document and (
            document.get("ok") is False
            or document.get("status") in {"failed", "blocked", "failure"}
        ):
            return path.name, document
    return None


def _result(
    category: str | None,
    *,
    source: str,
    code: str | None = None,
    detail: str | None = None,
    context: Mapping[str, Any] | None = None,
    evidence: Iterable[str] = (),
    unclassified_reason: str | None = None,
) -> dict[str, Any]:
    first_failure: dict[str, Any] = {"source": source}
    if code is not None:
        first_failure["code"] = code
    if detail is not None:
        first_failure["detail"] = detail
    if context:
        first_failure.update(context)
    output = {
        "format": FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "status": "failure" if category else "unclassified",
        "routeAware": True,
        "failureCategory": category,
        "firstFailure": first_failure,
        "evidence": sorted(set(evidence)),
    }
    if unclassified_reason:
        output["unclassifiedReason"] = unclassified_reason
    return output


def classify_artifacts(artifact_dir: Path) -> dict[str, Any]:
    artifacts = artifact_dir.expanduser().resolve()
    manifest_path = artifacts / "scenario-manifest.json"
    manifest = _read_json(manifest_path)
    route_steps = _route_steps(manifest)
    if manifest is None:
        return {
            "format": FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "status": "unclassified",
            "routeAware": None,
            "failureCategory": None,
            "firstFailure": {"source": "scenario-manifest"},
            "evidence": [],
            "unclassifiedReason": "scenario manifest is unavailable or invalid",
        }
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

    preflight = _preflight_failure(artifacts, route_steps)
    if preflight:
        filename, report = preflight
        blocker = report.get("firstBlocker")
        detail = json.dumps(blocker, sort_keys=True) if blocker is not None else "exact-map preflight failed"
        return _result(
            "ROUTE_PREFLIGHT_FAILURE",
            source="route-preflight",
            code="PREFLIGHT_BLOCKED",
            detail=detail,
            evidence=[manifest_path.name, filename],
        )

    preparation_path = artifacts / "route-preparation.json"
    preparation = _read_json(preparation_path)
    if not preparation or preparation.get("status") != "passed":
        preparer_hash = artifacts / "route-preparer.sha256"
        if preparer_hash.is_file():
            return _result(
                "ROUTE_RESOLUTION_FAILURE",
                source="route-preparation",
                code="ROUTE_PREPARATION_FAILED",
                detail="route preparation did not produce a passed summary",
                evidence=[manifest_path.name, preparer_hash.name],
            )
        return _result(
            None,
            source="route-preparation",
            detail="route preparation evidence is absent before the canonical preparer was invoked",
            evidence=[manifest_path.name],
            unclassified_reason="insufficient evidence to classify route preparation as a resolution failure",
        )

    events_path = artifacts / "client-events.tsv"
    events = _read_events(events_path)
    error = _first_error(events)
    context = _route_context(artifacts, route_steps, events, error)
    if error:
        category, code, detail = _client_category(str(error["value"]), context, events)
        evidence = [manifest_path.name, preparation_path.name, events_path.name]
        route_id = context.get("routeId")
        if isinstance(route_id, str) and (artifacts / f"route-{route_id}.json").is_file():
            evidence.append(f"route-{route_id}.json")
        return _result(
            category,
            source="client-event",
            code=code,
            detail=detail,
            context={**context, "eventLine": error["line"], "eventKey": error["key"]},
            evidence=evidence,
            unclassified_reason=(
                None
                if category
                else "explicit client failure does not map deterministically to a supported category"
            ),
        )

    result_path = artifacts / "result.json"
    result = _read_json(result_path)
    if result and result.get("status") == "success":
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
                    preparation_path.name,
                    result_path.name,
                    *([events_path.name] if events_path.is_file() else []),
                }
            ),
        }
    if result and result.get("schema_version") == 1 and result.get("phase") == "scenario-resolution":
        return _result(
            "PLAN_LOAD_FAILURE",
            source="physical-runner",
            code="SCENARIO_RESOLUTION_FAILED",
            detail="physical runner failed while materializing the scenario plan",
            evidence=[manifest_path.name, preparation_path.name, result_path.name],
        )

    checks = result.get("checks") if isinstance(result, Mapping) else None
    if isinstance(checks, Mapping):
        if any(
            checks.get(name) is False
            for name in ("scenario_sql_assertions", "lastlogin_persisted", "lastlogout_persisted")
        ):
            return _result(
                "PERSISTENCE_FAILURE",
                source="result",
                code="PERSISTENCE_CHECK_FAILED",
                detail="one or more durable persistence checks failed",
                evidence=[manifest_path.name, preparation_path.name, result_path.name],
            )
        if (
            checks.get("two_server_logins_observed") is False
            and _has_event(events, "login_1", "success")
            and _has_event(events, "server_persistence_1", "confirmed")
            and not _has_event(events, "login_2", "success")
        ):
            return _result(
                "RELOG_FAILURE",
                source="result",
                code="SECOND_LOGIN_NOT_OBSERVED",
                detail="first login and persistence completed but second login was not observed",
                evidence=[manifest_path.name, preparation_path.name, result_path.name, events_path.name],
            )

    return _result(
        None,
        source="evidence",
        detail="route-aware evidence did not prove success or a supported first-failure category",
        evidence=[
            manifest_path.name,
            preparation_path.name,
            *([events_path.name] if events_path.is_file() else []),
            *([result_path.name] if result_path.is_file() else []),
        ],
        unclassified_reason="insufficient deterministic evidence",
    )


def write_triage(artifact_dir: Path, output: Path | None = None) -> dict[str, Any]:
    artifacts = artifact_dir.expanduser().resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    target = output.expanduser().resolve() if output else artifacts / "otbm-route-failure-triage.json"
    result = classify_artifacts(artifacts)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify the first deterministic failure in retained OTBM-aware Universal Physical E2E artifacts"
    )
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(json.dumps(write_triage(args.artifact_dir, args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
