---
task_id: CAN-20260721-otbm-qa-001-world-health
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-001-world-health-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "e55e0d548d6013da6676cc7b06cbb8d459ccdd1f"
risk: medium
related_issue: ""
related_pr: "672"
depends_on:
  - CAN-20260721-otbm-roadmap-all-proposals complete
blocks:
  - OTBM-QA-008 dependency graph composition
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_world_health.py
    - tools/ai-agent/otbm_world_health_tool.py
    - tools/ai-agent/test_otbm_world_health.py
    - tools/ai-agent/test_otbm_world_health_output_safety.py
    - tools/ai-agent/test_otbm_world_health_schema.py
    - docs/ai-agent/OTBM_WORLD_HEALTH.md
    - docs/ai-agent/OTBM_WORLD_HEALTH.schema.json
    - docs/agents/tasks/active/CAN-20260721-otbm-qa-001-world-health.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
    - docs/architecture/otbm-world-quality-repair.md
    - docs/ai-agent/OTBM_MAP_QUALITY_GATE.md
    - docs/ai-agent/OTBM_E2E_COVERAGE.md
modules_touched:
  - otbm-world-health
reuses:
  - OTBM Map Quality Gate
  - OTBM Reachability
  - OTBM-E2E coverage matrix
  - exact map and World Index provenance from existing reports
public_interfaces:
  - canary-otbm-world-health-v1
cross_repo_tasks: []
---

# CAN-20260721 — OTBM-QA-001 World Health Aggregator

## Status

ACTIVE — bounded implementation of the first successor roadmap package in draft PR #672.

## Goal

Add one deterministic, read-only world-health aggregation contract over compatible existing OTBM evidence without parsing/scanning OTBM, rebuilding the World Index, resolving scripts, pathfinding, executing Lua, modifying maps or taking Universal E2E ownership.

## Bounded slice

- Introduce `canary-otbm-world-health-v1`.
- Compose current Map Quality, Reachability and OTBM-E2E coverage evidence under exact compatible map provenance.
- Preserve separate dimensions for structural findings, runtime-handler resolution, reachability states, stale evidence and missing Physical E2E coverage.
- Preserve exact totals from source summaries and deterministic bounded samples without deduplicating distinct findings into inferred defects.
- Pin every contributing report by SHA-256 and preserve bounded/global coverage semantics.
- Fail closed on malformed, unsupported or incompatible contributing-report provenance while preserving explicitly stale target evidence as its own health dimension.
- Keep generated reports outside Git and use create-new/no-clobber output semantics.

## Explicit non-goals

- No second parser, scanner, World Index, Script Resolution engine, Reachability implementation, renderer, writer/materializer, E2E runner or workflow.
- No dynamic Lua execution.
- No map mutation or generated `.otbm`/`.widx`/report commits.
- No inference that selected-scope absence means global absence.
- No promotion of `unresolved`, `partially-resolved`, `referenced-only` or `conflicting` evidence.
- No feature-specific E2E scenario generation, fixtures, runtime assertions or acceptance decisions.
- No opaque health score used as a gate.

## Acceptance criteria

- Identical compatible inputs produce byte-stable semantic output ordering.
- Every accepted contributing report is format-validated, SHA-pinned and tied to the same exact source-map provenance.
- Structural and runtime-handler dimensions reuse Map Quality outcomes rather than reinterpret component semantics.
- Reachability totals preserve explicit route/mechanic states and bounded scope.
- Stale and missing-physical-coverage totals preserve OTBM-E2E coverage semantics and remain coverage evidence rather than breakage claims.
- Samples are deterministic and bounded while totals remain exact.
- Output safety rejects symlinks/input collisions and does not clobber an existing report unless explicitly requested.
- Focused aggregation, schema-contract and output-safety tests plus relevant AI Agent/OTBM gates pass.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T13:47:00+02:00
head: 6455f34cae694c62073640bfb9641c367999a072
branch: feat/otbm-qa-001-world-health-20260721
pr: 672
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_world_health.py
  - tools/ai-agent/otbm_world_health_tool.py
  - tools/ai-agent/test_otbm_world_health.py
  - tools/ai-agent/test_otbm_world_health_output_safety.py
  - tools/ai-agent/test_otbm_world_health_schema.py
  - docs/ai-agent/OTBM_WORLD_HEALTH.md
  - docs/ai-agent/OTBM_WORLD_HEALTH.schema.json
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-001-world-health.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - Consolidated roadmap OTBM-QA-001..018 merged through PR #669 and lifecycle archived through PR #671.
  - OTBM-QA-001 is the first unrealized package in the roadmap dependency sequence.
  - PR #672 is the bounded draft implementation PR for this task.
  - Existing Map Quality, Reachability and OTBM-E2E coverage schemas expose the exact provenance and explicit health dimensions reused by this package.
  - World Health core, CLI, focused aggregation tests, output-safety tests, schema-contract tests, v1 schema and contract documentation are present on the feature branch.
  - Corrected checkpoint head e825ffa91979af569b6ac514c65a9b238be2a541 passed CI run 29825728291, Agent Task Ownership run 29825728147, OTBM Map Tools run 29825728055 and AI Agent Tools run 29825728027.
  - The final MODULE_CATALOG PR diff adds exactly one OTBM World Health Aggregator row and preserves all existing catalogue text.
  - Main advanced to e55e0d548d6013da6676cc7b06cbb8d459ccdd1f through independent Oteryn governance documentation; no path in that commit overlaps this task ownership.
derived:
  - The smallest complete v1 composes one required Map Quality report with zero or more current-map Reachability reports and zero or more current-map coverage matrices while leaving future compatible adapters additive.
unknown:
  - Exact-head focused-gate outcome after adding the schema-contract test and updating its ownership declaration.
conflicts: []
first_failure:
  marker: agent-task-ownership-related-pr
  evidence: Agent Task Ownership run 29825597769 failed because changed active task related_pr was empty instead of current PR 672; the metadata was corrected and later ownership run 29825728147 passed.
rejected_hypotheses:
  - Rescanning OTBM to compute health.
  - Building another pathfinder or script resolver.
  - Collapsing all evidence into one opaque health score.
  - Treating a missing Physical E2E scenario as proof a mechanic is broken.
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260721-otbm-qa-001-world-health.md
  - docs/ai-agent/OTBM_WORLD_HEALTH.md
  - docs/ai-agent/OTBM_WORLD_HEALTH.schema.json
  - tools/ai-agent/otbm_world_health.py
  - tools/ai-agent/otbm_world_health_tool.py
  - tools/ai-agent/test_otbm_world_health.py
  - tools/ai-agent/test_otbm_world_health_output_safety.py
  - tools/ai-agent/test_otbm_world_health_schema.py
validation:
  - command: Agent Task Ownership run 29825597769
    result: FAIL
    evidence: Initial related_pr metadata mismatch only; corrected from empty to 672.
  - command: CI run 29825728291
    result: PASS
    evidence: Repository CI passed on corrected checkpoint head e825ffa91979af569b6ac514c65a9b238be2a541.
  - command: Agent Task Ownership run 29825728147
    result: PASS
    evidence: Active-task ownership and PR binding passed on corrected checkpoint head.
  - command: OTBM Map Tools run 29825728055
    result: PASS
    evidence: Focused OTBM tooling validation passed on corrected checkpoint head.
  - command: AI Agent Tools run 29825728027
    result: PASS
    evidence: Full tools/ai-agent unittest discovery and AI-agent validation passed on corrected checkpoint head.
blockers: []
next_action: Require current-head Ownership, AI Agent Tools, OTBM Map Tools and CI success including the new schema-contract test; fix any bounded failure, then apply ci:final-gate before the final checkpoint commit and perform exact-final-head validation with no post-green commits.
```
