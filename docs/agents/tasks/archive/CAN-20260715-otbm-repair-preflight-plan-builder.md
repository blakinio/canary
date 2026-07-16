---
task_id: CAN-20260715-otbm-repair-preflight-plan-builder
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-preflight-plan-builder
base_branch: main
created: 2026-07-15T23:34:13+02:00
updated: 2026-07-15T22:28:38Z
last_verified_commit: "0c0972526814f099b51fd3481f28331b9434446d"
risk: medium
related_issue: ""
related_pr: "406"
depends_on:
  - "OTBM Phase 8 bounded attribute patcher #325/#333"
  - "Unified OTBM World Index #219"
  - "OTBM script-resolution audit #104"
blocks: []
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_repair_preflight.py
    - tools/ai-agent/otbm_repair_preflight_tool.py
    - tools/ai-agent/test_otbm_repair_preflight.py
    - docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md
    - docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json
    - docs/agents/tasks/active/CAN-20260715-otbm-repair-preflight-plan-builder.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/OTBM_PHASE8_FINAL_HANDOFF.md
    - docs/ai-agent/OTBM_HD_PIPELINE.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/OTBM_BOUNDED_PATCH.md
    - docs/ai-agent/OTBM_BOUNDED_PATCH_PLAN.schema.json
    - docs/ai-agent/OTBM_BOUNDED_PATCH_RESULT.schema.json
    - docs/agents/decisions/ADR-20260714-otbm-fixed-width-patch-boundary.md
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_item_audit.py
    - tools/ai-agent/otbm_item_audit_tool.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_script_resolution_tool.py
    - tools/ai-agent/otbm_bounded_patch.py
    - tools/ai-agent/otbm_bounded_patch_types.py
    - tools/ai-agent/otbm_bounded_patch_tool.py
modules_touched:
  - OTBM real-map repair preflight and reviewed plan preparation
reuses:
  - existing native OTBM item/mechanic scanner and patch-anchor mode
  - existing OTBM item audit
  - existing OTBM script-resolution audit
  - canary-otbm-bounded-patch-plan-v1
public_interfaces:
  - canary-otbm-repair-preflight-v1
  - OTBM repair preflight CLI
cross_repo_tasks: []
completed: 2026-07-15T22:28:38Z
---

# Goal

Add one deterministic, read-only real-map repair preflight that reuses the existing OTBM item/mechanic audit, native patch-anchor evidence and script-resolution audit, narrows exact candidates by explicit selectors, preserves unresolved runtime evidence, and optionally emits a review-only `canary-otbm-bounded-patch-plan-v1` draft without modifying any OTBM.

# Acceptance criteria

- [x] Reuse the existing native scanner, item audit and script-resolution implementations; add no OTBM parser, renderer or writer.
- [x] Accept explicit selectors for position, item ID, action ID, unique ID, house-door ID and teleport destination.
- [x] Correlate exact patch anchors including `tilePlacementIndex`, `itemId`, `itemDepth`, attribute and current value.
- [x] Preserve `unresolved`, `referenced-only`, `partially-resolved` and `conflicting` script-resolution states.
- [x] Refuse incomplete/mismatched script-resolution evidence and ambiguous/repeated exact anchors rather than guessing.
- [x] Optionally build a draft existing-attribute Phase 8 plan only for one exact supported anchor.
- [x] Reject escape-width-changing replacements before a draft is considered ready.
- [x] Never execute the bounded patcher or write/modify an OTBM.
- [x] Publish report/draft outputs with create-new-only semantics and no source-map/symlink/hard-link collision.
- [x] Emit deterministic `canary-otbm-repair-preflight-v1` JSON and focused/native-scanner integration coverage.
- [x] Document the CLI, safety boundary and review workflow.
- [x] Update module catalogue/changelog narrowly.
- [x] Verify current-head GitHub checks and autonomous merge gate inputs before readiness.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` was `264a86b1eddf5f68666281c47489166f343c3e84`.
- Phase 8 is complete and not reopened; this task does not broaden its four existing fixed-width mutation kinds.
- Open PR #316 owns Targuna-specific audit/report paths and uses core OTBM tooling read-only; no exclusive overlap with this task was found.
- Open PR #393 is unrelated E2E/load work; `MODULE_CATALOG.md` and `CHANGELOG.md` are shared coordination paths.
- No local checkout is exposed in this connector session; repository/PR/CI evidence comes from GitHub, and local git/worktree claims are not invented.
- `OTS-OTBM-VALIDATION` is reused from the completed Phase 8 durable task as this active structured task's non-empty program/coordination identifier; no new program identifier is invented.

# Existing work to reuse

| Existing work | Reuse | Boundary |
|---|---|---|
| OTBM item audit | Full-map mechanic placements and source hash | No new parser. |
| Native `--patch-anchors` | Exact Phase 8 placement identity and current values | No scanner fork. |
| OTBM script resolution | Active Lua/XML/engine handler evidence | Unresolved remains unresolved. |
| `canary-otbm-bounded-patch-plan-v1` | Optional review-only draft | No second patch format or writer. |

# Ownership and overlap check

- PR #406 is in `blakinio/canary`, targets `main`, and uses the dedicated head `feat/otbm-repair-preflight-plan-builder` in the same repository.
- Exclusive claims are limited to the new preflight core/CLI/test/docs/schema and this task record.
- Shared claims are only `MODULE_CATALOG.md` and `CHANGELOG.md`.
- Phase 8 implementation and existing scanner/resolver paths remain read-only dependencies.
- Initial changed-task failures were metadata-only (`related_pr` empty, then `#406` instead of normalized `406`) and were corrected.
- Global ownership then exposed the active-structured-task requirement for non-empty `program_id`; durable `OTS-OTBM-VALIDATION` was reused and current-head ownership passed.
- Current PR changed-file inventory contains exactly eight claimed paths and no `.otbm`, `.widx`, client assets, generated reports or renders.
- PR #406 has no review submissions and no inline review threads at readiness checkpoint.

# Current state

PR #406 contains the complete read-only preflight implementation, focused tests, native-scanner integration coverage, report schema, operator documentation and narrow catalogue/changelog integration.

The final implementation:

- correlates item-audit placements with exact native Phase 8 patch anchors;
- requires complete, identity-matching script-resolution placement evidence;
- keeps unresolved/conflicting states explicit;
- never guesses ambiguous or repeated anchors;
- validates optional draft plans through the existing Phase 8 `PatchPlan` contract;
- checks OTBM escape-width compatibility before a draft is ready;
- reruns the existing resolver on a hypothetical in-memory replacement without modifying OTBM;
- rechecks source/scanner identity;
- publishes JSON artifacts with exclusive create-new semantics;
- preserves the diagnostic report when a requested draft plan is blocked;
- never invokes the bounded patcher.

No OTBM, `.widx`, client asset, generated report or render is committed.

# Plan

1. Let required workflows rerun on this readiness-only task-record head.
2. If all current-head checks pass, mark PR #406 ready, verify final diff/reviews/mergeability, and squash-merge.
3. After merge, inspect the lifecycle cleanup created for the active task and complete archival if repository automation does not finish it autonomously.

# Work log

## 2026-07-15T23:34:13+02:00

- Created dedicated branch/task and bounded ownership scope.
- Reused native patch-anchor identity instead of extending the legacy item-audit contract.

## 2026-07-15T23:50:12+02:00

- Added correlation core, read-only CLI, schema, docs, focused tests and native-scanner/item-audit/script-resolution integration coverage.
- Added source/scanner pin rechecks and report/draft path collision guards.

## 2026-07-15T23:52:24+02:00

- Normalized `related_pr` to repository-required numeric text `406` after changed-task validation exposed the exact metadata contract.

## 2026-07-16T00:09:00+02:00

- Hardened evidence correlation to fail closed on incomplete/mismatched script-resolution placements and repeated matching anchors.
- Hardened artifact publication to exclusive create-new writes with cleanup on multi-artifact publication failure and a final source immutability recheck.
- Removed accidental neighboring `MODULE_CATALOG.md` drift; its diff is only the review date and new preflight row.
- Reused durable `OTS-OTBM-VALIDATION` as non-empty program metadata required by the global ownership validator.

## 2026-07-16T00:12:00+02:00

- Verified implementation head `48411ffecca7e46eca2375fbc05646af19d9e03b` with all four task-relevant workflows green.
- Verified exact eight-file changed inventory, no forbidden artifacts, mergeable PR state, zero review submissions and zero inline review threads.
- Promoted the task to `ready`; this task-record-only commit must still pass current-head checks before merge.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Reuse `canary-otbm-bounded-patch-plan-v1`. | Avoids a second plan/writer contract. | Existing fixed-width patch boundary ADR |
| Run native patch anchors alongside item audit. | Exact tile-local Phase 8 identity already exists there. | Existing Phase 8 contract |
| Reuse existing script resolver for hypothetical replacement evidence. | Avoids a second resolver and keeps unresolved explicit. | Existing script-resolution contract |
| Keep gameplay correctness/player intent outside success. | Static/structural evidence cannot prove either. | Existing Phase 8 handoff |
| Publish only new JSON paths with exclusive creation. | Prevents overwrite/symlink races from turning read-only analysis into source modification. | Task-local hardening; writer boundary unchanged |

# Files and interfaces

| Path/interface | Mode | Status |
|---|---|---|
| `tools/ai-agent/otbm_repair_preflight.py` | exclusive | implemented |
| `tools/ai-agent/otbm_repair_preflight_tool.py` | exclusive | implemented |
| `tools/ai-agent/test_otbm_repair_preflight.py` | exclusive | implemented |
| `docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md` | exclusive | implemented |
| `docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json` | exclusive | implemented |
| `canary-otbm-bounded-patch-plan-v1` | reused/read-only | unchanged |

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `5e197326c51df8dc1a201089804f50f9ba5f6eb9` | AI Agent Tools | passed | run `29453314982`, including preflight integration tests |
| `e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214` | AI Agent Tools | passed | run `29454290579`, including fail-closed hardening tests |
| `48411ffecca7e46eca2375fbc05646af19d9e03b` | AI Agent Tools | passed | run `29454580316`; unit tests and all workflow steps succeeded |
| `48411ffecca7e46eca2375fbc05646af19d9e03b` | OTBM Map Tools | passed | run `29454580263` |
| `48411ffecca7e46eca2375fbc05646af19d9e03b` | Agent Task Ownership | passed | run `29454580206` |
| `48411ffecca7e46eca2375fbc05646af19d9e03b` | repository CI | passed | run `29454580586` |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Do not add `tilePlacementIndex` to legacy item-audit output; native patch anchors already provide it.
- Do not build a replacement-impact resolver; rerun the existing resolver against a hypothetical in-memory item-audit copy.
- Do not allow ordinary overwrite writes for final evidence; long-running preflight creates a TOCTOU window unless publication itself is exclusive.
- Do not discard the diagnostic report merely because an explicitly requested draft cannot be proven safe.
- Do not prefix numeric `related_pr` with `#`; changed-task validation requires normalized identity.
- Do not leave `program_id` empty on an active structured task; global ownership validation rejects it.

# Risks and compatibility

- Runtime: none; offline/read-only analysis.
- Data/migration: none.
- OTBM mutation: none.
- Security: subprocesses use argument vectors with `shell=False`; source/scanner identities are pinned and rechecked; output creation is exclusive.
- Backward compatibility: existing item-audit, script-resolution and Phase 8 plan contracts are unchanged.
- Cross-repo rollout: none.
- Rollback: revert text/Python/schema changes; no map rollback is required because no map is written.

# Remaining work

1. Pass current-head readiness checks and merge PR #406 if the autonomous merge gate remains satisfied.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T22:12:00Z
head: 48411ffecca7e46eca2375fbc05646af19d9e03b
branch: feat/otbm-repair-preflight-plan-builder
pr: 406
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_repair_preflight.py
  - tools/ai-agent/otbm_repair_preflight_tool.py
  - tools/ai-agent/test_otbm_repair_preflight.py
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json
  - docs/agents/tasks/active/CAN-20260715-otbm-repair-preflight-plan-builder.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - Phase 8 writer boundary is unchanged and no new parser, renderer, writer or script resolver was introduced.
  - The CLI never invokes the bounded patcher and final artifact publication uses exclusive create-new semantics.
  - Incomplete or identity-mismatched script-resolution evidence fails closed.
  - Ambiguous or repeated matching anchors never produce a draft plan.
  - A blocked requested draft still leaves a diagnostic preflight report and no draft-plan file.
  - PR 406 changed files contain only claimed preflight paths, the task record and two declared shared documentation paths.
  - MODULE_CATALOG diff contains only the review date and the new OTBM preflight row.
  - AI Agent Tools, OTBM Map Tools, Agent Task Ownership and repository CI passed on 48411ffecca7e46eca2375fbc05646af19d9e03b.
  - PR 406 has no review submissions or inline review threads at readiness checkpoint.
derived:
  - This orchestration layer closes the investigation-to-plan gap without a new ADR because mutation semantics are unchanged.
unknown:
  - Current-head workflow results for this readiness-only task-record commit.
conflicts: []
first_failure:
  marker: none
  evidence: prior metadata failures are resolved; implementation head 48411ffecca7e46eca2375fbc05646af19d9e03b is green on all task-relevant workflows
rejected_hypotheses:
  - Extend legacy item audit with patch identity.
  - Build a second script resolver.
  - Treat unresolved replacement resolution as handled.
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260715-otbm-repair-preflight-plan-builder.md
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json
  - tools/ai-agent/otbm_repair_preflight.py
  - tools/ai-agent/otbm_repair_preflight_tool.py
  - tools/ai-agent/test_otbm_repair_preflight.py
validation:
  - command: AI Agent Tools run 29454580316
    result: PASS
    evidence: all workflow steps succeeded on 48411ffecca7e46eca2375fbc05646af19d9e03b
  - command: OTBM Map Tools run 29454580263
    result: PASS
    evidence: completed successfully on 48411ffecca7e46eca2375fbc05646af19d9e03b
  - command: Agent Task Ownership run 29454580206
    result: PASS
    evidence: completed successfully on 48411ffecca7e46eca2375fbc05646af19d9e03b
  - command: CI run 29454580586
    result: PASS
    evidence: completed successfully on 48411ffecca7e46eca2375fbc05646af19d9e03b
blockers: []
next_action: Verify current-head checks for this readiness-only commit, then mark PR 406 ready and squash-merge if mergeability and review state remain clean.
```

# Handoff

Start from this task record and live PR #406. Do not reconstruct Phase 8 from chat history. Keep all Phase 8 implementation paths read-only unless a separate bounded task explicitly authorizes a contract change.

# Completion

- Final status: ready
- PR: #406
- Merge commit:
- Program record updated: n/a; durable identifier reused, no separate program document exists
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:

## Automated lifecycle completion

- Feature PR: #406.
- Feature head: `51a3d7da3676e9bb35ea2fddb195ae067b599b33`.
- Merge commit: `0c0972526814f099b51fd3481f28331b9434446d`.
- Merged at: `2026-07-15T22:28:38Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
