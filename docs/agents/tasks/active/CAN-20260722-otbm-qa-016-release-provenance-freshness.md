---
task_id: CAN-20260722-otbm-qa-016-release-provenance-freshness
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-016-release-provenance-freshness-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "8bdeb2747356727df80a3b95073aa29a4dca7818"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - OTBM-QA-015 implementation active on PR 735
blocks:
  - OTBM-QA-017 deterministic change risk
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
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
modules_touched:
  - otbm-release-provenance
reuses:
  - exact SHA-256 provenance from already-delivered OTBM reports and registries
public_interfaces:
  - canary-otbm-release-bom-v1
  - canary-otbm-release-provenance-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-016 Release Provenance, Upgrade Compatibility and Certification Freshness

## Status

IMPLEMENTING — read-only exact-provenance BOM/freshness composition. No map, asset, source, evidence or certification mutation.

## Goal

Make reviewed map baselines reproducible and deterministically identify which declared evidence dimensions become stale when exact dependency hashes change.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T22:10:00+02:00
head: 8bdeb2747356727df80a3b95073aa29a4dca7818
branch: feat/otbm-qa-016-release-provenance-freshness-20260722
pr: none
status: implementing
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
  - Roadmap QA-016 requires a release/map BOM, upgrade compatibility evidence, quality history and dependency-scoped certification freshness.
  - Upload or modified timestamps are explicitly not map-freshness evidence.
  - Exact component hashes and declared dimension dependencies are sufficient to determine dependency-scoped staleness without rerunning validators.
derived:
  - QA-016 can be a generic exact-hash BOM comparator; subsystem-specific revalidation remains outside this composer.
unknown:
  - Runtime/gameplay compatibility after a changed dependency requires the owning validators or Physical E2E and is not proven by this report.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation validation has run yet.
rejected_hypotheses:
  - Treat file timestamps as freshness proof: roadmap explicitly rejects timestamp-based freshness.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-016-release-provenance-freshness.md
validation:
  - command: fresh live-state/overlap preflight
    result: PASS
    evidence: main 8bdeb2747356727df80a3b95073aa29a4dca7818; no competing QA-016 PR found.
blockers: []
next_action: Open a draft PR, implement the exact BOM/freshness comparator and focused tests, then validate current-head OTBM/AI workflows.
```
