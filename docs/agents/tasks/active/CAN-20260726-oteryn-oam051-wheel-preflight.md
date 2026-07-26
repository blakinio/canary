---
task_id: CAN-20260726-oteryn-oam051-wheel-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-051
status: validating
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-051b-task-shop-preflight
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "525bfb3f81e11771b215b48f72cfb78b0d4071ac"
risk: high
related_issue: ""
related_pr: "959"
depends_on:
  - OAM-051A durably completed as bd0b58a362d89e449a6863ba299d1c50ad4e6685
blocks:
  - OAM-051B target implementation until this preflight merges
  - OAM-051 final lifecycle and durable reconciliation
  - OAM-052 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
    - docs/agents/OTERYN_OAM_051_WHEEL_OF_DESTINY_REVALIDATION.md
  shared: []
  read_only:
    - data/modules/scripts/taskboard/taskboard.lua
    - src/creatures/players/components/wheel/**
    - src/io/iologindata.cpp
    - src/creatures/players/components/player_storage.*
    - data/XML/storages.xml
    - blakinio/Otheryn
    - blakinio/otclient
---

# OAM-051B Hunting Task Shop preflight

OAM-051 remains `wheel-of-destiny → ADAPT`. Phase A is durably complete. Phase B is limited to the Hunting Task Shop Bonus Promotion contract. Exact Otheryn persistence and maintained-client parser evidence now resolves the preflight blockers and permits a bounded target server-and-tests task after this PR merges.

## Accepted candidate boundary

The accepted donor behavior from Canary PR #230 is limited to:

- one Bonus Promotion offer in the Task Shop;
- purchased points `0..50` with next-point display values `1..51`;
- cost `100 * (1 + n * (n - 1) / 2)` for next point `n`;
- Hunting Task Point mutation;
- Wheel extra-point accounting;
- current Taskboard packet handling;
- focused malformed-request, insufficient-balance, cap, persistence, duplicate and relog validation.

Generated Lua API documents and Canary-only Python validators are not migrated. The donor patch is not copied wholesale.

## Accepted transaction contract

The donor KV sequence is rejected. Otheryn source proves:

- `Player::useTaskHuntingPoints()` mutates the in-memory Task Hunting balance;
- `savePlayerTaskHuntingClass()` persists that balance inside `DBTransaction::executeWithinTransaction(savePlayerGuard)`;
- player storages are persisted inside the same SQL transaction;
- Wheel KV is deliberately staged only after the SQL transaction commits and is therefore a separate persistence domain.

The target must reserve `wheel.hunting_task_shop_points` as key `6` in the existing `1000000..2000000` Wheel storage range and persist the purchased count through SQL-backed `PlayerStorage`, not Wheel KV.

One bounded player operation must validate offer id, current cost, balance and cap before mutation, then update the Task Hunting balance and storage-backed count together. Any in-process failure restores both in-memory values. A crash before save loses both; a SQL save failure rolls back both; a successful SQL commit persists both. Duplicate/replayed requests re-evaluate current state and cannot use a stale lower cost or exceed 50.

Required target failure cells are mutation rejection, malformed/truncated/trailing request, wrong offer id, insufficient balance, cap, in-memory rollback, SQL save failure, interrupted save/relog, duplicate replay and successful save/relog.

## Accepted maintained-client wire contract

Maintained-client baseline: `blakinio/otclient@ce4329ee13b39576915240605c2fe6657096c517`.

Exact server payload:

```text
0x5B, U8 subtype=0x02, U8 offers_count,
U8 offer_type=0x04, U16 purchased_display_value,
U32 next_cost, U8 status
```

The parser derives purchased count as `max(display_value - 1, 0)`. Exact status values are available `0x00`, not enough points `0x02` and bought `0x04`; zero next cost also renders bought. The bounded buy request is client opcode `0x5F`, action `0x0B`, one `U16` offer id, with Bonus Promotion offer id `0`.

The baseline C++ parser consumes the payload and dispatches `g_game.onTaskHuntingShopData`, so the target package is server-first-safe at the wire level. The baseline does not ship a complete controller-owned `modules/game_taskboard` UI consumer. Therefore the Otheryn package may claim packet compatibility but must not claim a visible or operable maintained-client Taskboard UI. Any such UI is a separate `OTS-*` cross-repository milestone and is not part of OAM-051B.

## Authorized target package

After this preflight merges, a fresh Otheryn task may own only:

- `data/XML/storages.xml` for the named storage reservation;
- the smallest Player/PlayerWheel/Lua or Taskboard paths needed for one atomic purchase operation and response;
- focused unit, persistence/failure and source-contract tests;
- the OAM-051B target task/report lifecycle.

The target task must search current ownership and open PRs again, start from current Otheryn `main`, publish a draft PR early and run exact-head affected CI plus Required. Physical official-client evidence remains a final acceptance cell when available; static fixtures do not replace it.

## Preserved exclusions

- no maintained-client UI or assets;
- no Bounty or Weekly implementation;
- no other Task Shop offer;
- no Wheel balance, combat effect, spell, stance, area or geometry changes;
- no legacy parser transfer;
- no schema migration, map, deployment or production action.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T14:35:00+02:00
head: 525bfb3f81e11771b215b48f72cfb78b0d4071ac
branch: dudantas/oam-051b-task-shop-preflight
pr: 959
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - real-tibia-parity
  - protocol
  - player-persistence
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
  - docs/agents/OTERYN_OAM_051_WHEEL_OF_DESTINY_REVALIDATION.md
proven:
  - Canary current main is ec0d815570415a4c7ca7217e3e2aca41f6023dab.
  - Otheryn current main is 38bb62192d25984d63f96c2637348b4adc82f6cd.
  - Maintained-client baseline is ce4329ee13b39576915240605c2fe6657096c517.
  - OAM-051A is durably complete through Otheryn lifecycle merge bd0b58a362d89e449a6863ba299d1c50ad4e6685 and Canary governance merge d8416553be77d4999d81afcce2399a37a25337a6.
  - Canary PR 230 is a bounded candidate donor, not a complete target patch.
  - Otheryn Task Hunting points and PlayerStorage persist inside one player SQL transaction.
  - Otheryn Wheel KV persists after SQL commit in a separate domain and cannot provide atomic purchase durability with Task Hunting points.
  - The existing Wheel storage range 1000000..2000000 has keys 1..5 assigned and key 6 available for wheel.hunting_task_shop_points.
  - Maintained OTClient parses Bonus Promotion as U8 type 4, U16 display value, U32 cost and U8 status.
  - Maintained OTClient derives purchased count as display value minus one and defines statuses 0, 2 and 4 for available, insufficient and bought.
  - Maintained OTClient has the exact Taskboard parser callback but no complete shipped controller-owned Taskboard UI module.
  - The accepted rollout is server-first-safe for parsing, with no maintained-client UI claim.
derived:
  - SQL-backed PlayerStorage is the smallest existing target persistence domain that can commit the purchased count atomically with Task Hunting state without a schema migration.
  - A bounded Otheryn server-and-tests branch may start after this preflight merges.
  - A complete maintained-client Taskboard experience requires a separate OTS cross-repository task but does not block wire-compatible server-first delivery.
unknown:
  - Exact final-head CI and ownership result after this checkpoint commit.
  - Physical official-client acceptance result for the future Otheryn implementation.
conflicts: []
first_failure:
  marker: none
  evidence: The contract blockers are resolved; only exact-final-head preflight validation remains.
rejected_hypotheses:
  - Copy PR 230 wholesale.
  - Persist purchased points in Wheel KV.
  - Treat Lua/KV success in one process as durable atomic purchase proof.
  - Require an OTClient source change merely to consume the already-supported packet.
  - Claim maintained-client Taskboard UI availability from the C++ parser alone.
  - Expand OAM-051B into balance, effects, stances, spells or geometry.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
  - docs/agents/OTERYN_OAM_051_WHEEL_OF_DESTINY_REVALIDATION.md
validation:
  - command: exact Otheryn persistence-boundary review
    result: PASS
    evidence: Task Hunting and PlayerStorage are inside savePlayerGuard SQL transaction; Wheel KV is staged after commit.
  - command: exact maintained-client Task Shop parser review
    result: PASS
    evidence: field order, widths, purchased-count derivation, offer/status enums and callback dispatch are source-proven at ce4329ee13b39576915240605c2fe6657096c517.
  - command: target storage reservation review
    result: PASS
    evidence: wheel storage range 1000000..2000000 currently reserves keys 1..5; key 6 is unassigned.
blockers: []
next_action: Require Agent Task Ownership and CI to pass on the exact final head, recheck changed paths, discussions and mergeability, then squash-merge PR 959 and start the bounded Otheryn OAM-051B target task from current main.
```
