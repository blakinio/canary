#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    if new in content:
        return
    if old not in content:
        raise RuntimeError(f"marker not found in {path}: {old[:80]!r}")
    write(path, content.replace(old, new, 1))


# Main config switch.
replace_once(
    "config.lua.dist",
    'logLevel = "info"\n',
    'logLevel = "info"\n\n'
    '-- Account-wide quest access. Disable this to fail closed without removing data.\n'
    '-- Restart the server after changing this value.\n'
    'accountWideQuestSystemEnabled = true\n',
)

# ConfigManager enum and loader.
replace_once(
    "src/config/config_enums.hpp",
    "\tACTIONS_DELAY_INTERVAL,\n",
    "\tACTIONS_DELAY_INTERVAL,\n\tACCOUNT_WIDE_QUESTS_ENABLED,\n",
)
replace_once(
    "src/config/configmanager.cpp",
    '\tloadBoolConfig(L, AIMBOT_HOTKEY_ENABLED, "hotkeyAimbotEnabled", true);\n',
    '\tloadBoolConfig(L, ACCOUNT_WIDE_QUESTS_ENABLED, "accountWideQuestSystemEnabled", true);\n'
    '\tloadBoolConfig(L, AIMBOT_HOTKEY_ENABLED, "hotkeyAimbotEnabled", true);\n',
)

# Atomic affected-row DB primitive.
replace_once(
    "src/database/database.hpp",
    "\t#include <mutex>\n",
    "\t#include <mutex>\n\t#include <optional>\n",
)
replace_once(
    "src/database/database.hpp",
    "\tbool executeQuery(std::string_view query);\n\n\tDBResult_ptr storeQuery",
    "\tbool executeQuery(std::string_view query);\n\tstd::optional<uint64_t> executeQueryAffectedRows(std::string_view query);\n\n\tDBResult_ptr storeQuery",
)
replace_once(
    "src/database/database.cpp",
    "bool Database::executeQuery(std::string_view query) {\n",
    "bool Database::executeQuery(std::string_view query) {\n",
)
replace_once(
    "src/database/database.cpp",
    "\treturn success;\n}\n\nDBResult_ptr Database::storeQuery",
    "\treturn success;\n}\n\n"
    "std::optional<uint64_t> Database::executeQueryAffectedRows(std::string_view query) {\n"
    "\tif (!handle) {\n"
    "\t\tg_logger().error(\"Database not initialized!\");\n"
    "\t\treturn std::nullopt;\n"
    "\t}\n\n"
    "\tg_logger().trace(\"Executing Query with affected rows: {}\", query);\n\n"
    "\tmetrics::lock_latency measureLock(\"database\");\n"
    "\tstd::scoped_lock lock { databaseLock };\n"
    "\tmeasureLock.stop();\n\n"
    "\tmetrics::query_latency measure(query.substr(0, 50));\n"
    "\tif (!retryQuery(query, 10)) {\n"
    "\t\tmysql_free_result(mysql_store_result(handle));\n"
    "\t\treturn std::nullopt;\n"
    "\t}\n\n"
    "\tmysql_free_result(mysql_store_result(handle));\n"
    "\tconst auto affectedRows = mysql_affected_rows(handle);\n"
    "\tif (affectedRows == static_cast<my_ulonglong>(-1)) {\n"
    "\t\tg_logger().error(\"Failed to read affected rows: {}\", mysql_error(handle));\n"
    "\t\treturn std::nullopt;\n"
    "\t}\n"
    "\treturn static_cast<uint64_t>(affectedRows);\n"
    "}\n\n"
    "DBResult_ptr Database::storeQuery",
)
replace_once(
    "src/lua/functions/core/libs/db_functions.hpp",
    "\tstatic int luaDatabaseExecute(lua_State* L);\n",
    "\tstatic int luaDatabaseExecute(lua_State* L);\n\tstatic int luaDatabaseExecuteAffectedRows(lua_State* L);\n",
)
replace_once(
    "src/lua/functions/core/libs/db_functions.cpp",
    '\tLua::registerMethod(L, "db", "query", DBFunctions::luaDatabaseExecute);\n',
    '\tLua::registerMethod(L, "db", "query", DBFunctions::luaDatabaseExecute);\n'
    '\tLua::registerMethod(L, "db", "queryAffectedRows", DBFunctions::luaDatabaseExecuteAffectedRows);\n',
)
replace_once(
    "src/lua/functions/core/libs/db_functions.cpp",
    "int DBFunctions::luaDatabaseExecute(lua_State* L) {\n\t// db.query(query)\n\tLua::pushBoolean(L, Database::getInstance().executeQuery(Lua::getString(L, -1)));\n\treturn 1;\n}\n",
    "int DBFunctions::luaDatabaseExecute(lua_State* L) {\n\t// db.query(query)\n\tLua::pushBoolean(L, Database::getInstance().executeQuery(Lua::getString(L, -1)));\n\treturn 1;\n}\n\n"
    "int DBFunctions::luaDatabaseExecuteAffectedRows(lua_State* L) {\n"
    "\t// db.queryAffectedRows(query)\n"
    "\tconst auto affectedRows = Database::getInstance().executeQueryAffectedRows(Lua::getString(L, -1));\n"
    "\tif (!affectedRows.has_value()) {\n"
    "\t\tLua::pushBoolean(L, false);\n"
    "\t} else {\n"
    "\t\tlua_pushnumber(L, static_cast<lua_Number>(*affectedRows));\n"
    "\t}\n"
    "\treturn 1;\n"
    "}\n",
)

# Runtime switch, atomic reward claim, access inspection API and command.
account_path = "data-otservbr-global/scripts/custom/account_quest_system.lua"
account = read(account_path)
account = account.replace(
    "function AccountQuest.isEnabled()\n\treturn AccountQuest.config.enabled == true\nend",
    "function AccountQuest.isEnabled()\n"
    "\treturn configManager.getBoolean(configKeys.ACCOUNT_WIDE_QUESTS_ENABLED) and AccountQuest.config.enabled == true\n"
    "end",
    1,
)
account = account.replace(
    "\tif not AccountQuest.canClaimReward(player, normalizedId) then\n\t\treturn false\n\tend\n\n"
    "\treturn db.query(string.format(\"INSERT IGNORE INTO `account_quest_rewards` (`account_id`, `player_id`, `quest_id`, `reward_mode`, `claimed_by`) VALUES (%d, %d, %s, %s, %d)\", accountId, playerId, db.escapeString(normalizedId), db.escapeString(mode), player:getGuid()))",
    "\tlocal affectedRows = db.queryAffectedRows(string.format(\"INSERT IGNORE INTO `account_quest_rewards` (`account_id`, `player_id`, `quest_id`, `reward_mode`, `claimed_by`) VALUES (%d, %d, %s, %s, %d)\", accountId, playerId, db.escapeString(normalizedId), db.escapeString(mode), player:getGuid()))\n"
    "\treturn affectedRows == 1",
    1,
)
marker = "function AccountQuest.resetCharacterProgress(player, questId)\n"
if "function AccountQuest.getAccessList" not in account:
    access_api = '''function AccountQuest.getAccessList(player)\n\tlocal accountId = getPlayerAccountId(player)\n\tif not accountId then\n\t\treturn nil, \"Player has no valid account id.\"\n\tend\n\n\tlocal entries = {}\n\tlocal query = db.storeQuery(string.format([[\n\t\tSELECT `quest_id`, `unlocked_by`, DATE_FORMAT(`unlocked_at`, '%%Y-%%m-%%d %%H:%%i:%%s') AS `unlocked_at`\n\t\tFROM `account_quest_access`\n\t\tWHERE `account_id` = %d\n\t\tORDER BY `quest_id` ASC\n\t]], accountId))\n\tif not query then\n\t\treturn entries\n\tend\n\n\trepeat\n\t\ttable.insert(entries, {\n\t\t\tquestId = result.getString(query, \"quest_id\"),\n\t\t\tunlockedBy = result.getNumber(query, \"unlocked_by\"),\n\t\t\tunlockedAt = result.getString(query, \"unlocked_at\"),\n\t\t})\n\tuntil not result.next(query)\n\tresult.free(query)\n\treturn entries\nend\n\n'''
    account = account.replace(marker, access_api + marker, 1)
if 'local questAccess = TalkAction("/questaccess")' not in account:
    account += '''\nlocal questAccess = TalkAction("/questaccess")\n\nfunction questAccess.onSay(player, words, param)\n\tlocal target = player\n\tlocal playerName = param:gsub("^%s+", ""):gsub("%s+$", "")\n\tif playerName ~= "" then\n\t\ttarget = Player(playerName)\n\t\tif not target then\n\t\t\tplayer:sendCancelMessage("The target player must be online.")\n\t\t\treturn true\n\t\tend\n\tend\n\n\tlocal entries, errorMessage = AccountQuest.getAccessList(target)\n\tif not entries then\n\t\tplayer:sendCancelMessage(errorMessage)\n\t\treturn true\n\tend\n\n\tplayer:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("Account quest access for %s (account %d):", target:getName(), target:getAccountId()))\n\tif #entries == 0 then\n\t\tplayer:sendTextMessage(MESSAGE_EVENT_ADVANCE, "No account-wide quest access is recorded.")\n\t\treturn true\n\tend\n\n\tfor _, entry in ipairs(entries) do\n\t\tplayer:sendTextMessage(MESSAGE_EVENT_ADVANCE, string.format("%s | unlocked by GUID %d | %s", entry.questId, entry.unlockedBy, entry.unlockedAt))\n\tend\n\treturn true\nend\n\nquestAccess:separator(" ")\nquestAccess:groupType("god")\nquestAccess:register()\n'''
write(account_path, account)

# Versioned database migration.
write(
    "data-otservbr-global/migrations/62.lua",
    '''function onUpdateDatabase()\n\tlogger.info("Updating database to version 62 (account-wide quest persistence and migration audit)")\n\n\tif not db.query([[\n\t\tCREATE TABLE IF NOT EXISTS `account_quest_access` (\n\t\t\t`account_id` INT(11) UNSIGNED NOT NULL,\n\t\t\t`quest_id` VARCHAR(128) NOT NULL,\n\t\t\t`unlocked_by` INT(11) NOT NULL DEFAULT 0,\n\t\t\t`unlocked_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n\t\t\tPRIMARY KEY (`account_id`, `quest_id`),\n\t\t\tCONSTRAINT `account_quest_access_account_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE\n\t\t) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\t]]) then\n\t\treturn false\n\tend\n\n\tif not db.query([[\n\t\tCREATE TABLE IF NOT EXISTS `account_quest_rewards` (\n\t\t\t`account_id` INT(11) UNSIGNED NOT NULL,\n\t\t\t`player_id` INT(11) NOT NULL DEFAULT 0,\n\t\t\t`quest_id` VARCHAR(128) NOT NULL,\n\t\t\t`reward_mode` VARCHAR(32) NOT NULL,\n\t\t\t`claimed_by` INT(11) NOT NULL DEFAULT 0,\n\t\t\t`claimed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n\t\t\tPRIMARY KEY (`account_id`, `quest_id`, `reward_mode`, `player_id`),\n\t\t\tCONSTRAINT `account_quest_rewards_account_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE\n\t\t) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\t]]) then\n\t\treturn false\n\tend\n\n\treturn db.query([[\n\t\tCREATE TABLE IF NOT EXISTS `account_quest_migrations` (\n\t\t\t`id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,\n\t\t\t`migration_type` VARCHAR(32) NOT NULL,\n\t\t\t`old_value` VARCHAR(128) NOT NULL,\n\t\t\t`new_value` VARCHAR(128) NOT NULL,\n\t\t\t`rows_affected` INT UNSIGNED NOT NULL DEFAULT 0,\n\t\t\t`executed_by` VARCHAR(128) NOT NULL DEFAULT 'tool',\n\t\t\t`executed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\n\t\t\tPRIMARY KEY (`id`)\n\t\t) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\t]])\nend\n''',
)

# Fresh-install schema additions.
schema = read("schema.sql")
if "-- Table structure `account_quest_access`" not in schema:
    block = '''\n-- Table structure `account_quest_access`\nCREATE TABLE IF NOT EXISTS `account_quest_access` (\n    `account_id` int(11) UNSIGNED NOT NULL,\n    `quest_id` varchar(128) NOT NULL,\n    `unlocked_by` int(11) NOT NULL DEFAULT '0',\n    `unlocked_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,\n    CONSTRAINT `account_quest_access_pk` PRIMARY KEY (`account_id`, `quest_id`),\n    CONSTRAINT `account_quest_access_account_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n-- Table structure `account_quest_rewards`\nCREATE TABLE IF NOT EXISTS `account_quest_rewards` (\n    `account_id` int(11) UNSIGNED NOT NULL,\n    `player_id` int(11) NOT NULL DEFAULT '0',\n    `quest_id` varchar(128) NOT NULL,\n    `reward_mode` varchar(32) NOT NULL,\n    `claimed_by` int(11) NOT NULL DEFAULT '0',\n    `claimed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,\n    CONSTRAINT `account_quest_rewards_pk` PRIMARY KEY (`account_id`, `quest_id`, `reward_mode`, `player_id`),\n    CONSTRAINT `account_quest_rewards_account_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n-- Table structure `account_quest_migrations`\nCREATE TABLE IF NOT EXISTS `account_quest_migrations` (\n    `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT,\n    `migration_type` varchar(32) NOT NULL,\n    `old_value` varchar(128) NOT NULL,\n    `new_value` varchar(128) NOT NULL,\n    `rows_affected` int UNSIGNED NOT NULL DEFAULT '0',\n    `executed_by` varchar(128) NOT NULL DEFAULT 'tool',\n    `executed_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,\n    CONSTRAINT `account_quest_migrations_pk` PRIMARY KEY (`id`)\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n'''
    schema = schema.replace("\n-- Table structure `account_sessions`", block + "\n-- Table structure `account_sessions`", 1)
    write("schema.sql", schema)

# Migration CLI.
write(
    "tools/account-quests/migrate_account_quests.py",
    r'''#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
from contextlib import contextmanager

import pymysql

QUEST_ID = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")


def connect():
    return pymysql.connect(
        host=os.getenv("AQ_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("AQ_DB_PORT", "3306")),
        user=os.getenv("AQ_DB_USER", "root"),
        password=os.getenv("AQ_DB_PASSWORD", ""),
        database=os.getenv("AQ_DB_NAME", "canary"),
        autocommit=False,
        charset="utf8mb4",
    )


def scalar(cursor, sql, params):
    cursor.execute(sql, params)
    row = cursor.fetchone()
    return int(row[0])


def audit(cursor, kind, old, new, rows, executed_by):
    cursor.execute(
        "INSERT INTO account_quest_migrations "
        "(migration_type, old_value, new_value, rows_affected, executed_by) "
        "VALUES (%s, %s, %s, %s, %s)",
        (kind, str(old), str(new), rows, executed_by),
    )


def migrate_quest_id(connection, old_id, new_id, apply=False, executed_by="tool"):
    if not QUEST_ID.fullmatch(old_id) or not QUEST_ID.fullmatch(new_id):
        raise ValueError("quest ids must use lowercase letters, digits, _, -, or .")
    if old_id == new_id:
        raise ValueError("old and new quest ids are identical")

    with connection.cursor() as cursor:
        access_count = scalar(cursor, "SELECT COUNT(*) FROM account_quest_access WHERE quest_id=%s", (old_id,))
        reward_count = scalar(cursor, "SELECT COUNT(*) FROM account_quest_rewards WHERE quest_id=%s", (old_id,))
        if not apply:
            return {"access": access_count, "rewards": reward_count, "applied": False}

        cursor.execute(
            "INSERT INTO account_quest_access (account_id, quest_id, unlocked_by, unlocked_at) "
            "SELECT account_id, %s, unlocked_by, unlocked_at FROM account_quest_access WHERE quest_id=%s "
            "ON DUPLICATE KEY UPDATE "
            "unlocked_by=IF(VALUES(unlocked_at) < unlocked_at, VALUES(unlocked_by), unlocked_by), "
            "unlocked_at=LEAST(unlocked_at, VALUES(unlocked_at))",
            (new_id, old_id),
        )
        cursor.execute("DELETE FROM account_quest_access WHERE quest_id=%s", (old_id,))

        cursor.execute(
            "INSERT INTO account_quest_rewards "
            "(account_id, player_id, quest_id, reward_mode, claimed_by, claimed_at) "
            "SELECT account_id, player_id, %s, reward_mode, claimed_by, claimed_at "
            "FROM account_quest_rewards WHERE quest_id=%s "
            "ON DUPLICATE KEY UPDATE "
            "claimed_by=IF(VALUES(claimed_at) < claimed_at, VALUES(claimed_by), claimed_by), "
            "claimed_at=LEAST(claimed_at, VALUES(claimed_at))",
            (new_id, old_id),
        )
        cursor.execute("DELETE FROM account_quest_rewards WHERE quest_id=%s", (old_id,))
        audit(cursor, "quest-id", old_id, new_id, access_count + reward_count, executed_by)
    connection.commit()
    return {"access": access_count, "rewards": reward_count, "applied": True}


def migrate_storage(connection, old_key, new_key, policy="abort", apply=False, executed_by="tool"):
    if old_key < 0 or new_key < 0 or old_key == new_key:
        raise ValueError("storage keys must be distinct non-negative integers")
    if policy not in {"abort", "keep-target", "keep-source", "max"}:
        raise ValueError("invalid conflict policy")

    with connection.cursor() as cursor:
        source_count = scalar(cursor, "SELECT COUNT(*) FROM player_storage WHERE `key`=%s", (old_key,))
        conflict_count = scalar(
            cursor,
            "SELECT COUNT(*) FROM player_storage old_s "
            "JOIN player_storage new_s ON new_s.player_id=old_s.player_id AND new_s.`key`=%s "
            "WHERE old_s.`key`=%s",
            (new_key, old_key),
        )
        if conflict_count and policy == "abort":
            raise RuntimeError(f"{conflict_count} player storage conflicts; choose an explicit policy")
        if not apply:
            return {"source": source_count, "conflicts": conflict_count, "applied": False}

        if policy == "keep-target":
            cursor.execute(
                "DELETE old_s FROM player_storage old_s "
                "JOIN player_storage new_s ON new_s.player_id=old_s.player_id AND new_s.`key`=%s "
                "WHERE old_s.`key`=%s",
                (new_key, old_key),
            )
        elif policy == "keep-source":
            cursor.execute(
                "DELETE new_s FROM player_storage new_s "
                "JOIN player_storage old_s ON old_s.player_id=new_s.player_id AND old_s.`key`=%s "
                "WHERE new_s.`key`=%s",
                (old_key, new_key),
            )
        elif policy == "max":
            cursor.execute(
                "UPDATE player_storage new_s "
                "JOIN player_storage old_s ON old_s.player_id=new_s.player_id AND old_s.`key`=%s "
                "SET new_s.value=GREATEST(new_s.value, old_s.value) WHERE new_s.`key`=%s",
                (old_key, new_key),
            )
            cursor.execute(
                "DELETE old_s FROM player_storage old_s "
                "JOIN player_storage new_s ON new_s.player_id=old_s.player_id AND new_s.`key`=%s "
                "WHERE old_s.`key`=%s",
                (new_key, old_key),
            )

        cursor.execute("UPDATE player_storage SET `key`=%s WHERE `key`=%s", (new_key, old_key))
        audit(cursor, f"storage:{policy}", old_key, new_key, source_count, executed_by)
    connection.commit()
    return {"source": source_count, "conflicts": conflict_count, "applied": True}


def main():
    parser = argparse.ArgumentParser(description="Safely migrate account-quest ids or player storage keys")
    parser.add_argument("--apply", action="store_true", help="commit changes; default is dry-run")
    parser.add_argument("--executed-by", default=os.getenv("USER", "tool"))
    sub = parser.add_subparsers(dest="command", required=True)

    quest = sub.add_parser("quest-id")
    quest.add_argument("--from", dest="old", required=True)
    quest.add_argument("--to", dest="new", required=True)

    storage = sub.add_parser("storage")
    storage.add_argument("--from", dest="old", type=int, required=True)
    storage.add_argument("--to", dest="new", type=int, required=True)
    storage.add_argument("--conflict-policy", choices=["abort", "keep-target", "keep-source", "max"], default="abort")

    args = parser.parse_args()
    connection = connect()
    try:
        if args.command == "quest-id":
            result = migrate_quest_id(connection, args.old, args.new, args.apply, args.executed_by)
        else:
            result = migrate_storage(connection, args.old, args.new, args.conflict_policy, args.apply, args.executed_by)
        mode = "APPLIED" if result["applied"] else "DRY-RUN"
        print(f"{mode}: {result}")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"account quest migration failed: {error}", file=sys.stderr)
        raise SystemExit(1)
''',
)

# MariaDB integration tests.
write(
    "tools/account-quests/test_account_quests_db.py",
    r'''#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import os
import threading
import unittest
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("aq_migrate", ROOT / "tools/account-quests/migrate_account_quests.py")
migrate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(migrate)


def connection():
    return pymysql.connect(
        host=os.getenv("AQ_DB_HOST", "127.0.0.1"),
        port=int(os.getenv("AQ_DB_PORT", "3306")),
        user=os.getenv("AQ_DB_USER", "root"),
        password=os.getenv("AQ_DB_PASSWORD", "root"),
        database=os.getenv("AQ_DB_NAME", "account_quests_test"),
        autocommit=False,
        charset="utf8mb4",
    )


SCHEMA = """
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS account_quest_migrations;
DROP TABLE IF EXISTS account_quest_rewards;
DROP TABLE IF EXISTS account_quest_access;
DROP TABLE IF EXISTS player_storage;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS accounts;
SET FOREIGN_KEY_CHECKS=1;
CREATE TABLE accounts (id INT UNSIGNED PRIMARY KEY) ENGINE=InnoDB;
CREATE TABLE players (id INT PRIMARY KEY, account_id INT UNSIGNED NOT NULL, FOREIGN KEY(account_id) REFERENCES accounts(id)) ENGINE=InnoDB;
CREATE TABLE player_storage (player_id INT NOT NULL, `key` INT UNSIGNED NOT NULL, value INT NOT NULL, PRIMARY KEY(player_id, `key`), FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE) ENGINE=InnoDB;
CREATE TABLE account_quest_access (account_id INT UNSIGNED NOT NULL, quest_id VARCHAR(128) NOT NULL, unlocked_by INT NOT NULL DEFAULT 0, unlocked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(account_id, quest_id), FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE account_quest_rewards (account_id INT UNSIGNED NOT NULL, player_id INT NOT NULL DEFAULT 0, quest_id VARCHAR(128) NOT NULL, reward_mode VARCHAR(32) NOT NULL, claimed_by INT NOT NULL DEFAULT 0, claimed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(account_id, quest_id, reward_mode, player_id), FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE account_quest_migrations (id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, migration_type VARCHAR(32) NOT NULL, old_value VARCHAR(128) NOT NULL, new_value VARCHAR(128) NOT NULL, rows_affected INT UNSIGNED NOT NULL DEFAULT 0, executed_by VARCHAR(128) NOT NULL, executed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO accounts VALUES (1), (2);
INSERT INTO players VALUES (10,1), (11,1), (20,2);
"""


class AccountQuestDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        self.db = connection()
        with self.db.cursor() as cursor:
            for statement in SCHEMA.split(";"):
                if statement.strip():
                    cursor.execute(statement)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_atomic_reward_claim_has_exactly_one_winner(self):
        winners = []
        lock = threading.Lock()

        def claim(guid):
            db = connection()
            try:
                with db.cursor() as cursor:
                    cursor.execute(
                        "INSERT IGNORE INTO account_quest_rewards "
                        "(account_id, player_id, quest_id, reward_mode, claimed_by) "
                        "VALUES (1, 0, 'atomic-test', 'oncePerAccount', %s)",
                        (guid,),
                    )
                    db.commit()
                    with lock:
                        winners.append(cursor.rowcount)
            finally:
                db.close()

        threads = [threading.Thread(target=claim, args=(1000 + index,)) for index in range(16)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(1, sum(winners))
        with self.db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM account_quest_rewards WHERE quest_id='atomic-test'")
            self.assertEqual(1, cursor.fetchone()[0])

    def test_account_access_is_shared_only_inside_account(self):
        with self.db.cursor() as cursor:
            cursor.execute("INSERT INTO account_quest_access VALUES (1, 'the-ape-city', 10, NOW())")
            cursor.execute("SELECT COUNT(*) FROM account_quest_access WHERE account_id=(SELECT account_id FROM players WHERE id=11) AND quest_id='the-ape-city'")
            self.assertEqual(1, cursor.fetchone()[0])
            cursor.execute("SELECT COUNT(*) FROM account_quest_access WHERE account_id=(SELECT account_id FROM players WHERE id=20) AND quest_id='the-ape-city'")
            self.assertEqual(0, cursor.fetchone()[0])

    def test_quest_id_migration_merges_conflicts_and_audits(self):
        with self.db.cursor() as cursor:
            cursor.execute("INSERT INTO account_quest_access VALUES (1,'old-id',10,'2020-01-01')")
            cursor.execute("INSERT INTO account_quest_access VALUES (1,'new-id',11,'2021-01-01')")
            cursor.execute("INSERT INTO account_quest_rewards VALUES (1,0,'old-id','oncePerAccount',10,'2020-01-01')")
        self.db.commit()
        result = migrate.migrate_quest_id(self.db, "old-id", "new-id", apply=True, executed_by="test")
        self.assertTrue(result["applied"])
        with self.db.cursor() as cursor:
            cursor.execute("SELECT quest_id, unlocked_by, YEAR(unlocked_at) FROM account_quest_access")
            self.assertEqual(("new-id", 10, 2020), cursor.fetchone())
            cursor.execute("SELECT COUNT(*) FROM account_quest_migrations WHERE migration_type='quest-id'")
            self.assertEqual(1, cursor.fetchone()[0])

    def test_storage_migration_aborts_on_conflict_by_default(self):
        with self.db.cursor() as cursor:
            cursor.execute("INSERT INTO player_storage VALUES (10,100,3),(10,200,7),(11,100,5)")
        self.db.commit()
        with self.assertRaises(RuntimeError):
            migrate.migrate_storage(self.db, 100, 200, apply=True)
        self.db.rollback()
        result = migrate.migrate_storage(self.db, 100, 200, policy="max", apply=True, executed_by="test")
        self.assertEqual(1, result["conflicts"])
        with self.db.cursor() as cursor:
            cursor.execute("SELECT player_id, value FROM player_storage WHERE `key`=200 ORDER BY player_id")
            self.assertEqual(((10, 7), (11, 5)), cursor.fetchall())

    def test_character_storage_reset_does_not_remove_account_access(self):
        with self.db.cursor() as cursor:
            cursor.execute("INSERT INTO account_quest_access VALUES (1,'reset-test',10,NOW())")
            cursor.execute("INSERT INTO player_storage VALUES (10,300,9),(11,300,5)")
            cursor.execute("DELETE FROM player_storage WHERE player_id=10 AND `key`=300")
            cursor.execute("SELECT COUNT(*) FROM account_quest_access WHERE account_id=1 AND quest_id='reset-test'")
            self.assertEqual(1, cursor.fetchone()[0])
            cursor.execute("SELECT value FROM player_storage WHERE player_id=11 AND `key`=300")
            self.assertEqual(5, cursor.fetchone()[0])


if __name__ == "__main__":
    unittest.main()
''',
)

# Validator additions.
validator_path = "tools/account-quests/validate_account_quests.py"
validator = read(validator_path)
validator = validator.replace(
    'QUEST_DOORS = ROOT / "data/scripts/actions/doors/quest_door.lua"\n',
    'QUEST_DOORS = ROOT / "data/scripts/actions/doors/quest_door.lua"\n'
    'CONFIG_DIST = ROOT / "config.lua.dist"\n'
    'CONFIG_ENUMS = ROOT / "src/config/config_enums.hpp"\n'
    'CONFIG_MANAGER = ROOT / "src/config/configmanager.cpp"\n'
    'DB_FUNCTIONS = ROOT / "src/lua/functions/core/libs/db_functions.cpp"\n'
    'MIGRATION_TOOL = ROOT / "tools/account-quests/migrate_account_quests.py"\n'
    'DB_MIGRATION = ROOT / "data-otservbr-global/migrations/62.lua"\n',
    1,
)
validator = validator.replace(
    '    require(\'questReset:groupType("god")\' in text, "administrative reset command must remain god-only")\n',
    '    require(\'questReset:groupType("god")\' in text, "administrative reset command must remain god-only")\n'
    '    require(\'local questAccess = TalkAction("/questaccess")\' in text, "account access inspection command is missing")\n'
    '    require(\'questAccess:groupType("god")\' in text, "account access inspection must remain god-only")\n'
    '    claim_body = function_body(text, "claimReward", "resetCharacterProgress")\n'
    '    require("db.queryAffectedRows" in claim_body, "reward claim must use atomic affected-row insert")\n'
    '    require("AccountQuest.canClaimReward" not in claim_body, "reward claim must not use read-then-insert")\n',
    1,
)
validator = validator.replace(
    '        door_text = read(QUEST_DOORS)\n',
    '        door_text = read(QUEST_DOORS)\n'
    '        config_dist = read(CONFIG_DIST)\n'
    '        config_enums = read(CONFIG_ENUMS)\n'
    '        config_manager = read(CONFIG_MANAGER)\n'
    '        db_functions = read(DB_FUNCTIONS)\n'
    '        migration_tool = read(MIGRATION_TOOL)\n'
    '        db_migration = read(DB_MIGRATION)\n',
    1,
)
validator = validator.replace(
    '        validate_door_integration(door_text)\n',
    '        validate_door_integration(door_text)\n'
    '        require("accountWideQuestSystemEnabled = true" in config_dist, "main config switch is missing")\n'
    '        require("ACCOUNT_WIDE_QUESTS_ENABLED" in config_enums, "config enum is missing")\n'
    '        require(\'"accountWideQuestSystemEnabled"\' in config_manager, "ConfigManager binding is missing")\n'
    '        require(\'"queryAffectedRows"\' in db_functions, "atomic DB Lua primitive is missing")\n'
    '        require("--apply" in migration_tool and "conflict-policy" in migration_tool, "migration CLI safety controls are missing")\n'
    '        require("account_quest_migrations" in db_migration, "migration audit table is missing")\n',
    1,
)
write(validator_path, validator)

# Validator test expected set remains five IDs and gets hardening tests.
test_path = "tools/account-quests/test_validate_account_quests.py"
tests = read(test_path)
if "test_atomic_claim_contract" not in tests:
    tests = tests.replace(
        "\n\nif __name__ == \"__main__\":",
        '''\n    def test_atomic_claim_contract(self) -> None:\n        self.assertIn("db.queryAffectedRows", self.runtime)\n        claim = validator.function_body(self.runtime, "claimReward", "resetCharacterProgress")\n        self.assertNotIn("AccountQuest.canClaimReward", claim)\n\n    def test_main_config_switch_contract(self) -> None:\n        self.assertIn("accountWideQuestSystemEnabled = true", validator.CONFIG_DIST.read_text(encoding="utf-8"))\n        self.assertIn("ACCOUNT_WIDE_QUESTS_ENABLED", validator.CONFIG_ENUMS.read_text(encoding="utf-8"))\n\n    def test_admin_access_command_contract(self) -> None:\n        self.assertIn('TalkAction("/questaccess")', self.runtime)\n        self.assertIn('questAccess:groupType("god")', self.runtime)\n\n\nif __name__ == "__main__":''',
        1,
    )
write(test_path, tests)

# Dedicated workflow with temporary MariaDB.
write(
    ".github/workflows/account-quests.yml",
    '''---\nname: Account Quests\n\non:\n  pull_request:\n    paths:\n      - "config.lua.dist"\n      - "schema.sql"\n      - "src/config/**"\n      - "src/database/**"\n      - "src/lua/functions/core/libs/db_functions.*"\n      - "data-otservbr-global/account_quests.lua"\n      - "data-otservbr-global/migrations/**"\n      - "data-otservbr-global/scripts/custom/account_quest_system.lua"\n      - "data-otservbr-global/scripts/quests/**"\n      - "data/scripts/actions/doors/quest_door.lua"\n      - "docs/systems/account-wide-quests*"\n      - "tools/account-quests/**"\n      - ".github/workflows/account-quests.yml"\n  push:\n    branches: [main]\n    paths:\n      - "config.lua.dist"\n      - "schema.sql"\n      - "src/config/**"\n      - "src/database/**"\n      - "src/lua/functions/core/libs/db_functions.*"\n      - "data-otservbr-global/account_quests.lua"\n      - "data-otservbr-global/migrations/**"\n      - "data-otservbr-global/scripts/custom/account_quest_system.lua"\n      - "data-otservbr-global/scripts/quests/**"\n      - "data/scripts/actions/doors/quest_door.lua"\n      - "docs/systems/account-wide-quests*"\n      - "tools/account-quests/**"\n      - ".github/workflows/account-quests.yml"\n  workflow_dispatch:\n\npermissions:\n  contents: read\n\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n      - name: Validate account quest contract\n        run: python tools/account-quests/validate_account_quests.py\n      - name: Run account quest validator tests\n        run: python -m unittest discover -s tools/account-quests -p "test_validate_*.py" -v\n\n  mariadb-integration:\n    runs-on: ubuntu-latest\n    services:\n      mariadb:\n        image: mariadb:11.4\n        env:\n          MARIADB_ROOT_PASSWORD: root\n          MARIADB_DATABASE: account_quests_test\n        ports:\n          - 3306:3306\n        options: >-\n          --health-cmd="healthcheck.sh --connect --innodb_initialized"\n          --health-interval=5s\n          --health-timeout=5s\n          --health-retries=20\n    env:\n      AQ_DB_HOST: 127.0.0.1\n      AQ_DB_PORT: 3306\n      AQ_DB_USER: root\n      AQ_DB_PASSWORD: root\n      AQ_DB_NAME: account_quests_test\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.12"\n      - run: python -m pip install --disable-pip-version-check pymysql\n      - name: Run MariaDB integration tests\n        run: python -m unittest tools/account-quests/test_account_quests_db.py -v\n''',
)

# Final handoff source of truth.
write(
    "docs/systems/account-wide-quests-handoff.md",
    '''# Account-wide quest access — handoff\n\nStatus updated: 2026-07-12\n\n## Goal\n\nKeep quest progress, fight state and cooldowns per character while sharing only permanent location access across characters on the same account. Never copy quest-completion storages to alternate characters.\n\n## Completed scope\n\nThe following are implemented on `main` or in the production-hardening batch:\n\n- framework persistence, reward modes and character reset;\n- The Ape City;\n- The Secret Service;\n- In Service of Yalahar;\n- The New Frontier;\n- Wrath of the Emperor;\n- completion-only unlock gates;\n- contract validation and MariaDB integration coverage;\n- main `config.lua` switch: `accountWideQuestSystemEnabled`;\n- god-only `/questaccess [Player Name]` inspection command;\n- atomic reward claim through `db.queryAffectedRows`;\n- versioned DB migration 62 and fresh-install schema;\n- audited quest-id/storage migration CLI.\n\n## Operational commands\n\n```text\n/questaccess\n/questaccess Player Name\n/questreset Player Name, quest-id\n```\n\n`/questaccess` shows every persisted account access row, the unlocking character GUID and timestamp. It is god-only.\n\n## Main switch\n\n```lua\naccountWideQuestSystemEnabled = true\n```\n\nThe main switch and `data-otservbr-global/account_quests.lua.enabled` must both be true. Disabling the switch fails closed without deleting access or reward history. Restart after changing it.\n\n## Reward claim safety\n\n`claimReward` no longer performs `SELECT` followed by `INSERT`. It performs one `INSERT IGNORE` through `db.queryAffectedRows`, which executes the statement and reads `mysql_affected_rows()` while holding the same database lock. Exactly one concurrent caller receives `true`; duplicate callers receive `false`.\n\n## Database integration tests\n\nThe Account Quests workflow starts a temporary MariaDB 11.4 service and verifies:\n\n- exactly one winner across concurrent reward claims;\n- access sharing inside one account and isolation from another account;\n- quest-id migration with conflict merging and audit history;\n- storage conflict protection and explicit merge policy;\n- character storage reset preserving account access and other characters.\n\n## Migration procedure\n\nThe tool defaults to dry-run and requires `--apply` to write. Connection variables are `AQ_DB_HOST`, `AQ_DB_PORT`, `AQ_DB_USER`, `AQ_DB_PASSWORD`, and `AQ_DB_NAME`. Take a database backup and stop the game server before storage migration.\n\nQuest ID:\n\n```bash\npython tools/account-quests/migrate_account_quests.py quest-id --from old-id --to new-id\npython tools/account-quests/migrate_account_quests.py --apply --executed-by operator quest-id --from old-id --to new-id\n```\n\nStorage key:\n\n```bash\npython tools/account-quests/migrate_account_quests.py storage --from 41950 --to 51950\npython tools/account-quests/migrate_account_quests.py --apply --executed-by operator storage --from 41950 --to 51950 --conflict-policy abort\n```\n\nConflict policies:\n\n- `abort` — default and safest; no writes when any player has both keys;\n- `keep-target` — discard the old conflicting value;\n- `keep-source` — overwrite the target conflicting value;\n- `max` — retain the larger value, only for known monotonic progress storages.\n\nEvery applied migration writes an `account_quest_migrations` audit row. Quest-ID migration merges existing destination records and retains the earliest unlock/claim timestamp.\n\n## Access boundaries\n\nStill per character by design:\n\n- quest logs and mission storages;\n- reward rooms and physical rewards;\n- boss/fight state and cooldowns;\n- Yalahar final fight and side decision;\n- New Frontier Tome-of-Knowledge access and reward door;\n- Wrath special teleport states 2/3 and item-dependent behavior.\n\n## Acceptance and deployment\n\nRepository verification consists of standard CI, Account Quests contract tests, a C++ build, and temporary-MariaDB tests. Operators should still perform a short smoke test on their own production-like server because repository CI cannot connect to an external live world:\n\n1. character A completes a quest and records access;\n2. character B on the same account can use only shared permanent access;\n3. character C on another account is denied;\n4. `/questreset` clears only the selected character progress;\n5. restart preserves account access;\n6. reward and final-fight gates remain inaccessible through account access.\n\n## Definition of done\n\nRepository-side implementation is complete when the production-hardening PR is merged with green standard CI and Account Quests MariaDB integration tests. Production rollout is complete after the operator runs the six smoke checks above on the target deployment.\n''',
)

# Remove bootstrap artifacts after applying the patch so the resulting PR contains only product changes.
(ROOT / ".github/workflows/account-quests-bootstrap.yml").unlink(missing_ok=True)
Path(__file__).unlink(missing_ok=True)
