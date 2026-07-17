---
task_id: CAN-20260717-e2e-scenario-server-selection
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-SERVER-SELECTION-001
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/e2e-scenario-server-selection
base_branch: main
created: 2026-07-17T09:55:00+02:00
updated: 2026-07-17T10:16:00+02:00
last_verified_commit: "a1b12772df5945ce44af1f73a6da7f74e10f0fc7"
risk: medium
related_issue: ""
related_pr: "468"
depends_on:
  - CAN-20260716-universal-e2e-gameplay-capabilities-v2
blocks:
  - physical Instanced Test Arena combat scenario
owned_paths:
  exclusive:
    - tools/e2e/server_selection.py
    - tools/e2e/run_physical_e2e.sh
    - tests/e2e/test_agent_e2e_server_selection.py
    - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
    - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/test_agent_e2e_scenario_plan.py
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

- [x] Materialize the validated scenario datapack and map values through the existing scenario manifest/environment boundary.
- [x] Reject unsafe datapack/map path values before runtime materialization.
- [x] Resolve the selected map only inside the repository-selected datapack world directory.
- [x] Preserve the existing downloaded `data-otservbr-global/world/otservbr.otbm` behavior for the canonical default scenario.
- [x] Fail closed when a non-default selected map is absent instead of downloading an arbitrary manifest-selected target.
- [x] Write the selected datapack and map into generated `config.lua` and runtime provenance evidence.
- [x] Keep `.github/workflows/universal-agent-e2e.yml` and the controlled OTClient driver unchanged.
- [x] Add focused regression coverage for safe-name rejection, repository confinement, default global selection, repository-local non-default selection and environment materialization.
- [ ] Pass exact-head applicable CI and Universal Agent E2E while preserving canonical login/relog behavior.
- [ ] Audit final changed paths and merge only after the exact-final-head gate is green.

# Proven blocker

- `scenario.server.datapack` and `scenario.server.map` were validated but not materialized by the physical runner.
- `tools/e2e/run_physical_e2e.sh` hardcoded `data-otservbr-global/world/otservbr.otbm`, `dataPackDirectory = "data-otservbr-global"`, and `mapName = "otservbr"`.
- `InstanceArenaService`'s two reviewed regions are explicitly evidence-backed against `data-canary/world/canary.otbm`.
- A bounded read-only scan of the exact physical-E2E `otservbr` snapshot (`a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`) found zero tiles across both configured Instance Arena region boxes, so the arena cannot be reused physically under the hardcoded global-map runtime.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T10:16:00+02:00
head: a1b12772df5945ce44af1f73a6da7f74e10f0fc7
branch: feat/e2e-scenario-server-selection
pr: 468
status: implementing
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - tools/e2e/server_selection.py
  - tools/e2e/run_physical_e2e.sh
  - tests/e2e/test_agent_e2e_server_selection.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - current task base is blakinio/canary main 317c1c4235377c388883aa2fd425d324f8ce4d2e
  - draft PR 468 is the authoritative delivery branch for this task
  - Universal OTS E2E action-plan platform from PR 446 is merged and is extended rather than replaced
  - scenario validation already requires non-empty server.datapack and server.map strings
  - canonical login/relog scenario declares data-otservbr-global and otservbr
  - InstanceArenaService configured regions are backed by data-canary/world/canary.otbm rather than the downloaded otservbr map
  - exact-hash physical otservbr map contains zero tiles in both configured Instance Arena region boxes
  - open PR 457 owns only its movement scenario/task record and keeps tools/e2e read-only
  - open PR 462 is confined to Security Validation paths
  - open PR 453 is documentation-only and does not own tools/e2e
  - no open PR owns this task's server-selection implementation paths
  - tools/e2e/server_selection.py resolves only safe single-segment datapack/map names inside the repository and rejects symlink/path escape
  - only the canonical data-otservbr-global/otservbr pair retains the existing configured map-download fallback
  - non-default selected maps must already exist and be non-empty under the selected datapack world directory
  - run_physical_e2e.sh invokes the resolver after canonical scenario resolution and before runtime startup
  - generated config.lua now receives the selected datapack and map while preserving all other physical lifecycle configuration
  - runtime-contract.txt records selected datapack/map and runtime-hashes.txt includes the server-selection helper
  - workflow and controlled OTClient driver remain unchanged
derived:
  - honoring the existing manifest server fields is the smallest reusable change that can let future physical scenarios select the already-reviewed data-canary arena map without duplicating lifecycle code
  - arbitrary map download support is unnecessary and remains disallowed for non-default selections
  - a later combat task can own its privileged account/player fixture separately without broadening this platform prerequisite
unknown:
  - exact-head CI and Universal Agent E2E conclusion after the implementation/docs batch
  - whether data-canary physical login succeeds with a later dedicated combat fixture; this task does not claim that runtime proof
conflicts: []
first_failure:
  marker: scenario-server-fields-not-materialized
  evidence: run_agent_e2e.py validated server.datapack/map but the physical runner ignored them and hardcoded the global datapack/map
rejected_hypotheses:
  - create a second E2E workflow or orchestrator
  - repoint InstanceArenaService production regions to unrelated global-map coordinates solely for E2E
  - add arbitrary manifest-provided map URLs or filesystem paths
  - alter the canonical login/relog scenario
  - add privileged combat fixtures to this platform prerequisite
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_agent_e2e_server_selection.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/server_selection.py
validation:
  - command: PR diff audit for tools/e2e/run_physical_e2e.sh
    result: PASS
    evidence: diff is confined to server selection resolution, selected map materialization/config, dynamic cleanup and provenance hashing
blockers: []
next_action: Fix the documentation table typo for wait_creature, add the required module-catalog/changelog discovery entries, inspect exact-head CI/ownership/E2E results and repair only real failures before final-gate synchronization.
```
