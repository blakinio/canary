---
task_id: CAN-20260721-otbm-qa-004-reviewed-candidate-repair
program_id: CAN-PROGRAM-OTBM
status: active
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-004-reviewed-candidate-repair-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "c35b44f04803bcd4e4bfa0c90df762d0425f88d1"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-qa-003-repair-recommendations complete
blocks:
  - OTBM-QA-005 coverage dashboard and certification model
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_reviewed_candidate_repair.py
    - tools/ai-agent/otbm_reviewed_candidate_repair_tool.py
    - tools/ai-agent/test_otbm_reviewed_candidate_repair.py
    - tools/ai-agent/test_otbm_reviewed_candidate_repair_output_safety.py
    - tools/ai-agent/test_otbm_reviewed_candidate_repair_schema.py
    - docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR.md
    - docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR_APPROVAL.schema.json
    - docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR.schema.json
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-004-reviewed-candidate-repair.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/architecture/otbm-world-quality-repair.md
    - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.md
    - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.schema.json
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.schema.json
    - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.schema.json
    - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
    - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.schema.json
modules_touched:
  - otbm-reviewed-candidate-repair
reuses:
  - OTBM-QA-003 repair recommendation
  - OTBM repair/materialization pipeline
  - Semantic OTBM Diff
  - OTBM-E2E-008 impacted Physical E2E selection
  - OTBM-E2E-009 candidate-map Physical E2E validation
public_interfaces:
  - canary-otbm-reviewed-candidate-repair-approval-v1
  - canary-otbm-reviewed-candidate-repair-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-004 Reviewed Candidate Repair Orchestration

## Status

ACTIVE — bounded implementation started from post-QA-003 lifecycle `main`.

## Goal

Create a deterministic fail-closed evidence-chain orchestrator that binds one supported QA-003 recommendation and one explicit human/review approval to exactly one existing repair/materialization pipeline result and one compatible OTBM-E2E-009 candidate validation result, without executing or duplicating any writer, materializer, Semantic Diff implementation, impacted selector, Physical E2E runner or workflow.

## Bounded slice

- Introduce `canary-otbm-reviewed-candidate-repair-approval-v1` as the explicit review authorization envelope.
- Approval must pin the exact recommendation bytes, exact source map SHA-256, exact selector, expected old state, intended target state, one canonical pipeline mutation mode and the exact existing writer/materializer-specific plan/approval evidence SHA-256.
- Introduce `canary-otbm-reviewed-candidate-repair-v1` as the auditable composed result over:
  - QA-003 recommendation;
  - explicit approval;
  - successful `canary-otbm-repair-materialization-pipeline-v1` result;
  - exact compatible Semantic Diff;
  - exact compatible OTBM-E2E-008 impacted selection;
  - exact compatible `canary-otbm-candidate-physical-validation-v1` result.
- Require recommendation state to be one of the three supported existing-path states and require deterministic mapping from recommendation capability to one existing pipeline mode.
- Require the pipeline result to prove source immutability, create-new candidate identity, exact candidate Map Quality identity and use of the exact writer/materializer authorization pinned by approval.
- Require Semantic Diff before/source and after/candidate identities to match the approved source and finalized candidate.
- Require impacted selection to pin the exact Semantic Diff bytes and the same before/after map identities.
- Require OTBM-E2E-009 evidence pins to match the exact pipeline result, Semantic Diff and impacted selection bytes.
- Report either a fully validated candidate, a fully validated candidate with exact non-impact proving no represented Physical E2E execution was required, or an explicit `physical-e2e-required` pending state when selected scenarios exist but execution was not performed.
- Keep reports external to Git and use create-new/no-clobber output semantics.

## Explicit non-goals

- No OTBM parsing/scanning, World Index construction, Script Resolution, pathfinding, rendering or map mutation.
- No invocation or reimplementation of Phase 8 patching or any TILE_AREA/raw-tile materializer.
- No invocation or reimplementation of the canonical repair/materialization pipeline.
- No recomputation of Semantic Diff or OTBM-E2E-008 selection.
- No invocation or reimplementation of Universal Physical E2E or OTBM-E2E-009.
- No approval generation; approval is caller-supplied reviewed evidence.
- No mutation-mode widening, arbitrary serializer, in-place map writes, deployment or promotion.
- No claim that approval or successful static mutation proves gameplay correctness beyond exact retained Physical E2E evidence.

## Acceptance criteria

- Identical compatible inputs produce byte-stable semantic output ordering.
- Unsupported/non-supported QA-003 recommendation states fail closed.
- Approval recommendation SHA, source SHA, selector, expected old state and intended target state exactly match QA-003 recommendation evidence.
- Approval pipeline mode exactly matches the supported recommendation capability family/mode mapping.
- Approval pins the exact existing writer/materializer-specific plan or approval format required by that mode.
- Pipeline result source SHA equals approval/recommendation source SHA; output is create-new and quality source SHA equals candidate SHA.
- Pipeline input pins contain the exact mutation authorization evidence SHA and expected format from approval.
- Semantic Diff before/after map identities equal source/candidate.
- Impacted selection pins the exact Semantic Diff bytes and compatible before/after map and World Index identities.
- OTBM-E2E-009 pins exact pipeline/Semantic Diff/selection bytes and source/candidate identities.
- Selected Physical E2E scenarios cannot yield a fully validated claim unless execution was performed successfully; exact zero-selected evidence may yield a validated-no-physical-required state.
- Output safety rejects symlinks, duplicate inputs and input/output collisions and does not clobber existing reports without explicit overwrite.
- Focused aggregation/schema/output-safety tests plus relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T17:20:00+02:00
head: c35b44f04803bcd4e4bfa0c90df762d0425f88d1
branch: feat/otbm-qa-004-reviewed-candidate-repair-20260721
pr: null
status: active
context_routes:
  - otbm
  - agent-governance
proven:
  - OTBM-QA-003 feature PR #681 merged as 31257824fe7dde510fc2885f818732861e375efb.
  - OTBM-QA-003 lifecycle PR #682 merged as c35b44f04803bcd4e4bfa0c90df762d0425f88d1.
  - Current main is identical to c35b44f04803bcd4e4bfa0c90df762d0425f88d1 at fresh post-lifecycle preflight.
  - Fresh preflight found no open OTBM-QA PR, no otbm-qa branch and no existing QA-004 task.
  - Live roadmap identifies OTBM-QA-004 Reviewed Candidate Repair Orchestration immediately after QA-003.
  - Canonical repair/materialization pipeline supports exactly one of fixed-width-attribute, tile-area, tile-replacement, tile-insertion, tile-deletion or tile-type-conversion per run and emits canary-otbm-repair-materialization-pipeline-v1.
  - OTBM-E2E-009 consumes successful pipeline evidence plus exact Semantic Diff and OTBM-E2E-008 selection and emits canary-otbm-candidate-physical-validation-v1 without adding another runner or workflow.
derived:
  - The smallest complete QA-004 v1 is an evidence-chain orchestrator/validator over explicit approval and already-produced canonical outputs; it need not execute or duplicate mutation or Physical E2E boundaries.
unknown:
  - Exact approval/report field contract until implementation and focused tests land.
conflicts: []
first_failure:
  marker: none
  evidence: No QA-004 implementation has been attempted yet.
blockers: []
next_action: Open a draft PR for this bounded ownership scope, bind related_pr, then implement the approval/report contracts, deterministic validator, CLI and focused tests before final-gate checkpointing.
```
