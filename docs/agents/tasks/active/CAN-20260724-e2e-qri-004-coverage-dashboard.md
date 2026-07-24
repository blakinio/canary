---
task_id: CAN-20260724-e2e-qri-004-coverage-dashboard
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QRI-004
status: planned
agent: "GPT-5.6 Thinking"
branch: docs/e2e-qri-004-compact-handover
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "502ae8d54b9245f9608783612cf622becbea6454"
risk: medium
related_issue: ""
related_pr: "885"
depends_on:
  - E2E-QRI-005 merged result envelope and lifecycle closure
  - E2E-QRI-006 merged cleanup certification and lifecycle closure
blocks:
  - E2E-QRI-004 implementation and delivery
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md
  shared: []
  read_only:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-quality-resilience-roadmap.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - tools/e2e/result_envelope.py
    - tools/e2e/result_envelope_impl.py
    - tools/e2e/cleanup_certification.py
    - tests/e2e/scenarios/**
modules_touched:
  - Universal E2E factual coverage dashboard
reuses:
  - canary-universal-e2e-result-envelope-v1 schema version 3
  - canary-universal-e2e-cleanup-certification-v1 schema version 1
public_interfaces: []
cross_repo_tasks: []
---

# E2E-QRI-004 factual coverage dashboard

## Goal

Prepare the bounded continuation for a factual M0-M5 and orthogonal quality-dimension coverage dashboard that consumes existing Universal E2E evidence contracts without creating another runner, workflow, result envelope or inferred coverage model.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T18:07:00+02:00
head: 502ae8d54b9245f9608783612cf622becbea6454
branch: docs/e2e-qri-004-compact-handover
pr: 885
status: investigating
context_routes:
  - agent-governance
  - universal-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md
proven:
  - E2E-QRI-005 delivery PR 850, lifecycle PR 861 and discovery PR 869 established the single schema-v3 canary-universal-e2e-result-envelope-v1 contract.
  - E2E-QRI-006 delivery PR 871, hardening PR 875 and lifecycle PR 881 established canary-universal-e2e-cleanup-certification-v1 and physically proved cleanup 18 of 18 with basename-only client events.
  - E2E-QRI-001, E2E-QRI-002 and E2E-QRI-003 are delivered foundations, including the representative promotion-combat-persistence M4 sentinel.
  - The E2E automation programme names E2E-QRI-004 as the next recommended package before E2E-QRI-022.
  - The result envelope keeps M0-M5 evidence maturity separate from orthogonal quality dimensions and preserves attempts, failures, warnings and unknowns.
  - Cleanup certification is an independent quality dimension and does not imply gameplay success or any other quality dimension.
  - Fresh handover preflight found no earlier open E2E-QRI pull request or active QRI-004 owner; draft PR 885 now owns only this continuation task record.
derived:
  - QRI-004 should aggregate only exact retained result and cleanup evidence and must fail closed rather than infer coverage from scenario registration, documentation or artifact presence.
  - Implementation paths and the dashboard output contract require a fresh reuse and ownership inventory before they are claimed.
unknown:
  - Whether a canonical factual coverage dashboard, report generator or equivalent consumer already exists under another module name.
  - The exact registered scenario inventory and which scenarios currently emit complete schema-v3 result and cleanup evidence.
  - The minimum stable dashboard output format, grouping keys and historical evidence-retention boundary.
  - Whether retained GitHub artifacts alone are sufficient for the first factual baseline or a scheduled evidence collection seam is required.
conflicts: []
first_failure:
  marker: none
  evidence: QRI-004 implementation preflight has not started; no owned defect is established.
rejected_hypotheses:
  - Treat scenario registration or documentation as proof of executed M0-M5 or quality-dimension coverage.
  - Create a second E2E runner, workflow, result envelope or cleanup evidence path for the dashboard.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md
validation:
  - command: live E2E-QRI programme and dependency review
    result: PASS
    evidence: QRI-005 and QRI-006 are merged and lifecycle-closed; the programme recommends QRI-004 next.
  - command: live open-PR and ownership search
    result: PASS
    evidence: No earlier open E2E-QRI PR or active QRI-004 owner was found; PR 885 is the bounded continuation owner.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260724-e2e-qri-004-coverage-dashboard.md --require-checkpoint
    result: NOT_RUN
    evidence: Agent Task Ownership must validate this PR-aware checkpoint commit.
blockers: []
next_action: Inventory existing result-envelope consumers, scenario registries and coverage-report modules, then select the smallest QRI-004 output contract and exact owned paths without changing runtime state.
```
