---
task_id: CAN-20260714-fs-mkdir-shell-injection
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-006
status: active
agent: "GPT-5.6 Thinking"
branch: security/fs-mkdir-shell-free
base_branch: main
created: 2026-07-14T08:00:00+02:00
updated: 2026-07-14T09:30:00+02:00
last_verified_commit: "a5cd00cc9af507f3281defb38e9f427377ef6b2f"
risk: high
related_issue: ""
related_pr: "#310"
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
    - docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md
    - artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md
    - artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json
    - tools/ai-agent/apply_fs_mkdir_shell_free.py
    - .github/workflows/apply-fs-mkdir-shell-free.yml
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
    - src/lua/functions/core/core_functions.hpp
    - src/lua/functions/core/libs/core_libs_functions.hpp
    - .github/workflows/reusable-tests-lua.yml
modules_touched:
  - Lua filesystem helper boundary
reuses:
  - existing Lua test and CI infrastructure after discovery
  - existing filesystem/Lua bindings if current source proves one exists
  - existing bounded self-removing audit workflow pattern
public_interfaces:
  - "FS.mkdir(path) -> success[, errorMessage]"
  - "FS.mkdir_p(path) -> success[, errorMessage]"
  - "FileSystem.createDirectory(path) -> success[, errorMessage]"
  - "FileSystem.createDirectories(path) -> success[, errorMessage]"
cross_repo_tasks: []
---

# Goal

Determine whether `FS.mkdir` can execute shell metacharacters from any reachable Canary call site, then remove shell execution through the smallest architecture-native solution if the risk is confirmed, while preserving valid directory-creation behavior on maintained platforms.

# Acceptance criteria

- [x] Full current-repository inventory of `FS.mkdir`, `FS.mkdir_p`, their call sites, and path provenance is recorded with exact files and lines.
- [x] Existing shell-free filesystem facilities and Lua bindings are inventoried before adding any new helper.
- [x] CrystalServer commit `891685169745e46f665069edcc35847f0704aa21` is treated as evidence only; its denylist-plus-shell patch is not copied blindly.
- [ ] A deterministic regression demonstrates that shell metacharacters cannot execute an additional command or create an unintended marker.
- [ ] Valid single-level and recursive directory creation, existing-directory behavior, spaces, separators, and error returns remain covered.
- [ ] The implementation is shell-free, or the task is closed without a runtime change if no safe architecture-native implementation is justified.
- [ ] Required Lua/runtime checks pass on the current PR head.
- [ ] No protocol, client, schema, migration, map, item, asset, or production configuration changes.
- [ ] Program, changelog, and handoff records are current.
- [ ] Autonomous merge gate is satisfied.

# Confirmed context

- Target repository: `blakinio/canary`; no other repository is writable.
- Task baseline: `42c0afa817b60f3b888c46b690b286cd224a3062`.
- Current implementation uses `os.execute('mkdir "' .. path .. '"')` in `data/libs/functions/fs.lua`.
- The same file exposes `FS.mkdir_p`, which delegates each path component to `FS.mkdir`.
- CrystalServer commit `891685169745e46f665069edcc35847f0704aa21` adds a metacharacter denylist but still invokes a shell; the comparison program explicitly requires an independent security design.
- Open PR search for `FS.mkdir`, `fs.lua`, and `mkdir_p` returned no overlap at task start.
- Open runtime work exists in instance/multichannel/game areas; this task avoids those paths.
- Local Git/worktree/build access is unavailable: `git ls-remote` fails with `Could not resolve host: github.com`.

# Existing work to reuse

| System | Intended reuse | Evidence status |
|---|---|---|
| Lua/Fast Checks workflow | Syntax, formatting and Lua regression execution | verify after audit |
| Existing filesystem APIs/bindings | Reuse engine-standard `std::filesystem`; no directory binding existed | broad and targeted audit complete |
| Bounded self-removing workflow | Full-checkout discovery while local clone is unavailable | approved repository precedent; temporary files must leave final diff |
| CrystalServer comparison program | Candidate provenance, risk and sequencing | current program record |

# Ownership and overlap check

- Open PRs and current main were refreshed on 2026-07-14.
- No open PR matched `FS.mkdir`, `fs.lua`, or `mkdir_p`.
- `data/libs/functions/fs.lua` is exclusively claimed by this task.
- Shared program/changelog edits must remain narrow.
- The temporary audit workflow/script must remove themselves after producing the evidence report.

# Plan

1. Publish this task and a draft PR for visibility.
2. Run a self-removing full-checkout audit to enumerate call sites, path provenance, tests, `os.execute`, and native filesystem facilities.
3. Classify reachability and revise `CS-006` from `PARTIAL_VALUE` to an evidence-backed final status.
4. Add regression coverage before the fix where practical.
5. Implement the smallest shell-free solution using an existing binding when available; otherwise add the narrowest justified native binding with all maintained build/test entries.
6. Run current-head CI, review the complete diff, and merge only through the autonomous gate.
7. Archive the task in a separate cleanup PR.

# Work log

## 2026-07-14T08:00:00+02:00

- Changed: created a dedicated branch and claimed the exact Lua/security/report paths.
- Learned: current Canary still invokes the shell directly; upstream's denylist continues to use a shell and is not sufficient as the design.
- Failed/blocked: local clone/fetch/build unavailable because DNS cannot resolve GitHub.
- Result: proceed with a bounded GitHub Actions audit on the exact task branch.

## 2026-07-14T09:15:00+02:00

- Changed: published deterministic Markdown/JSON evidence after scanning 6,857 tracked files; temporary audit runners removed themselves.
- Learned: production uses are player-report paths in `data/events/scripts/player.lua`; the default validator permits only letters, apostrophes and spaces, but `FS.mkdir` remains a general Lua shell primitive for DB/custom-script paths.
- Failed/blocked: the first report commit omitted ignored `artifacts/**`; a second run exposed trailing whitespace. Both publication issues were fixed without weakening `git diff --check`.
- Result: `CS-006` is `VALID_FIX_MISSING`; use existing `GlobalFunctions` plus `std::filesystem`, with focused Lua and C++ tests.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Separate `CS-006` from `CS-007` | Shell/path handling and deserialization compatibility have different threat models and test contracts. | none |
| Do not copy the CrystalServer denylist | Denylists are incomplete by construction and leave shell interpretation in the execution path. | none |
| Audit call sites before changing the API | Security severity and compatibility depend on actual path sources and existing uses. | none |
| Add two narrow methods to existing `GlobalFunctions` | No directory binding exists; this avoids a new subsystem/build unit while reusing established Lua registration and `std::filesystem`. | none |
| Preserve `FS` as a compatibility wrapper | Existing datapack/custom scripts keep their API while shell execution disappears. | none |

# Validation and CI

| Commit | Check | Result | Evidence |
|---|---|---|---|
| `42c0afa817b60f3b888c46b690b286cd224a3062` | local Git/worktree/build preflight | unavailable | DNS failure recorded; no pass claimed |

Never record `passed` without verification on the stated commit.

# Risks and compatibility

- Security: direct command construction can become command injection if any path contains shell metacharacters and reaches `FS.mkdir`.
- Compatibility: path quoting, Windows drive/UNC paths, relative roots, separators, spaces and existing return conventions must be preserved deliberately.
- Runtime: directory creation may happen during startup or tooling; failures must remain visible and must not silently change locations.
- Cross-repository: none expected.
- Rollback: revert the implementation PR; no persisted schema or data migration is planned.

# Remaining work

1. Apply and review the bounded implementation/test diff.
2. Run Lua tests, full Ready-state C++ CI and generated Lua API documentation checks.
3. Merge only after reviews, threads, ownership and Required pass; archive separately.

# Handoff

## Start here

Read this task, the comparison program, `data/libs/functions/fs.lua`, CrystalServer commit `891685169745e46f665069edcc35847f0704aa21`, and the generated `CS006_FS_MKDIR_AUDIT` report.

## Do not repeat

- Do not combine this with `table.unserialize`.
- Do not copy the upstream denylist and continue invoking a shell.
- Do not introduce a second general filesystem framework without checking current Lua/native facilities.
- Do not infer that a path is trusted without tracing its call site.

## Open questions

- Which current call sites exist, and can any path contain configuration, network, player, database, or script-derived data?
- Does Canary already expose shell-free directory creation to Lua?
- Which maintained test harness can safely prove no marker command is executed?

# Completion

- Final status: active
- PR: pending
- Merge commit:
- Program record updated: pending
- Catalogue updated: pending applicability review
- Changelog updated: pending
- Archived at: pending
