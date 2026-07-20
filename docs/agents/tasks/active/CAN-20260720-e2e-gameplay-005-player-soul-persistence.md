---
task_id: CAN-20260720-e2e-gameplay-005-player-soul-persistence
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005-SOUL
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/e2e-player-soul-persistence-contract
base_branch: main
created: 2026-07-20T10:17:00+02:00
updated: 2026-07-20T21:26:48+02:00
last_verified_commit: "9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5"
risk: medium
related_issue: ""
related_pr: "615"
depends_on:
  - merged E2E-GAMEPLAY-005 typed persistence foundation
  - merged PR #608 player_vocation persistence
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-005-player-soul-persistence.md
    - docs/e2e/PLAYER_SOUL_PERSISTENCE.md
    - tests/e2e/test_player_soul_persistence.py
  shared:
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/scenarios/**
    - .github/workflows/**
    - schema.sql
modules_touched:
  - Universal OTS E2E physical gameplay action plans
reuses:
  - Universal Agent E2E two-session lifecycle
  - typed persistence assertion compiler
  - maintained OTClient LocalPlayer.getSoul API
public_interfaces:
  - typed player_soul persistence assertion
cross_repo_tasks: []
---

# Goal

Add one bounded reusable `player_soul` persistence assertion for exact values `0..255`, verify it after relog through maintained `LocalPlayer.getSoul()`, and verify final durable state through fixed `players.soul` SQL.

# Acceptance criteria

- [x] Exact typed `player_soul` assertion with integer `equals` in `0..255`.
- [x] Reject booleans, out-of-range values, unknown fields and arbitrary SQL surfaces.
- [x] Re-verify after relog through maintained `LocalPlayer.getSoul()`.
- [x] Compile final scalar SQL only against fixed `players.soul`.
- [x] Preserve existing persistence behavior and add focused regression coverage.
- [x] Reuse the existing Universal Agent E2E two-session lifecycle.
- [x] Exact-final-head Ownership, CI, Universal Agent E2E and ready-triggered validation passed.
- [x] PR #615 squash-merged with the frozen expected head.
- [ ] Archive this merged task through the normal governance lifecycle cleanup.

# Current state

Feature delivery is complete and merged in PR #615. The active task record remains only because the post-merge lifecycle archive has not yet been created or merged. No feature-code continuation is required.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T21:26:48+02:00
head: 926cbf5c157aae88e1c92a0d660c3ad830805228
branch: feat/e2e-player-soul-persistence-contract
pr: 615
status: ready
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-005-player-soul-persistence.md
  - docs/e2e/PLAYER_SOUL_PERSISTENCE.md
  - tests/e2e/test_player_soul_persistence.py
  - tools/e2e/persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - docs/agents/MODULE_CATALOG.md
proven:
  - PR 615 is merged; final feature head is 926cbf5c157aae88e1c92a0d660c3ad830805228 and squash merge commit is 9648e213792c21b59e7c8b7c5310609e6b554141
  - exact-final-head Agent Task Ownership run 29728787270 completed success
  - exact-final-head CI run 29728787498 completed success
  - exact-final-head Universal Agent E2E run 29728787426 completed success
  - ready-triggered autofix.ci run 29730667609 completed success without moving the feature head
  - ready-triggered full CI run 29730667834 completed success
  - the player soul task record still exists under docs/agents/tasks/active on the latest observed main 9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5
  - no open PR matched a PR 615 lifecycle or archive cleanup at the handoff check
derived:
  - player_soul feature delivery is complete and merged; the remaining work is governance-only lifecycle archival of this active task record
unknown:
  - whether main advances beyond 9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5 before the continuation agent starts
conflicts: []
first_failure:
  marker: none
  evidence: none; the feature PR merged after all required exact-head gates and blocker audit completed
rejected_hypotheses:
  - continue feature implementation: PR 615 is already merged at the proven frozen final head
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-e2e-gameplay-005-player-soul-persistence.md
validation:
  - command: GitHub live PR 615 state
    result: PASS
    evidence: merged true; head 926cbf5c157aae88e1c92a0d660c3ad830805228; merge commit 9648e213792c21b59e7c8b7c5310609e6b554141
  - command: GitHub workflow runs for 926cbf5c157aae88e1c92a0d660c3ad830805228
    result: PASS
    evidence: Ownership 29728787270, CI 29728787498, Universal Agent E2E 29728787426, autofix 29730667609 and ready CI 29730667834 all completed success
  - command: GitHub open PR search for PR 615 lifecycle archive cleanup
    result: PASS
    evidence: no matching open PR found at handoff check
blockers: []
next_action: From current main, re-verify that no lifecycle cleanup PR for 615 exists, then create the minimal governance-only task archive cleanup for this merged feature without modifying feature code.
```
