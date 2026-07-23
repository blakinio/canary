---
task_id: CAN-20260723-ots-vocation-balance-forum-guidance
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: ""
status: blocked
agent: "GPT-5.6 Thinking"
branch: docs/ots-vocation-balance-forum-guidance-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "fcd258bb4f4702b8a735947afe38c3266242ce0b"
risk: low
related_issue: ""
related_pr: "843"
depends_on:
  - "PR #799 for the proposed OTS vocation/class role and balance framework"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md
    - docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md
  shared: []
  read_only:
    - docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md
    - docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md
modules_touched:
  - OTS future gameplay roadmap
  - OTS vocation/class balance design
reuses:
  - docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md
  - PR #799 OTS vocation/class role and balance framework
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — OTS vocation balance forum-derived guidance

## Status

BLOCKED — documentation synthesis is complete in draft PR #843, but the upstream vocation/class framework is still owned by open PR #799. This task does not modify or duplicate PR #799 paths and should not merge ahead of the framework dependency without an explicit rebase/reconciliation review.

## Goal

Convert recurring design and validation lessons from `docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md` into durable implementation-neutral guidance for future vocation balance work in `blakinio/canary`.

## Scope

- document cross-vocation balance principles derived from the forum analysis;
- define package-level, difficulty/risk, progression-breakpoint, reliability, input-burden and scenario-matrix guidance;
- record per-vocation investigation priorities without inventing numeric values;
- define a standard per-vocation worksheet and future balance decision pipeline;
- keep Real Tibia parity claims and OTS-specific design decisions explicitly separated;
- avoid runtime, datapack, protocol, map, binary, item or production changes.

## Context routes

- agent-governance
- real-tibia-parity

## Evidence state

- `PROVEN`: the source forum-analysis document explicitly classifies community feedback as prioritization evidence rather than gameplay parity or numeric authority.
- `PROVEN`: the source report contains seven complete official Tibia forum threads with 7,187 accessible unique posts plus a bounded Druid page-one sample at the observed baseline.
- `PROVEN`: open PR #799 owns `docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md` and explicitly defines class identity, role taxonomy, solo/party viability, target bands, progression bands, telemetry and balance governance.
- `PROVEN`: this task owns only a new guidance document and its task record, so it does not overlap PR #799's exclusive paths.
- `DERIVED`: the forum evidence is best used to improve the balance methodology and investigation order rather than to select coefficients directly.
- `UNKNOWN`: exact current Canary behavior, exact current Real Tibia values and final per-vocation target bands remain implementation-time work.

## Acceptance criteria

- [x] Analyze the current forum report as a bounded evidence source.
- [x] Preserve its evidence boundary and avoid copying proposal/live values as Canary authority.
- [x] Reuse the vocation/class framework proposed by PR #799 instead of creating a competing framework.
- [x] Add a standalone forum-derived guidance document on a non-overlapping path.
- [x] Cover cross-vocation methodology and all five supported vocation families discussed in the source.
- [x] Record source incompleteness for Druid and pending Paladin supplement work.
- [x] Define reusable per-vocation worksheet, decision pipeline and future research packages.
- [x] Open draft PR #843.
- [ ] Verify exact changed-file scope and diff after the task-record PR update.
- [ ] Verify applicable documentation ownership and CI gates on the newest head.
- [ ] Reconcile dependency against PR #799 before readiness/merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T23:50:00+02:00"
head: "fcd258bb4f4702b8a735947afe38c3266242ce0b"
branch: "docs/ots-vocation-balance-forum-guidance-20260723"
pr: "843"
status: "blocked"
context_routes:
  - "agent-governance"
  - "real-tibia-parity"
owned_paths:
  - "docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md"
  - "docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md"
proven:
  - "The source forum report is community-feedback evidence and explicitly does not establish current formulas, live values, Canary defects or numeric values to encode."
  - "At the observed source baseline the report states seven complete official Tibia forum threads with 7,187 accessible unique posts plus a bounded Druid page-one sample."
  - "PR #799 is open and owns the proposed OTS vocation/class role and balance framework; this task does not edit any of its owned paths."
  - "PR #823 is open and preparing a bounded Paladin design-thread supplement; the new guidance records that future RP work must re-read the updated source after that supplement lands."
  - "PR #843 is an in-repository draft against blakinio/canary:main and contains the new forum-derived guidance plus this task record."
  - "The new guidance document defines package-level balance, compensation ledger, difficulty premium, functional-before-numeric ordering, progression breakpoints, context separation, human-input cost, reliability budget, balance debt, vocation-specific priorities, a standard worksheet, a decision pipeline and future research packages."
derived:
  - "Future balance should define role/risk/execution/progression expectations before tuning coefficients."
  - "Damage changes must be evaluated together with leech, kill time, incoming turns, supplies, economy and party value."
  - "Functional defects in targeting, geometry or state transitions should be resolved before damage tuning."
  - "Core rotations should become functional before extreme endgame investment; later progression should primarily scale or specialize them."
unknown:
  - "Exact per-vocation current Canary runtime behavior and balance state."
  - "Exact current Real Tibia formulas and values."
  - "Final role-appropriate target bands and acceptable difficulty premiums."
  - "Whether the pending Paladin supplement or later broader Druid evidence will materially change vocation-specific prioritization."
conflicts: []
rejected_hypotheses:
  - "Forum post volume is sufficient numeric authority for Canary balance values."
  - "A flat global buff or nerf is the default answer to recurring vocation complaints."
  - "Raw DPS alone is a sufficient balance model."
  - "A new competing vocation-role framework should be created while PR #799 already owns that responsibility."
changed_paths:
  - "docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md"
  - "docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md"
validation:
  - command: "Repository/document evidence review via GitHub connector"
    result: "PASS"
    evidence: "Reviewed AGENTS.md, repository/context routing, Real Tibia evidence/playbook, source forum analysis, merged PR #821, open PR #799 framework and open PR #823 Paladin supplement scope."
blockers:
  - "PR #799 is the upstream design-framework dependency and remains open; this task must not modify its owned paths or merge without dependency reconciliation."
next_action: "Inspect PR #843 exact changed-file list and diff, verify current-head workflow results, then hold readiness/merge until PR #799 dependency is resolved and the guidance is reconciled against the merged framework."
```
