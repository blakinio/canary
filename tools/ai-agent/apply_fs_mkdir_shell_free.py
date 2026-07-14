#!/usr/bin/env python3
"""Apply the bounded CS-006 shell-free FS.mkdir implementation and tests."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old[:80]!r}")
    write(path, content.replace(old, new, 1))


LICENSE = """/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */
"""


def main() -> None:
    replace_once(
        "src/lua/functions/core/game/global_functions.hpp",
        "\tstatic int luaGetFormattedTimeRemaining(lua_State* L);\n\tstatic int luaReportError(lua_State* L);",
        "\tstatic int luaGetFormattedTimeRemaining(lua_State* L);\n\tstatic int luaFileSystemCreateDirectory(lua_State* L);\n\tstatic int luaFileSystemCreateDirectories(lua_State* L);\n\tstatic int luaReportError(lua_State* L);",
    )

    replace_once(
        "src/lua/functions/core/game/global_functions.cpp",
        '#include "creatures/players/player.hpp"\n\nvoid GlobalFunctions::init(lua_State* L) {',
        '#include "creatures/players/player.hpp"\n\n#ifndef USE_PRECOMPILED_HEADERS\n\t#include <filesystem>\n#endif\n\nnamespace {\n\tint pushDirectoryCreationResult(lua_State* L, const std::filesystem::path &path, bool recursive) {\n\t\tif (path.empty()) {\n\t\t\tLua::pushBoolean(L, false);\n\t\t\tLua::pushString(L, "Directory path must not be empty");\n\t\t\treturn 2;\n\t\t}\n\n\t\tstd::error_code error;\n\t\tif (std::filesystem::is_directory(path, error) && !error) {\n\t\t\tLua::pushBoolean(L, true);\n\t\t\treturn 1;\n\t\t}\n\n\t\terror.clear();\n\t\tconst bool created = recursive\n\t\t\t? std::filesystem::create_directories(path, error)\n\t\t\t: std::filesystem::create_directory(path, error);\n\t\tif (created) {\n\t\t\tLua::pushBoolean(L, true);\n\t\t\treturn 1;\n\t\t}\n\n\t\tif (!error) {\n\t\t\tstd::error_code statusError;\n\t\t\tif (std::filesystem::is_directory(path, statusError) && !statusError) {\n\t\t\t\tLua::pushBoolean(L, true);\n\t\t\t\treturn 1;\n\t\t\t}\n\t\t\tif (statusError) {\n\t\t\t\terror = statusError;\n\t\t\t}\n\t\t}\n\n\t\tLua::pushBoolean(L, false);\n\t\tLua::pushString(L, error ? error.message() : "Directory could not be created");\n\t\treturn 2;\n\t}\n} // namespace\n\nvoid GlobalFunctions::init(lua_State* L) {',
    )

    replace_once(
        "src/lua/functions/core/game/global_functions.cpp",
        '\tLua::registerGlobalMethod(L, "getFormattedTimeRemaining", GlobalFunctions::luaGetFormattedTimeRemaining);\n\tLua::registerGlobalMethod(L, "reportError", GlobalFunctions::luaReportError);',
        '\tLua::registerGlobalMethod(L, "getFormattedTimeRemaining", GlobalFunctions::luaGetFormattedTimeRemaining);\n\n\tLua::registerTable(L, "FileSystem");\n\tLua::registerMethod(L, "FileSystem", "createDirectory", GlobalFunctions::luaFileSystemCreateDirectory);\n\tLua::registerMethod(L, "FileSystem", "createDirectories", GlobalFunctions::luaFileSystemCreateDirectories);\n\n\tLua::registerGlobalMethod(L, "reportError", GlobalFunctions::luaReportError);',
    )

    replace_once(
        "src/lua/functions/core/game/global_functions.cpp",
        "\nint GlobalFunctions::luaDoPlayerAddItem(lua_State* L) {",
        """
/***
 * Creates one directory without invoking a command shell.
 * @function FileSystem.createDirectory
 * @param path string
 * @return boolean success
 * @return string? errorMessage
 */
int GlobalFunctions::luaFileSystemCreateDirectory(lua_State* L) {
\treturn pushDirectoryCreationResult(L, std::filesystem::path(Lua::getString(L, 1)), false);
}

/***
 * Creates a directory and every missing parent without invoking a command shell.
 * @function FileSystem.createDirectories
 * @param path string
 * @return boolean success
 * @return string? errorMessage
 */
int GlobalFunctions::luaFileSystemCreateDirectories(lua_State* L) {
\treturn pushDirectoryCreationResult(L, std::filesystem::path(Lua::getString(L, 1)), true);
}

int GlobalFunctions::luaDoPlayerAddItem(lua_State* L) {""",
    )

    replace_once(
        "data/libs/functions/fs.lua",
        """function FS.mkdir(path)
\tif FS.exists(path) then
\t\treturn true
\tend
\tlocal success, err = os.execute('mkdir "' .. path .. '"')
\tif not success then
\t\treturn false, err
\tend
\treturn true
end

function FS.mkdir_p(path)
\tif path == "" then
\t\treturn true
\tend

\tlocal components = {}
\tfor component in path:gmatch("[^/\\\\]+") do
\t\ttable.insert(components, component)
\tend

\tlocal currentPath = ""
\tfor i, component in ipairs(components) do
\t\tcurrentPath = currentPath .. component

\t\tif not FS.exists(currentPath) then
\t\t\tlocal success, err = FS.mkdir(currentPath)
\t\t\tif not success then
\t\t\t\treturn false, err
\t\t\tend
\t\tend

\t\tif i < #components then
\t\t\tcurrentPath = currentPath .. "/"
\t\tend
\tend

\treturn true
end
""",
        """function FS.mkdir(path)
\treturn FileSystem.createDirectory(path)
end

function FS.mkdir_p(path)
\tif path == "" then
\t\treturn true
\tend
\treturn FileSystem.createDirectories(path)
end
""",
    )

    write(
        "tests/lua/test_fs.lua",
        """-- Run: luajit tests/lua/test_fs.lua

local calls = {}
local shellCalled = false
local realExecute = os.execute

os.execute = function()
\tshellCalled = true
\terror("FS helpers must not invoke os.execute")
end

FileSystem = {
\tcreateDirectory = function(path)
\t\ttable.insert(calls, { method = "createDirectory", path = path })
\t\treturn true
\tend,
\tcreateDirectories = function(path)
\t\ttable.insert(calls, { method = "createDirectories", path = path })
\t\treturn true
\tend,
}

dofile("data/libs/functions/fs.lua")

local function assertEqual(actual, expected, message)
\tif actual ~= expected then
\t\terror(string.format("%s: expected %s, got %s", message, tostring(expected), tostring(actual)))
\tend
end

assertEqual(FS.mkdir("reports/player $(touch marker)"), true, "single directory result")
assertEqual(calls[1].method, "createDirectory", "single directory method")
assertEqual(calls[1].path, "reports/player $(touch marker)", "single directory path")

assertEqual(FS.mkdir_p("reports/bugs/player name"), true, "recursive directory result")
assertEqual(calls[2].method, "createDirectories", "recursive directory method")
assertEqual(calls[2].path, "reports/bugs/player name", "recursive directory path")

local beforeEmpty = #calls
assertEqual(FS.mkdir_p(""), true, "empty recursive path")
assertEqual(#calls, beforeEmpty, "empty recursive path must not call native binding")

FileSystem.createDirectory = function(path)
\treturn false, "denied: " .. path
end
local success, err = FS.mkdir("blocked")
assertEqual(success, false, "error success flag")
assertEqual(err, "denied: blocked", "error message passthrough")
assertEqual(shellCalled, false, "shell execution")

os.execute = realExecute
print("FS shell-free wrapper tests passed")
""",
    )

    write(
        "tests/unit/lua/filesystem_functions_test.cpp",
        LICENSE
        + """

#include "lua/functions/core/game/global_functions.hpp"

#include <gtest/gtest.h>

#ifndef USE_PRECOMPILED_HEADERS
\t#include <chrono>
\t#include <filesystem>
\t#include <memory>
\t#include <optional>
\t#include <stdexcept>
\t#include <string>
#endif

namespace {
\tstruct LuaDirectoryResult {
\t\tbool success = false;
\t\tstd::optional<std::string> error;
\t};

\tclass FileSystemFunctionsTest : public ::testing::Test {
\tprotected:
\t\tvoid SetUp() override {
\t\t\tpreviousPath = std::filesystem::current_path();
\t\t\tconst auto suffix = std::chrono::steady_clock::now().time_since_epoch().count();
\t\t\ttemporaryPath = std::filesystem::temp_directory_path() / ("canary-filesystem-functions-" + std::to_string(suffix));
\t\t\tstd::filesystem::create_directories(temporaryPath);
\t\t\tstd::filesystem::current_path(temporaryPath);

\t\t\tluaState.reset(luaL_newstate());
\t\t\tASSERT_NE(luaState, nullptr);
\t\t\tluaL_openlibs(luaState.get());
\t\t\tGlobalFunctions::init(luaState.get());
\t\t}

\t\tvoid TearDown() override {
\t\t\tluaState.reset();
\t\t\tstd::filesystem::current_path(previousPath);
\t\t\tstd::error_code error;
\t\t\tstd::filesystem::remove_all(temporaryPath, error);
\t\t}

\t\tLuaDirectoryResult call(const char* method, const std::filesystem::path &path) {
\t\t\tauto* L = luaState.get();
\t\t\tlua_getglobal(L, "FileSystem");
\t\t\tlua_getfield(L, -1, method);
\t\t\tlua_remove(L, -2);
\t\t\tlua_pushstring(L, path.string().c_str());
\t\t\tif (lua_pcall(L, 1, 2, 0) != LUA_OK) {
\t\t\t\tconst std::string error = lua_tostring(L, -1) ? lua_tostring(L, -1) : "unknown Lua error";
\t\t\t\tlua_settop(L, 0);
\t\t\t\tADD_FAILURE() << error;
\t\t\t\treturn {};
\t\t\t}

\t\t\tLuaDirectoryResult result;
\t\t\tresult.success = lua_toboolean(L, -2) != 0;
\t\t\tif (lua_isstring(L, -1)) {
\t\t\t\tresult.error = lua_tostring(L, -1);
\t\t\t}
\t\t\tlua_settop(L, 0);
\t\t\treturn result;
\t\t}

\t\tstd::filesystem::path previousPath;
\t\tstd::filesystem::path temporaryPath;
\t\tstd::unique_ptr<lua_State, decltype(&lua_close)> luaState { nullptr, &lua_close };
\t};
} // namespace

TEST_F(FileSystemFunctionsTest, CreatesSingleDirectoryAndAcceptsExistingDirectory) {
\tconst auto path = temporaryPath / "reports with spaces";
\tauto created = call("createDirectory", path);
\tEXPECT_TRUE(created.success);
\tEXPECT_FALSE(created.error.has_value());
\tEXPECT_TRUE(std::filesystem::is_directory(path));

\tauto existing = call("createDirectory", path);
\tEXPECT_TRUE(existing.success);
\tEXPECT_FALSE(existing.error.has_value());
}

TEST_F(FileSystemFunctionsTest, CreatesMissingParentDirectories) {
\tconst auto path = temporaryPath / "reports" / "bugs" / "Player Name";
\tauto result = call("createDirectories", path);
\tEXPECT_TRUE(result.success);
\tEXPECT_FALSE(result.error.has_value());
\tEXPECT_TRUE(std::filesystem::is_directory(path));
}

TEST_F(FileSystemFunctionsTest, TreatsShellMetacharactersAsLiteralPathCharacters) {
\tconst std::filesystem::path literalPath = "player$(touch marker)";
\tauto result = call("createDirectory", literalPath);
\tEXPECT_TRUE(result.success);
\tEXPECT_TRUE(std::filesystem::is_directory(temporaryPath / literalPath));
\tEXPECT_FALSE(std::filesystem::exists(temporaryPath / "marker"));
}

TEST_F(FileSystemFunctionsTest, ReturnsErrorWhenSingleDirectoryParentIsMissing) {
\tauto result = call("createDirectory", std::filesystem::path("missing") / "child");
\tEXPECT_FALSE(result.success);
\tASSERT_TRUE(result.error.has_value());
\tEXPECT_FALSE(result.error->empty());
}
""",
    )

    replace_once(
        "tests/unit/lua/CMakeLists.txt",
        "    PRIVATE event_callback_manager_test.cpp\n            network_message_functions_test.cpp",
        "    PRIVATE event_callback_manager_test.cpp\n            filesystem_functions_test.cpp\n            network_message_functions_test.cpp",
    )

    replace_once(
        "docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md",
        "# Active tasks\n\nNone. Select exactly one bounded queue item and create a new task before implementation.",
        "# Active tasks\n\n| Task/PR | Candidate | Status | Scope |\n|---|---|---|---|\n| `CAN-20260714-fs-mkdir-shell-injection` / [#310](https://github.com/blakinio/canary/pull/310) | `CS-006` | active | Replace Lua shell-based directory creation with native `std::filesystem` operations and focused Lua/C++ regressions. |",
    )
    replace_once(
        "docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md",
        "| `CS-006` | `891685169745e46f665069edcc35847f0704aa21` | `PARTIAL_VALUE` | high | `FS.mkdir` shell construction | Independent security task; do not copy upstream denylist. |",
        "| `CS-006` | `891685169745e46f665069edcc35847f0704aa21` | `VALID_FIX_MISSING` | high | `FS.mkdir` shell construction | Active in task `CAN-20260714-fs-mkdir-shell-injection` / PR #310; preserve API behavior while removing all shell execution. |",
    )

    replace_once(
        "docs/agents/CHANGELOG.md",
        "## Unreleased\n",
        "## Unreleased\n\n- PR #310 replaces `FS.mkdir`/`FS.mkdir_p` shell command construction with native `FileSystem.createDirectory`/`createDirectories` Lua bindings backed by `std::filesystem`, preserving success/error returns and adding Lua plus C++ regressions for literal shell metacharacters, recursive paths, spaces and existing directories.\n",
    )

    replace_once(
        "docs/agents/MODULE_CATALOG.md",
        "| Forge history ID resolution | merged (#110) |",
        "| Lua FileSystem directory binding | active (#310) | Shell-free `FileSystem.createDirectory(path)` and `FileSystem.createDirectories(path)` operations used by the compatibility `FS.mkdir`/`FS.mkdir_p` wrappers | `src/lua/functions/core/game/global_functions.{hpp,cpp}`, `data/libs/functions/fs.lua`, focused Lua/C++ tests, `CS006_FS_MKDIR_AUDIT` | Reuse this binding for runtime directory creation; never reintroduce `os.execute` or a metacharacter denylist around a shell command. |\n| Forge history ID resolution | merged (#110) |",
    )

    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        'updated: 2026-07-14T08:00:00+02:00\nlast_verified_commit: "42c0afa817b60f3b888c46b690b286cd224a3062"',
        'updated: 2026-07-14T09:30:00+02:00\nlast_verified_commit: "a5cd00cc9af507f3281defb38e9f427377ef6b2f"',
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        'related_pr: "pending"',
        'related_pr: "#310"',
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        """  exclusive:
    - data/libs/functions/fs.lua
    - docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md
    - artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT.md
    - artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json
    - tools/ai-agent/audit_fs_mkdir.py
    - .github/workflows/audit-fs-mkdir.yml
  shared:
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - data/**
    - data-otservbr-global/**
    - src/**
    - tests/**""",
        """  exclusive:
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
    - .github/workflows/reusable-tests-lua.yml""",
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        """public_interfaces:
  - "FS.mkdir(path) return contract (preserve unless evidence requires a compatible extension)"
  - "FS.mkdir_p(path) behavior through FS.mkdir""",
        """public_interfaces:
  - "FS.mkdir(path) -> success[, errorMessage]"
  - "FS.mkdir_p(path) -> success[, errorMessage]"
  - "FileSystem.createDirectory(path) -> success[, errorMessage]"
  - "FileSystem.createDirectories(path) -> success[, errorMessage]""",
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        """- [ ] Full current-repository inventory of `FS.mkdir`, `FS.mkdir_p`, their call sites, and path provenance is recorded with exact files and lines.
- [ ] Existing shell-free filesystem facilities and Lua bindings are inventoried before adding any new helper.
- [ ] CrystalServer commit `891685169745e46f665069edcc35847f0704aa21` is treated as evidence only; its denylist-plus-shell patch is not copied blindly.""",
        """- [x] Full current-repository inventory of `FS.mkdir`, `FS.mkdir_p`, their call sites, and path provenance is recorded with exact files and lines.
- [x] Existing shell-free filesystem facilities and Lua bindings are inventoried before adding any new helper.
- [x] CrystalServer commit `891685169745e46f665069edcc35847f0704aa21` is treated as evidence only; its denylist-plus-shell patch is not copied blindly.""",
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        "| Existing filesystem APIs/bindings | Prefer shell-free native directory creation | audit pending |",
        "| Existing filesystem APIs/bindings | Reuse engine-standard `std::filesystem`; no directory binding existed | broad and targeted audit complete |",
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        """## 2026-07-14T08:00:00+02:00

- Changed: created a dedicated branch and claimed the exact Lua/security/report paths.
- Learned: current Canary still invokes the shell directly; upstream's denylist continues to use a shell and is not sufficient as the design.
- Failed/blocked: local clone/fetch/build unavailable because DNS cannot resolve GitHub.
- Result: proceed with a bounded GitHub Actions audit on the exact task branch.""",
        """## 2026-07-14T08:00:00+02:00

- Changed: created a dedicated branch and claimed the exact Lua/security/report paths.
- Learned: current Canary still invokes the shell directly; upstream's denylist continues to use a shell and is not sufficient as the design.
- Failed/blocked: local clone/fetch/build unavailable because DNS cannot resolve GitHub.
- Result: proceed with a bounded GitHub Actions audit on the exact task branch.

## 2026-07-14T09:15:00+02:00

- Changed: published deterministic Markdown/JSON evidence after scanning 6,857 tracked files; temporary audit runners removed themselves.
- Learned: production uses are player-report paths in `data/events/scripts/player.lua`; the default validator permits only letters, apostrophes and spaces, but `FS.mkdir` remains a general Lua shell primitive for DB/custom-script paths.
- Failed/blocked: the first report commit omitted ignored `artifacts/**`; a second run exposed trailing whitespace. Both publication issues were fixed without weakening `git diff --check`.
- Result: `CS-006` is `VALID_FIX_MISSING`; use existing `GlobalFunctions` plus `std::filesystem`, with focused Lua and C++ tests.""",
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        "| Prefer an existing native filesystem binding | Avoid a parallel helper or a new public surface unless current architecture requires it. | none |",
        "| Add two narrow methods to existing `GlobalFunctions` | No directory binding exists; this avoids a new subsystem/build unit while reusing established Lua registration and `std::filesystem`. | none |\n| Preserve `FS` as a compatibility wrapper | Existing datapack/custom scripts keep their API while shell execution disappears. | none |",
    )
    replace_once(
        "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md",
        """# Remaining work

1. Open the draft PR.
2. Produce the exact full-checkout call-site/native-facility audit.
3. Select tests and implementation from evidence.""",
        """# Remaining work

1. Apply and review the bounded implementation/test diff.
2. Run Lua tests, full Ready-state C++ CI and generated Lua API documentation checks.
3. Merge only after reviews, threads, ownership and Required pass; archive separately.""",
    )


if __name__ == "__main__":
    main()
