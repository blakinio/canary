# Active Work Index

Last reviewed: 2026-07-12T13:00:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| pending | `docs/otbm-aid-26002-review` | draft | Manual OTBM `actionId 26002` classification | OTBM review rules, evidence report and handoff | Reuses merged resolver #104; no map, datapack or runtime changes. |
| [#132](https://github.com/blakinio/canary/pull/132) | `fix/required-linux-check` | open | Required Linux CI check emission | `.github/workflows/ci.yml` | Workflow/path-filter changes must inspect this PR. |
| [#131](https://github.com/blakinio/canary/pull/131) | `docs/otbm-final-handoff-20260712` | draft | OTBM handoff documentation | OTBM handoff document | Superseded by merged #130/#133; current `main` is authoritative. |
| [#125](https://github.com/blakinio/canary/pull/125) | `feat/materialize-promotion-overlay` | open | Reviewed AI-content promotion overlay materializer | `tools/ai-agent/materialize_promotion_overlay.py` and tests | Feeds deployment work in #118. |
| [#124](https://github.com/blakinio/canary/pull/124) | `fix/account-quests-production-hardening` | open | Account-wide quest configuration, atomic claims, migrations, admin tooling | account-quest Lua/config/DB/tooling paths in PR | Crosses DB and Lua API contracts. |
| [#118](https://github.com/blakinio/canary/pull/118) | `feat/canary-staging-deployment` | open | Real staging validation and atomic deployment orchestration | `tools/deploy/**`, workflows, docs | Canonical deploy path; do not duplicate it. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
