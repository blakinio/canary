# Active Work Index

Last reviewed: 2026-07-12T13:12:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#137](https://github.com/blakinio/canary/pull/137) | `docs/otbm-aid-26002-review` | draft | AI world validation project handoff and manual OTBM `actionId 26002` classification | `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`, review rules and evidence report | Main continuity document for map/quest/NPC/spawn validation; reuses merged resolver #104; no map, datapack or runtime changes. |
| [#131](https://github.com/blakinio/canary/pull/131) | `docs/otbm-final-handoff-20260712` | draft | OTBM handoff documentation | OTBM handoff document | Superseded by merged #130/#133; current `main` is authoritative. |
| [#124](https://github.com/blakinio/canary/pull/124) | `fix/account-quests-production-hardening` | open | Account-wide quest configuration, atomic claims, migrations, admin tooling | account-quest Lua/config/DB/tooling paths in PR | Crosses DB and Lua API contracts. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
