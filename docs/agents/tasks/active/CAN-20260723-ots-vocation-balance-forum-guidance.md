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
last_verified_commit: "9b91951470e3d361c116196f7c80b88c076c028b"
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
    - docs/ai-agent/OTS_VOCATION_BALANCE_REFERENCE_DATASET.md
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
  - zimbadev/crystalserver read-only implementation candidates
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — OTS vocation balance forum-derived guidance

## Status

BLOCKED — documentation synthesis and the first full balance-reference dataset are present in draft PR #843, but the upstream vocation/class framework is still owned by open PR #799. This task does not modify or duplicate PR #799 paths and should not merge ahead of the framework dependency without an explicit rebase/reconciliation review.

## Goal

Convert recurring design and validation lessons from `docs/ai-agent/REAL_TIBIA_VOCATION_ADJUSTMENTS_FORUM_ANALYSIS.md` into durable guidance and a concrete data baseline for future vocation balance work in `blakinio/canary`.

## Scope

- document cross-vocation balance principles derived from the forum analysis;
- define package-level, difficulty/risk, progression-breakpoint, reliability, input-burden and scenario-matrix guidance;
- record per-vocation investigation priorities without inventing numeric values;
- build a concrete 2026 vocation-adjustment reference dataset covering spell names, incantations, base powers where officially established, mana, levels, cooldowns, targeting, areas, stances, Wheel values and global balance dependencies;
- compare current official data with pinned `blakinio/canary` and read-only `zimbadev/crystalserver` implementation candidates;
- identify current-value conflicts, stale donor values and formula paths where stored `basePower` is not consumed by runtime callbacks;
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
- `PROVEN`: official June 2, July 7, July 14 and July 15, 2026 material plus the current official spell library establish a concrete current/release dataset for the major 2026 vocation-adjustment surfaces, with explicit source conflicts retained rather than guessed.
- `PROVEN`: `zimbadev/crystalserver` at `75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac` contains implementations of multiple new 2026 spells and is useful as a read-only candidate source.
- `PROVEN`: several Crystal candidates are stale versus post-July official values, and several damage callbacks ignore their stored `basePower` parameter; metadata-only edits would therefore not implement current damage values.
- `PROVEN`: at Canary baseline `24d106b5eea40371833ce20de96184b55cd9b661`, expected standard paths for Shield Bash, Shield Slam, Divine Barrage, Ethereal Barrage, Death Echo, Forked Glacier, Forked Thorns and Thousand Fist Blows were not found in the bounded path checks used by this task.
- `DERIVED`: the forum evidence is best used to improve balance methodology and investigation order, while the new reference dataset supplies the concrete data needed to start bounded parity audits.
- `UNKNOWN`: exact current Canary runtime behavior for every adjusted mechanic, exact hidden Real Tibia formulas, and final OTS per-vocation target bands remain implementation-time work.

## Acceptance criteria

- [x] Analyze the current forum report as a bounded evidence source.
- [x] Preserve its evidence boundary and avoid copying forum consensus as numeric authority.
- [x] Reuse the vocation/class framework proposed by PR #799 instead of creating a competing framework.
- [x] Add a standalone forum-derived guidance document on a non-overlapping path.
- [x] Cover cross-vocation methodology and all five supported vocation families discussed in the source.
- [x] Record source incompleteness for Druid and pending Paladin supplement work.
- [x] Define reusable per-vocation worksheet, decision pipeline and future research packages.
- [x] Add a concrete reference dataset with current/release spell and mechanic values required for future balance analysis.
- [x] Add a pinned CrystalServer comparison and keep it explicitly read-only/non-authoritative.
- [x] Record stale donor values and formula-integration risks rather than presenting Crystal as parity proof.
- [x] Open draft PR #843.
- [ ] Verify exact changed-file scope and diff after the dataset/task-record updates.
- [ ] Verify applicable documentation ownership and CI gates on the newest head.
- [ ] Reconcile dependency against PR #799 before readiness/merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T23:59:00+02:00"
head: "9b91951470e3d361c116196f7c80b88c076c028b"
branch: "docs/ots-vocation-balance-forum-guidance-20260723"
pr: "843"
status: "blocked"
context_routes:
  - "agent-governance"
  - "real-tibia-parity"
owned_paths:
  - "docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md"
  - "docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md"
  - "docs/ai-agent/OTS_VOCATION_BALANCE_REFERENCE_DATASET.md"
proven:
  - "The source forum report is community-feedback evidence and explicitly does not establish current formulas, live values, Canary defects or numeric values to encode."
  - "At the observed source baseline the report states seven complete official Tibia forum threads with 7,187 accessible unique posts plus a bounded Druid page-one sample."
  - "PR #799 is open and owns the proposed OTS vocation/class role and balance framework; this task does not edit any of its owned paths."
  - "PR #823 is open and preparing a bounded Paladin design-thread supplement; future RP-specific work must re-read the updated source after that supplement lands."
  - "PR #843 contains forum-derived methodology, a concrete 2026 vocation balance reference dataset and this task record."
  - "The dataset records global 2026 balance changes plus EK/RP/MS/ED/Monk spell and mechanic data, current post-July numerical corrections, official spell-library metadata, historical Monk values needed to resolve current base powers, and a Canary/Crystal candidate matrix."
  - "CrystalServer is pinned at 75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac and used only as read-only implementation evidence."
  - "Crystal Death Echo, Forked Glacier, Forked Thorns, Strong Ice Wave and both Great Beams expose stored basePower values that their inspected formula callbacks do not consume; metadata-only corrections would not update runtime damage."
  - "Crystal headline values are stale for several post-July mechanics, including Death Echo, Forked Glacier, Forked Thorns, Strong Ice Wave, Great Death Beam, Great Energy Beam and Mystic Repulse."
  - "Crystal Divine Barrage and Ethereal Barrage are comparatively strong implementation candidates but still require deterministic targeting/area/formula validation."
  - "The current official Death Echo mana value remains a recorded conflict: June release-state says 155 while the current official spell library says 150."
derived:
  - "Future balance should define role/risk/execution/progression expectations before tuning coefficients."
  - "Damage changes must be evaluated together with leech, kill time, incoming turns, supplies, economy and party value."
  - "Functional defects in targeting, geometry or state transitions should be resolved before damage tuning."
  - "Core rotations should become functional before extreme endgame investment; later progression should primarily scale or specialize them."
  - "Crystal should be mined field-by-field rather than imported file-by-file because its 2026 vocation-adjustment coverage mixes current, stale and potentially semantically divergent implementations."
unknown:
  - "Exact per-vocation current Canary runtime behavior and complete registration coverage."
  - "Exact hidden current Real Tibia damage/healing formulas not published by official material."
  - "Final role-appropriate target bands and acceptable difficulty premiums."
  - "Whether the pending Paladin supplement or later broader Druid evidence will materially change vocation-specific prioritization."
conflicts:
  - "Death Echo mana: official June release-state 155 versus current official spell library 150; resolve by current live/runtime evidence or later explicit official change."
rejected_hypotheses:
  - "Forum post volume is sufficient numeric authority for Canary balance values."
  - "A flat global buff or nerf is the default answer to recurring vocation complaints."
  - "Raw DPS alone is a sufficient balance model."
  - "A new competing vocation-role framework should be created while PR #799 already owns that responsibility."
  - "A CrystalServer implementation with the correct spell name or basePower metadata is automatically current Real Tibia parity."
changed_paths:
  - "docs/ai-agent/OTS_VOCATION_BALANCE_FORUM_DERIVED_GUIDANCE.md"
  - "docs/ai-agent/OTS_VOCATION_BALANCE_REFERENCE_DATASET.md"
  - "docs/agents/tasks/active/CAN-20260723-ots-vocation-balance-forum-guidance.md"
validation:
  - command: "Repository/document evidence review via GitHub connector"
    result: "PASS"
    evidence: "Reviewed AGENTS.md, repository/context routing, Real Tibia evidence/playbook, source forum analysis, merged PR #821, open PR #799 framework and open PR #823 Paladin supplement scope."
  - command: "Official 2026 vocation-adjustment chronology and current spell-library review"
    result: "PASS"
    evidence: "Recorded June release state, July 7 balance corrections, June 23/July 7/July 14/July 15 fixes and current official spell metadata; conflicts remain explicit."
  - command: "Pinned CrystalServer candidate inspection"
    result: "PASS"
    evidence: "Inspected representative new/changed spell implementations and formula callbacks at pinned Crystal commit; documented stale values and semantic/formula risks."
blockers:
  - "PR #799 is the upstream design-framework dependency and remains open; this task must not modify its owned paths or merge without dependency reconciliation."
next_action: "Inspect PR #843 exact changed-file list and newest-head diff, verify current-head workflow results, then hold readiness/merge until PR #799 dependency is resolved and the dataset/guidance are reconciled against the merged framework."
```
