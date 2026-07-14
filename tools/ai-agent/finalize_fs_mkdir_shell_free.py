#!/usr/bin/env python3
"""Finalize CS-006 around the dedicated lowercase fs binding."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old[:100]!r}")
    write(path, content.replace(old, new, 1))


def main() -> None:
    global_cpp = "src/lua/functions/core/game/global_functions.cpp"
    replace_once(
        global_cpp,
        '''#ifndef USE_PRECOMPILED_HEADERS
\t#include <filesystem>
#endif

namespace {
\tint pushDirectoryCreationResult(lua_State* L, const std::filesystem::path &path, bool recursive) {
\t\tif (path.empty()) {
\t\t\tLua::pushBoolean(L, false);
\t\t\tLua::pushString(L, "Directory path must not be empty");
\t\t\treturn 2;
\t\t}

\t\tstd::error_code error;
\t\tif (std::filesystem::is_directory(path, error) && !error) {
\t\t\tLua::pushBoolean(L, true);
\t\t\treturn 1;
\t\t}

\t\terror.clear();
\t\tconst bool created = recursive
\t\t\t? std::filesystem::create_directories(path, error)
\t\t\t: std::filesystem::create_directory(path, error);
\t\tif (created) {
\t\t\tLua::pushBoolean(L, true);
\t\t\treturn 1;
\t\t}

\t\tif (!error) {
\t\t\tstd::error_code statusError;
\t\t\tif (std::filesystem::is_directory(path, statusError) && !statusError) {
\t\t\t\tLua::pushBoolean(L, true);
\t\t\t\treturn 1;
\t\t\t}
\t\t\tif (statusError) {
\t\t\t\terror = statusError;
\t\t\t}
\t\t}

\t\tLua::pushBoolean(L, false);
\t\tLua::pushString(L, error ? error.message() : "Directory could not be created");
\t\treturn 2;
\t}
} // namespace

''',
        "",
    )
    replace_once(
        global_cpp,
        '''
\tLua::registerTable(L, "FileSystem");
\tLua::registerMethod(L, "FileSystem", "createDirectory", GlobalFunctions::luaFileSystemCreateDirectory);
\tLua::registerMethod(L, "FileSystem", "createDirectories", GlobalFunctions::luaFileSystemCreateDirectories);
''',
        "",
    )
    replace_once(
        global_cpp,
        '''/***
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

''',
        "",
    )
    replace_once(
        "src/lua/functions/core/game/global_functions.hpp",
        "\tstatic int luaFileSystemCreateDirectory(lua_State* L);\n\tstatic int luaFileSystemCreateDirectories(lua_State* L);\n",
        "",
    )

    fs_cpp = "src/lua/functions/core/libs/filesystem_functions.cpp"
    replace_once(
        fs_cpp,
        '''int FilesystemFunctions::luaCreateDirectory(lua_State* L) {
\t// fs.createDirectory(path)
''',
        '''/***
 * Creates one directory without invoking a command shell.
 * @function fs.createDirectory
 * @param path string
 * @return boolean success
 * @return string? errorMessage
 */
int FilesystemFunctions::luaCreateDirectory(lua_State* L) {
''',
    )
    replace_once(
        fs_cpp,
        '''int FilesystemFunctions::luaCreateDirectories(lua_State* L) {
\t// fs.createDirectories(path)
''',
        '''/***
 * Creates a directory and every missing parent without invoking a command shell.
 * @function fs.createDirectories
 * @param path string
 * @return boolean success
 * @return string? errorMessage
 */
int FilesystemFunctions::luaCreateDirectories(lua_State* L) {
''',
    )

    replace_once(
        "docs/agents/CHANGELOG.md",
        "- PR #310 replaces `FS.mkdir`/`FS.mkdir_p` shell command construction with native `FileSystem.createDirectory`/`createDirectories` Lua bindings backed by `std::filesystem`, preserving success/error returns and adding Lua plus C++ regressions for literal shell metacharacters, recursive paths, spaces and existing directories.",
        "- PR #310 replaces `FS.mkdir`/`FS.mkdir_p` shell command construction with native `fs.createDirectory`/`fs.createDirectories` Lua bindings backed by `std::filesystem`, preserving success/error returns and adding Lua plus C++ regressions for literal shell metacharacters, recursive paths, spaces and existing directories.",
    )
    replace_once(
        "docs/agents/MODULE_CATALOG.md",
        "| Lua FileSystem directory binding | active (#310) | Shell-free `FileSystem.createDirectory(path)` and `FileSystem.createDirectories(path)` operations used by the compatibility `FS.mkdir`/`FS.mkdir_p` wrappers | `src/lua/functions/core/game/global_functions.{hpp,cpp}`, `data/libs/functions/fs.lua`, focused Lua/C++ tests, `CS006_FS_MKDIR_AUDIT` | Reuse this binding for runtime directory creation; never reintroduce `os.execute` or a metacharacter denylist around a shell command. |",
        "| Lua filesystem directory binding | active (#310) | Shell-free `fs.createDirectory(path)` and `fs.createDirectories(path)` operations used by the compatibility `FS.mkdir`/`FS.mkdir_p` wrappers | `src/lua/functions/core/libs/filesystem_functions.{hpp,cpp}`, `data/libs/functions/fs.lua`, focused Lua/C++ tests, `CS006_FS_MKDIR_AUDIT` | Reuse this binding for runtime directory creation; never reintroduce `os.execute` or a metacharacter denylist around a shell command. |",
    )

    task = "docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md"
    replace_once(task, 'updated: 2026-07-14T09:30:00+02:00\nlast_verified_commit: "a5cd00cc9af507f3281defb38e9f427377ef6b2f"', 'updated: 2026-07-14T09:55:00+02:00\nlast_verified_commit: "c9ca0e38ec73f5cac9c70be210be3835247d78bb"')
    replace_once(task, '''    - src/lua/functions/core/game/global_functions.cpp
    - src/lua/functions/core/game/global_functions.hpp
''', '''    - src/lua/functions/core/libs/filesystem_functions.cpp
    - src/lua/functions/core/libs/filesystem_functions.hpp
    - src/lua/functions/core/libs/core_libs_functions.hpp
    - src/lua/functions/core/CMakeLists.txt
    - vcproj/canary.vcxproj
''')
    replace_once(task, '''    - tools/ai-agent/apply_fs_mkdir_shell_free.py
    - .github/workflows/apply-fs-mkdir-shell-free.yml
''', "")
    replace_once(task, '''    - src/lua/functions/core/libs/core_libs_functions.hpp
''', "")
    replace_once(task, '''  - existing Lua test and CI infrastructure after discovery
  - existing filesystem/Lua bindings if current source proves one exists
  - existing bounded self-removing audit workflow pattern
''', '''  - existing `CoreLibsFunctions` registration surface
  - engine-standard `std::filesystem` operations
  - existing standalone Lua and `canary_ut` test infrastructure
  - existing bounded self-removing audit workflow pattern
''')
    replace_once(task, '''  - "FileSystem.createDirectory(path) -> success[, errorMessage]"
  - "FileSystem.createDirectories(path) -> success[, errorMessage]"
''', '''  - "fs.createDirectory(path) -> success[, errorMessage]"
  - "fs.createDirectories(path) -> success[, errorMessage]"
''')
    replace_once(task, '''- [ ] A deterministic regression demonstrates that shell metacharacters cannot execute an additional command or create an unintended marker.
- [ ] Valid single-level and recursive directory creation, existing-directory behavior, spaces, separators, and error returns remain covered.
- [ ] The implementation is shell-free, or the task is closed without a runtime change if no safe architecture-native implementation is justified.
''', '''- [x] A deterministic Lua regression fails if `os.execute` is called, and a native C++ regression verifies no marker is created from shell metacharacters.
- [x] Source coverage includes single-level and recursive creation, existing-directory behavior, spaces, empty recursive input and error returns.
- [x] The implementation is shell-free and backed by `std::filesystem`.
''')
    replace_once(task, '''- [ ] No protocol, client, schema, migration, map, item, asset, or production configuration changes.
- [ ] Program, changelog, and handoff records are current.
''', '''- [x] No protocol, client, schema, migration, map, item, asset, or production configuration changes.
- [x] Program, changelog, module catalogue and handoff records are current.
''')
    replace_once(task, "- Current implementation uses `os.execute('mkdir \"' .. path .. '\"')` in `data/libs/functions/fs.lua`.\n- The same file exposes `FS.mkdir_p`, which delegates each path component to `FS.mkdir`.\n", "- Baseline `FS.mkdir` invoked `os.execute('mkdir \"' .. path .. '\"')`; `FS.mkdir_p` delegated every component to that shell boundary.\n- The current implementation delegates to the dedicated lowercase `fs` binding and performs no shell execution.\n")
    replace_once(task, '''| Lua/Fast Checks workflow | Syntax, formatting and Lua regression execution | verify after audit |
''', '''| Lua/Fast Checks workflow | Syntax, formatting and Lua regression execution | focused Lua test passed; exact-head Ready validation pending |
''')
    replace_once(task, '''- Result: `CS-006` is `VALID_FIX_MISSING`; use existing `GlobalFunctions` plus `std::filesystem`, with focused Lua and C++ tests.
''', '''- Result: `CS-006` is `VALID_FIX_MISSING`; use a dedicated `FilesystemFunctions` library registered through `CoreLibsFunctions`, with focused Lua and C++ tests.
''')
    replace_once(task, "| Add two narrow methods to existing `GlobalFunctions` | No directory binding exists; this avoids a new subsystem/build unit while reusing established Lua registration and `std::filesystem`. | none |", "| Add one narrow `FilesystemFunctions` library to `CoreLibsFunctions` | No directory binding existed; the dedicated library is discoverable, directly testable and uses existing Lua registration/build conventions. | none |")
    replace_once(task, "- Which current call sites exist, and can any path contain configuration, network, player, database, or script-derived data?\n- Does Canary already expose shell-free directory creation to Lua?\n- Which maintained test harness can safely prove no marker command is executed?\n", "- Does the Lua API generator accept the two `fs.*` annotations unchanged, or require generated documentation updates?\n- Do all maintained platform builds accept the literal shell-character regression path?\n")
    replace_once(task, "- PR: pending\n", "- PR: #310\n")
    replace_once(task, "- Program record updated: pending\n- Catalogue updated: pending applicability review\n- Changelog updated: pending\n", "- Program record updated: yes, active task and `VALID_FIX_MISSING`\n- Catalogue updated: yes, active reusable binding\n- Changelog updated: yes\n")
    write(task, read(task).rstrip() + '''

## 2026-07-14T09:55:00+02:00

- Changed: removed the duplicate `FileSystem` implementation from `GlobalFunctions`; the final design exposes only lowercase `fs` through the dedicated `FilesystemFunctions` library.
- Changed: added generator-facing Lua API annotations and synchronized changelog, module catalogue, ownership and public-interface records with the actual API.
- Learned: draft CI `1674` reported success while skipping Fast Checks, Lua and all builds, so it is not accepted as runtime validation.
- Result: final-source review complete; a connector-authored commit must trigger normal ownership/formatter checks before the PR enters Ready state.
''')


if __name__ == "__main__":
    main()
