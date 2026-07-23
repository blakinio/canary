---
task_id: CAN-20260723-otbm-qa-007-continuous-assurance
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-006-007-certification-assurance-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "419536ce3dfe452f7af0a23c8c1f771d190d2eb5"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260723-otbm-qa-006-region-quest-certification complete in same bounded delivery
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_continuous_assurance.py
    - tools/ai-agent/otbm_continuous_assurance_tool.py
    - tools/ai-agent/test_otbm_continuous_assurance.py
    - tools/ai-agent/test_otbm_continuous_assurance_output_safety.py
    - tools/ai-agent/test_otbm_continuous_assurance_schema.py
    - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.md
    - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE_EXECUTION.schema.json
    - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.schema.json
    - docs/agents/tasks/active/CAN-20260723-otbm-qa-007-continuous-assurance.md
  shared: []
  read_only:
    - tools/ai-agent/otbm_map_change_regression.py
    - tools/ai-agent/otbm_world_health.py
    - tools/ai-agent/otbm_region_quest_certification.py
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
modules_touched:
  - otbm-continuous-assurance
reuses:
  - canary-otbm-map-change-regression-v1
  - canary-otbm-world-health-v1
  - canary-otbm-region-quest-certification-v1
public_interfaces:
  - canary-otbm-continuous-assurance-execution-v1
  - canary-otbm-continuous-assurance-v1
cross_repo_tasks: []
---

# CAN-20260723 — OTBM-QA-007 Continuous World Assurance Gate

## Status

IMPLEMENTING — bounded fail-closed orchestration over exact QA-002, QA-001 and QA-006 evidence plus an explicit execution ledger. No validator, E2E runner, workflow, map, datapack or runtime mutation is authorized.

## Goal

Emit one auditable assurance result for an exact before/after map change by verifying selected validation execution, World Health deltas and certification deltas without recomputing underlying evidence.

## Scope

- Require exact compatible before/after map and World Index identities.
- Require execution-ledger result sets to exactly match QA-002 selected static validators and represented selected Physical E2E scenarios.
- Fail on failed/not-run selected validation.
- Fail on QA-002 static fail-closed uncertainty or manual physical selection requirements.
- Fail on positive problem-count deltas in explicit World Health dimensions.
- Fail when a previously represented certification target disappears, decreases level or becomes stale.
- Emit deterministic blocker codes and an auditable certification delta.
- Never suppress unrelated non-OTBM suites or authorize deployment.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T10:40:00+02:00
head: 419536ce3dfe452f7af0a23c8c1f771d190d2eb5
branch: feat/otbm-qa-006-007-certification-assurance-20260723
pr: null
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_continuous_assurance.py
  - tools/ai-agent/otbm_continuous_assurance_tool.py
  - tools/ai-agent/test_otbm_continuous_assurance.py
  - tools/ai-agent/test_otbm_continuous_assurance_output_safety.py
  - tools/ai-agent/test_otbm_continuous_assurance_schema.py
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.md
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE_EXECUTION.schema.json
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.schema.json
  - docs/agents/tasks/active/CAN-20260723-otbm-qa-007-continuous-assurance.md
proven:
  - QA-002 already owns deterministic static-validator and represented Physical E2E selection.
  - QA-001 already owns explicit World Health aggregation.
  - QA-006 provides formal bounded C0-C7 certification in the same delivery chain.
derived:
  - QA-007 can remain a pure composition gate and use an exact execution ledger instead of creating a second validator or E2E runner.
unknown:
  - Exact feature-head CI outcomes until the implementation branch is validated.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation failure observed before branch validation.
rejected_hypotheses:
  - Rerun Semantic Diff or selected validators inside QA-007.
  - Create another Physical E2E runner or workflow.
  - Treat a passed OTBM gate as deployment authorization.
changed_paths:
  - tools/ai-agent/otbm_continuous_assurance.py
  - tools/ai-agent/otbm_continuous_assurance_tool.py
  - tools/ai-agent/test_otbm_continuous_assurance.py
  - tools/ai-agent/test_otbm_continuous_assurance_output_safety.py
  - tools/ai-agent/test_otbm_continuous_assurance_schema.py
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.md
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE_EXECUTION.schema.json
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.schema.json
  - docs/agents/tasks/active/CAN-20260723-otbm-qa-007-continuous-assurance.md
proven:
  - QA-002 already owns deterministic static-validator and represented Physical E2E selection.
  - QA-001 already owns explicit World Health aggregation.
  - QA-006 provides formal bounded C0-C7 certification in the same delivery chain.
derived:
  - QA-007 can remain a pure composition gate and use an exact execution ledger instead of creating a second validator or E2E runner.
unknown:
  - Exact feature-head CI outcomes until the implementation branch is validated.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation failure observed before branch validation.
rejected_hypotheses:
  - Rerun Semantic Diff or selected validators inside QA-007.
  - Create another Physical E2E runner or workflow.
  - Treat a passed OTBM gate as deployment authorization.
changed_paths:
  - tools/ai-agent/otbm_continuous_assurance.py
  - tools/ai-agent/otbm_continuous_assurance_tool.py
  - tools/ai-agent/test_otbm_continuous_assurance.py
  - tools/ai-agent/test_otbm_continuous_assurance_output_safety.py
  - tools/ai-agent/test_otbm_continuous_assurance_schema.py
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.md
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE_EXECUTION.schema.json
  - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.schema.json
  - docs/agents/tasks/active/CAN-20260723-otbm-qa-007-continuous-assurance.md
validation: []
blockers: []
next_action: Implement and validate QA-007 on the bounded combined QA-006/007 delivery branch.
```
