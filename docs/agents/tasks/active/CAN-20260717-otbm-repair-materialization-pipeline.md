---
task_id: CAN-20260717-otbm-repair-materialization-pipeline
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-repair-materialization-pipeline
base_branch: main
created: 2026-07-17T08:15:22+02:00
updated: 2026-07-17T08:45:00+02:00
last_verified_commit: "c2e181f892ce2f094e887f1da5c6c7df207629c9"
risk: high
related_issue: ""
related_pr: "456"
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

Add the smallest reusable fail-closed orchestration boundary that composes the already-merged OTBM repair/materialization tools into one create-new finalization workflow without introducing another OTBM parser, writer, World Index, Semantic Diff, script resolver, renderer, E2E orchestrator or deployment system.

# Lean reuse decision

- Reuse unchanged: real-map repair preflight, Phase 8 bounded patcher, repair sandbox verifier, donor/region merge planner, complete TILE_AREA materializer, Map Quality Gate, canonical World Index and Semantic Diff.
- Missing boundary: one deterministic controller that selects exactly one existing mutation path, pins every explicit direct file input, invokes only the matching existing mutation/verification contract into an internal candidate, reruns the existing Map Quality Gate over explicit compatible component reports, proves exact candidate/output identity and source immutability, then publishes a create-new final artifact.
- Configuration alone is insufficient because the existing CLIs intentionally remain separate: no current contract binds mutation-mode exclusivity, exact input pins, reviewed mutation evidence, post-write quality source identity and final create-new publication into one fail-closed result.
- Map Quality component reports remain explicit inputs because Reachability origins/routes/transitions cannot be invented by orchestration. They are expected to come from a previously reviewed deterministic candidate; finalization replays the exact mutation and requires the newly produced candidate SHA-256 to match those reports.
- No new writer or approval semantics are introduced. The Phase 8 reviewed plan remains the attribute authorization boundary; TILE_AREA mode retains the separate existing approval contract. No new ADR is required.

# Acceptance criteria

- [x] Accept explicit source inputs only; no implicit production map or asset discovery.
- [x] Support exactly two mutation modes: reviewed Phase 8 fixed-width attribute repair through the existing repair sandbox, or approved zero-translation complete-TILE_AREA materialization through the existing materializer.
- [x] Require the existing reviewed Phase 8 plan for attribute mode and the existing region plan plus separate area-materialization approval for TILE_AREA mode.
- [x] SHA-256 pin every supplied direct file input, plan, approval and quality-component report used by finalization.
- [x] Reject mode ambiguity, symlinks, path escape and overwrite of existing final/evidence destinations.
- [x] Never mutate a source map in place and prove source SHA-256/size/stat identity unchanged before final publication.
- [x] Reuse existing mutation/post-write proof rather than duplicating Phase 8 or materializer reparse/World Index/Semantic Diff logic.
- [x] Rebuild the existing `canary-otbm-map-quality-v1` gate from explicit Geometry, Reachability and Script Resolution reports; require their common source SHA-256 to equal the newly materialized candidate; preserve error/warning/unresolved/info separately.
- [x] Fail closed on quality errors; optionally fail on warnings or unresolved evidence; never promote unresolved evidence to handled.
- [x] Publish deterministic `canary-otbm-repair-materialization-pipeline-v1` evidence with exact source/output hashes, direct input pins, mutation result pin, quality-report pin and explicit non-claims for gameplay correctness/physical E2E.
- [x] Publish the final map only after mutation verification and Map Quality success, as a byte-identical create-new copy of the internal verified candidate.
- [x] Keep generated maps, `.widx`, assets, reports and renders outside Git.
- [x] Add focused fail-closed tests plus a real synthetic TILE_AREA integration round trip without private/user maps or client assets.
- [ ] Update catalogue/changelog narrowly after resolving current shared-path overlap with PR #451.
- [ ] Pass the repository exact-final-head gate before squash merge; archive lifecycle in a separate PR.

# Confirmed context

- Writable repository is exactly `blakinio/canary`; all `opentibiabr/*` repositories are read-only.
- Task-start `main` is `c2e181f892ce2f094e887f1da5c6c7df207629c9`.
- No open OTBM-specific PR was found by live PR search at task start.
- Open PRs #451, #453 and #455 were unrelated at task start. PR #451 also touched shared `MODULE_CATALOG.md` and `CHANGELOG.md`; exclusive implementation paths do not overlap.
- Existing writer boundaries remain closed: fixed-width existing attributes only for Phase 8 and complete same-coordinate zero-translation TILE_AREA replacement/insertion/deletion only for the area materializer.
- Physical-client E2E is deferred from this slice and must reuse the existing Universal OTS E2E platform when deterministic feature-owned runtime scenarios exist.

# CI repair note

- Head `5900bae465719f81a5afb61944dc26681b8513d3` passed repository CI, OTBM Map Tools and AI Agent Tools; Ownership rejected unsupported checkpoint `status: active`.
- Head `dfec4b0233ff5085e5e2be2f3fd866ac0713a98a` again passed repository CI, OTBM Map Tools and AI Agent Tools; Ownership then exposed a second checkpoint-only defect: validation rows lacked mandatory `evidence` fields and one `result` value was not the required enum.
- Head `a5c5fd49d339bd18918ca902b46a5d0f7465bccc` passed repository CI while Ownership exposed the remaining record-level status requirement: an active task record itself must use a lifecycle status such as `implementing`, not literal `active`.
- This record and checkpoint now both use `implementing`. No OTBM implementation change is attributed to these governance repairs.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-17T08:45:00+02:00
head: a5c5fd49d339bd18918ca902b46a5d0f7465bccc
branch: feat/otbm-repair-materialization-pipeline
pr: 456
status: implementing
context_routes:
  - agent-governance
  - otbm
  - ci-repair
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
  - current task-start main is c2e181f892ce2f094e887f1da5c6c7df207629c9
  - no open OTBM-specific PR existed at task start
  - existing Phase 8 and TILE_AREA writer boundaries are reused unchanged
  - existing sandbox and materializer own mutation confinement reparse World Index and Semantic Diff proof
  - existing Map Quality Gate is reused directly and retains exact same-map SHA identity plus unresolved evidence
  - final publication occurs only after mutation verification and quality success
  - explicit quality component reports bind deterministic reviewed-candidate evidence to the replayed finalization candidate hash
  - no new approval contract or ADR is introduced
  - synthetic TILE_AREA integration coverage reuses native scanner World Index planner and materializer
  - repository CI OTBM Map Tools and AI Agent Tools passed on 5900bae465719f81a5afb61944dc26681b8513d3
  - repository CI OTBM Map Tools and AI Agent Tools passed again on dfec4b0233ff5085e5e2be2f3fd866ac0713a98a
  - repository CI passed on a5c5fd49d339bd18918ca902b46a5d0f7465bccc before this record-status-only repair
  - ownership failures so far are checkpoint/task-schema defects only and have not identified an OTBM implementation failure
  - PR 451 overlap is limited to shared catalogue/changelog paths and must be rechecked before editing those shared files
derived:
  - deterministic mutation replay plus exact quality-source hash binding closes the orchestration boundary without inventing reachability policy
unknown:
  - current-head ownership validation after correcting the active-record lifecycle status
  - whether PR 451 shared-path ownership is still active
conflicts: []
first_failure:
  marker: task ownership metadata
  evidence: Agent Task Ownership runs 29560033886, 29560198747 and 29560429143 rejected task/checkpoint schema fields while implementation workflows passed on the corresponding heads
rejected_hypotheses:
  - another OTBM parser World Index Semantic Diff script resolver renderer or full-map writer
  - broadening Phase 8 or TILE_AREA materializer writer boundaries
  - inventing reachability origins routes transitions coordinates or gameplay evidence
  - introducing a second approval format
  - publishing the final map before quality verification
changed_paths:
  - docs/agents/tasks/active/CAN-20260717-otbm-repair-materialization-pipeline.md
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.md
  - docs/ai-agent/OTBM_REPAIR_MATERIALIZATION_PIPELINE.schema.json
  - tools/ai-agent/otbm_repair_materialization_pipeline.py
  - tools/ai-agent/otbm_repair_materialization_pipeline_tool.py
  - tools/ai-agent/test_otbm_repair_materialization_pipeline.py
validation:
  - command: GitHub Actions CI run 29560198886 on head dfec4b0233ff5085e5e2be2f3fd866ac0713a98a
    result: PASS
    evidence: repository CI completed successfully on the implementation head before checkpoint-only repairs
  - command: GitHub Actions OTBM Map Tools run 29560198811 on head dfec4b0233ff5085e5e2be2f3fd866ac0713a98a
    result: PASS
    evidence: OTBM Map Tools completed successfully on the implementation head before checkpoint-only repairs
  - command: GitHub Actions AI Agent Tools run 29560198788 on head dfec4b0233ff5085e5e2be2f3fd866ac0713a98a
    result: PASS
    evidence: AI Agent Tools completed successfully on the implementation head before checkpoint-only repairs
  - command: GitHub Actions Agent Task Ownership run 29560429143 on head a5c5fd49d339bd18918ca902b46a5d0f7465bccc
    result: FAIL
    evidence: active-task-ownership artifact reports only that the record under tasks/active used literal status active instead of the required lifecycle status
blockers: []
next_action: Verify current-head ownership and implementation workflows, then recheck PR 451 shared-path ownership before narrow catalogue/changelog integration.
```
