---
task_id: CAN-20260716-otbm-repair-evidence-hardening
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-evidence-hardening
base_branch: main
created: 2026-07-16T09:20:00+02:00
updated: 2026-07-16T09:35:00+02:00
last_verified_commit: "32b2909097b2d3f474e0cc959a4f2666fb4ccf15"
risk: medium
related_issue: ""
related_pr: "413"
depends_on:
  - "OTBM real-map repair preflight #406"
  - "OTBM Phase 8 bounded attribute patcher #325/#333"
  - "OTBM script-resolution audit #104"
blocks:
  - "future OTBM map quality gate and sandbox verification"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_repair_preflight.py
    - tools/ai-agent/otbm_repair_preflight_tool.py
    - tools/ai-agent/test_otbm_repair_preflight.py
    - tools/ai-agent/test_otbm_repair_preflight_hardening.py
    - docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md
    - docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json
    - docs/agents/tasks/active/CAN-20260716-otbm-repair-evidence-hardening.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/OTBM_PHASE8_FINAL_HANDOFF.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/OTBM_BOUNDED_PATCH.md
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_bounded_patch_types.py
modules_touched:
  - OTBM real-map repair preflight
reuses:
  - existing OTBM item audit
  - existing native patch-anchor scanner
  - existing OTBM script-resolution audit
  - existing Phase 8 patch-plan validation
public_interfaces:
  - canary-otbm-repair-preflight-v1
  - OTBM repair preflight CLI
cross_repo_tasks: []
---

# Goal

Harden the merged read-only OTBM real-map repair preflight so a reviewer can distinguish a mere selector match from an exact correlated/patchable candidate, reproduce the evidence inputs used by the run, and inspect exact hypothetical script-resolution changes before approving a Phase 8 draft plan.

# Acceptance criteria

- [x] Preserve the existing Phase 8 bounded patch contracts and supported mutation kinds unchanged.
- [x] Keep `ok` backward-compatible as selector-match evidence while adding an explicit readiness model for matched, correlated, runtime-resolved, patchable and review-ready state.
- [x] Add deterministic hashes/pins for appearances input, `items.xml`, optional rules/review-rules and the selected script corpus used by script resolution.
- [x] Record repository/script evidence without claiming a clean Git worktree when connector/local Git state is unavailable.
- [x] Compare hypothetical before/after script-resolution placement evidence structurally, not only by top-level status string.
- [x] Surface handler/registration/source/confidence/resolution changes in a deterministic diff payload.
- [x] Preserve unresolved, referenced-only, partially-resolved and conflicting evidence without promotion to handled.
- [x] Keep the source map immutable and retain existing source/scanner rechecks and create-new output safety.
- [x] Add focused unit/integration regression coverage and update the report schema/docs.
- [ ] Update catalogue/changelog narrowly only if the reusable interface description materially changes.
- [ ] Verify current-head required checks before readiness/merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `8950a275e258ccc0f1a6781c9ff9c8ea089210a0` based on live repository commit search.
- Draft PR #413 targets `blakinio/canary:main` from `blakinio/canary:feat/otbm-repair-evidence-hardening`.
- Phase 8 is complete and remains closed; this task does not add map geometry/item/tile insertion or another writer.
- Open PR #316 owns Targuna donor-isolation evidence and temporary audit paths; no exclusive overlap with this task.
- Open PR #393 touches shared catalogue/test-infrastructure documentation; shared index edits must be rebased narrowly from current `main`.
- Open PR #411 is OAM engine/build/runtime governance and does not overlap these OTBM preflight implementation paths.
- No local checkout is available through the current GitHub connector session, so local `git status`/worktree cleanliness is UNKNOWN and must not be invented.

# Design boundary

This task hardens evidence and readiness only. It does not execute the bounded patcher, write an OTBM, add a sandbox mutation runner, add a map-wide quality gate, add gameplay E2E, or implement donor/region merge. Those remain separate bounded tasks.

## Context checkpoint

### State

- PROVEN: root `AGENTS.md`, repository map, context routing and Phase 8 final handoff were re-read from current `main`.
- PROVEN: current reusable OTBM catalogue already contains World Index, Quest Map Validator, Reachability, Spawn/NPC, Storage Graph, Semantic Diff, Geometry Audit, Script Resolution and Repair Preflight.
- PROVEN: open PR #316 is donor/Targuna evidence only and explicitly does not introduce map writing.
- PROVEN: draft PR #413 is open and mergeable on the dedicated branch.
- PROVEN: the current branch adds deterministic appearances/items/rules/script-corpus pins, explicit readiness and structural hypothetical resolver diffing.
- PROVEN: a new focused hardening test module covers readiness, same-status handler changes, order normalization and evidence pins.
- PROVEN: the report schema remains `canary-otbm-repair-preflight-v1`; new hardening fields are described without making old v1 reports invalid.
- PROVEN: changed files currently contain only the task record, preflight core/CLI/docs/schema and the dedicated hardening test.
- UNKNOWN: local Git worktree state; no local checkout is exposed.
- UNKNOWN: current-head CI result; validation has not yet completed.

### Current implementation plan

1. inspect the complete PR diff for correctness and accidental scope expansion;
2. apply only the narrow catalogue/changelog description updates justified by the public evidence contract change;
3. run/inspect current-head GitHub checks;
4. repair any failing validation without weakening tests or safety gates;
5. update this checkpoint and PR body, then mark ready/merge only when the autonomous merge gate is satisfied.

### Next action

Review the complete PR #413 diff, then make narrow shared-document updates from current branch/main state before CI readiness.
