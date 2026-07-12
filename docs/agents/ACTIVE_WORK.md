# Active Work Index

Last reviewed: 2026-07-12T18:58:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#161](https://github.com/blakinio/canary/pull/161) | `feat/otbm-hd-batch-ai-backend` | draft | One-process batch external AI backend and optional TibiaSR 2x reference adapter for the merged OTBM HD pipeline | `tools/ai-agent/otbm_hd_batch*`, focused tests/docs | Reuses #154 override validation; local Cobra AI batch smoke is 287/287 with one model process and no committed assets. |
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
