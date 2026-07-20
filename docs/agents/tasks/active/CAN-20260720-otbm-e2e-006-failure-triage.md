---
task_id: CAN-20260720-otbm-e2e-006-failure-triage
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-006
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-006-failure-triage
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "4749654b2a8c951188dff7b7c8f363ae7068a27f"
risk: medium
related_issue: ""
related_pr: "620"
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
head: 4749654b2a8c951188dff7b7c8f363ae7068a27f
branch: feat/otbm-e2e-006-failure-triage
pr: 620
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
  - classifier contract and 26 focused classifier tests passed before the rejected final candidate
  - rejected final candidate 066d18dc18868a39b890c9e0256b95f61c597f9a passed Ownership and CI
  - its Universal run 29734058030 failed before physical execution at route-preparation metadata resolution
  - retained physical evidence proved the scenario manifest was polluted by a selection diagnostic emitted before the JSON payload
  - resolver diagnostic was moved from stdout to stderr in commit 5835b3d37a8179cf8ec901f6df0d42b0c9376404 without changing selection semantics
  - corrected code head 5835b3d37a8179cf8ec901f6df0d42b0c9376404 passed Ownership run 29736661974, CI run 29736662272 and Universal Agent E2E run 29736662236
  - current main was synchronized into the task branch through technical PR 625, producing branch sync commit cbff718c7a34307a9f7add1c572343a5b5b73249
  - focused resolve stdout-purity regression was added in commit 4749654b2a8c951188dff7b7c8f363ae7068a27f
  - ci:final-gate remains applied to PR 620
  - no pull-request reviews or unresolved review threads are present on PR 620

derived:
  - repeated retry of the rejected candidate could not fix deterministic stdout pollution
  - the bounded stderr redirect plus direct resolve stdout regression is sufficient to cover the identified integration defect
  - this checkpoint update is the intended final task mutation before exact-final-head validation
unknown:
  - exact-final-head workflow conclusions for the checkpoint commit
  - final merge SHA
  - lifecycle archive SHA
blockers: []
conflicts: []
rejected_hypotheses:
  - change scenario selection semantics
  - modify the workflow or server-selection contract to tolerate non-JSON resolver stdout
  - retry the same deterministic metadata failure without a fix
  - add a second OTBM parser, route planner, E2E runner or workflow
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tests/e2e/test_agent_e2e_resolve_stdout.py
  - tests/e2e/test_otbm_route_failure_triage.py
  - tools/e2e/otbm_route_failure_triage.py
  - tools/e2e/run_agent_e2e.py
validation:
  - command: focused classifier tests
    result: PASS
    evidence: 26 focused cases passed before the rejected final candidate
  - command: exact-head Ownership and CI on rejected candidate
    result: PASS
    evidence: runs 29734057923 and 29734058099
  - command: Universal Agent E2E on rejected candidate
    result: FAIL
    evidence: run 29734058030 and retained artifact 8458266455 identified deterministic resolver stdout pollution before route preparation
  - command: corrected code-head Ownership, CI and Universal Agent E2E
    result: PASS
    evidence: runs 29736661974, 29736662272 and 29736662236 passed on 5835b3d37a8179cf8ec901f6df0d42b0c9376404
  - command: exact-final-head gate after this checkpoint commit
    result: PENDING
    evidence: must complete on the immutable checkpoint head before readiness or merge
first_failure:
  marker: universal-e2e-route-preparation-metadata-json
  evidence: Universal run 29734058030 failed because resolver selection diagnostics preceded the JSON manifest on stdout; corrected by moving the diagnostic to stderr and adding direct stdout-purity coverage
next_action: Wait only for the exact-final-head Ownership, CI and Universal Agent E2E runs triggered by this checkpoint commit; then inspect the final diff, reviews, threads and mergeability, mark PR 620 ready, squash-merge, and archive the task if every gate is green.
```
