---
task_id: CAN-20260718-e2e-gameplay-005-persistence-assertions
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: review
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-persistence-assertions
base_branch: main
created: 2026-07-18T23:32:00+02:00
updated: 2026-07-19T00:31:00+02:00
last_verified_commit: "f6e27c67c787f001701b5782286680e2791213d6"
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

The first slice deliberately covers one natural persistence type only: exact integer assertions over a conservative whitelist of durable, directly comparable progression fields (`level`, `experience`). Feature-specific expected values remain in scenario manifests. Raw server vocation IDs are deferred because physical E2E proved that the controlled client uses a different numeric vocation representation.

# Why this slice

- Current Universal E2E already owns the two-session lifecycle and post-cycle read-only scalar SQL evaluator, so persistence assertions extend those proven surfaces rather than creating a second runner or workflow.
- The controlled OTClient exposes read-only `LocalPlayer:getLevel()` and `LocalPlayer:getExperience()` values that are directly comparable with persisted `players` columns after relog.
- The disposable fixture provides deterministic `level=500` for `Knight 1`, allowing one real platform scenario to consume the contract without inventing item IDs, storages, quest values or map data.
- Final-gate physical evidence rejected the initial assumption that raw server `vocation=4` is numerically identical to the controlled-client value: after relog the client reported `getVocation()=1`. The first slice therefore fails closed by excluding `vocation` until an explicit normalization contract exists.
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
- [ ] Verify all required GitHub checks on the exact repaired `ci:final-gate` head and merge only if the autonomous merge gate is satisfied.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19T00:31:00+02:00
head: f6e27c67c787f001701b5782286680e2791213d6
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
  - typed player_field assertions are now strictly limited to directly comparable level and experience values and expose no arbitrary SQL through the reusable contract
  - the same validated checks are rendered into scenario-plan.lua persistence_checks for phase-2 controlled-client verification and compiled into the existing post-cycle scalar SQL path
  - action-plan-contract now uses deterministic Knight 1 level 500 as its real typed persistence proof and requires persistence_check_level plus persistence_plan markers
  - final-gate Universal Agent E2E run 29663122815 reached the real second login and proved persistence_check_level=success before failing persistence_check_vocation because the controlled client reported actual=1 while the persisted server fixture expected raw vocation=4
  - artifact 8435191728 contains result.json and client-events.tsv proving the above runtime mismatch; this was classified as a representation-contract error, not persistence loss
  - the public typed contract, tests, platform scenario, documentation, catalogue and changelog were narrowed to level/experience; vocation is rejected until an explicit normalization layer is designed
  - raw scenario-owned assertions.sql remains supported and unchanged for scenarios without typed persistence declarations
  - exact changed-file review found nine text/source/documentation paths and no OTBM maps, items.otb, client assets, database dumps, credentials or secrets
  - PR 565 remains ready for review and labeled ci:final-gate; no runner/workflow or OTBM routing paths were added
  - final-gate head 27da7cee3cd8da5359881dddde3c312fce21278d passed Agent Task Ownership and full CI before Universal Agent E2E exposed the vocation representation mismatch
  - no local Git checkout is available in the execution sandbox; focused Python unit tests are committed but are not claimed as locally executed; exact-head scenario validation and physical E2E are the available integration/runtime evidence
  - repository writes were restricted to blakinio/canary; blakinio/otclient and upstream/reference repositories remained read-only

derived:
  - typed player_field persistence evidence is fail-closed at two independent post-action layers: controlled-client value after relog and exact scalar SQL after the second safe logout
  - directly comparable fields are a required invariant for the initial shared equals contract; representation-specific fields such as vocation require a future normalization contract rather than hidden mapping assumptions
  - feature-specific expected values stay in scenario manifests while tools/e2e owns only the reusable typed capability
unknown:
  - future normalization contract for raw server vocation IDs versus controlled-client vocation representation
  - whether a later storage assertion should target a dedicated table or another persistence abstraction; do not guess in this task
  - deterministic inventory mutation fixture suitable for a reusable follow-up persistence slice
conflicts: []
blockers: []
first_failure:
  marker: agent-task-ownership/validate-changed
  evidence: Initial ownership validation rejected scalar first_failure null; the task checkpoint was corrected to the required mapping and later ownership validation passed.
rejected_hypotheses:
  - create a second persistence runner or workflow
  - treat a pre-logout static SQL check as persistence proof
  - add storage or inventory semantics without a proven deterministic fixture/contract
  - duplicate or consume unfinished OTBM route contracts from PR 562
  - force-rewrite the published task branch after main advanced
  - assume raw server vocation IDs and controlled-client vocation values are numerically identical
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
  - command: GitHub CI on final-gate head 27da7cee3cd8da5359881dddde3c312fce21278d
    result: PASS
    evidence: full CI completed successfully before physical E2E failure classification
  - command: Agent Task Ownership on final-gate head 27da7cee3cd8da5359881dddde3c312fce21278d
    result: PASS
    evidence: ownership validation completed successfully
  - command: Universal Agent E2E on final-gate head 27da7cee3cd8da5359881dddde3c312fce21278d
    result: FAIL
    evidence: run 29663122815 artifact 8435191728 proved level persistence after relog, then failed vocation exact equality because runtime actual=1 while raw persisted expectation=4; contract narrowed to comparable fields as the root-cause repair
next_action: Verify every required ci:final-gate workflow on the exact new task-record head created by this checkpoint commit. If all checks pass, PR 565 remains mergeable, and no review or ownership blocker appears, squash-merge PR 565. Make no further commit after the green repaired final-head gate.
```
