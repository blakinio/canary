# Active Work Index

Last reviewed: 2026-07-13T08:24:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#230](https://github.com/blakinio/canary/pull/230) | `feat/wheel-15-25-runtime-completion` | draft | Complete the six explicit Tibia 15.25 Wheel runtime gaps: vocation stances/replacement spells, Revelation/passive reworks, critical healing, Strong Ice Wave geometry, bounded Task Shop Wheel points, and end-to-end tests | `src/creatures/players/components/wheel/**`, combat/player/protocol runtime, `data/scripts/spells/**`, Taskboard shim, focused tests and Wheel validation docs | Reuses PlayerWheel, existing Combat/chain helpers, official Taskboard packets and the merged PR #169 audit. Do not overlap these paths without coordination. |
| [#156](https://github.com/blakinio/canary/pull/156) | `fix/the-beginning-zirella-door-rewards-clean` | ready; stale base | Zirella reward-room gate and current shovel/rope tutorial UIDs | UID `50085` door Action, quest reward tutorial mapping, focused test | Green final-head validation recorded; currently needs refresh against advanced `main`; no merge performed. |
| [#157](https://github.com/blakinio/canary/pull/157) | `fix/the-beginning-carlos-flow` | ready | Carlos outfit, gated trade, successful-sale progression | Carlos NPC, focused contract test, task record | AI tools, Lua/Fast checks, Linux build and global datapack smoke passed; no map, item, economy, or engine changes. |
| [#190](https://github.com/blakinio/canary/pull/190) | `feat/otbm-world-index` | draft | Deterministic read-only unified OTBM world index and query contract; foundation for quest, teleport, spawn/NPC, storage and semantic-diff validators | `tools/ai-agent/otbm_world_index*`, schema/tests/workflow, `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` | Reuses the existing native item scan, script-resolution audit and factual renderer; no map/parser duplication or binary asset changes. |
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
