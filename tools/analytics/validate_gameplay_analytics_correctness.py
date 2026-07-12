#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CORRECTNESS = ROOT / "data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua"
RUNTIME = ROOT / "data-otservbr-global/scripts/systems/gameplay_analytics.lua"
CONFIG = ROOT / "data-otservbr-global/scripts/config/gameplay_analytics.lua"
FIREBALL = ROOT / "data/scripts/runes/fireball.lua"
INTENSE_HEALING = ROOT / "data/scripts/runes/intense_healing_rune.lua"
DOCS = ROOT / "docs/systems/gameplay-analytics.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def validate_correctness(text: str) -> None:
    for token in (
        "Analytics.correctnessInstalled",
        "Analytics.correctnessStats",
        "local function utcDay",
        "local function hasCombatOrDeath",
        'reason == "death"',
        'reason == "utc-day-rollover"',
        "Analytics.config.minimumSessionSeconds = minimum",
        "function Analytics.expireInactive()",
        "discardedNonCombatSessions",
        "expiredNonCombatSessions",
        "shortDeathSessionsPersisted",
        "shortRolloverSessionsPersisted",
    ):
        require(token in text, f"correctness layer lacks {token}")
    require(
        "if not hasCombatOrDeath(session) then" in text,
        "non-combat sessions must be rejected before persistence",
    )
    require(
        "utcDay(current.startedAt) < utcDay(timestamp)" in text,
        "active sessions must roll over at the next UTC day",
    )
    require(
        'callFinishWithMinimum(player, "activity-timeout", 0)' in text,
        "expired non-combat sessions must reach the explicit eligibility filter regardless of normal minimum duration",
    )


def validate_runtime(text: str) -> None:
    reliability = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")'
    correctness = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")'
    require(reliability in text, "runtime lacks reliability layer")
    require(correctness in text, "runtime lacks correctness layer")
    require(text.index(reliability) < text.index(correctness), "correctness layer must load after reliability")
    for field in ("dayRollovers", "discardedNonCombatSessions", "shortDeathSessionsPersisted"):
        require(f"status.{field}" in text, f"runtime status command lacks {field}")


def validate_config(text: str) -> None:
    require("levelBrackets" not in text, "runtime config must not expose maintenance-only level brackets")
    require("minimumSessionSeconds" in text, "runtime config must retain the normal minimum session duration")
    require("combatTimeoutSeconds" in text, "runtime config must retain the inactivity timeout")


def validate_rune(text: str, name: str) -> None:
    guard = "configManager.getBoolean(configKeys.REMOVE_RUNE_CHARGES)"
    require(guard in text, f"{name} supply tracking must respect rune charge removal")
    require("recordSupply" in text, f"{name} must retain Analytics supply tracking")
    require(text.index(guard) < text.index("recordSupply"), f"{name} charge guard must wrap recordSupply")


def validate_docs(text: str) -> None:
    normalized = text.lower()
    for phrase in (
        "utc day rollover",
        "non-combat sessions",
        "short death sessions",
        "remove_rune_charges",
    ):
        require(phrase in normalized, f"runtime documentation lacks: {phrase}")


def main() -> int:
    try:
        validate_correctness(read(CORRECTNESS))
        validate_runtime(read(RUNTIME))
        validate_config(read(CONFIG))
        validate_rune(read(FIREBALL), "fireball rune")
        validate_rune(read(INTENSE_HEALING), "intense healing rune")
        validate_docs(read(DOCS))
    except AssertionError as error:
        print(f"gameplay analytics correctness validation failed: {error}", file=sys.stderr)
        return 1

    print("gameplay analytics correctness validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
