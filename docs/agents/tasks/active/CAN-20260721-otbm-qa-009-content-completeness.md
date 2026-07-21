---
task_id: CAN-20260721-otbm-qa-009-content-completeness
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-009-content-completeness-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "1aabdb80bd0b847d3354cbd26e8c7f3890c899cb"
risk: medium
related_issue: ""
related_pr: "700"
depends_on:
  - CAN-20260721-otbm-qa-008-dependency-blast-radius complete
  - CAN-20260721-otbm-qa-005-coverage-dashboard complete
blocks:
  - OTBM-QA-010 quest state reachability
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_content_completeness.py
    - tools/ai-agent/otbm_content_completeness_tool.py
    - tools/ai-agent/test_otbm_content_completeness.py
    - tools/ai-agent/test_otbm_content_completeness_output_safety.py
    - tools/ai-agent/test_otbm_content_completeness_schema.py
    - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.md
    - docs/ai-agent/OTBM_CONTENT_COMPLETENESS_MANIFEST.schema.json
    - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.schema.json
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-009-content-completeness.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.md
    - docs/ai-agent/OTBM_DEPENDENCY_GRAPH.schema.json
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.md
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.schema.json
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

READY — bounded QA-009 implementation is complete in PR #700; exact-final-head gates remain before merge.

## Goal

Identify selected-scope dead/orphaned-content candidates and summarize reviewed quest/mechanic completeness conservatively by composing exact QA-008 dependency evidence and QA-005 coverage evidence without rescanning the map, rebuilding dependency logic, executing Lua or claiming runtime quest completion.

## Bounded slice

- Add an explicit reviewed completeness manifest for selected `quest` and `mechanic-set` targets.
- Model reviewed quest stages including entry, source trigger, storage, mechanic, door/lever/passage, transition/teleport, boss/spawn, reward and exit/return evidence.
- Reference exact QA-008 dependency node IDs, existing QA-008 query IDs and QA-005 target/dimension requirements.
- Add reviewed orphan/disconnection checks over exact QA-008 node/edge relations and counterpart kinds.
- Preserve `confirmed`, `map-only`, `script-only`, `unresolved`, `conflicting` and `not-applicable` classifications.
- Emit deterministic findings and selected-scope `requirementsSatisfied` without promoting static completeness to runtime gameplay proof.
- Keep generated reports outside Git with create-new/no-clobber output safety.

## Explicit non-goals

- No OTBM parser/scanner, World Index, Script Resolution, Storage Dependency Graph, Reachability/pathfinding or QA-008 graph recomputation.
- No dynamic Lua execution or Physical E2E execution.
- No quest-stage inference from names, proximity, sprites, source proximity or chat history.
- No global dead-content claim from selected-scope absence.
- No automatic repair, mutation, certification or downstream scenario prioritization.

## Acceptance criteria

- QA-008 Dependency Graph and QA-005 Coverage Dashboard must pin the same current map and World Index; the reviewed manifest pins that same pair.
- Unknown dependency node, dependency query, coverage target or coverage dimension fails closed.
- Required stages remain incomplete when declared node/path/coverage evidence is unresolved, conflicting, stale or missing.
- Existing unresolved QA-008 edges never become `map-only`/`script-only` merely because no proven edge exists.
- `map-only`/`script-only` are emitted only from an explicit reviewed missing-side classification.
- Orphan checks use bounded reviewed direction/relation/counterpart-kind rules and do not infer global absence.
- `runtimeGameplayCompletionProven` and `runtimeGameplayCompletionClaimed` remain false.
- Output safety rejects symlinks, duplicate inputs, input/output collisions and no-clobber violations.
- Focused semantic/schema/output-safety tests plus relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T00:12:00+02:00
head: 1aabdb80bd0b847d3354cbd26e8c7f3890c899cb
branch: feat/otbm-qa-009-content-completeness-20260721
pr: 700
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_content_completeness.py
  - tools/ai-agent/otbm_content_completeness_tool.py
  - tools/ai-agent/test_otbm_content_completeness.py
  - tools/ai-agent/test_otbm_content_completeness_output_safety.py
  - tools/ai-agent/test_otbm_content_completeness_schema.py
  - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.md
  - docs/ai-agent/OTBM_CONTENT_COMPLETENESS_MANIFEST.schema.json
  - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.schema.json
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-009-content-completeness.md
proven:
  - QA-008 feature PR #694 merged as d760ce44c55b9aa6f01e80d2d407f6833938bdce and lifecycle PR #698 merged as 7f32462c0e55f1efa397438652bb41f7e200f3d9.
  - Current main remained identical to 7f32462c0e55f1efa397438652bb41f7e200f3d9 through the QA-009 pre-final overlap check.
  - QA-009 delivers canary-otbm-content-completeness-manifest-v1 and canary-otbm-content-completeness-audit-v1 over exact compatible QA-008 and QA-005 evidence.
  - Required stages compose explicit dependency nodes, existing QA-008 query reachability results and exact QA-005 dimensions; the audit does not recompute dependency traversal or pathfinding.
  - Orphan/disconnection checks are explicit reviewed node/direction/relation/counterpart-kind rules; unresolved matching QA-008 edges remain unresolved/conflicting rather than being promoted to map-only or script-only absence.
  - Target requirementsSatisfied is selected-scope static evidence only; runtimeGameplayCompletionProven and runtimeGameplayCompletionClaimed remain false.
  - Pre-final complete implementation head 1aabdb80bd0b847d3354cbd26e8c7f3890c899cb passed CI 29872181174, Agent Task Ownership 29872180917, OTBM Map Tools 29872180921 and AI Agent Tools 29872180910.
derived:
  - QA-009 remains a conservative selected-target evidence audit rather than a second quest topology resolver, Script Resolution engine, storage graph, pathfinder or runtime acceptance layer.
unknown:
  - MODULE_CATALOG shared-path row was not modified in the bounded feature branch; delivered public contracts are documented in OTBM_CONTENT_COMPLETENESS.md and task metadata.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation, focused-test, provenance or ownership failure remains before exact-final-head validation.
rejected_hypotheses:
  - Inferring quest stages or orphaned content from names/proximity: rejected because roadmap requires explicit compatible evidence.
  - Treating missing selected-scope dependency edges as global dead content: rejected; explicit reviewed missing-side classifications are bounded to the supplied graph only.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-009-content-completeness.md
  - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.md
  - docs/ai-agent/OTBM_CONTENT_COMPLETENESS.schema.json
  - docs/ai-agent/OTBM_CONTENT_COMPLETENESS_MANIFEST.schema.json
  - tools/ai-agent/otbm_content_completeness.py
  - tools/ai-agent/otbm_content_completeness_tool.py
  - tools/ai-agent/test_otbm_content_completeness.py
  - tools/ai-agent/test_otbm_content_completeness_output_safety.py
  - tools/ai-agent/test_otbm_content_completeness_schema.py
validation:
  - command: local focused unittest discovery for test_otbm_content_completeness*.py
    result: PASS
    evidence: 17 tests passed in isolated QA-009 draft workspace before repository writes; repository focused OTBM and AI Agent suites subsequently passed.
  - command: GitHub Actions CI run 29872181174
    result: PASS
    evidence: pre-final complete implementation head 1aabdb80bd0b847d3354cbd26e8c7f3890c899cb
  - command: GitHub Actions Agent Task Ownership run 29872180917
    result: PASS
    evidence: pre-final complete implementation head 1aabdb80bd0b847d3354cbd26e8c7f3890c899cb
  - command: GitHub Actions OTBM Map Tools run 29872180921
    result: PASS
    evidence: pre-final complete implementation head 1aabdb80bd0b847d3354cbd26e8c7f3890c899cb
  - command: GitHub Actions AI Agent Tools run 29872180910
    result: PASS
    evidence: pre-final complete implementation head 1aabdb80bd0b847d3354cbd26e8c7f3890c899cb
blockers: []
next_action: Verify exact-final-head CI, Agent Task Ownership, OTBM Map Tools and AI Agent Tools on the immutable final feature head, audit reviews, then squash-merge PR #700; leave the merged feature task active only for the separate lifecycle active-to-archive follow-up and compact resume handoff.
```
