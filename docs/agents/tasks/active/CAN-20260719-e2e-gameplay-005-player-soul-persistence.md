---
task_id: CAN-20260719-e2e-gameplay-005-player-soul-persistence
program_id: CAN-PROGRAM-E2E-AUTOMATION
coordination_id: E2E-GAMEPLAY-005-SOUL
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-soul-persistence
base_branch: main
created: 2026-07-19T23:33:00+02:00
updated: 2026-07-19T23:33:00+02:00
last_verified_commit: "183d7224cb5de57585294d72631f37783b93dc89"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - merged E2E-GAMEPLAY-005 typed persistence foundation
  - merged PR #603 player_skill_level persistence
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-soul-persistence.md
    - docs/e2e/PLAYER_SOUL_PERSISTENCE.md
    - tests/e2e/test_player_soul_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/route_plan_execution.py
    - tests/e2e/scenarios/**
    - .github/workflows/**
    - docs/ai-agent/OTBM_*
modules_touched:
  - Universal OTS E2E physical gameplay action plans
reuses:
  - Universal Agent E2E two-session lifecycle
  - typed persistence assertion compiler
  - maintained OTClient LocalPlayer soul API
public_interfaces:
  - typed player_soul persistence assertion
cross_repo_tasks: []
---

# Goal

Add one bounded reusable `player_soul` persistence assertion for the durable Canary `players.soul` value. Re-verify the persisted value through maintained `LocalPlayer.getSoul()` after relog and through final scalar SQL without exposing arbitrary SQL or unrelated player fields.

# Acceptance criteria

- [ ] Add exactly one `player_soul` assertion type with an `equals` value.
- [ ] Accept exact integer soul values only in the maintained-client `uint8` range `0..255`.
- [ ] Re-verify after relog through maintained `LocalPlayer.getSoul()`.
- [ ] Compile final scalar SQL only against the fixed Canary `players.soul` column.
- [ ] Reject unknown fields, booleans, negative values, non-integers and values above `255`.
- [ ] Keep regeneration, stamina, offline training, vocation normalization and other player progression state out of scope.
- [ ] Preserve all existing persistence assertion types and route/runtime behavior.
- [ ] Add focused regression coverage and a durable public contract document.
- [ ] Do not modify the E2E runner, workflows, route execution, OTBM tooling, map/client assets or reference repositories.
- [ ] Update the module catalogue narrowly.
- [ ] Apply `ci:final-gate` before the final checkpoint commit and make no post-final-head commits.
- [ ] Require exact-final-head Ownership, CI, Universal Agent E2E and autofix as applicable plus a clean review blocker audit before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T23:33:00+02:00
head: 183d7224cb5de57585294d72631f37783b93dc89
branch: feat/e2e-player-soul-persistence
pr: null
status: implementing
next_action: Publish the draft PR, implement the bounded player_soul validator/compiler and maintained-client relog check, then add focused tests/docs and audit the exact diff.
context_routes:
  - agent-governance
  - universal-e2e
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-soul-persistence.md
  - docs/e2e/PLAYER_SOUL_PERSISTENCE.md
  - tests/e2e/test_player_soul_persistence.py
  - tools/e2e/persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/agents/MODULE_CATALOG.md
proven:
  - live main at task start is 183d7224cb5de57585294d72631f37783b93dc89
  - no open E2E persistence PR overlaps this contract; PR 600 remains separately owned OTBM route work
  - Canary schema stores durable soul in the fixed players.soul column
  - maintained blakinio/otclient LocalPlayer exposes getSoul returning uint8_t
  - existing Universal E2E persistence compiler and two-session relog verification are reusable
  - raw server vocation IDs remain outside exact equality until a separate normalization contract exists
unknown:
  - exact final-head validation outcomes are not known yet
conflicts: []
rejected_hypotheses:
  - expose caller-controlled player columns or arbitrary SQL
  - fold vocation normalization into this scalar soul contract
  - add a second E2E runner or lifecycle
changed_paths:
  - docs/agents/tasks/active/CAN-20260719-e2e-gameplay-005-player-soul-persistence.md
blockers: []
validation:
  - command: evidence review of current Canary schema and maintained OTClient LocalPlayer API
    result: PASS
    evidence: players.soul is a fixed durable column and LocalPlayer.getSoul is a uint8_t read surface suitable for exact 0..255 relog verification.
```
