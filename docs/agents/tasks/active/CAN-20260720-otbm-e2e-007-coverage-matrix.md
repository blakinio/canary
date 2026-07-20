---
task_id: CAN-20260720-otbm-e2e-007-coverage-matrix
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-007
status: implementing
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-007-coverage-matrix
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "c34cca6da19b05d8cc05d45d2cf25fb8d71ef81b"
risk: medium
related_issue: ""
related_pr: "639"
depends_on:
  - merged and archived OTBM-E2E-006
  - existing OTBM Item Audit and Unified World Index evidence
  - existing OTBM Script Resolution and Reachability reports
  - existing Universal Physical E2E retained artifact contract
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-otbm-e2e-007-coverage-matrix.md
    - tools/ai-agent/otbm_e2e_coverage.py
    - tools/ai-agent/test_otbm_e2e_coverage.py
    - docs/ai-agent/OTBM_E2E_COVERAGE.md
    - docs/ai-agent/OTBM_E2E_COVERAGE_TARGETS.schema.json
    - docs/ai-agent/OTBM_E2E_COVERAGE_MATRIX.schema.json
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_WORLD_INDEX.md
    - docs/ai-agent/OTBM_ITEM_AUDIT_REPORT.schema.json
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION_REPORT.schema.json
    - docs/ai-agent/OTBM_REACHABILITY.md
    - docs/ai-agent/OTBM_REACHABILITY.schema.json
    - docs/ai-agent/OTBM_E2E_ROUTE_PLAN.schema.json
    - tests/e2e/scenarios/**
modules_touched:
  - OTBM mechanic to Physical E2E coverage matrix
reuses:
  - canary-otbm-item-audit-v1
  - canary-otbm-world-index-v1 provenance
  - canary-otbm-script-resolution-v1
  - canary-otbm-reachability-v1
  - canary-otbm-e2e-route-plan-v1
  - Universal Physical E2E retained artifacts
public_interfaces:
  - canary-otbm-e2e-coverage-targets-v1
  - canary-otbm-e2e-coverage-matrix-v1
cross_repo_tasks: []
---

# Goal

Deliver OTBM-E2E-007 as one deterministic read-only evidence aggregator that correlates reviewed critical OTBM mechanic placements with existing static indexing, Script Resolution, Reachability and Universal Physical E2E route artifacts without adding a parser, pathfinder, runner or workflow.

# Acceptance criteria

- [ ] Accept only reviewed exact mechanic targets with an exact `x,y,z` position and at least one mechanic identity selector.
- [ ] Prove static indexing from existing `canary-otbm-item-audit-v1` evidence pinned to the current World Index source-map SHA-256.
- [ ] Preserve unresolved Script Resolution states as not resolved.
- [ ] Count Reachability coverage only on exact current map and World Index provenance.
- [ ] Associate physical scenarios only through executed `follow_route` plans with exact mechanic transition or interaction evidence.
- [ ] Require successful E2E result, executable route plan and retained current runtime-map provenance for current-map physical proof.
- [ ] Keep stale evidence explicit and fail closed.
- [ ] Report missing physical scenarios as coverage gaps, not mechanic failures.
- [ ] Support retained E2E artifact directories and ZIP files without committing generated artifacts.
- [ ] Add focused tests, schemas, documentation and module catalogue entry.
- [ ] Keep OTBM parsing, World Index generation, script resolution, Reachability and physical lifecycle unchanged.
- [ ] Apply `ci:final-gate` before final checkpoint commit and pass exact-final-head required checks.
- [ ] Complete final review/overlap/mergeability audit, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20
head: c34cca6da19b05d8cc05d45d2cf25fb8d71ef81b
branch: feat/otbm-e2e-007-coverage-matrix
pr: 639
status: implementing
context_routes:
  - agent-governance
  - otbm
  - universal-e2e
owned_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-007-coverage-matrix.md
  - docs/ai-agent/OTBM_E2E_COVERAGE.md
  - docs/ai-agent/OTBM_E2E_COVERAGE_TARGETS.schema.json
  - docs/ai-agent/OTBM_E2E_COVERAGE_MATRIX.schema.json
  - tools/ai-agent/otbm_e2e_coverage.py
  - tools/ai-agent/test_otbm_e2e_coverage.py
proven:
  - OTBM-E2E-006 feature PR 628 merged as 94f21d32891978e115a11ddcbe2c0dbd77fea8bd and lifecycle PR 638 merged as 052d96014c805aacaa120ce888b7bed038817a72 before this task started
  - draft PR 639 was opened from post-lifecycle main before implementation files were committed
  - existing Item Audit exposes exact mechanic placements without requiring this task to parse OTBM
  - existing Script Resolution preserves unresolved and conflicting runtime-handler states
  - existing Reachability retains map and World Index provenance and remains static evidence only
  - existing Universal Physical E2E artifacts retain scenario manifest result runtime map hash and route plans
  - local pre-implementation prototype passed 15 focused deterministic correlation and fail-closed tests
  - successful retained OTBM-E2E-005 pure movement artifact produced zero mechanic proof candidates
derived:
  - reviewed exact target input is required because criticality must not be guessed from item names sprites identifiers coordinates or chat history
  - physical mechanic proof must require an exact executed route-plan mechanic reference rather than movement through a coordinate
unknown:
  - exact final-head workflow conclusions
  - final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none
  evidence: no implementation failure recorded; local prototype validation is pre-branch evidence only
rejected_hypotheses:
  - scan or parse OTBM again for coverage: existing Item Audit and World Index evidence are authoritative inputs
  - infer critical mechanics automatically: criticality remains reviewed target input
  - treat confirmed Reachability as physical gameplay proof: static geometry evidence remains separate
  - treat successful follow_route movement as proof of every mechanic position crossed: only exact route transition or interaction references count
  - promote stale unresolved or missing-provenance evidence to current handled coverage: fail closed instead
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-007-coverage-matrix.md
validation:
  - command: local pre-implementation prototype focused tests
    result: PASS
    evidence: 15 focused tests passed for exact static script reachability and physical correlation plus fail-closed cases
  - command: retained OTBM-E2E-005 artifact sanity check
    result: PASS
    evidence: successful current-map pure movement route exposes zero mechanic transition or interaction proof candidates
blockers: []
next_action: Commit the bounded implementation, schemas, documentation and module catalogue entry, then run focused repository validation.
```
