---
task_id: CAN-20260713-achievement-point-reconciliation
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/achievement-point-reconciliation
base_branch: main
created: 2026-07-13T16:50:00+02:00
updated: 2026-07-13T23:38:17+02:00
last_verified_commit: "d14d5c992d4095c79672a8469050aa9e103e34bb"
risk: high
related_issue: ""
related_pr: "#264"
depends_on:
  - "merged comprehensive achievement audit PR #238"
  - "merged non-point metadata parity PR #256"
  - "archived task cleanup PR #261"
blocks:
  - "remaining achievement handler parity work"
owned_paths:
  - src/creatures/players/components/player_achievement.hpp
  - src/creatures/players/components/player_achievement.cpp
  - data/scripts/lib/register_achievements.lua
  - tests/unit/players/components/player_achievement_test.cpp
  - tests/unit/players/components/CMakeLists.txt
  - docs/ai-agent/ACHIEVEMENT_POINT_RECONCILIATION.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - PlayerAchievement persistence
  - achievement registry metadata
  - C++ component unit tests
reuses:
  - canary-achievement-audit-v2
  - PlayerAchievement canonical-name KV
  - existing InjectionFixture/KVMemory unit-test harness
public_interfaces:
  - PlayerAchievement::reconcilePoints
  - PlayerAchievement::calculateUnlockedPoints
cross_repo_tasks: []
---

# Goal and completed scope

Correct five evidence-backed Real Tibia achievement point values and reconcile the persisted aggregate for existing characters without changing unlock state or gameplay handlers.

Registry corrections:

| ID | Achievement | Before | After |
|---:|---|---:|---:|
| 526 | King's Council | 0 | 2 |
| 555 | Inner Peace | 2 | 3 |
| 556 | Fiend Rider | 2 | 3 |
| 559 | Hope of the Merudri | 3 | 2 |
| 562 | Alpha Rider | 2 | 3 |

Persistence behavior:

- authoritative points are calculated from resolved canonical unlock IDs and current registry definitions;
- `achievements/points` is updated only when different;
- upward, downward and empty-set reconciliation are supported;
- unlock names and timestamps are preserved;
- repeated load is idempotent and duplicate-free;
- no achievement is awarded, removed or backfilled;
- any unresolved historical canonical name preserves the old aggregate and blocks overwrite;
- overflow or missing definitions abort reconciliation safely.

# Acceptance criteria

- [x] Existing audit/parser reused; no competing validator created.
- [x] Current main and open PR overlap checked.
- [x] Dedicated branch, task record and draft PR created.
- [x] Exact five reference/registry differences reverified.
- [x] Login lifecycle and historical migration semantics proven.
- [x] Authoritative point calculation and reconciliation APIs implemented.
- [x] Unknown-name preservation policy implemented.
- [x] Canonical unlock keys and timestamps remain unchanged.
- [x] Existing add/remove arithmetic remains valid after reconciliation.
- [x] Seven focused C++ tests cover upward, downward, repeat, empty, unknown, timestamps and add/remove behavior.
- [x] Achievement audit confirms the five point conflicts are removed.
- [x] Final implementation diff contains exactly eight intended files and no temporary workflow.
- [x] No achievement names, IDs, grades, secret flags, conditions, handlers, quests, maps, items, DB schema, protocol or production config changed.
- [x] Fast Checks, Lua Tests, Linux release/debug, `canary_ut`, datapack smoke, Windows, macOS and Docker passed.
- [x] Achievement Validation, Weapon Proficiency Audit, AI Agent Tools, ownership and autofix passed.
- [x] No review threads or requested changes remained.
- [x] PR #264 squash-merged.
- [x] Task archived and module catalogue marked merged in a separate cleanup PR.

# Sources and dates

| Source | Read | Result |
|---|---|---|
| `ACHIEVEMENT_REFERENCE_CATALOG.json`, MediaWiki revision `1188274` | 2026-07-13 | target values `2/3/3/2/3` |
| `register_achievements.lua` before repair | 2026-07-13 | values `0/2/2/3/2` |
| `player_achievement.cpp/.hpp` | 2026-07-13 | aggregate stored separately from canonical unlock keys |
| `iologindata_load_player.cpp:1010` | 2026-07-13 | `loadUnlockedAchievements()` runs during player load |
| migration `20241708000535_move_achievement_to_kv.lua` | 2026-07-13 | points are intended as the sum of unlocked definitions |
| inspection artifact `8285423590` | 2026-07-13 | lifecycle/API/KV/test evidence; digest `sha256:6129206d5aa20412e01a243854408480b802b09375e6c7c0bead22954da83838` |
| Achievement Validation artifact `8292258715` | 2026-07-13 | corrected points verified; digest `sha256:3ee4e0b04e6280ac085b5b90ce30e2f779169caa40356c7834003716f7c2a524` |

# Confirmed findings

- Registry-only point edits would leave existing characters stale.
- Canonical unlock names are the persistence identity and must not be renamed here.
- The aggregate can safely be reconstructed only when every stored name resolves.
- Unknown historical names may represent removed/renamed content; their contribution is not inferable.
- PR #272 has no changed-file overlap with this work.
- After correction, the comprehensive audit conflict count dropped from 31 to 24; remaining conflicts are missing definitions rather than these point values.

# Uncertain findings retained

- A real production database may contain unknown historical names; those characters intentionally retain their previous aggregate and emit an error until a reviewed alias/migration exists.
- Full production login with real historical data remains operational validation outside this focused PR.

# Files changed and purpose

| Path | Purpose |
|---|---|
| `src/creatures/players/components/player_achievement.hpp` | calculation and reconciliation API |
| `src/creatures/players/components/player_achievement.cpp` | idempotent load and aggregate reconciliation |
| `data/scripts/lib/register_achievements.lua` | five point corrections |
| `tests/unit/players/components/player_achievement_test.cpp` | seven regression tests |
| `tests/unit/players/components/CMakeLists.txt` | test source registration |
| `docs/ai-agent/ACHIEVEMENT_POINT_RECONCILIATION.md` | persistence semantics, safety and rollback |
| `docs/agents/MODULE_CATALOG.md` | reusable module/API entry |
| this archive record | durable execution evidence and handoff |

# Commands and tests

Representative commands executed by materializer and CI:

```text
clang-format -i src/creatures/players/components/player_achievement.hpp src/creatures/players/components/player_achievement.cpp tests/unit/players/components/player_achievement_test.cpp
python -m unittest discover -s tools/ai-agent -p "test_achievement_validation.py" -v
python -m py_compile tools/ai-agent/achievement_validation.py tools/ai-agent/test_achievement_validation.py
python -m json.tool docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
git diff --check
git diff --cached --check
cmake --build --preset linux-debug
ctest / canary_ut through repository CI
Canary and global datapack smoke through repository CI
```

# CI and artifact evidence

| Commit/context | Run | Result |
|---|---:|---|
| inspection head | `29266034973` | success; artifact `8285423590` |
| materializer | `29283419100` | success; implementation committed and temporary workflow removed |
| validator head | `29283559657` | success; artifact `8292258715`, five point conflicts removed |
| first full C++ attempt | `29283729292` | failed only in test compile due ambiguous `uint32_t` to `ValueWrapper` conversion |
| compile diagnostics | `29284512167` | exact compiler error captured; artifact `8292611214`, digest `sha256:93d28eb155a7041e3c0a8e65c5619e16ce56432434cc25f1292c880c827bb91d` |
| corrected pre-refresh head | `29284715043` | success across full matrix and `canary_ut` |
| final head `d14d5c992d4095c79672a8469050aa9e103e34bb` | `29286023546` | success across full matrix and Required |
| final head | `29286023467` | Achievement Validation success |
| final head | `29286023443` | Weapon Proficiency Achievement Audit success |
| final head | `29286023456` | AI Agent Tools success |
| final head | `29286023560` | Agent Task Ownership success |
| final head | `29286023452` | autofix.ci success |

Final CI included Linux debug/release, seven new `PlayerAchievement` tests inside full `canary_ut`, Canary/global datapack smoke, Windows CMake/Solution, macOS and Docker.

# Failed approaches and causes

1. The original draft PR contained only an inspection task/workflow and no implementation.
2. Workflow-generated implementation commits produced `action_required`; a user-authored synchronization commit triggered authoritative CI.
3. Autofix formatted the component `CMakeLists.txt` and failed while publishing its own result; the formatted commit was retained and revalidated.
4. First Linux debug compilation failed because the test helper passed `uint32_t` to overloaded `ValueWrapper` constructors. Diagnostics proved the exact line; changing the test timestamp parameter to `int`, matching production usage, fixed it.
5. `main` advanced repeatedly through unrelated InstanceArena, OTBM, Redis and CrystalServer commits. The branch was rebuilt on current main while preserving only the exact eight-file diff. No runtime overlap existed; shared `MODULE_CATALOG.md` was merged deliberately.

# Design decisions

| Decision | Reason |
|---|---|
| Recompute from resolved canonical unlocks | current registry is authoritative for current point totals |
| Abort on unknown stored names | prevents silent historical point loss |
| Use checked wider accumulator | prevents overflow corruption |
| Clear and rebuild in-memory unlocks on load | guarantees repeated-load idempotence |
| Preserve keys and timestamps | repair changes only the derived aggregate |
| Keep unlock awards/backfill out | different gameplay and evidence boundary |
| Keep #264 separate from #272 | different subsystem and no file overlap |

# Follow-up work

- Review unknown historical canonical names only when real production evidence identifies them.
- Continue remaining achievement definitions/handlers/backfill in separate evidence-backed PRs.
- Do not rename canonical achievements without a reviewed KV alias or migration.

# Handoff

- implementation branch: `fix/achievement-point-reconciliation`
- merged PR: `#264`
- final validated head: `d14d5c992d4095c79672a8469050aa9e103e34bb`
- merge commit: `b2036bd5d56423894b72eaa2ebaff32feba382a5`
- last full CI: `29286023546` — success
- blockers: none for this completed scope
- next concrete achievement step: inspect the status of PR #272, refresh it on current main if necessary, and merge only after its own current-head full C++ matrix passes

Reproduction entry points:

```text
python -m unittest discover -s tools/ai-agent -p "test_achievement_validation.py" -v
python -m py_compile tools/ai-agent/achievement_validation.py tools/ai-agent/test_achievement_validation.py
python -m json.tool docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json > /dev/null
git diff --check
```

Do not edit `docs/agents/ACTIVE_WORK.md` manually.

# Completion

- Final status: completed
- PR: #264
- Merge commit: `b2036bd5d56423894b72eaa2ebaff32feba382a5`
- Catalogue updated: yes
- Archived at: 2026-07-13T23:38:17+02:00
