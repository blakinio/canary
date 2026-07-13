---
task_id: CAN-20260713-imbuement-vibrancy-scrolls
program_id: ""
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-vibrancy-scrolls
base_branch: main
created: 2026-07-13T10:22:00+02:00
updated: 2026-07-13T10:22:00+02:00
last_verified_commit: "f96680987955cde24d4264e9473bde70501ed534"
risk: medium
related_issue: "IMB-004"
related_pr: ""
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
  shared:
    - .github/workflows/imbuement-validation.yml
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - data-otservbr-global/scripts/actions/object/imbuement_scrolls.lua
    - src/creatures/players/imbuements/imbuements.cpp
    - src/creatures/players/imbuements/imbuements.hpp
    - src/lua/functions/creatures/player/player_functions.cpp
    - src/creatures/players/player.cpp
    - src/items/item.cpp
    - src/items/item.hpp
modules_touched:
  - Imbuement XML registry
  - Imbuement deterministic validation
  - Imbuement focused tests
reuses:
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/imbuement_storage_validation.py
  - tests/shared/imbuements/imbuements_test_fixture.hpp
  - .github/workflows/imbuement-validation.yml
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Repair only IMB-004 so Intricate Vibrancy scroll `51746` and Powerful Vibrancy scroll `51466` resolve through the active XML loader and apply through the existing scroll path, with focused resolution, target-rejection and consumption-atomicity regression evidence.

# Acceptance criteria

- [x] Confirm both candidate IDs on current `main` in the active Lua action.
- [x] Confirm the missing XML mappings on current `main`.
- [x] Confirm the runtime chain through `getImbuementByScrollID()` on current `main`.
- [ ] Add the minimal Intricate Vibrancy XML mapping.
- [ ] Add the minimal Powerful Vibrancy XML mapping.
- [ ] Add successful resolution tests for both scroll IDs.
- [ ] Add successful application coverage on a valid target.
- [ ] Add invalid-target coverage.
- [ ] Add occupied-category coverage.
- [ ] Prove failed operations do not consume a scroll.
- [ ] Prove a successful operation consumes exactly one scroll.
- [ ] Check mutation/resource atomicity.
- [ ] Extend the existing validator; do not add a competing parser.
- [ ] Update `IMBUEMENT_VALIDATION_REPORT.md` and the runtime plan where applicable.
- [ ] Verify no economy, effect, storage, map, `items.otb`, asset or protocol changes.
- [ ] Run all validation available in the execution environment and record unavailable local checks separately.
- [ ] Verify every concrete CI job and relevant log on the final head.
- [ ] Satisfy the autonomous merge gate, squash-merge and archive this task.

# Confirmed context

- Branch base and current `main` at task creation: `f96680987955cde24d4264e9473bde70501ed534`.
- `data-otservbr-global/scripts/actions/object/imbuement_scrolls.lua` registers Powerful IDs `51444..51467` and Intricate IDs `51724..51747`; therefore `51466` and `51746` are active action IDs.
- The same action rejects a non-item target and a target with zero Imbuement slots before calling `player:applyImbuementScroll(target, item)`.
- `data/XML/imbuements.xml` contains no `scroll` child for Intricate or Powerful Vibrancy, while adjacent Intricate/Powerful families do contain one.
- `Imbuements::loadFromXml()` reads only XML `scroll` attributes into `Imbuement::scrollId`, then populates `scrollIdMap`; `getImbuementByScrollID()` only queries that map.
- Lua `Player.applyImbuementScroll` delegates to `Player::applyScrollImbuement`.
- `Player::applyScrollImbuement` validates free slot, XML resolution, base entry and `Item::canAddImbuement` before `internalRemoveItem(scrollItem, 1)`; the target is mutated only after that exact one-item removal succeeds.
- The existing deterministic baseline already records `Vibrancy: (None, 51746, 51466)` and currently reports exactly those registered-but-unmapped IDs.
- The current external Imbuing reference observed on 2026-07-13 states that Intricate and Powerful Imbuements are available as scrolls and that Vibrancy applies to boots; the numeric IDs are not taken from that prose alone.
- Read-only inspection of current upstream `opentibiabr/canary` shows the same missing Vibrancy XML attributes, so upstream is not a repair source.
- Excluded findings remain IMB-001, IMB-002, IMB-003 and IMB-006.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Imbuement audit #166 | XML parser, scroll-range correlation, runtime markers, tests and report | `tools/ai-agent/imbuement_validation.py` | Already detects IMB-004 conservatively. |
| Storage repair #206 / cleanup #237 | Current main baseline and lifecycle precedent | archived task and report | Completed, merged and must not be resumed. |
| Imbuements C++ fixture | Loader-level registry tests | `tests/shared/imbuements/imbuements_test_fixture.hpp` | Existing fixture reloads the real XML loader. |
| Focused workflow | Python compilation, focused unit tests, validators and artifacts | `.github/workflows/imbuement-validation.yml` | Must be extended only if existing jobs do not cover required tests. |

# Ownership and overlap check

- Program record: none required for this bounded follow-up.
- Open PRs inspected: live open PRs and searches for `imbuement`, `imbuing`, `scroll`, and `item action`; no matching open PR exists. Unrelated open PRs include #238, #234, #230 and #224.
- Active tasks inspected: `ACTIVE_WORK.md` as a read-only snapshot plus live PR/task searches; no active Imbuement/scroll/item-action ownership overlaps were found.
- Ownership checker result: not run locally because no checkout is available.
- Exclusive claims: only the focused XML, validator, fixture/test and durable documentation paths listed above.
- Shared claims: focused workflow only if concrete CI coverage must be added.
- Read-only dependencies: active Lua action, loader, Lua binding, Player application path and Item eligibility path.
- Overlaps: none found.
- Resolution: proceed on this dedicated branch; do not edit `docs/agents/ACTIVE_WORK.md`.

# Current state

Task claimed from current `main`; no runtime/data implementation change has been made yet. Draft PR is the next action.

# Plan

1. Publish the task branch and open a draft PR.
2. Inspect `Item::canAddImbuement`, item mutation helpers and existing C++ test infrastructure to choose executable application/atomicity coverage.
3. Add exactly two XML `scroll` attributes.
4. Extend the existing validator and focused tests; add or wire C++ coverage where required.
5. Update the report/runtime plan and task after each result.
6. Inspect the complete diff, mark ready, verify concrete post-ready CI jobs/logs on the final SHA, merge and archive.

# Work log

## 2026-07-13T10:22:00+02:00

- Changed: created `fix/imbuement-vibrancy-scrolls` from `main` and claimed this task record.
- Learned: both IDs are active in Lua; both XML mappings are absent; runtime resolution is XML-map-only; scroll removal is ordered after eligibility validation and before target mutation.
- Failed/blocked: local Git checkout and local tests are unavailable because the execution environment cannot resolve `github.com`.
- Result: scope and runtime defect are confirmed; implementation has not started.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add only the two missing XML mappings | Existing loader and action already support the behavior; no runtime redesign is justified. | none |
| Keep IMB-006 storage bypass unchanged | Exact Dream Courts completion storage is outside this task and remains unresolved. | none |
| Treat CI and local validation as separate evidence | The environment lacks DNS; CI cannot be reported as local execution. | none |
| Extend existing validator and C++ fixture | Repository catalogue and user scope prohibit duplicate parsing/tooling. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `data/XML/imbuements.xml` | exclusive | Two exact scroll mappings | planned |
| `tools/ai-agent/imbuement_validation.py` | exclusive | Exact resolved mapping/runtime contract | planned |
| `tools/ai-agent/test_imbuement_validation.py` | exclusive | Deterministic regression | planned |
| `tests/fixture/core/XML/imbuements.xml` | exclusive | Real loader fixture for both tiers | planned |
| `tests/unit/players/imbuements/imbuements_test.cpp` | exclusive | C++ loader resolution tests | planned |
| `.github/workflows/imbuement-validation.yml` | shared | Focused CI coverage if required | under review |
| report/runtime plan/task | exclusive | Durable evidence and handoff | in progress |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| environment | `git ls-remote https://github.com/blakinio/canary.git HEAD` | blocked | `fatal: unable to access ... Could not resolve host: github.com` |
| environment | `getent hosts github.com` | blocked | no DNS result |
| not available | `git clone https://github.com/blakinio/canary.git` | not-run | checkout cannot begin without DNS |
| not available | `git status --short --branch`; `git branch -vv`; `git remote -v`; `git worktree list` | not-run | no local checkout |
| not available | `python tools/agents/task_ownership.py` | not-run | no local checkout |
| not available | `python -m py_compile tools/ai-agent/imbuement_validation.py tools/ai-agent/imbuement_storage_validation.py tools/ai-agent/test_imbuement_validation.py tools/ai-agent/test_imbuement_storage_validation.py` | not-run | no local checkout |
| not available | `python -m unittest discover -s tools/ai-agent -p 'test_imbuement*_validation.py' -v` | not-run | no local checkout |
| not available | `python tools/ai-agent/imbuement_validation.py --repository-root . --output artifacts/IMBUEMENT_VALIDATION.json --runtime-plan artifacts/IMBUEMENT_RUNTIME_TEST_PLAN.json` | not-run | no local checkout |
| not available | `python tools/ai-agent/imbuement_storage_validation.py --repository-root . --output artifacts/IMBUEMENT_STORAGE_VALIDATION.json --strict` | not-run | no local checkout |

Never write `passed` without verification on the stated commit. CI workflow IDs, exact jobs, tests and logs will be added only after they run on the implementation head.

# Failed approaches and dead ends

- Direct local Git access cannot be used in this execution environment because `github.com` DNS resolution fails.
- Current upstream XML contains the same omission and therefore cannot be copied as evidence of a fix.

# Risks and compatibility

- Runtime: low implementation size, medium validation risk because scroll consumption mutates inventory and target state.
- Data/migration: XML-only registry mapping; no database/schema migration.
- Security: no security-sensitive surface.
- Backward compatibility: adds resolution for two already-registered item actions; no removal or identifier reassignment.
- Cross-repo rollout: none; no protocol/client contract change.
- Rollback: revert the two XML attributes and corresponding tests/docs.

# Remaining work

1. Open the draft PR and record its number.
2. Prove executable application/invalid-target/occupied-category/consumption coverage through existing test infrastructure or record a precise blocker.
3. Implement and validate the two mappings.

# Handoff

## Start here

Read this record, then inspect the draft PR and current branch head. Do not resume PR #206 or its archived branch/task.

## Do not repeat

The Lua ranges, missing XML attributes and loader path are already confirmed above.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/agents/REPOSITORY_MAP.md`
- `docs/agents/KNOWN_RISKS.md`
- `docs/agents/BUILD_TEST_MATRIX.md`
- `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`
- `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json`
- active action, loader, Player application path and focused tests/workflow

## Open questions

- Which existing test target can execute `Player::applyScrollImbuement` with a real target and removable scroll without introducing a new test framework?

# Completion

- Final status: in progress
- PR: pending
- Merge commit: pending
- Program record updated: not applicable
- Catalogue updated: not required unless a reusable interface changes
- Changelog updated: pending scope review
- Archived at: pending
