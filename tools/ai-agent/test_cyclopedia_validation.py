from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("cyclopedia_validation.py")
SPEC = importlib.util.spec_from_file_location("cyclopedia_validation", MODULE_PATH)
assert SPEC and SPEC.loader
cv = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cv)

CHARMS = '''
local charms = {
 [1] = { name = "Wound", category = CHARM_MAJOR, type = CHARM_OFFENSIVE,
         chance = {5, 10, 11}, points = {240, 360, 1200} },
 [2] = { name = "Cripple", category = CHARM_MINOR, type = CHARM_OFFENSIVE,
         chance = {6, 9, 12}, points = {100, 150, 225} },
}
'''

BESTIARY = '''
local mType = Game.createMonsterType("Giant Spider")
local monster = {}
monster.raceId = 38
monster.Bestiary = {
 class = "Vermin", race = BESTY_RACE_VERMIN, toKill = 1000,
 FirstUnlock = 50, SecondUnlock = 500, CharmsPoints = 25,
 Stars = 3, Occurrence = 0,
}
'''

BOSSTIARY = '''
local mType = Game.createMonsterType("Brain Head")
local monster = {}
monster.bosstiary = { bossRaceId = 1862, bossRace = RARITY_ARCHFOE }
'''


class CyclopediaValidationTests(unittest.TestCase):
    def test_parse_charm_registry(self) -> None:
        entries = cv.parse_charm_registry(CHARMS)
        self.assertEqual([entry["luaId"] for entry in entries], [1, 2])
        self.assertEqual(entries[0]["chance"], [5, 10, 11])
        self.assertEqual(entries[1]["category"], "CHARM_MINOR")

    def test_sparse_ids_and_tiers(self) -> None:
        entries = cv.parse_charm_registry(
            CHARMS.replace("[2]", "[3]").replace("{6, 9, 12}", "{6, 9}")
        )
        ids = {finding["id"] for finding in cv.validate_charms(entries)}
        self.assertIn("CHARM-SPARSE-LUA-IDS", ids)
        self.assertIn("CHARM-3-CHANCE-TIERS", ids)

    def test_parse_active_monsters(self) -> None:
        bestiary = cv.parse_monster_definition(BESTIARY, "bestiary.lua")
        bosstiary = cv.parse_monster_definition(BOSSTIARY, "bosstiary.lua")
        self.assertEqual(bestiary["raceId"], 38)
        self.assertEqual(bestiary["bestiary"]["SecondUnlock"], 500)
        self.assertEqual(bosstiary["bosstiary"]["bossRaceId"], 1862)
        self.assertEqual(
            cv.validate_monsters(self.inventory([bestiary], [bosstiary])), []
        )

    def test_missing_bestiary_race_is_metadata_warning(self) -> None:
        entry = cv.parse_monster_definition(
            BESTIARY.replace("race = BESTY_RACE_VERMIN, ", ""),
            "missing_race.lua",
        )
        findings = cv.validate_monsters(self.inventory([entry], []))
        by_id = {finding["id"]: finding for finding in findings}
        self.assertEqual(
            by_id["BESTIARY-MISSING-RACE-METADATA"]["disposition"],
            "display-metadata-defect",
        )
        self.assertNotIn("BESTIARY-MISSING-FIELDS", by_id)

    def test_invalid_monster_data(self) -> None:
        first = cv.parse_monster_definition(
            BESTIARY.replace("38", "7").replace("FirstUnlock = 50", "FirstUnlock = 1200")
            + '\nmonster.bosstiary = { bossRaceId = 9, bossRace = RARITY_UNKNOWN }',
            "one.lua",
        )
        second = cv.parse_monster_definition(
            BESTIARY.replace("38", "7")
            + '\nmonster.bosstiary = { bossRaceId = 9, bossRace = RARITY_BANE }',
            "two.lua",
        )
        ids = {
            finding["id"]
            for finding in cv.validate_monsters(self.inventory([first, second], [first, second]))
        }
        self.assertIn("BESTIARY-INVALID-THRESHOLDS", ids)
        self.assertIn("BESTIARY-DUPLICATE-RACE-ID-7", ids)
        self.assertIn("BOSSTIARY-INVALID-RARITY", ids)
        self.assertIn("BOSSTIARY-DUPLICATE-BOSS-RACE-ID-9", ids)

    def test_protocol_inventory(self) -> None:
        inventory = cv.collect_protocol_methods(
            "void parseCyclopediaCharacterInfo(); void sendBestiaryCharms(); void sendHousesInfo();",
            "void ProtocolGame::parseCyclopediaCharacterInfo() {} void ProtocolGame::sendBestiaryCharms() {}",
        )
        self.assertEqual(inventory["missingDefinitions"], ["sendHousesInfo"])
        self.assertIn(
            "parseCyclopediaCharacterInfo",
            inventory["byDomain"]["character"]["definitions"],
        )

    def test_known_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.write_fixture(root)
            by_id = {finding["id"]: finding for finding in cv.known_patterns(root)}
            self.assertEqual(
                by_id["BESTIARY-DIFFICULTY-INTEGER-DIVISION"]["disposition"],
                "confirmed-runtime-defect",
            )
            self.assertIn("CHARM-CATEGORY-GUARD-USES-TYPE", by_id)
            self.assertIn("BESTIARY-MTYPE-DEREFERENCE-BEFORE-GUARD", by_id)
            self.assertIn("CHARACTER-RECENT-PVP-COUNT-WINDOW-MISMATCH", by_id)
            self.assertTrue(
                by_id["BOSSTIARY-EMPTY-RESULT-FALLBACK-UNREACHABLE"]["evidence"][
                    "cleanSchemaSeedsDefaultRow"
                ]
            )

    def test_report_is_read_only_and_scans_client(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, client = Path(temp) / "canary", Path(temp) / "otclient"
            self.write_fixture(root)
            self.write_client(client)
            before = sorted(path.relative_to(root) for path in root.rglob("*"))
            report = cv.build_report(root, client)
            after = sorted(path.relative_to(root) for path in root.rglob("*"))
            self.assertEqual(before, after)
            self.assertEqual(report["summary"]["domains"], 7)
            self.assertEqual(report["summary"]["charmCount"], 2)
            self.assertEqual(report["otclient"]["status"], "scanned")
            json.dumps(report)

    def test_missing_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            report = cv.build_report(Path(temp))
            self.assertTrue(any(item["id"] == "SOURCE-MISSING" for item in report["findings"]))
            self.assertTrue(any(item["id"] == "ACTIVE-MONSTER-DATAPACK-MISSING" for item in report["findings"]))

    @staticmethod
    def inventory(bestiary: list[dict], bosstiary: list[dict]) -> dict:
        records = list(dict.fromkeys(id(item) for item in bestiary + bosstiary))
        return {
            "roots": [{"path": "data-otservbr-global/monster", "exists": True, "files": len(records)}],
            "records": bestiary + [item for item in bosstiary if item not in bestiary],
            "bestiaryEntries": bestiary,
            "bosstiaryEntries": bosstiary,
            "summary": {"scannedFiles": len(records), "records": len(records), "bestiaryEntries": len(bestiary), "bosstiaryEntries": len(bosstiary)},
        }

    @staticmethod
    def write_fixture(root: Path) -> None:
        files = {
            cv.CHARM_REGISTRY: CHARMS,
            cv.CHARM_HELPER: "registerCharm.category = function(charm, mask) if mask.type then charm:category(mask.category) end end",
            cv.BESTIARY_CPP: '''
void IOBestiary::sendBuyCharmRune() { auto resetAllCharmsCost = 100000 + (playerLevel > 100 ? playerLevel * 11000 : 0); }
void IOBestiary::addBestiaryKill(const MonsterTypePtr &mtype) const { auto id = mtype->info.raceid; if (!mtype) return; }
int IOBestiary::calculateDifficult(uint32_t chance) const { float chanceInPercent = chance / 1000; if (chanceInPercent < 1) return 3; return 0; }
''',
            cv.BOSSTIARY_CPP: "void IOBosstiary::loadBoostedBoss() { auto result = query(); if (!result) { return; } if (!result) selectNewBoss(); }",
            cv.PLAYER_CYCLOPEDIA_CPP: '''
void PlayerCyclopedia::loadRecentKills() { auto q = "SELECT * FROM (SELECT count(*) AS entries FROM player_deaths) AS t1, (SELECT * FROM player_deaths WHERE time >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 70 DAY))) AS t2"; }
''',
            cv.SERVER_PROTOCOL[0]: "void parseCyclopediaCharacterInfo(); void sendBestiaryCharms(); void sendBosstiaryData(); void sendHousesInfo();",
            cv.SERVER_PROTOCOL[1]: "void ProtocolGame::parseCyclopediaCharacterInfo() {} void ProtocolGame::sendBestiaryCharms() {} void ProtocolGame::sendBosstiaryData() {} void ProtocolGame::sendHousesInfo() {}",
            cv.SCHEMA_SQL: "INSERT INTO `boosted_boss` (`boostname`) VALUES ('default');",
            "data-otservbr-global/monster/vermins/giant_spider.lua": BESTIARY,
            "data-otservbr-global/monster/bosses/brain_head.lua": BOSSTIARY,
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    @staticmethod
    def write_client(root: Path) -> None:
        files = {
            cv.CLIENT_PROTOCOL[0]: "void parseCyclopediaCharacterInfo(); void sendRequestBestiary();",
            cv.CLIENT_PROTOCOL[1]: "void ProtocolGame::parseCyclopediaCharacterInfo() {}",
            cv.CLIENT_PROTOCOL[2]: "void ProtocolGame::sendRequestBestiary() {}",
        }
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
