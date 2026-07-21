---
task_id: CAN-20260721-e2e-gameplay-005-persistence-matrix-closure
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005-PERSISTENCE-MATRIX-CLOSURE
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/e2e-gameplay-005-persistence-matrix-closure
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "14bb82c82aa3bde82b8fede71697f07c48cc23b8"
risk: low
related_issue: ""
related_pr: "666"
depends_on:
  - merged E2E-GAMEPLAY-005 typed persistence slices PRs 565, 583, 586, 591, 595, 603, 608, 615
blocks:
  - durable E2E-GAMEPLAY-005 programme closure
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-005-persistence-matrix-closure.md
    - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  read_only:
    - docs/architecture/universal-e2e-gameplay-validation.md
    - tools/e2e/persistence_assertions.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_persistence_assertions.py
    - tests/e2e/test_player_storage_persistence.py
    - tests/e2e/test_player_item_presence_persistence.py
    - tests/e2e/test_player_balance_persistence.py
    - tests/e2e/test_player_magic_level_persistence.py
    - tests/e2e/test_player_skill_level_persistence.py
    - tests/e2e/test_player_vocation_persistence.py
    - tests/e2e/test_player_soul_persistence.py
modules_touched:
  - Universal E2E persistence contract documentation
reuses:
  - canonical Universal E2E two-session login/safe-logout/relog lifecycle
  - merged typed persistence assertion surfaces
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Close `E2E-GAMEPLAY-005` with one durable, feature-neutral persistence assertion matrix over the already merged typed contracts, without adding speculative runtime capability or feature-specific values.

# Acceptance criteria

- [ ] Audit the current merged typed persistence assertion surfaces on `main`.
- [ ] Add one durable matrix covering `player_field`, `player_storage`, `player_item_presence`, `player_balance`, `player_magic_level`, `player_skill_level`, `player_vocation`, and `player_soul`.
- [ ] Record which types are verified through controlled-client post-relog plus SQL and which are intentionally database-only.
- [ ] Keep quest storage keys, item IDs, economy values, progression values, and other feature-specific expectations out of shared platform documentation.
- [ ] Do not add a new assertion type unless the audit proves a concrete reusable gap required for matrix completeness.
- [ ] Update the Universal E2E programme record to reflect the actual `E2E-GAMEPLAY-005` closure state.
- [ ] Pass checkpoint validation and applicable docs/ownership/CI checks on the final head.
- [ ] Merge only after the normal autonomous merge gate passes, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T12:07:00+02:00
head: 14bb82c82aa3bde82b8fede71697f07c48cc23b8
branch: docs/e2e-gameplay-005-persistence-matrix-closure
pr: 666
status: investigating
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-005-persistence-matrix-closure.md
  - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
proven:
  - E2E-GAMEPLAY-003 feature PR 637 and lifecycle PR 663 are merged
  - roadmap permits E2E-GAMEPLAY-005 to proceed independently of route planning
  - typed persistence slices PRs 565, 583, 586, 591, 595, 603, 608, and 615 are merged
  - player soul lifecycle debt was archived by merged PR 636
  - draft PR 666 owns this bounded persistence matrix closure task
derived:
  - the next bounded E2E platform task is a feature-neutral E2E-GAMEPLAY-005 matrix and programme-closure audit rather than another persistence implementation slice
unknown:
  - whether current main documentation already captures every merged persistence type and verification surface consistently
  - whether the audit will expose any concrete reusable persistence domain gap that must be handled before formal E2E-GAMEPLAY-005 closure
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved failure is established at handover
rejected_hypotheses:
  - OTBM-E2E-002 should be resumed by this task: user assigned that scope to another owner and the OTBM route programme is already closed
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-005-persistence-matrix-closure.md
validation:
  - command: live GitHub PR state for persistence slices 565, 583, 586, 591, 595, 603, 608, 615
    result: PASS
    evidence: each PR is closed and merged on blakinio/canary
  - command: live GitHub PR state for E2E-GAMEPLAY-003 feature 637 and lifecycle 663
    result: PASS
    evidence: both PRs are closed and merged
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260721-e2e-gameplay-005-persistence-matrix-closure.md --require-checkpoint
    result: PASS
    evidence: Validated 1 task checkpoint(s).
blockers: []
next_action: Audit the current merged persistence contracts and focused tests on main, then draft docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md and the narrow E2E programme status update without runtime changes unless a concrete reusable gap is proven.
```
