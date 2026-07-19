#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any

MAX_ASSERTIONS = 32
ASSERTION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
PLAYER_FIELDS = frozenset({"level", "experience"})


class PersistenceAssertionError(ValueError):
    pass


def _sql_string(value: str) -> str:
    if "\x00" in value:
        raise PersistenceAssertionError("fixture character must not contain NUL")
    return "'" + value.replace("'", "''") + "'"


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PersistenceAssertionError(f"{path} must be an object")
    return value


def _reject_unknown_fields(mapping: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise PersistenceAssertionError(f"{path} contains unknown field(s): {', '.join(unknown)}")


def _require_string(mapping: dict[str, Any], key: str, path: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise PersistenceAssertionError(f"{path}.{key} must be a non-empty string")
    return value.strip()


def _require_nonnegative_int(mapping: dict[str, Any], key: str, path: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PersistenceAssertionError(f"{path}.{key} must be a non-negative integer")
    if value > 9_223_372_036_854_775_807:
        raise PersistenceAssertionError(f"{path}.{key} exceeds signed BIGINT range")
    return value


def validate_persistence_assertions(raw: Any) -> list[dict[str, Any]]:
    """Validate the feature-neutral persistence contract for runtime and SQL use."""

    if raw is None:
        return []

    config = _require_mapping(raw, "scenario.assertions.persistence")
    _reject_unknown_fields(config, {"required", "checks"}, "scenario.assertions.persistence")

    required = config.get("required")
    if not isinstance(required, bool):
        raise PersistenceAssertionError("scenario.assertions.persistence.required must be a boolean")

    checks = config.get("checks")
    if not isinstance(checks, list):
        raise PersistenceAssertionError("scenario.assertions.persistence.checks must be an array")
    if len(checks) > MAX_ASSERTIONS:
        raise PersistenceAssertionError(
            f"scenario.assertions.persistence.checks must contain at most {MAX_ASSERTIONS} assertions"
        )
    if required and not checks:
        raise PersistenceAssertionError(
            "scenario.assertions.persistence.checks must not be empty when persistence is required"
        )
    if checks and not required:
        raise PersistenceAssertionError(
            "scenario.assertions.persistence.required must be true when persistence checks are declared"
        )

    validated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for index, item in enumerate(checks):
        path = f"scenario.assertions.persistence.checks[{index}]"
        check = _require_mapping(item, path)
        _reject_unknown_fields(check, {"id", "type", "field", "equals"}, path)

        assertion_id = _require_string(check, "id", path)
        if not ASSERTION_ID_RE.fullmatch(assertion_id):
            raise PersistenceAssertionError(f"{path}.id must match {ASSERTION_ID_RE.pattern}")
        if assertion_id in seen_ids:
            raise PersistenceAssertionError(
                f"scenario.assertions.persistence.checks contains duplicate id {assertion_id!r}"
            )
        seen_ids.add(assertion_id)

        assertion_type = _require_string(check, "type", path)
        if assertion_type != "player_field":
            raise PersistenceAssertionError(
                f"{path}.type unsupported: {assertion_type!r}; allowed: player_field"
            )

        field = _require_string(check, "field", path)
        if field not in PLAYER_FIELDS:
            raise PersistenceAssertionError(
                f"{path}.field unsupported: {field!r}; allowed: {', '.join(sorted(PLAYER_FIELDS))}"
            )
        expected = _require_nonnegative_int(check, "equals", path)

        validated.append(
            {
                "id": assertion_id,
                "type": assertion_type,
                "field": field,
                "equals": expected,
            }
        )

    return validated


def compile_persistence_assertions(raw: Any, *, character: str) -> list[str]:
    """Compile validated checks to the existing post-cycle scalar SQL contract.

    The Universal Physical E2E SQL evaluator accepts one semicolon-free SELECT per
    assertion and considers only stdout == "1" successful. The same typed checks
    are also emitted to the controlled-client phase-two plan by run_agent_e2e.py.
    """

    checks = validate_persistence_assertions(raw)
    if not checks:
        return []
    if not isinstance(character, str) or not character.strip():
        raise PersistenceAssertionError("fixture character must be a non-empty string")

    character_sql = _sql_string(character.strip())
    queries: list[str] = []
    for check in checks:
        queries.append(
            "SELECT IF((SELECT `"
            + str(check["field"])
            + "` FROM `players` WHERE `name` = "
            + character_sql
            + ") = "
            + str(check["equals"])
            + ", 1, 0)"
        )
    return queries
