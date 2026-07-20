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
    - tools/e2e/run_agent_e2e.py
    - tests/e2e/test_agent_e2e_pr_scenario_selection.py
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
- [ ] Keep `run_agent_e2e.py resolve` stdout valid JSON while selection diagnostics go to stderr.
- [ ] Add focused regression coverage for resolver stdout purity.
- [ ] Create a new immutable final checkpoint after the bounded fix.
- [ ] Require exact-final-head Ownership, CI and Universal Agent E2E success.
- [ ] Complete review/overlap/mergeability gates and post-merge lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: 066d18dc18868a39b890c9e0256b95f61c597f9a
branch: feat/otbm-e2e-006-failure-triage
pr: 620
status: implementing
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tests/e2e/test_agent_e2e_pr_scenario_selection.py
  - tests/e2e/test_otbm_route_failure_triage.py
  - tools/e2e/otbm_route_failure_triage.py
  - tools/e2e/run_agent_e2e.py
proven:
  - classifier contract and 26 focused classifier tests passed before the rejected final candidate
  - rejected final candidate 066d18dc18868a39b890c9e0256b95f61c597f9a passed Ownership and CI
  - its Universal run 29734058030 failed before physical execution at route-preparation metadata resolution
  - retained physical evidence contains a scenario-manifest file with a selection diagnostic line before the JSON payload
  - the workflow redirects resolver stdout directly into that manifest and then parses it as JSON
  - run_agent_e2e.py emits the selection diagnostic on stdout
  - moving only that diagnostic to stderr preserves scenario selection semantics and downstream JSON
  - open PRs have no writer overlap on run_agent_e2e.py or the existing PR-selection regression test
  - ci:final-gate remains applied to PR #620

derived:
  - repeated retry cannot fix deterministic stdout pollution
  - the smallest correction is one stderr redirect plus a focused regression test
  - the rejected final candidate must be superseded by a new final head and full final gates
unknown:
  - corrected implementation SHA and new final checkpoint SHA until the fix is committed
  - exact-final-head workflow conclusions after correction
  - final merge and lifecycle archive SHAs
blockers:
  - final Universal E2E cannot pass until resolver stdout remains machine-readable JSON
conflicts: []
rejected_hypotheses:
  - change scenario selection semantics
  - modify the workflow or server-selection contract to tolerate non-JSON resolver stdout
  - retry the same deterministic metadata failure without a fix
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-006-failure-triage.md
  - tests/e2e/test_otbm_route_failure_triage.py
  - tools/e2e/otbm_route_failure_triage.py
validation:
  - command: focused classifier tests
    result: PASS
    evidence: 26 focused cases passed before the rejected final candidate
  - command: exact-final-head Ownership and CI on rejected candidate
    result: PASS
    evidence: runs 29734057923 and 29734058099
  - command: exact-final-head Universal Agent E2E on rejected candidate
    result: FAIL
    evidence: run 29734058030 and retained artifact 8458266455 identify deterministic resolver stdout pollution before route preparation
first_failure:
  marker: Agent Task Ownership checkpoint schema
  evidence: initial task checkpoint omitted required fields and was corrected without weakening validation
next_action: Apply the claimed resolver stderr fix and stdout-purity regression, run focused tests, then create a new immutable final checkpoint and repeat exact-final-head gates.
```
