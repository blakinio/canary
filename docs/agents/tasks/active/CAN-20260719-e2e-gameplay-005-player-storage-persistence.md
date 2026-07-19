---
task_id: CAN-20260719-e2e-gameplay-005-player-storage-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-player-storage-persistence
base_branch: main
created: 2026-07-19T13:00:00+02:00
updated: 2026-07-19T13:08:00+02:00
last_verified_commit: "ae6a2667da52b8671435a293f12a9f4386010606"
risk: medium
related_issue: ""
related_pr: "583"
depends_on:
  - merged PR #565 typed player_field persistence assertions
  - existing Universal Physical E2E two-session lifecycle
blocks:
  - feature-owned quest scenarios requiring typed durable player storage assertions
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-storage-persistence.md
    - tests/e2e/test_player_storage_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/test_persistence_assertions.py
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/client/agent_e2e_scenario.lua
    - tools/e2e/run_physical_e2e.sh
    - .github/workflows/**
    - schema.sql
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
modules_touched:
  - Universal OTS E2E physical gameplay persistence assertions
reuses:
  - existing post-cycle scalar SQL assertion evaluator
  - existing two-session physical login/logout/relog lifecycle
  - existing scenario.assertions.persistence contract
public_interfaces:
  - persistence assertion type player_storage
cross_repo_tasks: []
---

# Goal

Extend the existing feature-neutral `scenario.assertions.persistence` contract with a bounded typed `player_storage` assertion for durable Canary `player_storage` rows without introducing arbitrary SQL, feature-specific storage IDs, a second E2E runner, or any routing dependency.

`player_storage` is intentionally a post-cycle database persistence assertion. Unlike directly comparable `player_field` values, arbitrary server-side storage values are not exposed as a generic trustworthy controlled-OTClient read surface, so they must not be fabricated as phase-two client checks.

# Acceptance criteria

- [x] Add `player_storage` persistence checks with exact `key` and `equals` integers.
- [x] Validate storage keys against the current schema `INT(10) UNSIGNED` range.
- [x] Validate storage values against the current schema signed `INT(11)` range.
- [x] Compile only fixed-shape semicolon-free scalar SELECT statements joining `player_storage` to the fixture player by exact character name.
- [x] Preserve `player_field` phase-two controlled-client checks unchanged.
- [x] Exclude `player_storage` from generated phase-two client checks rather than pretending arbitrary storage is client-readable.
- [x] Reject unknown fields/types and duplicate assertion IDs fail-closed.
- [x] Add focused compiler and manifest/Lua-plan integration tests, including mixed `player_field` + `player_storage` checks.
- [ ] Document the database-only verification boundary for `player_storage`.
- [x] Keep feature-specific storage keys and expected values in feature scenario manifests; do not add invented shared fixture storage IDs.
- [ ] Apply `ci:final-gate` before the final checkpoint commit.
- [ ] Require exact-final-head Ownership, CI and Universal Agent E2E success before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T13:08:00+02:00
head: ae6a2667da52b8671435a293f12a9f4386010606
branch: feat/e2e-gameplay-005-player-storage-persistence
pr: 583
status: implementing
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-storage-persistence.md
  - tools/e2e/persistence_assertions.py
  - tests/e2e/test_player_storage_persistence.py
  - tools/e2e/run_agent_e2e.py
  - tests/e2e/test_persistence_assertions.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - live main at task start is 7b517aec1dfe9e89befc68a53d7aece383098623
  - draft PR 583 owns branch feat/e2e-gameplay-005-player-storage-persistence
  - no open PR matched E2E-GAMEPLAY-005 player_storage persistence ownership at task start
  - PR #565 merged the existing typed player_field persistence contract for level and experience
  - current schema defines player_storage.key as int(10) unsigned and player_storage.value as signed int(11)
  - E2E roadmap explicitly allows persistence assertion work to proceed independently of OTBM route planning
  - PR #580 owns OTBM-E2E-001B and does not touch tools/e2e paths
  - player_storage validation and fixed-shape SQL compilation are implemented on ae6a2667da52b8671435a293f12a9f4386010606
  - mixed-contract focused tests prove player_storage compiles to SQL while only player_field is emitted to the Lua phase-two plan
  - CI run 29684541033 succeeded on ae6a2667da52b8671435a293f12a9f4386010606
  - no feature-specific storage key or expected value was added to shared platform fixtures
derived:
  - player_storage safely reuses the existing post-cycle scalar SQL evaluator while player_field remains the only current phase-two client-readable persistence type
  - filtering runtime checks by assertion type preserves the real-client verification boundary without weakening database persistence proof
unknown:
  - exact-final-head workflow conclusions after documentation and final checkpoint
conflicts: []
first_failure:
  marker: ownership_related_pr_mismatch
  evidence: Agent Task Ownership run 29684540982 failed because the initial active task had related_pr empty while the live current PR is 583; no code/test failure was reported
rejected_hypotheses:
  - inventing a shared test storage key only to force a physical assertion
  - exposing arbitrary SQL through the typed persistence contract
  - pretending arbitrary player storage is readable from the controlled OTClient
  - modifying OTBM routing or PR #580 scope
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-storage-persistence.md
  - tools/e2e/persistence_assertions.py
  - tests/e2e/test_player_storage_persistence.py
validation:
  - command: CI run 29684541033
    result: PASS
    evidence: repository CI succeeded on implementation head ae6a2667da52b8671435a293f12a9f4386010606
  - command: Agent Task Ownership run 29684540982
    result: FAIL
    evidence: initial task record related_pr was empty; corrected to 583 in the next checkpoint commit
blockers: []
next_action: Complete public documentation/catalogue/changelog updates, verify ownership recovery and Universal Agent E2E, then apply ci:final-gate before the final checkpoint commit.
```
