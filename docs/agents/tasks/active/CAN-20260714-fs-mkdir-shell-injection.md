---
task_id: CAN-20260714-fs-mkdir-shell-injection
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-006
status: active
agent: "GPT-5.6 Thinking"
branch: security/fs-mkdir-shell-free-current
base_branch: main
created: 2026-07-14T08:00:00+02:00
updated: 2026-07-14T10:00:00+02:00
last_verified_commit: "28e7c3638fb3a4b420d81cc0cda8f9fce797daa3"
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
  - existing bounded self-removing audit/patch workflow pattern
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
- [ ] Exact-current-head formatter, Lua tests and full runtime CI pass.
- [x] No protocol, client, schema, migration, map, item, asset or production configuration changes.
- [x] Program, changelog, module catalogue and handoff records are synchronized.
- [ ] Autonomous merge gate is satisfied.

# Evidence and threat classification

- Baseline task commit: `42c0afa817b60f3b888c46b690b286cd224a3062`.
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

- Created the dedicated branch, task and draft PR #310 after refreshing main, open PRs and ownership.
- Confirmed direct shell construction and rejected the upstream denylist design.
- Local Git/build remained unavailable because DNS could not resolve `github.com`.

## 2026-07-14T09:15:00+02:00

- Published deterministic Markdown/JSON evidence; all temporary audit runners removed themselves.
- Corrected ignored-artifact staging and trailing whitespace without weakening `git diff --check`.
- Classified `CS-006` as `VALID_FIX_MISSING`.

## 2026-07-14T09:30:00+02:00

- Replaced shell-backed wrappers with native methods and added focused Lua/C++ tests.
- Exact-anchor apply run `29314889189` passed `luajit tests/lua/test_fs.lua`, the no-`os.execute` check, the changed-file allowlist and `git diff --check` on `c07bb271f288eae53824437b102d37cafe9751dd`.

## 2026-07-14T09:45:00+02:00

- Consolidated competing implementation shapes and retained one `FileSystem` table in the already compiled `GlobalFunctions` module.
- Strengthened native functions with non-string argument checks and changed the C++ regression to invoke the real Lua binding.
- Removed all temporary finalizer files; final source diff contains only intended runtime, test, docs and evidence paths.

## 2026-07-14T10:00:00+02:00

- Ready-state CI `1691` passed formatting, Lua API quality and standalone Lua tests, then correctly stopped because the two new methods were absent from `docs/lua-api/lua_api.json`.
- Added deterministic `FileSystem` class entries in alphabetical order and ran `tools/check_lua_api_quality.py` plus `tools/check_lua_api_binding_docs.py --base origin/main`; both passed in workflow `29315799252`.
- The documentation updater removed itself; bot-authored head `28e7c3638fb3a4b420d81cc0cda8f9fce797daa3` reported `action_required` with no standard jobs, so no CI result is claimed for that head.

# Decisions

| Decision | Reason |
|---|---|
| Keep `CS-006` separate from `CS-007` | Filesystem shell execution and deserialization have different threat models and compatibility gates. |
| Remove the shell instead of filtering characters | A denylist is incomplete and retains command interpretation. |
| Use existing `GlobalFunctions` | It avoids a second subsystem and new maintained build registrations while exposing only two narrow methods. |
| Preserve `FS` wrappers | Existing datapack and custom scripts keep their public API. |
| Use `std::error_code` | Directory failures remain visible to Lua without exceptions crossing the binding boundary. |
| Catalogue the methods explicitly | Repository policy requires every new registration in the generated Lua API catalogue before build execution. |
| Do not claim default-client RCE | Standard name validation blocks shell syntax; broader custom/DB/script input remains the relevant boundary. |

# Validation

| Commit/run | Check | Result |
|---|---|---|
| `42c0afa817b60f3b888c46b690b286cd224a3062` | local Git/worktree/build preflight | unavailable; DNS failure, no pass claimed |
| `4695d10158386da1af517a233bdb3e5cda0d2c23` / `29314149659` | deterministic audit publication | passed |
| `c07bb271f288eae53824437b102d37cafe9751dd` / `29314889189` | exact implementation, focused Lua test, no-shell check, allowlist, `git diff --check` | passed |
| `c9ca0e38ec73f5cac9c70be210be3835247d78bb` / CI `1674` | draft Required | insufficient; build/test jobs skipped |
| `2f533d00ee0624ead7a13c05dfdc7d6ea60d496c` / CI `1691` | first Ready gate | Lua passed; Fast Checks failed only on missing Lua API catalogue entries; builds correctly skipped |
| `28e7c3638fb3a4b420d81cc0cda8f9fce797daa3` / `29315799252` | catalogue update and both documentation validators | passed |

Never record `passed` without verification on the stated commit.

# Risks and compatibility

- Security: shell interpretation is removed from the filesystem helper boundary.
- Compatibility: spaces, native separators, absolute/drive roots and recursive creation are delegated to `std::filesystem` rather than reconstructed manually.
- Existing-directory behavior remains successful.
- Invalid input and filesystem errors remain explicit boolean/error returns.
- Cross-repository impact: none.
- Rollback: revert PR #310; no migration or irreversible state exists.

# Remaining work

1. Run exact-head ownership, formatter, Lua and full C++ CI from this connector-authored commit.
2. Repair only concrete failures without weakening gates.
3. Review comments, reviews, threads and final diff; enable auto-merge only on the unchanged validated SHA.
4. Archive this task and close `CS-006` in a separate cleanup PR.

# Handoff

Read this task, PR #310, both audit reports, `data/libs/functions/fs.lua`, `global_functions.*`, `docs/lua-api/lua_api.json` and both focused tests.

Do not restore shell execution, do not replace it with a denylist, do not merge `table.unserialize` into this task, and do not treat a skipped or `action_required` run as C++ validation.

# Completion

- Final status: active
- PR: #317
- Current reviewed source/docs head: `28e7c3638fb3a4b420d81cc0cda8f9fce797daa3`
- Merge commit:
- Program record updated: yes, active task and `VALID_FIX_MISSING`
- Catalogue updated: yes, active reusable binding
- Changelog updated: yes
- Archived at: pending

## 2026-07-14T10:05:00+02:00

- Validation repair: added strongly typed `FileSystem.createDirectory` and `FileSystem.createDirectories` entries to the committed Lua API index so the pre-build binding-documentation gate can validate the new public methods.
- The Linux release build remains authoritative for full generated `docs/lua-api` synchronization.

## 2026-07-14 current-main transfer

- Changed: transferred the already reviewed implementation/evidence from predecessor PR #310 to PR #317 on exact current main `d88e7f354eb5b33068cdded7696e9cdb89b05268`.
- Learned: main advancement overlapped only shared changelog/catalogue paths; runtime, tests, Lua API catalogue and evidence paths had no overlap.
- Result: predecessor PR #310 is superseded and must remain closed without merge; all final checks belong to PR #317.
