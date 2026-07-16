---
task_id: CAN-20260716-otbm-map-quality-gate
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/otbm-map-quality-gate
base_branch: main
created: 2026-07-16T10:12:00+02:00
updated: 2026-07-16T10:31:00+02:00
last_verified_commit: "7d1989a3fa20632bc79994eb719d37cb8d3c679a"
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
- [x] Add schema/docs and narrow catalogue/changelog updates.
- [x] Verify current-head required implementation checks before readiness.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `870fc9acb31d8ec19f7466be9b5f4fa99567eb21`, the squash merge of PR #413.
- PR #419 targets `blakinio/canary:main` from `blakinio/canary:feat/otbm-map-quality-gate`.
- PR #316 remains a separate bounded Targuna donor-isolation audit; this task does not own donor extraction or import paths.
- No open PR or repository search result was found for an existing OTBM Map Quality Gate or sandbox verifier.
- Geometry source identity is `provenance.source.sha256`; reachability is `provenance.worldIndexManifest.source.sha256`; script resolution is `sources.itemAudit.map.sha256`.
- Existing script resolution keeps runtime resolution separate from review disposition; reviewed unresolved evidence remains unresolved.
- Module catalogue diff contains only the new OTBM static map quality gate row.
- Changelog diff contains only one new OTBM static map quality gate Unreleased entry.
- No local checkout is exposed in this connector session, so local Git/worktree state is UNKNOWN and is not claimed as clean.

# Design boundary

Version 1 is a thin report aggregator over exactly three canonical inputs: Geometry Audit, Reachability and Script Resolution. Quest Map Validator and Spawn/NPC validation remain future optional adapters because their selected source/scope semantics require an explicit compatibility policy. This task does not implement sandbox mutation, server runtime E2E, physical-client E2E, donor-map merge planning or region writing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:31:00+02:00
head: 7d1989a3fa20632bc79994eb719d37cb8d3c679a
branch: feat/otbm-map-quality-gate
pr: 419
status: ready
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
  - PR 419 is isolated on a dedicated blakinio/canary branch with base main
  - core aggregation reuses geometry reachability and script-resolution reports only
  - all three adapters require exact same-map SHA-256 evidence and fail closed on mismatch or missing provenance
  - exact totals come from component summaries while bounded samples preserve original evidence
  - script conflicts normalize to error and unresolved statuses remain unresolved
  - default severity gate fails on errors while unresolved failure is an independent opt-in policy
  - create-new output publication uses exclusive creation and cannot clobber a late-created output path
  - report schema and durable docs define canary-otbm-map-quality-v1 without claiming gameplay or global coverage
  - MODULE_CATALOG patch contains exactly one added OTBM quality-gate row
  - CHANGELOG patch contains exactly one added OTBM quality-gate entry
  - Agent Task Ownership run 29483631860 passed on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
  - CI run 29483632065 passed on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
  - OTBM Map Tools run 29483631261 passed on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
  - AI Agent Tools run 29483631187 passed on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
derived:
  - the static map-test aggregation layer is complete and ready for final ready-state validation
unknown:
  - exact-head ready-state checks after this task-record commit
  - final review and branch-protection merge state
conflicts: []
first_failure:
  marker: none remaining
  evidence: implementation and shared-document exact-head checks are green
rejected_hypotheses:
  - rescan or reparse OTBM inside the quality gate
  - infer stairs ladders holes or gameplay intent from sprites or names
  - combine quest and spawn selected-scope semantics into v1 without an explicit compatibility contract
  - use atomic replace for create-new publication without exclusive no-clobber semantics
  - deduplicate cross-component events into inferred root-cause defects
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-otbm-map-quality-gate.md
  - docs/ai-agent/OTBM_MAP_QUALITY_GATE.md
  - docs/ai-agent/OTBM_MAP_QUALITY_GATE.schema.json
  - tools/ai-agent/otbm_map_quality.py
  - tools/ai-agent/otbm_map_quality_tool.py
  - tools/ai-agent/test_otbm_map_quality.py
  - tools/ai-agent/test_otbm_map_quality_output_safety.py
validation:
  - command: GitHub Actions Agent Task Ownership run 29483631860
    result: PASS
    evidence: completed success on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
  - command: GitHub Actions CI run 29483632065
    result: PASS
    evidence: completed success on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
  - command: GitHub Actions OTBM Map Tools run 29483631261
    result: PASS
    evidence: completed success on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
  - command: GitHub Actions AI Agent Tools run 29483631187
    result: PASS
    evidence: unit tests and repository-wide AI-agent validation completed successfully on head 7d1989a3fa20632bc79994eb719d37cb8d3c679a
blockers: []
next_action: Mark PR 419 ready for review, verify ready-state exact-head checks and mergeability, then squash-merge only if every gate remains green.
```

# Completion

- Final status: ready
- Canary PR: #419
- Catalogue updated: yes; one OTBM quality-gate row only
- Changelog updated: yes; one OTBM quality-gate Unreleased entry only
- Archived at: pending post-merge lifecycle automation
