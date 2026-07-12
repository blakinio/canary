# Cyclopedia Validation — evidence report

Last updated: 2026-07-12 20:59 Europe/Warsaw  
Branch: `feat/cyclopedia-validation-audit`  
PR: [#170](https://github.com/blakinio/canary/pull/170) — draft  
Reference: `https://tibia.fandom.com/wiki/Cyclopedia`

## Scope and evidence rule

This report covers Items, Bestiary, Charms, Bosstiary, Map, Character/Titles and Houses. PR #170 is read-only: it inventories active data, runtime patterns, persistence and Canary ↔ OTClient surfaces. Reference-page differences are not defects without active-code or runtime evidence.

## Automated coverage

`tools/ai-agent/cyclopedia_validation.py`:

- parses the active Charm registry and validates IDs, names, category/type and three tier arrays;
- scans only `data/monster` and `data-otservbr-global/monster`; `data-canary` is excluded;
- parses `monster.raceId`, `monster.Bestiary`, `monster.bosstiary`, thresholds, points, boss IDs and rarity;
- reports duplicate Bestiary/Bosstiary IDs for explicit semantic review;
- inventories Canary protocol declarations/definitions and maintained OTClient send/parse methods;
- records bounded source hashes;
- detects known semantic/resilience patterns without writing game data.

Focused tests cover Charm parsing, sparse IDs, tiers, Bestiary/Bosstiary parsing, thresholds, rarity, duplicates, optional race metadata, protocol matching, semantic patterns, read-only behavior and missing sources.

## Final verified full-checkout result

Verified audit code head: `741ffed81275d37fd700cacdb05cbae05a0a1356`, directly based on `main` commit `ab0ca005625ca4f80fc5931d86a3f8d0b0304299`.

Workflow run `29204136200` completed successfully. All 23 steps passed: Canary checkout, read-only maintained OTClient checkout, 9 focused tests, bytecode compilation, full scan, JSON validation, invariants, summary and artifact upload. Repository CI run `29204136318` and AI Agent Tools run `29204136186` also succeeded on the same code head.

| Metric | Result |
|---|---:|
| Cyclopedia domains | 7 |
| Active monster Lua files | 1,656 |
| Bestiary definitions | 749 |
| Bosstiary definitions | 249 |
| Charm definitions | 25 |
| Server/client declaration-definition gaps | 0 |
| Scanner findings | 18 |
| Scanner errors | 3 |
| Scanner warnings | 15 |

Verified artifact:

```text
artifact id: 8263239684
archive digest: sha256:36df08b9c52fd850f0be1e0f447d6d883e9e0b4fc798412bc6e458fd2228ac38
JSON digest: sha256:e3fad997b2c1104e221807a596e48638a4a3992ea0f85d75d4bb72bc61b8574f
```

Scanner dispositions:

```text
confirmed-runtime-defect: 2
definition-invalid: 1
definition-needs-review: 7
display-metadata-defect: 4
latent-helper-defect: 3
needs-evidence: 1
```

Two duplicate review warnings are upgraded below after reference and runtime-key analysis.

## Domain inventory

| Domain | Confirmed sources | Current disposition |
|---|---|---|
| Items | `protocolgame.*`, item inspection/price paths, OTClient Items module | static inventory; asset/runtime parity pending |
| Bestiary | active monster Lua, `src/io/iobestiary.*`, protocol and player state | full static scan complete |
| Charms | active Lua registry/helper, Bestiary runtime, `player_charms`, protocol resources | full registry scan complete |
| Bosstiary | active boss Lua, `src/io/io_bosstiary.*`, `boosted_boss`, `player_bosstiary` | full static scan complete |
| Map | enum/map-action paths and OTClient map module | static inventory; trigger/persistence proof pending |
| Character/Titles | player component, title component, death/kill tables, protocol | static query defect confirmed |
| Houses | house runtime/schema and protocol/client modules | static inventory; state matrix pending |

## Confirmed runtime/data defects — high confidence

1. **`BESTIARY-DIFFICULTY-INTEGER-DIVISION`**  
   `chance / 1000` uses integer operands before floating-point assignment, collapsing the fractional difficulty band.

2. **`CHARACTER-RECENT-PVP-COUNT-WINDOW-MISMATCH`**  
   displayed rows use a 70-day filter, while the pagination `count(*)` subquery does not. Older deaths can inflate page totals and advertise empty pages.

3. **`BESTIARY-MISSING-RACE-ID` — Crypt Warrior**  
   the active definition has `monster.Bestiary` but no positive `monster.raceId`, so kill progress cannot use a valid Bestiary key.

4. **Bestiary race ID `1946` collision**  
   Druid's Apparition and Monk's Apparition are distinct Bestiary creatures in the reference data, but share one server race ID. Canary keys kill progress and Charm assignment by race ID, so their progression collides.

5. **Bosstiary boss ID `1225` collision**  
   Eradicator and Rupture are distinct Archfoe bosses in the reference data, but share one server boss ID. Canary stores Bosstiary progress and boss-slot state by boss race ID, so their state collides.

No gameplay/data fix is included in #170. Each correction requires a focused PR and regression test; replacement IDs must be sourced, not invented.

## Display metadata defects — high confidence

The loader accepts missing `Bestiary.race`, but leaves numeric race classification at `BESTY_RACE_NONE`; numeric filters and unlocked counts can omit:

- Agrestic Chicken (`raceId 1979`);
- Terrified Elephant (`raceId 771`);
- Haunted Dragon (`raceId 1376`);
- Crypt Warrior (also missing `raceId`).

## Latent helper/resilience defects — high confidence

- **`CHARM-CATEGORY-GUARD-USES-TYPE`** — category assignment is guarded by `mask.type` instead of `mask.category`; current active entries define both.
- **`BESTIARY-MTYPE-DEREFERENCE-BEFORE-GUARD`** — `addBestiaryKill` dereferences `mtype` before its explicit null guard.
- **`BOSSTIARY-EMPTY-RESULT-FALLBACK-UNREACHABLE`** — an early return makes the later empty-result fallback unreachable; clean schema seeding reduces current impact.

## Needs evidence — medium confidence

- **`CHARM-RESET-ALL-LEVEL-FORMULA`** — the formula multiplies the entire level by 11,000 after level 100. The current authoritative rule and level 100/101/102 tests are required before a fix.

## Duplicate IDs retained as review warnings

Likely intentional shared colour/form/phase entries, kept visible by the scanner:

- Bestiary `213`: Pink Butterfly + Purple Butterfly;
- Bestiary `227`: Blue Butterfly + Butterfly;
- Bosstiary `1406`: Armored + Unarmored Voidborn;
- Bosstiary `1811`: five Urmahlullu forms;
- Bosstiary `1969`: two Goshnar's Megalomania forms.

## Canary ↔ OTClient boundary

Static producer/consumer families exist for Bestiary, Charms, Bosstiary, boss slots, Character information, map actions and Houses. This does not prove byte-level compatibility. Field ordering, counts, optional data and feature gates remain covered by the packet-smoke scenario in `CYCLOPEDIA_RUNTIME_TEST_PLAN.json`.

## Validation status

- focused tests: `9/9` passed on the verified code head;
- `py_compile`: passed;
- Cyclopedia Validation: success;
- repository CI: success;
- AI Agent Tools: success;
- branch state at verification: one commit ahead of `main`, zero behind;
- PR mergeable at verification: true;
- runtime/DB/packet scenarios: not executed yet.

## Still unproven

- exact byte-level packet compatibility;
- map discovery trigger/persistence completeness;
- item catalogue parity with client assets and market metadata;
- Character stat/title unlock parity;
- Houses auction/transfer atomicity;
- relog persistence for every Charm, Bestiary and Bosstiary path;
- runtime verification of remapped Bestiary/Bosstiary progress after deployment.

## Remediation log

### 2026-07-12 22:20 Europe/Warsaw — runtime correctness batch

- corrected Bestiary difficulty arithmetic to preserve fractional thresholds;
- corrected the all-Charm reset formula to charge 11,000 gold only for levels above 100;
- made Bestiary kill attribution null-safe before reading the monster type;
- corrected the Charm category guard;
- aligned recent-PvP pagination count with the 70-day row window;
- restored boosted-boss initialization when the table has no row;
- added four source-contract regression tests covering all six corrections;
- no protocol, schema, map, asset or player-data migration was added in this batch.

## Data remediation log

### 2026-07-12 22:45 Europe/Warsaw — Bestiary/Bosstiary data batch

- assigned Monk's Apparition Bestiary ID `2636`;
- assigned Crypt Warrior Bestiary ID `1995` and Undead race metadata;
- added Bird, Mammal and Dragon numeric race metadata to the three affected definitions;
- moved the alternate Eradicator form from Rupture ID `1225` to Eradicator ID `1226`;
- added exact path-set allowlists for intentional shared forms; unexpected extra or missing forms still fail validation;
- added full active-monster inventory and source-contract regression tests;
- target result: zero Cyclopedia scanner findings.

Evidence used before changing technical IDs:

- Crypt Warrior uses Bestiary ID `1995` in an independent complete Bestiary registry; `1674` is already occupied by Skeleton Elite Warrior.
- Monk's Apparition uses `2636` in two independent modern server datasets, while Druid's Apparition remains `1946`.
- `eradicator2.lua` exposes the display name Eradicator and is an alternate Eradicator form; it now shares `1226` with `eradicator.lua` instead of colliding with Rupture `1225`.
- Existing ambiguous historical counters are not copied or duplicated: `1946` remains Druid's Apparition, `1225` remains Rupture, and Eradicator forms use `1226`.

<!-- dry-run trigger: 2026-07-12 current-main verification -->
