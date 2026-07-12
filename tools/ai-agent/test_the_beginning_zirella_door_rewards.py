from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOOR_SCRIPT = ROOT / "data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua"
QUEST_SYSTEM = ROOT / "data-otservbr-global/scripts/actions/other/others/quest_system1.lua"
EXPECTED_TUTORIAL_IDS = {
    50080: 5,
    50082: 6,
    50093: 10,
    50094: 11,
}


def parse_tutorial_ids(source: str) -> dict[int, int]:
    match = re.search(r"local tutorialIds\s*=\s*\{(.*?)\n\}", source, re.DOTALL)
    if not match:
        raise AssertionError("tutorialIds table not found")
    return {
        int(uid): int(tutorial_id)
        for uid, tutorial_id in re.findall(r"\[(\d+)\]\s*=\s*(\d+)", match.group(1))
    }


class TheBeginningZirellaDoorRewardsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.door_source = DOOR_SCRIPT.read_text(encoding="utf-8")
        cls.quest_source = QUEST_SYSTEM.read_text(encoding="utf-8")

    def test_uses_exact_verified_door_contract(self) -> None:
        self.assertIn("Storage.Quest.U8_2.TheBeginningQuest", self.door_source)
        self.assertRegex(self.door_source, r"ZIRELLA_DOOR_UID\s*=\s*50085\b")
        self.assertRegex(self.door_source, r"ZIRELLA_REWARD_STAGE\s*=\s*8\b")
        self.assertRegex(self.door_source, r"CLOSED_DOOR_ITEM_ID\s*=\s*6898\b")
        self.assertRegex(self.door_source, r"OPEN_DOOR_ITEM_ID\s*=\s*6899\b")
        self.assertIn("Position(32058, 32266, 7)", self.door_source)
        self.assertIn("zirellaDoor:uid(ZIRELLA_DOOR_UID)", self.door_source)
        self.assertEqual(self.door_source.count("Action()"), 1)
        self.assertEqual(self.door_source.count(":register()"), 1)

    def test_denies_closed_door_before_zirella_reward(self) -> None:
        self.assertRegex(
            self.door_source,
            re.compile(
                r"item\.itemid\s*==\s*CLOSED_DOOR_ITEM_ID.*?"
                r"ZirellaNpcGreetStorage\)\s*<\s*ZIRELLA_REWARD_STAGE",
                re.DOTALL,
            ),
        )
        self.assertIn(
            'player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The door seems to be sealed against unwanted intruders.")',
            self.door_source,
        )

    def test_opens_with_current_door_semantics(self) -> None:
        self.assertIn("item:transform(OPEN_DOOR_ITEM_ID)", self.door_source)
        self.assertIn(
            "item:getPosition():sendSingleSoundEffect(SOUND_EFFECT_TYPE_ACTION_OPEN_DOOR)",
            self.door_source,
        )
        self.assertIn("player:teleportTo(toPosition, true)", self.door_source)

    def test_closes_only_when_doorway_is_clear(self) -> None:
        self.assertRegex(
            self.door_source,
            re.compile(
                r"item\.itemid\s*==\s*OPEN_DOOR_ITEM_ID.*?"
                r"Creature\.checkCreatureInsideDoor\(player, toPosition\).*?"
                r"item:transform\(CLOSED_DOOR_ITEM_ID\)",
                re.DOTALL,
            ),
        )
        self.assertIn(
            "item:getPosition():sendSingleSoundEffect(SOUND_EFFECT_TYPE_ACTION_CLOSE_DOOR)",
            self.door_source,
        )

    def test_maps_tutorials_to_current_reward_chests(self) -> None:
        self.assertEqual(parse_tutorial_ids(self.quest_source), EXPECTED_TUTORIAL_IDS)
        self.assertNotIn("[50084]", self.quest_source)
        self.assertNotIn("[50086]", self.quest_source)
        self.assertIn("[50093] = 10", self.quest_source)
        self.assertIn("[50094] = 11", self.quest_source)

    def test_preserves_generic_one_shot_reward_flow(self) -> None:
        required = (
            "storage = item.uid",
            "player:getStorageValue(storage) > 0",
            "player:addItemEx(reward)",
            "player:setStorageValue(storage, 1)",
            "questSystem1:aid(2000)",
            "if item.uid == 50080 then",
            "SantiagoNpcGreetStorage, 3",
        )
        for token in required:
            self.assertIn(token, self.quest_source)

    def test_does_not_modify_map_or_reward_contents(self) -> None:
        forbidden_door_tokens = (
            "setActionId",
            "setUniqueId",
            "Game.createItem",
            "Game.createMonster",
            "addExperience",
            "addItem",
        )
        for token in forbidden_door_tokens:
            self.assertNotIn(token, self.door_source)

        self.assertNotIn("3457", self.door_source)
        self.assertNotIn("3003", self.door_source)


if __name__ == "__main__":
    unittest.main()
