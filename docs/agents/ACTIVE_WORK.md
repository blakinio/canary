# Active Work Index

Last reviewed: 2026-07-12T20:12:32+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#166](https://github.com/blakinio/canary/pull/166) | `feat/imbuement-validation-audit` | draft | Deterministic read-only audit of Imbuing XML/reference values, runtime paths and unlock-storage wiring | `tools/ai-agent/imbuement*_validation*`, focused workflow and `docs/ai-agent/IMBUEMENT_*` | Found seven stale nonzero storage IDs affecting 22 Powerful families plus two zero-storage bypasses; no gameplay, map, asset or engine changes. |
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
