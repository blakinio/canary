---
task_id: CAN-20260723-otbm-qa-007-continuous-assurance
program_id: CAN-PROGRAM-OTBM
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-006-007-certification-assurance-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "bd3806aa9f273a1af6e4505485bb198d79b57fa6"
risk: medium
related_issue: ""
related_pr: "759"
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

VALIDATING — bounded fail-closed orchestration over exact QA-002, QA-001 and QA-006 evidence plus an explicit execution ledger. No validator, E2E runner, workflow, map, datapack or runtime mutation is authorized.

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
updated_at: 2026-07-23T11:22:00+02:00
head: bd3806aa9f273a1af6e4505485bb198d79b57fa6
branch: feat/otbm-qa-006-007-certification-assurance-20260723
pr: 759
status: validating
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
  - Focused local combined QA-006/007 validation passed 20 semantic, schema and output-safety tests before publication.
  - PR 759 pre-final CI run 29993845854 succeeded on head 96375947b358eb3256473b9c9aae80082582baff.
  - PR 759 pre-final Agent Task Ownership run 29993845514 succeeded on the same head.
  - PR 759 pre-final OTBM Map Tools run 29993845673 succeeded on the same head after dependency-free schema-test correction.
  - PR 759 pre-final AI Agent Tools job in run 29993845590 completed successfully on the same head.
  - ci:final-gate was applied before the final QA-006 and QA-007 checkpoint commits.
derived:
  - QA-007 remains a pure composition gate and uses an exact execution ledger instead of creating a second validator or E2E runner.
unknown:
  - Exact-final-head CI, Ownership, OTBM Map Tools and AI Agent Tools conclusions after this immutable final checkpoint commit.
conflicts: []
first_failure:
  marker: checkpoint-and-test-boundary
  evidence: Initial ownership validation required related_pr to bind both active tasks to PR 759; subsequent OTBM validation exposed only test-time jsonschema imports unavailable in the focused workflow. Both checkpoint and test-only dependency issues were corrected, after which all pre-final required validations passed.
rejected_hypotheses:
  - Rerun Semantic Diff or selected validators inside QA-007.
  - Create another Physical E2E runner or workflow.
  - Treat a passed OTBM gate as deployment authorization.
  - Add jsonschema as a production or workflow dependency solely for focused schema tests.
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
validation:
  - command: local focused QA-006/007 test run
    result: PASS
    evidence: 20 targeted semantic, schema and output-safety tests passed before publication.
  - command: GitHub Actions CI 29993845854
    result: PASS
    evidence: Pre-final CI passed on 96375947b358eb3256473b9c9aae80082582baff.
  - command: GitHub Actions Agent Task Ownership 29993845514
    result: PASS
    evidence: Pre-final ownership validation passed.
  - command: GitHub Actions OTBM Map Tools 29993845673
    result: PASS
    evidence: Pre-final focused OTBM suite passed after the test-only dependency correction.
  - command: GitHub Actions AI Agent Tools 29993845590
    result: PASS
    evidence: Pre-final AI Agent Tools job completed successfully.
blockers: []
next_action: Verify all exact-final-head required checks on the immutable PR head created by this commit; if green and review/scope audit is clean, mark PR 759 ready and merge without further feature commits.
```
