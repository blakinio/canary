#!/usr/bin/env python3
from __future__ import annotations

import unittest

import validate_gameplay_analytics_correctness as validator


class GameplayAnalyticsCorrectnessValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.correctness = validator.CORRECTNESS.read_text(encoding="utf-8")
        self.runtime = validator.RUNTIME.read_text(encoding="utf-8")
        self.config = validator.CONFIG.read_text(encoding="utf-8")
        self.fireball = validator.FIREBALL.read_text(encoding="utf-8")
        self.intense_healing = validator.INTENSE_HEALING.read_text(encoding="utf-8")
        self.docs = validator.DOCS.read_text(encoding="utf-8")

    def test_repository_correctness_contract(self) -> None:
        validator.validate_correctness(self.correctness)
        validator.validate_runtime(self.runtime)
        validator.validate_config(self.config)
        validator.validate_rune(self.fireball, "fireball rune")
        validator.validate_rune(self.intense_healing, "intense healing rune")
        validator.validate_docs(self.docs)

    def test_rejects_persisted_non_combat_sessions(self) -> None:
        broken = self.correctness.replace("if not hasCombatOrDeath(session) then", "if false then", 1)
        self.assertNotEqual(broken, self.correctness)
        with self.assertRaisesRegex(AssertionError, "non-combat"):
            validator.validate_correctness(broken)

    def test_rejects_wrong_wrapper_order(self) -> None:
        reliability = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")'
        correctness = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")'
        broken = self.runtime.replace(f"{reliability}\n{correctness}", f"{correctness}\n{reliability}", 1)
        self.assertNotEqual(broken, self.runtime)
        with self.assertRaisesRegex(AssertionError, "after reliability"):
            validator.validate_runtime(broken)

    def test_rejects_runtime_level_brackets(self) -> None:
        broken = self.config.replace("detailLevel = 1,", "detailLevel = 1,\n\tlevelBrackets = { 100, 200 },", 1)
        with self.assertRaisesRegex(AssertionError, "maintenance-only"):
            validator.validate_config(broken)

    def test_rejects_unconditional_rune_supply(self) -> None:
        broken = self.fireball.replace(" and configManager.getBoolean(configKeys.REMOVE_RUNE_CHARGES)", "", 1)
        self.assertNotEqual(broken, self.fireball)
        with self.assertRaisesRegex(AssertionError, "charge removal"):
            validator.validate_rune(broken, "fireball rune")


if __name__ == "__main__":
    unittest.main()
