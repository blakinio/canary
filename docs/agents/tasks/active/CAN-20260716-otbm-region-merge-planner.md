---
task_id: CAN-20260716-otbm-region-merge-planner
program_id: "OTS-OTBM-VALIDATION"
coordination_id: "OTS-OTBM-VALIDATION"
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-region-merge-planner
base_branch: main
created: 2026-07-16T11:20:00+02:00
updated: 2026-07-16T12:50:00+02:00
last_verified_commit: "5614f2bcfd6146b6c0b0efed5b14b01919bb01a9"
risk: high
related_issue: ""
related_pr: "424"
depends_on:
  - "OTBM World Index #219"
  - "Semantic OTBM Diff #311"
  - "OTBM script resolution #104"
  - "OTBM repair sandbox verifier #422"
blocks:
  - "future structural OTBM region import writer"
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_region_merge_planner.py
    - tools/ai-agent/otbm_region_merge_planner_tool.py
    - tools/ai-agent/test_otbm_region_merge_planner.py
    - docs/ai-agent/OTBM_REGION_MERGE_PLANNER.md
    - docs/ai-agent/OTBM_REGION_MERGE_PLAN.schema.json
    - docs/agents/tasks/active/CAN-20260716-otbm-region-merge-planner.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_semantic_diff.py
    - tools/ai-agent/otbm_script_resolution.py
modules_touched:
  - OTBM donor/region merge planner
reuses:
  - canonical OTBM World Index
  - Semantic Diff provenance validation
  - script-resolution report format
public_interfaces:
  - canary-otbm-region-merge-plan-v1
  - OTBM region merge planner CLI
cross_repo_tasks: []
---

# Goal

Add a deterministic read-only review planner for an explicit donor World Index region translated to an explicit target region. No OTBM writing, heuristic alignment or Phase 8 expansion.

# Acceptance criteria

- [x] Consume canonical current/donor `.widx` plus manifests without parsing OTBM.
- [x] Require explicit donor bounds and target origin; fail closed on coordinate overflow.
- [x] Support review-only `overlay` and `replace-region` policies.
- [x] Emit deterministic unchanged/add/replace/delete-candidate/preserve-current-only actions with exact snapshots.
- [x] Detect global retained-map UID/AID and house-door conflicts.
- [x] Compare optional current/donor script-resolution evidence without promoting unresolved to handled.
- [x] Translate only internal donor-region teleport destinations; preserve external destinations for explicit review.
- [x] Emit `canary-otbm-region-merge-plan-v1` with `writerReady: false`, exact totals and bounded samples.
- [x] Pin indexes, manifests and optional resolver inputs.
- [x] Add focused tests, schema/docs and narrow catalogue/changelog updates.
- [ ] Verify final exact-head required checks before readiness/merge.

# Confirmed context

- Writes are authorized only in `blakinio/canary`.
- Task-start main: `52eb5932d94feeec8a1ba81ece7de7958ed06eea` (#422 merge).
- Current observed main during shared-doc updates: `c36e8548f195843254f16963adc7cb1d497084aa`.
- PR #316 owns only Targuna-specific audit paths and does not overlap this planner.
- Future structural region writing remains a separate ADR/bounded task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T12:50:00+02:00
head: 5614f2bcfd6146b6c0b0efed5b14b01919bb01a9
branch: feat/otbm-region-merge-planner
pr: 424
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_region_merge_planner.py
  - tools/ai-agent/otbm_region_merge_planner_tool.py
  - tools/ai-agent/test_otbm_region_merge_planner.py
  - docs/ai-agent/OTBM_REGION_MERGE_PLANNER.md
  - docs/ai-agent/OTBM_REGION_MERGE_PLAN.schema.json
  - docs/agents/tasks/active/CAN-20260716-otbm-region-merge-planner.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
proven:
  - planner reuses WorldIndex and Semantic Diff provenance validation instead of adding an OTBM parser or duplicate index validator
  - overlay and replace-region are review-only and writerReady remains false
  - global retained-map UID AID and house-door conflicts are checked beyond the target region
  - internal donor teleports are translated only inside selected donor bounds and external destinations are never guessed
  - same-handler AID reuse requires explicit compatible resolver evidence while UID collisions remain blocking
  - output without overwrite uses exclusive create-new publication
  - functional CI OTBM Map Tools and AI Agent Tools passed on c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - MODULE_CATALOG patch is one added planner row with no unrelated drift
  - CHANGELOG patch is one added Unreleased planner bullet with no unrelated drift
derived:
  - a structural writer requires a separate contract ADR and bounded task
unknown:
  - final exact-head gate after checkpoint-format repair
conflicts: []
first_failure:
  marker: initial-ownership-metadata
  evidence: initial task checkpoint lacked PR binding; later ownership run 29491809836 exposed invalid string validation entries and this update converts them to required mappings
rejected_hypotheses:
  - heuristic donor-to-target alignment
  - direct OTBM region writing
  - silent overwrite of current-only content
  - actionId compatibility without explicit resolver evidence
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260716-otbm-region-merge-planner.md
  - docs/ai-agent/OTBM_REGION_MERGE_PLAN.schema.json
  - docs/ai-agent/OTBM_REGION_MERGE_PLANNER.md
  - tools/ai-agent/otbm_region_merge_planner.py
  - tools/ai-agent/otbm_region_merge_planner_tool.py
  - tools/ai-agent/test_otbm_region_merge_planner.py
validation:
  - command: CI run 29490967322
    result: PASS
    evidence: functional head c3ed48f3b80700309178a7348dfd675ce7f88b2e passed
  - command: OTBM Map Tools run 29490967134
    result: PASS
    evidence: focused planner and map-tool validation passed on c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - command: AI Agent Tools run 29490967167
    result: PASS
    evidence: unit and schema/content validation passed on c3ed48f3b80700309178a7348dfd675ce7f88b2e
  - command: Agent Task Ownership run 29491809836
    result: FAIL
    evidence: validation entries were strings instead of command result evidence mappings; fixed by this update
blockers: []
next_action: Run all required checks on the new exact head then set task ready and mark PR 424 ready only if the diff remains clean.
```

# Completion

- Final status: implementing
- Canary PR: #424
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: not archived
