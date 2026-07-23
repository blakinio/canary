# CAN-20260723-ots-social-itemization-qol-roadmap

## Status

active

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

- Record the approved design directions in a durable detailed design file.
- Add concise integration entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` without duplicating existing systems.
- Add explicit `ORIGIN` and `TYPE` entries to `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md`.
- Preserve open balance questions rather than inventing final numeric contracts.
- Keep all changes documentation-only.

## Context checkpoint

### PROVEN

- `OTS_FUTURE_GAMEPLAY_SYSTEMS.md` already contains `Character markers on minimap`, `Party Finder 2.0`, `Loot System Rework`, `Equipment Presets` references, `Better Map UX`, Bank/Trade systems, and Bounty/Weekly redesign entries.
- `OTS_FUTURE_GAMEPLAY_SYSTEMS_CLASSIFICATION.md` currently classifies proposals 1-68; new accepted proposals must continue the index without reclassifying unrelated existing entries.
- No open PR matching `OTS_FUTURE_GAMEPLAY_SYSTEMS` was found during task preflight.

### USER-DIRECTION TO PERSIST

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

### next_action

Create the detailed design record, integrate concise roadmap entries, update proposal classification, review the final diff, and keep the PR documentation-only.
