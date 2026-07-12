from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = Path(__file__).with_name("cyclopedia_validation.py")
SPEC = importlib.util.spec_from_file_location("cyclopedia_validation_data_contracts", MODULE_PATH)
assert SPEC and SPEC.loader
cv = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cv)


class CyclopediaBestiaryDataContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_corrected_ids_and_metadata(self) -> None:
        expected = {
            "data-otservbr-global/monster/quests/soul_war/normal_monsters/monk's_apparition.lua": ("monster.raceId = 2636", "race = BESTY_RACE_UNDEAD"),
            "data-otservbr-global/monster/undeads/crypt_warrior.lua": ("monster.raceId = 1995", "race = BESTY_RACE_UNDEAD"),
            "data-otservbr-global/monster/birds/agrestic_chicken.lua": ("monster.raceId = 1979", "race = BESTY_RACE_BIRD"),
            "data-otservbr-global/monster/mammals/terrified_elephant.lua": ("monster.raceId = 771", "race = BESTY_RACE_MAMMAL"),
            "data-otservbr-global/monster/quests/the_first_dragon/haunted_dragon.lua": ("monster.raceId = 1376", "race = BESTY_RACE_DRAGON"),
            "data-otservbr-global/monster/quests/heart_of_destruction/eradicator2.lua": ("bossRaceId = 1226", "bossRace = RARITY_ARCHFOE"),
        }
        for path, needles in expected.items():
            text = self.read(path)
            for needle in needles:
                self.assertIn(needle, text, f"{path}: missing {needle}")

    def test_full_active_monster_inventory_has_no_findings(self) -> None:
        findings = cv.validate_monsters(cv.collect_monsters(ROOT))
        self.assertEqual(findings, [])

    def test_shared_id_allowlists_are_exact(self) -> None:
        inventory = cv.collect_monsters(ROOT)
        bestiary = {}
        bosstiary = {}
        for item in inventory["bestiaryEntries"]:
            bestiary.setdefault(item.get("raceId"), set()).add(item["path"])
        for item in inventory["bosstiaryEntries"]:
            bosstiary.setdefault(item["bosstiary"].get("bossRaceId"), set()).add(item["path"])
        for race_id, paths in cv.KNOWN_SHARED_BESTIARY_IDS.items():
            self.assertEqual(bestiary.get(race_id), set(paths))
        for boss_id, paths in cv.KNOWN_SHARED_BOSSTIARY_IDS.items():
            self.assertEqual(bosstiary.get(boss_id), set(paths))


if __name__ == "__main__":
    unittest.main()
