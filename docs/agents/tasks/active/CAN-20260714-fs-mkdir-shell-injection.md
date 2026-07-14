---
task_id: CAN-20260714-fs-mkdir-shell-injection
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-006
status: active
agent: "GPT-5.6 Thinking"
branch: security/fs-mkdir-shell-free-final
base_branch: main
created: 2026-07-14T08:00:00+02:00
updated: 2026-07-14T12:05:00+02:00
last_verified_commit: "3c78b9b3f3e1e6c4f1e504bf63d5db2b26299405"
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
    - docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md
    - artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md
    - artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json
  shared:
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/CHANGELOG.md
    - docs/agents/MODULE_CATALOG.md
    - data/events/scripts/player.lua
    - src/utils/tools.cpp
    - .github/workflows/reusable-tests-lua.yml
modules_touched:
  - Lua filesystem helper boundary
reuses:
  - existing `GlobalFunctions` Lua registration surface
  - engine-standard `std::filesystem` operations
  - existing standalone Lua and `canary_ut` test infrastructure
  - existing Lua API catalogue and validators
public_interfaces:
  - "FS.mkdir(path) -> success[, errorMessage]"
  - "FS.mkdir_p(path) -> success[, errorMessage]"
  - "FileSystem.createDirectory(path) -> success[, errorMessage]"
  - "FileSystem.createDirectories(path) -> success[, errorMessage]"
cross_repo_tasks: []
---

# Goal

Remove command-shell execution from `FS.mkdir` and `FS.mkdir_p` through the smallest architecture-native implementation while preserving the existing Lua compatibility contract.

# Acceptance criteria

- [x] Full repository inventory of definitions, call sites and path provenance is recorded with exact files and lines.
- [x] CrystalServer commit `891685169745e46f665069edcc35847f0704aa21` is evidence only; its denylist-plus-shell patch was not copied.
- [x] A standalone Lua regression fails if the wrapper invokes `os.execute`.
- [x] A C++ regression invokes the real Lua binding and covers directory creation, existing paths, files, empty input and a shell-metacharacter payload without creating a marker.
- [x] `FS.mkdir` remains single-level and `FS.mkdir_p` remains recursive; success/error returns are preserved.
- [x] The implementation performs no shell execution and uses `std::filesystem` with `std::error_code`.
- [x] New Lua methods are present in `docs/lua-api/lua_api.json`.
- [ ] Exact-head ownership, formatter, Lua tests and full runtime/platform CI pass on PR #326.
- [x] No protocol, client, schema, migration, map, item, asset or production configuration changes.
- [ ] Autonomous merge gate is satisfied.

# Evidence and threat classification

- Initial baseline: `42c0afa817b60f3b888c46b690b286cd224a3062`.
- Current final branch baseline: `9b04ab3ef3dfbc9440274d63e15e6102c5501d85`.
- Baseline `data/libs/functions/fs.lua` constructed `mkdir` through `os.execute`.
- Audit reports:
  - `artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md`;
  - `artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json`.
- The audit scanned 6,857 tracked files and found two production uses in player-rule and bug-report paths.
- Default name validation blocks shell syntax, so this task does not claim default-client remote RCE.
- The verified defect is a general unsafe command-execution primitive for arbitrary custom, database or script-derived paths.

# Final design

- `FileSystem.createDirectory(path)` calls `std::filesystem::create_directory`.
- `FileSystem.createDirectories(path)` calls `std::filesystem::create_directories`.
- Both reject non-string input, avoid exceptions through `std::error_code`, accept existing directories and return `false, errorMessage` for failures.
- `FS.mkdir` and `FS.mkdir_p` remain compatibility wrappers; `FS.mkdir_p("")` remains a no-op success.
- No new C++ source unit or Visual Studio registration is required.

# Delivery history

- PR #310: initial implementation branch; closed without merge after main advanced.
- PR #317: current-main replacement; full CI `1736` passed on `925602f6a85414caf1bbe59407a8318162aa3f53`, then main advanced again and changed shared governance files; closed without merge.
- PR #326: final branch created directly from current main `9b04ab3ef3dfbc9440274d63e15e6102c5501d85`.
- Materializer run `29323941098` succeeded and removed itself.
- PR #326 contains exactly eleven intended runtime, test, API, task/program and audit paths. `CHANGELOG.md` and `MODULE_CATALOG.md` are intentionally deferred to the cleanup/archive PR.

# Validation history

| Commit/run | Check | Result |
|---|---|---|
| `4695d10158386da1af517a233bdb3e5cda0d2c23` / `29314149659` | deterministic audit publication | passed |
| `c07bb271f288eae53824437b102d37cafe9751dd` / `29314889189` | focused Lua, no-shell check, allowlist and `git diff --check` | passed |
| `6196c95493171968f8f13530f009d0b03e9ee8ee` / CI `1714` | complete affected matrix and `Run Tests` | passed |
| `925602f6a85414caf1bbe59407a8318162aa3f53` / CI `1736` | current-main full matrix, platform builds and binding regression | passed |
| `3c78b9b3f3e1e6c4f1e504bf63d5db2b26299405` / `29323941098` | final current-main materialization and exact 11-file scope | passed |

Never record `passed` without verification on the stated commit.

# Risks and compatibility

- Security: shell interpretation is removed from the filesystem helper boundary.
- Compatibility: spaces, native separators, absolute/drive roots and recursive creation are delegated to `std::filesystem`.
- Existing-directory behavior remains successful.
- Invalid input and filesystem errors remain explicit boolean/error returns.
- Cross-repository impact: none.
- Rollback: revert the eventual PR #326 merge; PRs #310 and #317 remain closed and unmerged.

# Remaining work

1. Verify draft ownership and exact 11-file scope on the connector-authored PR #326 head.
2. Mark PR #326 Ready and require fresh full Linux C++ tests plus all selected platform gates and `Required`.
3. Review comments, reviews, threads and final diff; merge only the unchanged validated SHA.
4. Archive this task and close `CS-006` in a separate cleanup PR that also updates `CHANGELOG.md` and `MODULE_CATALOG.md` from then-current main.

# Handoff

Read this task, PR #326, both audit reports, `data/libs/functions/fs.lua`, `global_functions.*`, `docs/lua-api/lua_api.json` and both focused tests. PRs #310 and #317 are historical evidence only.

Do not restore shell execution, do not replace it with a denylist, do not merge `table.unserialize` into this task, and do not treat skipped or `action_required` jobs as C++ validation.

# Completion

- Final status: active
- PR: #326
- Current materialized head: `3c78b9b3f3e1e6c4f1e504bf63d5db2b26299405`
- Predecessors: #310 and #317, closed without merge
- Merge commit:
- Program record updated: yes, active task and `VALID_FIX_MISSING`
- Catalogue/changelog cleanup: pending separate PR
- Archived at: pending
