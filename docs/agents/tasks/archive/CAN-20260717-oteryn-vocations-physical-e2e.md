---
task_id: CAN-20260717-oteryn-vocations-physical-e2e
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-009
status: completed
agent: "GPT-5.5 Thinking"
branch: test/oam-009-vocations-physical-e2e
base_branch: main
created: 2026-07-17T16:50:00+02:00
updated: 2026-07-17T18:45:39Z
last_verified_commit: "533a1063ab2d25199fb39239e28dace6a064d395"
risk: low
related_issue: ""
related_pr: "489"
depends_on:
  - OAM-008
blocks:
  - OAM-010
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-physical-e2e.md
    - docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md
    - tests/e2e/scenarios/login/scenario.json
    - tools/e2e/run_physical_e2e.sh
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docker/data/02-test_account_players.sql
    - src/io/functions/iologindata_load_player.cpp
    - data/XML/vocations.xml
    - .github/workflows/universal-agent-e2e.yml
modules_touched:
  - vocations
reuses:
  - existing Universal Agent E2E login/relog scenario
  - maintained OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
public_interfaces:
  - physical login resolution of persisted player vocation id
cross_repo_tasks: []
completed: 2026-07-17T18:45:39Z
---

# Goal

Prove the bounded OAM-009 claim that exact target `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` physically logs in fixture `Knight 1` with persisted `vocation = 4` through the migrated vocation registry.

# Acceptance criteria

- [x] Verify fixture `Knight 1` has `vocation = 4` and target load is fail-closed for unknown vocation IDs.
- [x] Add `SELECT vocation = 4 FROM players WHERE name = 'Knight 1'` to canonical `login/relog`.
- [x] Extend the existing generic physical runner to execute canonical SQL assertions fail-closed; no second orchestrator.
- [x] Accept exact-target physical proof only after all three SQL assertions execute and return `1`.
- [x] Record exact target/client refs, artifact digest, and executable hashes.
- [x] Remove proof-only controlled-server pin.
- [x] Reconstruct PR #489 directly on inspected `main@2edc59f59c417f82efb0547f3ff87b426f8bbe5a` with exactly four durable OAM-009 paths.
- [ ] Pass final synchronized exact-head Ownership, CI, Universal Agent E2E, and review-thread gates; squash-merge PR #489.
- [ ] Complete separate lifecycle/archive and durable program reconciliation before OAM-010.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T20:10:48+02:00
head: fe7ad44e607217bd89425c96ab8afdb1e11d3842
branch: test/oam-009-vocations-physical-e2e
pr: 489
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
  - vocations
owned_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-physical-e2e.md
  - docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md
  - tests/e2e/scenarios/login/scenario.json
  - tools/e2e/run_physical_e2e.sh
proven:
  - OAM-008 is fully complete
  - exact Otheryn proof target is f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
  - maintained OTClient is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - accepted exact-target Universal Agent E2E run 29593102547 passed physical login logout relog logout
  - run 29593102547 executed all three canonical SQL assertions and each returned 1 including vocation = 4
  - accepted physical artifact digest is sha256:f880b2fb58c53d8e53aad4cc30725a26a050c352bd5412a10c56b8a61f327f3f
  - accepted server executable SHA256 is 3a191e398ea22818a9e71cd3ce0fe60486e1e0592cddb379295504a77dc62925
  - accepted client executable SHA256 is 5dcaed6cdfcaecf2de4b9de80183a28fe8e0722e21b4df588cc627c558da5ee9
  - proof-only server pin is absent from final scope
  - latest inspected Canary main is 2edc59f59c417f82efb0547f3ff87b426f8bbe5a
  - PR 489 was reconstructed directly on that main with exactly four durable OAM-009 paths
derived: []
unknown:
  - final synchronized feature head gate results
  - feature merge SHA
  - lifecycle merge SHA
  - program reconciliation merge SHA
conflicts: []
first_failure:
  marker: manifest SQL assertions were not executed by the original physical runner
  evidence: preliminary run 29589941229 passed physical flow but was rejected until the existing runner was fixed and accepted run 29593102547 passed with executed SQL assertions
rejected_hypotheses:
  - aggregate CI alone proves target vocation resolution
  - declared SQL assertions count as executed evidence
  - a Canary-server run substitutes for exact Otheryn proof
  - a second E2E orchestrator is necessary
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-physical-e2e.md
  - docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md
  - tests/e2e/scenarios/login/scenario.json
  - tools/e2e/run_physical_e2e.sh
validation:
  - command: Universal Agent E2E run 29589941229
    result: FAIL
    evidence: preliminary physical pass only; manifest SQL assertions were not executed
  - command: Universal Agent E2E run 29593102547
    result: PASS
    evidence: exact Otheryn physical flow passed and all three canonical SQL assertions returned 1 including vocation = 4
blockers: []
next_action: Pass final exact-head gates on the feature head synchronized to main 2edc59f59c417f82efb0547f3ff87b426f8bbe5a, squash-merge PR 489, then complete lifecycle/archive and program reconciliation before any OAM-010 work.
```

## Automated lifecycle completion

- Feature PR: #489.
- Feature head: `d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c`.
- Merge commit: `533a1063ab2d25199fb39239e28dace6a064d395`.
- Merged at: `2026-07-17T18:45:39Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
