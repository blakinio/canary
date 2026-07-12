# Active Work Index

Last reviewed: 2026-07-12T19:45:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#169](https://github.com/blakinio/canary/pull/169) | `feat/wheel-of-destiny-validation-audit` | draft | Deterministic Wheel of Destiny and Gem Atelier validation | `tools/ai-agent/wheel_of_destiny_validation.py`, focused tests, specialist project/report/runtime-plan docs | Read-only audit first; no Wheel balance, gameplay, protocol, schema, datapack, map or asset changes. |
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
