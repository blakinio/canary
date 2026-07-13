---
task_id: CAN-20260713-achievement-metadata-parity
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: fix/achievement-metadata-parity
base_branch: main
created: 2026-07-13T15:30:00+02:00
updated: 2026-07-13T16:35:00+02:00
last_verified_commit: "26162dd10231c2362cf1c271b5ce6bcffb20be81"
risk: medium
related_issue: ""
related_pr: "#256"
depends_on:
  - "merged comprehensive achievement audit PR #238"
  - "merged achievement validator/helper repairs #165, #176 and #184"
blocks:
  - "achievement point reconciliation and backfill task"
  - "achievement handler parity work"
owned_paths:
  exclusive:
    - data/scripts/lib/register_achievements.lua
    - tools/ai-agent/test_achievement_validation.py
    - docs/ai-agent/ACHIEVEMENT_METADATA_PARITY_FIX.md
    - docs/agents/tasks/active/CAN-20260713-achievement-metadata-parity.md
  read_only:
    - docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
    - docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
    - docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
    - tools/ai-agent/achievement_validation.py
    - src/creatures/players/components/player_achievement.*
modules_touched:
  - achievement registry metadata
  - achievement validation regression coverage
reuses:
  - canary-achievement-audit-v2
  - Achievement Validation workflow
  - factual reference revision 1188274 from PR #238
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Correct the two non-point achievement metadata conflicts that are safe without a persistence migration, while preserving the five point conflicts for a separate backfill-aware task.

# Exact scope

Implemented:

1. ID 406 `The More the Merrier`: grade `1 -> 0`.
2. ID 513 `Soul Mender`: secret `false/default -> true`.

Deferred:

1. ID 526 `King's Council`: points `0 -> 2`.
2. ID 555 `Inner Peace`: points `2 -> 3`.
3. ID 556 `Fiend Rider`: points `2 -> 3`.
4. ID 559 `Hope of the Merudri`: points `3 -> 2`.
5. ID 562 `Alpha Rider`: points `2 -> 3`.

No achievement name, ID, points value, award condition, handler, storage, unlock timestamp, quest, map, item, database schema or client contract is changed in PR #256.

# Acceptance criteria

- [x] Current main and open achievement-related PR state inspected.
- [x] No open PR owns `register_achievements.lua`, `player_achievement.cpp` or `achievement_validation.py`.
- [x] Dedicated branch and durable task record created.
- [x] Draft PR #256 opened early.
- [x] Exact seven registry definitions and factual reference rows inspected.
- [x] Current live evidence for IDs 406, 513, 526 and 559 rechecked on 2026-07-13.
- [x] Pinned full-table revision/hash retained for all seven rows.
- [x] `PlayerAchievement` point persistence inspected before implementation.
- [x] Unsafe registry-only point edits split into a separate reconciliation task.
- [x] Only grade 406 and secret 513 changed.
- [x] Real-registry regression test added.
- [x] Fourteen focused tests pass.
- [x] Comprehensive audit removes exactly two conflicts: `31 -> 29`.
- [x] Five point conflicts remain visible.
- [x] Point total remains `1428`.
- [x] Static/reference disposition counts remain unchanged.
- [x] Temporary materializer workflow removed.
- [x] Durable focused documentation created.
- [x] PR title/body narrowed to the implemented scope.
- [x] Exact four-file diff reviewed.
- [x] Review threads and reviews are empty.
- [x] Dedicated audit, Weapon Proficiency audit, AI Agent Tools, ownership and required CI passed on `26162dd10231c2362cf1c271b5ce6bcffb20be81`.
- [x] `autofix.ci` was explicitly skipped on that head; it is not misreported as passed.
- [ ] Current-head checks pass after this final task-record commit.
- [ ] PR marked Ready and auto-merge enabled after the final current-head gates.
- [ ] Task archived in a separate cleanup PR after merge.

# Sources and observation dates

| Source | Date | Purpose |
|---|---|---|
| `docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json` revision `1188274` | 2026-07-13 | complete factual metadata |
| `data/scripts/lib/register_achievements.lua` | 2026-07-13 | active Canary values |
| `src/creatures/players/components/player_achievement.cpp` | 2026-07-13 | point persistence and load behavior |
| live Fandom `The More the Merrier` | 2026-07-13 | grade 0, 0 points, secret, historical availability |
| live Fandom `Soul Mender` | 2026-07-13 | grade 4, 10 points, secret |
| live Fandom `King's Council` | 2026-07-13 | 2 points, active/current obtainability note |
| live Fandom `Hope of the Merudri` | 2026-07-13 | 2 points |
| PR #238 | 2026-07-13 | audit v2 and provenance |
| live open PR search | 2026-07-13 | overlap check |

# Confirmed findings

- Current reference source SHA-256 is `8a429425ab7b088758646b07f036afdd1d579188d056491aed8e77650306ae8b`.
- ID 406 is currently grade 0, zero-point and secret; its live page says it is no longer obtainable for new players.
- ID 513 is grade 4, ten-point and secret.
- Canary previously stored 406 as grade 1 and treated 513 as public by default.
- `PlayerAchievement::add()` increments the persisted points KV from the definition.
- `getPoints()` reads the persisted aggregate.
- `loadUnlockedAchievements()` restores unlocks by canonical name but does not recompute points.
- Registry-only point edits would create existing-player drift.
- After the two safe fixes, public/secret becomes `349/192`, total points remain `1428`, and conflicts become `29`.
- Handler/disposition evidence remains unchanged: 182 API references, 160 resolved static, 0 unknown static, 22 dynamic.

# Uncertain findings requiring later proof

- Authoritative lifecycle for point reconciliation: per-load calculation, versioned migration marker or administrative migration.
- Behavior when an unlocked canonical name no longer resolves.
- Whether a mismatch should be repaired silently or recorded diagnostically.
- Runtime/E2E parity for the award conditions of IDs 406 and 513; this PR changes metadata only.

# Conflicts and disposition

| ID | Field | Before | Reference | Disposition |
|---:|---|---|---|---|
| 406 | grade | 1 | 0 | repaired #256 |
| 513 | secret | false | true | repaired #256 |
| 526 | points | 0 | 2 | deferred with backfill |
| 555 | points | 2 | 3 | deferred with backfill |
| 556 | points | 2 | 3 | deferred with backfill |
| 559 | points | 3 | 2 | deferred with backfill |
| 562 | points | 2 | 3 | deferred with backfill |

# Files changed and purpose

| Path | Purpose |
|---|---|
| `data/scripts/lib/register_achievements.lua` | two exact registry field corrections |
| `tools/ai-agent/test_achievement_validation.py` | real-registry regression |
| `docs/ai-agent/ACHIEVEMENT_METADATA_PARITY_FIX.md` | evidence and point-backfill boundary |
| `docs/agents/tasks/active/CAN-20260713-achievement-metadata-parity.md` | durable task and handoff |

# Commands and tests

```text
python -m py_compile tools/ai-agent/achievement_validation.py tools/ai-agent/test_achievement_validation.py
python -m unittest discover -s tools/ai-agent -p "test_achievement_validation.py" -v
python tools/ai-agent/achievement_validation.py \
  --repository-root . \
  --reference-baseline docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json \
  --reference-catalog docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json \
  --reviewed-evidence docs/ai-agent/ACHIEVEMENT_REVIEWED_EVIDENCE.json \
  --output artifacts/ACHIEVEMENT_AUDIT.json \
  --markdown artifacts/ACHIEVEMENT_AUDIT.md \
  --allow-findings
python -m json.tool artifacts/ACHIEVEMENT_AUDIT.json > /dev/null
git diff --check
```

# Validation and CI

| Head/run | Check | Result |
|---|---|---|
| `54ea4b4bc2e70052d97bd923b056bcf1a9ee0765` / `29257029150` | first materializer | failed: generated test indentation |
| `8bb89b058010471fdfe20cba4ea9a2e4a9987e6c` / `29257339662` | diagnostics | artifact captured failure; status propagation was incorrect |
| `1cc51c32268a1780a544511ec75780c959b105c6` / `29257442036` | corrected materializer | passed 14/14, compile, audit, JSON, diff check |
| `9816bb21a8f60f8b1d318cb6c92f4ed97475de01` / `29257672213` | atomic publication | passed; created `b0015325c6bfd4d5db48f7fbeee28da08fd84473` and removed workflow |
| `26162dd10231c2362cf1c271b5ce6bcffb20be81` / `29257883595` | Achievement Validation | success |
| same / `29257882359` | Weapon Proficiency Achievement Audit | success |
| same / `29257883228` | AI Agent Tools | success |
| same / `29257882821` | Agent Task Ownership | success |
| same / `29257884508` | required CI | success |
| same / `29257882587` | autofix.ci | skipped |

# Failed approaches and causes

1. Duplicate branch creation returned `422 Reference already exists`; no state changed.
2. Creating an already-existing task file returned `422`; subsequent writes used update semantics.
3. First materializer inserted the test body at the wrong indentation.
4. First diagnostic status captured the last command rather than the earlier failed test.
5. Explicit test-string indentation and per-command status capture fixed both defects.

# Decisions

| Decision | Reason |
|---|---|
| Repair only grade 406 and secret 513 | no persisted point-total mutation |
| Split five point changes | existing players use incremental aggregate KV |
| Preserve names and IDs | canonical-name persistence compatibility |
| Keep handlers out | separate evidence and runtime risk |
| Parse real registry in test | avoids fixture-only confidence |
| Remove materializer atomically | no transport infrastructure in final diff |

# Remaining work

1. Wait for final current-head gates triggered by this commit.
2. Mark PR Ready and enable auto-merge when green.
3. Confirm merge.
4. Archive this task in a separate cleanup PR.
5. Start a new point-reconciliation task from updated `main`.

# Handoff

- branch: `fix/achievement-metadata-parity`
- PR: `#256`
- last fully validated head before this final task update: `26162dd10231c2362cf1c271b5ce6bcffb20be81`
- implementation commit: `b0015325c6bfd4d5db48f7fbeee28da08fd84473`
- completed: grade 406, secret 513, regression, docs, clean diff
- not completed by design: five point changes, backfill, handler/runtime parity
- last focused validation: run `29257442036`, 14/14
- blockers: final current-head CI only
- first next step: inspect workflow runs for this task-record commit; do not add point changes

# Completion

- Final status: ready-for-review
- PR: #256
- Merge commit:
- Archived at:
