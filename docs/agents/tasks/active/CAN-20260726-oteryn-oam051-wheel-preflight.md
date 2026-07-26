---
task_id: CAN-20260726-oteryn-oam051-wheel-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-051
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-051b-task-shop-preflight
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "d8416553be77d4999d81afcce2399a37a25337a6"
risk: high
related_issue: ""
related_pr: "959"
depends_on:
  - OAM-051A durably completed as bd0b58a362d89e449a6863ba299d1c50ad4e6685
blocks:
  - OAM-051B target implementation
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
    - src/lua/functions/creatures/player/player_functions.*
    - tests/unit/players/**
    - blakinio/Otheryn
    - blakinio/otclient
---

# OAM-051B Hunting Task Shop preflight

OAM-051 remains `wheel-of-destiny → ADAPT`. Phase A is durably complete. Phase B is limited to the Hunting Task Shop Bonus Promotion contract and is not yet authorized for target implementation.

## Candidate boundary

Candidate donor behavior from Canary PR #230 is limited to:

- one Bonus Promotion offer in the Task Shop;
- points 1 through 50 with cost `100 * (1 + n * (n - 1) / 2)`;
- bounded purchased-point state under `wheel-of-destiny/hunting-task-shop-points`;
- Wheel extra-point accounting and current-client payload field;
- one Player Lua binding used by the Taskboard script;
- focused validation for malformed requests, insufficient balance, cap, load and relog.

Generated Lua API documents and Canary-only Python validators are not migrated.

## Transaction contract required before target writes

The legacy sequence removes Hunting Task Points before writing Wheel KV. That sequence does not prove atomic durable purchase behavior. The target package must choose and test one explicit model:

1. rollback the resource mutation when Wheel-state persistence fails; or
2. stage a recoverable purchase intent that is replayed or compensated after relog; or
3. use an existing target transaction boundary proven to cover both mutations.

A target PR must not claim durability from in-memory success alone. Required failure cells include mutation rejection, KV write failure, interrupted save/relog, duplicate replay and already-at-cap state.

## Maintained-client contract required before target writes

Current maintained client baseline is `blakinio/otclient@ce4329ee13b39576915240605c2fe6657096c517`. Repository search did not isolate an authoritative parser/UI interpretation for the Task Shop Wheel field. Before target implementation, evidence must identify:

- exact server packet field order and width;
- whether the client derives purchased count as `value - 1`;
- status values for available, insufficient points and bought;
- behavior at point 50 and after relog;
- whether server-only delivery is compatible or a separately authorized client change is required.

Static donor comments are not sufficient. Exact source or physical-client evidence is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T11:10:00+02:00
head: d8416553be77d4999d81afcce2399a37a25337a6
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
  - Canary OAM-051A governance merged as d8416553be77d4999d81afcce2399a37a25337a6.
  - Otheryn main after OAM-051A lifecycle is bd0b58a362d89e449a6863ba299d1c50ad4e6685.
  - Maintained-client main is ce4329ee13b39576915240605c2fe6657096c517.
  - Current Otheryn still lacks the bounded Task Shop Bonus Promotion package.
  - Canary PR 230 is a candidate donor, not a complete transaction or interoperability proof.
  - The donor removes Hunting Task Points before persisting purchased Wheel points.
  - No exact maintained-client Task Shop field interpretation was isolated by repository search.
derived:
  - OAM-051B remains blocked for contract evidence and must not start target source changes yet.
  - The smallest safe target package is server plus tests only if exact maintained-client evidence proves wire compatibility.
  - Any necessary client mutation requires separate repository ownership and a cross-repository rollout contract.
unknown:
  - Exact maintained-client parser/UI interpretation for the Bonus Promotion field.
  - Exact failure-safe transaction model for resource and Wheel-state persistence.
  - Exact target failure-injection seam and physical-client scenario.
conflicts: []
first_failure:
  marker: task-shop-contract-evidence-incomplete
  result: BLOCKED_FOR_PREFLIGHT
  evidence: neither exact client interpretation nor cross-resource durability is proven
rejected_hypotheses:
  - Copy PR 230 wholesale.
  - Treat Lua/KV success in one process as durable atomic purchase proof.
  - Modify OTClient without proving a client change is required.
  - Expand OAM-051B into balance, effects, stances, spells or geometry.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
  - docs/agents/OTERYN_OAM_051_WHEEL_OF_DESTINY_REVALIDATION.md
validation:
  - command: fresh Canary Otheryn and maintained-client baseline review
    result: PASS
    evidence: exact current heads recorded after durable OAM-051A governance
  - command: donor transaction-sequence review
    result: PASS
    evidence: resource mutation precedes Wheel KV update and therefore requires a new failure contract
  - command: maintained-client parser/UI proof
    result: BLOCKED
    evidence: repository search did not isolate authoritative interpretation; exact source or physical evidence is still required
blockers:
  - exact maintained-client Task Shop field proof
  - explicit target durability and failure-recovery model
  - deterministic failure-injection and relog validation plan
next_action: Identify the exact maintained-client Task Shop parser/UI field semantics and define a tested rollback or recoverable-staging transaction model before opening any Otheryn OAM-051B source branch.
```
