---
task_id: CAN-20260721-otbm-qa-009-content-completeness
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/archive-otbm-qa-009-content-completeness-700
base_branch: main
created: 2026-07-21
updated: 2026-07-22
last_verified_commit: "11e301005fd43f847b1a316f75fd8427abcaed98"
risk: medium
related_issue: ""
related_pr: "704"
depends_on:
  - CAN-20260721-otbm-qa-008-dependency-blast-radius complete
  - CAN-20260721-otbm-qa-005-coverage-dashboard complete
blocks:
  - OTBM-QA-010 quest state reachability
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-009-content-completeness.md
    - docs/agents/tasks/archive/CAN-20260721-otbm-qa-009-content-completeness.md
  shared: []
  read_only:
    - tools/ai-agent/otbm_content_completeness.py
    - tools/ai-agent/otbm_content_completeness_tool.py
    - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.md
    - docs/ai-agent/OTBM_CONTENT_COMPLETENESS_MANIFEST.schema.json
    - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.schema.json
modules_touched:
  - otbm-content-completeness
reuses:
  - OTBM-QA-008 Dependency and Blast-Radius Graph
  - OTBM-QA-005 Coverage Dashboard
public_interfaces:
  - canary-otbm-content-completeness-manifest-v1
  - canary-otbm-content-completeness-audit-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-009 Dead/Orphaned Content and Quest Completeness Audit

## Status

READY — feature implementation is merged through PR #700; lifecycle-only archive follow-up is isolated in draft PR #704.

## Goal

Identify selected-scope dead/orphaned-content candidates and summarize reviewed quest/mechanic completeness conservatively by composing exact QA-008 dependency evidence and QA-005 coverage evidence without rescanning the map, rebuilding dependency logic, executing Lua or claiming runtime quest completion.

## Delivered

- Added `canary-otbm-content-completeness-manifest-v1` and `canary-otbm-content-completeness-audit-v1`.
- Required exact-compatible QA-008 Dependency/Blast-Radius and QA-005 Coverage Dashboard provenance.
- Added explicit reviewed quest/mechanic stages and orphan/disconnection checks without inferring quest topology.
- Preserved `confirmed`, `map-only`, `script-only`, `unresolved`, `conflicting` and `not-applicable` classifications.
- Kept unresolved QA-008 boundaries fail-closed instead of promoting them to false map-only/script-only absence.
- Kept `requirementsSatisfied` selected-scope/static only and explicitly retained runtime gameplay completion as unproven.
- Added fail-closed CLI/output safety, schemas, documentation and focused tests.

## Explicit non-goals

- No OTBM parser/scanner, World Index, Script Resolution, Storage Dependency Graph, Reachability/pathfinding or QA-008 graph recomputation.
- No dynamic Lua execution or Physical E2E execution.
- No global dead-content claim, automatic repair/mutation, certification or E2E scenario prioritization.

## Merge evidence

- Feature PR: #700 — `feat(otbm): add dead/orphaned content completeness audit`.
- Final feature head: `e15a178125acf3da20040e7d493ea8593e2ccf59`.
- Squash merge: `11e301005fd43f847b1a316f75fd8427abcaed98`.
- Exact-final-head CI run `29872380096`: success.
- Exact-final-head Agent Task Ownership run `29872372611`: success.
- Exact-final-head OTBM Map Tools run `29872372560`: success.
- Exact-final-head AI Agent Tools run `29872372558`: success.
- Final review audit found zero inline review threads and zero review submissions.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T00:26:00+02:00
head: 24b835781d16cb5b4a5f779483d6952f3c58a1df
branch: docs/archive-otbm-qa-009-content-completeness-700
pr: 704
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-009-content-completeness.md
  - docs/agents/tasks/archive/CAN-20260721-otbm-qa-009-content-completeness.md
proven:
  - QA-008 feature PR #694 and lifecycle PR #698 are merged and complete.
  - QA-009 feature PR #700 merged as 11e301005fd43f847b1a316f75fd8427abcaed98 from final head e15a178125acf3da20040e7d493ea8593e2ccf59.
  - Exact-final QA-009 CI 29872380096, Ownership 29872372611, OTBM Map Tools 29872372560 and AI Agent Tools 29872372558 passed.
  - PR #700 changed exactly nine bounded implementation/task paths and had zero review threads or review submissions at final audit.
  - Current main is identical to QA-009 squash merge 11e301005fd43f847b1a316f75fd8427abcaed98.
  - Lifecycle-only follow-up is open as draft PR #704 and currently owns only the active/archive task-record paths.
  - QA-009 runtime gameplay completion remains explicitly unproven; the delivered audit is selected-scope static evidence only.
derived:
  - The only remaining QA-009 work is lifecycle-only movement of this completed task record from active to archive on PR #704.
unknown:
  - MODULE_CATALOG shared-path row was not modified in the bounded feature branch; delivered contracts are documented in OTBM_CONTENT_COMPLETENESS.md and task metadata.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved feature, provenance, ownership, focused-test or final-gate failure remains.
rejected_hypotheses:
  - Inferring quest stages or orphaned content from names or proximity.
  - Treating missing selected-scope dependency edges as global dead content.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-009-content-completeness.md
  - docs/agents/tasks/archive/CAN-20260721-otbm-qa-009-content-completeness.md
validation:
  - command: GitHub Actions CI run 29872380096
    result: PASS
    evidence: Exact-final-head full repository CI completed successfully before feature merge.
  - command: GitHub Actions Agent Task Ownership run 29872372611
    result: PASS
    evidence: Exact-final-head ownership validation passed.
  - command: GitHub Actions OTBM Map Tools run 29872372560
    result: PASS
    evidence: Exact-final-head OTBM focused validation passed.
  - command: GitHub Actions AI Agent Tools run 29872372558
    result: PASS
    evidence: Exact-final-head AI-agent validation passed.
blockers: []
next_action: On draft PR #704, complete the lifecycle-only active-to-archive move for this task without behavior changes; merge it after lifecycle gates, then perform a fresh preflight before any QA-010 work.
```
