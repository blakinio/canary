# Game Catalog metadata evidence

This directory is a bounded reviewed seed for the repository-default
`data-otservbr-global` datapack. It is not a claim that the datapack is
historically complete or that a production deployment uses this profile.

| Manifest claim | Repository evidence | Review conclusion |
|---|---|---|
| Runtime and content target `15.25` | `src/core.hpp` declares `CLIENT_VERSION = 1525`. | This is the current repository target only. It does not prove content completeness. |
| Unknown verified and contained content boundaries | `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` separates protocol support from datapack coverage. | Both snapshot-wide boundaries remain `null`. |
| Item source key `3416` and canonical key `item:dragon-shield` | `data/items/items.xml`, item `id="3416"` named `dragon shield`. | The current runtime identity is reviewed; historical introduction and removal releases remain unknown. |
| Creature source key `dragon` and canonical key `creature:dragon` | `data-otservbr-global/monster/dragons/dragon.lua` registers `Dragon`. | The current runtime identity is reviewed; historical introduction and removal releases remain unknown. |
| Creature availability `encounterable` | `data-otservbr-global/world/otservbr-monster.xml` contains explicit `Dragon` spawn entries. | A reviewed spawn proves encounterability for the repository datapack. |
| Item availability `obtainable` | `data-otservbr-global/monster/dragons/dragon.lua` lists `dragon shield` in `monster.loot`. | A reviewed enabled loot source proves obtainability for the repository datapack. |
| Loot source key `dragon\|3416\|20` and canonical key `loot:dragon:dragon-shield` | The Dragon loot list contains dragon shield at zero-based block path `20`; the runtime exporter resolves the name to server item `3416`. | The exact key must also appear in the deterministic runtime export before this seed is accepted. |
| Completeness `unverified` and null `introduced_in`/`removed_in` | No reviewed repository evidence establishes full historical coverage or release bounds for this seed. | Missing evidence remains explicit and is not inferred from external sources. |

Production import and activation are outside this metadata task.
