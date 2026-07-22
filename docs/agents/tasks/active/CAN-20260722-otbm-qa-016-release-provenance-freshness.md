---
task_id: CAN-20260722-otbm-qa-016-release-provenance-freshness
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-016-release-provenance-freshness-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "29d3831678e7f568cfbd218e0aadfd9ec64d51db"
risk: medium
related_issue: ""
related_pr: "737"
depends_on:
  - shared-doc governance PR 743 merged
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_release_provenance.py
    - tools/ai-agent/otbm_release_provenance_tool.py
    - tools/ai-agent/test_otbm_release_provenance.py
    - tools/ai-agent/test_otbm_release_provenance_output_safety.py
    - tools/ai-agent/test_otbm_release_provenance_schema.py
    - docs/ai-agent/OTBM_RELEASE_PROVENANCE.md
    - docs/ai-agent/OTBM_RELEASE_BOM.schema.json
    - docs/ai-agent/OTBM_RELEASE_PROVENANCE.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
modules_touched:
  - otbm-release-provenance
public_interfaces:
  - canary-otbm-release-bom-v1
  - canary-otbm-release-provenance-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-016 Release Provenance, Upgrade Compatibility and Certification Freshness

## Status

READY — bounded QA-016 implementation is complete on PR #737. Shared governance merged through PR #743. `ci:final-gate` was applied before this final checkpoint commit; no further feature-branch commits are permitted.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:22:00+02:00
head: 29d3831678e7f568cfbd218e0aadfd9ec64d51db
branch: feat/otbm-qa-016-release-provenance-freshness-20260722
pr: 737
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_release_provenance.py
  - tools/ai-agent/otbm_release_provenance_tool.py
  - tools/ai-agent/test_otbm_release_provenance.py
  - tools/ai-agent/test_otbm_release_provenance_output_safety.py
  - tools/ai-agent/test_otbm_release_provenance_schema.py
  - docs/ai-agent/OTBM_RELEASE_PROVENANCE.md
  - docs/ai-agent/OTBM_RELEASE_BOM.schema.json
  - docs/ai-agent/OTBM_RELEASE_PROVENANCE.schema.json
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
proven:
  - PR 737 implements exact component SHA-256 BOM comparison and dependency-scoped freshness without using timestamps as freshness evidence.
  - The composer does not rerun validators, Semantic Diff or Physical E2E and does not mutate evidence or certification.
  - Pre-final CI 29959344000, Ownership 29959343913, OTBM Map Tools 29959343853 and AI Agent Tools 29959343638 passed on head 29d3831678e7f568cfbd218e0aadfd9ec64d51db.
  - Shared governance PR 743 merged as 47759e49fca04526ef24097e9f3cf859b0f66b3a after full final-gate CI 29960786583 succeeded.
  - ci:final-gate was applied to PR 737 before this final checkpoint commit.
derived:
  - QA-016 is ready for immutable exact-final-head validation and merge without further feature changes.
unknown:
  - Runtime/gameplay compatibility after changed dependencies still requires owning validators or Physical E2E.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation, focused-test or governance failure remains.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
  - tools/ai-agent/otbm_release_provenance.py
  - tools/ai-agent/otbm_release_provenance_tool.py
  - tools/ai-agent/test_otbm_release_provenance.py
  - tools/ai-agent/test_otbm_release_provenance_output_safety.py
  - tools/ai-agent/test_otbm_release_provenance_schema.py
  - docs/ai-agent/OTBM_RELEASE_PROVENANCE.md
  - docs/ai-agent/OTBM_RELEASE_BOM.schema.json
  - docs/ai-agent/OTBM_RELEASE_PROVENANCE.schema.json
validation:
  - command: GitHub Actions pre-final CI/Ownership/OTBM/AI
    result: PASS
    evidence: 29959344000, 29959343913, 29959343853 and 29959343638 all succeeded.
blockers: []
next_action: Verify exact-final-head CI, Ownership, OTBM Map Tools and AI Agent Tools plus review/mergeability on PR 737, then mark ready, enable auto-merge and complete lifecycle closure after merge.
```
