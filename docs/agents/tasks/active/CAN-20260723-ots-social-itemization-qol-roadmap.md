---
task_id: CAN-20260723-ots-social-itemization-qol-roadmap
program_id: ""
coordination_id: ""
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/ots-social-itemization-qol-20260723
base_branch: main
created: 2026-07-23T15:31:47+02:00
updated: 2026-07-23T15:42:48+02:00
last_verified_commit: "56abcd01630b03282ad9e6b970c49caaee0bd16e"
risk: low
related_issue: ""
related_pr: "799"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md
    - docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md
  shared: []
  read_only: []
modules_touched:
  - OTS future gameplay roadmap
  - OTS gameplay proposal classification
reuses:
  - Character markers on minimap
  - Better Map UX
  - Party Finder 2.0
  - Loot System Rework
  - Equipment Presets
  - Financial & Trading System 2.0
  - Bounty and Weekly Tasks Rework
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — OTS Social, Itemization and QoL Roadmap

## Status

READY — user-approved 2026-07-23 future gameplay directions are persisted and classified in PR #799. Documentation/design only; final-head CI and ownership validation remain the merge gate.

## Goal

Persist the user-approved future OTS design directions discussed on 2026-07-23 around world/social map UX, privacy-aware contacts, party UX/accounting, itemization/build testing, inventory/storage, market/trade, and a slot-based Imbuement System 2.0.

## Scope

Documentation/design only. No gameplay runtime, protocol, datapack, map, binary, economy configuration, client binary, or production behavior changes.

## Context routes

- agent-governance
- real-tibia-parity (classification/baseline cautions only where an existing Tibia mechanic is being extended)
- cross-repo (future Canary/OTClient design surface only; no cross-repo write)

## Reuse / overlap policy

- Extend existing `Character markers on minimap`, `Party Finder 2.0`, `Loot System Rework`, `Equipment Presets`, `Better Map UX`, `Bank/Trade`, and Bounty/Weekly concepts where applicable instead of creating duplicate parallel systems.
- New proposal names are used only for genuinely broader systems or missing sub-systems.
- Existing Tibia foundations are classified as `TIBIA-BASELINE`/`TIBIA-OFFICIAL` only when the roadmap already has suitable evidence; otherwise classification remains `MIXED` or `OUR-DESIGN` with implementation-time reverification required.

## Acceptance criteria

- [x] Record the approved design directions in a durable detailed design file.
- [x] Add concise integration entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` without duplicating existing systems.
- [x] Add explicit `ORIGIN` and `TYPE` entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md`.
- [x] Preserve open balance questions rather than inventing final numeric contracts.
- [x] Keep all changes documentation-only.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T15:42:48+02:00"
head: "56abcd01630b03282ad9e6b970c49caaee0bd16e"
branch: "docs/ots-social-itemization-qol-20260723"
pr: "799"
status: "ready"
context_routes:
  - "agent-governance"
  - "real-tibia-parity"
  - "cross-repo"
owned_paths:
  - "docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md"
  - "docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md"
proven:
  - "The existing roadmap already contained Character markers on minimap, Party Finder 2.0, Loot System Rework, Equipment Presets references, Better Map UX, Bank/Trade systems and Bounty/Weekly redesign entries; the new sections extend those concepts instead of creating parallel duplicates."
  - "docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md now contains the detailed user-approved design record for world/social map, Friends/VIP privacy, active Party 2.0, party combat visibility/accounting, Itemization & Build 2.0, Training Arena, Inventory/Depot/Stash 2.0, Market/Trade additions and Imbuement System 2.0."
  - "OTS_FUTURE_GAMEPLAY_SYSTEMS.md contains concise sections 29-35 integrating the new directions and dependency-map addendum."
  - "OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md continues the authoritative proposal index with entries 69-88 and explicit ORIGIN/TYPE classifications while preserving entries 1-68."
  - "No new TIBIA-OFFICIAL claims were introduced without dedicated parity proof; mixed existing foundations and custom directions remain MIXED/OUR-DESIGN with implementation-time reverification required."
  - "The final feature scope is documentation-only and contains exactly four expected paths."
  - "PR #799 targets blakinio/canary:main from blakinio/canary:docs/ots-social-itemization-qol-20260723 and is mergeable."
  - "Main advanced after branch creation only in unrelated paths, so there is no observed owned-path overlap."
  - "CI run 30012290450 succeeded on pre-fix final head 56abcd01630b03282ad9e6b970c49caaee0bd16e."
  - "Agent Task Ownership run 30012290185 failed only because the task Context checkpoint lacked the required fenced YAML block; this commit corrects that format defect."
derived:
  - "The user-approved design directions are durably recorded and classification-complete; remaining work is repository validation/merge coordination rather than product-design reconstruction."
unknown:
  - "Exact current Tibia/Canary/OTClient parity for every Imbuement detail remains implementation-time work."
  - "Exact slot-level progression, active-channel counts, elemental attunement strength, lifecycle and economy costs remain open balance contracts."
  - "Exact privacy/PvP information-leak rules for live social tracking remain open."
  - "Exact TC/alternative-currency legal, accounting, protocol and abuse constraints remain open."
  - "Exact party accounting settlement mechanism and whether transfers are automatic or calculation-only remains open."
conflicts: []
first_failure:
  marker: "ownership-checkpoint-format"
  evidence: "Agent Task Ownership run 30012290185 reported: context checkpoint heading has no fenced YAML block."
rejected_hypotheses:
  - "A new parallel Party Finder is required."
  - "A new generic item rarity system should replace existing item classification/Forge foundations."
  - "Elemental Imbuements must permanently compete with all Crit/Leech/Skill active channels in the proposed redesign."
changed_paths:
  - "docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md"
  - "docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md"
validation:
  - command: "Connector diff review"
    result: PASS
    evidence: "Four expected documentation paths only; roadmap has one purpose-line adjustment plus appended sections 29-35; classification has one purpose-link adjustment plus entries 69-88."
  - command: "GitHub CI run 30012290450"
    result: PASS
    evidence: "Completed successfully on head 56abcd01630b03282ad9e6b970c49caaee0bd16e before the checkpoint-format repair."
  - command: "Agent Task Ownership run 30012290185"
    result: FAIL_FIXED
    evidence: "Only failure was missing fenced YAML checkpoint; this commit adds the required machine-readable checkpoint."
blockers:
  - "Exact-final Agent Task Ownership, AI Agent Tools and CI runs for the checkpoint-format repair head must pass before merge."
next_action: "Make no further commits. Verify exact-final PR #799 workflow results and empty review threads; if required checks are green and the autonomous merge gate is satisfied, mark ready and squash-merge."
```
