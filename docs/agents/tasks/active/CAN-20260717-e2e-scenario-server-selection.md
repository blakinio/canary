---
task_id: CAN-20260717-e2e-scenario-server-selection
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-SERVER-SELECTION-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-scenario-server-selection
base_branch: main
created: 2026-07-17T09:55:00+02:00
updated: 2026-07-17T09:55:00+02:00
last_verified_commit: "317c1c4235377c388883aa2fd425d324f8ce4d2e"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260716-universal-e2e-gameplay-capabilities-v2
blocks:
  - physical Instanced Test Arena combat scenario
owned_paths:
  exclusive:
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/run_physical_e2e.sh
    - tests/e2e/test_agent_e2e_scenario_plan.py
    - tests/e2e/test_agent_e2e_server_selection.py
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tools/e2e/client/agent_e2e_scenario.lua
    - tests/e2e/scenarios/login/scenario.json
    - tests/e2e/scenarios/movement/physical-movement.json
    - src/game/instance/**
    - data-canary/world/canary.otbm
modules_touched:
  - Universal OTS E2E physical server selection
reuses:
  - existing Universal Agent E2E lifecycle and workflow
  - existing scenario.server.datapack and scenario.server.map manifest fields
  - existing global-map download path for the canonical otservbr scenario
public_interfaces:
  - scenario.server.datapack materialized as the physical runtime datapack directory
  - scenario.server.map materialized as the physical runtime map basename
cross_repo_tasks: []
---

# Goal

Make the already-declared `scenario.server.datapack` and `scenario.server.map` fields drive the existing physical E2E server runtime, without creating a second orchestrator or changing the canonical login/relog scenario.

# Acceptance criteria

- [ ] Export the validated scenario datapack and map values through the existing scenario environment contract.
- [ ] Reject unsafe datapack/map path values before runtime materialization.
- [ ] Resolve the selected map only inside the repository-selected datapack world directory.
- [ ] Preserve the existing downloaded `data-otservbr-global/world/otservbr.otbm` behavior for the canonical default scenario.
- [ ] Fail closed when a non-default selected map is absent instead of downloading an arbitrary manifest-selected target.
- [ ] Write the selected datapack and map into generated `config.lua` and runtime provenance evidence.
- [ ] Keep `.github/workflows/universal-agent-e2e.yml` and the controlled OTClient driver unchanged.
- [ ] Add focused regression coverage for environment export, safe-name rejection, default global selection and repository-local non-default selection.
- [ ] Pass exact-head applicable CI and Universal Agent E2E while preserving canonical login/relog behavior.
- [ ] Audit final changed paths and merge only after the exact-final-head gate is green.

# Proven blocker

- `scenario.server.datapack` and `scenario.server.map` are currently validated but omitted from `github_environment()`.
- `tools/e2e/run_physical_e2e.sh` hardcodes `data-otservbr-global/world/otservbr.otbm`, `dataPackDirectory = "data-otservbr-global"`, and `mapName = "otservbr"`.
- `InstanceArenaService`'s two reviewed regions are explicitly evidence-backed against `data-canary/world/canary.otbm`.
- A bounded read-only scan of the exact physical-E2E `otservbr` snapshot (`a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`) found zero tiles across both configured Instance Arena region boxes, so the arena cannot be reused physically under the current hardcoded global-map runtime.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T09:55:00+02:00
head: 317c1c4235377c388883aa2fd425d324f8ce4d2e
branch: feat/e2e-scenario-server-selection
pr: null
status: investigating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/run_agent_e2e.py
  - tools/e2e/run_physical_e2e.sh
  - tests/e2e/test_agent_e2e_scenario_plan.py
  - tests/e2e/test_agent_e2e_server_selection.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - current task base is blakinio/canary main 317c1c4235377c388883aa2fd425d324f8ce4d2e
  - Universal OTS E2E action-plan platform from PR 446 is merged and must be extended rather than replaced
  - scenario validation already requires non-empty server.datapack and server.map strings
  - github_environment currently exports client, fixture and timing fields but not server.datapack or server.map
  - physical runner currently hardcodes data-otservbr-global and otservbr for both map materialization and generated config
  - canonical login/relog scenario declares data-otservbr-global and otservbr, so materializing its declared values can preserve current behavior
  - InstanceArenaService configured regions are backed by data-canary/world/canary.otbm rather than the downloaded otservbr map
  - exact-hash physical otservbr map contains zero tiles in both configured Instance Arena region boxes
  - open PR 457 owns only its movement scenario/task record and keeps tools/e2e read-only
  - open PR 462 is confined to Security Validation paths
  - open PR 453 is documentation-only and does not own tools/e2e
  - no open PR currently owns the proposed server-selection paths
  - no workflow or controlled-client change is required for this bounded contract repair
derived:
  - honoring the existing manifest server fields is the smallest reusable change that can let future physical scenarios select the already-reviewed data-canary arena map without duplicating lifecycle code
  - safe basename/segment validation plus repository confinement can prevent manifest path traversal while keeping the existing declarative contract
  - arbitrary map download support is unnecessary; only the canonical default global map needs the existing configured download fallback
unknown:
  - exact focused test file structure best matching current tests/e2e conventions
  - whether data-canary physical login succeeds with the maintained client after this contract is wired; exact runtime proof belongs to applicable CI and the later combat scenario
conflicts: []
first_failure:
  marker: scenario-server-fields-not-materialized
  evidence: run_agent_e2e.py validates server.datapack/map but does not export them, while run_physical_e2e.sh hardcodes the global datapack/map
rejected_hypotheses:
  - create a second E2E workflow or orchestrator
  - repoint InstanceArenaService production regions to unrelated global-map coordinates solely for E2E
  - add arbitrary manifest-provided map URLs or filesystem paths
  - alter the canonical login/relog scenario
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
validation: []
blockers: []
next_action: Open a draft PR, inspect current E2E test conventions, then implement the smallest fail-closed materialization of existing server.datapack/map fields with focused tests while keeping workflow and controlled OTClient paths unchanged.
```
