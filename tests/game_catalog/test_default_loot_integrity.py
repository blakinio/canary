#!/usr/bin/env python3

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MONSTERS = ROOT / "data-otservbr-global" / "monster"


class DefaultLootIntegrityTests(unittest.TestCase):
    def test_runtime_roll_formula_keeps_configured_threshold_and_dynamic_factor(self) -> None:
        constants = (ROOT / "src" / "utils" / "const.hpp").read_text(encoding="utf-8")
        functions = (ROOT / "data" / "libs" / "functions" / "functions.lua").read_text(encoding="utf-8")
        monster_type = (ROOT / "data" / "libs" / "functions" / "monstertype.lua").read_text(encoding="utf-8")
        global_lua = (ROOT / "data" / "global.lua").read_text(encoding="utf-8")

        self.assertRegex(constants, r"MAX_LOOTCHANCE\s*=\s*100000")
        self.assertRegex(global_lua, r"SCHEDULE_LOOT_RATE\s*=\s*100")
        self.assertIn("math.random(0, MAX_LOOTCHANCE)", functions)
        self.assertIn("return randomValue * 100 / multi", functions)
        self.assertIn("math.random(95, 105) / 100", monster_type)
        self.assertIn("local adjustedChance = chance * dynamicFactor", monster_type)
        self.assertIn("if randValue >= adjustedChance then", monster_type)

    def test_default_datapack_contains_review_required_thresholds(self) -> None:
        chance_pattern = re.compile(r"\bchance\s*=\s*(\d+)")
        findings: list[tuple[Path, int]] = []
        for path in sorted(MONSTERS.rglob("*.lua")):
            for match in chance_pattern.finditer(path.read_text(encoding="utf-8")):
                chance = int(match.group(1))
                if chance > 100000:
                    findings.append((path.relative_to(ROOT), chance))

        self.assertEqual(len(findings), 92)
        self.assertIn(
            (
                Path("data-otservbr-global/monster/humanoids/broken_shaper.lua"),
                100320,
            ),
            findings,
        )
        self.assertIn(
            (
                Path("data-otservbr-global/monster/quests/the_curse_spreads/darkfang.lua"),
                13600000,
            ),
            findings,
        )


if __name__ == "__main__":
    unittest.main()
