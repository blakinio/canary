---
task_id: CAN-20260714-fs-mkdir-shell-injection
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-006
status: completed
agent: "GPT-5.6 Thinking"
branch: security/fs-mkdir-shell-free-final
base_branch: main
created: 2026-07-14T08:00:00+02:00
updated: 2026-07-14T12:30:00+02:00
completed: 2026-07-14T12:20:00+02:00
last_verified_commit: "70f6930647d818edfdf0a30b745aabe8d4fdaa29"
risk: high
related_issue: ""
related_pr: "#326"
depends_on:
  - "CAN-PROGRAM-CRYSTALSERVER-COMPARISON Stage 1 / PR #291"
blocks: []
owned_paths:
  exclusive:
    - data/libs/functions/fs.lua
    - src/lua/functions/core/game/global_functions.cpp
    - src/lua/functions/core/game/global_functions.hpp
    - tests/lua/test_fs.lua
    - tests/unit/lua/filesystem_functions_test.cpp
    - tests/unit/lua/CMakeLists.txt
    - docs/lua-api/lua_api.json
    - artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md
    - artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json
    - docs/agents/tasks/archive/CAN-20260714-fs-mkdir-shell-injection.md
  shared:
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - docs/agents/CHANGELOG.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
modules_touched:
  - Lua filesystem helper boundary
reuses:
  - existing `GlobalFunctions` Lua registration surface
  - engine-standard `std::filesystem` operations
  - existing standalone Lua and `canary_ut` infrastructure
public_interfaces:
  - "FS.mkdir(path) -> success[, errorMessage]"
  - "FS.mkdir_p(path) -> success[, errorMessage]"
  - "FileSystem.createDirectory(path) -> success[, errorMessage]"
  - "FileSystem.createDirectories(path) -> success[, errorMessage]"
cross_repo_tasks: []
---

# Completion state

CS-006 is complete and merged.

- Feature PR: #326.
- Final feature head: `4a3c42113319550ca24956acb449501416cbf9a3`.
- Squash merge: `70f6930647d818edfdf0a30b745aabe8d4fdaa29`.
- Historical PRs #310 and #317: closed without merge; do not reopen.
- Final implementation scope: exactly eleven runtime, test, API, program/task and audit-evidence paths.
- Cleanup branch: `docs/archive-cs006-fs-mkdir`.
- Rollback: revert `70f6930647d818edfdf0a30b745aabe8d4fdaa29`; no migration, database, map, item, asset, protocol or client cleanup is required.

# Delivered behavior

- `FS.mkdir` remains single-level and `FS.mkdir_p` remains recursive.
- Both wrappers delegate to native `FileSystem.createDirectory`/`createDirectories` methods.
- Native methods use `std::filesystem` with `std::error_code`; no shell command is built or executed.
- Existing-directory success and boolean/error return behavior are preserved.
- Empty recursive paths remain no-op success.
- Non-string input, existing files and filesystem errors remain explicit failures.
- The implementation does not claim default-client remote RCE because standard character names exclude shell syntax; it removes the unsafe general helper boundary for custom/database/script-derived paths.
- CS-007 `table.unserialize` remains independent and unresolved by this work.

# Evidence and validation

- Deterministic audit scanned 6,857 tracked files and recorded definitions, call sites and path provenance in the two committed CS-006 reports.
- The CrystalServer denylist-plus-shell patch was evidence only and was not copied.
- Standalone Lua regression fails on any `os.execute` call.
- C++ regression invokes the real Lua binding and verifies directory creation, existing paths, files, empty input, literal shell metacharacters and absence of marker creation.
- Final head `4a3c42113319550ca24956acb449501416cbf9a3` passed Agent Task Ownership run 705, Achievement Validation run 244, autofix run 1208 and full CI run 1811 (`29324115804`).
- Fast Checks, formatter, Reviewdog, yamllint, Lua API validators, standalone Lua, Linux release/debug, Windows CMake/Solution, macOS, Docker, Canary smoke, schema import and Linux debug `Run Tests` all passed.
- Final review found no reviews, comments or unresolved threads.
- Green CI proves only the executed repository checks; no local or production-runtime result is claimed.

# Acceptance criteria

- [x] Shell execution removed rather than filtered.
- [x] Public compatibility wrappers preserved.
- [x] Lua and real-binding C++ regressions merged.
- [x] Lua API catalogue updated.
- [x] Exact final scope reviewed.
- [x] Full exact-head CI passed.
- [x] PR #326 squash-merged.
- [x] Historical PRs closed without merge.
- [x] Task moved from `tasks/active` to `tasks/archive` in a separate lifecycle PR.

# Handoff

CS-006 requires no further implementation. Preserve the native filesystem boundary and both regression layers. Do not restore shell execution or substitute a denylist. Select any later CrystalServer candidate only through a fresh bounded task and current ownership/contract review.

# Completion

- Final status: completed
- Feature PR: #326
- Feature merge commit: `70f6930647d818edfdf0a30b745aabe8d4fdaa29`
- Cleanup PR: pending
- Archived at: `docs/agents/tasks/archive/CAN-20260714-fs-mkdir-shell-injection.md`
