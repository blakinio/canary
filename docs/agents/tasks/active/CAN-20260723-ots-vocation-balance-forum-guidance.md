---
task_id: CAN-20260723-ots-vocation-balance-forum-guidance
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: OTS-VOCATION-BALANCE-FORUM-GUIDANCE
status: review
agent: "GPT-5.6 Thinking"
branch: docs/ots-vocation-balance-forum-guidance-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-24
last_verified_commit: "3e6a0302918c28eea924087d413dcc43f2d8ddba"
risk: low
related_issue: ""
related_pr: "843"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md
    - docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md
    - docs/ai-agent/OTS_VOCATION_BALANCE_REFERENCE_DATASET.md
  shared: []
  read_only:
    - docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md
    - docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md
modules_touched:
  - OTS vocation/class balance design
  - Real Tibia vocation evidence
reuses:
  - docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md
  - merged OTS vocation/class role and balance framework from PR #799
  - zimbadev/crystalserver read-only implementation candidates
public_interfaces: []
cross_repo_tasks: []
---

# OTS vocation balance forum-derived guidance

## Status

REVIEW — the upstream vocation/class framework merged through PR #799 as `8b48671a47584de9335d1fe403eb89222dd45402`. The forum-derived methodology and concrete 2026 reference dataset are reconciled as a downstream design/evidence layer. PR #823 was closed without merge because it never delivered the planned Paladin supplement; no missing data was inferred.

## Goal

Convert recurring design and validation lessons from the retained vocation-forum analysis into durable guidance and a concrete current/release data baseline for future bounded vocation-balance work.

## Acceptance criteria

- [x] Preserve forum evidence as prioritisation input, never numeric authority.
- [x] Define package-level, difficulty/risk, progression, reliability and scenario-matrix guidance.
- [x] Cover all five supported vocation families without inventing final values.
- [x] Add the concrete 2026 official/Canary/Crystal comparison dataset.
- [x] Record source conflicts, stale donor values and formula-integration risks.
- [x] Keep CrystalServer read-only and non-authoritative.
- [x] Keep exact runtime parity and hidden formulas explicitly unresolved.
- [x] Reconcile against merged PR #799 without editing its framework paths.
- [x] Close unsupported PR #823 without merging a checkpoint-only deliverable.
- [ ] Pass exact-final Agent Task Ownership, AI Agent Tools and CI.
- [ ] Mark ready and squash-merge through repository protection.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T17:30:00+02:00
head: 3e6a0302918c28eea924087d413dcc43f2d8ddba
branch: docs/ots-vocation-balance-forum-guidance-20260723
pr: 843
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md
  - docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md
  - docs/ai-agent/OTS_VOCATION_BALANCE_REFERENCE_DATASET.md
proven:
  - The source report explicitly treats community feedback as prioritisation evidence rather than proof of formulas, live values or Canary defects.
  - The observed source baseline contains seven complete official Tibia forum threads with 7,187 accessible unique posts plus a bounded Druid page-one sample.
  - The guidance and dataset change exactly two documentation paths plus this task record and no runtime, datapack, protocol, map, binary or production path.
  - The dataset records current/release official states, Canary observations, pinned Crystal candidates, conflicts and unknowns separately.
  - CrystalServer is pinned at 75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac and remains read-only/non-authoritative.
  - Several Crystal candidates are stale after July 2026 and several inspected callbacks do not consume their stored basePower value.
  - PR 799 final head c59ef0b22414133c1deb92b4652c66410fb76dc6 squash-merged as 8b48671a47584de9335d1fe403eb89222dd45402 after exact-head Ownership, AI Agent Tools and ready-state CI success.
  - The merged framework defines class identity, role taxonomy, solo/party viability, target bands, progression-band analysis, context-separated balance, telemetry and governance reused by this package.
  - PR 823 was closed without merge because it contained only a checkpoint and no supported Paladin supplement deliverable.
derived:
  - Balance work should define role, risk, execution and progression expectations before coefficient tuning.
  - Functional targeting, geometry and state-machine correctness must precede numeric balance changes.
  - Donor implementations must be reused field-by-field only after deterministic proof.
unknown:
  - Exact current Canary runtime behavior and complete registration for every adjusted mechanic.
  - Hidden current Real Tibia formulas not published by official material.
  - Final role-appropriate target bands and acceptable difficulty premiums.
  - Whether a future fresh Paladin-specific corpus will materially change RP prioritisation.
conflicts:
  - Death Echo mana remains an official-source conflict: June release-state 155 versus current spell-library 150.
first_failure:
  marker: dependency-and-ownership-gate
  evidence: Earlier ownership validation required checkpoint repair and the task then remained blocked until the framework merged; both conditions are now resolved for final exact-head validation.
rejected_hypotheses:
  - Forum post volume is numeric authority.
  - Raw DPS alone is a sufficient balance model.
  - CrystalServer spell metadata proves current Tibia parity.
  - Missing Paladin supplement results may be reconstructed or inferred from its checkpoint.
changed_paths:
  - docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md
  - docs/ai-agent/OTS_VOCATION_BALANCE_REFERENCE_DATASET.md
  - docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md
validation:
  - command: repository/document evidence review
    result: PASS
    evidence: Scope, source boundaries, official chronology, Canary observations and pinned Crystal candidates were reviewed and retained separately.
  - command: merged PR 799 framework reconciliation
    result: PASS
    evidence: The downstream documents reuse the merged role/balance framework without modifying or duplicating its paths.
  - command: PR 823 delivery review
    result: PASS
    evidence: The PR contained only its task/checkpoint and no report modification; it was closed without merge.
  - command: exact-final Agent Task Ownership, AI Agent Tools and CI
    result: NOT_RUN
    evidence: Required workflows must run on this final checkpoint commit after ci:final-gate.
blockers: []
next_action: Require exact-final checks, inspect reviews/threads, mark PR 843 ready and squash-merge with expected head if all gates pass.
```
