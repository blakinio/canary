---
task_id: CAN-20260718-universal-e2e-gameplay-roadmap
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-E2E-GAMEPLAY-ROADMAP-V1
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/e2e-gameplay-validation-roadmap-20260718
base_branch: main
created: 2026-07-18T23:08:00+02:00
updated: 2026-07-18T23:08:00+02:00
last_verified_commit: "be7842412beb5d240e76ffd4cd18aacdc3a2dcca"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - CAN-PROGRAM-E2E-PLATFORM
  - PR #562 OTBM-aware physical E2E routing programme (interface dependency only; no path overlap)
blocks:
  - E2E-GAMEPLAY-001 programme reconciliation
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

Publish one durable architecture and ordered implementation roadmap for the next phase of Universal Physical E2E: move from isolated proof scenarios to reusable, evidence-backed gameplay journeys covering navigation, quests/NPCs, combat, persistence, multi-client behavior, runtime recovery and cross-system flows, while preserving the existing single E2E platform and delegating static map-route planning to the OTBM integration programme.

# Acceptance criteria

- [ ] Reconcile the stale E2E programme record with merged platform and physical-proof work.
- [ ] Define the durable architecture layers and responsibility boundaries between static evidence, route planning, physical execution, assertions and retained evidence.
- [ ] Reference PR #562 as the owner of OTBM route planning/landmarks/route-plan contracts without duplicating its scope.
- [ ] Define an ordered work-package queue with dependencies, ownership boundaries, deliverables and acceptance gates.
- [ ] Cover the requested future domains: OTBM-aware navigation, quests, NPCs, combat, persistence, multi-client, runtime fault/recovery and cross-system journeys.
- [ ] Define scenario maturity levels so agents know when a static check, physical proof and persistence proof are each required.
- [ ] Record durable architectural decisions in an ADR.
- [ ] Keep implementation/runtime/workflow paths read-only in this planning task.
- [ ] Update the programme handoff so future agents start from current architecture rather than superseded PR #224.
- [ ] Open a draft PR early and keep changes documentation-only.

# Confirmed context

- `main` at task start is `be7842412beb5d240e76ffd4cd18aacdc3a2dcca`.
- The original `E2E_AUTOMATION_PROGRAM.md` is stale: it still calls PR #224 the active prototype and lists pre-bootstrap queue items.
- PR #245 is merged and is the authoritative reusable Universal E2E platform baseline.
- PRs #446, #477, #481, #512 and #525 are merged and establish generic gameplay actions, scenario selection, physical movement, floor change and teleport evidence.
- Draft PR #562 owns the OTBM-to-E2E route-integration programme and explicitly plans route export, semantic landmarks, interaction semantics, `follow_route`, preflight and a first landmark-to-landmark scenario.
- This task must not edit PR #562 exclusive paths or implement route planning itself.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #245 | Universal disposable Canary/MariaDB/controlled-OTClient lifecycle | `tools/e2e/**`, workflow and scenario infrastructure | canonical physical E2E platform |
| PR #446 | bounded declarative physical gameplay actions | `docs/e2e/PHYSICAL_GAMEPLAY_ACTION_PLANS.md` | generic action layer for feature suites |
| PR #477 | select one changed scenario on same-repo PRs | Universal E2E workflow/resolver | feature-owned scenarios can run automatically |
| PR #481 | physical movement proof | movement scenario/evidence | proves real-client positional execution |
| PR #512 | physical floor-change proof | floor-change scenario/evidence | proves cross-floor physical execution |
| PR #525 | physical teleport proof | teleport scenario/evidence | proves map mechanic execution and relog sentinel |
| PR #562 | OTBM-aware routing programme | draft planning PR | owns static route/landmark/interaction bridge |

# Ownership and overlap check

- Program record: `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`.
- Open PRs inspected: PR #562 is the only open E2E-related planning PR found.
- Active tasks inspected: PR #562 task owns only its new OTBM-route planning documents and task record.
- Exclusive claims: this task's architecture doc, ADR and task record only.
- Shared claims: narrow reconciliation of E2E programme and changelog.
- Read-only dependencies: all E2E implementation paths and PR #562 planned durable documents.
- Overlaps: none on exclusive paths.
- Resolution: this task defines the umbrella gameplay-E2E architecture; PR #562 remains authoritative for the OTBM routing bridge.

# Current state

Planning/documentation task started from current `main`; no implementation paths changed.

# Plan

1. Open a draft PR with this task record.
2. Write the durable gameplay-E2E architecture and ADR.
3. Reconcile `E2E_AUTOMATION_PROGRAM.md` to current merged state and ordered next-phase queue.
4. Add a narrow architecture-level changelog entry.
5. Review the full changed-file list for scope and cross-agent overlap; then run required documentation/ownership checks through GitHub CI.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep one Universal Physical E2E platform; feature suites consume it | merged PR #245 and repository programme contract | `ADR-20260718-universal-e2e-gameplay-validation-layers.md` |
| OTBM owns static map truth and route planning; E2E owns physical execution and runtime truth | avoids duplicate parser/pathfinder/orchestrator and matches PR #562 boundary | same ADR |
| Add capabilities only when demanded by a concrete feature suite | preserves feature/platform ownership separation | same ADR |

# Risks and compatibility

- Runtime: none in this docs-only task.
- Data/migration: none.
- Security: no production targets, credentials, maps or assets are introduced.
- Backward compatibility: existing E2E scenarios remain authoritative; this task only documents future sequencing.
- Cross-repo rollout: future OTClient API changes require separate cross-repository tasks; none are performed here.
- Rollback: revert the documentation PR.

# Remaining work

1. Open the draft PR and publish the two durable architecture documents plus programme reconciliation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T23:08:00+02:00
head: be7842412beb5d240e76ffd4cd18aacdc3a2dcca
branch: docs/e2e-gameplay-validation-roadmap-20260718
pr: none
status: implementing
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
  - draft PR 562 owns the OTBM-aware route integration programme and has no exclusive-path overlap with this task
derived:
  - the next durable E2E phase should organize feature coverage and evidence maturity around the existing platform rather than add another runner
  - OTBM route planning and Universal E2E physical execution should remain separate responsibility layers
unknown:
  - final merged contract details from draft PR 562; this roadmap references the programme boundary and must not depend on unmerged field-level schemas
conflicts: []
first_failure:
  marker: none
  evidence: narrow open-PR search found no exclusive-path overlap
rejected_hypotheses:
  - duplicate OTBM routing design in this task: PR 562 already owns that scope
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-universal-e2e-gameplay-roadmap.md
validation:
  - command: repository instruction and routed-context review
    result: PASS
    evidence: AGENTS.md, REPOSITORY_MAP.md, CONTEXT_ROUTING.md, E2E_AUTOMATION_PROGRAM.md and PR 562 inspected
blockers:
  - none
next_action: Open a draft PR for the task branch, then add the architecture, ADR and programme reconciliation.
```
