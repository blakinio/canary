---
task_id: CAN-20260723-e2e-quality-resilience-roadmap
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-QUALITY-RESILIENCE-ROADMAP-20260723
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/e2e-quality-resilience-roadmap-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "115f3ac2fffc36bb4e415c2a6fb45908d9538ba3"
risk: low
related_issue: ""
related_pr: "797"
depends_on:
  - E2E-GAMEPLAY-001 through E2E-GAMEPLAY-008 delivered and lifecycle-closed
  - merged Universal Physical E2E platform and bounded action-plan lifecycle
  - merged bounded two-client orchestration and client-disconnect recovery contracts
  - merged OTBM-aware route-plan, follow_route and exact-map preflight foundations
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-e2e-quality-resilience-roadmap.md
    - docs/architecture/universal-e2e-quality-resilience-roadmap.md
    - docs/agents/decisions/ADR-20260723-universal-e2e-quality-resilience-intelligence.md
  shared:
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/architecture/universal-e2e-gameplay-validation.md
    - docs/agents/MODULE_CATALOG.md
    - tools/e2e/**
    - tests/e2e/**
    - .github/workflows/universal-agent-e2e.yml
modules_touched:
  - Universal E2E quality, resilience and test-intelligence roadmap
reuses:
  - single canonical disposable Canary/MariaDB/controlled-OTClient lifecycle
  - existing evidence maturity levels M0 through M5
  - existing OTBM-aware route execution and exact-map preflight contracts
  - existing bounded two-client orchestration
  - existing controlled client-disconnect recovery
  - existing typed persistence assertions
  - existing changed-scenario and Semantic Diff impact selection
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — Universal E2E quality, resilience and intelligence roadmap

## Goal

Extend the durable Universal E2E roadmap beyond the delivered E2E-GAMEPLAY-001..008 bootstrap/maturity packages with a prioritized, dependency-aware programme for broader gameplay coverage, resilience, determinism, diagnostics, performance and release confidence. This task is documentation and architecture only; it does not implement new runner behavior, workflows, fault seams or gameplay scenarios.

## Acceptance criteria

- [x] Publish one durable post-008 roadmap that captures every discussed improvement without claiming any unimplemented capability is already delivered.
- [x] Organize the roadmap into gameplay coverage, reliability/resilience, test intelligence/diagnostics and operational/release-validation workstreams.
- [x] Include concrete packages for real two-player trade/persistence, Canary restart recovery, a broader real-player journey, coverage maturity reporting, flake/stability certification, controlled DB interruption, richer first-failure evidence and OTClient UI assertions.
- [x] Include differential runtime E2E, deterministic replay, failure minimization, fixture snapshot/restore, exactly-once validation, concurrency/race validation, soak tests, performance regression, client/server compatibility matrices, datapack matrices, migration E2E, save/restart consistency, controlled test time, invariant/property validation, reproducible gameplay fuzzing, protocol/state-machine misuse tests, cleanup certification, dependency-graph test selection, crash artifact bundles and release certification suites.
- [x] Define dependencies and safe rollout boundaries so destructive or production-facing fault injection remains forbidden and isolated seams are required.
- [x] Preserve one canonical E2E orchestrator and workflow family; no second runner, independent pathfinder or feature-specific full lifecycle is proposed.
- [x] Distinguish PR-gating suites, scheduled/nightly suites, release-certification suites and on-demand investigation to control cost and flakiness.
- [x] Record a durable ADR for the post-008 architecture decision.
- [x] Update the E2E programme record to point at the successor roadmap and mark 001..008 as the delivered foundation rather than the active future queue.
- [x] Update the agent-facing changelog with the architecture-level roadmap addition.
- [ ] Pass Agent Task Ownership and repository documentation/CI validation on the exact final head before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T15:10:00+02:00
head: 220c9e313cbf7da122ea2c7047ea0eaad052c285
branch: docs/e2e-quality-resilience-roadmap-20260723
pr: 797
status: validating
context_routes:
  - universal-e2e
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-quality-resilience-roadmap.md
  - docs/architecture/universal-e2e-quality-resilience-roadmap.md
  - docs/agents/decisions/ADR-20260723-universal-e2e-quality-resilience-intelligence.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/CHANGELOG.md
proven:
  - E2E-GAMEPLAY-006 bounded two-client orchestration is delivered through PR 747 and lifecycle archive PR 753.
  - E2E-GAMEPLAY-007 controlled client-disconnect recovery is delivered through PR 751 and lifecycle archive PR 764.
  - E2E-GAMEPLAY-008 representative cross-system promotion/combat/persistence journey is delivered through PR 765 and lifecycle archive PR 791.
  - PR 797 adds a documentation-only successor roadmap with 28 E2E-QRI packages covering all discussed gameplay, resilience, intelligence, diagnostics, operational and release ideas.
  - The roadmap keeps M0 through M5 unchanged and defines determinism, stability, resilience, exactly-once, concurrency, cleanup, performance, compatibility and diagnostics as orthogonal quality dimensions.
  - The roadmap separates PR-required, scheduled/nightly, release-certification and on-demand execution tiers and forbids arbitrary fault-command surfaces or production targets.
  - The E2E programme now treats E2E-GAMEPLAY-001 through 008 as the delivered foundation and points future work to the E2E-QRI successor roadmap.
  - The architecture decision is recorded in ADR-20260723-universal-e2e-quality-resilience-intelligence and the agent-facing changelog includes the new roadmap.
derived:
  - The first implementation wave should establish result/diagnostic and cleanup foundations before expensive repetition, then prove real trade, Canary restart recovery, Journey 002, factual coverage and stability certification.
  - Expensive soak, matrix, fuzz and resilience suites belong in scheduled, release or on-demand tiers rather than unconditional every-PR execution.
unknown:
  - Exact implementation package ordering may change when future tasks inspect live feature demand and path ownership.
conflicts: []
first_failure:
  marker: none
  evidence: Documentation-only roadmap package is implemented; pre-final ownership and CI validation remain to be evaluated.
rejected_hypotheses:
  - Create E2E-GAMEPLAY-009 immediately: rejected because the successor roadmap separates 28 bounded packages selected later from concrete demand and live dependencies.
  - Add a second E2E runner for resilience or soak testing: rejected because the canonical Universal E2E lifecycle remains authoritative.
  - Extend M0-M5 with linear levels for performance or stability: rejected because those are orthogonal quality dimensions rather than stronger gameplay maturity proofs.
  - Run soak, fuzzing and compatibility matrices on every PR: rejected because cost and noise require tiered execution.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-e2e-quality-resilience-roadmap.md
  - docs/architecture/universal-e2e-quality-resilience-roadmap.md
  - docs/agents/decisions/ADR-20260723-universal-e2e-quality-resilience-intelligence.md
  - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
  - docs/agents/CHANGELOG.md
validation:
  - command: GitHub preflight for open E2E programme/architecture PR overlap
    result: PASS
    evidence: No open PR matched E2E_AUTOMATION_PROGRAM or universal-e2e-gameplay-validation at task start.
  - command: Manual roadmap completeness audit against discussed E2E improvement set
    result: PASS
    evidence: E2E-QRI-001 through 028 cover every improvement discussed in both follow-up idea sets and retain safety/execution-tier boundaries.
blockers: []
next_action: Audit PR 797 exact changed-file list and diff, run pre-final Ownership/CI, then apply ci:final-gate before the final checkpoint commit and require exact-final-head checks before merge.
```
