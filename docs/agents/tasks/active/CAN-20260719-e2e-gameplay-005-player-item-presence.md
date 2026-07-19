---
task_id: CAN-20260719-e2e-gameplay-005-player-item-presence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-player-item-presence
base_branch: main
created: 2026-07-19T13:58:00+02:00
updated: 2026-07-19T14:12:00+02:00
last_verified_commit: "10a9e6b0594c8dc5980bf8cf896b17f8f0709df8"
risk: medium
related_issue: ""
related_pr: "586"
depends_on:
  - merged PR #583 typed player_storage persistence assertions
  - existing Universal Physical E2E two-session lifecycle
blocks:
  - feature-owned item/depot/inbox scenarios requiring typed durable item-presence assertions
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-item-presence.md
    - tests/e2e/test_player_item_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tools/e2e/run_physical_e2e.sh
    - tests/e2e/test_persistence_assertions.py
    - tests/e2e/test_player_storage_persistence.py
    - docs/agents/CHANGELOG.md
    - .github/workflows/**
    - schema.sql
    - src/io/iologindata.cpp
    - src/io/functions/iologindata_save_player.cpp
    - src/io/functions/iologindata_load_player.cpp
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
modules_touched:
  - Universal OTS E2E physical gameplay persistence assertions
reuses:
  - existing post-cycle scalar SQL assertion evaluator
  - existing two-session physical login/logout/relog lifecycle
  - existing scenario.assertions.persistence contract
public_interfaces:
  - persistence assertion type player_item_presence
cross_repo_tasks: []
---

# Goal

Extend the existing feature-neutral `scenario.assertions.persistence` contract with a bounded typed `player_item_presence` assertion for durable inventory, depot and inbox item rows without exposing arbitrary SQL, interpreting serialized `count` as universal item quantity, or depending on OTBM routing.

The assertion deliberately proves only database row presence/absence by exact item type in one fixed location table after the full physical two-session lifecycle. Feature scenarios own the action that creates/removes the item and any stronger client-visible outcome.

# Acceptance criteria

- [x] Add `player_item_presence` checks with exact `location`, `item_id` and `present` fields.
- [x] Support only fixed locations `inventory`, `depot`, and `inbox`, mapped internally to `player_items`, `player_depotitems`, and `player_inboxitems`.
- [x] Validate `item_id` in the uint16 range used by the current item loader and existing E2E item action boundary.
- [x] Compile only fixed-shape semicolon-free scalar `EXISTS` / `NOT EXISTS` queries joined to the fixture player by exact character name.
- [x] Do not expose caller-controlled table names, columns, predicates, `pid`, `sid`, or SQL fragments.
- [x] Do not infer item quantity from the persisted `count` column because the saver writes `item->getSubType()`, whose meaning depends on item type.
- [x] Keep `player_field` as the only current phase-two controlled-client typed persistence check; item presence remains database-only for one consistent inventory/depot/inbox contract.
- [x] Add focused compiler and manifest/Lua-plan integration tests covering all locations, presence/absence, invalid locations/IDs and mixed typed checks.
- [x] Document the database-only item-presence boundary and feature-owned stronger assertions.
- [x] Keep feature-specific item IDs and expected presence out of shared fixtures.
- [x] Apply `ci:final-gate` before the final checkpoint commit.
- [ ] Require exact-final-head Ownership, CI and Universal Agent E2E success before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T14:12:00+02:00
head: 10a9e6b0594c8dc5980bf8cf896b17f8f0709df8
branch: feat/e2e-gameplay-005-player-item-presence
pr: 586
status: validating
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-item-presence.md
  - tests/e2e/test_player_item_persistence.py
  - tools/e2e/persistence_assertions.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is bbf6e8d6c8f02129b196bc229cca66cebabf86e6 and includes merged PR #580 and PR #583
  - draft PR 586 owns branch feat/e2e-gameplay-005-player-item-presence
  - no open PR matched player item inventory/depot/inbox typed persistence ownership at task start
  - existing merged PR #583 task claims overlapping persistence compiler/documentation paths as shared, not exclusive
  - ownership validation enforces conflicts only between active exclusive claims
  - current schema has separate player_items, player_depotitems and player_inboxitems tables with player_id, sid, pid, itemtype, count and attributes
  - current savePlayerGuard invokes inventory, depot and inbox persistence paths in the canonical player-save transaction
  - current saveItems writes item->getID() to itemtype and item->getSubType() to count for both top-level and nested serialized rows
  - current loadItems reads itemtype and count as uint16 and reconstructs items with Item::CreateItem(type, count)
  - existing E2E item action validation requires positive uint16 item IDs, matching the new 1..65535 persistence assertion range
  - player_item_presence validation supports only inventory, depot and inbox and maps them internally to fixed persistence tables
  - fixed-shape EXISTS and NOT EXISTS SQL compilation accepts no caller-selected table, column, pid, sid, predicate or SQL fragment
  - mixed-contract focused tests prove player_field remains the only phase-two Lua check while player_storage and player_item_presence compile to post-cycle SQL
  - CI run 29686234981 succeeded and Agent Task Ownership run 29686234869 succeeded on implementation/documentation head 81c101bdcebda21a48fae56cdfe60ce287416a6f
  - MODULE_CATALOG patch audit contains exactly one intended Universal OTS E2E row update
  - canonical PHYSICAL_GAMEPLAY_ACTION_PLANS documentation defines database-only item presence, fixed locations, no generic quantity semantics and feature-owned stronger assertions
  - no feature-specific item ID or expected presence was added to shared scenario fixtures
  - ci:final-gate was applied to PR 586 before this final checkpoint commit
derived:
  - a location-to-fixed-table EXISTS/NOT EXISTS assertion proves durable serialized item-row presence without interpreting pid/sid hierarchy or subtype/count semantics
  - one database-only contract across inventory, depot and inbox avoids claiming a uniform controlled-client getter that does not exist for all three locations
unknown:
  - exact-final-head workflow conclusions after this final checkpoint
conflicts: []
first_failure:
  marker: ownership_related_pr_mismatch
  evidence: Agent Task Ownership run 29686089142 failed on the initial PR head because related_pr was empty before PR 586 was bound; the focused tooling/tests passed and the task was immediately corrected to related_pr 586
rejected_hypotheses:
  - summing persisted count as a generic inventory quantity
  - exposing pid/sid hierarchy as a stable feature assertion surface
  - caller-selected SQL table names or arbitrary SQL
  - inventing shared fixture item IDs only to force a physical assertion
  - modifying route execution or OTBM tooling
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-item-presence.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_player_item_persistence.py
  - tools/e2e/persistence_assertions.py
validation:
  - command: Agent Task Ownership run 29686089142
    result: FAIL
    evidence: initial task-to-PR binding was empty before PR 586 was recorded
  - command: CI run 29686234981
    result: PASS
    evidence: repository CI succeeded on implementation/documentation head 81c101bdcebda21a48fae56cdfe60ce287416a6f
  - command: Agent Task Ownership run 29686234869
    result: PASS
    evidence: corrected ownership/task binding validated successfully
  - command: PR #586 MODULE_CATALOG patch audit
    result: PASS
    evidence: patch contains only the intended Universal OTS E2E row update
  - command: ci:final-gate label
    result: PASS
    evidence: label applied before final checkpoint commit
blockers: []
next_action: Make no further commits. Mark PR ready and require exact-final-head Ownership, CI and Universal Agent E2E success plus clean review/merge state before squash merge.
```
