---
task_id: CAN-20260713-imbuement-vibrancy-scrolls
program_id: ""
coordination_id: ""
status: validation_pending
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-vibrancy-scrolls
base_branch: main
created: 2026-07-13T10:22:00+02:00
updated: 2026-07-13T10:52:00+02:00
last_verified_commit: "fa9247068c32d46981f6a5ae73aecc5f2448c332"
risk: medium
related_issue: "IMB-004"
related_pr: "#239"
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
    - docs/agents/tasks/active/CAN-20260713-imbuement-vibrancy-scrolls.md
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

Repair only IMB-004 so Intricate Vibrancy scroll `51746` and Powerful Vibrancy scroll `51466` resolve through the existing XML loader and apply through the existing scroll runtime path. Do not change IMB-001, IMB-002, IMB-003, IMB-006 or redesign Imbuing.

# Current state

Implementation and focused draft-head validation are complete. PR #239 remains draft until the task/PR records are current; full post-ready CI, review-thread inspection, merge and archive remain.

# Acceptance criteria

- [x] Confirm both scroll IDs on current `main` in the active Lua action.
- [x] Confirm both missing XML mappings on current `main`.
- [x] Confirm the exact runtime path through `getImbuementByScrollID()`.
- [x] Add the minimal Intricate Vibrancy mapping `51746`.
- [x] Add the minimal Powerful Vibrancy mapping `51466`.
- [x] Add successful resolution tests for both IDs.
- [x] Add successful application tests on a valid boots target.
- [x] Add invalid-target rejection coverage.
- [x] Add occupied-category rejection coverage.
- [x] Assert no scroll consumption on failed operations.
- [x] Assert exactly one scroll is consumed on success.
- [x] Check mutation/resource atomicity through runtime ordering and executable tests.
- [x] Extend the existing validator instead of adding another parser.
- [x] Update `IMBUEMENT_VALIDATION_REPORT.md` and `IMBUEMENT_RUNTIME_TEST_PLAN.json`.
- [x] Confirm no economy, effect, storage, map, `items.otb`, asset or protocol changes.
- [x] Run all validation available without a local checkout and record local unavailability separately.
- [ ] Mark PR ready and verify every concrete post-ready CI job and relevant failure log on the final head.
- [ ] Inspect review threads and final changed files/diff.
- [ ] Set `last_verified_commit` to final head, enable auto-merge, squash-merge and archive this task.

# Exact evidence

## Identifiers and XML

- Active Lua registers Powerful range `51444..51467` and Intricate range `51724..51747`; therefore `51466` and `51746` are active scroll actions.
- On base commit `f96680987955cde24d4264e9473bde70501ed534`, neither Intricate nor Powerful Vibrancy had a `scroll` child.
- PR #239 adds only `<attribute key="scroll" value="51746" />` to Intricate Vibrancy and `<attribute key="scroll" value="51466" />` to Powerful Vibrancy.
- Current upstream `opentibiabr/canary` had the same omission and was used read-only; it was not treated as a fix source.

## Runtime chain and atomicity

1. `imbuement_scrolls.lua` validates an item target with Imbuement slots and calls `player:applyImbuementScroll(target, item)`.
2. The Lua Player binding delegates to `Player::applyScrollImbuement`.
3. `Player::applyScrollImbuement` obtains a free slot.
4. It calls `getImbuementByScrollID(scrollItem->getID())`; the lookup reads `scrollIdMap`, populated only from XML `scroll` children by `Imbuements::loadFromXml()`.
5. It resolves base data and calls `Item::canAddImbuement`, which rejects unsupported targets and an occupied category.
6. Only after those checks does it call `internalRemoveItem(scrollItem, 1)`.
7. Only after successful removal does it call `setImbuement` and start decay.

The validator now checks the exact two ID-to-family/tier mappings and the required ordering. The C++ fixture executes the real Player/Inbox/Item path and asserts target state and scroll count.

## Tests added

- `ResolvesIntricateAndPowerfulVibrancyScrolls`
- `AppliesEachVibrancyScrollAndConsumesExactlyOne`
- `RejectsInvalidTargetWithoutConsumingScrollOrMutatingItem`
- `RejectsOccupiedVibrancyCategoryWithoutConsumingScroll`
- Python regression `test_vibrancy_scrolls_resolve_to_exact_tiers`

# Scope review

Final changed paths at implementation cleanup head `fa9247068c32d46981f6a5ae73aecc5f2448c332`:

- `data/XML/imbuements.xml`
- `tools/ai-agent/imbuement_validation.py`
- `tools/ai-agent/test_imbuement_validation.py`
- `tests/fixture/core/XML/imbuements.xml`
- `tests/unit/players/imbuements/imbuements_test.cpp`
- `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`
- `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json`
- this task record

No workflow remains changed. `docs/agents/ACTIVE_WORK.md` was not edited. No economy, success percentage, fee, effect, material, storage, map, `items.otb`, asset, protocol, client, schema, database or production configuration path changed.

# Local checkout and tests

Local checkout and local tests are unavailable because the execution environment cannot resolve `github.com`. CI is recorded separately and is not described as local validation.

Commands attempted and blocked:

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access ... Could not resolve host: github.com
```

Commands that could not be run because no local checkout exists:

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

None of these local commands is claimed as passed.

# CI evidence

| Head / run | Workflow / job | Result | Concrete coverage |
|---|---|---|---|
| `fa9247068c32d46981f6a5ae73aecc5f2448c332`, run `29236654064` | Agent Task Ownership | success | repository ownership validation |
| `fa9247068c32d46981f6a5ae73aecc5f2448c332`, run `29236654112`, job `86772772470` | Imbuement Validation / Audit imbuement definitions and runtime wiring | success | focused Python compilation; focused unit tests; registry and storage validators; generated audit/runtime JSON; JSON validation; artifacts |
| `fa9247068c32d46981f6a5ae73aecc5f2448c332`, run `29236654386` | CI | success only for draft gate | Detect Build Scope and Required succeeded; Fast Checks, Lua Tests, Linux/Windows/macOS builds and C++ tests were skipped because PR was draft. This is not full validation. |

The post-ready CI run ID, all concrete jobs, C++ `ctest` result and final head SHA are still pending and must be recorded before merge.

# Work log

## 2026-07-13T10:22:00+02:00

- Created branch from `main` commit `f96680987955cde24d4264e9473bde70501ed534`.
- Created this task and draft PR #239 after overlap search found no active Imbuement/scroll/item-action conflict.

## 2026-07-13T10:35:00+02:00

- Confirmed both IDs, the XML omission, loader-only resolution and pre-removal validation ordering.
- Added exact XML mappings, validator assertions, Python tests and real C++ application/atomicity tests.

## 2026-07-13T10:46:00+02:00

- Used temporary branch-only staging files because the execution environment had no Git checkout. They were removed before scope review and do not appear in the final changed-file list.
- Failed patch workflow runs:
  - `29236378484`: initial combined apply/self-cleanup attempt failed;
  - `29236466671`: retry failed;
  - `29236517422`: `git diff --check` exposed four trailing-whitespace lines in the report patch.
- Fixed the actual whitespace issue instead of suppressing the check.
- Successful deterministic patch application run: `29236611125`; implementation commit `b1501511a050dcf327f17e1f84ea1c1ad577399e`.
- Removed temporary patch and workflow through GitHub API; cleanup head `fa9247068c32d46981f6a5ae73aecc5f2448c332`.

# Decisions

- Keep the fix XML-only at runtime; the existing action, loader and Player path are reused unchanged.
- Keep IMB-006 `storage=0` behavior unchanged because the exact Dream Courts storage is outside this task.
- Use real C++ runtime objects for application/consumption tests rather than a Python model.
- Treat CI as separate evidence; draft `Required` is insufficient because heavy jobs were skipped.
- No module catalogue or changelog update is required: no reusable public interface or broad behavior architecture changed.

# Failed approaches

- Local clone/test execution: blocked by DNS, exact commands above.
- Temporary patch run `29236517422`: failed correctly on trailing whitespace; fixed at source.
- No check was disabled, weakened or marked successful manually.

# Remaining work

1. Update PR body and mark #239 ready.
2. Wait for the full ready-for-review CI event and inspect every job, including Linux Debug `ctest`.
3. Repair any in-scope failure and repeat on the new final head.
4. Inspect review threads, complete changed files/diff and set final SHA/run IDs here.
5. Enable auto-merge or squash-merge after the autonomous merge gate passes.
6. Move this record to `docs/agents/tasks/archive/` in the proper cleanup step.

# Handoff

Start with PR #239 and this record. The next concrete command in a local checkout would be:

```text
python -m unittest discover -s tools/ai-agent -p 'test_imbuement*_validation.py' -v
```

Do not resume PR #206 or the archived Forgotten Knowledge task. Do not expand scope to IMB-001, IMB-002, IMB-003 or IMB-006.
