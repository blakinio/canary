---
task_id: CAN-20260717-oteryn-vocations-physical-e2e
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-009
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/oam-009-vocations-physical-e2e
base_branch: main
created: 2026-07-17T16:50:00+02:00
updated: 2026-07-17T18:21:00+02:00
last_verified_commit: "24e6c6f7733990f305123b696461d800e6b1a4d7"
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
    - tools/e2e/run_physical_e2e.sh
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docker/data/02-test_account_players.sql
    - src/io/functions/iologindata_load_player.cpp
    - data/XML/vocations.xml
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_agent_e2e.py
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
- [x] Make the existing generic physical E2E runner execute every canonical `scenario.assertions.sql` entry as a scalar boolean assertion and fail closed unless each returns exactly `1`.
- [x] Run the existing Universal Agent E2E against exact controlled server `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` after the SQL-assertion runner fix.
- [x] Require physical login, safe logout, relog, second safe logout, existing persistence assertions, and the new bounded vocation assertion to pass.
- [x] Record exact final workflow run, exact controlled server SHA, artifact digest and executable hashes from the accepted physical evidence.
- [x] Remove any temporary controlled-server pin before merge while preserving the physical evidence record.
- [ ] Require final PR head ownership/CI/review gates with zero unresolved review threads before squash merge.
- [ ] Complete lifecycle/archive before starting OAM-010.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T18:21:00+02:00
head: 24e6c6f7733990f305123b696461d800e6b1a4d7
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
  - tools/e2e/run_physical_e2e.sh
proven:
  - Canary task-start is 4154d43a5b89ddc067569fde6d70f3d2c1e1e320
  - Otheryn target is f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
  - maintained OTClient is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - OAM-008 feature and lifecycle are complete
  - OAM-009 durable program state was not created or started before this task
  - Knight 1 fixture is level 500 with vocation 4
  - exact target loadPlayerBasicInfo reads vocation and fails closed when setVocation fails
  - exact target vocations.xml defines vocation id 4 as Knight
  - existing login/relog scenario proves two physical sessions and lastlogin/lastlogout persistence
  - current open PRs inspected at task start did not overlap tests/e2e/scenarios/login/scenario.json or this OAM task path
  - PR 489 is the bounded OAM-009 feature PR
  - login/relog scenario declares SELECT vocation = 4 for Knight 1
  - preliminary Universal Agent E2E run 29589941229 physically passed on exact target but is not accepted because the then-current runner did not execute manifest assertions.sql
  - existing generic physical runner now executes every canonical scenario.assertions.sql entry fail closed and requires scalar result exactly 1
  - accepted Universal Agent E2E run 29593102547 physically passed login/logout/relog/logout on exact Otheryn target and maintained OTClient
  - accepted run 29593102547 records scenario_sql_assertions true
  - accepted run 29593102547 executed all three canonical SQL assertions and each returned stdout 1
  - accepted run 29593102547 executed SELECT vocation = 4 FROM players WHERE name = 'Knight 1' and it passed
  - accepted physical artifact digest is sha256:f880b2fb58c53d8e53aad4cc30725a26a050c352bd5412a10c56b8a61f327f3f
  - accepted exact controlled-server executable SHA256 is 3a191e398ea22818a9e71cd3ce0fe60486e1e0592cddb379295504a77dc62925
  - accepted controlled-client executable SHA256 is 5dcaed6cdfcaecf2de4b9de80183a28fe8e0722e21b4df588cc627c558da5ee9
  - proof-only controlled-server pin was removed before final merge gates
  - latest non-overlapping main 8aa4d7def083c3701b9c81119ec2aa8ea26a68af was synchronized into the feature branch through PR 495 without cherry-picking
  - synchronization commit on the OAM-009 branch is 24e6c6f7733990f305123b696461d800e6b1a4d7
derived: []
unknown: []
conflicts: []
first_failure:
  marker: manifest SQL assertions were not executed by the existing physical runner
  evidence: Universal Agent E2E run 29589941229 succeeded while tools/e2e/run_physical_e2e.sh evaluated only hardcoded lastlogin and lastlogout queries; the gap was resolved before accepted run 29593102547
rejected_hypotheses:
  - successful aggregate CI without physical client evidence proves target vocation resolution
  - SQL assertion presence in scenario-manifest.json means the assertion was executed
  - SQL assertion alone proves runtime registry resolution
  - a Canary-server physical run can substitute for exact Otheryn target proof
  - creating a second E2E workflow or runner is necessary
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-oteryn-vocations-physical-e2e.md
  - docs/agents/OTERYN_OAM_009_VOCATIONS_PHYSICAL_E2E.md
  - tests/e2e/scenarios/login/scenario.json
  - .github/e2e-controlled-server.env
  - tools/e2e/run_physical_e2e.sh
validation:
  - command: Universal Agent E2E run 29589941229
    result: FAIL
    evidence: Physical login/relog flow passed on exact Otheryn target, but canonical manifest SQL assertions were not executed by the then-current runner; preliminary evidence only.
  - command: Universal Agent E2E run 29593102547
    result: PASS
    evidence: Physical login/logout/relog/logout passed on exact Otheryn f59a58426b4d3910ba0cdc0d2332c24f31a1db4f; scenario_sql_assertions=true and all three canonical SQL assertions returned 1, including vocation = 4.
blockers: []
next_action: Require final exact-head ownership, CI, physical-E2E/reuse and review-thread gates on PR 489; if clean, mark ready and squash merge, then complete the separate lifecycle/archive before any OAM-010 work.
```
