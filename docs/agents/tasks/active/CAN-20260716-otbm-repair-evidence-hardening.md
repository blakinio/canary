---
task_id: CAN-20260716-otbm-repair-evidence-hardening
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-evidence-hardening
base_branch: main
created: 2026-07-16T09:20:00+02:00
updated: 2026-07-16T09:50:00+02:00
last_verified_commit: "ba8d3195e22fbcc2a2a7060a683feef889e5d9b9"
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

Harden the merged read-only OTBM real-map repair preflight so a reviewer can distinguish a selector match from an exact correlated/patchable candidate, reproduce the evidence inputs used by the run, and inspect exact hypothetical script-resolution changes before approving a Phase 8 draft plan.

# Acceptance criteria

- [x] Preserve the existing Phase 8 bounded patch contracts and supported mutation kinds unchanged.
- [x] Keep `ok` backward-compatible as selector-match evidence while adding explicit matched/correlated/runtime-resolved/patchable/review-ready state.
- [x] Add deterministic hashes/pins for appearances input, `items.xml`, optional rules/review-rules and the selected script corpus.
- [x] Record repository Git evidence without claiming cleanliness when Git state is unavailable.
- [x] Compare hypothetical before/after script-resolution evidence structurally, not only by top-level status string.
- [x] Surface handler/registration/source/confidence/resolution changes deterministically.
- [x] Preserve unresolved, referenced-only, partially-resolved and conflicting evidence without promotion to handled.
- [x] Keep the source map immutable and retain source/scanner rechecks and create-new output safety.
- [x] Add focused regression coverage and update report schema/docs.
- [ ] Finish narrow catalogue/changelog integration without unrelated shared-index drift.
- [ ] Verify current-head required checks before readiness/merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` was `8950a275e258ccc0f1a6781c9ff9c8ea089210a0`.
- Draft PR #413 targets `blakinio/canary:main` from `blakinio/canary:feat/otbm-repair-evidence-hardening`.
- Phase 8 remains closed; this task does not add map geometry/item/tile insertion or another writer.
- PR #316 owns separate Targuna donor-isolation evidence and does not overlap exclusive paths here.
- PR #393 touches shared catalogue/test-infrastructure documentation; shared-index edits must remain narrow.
- No local checkout is exposed in this connector session, so local worktree state is not used as proof.

# Design boundary

This task hardens evidence and readiness only. It does not execute the bounded patcher, write an OTBM, add a sandbox mutation runner, add a map-wide quality gate, add gameplay E2E, or implement donor/region merge. Those remain separate bounded tasks.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T09:50:00+02:00
head: ba8d3195e22fbcc2a2a7060a683feef889e5d9b9
branch: feat/otbm-repair-evidence-hardening
pr: 413
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_repair_preflight.py
  - tools/ai-agent/otbm_repair_preflight_tool.py
  - tools/ai-agent/test_otbm_repair_preflight.py
  - tools/ai-agent/test_otbm_repair_preflight_hardening.py
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json
  - docs/agents/tasks/active/CAN-20260716-otbm-repair-evidence-hardening.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - Phase 8 remains closed and its supported mutation kinds are unchanged
  - PR 413 adds deterministic appearances items rules and script-corpus evidence pins
  - PR 413 adds explicit matched correlated runtimeResolved patchable and reviewReady evidence
  - hypothetical resolver comparison detects structural evidence changes even when status text is unchanged
  - source-map and native-scanner immutability checks remain in place
  - AI Agent Tools OTBM Map Tools and repository CI passed on prior implementation heads
derived:
  - the implementation is functionally green and observed failures so far are task-checkpoint metadata only
unknown:
  - final exact-head validation after checkpoint and shared-index cleanup
  - final review and branch-protection state
conflicts: []
first_failure:
  marker: Agent Task Ownership checkpoint metadata
  evidence: latest run rejected checkpoint status active; checkpoint status is now implementing
rejected_hypotheses:
  - broaden Phase 8 to implement map geometry or region writing in this task
  - treat top-level ok as proof of patch safety or gameplay correctness
  - treat unavailable Git metadata as a clean worktree
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-otbm-repair-evidence-hardening.md
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md
  - docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json
  - tools/ai-agent/otbm_repair_preflight.py
  - tools/ai-agent/otbm_repair_preflight_tool.py
  - tools/ai-agent/test_otbm_repair_preflight_hardening.py
validation:
  - command: GitHub Actions AI Agent Tools
    result: PASS
    evidence: successful on implementation heads before metadata-only fixes
  - command: GitHub Actions OTBM Map Tools
    result: PASS
    evidence: successful on implementation heads before metadata-only fixes
  - command: GitHub Actions CI
    result: PASS
    evidence: successful on implementation heads before metadata-only fixes
  - command: GitHub Actions Agent Task Ownership
    result: FAIL
    evidence: latest failure was unsupported checkpoint status active; corrected to implementing
blockers:
  - exact-head validation after metadata repair
  - remove unrelated MODULE_CATALOG drift and add narrow changelog entry
next_action: Remove unrelated shared-index drift, add only the OTBM preflight changelog/catalogue updates, then verify exact-head ownership and repository checks.
```

# Completion

- Final status: implementing
- Canary PR: #413
- Catalogue updated: pending narrow cleanup
- Changelog updated: pending narrow integration
- Archived at: not archived
