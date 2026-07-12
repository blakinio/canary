#!/usr/bin/env python3
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
