---
task_id: CAN-20260717-oteryn-vocations-physical-e2e
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-009
status: completed
agent: "GPT-5.5 Thinking"
branch: test/oam-009-vocations-physical-e2e
base_branch: main
created: 2026-07-17T16:50:00+02:00
updated: 2026-07-17T20:55:00+02:00
last_verified_commit: "d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c"
risk: low
related_issue: ""
related_pr: "489"
depends_on:
  - OAM-008
blocks:
  - OAM-010
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260717-oteryn-vocations-physical-e2e.md
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
completed: 2026-07-17T20:55:00+02:00
---

# Goal

Prove the bounded OAM-009 claim that exact target `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` physically logs in fixture `Knight 1` with persisted `vocation = 4` through the migrated vocation registry.

# Acceptance criteria

- [x] Fixture `Knight 1` has `vocation = 4` and target load fails closed for unknown vocation IDs.
- [x] Canonical `login/relog` includes `SELECT vocation = 4 FROM players WHERE name = 'Knight 1'`.
- [x] Existing generic physical runner executes canonical SQL assertions fail closed; no second orchestrator.
- [x] Accepted exact-target physical proof executed all three SQL assertions and returned `1`.
- [x] Exact target/client refs, artifact digest, and executable hashes are recorded.
- [x] Proof-only controlled-server pin was removed.
- [x] PR #489 was reconstructed on inspected `main@2edc59f59c417f82efb0547f3ff87b426f8bbe5a` with exactly four durable OAM-009 paths.
- [x] Exact merged head passed Ownership, CI and Universal Agent E2E.
- [x] PR #489 squash merged.
- [ ] Durable program reconciliation is completed separately before OAM-010.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T20:55:00+02:00
head: d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c
branch: test/oam-009-vocations-physical-e2e
pr: 489
status: completed
context_routes:
  - agent-governance
  - universal-e2e
  - vocations
owned_paths:
  - docs/agents/tasks/archive/CAN-20260717-oteryn-vocations-physical-e2e.md
  - docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md
  - tests/e2e/scenarios/login/scenario.json
  - tools/e2e/run_physical_e2e.sh
proven:
  - OAM-008 is fully complete
  - exact Otheryn proof target is f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
  - maintained OTClient is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - accepted exact-target Universal Agent E2E run 29593102547 passed physical login logout relog logout and all three canonical SQL assertions returned 1 including vocation = 4
  - accepted physical artifact digest is sha256:f880b2fb58c53d8e53aad4cc30725a26a050c352bd5412a10c56b8a61f327f3f
  - accepted server executable SHA256 is 3a191e398ea22818a9e71cd3ce0fe60486e1e0592cddb379295504a77dc62925
  - accepted client executable SHA256 is 5dcaed6cdfcaecf2de4b9de80183a28fe8e0722e21b4df588cc627c558da5ee9
  - proof-only server pin is absent from final scope
  - exact merged feature head d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c passed Agent Task Ownership run 29603179802
  - exact merged feature head d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c passed CI run 29603179331
  - exact merged feature head d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c passed Universal Agent E2E run 29603179422
  - PR 489 squash merged as 533a1063ab2d25199fb39239e28dace6a064d395
derived:
  - the exact-target physical proof supports only the bounded vocation-ID resolution claim and does not establish broader vocation gameplay parity
  - the existing Universal Agent E2E runner is sufficient for SQL-backed persistence assertions and no second orchestrator is required
unknown:
  - durable OAM-009 program reconciliation merge SHA
conflicts: []
first_failure:
  marker: manifest SQL assertions were not executed by the original physical runner
  evidence: preliminary run 29589941229 passed physical flow but was rejected until the existing runner was fixed; accepted run 29593102547 executed all assertions
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
  - command: Universal Agent E2E run 29593102547
    result: PASS
    evidence: accepted exact Otheryn physical proof with all three SQL assertions returning 1
  - command: Agent Task Ownership run 29603179802
    result: PASS
    evidence: exact merged feature head d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c
  - command: CI run 29603179331
    result: PASS
    evidence: exact merged feature head d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c
  - command: Universal Agent E2E run 29603179422
    result: PASS
    evidence: exact merged feature head d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c
  - command: squash merge PR 489
    result: PASS
    evidence: merge commit 533a1063ab2d25199fb39239e28dace6a064d395
blockers:
  - durable program reconciliation before OAM-010
next_action: Complete durable OAM-009 program reconciliation before any OAM-010 work.
```

## Lifecycle completion

- Feature PR: #489.
- Exact merged feature head: `d90866eeb30b8e1f6fbd3b45f452d68fc0f6185c`.
- Feature merge commit: `533a1063ab2d25199fb39239e28dace6a064d395`.
- Exact-head runs: Ownership `29603179802`, CI `29603179331`, Universal Agent E2E `29603179422`.
- Accepted exact-target proof run: `29593102547`.
- Durable program reconciliation remains a separate required lifecycle step before OAM-010.
