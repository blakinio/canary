---
task_id: CAN-20260717-oteryn-vocations-physical-e2e
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-009
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/oam-009-vocations-physical-e2e
base_branch: main
created: 2026-07-17T16:50:00+02:00
updated: 2026-07-17T16:54:00+02:00
last_verified_commit: "a177e6cca5c0db6dc15a6f56ea059fd8dfe59260"
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
    - .github/e2e-controlled-server.env
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docker/data/02-test_account_players.sql
    - src/io/functions/iologindata_load_player.cpp
    - data/XML/vocations.xml
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - blakinio/canary@4154d43a5b89ddc067569fde6d70f3d2c1e1e320
    - blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
    - blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
modules_touched:
  - vocations
reuses:
  - existing Universal Agent E2E login/relog scenario
  - existing controlled-server pin contract from OTS-001
  - maintained OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
public_interfaces:
  - physical login resolution of persisted player vocation id
cross_repo_tasks: []
---

# Goal

Prove, with the existing physical-client E2E platform, that exact target `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` can physically log in the deterministic fixture player `Knight 1`, whose persisted database `vocation` value is `4`, and preserve that value through the canonical login/logout/relog sentinel.

The claim is intentionally bounded to successful physical login resolving vocation ID `4` through the target registry. It does not claim broader vocation gameplay correctness.

# Acceptance criteria

- [x] Re-fetch exact task-start baselines before implementation.
- [x] Verify no open PR overlaps the owned scenario/task paths.
- [x] Verify deterministic fixture `Knight 1` has `vocation = 4`.
- [x] Verify exact target load path is fail-closed when `player->setVocation(vocationId)` returns false.
- [x] Verify exact target `vocations.xml` contains vocation ID `4` as Knight.
- [x] Add only the bounded SQL assertion `SELECT vocation = 4 FROM players WHERE name = 'Knight 1'` to the existing login/relog scenario.
- [ ] Run the existing Universal Agent E2E against exact controlled server `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- [ ] Require physical login, safe logout, relog, second safe logout, existing persistence assertions, and the new bounded vocation assertion to pass.
- [ ] Record exact workflow run, exact controlled server SHA, artifact digest and executable hashes from the physical evidence.
- [ ] Remove any temporary controlled-server pin before merge while preserving the physical evidence record.
- [ ] Require final PR head ownership/CI/review gates with zero unresolved review threads before squash merge.
- [ ] Complete lifecycle/archive before starting OAM-010.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T16:54:00+02:00
head: a177e6cca5c0db6dc15a6f56ea059fd8dfe59260
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
  - .github/e2e-controlled-server.env
proven:
  - Canary task-start is 4154d43a5b89ddc067569fde6d70f3d2c1e1e320
  - Otheryn target is f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
  - maintained OTClient is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - OAM-008 feature and lifecycle are complete
  - OAM-009 durable program state was not created or started before this task
  - Knight 1 fixture is level 500 with vocation 4
  - exact target loadPlayerBasicInfo reads vocation and fails closed when setVocation fails
  - exact target vocations.xml defines vocation id 4 as Knight
  - existing login/relog scenario already proves two physical sessions and lastlogin/lastlogout persistence
  - current open PRs inspected do not touch tests/e2e/scenarios/login/scenario.json or this OAM task path
  - PR 489 is open as the bounded OAM-009 draft
  - login/relog scenario now asserts SELECT vocation = 4 for Knight 1
  - temporary same-repository controlled-server pin selects exact Otheryn target f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
unknown:
  - exact physical workflow run id
  - exact artifact digest and executable hashes
conflicts: []
first_failure:
  marker: none active
  evidence: no OAM-009 runtime validation failure has been observed; the initial ownership failure was task-checkpoint formatting only
rejected_hypotheses:
  - successful aggregate CI without physical client evidence proves target vocation resolution
  - SQL assertion alone proves runtime registry resolution
  - a Canary-server physical run can substitute for exact Otheryn target proof
  - creating a second E2E workflow or runner is necessary
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-physical-e2e.md
  - docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md
  - tests/e2e/scenarios/login/scenario.json
  - .github/e2e-controlled-server.env
validation: []
blockers: []
next_action: Inspect the automatically triggered PR 489 Universal Agent E2E on the exact pinned Otheryn target; if the physical proof passes, record the evidence and remove only the temporary controlled-server pin before final merge gates.
```
