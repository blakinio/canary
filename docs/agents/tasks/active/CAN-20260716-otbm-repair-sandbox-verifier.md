---
task_id: CAN-20260716-otbm-repair-sandbox-verifier
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-sandbox-verifier
base_branch: main
created: 2026-07-16T10:42:00+02:00
updated: 2026-07-16T10:42:00+02:00
last_verified_commit: "8660f7cb81978616df804ee6d4b0516e9c0af38f"
risk: high
related_issue: ""
related_pr: ""
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
modules_touched:
  - OTBM repair sandbox verifier
reuses:
  - existing Phase 8 bounded patcher and proof
  - existing item audit
  - existing script-resolution audit
  - existing repair-preflight correlation and runtime diff
public_interfaces:
  - canary-otbm-repair-sandbox-verification-v1
  - OTBM repair sandbox verifier CLI
cross_repo_tasks: []
---

# Goal

Verify an already-reviewed Phase 8 patch on its distinct artifact copy using real before/after item-audit and script-resolution evidence, while reusing Phase 8 confinement, reparse, World Index and Semantic Diff proof and preserving the original map unchanged.

# Acceptance criteria

- [ ] Reuse `apply_bounded_patch()`; no new writer/parser/World Index/Semantic Diff pipeline.
- [ ] Require a valid Phase 8 plan and matching source map.
- [ ] Require Phase 8 `ok`, `source.unchanged` and all confinement proof flags.
- [ ] Run existing item audit and script resolution on source and actual patched copy.
- [ ] Correlate exactly one before/after candidate per operation with stable position/itemId/itemDepth/tilePlacementIndex.
- [ ] Prove targeted attribute is `expected` before and `replacement` after and other mechanic attrs stay unchanged.
- [ ] Emit existing structural resolver before/after diff; preserve unresolved/conflicting evidence.
- [ ] Recheck original source hash before publication.
- [ ] Pin plan/source/scanner/metadata/rules/script and Phase 8 result evidence.
- [ ] Create verification report with no-clobber publication.
- [ ] Never claim gameplay correctness, player intent, reachability or physical-client E2E.
- [ ] Do not invent reachability inputs for Map Quality Gate integration.
- [ ] Add real-scanner synthetic integration coverage and schema/docs.
- [ ] Update catalogue/changelog narrowly and pass current-head gates.

# Confirmed context

- Writable repository is exactly `blakinio/canary`.
- Task-start `main` is `8660f7cb81978616df804ee6d4b0516e9c0af38f` (PR #419 merge).
- No overlapping repair-sandbox PR/implementation was found by targeted search.
- Phase 8 already owns copy-only mutation, byte confinement, full reparse, World Index and exact Semantic Diff proof.
- #413 provides exact correlation and structural runtime diff helpers.
- #419 cannot be auto-run without explicit compatible Reachability inputs; v1 sandbox will not invent them.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:42:00+02:00
head: 8660f7cb81978616df804ee6d4b0516e9c0af38f
branch: feat/otbm-repair-sandbox-verifier
pr: null
status: implementing
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
  - item audit and script resolution can run on both source and patched output
  - repair preflight exposes reusable exact correlation and runtime-diff helpers
  - no overlapping sandbox implementation was found
derived:
  - new responsibility is real before/after mechanic and resolver verification over the Phase 8 copy
unknown:
  - exact Phase 8 evidence filename adapter details until implemented against live result contract
  - current-head CI after implementation
conflicts: []
first_failure:
  marker: none
  evidence: implementation has not run yet
rejected_hypotheses:
  - another OTBM writer or parser
  - duplicate World Index or Semantic Diff proof
  - invented reachability origins/routes
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-otbm-repair-sandbox-verifier.md
validation: []
blockers: []
next_action: Open an early draft PR and implement a thin verifier around apply_bounded_patch plus real before/after item-audit and script-resolution evidence.
```

# Completion

- Final status: implementing
- Canary PR: pending
- Catalogue updated: pending
- Changelog updated: pending
- Archived at: not archived
