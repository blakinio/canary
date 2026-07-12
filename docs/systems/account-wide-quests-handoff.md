# Account-wide quest access — handoff

Status updated: 2026-07-12

## Goal

Keep quest progress, fight state and cooldowns per character while sharing only permanent location access across characters on the same account. Never copy quest-completion storages to alternate characters.

## Completed scope

The following are implemented on `main` or in the production-hardening batch:

- framework persistence, reward modes and character reset;
- The Ape City;
- The Secret Service;
- In Service of Yalahar;
- The New Frontier;
- Wrath of the Emperor;
- completion-only unlock gates;
- contract validation and MariaDB integration coverage;
- main `config.lua` switch: `accountWideQuestSystemEnabled`;
- god-only `/questaccess [Player Name]` inspection command;
- atomic reward claim through `db.queryAffectedRows`;
- versioned DB migration 62 and fresh-install schema;
- audited quest-id/storage migration CLI.

## Operational commands

```text
/questaccess
/questaccess Player Name
/questreset Player Name, quest-id
```

`/questaccess` shows every persisted account access row, the unlocking character GUID and timestamp. It is god-only.

## Main switch

```lua
accountWideQuestSystemEnabled = true
```

The main switch and `data-otservbr-global/account_quests.lua.enabled` must both be true. Disabling the switch fails closed without deleting access or reward history. Restart after changing it.

## Reward claim safety

`claimReward` no longer performs `SELECT` followed by `INSERT`. It performs one `INSERT IGNORE` through `db.queryAffectedRows`, which executes the statement and reads `mysql_affected_rows()` while holding the same database lock. Exactly one concurrent caller receives `true`; duplicate callers receive `false`.

## Database integration tests

The Account Quests workflow starts a temporary MariaDB 11.4 service and verifies:

- exactly one winner across concurrent reward claims;
- access sharing inside one account and isolation from another account;
- quest-id migration with conflict merging and audit history;
- storage conflict protection and explicit merge policy;
- character storage reset preserving account access and other characters.

## Migration procedure

The tool defaults to dry-run and requires `--apply` to write. Connection variables are `AQ_DB_HOST`, `AQ_DB_PORT`, `AQ_DB_USER`, `AQ_DB_PASSWORD`, and `AQ_DB_NAME`. Take a database backup and stop the game server before storage migration.

Quest ID:

```bash
python tools/account-quests/migrate_account_quests.py quest-id --from old-id --to new-id
python tools/account-quests/migrate_account_quests.py --apply --executed-by operator quest-id --from old-id --to new-id
```

Storage key:

```bash
python tools/account-quests/migrate_account_quests.py storage --from 41950 --to 51950
python tools/account-quests/migrate_account_quests.py --apply --executed-by operator storage --from 41950 --to 51950 --conflict-policy abort
```

Conflict policies:

- `abort` — default and safest; no writes when any player has both keys;
- `keep-target` — discard the old conflicting value;
- `keep-source` — overwrite the target conflicting value;
- `max` — retain the larger value, only for known monotonic progress storages.

Every applied migration writes an `account_quest_migrations` audit row. Quest-ID migration merges existing destination records and retains the earliest unlock/claim timestamp.

## Access boundaries

Still per character by design:

- quest logs and mission storages;
- reward rooms and physical rewards;
- boss/fight state and cooldowns;
- Yalahar final fight and side decision;
- New Frontier Tome-of-Knowledge access and reward door;
- Wrath special teleport states 2/3 and item-dependent behavior.

## Acceptance and deployment

Repository verification consists of standard CI, Account Quests contract tests, a C++ build, and temporary-MariaDB tests. Operators should still perform a short smoke test on their own production-like server because repository CI cannot connect to an external live world:

1. character A completes a quest and records access;
2. character B on the same account can use only shared permanent access;
3. character C on another account is denied;
4. `/questreset` clears only the selected character progress;
5. restart preserves account access;
6. reward and final-fight gates remain inaccessible through account access.

## Definition of done

Repository-side implementation is complete when the production-hardening PR is merged with green standard CI and Account Quests MariaDB integration tests. Production rollout is complete after the operator runs the six smoke checks above on the target deployment.
