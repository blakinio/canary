---
task_id: CAN-20260716-otbm-map-quality-gate
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-map-quality-gate
base_branch: main
created: 2026-07-16T10:12:00+02:00
updated: 2026-07-16T10:15:00+02:00
last_verified_commit: "7ff56defc2b4368bb70a500de225ea2f84c22a55"
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

- [ ] Reuse existing reports; do not parse or write OTBM and do not rescan the map independently.
- [ ] Require one geometry report, one reachability report and one script-resolution report in their existing versioned formats.
- [ ] Prove all three reports refer to the same map SHA-256; fail closed when source identity cannot be extracted or differs.
- [ ] Hash and pin every input report and record the exact supported format consumed.
- [ ] Preserve original component findings/statuses and normalize them deterministically without inventing gameplay intent.
- [ ] Keep `error`, `warning`, `unresolved` and `info` separate in summary and samples.
- [ ] Treat script-resolution conflicts as errors; preserve runtime unresolved/referenced-only/partially-resolved evidence as unresolved rather than handled.
- [ ] Do not promote geometry orphan candidates, conditional reachability or reviewed unresolved identifiers into proven gameplay defects.
- [ ] Expose a configurable fail threshold without changing underlying evidence classification.
- [ ] Bound and deterministically sample normalized findings while retaining exact totals.
- [ ] Emit only a report artifact; never modify source maps, `.widx`, datapacks, scripts or assets.
- [ ] Add focused tests for source mismatch, severity aggregation, unresolved preservation, deterministic ordering/truncation and CLI exit policy.
- [ ] Add schema/docs and narrow catalogue/changelog updates.
- [ ] Verify current-head required checks before readiness/merge.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; upstream/donor repositories remain read-only.
- Task-start `main` is `870fc9acb31d8ec19f7466be9b5f4fa99567eb21`, the squash merge of PR #413.
- Draft PR #419 targets `blakinio/canary:main` from `blakinio/canary:feat/otbm-map-quality-gate`.
- PR #316 remains a separate bounded Targuna donor-isolation audit; this task does not own donor extraction or import paths.
- No open PR or repository search result was found for an existing OTBM Map Quality Gate or sandbox verifier.
- Existing geometry and reachability reports expose versioned findings with severity/position evidence and World Index provenance.
- Existing script resolution keeps runtime resolution separate from review disposition; reviewed unresolved evidence must stay unresolved.
- No local checkout is exposed in this connector session, so local Git/worktree state is UNKNOWN and is not claimed as clean.

# Design boundary

Version 1 is a thin report aggregator over exactly three canonical inputs: Geometry Audit, Reachability and Script Resolution. Quest Map Validator and Spawn/NPC validation remain future optional adapters because their selected source/scope semantics require an explicit compatibility policy. This task does not implement sandbox mutation, server runtime E2E, physical-client E2E, donor-map merge planning or region writing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T10:15:00+02:00
head: 7ff56defc2b4368bb70a500de225ea2f84c22a55
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
  - docs/ai-agent/OTBM_MAP_QUALITY_GATE.md
  - docs/ai-agent/OTBM_MAP_QUALITY_GATE.schema.json
  - docs/agents/tasks/active/CAN-20260716-otbm-map-quality-gate.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - task-start main is 870fc9acb31d8ec19f7466be9b5f4fa99567eb21
  - draft PR 419 is open in blakinio/canary with base main and dedicated head branch
  - geometry reachability and script-resolution tooling already exist and are reusable
  - PR 316 donor Targuna work does not own the planned quality-gate implementation paths
  - no existing map-quality-gate or sandbox-verifier implementation was found by targeted repository and PR search
derived:
  - a report aggregator is the smallest complete first static map-test layer and avoids creating another parser
unknown:
  - exact source-pin field paths for every supported component report until adapters are implemented and tested against fixtures
  - current-head CI after implementation
conflicts: []
first_failure:
  marker: none
  evidence: no implementation validation has run yet
rejected_hypotheses:
  - rescan or reparse OTBM inside the quality gate
  - infer stairs ladders holes or gameplay intent from sprites or names
  - combine quest and spawn selected-scope semantics into v1 without an explicit compatibility contract
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-otbm-map-quality-gate.md
validation: []
blockers: []
next_action: Implement deterministic source-identity extraction and the geometry reachability and script-resolution adapters, then add focused tests before shared index edits.
```

# Completion

- Final status: implementing
- Canary PR: #419
- Catalogue updated: pending
- Changelog updated: pending
- Archived at: not archived
