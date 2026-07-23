---
task_id: CAN-20260722-otbm-qa-016-release-provenance-freshness
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
related_pr: "737"
depends_on:
  - shared-doc governance PR 743 merged
owned_paths:
  exclusive: []
  shared: []
  read_only:
    - tools/ai-agent/otbm_release_provenance.py
    - tools/ai-agent/otbm_release_provenance_tool.py
    - docs/ai-agent/OTBM_RELEASE_PROVENANCE.md
    - docs/ai-agent/OTBM_RELEASE_BOM.schema.json
    - docs/ai-agent/OTBM_RELEASE_PROVENANCE.schema.json
modules_touched:
  - otbm-release-provenance
public_interfaces:
  - canary-otbm-release-bom-v1
  - canary-otbm-release-provenance-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-016 Release Provenance, Upgrade Compatibility and Certification Freshness

## Status

COMPLETE — bounded QA-016 implementation merged through feature PR #737 and shared governance merged through PR #743. This lifecycle record releases active ownership.

## Delivered

- Exact component SHA-256 release BOM comparison.
- Dependency-scoped freshness and stale certification dimensions without treating timestamps as proof.
- Deterministic read-only output and provenance.
- No rerun of Semantic Diff, validators or Physical E2E and no mutation of map, assets, evidence or certification.

## Merge evidence

- Feature PR #737 final head: `bea72729712015bfc11f3f0c23c56d164c1cd16d`.
- Feature squash merge: `e93ab989229bde400e9660e0adf9d336668b26ea`.
- Exact-final CI `29963659235`: success.
- Exact-final Agent Task Ownership `29963082646`: success.
- Exact-final OTBM Map Tools `29963082630`: success.
- Exact-final AI Agent Tools `29963082640`: success.
- Shared governance PR #743 merged as `47759e49fca04526ef24097e9f3cf859b0f66b3a`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T09:32:00+02:00
head: 4f074077da44d1cc9d77db7ac768be0589313332
branch: docs/archive-otbm-qa-014-018-20260723
pr: 737
status: complete
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
proven:
  - Feature PR 737 merged as e93ab989229bde400e9660e0adf9d336668b26ea from final head bea72729712015bfc11f3f0c23c56d164c1cd16d.
  - CI 29963659235, Ownership 29963082646, OTBM Map Tools 29963082630 and AI Agent Tools 29963082640 all passed on the final feature head.
  - Shared governance PR 743 merged as 47759e49fca04526ef24097e9f3cf859b0f66b3a.
derived:
  - Active ownership can be released because feature and shared governance are merged and exact-head validation is green.
unknown:
  - Runtime/gameplay compatibility after changed dependencies still requires owning validators or Physical E2E.
conflicts: []
first_failure:
  marker: checkpoint-contract-normalization
  evidence: Feature-branch ownership diagnostics found checkpoint-only schema issues; the corrected final head passed exact-head validation.
rejected_hypotheses:
  - Treat timestamps as evidence of release freshness.
  - Treat dependency-hash stability as runtime gameplay proof.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
  - docs/agents/tasks/archive/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
validation:
  - command: GitHub Actions exact-final QA-016 validation
    result: PASS
    evidence: CI 29963659235, Ownership 29963082646, OTBM 29963082630 and AI 29963082640 succeeded.
blockers: []
next_action: none
```
