# OTS Future Gameplay Systems — Origin and Type Classification

## Purpose

Authoritative classification index for proposals recorded in `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md` and the detailed `docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md` design record.

This index exists to prevent three recurring mistakes:

1. describing an original-Tibia feature as an OTS invention;
2. describing an OTS-inspired extension as if the whole underlying system were custom;
3. treating our own design direction as proof that Canary, OTClient or current Tibia already implements it.

## Classification rules

### ORIGIN

- `TIBIA-OFFICIAL`: explicitly verified as an original/current Tibia system in a dedicated parity check.
- `TIBIA-BASELINE`: proposal builds on a known Tibia mechanic/system, but exact current-Tibia parity must still be reverified before implementation.
- `OTS-INSPIRED`: a specific design direction came from analysis of another OTS. Only the evidenced extension is attributed to the OTS, not the underlying Tibia system.
- `OUR-DESIGN`: created or selected in the user's OTS product-design discussion.
- `EXTERNAL-TOOLING`: client/web/agent/security tooling rather than a native gameplay-system origin.
- `MIXED`: combines two or more of the above.

### TYPE

- `TIBIA-EXTENSION`: changes or expands an original Tibia mechanic.
- `HYBRID`: combines an existing Tibia foundation with substantial custom gameplay/UX behavior.
- `FULLY-CUSTOM`: standalone gameplay system not treated as an original Tibia baseline feature.
- `CLIENT-UX`: primarily client/interface/presentation behavior.
- `EXTERNAL-SECURITY`: telemetry, AI analysis, anti-cheat or operational security layer.
- `META-ECONOMY`: economy-wide framework rather than one isolated gameplay feature.
- `PARITY-INTEGRATION`: preserve, verify or integrate an existing official feature rather than inventing a duplicate.

`TIBIA-BASELINE` does **not** mean exact 2026 parity has been proven. Before implementation, current Tibia, Canary and OTClient must be reverified where relevant.

## Classified proposal index

| # | Proposal | ORIGIN | TYPE | Classification note |
|---|---|---|---|---|
| 1 | Huntfinder 2.0 | `OTS-INSPIRED` | `HYBRID` | Inspired by RubinOT-style hunt discovery/recommendation tooling layered on Tibia hunting content. |
| 2 | Hunting Spot Availability | `OUR-DESIGN` | `FULLY-CUSTOM` | Live free/probably occupied/occupied/unknown status inferred from real activity. |
| 3 | Party Finder 2.0 | `MIXED` | `TIBIA-EXTENSION` | Rework/extension of an existing party-finding concept; exact current Tibia baseline must be reverified. |
| 4 | Account-wide quest progression | `OUR-DESIGN` | `TIBIA-EXTENSION` | Changes character-centric quest persistence into selectively account-wide progression. |
| 5 | Independent auto attack and spell casting | `OUR-DESIGN` | `TIBIA-EXTENSION` | Changes combat scheduling so spell use does not cancel/reset/skip weapon auto attacks. |
| 6 | Character markers on minimap | `OUR-DESIGN` | `CLIENT-UX` | Party/guild/friend/whitelist markers with server-authoritative privacy/PvP rules where needed. |
| 7 | Loot System Rework | `MIXED` | `TIBIA-EXTENSION` | Extends Tibia loot/quick-loot foundations with Loot Nearby, Loot All, queueing, filters and destination UX. |
| 8 | Summon Loot Assistant | `OUR-DESIGN` | `HYBRID` | Extends the existing summon concept with controlled loot-assistance behavior. |
| 9 | Bank UI 2.0 | `OUR-DESIGN` | `TIBIA-EXTENSION` | Replaces chat-heavy interaction around an existing banking concept with dedicated UI. |
| 10 | Transaction History | `OUR-DESIGN` | `HYBRID` | Adds durable financial audit/history to bank and system transactions. |
| 11 | Trade System 2.0 | `OUR-DESIGN` | `TIBIA-EXTENSION` | Extends player trade to use bank balance directly and adds safer negotiation/confirmation UX. |
| 12 | Death System 2.0 | `OUR-DESIGN` | `TIBIA-EXTENSION` | Rebalances Tibia death consequences around sustainable high-level progression. |
| 13 | Recovery Pool | `OUR-DESIGN` | `HYBRID` | Custom recovery layer attached to death losses. |
| 14 | Death Fatigue / Post-Death Weakness | `OUR-DESIGN` | `HYBRID` | Moves part of death cost from permanent loss to bounded temporary penalties. |
| 15 | Connection Loss Protection | `OUR-DESIGN` | `HYBRID` | Server-side protection/compensation policy layered on Tibia combat/logout behavior. |
| 16 | Disconnect Abuse Detection | `OUR-DESIGN` | `EXTERNAL-SECURITY` | Long-term telemetry and risk scoring for suspicious disconnect patterns. |
| 17 | AI Anti-Bot / Anti-Cheat Platform | `OUR-DESIGN` | `EXTERNAL-SECURITY` | Multi-layer client integrity, server telemetry, AI behavioral analysis and cross-account graph detection. |
| 18 | PvP System 2.0 | `OUR-DESIGN` | `TIBIA-EXTENSION` | Reworks existing Tibia PvP foundations for more skill expression and less grief-driven frustration. |
| 19 | PvP rating / prestige / seasons | `MIXED` | `HYBRID` | Structured competitive progression layered over PvP; shares patterns with ranked systems in custom OTS/MMOs. |
| 20 | High-Risk PvP Zones | `OUR-DESIGN` | `HYBRID` | Opt-in zones with stronger risk/reward rules instead of applying extreme loss globally. |
| 21 | Adaptive UI / Scalable Client | `OUR-DESIGN` | `CLIENT-UX` | Modern OTClient rendering/UI direction for ultrawide, high DPI, 1440p and 4K. |
| 22 | Layout Presets | `MIXED` | `CLIENT-UX` | Hunting/boss/PvP/trading panel layouts; related to equipment/client preset inspiration but focused on UI layout. |
| 23 | Boss System 2.0 | `MIXED` | `TIBIA-EXTENSION` | Builds on original Tibia bossing while incorporating our redesign and selected current-Tibia/OTS inspiration. |
| 24 | Adventure Guild Boss Hub | `OUR-DESIGN` | `HYBRID` | Custom convenience hub that must be earned through discovery/access/mastery. |
| 25 | Flexible Boss Party Size | `OUR-DESIGN` | `TIBIA-EXTENSION` | Replaces rigid group-size expectations with controlled encounter scaling. |
| 26 | Boss Difficulty Tiers | `MIXED` | `TIBIA-EXTENSION` | Practice/normal/scalable tiers inspired partly by modern Tibia boss-system direction; exact official baseline must be reverified. |
| 27 | Personal Loot | `OUR-DESIGN` | `HYBRID` | Per-player loot resolution layered on boss encounters. |
| 28 | Bad Luck Protection / Pity | `MIXED` | `TIBIA-EXTENSION` | Selected as a boss-loot extension; current Tibia 2026 bad-luck mechanics must be reverified before parity claims. |
| 29 | Boss Essence / Guaranteed Progression | `OUR-DESIGN` | `HYBRID` | Bounded kill currency/fragments so no-drop sessions still create progress. |
| 30 | Threat-Based Monster Collision | `OUR-DESIGN` | `TIBIA-EXTENSION` | Alters existing body-blocking based on monster threat and relative player power. |
| 31 | Break Free / Emergency Breakthrough | `OUR-DESIGN` | `FULLY-CUSTOM` | Limited active escape mechanic for genuine dangerous surrounds. |
| 32 | Transition Safety | `OUR-DESIGN` | `TIBIA-EXTENSION` | Improves holes/ladders/stairs/teleports without removing meaningful combat danger. |
| 33 | Guaranteed Escape Path | `OUR-DESIGN` | `HYBRID` | Adds bounded landing-area guarantees after forced transitions. |
| 34 | Fishing System 2.0 | `OUR-DESIGN` | `TIBIA-EXTENSION` | Expands Tibia fishing into mastery, biomes, hotspots, bait and active interaction. |
| 35 | Fishing Codex / Records / Tournaments | `OUR-DESIGN` | `HYBRID` | Custom progression/social layer attached to fishing. |
| 36 | Cooking 2.0 | `OUR-DESIGN` | `HYBRID` | Expands existing food concepts into preparation/build-support crafting. |
| 37 | House Chef | `MIXED` | `HYBRID` | Expands the existing house/hireling/cook concept into an ingredient-service-recipe loop; exact current baseline must be reverified. |
| 38 | Economy Sink Framework | `OUR-DESIGN` | `META-ECONOMY` | Cross-system inflation-control strategy using desirable convenience/luxury sinks. |
| 39 | House upgrades / services / luxury sinks | `OUR-DESIGN` | `META-ECONOMY` | Optional money sinks tied to housing and prestige rather than punitive basic costs. |
| 40 | Equipment Durability | `OUR-DESIGN` | `FULLY-CUSTOM` | Optional soft maintenance system; not assumed to be original Tibia parity. |
| 41 | Repair All / Auto Repair | `OUR-DESIGN` | `HYBRID` | Convenience layer for the proposed custom durability system. |
| 42 | Skill Wheel changes outside temple without PZ/combat lock | `MIXED` | `TIBIA-EXTENSION` | Extends original Tibia skill-wheel access rules; Wheel remains an original Tibia system. |
| 43 | Skill Progression 2.0 | `MIXED` | `TIBIA-EXTENSION` | Extends classic Tibia skills/offline/exercise-training foundations so genuine gameplay is a strong progression path. |
| 44 | Real Combat Training | `OUR-DESIGN` | `TIBIA-EXTENSION` | Changes classic skill gain to consider real combat context rather than raw repetitive hit count alone. |
| 45 | Threat coefficient for classic skill gain | `OUR-DESIGN` | `HYBRID` | Relative target threat modifies Skill Progression 2.0 gain; exact formula remains open. |
| 46 | Diminishing returns on one persistent training target | `OUR-DESIGN` | `HYBRID` | Anti-AFK/anti-immortal-target layer for classic skill progression. |
| 47 | Combat Activity Score | `OUR-DESIGN` | `HYBRID` | Bounded activity signal used only to distinguish genuine combat from repetitive training; must not force unnatural play. |
| 48 | Shielding progression in real combat | `OUR-DESIGN` | `TIBIA-EXTENSION` | Extends classic Shielding progression to reward relevant incoming pressure rather than trivial AFK tanking. |
| 49 | Offline training as slower convenience path | `TIBIA-BASELINE` | `PARITY-INTEGRATION` | Keep official-style offline training as a slower bounded alternative; exact current values must be reverified. |
| 50 | Exercise weapons as faster gold-sink path | `TIBIA-BASELINE` | `PARITY-INTEGRATION` | Retain the original-Tibia exercise-training concept while balancing it against active play and economy goals. |
| 51 | Classic skills and Weapon Proficiency remain separate | `TIBIA-OFFICIAL` | `PARITY-INTEGRATION` | Do not invent a duplicate generic Weapon Mastery system. Weapon Proficiency/Mastery already exists in Tibia. |
| 52 | Natural hunts advance classic skills and Weapon Proficiency independently | `MIXED` | `PARITY-INTEGRATION` | Classic skill gain follows use/Skill Progression rules; Weapon Proficiency follows its own official-style encounter/kill progression. |
| 53 | Equipment Presets | `OTS-INSPIRED` | `HYBRID` | RubinOT-inspired whole-set switching integrated with client/action-bar behavior. |
| 54 | Linked Tasks | `OTS-INSPIRED` | `HYBRID` | RubinOT-inspired chained/repeatable progression layered over quest/task concepts. |
| 55 | Better Map UX | `OTS-INSPIRED` | `CLIENT-UX` | RubinOT-inspired map/client usability improvements; exact features require direct verification before copying. |
| 56 | Castle / Battleground | `OTS-INSPIRED` | `FULLY-CUSTOM` | Custom structured PvP/event concept inspired by RubinOT's Castle direction. |
| 57 | Prestige Arena | `OTS-INSPIRED` | `FULLY-CUSTOM` | Ranked custom PvP arena direction inspired by RubinOT's Prestige Arena. |
| 58 | Crash-aware boss cooldown compensation / Obelisk concept | `OTS-INSPIRED` | `HYBRID` | OTS-inspired operational/gameplay compensation around boss cooldowns and confirmed crashes. |

## Additional researched systems not yet promoted into the main proposal backlog

The following were discussed as potentially interesting but are **not automatically approved implementation directions** merely because another OTS uses them:

| System | ORIGIN | TYPE | Status |
|---|---|---|---|
| Faction & Reputation System 2.0 | `OTS-INSPIRED` | `HYBRID` | Candidate inspired by Medivia-style faction progression; requires separate approval before roadmap promotion. |
| Professions 2.0 | `OTS-INSPIRED` | `HYBRID` | Candidate inspired by Archlight-style professions; avoid mandatory vertical stat stacking. |
| Guild Progression 2.0 | `OTS-INSPIRED` | `HYBRID` | Candidate inspired by TibiaScape-style guild progression; prefer utility/prestige over mandatory combat power. |
| Adventurer Caravan / Expedition System | `OTS-INSPIRED` | `FULLY-CUSTOM` | Candidate inspired by RunePath-style caravan concepts. |
| Region Discovery + Quest Chains | `OTS-INSPIRED` | `HYBRID` | Candidate inspired by Tibia Relic/Medivia-style exploration-driven progression. |
| Item rarity / random affixes | `OTS-INSPIRED` | `HYBRID` | Discussed but currently low-priority/cautionary because it may undermine Tibia item identity. |
| Awakening / Prestige reset | `OTS-INSPIRED` | `FULLY-CUSTOM` | Discussed but not recommended for our unlimited-progression philosophy. |

## Weapon Proficiency special rule

`TIBIA-OFFICIAL`

Weapon Proficiency itself is **not** an OTS-original proposal. The detailed verified classification and current Canary/OTClient baseline are maintained in `docs/ai-agent/OTS_SKILL_PROGRESSION_2_0.md`.

Any future comparison with an OTS must classify only the **specific documented extension** as `OTS-INSPIRED` or `OTS-EXTENSION-CLAIM`; it must not attribute the underlying Weapon Proficiency system to that OTS.

## Maintenance policy

1. Add every newly approved gameplay proposal to this index when it is added to the roadmap.
2. Prefer `TIBIA-BASELINE` over `TIBIA-OFFICIAL` when current official behavior has not been freshly verified.
3. Promote `TIBIA-BASELINE` to `TIBIA-OFFICIAL` only with current authoritative evidence.
4. Attribute another OTS only for the specific mechanic actually evidenced.
5. Keep `ORIGIN` separate from `TYPE`: a system can be OTS-inspired while still being a Tibia extension.
6. Classification is product provenance, not implementation proof. Canary/OTClient support must be verified separately.
