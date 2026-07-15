---
task_id: CAN-20260715-otbm-repair-preflight-plan-builder
program_id: ""
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-preflight-plan-builder
base_branch: main
created: 2026-07-15T23:34:13+02:00
updated: 2026-07-15T23:34:13+02:00
last_verified_commit: "264a86b1eddf5f68666281c47489166f343c3e84"
risk: medium
related_issue: ""
related_pr: ""
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

- [ ] Reuse the existing native scanner, item audit and script-resolution implementations; add no OTBM parser, renderer or writer.
- [ ] Accept explicit bounded selectors for position, item ID, action ID, unique ID, house-door ID and teleport destination.
- [ ] Correlate matched mechanic placements with exact patch anchors including `tilePlacementIndex`, `itemId`, `itemDepth`, attribute and current value.
- [ ] Correlate each candidate with the existing script-resolution placement evidence and preserve `unresolved`, `referenced-only`, `partially-resolved` and `conflicting` statuses exactly.
- [ ] Optionally build a draft existing-attribute Phase 8 plan only when one exact anchor is selected and the requested operation targets an already-existing supported attribute.
- [ ] Never execute `otbm_bounded_patch_tool.py` or write/modify an OTBM.
- [ ] Emit deterministic JSON report `canary-otbm-repair-preflight-v1` and validate focused unit/integration behavior.
- [ ] Document CLI, safety boundary and review workflow.
- [ ] Update module catalogue/changelog narrowly.
- [ ] Verify current-head GitHub checks and autonomous merge gate before merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `264a86b1eddf5f68666281c47489166f343c3e84`.
- `docs/agents/OTBM_PHASE8_FINAL_HANDOFF.md` states Phase 8 is complete and must not be reopened; future real-map repairs must reuse the merged scanner, script resolution, bounded plan and semantic validation contracts.
- Supported write operations remain only existing action ID, unique ID, house-door ID and teleport destination attributes.
- The new task is preflight/plan preparation only and does not broaden the Phase 8 write boundary.
- Open PR #316 owns Targuna-specific temporary audit/report paths and lists core OTBM scanner/index/diff tooling as read-only; no exclusive overlap exists with this task.
- Open PR #393 is unrelated E2E/load work; `MODULE_CATALOG.md` and `CHANGELOG.md` are shared coordination paths only.
- No local checkout is available through this connector session, so local `git status`, branch/worktree inspection and `task_ownership.py` cannot be run here; GitHub repository/branch/PR state is used instead and this limitation is recorded rather than guessed.

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
- Ownership checker result: NOT_RUN because no local checkout is exposed in this session.
- Exclusive claims: five new preflight implementation/docs/test/schema paths plus this task record.
- Shared claims: `MODULE_CATALOG.md`, `CHANGELOG.md` only.
- Read-only dependencies: all Phase 8 patcher/scanner/resolver contracts and implementation paths.
- Overlaps: shared documentation only with PR #393; preserve current `main` entries and edit narrowly.
- Resolution: proceed on a dedicated branch; do not edit PR #316 paths or Phase 8 implementation files.

# Current state

Task branch created from exact current `main`. No implementation file exists yet and no OTBM/map/client asset has been written or committed.

# Plan

1. Implement a pure preflight correlation module over existing item-audit, patch-anchor and script-resolution JSON contracts.
2. Implement a CLI that runs the existing item audit, native patch-anchor mode and script resolution into a temporary workspace, then emits only the final preflight report and optional review-only draft plan.
3. Add focused tests with synthetic reports plus a native-scanner integration case where available.
4. Document the workflow and add the narrow catalogue/changelog entries.
5. Verify changed paths/diff and current-head CI; repair only evidence-backed failures.

# Work log

## 2026-07-15T23:34:13+02:00

- Changed: created dedicated task branch and claimed new paths.
- Learned: existing legacy item scan exposes mechanic placements but exact `tilePlacementIndex` is supplied by the already-existing native `--patch-anchors` mode; the preflight should correlate both rather than extending the parser.
- Failed/blocked: local ownership script unavailable because no local checkout is exposed.
- Result: bounded implementation scope established with no Phase 8 contract expansion.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Reuse `canary-otbm-bounded-patch-plan-v1` for optional draft output. | Avoids a second writer/plan contract and preserves Phase 8 boundary. | Existing ADR-20260714-otbm-fixed-width-patch-boundary.md |
| Run native `--patch-anchors` alongside item audit. | Item audit gives mechanic inventory; patch anchors give exact placement identity required by the Phase 8 plan. | Existing Phase 8 contract |
| Keep gameplay correctness outside preflight success. | Structural/script evidence cannot prove player intent or runtime gameplay correctness. | Existing Phase 8 handoff |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `tools/ai-agent/otbm_repair_preflight.py` | exclusive | Correlation and draft-plan logic | planned |
| `tools/ai-agent/otbm_repair_preflight_tool.py` | exclusive | Read-only orchestration CLI | planned |
| `tools/ai-agent/test_otbm_repair_preflight.py` | exclusive | Focused regression tests | planned |
| `docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md` | exclusive | Operator/review contract | planned |
| `docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json` | exclusive | Machine-readable report contract | planned |
| `canary-otbm-bounded-patch-plan-v1` | read_only/reused | Existing reviewed patch plan | unchanged |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | focused Python tests | not-run | Implementation not committed yet. |
| pending | Agent Task Ownership | not-run | Will run on draft PR. |
| pending | repository CI | not-run | Will verify current feature head. |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Do not add `tilePlacementIndex` to the legacy item-audit contract: exact Phase 8 anchor identity already exists in native `--patch-anchors` output.

# Risks and compatibility

- Runtime: none; tool runs offline and read-only.
- Data/migration: none; no OTBM modification and no schema/database migration.
- Security: subprocesses remain argument-vector calls to repository tools; no shell execution is required.
- Backward compatibility: existing item-audit, script-resolution and Phase 8 plan contracts remain unchanged.
- Cross-repo rollout: none.
- Rollback: revert this task's text/Python/schema additions; no map rollback is needed because this task never writes maps.

# Remaining work

1. Implement the read-only correlation core and CLI on the task branch.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-15T21:34:13Z
head: 264a86b1eddf5f68666281c47489166f343c3e84
branch: feat/otbm-repair-preflight-plan-builder
pr: none
status: implementing
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
  - Phase 8 is complete and its writer boundary must not be broadened by this task.
  - Existing item audit exposes mechanicPlacements and existing native patch-anchor mode exposes exact tilePlacementIndex/itemDepth/attribute/value identity.
  - Existing script resolution preserves unresolved and conflicting states and already correlates active Lua/XML handlers.
  - Open PR 316 has no exclusive overlap with the new preflight paths; core OTBM tooling is read-only there.
derived:
  - A read-only orchestration/correlation layer can close the repair-investigation gap without a new parser, renderer, writer or ADR.
unknown:
  - Focused test and CI results after implementation.
conflicts: []
first_failure:
  marker: none
  evidence: implementation has not started
rejected_hypotheses:
  - Extend the legacy item-audit format with patch identity: rejected because native patch-anchor mode already provides the required identity.
changed_paths:
  - docs/agents/tasks/active/CAN-20260715-otbm-repair-preflight-plan-builder.md
validation:
  - command: GitHub open-PR and ownership overlap inspection
    result: PASS
    evidence: PR 316 and PR 393 inspected; no exclusive path overlap found
  - command: local task_ownership.py
    result: BLOCKED
    evidence: no local checkout is exposed in this connector session
blockers:
  - none
next_action: Implement the read-only preflight correlation core and orchestration CLI using the existing item audit, patch-anchor and script-resolution contracts.
```

# Handoff

Start from this task record and current live PR/branch. Do not reconstruct Phase 8 from chat history and do not edit any Phase 8 implementation path unless a separately reviewed bounded task explicitly authorizes it.

# Completion

- Final status: active
- PR:
- Merge commit:
- Program record updated: n/a
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
