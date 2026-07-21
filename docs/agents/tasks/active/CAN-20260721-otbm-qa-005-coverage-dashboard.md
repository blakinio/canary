---
task_id: CAN-20260721-otbm-qa-005-coverage-dashboard
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-005-coverage-dashboard-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "951d04cb9bf4a51f6eddb8c2238b8e1157a9f252"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-qa-004-reviewed-candidate-repair complete
blocks:
  - OTBM-QA-006 region and quest certification
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_coverage_dashboard.py
    - tools/ai-agent/otbm_coverage_dashboard_tool.py
    - tools/ai-agent/test_otbm_coverage_dashboard.py
    - tools/ai-agent/test_otbm_coverage_dashboard_output_safety.py
    - tools/ai-agent/test_otbm_coverage_dashboard_schema.py
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.md
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD_TARGETS.schema.json
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.schema.json
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-005-coverage-dashboard.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/ai-agent/OTBM_E2E_COVERAGE.md
    - docs/ai-agent/OTBM_E2E_COVERAGE_MATRIX.schema.json
    - docs/ai-agent/OTBM_MAP_QUALITY_GATE.md
    - docs/ai-agent/OTBM_MAP_QUALITY_GATE.schema.json
    - docs/ai-agent/OTBM_WORLD_HEALTH.md
    - docs/ai-agent/OTBM_WORLD_HEALTH.schema.json
    - docs/ai-agent/QUEST_MAP_VALIDATION.md
    - docs/ai-agent/QUEST_MAP_VALIDATION.schema.json
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR.md
    - docs/ai-agent/OTBM_REVIEWED_CANDIDATE_REPAIR.schema.json
modules_touched:
  - otbm-coverage-dashboard
reuses:
  - OTBM-E2E coverage matrix
  - OTBM Map Quality Gate
  - OTBM World Health Aggregator
  - Quest Map Validation
  - canonical executable OTBM route plans
  - OTBM-QA-004 reviewed candidate repair evidence
public_interfaces:
  - canary-otbm-coverage-dashboard-targets-v1
  - canary-otbm-coverage-dashboard-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-005 Coverage Dashboard and Evidence Model

## Status

ACTIVE — bounded implementation started from post-QA-004 lifecycle `main`.

## Goal

Expose deterministic factual coverage state for explicitly reviewed world, region, landmark-route, quest and mechanic-set targets by composing compatible existing OTBM evidence without rescanning, rerunning validators, executing gameplay, or assigning formal QA-006 certification levels.

## Bounded slice

- Add `canary-otbm-coverage-dashboard-targets-v1` for reviewed dashboard targets.
- Add `canary-otbm-coverage-dashboard-v1` with independent evidence dimensions rather than one opaque score.
- Require one current-map OTBM-E2E coverage matrix, one compatible Map Quality report and one compatible World Health report.
- Allow optional exact-SHA-bound Quest Map Validation reports, canonical executable route plans and QA-004 reviewed candidate repair reports.
- Support target kinds `world`, `region`, `landmark-route`, `quest` and `mechanic-set`.
- Resolve target mechanic populations only from the existing reviewed Coverage Matrix: all reviewed mechanics for `world`, exact position-bounded members for `region`, and explicit reviewed mechanic IDs for other target kinds.
- Preserve independent states for indexed-on-exact-map, source-correlated, script-resolved, statically-reachable, interaction-resolved, static-quality-compatible, executable-route-covered, physically-runtime-proven, candidate-map-validated and stale-against-current-map.
- Require explicit report SHA/evidence IDs for source correlation and explicit report SHA for route/candidate evidence; missing bindings remain `not-evaluated` rather than guessed.
- Allow reviewed `requiredDimensions` only to derive a transparent `requirementsSatisfied` convenience boolean; do not assign C0-C7 or other formal certification levels.
- Emit deterministic coverage gaps with exact target/dimension/member evidence; gaps are evidence for downstream owners, not scenario prioritization instructions.
- Keep generated reports outside Git and use create-new/no-clobber output semantics.

## Explicit non-goals

- No OTBM parsing/scanning, World Index construction, Script Resolution, pathfinding, rendering or map mutation.
- No Quest Map Validation, Map Quality, World Health or Coverage Matrix recomputation.
- No route generation, route preflight, interaction resolution execution or Physical E2E execution.
- No candidate mutation or candidate validation execution.
- No second E2E runner or workflow.
- No inference of quest membership, target criticality, source correlation, route membership or interaction requirements from names, proximity, sprites or chat history.
- No formal QA-006 C0-C7 certification assignment.
- No opaque score as a gate.

## Acceptance criteria

- Identical compatible inputs produce byte-stable semantic output ordering.
- Required Coverage Matrix, Map Quality and World Health inputs pin the same current source map; Coverage Matrix and World Health also pin the same current World Index.
- `world` uses only all reviewed Coverage Matrix mechanics and explicitly states that this is reviewed-target population, not proof of all map mechanics.
- `region` membership is derived only by exact selector position containment inside the explicit inclusive region.
- `landmark-route`, `quest` and `mechanic-set` use explicit reviewed Coverage Matrix mechanic IDs; unknown IDs fail closed.
- Indexed/script/reachability/physical/stale states preserve exact current Coverage Matrix evidence and never promote stale evidence.
- Source correlation is proven only from explicitly SHA-bound Quest Map Validation evidence IDs whose classification is `confirmed`; incompatible World Index evidence is stale, unresolved/conflicting/other classifications remain blocking.
- Executable-route coverage requires an explicitly SHA-bound canonical route plan with exact current map/World Index provenance and `executionStatus=executable`.
- Interaction resolution is proven only when the reviewed target declares interaction required and the exact current executable route evidence contains at least one interaction resolution and every retained interaction is executable; otherwise it is blocked or not-applicable/not-evaluated.
- Static quality compatibility is proven only when Map Quality is green and its exact bounded Geometry/Reachability region equals the target's exact region; full-world global quality is not inferred because Map Quality v1 explicitly lacks global coverage proof.
- Candidate-map validation uses explicitly SHA-bound QA-004 reports only and never becomes global proof; source map must equal current map and linked repair selectors must belong to the target's selected reviewed mechanic population.
- Missing optional evidence remains `not-evaluated`; it never becomes proven absence or global non-coverage.
- `requirementsSatisfied` is derived only from target-declared `requiredDimensions` and explicit dimension states; formal certification levels remain out of scope.
- Output safety rejects symlinks, duplicate inputs and input/output collisions and does not clobber existing reports without explicit overwrite.
- Focused aggregation/schema/output-safety tests plus relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T18:35:00+02:00
head: 951d04cb9bf4a51f6eddb8c2238b8e1157a9f252
branch: feat/otbm-qa-005-coverage-dashboard-20260721
pr: null
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_coverage_dashboard.py
  - tools/ai-agent/otbm_coverage_dashboard_tool.py
  - tools/ai-agent/test_otbm_coverage_dashboard.py
  - tools/ai-agent/test_otbm_coverage_dashboard_output_safety.py
  - tools/ai-agent/test_otbm_coverage_dashboard_schema.py
  - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.md
  - docs/ai-agent/OTBM_COVERAGE_DASHBOARD_TARGETS.schema.json
  - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.schema.json
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-005-coverage-dashboard.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - OTBM-QA-004 feature PR #684 merged as e11ad06beebb3cd7c11a4d686f749ac54155cce5.
  - OTBM-QA-004 lifecycle PR #686 merged as 951d04cb9bf4a51f6eddb8c2238b8e1157a9f252.
  - Current main is identical to 951d04cb9bf4a51f6eddb8c2238b8e1157a9f252 at fresh post-lifecycle preflight.
  - Fresh preflight found no open OTBM-QA PR, no otbm-qa branch and no existing QA-005 task.
  - Live roadmap identifies OTBM-QA-005 Coverage Dashboard and Certification Model after QA-004 and reserves formal C0-C7 certification levels for QA-006.
  - Existing Coverage Matrix already provides exact current-map reviewed-mechanic indexed, script, reachability, physical and stale dimensions.
  - Map Quality v1 is bounded and explicitly sets globalCoverageProven=false; therefore it cannot authorize a full-world static-quality claim.
  - Quest Map Validation exposes exact evidence IDs/classifications and World Index SHA for conservative source-to-map correlation.
  - Canonical route plans expose exact map/World Index provenance, executionStatus and edge-level interaction resolutions.
  - QA-004 exposes exact reviewed candidate repair evidence without providing global gameplay correctness.
derived:
  - The smallest complete QA-005 v1 is a reviewed-target evidence dashboard with explicit optional evidence bindings and transparent required-dimension policy, not a new validator or formal certification engine.
unknown:
  - Exact target/report schema field details until implementation and focused tests land.
conflicts: []
first_failure:
  marker: none
  evidence: No QA-005 implementation has been attempted yet.
rejected_hypotheses:
  - Treating script resolution as source correlation.
  - Treating route presence as interaction resolution.
  - Treating bounded Map Quality as global world quality proof.
  - Treating missing optional evidence as a global absence finding.
  - Assigning QA-006 C0-C7 levels inside QA-005.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-005-coverage-dashboard.md
validation: []
blockers: []
next_action: Open a draft PR for this bounded ownership scope, bind related_pr, then implement the target/report contracts, deterministic aggregator, CLI and focused tests before pre-final checkpointing.
```
