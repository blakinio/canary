# Active Work Index

Last reviewed: 2026-07-12

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |
| [#153](https://github.com/blakinio/canary/pull/153) | `fix/the-beginning-zirella-door-rewards` | draft | Zirella reward-room gate and current shovel/rope tutorial UIDs | UID50085 door Action, quest reward tutorial mapping, focused test | Stacked on #149; do not merge before #149. No map or reward-content changes. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
