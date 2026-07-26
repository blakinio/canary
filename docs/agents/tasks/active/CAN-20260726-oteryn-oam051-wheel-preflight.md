---
task_id: CAN-20260726-oteryn-oam051-wheel-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-051
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-051a-wheel-governance
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "477a3b9b6938e4777ec0df5b2b38ef021b60ece1"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - OAM-050 durably completed as d0c76c6f964a5266789b252173eb24832a309e80
blocks:
  - OAM-051B Hunting Task Shop contract and target adaptation
  - OAM-051 final governance, lifecycle and durable reconciliation
  - OAM-052 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
    - docs/agents/OTERYN_OAM_051_WHEEL_OF_DESTINY_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/real-tibia/registry/modules/wheel-of-destiny.yaml
    - docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
    - src/creatures/players/components/wheel/**
    - src/io/io_wheel.*
    - src/server/network/protocol/protocolgame.*
    - src/creatures/combat/**
    - data/scripts/spells/**
    - data/modules/scripts/taskboard/**
    - tests/unit/players/**
    - tests/integration/**
    - blakinio/Otheryn
    - blakinio/otclient
    - opentibiabr/canary
    - zimbadev/crystalserver
---

# OAM-051 Wheel of Destiny governance

Current disposition: `wheel-of-destiny → ADAPT`.

OAM-051 remains active and decomposed. OAM-051A is durably complete in Otheryn as the bounded server-side safety and state-integrity adaptation selected by preflight PR #951. OAM-051B remains pending for the separately client- and persistence-coupled Hunting Task Shop Bonus Promotion contract. The complete Wheel subsystem must not be bulk-copied, and deferred current-balance or gameplay-parity behavior remains outside OAM migration permission.

## Phase ledger

### OAM-051A — completed

Delivered target boundary:

- atomic allocation proposal validation before mutation;
- temple-only decrease enforcement;
- saturating point accounting;
- safe gem, grade, index, affinity and persisted-state handling;
- permanent point-source load ordering;
- current-protocol malformed-input rejection without wire-shape changes;
- focused deterministic tests.

Exact target evidence:

- feature head `1f4ce3c11f6acf292775daac886e9dace7e8280f`;
- autofix `30193154587` success;
- full CI `30193154684` success;
- Required `30193154608` success;
- feature merge `47863ce250bce73c1b9af3077f82e9bf6e99e3d1`;
- lifecycle head `299b85cddd61dc24054becc33a9188d4c2e38c99`;
- lifecycle Required `30193946125` success;
- lifecycle merge `bd0b58a362d89e449a6863ba299d1c50ad4e6685`.

### OAM-051B — pending bounded contract

Candidate behavior roots from Canary PR #230:

- `data/modules/scripts/taskboard/taskboard.lua`;
- selected `player_wheel.cpp/.hpp` state, load, payload and accounting additions;
- selected `player_functions.cpp/.hpp` Lua binding additions;
- focused target tests.

Required before target implementation:

- exact maintained-client field and UI interpretation proof;
- 1 through 50 purchase-cost contract;
- invalid offer, insufficient points and cap behavior;
- KV clamp/load/relog proof;
- explicit resource-mutation versus persisted-Wheel transaction/failure semantics;
- decision whether rollback, recoverable staging or another bounded durability model is required.

Generated `docs/lua-api/*` remain generated outputs. Canary validation scripts remain evidence tooling and are not migrated.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T10:35:00+02:00
head: e4a29ce11ca4bc68d4dfa81595dabf46e2961c71
branch: dudantas/oam-051a-wheel-governance
pr: null
status: implementing
context_routes:
  - agent-governance
  - cross-repo
  - real-tibia-parity
  - protocol
  - player-persistence
  - github-actions
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
  - docs/agents/OTERYN_OAM_051_WHEEL_OF_DESTINY_REVALIDATION.md
proven:
  - Canary OAM-051 preflight PR 951 merged as a4a35495d4a8dc047bd3315b95c9fb577ac597af.
  - Current Canary governance base is 477a3b9b6938e4777ec0df5b2b38ef021b60ece1.
  - Current Otheryn main is bd0b58a362d89e449a6863ba299d1c50ad4e6685.
  - No open Canary PR claims OAM-051 or Wheel migration paths.
  - OAM-051A feature PR 115 passed exact-head autofix 30193154587, full CI 30193154684 and Required 30193154608 and merged as 47863ce250bce73c1b9af3077f82e9bf6e99e3d1.
  - Full target CI included Fast Checks, Lua, Linux debug/release, all C++ tests, schema import, Canary and Global runtime smoke, macOS, Windows CMake, Windows Solution and Docker validation.
  - Feature PR 115 changed exactly eight implementation/test paths plus task and report and had no discussion or review blockers.
  - Otheryn lifecycle PR 118 changed only active/archive/report documentation, passed Required 30193946125 on exact head 299b85cddd61dc24054becc33a9188d4c2e38c99 and merged as bd0b58a362d89e449a6863ba299d1c50ad4e6685.
  - OAM-051A preserved Task Shop, WheelBalance, full-resonance, combat-effect, spell-area, legacy game-parser and client exclusions.
  - Historical Supreme Grade II value 12000000 remained unchanged.
  - Current Canary PR 230 proves a bounded Task Shop candidate but removes Hunting Task Points before writing Wheel KV.
derived:
  - OAM-051A is durably complete, but the parent OAM-051 task must remain active until the separately declared OAM-051B boundary is classified and delivered or explicitly rejected.
  - OAM-051B requires a fresh transaction and maintained-client contract preflight before any target source branch.
  - OAM-051A validation of existing packet shapes does not prove Task Shop payload interoperability.
  - Deferred balance, critical-healing, stance, replacement-spell and geometry work remains Wheel parity work, not an automatic OAM-051B scope expansion.
unknown:
  - Whether current maintained OTClient interprets the PR 230 Task Shop field exactly as assumed under physical runtime proof.
  - Whether a durable Task Shop purchase requires rollback, recoverable staging or another explicit failure model across Hunting Task Points and Wheel KV.
  - Exact target test seam for failure injection and relog proof.
  - Current authoritative behavior for deferred Wheel balance and gameplay-parity packages.
conflicts: []
first_failure:
  marker: task-shop-transaction-contract-unproven
  command: current Canary PR 230 purchase-sequence review
  result: BLOCKED_FOR_PREFLIGHT
  evidence: the candidate removes Hunting Task Points before persisting the purchased Wheel point; no exact rollback or recoverability proof has yet been established for Otheryn
rejected_hypotheses:
  - Archive OAM-051 after only OAM-051A despite the preflight-declared second package.
  - Bulk-copy Canary PR 230 or the complete Wheel subsystem.
  - Claim atomic Task Shop durability from the current donor sequence.
  - Include current-balance, effect, stance, replacement-spell or geometry changes in OAM-051B.
  - Modify OTClient before an exact cross-repository contract proves that a client change is necessary.
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam051-wheel-preflight.md
  - docs/agents/OTERYN_OAM_051_WHEEL_OF_DESTINY_REVALIDATION.md
validation:
  - command: OAM-051A target feature and lifecycle evidence reconciliation
    result: PASS
    evidence: exact feature/lifecycle heads, runs, paths, audits and merge commits are recorded
  - command: OAM-051A exclusion reconciliation
    result: PASS
    evidence: target report and merged diff retain every preflight exclusion
  - command: OAM-051 parent lifecycle decision
    result: PASS
    evidence: parent remains active because OAM-051B was explicitly declared by preflight and is not yet classified
  - command: Canary governance exact-head Ownership and CI
    result: NOT_RUN
    evidence: governance PR has not yet been opened and synchronized
blockers:
  - Canary governance exact-head Ownership and CI
  - clean governance discussion and Canary-main drift audit
next_action: Merge the OAM-051A governance checkpoint after exact-head gates, then perform a fresh OAM-051B Task Shop transaction and maintained-client contract preflight before any target source change.
```
