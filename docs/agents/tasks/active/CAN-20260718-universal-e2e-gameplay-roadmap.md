---
task_id: CAN-20260718-universal-e2e-gameplay-roadmap
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-GAMEPLAY-ROADMAP-V1
status: validating
agent: "GPT-5.5 Thinking"
branch: docs/e2e-gameplay-validation-roadmap-20260718
base_branch: main
created: 2026-07-18T23:08:00+02:00
updated: 2026-07-18T23:19:00+02:00
last_verified_commit: "9dd85acdb3af9a336fbe516954a5c36f30e6278f"
risk: low
related_issue: ""
related_pr: "563"
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM
  - PR #562 OTBM-aware physical E2E routing programme (interface dependency only; no path overlap)
blocks:
  - E2E-GAMEPLAY-002 OTBM-aware route consumption
  - E2E-GAMEPLAY-003 quest and NPC physical suites
  - E2E-GAMEPLAY-004 combat physical suite
  - E2E-GAMEPLAY-005 persistence matrix
  - E2E-GAMEPLAY-006 multi-client orchestration
  - E2E-GAMEPLAY-007 runtime fault and recovery validation
  - E2E-GAMEPLAY-008 cross-system journey scenarios
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260718-universal-e2e-gameplay-roadmap.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - docs/agents/decisions/ADR-20260718-universal-e2e-gameplay-validation-layers.md
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/agents/programs/OTBM_E2E_ROUTE_INTEGRATION_PROGRAM.md
    - docs/ai-agent/OTBM_E2E_ROUTE_INTEGRATION.md
    - tools/e2e/**
    - tests/e2e/**
    - .github/workflows/**
modules_touched:
  - Universal OTS E2E automation programme architecture
reuses:
  - Universal OTS E2E platform from merged PR #245
  - declarative physical gameplay action plans from merged PR #446
  - same-repository scenario selection from merged PR #477
  - physical movement proof from merged PR #481
  - physical floor-change proof from merged PR #512
  - physical teleport proof from merged PR #525
  - OTBM-aware route integration programme from draft PR #562
public_interfaces:
  - programme work-package IDs E2E-GAMEPLAY-001 through E2E-GAMEPLAY-008
cross_repo_tasks: []
---

# Goal

Publish one durable architecture and ordered implementation roadmap for the next phase of Universal Physical E2E: move from isolated physical proofs to reusable evidence-backed gameplay validation covering OTBM-aware navigation, quests/NPCs, combat, persistence, multi-client behavior, runtime recovery and cross-system journeys while preserving the single existing E2E platform.

# Acceptance criteria

- [x] Reconcile the stale E2E programme record with merged platform and physical-proof work.
- [x] Define durable architecture layers and responsibility boundaries between static evidence, route planning, physical execution, assertions and retained evidence.
- [x] Reference PR #562 as owner of OTBM route planning/landmarks/route-plan work without duplicating its scope.
- [x] Define an ordered work-package queue with dependencies, ownership boundaries, deliverables and acceptance gates.
- [x] Cover OTBM-aware navigation, quests, NPCs, combat, persistence, multi-client, runtime fault/recovery and cross-system journeys.
- [x] Define evidence maturity levels from static evidence through recovery proof.
- [x] Record durable architectural decisions in an ADR.
- [x] Keep implementation/runtime/workflow paths read-only in this planning task.
- [x] Update the programme handoff so future agents start from current architecture rather than superseded PR #224.
- [x] Open draft PR #563 and keep changes documentation-only.
- [ ] Verify exact changed-file scope and required current-head GitHub checks before readiness/merge.

# Confirmed context

- Task-start `main`: `be7842412beb5d240e76ffd4cd18aacdc3a2dcca`.
- PR #245 is the merged reusable Universal E2E platform baseline.
- PRs #446, #477, #481, #512 and #525 establish merged generic gameplay actions, scenario selection, movement, floor change and teleport proof.
- Draft PR #562 owns the detailed OTBM-to-E2E route-integration programme.
- PR #563 is this umbrella E2E architecture/roadmap task and does not edit PR #562 exclusive paths.

# Delivered

- `docs/architecture/universal-e2e-gameplay-validation.md`
  - eight architecture layers;
  - M0-M5 evidence maturity model;
  - work packages `E2E-GAMEPLAY-001` through `E2E-GAMEPLAY-008`;
  - dependency graph and per-package acceptance gates;
  - future-agent startup and non-duplication rules.
- `docs/agents/decisions/ADR-20260718-universal-e2e-gameplay-validation-layers.md`
  - durable separation of static world intelligence, route planning and physical runtime proof;
  - one Universal E2E orchestrator remains authoritative.
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`
  - stale PR #224 prototype state replaced by current merged baseline and next-phase queue;
  - PR #562 recorded as the separate OTBM routing owner.
- `docs/agents/CHANGELOG.md`
  - architecture-level discovery entry added.

# Ordered implementation plan

1. `E2E-GAMEPLAY-002`: consume stable OTBM route plans in Universal Physical E2E; no independent E2E pathfinder.
2. `E2E-GAMEPLAY-005`: reusable persistence assertion matrix; may proceed independently of route work.
3. `E2E-GAMEPLAY-003`: one deterministic quest/NPC vertical slice with M3 persistence where durable state is expected.
4. `E2E-GAMEPLAY-004`: one deterministic bounded combat vertical slice.
5. `E2E-GAMEPLAY-006`: multi-client orchestration only when a concrete feature requires it.
6. `E2E-GAMEPLAY-007`: controlled runtime fault/recovery validation after a stable baseline exists.
7. `E2E-GAMEPLAY-008`: cross-system journeys composed only from already-proven lower-level capabilities.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep one Universal Physical E2E platform | merged PR #245 and existing platform contract | `ADR-20260718-universal-e2e-gameplay-validation-layers.md` |
| OTBM owns static map truth/route planning; E2E owns physical execution/runtime truth | avoids duplicate parser/pathfinder/orchestrator and matches PR #562 boundary | same ADR |
| Feature suites own expected gameplay values | keeps shared platform feature-neutral | same ADR |
| Generic capabilities are separate platform tasks | preserves ownership and reuse | same ADR |

# Risks and compatibility

- Runtime: none; documentation-only task.
- Data/migration: none.
- Security: no production targets, credentials, maps, dumps or assets introduced.
- Backward compatibility: no existing scenario/runtime/workflow changed.
- Cross-repo rollout: future OTClient changes require separate coordinated tasks; none here.
- Rollback: revert PR #563.

# Remaining work

1. Verify PR #563 changed files and current-head required checks; fix only task-scoped failures.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:19:00+02:00
head: 9dd85acdb3af9a336fbe516954a5c36f30e6278f
branch: docs/e2e-gameplay-validation-roadmap-20260718
pr: 563
status: validating
context_routes:
  - agent-governance
  - universal-e2e
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260718-universal-e2e-gameplay-roadmap.md
  - docs/architecture/universal-e2e-gameplay-validation.md
  - docs/agents/decisions/ADR-20260718-universal-e2e-gameplay-validation-layers.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/CHANGELOG.md
proven:
  - main task-start SHA is be7842412beb5d240e76ffd4cd18aacdc3a2dcca
  - PR 245 is the merged Universal E2E platform baseline
  - PRs 446, 477, 481, 512 and 525 provide merged gameplay-action, scenario-selection, movement, floor-change and teleport foundations
  - draft PR 562 owns the OTBM-aware route integration programme and has no exclusive-path overlap with PR 563
  - PR 563 contains the umbrella architecture, ADR, reconciled E2E programme and changelog entry
derived:
  - future gameplay E2E work should be delivered as bounded vertical slices on the existing platform
  - nontrivial navigation should consume the OTBM route bridge once stable rather than embed blind directional scripts
unknown:
  - final merged field-level contracts from draft PR 562
conflicts: []
first_failure:
  marker: none
  evidence: implementation paths remain read-only and no exclusive-path overlap was found
rejected_hypotheses:
  - duplicate OTBM routing design in PR 563: PR 562 already owns that scope
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-universal-e2e-gameplay-roadmap.md
  - docs/architecture/universal-e2e-gameplay-validation.md
  - docs/agents/decisions/ADR-20260718-universal-e2e-gameplay-validation-layers.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/CHANGELOG.md
validation:
  - command: repository instruction and routed-context review
    result: PASS
    evidence: AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, E2E_AUTOMATION_PROGRAM.md and PR 562 inspected
  - command: documentation-only scope review
    result: PASS
    evidence: no tools/e2e, tests/e2e, workflow, runtime, OTBM binary or asset path intentionally edited
blockers:
  - none
next_action: Verify PR 563 exact changed-file list and current-head GitHub checks before readiness.
```
