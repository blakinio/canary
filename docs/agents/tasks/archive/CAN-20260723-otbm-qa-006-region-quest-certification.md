---
task_id: CAN-20260723-otbm-qa-006-region-quest-certification
program_id: CAN-PROGRAM-OTBM
status: complete
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-006-007-certification-assurance-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "61fd176fd8dd5c258db413a9a0e781a8333479fe"
risk: medium
related_issue: ""
related_pr: "759"
depends_on:
  - CAN-20260721-otbm-qa-005-coverage-dashboard complete
owned_paths:
  exclusive: []
  shared: []
  read_only:
    - tools/ai-agent/otbm_region_quest_certification.py
    - tools/ai-agent/otbm_region_quest_certification_tool.py
    - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.md
    - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION_MANIFEST.schema.json
    - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.schema.json
modules_touched:
  - otbm-region-quest-certification
reuses:
  - canary-otbm-coverage-dashboard-v1
public_interfaces:
  - canary-otbm-certification-targets-v1
  - canary-otbm-region-quest-certification-v1
cross_repo_tasks: []
---

# CAN-20260723 — OTBM-QA-006 Region and Quest Certification

## Status

COMPLETE — feature PR #759 merged QA-006 and QA-007 as one bounded dependency chain. This lifecycle record releases QA-006 active ownership.

## Delivered

- Reviewed `canary-otbm-certification-targets-v1` bounded target selection.
- Deterministic contiguous C0-C7 certification over exact QA-005 Coverage Dashboard evidence.
- Current-map provenance requirement with stale/mixed/not-evaluated evidence collapsing formal certification to C0.
- Region/landmark-route cap at C5 and quest/mechanic-set cap at C7.
- Stable input reads, SHA-256 provenance, create-new output and explicit atomic overwrite.
- No parser, World Index, Script Resolution, pathfinder, validator, Physical E2E or candidate execution duplication.

## Merge evidence

- Feature PR #759 final head: `61fd176fd8dd5c258db413a9a0e781a8333479fe`.
- Feature squash merge: `cc376677178e7de3551675bc17639b1fe0422c6f`.
- Exact-final CI: `29994468777` — success.
- Exact-final Agent Task Ownership: `29994468554` — success.
- Exact-final OTBM Map Tools: `29994468996` — success.
- Exact-final AI Agent Tools: `29994468635` — success.
- Ready-state full CI / protected `Required`: `29994628428` — success, including Linux debug full tests and all platform builds.
- Final review audit before merge: zero inline review threads and zero review submissions.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T12:00:00+02:00
head: 61fd176fd8dd5c258db413a9a0e781a8333479fe
branch: docs/archive-otbm-qa-006-007-20260723
pr: null
status: complete
context_routes:
  - otbm
  - agent-governance
owned_paths: []
proven:
  - PR 759 merged as cc376677178e7de3551675bc17639b1fe0422c6f from final head 61fd176fd8dd5c258db413a9a0e781a8333479fe.
  - Exact-final CI 29994468777, Ownership 29994468554, OTBM Map Tools 29994468996 and AI Agent Tools 29994468635 all succeeded.
  - Ready-state full CI 29994628428 completed successfully and satisfied protected Required.
derived:
  - QA-006 active ownership can be released.
unknown: []
conflicts: []
first_failure:
  marker: resolved-validation-boundaries
  evidence: Initial related_pr/checkpoint status and test-only jsonschema dependency issues were corrected before immutable final-head validation and merge.
rejected_hypotheses:
  - Recompute QA-005 evidence inside QA-006.
  - Treat stale evidence as current certification.
  - Certify the whole world from bounded selected targets.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-otbm-qa-006-region-quest-certification.md
  - docs/agents/tasks/archive/CAN-20260723-otbm-qa-006-region-quest-certification.md
validation:
  - command: PR 759 exact-final and ready-state protected checks
    result: PASS
    evidence: Exact-final focused checks and full ready-state CI all succeeded before merge.
blockers: []
next_action: none
```
