---
task_id: CAN-20260717-e2e-scenario-server-selection
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-SERVER-SELECTION-001
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/e2e-scenario-server-selection
base_branch: main
created: 2026-07-17T09:55:00+02:00
updated: 2026-07-17T12:45:00+02:00
last_verified_commit: "9d6133fe51cdb8cfa127fe7431b2ea6a8c2ba2ab"
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
    - .github/workflows/universal-agent-e2e.yml
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/test_agent_e2e_scenario_plan.py
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
- [x] Keep the controlled OTClient driver unchanged and preserve the single existing Universal Agent E2E workflow.
- [x] Ensure changes to the server-selection helper trigger that existing physical E2E workflow.
- [x] Add focused regression coverage for safe-name rejection, repository confinement, default global selection, repository-local non-default selection, nested symlink escape and environment materialization.
- [ ] Pass exact-final-head applicable CI and Universal Agent E2E while preserving canonical login/relog behavior.
- [x] Audit final changed paths, synchronize with current main, clear reviews/threads and preserve the exact-final-head gate before the final checkpoint commit.

# Proven blocker

- `scenario.server.datapack` and `scenario.server.map` were validated but not materialized by the physical runner.
- `tools/e2e/run_physical_e2e.sh` hardcoded `data-otservbr-global/world/otservbr.otbm`, `dataPackDirectory = "data-otservbr-global"`, and `mapName = "otservbr"`.
- `InstanceArenaService`'s two reviewed regions are explicitly evidence-backed against `data-canary/world/canary.otbm`.
- A bounded read-only scan of the exact physical-E2E `otservbr` snapshot (`a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`) found zero tiles across both configured Instance Arena region boxes, so the arena cannot be reused physically under the hardcoded global-map runtime.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T12:45:00+02:00
head: 9d6133fe51cdb8cfa127fe7431b2ea6a8c2ba2ab
branch: feat/e2e-scenario-server-selection
pr: 468
status: ready
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - .github/workflows/universal-agent-e2e.yml
  - tools/e2e/server_selection.py
  - tools/e2e/run_physical_e2e.sh
  - tests/e2e/test_agent_e2e_server_selection.py
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 468 is ready for review
  - Universal OTS E2E action-plan platform from PR 446 is merged and is extended rather than replaced
  - scenario validation already requires non-empty server.datapack and server.map strings
  - canonical login/relog scenario declares data-otservbr-global and otservbr
  - InstanceArenaService configured regions are backed by data-canary/world/canary.otbm rather than the downloaded otservbr map
  - exact-hash physical otservbr map contains zero tiles in both configured Instance Arena region boxes
  - open PR 457 owns only its movement scenario/task record and explicitly keeps shared tools/e2e and the workflow read-only absent a separately owned platform blocker
  - latest overlap audits found no competing owner for this task's server-selection helper or workflow path
  - tools/e2e/server_selection.py resolves only safe single-segment datapack/map names inside the repository and rejects datapack, world and map symlink/path escape
  - only the canonical data-otservbr-global/otservbr pair retains the existing configured map-download fallback
  - non-default selected maps must already exist and be non-empty under the selected datapack world directory
  - run_physical_e2e.sh invokes the resolver after canonical scenario resolution and before runtime startup
  - generated config.lua receives the selected datapack and map while preserving the existing physical lifecycle
  - runtime-contract.txt records selected datapack/map and runtime-hashes.txt includes the server-selection helper
  - controlled OTClient driver and canonical login/relog scenario remain unchanged
  - workflow change is limited to adding tools/e2e/server_selection.py to the existing pull_request path filter so helper-only changes cannot bypass physical E2E
  - workflow patch audit shows exactly that one added path and no other workflow drift
  - shared CHANGELOG.md and MODULE_CATALOG.md were normalized byte-for-byte to current main and are no longer part of the net PR diff
  - focused local validation passed py_compile and 8 of 8 server-selection unittests
  - final net changed-file audit contains exactly six bounded server-selection/task paths
  - pull-request review-thread audit found no unresolved review threads and review audit found no submitted reviews requiring action
  - branch was synchronized to current main by a non-force fast-forward to GitHub's generated merge result 9d6133fe51cdb8cfa127fe7431b2ea6a8c2ba2ab
  - ci:final-gate label remains applied before this final checkpoint commit
  - this checkpoint commit is intended to be the final feature-branch commit; no post-green feature commit is permitted

derived:
  - honoring the existing manifest server fields is the smallest reusable change that can let future physical scenarios select the already-reviewed data-canary arena map without duplicating lifecycle code
  - arbitrary map download support is unnecessary and remains disallowed for non-default selections
  - adding the helper to the existing workflow path filter is safer and smaller than refactoring the large scenario resolver solely to inherit an existing trigger
  - a later combat task can own its privileged account/player fixture separately without broadening this platform prerequisite
unknown:
  - exact-final-head CI and Universal Agent E2E conclusions after this final checkpoint commit
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
  - refactor the large scenario resolver only to make the new helper inherit its workflow path trigger
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - docs/agents/tasks/active/CAN-20260717-e2e-scenario-server-selection.md
  - docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md
  - tests/e2e/test_agent_e2e_server_selection.py
  - tools/e2e/run_physical_e2e.sh
  - tools/e2e/server_selection.py
validation:
  - command: focused local py_compile of server_selection.py and test_agent_e2e_server_selection.py
    result: PASS
    evidence: both files compiled with exit code 0
  - command: focused local test_agent_e2e_server_selection.py
    result: PASS
    evidence: 8 tests ran successfully with exit code 0; unrelated sandbox artifact_tool warmup stderr did not affect the test process result
  - command: PR diff audit for tools/e2e/run_physical_e2e.sh
    result: PASS
    evidence: diff is confined to server selection resolution, selected map materialization/config, dynamic cleanup and provenance hashing
  - command: PR diff audit for .github/workflows/universal-agent-e2e.yml
    result: PASS
    evidence: exactly one pull_request path-filter entry was added for tools/e2e/server_selection.py
  - command: final net changed-file and shared-document diff audit
    result: PASS
    evidence: exactly six expected paths; CHANGELOG.md and MODULE_CATALOG.md are byte-for-byte identical to current main
  - command: review and overlap audit
    result: PASS
    evidence: no unresolved review threads, no submitted reviews requiring action and no competing live owner for the server-selection paths
  - command: final-gate preparation
    result: PASS
    evidence: PR is ready and ci:final-gate remains applied before this checkpoint commit
blockers: []
next_action: Make no further feature-branch changes. Require Agent Task Ownership, CI and full Universal Agent E2E success on the exact final checkpoint head; recheck current main/reviews before merge; squash merge only if all exact-head evidence is green, otherwise repair the concrete failure and repeat final-gate preparation.
```
