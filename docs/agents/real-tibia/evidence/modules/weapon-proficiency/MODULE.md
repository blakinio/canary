# Weapon Proficiency evidence dossier

## Status and scope

- Module: `weapon-proficiency`.
- Campaign: RTEC-004 wave 1.
- Canary baseline: `124b029d1a2498a64fa6612b16efa386b8786a83`.
- Maintained OTClient search baseline: `226289a7d99f5f1b787c3b3eea627b4fa55c0b46`.
- Official-source verification date: `2026-07-25`.
- Strongest current maturity: official feature identity `definition-found`; selected Canary static-tree runtime path `runtime-path-proven`; manipulation and character-switch conformance unproven.

This package covers only the Summer Update 2026 weapon-proficiency manipulation feature, the selected current Canary static-tree/per-weapon KV implementation, and the official 2026-07-14 pending-level-up character-switch fix.

It excludes gameplay implementation, formulas, randomisation probabilities, packet layout, maintained-client UI implementation, database durability tests, physical-client execution, achievements beyond existing pointers, combat balance and broad weapon data parity.

## Official behavior

The official 2026 feature definition permits modification of up to two perk slots per weapon. The first and second slots have different progression and dust requirements. A modified effect can be refined, maximised, reshaped or cleared, and changes are restricted to protection zones. The Summer Update 2026 release announcement confirms the manipulation feature was released on 2026-07-13.

These statements establish public feature identity and visible rules only.

## Current Canary source model

At the pinned commit, the selected canonical module:

- loads static per-level perk choices from `data/items/proficiencies.json`;
- stores experience, mastery and selected original-tree perks in player-scoped, per-weapon KV state;
- validates weapon, unlocked level and perk index;
- retains at most one valid selected original-tree perk per level;
- normalises stored selections against current definitions;
- applies validated selected perks through production code.

The selected component does not define modified-slot state, dust costs, random rolled replacement effects, refinement levels, maximisation items, reshaping choices or clearing of a modified slot. This is a bounded selected-path comparison, not an absolute repository-wide absence claim.

## Character-switch isolation

The official 2026-07-14 fix states that a pending weapon-proficiency level-up had been displayed for other characters after switching characters. The selected server component is Player-owned and emits proficiency updates, but that fact does not prove maintained-client pending-notification ownership or reset behavior. No controlled character-switch result is present in this dossier.

## Persistence and recovery

Source tracing proves that the selected component serialises per-weapon state into a player-scoped `weapon-proficiency` KV namespace and normalises loaded data. It does not prove database commit timing, restart/relog round trips, concurrent writers, rollback or corruption recovery under execution.

## Protocol and client

No exact maintained-client symbol, packet field or retained client result was identified by the bounded search. Protocol and client interpretation remain `UNKNOWN`.

## Evidence records

| ID | Claim | State | Proof |
|---|---|---|---|
| `RT-WEAPON-PROFICIENCY-0001` | official manipulation lifecycle | `PROVEN` | `definition-found` |
| `RT-WEAPON-PROFICIENCY-0002` | current Canary static tree and KV runtime path | `PROVEN` | `runtime-path-proven` |
| `RT-WEAPON-PROFICIENCY-0003` | pending level-up character-switch isolation | `UNKNOWN` | `definition-found` |

## Nonclaims

This dossier does not prove complete weapon-proficiency parity, manipulation support in Canary, live KV durability, client UI isolation, exact protocol compatibility, gameplay behavior, physical-client behavior or release readiness.
