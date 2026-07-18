---
task_id: CAN-20260718-e2e-gameplay-005-persistence-assertions
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-GAMEPLAY-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-gameplay-005-persistence-assertions
base_branch: main
created: 2026-07-18T23:32:00+02:00
updated: 2026-07-18T23:32:00+02:00
last_verified_commit: "be7842412beb5d240e76ffd4cd18aacdc3a2dcca"
risk: medium
related_issue: ""
related_pr: ""
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
    - tests/e2e/scenarios/platform/action-plan-contract.json
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/client/**
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
  - existing action-plan-contract platform scenario
public_interfaces:
  - optional scenario.assertions.persistence list
  - persistence assertion type player_field
cross_repo_tasks: []
---

# Goal

Implement the smallest complete reusable slice of `E2E-GAMEPLAY-005`: a feature-neutral typed persistence assertion surface for durable player fields, compiled into the existing Universal Physical E2E SQL assertion path and evaluated only after the canonical `login -> physical actions -> safe logout -> persisted state -> relog -> verification window -> safe logout` cycle completes.

The first slice deliberately covers one natural persistence type only: exact integer assertions over a conservative whitelist of durable `players` fields (`level`, `vocation`, `experience`, `balance`). Feature-specific expected values remain in scenario manifests.

# Why this slice

- Current Universal E2E already executes scenario-owned read-only scalar SQL after the second safe logout, so the smallest reusable extension is typed compilation into that proven path rather than a second runner or workflow.
- The disposable fixture already provides deterministic `level` and `vocation` values for `Knight 1`, allowing one real platform scenario to consume the contract without inventing item IDs, storages, quest values or map data.
- No deterministic inventory mutation fixture or stable generic storage assertion contract was identified in the current physical platform baseline, so inventory/storage are deferred rather than guessed.

# Acceptance criteria

- [ ] Create a reusable, deterministic persistence assertion compiler with strict field/type validation and no arbitrary SQL surface.
- [ ] Extend existing scenario validation to accept optional `assertions.persistence` without creating a new runner/workflow.
- [ ] Compile typed persistence assertions into the existing post-cycle SQL assertion list in normalized manifests.
- [ ] Keep raw scenario-owned `assertions.sql` behavior backward compatible.
- [ ] Add focused tests for valid compilation, invalid types/fields/values, SQL literal safety and manifest integration.
- [ ] Update at least one real existing physical scenario to use the new typed persistence assertion mechanism.
- [ ] Preserve the current login/logout/relog sentinel and leave client/OTBM routing paths untouched.
- [ ] Update reusable-interface documentation/catalogue and changelog.
- [ ] Run focused validation and required GitHub checks on the exact final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:32:00+02:00
head: be7842412beb5d240e76ffd4cd18aacdc3a2dcca
branch: feat/e2e-gameplay-005-persistence-assertions
pr: null
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-e2e-gameplay-005-persistence-assertions.md
  - tools/e2e/persistence_assertions.py
  - tests/e2e/test_persistence_assertions.py
  - tools/e2e/run_agent_e2e.py
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - main task-start SHA is be7842412beb5d240e76ffd4cd18aacdc3a2dcca
  - PR 563 is open and unmerged at task start; its architecture defines E2E-GAMEPLAY-005 and explicitly allows persistence work independently of OTBM route integration
  - PR 562 is open and owns OTBM-to-E2E routing programme paths; this task has no path overlap and keeps those paths read-only
  - current generic gameplay driver executes physical action steps in phase 1 and preserves a phase-2 relog plus second safe logout
  - run_physical_e2e.sh evaluates scenario assertions.sql only after the physical client exits following the second session
  - current platform fixture defines Knight 1 with level 500 and vocation 4
  - MODULE_CATALOG identifies the existing Universal OTS E2E physical gameplay action-plan layer as the reusable platform surface
  - no open PR was found by targeted search for tools/e2e overlap
  - no local Git checkout is available in the execution sandbox; GitHub connector state is authoritative for branch/PR operations
  - repository writes are restricted to blakinio/canary

derived:
  - typed player_field assertions can prove durable progression/vocation/economy fields after the canonical relog cycle while reusing the existing SQL evaluator
  - compiling typed assertions during scenario resolution avoids adding a second runtime orchestrator or client driver
unknown:
  - whether a later storage assertion should target a dedicated table or another persistence abstraction; do not guess in this task
  - deterministic inventory mutation fixture suitable for a reusable first-slice physical scenario
conflicts: []
blockers: []
first_failure: null
rejected_hypotheses:
  - create a second persistence runner or workflow
  - execute feature-specific persistence checks in tools/e2e client code
  - add storage or inventory semantics without a proven deterministic fixture/contract
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-e2e-gameplay-005-persistence-assertions.md
validation:
  - command: lean startup repository/PR/path ownership review
    result: PASS
    evidence: AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, MODULE_CATALOG targeted entry, PR 562 task, PR 563 task/architecture diff, current Universal E2E runner/client lifecycle reviewed
next_action: Open an early draft PR, then implement the typed player_field persistence compiler and integrate it into run_agent_e2e.py manifest normalization with focused tests.
```
