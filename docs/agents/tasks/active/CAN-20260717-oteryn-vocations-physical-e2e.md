---
task_id: CAN-20260717-oteryn-vocations-physical-e2e
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-009
status: implementing
agent: "GPT-5.5 Thinking"
branch: test/oam-009-vocations-physical-e2e
base_branch: main
created: 2026-07-17T16:50:00+02:00
updated: 2026-07-17T17:36:00+02:00
last_verified_commit: "1c6cc217c956ffb9d050917612f6c52b1f8086d5"
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
- [ ] Make the existing generic physical E2E runner execute every canonical `scenario.assertions.sql` entry as a scalar boolean assertion and fail closed unless each returns exactly `1`.
- [ ] Run the existing Universal Agent E2E against exact controlled server `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` after the SQL-assertion runner fix.
- [ ] Require physical login, safe logout, relog, second safe logout, existing persistence assertions, and the new bounded vocation assertion to pass.
- [ ] Record exact final workflow run, exact controlled server SHA, artifact digest and executable hashes from the accepted physical evidence.
- [ ] Remove any temporary controlled-server pin before merge while preserving the physical evidence record.
- [ ] Require final PR head ownership/CI/review gates with zero unresolved review threads before squash merge.
- [ ] Complete lifecycle/archive before starting OAM-010.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T17:36:00+02:00
head: 1c6cc217c956ffb9d050917612f6c52b1f8086d5
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
  - existing login/relog scenario already proves two physical sessions and lastlogin/lastlogout persistence
  - current open PRs inspected do not touch tests/e2e/scenarios/login/scenario.json or this OAM task path
  - PR 489 is open as the bounded OAM-009 draft
  - login/relog scenario now declares SELECT vocation = 4 for Knight 1
  - temporary same-repository controlled-server pin selects exact Otheryn target f59a58426b4d3910ba0cdc0d2332c24f31a1db4f
  - Universal Agent E2E run 29589941229 physically passed login/relog on exact Otheryn target and maintained OTClient
  - run 29589941229 is not accepted as final OAM-009 proof because the runner did not execute manifest assertions.sql
  - run 29589941229 physical artifact digest is sha256:cd8a31ded88f89badf0361f07a4222fc681ecdbc6d197d59139fe3dad125400f
  - run 29589941229 exact server binary SHA256 is e23f4dc0ee0f3252f6285d7635e37d699ea2634ff539107a258a002f53ed0341
  - run 29589941229 controlled client binary SHA256 is 778fa8c59142a0b15f4b2c1c49dbd2c6e457b0e35595a9949bd4132361baebbb
derived: []
unknown:
  - exact accepted physical workflow run id after the SQL assertion runner fix
  - exact accepted artifact digest and executable hashes after the SQL assertion runner fix
conflicts: []
first_failure:
  marker: manifest SQL assertions are not executed by the existing physical runner
  evidence: Universal Agent E2E run 29589941229 succeeded while tools/e2e/run_physical_e2e.sh evaluated only hardcoded lastlogin and lastlogout queries, so the declared vocation = 4 SQL assertion was not proven
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
  - run 29589941229 physical login/relog flow SUCCESS on exact target, retained as diagnostic/preliminary evidence only
blockers:
  - existing physical runner must execute canonical manifest SQL assertions before OAM-009 proof can be accepted
next_action: Patch the existing generic tools/e2e/run_physical_e2e.sh to execute every scenario.assertions.sql query as a scalar boolean assertion, rerun PR 489 on the exact pinned Otheryn target, and accept proof only if all physical markers plus all three SQL assertions pass.
```
