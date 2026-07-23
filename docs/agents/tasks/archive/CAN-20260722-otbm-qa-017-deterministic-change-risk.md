---
task_id: CAN-20260722-otbm-qa-017-deterministic-change-risk
program_id: CAN-PROGRAM-OTBM
status: complete
agent: "GPT-5.6 Thinking"
branch: docs/archive-otbm-qa-014-018-20260723
base_branch: main
created: 2026-07-22
updated: 2026-07-23
last_verified_commit: "4f074077da44d1cc9d77db7ac768be0589313332"
risk: medium
related_issue: ""
related_pr: "739"
depends_on:
  - shared-doc governance PR 743 merged
owned_paths:
  exclusive: []
  shared: []
  read_only:
    - tools/ai-agent/otbm_change_risk.py
    - tools/ai-agent/otbm_change_risk_tool.py
    - docs/ai-agent/OTBM_CHANGE_RISK.md
    - docs/ai-agent/OTBM_CHANGE_RISK_POLICY.schema.json
    - docs/ai-agent/OTBM_CHANGE_RISK_INPUT.schema.json
    - docs/ai-agent/OTBM_CHANGE_RISK.schema.json
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

COMPLETE — bounded QA-017 implementation merged through feature PR #739 and shared governance merged through PR #743. This lifecycle record releases active ownership.

## Delivered

- Exact before/after map hashes and exact evidence references.
- Explicit factor statuses, visible weights and deterministic thresholds.
- Review-only risk classification that never authorizes validation skip, repair or merge.
- Focused semantic, schema and output-safety tests plus documentation.

## Merge evidence

- Feature PR #739 final head: `9e5fee8a8a35d42c4bbd23f6367b0132214d385f`.
- Feature squash merge: `0a44a6ec6912e5a362c79794dd2d5367e55b4a92`.
- Exact-final CI `29963486472`: success.
- Exact-final Agent Task Ownership `29963048638`: success.
- Exact-final OTBM Map Tools `29963048693`: success.
- Exact-final AI Agent Tools `29963048655`: success.
- Shared governance PR #743 merged as `47759e49fca04526ef24097e9f3cf859b0f66b3a`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T09:33:00+02:00
head: 4f074077da44d1cc9d77db7ac768be0589313332
branch: docs/archive-otbm-qa-014-018-20260723
pr: 739
status: complete
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
proven:
  - Feature PR 739 merged as 0a44a6ec6912e5a362c79794dd2d5367e55b4a92 from final head 9e5fee8a8a35d42c4bbd23f6367b0132214d385f.
  - CI 29963486472, Ownership 29963048638, OTBM Map Tools 29963048693 and AI Agent Tools 29963048655 all passed on the final feature head.
  - Shared governance PR 743 merged as 47759e49fca04526ef24097e9f3cf859b0f66b3a.
derived:
  - Active ownership can be released because feature and shared governance are merged and exact-head validation is green.
unknown:
  - Risk classification does not prove actual gameplay regression or merge safety.
conflicts: []
first_failure:
  marker: checkpoint-contract-normalization
  evidence: Earlier ownership diagnostics found checkpoint-only schema issues; the corrected final head passed exact-head validation.
rejected_hypotheses:
  - Treat an opaque risk score as authorization to skip validation or merge.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-017-deterministic-change-risk.md
validation:
  - command: GitHub Actions exact-final QA-017 validation
    result: PASS
    evidence: CI 29963486472, Ownership 29963048638, OTBM 29963048693 and AI 29963048655 succeeded.
blockers: []
next_action: none
```
