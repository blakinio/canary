---
task_id: CAN-20260720-otbm-e2e-007-coverage-matrix
program_id: CAN-PROGRAM-OTBM-E2E-ROUTING
coordination_id: OTBM-E2E-007
status: ready
agent: "GPT-5.5 Thinking"
branch: feat/otbm-e2e-007-coverage-matrix
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "060cd22c7ba3eff2e8dcece58db95b8d7b4a87ef"
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

- [x] Accept only reviewed exact mechanic targets with an exact `x,y,z` position and at least one mechanic identity selector.
- [x] Prove static indexing from existing `canary-otbm-item-audit-v1` evidence pinned to the current World Index source-map SHA-256.
- [x] Preserve unresolved Script Resolution states as not resolved.
- [x] Count Reachability coverage only on exact current map and World Index provenance.
- [x] Associate physical scenarios only through executed `follow_route` plans with exact mechanic transition or interaction evidence.
- [x] Require successful E2E result, executable route plan and retained current runtime-map provenance for current-map physical proof.
- [x] Keep stale evidence explicit and fail closed.
- [x] Report missing physical scenarios as coverage gaps, not mechanic failures.
- [x] Support retained E2E artifact directories and ZIP files without committing generated artifacts.
- [x] Add focused tests, schemas, documentation and module catalogue entry.
- [x] Keep OTBM parsing, World Index generation, script resolution, Reachability and physical lifecycle unchanged.
- [ ] Pass exact-final-head required checks after the already-applied `ci:final-gate` label.
- [ ] Complete final review/overlap/mergeability audit, squash merge and lifecycle archive.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T20:20:00Z
head: 060cd22c7ba3eff2e8dcece58db95b8d7b4a87ef
branch: feat/otbm-e2e-007-coverage-matrix
pr: 639
status: validating
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
  - OTBM-E2E-006 feature PR 628 merged as 94f21d32891978e115a11ddcbe2c0dbd77fea8bd and lifecycle PR 638 merged as 052d96014c805aacaa120ce888b7bed038817a72 before OTBM-E2E-007 started
  - PR 639 delivers only seven bounded task catalogue documentation schema tool and test paths with no OTBM map or runtime lifecycle changes
  - repository AI Agent Tools OTBM Map Tools Agent Task Ownership and CI all passed on implementation head d58a42646f5ce5d051020cb72fd271c64af79b5c before the catalogue-only correction
  - the coverage aggregator reuses Item Audit Script Resolution Reachability route-plan and retained Universal Physical E2E evidence without parsing OTBM or creating another World Index pathfinder runner or workflow
  - unresolved ambiguous stale and missing-provenance evidence is not promoted to resolved or current-map runtime proof
  - physical mechanic evidence requires an executed follow_route route plan with an exact transition or interaction selector reference and current runtime map.sha256 for current-map proof
  - retained successful OTBM-E2E-005 evidence is a current-map pure movement route and produces zero mechanic proof candidates
  - ci:final-gate was applied to PR 639 before this final checkpoint commit
 derived:
  - reviewed exact target input keeps mechanic criticality outside automatic guessing
  - the delivered matrix separates static reachability evidence from physical gameplay proof and exposes missing physical scenarios as coverage gaps
unknown:
  - exact-final-head workflow conclusions after this checkpoint commit
  - final feature and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none
  evidence: no implementation failure remains; pre-final implementation workflows passed and exact-final-head validation is pending
rejected_hypotheses:
  - rescan or parse OTBM for coverage: existing Item Audit and World Index evidence are authoritative inputs
  - infer critical mechanics automatically: criticality remains reviewed target input
  - treat confirmed Reachability as physical gameplay proof: static geometry evidence remains separate
  - treat successful movement through a coordinate as mechanic proof: only exact executed transition or interaction route evidence counts
  - promote stale unresolved ambiguous or missing-provenance evidence to current handled coverage: fail closed instead
changed_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/tasks/active/CAN-20260720-otbm-e2e-007-coverage-matrix.md
  - docs/ai-agent/OTBM_E2E_COVERAGE.md
  - docs/ai-agent/OTBM_E2E_COVERAGE_TARGETS.schema.json
  - docs/ai-agent/OTBM_E2E_COVERAGE_MATRIX.schema.json
  - tools/ai-agent/otbm_e2e_coverage.py
  - tools/ai-agent/test_otbm_e2e_coverage.py
validation:
  - command: AI Agent Tools run 29775184324
    result: PASS
    evidence: repository AI agent unit-test workflow passed on implementation head d58a42646f5ce5d051020cb72fd271c64af79b5c
  - command: OTBM Map Tools run 29775184383
    result: PASS
    evidence: repository OTBM map tooling workflow passed on implementation head d58a42646f5ce5d051020cb72fd271c64af79b5c
  - command: Agent Task Ownership run 29775527684
    result: PASS
    evidence: ownership and checkpoint governance passed after the bounded catalogue correction
  - command: CI run 29775528020
    result: PASS
    evidence: repository CI passed after the bounded catalogue correction
  - command: retained OTBM-E2E-005 artifact sanity check
    result: PASS
    evidence: successful current-map pure movement artifact has one executable route plan and zero mechanic transition or interaction proof candidates
blockers: []
next_action: Verify exact-final-head workflows on the checkpoint commit; if green, audit current main overlap reviews threads and mergeability, mark PR 639 ready, squash-merge, then archive the task lifecycle.
```
