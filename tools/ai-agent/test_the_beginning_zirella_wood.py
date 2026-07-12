from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua"
EXPECTED_TREE_POSITIONS = {
    "32073:32276:7",
    "32067:32281:7",
    "32079:32285:7",
    "32081:32276:7",
    "32066:32288:7",
}


class TheBeginningZirellaWoodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SCRIPT.read_text(encoding="utf-8")

    def test_uses_current_item_and_storage_contract(self) -> None:
        self.assertIn("Storage.Quest.U8_2.TheBeginningQuest", self.source)
        self.assertRegex(self.source, r"DEAD_TREE_ITEM_ID\s*=\s*7753\b")
        self.assertRegex(self.source, r"BRANCH_ITEM_ID\s*=\s*7772\b")
        self.assertRegex(self.source, r"ZIRELLA_CART_ITEM_ID\s*=\s*7751\b")
        self.assertRegex(self.source, r"ZIRELLA_ACTIVE_STAGE\s*=\s*6\b")
        self.assertRegex(self.source, r"ZIRELLA_DELIVERED_STAGE\s*=\s*7\b")
        self.assertIn("ZirellaNpcGreetStorage", self.source)
        self.assertIn("ZirellaQuestLog", self.source)

    def test_bounds_tree_use_to_verified_tutorial_positions(self) -> None:
        positions = set(re.findall(r'\["(\d+:\d+:\d+)"\]\s*=\s*true', self.source))
        self.assertEqual(positions, EXPECTED_TREE_POSITIONS)
        self.assertIn("tutorialDeadTreePositions[positionKey(fromPosition)]", self.source)

    def test_creates_a_movable_ground_branch_not_inventory_reward(self) -> None:
        self.assertIn("Game.createItem(BRANCH_ITEM_ID, 1, player:getPosition())", self.source)
        self.assertIn("branch:decay()", self.source)
        self.assertNotIn("player:addItem(BRANCH_ITEM_ID", self.source)
        self.assertNotIn("player:addItem(7772", self.source)

    def test_requires_the_exact_accepted_quest_stage(self) -> None:
        self.assertRegex(
            self.source,
            re.compile(
                r"ZirellaNpcGreetStorage\)\s*==\s*ZIRELLA_ACTIVE_STAGE.*?"
                r"ZirellaQuestLog\)\s*==\s*ZIRELLA_ACTIVE_STAGE",
                re.DOTALL,
            ),
        )
        self.assertGreaterEqual(self.source.count("if not isCollectingWoodActive(player) then"), 2)

    def test_preserves_five_second_cooldown_and_hint_progression(self) -> None:
        self.assertRegex(self.source, r"TREE_EXHAUST_SECONDS\s*=\s*5\b")
        self.assertIn("local treeExhaustUntil = {}", self.source)
        self.assertIn("local playerGuid = player:getGuid()", self.source)
        self.assertIn("local now = os.time()", self.source)
        self.assertIn("(treeExhaustUntil[playerGuid] or 0) > now", self.source)
        self.assertIn(
            "treeExhaustUntil[playerGuid] = now + TREE_EXHAUST_SECONDS",
            self.source,
        )
        self.assertNotIn("CONDITION_EXHAUST_WEAPON", self.source)
        self.assertNotIn("Condition(", self.source)
        self.assertIn("player:sendTutorial(24)", self.source)
        self.assertRegex(self.source, r"BRANCH_HINT_STAGE\s*=\s*15\b")
        self.assertIn(
            "player:setStorageValue(tutorialStorage.TutorialHintsStorage, BRANCH_HINT_STAGE)",
            self.source,
        )

    def test_accepts_only_the_verified_zirella_cart(self) -> None:
        self.assertIn("Position(32062, 32271, 7)", self.source)
        self.assertIn("target.itemid ~= ZIRELLA_CART_ITEM_ID", self.source)
        self.assertIn("not isSamePosition(toPosition, zirellaCartPosition)", self.source)

    def test_consumes_one_branch_and_advances_both_storages_once(self) -> None:
        self.assertEqual(self.source.count("item:remove(1)"), 1)
        self.assertIn("toPosition:sendMagicEffect(CONST_ME_MAGIC_GREEN)", self.source)
        self.assertIn(
            "player:setStorageValue(tutorialStorage.ZirellaNpcGreetStorage, ZIRELLA_DELIVERED_STAGE)",
            self.source,
        )
        self.assertIn(
            "player:setStorageValue(tutorialStorage.ZirellaQuestLog, ZIRELLA_DELIVERED_STAGE)",
            self.source,
        )
        self.assertIn("Well done! You successfully used a branch on Zirella's cart.", self.source)

    def test_registers_exactly_the_two_expected_actions(self) -> None:
        self.assertEqual(self.source.count("Action()"), 2)
        self.assertEqual(self.source.count(":register()"), 2)
        self.assertIn("tutorialDeadTree:id(DEAD_TREE_ITEM_ID)", self.source)
        self.assertIn("tutorialBranch:id(BRANCH_ITEM_ID)", self.source)
        self.assertNotIn(":aid(", self.source)
        self.assertNotIn(":uid(", self.source)

    def test_does_not_modify_map_or_unrelated_runtime(self) -> None:
        forbidden = (
            "setActionId",
            "setUniqueId",
            "teleportTo",
            "Game.createMonster",
            "Game.setStorageValue",
        )
        for token in forbidden:
            self.assertNotIn(token, self.source)


if __name__ == "__main__":
    unittest.main()
