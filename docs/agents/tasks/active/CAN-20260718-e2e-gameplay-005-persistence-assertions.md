---
task_id: CAN-20260718-e2e-gameplay-005-persistence-assertions
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-persistence-assertions-v2
base_branch: main
created: 2026-07-18T23:32:00+02:00
updated: 2026-07-18T23:59:00+02:00
last_verified_commit: "c1c0d10ed1e758cb72728be5fe22458cd9d9e61a"
risk: medium
related_issue: ""
related_pr: ""
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

- Current Universal E2E already owns the two-session lifecycle and post-cycle read-only scalar SQL evaluator, so persistence assertions can extend those proven surfaces rather than creating a second runner or workflow.
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
- [ ] Run focused validation and required GitHub checks on the exact final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:59:00+02:00
head: c1c0d10ed1e758cb72728be5fe22458cd9d9e61a
branch: feat/e2e-gameplay-005-persistence-assertions-v2
pr: pending
status: implementing
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
  - PR 562 merged as 59916930b08bafb87dcddec89230d16b8e1f0712 and its route-consumption prerequisites remain separate from this persistence slice
  - PR 563 merged as c1c0d10ed1e758cb72728be5fe22458cd9d9e61a and the merged architecture explicitly permits E2E-GAMEPLAY-005 in parallel with route work
  - merged architecture requires M3 persistence evidence across safe logout, persisted-state verification, relog and re-verification
  - current generic gameplay driver executes physical action steps in phase 1 and preserves a phase-2 relog plus second safe logout
  - run_physical_e2e.sh evaluates scenario assertions.sql only after the physical client exits following the second session
  - controlled blakinio/otclient exposes LocalPlayer getLevel/getExperience and Player getVocation read APIs without client changes
  - current platform fixture defines Knight 1 with level 500 and vocation 4
  - implementation was developed on draft PR 565 but that branch diverged from main after PR 563 merged and is being superseded without force-rewriting published history
  - no local Git checkout is available in the execution sandbox; GitHub connector state is authoritative for branch/PR operations
  - repository writes are restricted to blakinio/canary
derived:
  - typed player_field assertions are checked twice: through the real client after relog and through the existing scalar SQL evaluator after the second safe logout
  - compiling typed assertions during scenario resolution and executing them in the existing phase-2 driver preserves the single orchestrator and lifecycle
unknown:
  - whether a later storage assertion should target a dedicated table or another persistence abstraction; do not guess in this task
  - deterministic inventory mutation fixture suitable for a reusable first-slice physical scenario
conflicts: []
blockers: []
first_failure:
  marker: agent-task-ownership/validate-changed
  evidence: Initial PR 565 ownership validation rejected scalar first_failure null; the task checkpoint was corrected to the required mapping before migration to the current-main branch.
rejected_hypotheses:
  - create a second persistence runner or workflow
  - treat a pre-logout static SQL check as persistence proof
  - add storage or inventory semantics without a proven deterministic fixture/contract
  - force-rewrite the published PR 565 branch after main advanced
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-e2e-gameplay-005-persistence-assertions.md
  - tools/e2e/persistence_assertions.py
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_persistence_assertions.py
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
validation:
  - command: lean startup repository/PR/path ownership review
    result: PASS
    evidence: AGENTS.md, repository/context routing, merged PR 562 programme, merged PR 563 architecture/ADR/programme and current Universal E2E lifecycle reviewed
  - command: exact PR 565 runner and client-driver diff review
    result: PASS
    evidence: implementation changes are limited to typed persistence validation, manifest SQL compilation, persistence_checks rendering and phase-two client verification
  - command: GitHub CI workflow at 4609a1e393ba4b55a6f1dcd611979c9e9038145b
    result: PASS
    evidence: workflow run 29662197722 completed success before branch migration; exact-current-head validation remains required
next_action: Open the replacement draft PR from current main, restore the verified nine-file implementation diff, close PR 565 as superseded, then run current-head validation and final gate.
```
