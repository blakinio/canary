# Active Work Index

Last reviewed: 2026-07-12T23:33:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#211](https://github.com/blakinio/canary/pull/211) | `feat/otbm-world-index-implementation` | draft | Actual deterministic binary OTBM world index, memory-mapped query library and CLI; foundation for quest, teleport, spawn/NPC, storage and semantic-diff validators | existing native scanner plus `tools/ai-agent/otbm_world_index*`, schema/tests/workflow/docs | Reuses the canonical OTBM parser; real-map smoke indexed 17,972,761 tiles and 23,359,571 placements in 32.72 s. No map, asset or datapack changes. Supersedes roadmap-only PR #190. |
| [#205](https://github.com/blakinio/canary/pull/205) | `fix/raid-startup-waves` | ready | Progressive scripted raid spawn waves for upstream #3599 | active Draptor/Yeti encounters, Undead Cavebear identity, focused timing/totals contract | Preserves populations and broadcasts, enforces spawn-before-advance, and removes Draptor's duplicate encounter identity; no framework, map or asset change. |
| [#156](https://github.com/blakinio/canary/pull/156) | `fix/the-beginning-zirella-door-rewards-clean` | ready; stale base | Zirella reward-room gate and current shovel/rope tutorial UIDs | UID `50085` door Action, quest reward tutorial mapping, focused test | Green final-head validation recorded; currently needs refresh against advanced `main`; no merge performed. |
| [#157](https://github.com/blakinio/canary/pull/157) | `fix/the-beginning-carlos-flow` | ready | Carlos outfit, gated trade, successful-sale progression | Carlos NPC, focused contract test, task record | AI tools, Lua/Fast checks, Linux build and global datapack smoke passed; no map, item, economy, or engine changes. |
| [#169](https://github.com/blakinio/canary/pull/169) | `feat/wheel-of-destiny-validation-audit` | draft | Deterministic Wheel of Destiny and Gem Atelier validation | `tools/ai-agent/wheel_of_destiny_validation.py`, focused tests, specialist project/report/runtime-plan docs | Read-only audit first; no Wheel balance, gameplay, protocol, schema, datapack, map or asset changes. |
| [#170](https://github.com/blakinio/canary/pull/170) | `feat/cyclopedia-validation-audit` | ready | Deterministic Cyclopedia registry, runtime-pattern and Canary ↔ OTClient contract validation | `tools/ai-agent/cyclopedia_validation.py`, focused workflow/tests, `docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md` | Read-only audit is ready; confirmed defects are being fixed in separate focused PRs with the project log updated after every change. |
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
