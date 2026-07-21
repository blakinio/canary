---
task_id: CAN-20260721-otbm-qa-003-repair-recommendations
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-003-repair-recommendations-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "901bd3db5aa8d6b7a7ef3799a033906aea900f3c"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-qa-002-map-change-regression complete
blocks:
  - OTBM-QA-004 reviewed candidate repair orchestration
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_repair_recommendation.py
    - tools/ai-agent/otbm_repair_recommendation_tool.py
    - tools/ai-agent/test_otbm_repair_recommendation.py
    - tools/ai-agent/test_otbm_repair_recommendation_output_safety.py
    - tools/ai-agent/test_otbm_repair_recommendation_schema.py
    - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.md
    - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION_REQUEST.schema.json
    - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.schema.json
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-003-repair-recommendations.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/architecture/otbm-world-quality-repair.md
    - docs/ai-agent/OTBM_REPAIR_PREFLIGHT.md
    - docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json
    - docs/ai-agent/OTBM_AREA_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_INSERTION_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_DELETION_MATERIALIZER.md
    - docs/ai-agent/OTBM_TILE_TYPE_CONVERSION_MATERIALIZER.md
modules_touched:
  - otbm-repair-recommendation
reuses:
  - OTBM real-map repair preflight
  - Phase 8 bounded attribute patch plan
  - bounded TILE_AREA materialization capability
  - bounded raw-tile replacement/insertion/deletion/type-conversion capability inventory
public_interfaces:
  - canary-otbm-repair-recommendation-request-v1
  - canary-otbm-repair-recommendation-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-003 Repair Recommendation Orchestrator

## Status

ACTIVE — bounded implementation selected by a fresh post-QA-002-lifecycle preflight.

## Goal

Generate deterministic review-only repair recommendations from one exact finding request plus compatible existing repair-preflight/capability evidence, without mutating a map, generating approval, executing a writer, or broadening any existing mutation boundary.

## Bounded slice

- Introduce `canary-otbm-repair-recommendation-request-v1` as an exact caller-supplied finding/selector/mutation-shape envelope; the orchestrator must not invent any target identity or desired state.
- Introduce `canary-otbm-repair-recommendation-v1` with the roadmap states `no-repair-evidence`, `review-required`, `supported-by-existing-attribute-path`, `supported-by-existing-tile-area-path`, `supported-by-existing-raw-tile-path`, `unsupported-mutation-shape`, `blocked-by-runtime-evidence`, and `ambiguous-target`.
- Require one compatible `canary-otbm-repair-preflight-v1` report for exact selector/source correlation and runtime evidence.
- Treat existing Phase 8 review-ready draft plans as evidence that an exact supported attribute path exists; never execute the plan.
- Recognize TILE_AREA support only from an explicit exact `replace-region`, zero-translation, complete 256-aligned change-shape request; final materializer-specific plan/approval/provenance gates remain mandatory downstream.
- Recognize raw-tile support only for the already-delivered replacement/insertion/deletion/type-conversion shape families at an explicit exact position; final span/index/approval/provenance gates remain mandatory downstream.
- Preserve exact source-map/finding/preflight evidence pins, selector, expected old state, proposed target state, blockers and required downstream reviews.
- Fail closed on ambiguous target correlation, unresolved/conflicting runtime evidence, incompatible source/selector evidence, unsupported shapes, or missing required exact request fields.
- Keep generated reports outside Git and use create-new/no-clobber output semantics.

## Explicit non-goals

- No OTBM parsing/scanning, World Index construction, Script Resolution, pathfinding, rendering, map mutation, materialization, candidate publication, Physical E2E execution or workflow creation.
- No automatic approval document generation.
- No invention of AID, UID, item ID, house-door ID, teleport destination, tile, stack order, coordinate, expected old state or proposed target state.
- No claim that a technically supported mutation path proves a finding is a real defect or that the proposed repair is gameplay-correct.
- No widening of Phase 8, TILE_AREA or raw-tile materializer capabilities.

## Acceptance criteria

- Identical compatible inputs produce byte-stable semantic output ordering.
- Every recommendation pins the exact request and repair-preflight inputs by SHA-256.
- Request source-map identity and selector must exactly match repair-preflight evidence.
- Ambiguous or missing target correlation never yields a supported mutation state.
- Unresolved, partially-resolved, referenced-only or conflicting runtime evidence remains blocking when the requested recommendation depends on runtime handling.
- `supported-by-existing-attribute-path` requires an existing review-ready Phase 8 draft plan for the exact target.
- TILE_AREA/raw-tile supported states are capability classifications only; output explicitly retains all downstream materializer-specific evidence and human-approval requirements.
- Unsupported shapes remain `unsupported-mutation-shape` rather than being adapted heuristically.
- Output safety rejects symlinks, duplicate inputs and input/output collisions and does not clobber existing reports without explicit overwrite.
- Focused aggregation/schema/output-safety tests plus relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T16:20:00+02:00
head: 901bd3db5aa8d6b7a7ef3799a033906aea900f3c
branch: feat/otbm-qa-003-repair-recommendations-20260721
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_repair_recommendation.py
  - tools/ai-agent/otbm_repair_recommendation_tool.py
  - tools/ai-agent/test_otbm_repair_recommendation.py
  - tools/ai-agent/test_otbm_repair_recommendation_output_safety.py
  - tools/ai-agent/test_otbm_repair_recommendation_schema.py
  - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.md
  - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION_REQUEST.schema.json
  - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.schema.json
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-003-repair-recommendations.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - OTBM-QA-002 feature PR #679 merged as 4a28063b65890401472295575858aa939d0ff07c and lifecycle PR #680 merged as 901bd3db5aa8d6b7a7ef3799a033906aea900f3c.
  - Current main at task start is 901bd3db5aa8d6b7a7ef3799a033906aea900f3c.
  - Fresh post-lifecycle preflight found no open OTBM-QA PR and no otbm-qa branch.
  - Live roadmap identifies OTBM-QA-003 Repair Recommendation Orchestrator after OTBM-QA-002.
  - Architecture Layer 5 requires a non-mutating recommendation carrying exact target position, expected old state, evidence hashes and blockers, with explicit review before mutation.
  - Repair Preflight v1 is the canonical exact mechanic-selector/anchor/runtime evidence source and exposes explicit matched/correlated/runtime/patch/review readiness.
  - Existing approved mutation families are Phase 8 existing-attribute replacement, complete same-coordinate zero-translation TILE_AREA materialization, and bounded raw-tile replacement/insertion/deletion/type-conversion.
derived:
  - The smallest bounded v1 should classify exact caller-declared mutation shapes against the existing capability inventory while using Repair Preflight as the exact selector/runtime gate; it must not duplicate any writer or materializer implementation.
unknown:
  - Exact final request/report field shape and test fixtures until implementation is completed.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation validation has run yet.
rejected_hypotheses:
  - Executing a writer from the recommendation layer.
  - Generating approval documents automatically.
  - Inferring repair targets or desired values from names, proximity, visual similarity or intent.
  - Treating materializer capability as proof the proposed repair is correct.
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-003-repair-recommendations.md
validation: []
blockers: []
next_action: Open a draft PR, bind this task to it, then implement the smallest deterministic recommendation contract over exact request plus Repair Preflight evidence with conservative existing mutation-family classification and focused tests.
```
