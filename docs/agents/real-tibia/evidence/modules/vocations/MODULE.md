# Vocations evidence dossier

## Status and scope

- Module: `vocations`.
- Pilot: RTEC-002.
- Current Canary baseline: `930e0a15767b7e5348bb36c679fa5e458a76f184`.
- Official-source verification date: `2026-07-25`.
- Strongest current maturity: official identity `definition-found`; current Canary registry `registration-proven`; runtime application `UNKNOWN`.

This dossier covers the shared vocation registry, base/promoted identity, the official current HP/mana/capacity gain table, promotion titles, the current Canary XML representation and the exact source paths that load and query those definitions.

It excludes combat formula parity, spells, weapons, Wheel of Destiny and gem behavior, client presentation, protocol serialization, persistence, premium/promotion purchase rules, map/NPC content and physical-client execution.

## Official purpose and player-visible outcomes

The current official manual describes vocations as character professions selected after level 8. It identifies Druid, Knight, Monk, Paladin and Sorcerer and publishes their base per-level HP, mana and capacity gains plus promotion titles.

The dossier does not infer hidden formulas from that player-facing description.

## Actors and ownership boundaries

- **Player:** selects and plays a vocation and may later obtain its promotion.
- **Official Tibia material:** authority for current public vocation identity, public gain table, promotion names and Monk chronology.
- **Current Canary source/XML:** authority only for the exact implementation definitions at the pinned commit.
- **Feature owner:** owns controlled runtime proof for level advancement and promotion application.
- **RTEC Collector:** owns only this dossier, evidence records, deterministic indexes and the request contract.

## Inputs, outputs and preconditions

### Definition inputs

- `data/XML/vocations.xml`;
- `Vocations::loadFromXml()`;
- `Vocations::getPromotedVocation()`;
- current official manual sections 5.1.6 and 5.1.9.

### Definition outputs

The source model exposes vocation IDs, client/base IDs, names, descriptions, growth and regeneration parameters, skill/mana multipliers, promotion relationships and selected combat/Wheel-adjacent fields. Only the bounded identity/gain/promotion subset is compared here.

### Preconditions

- the exact Canary commit is available;
- the XML file is parsed successfully;
- a consumer requests an existing vocation ID or promotion relationship.

Runtime satisfaction of those preconditions is not proven by this dossier.

## States and transitions

The source-defined registry lifecycle is:

1. **unloaded**;
2. `loadFromXml()` attempts to parse `CORE_DIRECTORY/XML/vocations.xml`;
3. **loaded definitions** when parsing completes;
4. `reload()` clears the registry and invokes the loader again;
5. lookups return a configured entry or no entry;
6. promotion lookup searches for a distinct entry whose `fromVocation` equals the base ID.

Controlled execution of these transitions is not part of Collector evidence. See `BEHAVIOR_MODEL.md` and `RTREQ-FEATURE-VOCATIONS-0001`.

## Bounded factual values

| Base vocation | Official HP/mana/cap gain | Canary XML HP/mana/cap gain | Promotion |
|---|---:|---:|---|
| Druid | 5 / 30 / 10 | 5 / 30 / 10 | Elder Druid |
| Knight | 15 / 5 / 25 | 15 / 5 / 25 | Elite Knight |
| Monk | 10 / 10 / 25 | 10 / 10 / 25 | Exalted Monk |
| Paladin | 10 / 15 / 20 | 10 / 15 / 20 | Royal Paladin |
| Sorcerer | 5 / 30 / 10 | 5 / 30 / 10 | Master Sorcerer |

The loader multiplies XML `gaincap` by 100 for the internal representation. The table proves static source correspondence only.

## Time, cooldown and server-save behavior

- The selected official table does not define server-save behavior.
- Current source contains regeneration and attack tick fields, but this pilot does not compare their official values or execute them.
- No cooldown, restart, save or rollback claim is made.

## Account, character and world scope

A vocation is represented as character-facing configuration. The selected sources do not establish account-wide or world-specific variation. Persistence of vocation and promotion state is outside this pilot.

## Persistence, migration and exactly-once behavior

`UNKNOWN` for this dossier. No database schema, save/load path, migration, retry or exactly-once evidence was selected.

## Protocol and client interpretation

`not-assessed`. Client IDs exist in the XML and header contract, but this pilot does not prove packet fields, capability gates, UI behavior or maintained-client compatibility.

## Dependencies and interactions

The canonical registry gives `vocations` no hard dependency edge. Descriptive interactions remain with:

- `character-progression`;
- `combat`;
- `spells`;
- `weapon-proficiency`;
- `wheel-of-destiny`.

Those modules are not absorbed by this dossier.

## Concurrency and multi-client behavior

`UNKNOWN`. The source registry is process-local; no concurrent reload, multiple-process or multi-client result is selected.

## Failure, disconnect, relog and restart behavior

- Missing XML or parse failure returns failure from the loader.
- Missing vocation lookup returns no entry.
- The consequences for startup, live reload, logged-in players, reconnect, restart and rollback remain untested here.

## Security and authorization

No authorization decision is owned by the registry evidence selected here. Promotion eligibility, payment, entitlement and command/NPC authorization remain outside scope.

## Version timeline

- 2025-02-10: official Monk announcement.
- 2025-04-08: official Monk release.
- 2026-07-25: current official five-vocation manual verified.
- `930e0a15767b7e5348bb36c679fa5e458a76f184`: current Canary vocation source/XML snapshot observed.

See `VERSION_HISTORY.yaml` for separate version axes and proof boundaries.

## Current Canary comparison

- The five base HP/mana/capacity triples match the current official manual table at the static definition layer.
- The five base-to-promoted names/relationships match the current official table at the static definition layer.
- Canary additionally contains many parameters not assessed by this comparison.
- No runtime level-up or promotion application result exists in the selected corpus.

## Evidence gaps and owner request

`RTREQ-FEATURE-VOCATIONS-0001` asks the feature owner for one controlled behavior-level result on the exact Canary baseline. It is non-blocking for completing the evidence pilot but blocks any runtime/parity promotion of the corresponding claim.

## Decisions and rejected alternatives

See `DECISIONS.md`. The pilot deliberately rejects broad combat, spell, Wheel, protocol and persistence comparison.

## Maturity by dimension

| Dimension | Maturity | Evidence |
|---|---|---|
| official feature identity | `definition-found` | `RT-VOCATIONS-0001` |
| historical version | `definition-found` | `RT-VOCATIONS-0002` |
| current Canary registry | `registration-proven` | `RT-VOCATIONS-0003` |
| static official/Canary comparison | `registration-proven` | `RT-VOCATIONS-0004` |
| runtime level gain/promotion application | `UNKNOWN` | `RT-VOCATIONS-0005`, owner request |

## Nonclaims

This dossier does not prove complete vocation gameplay, full Real Tibia parity, runtime level-up correctness, promotion authorization, persistence, protocol/client compatibility, combat balance, spell/weapon eligibility, Wheel behavior, physical-client behavior or release readiness.
