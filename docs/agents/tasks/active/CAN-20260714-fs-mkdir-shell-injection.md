---
task_id: CAN-20260714-fs-mkdir-shell-injection
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-006
status: active
agent: "GPT-5.6 Thinking"
branch: security/fs-mkdir-shell-free-current
base_branch: main
created: 2026-07-14T08:00:00+02:00
updated: 2026-07-14T10:20:00+02:00
last_verified_commit: "bac8c5d6fdb7deb3d7e0e1e51bcd541fe11af8e2"
risk: high
related_issue: ""
related_pr: "#317"
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
    - docs/agents/CHANGELOG.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
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
  - existing bounded self-removing audit/materialization workflow pattern
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

- [x] Full current-repository inventory of definitions, call sites and path provenance is recorded with exact files and lines.
- [x] Existing native filesystem facilities and Lua registration surfaces were inspected before implementation.
- [x] CrystalServer commit `891685169745e46f665069edcc35847f0704aa21` is evidence only; its denylist-plus-shell patch was not copied.
- [x] A standalone Lua regression fails if the wrapper invokes `os.execute`.
- [x] A C++ regression invokes the real Lua binding and covers directory creation, existing paths, files, empty input and a shell-metacharacter payload without creating a marker.
- [x] `FS.mkdir` remains single-level and `FS.mkdir_p` remains recursive; success/error returns are preserved.
- [x] The implementation performs no shell execution and uses `std::filesystem` with `std::error_code`.
- [x] New Lua methods are present in `docs/lua-api/lua_api.json`; both documentation validators pass.
- [ ] Exact-current-head formatter, Lua tests and full runtime CI pass on PR #317.
- [x] No protocol, client, schema, migration, map, item, asset or production configuration changes.
- [x] Program, changelog, module catalogue and handoff records are synchronized.
- [ ] Autonomous merge gate is satisfied.

# Evidence and threat classification

- Initial baseline: `42c0afa817b60f3b888c46b690b286cd224a3062`.
- Current-main transfer baseline: `d88e7f354eb5b33068cdded7696e9cdb89b05268`.
- Baseline `data/libs/functions/fs.lua` constructed `mkdir` through `os.execute`.
- Audit reports:
  - `artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md`;
  - `artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json`.
- Audit scanned 6,857 tracked files and found the two production uses in player-rule and bug-report paths.
- Default `validateName` accepts only letters, apostrophes and spaces, so default character creation does not directly supply shell syntax.
- The general Lua helper still accepted arbitrary custom/DB/script-derived paths; the verified defect is an unsafe command-execution primitive, not a claim of default-client remote RCE.
- No existing shell-free Lua directory binding was present; `std::filesystem` was already used throughout maintained server code.

# Final source design

- `FileSystem.createDirectory(path)` is registered in existing `GlobalFunctions` and calls `std::filesystem::create_directory`.
- `FileSystem.createDirectories(path)` calls `std::filesystem::create_directories`.
- Both reject non-string inputs, avoid exceptions through `std::error_code`, accept existing directories and return `false, errorMessage` for failures.
- `FS.mkdir` and `FS.mkdir_p` are compatibility wrappers; `FS.mkdir_p("")` remains a no-op success.
- No new C++ source unit or Visual Studio/CMake registration is required.

# Work log

## 2026-07-14T08:00:00+02:00

- Created the dedicated task and predecessor draft PR #310 after refreshing main, open PRs and ownership.
- Confirmed direct shell construction and rejected the upstream denylist design.
- Local Git/build remained unavailable because DNS could not resolve `github.com`.

## 2026-07-14T09:15:00+02:00

- Published deterministic Markdown/JSON evidence; all temporary audit runners removed themselves.
- Corrected ignored-artifact staging and trailing whitespace without weakening `git diff --check`.
- Classified `CS-006` as `VALID_FIX_MISSING`.

## 2026-07-14T09:30:00+02:00

- Replaced shell-backed wrappers with native methods and added focused Lua/C++ tests.
- Exact-anchor apply run `29314889189` passed `luajit tests/lua/test_fs.lua`, the no-`os.execute` check, the changed-file allowlist and `git diff --check` on `c07bb271f288eae53824437b102d37cafe9751dd`.

## 2026-07-14T10:00:00+02:00

- Ready-state CI `1691` correctly stopped on missing committed Lua API catalogue entries after formatting and standalone Lua tests passed.
- Added deterministic `FileSystem` entries and verified `tools/check_lua_api_quality.py` plus `tools/check_lua_api_binding_docs.py --base origin/main` in workflow `29315799252`.

## 2026-07-14T10:10:00+02:00

- Full CI `1714` (`29316118599`) passed on reviewed source commit `6196c95493171968f8f13530f009d0b03e9ee8ee`.
- Passed surfaces included Fast Checks, standalone Lua tests, Linux release/debug builds, generated Lua API synchronization, Canary/global smoke tests, schema import, Linux `Run Tests`, Windows CMake/Solution, macOS and Docker.
- The C++ regression invoking the real binding therefore compiled and executed successfully.

## 2026-07-14T10:20:00+02:00

- `main` advanced after the green run and overlapped only shared changelog/catalogue paths.
- Closed predecessor PR #310 without merge and created current-main PR #317 from exact main `d88e7f354eb5b33068cdded7696e9cdb89b05268`.
- A bounded materializer imported the reviewed runtime/tests/API/evidence, merged the current shared documentation, ran focused Lua/documentation/no-shell gates and removed itself.
- PR #317 now contains exactly thirteen intended files and no temporary workflow.
- Result: all final checks and merge ownership belong exclusively to PR #317.

# Decisions

| Decision | Reason |
|---|---|
| Keep `CS-006` separate from `CS-007` | Filesystem shell execution and deserialization have different threat models and compatibility gates. |
| Remove the shell instead of filtering characters | A denylist is incomplete and retains command interpretation. |
| Use existing `GlobalFunctions` | It avoids a second subsystem and new maintained build registrations while exposing only two narrow methods. |
| Preserve `FS` wrappers | Existing datapack and custom scripts keep their public API. |
| Use `std::error_code` | Directory failures remain visible to Lua without exceptions crossing the binding boundary. |
| Catalogue the methods explicitly | Repository policy requires every new registration in the committed Lua API catalogue. |
| Transfer to fresh current-main PR #317 | Avoid merging a conflicted historical branch; preserve current shared docs and revalidate the exact final tree. |
| Do not claim default-client RCE | Standard name validation blocks shell syntax; broader custom/DB/script input remains the relevant boundary. |

# Validation

| Commit/run | Check | Result |
|---|---|---|
| `42c0afa817b60f3b888c46b690b286cd224a3062` | local Git/worktree/build preflight | unavailable; DNS failure, no pass claimed |
| `4695d10158386da1af517a233bdb3e5cda0d2c23` / `29314149659` | deterministic audit publication | passed |
| `c07bb271f288eae53824437b102d37cafe9751dd` / `29314889189` | exact implementation, focused Lua test, no-shell check, allowlist, `git diff --check` | passed |
| `2f533d00ee0624ead7a13c05dfdc7d6ea60d496c` / CI `1691` | first Ready gate | expected documentation failure only; builds skipped |
| `28e7c3638fb3a4b420d81cc0cda8f9fce797daa3` / `29315799252` | catalogue update and both documentation validators | passed |
| `6196c95493171968f8f13530f009d0b03e9ee8ee` / CI `1714` (`29316118599`) | complete affected matrix and `Run Tests` | passed |
| `bac8c5d6fdb7deb3d7e0e1e51bcd541fe11af8e2` | current-main materialization for PR #317 | focused gates passed; full exact-head CI pending |

Never record `passed` without verification on the stated commit.

# Risks and compatibility

- Security: shell interpretation is removed from the filesystem helper boundary.
- Compatibility: spaces, native separators, absolute/drive roots and recursive creation are delegated to `std::filesystem` rather than reconstructed manually.
- Existing-directory behavior remains successful.
- Invalid input and filesystem errors remain explicit boolean/error returns.
- Cross-repository impact: none.
- Rollback: revert the eventual PR #317 merge; predecessor PR #310 remains closed and unmerged.

# Remaining work

1. Verify ownership and draft checks on the connector-authored PR #317 head.
2. Mark PR #317 Ready and require fresh full Linux C++ build/tests plus all selected platform gates and `Required`.
3. Review comments, reviews, threads and final diff; enable auto-merge only on the unchanged validated SHA.
4. Archive this task and close `CS-006` in a separate cleanup PR.

# Handoff

Read this task, PR #317, predecessor PR #310 only for historical evidence, both audit reports, `data/libs/functions/fs.lua`, `global_functions.*`, `docs/lua-api/lua_api.json` and both focused tests.

Do not restore shell execution, do not replace it with a denylist, do not merge `table.unserialize` into this task, and do not treat a skipped or `action_required` run as C++ validation.

# Completion

- Final status: active
- PR: #317
- Current reviewed current-main head: `bac8c5d6fdb7deb3d7e0e1e51bcd541fe11af8e2`
- Predecessor PR: #310, closed without merge
- Merge commit:
- Program record updated: yes, active task and `VALID_FIX_MISSING`
- Catalogue updated: yes, active reusable binding
- Changelog updated: yes
- Archived at: pending
