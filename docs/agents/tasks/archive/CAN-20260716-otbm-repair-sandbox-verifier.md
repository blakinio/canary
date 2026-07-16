---
task_id: CAN-20260716-otbm-repair-sandbox-verifier
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-sandbox-verifier
base_branch: main
created: 2026-07-16T10:42:00+02:00
updated: 2026-07-16T09:12:28Z
last_verified_commit: "52eb5932d94feeec8a1ba81ece7de7958ed06eea"
risk: high
related_issue: ""
related_pr: "422"
depends_on:
  - "OTBM Phase 8 bounded patcher #325/#333"
  - "OTBM repair preflight #406/#413"
  - "OTBM map quality gate #419"
  - "OTBM script resolution #104"
blocks:
  - "future real-map repair execution workflow"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_repair_sandbox.py
    - tools/ai-agent/otbm_repair_sandbox_tool.py
    - tools/ai-agent/test_otbm_repair_sandbox.py
    - docs/ai-agent/OTBM_REPAIR_SANDBOX.md
    - docs/ai-agent/OTBM_REPAIR_SANDBOX_REPORT.schema.json
    - docs/agents/tasks/active/CAN-20260716-otbm-repair-sandbox-verifier.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_bounded_patch.py
    - tools/ai-agent/otbm_bounded_patch_types.py
    - tools/ai-agent/otbm_item_audit.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_repair_preflight.py
    - tools/ai-agent/otbm_repair_preflight_tool.py
modules_touched:
  - OTBM repair sandbox verifier
reuses:
  - existing Phase 8 bounded patcher and proof
  - existing item audit
  - existing script-resolution audit
  - existing repair-preflight correlation and runtime diff
  - existing repair-preflight evidence pin helpers
public_interfaces:
  - canary-otbm-repair-sandbox-verification-v1
  - OTBM repair sandbox verifier CLI
cross_repo_tasks: []
completed: 2026-07-16T09:12:28Z
---

# Goal

Verify an already-reviewed Phase 8 patch on its distinct artifact copy using real before/after item-audit and script-resolution evidence, while reusing Phase 8 confinement, reparse, World Index and Semantic Diff proof and preserving the original map unchanged.

# Acceptance criteria

- [x] Reuse `apply_bounded_patch()`; no new writer/parser/World Index/Semantic Diff pipeline.
- [x] Require a valid Phase 8 plan and matching source map.
- [x] Require Phase 8 `ok`, `source.unchanged` and all confinement proof flags.
- [x] Run existing item audit and script resolution on source and actual patched copy.
- [x] Correlate exactly one before/after candidate per operation with stable position/itemId/itemDepth/tilePlacementIndex.
- [x] Prove targeted attribute is `expected` before and `replacement` after and other mechanic attrs stay unchanged.
- [x] Emit existing structural resolver before/after diff; preserve unresolved/conflicting evidence.
- [x] Recheck original source hash before publication.
- [x] Pin plan/source/scanner/metadata/rules/script and Phase 8 result/evidence.
- [x] Create verification report with no-clobber publication.
- [x] Never claim gameplay correctness, player intent, reachability or physical-client E2E.
- [x] Do not invent reachability inputs for Map Quality Gate integration.
- [x] Add real-scanner synthetic integration coverage and schema/docs.
- [x] Update catalogue/changelog narrowly.
- [x] Pass exact-head implementation checks before readiness.

# Confirmed context

- Writable repository is exactly `blakinio/canary`.
- Task-start `main` was `8660f7cb81978616df804ee6d4b0516e9c0af38f` (PR #419 merge).
- `main` advanced to `44cd23bec185a5e0a6167d6180008eddd47ac594` after branch creation through later lifecycle governance; no sandbox implementation-path conflict is known.
- PR #422 targets `blakinio/canary:main` from `feat/otbm-repair-sandbox-verifier` and is mergeable.
- No overlapping repair-sandbox PR/implementation was found by targeted search.
- Phase 8 already owns copy-only mutation, byte confinement, full reparse, World Index and exact Semantic Diff proof.
- #413 provides exact correlation, structural runtime diff and deterministic evidence-pin helpers.
- #419 cannot be auto-run without explicit compatible Reachability inputs; v1 sandbox does not invent them.
- The catalogue patch adds exactly one sandbox row and the changelog patch adds exactly one sandbox bullet.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T11:10:00+02:00
head: 080b69cd20bbc05b1c1f21cf05f66c031e6a1817
branch: feat/otbm-repair-sandbox-verifier
pr: 422
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_repair_sandbox.py
  - tools/ai-agent/otbm_repair_sandbox_tool.py
  - tools/ai-agent/test_otbm_repair_sandbox.py
  - docs/ai-agent/OTBM_REPAIR_SANDBOX.md
  - docs/ai-agent/OTBM_REPAIR_SANDBOX_REPORT.schema.json
  - docs/agents/tasks/active/CAN-20260716-otbm-repair-sandbox-verifier.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - Phase 8 already provides patch confinement reparse World Index and exact Semantic Diff proof
  - sandbox verifier calls existing apply_bounded_patch and verifies the persisted Phase 8 result/evidence manifest
  - real item audit and script resolution run on both source and actual patched output
  - each operation requires exact before/after correlation at planned tilePlacementIndex itemId and itemDepth
  - target expected-to-replacement and untargeted mechanic preservation are verified
  - structural runtime diff is measured from real before/after resolver placements
  - source plan scanner and content-affecting audit/script evidence are rechecked before create-new report publication
  - real native-scanner integration test observes handled-directly to unresolved on the actual Phase 8 output while source bytes remain unchanged
  - MODULE_CATALOG diff contains exactly one new sandbox row
  - CHANGELOG diff contains exactly one new sandbox bullet
  - CI run 29485653505 passed on head 080b69cd20bbc05b1c1f21cf05f66c031e6a1817
  - Agent Task Ownership run 29485653261 passed on head 080b69cd20bbc05b1c1f21cf05f66c031e6a1817
  - OTBM Map Tools run 29485653239 passed on head 080b69cd20bbc05b1c1f21cf05f66c031e6a1817
  - AI Agent Tools run 29485653289 passed on head 080b69cd20bbc05b1c1f21cf05f66c031e6a1817
derived:
  - sandbox structural verification is complete and ready for final ready-state validation
unknown:
  - exact-head ready-state checks after this task-record commit
  - final review and branch-protection merge state
conflicts: []
first_failure:
  marker: none remaining
  evidence: implementation and exact-head checks are green
rejected_hypotheses:
  - another OTBM writer or parser
  - duplicate World Index or Semantic Diff proof
  - invented reachability origins/routes
  - treating sandbox ok as proof of gameplay correctness or absence of runtime regression
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-otbm-repair-sandbox-verifier.md
  - docs/ai-agent/OTBM_REPAIR_SANDBOX.md
  - docs/ai-agent/OTBM_REPAIR_SANDBOX_REPORT.schema.json
  - tools/ai-agent/otbm_repair_sandbox.py
  - tools/ai-agent/otbm_repair_sandbox_tool.py
  - tools/ai-agent/test_otbm_repair_sandbox.py
validation:
  - command: GitHub Actions CI run 29485653505
    result: PASS
    evidence: exact implementation/shared-doc head 080b69cd20bbc05b1c1f21cf05f66c031e6a1817
  - command: GitHub Actions Agent Task Ownership run 29485653261
    result: PASS
    evidence: exact implementation/shared-doc head
  - command: GitHub Actions OTBM Map Tools run 29485653239
    result: PASS
    evidence: exact implementation/shared-doc head
  - command: GitHub Actions AI Agent Tools run 29485653289
    result: PASS
    evidence: exact implementation/shared-doc head including real scanner sandbox integration test
blockers: []
next_action: Mark PR 422 ready for review, verify exact-head ready-state checks, review threads and Required status, then squash-merge only if every gate remains green.
```

# Completion

- Final status: ready
- Canary PR: #422
- Catalogue updated: yes; one sandbox row only
- Changelog updated: yes; one sandbox bullet only
- Archived at: pending post-merge lifecycle automation

## Automated lifecycle completion

- Feature PR: #422.
- Feature head: `f3128dd3133b0b2590321f485726b9b789f050a9`.
- Merge commit: `52eb5932d94feeec8a1ba81ece7de7958ed06eea`.
- Merged at: `2026-07-16T09:12:28Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
