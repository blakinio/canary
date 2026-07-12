# Active Work Index

Last reviewed: 2026-07-12T13:24:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#140](https://github.com/blakinio/canary/pull/140) | `test/analytics-dry-run-audit` | ready | Gameplay Analytics no-server/no-database adversarial tests | Analytics correctness edge tests, maintenance config validation, dedicated dry-run workflow | Task: `CAN-20260712-analytics-dry-run-audit`; all current-head checks passed. |
| [#131](https://github.com/blakinio/canary/pull/131) | `docs/otbm-final-handoff-20260712` | draft | OTBM handoff documentation | OTBM handoff document | Verify whether superseded by merged #130/#133. |
| [#124](https://github.com/blakinio/canary/pull/124) | `fix/account-quests-production-hardening` | open | Account-wide quest configuration, atomic claims, migrations, admin tooling | account-quest Lua/config/DB/tooling paths in PR | Crosses DB and Lua API contracts. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
