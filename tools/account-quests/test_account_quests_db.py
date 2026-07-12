#!/usr/bin/env python3
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
