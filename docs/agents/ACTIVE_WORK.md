# Active Work Index

Last reviewed: 2026-07-12T22:18:00+02:00

Open pull requests and current changed files/checks are authoritative. This index helps agents detect likely overlap.

| PR | Branch | State | Area / reusable work | Primary paths | Coordination note |
|---:|---|---|---|---|---|
| [#190](https://github.com/blakinio/canary/pull/190) | `feat/otbm-world-index` | draft | Deterministic read-only unified OTBM world index and query contract; foundation for quest, teleport, spawn/NPC, storage and semantic-diff validators | `tools/ai-agent/otbm_world_index*`, schema/tests/workflow, `docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md` | Reuses the existing native item scan, script-resolution audit and factual renderer; no map/parser duplication or binary asset changes. |
| [#170](https://github.com/blakinio/canary/pull/170) | `feat/cyclopedia-validation-audit` | ready | Deterministic Cyclopedia registry, runtime-pattern and Canary ↔ OTClient contract validation | `tools/ai-agent/cyclopedia_validation.py`, focused workflow/tests, `docs/ai-agent/OTS_AI_CYCLOPEDIA_VALIDATION_PROJECT.md` | Read-only audit is ready; confirmed defects are being fixed in separate focused PRs with the project log updated after every change. |
| [#166](https://github.com/blakinio/canary/pull/166) | `feat/imbuement-validation-audit` | draft | Deterministic read-only audit of Imbuing XML/reference values, runtime paths and unlock-storage wiring | `tools/ai-agent/imbuement*_validation*`, focused workflow and `docs/ai-agent/IMBUEMENT_*` | Found seven stale nonzero storage IDs affecting 22 Powerful families plus two zero-storage bypasses; no gameplay, map, asset or engine changes. |
| [#149](https://github.com/blakinio/canary/pull/149) | `fix/the-beginning-zirella-wood` | ready | Authentic Zirella Collecting Wood progression | The Beginning quest Action, focused contract test, task record | No map change; exact tree/cart positions and current item/storage IDs. Depends on merged #146. |

## Rules

- Add a row after publishing a task branch and draft PR.
- Include reusable modules/contracts, not only feature titles.
- Remove or supersede rows after merge/closure.
- Detailed logs belong in task records.
