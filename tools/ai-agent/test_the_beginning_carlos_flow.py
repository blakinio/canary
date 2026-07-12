from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CARLOS_SCRIPT = ROOT / "data-otservbr-global/npc/carlos.lua"


def function_body(source: str, name: str, next_name: str) -> str:
    match = re.search(
        rf"local function {re.escape(name)}\b(.*?)\nend\n\nlocal function {re.escape(next_name)}\b",
        source,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"function {name} not found")
    return match.group(1)


class TheBeginningCarlosFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARLOS_SCRIPT.read_text(encoding="utf-8")

    def test_preserves_current_food_items_and_prices(self) -> None:
        self.assertRegex(self.source, r"MEAT_ITEM_ID\s*=\s*3577\b")
        self.assertRegex(self.source, r"HAM_ITEM_ID\s*=\s*3582\b")
        self.assertIn('{ itemName = "ham", clientId = HAM_ITEM_ID, sell = 2, count = 1 }', self.source)
        self.assertIn('{ itemName = "meat", clientId = MEAT_ITEM_ID, sell = 2, count = 1 }', self.source)

    def test_outfit_keyword_uses_the_stage_two_instruction(self) -> None:
        outfit = re.search(
            r'elseif MsgContains\(message, "outfit"\) then(.*?)elseif MsgContains\(message, "ready"\) then',
            self.source,
            re.DOTALL,
        )
        self.assertIsNotNone(outfit)
        outfit_body = outfit.group(1)
        self.assertIn("storeTalkCid[playerId] == 1", outfit_body)
        self.assertIn("teachOutfit(npc, creature, player)", outfit_body)
        self.assertNotIn("CarlosQuestLog, 7", outfit_body)
        self.assertNotIn("CarlosNpcGreetStorage, 8", outfit_body)

        teach_outfit = function_body(self.source, "teachOutfit", "creatureSayCallback")
        self.assertIn("CarlosNpcGreetStorage, 2", teach_outfit)
        self.assertIn("CarlosQuestLog, 2", teach_outfit)
        self.assertIn("player:sendTutorial(12)", teach_outfit)
        self.assertNotIn("CARLOS_READY_STAGE", teach_outfit)

    def test_registers_and_bounds_the_trade_request(self) -> None:
        trade_request = function_body(self.source, "onTradeRequest", "onReleaseFocus")
        self.assertIn("CarlosNpcGreetStorage) ~= CARLOS_TRADE_STAGE", trade_request)
        self.assertIn("CarlosQuestLog) ~= CARLOS_TRADE_STAGE", trade_request)
        self.assertIn("tradeState ~= TRADE_AVAILABLE", trade_request)
        self.assertIn("tradeState ~= TRADE_OPENED", trade_request)
        self.assertIn("player:sendTutorial(13)", trade_request)
        self.assertIn("CarlosNpcTradeStorage, TRADE_OPENED", trade_request)
        self.assertNotIn("CarlosQuestLog, CARLOS_READY_STAGE", trade_request)
        self.assertNotIn("CarlosNpcGreetStorage, CARLOS_READY_STAGE", trade_request)
        self.assertIn(
            "npcHandler:setCallback(CALLBACK_ON_TRADE_REQUEST, onTradeRequest)",
            self.source,
        )

    def test_advances_only_after_a_successful_food_sale(self) -> None:
        sell = re.search(
            r"npcType\.onSellItem\s*=\s*function\(.*?\)(.*?)\nend\n-- On check npc shop message",
            self.source,
            re.DOTALL,
        )
        self.assertIsNotNone(sell)
        sell_body = sell.group(1)
        self.assertIn("amount < 1", sell_body)
        self.assertIn("itemId ~= MEAT_ITEM_ID and itemId ~= HAM_ITEM_ID", sell_body)
        self.assertIn("CarlosNpcGreetStorage) ~= CARLOS_TRADE_STAGE", sell_body)
        self.assertIn("CarlosQuestLog) ~= CARLOS_TRADE_STAGE", sell_body)
        self.assertIn("CarlosNpcTradeStorage) ~= TRADE_OPENED", sell_body)
        self.assertIn("CarlosQuestLog, CARLOS_READY_STAGE", sell_body)
        self.assertIn("CarlosNpcGreetStorage, CARLOS_READY_STAGE", sell_body)
        self.assertIn("CarlosNpcTradeStorage, TRADE_COMPLETED", sell_body)
        self.assertIn("storeTalkCid[player:getId()] = CARLOS_READY_STAGE", sell_body)

    def test_keeps_shop_transaction_authoritative(self) -> None:
        forbidden = (
            "player:removeItem(",
            "player:addMoney(",
            "player:removeMoney(",
            "Game.createItem(",
        )
        for token in forbidden:
            self.assertNotIn(token, self.source)

    def test_ready_completion_remains_stage_seven_only(self) -> None:
        ready = re.search(
            r'elseif MsgContains\(message, "ready"\) then(.*?)\n\tend\n\treturn true',
            self.source,
            re.DOTALL,
        )
        self.assertIsNotNone(ready)
        ready_body = ready.group(1)
        self.assertIn("storeTalkCid[playerId] == CARLOS_READY_STAGE", ready_body)
        self.assertIn("CarlosQuestLog, CARLOS_READY_STAGE", ready_body)
        self.assertIn("CarlosNpcGreetStorage, 8", ready_body)

    def test_does_not_touch_map_or_unrelated_runtime(self) -> None:
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
