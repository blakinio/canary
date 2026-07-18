#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SECRET_KEY_RE = re.compile(r"(?:password|secret|token|private[_-]?key)$", re.IGNORECASE)
ALLOWED_SECRET_REFERENCES = {"password_env"}
MAX_STEPS = 64
MAX_STEP_TEXT = 512
MAX_STEP_DELAY_MS = 120_000
MAX_STEP_COUNT = 64
CANONICAL_PR_SUITE = "login"
CANONICAL_PR_SCENARIO = "relog"

DIRECTIONS = {
    "north",
    "east",
    "south",
    "west",
    "northeast",
    "southeast",
    "southwest",
    "northwest",
}

ACTION_FIELDS: dict[str, set[str]] = {
    "wait": {"id", "action", "ms"},
    "walk": {"id", "action", "direction", "count", "interval_ms"},
    "talk": {"id", "action", "text"},
    "attack_visible": {"id", "action", "creature", "timeout_ms"},
    "use_inventory_item": {"id", "action", "item_id"},
    "request_quest_log": {"id", "action"},
    "request_channels": {"id", "action"},
    "observe_online": {"id", "action", "expected"},
    "observe_position_changed": {"id", "action"},
    "observe_floor_delta": {"id", "action", "delta"},
    "observe_health_percent_below": {"id", "action", "percent"},
    "observe_inventory_count_at_least": {"id", "action", "item_id", "count", "tier"},
    "wait_creature": {"id", "action", "creature", "present", "timeout_ms"},
    "observe_attacking": {"id", "action", "expected"},
}


class ScenarioError(ValueError):
    pass


@dataclass(frozen=True)
class Scenario:
    path: Path
    data: dict[str, Any]

    @property
    def suite(self) -> str:
        return str(self.data["suite"])

    @property
    def scenario_id(self) -> str:
        return str(self.data["id"])

    @property
    def key(self) -> str:
        return f"{self.suite}/{self.scenario_id}"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def scenario_root(root: Path) -> Path:
    return root / "tests" / "e2e" / "scenarios"


def _load_pr_scenario_selector():
    module_path = Path(__file__).resolve().with_name("pr_scenario_selection.py")
    spec = importlib.util.spec_from_file_location("canary_e2e_pr_scenario_selection", module_path)
    if spec is None or spec.loader is None:
        raise ScenarioError(f"cannot load PR scenario selector: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_pr_fallback_selection(root: Path, suite: str, scenario_id: str) -> tuple[str, str]:
    """Replace only the canonical PR fallback with one exact changed scenario."""

    if (suite, scenario_id) != (CANONICAL_PR_SUITE, CANONICAL_PR_SCENARIO):
        return suite, scenario_id
    if os.environ.get("GITHUB_EVENT_NAME") != "pull_request":
        return suite, scenario_id

    event_path_raw = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path_raw:
        raise ScenarioError("GITHUB_EVENT_PATH is required for pull-request scenario selection")
    event_path = Path(event_path_raw)
    try:
        payload = json.loads(event_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ScenarioError(f"cannot read pull-request event payload: {exc}") from exc
    if not isinstance(payload, dict):
        raise ScenarioError("pull-request event payload must be a JSON object")

    pull_request = payload.get("pull_request")
    repository = payload.get("repository")
    if not isinstance(pull_request, dict) or not isinstance(repository, dict):
        raise ScenarioError("pull-request event payload is missing repository or pull_request evidence")

    current_repository = os.environ.get("GITHUB_REPOSITORY") or repository.get("full_name")
    head = pull_request.get("head")
    base = pull_request.get("base")
    if not isinstance(head, dict) or not isinstance(base, dict):
        raise ScenarioError("pull-request event payload is missing exact head/base evidence")
    head_repository = head.get("repo")
    if not isinstance(head_repository, dict):
        raise ScenarioError("pull-request event payload is missing head repository evidence")

    pr_head_repository = head_repository.get("full_name")
    base_sha = base.get("sha")
    head_sha = head.get("sha")
    if not all(isinstance(value, str) for value in (current_repository, pr_head_repository, base_sha, head_sha)):
        raise ScenarioError("pull-request event payload contains invalid repository or SHA evidence")

    selector = _load_pr_scenario_selector()
    try:
        selection = selector.select_for_event(
            event_name="pull_request",
            current_repository=current_repository,
            pr_head_repository=pr_head_repository,
            requested_suite=suite,
            requested_scenario=scenario_id,
            base_sha=base_sha,
            head_sha=head_sha,
            repo_root=root,
            api_repository=current_repository,
            api_url=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
            api_token=os.environ.get("GITHUB_TOKEN", ""),
        )
    except selector.SelectionError as exc:
        raise ScenarioError(f"cannot prove pull-request scenario selection: {exc}") from exc

    print(
        "Pull-request scenario selection: "
        f"{selection.suite}/{selection.scenario} reason={selection.reason}"
        + (f" manifest={selection.manifest}" if selection.manifest else "")
    )
    return selection.suite, selection.scenario


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScenarioError(f"{path} must be an object")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ScenarioError(f"{path} must be an array")
    return value


def _require_string(mapping: dict[str, Any], key: str, path: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ScenarioError(f"{path}.{key} must be a non-empty string")
    return value.strip()


def _require_positive_int(mapping: dict[str, Any], key: str, path: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ScenarioError(f"{path}.{key} must be a positive integer")
    return value


def _require_bounded_positive_int(
    mapping: dict[str, Any],
    key: str,
    path: str,
    maximum: int,
    *,
    default: int | None = None,
) -> int:
    if key not in mapping and default is not None:
        return default
    value = _require_positive_int(mapping, key, path)
    if value > maximum:
        raise ScenarioError(f"{path}.{key} must be <= {maximum}")
    return value


def _require_bool(mapping: dict[str, Any], key: str, path: str) -> bool:
    value = mapping.get(key)
    if not isinstance(value, bool):
        raise ScenarioError(f"{path}.{key} must be a boolean")
    return value


def _require_uint16(mapping: dict[str, Any], key: str, path: str) -> int:
    value = _require_positive_int(mapping, key, path)
    if value > 65535:
        raise ScenarioError(f"{path}.{key} must be <= 65535")
    return value


def _reject_unknown_fields(mapping: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ScenarioError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _require_safe_text(mapping: dict[str, Any], key: str, path: str) -> str:
    value = _require_string(mapping, key, path)
    if "\n" in value or "\r" in value or "\x00" in value:
        raise ScenarioError(f"{path}.{key} must not contain control newlines or NUL")
    if len(value) > MAX_STEP_TEXT:
        raise ScenarioError(f"{path}.{key} must be <= {MAX_STEP_TEXT} characters")
    return value


def _walk_for_embedded_secrets(value: Any, path: str = "scenario") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if SECRET_KEY_RE.search(str(key)) and key not in ALLOWED_SECRET_REFERENCES:
                if child not in (None, "", [], {}):
                    yield f"{child_path} must not embed a credential; reference an environment variable instead"
            yield from _walk_for_embedded_secrets(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_for_embedded_secrets(child, f"{path}[{index}]")


def _validate_step(step: Any, index: int) -> dict[str, Any]:
    path = f"scenario.steps[{index}]"
    mapping = _require_mapping(step, path)
    step_id = _require_string(mapping, "id", path)
    if not SLUG_RE.fullmatch(step_id):
        raise ScenarioError(f"{path}.id must match {SLUG_RE.pattern}")
    action = _require_string(mapping, "action", path)
    allowed = ACTION_FIELDS.get(action)
    if allowed is None:
        raise ScenarioError(
            f"{path}.action unsupported: {action!r}; allowed: {', '.join(sorted(ACTION_FIELDS))}"
        )
    _reject_unknown_fields(mapping, allowed, path)

    if action == "wait":
        _require_bounded_positive_int(mapping, "ms", path, MAX_STEP_DELAY_MS)
    elif action == "walk":
        direction = _require_string(mapping, "direction", path).lower()
        if direction not in DIRECTIONS:
            raise ScenarioError(f"{path}.direction unsupported: {direction!r}")
        _require_bounded_positive_int(mapping, "count", path, MAX_STEP_COUNT, default=1)
        _require_bounded_positive_int(mapping, "interval_ms", path, 10_000, default=250)
    elif action == "talk":
        _require_safe_text(mapping, "text", path)
    elif action == "attack_visible":
        _require_safe_text(mapping, "creature", path)
        _require_bounded_positive_int(mapping, "timeout_ms", path, MAX_STEP_DELAY_MS, default=10_000)
    elif action == "use_inventory_item":
        _require_uint16(mapping, "item_id", path)
    elif action in {"request_quest_log", "request_channels", "observe_position_changed"}:
        pass
    elif action == "observe_online":
        _require_bool(mapping, "expected", path)
    elif action == "observe_floor_delta":
        delta = mapping.get("delta")
        if not isinstance(delta, int) or isinstance(delta, bool) or delta == 0 or abs(delta) > 15:
            raise ScenarioError(f"{path}.delta must be a non-zero integer between -15 and 15")
    elif action == "observe_health_percent_below":
        percent = mapping.get("percent")
        if not isinstance(percent, int) or isinstance(percent, bool) or not 0 <= percent <= 100:
            raise ScenarioError(f"{path}.percent must be an integer between 0 and 100")
    elif action == "observe_inventory_count_at_least":
        _require_uint16(mapping, "item_id", path)
        _require_bounded_positive_int(mapping, "count", path, 1_000_000)
        if "tier" in mapping:
            tier = mapping["tier"]
            if not isinstance(tier, int) or isinstance(tier, bool) or not 0 <= tier <= 255:
                raise ScenarioError(f"{path}.tier must be an integer between 0 and 255")
    elif action == "wait_creature":
        _require_safe_text(mapping, "creature", path)
        _require_bool(mapping, "present", path)
        _require_bounded_positive_int(mapping, "timeout_ms", path, MAX_STEP_DELAY_MS, default=10_000)
    elif action == "observe_attacking":
        _require_bool(mapping, "expected", path)

    return mapping


def validate_steps(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw_steps = data.get("steps")
    if raw_steps is None:
        return []
    steps = _require_list(raw_steps, "scenario.steps")
    if not steps:
        raise ScenarioError("scenario.steps must not be empty when present")
    if len(steps) > MAX_STEPS:
        raise ScenarioError(f"scenario.steps must contain at most {MAX_STEPS} actions")

    validated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, step in enumerate(steps):
        mapping = _validate_step(step, index)
        step_id = str(mapping["id"])
        if step_id in seen_ids:
            raise ScenarioError(f"scenario.steps contains duplicate id {step_id!r}")
        seen_ids.add(step_id)
        validated.append(mapping)
    return validated


def validate_scenario(path: Path, root: Path) -> Scenario:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScenarioError(f"{path}: invalid JSON: {exc}") from exc
    except OSError as exc:
        raise ScenarioError(f"{path}: cannot read scenario: {exc}") from exc

    if not isinstance(data, dict):
        raise ScenarioError(f"{path}: scenario root must be an object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ScenarioError(
            f"{path}: schema_version must be {SCHEMA_VERSION}, got {data.get('schema_version')!r}"
        )

    scenario_id = _require_string(data, "id", "scenario")
    suite = _require_string(data, "suite", "scenario")
    _require_string(data, "name", "scenario")
    _require_string(data, "program_id", "scenario")
    _require_string(data, "description", "scenario")
    if not SLUG_RE.fullmatch(scenario_id):
        raise ScenarioError(f"{path}: id must match {SLUG_RE.pattern}")
    if not SLUG_RE.fullmatch(suite):
        raise ScenarioError(f"{path}: suite must match {SLUG_RE.pattern}")

    relative = path.resolve().relative_to(scenario_root(root).resolve())
    if len(relative.parts) < 2 or relative.parts[0] != suite:
        raise ScenarioError(f"{path}: suite must match its directory under tests/e2e/scenarios")

    client = _require_mapping(data.get("client"), "scenario.client")
    _require_string(client, "repository", "scenario.client")
    _require_string(client, "ref", "scenario.client")
    automation = _require_string(client, "automation", "scenario.client")
    automation_path = (root / automation).resolve()
    if not automation_path.is_relative_to(root.resolve()):
        raise ScenarioError(f"{path}: client.automation must remain inside the repository")
    if not automation_path.is_file():
        raise ScenarioError(f"{path}: client.automation does not exist: {automation}")

    server = _require_mapping(data.get("server"), "scenario.server")
    _require_string(server, "datapack", "scenario.server")
    _require_string(server, "map", "scenario.server")
    _require_string(server, "database_image", "scenario.server")

    fixture = _require_mapping(data.get("fixture"), "scenario.fixture")
    _require_string(fixture, "account", "scenario.fixture")
    _require_string(fixture, "password_env", "scenario.fixture")
    _require_string(fixture, "character", "scenario.fixture")
    _require_string(fixture, "world", "scenario.fixture")
    _require_string(fixture, "host", "scenario.fixture")
    port = _require_positive_int(fixture, "game_port", "scenario.fixture")
    if port > 65535:
        raise ScenarioError(f"{path}: scenario.fixture.game_port must be <= 65535")

    timing = _require_mapping(data.get("timing"), "scenario.timing")
    _require_positive_int(timing, "global_timeout_seconds", "scenario.timing")
    _require_positive_int(timing, "session_hold_ms", "scenario.timing")
    _require_positive_int(timing, "relog_delay_ms", "scenario.timing")

    assertions = _require_mapping(data.get("assertions"), "scenario.assertions")
    markers = _require_list(assertions.get("required_markers"), "scenario.assertions.required_markers")
    if not markers or any(not isinstance(marker, str) or not marker for marker in markers):
        raise ScenarioError(f"{path}: required_markers must contain non-empty strings")
    sql = _require_list(assertions.get("sql"), "scenario.assertions.sql")
    if not sql or any(not isinstance(item, str) or not item.strip() for item in sql):
        raise ScenarioError(f"{path}: assertions.sql must contain non-empty SQL statements")

    artifacts = _require_list(data.get("artifacts"), "scenario.artifacts")
    if not artifacts or any(not isinstance(item, str) or not item.strip() for item in artifacts):
        raise ScenarioError(f"{path}: artifacts must contain non-empty repository-relative names")
    for artifact in artifacts:
        artifact_path = Path(artifact)
        if artifact_path.is_absolute() or ".." in artifact_path.parts:
            raise ScenarioError(f"{path}: unsafe artifact path {artifact!r}")

    validate_steps(data)

    secret_errors = list(_walk_for_embedded_secrets(data))
    if secret_errors:
        raise ScenarioError(f"{path}: " + "; ".join(secret_errors))

    return Scenario(path=path, data=data)


def discover(root: Path) -> list[Scenario]:
    directory = scenario_root(root)
    if not directory.is_dir():
        raise ScenarioError(f"scenario directory does not exist: {directory}")

    scenarios: list[Scenario] = []
    errors: list[str] = []
    for path in sorted(directory.rglob("*.json")):
        try:
            scenarios.append(validate_scenario(path, root))
        except ScenarioError as exc:
            errors.append(str(exc))

    if errors:
        raise ScenarioError("\n".join(errors))
    if not scenarios:
        raise ScenarioError(f"no scenarios found under {directory}")

    seen: dict[str, Path] = {}
    for scenario in scenarios:
        previous = seen.get(scenario.key)
        if previous:
            raise ScenarioError(f"duplicate scenario key {scenario.key}: {previous} and {scenario.path}")
        seen[scenario.key] = scenario.path
    return scenarios


def select(scenarios: Iterable[Scenario], suite: str, scenario_id: str) -> Scenario:
    matches = [scenario for scenario in scenarios if scenario.suite == suite and scenario.scenario_id == scenario_id]
    if len(matches) != 1:
        available = ", ".join(sorted(scenario.key for scenario in scenarios))
        raise ScenarioError(f"scenario {suite}/{scenario_id} not found; available: {available}")
    return matches[0]


def normalized_manifest(scenario: Scenario) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "key": scenario.key,
        "source": scenario.path.as_posix(),
        "scenario": scenario.data,
    }


def github_environment(scenario: Scenario) -> dict[str, str]:
    data = scenario.data
    client = data["client"]
    fixture = data["fixture"]
    timing = data["timing"]
    return {
        "AGENT_E2E_SUITE": scenario.suite,
        "AGENT_E2E_SCENARIO_ID": scenario.scenario_id,
        "AGENT_E2E_SCENARIO_KEY": scenario.key,
        "AGENT_E2E_CLIENT_REPOSITORY": str(client["repository"]),
        "AGENT_E2E_CLIENT_REF": str(client["ref"]),
        "AGENT_E2E_CLIENT_AUTOMATION": str(client["automation"]),
        "AGENT_E2E_ACCOUNT": str(fixture["account"]),
        "AGENT_E2E_PASSWORD_ENV": str(fixture["password_env"]),
        "AGENT_E2E_CHARACTER": str(fixture["character"]),
        "AGENT_E2E_WORLD": str(fixture["world"]),
        "AGENT_E2E_HOST": str(fixture["host"]),
        "AGENT_E2E_GAME_PORT": str(fixture["game_port"]),
        "AGENT_E2E_GLOBAL_TIMEOUT_SECONDS": str(timing["global_timeout_seconds"]),
        "AGENT_E2E_SESSION_HOLD_MS": str(timing["session_hold_ms"]),
        "AGENT_E2E_RELOG_DELAY_MS": str(timing["relog_delay_ms"]),
    }


def write_github_env(path: Path, values: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            if "\n" in value or "\r" in value:
                raise ScenarioError(f"environment value for {key} contains a newline")
            handle.write(f"{key}={value}\n")


def _lua_string(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'


def _lua_value(value: Any) -> str:
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _lua_string(value)
    if isinstance(value, int):
        return str(value)
    raise ScenarioError(f"unsupported Lua plan value type: {type(value).__name__}")


def render_lua_plan(scenario: Scenario) -> str:
    steps = validate_steps(scenario.data)
    lines = [
        "-- Generated by tools/e2e/run_agent_e2e.py; do not edit.",
        "return {",
        f"  schema_version = {SCHEMA_VERSION},",
        f"  scenario = {_lua_string(scenario.key)},",
        "  steps = {",
    ]
    for step in steps:
        fields = []
        for key in sorted(step):
            fields.append(f"{key} = {_lua_value(step[key])}")
        lines.append("    { " + ", ".join(fields) + " },")
    lines.extend(["  },", "}", ""])
    return "\n".join(lines)


def write_lua_plan(path: Path, scenario: Scenario) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_lua_plan(scenario), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover and validate universal Canary agent E2E scenarios.")
    parser.add_argument("--root", type=Path, default=repository_root())
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List validated scenarios.")
    subparsers.add_parser("validate", help="Validate every scenario.")

    resolve = subparsers.add_parser("resolve", help="Resolve one scenario and emit its manifest/environment.")
    resolve.add_argument("--suite", required=True)
    resolve.add_argument("--scenario", required=True)
    resolve.add_argument("--manifest", type=Path)
    resolve.add_argument("--github-env", type=Path)
    resolve.add_argument("--plan-lua", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        scenarios = discover(root)
        if args.command == "list":
            for scenario in scenarios:
                print(f"{scenario.key}\t{scenario.data['name']}\t{scenario.path.relative_to(root)}")
        elif args.command == "validate":
            print(f"Validated {len(scenarios)} E2E scenario(s).")
        elif args.command == "resolve":
            selected_suite, selected_scenario = _resolve_pr_fallback_selection(root, args.suite, args.scenario)
            scenario = select(scenarios, selected_suite, selected_scenario)
            manifest = normalized_manifest(scenario)
            rendered = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            if args.manifest:
                args.manifest.parent.mkdir(parents=True, exist_ok=True)
                args.manifest.write_text(rendered, encoding="utf-8")
            else:
                sys.stdout.write(rendered)
            plan_path = args.plan_lua
            if plan_path is None and args.manifest is not None and scenario.data.get("steps") is not None:
                plan_path = args.manifest.with_name("scenario-plan.lua")
            if plan_path is not None:
                write_lua_plan(plan_path, scenario)
            if args.github_env:
                write_github_env(args.github_env, github_environment(scenario))
        else:  # pragma: no cover
            parser.error(f"unsupported command {args.command}")
    except (ScenarioError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
