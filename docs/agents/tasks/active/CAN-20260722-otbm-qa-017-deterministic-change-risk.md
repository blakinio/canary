---
task_id: CAN-20260722-otbm-qa-017-deterministic-change-risk
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-017-deterministic-change-risk-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "1700f64ffb95e0501b3bacaca8e78f5475bdffaf"
risk: medium
related_issue: ""
related_pr: "739"
depends_on:
  - shared-doc governance PR 743 merged
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
modules_touched:
  - otbm-change-risk
public_interfaces:
  - canary-otbm-change-risk-policy-v1
  - canary-otbm-change-risk-input-v1
  - canary-otbm-change-risk-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-017 Deterministic Change Risk Classification

## Status

READY — bounded QA-017 implementation is complete on PR #739. Shared governance merged through PR #743. `ci:final-gate` was applied before this final checkpoint commit; no further feature-branch commits are permitted.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:23:00+02:00
head: 1700f64ffb95e0501b3bacaca8e78f5475bdffaf
branch: feat/otbm-qa-017-deterministic-change-risk-20260722
pr: 739
status: ready
context_routes: [otbm, agent-governance]
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
  - PR 739 implements exact before/after map hashes, exact evidence references, explicit factor statuses, visible weights and deterministic thresholds.
  - The report is not an opaque AI score and never authorizes validation skip, repair or merge.
  - Pre-final CI 29959602719, Ownership 29959601792, OTBM Map Tools 29959601766 and AI Agent Tools 29959602051 passed on head 1700f64ffb95e0501b3bacaca8e78f5475bdffaf.
  - Shared governance PR 743 merged as 47759e49fca04526ef24097e9f3cf859b0f66b3a after full final-gate CI 29960786583 succeeded.
  - ci:final-gate was applied to PR 739 before this final checkpoint commit.
derived:
  - QA-017 is ready for immutable exact-final-head validation and merge without further feature changes.
unknown:
  - Risk classification does not prove actual gameplay regression or merge safety.
conflicts: []
first_failure: {marker: none, evidence: No unresolved implementation, focused-test or governance failure remains.}
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
  - tools/ai-agent/otbm_change_risk.py
  - tools/ai-agent/otbm_change_risk_tool.py
  - tools/ai-agent/test_otbm_change_risk.py
  - tools/ai-agent/test_otbm_change_risk_output_safety.py
  - tools/ai-agent/test_otbm_change_risk_schema.py
  - docs/ai-agent/OTBM_CHANGE_RISK.md
  - docs/ai-agent/OTBM_CHANGE_RISK_POLICY.schema.json
  - docs/ai-agent/OTBM_CHANGE_RISK_INPUT.schema.json
  - docs/ai-agent/OTBM_CHANGE_RISK.schema.json
validation:
  - command: GitHub Actions pre-final CI/Ownership/OTBM/AI
    result: PASS
    evidence: 29959602719, 29959601792, 29959601766 and 29959602051 all succeeded.
blockers: []
next_action: Verify exact-final-head CI, Ownership, OTBM Map Tools and AI Agent Tools plus review/mergeability on PR 739, then mark ready, enable auto-merge and complete lifecycle closure after merge.
```
