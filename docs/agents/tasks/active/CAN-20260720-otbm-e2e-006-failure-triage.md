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
last_verified_commit: "c9e41d4515480a4776886e7d1eab5d51e6899c9e"
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
head: c9e41d4515480a4776886e7d1eab5d51e6899c9e
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
  - classifier contract and 26 focused classifier tests passed before the rejected final candidate
  - Universal run 29734058030 exposed deterministic resolver stdout pollution before route preparation
  - resolver diagnostics were moved to stderr in 5835b3d37a8179cf8ec901f6df0d42b0c9376404 without changing selection semantics
  - corrected code head 5835b3d37a8179cf8ec901f6df0d42b0c9376404 passed Ownership 29736661974 CI 29736662272 and Universal Agent E2E 29736662236
  - direct resolve stdout-purity regression is preserved in the clean replay
  - clean replay branch started from main 9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5 with exactly six bounded OTBM-E2E-006 changed files
  - ci:final-gate was applied to PR 628 before final checkpoint mutations
  - original PR 620 was closed as superseded without force-pushing
  - first clean final checkpoint c9e41d4515480a4776886e7d1eab5d51e6899c9e failed only checkpoint schema because PENDING is not an allowed validation result

derived:
  - repeated retry of the rejected candidate could not fix deterministic stdout pollution
  - the bounded stderr redirect plus direct resolve stdout regression covers the identified integration defect
  - replacing checkpoint validation result PENDING with NOT_RUN is the smallest schema-only correction
unknown:
  - exact-final-head workflow conclusions for this schema-corrected checkpoint commit
  - final merge SHA
  - lifecycle archive SHA
blockers: []
conflicts: []
rejected_hypotheses:
  - change scenario selection semantics
  - tolerate non-JSON resolver stdout in the workflow
  - retry the same deterministic metadata failure without a fix
  - weaken checkpoint validation to accept unsupported result values
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
  - command: Universal Agent E2E on rejected candidate
    result: FAIL
    evidence: run 29734058030 identified deterministic resolver stdout pollution before route preparation
  - command: corrected code-head Ownership CI and Universal Agent E2E
    result: PASS
    evidence: runs 29736661974 29736662272 and 29736662236 passed on 5835b3d37a8179cf8ec901f6df0d42b0c9376404
  - command: clean current-main replay audit
    result: PASS
    evidence: replay head f9790611629e34199d7e18c45adc22282c248c91 was one commit ahead of main and zero behind with exactly six bounded changed files
  - command: first clean final checkpoint Ownership
    result: FAIL
    evidence: run 29769967380 rejected only unsupported validation result PENDING in the task checkpoint
  - command: exact-final-head gate after this schema correction
    result: NOT_RUN
    evidence: Ownership CI and Universal Agent E2E must complete on the new immutable head before readiness or merge
first_failure:
  marker: universal-e2e-route-preparation-metadata-json
  evidence: Universal run 29734058030 failed because resolver selection diagnostics preceded the JSON manifest on stdout; corrected by moving the diagnostic to stderr and adding direct stdout-purity coverage
next_action: Run and inspect exact-final-head Ownership CI and Universal Agent E2E on this schema-corrected checkpoint commit; if green, verify final diff reviews threads and mergeability, mark PR 628 ready, squash-merge, and archive the task.
```
