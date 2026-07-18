---
task_id: CAN-20260718-e2e-gameplay-005-persistence-assertions
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-persistence-assertions
base_branch: main
created: 2026-07-18T23:32:00+02:00
updated: 2026-07-18T23:47:00+02:00
last_verified_commit: "4609a1e393ba4b55a6f1dcd611979c9e9038145b"
risk: medium
related_issue: ""
related_pr: "565"
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM existing Universal Physical E2E two-session lifecycle
  - PR #563 Universal E2E gameplay validation architecture/roadmap (read-only planning dependency; unmerged at task start)
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
- [ ] Update reusable-interface documentation/catalogue and changelog.
- [ ] Run focused validation and required GitHub checks on the exact final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:47:00+02:00
head: 4609a1e393ba4b55a6f1dcd611979c9e9038145b
branch: feat/e2e-gameplay-005-persistence-assertions
pr: 565
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
  - main task-start SHA is be7842412beb5d240e76ffd4cd18aacdc3a2dcca
  - PR 565 is the early draft PR for this task in blakinio/canary
  - PR 562 merged to main as 59916930b08bafb87dcddec89230d16b8e1f0712; its programme still requires route-export and bridge implementation contracts before E2E route consumption, so E2E-GAMEPLAY-002 is not a higher-priority unblocked replacement for this task
  - PR 563 was open and unmerged at task start; its architecture defines E2E-GAMEPLAY-005 and explicitly allows persistence work independently of OTBM route integration
  - current generic gameplay driver executes physical action steps in phase 1 and preserves a phase-2 relog plus second safe logout
  - run_physical_e2e.sh evaluates scenario assertions.sql only after the physical client exits following the second session
  - controlled blakinio/otclient exposes LocalPlayer getLevel/getExperience and Player getVocation read APIs without client changes
  - current platform fixture defines Knight 1 with level 500 and vocation 4
  - typed player_field checks are rendered into scenario-plan.lua persistence_checks for phase-2 controlled-client verification and compiled into final post-cycle SQL checks
  - action-plan-contract now requires persistence_check_level, persistence_check_vocation and persistence_plan success markers
  - exact PR runner diff contains only intended persistence integration after repair of the accidental suite-validation message
  - CI workflow completed successfully at head 4609a1e393ba4b55a6f1dcd611979c9e9038145b
  - no open PR was found by targeted search for agent_e2e_scenario.lua ownership overlap
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
  evidence: First ownership run on head 4609a1e393ba4b55a6f1dcd611979c9e9038145b failed because checkpoint first_failure was encoded as scalar null; this checkpoint corrects it to the required mapping.
rejected_hypotheses:
  - create a second persistence runner or workflow
  - treat a pre-logout static SQL check as persistence proof
  - add storage or inventory semantics without a proven deterministic fixture/contract
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-e2e-gameplay-005-persistence-assertions.md
  - tools/e2e/persistence_assertions.py
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_persistence_assertions.py
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
validation:
  - command: lean startup repository/PR/path ownership review
    result: PASS
    evidence: AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, MODULE_CATALOG targeted entry, PR 562 programme, PR 563 task/architecture diff and current Universal E2E lifecycle reviewed
  - command: exact PR 565 runner and client-driver diff review
    result: PASS
    evidence: runner changes are limited to typed persistence validation, manifest SQL compilation and persistence_checks rendering; client changes are limited to phase-2 typed checks and plan contract extension
  - command: GitHub CI workflow at 4609a1e393ba4b55a6f1dcd611979c9e9038145b
    result: PASS
    evidence: workflow run 29662197722 completed success
  - command: Agent Task Ownership at 4609a1e393ba4b55a6f1dcd611979c9e9038145b
    result: FAIL
    evidence: validate-changed rejected scalar first_failure null; exact artifact recorded the schema error and this checkpoint repairs it
next_action: Update MODULE_CATALOG.md and CHANGELOG.md for the reusable persistence interface, then inspect current-head CI including Universal Agent E2E and prepare the final-head gate.
```
