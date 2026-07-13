---
task_id: CAN-20260713-achievement-metadata-parity
status: active
agent: "GPT-5.6 Thinking"
branch: fix/achievement-metadata-parity
base_branch: main
created: 2026-07-13T15:30:00+02:00
updated: 2026-07-13T16:25:00+02:00
last_verified_commit: "b0015325c6bfd4d5db48f7fbeee28da08fd84473"
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

Correct the non-point achievement metadata conflicts that are safe without a persistence migration, and split point changes into a separate backfill-aware task.

# Exact scope

Implemented in PR #256:

1. ID 406 `The More the Merrier`: grade 1 -> 0.
2. ID 513 `Soul Mender`: secret false/default -> true.

Explicitly deferred to a separate point reconciliation task:

1. ID 526 `King's Council`: points 0 -> 2.
2. ID 555 `Inner Peace`: points 2 -> 3.
3. ID 556 `Fiend Rider`: points 2 -> 3.
4. ID 559 `Hope of the Merudri`: points 3 -> 2.
5. ID 562 `Alpha Rider`: points 2 -> 3.

No achievement name, ID, award condition, handler, storage, unlock timestamp, quest, map or item is changed.

# Acceptance criteria

- [x] Current main and open achievement-related PR state inspected.
- [x] No open PR owns `register_achievements.lua`, `player_achievement.cpp` or `achievement_validation.py`.
- [x] Dedicated branch and durable task record created.
- [x] Draft PR #256 opened.
- [x] Exact seven registry definitions and reference catalogue rows inspected.
- [x] Live external evidence for IDs 406, 513, 526 and 559 rechecked on 2026-07-13.
- [x] Pinned complete table revision and source hash retained for all seven rows.
- [x] Persistence behavior inspected before changing point values.
- [x] Unsafe registry-only point changes split into a separate backfill-aware task.
- [x] Only evidence-backed non-point metadata fields changed.
- [x] No achievement name/ID, handler, storage, backfill, map, item or quest condition changed.
- [x] Focused real-registry regression test added.
- [x] Fourteen focused tests pass after the corrections.
- [x] Comprehensive validator removes exactly the two repaired metadata conflicts.
- [x] Five point conflicts remain explicit rather than hidden or guessed.
- [x] Existing handler/disposition counts remain unchanged.
- [x] Temporary materializer workflow removed from the final diff.
- [x] Durable focused documentation created.
- [ ] Current-head dedicated audit, AI Agent Tools, ownership, autofix and required CI pass after final task/document update.
- [ ] PR body narrowed to the implemented two-field scope.
- [ ] PR marked Ready and auto-merge enabled only after all current-head gates pass.
- [ ] Task archived in a separate cleanup PR after merge.

# Sources and observation dates

| Source | Date | Purpose |
|---|---|---|
| `docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md` | 2026-07-13 | seven original metadata conflicts |
| `docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json` revision `1188274` | 2026-07-13 | complete factual reference metadata |
| `data/scripts/lib/register_achievements.lua` | 2026-07-13 | active Canary registry values |
| `src/creatures/players/components/player_achievement.cpp` | 2026-07-13 | persisted point-total behavior |
| live Fandom page `The More the Merrier` | 2026-07-13 | grade 0, 0 points, secret, historical obtainability |
| live Fandom page `Soul Mender` | 2026-07-13 | grade 4, 10 points, secret |
| live Fandom page `King's Council` | 2026-07-13 | 2 points and post-Winter-Update-2025 obtainability |
| live Fandom page `Hope of the Merudri` | 2026-07-13 | 2 points |
| merged PR #238 | 2026-07-13 | validator v2, provenance and evidence model |
| live open PR search | 2026-07-13 | ownership/overlap check |

# Confirmed findings

- PR #238 merged as `3ad10132cbd76adc42f946da3ca3077e5bd6bbd0`.
- Audit v2 initially reported 31 conflicts: seven metadata conflicts plus other missing/structural conflicts.
- ID 406 is grade 0, zero-point and secret in the current live reference; the page states it is no longer obtainable for new players.
- ID 513 is grade 4, ten-point and secret in the current live reference.
- The Canary registry had ID 406 at grade 1 and ID 513 without `secret=true`.
- `PlayerAchievement::add()` increments the persisted points KV from the definition at unlock time.
- `getPoints()` reads the persisted aggregate; `loadUnlockedAchievements()` does not recompute it.
- A registry-only point correction would fix new unlocks but leave existing characters with stale totals.
- The five point changes therefore require deterministic reconciliation/backfill in a separate PR.
- The implemented two-field correction changes public/secret count from `350/191` to `349/192`, while point total remains `1428`.
- The comprehensive audit after the patch reports `conflicting=29`, `handler-missing=3`, `partially-confirmed=121`, `unresolved=411`.
- Static reference/disposition counts remain unchanged: 182 references, 160 resolved static, 0 unknown static, 22 dynamic.

# Uncertain findings requiring future evidence

- The final exact design for idempotent point reconciliation.
- Whether point reconciliation should happen on every load, once by a versioned migration marker, or through an administrative migration command.
- Handling of unlocked canonical names that no longer resolve to a current definition.
- Whether historical grade changes need any UI cache invalidation beyond reading current registry metadata.

# Conflicts and disposition

| ID | Field | Canary before | Reference | Current disposition |
|---:|---|---|---|---|
| 406 | grade | 1 | 0 | repaired in #256 |
| 513 | secret | false/default | true | repaired in #256 |
| 526 | points | 0 | 2 | deferred; requires point reconciliation |
| 555 | points | 2 | 3 | deferred; requires point reconciliation |
| 556 | points | 2 | 3 | deferred; requires point reconciliation |
| 559 | points | 3 | 2 | deferred; requires point reconciliation |
| 562 | points | 2 | 3 | deferred; requires point reconciliation |

# Files changed and purpose

| Path | Purpose |
|---|---|
| `data/scripts/lib/register_achievements.lua` | correct grade 406 and secret flag 513 |
| `tools/ai-agent/test_achievement_validation.py` | real-registry regression for exact two entries |
| `docs/ai-agent/ACHIEVEMENT_METADATA_PARITY_FIX.md` | evidence, persistence boundary and follow-up plan |
| `docs/agents/tasks/active/CAN-20260713-achievement-metadata-parity.md` | durable execution record and handoff |

# Commands and tests

Materializer equivalent commands:

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

| Commit/run | Check | Result |
|---|---|---|
| `54ea4b4bc2e70052d97bd923b056bcf1a9ee0765` / `29257029150` | first materializer | failed: generated test indentation error |
| `8bb89b058010471fdfe20cba4ea9a2e4a9987e6c` / `29257339662` | diagnostic materializer | artifact produced; exposed incorrect status propagation and indentation failure |
| `1cc51c32268a1780a544511ec75780c959b105c6` / `29257442036` | corrected materializer validation | passed: 14/14 tests, Python compilation, full audit, JSON validation, `git diff --check` |
| `9816bb21a8f60f8b1d318cb6c92f4ed97475de01` / `29257672213` | atomic publication | passed; created `b0015325c6bfd4d5db48f7fbeee28da08fd84473`, removed temporary workflow |
| `9816bb21a8f60f8b1d318cb6c92f4ed97475de01` / `29257672528` | baseline CI before published commit | passed; not accepted as final current-head proof |

Never represent the diagnostic run as a passed validation; its artifact deliberately preserved the failure.

# Failed approaches and causes

1. An unnecessary second branch-create request returned `422 Reference already exists`; no state changed.
2. A create-file request targeted an existing task record and returned `422`; the correct update operation is used afterward.
3. Materializer run `29257029150` generated the test body at class indentation instead of method-body indentation.
4. Diagnostic run `29257339662` incorrectly captured the final shell-command status rather than the earlier failing test; its log, not its status file, exposed the issue.
5. Explicit string construction fixed indentation, and per-command status propagation fixed diagnostics.

# Decisions

| Decision | Reason |
|---|---|
| Repair only grade 406 and secret 513 in #256 | they do not mutate persisted point totals |
| Split all point corrections | existing characters store an incremental aggregate KV |
| Keep names unchanged | unlock persistence is keyed by canonical name |
| Do not bundle handlers or missing definitions | different evidence, rollback and test boundaries |
| Test the real registry | prevents fixture-only false confidence |
| Publish atomically and delete materializer | final diff must contain no transport infrastructure |

# Remaining work in this task

1. Narrow PR title/body to the implemented non-point scope.
2. Run all current-head gates after this task/document commit.
3. Review exact four-file diff and review threads.
4. Mark Ready and enable auto-merge only after green gates.
5. Archive this task after merge in a separate cleanup PR.
6. Create the point-reconciliation task from current `main` after cleanup.

# Handoff

## Current state

- branch: `fix/achievement-metadata-parity`
- PR: `#256`
- published implementation commit: `b0015325c6bfd4d5db48f7fbeee28da08fd84473`
- current task/document head: generated by this update
- implemented: grade 406 and secret 513
- deliberately not implemented: five point changes and point backfill
- last valid focused validation: run `29257442036`, 14/14 tests
- blocker: final current-head CI only

## First next step

Update PR #256 body/title to the two-field scope, then inspect workflow runs for the current task/document head. Do not add point changes to this PR.

## Reproduction commands

```text
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

# Completion

- Final status: active
- PR: #256
- Merge commit:
- Archived at:
