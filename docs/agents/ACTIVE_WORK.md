# Active Work Index

Last reviewed: 2026-07-12T21:45:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#170](https://github.com/blakinio/canary/pull/170) | `feat/cyclopedia-validation-audit` | ready | Deterministic Cyclopedia registry, runtime-pattern and Canary ↔ OTClient contract validation | `tools/ai-agent/cyclopedia_validation.py`, focused workflow/tests, `docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md` | Read-only audit is ready; confirmed defects are being fixed in separate focused PRs with the project log updated after every change. |
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
