---
task_id: CAN-20260715-otbm-repair-preflight-plan-builder
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-preflight-plan-builder
base_branch: main
created: 2026-07-15T23:34:13+02:00
updated: 2026-07-16T00:09:00+02:00
last_verified_commit: "e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214"
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
- [ ] Verify all current-head required checks and autonomous merge gate.

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

- PR: #406, same repository, base `main`, dedicated head branch.
- Exclusive claims are limited to the new preflight core/CLI/test/docs/schema and this task record.
- Shared claims are only `MODULE_CATALOG.md` and `CHANGELOG.md`.
- Phase 8 implementation and existing scanner/resolver paths remain read-only dependencies.
- Initial changed-task failures were metadata-only (`related_pr` empty, then `#406` instead of normalized `406`) and were corrected.
- Run `29454290592` passed changed-task checkpoint validation and then failed the global ownership step while this active structured task still had empty `program_id`; `tools/agents/task_ownership.py` requires non-empty `program_id`, `agent`, and `branch` for every active structured task. This update reuses `OTS-OTBM-VALIDATION` as the non-empty program identifier and leaves ownership scope unchanged.

# Current state

PR #406 contains the complete read-only preflight implementation, focused tests, native-scanner integration coverage, report schema, operator documentation and narrow catalogue/changelog integration. Final hardening now also requires exact script-resolution placement coverage/identity, treats repeated matching anchors as ambiguous, rechecks source immutability before publication, and publishes JSON artifacts with exclusive create-new semantics.

No OTBM, `.widx`, client asset, generated report or render is committed.

# Plan

1. Re-run current-head ownership, AI Agent Tools, OTBM Map Tools and repository CI after the program metadata normalization.
2. Repair only evidence-backed failures on the same PR.
3. Review final changed files/diff, update this checkpoint and PR body, mark ready, and squash-merge only if the autonomous merge gate is fully satisfied.

# Work log

## 2026-07-15T23:34:13+02:00

- Created the dedicated branch/task and bounded ownership scope.
- Reused native patch-anchor identity instead of extending the legacy item-audit contract.

## 2026-07-15T23:50:12+02:00

- Added correlation core, read-only CLI, schema, docs, focused tests and native-scanner/item-audit/script-resolution integration coverage.
- Added source/scanner pin rechecks and report/draft path collision guards.

## 2026-07-15T23:52:24+02:00

- Normalized `related_pr` to repository-required numeric text `406` after two changed-task validation failures exposed the exact metadata contract.

## 2026-07-16T00:09:00+02:00

- Hardened evidence correlation to fail closed on incomplete/mismatched script-resolution placements and repeated matching anchors.
- Hardened artifact publication to exclusive create-new writes with cleanup on multi-artifact publication failure and a final source immutability recheck.
- Removed all accidental neighboring `MODULE_CATALOG.md` drift; its PR diff is now only the review date and the new OTBM preflight row.
- Identified the global ownership violation: active structured tasks require a non-empty `program_id`; reused durable `OTS-OTBM-VALIDATION` instead of inventing a new identifier.

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
| `5e197326c51df8dc1a201089804f50f9ba5f6eb9` | OTBM Map Tools | passed | run `29453314939` |
| `5e197326c51df8dc1a201089804f50f9ba5f6eb9` | repository CI | passed | run `29453315139` |
| `e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214` | repository CI | passed | run `29454290830` |
| `e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214` | OTBM Map Tools | passed | run `29454290602` |
| `e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214` | Agent Task Ownership | failed | run `29454290592`: changed-task checkpoint passed; global ownership step failed while active structured task had empty `program_id`; source contract requires non-empty program ID |
| `e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214` | AI Agent Tools | in progress at checkpoint | run `29454290579`; no success claim yet |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Do not add `tilePlacementIndex` to legacy item-audit output; native patch anchors already provide it.
- Do not build a replacement-impact resolver; rerun the existing resolver against a hypothetical in-memory item-audit copy.
- Do not allow ordinary overwrite writes for final evidence; long-running preflight creates a TOCTOU window unless publication itself is exclusive.
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

1. Verify all current-head required checks after the `program_id` normalization.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T22:09:00Z
head: e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214
branch: feat/otbm-repair-preflight-plan-builder
pr: 406
status: validating
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
  - Incomplete or identity-mismatched script-resolution evidence now fails closed.
  - Ambiguous or repeated matching anchors never produce a draft plan.
  - PR 406 changed files contain only claimed preflight paths, the task record and two declared shared documentation paths.
  - MODULE_CATALOG diff contains only the review date and the new OTBM preflight row.
  - Repository CI and OTBM Map Tools passed on e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214.
derived:
  - This orchestration layer closes the investigation-to-plan gap without a new ADR because mutation semantics are unchanged.
unknown:
  - Current-head Agent Task Ownership after non-empty program_id normalization.
  - Current-head AI Agent Tools result after final fail-closed and publication hardening.
conflicts: []
first_failure:
  marker: Agent Task Ownership global task validation
  evidence: run 29454290592 passed changed-task checkpoint validation then failed global ownership; task_ownership.py requires non-empty program_id for active structured tasks and this task had program_id empty
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
  - command: AI Agent Tools run 29453314982
    result: PASS
    evidence: unit/integration tests and all workflow steps succeeded on implementation head 5e197326c51df8dc1a201089804f50f9ba5f6eb9
  - command: OTBM Map Tools run 29454290602
    result: PASS
    evidence: completed successfully on e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214
  - command: CI run 29454290830
    result: PASS
    evidence: completed successfully on e19d1ed1f9a0fef80a5ef9ee6b1e14f69dd5c214
  - command: Agent Task Ownership run 29454290592
    result: FAIL
    evidence: changed-task checkpoint passed; active structured task program_id was empty contrary to global validator contract and is corrected by this update
blockers:
  - none
next_action: Verify the new PR head and inspect current-head Agent Task Ownership, AI Agent Tools, OTBM Map Tools and repository CI.
```

# Handoff

Start from this task record and live PR #406. Do not reconstruct Phase 8 from chat history. Keep all Phase 8 implementation paths read-only unless a separate bounded task explicitly authorizes a contract change.

# Completion

- Final status: active
- PR: #406
- Merge commit:
- Program record updated: n/a; durable identifier reused, no separate program document exists
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
