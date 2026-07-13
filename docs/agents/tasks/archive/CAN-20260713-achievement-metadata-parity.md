---
task_id: CAN-20260713-achievement-metadata-parity
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/achievement-metadata-parity
base_branch: main
created: 2026-07-13T15:30:00+02:00
updated: 2026-07-13T16:45:00+02:00
last_verified_commit: "45e0f2e5b53f1889347db8d7cf8a48f4eabdead3"
risk: medium
related_issue: ""
related_pr: "#256"
depends_on:
  - "merged comprehensive achievement audit PR #238"
blocks:
  - "achievement point reconciliation and backfill task"
  - "achievement handler parity work"
owned_paths:
  - data/scripts/lib/register_achievements.lua
  - tools/ai-agent/test_achievement_validation.py
  - docs/ai-agent/ACHIEVEMENT_METADATA_PARITY_FIX.md
modules_touched:
  - achievement registry metadata
  - achievement validation regression coverage
reuses:
  - canary-achievement-audit-v2
  - factual reference revision 1188274
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Correct the two Real Tibia metadata conflicts that were safe without changing the persisted achievement point total.

# Completed scope

- ID 406 `The More the Merrier`: grade `1 -> 0`.
- ID 513 `Soul Mender`: secret `false/default -> true`.
- Added a regression test that parses the real registry and asserts the complete metadata tuple for both IDs.
- Added `docs/ai-agent/ACHIEVEMENT_METADATA_PARITY_FIX.md` with provenance and the persistence boundary.

No achievement name, ID, points value, award condition, handler, storage, unlock timestamp, quest, map, item, schema or client contract was changed.

# Deferred point conflicts

The following remain a separate backfill-aware package:

| ID | Achievement | Canary | Reference |
|---:|---|---:|---:|
| 526 | King's Council | 0 | 2 |
| 555 | Inner Peace | 2 | 3 |
| 556 | Fiend Rider | 2 | 3 |
| 559 | Hope of the Merudri | 3 | 2 |
| 562 | Alpha Rider | 2 | 3 |

They were not edited because `PlayerAchievement` maintains an incremental persisted aggregate at `achievements/points`; loading unlock names does not recompute it. A registry-only edit would leave existing players stale.

# Sources

- `docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json`, revision `1188274`, observed 2026-07-13.
- Source SHA-256 `8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b`.
- Live Fandom pages for `The More the Merrier`, `Soul Mender`, `King's Council` and `Hope of the Merudri`, read 2026-07-13.
- `data/scripts/lib/register_achievements.lua`.
- `src/creatures/players/components/player_achievement.cpp`.

# Confirmed results

- public/secret registry count changed from `350/191` to `349/192`;
- registry point total remained `1428`;
- comprehensive conflicts changed from `31` to `29`;
- `handler-missing=3`, `partially-confirmed=121` and static reference counts remained unchanged;
- the five point conflicts remained visible;
- final PR diff contained exactly four intended files and no temporary workflow;
- review threads and reviews were empty.

# Validation

| Head/run | Check | Result |
|---|---|---|
| `1cc51c32268a1780a544511ec75780c959b105c6` / `29257442036` | Python compilation, 14 focused tests, full audit, JSON and diff check | passed |
| `9816bb21a8f60f8b1d318cb6c92f4ed97475de01` / `29257672213` | atomic publication and materializer removal | passed |
| `45e0f2e5b53f1889347db8d7cf8a48f4eabdead3` / `29258060120` | Achievement Validation | passed |
| same / `29258057200` | Weapon Proficiency Achievement Audit | passed |
| same / `29258057480` | AI Agent Tools | passed |
| same / `29258061433` | Agent Task Ownership | passed |
| same / `29258076800` | autofix.ci | passed |
| same / `29258077128` | Fast Checks, Lua Tests, Linux release, both datapack smoke and Required | passed |

# Failed approaches

1. Duplicate branch creation returned `422`; the existing branch was retained.
2. Creating an existing task file returned `422`; subsequent writes used update semantics.
3. First materializer run generated an incorrectly indented test.
4. First diagnostic wrapper captured only the final command status.
5. Explicit indentation plus per-command status propagation fixed both issues.
6. Enabling auto-merge returned `UNPROCESSABLE` because GitHub already considered the PR clean; a guarded immediate squash merge was used instead.

# Design decisions

- Grade 406 and secret 513 were separated from point changes because they do not mutate persisted totals.
- Names and IDs were preserved because unlock persistence is canonical-name keyed.
- Point changes, handlers and missing definitions remain separate risk domains.
- The regression parses the production registry rather than only a fixture.

# Merge

- PR: #256
- merge commit: `bb5ceef0354a8e6a09f44b74c89fcce084e6d848`
- method: squash
- result: merged successfully after all current-head gates passed

# Handoff

The next task must implement achievement point reconciliation for IDs 526, 555, 556, 559 and 562. Start from current `main`. First prove the exact load lifecycle and add an idempotent total-calculation API. Do not change award handlers or canonical names. Required tests: upward correction, downward correction, no-op, repeated reconciliation, empty unlock set, unresolved stored name, unchanged timestamps and current/new-player behavior.

# Completion

- Final status: completed
- PR: #256
- Merge commit: `bb5ceef0354a8e6a09f44b74c89fcce084e6d848`
- Archived at: 2026-07-13T16:45:00+02:00
