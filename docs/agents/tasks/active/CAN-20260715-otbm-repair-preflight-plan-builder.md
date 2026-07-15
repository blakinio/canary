---
task_id: CAN-20260715-otbm-repair-preflight-plan-builder
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-preflight-plan-builder
base_branch: main
created: 2026-07-15T23:34:13+02:00
updated: 2026-07-15T23:52:24+02:00
last_verified_commit: "3a117ae7dfc706a1aa9a00971c12f0a391e3afb8"
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

Add one deterministic, read-only real-map repair preflight that orchestrates the existing OTBM item/mechanic audit, native patch-anchor evidence and script-resolution audit, narrows exact repair candidates by explicit selectors, preserves unresolved runtime evidence, and optionally emits a review-only `canary-otbm-bounded-patch-plan-v1` draft without modifying any OTBM.

# Acceptance criteria

- [x] Reuse the existing native scanner, item audit and script-resolution implementations; add no OTBM parser, renderer or writer.
- [x] Accept explicit bounded selectors for position, item ID, action ID, unique ID, house-door ID and teleport destination.
- [x] Correlate matched mechanic placements with exact patch anchors including `tilePlacementIndex`, `itemId`, `itemDepth`, attribute and current value.
- [x] Correlate each candidate with the existing script-resolution placement evidence and preserve `unresolved`, `referenced-only`, `partially-resolved` and `conflicting` statuses exactly.
- [x] Optionally build a draft existing-attribute Phase 8 plan only when one exact anchor is selected and the requested operation targets an already-existing supported attribute.
- [x] Never execute `otbm_bounded_patch_tool.py` or write/modify an OTBM.
- [x] Emit deterministic JSON report `canary-otbm-repair-preflight-v1` and add focused unit/integration coverage.
- [x] Document CLI, safety boundary and review workflow.
- [x] Update module catalogue/changelog narrowly.
- [ ] Verify current-head GitHub checks and autonomous merge gate before merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `264a86b1eddf5f68666281c47489166f343c3e84`.
- `docs/agents/OTBM_PHASE8_FINAL_HANDOFF.md` states Phase 8 is complete and must not be reopened; future real-map repairs must reuse the merged scanner, script resolution, bounded plan and semantic validation contracts.
- Supported write operations remain only existing action ID, unique ID, house-door ID and teleport destination attributes.
- The new task is preflight/plan preparation only and does not broaden the Phase 8 write boundary.
- Open PR #316 owns Targuna-specific temporary audit/report paths and lists core OTBM scanner/index/diff tooling as read-only; no exclusive overlap exists with this task.
- Open PR #393 is unrelated E2E/load work; `MODULE_CATALOG.md` and `CHANGELOG.md` are shared coordination paths only.
- No local checkout is available through this connector session, so local `git status`, branch/worktree inspection and `task_ownership.py` cannot be run here; GitHub repository/branch/PR state and GitHub Actions evidence are used instead and this limitation is recorded rather than guessed.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTBM item audit | Full-map mechanic placements and map source hash | `tools/ai-agent/otbm_item_audit*.py` | Existing authoritative mechanic inventory. |
| Native patch anchors | Exact physical and logical existing-attribute anchors | `otbm_item_audit_scan --patch-anchors` | Supplies Phase 8 identity including placement index/depth without parsing OTBM again. |
| OTBM script resolution | Runtime handler correlation and unresolved/conflict states | `tools/ai-agent/otbm_script_resolution*.py` | Existing active Lua/XML resolver; unresolved stays unresolved. |
| Phase 8 plan contract | Draft review plan output | `canary-otbm-bounded-patch-plan-v1` | Reuse exact existing writer input contract; do not add another patch format. |

# Ownership and overlap check

- Program record: none; this is a bounded continuation task under `OTS-OTBM-VALIDATION`.
- Open PRs inspected: #316 and #393.
- Active task overlap: PR #316 Targuna donor isolation; no exclusive path overlap. PR #393 is unrelated.
- Ownership checker result: first PR run failed because `related_pr` was empty; the next run proved the repository validator expects the normalized value `406` without a `#` prefix. This metadata now matches checkpoint `pr: 406`.
- Exclusive claims: five new preflight implementation/docs/test/schema paths plus this task record.
- Shared claims: `MODULE_CATALOG.md`, `CHANGELOG.md` only.
- Read-only dependencies: all Phase 8 patcher/scanner/resolver contracts and implementation paths.
- Overlaps: shared documentation only with PR #393; current `main` was rechecked at `264a86b1eddf5f68666281c47489166f343c3e84` before shared-file edits.
- Resolution: proceed on dedicated PR #406; do not edit PR #316 paths or Phase 8 implementation files.

# Current state

PR #406 contains the read-only correlation core, orchestration CLI, report schema, operator documentation, focused tests and native-scanner integration coverage. The CLI rejects source-map/symlink/hard-link output collisions, rechecks source and scanner identity after analysis, and never imports or executes the Phase 8 patcher. No OTBM, `.widx`, client asset, generated report or render is committed.

# Plan

1. Re-run current-head Agent Task Ownership with normalized `related_pr: "406"`.
2. Inspect AI Agent Tools and OTBM Map Tools results on the resulting head and repair only evidence-backed failures.
3. Review the full changed-file list/diff, remove any unrelated shared-index drift, update this checkpoint and PR body, then apply the autonomous merge gate.

# Work log

## 2026-07-15T23:34:13+02:00

- Changed: created dedicated task branch and claimed new paths.
- Learned: existing legacy item scan exposes mechanic placements but exact `tilePlacementIndex` is supplied by the already-existing native `--patch-anchors` mode; the preflight should correlate both rather than extending the parser.
- Failed/blocked: local ownership script unavailable because no local checkout is exposed.
- Result: bounded implementation scope established with no Phase 8 contract expansion.

## 2026-07-15T23:50:12+02:00

- Changed: added correlation core, read-only CLI, report schema, documentation, unit tests, a native-scanner/item-audit/script-resolution integration test, and narrow catalogue/changelog entries.
- Learned: report/draft output paths require an explicit source-map collision guard even though the tool itself never calls a writer; source and scanner are both pinned and rechecked after analysis.
- Failed/blocked: Agent Task Ownership run `29453314900` failed at `Validate changed active task checkpoints` because this task still had an empty `related_pr` after PR #406 was created.
- Result: task metadata was bound to PR 406 for the next validation run.

## 2026-07-15T23:52:24+02:00

- Changed: normalized frontmatter `related_pr` from `#406` to repository-required value `406`.
- Learned: Agent Task Ownership run `29453442383` normalizes the checkpoint PR to `406` and requires exact equality with frontmatter, so a leading `#` is invalid.
- Failed/blocked: run `29453442383` failed only changed-task checkpoint validation on the `#406` versus `406` mismatch; overlap validation did not run.
- Result: metadata format is corrected for the next current-head ownership run.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Reuse `canary-otbm-bounded-patch-plan-v1` for optional draft output. | Avoids a second writer/plan contract and preserves Phase 8 boundary. | Existing ADR-20260714-otbm-fixed-width-patch-boundary.md |
| Run native `--patch-anchors` alongside item audit. | Item audit gives mechanic inventory; patch anchors give exact placement identity required by the Phase 8 plan. | Existing Phase 8 contract |
| Keep gameplay correctness outside preflight success. | Structural/script evidence cannot prove player intent or runtime gameplay correctness. | Existing Phase 8 handoff |
| Rerun the existing script resolver against an in-memory hypothetical item-audit copy when a draft is ready. | Shows before/after static handler resolution without modifying OTBM or inventing a second resolver. | Existing script-resolution contract |
| Require new report/draft output paths distinct from the source map. | Prevents a read-only analysis command from overwriting the source through user-supplied output paths. | Task-local safety hardening; no writer-boundary change |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `tools/ai-agent/otbm_repair_preflight.py` | exclusive | Correlation, exact-anchor and existing-plan draft logic | implemented |
| `tools/ai-agent/otbm_repair_preflight_tool.py` | exclusive | Read-only audit/anchor/resolver orchestration CLI | implemented |
| `tools/ai-agent/test_otbm_repair_preflight.py` | exclusive | Focused regressions and real native-scanner integration | implemented |
| `docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md` | exclusive | Operator/review contract | implemented |
| `docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json` | exclusive | `canary-otbm-repair-preflight-v1` report contract | implemented |
| `canary-otbm-bounded-patch-plan-v1` | read_only/reused | Existing reviewed patch plan | unchanged |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `5e197326c51df8dc1a201089804f50f9ba5f6eb9` | repository CI | passed | GitHub Actions run `29453315139`. |
| `5e197326c51df8dc1a201089804f50f9ba5f6eb9` | AI Agent Tools | passed | Run `29453314982`; `Run unit tests` and all subsequent audit steps succeeded, including the new preflight tests on that code head. |
| `5e197326c51df8dc1a201089804f50f9ba5f6eb9` | OTBM Map Tools | passed | Run `29453314939`. |
| `5e197326c51df8dc1a201089804f50f9ba5f6eb9` | Agent Task Ownership | failed | Run `29453314900`; `related_pr` was empty while current PR is 406. |
| `3a117ae7dfc706a1aa9a00971c12f0a391e3afb8` | repository CI | passed | Run `29453442535`. |
| `3a117ae7dfc706a1aa9a00971c12f0a391e3afb8` | Agent Task Ownership | failed | Run `29453442383`; frontmatter used `#406` while normalized checkpoint/current PR value is `406`. |
| `3a117ae7dfc706a1aa9a00971c12f0a391e3afb8` | AI Agent Tools | in-progress-at-checkpoint | Run `29453442414`; no current-head result claimed yet. |
| `3a117ae7dfc706a1aa9a00971c12f0a391e3afb8` | OTBM Map Tools | in-progress-at-checkpoint | Run `29453442349`; no current-head result claimed yet. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Do not add `tilePlacementIndex` to the legacy item-audit contract: exact Phase 8 anchor identity already exists in native `--patch-anchors` output.
- Do not let a preflight report path reuse the source map: an early CLI review identified that an unconstrained `--output` could otherwise overwrite the source despite the analysis itself being read-only; explicit new-output collision checks were added before publishing the CLI.
- Do not prefix numeric `related_pr` with `#`: the changed-task validator requires the normalized PR identifier `406` to match checkpoint/current PR identity exactly.

# Risks and compatibility

- Runtime: none; tool runs offline and read-only.
- Data/migration: none; no OTBM modification and no schema/database migration.
- Security: subprocesses remain argument-vector calls to repository tools with `shell=False`; report/draft destinations reject source-map, hard-link and symlink collisions.
- Backward compatibility: existing item-audit, script-resolution and Phase 8 plan contracts remain unchanged.
- Cross-repo rollout: none.
- Rollback: revert this task's text/Python/schema additions; no map rollback is needed because this task never writes maps.

# Remaining work

1. Verify current-head ownership and focused AI/OTBM checks after the normalized `related_pr` metadata repair.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T21:52:24Z
head: 3a117ae7dfc706a1aa9a00971c12f0a391e3afb8
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
  - Phase 8 is complete and its writer boundary is not broadened by this task.
  - The implementation imports existing item audit, native patch-anchor scanning, script resolution and Phase 8 PatchPlan validation rather than adding a parser, writer or resolver.
  - The CLI never invokes the bounded patcher and rejects report/draft paths that collide with the source map.
  - Open PR 316 has no exclusive overlap with the new preflight paths; core OTBM tooling remains read-only there.
  - PR 406 changed-file list contains only the claimed new preflight paths, task record and two declared shared documentation paths.
  - AI Agent Tools and OTBM Map Tools passed on implementation head 5e197326c51df8dc1a201089804f50f9ba5f6eb9.
derived:
  - A read-only orchestration/correlation layer closes the repair-investigation gap without a new ADR because the Phase 8 mutation contract is unchanged.
unknown:
  - Current-head AI Agent Tools result after the metadata repair commit.
  - Current-head OTBM Map Tools result after the metadata repair commit.
  - Current-head Agent Task Ownership result after related_pr is normalized to 406.
conflicts: []
first_failure:
  marker: Agent Task Ownership changed active task checkpoint validation
  evidence: run 29453314900 artifact CHANGED_TASK_VALIDATION.txt reports initial empty related_pr mismatch with PR 406
rejected_hypotheses:
  - Extend the legacy item-audit format with patch identity: rejected because native patch-anchor mode already provides the required identity.
  - Add another script resolver for replacement impact: rejected because the existing resolver can run against a hypothetical in-memory item-audit copy.
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
  - command: GitHub open-PR and ownership overlap inspection
    result: PASS
    evidence: PR 316 and PR 393 inspected; no exclusive path overlap found
  - command: AI Agent Tools run 29453314982
    result: PASS
    evidence: unit tests and all AI Agent Tools steps completed successfully on implementation head 5e197326c51df8dc1a201089804f50f9ba5f6eb9
  - command: OTBM Map Tools run 29453314939
    result: PASS
    evidence: completed successfully on implementation head 5e197326c51df8dc1a201089804f50f9ba5f6eb9
  - command: CI run 29453442535
    result: PASS
    evidence: repository CI completed successfully on 3a117ae7dfc706a1aa9a00971c12f0a391e3afb8
  - command: Agent Task Ownership run 29453442383
    result: FAIL
    evidence: frontmatter related_pr used #406 while checkpoint/current PR normalize to 406; corrected by this update
  - command: local task_ownership.py
    result: BLOCKED
    evidence: no local checkout is exposed in this connector session
blockers:
  - none
next_action: Verify the new PR head and inspect current-head Agent Task Ownership, AI Agent Tools and OTBM Map Tools results.
```

# Handoff

Start from this task record and live PR #406. Do not reconstruct Phase 8 from chat history and do not edit any Phase 8 implementation path unless a separately reviewed bounded task explicitly authorizes it.

# Completion

- Final status: active
- PR: #406
- Merge commit:
- Program record updated: n/a
- Catalogue updated: yes
- Changelog updated: yes
- Archived at:
