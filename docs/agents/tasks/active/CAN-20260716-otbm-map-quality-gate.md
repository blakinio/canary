---
task_id: CAN-20260716-otbm-map-quality-gate
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-map-quality-gate
base_branch: main
created: 2026-07-16T10:12:00+02:00
updated: 2026-07-16T10:24:00+02:00
last_verified_commit: "1e01eb60e38de92e099342d9d3008b87ece87e7a"
risk: medium
related_issue: ""
related_pr: "419"
depends_on:
  - "OTBM World Index #219"
  - "OTBM script-resolution audit #104"
  - "OTBM reachability validator #274"
  - "OTBM geometry audit #322"
  - "OTBM repair evidence hardening #413"
blocks:
  - "future OTBM repair sandbox verifier"
  - "future OTBM donor/region merge quality gate"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_map_quality.py
    - tools/ai-agent/otbm_map_quality_tool.py
    - tools/ai-agent/test_otbm_map_quality.py
    - tools/ai-agent/test_otbm_map_quality_output_safety.py
    - docs/ai-agent/OTBM_MAP_QUALITY_GATE.md
    - docs/ai-agent/OTBM_MAP_QUALITY_GATE.schema.json
    - docs/agents/tasks/active/CAN-20260716-otbm-map-quality-gate.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/OTBM_PHASE8_FINAL_HANDOFF.md
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_GEOMETRY_AUDIT.md
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_reachability.py
    - tools/ai-agent/otbm_geometry_audit.py
modules_touched:
  - OTBM map quality gate
reuses:
  - existing versioned geometry-audit reports
  - existing versioned reachability reports
  - existing versioned script-resolution reports
  - existing World Index source provenance
public_interfaces:
  - canary-otbm-map-quality-v1
  - OTBM map quality gate CLI
cross_repo_tasks: []
---

# Goal

Add a deterministic read-only OTBM Map Quality Gate that combines already-generated canonical geometry, reachability and script-resolution evidence for one proven map source into one machine-readable quality report with explicit `error`, `warning`, `unresolved` and `info` outcomes.

# Acceptance criteria

- [x] Reuse existing reports; do not parse or write OTBM and do not rescan the map independently.
- [x] Require one geometry report, one reachability report and one script-resolution report in their existing versioned formats.
- [x] Prove all three reports refer to the same map SHA-256; fail closed when source identity cannot be extracted or differs.
- [x] Hash and pin every input report and record the exact supported format consumed.
- [x] Preserve original component findings/statuses and normalize them deterministically without inventing gameplay intent.
- [x] Keep `error`, `warning`, `unresolved` and `info` separate in summary and samples.
- [x] Treat script-resolution conflicts as errors; preserve runtime unresolved/referenced-only/partially-resolved evidence as unresolved rather than handled.
- [x] Do not promote geometry orphan candidates, conditional reachability or reviewed unresolved identifiers into proven gameplay defects.
- [x] Expose a configurable fail threshold without changing underlying evidence classification.
- [x] Bound and deterministically sample normalized findings while retaining exact totals.
- [x] Emit only a report artifact; never modify source maps, `.widx`, datapacks, scripts or assets.
- [x] Make create-new report publication fail closed against late output races; explicit overwrite remains separate.
- [x] Add focused tests for source mismatch, severity aggregation, unresolved preservation, deterministic ordering/truncation, CLI exit policy and output publication safety.
- [ ] Add schema/docs and narrow catalogue/changelog updates.
- [ ] Verify current-head required checks before readiness/merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `870fc9acb31d8ec19f7466be9b5f4fa99567eb21`, the squash merge of PR #413.
- Draft PR #419 targets `blakinio/canary:main` from `blakinio/canary:feat/otbm-map-quality-gate`.
- PR #316 remains a separate bounded Targuna donor-isolation audit; this task does not own donor extraction or import paths.
- No open PR or repository search result was found for an existing OTBM Map Quality Gate or sandbox verifier.
- Geometry source identity is `provenance.source.sha256`; reachability is `provenance.worldIndexManifest.source.sha256`; script resolution is `sources.itemAudit.map.sha256`.
- Existing script resolution keeps runtime resolution separate from review disposition; reviewed unresolved evidence remains unresolved.
- No local checkout is exposed in this connector session, so local Git/worktree state is UNKNOWN and is not claimed as clean.

# Design boundary

Version 1 is a thin report aggregator over exactly three canonical inputs: Geometry Audit, Reachability and Script Resolution. Quest Map Validator and Spawn/NPC validation remain future optional adapters because their selected source/scope semantics require an explicit compatibility policy. This task does not implement sandbox mutation, server runtime E2E, physical-client E2E, donor-map merge planning or region writing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:24:00+02:00
head: 1e01eb60e38de92e099342d9d3008b87ece87e7a
branch: feat/otbm-map-quality-gate
pr: 419
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_map_quality.py
  - tools/ai-agent/otbm_map_quality_tool.py
  - tools/ai-agent/test_otbm_map_quality.py
  - tools/ai-agent/test_otbm_map_quality_output_safety.py
  - docs/ai-agent/OTBM_MAP_QUALITY_GATE.md
  - docs/ai-agent/OTBM_MAP_QUALITY_GATE.schema.json
  - docs/agents/tasks/active/CAN-20260716-otbm-map-quality-gate.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - task-start main is 870fc9acb31d8ec19f7466be9b5f4fa99567eb21
  - draft PR 419 is open in blakinio/canary with base main and dedicated head branch
  - core aggregation reuses geometry reachability and script-resolution reports only
  - all three adapters require exact same-map SHA-256 evidence and fail closed on mismatch or missing provenance
  - exact totals come from component summaries while bounded samples preserve original evidence
  - script conflicts normalize to error and unresolved statuses remain unresolved
  - default severity gate fails on errors while unresolved failure is an independent opt-in policy
  - create-new output publication uses exclusive creation and cannot clobber a late-created output path
  - PR 316 donor Targuna work does not own the quality-gate implementation paths
derived:
  - this report aggregator is the smallest complete static map-test layer and avoids creating another parser
unknown:
  - current-head CI and focused test results after implementation
conflicts: []
first_failure:
  marker: none
  evidence: implementation validation has not been inspected yet
rejected_hypotheses:
  - rescan or reparse OTBM inside the quality gate
  - infer stairs ladders holes or gameplay intent from sprites or names
  - combine quest and spawn selected-scope semantics into v1 without an explicit compatibility contract
  - use atomic replace for create-new publication without exclusive no-clobber semantics
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-otbm-map-quality-gate.md
  - tools/ai-agent/otbm_map_quality.py
  - tools/ai-agent/otbm_map_quality_tool.py
  - tools/ai-agent/test_otbm_map_quality.py
  - tools/ai-agent/test_otbm_map_quality_output_safety.py
validation: []
blockers: []
next_action: Add the v1 JSON schema and durable documentation, inspect CI/focused-test results, then make only narrow shared catalogue and changelog edits.
```

# Completion

- Final status: implementing
- Canary PR: #419
- Catalogue updated: pending
- Changelog updated: pending
- Archived at: not archived
