# Account-wide quest access — handoff

Status updated: 2026-07-12

## Goal

Keep quest progress, fight state and cooldowns per character while sharing only permanent location access across every character on the same account. Never copy quest-completion storages to alternate characters. Rewards remain controlled by `rewardMode` and their original quest scripts.

## Existing merged foundation

- PR #31: framework, persistence, reward modes and character reset;
- PR #37: The Ape City;
- PR #39: The Secret Service;
- PR #42: formatting cleanup;
- PR #53: registered-ID checks, correct quest counting, completion-only unlocks and contract validation.

Core files:

```text
data-otservbr-global/account_quests.lua
data-otservbr-global/scripts/custom/account_quest_system.lua
data/scripts/actions/doors/quest_door.lua
tools/account-quests/validate_account_quests.py
tools/account-quests/test_validate_account_quests.py
```

## Current branch

```text
feature/account-wide-legacy-quest-access
```

This branch completes the first planned five-quest batch by adding:

- In Service of Yalahar;
- The New Frontier;
- Wrath of the Emperor.

## In Service of Yalahar

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

## The New Frontier

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

## Wrath of the Emperor

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

Configured progress reset includes mission and helper storages for the three quests. It intentionally excludes:

- New Frontier rewards and Tome-of-Knowledge access;
- Wrath reward chests;
- unrelated global state;
- account access and account reward history.

## Contract validation

The validator must continue to enforce:

- every integrated quest ID is configured;
- only explicit completion gates unlock account access;
- Yalahar final fight is not shared;
- New Frontier reward door is not shared;
- Wrath Mission12 reward stage is not shared;
- ordinary early doors never unlock a whole quest.

## Remaining before merge

1. Run Stylua and the account-quests validator in CI.
2. Fix every CI failure before merge.
3. Test with three characters:
   - A: completed quest;
   - B: same account, no completion storage;
   - C: different account.
4. Verify `/questreset` for all three new quest IDs.
5. Confirm reward and fight scripts do not become reachable through shared access.
6. Merge only after green CI.

## Known framework follow-up

`AccountQuest.claimReward` still uses a `canClaimReward` query followed by `INSERT IGNORE`. Two concurrent calls may both pass the initial read. Before changing this, verify Canary's DB affected-row semantics or find an established atomic-claim pattern in the repository. This does not block location access, but it prevents calling the reward subsystem fully production-hardened.

## Definition of done

The first batch is complete only when all five quests are on `main`, CI is green, A/B/C access tests pass, reset tests pass, no reward/fight gate is shared unintentionally, and this document reflects the merged state.
