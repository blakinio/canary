---
task_id: CAN-20260723-ots-social-itemization-qol-roadmap
program_id: ""
coordination_id: ""
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/ots-social-itemization-qol-20260723
base_branch: main
created: 2026-07-23T15:31:47+02:00
updated: 2026-07-23T15:49:00+02:00
last_verified_commit: "b49d68cd5ca7eefa0589b0abc6abd07f4b9685a1"
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
    - docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md
  shared: []
  read_only: []
modules_touched:
  - OTS future gameplay roadmap
  - OTS gameplay proposal classification
  - OTS vocation/class role and balance framework
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

READY — user-approved 2026-07-23 future gameplay directions are persisted and classified in PR #799, including the later-added Vocation/Class Identity, Roles and Balance Framework. Documentation/design only; exact-final CI and ownership validation remain the merge gate.

## Goal

Persist the user-approved future OTS design directions discussed on 2026-07-23 around world/social map UX, privacy-aware contacts, party UX/accounting, itemization/build testing, inventory/storage, market/trade, slot-based Imbuement System 2.0, and explicit vocation/class identity, role and balance definitions.

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
- Vocation/class roles are formalized as product expectations only; no final current-vocation role assignment or numeric balance values are invented before implementation-time audit.

## Acceptance criteria

- [x] Record the approved social/itemization/QoL design directions in a durable detailed design file.
- [x] Add concise integration entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` without duplicating existing systems.
- [x] Add explicit `ORIGIN` and `TYPE` entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md`.
- [x] Add a durable Vocation/Class Identity, Roles and Balance Framework with explicit solo/party/context balance principles.
- [x] Classify the vocation/class balance proposals without introducing unsupported `TIBIA-OFFICIAL` claims.
- [x] Preserve open balance questions rather than inventing final numeric contracts.
- [x] Keep all changes documentation-only.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T15:49:00+02:00"
head: "b49d68cd5ca7eefa0589b0abc6abd07f4b9685a1"
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
  - "docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md"
proven:
  - "The existing roadmap already contained Character markers on minimap, Party Finder 2.0, Loot System Rework, Equipment Presets references, Better Map UX, Bank/Trade systems and Bounty/Weekly redesign entries; the new sections extend those concepts instead of creating parallel duplicates."
  - "docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md contains the detailed user-approved design record for world/social map, Friends/VIP privacy, active Party 2.0, party combat visibility/accounting, Itemization & Build 2.0, Training Arena, Inventory/Depot/Stash 2.0, Market/Trade additions and Imbuement System 2.0."
  - "docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md now defines the required class/vocation identity contract, shared role taxonomy, solo versus party viability principles, multi-dimensional target bands, progression-band analysis, separate PvE/boss/PvP contexts, build dependencies, telemetry and balance governance."
  - "The vocation framework deliberately avoids assigning speculative final numeric values or unsupported current-vocation mechanics before implementation-time audit."
  - "OTS_FUTURE_GAMEPLAY_SYSTEMS.md contains concise sections 29-35 integrating the social/itemization/QoL directions and dependency-map addendum."
  - "OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md continues the authoritative proposal index with entries 69-93 and explicit ORIGIN/TYPE classifications while preserving entries 1-68."
  - "No new TIBIA-OFFICIAL claims were introduced without dedicated parity proof; mixed existing foundations and custom directions remain MIXED/OUR-DESIGN with implementation-time reverification required."
  - "The feature scope remains documentation-only."
  - "PR #799 targets blakinio/canary:main from blakinio/canary:docs/ots-social-itemization-qol-20260723."
derived:
  - "Class/vocation definitions should become an upstream design dependency for Party System 2.0, Itemization & Build System 2.0, Imbuement System 2.0, Build Impact Calculator and Training Arena balance work."
  - "Balance should use role-appropriate target bands rather than forcing identical DPS or a rigid hard-trinity composition."
unknown:
  - "Exact current Tibia/Canary/OTClient parity for every Imbuement and vocation/class detail remains implementation-time work."
  - "Exact per-vocation identity, role assignment and numeric target bands remain open until each supported vocation/class is audited."
  - "Exact slot-level progression, active-channel counts, elemental attunement strength, lifecycle and economy costs remain open balance contracts."
  - "Exact privacy/PvP information-leak rules for live social tracking remain open."
  - "Exact TC/alternative-currency legal, accounting, protocol and abuse constraints remain open."
  - "Exact party accounting settlement mechanism and whether transfers are automatic or calculation-only remains open."
conflicts: []
first_failure:
  marker: "ownership-checkpoint-format"
  evidence: "Earlier Agent Task Ownership run 30012290185 reported that the context checkpoint lacked a fenced YAML block; the task record was repaired before the vocation framework extension."
rejected_hypotheses:
  - "A new parallel Party Finder is required."
  - "A new generic item rarity system should replace existing item classification/Forge foundations."
  - "Elemental Imbuements must permanently compete with all Crit/Leech/Skill active channels in the proposed redesign."
  - "Balanced vocations/classes must all have identical DPS."
  - "Every group activity must be forced into a rigid tank/healer/DPS composition."
changed_paths:
  - "docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md"
  - "docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md"
  - "docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md"
validation:
  - command: "Connector diff review before vocation extension"
    result: PASS
    evidence: "The prior four-path social/itemization/QoL scope was documentation-only and classification-complete through entry 88."
  - command: "Vocation framework classification review"
    result: PASS
    evidence: "New entries 89-93 classify class identity, role taxonomy, target-band telemetry, solo/party viability and context-separated balance without unsupported TIBIA-OFFICIAL claims."
blockers:
  - "Exact-final Agent Task Ownership, AI Agent Tools and CI runs for the newest head must pass before merge."
next_action: "Make no further feature-content commits. Verify exact-final PR #799 workflow results and review threads; if required checks are green and the autonomous merge gate is satisfied, mark ready and squash-merge."
```
