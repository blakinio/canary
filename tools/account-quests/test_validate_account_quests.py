#!/usr/bin/env python3
from __future__ import annotations

import unittest

import validate_account_quests as validator


class AccountQuestValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = validator.RUNTIME.read_text(encoding="utf-8")
        self.config = validator.CONFIG.read_text(encoding="utf-8")

    def test_repository_contract(self) -> None:
        configured = validator.configured_quest_ids(self.config)
        self.assertFalse(validator.integrated_quest_ids() - configured)
        validator.validate_runtime(self.runtime)

    def test_rejects_length_operator_for_string_keyed_quests(self) -> None:
        broken = self.runtime.replace("countRegisteredQuests()", "#AccountQuest.config.quests", 1)
        with self.assertRaisesRegex(AssertionError, "length operator"):
            validator.validate_runtime(broken)

    def test_rejects_missing_registration_guard(self) -> None:
        broken = self.runtime.replace(
            "if not definition or not normalizedId or not accountId then",
            "if not normalizedId or not accountId then",
            1,
        )
        with self.assertRaisesRegex(AssertionError, "reject unregistered"):
            validator.validate_runtime(broken)

    def test_rejects_invalid_configured_id(self) -> None:
        broken = self.config.replace('["the-ape-city"]', '["../the-ape-city"]', 1)
        with self.assertRaisesRegex(AssertionError, "invalid configured quest ids"):
            validator.configured_quest_ids(broken)


if __name__ == "__main__":
    unittest.main()
