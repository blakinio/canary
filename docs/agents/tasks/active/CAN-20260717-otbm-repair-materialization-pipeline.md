---
task_id: CAN-20260717-otbm-repair-materialization-pipeline
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: active
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-materialization-pipeline
base_branch: main
created: 2026-07-17T08:15:22+02:00
updated: 2026-07-17T08:15:22+02:00
last_verified_commit: "c2e181f892ce2f094e887f1da5c6c7df207629c9"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OTBM Phase 8 bounded attribute patcher #325"
  - "OTBM real-map repair preflight #406/#413"
  - "OTBM static map quality gate #419"
  - "OTBM repair sandbox verifier #422"
  - "OTBM donor/region merge planner #424"
  - "OTBM bounded tile-area materializer #426"
blocks:
  - "future map-specific physical-client E2E scenarios"
  - "future controlled staging/promotion of verified final map artifacts"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_repair_materialization_pipeline.py
    - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
    - tools/ai-agent/test_otbm_repair_materialization_pipeline.py
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
    - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
    - docs/agents/tasks/active/CAN-20260717-otbm-repair-materialization-pipeline.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_repair_preflight.py
    - tools/ai-agent/otbm_repair_preflight_tool.py
    - tools/ai-agent/otbm_bounded_patch.py
    - tools/ai-agent/otbm_bounded_patch_types.py
    - tools/ai-agent/otbm_repair_sandbox.py
    - tools/ai-agent/otbm_repair_sandbox_tool.py
    - tools/ai-agent/otbm_region_merge_planner.py
    - tools/ai-agent/otbm_region_merge_planner_tool.py
    - tools/ai-agent/otbm_area_materializer.py
    - tools/ai-agent/otbm_area_materializer_tool.py
    - tools/ai-agent/otbm_map_quality.py
    - tools/ai-agent/otbm_map_quality_tool.py
modules_touched:
  - OTBM repair/materialization orchestration pipeline
reuses:
  - OTBM real-map repair preflight
  - Phase 8 bounded existing-attribute patcher
  - OTBM repair sandbox verifier
  - OTBM donor/region merge planner
  - OTBM bounded tile-area materializer
  - OTBM static map quality gate
  - Unified OTBM World Index
  - Semantic OTBM Diff
public_interfaces:
  - canary-otbm-repair-materialization-pipeline-v1
  - OTBM repair/materialization pipeline CLI
cross_repo_tasks: []
---

# Goal

Add the smallest reusable fail-closed orchestration boundary that composes the already-merged OTBM repair/materialization tools into one create-new artifact workflow without introducing another OTBM parser, writer, World Index, Semantic Diff, script resolver, renderer, E2E orchestrator or deployment system.

# Lean reuse decision

- Reuse unchanged: real-map repair preflight, Phase 8 bounded patcher, repair sandbox verifier, donor/region merge planner, complete TILE_AREA materializer, Map Quality Gate, canonical World Index and Semantic Diff.
- Missing boundary: one deterministic controller that selects exactly one existing mutation path, pins every explicit input/plan/approval, invokes only the matching existing mutation/verification contract, requires an explicit post-write Map Quality report for the exact produced output map, proves the original source remains unchanged, and publishes a machine-readable pipeline result.
- Configuration alone is insufficient because the existing CLIs intentionally remain separate: no current contract binds mutation-mode exclusivity, exact input pins, produced-output identity, post-write quality-gate identity and final create-new artifact evidence into one fail-closed result.
- No new writer or approval semantics are introduced. Therefore no new ADR is planned unless implementation discovery proves a genuinely new safety/approval boundary is unavoidable.

# Acceptance criteria

- [ ] Accept explicit source inputs only; no implicit production map or asset discovery.
- [ ] Support exactly two mutation modes: reviewed Phase 8 fixed-width attribute repair through the existing repair sandbox, or approved zero-translation complete-TILE_AREA materialization through the existing materializer.
- [ ] Require the existing reviewed Phase 8 plan for attribute mode and the existing region plan plus separate area-materialization approval for TILE_AREA mode.
- [ ] SHA-256 pin every supplied file input, plan, approval and post-write evidence input used by the orchestration result.
- [ ] Reject mode ambiguity, symlinks, path escape, output/source collision and overwrite of an existing final artifact/result.
- [ ] Never mutate a source map in place and prove source SHA-256/size/stat identity unchanged before final publication.
- [ ] Reuse existing mutation/post-write proof rather than duplicating Phase 8 or materializer reparse/World Index/Semantic Diff logic.
- [ ] Require an explicit existing `canary-otbm-map-quality-v1` report whose source-map SHA-256 exactly matches the produced output map; preserve error/warning/unresolved/info and fail closed when configured policy is not satisfied.
- [ ] Preserve unresolved/conflicting runtime evidence; never promote it to handled.
- [ ] Publish deterministic `canary-otbm-repair-materialization-pipeline-v1` evidence with exact source/output hashes, mutation result pins, quality-report pin and explicit non-claims for gameplay correctness/physical E2E.
- [ ] Keep generated maps, `.widx`, assets, reports and renders outside Git.
- [ ] Add focused synthetic/integration tests without private/user maps or client assets.
- [ ] Update catalogue/changelog narrowly after resolving current shared-path overlap with PR #451.
- [ ] Pass the repository exact-final-head gate before squash merge; archive lifecycle in a separate PR.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; all `opentibiabr/*` repositories are read-only.
- Task-start `main` is `c2e181f892ce2f094e887f1da5c6c7df207629c9`.
- No open OTBM-specific PR was found by live PR search at task start.
- Open PRs #451, #453 and #455 are unrelated. PR #451 currently also touches shared `MODULE_CATALOG.md` and `CHANGELOG.md`; exclusive implementation paths do not overlap.
- Existing writer boundaries remain closed: fixed-width existing attributes only for Phase 8 and complete same-coordinate zero-translation TILE_AREA replacement/insertion/deletion only for the area materializer.
- Physical-client E2E is deferred from this slice and must reuse the existing Universal OTS E2E platform when deterministic feature-owned runtime scenarios exist.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T08:15:22+02:00
head: c2e181f892ce2f094e887f1da5c6c7df207629c9
branch: feat/otbm-repair-materialization-pipeline
pr: null
status: active
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - tools/ai-agent/otbm_repair_materialization_pipeline.py
  - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
  - tools/ai-agent/test_otbm_repair_materialization_pipeline.py
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
  - docs/agents/tasks/active/CAN-20260717-otbm-repair-materialization-pipeline.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - current main is c2e181f892ce2f094e887f1da5c6c7df207629c9
  - no open OTBM-specific PR was found at task start
  - existing Phase 8 and TILE_AREA writer boundaries are sufficient and must remain unchanged
  - existing sandbox and materializer already own mutation confinement reparse World Index and Semantic Diff proof
  - existing Map Quality Gate requires exact same-map SHA identity and preserves unresolved evidence
  - missing reusable boundary is orchestration and evidence binding only
  - PR 451 overlap is limited to shared catalogue/changelog paths and must be resolved before editing those shared files
derived:
  - one mode-exclusive orchestration result can compose existing contracts without a new structural writer ADR
unknown:
  - exact minimal live callable surface for area materializer and map-quality CLI until source inspection completes
conflicts: []
first_failure:
  marker: none
  evidence: no implementation attempted yet
rejected_hypotheses:
  - another OTBM parser
  - another World Index or Semantic Diff
  - another script resolver or renderer
  - another full-map writer
  - broadening Phase 8 or TILE_AREA materializer writer boundaries
  - inventing reachability origins routes transitions coordinates or gameplay evidence
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-repair-materialization-pipeline.md
validation: []
blockers: []
next_action: Open a draft PR, inspect the exact callable APIs of the existing sandbox, area materializer and map-quality gate, then implement the smallest composition layer on new paths only.
```
