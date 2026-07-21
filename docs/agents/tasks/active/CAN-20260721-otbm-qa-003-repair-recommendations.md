---
task_id: CAN-20260721-otbm-qa-003-repair-recommendations
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-003-repair-recommendations-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "77d7642fc4e29460efd5815553767282423c90d0"
risk: medium
related_issue: ""
related_pr: "681"
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

READY — bounded implementation is complete in PR #681; `ci:final-gate` is applied and no further feature/checkpoint commits are permitted after this final checkpoint commit.

## Goal

Generate deterministic review-only repair recommendations from one exact finding request plus compatible existing repair-preflight/capability evidence, without mutating a map, generating approval, executing a writer, or broadening any existing mutation boundary.

## Bounded slice

- Introduce `canary-otbm-repair-recommendation-request-v1` as an exact caller-supplied finding/selector/mutation-shape envelope; the orchestrator never invents target identity or desired state.
- Introduce `canary-otbm-repair-recommendation-v1` with the roadmap states `no-repair-evidence`, `review-required`, `supported-by-existing-attribute-path`, `supported-by-existing-tile-area-path`, `supported-by-existing-raw-tile-path`, `unsupported-mutation-shape`, `blocked-by-runtime-evidence`, and `ambiguous-target`.
- Require one compatible `canary-otbm-repair-preflight-v1` report for exact selector/source correlation and runtime evidence.
- Treat existing Phase 8 review-ready draft plans as evidence that an exact supported attribute path exists; never execute the plan.
- Recognize TILE_AREA support only from an explicit exact `replace-region`, zero-translation, complete 256-aligned change-shape request; final materializer-specific plan/approval/provenance gates remain mandatory downstream.
- Recognize raw-tile support only for the delivered replacement/insertion/deletion/type-conversion shape families at an explicit exact position; final span/index/approval/provenance gates remain mandatory downstream.
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
- Request source-map identity and selector exactly match repair-preflight evidence.
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
updated_at: 2026-07-21T16:39:53+02:00
head: 77d7642fc4e29460efd5815553767282423c90d0
branch: feat/otbm-qa-003-repair-recommendations-20260721
pr: 681
status: ready
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
  - Current main remains 901bd3db5aa8d6b7a7ef3799a033906aea900f3c and is identical to the feature base at the pre-final audit.
  - Fresh post-lifecycle preflight found no open OTBM-QA PR and no otbm-qa branch before QA-003 ownership was established.
  - Live roadmap identifies OTBM-QA-003 Repair Recommendation Orchestrator after OTBM-QA-002.
  - Architecture Layer 5 requires a non-mutating recommendation carrying exact target position, expected old state, evidence hashes and blockers, with explicit review before mutation.
  - Repair Preflight v1 is reused as the canonical exact mechanic-selector/anchor/runtime evidence source; QA-003 does not rerun Item Audit, native patch-anchor scanning or Script Resolution.
  - Existing mutation capability families remain Phase 8 existing-attribute replacement, complete same-coordinate zero-translation TILE_AREA materialization, and bounded raw-tile replacement/insertion/deletion/type-conversion.
  - The v1 core, CLI, focused state tests, output-safety tests, request/report schemas, schema-contract tests and contract documentation are present on PR #681.
  - Supported TILE_AREA/raw-tile states are capability-only classifications and preserve downstream plan/span/index/provenance/human-approval requirements rather than claiming writer readiness.
  - Every report keeps human review required, approvalGenerated false, mapModified false, gameplayCorrectnessProven false, playerIntentProven false and supportedPathMeansRepairCorrect false.
  - PR #681 changes exactly ten intended task/module/documentation/schema/test paths.
  - MODULE_CATALOG diff adds exactly one OTBM Repair Recommendation Orchestrator row and preserves all existing catalogue text.
  - Pre-final head 77d7642fc4e29460efd5815553767282423c90d0 passed CI run 29839974079, Agent Task Ownership run 29839973633, OTBM Map Tools run 29839974190 and AI Agent Tools run 29839973659.
  - ci:final-gate was applied before this final checkpoint commit.
derived:
  - The smallest complete v1 is a review-only capability classifier over exact request plus Repair Preflight evidence; no writer/materializer execution or new mutation semantics are required.
unknown:
  - Exact-final-head CI and focused-gate outcomes for this final checkpoint commit until GitHub Actions completes.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation, schema, ownership or CI failure was observed before the final checkpoint commit.
rejected_hypotheses:
  - Executing a writer from the recommendation layer.
  - Generating approval documents automatically.
  - Inferring repair targets or desired values from names, proximity, visual similarity or intent.
  - Treating materializer capability as proof the proposed repair is correct.
  - Consuming TILE_AREA/raw-tile capability classification as a substitute for downstream exact span/index/plan/provenance/approval gates.
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-003-repair-recommendations.md
  - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.md
  - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION.schema.json
  - docs/ai-agent/OTBM_REPAIR_RECOMMENDATION_REQUEST.schema.json
  - tools/ai-agent/otbm_repair_recommendation.py
  - tools/ai-agent/otbm_repair_recommendation_tool.py
  - tools/ai-agent/test_otbm_repair_recommendation.py
  - tools/ai-agent/test_otbm_repair_recommendation_output_safety.py
  - tools/ai-agent/test_otbm_repair_recommendation_schema.py
validation:
  - command: CI run 29839974079
    result: PASS
    evidence: Repository CI passed on pre-final head 77d7642fc4e29460efd5815553767282423c90d0.
  - command: Agent Task Ownership run 29839973633
    result: PASS
    evidence: Active-task ownership, owned path declarations and PR binding passed on pre-final head.
  - command: OTBM Map Tools run 29839974190
    result: PASS
    evidence: OTBM schema JSON validation and focused OTBM tests passed on pre-final head.
  - command: AI Agent Tools run 29839973659
    result: PASS
    evidence: Full tools/ai-agent unit-test discovery and AI-agent validation passed on pre-final head including QA-003 contract tests.
blockers: []
next_action: Mark PR #681 ready for review without changing files. Require exact-final-head CI, Agent Task Ownership, OTBM Map Tools and AI Agent Tools success on this checkpoint commit, confirm mergeability and zero review threads, then squash-merge #681 and perform lifecycle archive in a separate bounded PR before starting the next roadmap package.
```
