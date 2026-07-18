---
task_id: CAN-20260718-e2e-gameplay-005-persistence-assertions
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: review
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-persistence-assertions
base_branch: main
created: 2026-07-18T23:32:00+02:00
updated: 2026-07-19T00:15:00+02:00
last_verified_commit: "5976bc7d3b0b5a71fbcaf51710c52e6ade2a7f2c"
risk: medium
related_issue: ""
related_pr: "565"
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM existing Universal Physical E2E two-session lifecycle
  - merged PR #563 Universal E2E gameplay validation architecture/roadmap
blocks:
  - feature-owned scenarios requiring reusable M3 player-field persistence assertions
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-e2e-gameplay-005-persistence-assertions.md
    - tools/e2e/persistence_assertions.py
    - tests/e2e/test_persistence_assertions.py
  shared:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/scenarios/platform/action-plan-contract.json
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_physical_e2e.sh
    - .github/workflows/**
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - docs/agents/decisions/ADR-20260718-universal-e2e-gameplay-validation-layers.md
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
modules_touched:
  - Universal OTS E2E physical gameplay persistence assertions
reuses:
  - existing scenario assertions.sql execution after the canonical two-session client lifecycle
  - existing run_agent_e2e.py scenario validation and manifest normalization
  - existing generic gameplay driver and phase-2 relog lifecycle
  - existing action-plan-contract platform scenario
public_interfaces:
  - optional scenario.assertions.persistence object
  - persistence assertion type player_field
  - generated scenario-plan.lua persistence_checks
cross_repo_tasks: []
---

# Goal

Implement the smallest complete reusable slice of `E2E-GAMEPLAY-005`: a feature-neutral typed persistence assertion surface for durable player fields, verified through the existing Universal Physical E2E lifecycle as `login -> physical actions -> safe logout -> persisted state -> relog -> runtime verification -> safe logout -> final persisted SQL verification`.

The first slice deliberately covers one natural persistence type only: exact integer assertions over a conservative whitelist of durable player progression/vocation fields (`level`, `vocation`, `experience`). Feature-specific expected values remain in scenario manifests.

# Why this slice

- Current Universal E2E already owns the two-session lifecycle and post-cycle read-only scalar SQL evaluator, so persistence assertions extend those proven surfaces rather than creating a second runner or workflow.
- The controlled OTClient exposes read-only `LocalPlayer:getLevel()`, `Player:getVocation()` and `LocalPlayer:getExperience()`, allowing the same typed checks to be re-verified after relog before the second safe logout.
- The disposable fixture already provides deterministic `level` and `vocation` values for `Knight 1`, allowing one real platform scenario to consume the contract without inventing item IDs, storages, quest values or map data.
- No deterministic inventory mutation fixture or stable generic storage assertion contract was identified in the current physical platform baseline, so inventory/storage are deferred rather than guessed.

# Acceptance criteria

- [x] Create a reusable, deterministic persistence assertion compiler with strict field/type validation and no arbitrary SQL surface.
- [x] Extend existing scenario validation to accept optional `assertions.persistence` without creating a new runner/workflow.
- [x] Compile typed persistence assertions into the existing post-cycle SQL assertion list in normalized manifests.
- [x] Emit the same typed checks into the existing scenario plan and re-verify them through the controlled OTClient after relog before the second safe logout.
- [x] Keep raw scenario-owned `assertions.sql` behavior backward compatible.
- [x] Add focused tests for valid compilation, invalid types/fields/values, SQL literal safety, plan rendering and manifest integration.
- [x] Update at least one real existing physical scenario to use the new typed persistence assertion mechanism.
- [x] Preserve the current login/logout/relog sentinel and leave OTBM routing paths untouched.
- [x] Update reusable-interface documentation/catalogue and changelog.
- [ ] Verify all required GitHub checks on the exact `ci:final-gate` head and merge only if the autonomous merge gate is satisfied.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T00:15:00+02:00
head: 5976bc7d3b0b5a71fbcaf51710c52e6ade2a7f2c
branch: feat/e2e-gameplay-005-persistence-assertions
pr: 565
status: validating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-e2e-gameplay-005-persistence-assertions.md
  - tools/e2e/persistence_assertions.py
  - tests/e2e/test_persistence_assertions.py
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - task-start main SHA was be7842412beb5d240e76ffd4cd18aacdc3a2dcca
  - PR 562 merged as 59916930b08bafb87dcddec89230d16b8e1f0712; its OTBM route-export and bridge contracts remain separate from this persistence slice
  - PR 563 merged as c1c0d10ed1e758cb72728be5fe22458cd9d9e61a; its architecture, ADR and E2E automation programme were read after merge and explicitly permit E2E-GAMEPLAY-005 independently of route-consumption work
  - merged architecture requires M3 evidence across safe logout, persisted-state verification, relog and re-verification
  - one existing Universal Physical E2E orchestrator remains authoritative; no runner or workflow was added
  - typed player_field assertions are strictly limited to level, vocation and experience and expose no arbitrary SQL through the reusable contract
  - the same validated checks are rendered into scenario-plan.lua persistence_checks for phase-2 controlled-client verification and compiled into the existing post-cycle scalar SQL path
  - controlled blakinio/otclient exposes LocalPlayer getLevel/getExperience and Player getVocation read APIs; no client repository mutation was made
  - action-plan-contract uses deterministic Knight 1 fixture expectations level 500 and vocation 4 and requires post-relog persistence markers
  - raw scenario-owned assertions.sql remains supported and unchanged for scenarios without typed persistence declarations
  - exact changed-file review found nine text/source/documentation paths and no OTBM maps, items.otb, client assets, database dumps, credentials or secrets
  - MODULE_CATALOG and CHANGELOG contain the reusable persistence interface and behavior-level change; the shared changelog conflict caused by merged PR 563 was reconciled without force-rewriting published history
  - PR 565 is ready for review, labeled ci:final-gate, mergeable before final-gate checkpoint commits, and has no review threads or submitted requested-change reviews
  - pre-final head f18eb252f743092443f00c94b878c25729b851bd passed CI run 29662746814 and Agent Task Ownership run 29662746752
  - pre-final Universal Agent E2E run 29662746820 passed exact scenario resolution, deterministic database bootstrap and exact Canary linux-release build before final-gate synchronization superseded its still-running controlled-OTClient build
  - final-gate head 5976bc7d3b0b5a71fbcaf51710c52e6ade2a7f2c failed Agent Task Ownership only because this task record used unsupported validation result SUPERSEDED_BY_FINAL_HEAD; artifact 8434907618 identified that exact checkpoint-schema error and this commit repairs it to NOT_RUN
  - no local Git checkout is available in the execution sandbox; focused Python unit tests are committed but were not claimed as locally executed; exact-head scenario list/validate/resolve and physical E2E are the available integration/runtime evidence
  - repository writes were restricted to blakinio/canary; blakinio/otclient and upstream repositories remained read-only

derived:
  - typed player_field persistence evidence is fail-closed at two independent post-action layers: controlled-client value after relog and exact scalar SQL after the second safe logout
  - feature-specific expected values stay in scenario manifests while tools/e2e owns only the reusable typed capability
unknown:
  - whether a later storage assertion should target a dedicated table or another persistence abstraction; do not guess in this task
  - deterministic inventory mutation fixture suitable for a reusable follow-up persistence slice
conflicts: []
blockers: []
first_failure:
  marker: agent-task-ownership/validate-changed
  evidence: Initial ownership validation rejected scalar first_failure null; the task checkpoint was corrected to the required mapping and current-head ownership validation subsequently passed.
rejected_hypotheses:
  - create a second persistence runner or workflow
  - treat a pre-logout static SQL check as persistence proof
  - add storage or inventory semantics without a proven deterministic fixture/contract
  - duplicate or consume unfinished OTBM route contracts from PR 562
  - force-rewrite the published task branch after main advanced
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260718-e2e-gameplay-005-persistence-assertions.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - tests/e2e/test_persistence_assertions.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tools/e2e/persistence_assertions.py
  - tools/e2e/run_agent_e2e.py
validation:
  - command: lean startup repository/PR/path ownership review
    result: PASS
    evidence: AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, targeted MODULE_CATALOG/BUILD_TEST_MATRIX, merged PR 562 programme, merged PR 563 architecture/ADR/programme and current Universal E2E lifecycle reviewed
  - command: exact PR 565 full changed-file and focused patch review
    result: PASS
    evidence: nine expected text/source/documentation paths only; runner/client changes are limited to typed persistence validation, plan rendering, phase-two checks and existing SQL compilation
  - command: GitHub CI on pre-final head f18eb252f743092443f00c94b878c25729b851bd
    result: PASS
    evidence: workflow run 29662746814 completed success
  - command: Agent Task Ownership on pre-final head f18eb252f743092443f00c94b878c25729b851bd
    result: PASS
    evidence: workflow run 29662746752 completed success
  - command: Universal Agent E2E on pre-final head f18eb252f743092443f00c94b878c25729b851bd
    result: NOT_RUN
    evidence: run 29662746820 passed scenario resolution, DB bootstrap and exact Canary build but was superseded before controlled-OTClient build and physical execution completed
  - command: Agent Task Ownership final-gate attempt on head 5976bc7d3b0b5a71fbcaf51710c52e6ade2a7f2c
    result: FAIL
    evidence: run 29663063422 artifact 8434907618 reported only unsupported checkpoint validation result SUPERSEDED_BY_FINAL_HEAD; this checkpoint repair addresses that exact failure
next_action: Verify every required ci:final-gate workflow on the exact new task-record head. If all checks pass, PR 565 remains mergeable, and no review or ownership blocker appears, squash-merge PR 565. Make no further commit after the green final-head gate.
```
