---
task_id: CAN-20260718-universal-e2e-gameplay-roadmap
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-GAMEPLAY-ROADMAP-V1
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/e2e-gameplay-validation-roadmap-20260718
base_branch: main
created: 2026-07-18T23:08:00+02:00
updated: 2026-07-18T21:35:35Z
last_verified_commit: "c1c0d10ed1e758cb72728be5fe22458cd9d9e61a"
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
completed: 2026-07-18T21:35:35Z
---

# Goal

Publish one durable architecture and ordered implementation roadmap for the next phase of Universal Physical E2E, covering OTBM-aware navigation, quests/NPCs, combat, persistence, multi-client behavior, runtime recovery and cross-system journeys while preserving the single existing E2E platform.

# Acceptance criteria

- [x] Reconcile stale E2E programme state with merged platform and physical-proof work.
- [x] Define durable responsibility layers for static evidence, route planning, physical execution, assertions and evidence.
- [x] Keep PR #562 authoritative for detailed OTBM routing contracts without duplicating its scope.
- [x] Define ordered work packages `E2E-GAMEPLAY-001` through `E2E-GAMEPLAY-008` with dependencies and acceptance gates.
- [x] Cover navigation, quests/NPCs, combat, persistence, multi-client, recovery and cross-system journeys.
- [x] Define M0-M5 evidence maturity levels.
- [x] Record the durable decision in an ADR.
- [x] Keep E2E runtime/workflow and OTBM implementation paths read-only.
- [x] Update programme handoff away from superseded PR #224.
- [x] Open draft PR #563.
- [x] Verify changed-file scope is exactly five intended documentation paths.
- [ ] Verify required current-head GitHub checks before readiness/merge.

# Delivered

- `docs/architecture/universal-e2e-gameplay-validation.md`: target architecture, evidence maturity model, dependency graph, eight work packages and future-agent rules.
- `docs/agents/decisions/ADR-20260718-universal-e2e-gameplay-validation-layers.md`: static-world/route-planning/physical-runtime separation and single-orchestrator decision.
- `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`: current merged baseline and ordered next-phase queue.
- `docs/agents/CHANGELOG.md`: architecture-level discovery entry.

# Ordered implementation plan

1. `E2E-GAMEPLAY-002`: consume stable OTBM route plans; no independent E2E pathfinder.
2. `E2E-GAMEPLAY-005`: reusable persistence assertion matrix; may proceed independently of route work.
3. `E2E-GAMEPLAY-003`: one deterministic quest/NPC vertical slice with M3 persistence where applicable.
4. `E2E-GAMEPLAY-004`: one deterministic bounded combat vertical slice.
5. `E2E-GAMEPLAY-006`: multi-client orchestration only from concrete feature demand.
6. `E2E-GAMEPLAY-007`: controlled fault/recovery proof after a stable baseline exists.
7. `E2E-GAMEPLAY-008`: cross-system journeys composed from already-proven capabilities.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep one Universal Physical E2E platform | merged PR #245 | `ADR-20260718-universal-e2e-gameplay-validation-layers.md` |
| OTBM owns static map truth/route planning; E2E owns physical execution/runtime truth | avoids duplicate parser/pathfinder/orchestrator; aligns with PR #562 | same ADR |
| Feature suites own expected gameplay values | keeps platform feature-neutral | same ADR |
| Generic capabilities use separate platform tasks | preserves ownership and reuse | same ADR |

# Validation and CI

- Exact PR #563 changed-file list: PASS; only five intended documentation paths.
- Final-gate CI run `29661291970`: PASS on head `21731fe7199f187eeb1a923c5d8a183cd4c464f6`.
- Final-gate Agent Task Ownership run `29661291928`: FAIL because this task used frontmatter `status: validating`, which is not an active status for a record under `tasks/active`.
- Root cause repair in this commit: frontmatter restored to active `status: implementing`; checkpoint execution state may remain `validating`.
- `ci:final-gate` remains applied, so this synchronize commit must receive a new exact-head validation set.

# Remaining work

1. Verify CI and Agent Task Ownership on the new final head; merge only if all required checks are green and no review blocker exists.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:29:00+02:00
head: 21731fe7199f187eeb1a923c5d8a183cd4c464f6
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
  - PRs 446, 477, 481, 512 and 525 provide merged E2E foundations used by this roadmap
  - draft PR 562 owns OTBM-aware routing and has no exclusive-path overlap with PR 563
  - PR 563 changed-file list is exactly five intended documentation paths
  - CI 29661291970 passed on 21731fe7199f187eeb1a923c5d8a183cd4c464f6
  - Ownership 29661291928 failed only because active task frontmatter used non-active status validating
derived:
  - future gameplay E2E should use bounded vertical slices on the existing platform
  - nontrivial navigation should consume the OTBM route bridge once stable
unknown:
  - final merged field-level contracts from draft PR 562
  - current-head checks after the active-status repair commit
conflicts: []
first_failure:
  marker: active-task-frontmatter-status
  evidence: run 29661291928 rejected status validating under tasks/active; repaired to implementing in this commit
rejected_hypotheses:
  - ownership-path overlap: exact changed-file review and PR 562 task ownership show no exclusive overlap
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-universal-e2e-gameplay-roadmap.md
  - docs/architecture/universal-e2e-gameplay-validation.md
  - docs/agents/decisions/ADR-20260718-universal-e2e-gameplay-validation-layers.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/CHANGELOG.md
validation:
  - command: exact PR 563 changed-file list review
    result: PASS
    evidence: exactly five intended documentation paths
  - command: CI 29661291970
    result: PASS
    evidence: exact head 21731fe7199f187eeb1a923c5d8a183cd4c464f6
  - command: Agent Task Ownership 29661291928
    result: FAIL
    evidence: non-active frontmatter status validating; root cause repaired to implementing
blockers:
  - none after active-status repair; awaiting exact-head checks
next_action: Verify required GitHub checks on the repaired final PR 563 head and merge only if the autonomous merge gate is satisfied.
```

## Automated lifecycle completion

- Feature PR: #563.
- Feature head: `3043cd5ba28e4801c160e2d19da1de64346a8868`.
- Merge commit: `c1c0d10ed1e758cb72728be5fe22458cd9d9e61a`.
- Merged at: `2026-07-18T21:35:35Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
