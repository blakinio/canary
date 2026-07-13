# Cyclopedia Validation — evidence report

Last updated: 2026-07-13 13:35 Europe/Warsaw  
Branch: `ci/cyclopedia-validation-gate`  
PR: [#243](https://github.com/blakinio/canary/pull/243) — ready for review  
Reference: `https://tibia.fandom.com/wiki/Cyclopedia`

## Current verified state

- verified repository `main`: `88e0140329a91fb877633307d2b749fecb175a43`;
- completed audit/remediation PRs: #170, #188 and #192;
- completed archive/cleanup PR: #203;
- archived task: `docs/agents/tasks/archive/CAN-20260712-cyclopedia-validation.md`;
- report schema: `1`;
- strict validation head before final bookkeeping rebuild: `cdaca34c99178a2c21c4de39747213cde5cf03d9`;
- Cyclopedia Validation run `29244075969`: success;
- job `Audit Cyclopedia registries and contracts`: all 23 steps succeeded;
- artifact `8276638913`, archive digest `sha256:1bdc198865f608023958dc881ca13343ec462a7fef7437bc1d3618f2293ddd49`;
- JSON digest `sha256:44a02cf4c524be4313443a8dfd339a2352166f52a522b7b20fa77f7c1d8df8eb`;
- parsed artifact: 7 domains, 1,656 active monster files, 749 Bestiary entries, 249 Bosstiary entries, 25 Charms, `findingCount = 0`, `findings = []`.

The branch was rebuilt on current `main` after unrelated PRs #242 and #244 advanced the base. Those PRs changed only Equipment Upgrade validation/task documentation and do not overlap Cyclopedia ownership or scanner source paths. Final current-head CI is still required after the bookkeeping rebuild.

## Related PR review

- PR #224 remains a separate paused physical-client E2E experiment. It is open and draft, has no changed-path overlap with PR #243, is not continued, and is not evidence for runtime, gameplay or persistence.
- PR #242 refreshed Equipment Upgrade documentation; PR #244 archived that task. Neither touches Cyclopedia paths.
- Merged PR #210 changed `src/io/io_bosstiary.cpp` for multichannel boosted-boss leader election. Its source is present in `main` and included in the zero-finding scan; PR #243 does not modify it.
- Merged PR #220 changed Wheel-specific sections of `src/server/network/protocol/protocolgame.cpp`. Its source is present in `main` and included in the zero-finding scan; PR #243 does not modify it.
- Open PR searches for `cyclopedia-validation.yml`, `CYCLOPEDIA_VALIDATION_REPORT.md` and `test_cyclopedia` found no overlapping PR other than #243.

## Scope and evidence rule

This report covers Items, Bestiary, Charms, Bosstiary, Map, Character/Titles and Houses. The reference page is factual input, not authority to change gameplay. A definition is not registration proof; registration is not persistence proof; static evidence is not gameplay or physical-client E2E proof.

## Automated coverage

`tools/ai-agent/cyclopedia_validation.py`:

- parses the active Charm registry and validates IDs, names, category/type and tier arrays;
- scans only `data/monster` and `data-otservbr-global/monster`;
- parses monster race IDs, Bestiary metadata, unlock thresholds, points, boss IDs and rarity;
- reports duplicate Bestiary/Bosstiary IDs for explicit semantic review;
- inventories Canary protocol declarations/definitions and maintained OTClient send/parse methods;
- records bounded source hashes;
- detects known semantic/resilience patterns without writing game data.

Focused tests cover scanner parsing, thresholds, duplicate IDs, optional race metadata, protocol inventory, known patterns, read-only behavior and missing sources. Source-contract suites protect merged runtime/helper and Bestiary/Bosstiary data corrections.

## Original audit result

The original full-checkout audit at head `741ffed81275d37fd700cacdb05cbae05a0a1356` found:

| Metric | Result |
|---|---:|
| Cyclopedia domains | 7 |
| Active monster Lua files | 1,656 |
| Bestiary definitions | 749 |
| Bosstiary definitions | 249 |
| Charm definitions | 25 |
| Scanner findings | 18 |
| Scanner errors | 3 |
| Scanner warnings | 15 |

Original artifact:

```text
artifact id: 8263239684
archive digest: sha256:36df08b9c52fd850f0be1e0f447d6d883e9e0b4fc798412bc6e458fd2228ac38
JSON digest: sha256:e3fad997b2c1104e221807a596e48638a4a3992ea0f85d75d4bb72bc61b8574f
```

## Repaired runtime/data defects

- `BESTIARY-DIFFICULTY-INTEGER-DIVISION`: fractional thresholds preserved.
- `CHARACTER-RECENT-PVP-COUNT-WINDOW-MISMATCH`: row and count queries use the same 70-day window.
- Crypt Warrior: Bestiary ID `1995` and Undead race metadata.
- Monk's Apparition: Bestiary ID `2636`; Druid's Apparition remains `1946`.
- alternate Eradicator: Bosstiary ID `1226`; Rupture remains `1225`.

## Repaired display/helper defects

- race metadata added for Agrestic Chicken, Terrified Elephant, Haunted Dragon and Crypt Warrior;
- Charm category guard uses `mask.category`;
- `addBestiaryKill` validates player and monster type before dereference;
- missing boosted-boss row is initialized before daily selection;
- full Charm reset charges 11,000 gold only for levels above 100.

## Intentional shared forms

Exact active path-set allowlists remain for:

- Bestiary `213`: Pink Butterfly + Purple Butterfly;
- Bestiary `227`: Blue Butterfly + Butterfly;
- Bosstiary `1226`: two Eradicator forms;
- Bosstiary `1406`: Armored + Unarmored Voidborn;
- Bosstiary `1811`: five Urmahlullu forms;
- Bosstiary `1969`: two Goshnar's Megalomania forms.

## Evidence boundary

Verified:

- structural/static registry scan;
- semantic patterns encoded by the deterministic scanner;
- focused Python tests;
- runtime source-contract tests;
- Bestiary/Bosstiary data contract tests;
- maintained OTClient static inventory;
- zero-finding generated artifact;
- Linux Release CMake/build on run `29244075959`.

Not claimed:

- physical-client E2E;
- gameplay confirmation;
- full live DB/relog persistence;
- exact byte-level packet compatibility;
- map discovery trigger/persistence completeness;
- item catalogue parity with client assets and market metadata;
- Character stat/title unlock parity;
- Houses auction/transfer atomicity.

Repository CI run `29244075959` succeeded for Detect Build Scope, Fast Checks, Lua Tests and Linux Release CMake/build. Runtime smoke and C++ tests were skipped by scope detection, so this run is not runtime/gameplay proof.

## Deterministic gate finding

Classification before repair: `confirmed`.

The dedicated workflow previously:

- invoked the scanner with `--fail-on none`;
- lacked an exact `findingCount == 0` invariant;
- executed only `test_cyclopedia_validation.py`;
- omitted source/data contract suites from dedicated execution and path filters.

A warning-only finding or a regression covered only by those suites could coexist with a green dedicated workflow.

## Bounded repair in PR #243

- discover and compile every `test_cyclopedia*.py` module;
- trigger on every Cyclopedia test module;
- run scanner with `--fail-on error`;
- assert both `findingCount == 0` and `findings == []`;
- add `test_cyclopedia_workflow_contracts.py` to prevent gate regression.

Classification after green final-head CI: `repaired`.

This repair changes validation enforcement only. It does not change gameplay, protocol, persistence, schema, monster data, OTClient or physical-client E2E.
