---
task_id: CAN-20260716-universal-e2e-gameplay-capabilities-v2
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: "OTS-E2E-GAMEPLAY-V1"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/universal-e2e-gameplay-capabilities-v3
base_branch: main
created: 2026-07-16T22:30:00+02:00
updated: 2026-07-16T22:30:00+02:00
last_verified_commit: ""
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM
blocks:
  - future physical movement scenario tasks
  - future physical combat scenario tasks
  - future physical item/inventory/container scenario tasks
  - future physical quest/NPC/depot/bank/trade scenario tasks
  - future multi-client and runtime-fault scenario tasks
owned_paths:
  exclusive:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/test_agent_e2e_scenario_plan.py
    - tests/e2e/scenarios/platform/action-plan-contract.json
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities-v2.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/client/agent_e2e.lua
    - tests/e2e/scenarios/login/scenario.json
modules_touched:
  - Universal OTS E2E automation
reuses:
  - existing scenario discovery and validation
  - existing physical Canary + MariaDB + controlled OTClient lifecycle
  - existing two-session login/logout/relog correctness sentinel
  - maintained OTClient g_game/g_map/LocalPlayer Lua bindings
public_interfaces:
  - optional scenario.steps declarative client action plan
  - generated scenario-plan.lua artifact
  - generic agent_e2e_scenario.lua physical client driver
cross_repo_tasks: []
---

# Goal

Extend the existing Universal OTS E2E platform with a reusable, declarative physical-client gameplay action plan without creating another orchestrator and without overwriting the active OAM-006 shared workflow contract. Preserve the exact-head Canary/MariaDB/controlled-OTClient lifecycle and the two-session login/logout/relog persistence sentinel while adding bounded client actions and observations reusable by feature-owned physical scenarios.

# Acceptance criteria

- [ ] Preserve schema-v1 login/relog behavior when `steps` is absent.
- [ ] Add strict optional declarative `steps` validation with bounded action types and exact fields.
- [ ] Reject unknown actions/fields, unsafe text, invalid directions, invalid IDs and unbounded plans.
- [ ] Resolve a validated plan into deterministic `scenario-plan.lua` beside the scenario manifest.
- [ ] Add a generic OTClient Lua driver using verified maintained-client bindings.
- [ ] Support bounded wait, walk, talk/spell text, visible-target attack, inventory-item use, quest-log request and channel-list request.
- [ ] Support online, position, floor, health, inventory, visible-creature and attack-state observations.
- [ ] Record deterministic action start/result markers for existing required-marker assertions.
- [ ] Fail closed on timeout, missing player/target/item, unexpected disconnect, login/connection error or unknown runtime action.
- [ ] Add focused Python regressions including declared-action ↔ runtime-driver parity.
- [ ] Register a platform-owned action-plan contract scenario with no guessed map coordinates, item IDs, NPCs or monsters.
- [ ] Document safety and feature-owned follow-up boundaries.
- [ ] Keep `.github/workflows/universal-agent-e2e.yml` and `run_physical_e2e.sh` read-only in this task.
- [ ] Update catalogue/changelog narrowly.
- [ ] Pass exact-final-head CI, ownership and full physical E2E gate before merge.

# Confirmed context

- Repository writes are limited to `blakinio/canary`.
- This replacement branch was created directly from current `main`; draft PR #439 was closed without merge to avoid rewriting published history.
- The existing Universal Agent E2E lifecycle already owns MariaDB, exact server builds, controlled OTClient builds, matching assets, Xvfb, packet/session evidence and cleanup.
- OAM-006 shares `.github/workflows/universal-agent-e2e.yml`; this task does not edit that path.
- Maintained OTClient bindings required by the generic actions were previously verified at pinned ref `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T22:30:00+02:00
head: replacement-branch-start
branch: feat/universal-e2e-gameplay-capabilities-v3
pr: ""
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/client/agent_e2e_scenario.lua
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tests/e2e/scenarios/platform/action-plan-contract.json
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities-v2.md
proven:
  - replacement branch was created directly from current main
  - old PR 439 was closed without merge rather than force-pushed
  - existing physical E2E lifecycle and maintained-client API evidence are reusable
  - prior draft implementation passed focused plan tests and repeated repository CI/ownership checks before replacement
  - no concrete map coordinates, item IDs, NPC names or monster names are invented by the platform contract
derived:
  - generic declarative actions are the safest reusable platform layer before feature-owned fixture scenarios
unknown:
  - final replacement PR number
  - exact final-head physical E2E result
conflicts:
  - OAM-006 owns shared workflow .github/workflows/universal-agent-e2e.yml; this task keeps it read-only
first_failure:
  marker: superseded draft PR 439 / behind-main strict mergeability
  evidence: work was moved to a clean branch from current main instead of force-pushing published history
rejected_hypotheses:
  - force-pushing published history is acceptable for synchronization
  - one giant scenario should invent feature-specific fixture identifiers
  - a second physical E2E orchestrator is required
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-universal-e2e-gameplay-capabilities-v2.md
validation: []
blockers: []
next_action: Reapply the already-audited bounded gameplay action-plan implementation on this clean current-main branch, open the replacement draft PR, then run focused and repository validation.
```
