#!/usr/bin/env python3
"""Contract tests for GameStore coin-balance packet sequencing."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SENDERS = (ROOT / "data/libs/gamestore/senders.lua").read_text(encoding="utf-8")
PLAYER = (ROOT / "data/libs/gamestore/player.lua").read_text(encoding="utf-8")
PARSERS = (ROOT / "data/libs/gamestore/parsers.lua").read_text(encoding="utf-8")


def lua_function(source: str, name: str) -> str:
    start = source.index(f"local function {name}(")
    next_function = source.find("\nlocal function ", start + 1)
    return source[start:] if next_function == -1 else source[start:next_function]


class GameStoreBalancePacketsTest(unittest.TestCase):
    def test_balance_updating_sender_emits_only_requested_state(self):
        body = lua_function(SENDERS, "sendStoreBalanceUpdating")
        self.assertIn("msg:addByte(updating and 0x00 or 0x01)", body)
        self.assertNotIn("sendUpdatedStoreBalances(", body)

    def test_open_store_finishes_initial_balance_update(self):
        body = lua_function(SENDERS, "openStore")
        self.assertRegex(
            body,
            re.compile(
                r"sendStoreBalanceUpdating\(playerId, true\).*"
                r"sendUpdatedStoreBalances\(playerId\)",
                re.S,
            ),
        )

    def test_mutations_bracket_balance_packets(self):
        expected_mutations = {
            "removeCoinsBalance": "self:removeTibiaCoins(coins)",
            "addCoinsBalance": "self:addTibiaCoins(coins)",
            "removeTransferableCoinsBalance": "self:removeTransferableCoins(coins)",
            "addTransferableCoinsBalance": "self:addTransferableCoins(coins)",
            "removeCombinedCoinsBalance": "self:removeTransferableAndTibiaCoins(coins)",
        }
        for function_name, mutation in expected_mutations.items():
            with self.subTest(function=function_name):
                body = lua_function(PLAYER, function_name)
                begin = body.index("sendStoreBalanceUpdating(self:getId(), true)")
                mutate = body.index(mutation)
                finish = body.index("sendUpdatedStoreBalances(self:getId())")
                self.assertLess(begin, mutate)
                self.assertLess(mutate, finish)

    def test_purchase_parser_does_not_repeat_transaction_balance(self):
        body = lua_function(PARSERS, "parseBuyStoreOffer")
        transaction = body.index("player:makeCoinTransaction(offer)")
        success = body.index("sendStorePurchaseSuccessful", transaction)
        self.assertNotIn("sendUpdatedStoreBalances(", body[transaction:success])


if __name__ == "__main__":
    unittest.main()
