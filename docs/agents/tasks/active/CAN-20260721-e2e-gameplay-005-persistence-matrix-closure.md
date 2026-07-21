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
last_verified_commit: "6919b14e8ab73102d3cf6859e73b7ed9676db90f"
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
    - tools/e2e/persistence_assertions.py
    - tests/e2e/test_player_field_persistence_precision.py
  read_only:
    - docs/architecture/universal-e2e-gameplay-validation.md
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_persistence_assertions.py
    - tests/e2e/test_player_storage_persistence.py
    - tests/e2e/test_player_item_persistence.py
    - tests/e2e/test_player_balance_persistence.py
    - tests/e2e/test_player_magic_level_persistence.py
    - tests/e2e/test_player_skill_level_persistence.py
    - tests/e2e/test_player_vocation_persistence.py
    - tests/e2e/test_player_soul_persistence.py
modules_touched:
  - Universal E2E persistence contract documentation
  - Universal E2E typed persistence validation
reuses:
  - canonical Universal E2E two-session login/safe-logout/relog lifecycle
  - merged typed persistence assertion surfaces
public_interfaces:
  - scenario.assertions.persistence player_field exact Lua-safe integer boundary
cross_repo_tasks: []
---

# Goal

Close `E2E-GAMEPLAY-005` with one durable, feature-neutral persistence assertion matrix over the already merged typed contracts, without adding speculative runtime capability or feature-specific values.

# Acceptance criteria

- [x] Audit the current merged typed persistence assertion surfaces on `main`.
- [x] Add one durable matrix covering `player_field`, `player_storage`, `player_item_presence`, `player_balance`, `player_magic_level`, `player_skill_level`, `player_vocation`, and `player_soul`.
- [x] Record which types are verified through controlled-client post-relog plus SQL and which are intentionally database-only.
- [x] Keep quest storage keys, item IDs, economy values, progression values, and other feature-specific expectations out of shared platform documentation.
- [x] Do not add a new assertion type unless the audit proves a concrete reusable gap required for matrix completeness.
- [x] Close the proven `player_field` exact-integer gap without changing the canonical lifecycle or adding a new assertion type.
- [x] Update the Universal E2E programme record to reflect the actual `E2E-GAMEPLAY-005` closure state.
- [ ] Pass checkpoint validation and applicable docs/ownership/CI checks on the exact final head.
- [ ] Merge only after the normal autonomous merge gate passes, then archive this task in a separate lifecycle PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T12:52:00+02:00
head: 6919b14e8ab73102d3cf6859e73b7ed9676db90f
branch: docs/e2e-gameplay-005-persistence-matrix-closure
pr: 666
status: implementing
context_routes:
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-005-persistence-matrix-closure.md
  - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - tools/e2e/persistence_assertions.py
  - tests/e2e/test_player_field_persistence_precision.py
proven:
  - E2E-GAMEPLAY-003 feature PR 637 and lifecycle PR 663 are merged
  - roadmap permits E2E-GAMEPLAY-005 to proceed independently of route planning
  - typed persistence slices PRs 565, 583, 586, 591, 595, 603, 608, and 615 are merged
  - PR 666 owns this bounded persistence matrix closure task and remains mergeable
  - the merged implementation exposes exactly eight typed persistence assertion types required by the task matrix
  - player_storage and player_item_presence are intentionally database-only after the canonical two-session cycle
  - player_field, player_balance, player_magic_level, player_skill_level, player_vocation, and player_soul have controlled-client post-relog verification plus final fixed-shape SQL verification
  - current main documentation did not capture all eight merged types consistently before this matrix package
  - the merged focused item-presence test is tests/e2e/test_player_item_persistence.py
  - maintained OTClient converts uint64 Lua-bound values to double while player_field previously accepted signed-64 expected values for client-verified experience
  - exact client equality above MAX_SAFE_LUA_INTEGER is not guaranteed for player_field experience
  - tools/e2e/persistence_assertions.py now applies MAX_SAFE_LUA_INTEGER to player_field expected values
  - tests/e2e/test_player_field_persistence_precision.py covers the accepted and rejected boundary
  - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md is the canonical eight-type closure inventory
  - no new persistence assertion type is required for matrix completeness
  - Agent Task Ownership run 29822994260 passed on pre-final head 6919b14e8ab73102d3cf6859e73b7ed9676db90f
derived:
  - E2E-GAMEPLAY-005 can close after exact-final-head gates pass because the declared priority domains are covered and the only concrete reusable audit gap has been corrected
unknown:
  - exact-final-head workflow conclusions after this checkpoint commit
conflicts: []
first_failure:
  marker: checkpoint-validation
  evidence: ownership validation exposed three checkpoint-only defects in sequence; missing derived/unsupported UNAVAILABLE, proven compactness overflow, and non-active validating status were all corrected before the pre-final ownership pass
rejected_hypotheses:
  - OTBM-E2E-002 should be resumed by this task: user assigned that scope to another owner and the OTBM route programme is already closed
  - current persistence documentation already provides one complete merged-type inventory: rejected because PHYSICAL_GAMEPLAY_ACTION_PLANS.md still describes only the earlier subset and treats vocation normalization as future work
  - E2E-GAMEPLAY-005 requires another assertion domain before closure: rejected after auditing all merged typed contracts against the declared priority domains
changed_paths:
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260721-e2e-gameplay-005-persistence-matrix-closure.md
  - docs/e2e/PERSISTENCE_ASSERTION_MATRIX.md
  - tests/e2e/test_player_field_persistence_precision.py
  - tools/e2e/persistence_assertions.py
validation:
  - command: live GitHub PR state for persistence slices 565, 583, 586, 591, 595, 603, 608, 615
    result: PASS
    evidence: each PR is closed and merged on blakinio/canary
  - command: live PR 666 ownership and overlap audit
    result: PASS
    evidence: PR 666 is the only open persistence-matrix closure PR; no open PR matched persistence_assertions.py or test_persistence_assertions.py
  - command: GitHub CI workflow at c14c057c1a1d27fe92b6d1f30f53350be17036ec
    result: PASS
    evidence: CI run 29822621295 completed successfully with the persistence code, regression test, matrix, and programme update
  - command: Agent Task Ownership at 6919b14e8ab73102d3cf6859e73b7ed9676db90f
    result: PASS
    evidence: run 29822994260 passed after checkpoint schema and compactness corrections
  - command: latest-main relevance check
    result: PASS
    evidence: main advanced to 824abcfe3d39d274e8cad534fff06236085b129b only through OTBM roadmap lifecycle archival, with no overlap on this task's five changed paths
  - command: local git/test execution
    result: NOT_RUN
    evidence: local container cannot resolve github.com; repository edits and executable validation use the authorized GitHub connector and PR workflows
blockers:
  - exact-final-head checks triggered by ci:final-gate must pass before readiness and merge
next_action: Apply ci:final-gate to PR 666, verify all required exact-final-head checks, then mark the PR ready and squash-merge without further feature-head commits.
```
