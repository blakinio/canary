# Active Work Index

Last reviewed: 2026-07-12T12:59:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#135](https://github.com/blakinio/canary/pull/135) | `fix/analytics-data-correctness` | draft | Gameplay Analytics data-correctness hardening | Analytics runtime, maintenance, reporting, rune supply and focused tests/docs | Task: `CAN-20260712-analytics-data-correctness`; avoid overlapping Analytics paths. |
| [#131](https://github.com/blakinio/canary/pull/131) | `docs/otbm-final-handoff-20260712` | draft | OTBM handoff documentation | OTBM handoff document | Verify whether superseded by merged #130/#133. |
| [#125](https://github.com/blakinio/canary/pull/125) | `feat/materialize-promotion-overlay` | open | Reviewed AI-content promotion overlay materializer | `tools/ai-agent/materialize_promotion_overlay.py` and tests | Feeds the merged staging/deployment pipeline from #118. |
| [#124](https://github.com/blakinio/canary/pull/124) | `fix/account-quests-production-hardening` | open | Account-wide quest configuration, atomic claims, migrations, admin tooling | account-quest Lua/config/DB/tooling paths in PR | Crosses DB and Lua API contracts. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
