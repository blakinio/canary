from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CyclopediaRuntimeFixContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_charm_category_guard_uses_category(self) -> None:
        text = self.read("data/scripts/lib/register_bestiary_charm.lua")
        self.assertIn("if mask.category then\n\t\tcharm:category(mask.category)", text)
        self.assertNotIn("if mask.type then\n\t\tcharm:category(mask.category)", text)

    def test_bestiary_arithmetic_and_null_guard(self) -> None:
        text = self.read("src/io/iobestiary.cpp")
        self.assertIn("100000 + (playerLevel > 100 ? (playerLevel - 100) * 11000 : 0)", text)
        self.assertIn("const double chanceInPercent = static_cast<double>(chance) / 1000.0;", text)
        function = re.search(r"void IOBestiary::addBestiaryKill.*?\n}", text, re.S)
        self.assertIsNotNone(function)
        body = function.group(0)
        self.assertLess(body.find("!player || !mtype"), body.find("mtype->info.raceid"))

    def test_recent_pvp_count_uses_same_window(self) -> None:
        text = self.read("src/creatures/players/components/player_cyclopedia.cpp")
        function = re.search(r"void PlayerCyclopedia::loadRecentKills.*?\n}", text, re.S)
        self.assertIsNotNone(function)
        self.assertGreaterEqual(function.group(0).count("INTERVAL 70 DAY"), 2)

    def test_boosted_boss_has_single_recoverable_empty_result_branch(self) -> None:
        text = self.read("src/io/io_bosstiary.cpp")
        function = re.search(r"void IOBosstiary::loadBoostedBoss.*?\n}", text, re.S)
        self.assertIsNotNone(function)
        body = function.group(0)
        self.assertEqual(body.count("if (!result)"), 1)
        self.assertIn("INSERT INTO `boosted_boss`", body)


if __name__ == "__main__":
    unittest.main()
