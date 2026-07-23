---
task_id: CAN-20260723-ots-social-itemization-qol-roadmap
program_id: ""
coordination_id: ""
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/ots-social-itemization-qol-20260723
base_branch: main
created: 2026-07-23T15:31:47+02:00
updated: 2026-07-23T16:55:00+02:00
last_verified_commit: "0af0302bc88118cc5565365c49e99f7b669c66de"
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
    - docs/ai-agent/OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md
  shared: []
  read_only: []
modules_touched:
  - OTS future gameplay roadmap
  - OTS gameplay proposal classification
  - OTS vocation/class role and balance framework
  - OTS Gem Atelier and gem progression review
reuses:
  - Character markers on minimap
  - Better Map UX
  - Party Finder 2.0
  - Loot System Rework
  - Equipment Presets
  - Financial & Trading System 2.0
  - Bounty and Weekly Tasks Rework
  - official Tibia Gem Atelier / Fragment Workshop foundation
  - open PR #794 equipment progression design as read-only conceptual coordination
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — OTS Social, Itemization and QoL Roadmap

## Status

READY — user-approved 2026-07-23 future gameplay directions are persisted and classified in PR #799, including Vocation/Class Identity, Roles and Balance plus a dedicated Gem Atelier / Fragment Workshop review mandate. Documentation/design only; exact-final CI and ownership validation remain the merge gate.

## Goal

Persist the user-approved future OTS design directions discussed on 2026-07-23 around world/social map UX, privacy-aware contacts, party UX/accounting, itemization/build testing, inventory/storage, market/trade, slot-based Imbuement System 2.0, explicit vocation/class identity and balance definitions, and a full Gem Atelier / gem progression audit integrated with build and economy analysis.

## Scope

Documentation/design only. No gameplay runtime, protocol, datapack, map, binary, economy configuration, client binary, or production behavior changes.

## Context routes

- agent-governance
- real-tibia-parity (classification/baseline cautions only where an existing Tibia mechanic is being extended or reviewed)
- cross-repo (future Canary/OTClient design surface only; no cross-repo write)

## Reuse / overlap policy

- Extend existing `Character markers on minimap`, `Party Finder 2.0`, `Loot System Rework`, `Equipment Presets`, `Better Map UX`, `Bank/Trade`, and Bounty/Weekly concepts where applicable instead of creating duplicate parallel systems.
- New proposal names are used only for genuinely broader systems or missing sub-systems.
- Existing Tibia foundations are classified as `TIBIA-BASELINE`/`TIBIA-OFFICIAL` only when suitable evidence exists; implementation support in Canary/OTClient remains separately verifiable.
- Vocation/class roles are formalized as product expectations only; no final current-vocation role assignment or numeric balance values are invented before implementation-time audit.
- Gem Atelier / Fragment Workshop is treated as an official Tibia foundation requiring parity/support audit and balance integration, not as an OTS-original invention.
- Open PR #794 has conceptual overlap around equipment progression; this task does not edit its owned file and records only the need to reconcile system responsibilities before implementation.

## Acceptance criteria

- [x] Record the approved social/itemization/QoL design directions in a durable detailed design file.
- [x] Add concise integration entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` without duplicating existing systems.
- [x] Add explicit `ORIGIN` and `TYPE` entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md` for promoted proposals and official-system review mandates.
- [x] Add a durable Vocation/Class Identity, Roles and Balance Framework with explicit solo/party/context balance principles.
- [x] Classify the vocation/class balance proposals without introducing unsupported `TIBIA-OFFICIAL` claims.
- [x] Add a durable Gem Atelier / Fragment Workshop review record grounded in current official Tibia documentation.
- [x] Classify Gem Atelier / Fragment Workshop review as `TIBIA-OFFICIAL` / `PARITY-INTEGRATION`, while keeping Canary/OTClient implementation support explicitly unproven until audit.
- [x] Record required Canary/OTClient parity audit, build/balance integration, RNG review and economy analysis for gems without inventing current fork support.
- [x] Preserve open balance questions rather than inventing final numeric contracts.
- [x] Keep all changes documentation-only.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T16:55:00+02:00"
head: "0af0302bc88118cc5565365c49e99f7b669c66de"
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
  - "docs/ai-agent/OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md"
proven:
  - "The existing roadmap already contained Character markers on minimap, Party Finder 2.0, Loot System Rework, Equipment Presets references, Better Map UX, Bank/Trade systems and Bounty/Weekly redesign entries; the new sections extend those concepts instead of creating parallel duplicates."
  - "docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md contains the detailed user-approved design record for world/social map, Friends/VIP privacy, active Party 2.0, party combat visibility/accounting, Itemization & Build 2.0, Training Arena, Inventory/Depot/Stash 2.0, Market/Trade additions and Imbuement System 2.0."
  - "docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md defines the required class/vocation identity contract, shared role taxonomy, solo versus party viability principles, multi-dimensional target bands, progression-band analysis, separate PvE/boss/PvP contexts, build dependencies, telemetry and balance governance."
  - "docs/ai-agent/OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md records the full Gem Atelier / Fragment Workshop audit mandate, current official baseline, required Canary/OTClient support audit, build/class balance integration, RNG review, economy analysis and interaction with open PR #794."
  - "Current official Tibia Game Guides verified Gem Atelier as a Wheel of Destiny subsystem with Lesser/Regular/Greater vocation gems, domain affinity, vessels/Vessel Resonance, locking/dismantling and Fragment Workshop Grade I-IV mod progression using gold and fragments; exact values remain time-sensitive."
  - "A narrow repository search did not return direct Gem Atelier/Wheel matches, but that is explicitly insufficient evidence to claim current Canary/OTClient support is absent."
  - "OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md now continues through entry 94; entry 94 classifies the Gem Atelier & Fragment Workshop parity/balance review as TIBIA-OFFICIAL / PARITY-INTEGRATION, while later custom changes must receive separate classifications."
  - "The classification diff was rechecked after correcting one transient unintended wording change to existing entry 39; no existing classification note remains intentionally modified beyond the purpose-link expansion."
  - "The vocation framework deliberately avoids assigning speculative final numeric values or unsupported current-vocation mechanics before implementation-time audit."
  - "OTS_FUTURE_GAMEPLAY_SYSTEMS.md contains concise sections 29-35 integrating the social/itemization/QoL directions and dependency-map addendum."
  - "The feature scope remains documentation-only."
  - "PR #799 targets blakinio/canary:main from blakinio/canary:docs/ots-social-itemization-qol-20260723."
derived:
  - "Class/vocation definitions should become an upstream design dependency for Party System 2.0, Itemization & Build System 2.0, Imbuement System 2.0, Gem Atelier balance analysis, Build Impact Calculator and Training Arena work."
  - "Balance should use role-appropriate target bands rather than forcing identical DPS or a rigid hard-trinity composition."
  - "Gem Atelier cannot be balanced independently from Wheel/Revelation progression, vocation identity, build tooling and economy sinks."
  - "Open PR #794 and the Gem/Imbuement/build proposals require explicit responsibility mapping before implementation to avoid overlapping generic progression layers."
unknown:
  - "Exact current Tibia/Canary/OTClient parity for every Imbuement, Gem Atelier and vocation/class detail remains implementation-time work."
  - "Exact current Canary and maintained-OTClient Gem Atelier, Fragment Workshop, vessel, resonance, gem persistence and protocol/UI implementation coverage is unknown."
  - "Exact per-vocation identity, role assignment and numeric target bands remain open until each supported vocation/class is audited."
  - "Exact gem drop probabilities, complete current 2026 mod catalogue and current numeric mod/mitigation values must be reverified immediately before implementation."
  - "Exact slot-level Imbuement progression, active-channel counts, elemental attunement strength, lifecycle and economy costs remain open balance contracts."
  - "Exact privacy/PvP information-leak rules for live social tracking remain open."
  - "Exact TC/alternative-currency legal, accounting, protocol and abuse constraints remain open."
  - "Exact party accounting settlement mechanism and whether transfers are automatic or calculation-only remains open."
conflicts: []
first_failure:
  marker: "ownership-checkpoint-format"
  evidence: "Earlier Agent Task Ownership run 30012290185 reported that the context checkpoint lacked a fenced YAML block; the task record was repaired before later roadmap extensions."
rejected_hypotheses:
  - "A new parallel Party Finder is required."
  - "A new generic item rarity system should replace existing item classification/Forge foundations."
  - "Elemental Imbuements must permanently compete with all Crit/Leech/Skill active channels in the proposed redesign."
  - "Balanced vocations/classes must all have identical DPS."
  - "Every group activity must be forced into a rigid tank/healer/DPS composition."
  - "Gem Atelier should be treated as an OTS-original system."
  - "A narrow zero-result code search proves that Gem Atelier is absent from Canary/OTClient."
changed_paths:
  - "docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md"
  - "docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md"
  - "docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md"
  - "docs/ai-agent/OTS_VOCATION_ROLE_AND_BALANCE_FRAMEWORK.md"
  - "docs/ai-agent/OTS_GEM_ATELIER_AND_GEM_PROGRESSION_REVIEW.md"
validation:
  - command: "Connector diff review before Gem Atelier extension"
    result: PASS
    evidence: "The existing social/itemization/QoL plus vocation scope was documentation-only."
  - command: "Official Tibia Gem Atelier / Fragment Workshop evidence review"
    result: PASS
    evidence: "Current official Game Guides and official update history support the recorded baseline: vocation-linked gems, sizes/mods, domains, vessels/resonance, locking/dismantling, fragments and Grade I-IV Fragment Workshop progression."
  - command: "Gem Atelier classification/provenance review"
    result: PASS
    evidence: "Entry 94 treats the review as TIBIA-OFFICIAL / PARITY-INTEGRATION and explicitly separates later OTS changes from official behavior."
  - command: "Classification diff review"
    result: PASS
    evidence: "Existing entry 39 wording restored; intended classification changes are purpose-link expansion plus entries 69-94 added by this task."
blockers:
  - "Exact-final Agent Task Ownership, AI Agent Tools and CI runs for the newest head must pass before merge."
next_action: "Make no further feature-content commits. Verify exact-final PR #799 workflow results and review threads; if required checks are green and the autonomous merge gate is satisfied, mark ready and squash-merge."
```