---
task_id: CAN-20260720-otbm-e2e-006-failure-triage
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-006
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-006-failure-triage
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "3fe0130a408d201d0ca846f86a37b0ab20479932"
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
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - tools/e2e/prepare_otbm_route.py
    - tools/e2e/run_physical_e2e.sh
    - tools/e2e/run_agent_e2e.py
    - tools/e2e/route_plan_execution.py
    - tools/e2e/client/agent_e2e_route.lua
    - tools/e2e/client/agent_e2e_scenario.lua
modules_touched:
  - OTBM-aware Universal E2E deterministic failure triage
reuses:
  - existing Universal E2E retained artifact directory
  - result.json
  - client-events.tsv
  - route-preparation.json
  - route-*-preflight.json
  - route-*.json
  - existing route executor failure codes
  - existing safe logout/persistence/relog markers
public_interfaces:
  - deterministic machine-readable OTBM route physical E2E first-failure classification artifact
cross_repo_tasks: []
---

# Goal

Deliver `OTBM-E2E-006 — Automatic E2E failure triage` as a deterministic classifier over existing retained Universal Physical E2E route artifacts, without adding another OTBM parser, route planner, workflow, runner or client lifecycle.

# Acceptance criteria

- [x] Emit `canary-otbm-e2e-failure-triage-v1` machine-readable output.
- [x] Support all fourteen failure categories defined by the programme.
- [x] Prefer structured artifacts and explicit existing failure codes over natural-language guessing.
- [x] Preserve exact first-failure route edge/transition context only when evidence supports it.
- [x] Distinguish route resolution from exact-map preflight failure using existing evidence.
- [x] Emit explicit success, not-applicable and fail-closed unclassified states.
- [x] Keep Universal workflow, physical runner, OTClient and persistence implementation unchanged.
- [x] Cover all required categories plus success/not-applicable/unclassified behavior with focused tests.
- [x] Catalogue the reusable classifier without overwriting current merged shared-index content.
- [x] Apply `ci:final-gate` before the immutable final checkpoint commit.
- [ ] Require exact-final-head Agent Task Ownership, CI and Universal Agent E2E success.
- [ ] Require clean review/thread state, fresh live-main overlap review and mergeability before squash merge.
- [ ] Complete active-to-archive lifecycle after feature merge before unblocking OTBM-E2E-007.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: 2bf4f45774b3374a72a1e5f1b66851366dd6bdbd
branch: feat/otbm-e2e-006-failure-triage
pr: 620
status: ready
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tests/e2e/test_otbm_route_failure_triage.py
  - tools/e2e/otbm_route_failure_triage.py
proven:
  - canonical OTBM-E2E-006 scope is deterministic first-failure classification from route plan plus current physical artifacts
  - classifier format is canary-otbm-e2e-failure-triage-v1 schemaVersion 1
  - all fourteen programme categories are implemented
  - ambiguous evidence fails closed instead of being promoted to a guessed category
  - MOVEMENT_TIMEOUT maps to BLOCKED_TILE without claiming which actor or dynamic condition caused the block
  - completed successful route edges are cleared before later persistence or relog failures are classified
  - exact current classifier and tests passed Python bytecode compilation and 26 focused unittest cases in isolated validation
  - Agent Task Ownership run 29733310895 passed on implementation head 2bf4f45774b3374a72a1e5f1b66851366dd6bdbd
  - CI run 29733310982 passed on implementation head 2bf4f45774b3374a72a1e5f1b66851366dd6bdbd
  - current live main at checkpoint preparation is 3fe0130a408d201d0ca846f86a37b0ab20479932
  - merged main drift from #615 is gameplay persistence plus shared catalogue and from #619 is Oteryn programme documentation
  - classifier and focused test paths do not overlap those main changes
  - branch MODULE_CATALOG preserves current main security, soul-persistence and route-plan rows and adds only the separate OTBM triage row
  - open PR #514 touches shared catalogue metadata but its security row is semantically disjoint from the OTBM triage row
  - ci:final-gate was applied to PR #620 before this checkpoint commit
  - no OTBM, World Index, pathfinder, Universal workflow, physical runner, OTClient execution or persistence source was modified

derived:
  - route-preparation failure is classified only after exact preflight evidence is checked first
  - transition-specific categories require retained exact edge evidence
  - the first explicit client error plus an active or explicitly failed route edge gives deterministic route failure context
  - successful completed route edges must not leak into later lifecycle failure context
  - a workflow post-processing hook is outside the smallest canonical OTBM-E2E-006 scope because the programme requires classification over current artifacts
unknown:
  - exact final checkpoint commit SHA and exact-final-head workflow conclusions until this commit exists and checks complete
  - whether live main advances again before merge
  - final feature merge SHA and lifecycle archive PR/merge SHA until closure completes
blockers: []
conflicts: []
rejected_hypotheses:
  - build a second OTBM parser, World Index, route planner, E2E workflow or physical runner
  - modify OTClient route execution solely to classify already-retained explicit failure events
  - infer unsupported interactions or runtime blockers without deterministic evidence
  - attach a previously successful route edge to a later persistence or relog failure
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tests/e2e/test_otbm_route_failure_triage.py
  - tools/e2e/otbm_route_failure_triage.py
validation:
  - command: python -m py_compile tools/e2e/otbm_route_failure_triage.py
    result: PASS
    evidence: exact current classifier contents completed with process exit code 0 in isolated validation
  - command: python -m unittest discover -s tests/e2e -p test_otbm_route_failure_triage.py -v
    result: PASS
    evidence: exact current classifier and tests passed 26 focused cases including stale-route-context regression
  - command: Agent Task Ownership on 2bf4f45774b3374a72a1e5f1b66851366dd6bdbd
    result: PASS
    evidence: workflow run 29733310895
  - command: CI on 2bf4f45774b3374a72a1e5f1b66851366dd6bdbd
    result: PASS
    evidence: workflow run 29733310982; incremental reuse is not substituted for focused Python validation
  - command: live-main semantic overlap audit before final checkpoint
    result: PASS
    evidence: current main 3fe0130a408d201d0ca846f86a37b0ab20479932 has no classifier/test overlap and shared catalogue content is preserved
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: initial ownership run 29731915649 rejected the checkpoint because derived and first_failure were absent; the task record was corrected without weakening validation
next_action: Treat this commit as the immutable final feature head; require exact-final-head Ownership, CI and Universal Agent E2E, then perform final review/thread/live-main/mergeability checks, mark PR #620 ready, squash merge with expected head SHA, verify main, and complete active-to-archive lifecycle before OTBM-E2E-007.
```
