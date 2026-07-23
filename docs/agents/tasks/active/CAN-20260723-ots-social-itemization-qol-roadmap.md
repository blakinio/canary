# CAN-20260723-ots-social-itemization-qol-roadmap

## Status

ready

## Goal

Persist the user-approved future OTS design directions discussed on 2026-07-23 around world/social map UX, privacy-aware contacts, party UX/accounting, itemization/build testing, inventory/storage, market/trade, and a slot-based Imbuement System 2.0.

## Scope

Documentation/design only. No gameplay runtime, protocol, datapack, map, binary, economy configuration, client binary, or production behavior changes.

## Context routes

- agent-governance
- real-tibia-parity (classification/baseline cautions only where an existing Tibia mechanic is being extended)
- cross-repo (future Canary/OTClient design surface only; no cross-repo write)

## Owned paths

- `docs/agents/tasks/active/CAN-20260723-ots-social-itemization-qol-roadmap.md`
- `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md`
- `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md`
- `docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md`

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

### PROVEN

- `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` already contained `Character markers on minimap`, `Party Finder 2.0`, `Loot System Rework`, `Equipment Presets` references, `Better Map UX`, Bank/Trade systems, and Bounty/Weekly redesign entries; the new roadmap sections extend those concepts rather than introducing parallel duplicates.
- `docs/ai-agent/OTS_SOCIAL_ITEMIZATION_AND_QOL_SYSTEMS.md` now contains the detailed user-approved design record for world/social map, Friends/VIP privacy, active Party 2.0, party combat visibility/accounting, Itemization & Build 2.0, Training Arena, Inventory/Depot/Stash 2.0, Market/Trade additions and Imbuement System 2.0.
- `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` now contains concise sections 29-35 integrating the new directions and dependency-map addendum.
- `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md` now continues the authoritative proposal index with entries 69-88 and explicit `ORIGIN`/`TYPE` classifications.
- Classification deliberately uses `MIXED`/`OUR-DESIGN` where the design combines an existing Tibia foundation with our custom direction; no new `TIBIA-OFFICIAL` claims were introduced without a dedicated parity proof.
- The final diff is documentation-only: one active task record, one new detailed design record, and narrow roadmap/classification updates.
- The branch was created from `blakinio/canary:main`; PR #799 targets `blakinio/canary:main` from `blakinio/canary:docs/ots-social-itemization-qol-20260723`.
- Main advanced after branch creation by three commits, but the intervening main changes do not touch any owned path in this task; PR mergeability/CI remains the final live-state gate.
- `ci:final-gate` was applied before this final checkpoint commit.

### USER-DIRECTION PERSISTED

- full/interactive world map with POIs, filters, search and navigation;
- live party/guild/friend/VIP map markers with consent/privacy controls;
- shared discovery markers for Echo Raid, Fiendish and similar discoveries;
- mutual/permissioned Friends/VIP model to prevent unilateral tracking;
- Party System 2.0: clearer combat visibility, party UI, roles/bonuses review and shared hunt accounting;
- automatic party loot/supply/profit ledger to remove manual hunt settlements;
- Itemization & Build System 2.0 with build impact comparison and practical Training Arena tests;
- Inventory/Depot/Stash 2.0 with global search, smart containers, sorting, reservations and task-item protection;
- Market/Trade 2.0 additions: no listing fee, commission on completed sale, multi-currency offers including TC, and high-value item support;
- Imbuement System 2.0 redesign around equipment-slot libraries/profiles, active-channel limits defined by equipped items, separate elemental attunement, optional slot progression/automation, effective-use lifecycle, build-preset integration, and recurring progression/maintenance gold sinks.

### OPEN

- exact slot-level progression, maximum active channels, elemental attunement strength, timer/charge lifecycle and economic costs;
- current Tibia/Canary/OTClient parity for every Imbuement detail before implementation;
- privacy, PvP and information-leak rules for live map/social tracking;
- TC/alternative-currency economic, legal/accounting and protocol constraints;
- exact party accounting settlement mechanism and whether transfers are automatic or merely calculated.

### Validation

- Connector diff review: 4 expected documentation paths only.
- Roadmap diff: one purpose-line adjustment plus appended sections 29-35; no unrelated roadmap sections removed.
- Classification diff: purpose link plus entries 69-88; existing entries 1-68 preserved.
- No runtime/build tests are applicable to this documentation-only change; required GitHub CI on the final head is still authoritative.

### next_action

Verify PR #799 current-head CI, mergeability and review-thread state; if required checks are green and the autonomous merge gate is satisfied, mark ready and squash-merge without another commit.
