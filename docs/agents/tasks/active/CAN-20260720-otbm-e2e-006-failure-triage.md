---
task_id: CAN-20260720-otbm-e2e-006-failure-triage
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-006
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-006-failure-triage-final
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "a87ed337cab28c569ef3276cd0b9ed5d89c87779"
risk: medium
related_issue: ""
related_pr: "628"
depends_on:
  - merged and archived OTBM-E2E-005 / PR #600
  - existing Universal Physical E2E artifact lifecycle
blocks:
  - OTBM-E2E-007 and later second-stage routing enhancements
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
    - tools/e2e/otbm_route_failure_triage.py
    - tests/e2e/test_otbm_route_failure_triage.py
    - tests/e2e/test_agent_e2e_resolve_stdout.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - tools/e2e/run_agent_e2e.py
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - tools/e2e/prepare_otbm_route.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/route_plan_execution.py
    - tools/e2e/client/agent_e2e_route.lua
    - tools/e2e/client/agent_e2e_scenario.lua
modules_touched:
  - OTBM-aware Universal E2E deterministic failure triage
  - Universal E2E resolver stdout purity
reuses:
  - existing Universal E2E retained artifact directory
  - existing route/preflight/plan/client/result evidence
public_interfaces:
  - deterministic machine-readable OTBM route physical E2E first-failure classification artifact
cross_repo_tasks: []
---

# Goal

Deliver OTBM-E2E-006 deterministic failure triage and preserve the existing E2E architecture. The exact-final-head gate exposed one pre-existing resolver output-contract defect; repair only that bounded shared seam.

# Acceptance criteria

- [x] Implement all fourteen programme triage categories plus success/not-applicable/unclassified states.
- [x] Preserve deterministic first-failure evidence and fail closed on ambiguity.
- [x] Keep OTBM parsing, routing, workflow, physical runner and client lifecycle unchanged.
- [x] Add focused classifier coverage and reusable module catalogue entry.
- [x] Keep `run_agent_e2e.py resolve` stdout valid JSON while selection diagnostics go to stderr.
- [x] Add focused regression coverage for resolver stdout purity.
- [x] Create a new immutable final checkpoint after the bounded fix.
- [ ] Require exact-final-head Ownership, CI and Universal Agent E2E success.
- [ ] Complete review/overlap/mergeability gates and post-merge lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: a87ed337cab28c569ef3276cd0b9ed5d89c87779
branch: feat/otbm-e2e-006-failure-triage-final
pr: 628
status: validating
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tests/e2e/test_agent_e2e_resolve_stdout.py
  - tests/e2e/test_otbm_route_failure_triage.py
  - tools/e2e/otbm_route_failure_triage.py
  - tools/e2e/run_agent_e2e.py
proven:
  - OTBM-E2E-006 classifier and direct resolve stdout-purity regression are present on clean PR 628 with exactly six bounded changed files
  - resolver selection diagnostics moved to stderr without changing selection semantics; corrected code head 5835b3d37a8179cf8ec901f6df0d42b0c9376404 previously passed Ownership CI and Universal Agent E2E
  - original PR 620 was closed as superseded after non-ancestral squash synchronization polluted its review diff; clean replay PR 628 was created from current main without force-push
  - ci:final-gate is applied to PR 628
  - exact-head Agent Task Ownership run 29770068815 passed on a87ed337cab28c569ef3276cd0b9ed5d89c87779 including focused unit tests and checkpoint validation
  - exact-head CI run 29770069685 passed on a87ed337cab28c569ef3276cd0b9ed5d89c87779 with Required success
  - Universal Agent E2E run 29770069732 on a87ed337cab28c569ef3276cd0b9ed5d89c87779 has passed validation-scope decision database bootstrap scenario resolution and exact Canary build
  - Universal run 29770069732 still had controlled OTClient build in progress at handoff checkpoint time

derived:
  - the original resolver JSON failure is repaired because the exact-head Resolve scenario job now succeeds
  - OTBM-E2E-006 is waiting only for completion of the exact-head Universal Agent E2E gate and final merge review
unknown:
  - final conclusion of Universal Agent E2E run 29770069732
  - live branch head after this handoff checkpoint commit
  - final merge and lifecycle archive SHAs
conflicts: []
first_failure:
  marker: universal-e2e-route-preparation-metadata-json
  evidence: run 29734058030 failed because resolver diagnostics preceded JSON on stdout; the stderr fix and direct regression removed that failure and exact-head Resolve scenario now passes
rejected_hypotheses:
  - retry the original deterministic metadata failure without code change: run 29734058030 proved stdout pollution required a fix
  - tolerate non-JSON resolver stdout in workflow: bounded stderr redirect preserves the machine-readable contract instead
  - weaken checkpoint validation: unsupported PENDING result was corrected to the existing schema without changing validator rules
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tests/e2e/test_agent_e2e_resolve_stdout.py
  - tests/e2e/test_otbm_route_failure_triage.py
  - tools/e2e/otbm_route_failure_triage.py
  - tools/e2e/run_agent_e2e.py
validation:
  - command: Agent Task Ownership run 29770068815
    result: PASS
    evidence: exact head a87ed337cab28c569ef3276cd0b9ed5d89c87779 passed focused tests ownership and checkpoint validation
  - command: CI run 29770069685
    result: PASS
    evidence: exact head a87ed337cab28c569ef3276cd0b9ed5d89c87779 completed successfully with Required success
  - command: Universal Agent E2E run 29770069732
    result: NOT_RUN
    evidence: run was still in progress at handoff; scenario resolution database bootstrap and exact Canary build had passed while controlled OTClient build remained in progress
blockers: []
next_action: Verify the live head created by this handoff checkpoint commit and its exact-head Ownership CI and Universal Agent E2E state; if all required gates are green, inspect final diff reviews threads and mergeability, mark PR 628 ready, squash-merge, then archive the task lifecycle.
```
