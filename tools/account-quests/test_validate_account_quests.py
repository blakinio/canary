#!/usr/bin/env python3
from __future__ import annotations

import unittest

import validate_account_quests as validator


class AccountQuestValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = validator.RUNTIME.read_text(encoding="utf-8")
        self.config = validator.CONFIG.read_text(encoding="utf-8")
        self.doors = validator.QUEST_DOORS.read_text(encoding="utf-8")

    def test_repository_contract(self) -> None:
        configured = validator.configured_quest_ids(self.config)
        integrated = validator.integrated_quest_ids()
        self.assertEqual(
            {
                "the-ape-city",
                "secret-service",
                "in-service-of-yalahar",
                "the-new-frontier",
                "wrath-of-the-emperor",
            },
            integrated,
        )
        self.assertFalse(integrated - configured)
        validator.validate_runtime(self.runtime)
        validator.validate_door_integration(self.doors)

    def test_rejects_length_operator_for_string_keyed_quests(self) -> None:
        broken = self.runtime.replace(
            'logger.info("[AccountQuest] Account-wide quest system enabled with {} registered quests.", countRegisteredQuests())',
            'logger.info("[AccountQuest] Account-wide quest system enabled with {} registered quests.", #AccountQuest.config.quests)',
            1,
        )
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

    def test_rejects_early_ape_city_unlock(self) -> None:
        broken = self.doors.replace(
            'addAccountQuestDoor(theApeCity.DworcDoor, "the-ape-city")',
            'addAccountQuestDoor(theApeCity.DworcDoor, "the-ape-city", true)',
            1,
        )
        with self.assertRaisesRegex(AssertionError, "early doors"):
            validator.validate_door_integration(broken)

    def test_rejects_generic_unlock_for_any_quest_door(self) -> None:
        broken = self.doors.replace(
            "if hasCharacterAccess and completionQuestId then",
            "if hasCharacterAccess and accountQuestId then",
            1,
        )
        with self.assertRaisesRegex(AssertionError, "ordinary quest doors"):
            validator.validate_door_integration(broken)

    def test_rejects_shared_yalahar_final_fight(self) -> None:
        marker = 'addAccountQuestDoor(yalahar.DoorToMatrix, "in-service-of-yalahar")'
        broken = self.doors.replace(
            marker,
            marker + '\naddAccountQuestDoor(yalahar.DoorToLastFight, "in-service-of-yalahar")',
            1,
        )
        with self.assertRaisesRegex(AssertionError, "final fight"):
            validator.validate_door_integration(broken)

    def test_rejects_shared_new_frontier_reward_door(self) -> None:
        marker = 'addAccountQuestDoor(newFrontier.Mission09 and newFrontier.Mission09.ArenaDoor, "the-new-frontier")'
        broken = self.doors.replace(
            marker,
            marker
            + '\naddAccountQuestDoor(newFrontier.Mission09 and newFrontier.Mission09.RewardDoor, "the-new-frontier")',
            1,
        )
        with self.assertRaisesRegex(AssertionError, "reward door"):
            validator.validate_door_integration(broken)

    def test_rejects_sharing_wrath_reward_stage(self) -> None:
        broken = self.doors.replace(
            'addAccountQuestDoor(wrath.Mission12, "wrath-of-the-emperor", true, false)',
            'addAccountQuestDoor(wrath.Mission12, "wrath-of-the-emperor", true)',
            1,
        )
        with self.assertRaisesRegex(AssertionError, "Mission 12"):
            validator.validate_door_integration(broken)

    def test_atomic_claim_contract(self) -> None:
        self.assertIn("db.queryAffectedRows", self.runtime)
        claim = validator.function_body(self.runtime, "claimReward", "resetCharacterProgress")
        self.assertNotIn("AccountQuest.canClaimReward", claim)

    def test_main_config_switch_contract(self) -> None:
        self.assertIn("accountWideQuestSystemEnabled = true", validator.CONFIG_DIST.read_text(encoding="utf-8"))
        self.assertIn("ACCOUNT_WIDE_QUESTS_ENABLED", validator.CONFIG_ENUMS.read_text(encoding="utf-8"))

    def test_admin_access_command_contract(self) -> None:
        self.assertIn('TalkAction("/questaccess")', self.runtime)
        self.assertIn('questAccess:groupType("god")', self.runtime)


if __name__ == "__main__":
    unittest.main()
