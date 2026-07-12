# Account-wide quest access — handoff

Status updated: 2026-07-12

## Goal

Keep quest progress, fight state and cooldowns per character while sharing only permanent location access across every character on the same account. Never copy quest-completion storages to alternate characters. Rewards remain controlled by `rewardMode` and their original quest scripts.

## Merged implementation

The first planned five-quest batch is merged to `main`.

Merged PRs:

- PR #31: framework, persistence, reward modes and character reset;
- PR #37: The Ape City;
- PR #39: The Secret Service;
- PR #42: formatting cleanup;
- PR #53: registered-ID checks, correct quest counting, completion-only unlocks and contract validation;
- PR #113: In Service of Yalahar, The New Frontier, Wrath of the Emperor, validators and this handoff.

Implemented quests:

- The Ape City;
- The Secret Service;
- In Service of Yalahar;
- The New Frontier;
- Wrath of the Emperor.

Core files:

```text
data-otservbr-global/account_quests.lua
data-otservbr-global/scripts/custom/account_quest_system.lua
data/scripts/actions/doors/quest_door.lua
tools/account-quests/validate_account_quests.py
tools/account-quests/test_validate_account_quests.py
```

## Current status

The location-access scope of the first batch is complete and merged. CI and the dedicated Account Quests workflow passed for PR #113.

The implementation currently provides:

- account-wide permanent location access for the five configured quests;
- completion-only unlock gates;
- per-character mission progress, fight state and special cooldown/state storages;
- per-character quest reset that preserves account access and reward history;
- contract validation for configured quest IDs and forbidden reward/fight sharing.

## Quest boundaries

### In Service of Yalahar

Shared after completion:

- confirmed ordinary location doors for the quest areas.

Completion gate:

- `DoorToReward` records account completion but is not itself shared.

Kept per character:

- final-fight door and teleport;
- reward room;
- Matrix reward;
- side decision;
- rewards and mission progress.

### The New Frontier

Shared after completion:

- confirmed ordinary mission doors;
- arena access;
- final Magic Carpet access.

Completion gate:

- `Mission10.MagicCarpetDoor`, awarded only after the final report to Ongulf.

Kept per character or separate progression:

- Mission09 reward door;
- potion/gold-ingot/pig-bank rewards;
- Tome of Knowledge counter;
- Zao Palace doors;
- Snake Head teleport;
- Corruption Hole.

Tome-based access must not be inferred from completing The New Frontier.

### Wrath of the Emperor

Shared after completion:

- confirmed ordinary quest doors;
- the normal A/B route of the quest teleport network.

Completion gate:

- Mission12 records account completion but the reward stage is not shared.

Kept per character:

- reward chests 43034–43036;
- special teleport states 2 and 3;
- item-dependent teleport behaviour;
- current fight state and rewards.

A character's own teleport storage always takes priority. Account access is only the fallback when no character-specific access exists.

## Reset boundaries

Configured progress reset intentionally excludes:

- New Frontier rewards and Tome-of-Knowledge access;
- Wrath reward chests;
- unrelated global state;
- account access and account reward history.

## Remaining required work

### 1. Make reward claiming atomic

`AccountQuest.claimReward` still performs:

```text
canClaimReward -> INSERT IGNORE
```

Two concurrent calls may both pass the initial read. The reward subsystem should not be considered fully production-hardened until the claim is atomic.

Required approach:

1. confirm Canary's DB affected-row semantics or locate an established atomic-claim pattern;
2. replace the read-then-insert flow with one authoritative reservation/insert operation;
3. grant the physical reward only after the reservation succeeds;
4. add a regression test for duplicate concurrent claims.

Do not implement this by guessing the return semantics of `db.query()`.

### 2. Run live-server acceptance tests

Automated contract validation passed, but the following still require an actual test server:

- character A: quest completed and account access recorded;
- character B: same account, no completion storage, receives only permitted location access;
- character C: different account, receives no access;
- `/questreset` for all five quest IDs;
- reward rooms and final-fight gates remain inaccessible through account access alone;
- account access survives logout, restart and character reset.

These tests are deployment verification, not missing implementation code.

## Optional improvements

These are not blockers for the completed first batch:

- add a top-level `config.lua`/`config.lua.dist` switch in addition to `account_quests.lua.enabled`;
- add more quests using the same opt-in integration model;
- add integration tests backed by a disposable database;
- add administrator inspection commands for account access and reward rows;
- document a migration strategy if quest IDs or storage mappings change.

## Contract validation

The validator must continue to enforce:

- every integrated quest ID is configured;
- only explicit completion gates unlock account access;
- Yalahar final fight is not shared;
- New Frontier reward door is not shared;
- Wrath Mission12 reward stage is not shared;
- ordinary early doors never unlock a whole quest.

## Definition of done

### First five-quest access batch

Complete and merged.

### Full production-hardening

Complete only when:

- reward claiming is atomic;
- live A/B/C and reset tests pass;
- no reward or fight gate is reachable through shared access;
- this document reflects the verified deployment state.
