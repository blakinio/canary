---
task_id: CAN-20260713-imbuement-vibrancy-scrolls
program_id: ""
coordination_id: ""
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-vibrancy-scrolls
base_branch: main
created: 2026-07-13T10:22:00+02:00
updated: 2026-07-13T11:20:00+02:00
completed: 2026-07-13T11:07:00+02:00
last_verified_commit: "4acd5a6c43f73478768f8f4e85d0a51abb7b8c6a"
merge_commit: "a356d5625e2290d6ffe45ecd6579f9dd8b7649bc"
risk: medium
related_issue: "IMB-004"
related_pr: "#239"
cleanup_branch: docs/archive-imbuement-vibrancy-scrolls
cleanup_pr: "#240"
depends_on:
  - merged Imbuement audit PR #166
  - merged Forgotten Knowledge storage repair PR #206
  - merged coordination cleanup PR #237
blocks: []
owned_paths:
  exclusive:
    - data/XML/imbuements.xml
    - tools/ai-agent/imbuement_validation.py
    - tools/ai-agent/test_imbuement_validation.py
    - tests/fixture/core/XML/imbuements.xml
    - tests/unit/players/imbuements/imbuements_test.cpp
    - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
    - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
    - docs/agents/tasks/archive/CAN-20260713-imbuement-vibrancy-scrolls.md
  shared: []
  read_only:
    - data-otservbr-global/scripts/actions/object/imbuement_scrolls.lua
    - src/creatures/players/imbuements/imbuements.cpp
    - src/lua/functions/creatures/player/player_functions.cpp
    - src/creatures/players/player.cpp
    - src/items/item.cpp
modules_touched:
  - Imbuement XML registry
  - Imbuement deterministic validator
  - Imbuement focused C++ and Python tests
reuses:
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/imbuement_storage_validation.py
  - tests/shared/imbuements/imbuements_test_fixture.hpp
  - .github/workflows/imbuement-validation.yml
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Repair only IMB-004 so Intricate Vibrancy scroll `51746` and Powerful Vibrancy scroll `51466` resolve through the existing XML loader and apply through the existing scroll runtime path. IMB-001, IMB-002, IMB-003, IMB-006 and any broad Imbuing redesign remained excluded.

# Final result

Feature PR #239 was squash-merged into `main` as `a356d5625e2290d6ffe45ecd6579f9dd8b7649bc`. The final feature head verified by full post-ready CI was `4acd5a6c43f73478768f8f4e85d0a51abb7b8c6a`.

The repair:

- maps Intricate Vibrancy to scroll item ID `51746`;
- maps Powerful Vibrancy to scroll item ID `51466`;
- extends the existing validator rather than adding a competing parser;
- adds executable successful-resolution, successful-application, invalid-target, occupied-category and consumption-atomicity tests;
- updates the validation report and runtime plan;
- changes no economy, effects, materials, storages, maps, `items.otb`, assets, protocol, client, schema, database or production configuration.

Cleanup PR #240 removes the active task record and preserves this final record under `tasks/archive/`.

# Acceptance criteria

- [x] Confirmed both scroll IDs on current `main` in the active Lua action.
- [x] Confirmed both missing XML mappings on current `main`.
- [x] Confirmed the exact runtime path through `getImbuementByScrollID()`.
- [x] Added minimal Intricate mapping `51746` and Powerful mapping `51466`.
- [x] Added successful resolution and application tests for both tiers.
- [x] Added invalid-target and occupied-category rejection tests.
- [x] Proved failed operations do not consume a scroll or mutate the target.
- [x] Proved success consumes exactly one scroll and applies the correct tier/duration.
- [x] Checked runtime mutation ordering and resource atomicity.
- [x] Extended the existing validator and tests.
- [x] Updated report and runtime plan.
- [x] Confirmed no excluded behavior or forbidden path changed.
- [x] Recorded local validation unavailability separately from CI.
- [x] Inspected concrete CI jobs and Linux Debug test artifact.
- [x] Inspected final changed files, diff, reviews, comments and threads.
- [x] Attempted auto-merge, then completed expected-head squash merge.
- [x] Moved the record from `tasks/active/` to `tasks/archive/` in cleanup PR #240.

# Evidence

## IDs and XML

Active Lua registers:

- Powerful range `51444..51467`, containing `51466`;
- Intricate range `51724..51747`, containing `51746`.

On base commit `f96680987955cde24d4264e9473bde70501ed534`, both Vibrancy entries lacked a `scroll` child. PR #239 added only:

```xml
<attribute key="scroll" value="51746" />
<attribute key="scroll" value="51466" />
```

Current read-only upstream `opentibiabr/canary` had the same omission and was not used as a repair source.

## Runtime path and atomicity

1. `imbuement_scrolls.lua` validates an item target and calls `player:applyImbuementScroll(target, item)`.
2. The Lua binding delegates to `Player::applyScrollImbuement`.
3. The Player path obtains a free slot.
4. It calls `getImbuementByScrollID(scrollItem->getID())`.
5. The getter queries `scrollIdMap`, populated only from XML `scroll` attributes by `Imbuements::loadFromXml()`.
6. Base resolution and `Item::canAddImbuement` run before consumption; unsupported targets and occupied categories are rejected.
7. `internalRemoveItem(scrollItem, 1)` removes exactly one scroll only after validation.
8. `setImbuement` and decay start only after successful removal.

The validator enforces the exact mappings and ordering. C++ tests execute the actual Player/Inbox/Item path.

# Feature changed files

- `data/XML/imbuements.xml`
- `tools/ai-agent/imbuement_validation.py`
- `tools/ai-agent/test_imbuement_validation.py`
- `tests/fixture/core/XML/imbuements.xml`
- `tests/unit/players/imbuements/imbuements_test.cpp`
- `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`
- `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json`
- the task record

`docs/agents/ACTIVE_WORK.md` was not edited. Temporary staging files were absent from the final feature diff.

# Local checkout and test limitation

Local checkout and local tests were unavailable because the execution environment could not resolve `github.com`. CI was separate evidence and was never described as local validation.

Attempted and blocked:

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access ... Could not resolve host: github.com
```

Not run because no local checkout existed:

```text
git clone https://github.com/blakinio/canary.git
git status --short --branch
git branch -vv
git remote -v
git worktree list
python tools/agents/task_ownership.py
python -m py_compile tools/ai-agent/imbuement_validation.py tools/ai-agent/imbuement_storage_validation.py tools/ai-agent/test_imbuement_validation.py tools/ai-agent/test_imbuement_storage_validation.py
python -m unittest discover -s tools/ai-agent -p 'test_imbuement*_validation.py' -v
python tools/ai-agent/imbuement_validation.py --repository-root . --output artifacts/IMBUEMENT_VALIDATION.json --runtime-plan artifacts/IMBUEMENT_RUNTIME_TEST_PLAN.json
python tools/ai-agent/imbuement_storage_validation.py --repository-root . --output artifacts/IMBUEMENT_STORAGE_VALIDATION.json --strict
ctest --test-dir build/linux-debug --output-on-failure -R canary_ut
```

None of these commands is recorded as locally passed.

# Tests and CI

## Final feature head

`4acd5a6c43f73478768f8f4e85d0a51abb7b8c6a`

## Feature workflows

| Workflow run ID | Job ID | Result | Coverage |
|---:|---:|---|---|
| `29236756475` | ownership job | success | Agent Task Ownership |
| `29236756588` | `86773107291` | success | focused Python compile/tests, registry/storage validators, audit/runtime-plan generation, JSON validation |
| `29236756496` | `86773107115` | success | AI Agent Tools unit and deterministic tooling validation |
| `29236786219` | autofix job | success | formatter automation, no formatting commit |
| `29236786366` | CI matrix | success | full post-ready CI |

Post-ready CI run `29236786366`:

- Detect Build Scope — success.
- Lua Tests job `86773199888` — success.
- Fast Checks job `86773199902` — success: clang-format, stylua, cmake-format, formatter diff, API docs checks, reviewdog and yamllint.
- Linux Debug job `86773515765` — success: build, runtime smoke, DB bootstrap and `Run Tests`.
- Linux Release job `86773515792` — success: build and Canary/global runtime smoke; release tests intentionally skipped.
- Windows CMake job `86773515784` — success: configure/build and runtime smoke.
- Windows Solution job `86773515783` — success: MSBuild compile.
- macOS job `86773515802` — success: configure/build and runtime smoke.
- Required — success.

Linux Debug artifact `8274081272` was downloaded and inspected:

- `ImbuementsUnitTest.ResolvesIntricateAndPowerfulVibrancyScrolls` — passed;
- `ImbuementsUnitTest.AppliesEachVibrancyScrollAndConsumesExactlyOne` — passed;
- `ImbuementsUnitTest.RejectsInvalidTargetWithoutConsumingScrollOrMutatingItem` — passed;
- `ImbuementsUnitTest.RejectsOccupiedVibrancyCategoryWithoutConsumingScroll` — passed;
- complete result: `100% tests passed, 0 tests failed out of 507`.

## Cleanup validation

Cleanup head before this final record update: `772bd8fd772e986627da3fa371d712f68088a3cc`.

- Agent Task Ownership run `29238041657`, job `86777243084` — success; ownership tooling compilation, focused tests and task/index validation passed.
- Imbuement Validation run `29238041699`, job `86777242619` — success; focused compile/tests, validators, generated JSON and artifacts passed.
- CI run `29238041959` — success:
  - Detect Build Scope job `86777244055` — success;
  - Required job `86777298233` — success;
  - Lua, Fast Checks and build jobs — intentionally skipped because the final diff is task documentation only.

This final record update triggers the same applicable checks on its new cleanup head; PR #240 must merge only after they pass.

# Review and merge gate

Feature PR #239:

- final changed-file list and full diff reviewed;
- no reviews, comments or unresolved threads;
- no blocker or forbidden file;
- auto-merge attempt returned `Pull request is in clean status`;
- expected-head squash merge completed at `a356d5625e2290d6ffe45ecd6579f9dd8b7649bc`.

Cleanup PR #240:

- final diff contains only deletion of the active record and addition of this archive record;
- `ACTIVE_WORK.md` unchanged;
- applicable checks are required on the current cleanup head before merge.

# Work log

## 2026-07-13T10:22:00+02:00

- Created `fix/imbuement-vibrancy-scrolls` from `main` commit `f96680987955cde24d4264e9473bde70501ed534`.
- Created the active task and draft PR #239 after overlap search found no conflicting Imbuement work.

## 2026-07-13T10:35:00+02:00

- Confirmed IDs, XML omission, XML-only lookup and mutation ordering.
- Added exact mappings, validator assertions, Python tests and real C++ application/atomicity tests.

## 2026-07-13T10:46:00+02:00

- Used temporary branch-only staging because no local checkout was possible.
- Failed temporary runs:
  - `29236378484`: initial apply/self-cleanup attempt;
  - `29236466671`: retry;
  - `29236517422`: `git diff --check` found four trailing-whitespace lines.
- Fixed whitespace at source; no check weakened.
- Successful patch application run `29236611125`; implementation commit `b1501511a050dcf327f17e1f84ea1c1ad577399e`.
- Removed all temporary staging files before final scope review.

## 2026-07-13T11:04:00+02:00

- Full post-ready CI `29236786366` passed on feature head `4acd5a6c43f73478768f8f4e85d0a51abb7b8c6a`.
- Inspected CTest artifact `8274081272`: all four new tests and all 507 tests passed.
- Rechecked changed files, reviews, comments and threads.

## 2026-07-13T11:07:00+02:00

- Auto-merge enablement returned clean-status error.
- Squash-merged PR #239 as `a356d5625e2290d6ffe45ecd6579f9dd8b7649bc`.

## 2026-07-13T11:20:00+02:00

- Created cleanup branch and PR #240 from merged `main`.
- Removed active task and added this archive record.
- Verified first cleanup-head ownership, Imbuement Validation and Required runs.
- Updated this record with final cleanup validation evidence.

# Decisions

| Decision | Reason | ADR |
|---|---|---|
| Add only two XML mappings | Existing runtime already supports scroll application. | none |
| Keep IMB-006 unchanged | Dream Courts storage remains outside scope. | none |
| Reuse existing validator | Prevent duplicate tooling. | none |
| Use real C++ objects | Required executable application/atomicity evidence. | none |
| Separate CI from local validation | DNS prevented local checkout. | none |
| Archive in cleanup PR #240 | Final feature head, CI and merge SHA were known only after delivery. | none |

# Failed approaches

- Local checkout/tests: blocked by DNS.
- Initial temporary self-cleaning patch workflow: failed; replaced by bounded apply plus API cleanup.
- One patch failed whitespace validation; whitespace was fixed.
- Auto-merge enablement returned clean status; immediate expected-head squash merge used.

# Remaining work

None. Cleanup PR #240 is the delivery mechanism for this completed archive record and must be merged only after applicable checks pass on its current head.

# Handoff

No work remains for IMB-004. Do not resume PR #206 or expand this task into IMB-001, IMB-002, IMB-003 or IMB-006. Any follow-up must start from current `main` with a new task, branch and PR.

# Completion

- Status: completed
- Feature branch: `fix/imbuement-vibrancy-scrolls`
- Feature PR: #239
- Feature final head: `4acd5a6c43f73478768f8f4e85d0a51abb7b8c6a`
- Feature merge commit: `a356d5625e2290d6ffe45ecd6579f9dd8b7649bc`
- Feature post-ready CI: `29236786366`, success
- Local tests: unavailable due DNS; not claimed as passed
- Cleanup branch: `docs/archive-imbuement-vibrancy-scrolls`
- Cleanup PR: #240
