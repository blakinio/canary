#!/usr/bin/env python3
"""Apply the reviewed Cyclopedia runtime fixes as one atomic source batch."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).relative_to(ROOT).as_posix()
WORKFLOW = ".github/workflows/apply-cyclopedia-runtime-fixes.yml"
MARKER = "2026-07-12 22:10 Europe/Warsaw — runtime correctness batch"


def load(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def replace_once(files: dict[str, str], relative: str, old: str, new: str) -> None:
    text = files.setdefault(relative, load(relative))
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{relative}: expected exactly one literal match, found {count}")
    files[relative] = text.replace(old, new, 1)


def replace_regex_once(files: dict[str, str], relative: str, pattern: str, replacement: str) -> None:
    text = files.setdefault(relative, load(relative))
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"{relative}: expected exactly one regex match, found {count}")
    files[relative] = updated


def append_once(files: dict[str, str], relative: str, body: str) -> None:
    text = files.setdefault(relative, load(relative))
    if MARKER in text:
        raise RuntimeError(f"{relative}: changelog marker already exists")
    files[relative] = text.rstrip() + "\n\n" + body.strip() + "\n"


def main() -> int:
    files: dict[str, str] = {}

    replace_once(
        files,
        "data/scripts/lib/register_bestiary_charm.lua",
        "registerCharm.category = function(charm, mask)\n\tif mask.type then\n\t\tcharm:category(mask.category)\n\tend\nend",
        "registerCharm.category = function(charm, mask)\n\tif mask.category then\n\t\tcharm:category(mask.category)\n\tend\nend",
    )

    replace_once(
        files,
        "src/io/iobestiary.cpp",
        "void IOBestiary::addBestiaryKill(const std::shared_ptr<Player> &player, const std::shared_ptr<MonsterType> &mtype, uint32_t amount /*= 1*/) {\n\tuint16_t raceid = mtype->info.raceid;\n\tif (raceid == 0 || !player || !mtype) {\n\t\treturn;\n\t}",
        "void IOBestiary::addBestiaryKill(const std::shared_ptr<Player> &player, const std::shared_ptr<MonsterType> &mtype, uint32_t amount /*= 1*/) {\n\tif (!player || !mtype) {\n\t\treturn;\n\t}\n\n\tconst uint16_t raceid = mtype->info.raceid;\n\tif (raceid == 0) {\n\t\treturn;\n\t}",
    )
    replace_once(
        files,
        "src/io/iobestiary.cpp",
        "uint64_t resetAllCharmsCost = 100000 + (playerLevel > 100 ? playerLevel * 11000 : 0);",
        "uint64_t resetAllCharmsCost = 100000 + (playerLevel > 100 ? (playerLevel - 100) * 11000 : 0);",
    )
    replace_once(
        files,
        "src/io/iobestiary.cpp",
        "float chanceInPercent = chance / 1000;",
        "const double chanceInPercent = static_cast<double>(chance) / 1000.0;",
    )

    replace_regex_once(
        files,
        "src/creatures/players/components/player_cyclopedia.cpp",
        r"\(select count\(\*\) FROM `player_deaths` WHERE \(\(`killed_by` = \{\} AND `is_player` = 1\) OR \(`mostdamage_by` = \{\} AND `mostdamage_is_player` = 1\)\)\) as `entries`",
        "(select count(*) FROM `player_deaths` WHERE ((`killed_by` = {} AND `is_player` = 1) OR (`mostdamage_by` = {} AND `mostdamage_is_player` = 1)) AND `time` >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 70 DAY))) as `entries`",
    )

    old_boss_block = '''\tDBResult_ptr result = database.storeQuery(query);\n\tif (!result) {\n\t\tg_logger().error("[{}] Failed to detect boosted boss database. (CODE 01)", __FUNCTION__);\n\t\treturn;\n\t}\n\n\tconst auto &bossMap = getBosstiaryMap();\n\tif (bossMap.size() <= 1) {\n\t\tg_logger().error("[{}] It is not possible to create a boosted boss with only one registered boss. (CODE 02)", __FUNCTION__);\n\t\treturn;\n\t}\n\n\tauto timeNow = getTimeNow();\n\tauto time = localtime(&timeNow);\n\tauto today = time->tm_mday;\n\n\tif (!result) {\n\t\tg_logger().warn("[{}] No boosted boss found in g_database(). A new one will be selected.", __FUNCTION__);\n\t} else {\n\t\tauto date = result->getNumber<uint16_t>("date");\n\t\tif (date == today) {\n\t\t\tstd::string bossName = result->getString("boostname");\n\t\t\tuint16_t bossId = result->getNumber<uint16_t>("raceid");\n\t\t\tsetBossBoostedName(bossName);\n\t\t\tsetBossBoostedId(bossId);\n\t\t\tg_logger().info("Boosted boss: {}", bossName);\n\t\t\treturn;\n\t\t}\n\t}'''
    new_boss_block = '''\tDBResult_ptr result = database.storeQuery(query);\n\n\tconst auto &bossMap = getBosstiaryMap();\n\tif (bossMap.size() <= 1) {\n\t\tg_logger().error("[{}] It is not possible to create a boosted boss with only one registered boss. (CODE 02)", __FUNCTION__);\n\t\treturn;\n\t}\n\n\tauto timeNow = getTimeNow();\n\tauto time = localtime(&timeNow);\n\tauto today = time->tm_mday;\n\n\tif (!result) {\n\t\tg_logger().warn("[{}] No boosted boss row found. A new one will be selected.", __FUNCTION__);\n\t\tif (!database.executeQuery("INSERT INTO `boosted_boss` (`boostname`, `date`, `raceid`) VALUES ('default', '0', '0')")) {\n\t\t\tg_logger().error("[{}] Failed to initialize the boosted boss database row. (CODE 01)", __FUNCTION__);\n\t\t\treturn;\n\t\t}\n\t} else {\n\t\tauto date = result->getNumber<uint16_t>("date");\n\t\tif (date == today) {\n\t\t\tstd::string bossName = result->getString("boostname");\n\t\t\tuint16_t bossId = result->getNumber<uint16_t>("raceid");\n\t\t\tsetBossBoostedName(bossName);\n\t\t\tsetBossBoostedId(bossId);\n\t\t\tg_logger().info("Boosted boss: {}", bossName);\n\t\t\treturn;\n\t\t}\n\t}'''
    replace_once(files, "src/io/io_bosstiary.cpp", old_boss_block, new_boss_block)

    test_path = "tools/ai-agent/test_cyclopedia_validation.py"
    test_insert = '''\n    def test_corrected_runtime_patterns_are_not_reported(self) -> None:\n        with tempfile.TemporaryDirectory() as temp:\n            root = Path(temp)\n            self.write_fixture(root)\n\n            replacements = {\n                cv.CHARM_HELPER: [("if mask.type then charm:category(mask.category)", "if mask.category then charm:category(mask.category)")],\n                cv.BESTIARY_CPP: [\n                    ("100000 + (playerLevel > 100 ? playerLevel * 11000 : 0)", "100000 + (playerLevel > 100 ? (playerLevel - 100) * 11000 : 0)"),\n                    ("auto id = mtype->info.raceid; if (!mtype) return;", "if (!mtype) return; auto id = mtype->info.raceid;"),\n                    ("float chanceInPercent = chance / 1000;", "const double chanceInPercent = static_cast<double>(chance) / 1000.0;"),\n                ],\n                cv.BOSSTIARY_CPP: [("if (!result) { return; } if (!result) selectNewBoss();", "if (!result) { initializeRow(); } else { useStoredBoss(); }")],\n                cv.PLAYER_CYCLOPEDIA_CPP: [("SELECT count(*) AS entries FROM player_deaths)", "SELECT count(*) AS entries FROM player_deaths WHERE time >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 70 DAY)))")],\n            }\n            for relative, substitutions in replacements.items():\n                path = root / relative\n                text = path.read_text(encoding="utf-8")\n                for old, new in substitutions:\n                    self.assertIn(old, text)\n                    text = text.replace(old, new, 1)\n                path.write_text(text, encoding="utf-8")\n\n            finding_ids = {item["id"] for item in cv.known_patterns(root)}\n            self.assertFalse({\n                "CHARM-CATEGORY-GUARD-USES-TYPE",\n                "CHARM-RESET-ALL-LEVEL-FORMULA",\n                "BESTIARY-DIFFICULTY-INTEGER-DIVISION",\n                "BESTIARY-MTYPE-DEREFERENCE-BEFORE-GUARD",\n                "CHARACTER-RECENT-PVP-COUNT-WINDOW-MISMATCH",\n                "BOSSTIARY-EMPTY-RESULT-FALLBACK-UNREACHABLE",\n            } & finding_ids)\n'''
    replace_once(
        files,
        test_path,
        "\n    @staticmethod\n    def inventory(bestiary: list[dict], bosstiary: list[dict]) -> dict:",
        test_insert + "\n    @staticmethod\n    def inventory(bestiary: list[dict], bosstiary: list[dict]) -> dict:",
    )

    changelog = f'''### {MARKER}\n\n- corrected Bestiary difficulty arithmetic to preserve fractional thresholds;\n- corrected the all-Charm reset formula to charge 11,000 gold only for levels above 100;\n- made Bestiary kill attribution null-safe before reading the monster type;\n- corrected the Charm category guard;\n- aligned recent-PvP pagination count with the 70-day row window;\n- restored boosted-boss initialization when the table has no row;\n- added a regression test proving all six bad source patterns disappear;\n- no protocol, schema, map, asset or player-data migration was added in this batch.\n'''
    append_once(files, "docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md", changelog)
    append_once(files, "docs/ai-agent/CYCLOPEDIA_VALIDATION_REPORT.md", "## Remediation log\n\n" + changelog)
    append_once(files, "docs/agents/tasks/active/CAN-20260712-cyclopedia-validation.md", "## Work log update\n\n" + changelog)
    append_once(files, "docs/ai-agent/CYCLOPEDIA_FIX_LOG.md", "## Applied batch\n\n" + changelog)

    for relative, text in files.items():
        (ROOT / relative).write_text(text, encoding="utf-8")

    (ROOT / SELF).unlink()
    (ROOT / WORKFLOW).unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
