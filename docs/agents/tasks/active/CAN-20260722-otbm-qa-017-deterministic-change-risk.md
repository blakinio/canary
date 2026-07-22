---
task_id: CAN-20260722-otbm-qa-017-deterministic-change-risk
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-017-deterministic-change-risk-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "8bdeb2747356727df80a3b95073aa29a4dca7818"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - OTBM-QA-014 implementation active on PR 734
  - OTBM-QA-015 implementation active on PR 735
  - OTBM-QA-016 implementation active on PR 737
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_change_risk.py
    - tools/ai-agent/otbm_change_risk_tool.py
    - tools/ai-agent/test_otbm_change_risk.py
    - tools/ai-agent/test_otbm_change_risk_output_safety.py
    - tools/ai-agent/test_otbm_change_risk_schema.py
    - docs/ai-agent/OTBM_CHANGE_RISK.md
    - docs/ai-agent/OTBM_CHANGE_RISK_POLICY.schema.json
    - docs/ai-agent/OTBM_CHANGE_RISK_INPUT.schema.json
    - docs/ai-agent/OTBM_CHANGE_RISK.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
modules_touched:
  - otbm-change-risk
reuses:
  - exact finding IDs and provenance from already-delivered OTBM evidence producers
public_interfaces:
  - canary-otbm-change-risk-policy-v1
  - canary-otbm-change-risk-input-v1
  - canary-otbm-change-risk-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-017 Deterministic Change Risk Classification

## Status

IMPLEMENTING — transparent review aid only; no opaque AI score and no skip/repair/merge authorization.

## Goal

Classify potential scope of one exact OTBM change from explicit evidence-backed factors and a versioned visible policy.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T22:35:00+02:00
head: 8bdeb2747356727df80a3b95073aa29a4dca7818
branch: feat/otbm-qa-017-deterministic-change-risk-20260722
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_change_risk.py
  - tools/ai-agent/otbm_change_risk_tool.py
  - tools/ai-agent/test_otbm_change_risk.py
  - tools/ai-agent/test_otbm_change_risk_output_safety.py
  - tools/ai-agent/test_otbm_change_risk_schema.py
  - docs/ai-agent/OTBM_CHANGE_RISK.md
  - docs/ai-agent/OTBM_CHANGE_RISK_POLICY.schema.json
  - docs/ai-agent/OTBM_CHANGE_RISK_INPUT.schema.json
  - docs/ai-agent/OTBM_CHANGE_RISK.schema.json
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
proven:
  - Roadmap QA-017 requires explicit visible contributing factors and forbids an opaque AI score from authorizing safe skip, repair or merge.
  - Candidate factors include critical infrastructure, identifier semantics, quest dependencies, fragile routes, certification invalidation, multi-region impact, unresolved evidence and asset-driven walkability semantics.
derived:
  - A versioned weight/threshold policy over exact caller-supplied factor evidence can provide a transparent deterministic review aid without duplicating upstream validators.
unknown:
  - Risk classification cannot prove actual gameplay regression or authorize merge safety.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation validation has run yet.
rejected_hypotheses:
  - Use model intuition or hidden weighting: roadmap requires explicit deterministic policy.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
validation:
  - command: fresh live-state/overlap preflight
    result: PASS
    evidence: main 8bdeb2747356727df80a3b95073aa29a4dca7818; no competing QA-017 PR found.
blockers: []
next_action: Open a draft PR, implement policy-driven factor classification with exact evidence references and focused tests, then validate current-head workflows.
```
