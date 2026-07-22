#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any

MAX_ASSERTIONS = 32
ASSERTION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
PLAYER_FIELDS = frozenset({"level", "experience"})
PLAYER_ITEM_TABLES = {
    "inventory": "player_items",
    "depot": "player_depotitems",
    "inbox": "player_inboxitems",
}
PLAYER_SKILL_LEVELS = {
    "fist": {"column": "skill_fist", "client_skill_id": 0},
    "club": {"column": "skill_club", "client_skill_id": 1},
    "sword": {"column": "skill_sword", "client_skill_id": 2},
    "axe": {"column": "skill_axe", "client_skill_id": 3},
    "distance": {"column": "skill_dist", "client_skill_id": 4},
    "shielding": {"column": "skill_shielding", "client_skill_id": 5},
    "fishing": {"column": "skill_fishing", "client_skill_id": 6},
}
PLAYER_VOCATIONS = {
    "none": {"server_vocation_id": 0, "client_vocation_id": 0},
    "sorcerer": {"server_vocation_id": 1, "client_vocation_id": 3},
    "druid": {"server_vocation_id": 2, "client_vocation_id": 4},
    "paladin": {"server_vocation_id": 3, "client_vocation_id": 2},
    "knight": {"server_vocation_id": 4, "client_vocation_id": 1},
    "master_sorcerer": {"server_vocation_id": 5, "client_vocation_id": 13},
    "elder_druid": {"server_vocation_id": 6, "client_vocation_id": 14},
    "royal_paladin": {"server_vocation_id": 7, "client_vocation_id": 12},
    "elite_knight": {"server_vocation_id": 8, "client_vocation_id": 11},
    "monk": {"server_vocation_id": 9, "client_vocation_id": 5},
    "exalted_monk": {"server_vocation_id": 10, "client_vocation_id": 15},
}
MAX_UINT8 = 255
MAX_UINT16 = 65_535
MAX_UINT32 = 4_294_967_295
MAX_SAFE_LUA_INTEGER = 9_007_199_254_740_991
MIN_INT32 = -2_147_483_648
MAX_INT32 = 2_147_483_647


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


def _require_bool(mapping: dict[str, Any], key: str, path: str) -> bool:
    value = mapping.get(key)
    if not isinstance(value, bool):
        raise PersistenceAssertionError(f"{path}.{key} must be a boolean")
    return value


def _require_int_range(
    mapping: dict[str, Any],
    key: str,
    path: str,
    *,
    minimum: int,
    maximum: int,
    description: str,
) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise PersistenceAssertionError(
            f"{path}.{key} must be {description} between {minimum} and {maximum}"
        )
    return value


def _require_nonnegative_bigint(mapping: dict[str, Any], key: str, path: str) -> int:
    return _require_int_range(
        mapping,
        key,
        path,
        minimum=0,
        maximum=MAX_SAFE_LUA_INTEGER,
        description="an exact Lua-safe non-negative integer",
    )


def _validate_all_persistence_assertions(raw: Any) -> list[dict[str, Any]]:
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

        assertion_id = _require_string(check, "id", path)
        if not ASSERTION_ID_RE.fullmatch(assertion_id):
            raise PersistenceAssertionError(f"{path}.id must match {ASSERTION_ID_RE.pattern}")
        if assertion_id in seen_ids:
            raise PersistenceAssertionError(
                f"scenario.assertions.persistence.checks contains duplicate id {assertion_id!r}"
            )
        seen_ids.add(assertion_id)

        assertion_type = _require_string(check, "type", path)
        if assertion_type == "player_field":
            _reject_unknown_fields(check, {"id", "type", "field", "equals"}, path)
            field = _require_string(check, "field", path)
            if field not in PLAYER_FIELDS:
                raise PersistenceAssertionError(
                    f"{path}.field unsupported: {field!r}; allowed: {', '.join(sorted(PLAYER_FIELDS))}"
                )
            expected = _require_nonnegative_bigint(check, "equals", path)
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "field": field,
                    "equals": expected,
                }
            )
            continue

        if assertion_type == "player_storage":
            _reject_unknown_fields(check, {"id", "type", "key", "equals"}, path)
            storage_key = _require_int_range(
                check,
                "key",
                path,
                minimum=0,
                maximum=MAX_UINT32,
                description="an unsigned integer",
            )
            expected = _require_int_range(
                check,
                "equals",
                path,
                minimum=MIN_INT32,
                maximum=MAX_INT32,
                description="a signed integer",
            )
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "key": storage_key,
                    "equals": expected,
                }
            )
            continue

        if assertion_type == "player_item_presence":
            _reject_unknown_fields(
                check,
                {"id", "type", "location", "item_id", "present"},
                path,
            )
            location = _require_string(check, "location", path)
            if location not in PLAYER_ITEM_TABLES:
                raise PersistenceAssertionError(
                    f"{path}.location unsupported: {location!r}; allowed: "
                    + ", ".join(sorted(PLAYER_ITEM_TABLES))
                )
            item_id = _require_int_range(
                check,
                "item_id",
                path,
                minimum=1,
                maximum=MAX_UINT16,
                description="an unsigned item id",
            )
            present = _require_bool(check, "present", path)
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "location": location,
                    "item_id": item_id,
                    "present": present,
                }
            )
            continue

        if assertion_type == "player_balance":
            _reject_unknown_fields(check, {"id", "type", "equals"}, path)
            expected = _require_int_range(
                check,
                "equals",
                path,
                minimum=0,
                maximum=MAX_SAFE_LUA_INTEGER,
                description="an exact Lua-safe integer",
            )
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "equals": expected,
                }
            )
            continue

        if assertion_type == "player_magic_level":
            _reject_unknown_fields(check, {"id", "type", "equals"}, path)
            expected = _require_int_range(
                check,
                "equals",
                path,
                minimum=0,
                maximum=MAX_UINT16,
                description="an unsigned magic level",
            )
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "equals": expected,
                }
            )
            continue

        if assertion_type == "player_soul":
            _reject_unknown_fields(check, {"id", "type", "equals"}, path)
            expected = _require_int_range(
                check,
                "equals",
                path,
                minimum=0,
                maximum=MAX_UINT8,
                description="an unsigned soul value",
            )
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "equals": expected,
                }
            )
            continue

        if assertion_type == "player_skill_level":
            _reject_unknown_fields(check, {"id", "type", "skill", "equals"}, path)
            skill = _require_string(check, "skill", path)
            if skill not in PLAYER_SKILL_LEVELS:
                raise PersistenceAssertionError(
                    f"{path}.skill unsupported: {skill!r}; allowed: "
                    + ", ".join(sorted(PLAYER_SKILL_LEVELS))
                )
            expected = _require_int_range(
                check,
                "equals",
                path,
                minimum=0,
                maximum=MAX_UINT16,
                description="an unsigned skill level",
            )
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "skill": skill,
                    "client_skill_id": PLAYER_SKILL_LEVELS[skill]["client_skill_id"],
                    "equals": expected,
                }
            )
            continue

        if assertion_type == "player_vocation":
            _reject_unknown_fields(check, {"id", "type", "vocation"}, path)
            vocation = _require_string(check, "vocation", path)
            if vocation not in PLAYER_VOCATIONS:
                raise PersistenceAssertionError(
                    f"{path}.vocation unsupported: {vocation!r}; allowed: "
                    + ", ".join(sorted(PLAYER_VOCATIONS))
                )
            validated.append(
                {
                    "id": assertion_id,
                    "type": assertion_type,
                    "vocation": vocation,
                    "server_vocation_id": PLAYER_VOCATIONS[vocation]["server_vocation_id"],
                    "client_vocation_id": PLAYER_VOCATIONS[vocation]["client_vocation_id"],
                }
            )
            continue

        raise PersistenceAssertionError(
            f"{path}.type unsupported: {assertion_type!r}; allowed: "
            "player_field, player_storage, player_item_presence, player_balance, "
            "player_magic_level, player_soul, player_skill_level, player_vocation"
        )

    return validated


def validate_persistence_assertions(raw: Any) -> list[dict[str, Any]]:
    """Return checks with a trustworthy controlled-client read surface.

    `player_field` checks use directly comparable LocalPlayer getters. `player_balance`
    uses the maintained LocalPlayer resource-balance getter and is restricted to exact
    Lua-safe integers. `player_magic_level` uses the maintained uint16 magic-level
    getter. `player_soul` uses the maintained uint8 soul getter. `player_skill_level`
    uses a fixed classic-skill mapping and the maintained LocalPlayer base-skill getter.
    `player_vocation`, arbitrary `player_storage` values, and cross-location
    `player_item_presence` checks remain on the post-cycle SQL boundary because the
    current physical protocol path does not provide a trustworthy exact promoted-vocation
    value through `LocalPlayer.getVocation()`.
    """

    client_checks: list[dict[str, Any]] = []
    for check in _validate_all_persistence_assertions(raw):
        if check["type"] in {
            "player_field",
            "player_balance",
            "player_magic_level",
            "player_soul",
            "player_skill_level",
        }:
            client_checks.append(check)
    return client_checks


def compile_persistence_assertions(raw: Any, *, character: str) -> list[str]:
    """Compile validated checks to the existing post-cycle scalar SQL contract.

    The Universal Physical E2E SQL evaluator accepts one semicolon-free SELECT per
    assertion and considers only stdout == "1" successful. `player_field`,
    `player_balance`, `player_magic_level`, `player_soul`, and `player_skill_level`
    checks are also emitted to the controlled-client phase-two plan by run_agent_e2e.py.
    `player_storage`, `player_item_presence`, and normalized `player_vocation` checks
    remain database-only after the full two-session cycle.
    """

    checks = _validate_all_persistence_assertions(raw)
    if not checks:
        return []
    if not isinstance(character, str) or not character.strip():
        raise PersistenceAssertionError("fixture character must be a non-empty string")

    character_sql = _sql_string(character.strip())
    queries: list[str] = []
    for check in checks:
        if check["type"] == "player_field":
            queries.append(
                "SELECT IF((SELECT `"
                + str(check["field"])
                + "` FROM `players` WHERE `name` = "
                + character_sql
                + ") = "
                + str(check["equals"])
                + ", 1, 0)"
            )
            continue

        if check["type"] == "player_storage":
            queries.append(
                "SELECT IF(EXISTS(SELECT 1 FROM `player_storage` AS `ps` "
                "INNER JOIN `players` AS `p` ON `p`.`id` = `ps`.`player_id` "
                "WHERE `p`.`name` = "
                + character_sql
                + " AND `ps`.`key` = "
                + str(check["key"])
                + " AND `ps`.`value` = "
                + str(check["equals"])
                + "), 1, 0)"
            )
            continue

        if check["type"] == "player_item_presence":
            table = PLAYER_ITEM_TABLES[str(check["location"])]
            existence = "EXISTS" if check["present"] else "NOT EXISTS"
            queries.append(
                "SELECT IF("
                + existence
                + "(SELECT 1 FROM `"
                + table
                + "` AS `pi` INNER JOIN `players` AS `p` ON `p`.`id` = `pi`.`player_id` "
                "WHERE `p`.`name` = "
                + character_sql
                + " AND `pi`.`itemtype` = "
                + str(check["item_id"])
                + "), 1, 0)"
            )
            continue

        if check["type"] == "player_balance":
            queries.append(
                "SELECT IF((SELECT `balance` FROM `players` WHERE `name` = "
                + character_sql
                + ") = "
                + str(check["equals"])
                + ", 1, 0)"
            )
            continue

        if check["type"] == "player_magic_level":
            queries.append(
                "SELECT IF((SELECT `maglevel` FROM `players` WHERE `name` = "
                + character_sql
                + ") = "
                + str(check["equals"])
                + ", 1, 0)"
            )
            continue

        if check["type"] == "player_soul":
            queries.append(
                "SELECT IF((SELECT `soul` FROM `players` WHERE `name` = "
                + character_sql
                + ") = "
                + str(check["equals"])
                + ", 1, 0)"
            )
            continue

        if check["type"] == "player_vocation":
            queries.append(
                "SELECT IF((SELECT `vocation` FROM `players` WHERE `name` = "
                + character_sql
                + ") = "
                + str(check["server_vocation_id"])
                + ", 1, 0)"
            )
            continue

        skill_column = PLAYER_SKILL_LEVELS[str(check["skill"])]["column"]
        queries.append(
            "SELECT IF((SELECT `"
            + str(skill_column)
            + "` FROM `players` WHERE `name` = "
            + character_sql
            + ") = "
            + str(check["equals"])
            + ", 1, 0)"
        )
    return queries
