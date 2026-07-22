---
task_id: CAN-20260722-otbm-qa-012-critical-access-integrity
program_id: CAN-PROGRAM-OTBM
status: complete
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-012-critical-access-integrity-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "27a2f87d1a329d95f0d0e40622208dffbf42031f"
risk: medium
related_issue: ""
related_pr: "721"
depends_on:
  - CAN-20260722-otbm-qa-011-connectivity-resilience complete
  - OTBM Semantic Landmark Registry available
  - OTBM geometry and consistency audit available
  - OTBM spawn, boss and NPC validator available
  - Unified OTBM World Index available
blocks:
  - OTBM-QA-013 identifier, selector and collision integrity
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive: []
  shared: []
  read_only:
    - tools/ai-agent/otbm_critical_access_integrity.py
    - tools/ai-agent/otbm_critical_access_integrity_tool.py
    - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.md
    - docs/ai-agent/OTBM_CRITICAL_ACCESS_TARGETS.schema.json
    - docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.schema.json
modules_touched:
  - otbm-critical-access-integrity
reuses:
  - Unified OTBM World Index exact tile/mechanic evidence
  - OTBM Semantic Landmark Registry
  - OTBM Connectivity Resilience report
  - OTBM geometry and consistency audit
  - OTBM spawn, boss and NPC validation
public_interfaces:
  - canary-otbm-critical-access-targets-v1
  - canary-otbm-critical-access-integrity-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-012 Critical Infrastructure, House and Spawn Access Integrity

## Status

COMPLETE — bounded QA-012 implementation merged through feature PR #717. Lifecycle-only active-to-archive closure is isolated in PR #721 without feature code, schema, runtime, map, datapack, E2E, workflow, catalogue or changelog changes.

## Goal

Provide targeted static integrity checks for explicitly reviewed high-value landmarks, houses and spawn/NPC/boss access contexts without guessing semantic importance, intended public accessibility or runtime behavior.

## Delivered

- Added reviewed target contract `canary-otbm-critical-access-targets-v1` and report `canary-otbm-critical-access-integrity-v1`.
- Reused exact Semantic Landmark, QA-011 Connectivity Resilience, World Index, Geometry Audit and Spawn/NPC validation evidence rather than implementing parallel scanners or pathfinding.
- Correlated exact reviewed house `houseId`/`houseDoorId`/position evidence and canonical `rewardBossLiteral=true` boss evidence.
- Preserved strict, optimistic and executable route evidence separately and failed closed on missing, stale, truncated, mismatched or ambiguous evidence.
- Added deterministic create-new/no-clobber CLI, schemas, documentation and focused semantic/schema/output-safety tests.
- Static evidence does not prove runtime/public accessibility and v1 does not infer change-based entrance bypass/sever regressions without compatible Semantic Diff evidence.

## Merge evidence

- Feature PR: #717 — `feat(otbm): add critical access integrity analysis`.
- Final feature head: `b284845c9f371ab03b744fbe668d140e77c556a0`.
- Squash merge: `27a2f87d1a329d95f0d0e40622208dffbf42031f`.
- Exact-final-head CI run `29915659002`: success.
- Exact-final-head Agent Task Ownership run `29915658783`: success.
- Exact-final-head OTBM Map Tools run `29915658846`: success.
- Exact-final-head AI Agent Tools run `29915658786`: success.
- Ready-for-review full CI run `29915819971` on the same immutable final head: success.
- Final review audit found zero inline review threads and zero review submissions.
- Feature PR changed exactly eleven bounded implementation/test/docs/shared-doc/task paths.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T16:30:00+02:00
head: 27a2f87d1a329d95f0d0e40622208dffbf42031f
branch: docs/archive-otbm-qa-012-critical-access-integrity-717
pr: 721
status: complete
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-012-critical-access-integrity.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-012-critical-access-integrity.md
proven:
  - QA-012 feature PR 717 merged as 27a2f87d1a329d95f0d0e40622208dffbf42031f from immutable final head b284845c9f371ab03b744fbe668d140e77c556a0.
  - Exact-final CI 29915659002, Ownership 29915658783, OTBM Map Tools 29915658846 and AI Agent Tools 29915658786 passed on the immutable feature head.
  - Ready-for-review full CI 29915819971 also passed on the same immutable feature head before auto-merge.
  - PR 717 changed exactly eleven bounded paths and had zero review threads or review submissions at final audit.
  - Lifecycle PR 721 is based on current main 997343078104831ae3761e691c96fd8ff8d6cfa2 and owns only the QA-012 active/archive task-record paths.
derived:
  - OTBM-QA-013 may begin only after lifecycle PR 721 merges and a fresh live-state/ownership preflight passes.
unknown:
  - A reviewed critical-access target registry covering every real-world critical landmark, house and spawn is not guaranteed; real target evaluation remains evidence-dependent.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved feature, provenance, ownership, focused-test or merge failure remains.
rejected_hypotheses:
  - Inferring critical infrastructure from names, sprites or proximity.
  - Recomputing route, geometry or spawn evidence inside QA-012.
  - Treating static evidence as proof of runtime/public accessibility.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-012-critical-access-integrity.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-012-critical-access-integrity.md
validation:
  - command: GitHub Actions CI run 29915659002
    result: PASS
    evidence: exact-final-head repository CI passed before feature merge.
  - command: GitHub Actions Agent Task Ownership run 29915658783
    result: PASS
    evidence: exact-final-head ownership validation passed.
  - command: GitHub Actions OTBM Map Tools run 29915658846
    result: PASS
    evidence: exact-final-head focused OTBM validation passed.
  - command: GitHub Actions AI Agent Tools run 29915658786
    result: PASS
    evidence: exact-final-head AI-agent validation passed.
  - command: GitHub Actions CI run 29915819971
    result: PASS
    evidence: ready-for-review full final-gate matrix passed on the same immutable feature head.
blockers: []
next_action: Remove the active QA-012 task record, validate lifecycle CI and ownership on PR 721, then apply final-gate before the last lifecycle checkpoint commit.
```
