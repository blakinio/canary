# TSD-004 — Cyclopedia Family Decomposition

> Status: bounded inventory for `blakinio/canary`.
> Task-start main: `9f82f93977e82784370961a72104efacd497c8e0`.
> Maintained OpenTibiaBR OTClient evidence observed at `bdea0b23b4a738809d698cb7e4f88a299dd6bffc`.
> This report is decision evidence for the canonical registry. It is not a second registry and does not prove gameplay, persistence, protocol or client correctness.

## Result

TSD-004 preserves `cyclopedia` as the broad compatibility/discovery umbrella and adds only four durable child boundaries supported by independent current implementation roots.

- Registry records before: **35**.
- New records: **4**.
- Registry records after: **39**.
- Existing module records modified: **0**.
- Category/schema/generator/mapper/workflow changes: **none**.
- Runtime/gameplay/database/protocol/client/map/asset changes: **none**.

Records added:

1. `bestiary`;
2. `bosstiary`;
3. `cyclopedia-character`;
4. `titles`.

Stable existing records preserved unchanged:

- `cyclopedia`;
- `charms`;
- `houses`;
- `achievements`;
- `protocol`;
- `character-lifecycle`;
- `character-progression`;
- `player-persistence`.

## Preflight and ownership

The task started from `main@9f82f93977e82784370961a72104efacd497c8e0` after TSD-003 feature and lifecycle merge.

Open PRs inspected:

| PR | Active area | TSD-004 treatment |
|---|---|---|
| #316 | bounded Targuna donor/map/content evidence | read-only; no map, OTBM, quest, NPC, monster, spawn or house-source edit |
| #245 | shared physical-client E2E platform | read-only; no scenario, driver or orchestrator edit |

OpenTibiaBR Canary and maintained OTClient remain read-only evidence sources. No upstream write, source copy or cross-repository contract change is authorized. `ACTIVE_WORK.md` remains read-only.

## Existing umbrella and child records

### `cyclopedia`

The existing record already covers the broad family and intentionally has wide server, protocol, player and client path hints. It remains the compatibility/discovery umbrella because:

- client navigation and protocol request/response surfaces cross all tabs;
- some server implementation still shares protocol and Player roots;
- stable existing ID compatibility is more valuable than replacing the umbrella;
- overlapping narrow child records are supported by current many-to-many lookup and source-role mapping.

TSD-004 does not edit its path hints, maturity or dependency edges.

### `charms`

Charms already has an independent record for definitions, costs, unlock state, assignment and combat effects. Although `IOBestiary` hosts Charm helper methods, TSD-004 does not merge Charms back into Bestiary and does not duplicate the record.

### `houses`

Houses already has a durable world/persistence lifecycle. The Cyclopedia house tab is a presentation/protocol view over that existing module, not a second house domain.

## Current implementation evidence

### Bestiary

`src/io/iobestiary.*` exposes a durable Bestiary lifecycle including:

- monster kill attribution;
- kill-status and unlock-stage calculations;
- Bestiary race lookup and unlocked counts;
- completed and stage-two creature lists;
- Charm-point and minor-echo rewards;
- the contract through which Bestiary progress feeds Charm use.

The same class also hosts Charm purchase/assignment/combat helpers. That implementation overlap does not transfer ownership: the existing `charms` record remains responsible for Charm definitions, unlocks, assignment and combat-effect lifecycle.

The maintained client has a dedicated `modules/game_cyclopedia/tab/bestiary/**` surface. This path is a discovery contract only and does not prove packet or rendering correctness.

All active monster files remain evidence inputs to the existing validator rather than Bestiary ownership paths. Claiming `data/monster/**` or `data-otservbr-global/monster/**` would make routine creature edits falsely look owned by this narrow module.

### Bosstiary

`src/io/io_bosstiary.*` exposes an independent lifecycle:

- boss race registry;
- Bane/Archfoe/Nemesis stage thresholds and points;
- boosted-boss load and identity state;
- boss kill tracking and completed lists;
- boss points and loot-bonus calculations;
- boss-slot level and removal-cost calculations.

The maintained client has a dedicated `modules/game_cyclopedia/tab/bosstiary/**` surface that requests and displays Bosstiary state.

Generic boss combat, encounter scheduling, rewards and monster definitions remain future creature/encounter package responsibilities. Podium presentation is not claimed as Bosstiary ownership.

### Cyclopedia Character

`src/creatures/players/components/player_cyclopedia.*` is an independent player component for:

- character summary values;
- death-history pagination;
- recent-kill pagination;
- KV-backed store-summary amounts and result maps.

The maintained client has a dedicated `modules/game_cyclopedia/tab/character/**` surface. The record excludes generic character load/save, progression formulas and title ownership even though those systems feed or share the tab.

### Titles

`src/creatures/players/components/player_title.*` has its own durable state and lifecycle:

- title definitions and sex-specific names;
- unlock, removal and current-title selection;
- KV-backed unlocked-title persistence;
- title refresh and cross-domain condition checks.

Cross-domain checks include level, highscore, Bestiary/Bosstiary, map, task, mount, outfit, gold and login streak. These are inputs to title eligibility, not ownership transfers from the underlying systems.

Titles intentionally shares the maintained-client character-tab path with `cyclopedia-character`. The current registry supports overlapping verified path hints, and `depends_on` is not used as a hierarchy substitute.

## Candidate decisions

| Candidate | Decision | Result / reason |
|---|---|---|
| `cyclopedia` | `KEEP_AS_UMBRELLA` | stable broad server/protocol/client family identity remains unchanged |
| `cyclopedia-items` | `MERGE_WITH_ANOTHER_MODULE` | item browsing is a Cyclopedia/protocol/client surface; generic item lifecycle belongs to TSD-007 |
| `bestiary` | `ADD_NOW` | independent kill, unlock-stage, race and completion progression lifecycle |
| `charms` | `ALREADY_COVERED` | preserve existing independent record |
| `bosstiary` | `ADD_NOW` | independent rarity-stage, point, boosted-boss, slot and loot-bonus lifecycle |
| `cyclopedia-map` | `MERGE_WITH_ANOTHER_MODULE` | map reveal/view is a Cyclopedia/protocol/client surface; world/map mechanics belong to TSD-008 |
| `cyclopedia-character` | `ADD_NOW` | independent summary/history/KV component and client tab |
| `titles` | `ADD_NOW` | independent definition, unlock, selection and persistence lifecycle |
| `cyclopedia-houses` | `ALREADY_COVERED` | existing `houses` owns house lifecycle; Cyclopedia tab remains presentation/protocol interaction |
| `outfits` | `DEFER_TO_NEXT_PACKAGE` | appearance definition/unlock lifecycle not owned by the Character tab |
| `mounts` | `DEFER_TO_NEXT_PACKAGE` | appearance definition/unlock lifecycle not owned by the Character tab |
| `familiars` | `DEFER_TO_NEXT_PACKAGE` | vocation/appearance/client boundary needs later inventory |
| `podiums-displays` | `MERGE_WITH_ANOTHER_MODULE` | presentation capability spanning Bosstiary/appearance/client; no independent current server root established |

## Relationships

Only fundamental implementation/discovery dependencies are encoded:

- `bestiary` depends on `cyclopedia` and `player-persistence`;
- `bosstiary` depends on `cyclopedia` and `player-persistence`;
- `cyclopedia-character` depends on `cyclopedia` and `player-persistence`;
- `titles` depends on `cyclopedia-character` and `player-persistence`.

Other links are descriptive `interacts_with`. In particular:

- Bestiary interacts with Charms, combat, protocol, spawns and Titles;
- Bosstiary interacts with protocol, spawns and Titles;
- Cyclopedia Character interacts with character lifecycle/progression, protocol and Titles;
- Titles interacts with achievements, Bestiary, Bosstiary, character progression, houses and protocol.

The dependency graph remains acyclic. Existing umbrella relationships are not rewritten.

## Maturity

All four records start at:

```text
lifecycle: inventory
implementation: inventory
evidence: inventory
persistence: not-assessed
protocol: not-assessed
automated_tests: not-assessed
runtime_validation: not-assessed
gameplay_e2e: not-assessed
```

The existing Cyclopedia validator, source-contract regressions and previously merged fixes remain evidence pointers. A new decomposition record does not inherit audited, runtime or E2E maturity automatically.

## Discovery boundaries

New path hints are deliberately narrow:

```text
src/io/iobestiary.*
  → bestiary

src/io/io_bosstiary.*
  → bosstiary

src/creatures/players/components/player_cyclopedia.*
  → cyclopedia-character

src/creatures/players/components/player_title.*
  → titles

modules/game_cyclopedia/tab/bestiary/**
  → bestiary (client source only)

modules/game_cyclopedia/tab/bosstiary/**
  → bosstiary (client source only)

modules/game_cyclopedia/tab/character/**
  → cyclopedia-character and titles (client source only)
```

Expected broad/narrow overlap is preserved:

- Bestiary/Bosstiary/Character/Title server paths may also match the broad `cyclopedia`, `player-persistence` or protocol-related records where existing hints apply;
- source-role-aware server mapping must exclude client-only paths;
- source-role-aware client mapping may use the narrow tab paths;
- path matches remain discovery and never edit authorization;
- unmapped paths and review decisions remain explicit and deterministic.

## Existing validator reuse

TSD-004 reuses the existing `tools/ai-agent/cyclopedia_validation.py` and its tests, workflow, report and runtime plan. It creates no second scanner.

That validator separates seven evidence domains:

1. items;
2. Bestiary;
3. Charms;
4. Bosstiary;
5. map;
6. character/titles;
7. houses.

Validator domain separation is evidence organization, not automatic module creation. TSD-004 creates records only where current source shows an independent durable lifecycle.

## Evidence limits

TSD-004 does **not** prove:

- Bestiary or Bosstiary ID uniqueness across all runtime data;
- kill-stage, Charm-point, boss-point, loot-bonus or removal-cost parity;
- boosted-boss initialization or recovery behavior;
- persistence completeness, atomicity, relog correctness or crash safety;
- title definitions, thresholds, permanence or unlock correctness;
- item/map/house presentation correctness;
- Canary ↔ maintained-OTClient packet compatibility;
- maintained-client parsing, rendering or UI behavior;
- runtime behavior or physical-client E2E;
- Real Tibia parity;
- Oteryn migration readiness.

## Next package

After feature merge and a separate lifecycle archive, TSD-005 must start from then-current `main`:

```text
task: CAN-20260714-tibia-system-decomposition-combat-weapons-vocations
package: TSD-005
branch: docs/tibia-system-decomposition-combat-weapons-vocations
```

TSD-005 should preserve `combat`, `spells`, `vocations` and `weapon-proficiency` records and split only durable targeting, permission, formula, mitigation, condition, weapon and vocation-combat boundaries supported by independent current implementation roots.
