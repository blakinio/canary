# CS-006 FS.mkdir security audit

- Repository: `blakinio/canary`
- Audited commit: `4695d10158386da1af517a233bdb3e5cda0d2c23`
- Tracked files: 6857
- Definitions: 2
- Non-definition calls: 5
- Lua `os.execute` references: 3
- Native/binding candidates: 189

## Method

Deterministic `git grep` inventory over all tracked text files at the exact branch commit. Lexical input labels are hints only; each call requires manual provenance tracing.

## Definitions

| Path | Line | Source |
|---|---:|---|
| `data/libs/functions/fs.lua` | 12 | `function FS.mkdir(path)` |
| `data/libs/functions/fs.lua` | 23 | `function FS.mkdir_p(path)` |

## Call sites

| Path | Line | Source |
|---|---:|---|
| `data/events/scripts/player.lua` | 441 | `FS.mkdir_p(string.format("%s/reports/players/%s", CORE_DIRECTORY, name))` |
| `data/events/scripts/player.lua` | 489 | `FS.mkdir_p(string.format("%s/reports/bugs/%s", CORE_DIRECTORY, name))` |
| `data/libs/functions/fs.lua` | 38 | `local success, err = FS.mkdir(currentPath)` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 48 | `- "FS.mkdir(path) return contract (preserve unless evidence requires a compatible extension)"` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 49 | `- "FS.mkdir_p(path) behavior through FS.mkdir"` |

### `data/events/scripts/player.lua:441`

Lexical signals: **player-user, filesystem-derived**; manual provenance required.

```text
436: 	local player = Player(playerGuid)
437: 	if not player then
438: 		return false
439: 	end
440: 	local name = player:getName():gsub("%s+", "_")
441: 	FS.mkdir_p(string.format("%s/reports/players/%s", CORE_DIRECTORY, name))
442: 	local file = io.open(string.format("%s/reports/players/%s-%s-%d.txt", CORE_DIRECTORY, name, targetName, reportType), "r")
443: 	if file then
444: 		io.close(file)
445: 		return true
446: 	end
```

### `data/events/scripts/player.lua:489`

Lexical signals: **player-user, filesystem-derived**; manual provenance required.

```text
484: 	return
485: end
486:
487: function Player:onReportBug(message, position, category)
488: 	local name = self:getName():gsub("%s+", "_")
489: 	FS.mkdir_p(string.format("%s/reports/bugs/%s", CORE_DIRECTORY, name))
490: 	local file = io.open(string.format("%s/reports/bugs/%s/report.txt", CORE_DIRECTORY, name), "a")
491:
492: 	if not file then
493: 		self:sendTextMessage(MESSAGE_EVENT_ADVANCE, "There was an error when processing your report, please contact a gamemaster.")
494: 		return true
```

### `data/libs/functions/fs.lua:38`

Lexical signals: **filesystem-derived**; manual provenance required.

```text
33: 	local currentPath = ""
34: 	for i, component in ipairs(components) do
35: 		currentPath = currentPath .. component
36:
37: 		if not FS.exists(currentPath) then
38: 			local success, err = FS.mkdir(currentPath)
39: 			if not success then
40: 				return false, err
41: 			end
42: 		end
43:
```

### `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md:48`

Lexical signals: **filesystem-derived**; manual provenance required.

```text
43: reuses:
44:   - existing Lua test and CI infrastructure after discovery
45:   - existing filesystem/Lua bindings if current source proves one exists
46:   - existing bounded self-removing audit workflow pattern
47: public_interfaces:
48:   - "FS.mkdir(path) return contract (preserve unless evidence requires a compatible extension)"
49:   - "FS.mkdir_p(path) behavior through FS.mkdir"
50: cross_repo_tasks: []
51: ---
52:
53: # Goal
```

### `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md:49`

Lexical signals: **filesystem-derived**; manual provenance required.

```text
44:   - existing Lua test and CI infrastructure after discovery
45:   - existing filesystem/Lua bindings if current source proves one exists
46:   - existing bounded self-removing audit workflow pattern
47: public_interfaces:
48:   - "FS.mkdir(path) return contract (preserve unless evidence requires a compatible extension)"
49:   - "FS.mkdir_p(path) behavior through FS.mkdir"
50: cross_repo_tasks: []
51: ---
52:
53: # Goal
54:
```

## Lua shell execution

| Path | Line | Source |
|---|---:|---|
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 153 | `- Current Canary evidence: Canary concatenates the path into \`os.execute('mkdir "' .. path .. '"')\` without validation.` |
| `data/libs/functions/fs.lua` | 16 | `local success, err = os.execute('mkdir "' .. path .. '"')` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 74 | `- Current implementation uses \`os.execute('mkdir "' .. path .. '"')\` in \`data/libs/functions/fs.lua\`.` |

## Native filesystem or binding candidates

| Path | Line | Source |
|---|---:|---|
| `src/canary_server.cpp` | 148 | `LuaApiDocGenerator apiDocGenerator(std::filesystem::current_path(), g_configManager().getString(LUA_API_DOCS_OUTPUT_DIRECTORY), logger);` |
| `src/database/database.cpp` | 94 | `std::filesystem::create_directories(backupDir);` |
| `src/database/database.cpp` | 119 | `std::filesystem::remove(tempConfigFile);` |
| `src/database/database.cpp` | 149 | `std::filesystem::remove(backupFileName);` |
| `src/database/database.cpp` | 156 | `for (const auto &entry : std::filesystem::directory_iterator("database_backup")) {` |
| `src/database/database.cpp` | 159 | `for (const auto &file : std::filesystem::directory_iterator(entry)) {` |
| `src/database/database.cpp` | 161 | `auto fileTime = std::filesystem::last_write_time(file);` |
| `src/database/database.cpp` | 162 | `auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(fileTime - std::filesystem::file_time_type::clock::now() + std::chrono::system_clock::now());` |
| `src/database/database.cpp` | 166 | `std::filesystem::remove(file);` |
| `src/database/database.cpp` | 171 | `} catch (const std::filesystem::filesystem_error &e) {` |
| `src/database/databasemanager.cpp` | 103 | `for (const auto &entry : std::filesystem::directory_iterator(migrationDirectory)) {` |
| `src/game/game.cpp` | 1019 | `void Game::loadCustomMaps(const std::filesystem::path &customMapPath) {` |
| `src/game/game.cpp` | 1023 | `namespace fs = std::filesystem;` |
| `src/game/game.cpp` | 1025 | `if (!fs::exists(customMapPath) && !fs::create_directory(customMapPath)) {` |
| `src/game/game.hpp` | 130 | `void loadCustomMaps(const std::filesystem::path &customMapPath);` |
| `src/game/scheduling/events_scheduler.cpp` | 58 | `const std::filesystem::path jsonEventSchedulerScriptsDir = "json/eventscheduler/scripts";` |
| `src/game/scheduling/events_scheduler.cpp` | 61 | `std::filesystem::path coreFolder;` |
| `src/game/scheduling/events_scheduler.cpp` | 62 | `std::filesystem::path primaryDir;` |
| `src/game/scheduling/events_scheduler.cpp` | 66 | `std::filesystem::path path { std::string(script) };` |
| `src/game/scheduling/events_scheduler.cpp` | 82 | `std::filesystem::path normalizedPath = path.lexically_normal();` |
| `src/game/scheduling/events_scheduler.cpp` | 96 | `std::optional<std::filesystem::path> resolveEventSchedulerScriptFilePath(` |
| `src/game/scheduling/events_scheduler.cpp` | 98 | `const std::filesystem::path &normalizedScript` |
| `src/game/scheduling/events_scheduler.cpp` | 100 | `const std::filesystem::path basePath = std::filesystem::current_path() / scriptSearchPaths.coreFolder;` |
| `src/game/scheduling/events_scheduler.cpp` | 101 | `std::filesystem::path primaryPath = basePath / scriptSearchPaths.primaryDir / normalizedScript;` |
| `src/game/scheduling/events_scheduler.cpp` | 102 | `if (std::filesystem::exists(primaryPath) && std::filesystem::is_regular_file(primaryPath)) {` |
| `src/game/scheduling/events_scheduler.cpp` | 126 | `const std::filesystem::path normalizedScript { *normalizedScriptOpt };` |
| `src/game/scheduling/events_scheduler.cpp` | 203 | `std::filesystem::path(coreFolder),` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 79 | `void incrementIterator(std::filesystem::recursive_directory_iterator &it, std::error_code &ec) {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1672 | `bool writeFileAtomically(const std::filesystem::path &path, const std::string &content, std::string &errorMessage) {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1674 | `const auto createdDirectory = std::filesystem::create_directories(path.parent_path(), ec);` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1681 | `if (std::filesystem::exists(path, ec) && !ec) {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1708 | `std::filesystem::rename(tempPath, path, ec);` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1710 | `const auto removedTarget = std::filesystem::remove(path, ec);` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1713 | `std::filesystem::rename(tempPath, path, ec);` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1723 | `LuaBindingScanner::LuaBindingScanner(std::filesystem::path rootPath) :` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1730 | `if (!std::filesystem::exists(sourceRoot, ec) \|\| ec) {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1734 | `std::filesystem::recursive_directory_iterator it(sourceRoot, std::filesystem::directory_options::skip_permission_denied, ec);` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1735 | `const std::filesystem::recursive_directory_iterator end;` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1763 | `void LuaBindingScanner::scanFile(const std::filesystem::path &filePath, LuaScanResult &result) const {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1776 | `void LuaBindingScanner::parseLuaReg(const std::string &content, const std::filesystem::path &filePath, LuaScanResult &result) const {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 1811 | `void LuaBindingScanner::parseRegistrations(const std::string &content, const std::filesystem::path &filePath, LuaScanResult &result) const {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2062 | `std::string LuaBindingScanner::relativePath(const std::filesystem::path &path) const {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2070 | `LuaApiDocGenerator::LuaApiDocGenerator(const std::filesystem::path &initialProjectRoot, std::filesystem::path outputDirectory, Logger &logger) :` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2078 | `const auto createdDirectory = std::filesystem::create_directories(docsDirectory, ec);` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2097 | `} catch (const std::filesystem::filesystem_error &e) {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2121 | `std::filesystem::path LuaApiDocGenerator::findProjectRoot(const std::filesystem::path &start) const {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2123 | `const auto existsWithoutError = [](const std::filesystem::path &path) {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2125 | `return std::filesystem::exists(path, ec) && !ec;` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2141 | `std::filesystem::path LuaApiDocGenerator::resolveDocsDirectory(const std::filesystem::path &outputDirectory) const {` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2142 | `const auto output = outputDirectory.empty() ? std::filesystem::path("docs/lua-api") : outputDirectory;` |
| `src/lua/docgen/lua_api_doc_generator.cpp` | 2242 | `return (std::filesystem::path(docsDirectoryPath) / fileName).generic_string();` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 75 | `explicit LuaBindingScanner(std::filesystem::path rootPath);` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 79 | `void scanFile(const std::filesystem::path &filePath, LuaScanResult &result) const;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 80 | `void parseLuaReg(const std::string &content, const std::filesystem::path &filePath, LuaScanResult &result) const;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 81 | `void parseRegistrations(const std::string &content, const std::filesystem::path &filePath, LuaScanResult &result) const;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 87 | `std::string relativePath(const std::filesystem::path &path) const;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 89 | `std::filesystem::path root;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 94 | `LuaApiDocGenerator(const std::filesystem::path &initialProjectRoot, std::filesystem::path outputDirectory, Logger &logger);` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 98 | `std::filesystem::path findProjectRoot(const std::filesystem::path &start) const;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 99 | `std::filesystem::path resolveDocsDirectory(const std::filesystem::path &outputDirectory) const;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 106 | `std::filesystem::path projectRoot;` |
| `src/lua/docgen/lua_api_doc_generator.hpp` | 107 | `std::filesystem::path docsDirectory;` |
| `src/lua/scripts/luascript.cpp` | 59 | `std::filesystem::path file;` |
| `src/lua/scripts/luascript.cpp` | 60 | `std::filesystem::path packFile;` |
| `src/lua/scripts/luascript.cpp` | 87 | `std::filesystem::path g_luaBytecodeCacheDirectory;` |
| `src/lua/scripts/luascript.cpp` | 89 | `std::filesystem::path g_luaStartupWorkingDirectory;` |
| `src/lua/scripts/luascript.cpp` | 119 | `std::optional<std::string> readLuaFileBuffer(const std::filesystem::path &file) {` |
| `src/lua/scripts/luascript.cpp` | 145 | `std::optional<LuaFileBufferLoadResult> loadLuaChunkFromFileBuffer(lua_State* luaState, const std::filesystem::path &file, const std::string &chunkName) {` |
| `src/lua/scripts/luascript.cpp` | 158 | `bool ensureLuaBytecodeCacheDirectory(const std::filesystem::path &cacheDirectory) {` |
| `src/lua/scripts/luascript.cpp` | 166 | `const auto createdDirectory = std::filesystem::create_directories(cacheDirectory, error);` |
| `src/lua/scripts/luascript.cpp` | 173 | `if (!std::filesystem::is_directory(cacheDirectory, statusError)) {` |
| `src/lua/scripts/luascript.cpp` | 184 | `[[nodiscard]] const std::filesystem::path &getLuaBytecodeCacheDirectory() {` |
| `src/lua/scripts/luascript.cpp` | 191 | `std::filesystem::path directory(configuredPath);` |
| `src/lua/scripts/luascript.cpp` | 194 | `const auto currentPath = std::filesystem::current_path(error);` |
| `src/lua/scripts/luascript.cpp` | 206 | `[[nodiscard]] const std::filesystem::path &getLuaStartupWorkingDirectory() {` |
| `src/lua/scripts/luascript.cpp` | 209 | `auto directory = std::filesystem::current_path(error);` |
| `src/lua/scripts/luascript.cpp` | 222 | `std::filesystem::path sourcePath(file);` |
| `src/lua/scripts/luascript.cpp` | 230 | `[[nodiscard]] std::filesystem::path getLuaBytecodePackFile(const std::string &sourceIdentity) {` |
| `src/lua/scripts/luascript.cpp` | 231 | `const auto sourceFolder = std::filesystem::path(sourceIdentity).parent_path().generic_string();` |
| `src/lua/scripts/luascript.cpp` | 257 | `[[nodiscard]] LuaBytecodePack readLuaBytecodePack(const std::filesystem::path &packFile) {` |
| `src/lua/scripts/luascript.cpp` | 300 | `[[nodiscard]] bool luaBytecodePackHasValidMagic(const std::filesystem::path &packFile) {` |
| `src/lua/scripts/luascript.cpp` | 335 | `void invalidateLuaBytecodePack(const std::filesystem::path &packFile) {` |
| `src/lua/scripts/luascript.cpp` | 338 | `static_cast<void>(std::filesystem::remove(packFile, error));` |
| `src/lua/scripts/luascript.cpp` | 353 | `const auto packSize = std::filesystem::file_size(cacheEntry.packFile, error);` |
| `src/lua/scripts/luascript.cpp` | 357 | `static_cast<void>(std::filesystem::remove(cacheEntry.packFile, error));` |
| `src/lua/scripts/luascript.cpp` | 399 | `const std::filesystem::directory_entry sourceEntry(file, error);` |
| `src/lua/scripts/luascript.cpp` | 461 | `static_cast<void>(std::filesystem::remove(temporaryFile, error));` |
| `src/lua/scripts/luascript.cpp` | 468 | `static_cast<void>(std::filesystem::remove(temporaryFile, error));` |
| `src/lua/scripts/luascript.cpp` | 474 | `static_cast<void>(std::filesystem::remove(cacheEntry.file, error));` |
| `src/lua/scripts/luascript.cpp` | 477 | `std::filesystem::rename(temporaryFile, cacheEntry.file, error);` |
| `src/lua/scripts/luascript.cpp` | 480 | `static_cast<void>(std::filesystem::remove(temporaryFile, error));` |
| `src/lua/scripts/luascript.cpp` | 545 | `static_cast<void>(std::filesystem::remove(bytecodeCacheEntry->file, error));` |
| `src/lua/scripts/luascript.hpp` | 22 | `std::filesystem::file_time_type lastWriteTime {};` |
| `src/lua/scripts/scripts.cpp` | 61 | `bool Scripts::loadEventSchedulerScripts(const std::filesystem::path &filePath) {` |
| `src/lua/scripts/scripts.cpp` | 62 | `if (!std::filesystem::exists(filePath) \|\| !std::filesystem::is_regular_file(filePath)) {` |
| `src/lua/scripts/scripts.cpp` | 81 | `const auto dir = std::filesystem::current_path() / folderName;` |
| `src/lua/scripts/scripts.cpp` | 88 | `if (!std::filesystem::exists(dir) \|\| !std::filesystem::is_directory(dir)) {` |
| `src/lua/scripts/scripts.cpp` | 104 | `for (const auto &entry : std::filesystem::recursive_directory_iterator(dir)) {` |
| `src/lua/scripts/scripts.hpp` | 26 | `bool loadEventSchedulerScripts(const std::filesystem::path &filePath);` |
| `src/map/map.cpp` | 56 | `if (mainMap && g_configManager().getBoolean(TOGGLE_DOWNLOAD_MAP) && !std::filesystem::exists(identifier)) {` |
| `src/map/map.hpp` | 36 | `std::filesystem::path getPath() const {` |
| `src/map/map.hpp` | 175 | `std::filesystem::path path;` |
| `tests/integration/game/money_it.cpp` | 15 | `previousPath_ = std::filesystem::current_path();` |
| `tests/integration/game/money_it.cpp` | 18 | `std::filesystem::current_path(repoRoot_);` |
| `tests/integration/game/money_it.cpp` | 28 | `std::filesystem::current_path(previousPath_);` |
| `tests/integration/game/money_it.cpp` | 32 | `std::filesystem::path repoRoot_ {};` |
| `tests/integration/game/money_it.cpp` | 33 | `std::filesystem::path previousPath_ {};` |
| `tests/integration/game/money_it.cpp` | 36 | `[[nodiscard]] static std::filesystem::path detectRepoRoot(std::filesystem::path start) {` |
| `tests/integration/game/money_it.cpp` | 37 | `const auto configPath = std::filesystem::path("tests/fixture/config/imbuements_test.lua");` |
| `tests/integration/game/money_it.cpp` | 40 | `const auto configExists = std::filesystem::exists(start / configPath, configEc);` |
| `tests/integration/game/otbm_loader_it.cpp` | 21 | `path = std::filesystem::temp_directory_path() / ("canary-otbm-loader-" + std::to_string(suffix));` |
| `tests/integration/game/otbm_loader_it.cpp` | 22 | `std::filesystem::create_directories(path);` |
| `tests/integration/game/otbm_loader_it.cpp` | 27 | `std::filesystem::remove_all(path, error);` |
| `tests/integration/game/otbm_loader_it.cpp` | 33 | `std::filesystem::path path;` |
| `tests/integration/game/otbm_loader_it.cpp` | 36 | `std::string shellQuote(const std::filesystem::path &value) {` |
| `tests/integration/game/otbm_loader_it.cpp` | 65 | `const auto fixtureScript = std::filesystem::path(TESTS_SOURCE_DIR) / "tests/fixture/generate_otbm_loader_fixture.py";` |
| `tests/integration/game/otbm_loader_it.cpp` | 66 | `const auto pythonExecutable = std::filesystem::path(CANARY_TEST_PYTHON_EXECUTABLE);` |
| `tests/integration/game/otbm_loader_it.cpp` | 72 | `ASSERT_TRUE(std::filesystem::is_regular_file(editedMap));` |
| `tests/integration/game/otbm_loader_it.cpp` | 73 | `ASSERT_TRUE(std::filesystem::is_regular_file(temporaryDirectory.path / "manifest.json"));` |
| `tests/integration/main.cpp` | 16 | `bool fileExists(const std::filesystem::path &path) {` |
| `tests/integration/main.cpp` | 18 | `return std::filesystem::exists(path, ec) && !ec;` |
| `tests/integration/main.cpp` | 21 | `std::filesystem::path detectRepoRoot(std::filesystem::path start) {` |
| `tests/integration/main.cpp` | 68 | `std::string detectConfigFile(const std::filesystem::path &repoRoot) {` |
| `tests/integration/main.cpp` | 108 | `const auto previousPath = std::filesystem::current_path();` |
| `tests/integration/main.cpp` | 115 | `std::filesystem::current_path(repoRoot);` |
| `tests/integration/main.cpp` | 116 | `std::fprintf(stderr, "[integration main] repoRoot=%s\n", std::filesystem::current_path().string().c_str());` |
| `tests/integration/main.cpp` | 120 | `const auto configFile = detectConfigFile(std::filesystem::current_path());` |
| `tests/integration/main.cpp` | 145 | `const auto appearancePath = (std::filesystem::path(config.getString(CORE_DIRECTORY)) / "items/appearances.dat").lexically_normal().string();` |
| `tests/integration/main.cpp` | 176 | `std::filesystem::current_path(previousPath);` |
| `tests/integration/test_database.hpp` | 84 | `if (std::filesystem::exists(TESTS_ENV_DEFAULT)) {` |
| `tests/integration/test_database.hpp` | 89 | `namespace fs = std::filesystem;` |
| `tests/integration/test_database.hpp` | 147 | `const auto candidate = std::filesystem::path(directory) / name;` |
| `tests/integration/test_database.hpp` | 148 | `if (std::filesystem::exists(candidate)) {` |
| `tests/integration/test_database.hpp` | 230 | `static std::filesystem::path writeMysqlDefaultsFile(const DbConfig &config) {` |
| `tests/integration/test_database.hpp` | 231 | `auto path = std::filesystem::current_path() / fmt::format(".canary-test-mysql-{}.cnf", std::chrono::steady_clock::now().time_since_epoch().count());` |
| `tests/integration/test_database.hpp` | 246 | `std::filesystem::permissions(` |
| `tests/integration/test_database.hpp` | 248 | `std::filesystem::perms::owner_read \| std::filesystem::perms::owner_write,` |
| `tests/integration/test_database.hpp` | 249 | `std::filesystem::perm_options::replace` |
| `tests/integration/test_database.hpp` | 268 | `if (!std::filesystem::exists(config.schemaPath)) {` |
| `tests/integration/test_database.hpp` | 272 | `std::filesystem::path defaultsFile;` |
| `tests/integration/test_database.hpp` | 284 | `std::filesystem::remove(defaultsFile);` |
| `tests/integration/test_database.hpp` | 289 | `std::filesystem::remove(defaultsFile);` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 13 | `previousPath_ = std::filesystem::current_path();` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 14 | `repoRoot_ = detectRepoRoot(std::filesystem::current_path());` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 16 | `std::filesystem::current_path(repoRoot_);` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 23 | `tempCoreDir_ = std::filesystem::temp_directory_path() / ("canary-events-scheduler-" + std::to_string(nowTicks));` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 24 | `std::filesystem::create_directories(tempCoreDir_ / "json/eventscheduler");` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 49 | `std::filesystem::remove_all(tempCoreDir_, ec);` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 50 | `std::filesystem::current_path(previousPath_);` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 89 | `std::filesystem::path repoRoot_ {};` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 90 | `std::filesystem::path previousPath_ {};` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 91 | `std::filesystem::path fixtureEventsJsonPath_ {};` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 92 | `std::filesystem::path eventsJsonPath_ {};` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 93 | `std::filesystem::path tempCoreDir_ {};` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 94 | `std::filesystem::path tempConfigFilePath_ {};` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 99 | `[[nodiscard]] static std::filesystem::path detectRepoRoot(std::filesystem::path start) {` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 100 | `const auto eventsRelative = std::filesystem::path("tests/fixture/core/json/eventscheduler/events.json");` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 101 | `const auto configRelative = std::filesystem::path("tests/fixture/config/events_scheduler_test.lua");` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 105 | `const auto eventsExists = std::filesystem::exists(start / eventsRelative, eventsEc);` |
| `tests/shared/game/events_scheduler_test_fixture.hpp` | 108 | `const auto configExists = std::filesystem::exists(start / configRelative, configEc);` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 33 | `previousPath_ = std::filesystem::current_path();` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 36 | `std::filesystem::current_path(repoRoot_);` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 50 | `std::filesystem::current_path(previousPath_);` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 54 | `std::filesystem::path repoRoot_ {};` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 55 | `std::filesystem::path previousPath_ {};` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 61 | `[[nodiscard]] static std::filesystem::path detectRepoRoot(std::filesystem::path start) {` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 62 | `const auto configPath = std::filesystem::path("tests/fixture/config/imbuements_test.lua");` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 63 | `const auto imbuementsPath = std::filesystem::path("tests/fixture/core/XML/imbuements.xml");` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 64 | `const auto vocationsPath = std::filesystem::path("tests/fixture/core/XML/vocations.xml");` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 68 | `const auto configExists = std::filesystem::exists(start / configPath, configEc);` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 71 | `const auto imbuementsExists = std::filesystem::exists(start / imbuementsPath, xmlEc);` |
| `tests/shared/imbuements/imbuements_test_fixture.hpp` | 72 | `const auto vocationsExists = std::filesystem::exists(start / vocationsPath, xmlEc);` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 252 | `std::vector<uint8_t> readFile(const std::filesystem::path& path) {` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 526 | `const std::filesystem::path& mapPath,` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 527 | `const std::filesystem::path& outputPath,` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 531 | `std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(".") : outputPath.parent_path());` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 739 | `const std::filesystem::path& outputPath,` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 757 | `if (std::filesystem::is_symlink(outputPath)) {` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 760 | `if (std::filesystem::exists(outputPath)) {` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 763 | `std::filesystem::create_directories(outputPath.parent_path().empty() ? std::filesystem::path(".") : outputPath.parent_path());` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 765 | `if (std::filesystem::is_symlink(temporaryPath)) {` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 768 | `std::filesystem::remove(temporaryPath);` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 1104 | `std::filesystem::rename(temporaryPath, outputPath);` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 1128 | `const std::filesystem::path mapPath = worldIndex ? argv[2] : argv[1];` |
| `tools/ai-agent/otbm_item_audit_scan.cpp` | 1129 | `const std::filesystem::path outputPath = worldIndex ? argv[3] : argv[2];` |
| `tools/ai-agent/otbm_reference_scan.cpp` | 31 | `std::filesystem::path mapPath;` |
| `tools/ai-agent/otbm_reference_scan.cpp` | 32 | `std::filesystem::path outputDirectory;` |
| `tools/ai-agent/otbm_reference_scan.cpp` | 85 | `std::vector<uint8_t> readFile(const std::filesystem::path& path) {` |
| `tools/ai-agent/otbm_reference_scan.cpp` | 192 | `std::filesystem::create_directories(options.outputDirectory);` |

## Broader mkdir mentions

| Path | Line | Source |
|---|---:|---|
| `.github/scripts/smoke_test_canary.py` | 179 | `map_path.parent.mkdir(parents=True, exist_ok=True)` |
| `.github/scripts/smoke_test_canary.py` | 202 | `download_target.parent.mkdir(parents=True, exist_ok=True)` |
| `.github/scripts/smoke_test_canary.py` | 278 | `log_dir.mkdir(parents=True, exist_ok=True)` |
| `.github/workflows/achievement-validation.yml` | 77 | `mkdir -p artifacts` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 1 | `name: Audit FS mkdir PR` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 17 | `if: github.repository == 'blakinio/canary' && github.event.pull_request.head.repo.full_name == 'blakinio/canary' && github.head_ref == 'security/fs-mkdir-shell-free'` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 23 | `ref: security/fs-mkdir-shell-free` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 34 | `python3 tools/ai-agent/audit_fs_mkdir.py` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 40 | `python3 -m json.tool artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json >/dev/null` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 45 | `rm -f tools/ai-agent/audit_fs_mkdir.py` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 46 | `rm -f .github/workflows/audit-fs-mkdir.yml` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 47 | `rm -f .github/workflows/audit-fs-mkdir-publish.yml` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 48 | `rm -f .github/workflows/audit-fs-mkdir-pr.yml` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 50 | `git add -f artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 51 | `git add -A tools/ai-agent/audit_fs_mkdir.py .github/workflows/audit-fs-mkdir.yml .github/workflows/audit-fs-mkdir-publish.yml .github/workflows/audit-fs-mkdir-pr.yml` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 57 | `allowed='^(artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT\.md\|artifacts/upstream/crystalserver/cs006_fs_mkdir_audit\.json\|tools/ai-agent/audit_fs_mkdir\.py\|\.github/workflows/audit-fs-mkdir\.yml\|\.github/workflows/audit-fs-mkdir-publish\.yml\|\.github/workflows/audit-fs-mkdir-pr\.yml)$'` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 62 | `test ! -e tools/ai-agent/audit_fs_mkdir.py` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 63 | `test ! -e .github/workflows/audit-fs-mkdir.yml` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 64 | `test ! -e .github/workflows/audit-fs-mkdir-publish.yml` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 65 | `test ! -e .github/workflows/audit-fs-mkdir-pr.yml` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 70 | `git commit -m "docs(security): publish FS mkdir call-site audit"` |
| `.github/workflows/audit-fs-mkdir-pr.yml` | 71 | `git push origin HEAD:security/fs-mkdir-shell-free` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 1 | `name: Publish FS mkdir audit` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 6 | `- security/fs-mkdir-shell-free` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 8 | `- .github/workflows/audit-fs-mkdir-publish.yml` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 16 | `if: github.repository == 'blakinio/canary' && github.ref == 'refs/heads/security/fs-mkdir-shell-free'` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 22 | `ref: security/fs-mkdir-shell-free` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 33 | `python3 tools/ai-agent/audit_fs_mkdir.py` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 34 | `python3 -m json.tool artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json >/dev/null` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 39 | `rm -f tools/ai-agent/audit_fs_mkdir.py` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 40 | `rm -f .github/workflows/audit-fs-mkdir.yml` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 41 | `rm -f .github/workflows/audit-fs-mkdir-publish.yml` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 43 | `git add -f artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 44 | `git add -A tools/ai-agent/audit_fs_mkdir.py .github/workflows/audit-fs-mkdir.yml .github/workflows/audit-fs-mkdir-publish.yml` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 50 | `allowed='^(artifacts/upstream/crystalserver/CS006_FS_MKDIR_AUDIT\.md\|artifacts/upstream/crystalserver/cs006_fs_mkdir_audit\.json\|tools/ai-agent/audit_fs_mkdir\.py\|\.github/workflows/audit-fs-mkdir\.yml\|\.github/workflows/audit-fs-mkdir-publish\.yml)$'` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 55 | `test ! -e tools/ai-agent/audit_fs_mkdir.py` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 56 | `test ! -e .github/workflows/audit-fs-mkdir.yml` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 57 | `test ! -e .github/workflows/audit-fs-mkdir-publish.yml` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 62 | `git commit -m "docs(security): publish FS mkdir call-site audit"` |
| `.github/workflows/audit-fs-mkdir-publish.yml` | 63 | `git push origin HEAD:security/fs-mkdir-shell-free` |
| `.github/workflows/deploy-canary-staging.yml` | 68 | `mkdir -p build/deployment-smoke-logs` |
| `.github/workflows/deploy-canary-staging.yml` | 79 | `mkdir -p "${work}/overlay" "${work}/deploy-root"` |
| `.github/workflows/deploy-canary-staging.yml` | 87 | `mkdir -p "${work}/overlay/$(dirname "${relative_file}")"` |
| `.github/workflows/deploy-pipeline.yml` | 40 | `mkdir -p build/deployment-test-logs` |
| `.github/workflows/deploy-pipeline.yml` | 49 | `mkdir -p "$work/deploy-root" "$work/content-v1/npc"` |
| `.github/workflows/deploy-pipeline.yml` | 83 | `mkdir -p "$work/content-v2"` |
| `.github/workflows/imbuement-validation.yml` | 78 | `mkdir -p artifacts` |
| `.github/workflows/otbm-map-tools.yml` | 61 | `mkdir -p artifacts` |
| `.github/workflows/otbm-reachability.yml` | 73 | `mkdir -p artifacts/toolkit` |
| `.github/workflows/otbm-spawn-npc-validation.yml` | 74 | `mkdir -p artifacts` |
| `.github/workflows/otbm-spawn-npc-validation.yml` | 111 | `mkdir -p artifacts/toolkit` |
| `.github/workflows/otbm-storage-graph.yml` | 64 | `mkdir -p artifacts` |
| `.github/workflows/otbm-storage-graph.yml` | 117 | `mkdir -p artifacts/toolkit` |
| `.github/workflows/quest-map-validation.yml` | 74 | `mkdir -p artifacts/toolkit` |
| `.github/workflows/quest-map-validation.yml` | 87 | `mkdir -p artifacts` |
| `.github/workflows/release.yml` | 335 | `mkdir -p dist` |
| `.github/workflows/release.yml` | 368 | `mkdir -p dist` |
| `.github/workflows/reusable-build-docker.yml` | 69 | `run: mkdir -p artifacts/docker-image artifacts/docker-rootfs/bin` |
| `.github/workflows/reusable-build-linux.yml` | 269 | `mkdir -p build/${{ matrix.buildtype }}/test-logs` |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 146 | `### CS-006 — shell construction in \`FS.mkdir\`` |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 151 | `- Files/symbols: \`data/libs/functions/fs.lua\`; \`FS.mkdir\`` |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 153 | `- Current Canary evidence: Canary concatenates the path into \`os.execute('mkdir "' .. path .. '"')\` without validation.` |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 251 | `2. **CS-006 — FS.mkdir security boundary**` |
| `artifacts/upstream/crystalserver/CRYSTALSERVER_COMPARISON_STAGE1.md` | 271 | `- \`FS.mkdir\` and \`table.unserialize\` reachability from untrusted input remains unknown.` |
| `artifacts/upstream/crystalserver/crystalserver_comparison_stage1.json` | 1 | `{"schema":"canary-crystalserver-comparison-v1","generated_at":"2026-07-13T21:01:05Z","analysis_date":"2026-07-13","stage":1,"functional_changes":false,"program_id":"CAN-PROGRAM-CRYSTALSERVER-COMPARISON","task_id":"CAN-20260713-crystalserver-comparison-inventory","baselines":{"target":{"repository":"blakinio/canary","branch":"main","sha":"360d79ebad5802edd4d89e99d0f210ab19b36b60","server_version":"3.6.1","client_protocol":1525,"access":"write-via-task-branch-and-pr"},"comparison":{"repository":"zimbadev/crystalserver","branch":"main","sha":"fc0d53b9f9965463b6082c07e6d3d482294541a7","server_version":"4.1.9","client_protocol":1525,"access":"read-only"},"reference":{"repository":"opentibiabr/canary","branch":"main","sha":"9365c1c4aa63529b9ff757f53737274894c02b8e","server_version":null,"client_protocol":null,"access":"read-only"}},"last_analyzed_crystal_commit":"fc0d53b9f9965463b6082c07e6d3d482294541a7","screening":{"queries":[{"term":"fix","hits_returned":50},{"term":"crash","hits_returned":30}],"overlap_not_fully_deduplicated":true,"deep_reviewed_unique":10,"deferred_unverified":4,"method":"Open CrystalServer diff, inspect corresponding current Canary source, then classify behaviorally."},"status_counts":{"ALREADY_PRESENT":2,"CANARY_SUPERIOR":1,"VALID_FIX_MISSING":1,"PARTIAL_VALUE":3,"CLIENT_COUPLED":2,"CONTENT_ONLY":0,"UNVERIFIED":0,"DANGEROUS":1,"REJECTED":0},"candidates":[{"id":"CS-001","repository":"zimbadev/crystalserver","crystal_commit":"a7350014528002fb27ed64d260a96d28a580d41a","author":"jprzimba","date":"2026-07-12","related_pr":822,"files":["src/creatures/combat/condition.cpp"],"symbols":["ConditionLight::startCondition","ConditionLight::unserializeProp"],"problem":"A zero light level reaches ticks / lightInfo.level and can cause integer division by zero.","evidence":["CrystalServer clamps the divisor and deserialized level to at least one.","Current Canary startCondition divides directly by lightInfo.level.","Current Canary deserialization assigns a persisted zero without normalization.","Other Canary mutation paths already clamp, showing a partial invariant."],"canary_locations":["src/creatures/combat/condition.cpp:ConditionLight::startCondition","src/creatures/combat/condition.cpp:ConditionLight::addCondition","src/creatures/combat/condition.cpp:ConditionLight::setParam","src/creatures/combat/condition.cpp:ConditionLight::unserializeProp"],"status":"VALID_FIX_MISSING","risk":"high","dependencies":["fresh ownership check","focused C++ regression test","required C++ build and CI"],"proposed_tests":["Deserialize CONDITIONATTR_LIGHTLEVEL=0 and start the condition without a division fault.","Verify normalized level and a valid lightChangeInterval.","Cover any reachable constructor or script path that can supply zero."],"decision":"Create a separate test-first implementation task after Stage 1 merges.","rationale":"The fault is deterministic from current source and the bounded guard is absent.","provenance_used":"Behavioral idea only: normalize invalid light level at persistence and division boundaries."},{"id":"CS-002","repository":"zimbadev/crystalserver","crystal_commit":"0c0f1acafd77a86fb5ce56fe768ff6d98d100c35","author":"jprzimba","date":"2026-07-11","related_pr":821,"files":["src/creatures/npcs/npc.cpp"],"symbols":["Npc::closeAllShopWindows"],"problem":"Callbacks while closing NPC shops can erase entries and invalidate iteration.","evidence":["CrystalServer snapshots GUIDs before callbacks.","Current Canary increments the iterator before calling closeShopWindow, then clears leftovers."],"canary_locations":["src/creatures/npcs/npc.cpp:Npc::closeAllShopWindows"],"status":"ALREADY_PRESENT","risk":"medium","dependencies":[],"proposed_tests":["Callbacks erase current entries while every shop player is visited exactly once and the map ends empty."],"decision":"No implementation.","rationale":"Current Canary already avoids using an iterator after the mutating callback.","provenance_used":"No code adapted."},{"id":"CS-003","repository":"zimbadev/crystalserver","crystal_commit":"90ac0eb7d2ba0a88476881c972d9de83fbbcb3e8","author":"matzinhozz","date":"2026-06-26","related_pr":799,"files":["src/lua/functions/core/libs/kv_functions.cpp"],"symbols":["KVFunctions::init","Lua::registerSharedClass","Lua::pushSharedUserdata"],"problem":"Shared KV userdata leaks if the metatable lacks shared-pointer garbage collection.","evidence":["CrystalServer changed non-shared class registration to shared registration.","Current Canary already uses typed registerSharedClass<KV> and pushSharedUserdata<KV>."],"canary_locations":["src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::init","src/lua/functions/core/libs/kv_functions.cpp:KVFunctions::luaKVScoped"],"status":"CANARY_SUPERIOR","risk":"high","dependencies":[],"proposed_tests":["Repeated scoped KV creation and Lua GC releases all Lua-held strong references."],"decision":"Preserve current Canary implementation.","rationale":"Canary already applies the safe typed shared-userdata pattern.","provenance_used":"No code adapted."},{"id":"CS-004","repository":"zimbadev/crystalserver","crystal_commit":"dcb4f00ffd55ede2399c979eee3b7fe6e7e0ee6e","author":"jprzimba","date":"2025-07-17","related_pr":292,"files":["src/items/containers/container.cpp"],"symbols":["Container::replaceThing"],"problem":"Null input or an out-of-range replacement index can cause invalid access.","evidence":["CrystalServer adds null and bounds guards.","Current Canary already performs both guards before item conversion and replacement."],"canary_locations":["src/items/containers/container.cpp:Container::replaceThing"],"status":"ALREADY_PRESENT","risk":"high","dependencies":[],"proposed_tests":["Null thing and index equal to size are no-ops with unchanged cache, weight, and parents."],"decision":"No implementation.","rationale":"Equivalent validation is already present.","provenance_used":"No code adapted."},{"id":"CS-005","repository":"zimbadev/crystalserver","crystal_commit":"fc0d53b9f9965463b6082c07e6d3d482294541a7","author":"jprzimba","date":"2026-07-12","related_pr":819,"files":["src/game/game.cpp","src/game/game.hpp"],"symbols":["Game::getPlayerByGUID","Game::addPlayer","Game::removePlayer"],"problem":"Online player GUID lookup is linear in the number of players.","evidence":["CrystalServer adds a GUID index maintained on add/remove.","Current Canary still scans the online player map.","No current Canary performance regression or benchmark was provided."],"canary_locations":["src/game/game.cpp:Game::getPlayerByGUID"],"status":"PARTIAL_VALUE","risk":"medium","dependencies":["benchmark","index lifecycle tests","concurrency review","resolve overlap with open PR #289"],"proposed_tests":["Add/remove/relogin consistency and duplicate GUID behavior.","Offline fallback remains unchanged.","Benchmark representative online-player counts."],"decision":"Defer until path ownership clears and measurements justify the index.","rationale":"The optimization is plausible but not a proven bug fix and adds synchronized state.","provenance_used":"Candidate design signal only."},{"id":"CS-006","repository":"zimbadev/crystalserver","crystal_commit":"891685169745e46f665069edcc35847f0704aa21","author":"jprzimba","date":"2026-07-10","related_pr":816,"files":["data/libs/functions/fs.lua"],"symbols":["FS.mkdir"],"problem":"A path is concatenated into a shell command without validation.","evidence":["Current Canary uses os.execute with a quoted but unsanitized path.","CrystalServer adds a denylist but still invokes a shell.","Call-site attacker control is not yet established."],"canary_locations":["data/libs/functions/fs.lua:FS.mkdir","data/libs/functions/fs.lua:FS.mkdir_p"],"status":"PARTIAL_VALUE","risk":"high","dependencies":["complete call-site inventory","supported path semantics","cross-platform safe filesystem API"],"proposed_tests":["Reject quotes, separators, substitutions, control characters, and other command syntax.","Preserve valid Windows, POSIX, relative, absolute, and Unicode paths as required.","Prove no shell interpretation occurs."],"decision":"Create a separate security task; do not copy the CrystalServer denylist.","rationale":"The dangerous construction exists, but the upstream patch is not a sufficient security design.","provenance_used":"Problem signal only; no parser or sanitizer code approved."},{"id":"CS-007","repository":"zimbadev/crystalserver","crystal_commit":"891685169745e46f665069edcc35847f0704aa21","author":"jprzimba","date":"2026-07-10","related_pr":816,"files":["data/libs/functions/tables.lua"],"symbols":["table.unserialize","table.serialize"],"problem":"Deserialization executes loadstring over the supplied serialized text.","evidence":["Current Canary evaluates loadstring('return ' .. str)().","CrystalServer replaces it with a bespoke parser.","Call-site trust and full serializer compatibility are not yet established."],"canary_locations":["data/libs/functions/tables.lua:table.serialize","data/libs/functions/tables.lua:table.unserialize"],"status":"PARTIAL_VALUE","risk":"high","dependencies":["complete call-site inventory","compatibility corpus","input size/depth policy","security review"],"proposed_tests":["Round-trip every value emitted by table.serialize.","Reject function calls, environment access, trailing code, malformed input, and resource-exhaustion payloads."],"decision":"Create a separate compatibility/security task; do not transplant the upstream parser.","rationale":"Dynamic execution is confirmed, but a replacement must preserve legitimate data and resist hostile input.","provenance_used":"Problem signal only; bespoke parser code not approved."},{"id":"CS-008","repository":"zimbadev/crystalserver","crystal_commit":"34cbec0c34325619ef23c5d12c940b7b1c276975","author":"jprzimba","date":"2026-07-01","related_pr":808,"files":["src/game/game.cpp","src/io/iomarket.cpp","src/io/iomarket.hpp"],"symbols":["Game::playerCreateMarketOffer","IOMarket::getActiveOffers","IOMarket::getPlayerOfferCountPerSide","IOMarket::getItemOfferCountPerSide"],"problem":"Large Market offer sets are claimed to crash the client.","evidence":["CrystalServer adds limits 1000, 700, and 1500 plus SQL LIMIT clauses.","Current Canary IOMarket lacks equivalent constants and count helpers.","No authoritative client capacity or exact protocol contract was established."],"canary_locations":["src/io/iomarket.hpp:IOMarket","src/io/iomarket.cpp","src/game/game.cpp:Game::playerCreateMarketOffer"],"status":"CLIENT_COUPLED","risk":"high","dependencies":["maintained OTClient source and tests","protocol 15.25 contract","DB concurrency test","physical-client E2E"],"proposed_tests":["Byte/payload boundary tests for oversized Market responses.","Concurrent offer creation does not bypass limits.","Exact ordering, pagination, per-player, and per-item behavior."],"decision":"No automatic implementation.","rationale":"The constants and behavior cannot be validated server-only.","provenance_used":"Candidate concept only."},{"id":"CS-009","repository":"zimbadev/crystalserver","crystal_commit":"cfc0c5c496eae53f1f33a07f563068f44914ddbb","author":"jprzimba","date":"2026-06-15","related_pr":766,"files":["src/enums/disconnect_client.hpp","src/server/network/protocol/protocolgame.cpp","src/server/network/protocol/protocolgame.hpp"],"symbols":["DisconnectClient_t","ProtocolGame::disconnectClient","ProtocolGame::onRecvFirstMessage"],"problem":"Disconnect packets without an expected reason byte are claimed to crash clients.","evidence":["CrystalServer appends a reason byte and classifies several rejection flows.","Current Canary disconnectClient accepts only a message.","Expected field presence/order and supported-profile behavior are unverified."],"canary_locations":["src/server/network/protocol/protocolgame.hpp:ProtocolGame::disconnectClient","src/server/network/protocol/protocolgame.cpp"],"status":"CLIENT_COUPLED","risk":"high","dependencies":["protocol-profile matrix","maintained OTClient parser","cross-repo contract","real-client integration"],"proposed_tests":["Byte-exact disconnect packets for each supported profile and reason.","Invalid credentials, outdated protocol, and duplicate-session real-client flows."],"decision":"No automatic implementation.","rationale":"Adding a byte is a protocol contract change even when both projects declare 15.25.","provenance_used":"Candidate packet shape only."},{"id":"CS-010","repository":"zimbadev/crystalserver","crystal_commit":"ffe4db548371c44ce01dfc280af0209318272292","author":"jprzimba","date":"2025-11-27","related_pr":513,"files":["src/game/game.cpp"],"symbols":["Game::removeCreature"],"problem":"Dereferencing a missing creature parent can crash removal.","evidence":["Current Canary dereferences creature->getParent() after optional tile removal.","CrystalServer returns false if parent is null.","The upstream return occurs after tile removal and notifications but before lifecycle cleanup."],"canary_locations":["src/game/game.cpp:Game::removeCreature"],"status":"DANGEROUS","risk":"critical","dependencies":["parent-null reproduction","lifecycle invariant","instance and multichannel review","focused integration tests"],"proposed_tests":["Parent null before removal and parent reset during tile removal.","Repeated removal for player, monster, NPC, and summon.","List, ID index, instance ownership, zone, summon, and logout cleanup remains complete."],"decision":"Investigate the defect signal but reject direct transplantation.","rationale":"The upstream early return can leave a creature partially removed and corrupt runtime state.","provenance_used":"Problem signal only; early-return implementation explicitly rejected."}],"deferred_backlog":[{"crystal_commit":"9e046413b965982745ca63559f68bd30264bfc9d","preliminary_status":"UNVERIFIED","reason":"Duplicate item-definition claim needs current Canary XML, identifier, and asset-contract validation."},{"crystal_commit":"809633b1f9fc9a690bef70ac0ecb916d5a5aa5d6","preliminary_status":"UNVERIFIED","reason":"God-command item limit is arbitrary without current parsing and resource-bound evidence."},{"crystal_commit":"55db69b7be12fa7b6a8865038033d953ae8cff18","preliminary_status":"UNVERIFIED","reason":"Corpse and reward-parent handling needs current symbol and state-transition tests."},{"crystal_commit":"6bda45e7d7b8f0e9a9c55b3b6b779b492504102f","preliminary_status":"UNVERIFIED","reason":"Broad spell-formula rewrite requires official behavior evidence and bounded decomposition."}],"proposed_tasks":[{"order":1,"candidate_ids":["CS-001"],"scope":"ConditionLight zero-level regression test and minimal fix."},{"order":2,"candidate_ids":["CS-006"],"scope":"FS.mkdir trust-boundary and safe filesystem-operation audit."},{"order":3,"candidate_ids":["CS-007"],"scope":"Serialized-table call-site inventory, compatibility corpus, and safe decoder design."},{"order":4,"candidate_ids":["CS-010"],"scope":"Creature-removal parent invariant reproduction and lifecycle-safe design."},{"order":5,"candidate_ids":["CS-008","CS-009"],"scope":"Separate maintained-OTClient protocol contract investigations."},{"order":6,"candidate_ids":["CS-005"],"scope":"GUID lookup benchmark and index-lifecycle proof after path ownership clears."}],"constraints":["All writes only to blakinio/canary.","No direct push to main.","No mass copying or broad cherry-picks.","No .otbm, items.otb, binary assets, sprites, secrets, private dumps, or production configuration.","One candidate implementation per task, branch, worktree, and draft PR.","Protocol, client, schema, migration, multichannel, instance, shared userdata, map, identifier, and asset candidates require extended analysis."],"limitations":["No local checkout or worktree was available.","Shell DNS could not resolve github.com, so local git status, branch, remote, worktree, ownership checker, diff-check, build, and tests were not run.","The 50 fix and 30 crash search hits overlap and are not a unique commit count.","Only ten unique candidate diffs were deeply reviewed.","No runtime reproduction or maintained-client integration was executed in Stage 1.","FS.mkdir and table.unserialize untrusted-input reachability is unknown.","Exact maintained OTClient Market and disconnect contracts are unknown."]}` |
| `data/events/scripts/player.lua` | 441 | `FS.mkdir_p(string.format("%s/reports/players/%s", CORE_DIRECTORY, name))` |
| `data/events/scripts/player.lua` | 489 | `FS.mkdir_p(string.format("%s/reports/bugs/%s", CORE_DIRECTORY, name))` |
| `data/libs/functions/fs.lua` | 12 | `function FS.mkdir(path)` |
| `data/libs/functions/fs.lua` | 16 | `local success, err = os.execute('mkdir "' .. path .. '"')` |
| `data/libs/functions/fs.lua` | 23 | `function FS.mkdir_p(path)` |
| `data/libs/functions/fs.lua` | 38 | `local success, err = FS.mkdir(currentPath)` |
| `docker/quickstart/myaac/Dockerfile` | 23 | `mkdir -p /tmp/myaac-src; \` |
| `docker/quickstart/myaac/Dockerfile` | 31 | `mkdir -p system/cache system/cache/twig system/logs system/php_sessions; \` |
| `docker/quickstart/myaac/entrypoint.sh` | 37 | `mkdir -p /canary/data/XML` |
| `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | 107 | `\| \`CS-006\` \| \`891685169745e46f665069edcc35847f0704aa21\` \| \`PARTIAL_VALUE\` \| high \| \`FS.mkdir\` shell construction \| Independent security task; do not copy upstream denylist. \|` |
| `docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md` | 190 | `- Which inputs reach \`FS.mkdir\` and \`table.unserialize\`, and are any attacker-controlled?` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 2 | `task_id: CAN-20260714-fs-mkdir-shell-injection` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 7 | `branch: security/fs-mkdir-shell-free` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 21 | `- docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 23 | `- artifacts/upstream/crystalserver/cs006_fs_mkdir_audit.json` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 24 | `- tools/ai-agent/audit_fs_mkdir.py` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 25 | `- .github/workflows/audit-fs-mkdir.yml` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 48 | `- "FS.mkdir(path) return contract (preserve unless evidence requires a compatible extension)"` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 49 | `- "FS.mkdir_p(path) behavior through FS.mkdir"` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 55 | `Determine whether \`FS.mkdir\` can execute shell metacharacters from any reachable Canary call site, then remove shell execution through the smallest architecture-native solution if the risk is confirmed, while preserving valid directory-creation behavior on maintained platforms.` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 59 | `- [ ] Full current-repository inventory of \`FS.mkdir\`, \`FS.mkdir_p\`, their call sites, and path provenance is recorded with exact files and lines.` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 74 | `- Current implementation uses \`os.execute('mkdir "' .. path .. '"')\` in \`data/libs/functions/fs.lua\`.` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 75 | `- The same file exposes \`FS.mkdir_p\`, which delegates each path component to \`FS.mkdir\`.` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 77 | `- Open PR search for \`FS.mkdir\`, \`fs.lua\`, and \`mkdir_p\` returned no overlap at task start.` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 93 | `- No open PR matched \`FS.mkdir\`, \`fs.lua\`, or \`mkdir_p\`.` |
| `docs/agents/tasks/active/CAN-20260714-fs-mkdir-shell-injection.md` | 136 | `- Security: direct command construction can become command injection if any path contains shell metacharacters and reaches \`FS.mkdir\`.` |
| `docs/agents/tasks/archive/CAN-20260713-crystalserver-comparison-inventory.md` | 103 | `2. Independently investigate \`CS-006\` (\`FS.mkdir\`) and \`CS-007\` (\`table.unserialize\`) without copying the upstream denylist/parser.` |
| `docs/building/wsl-debian.md` | 32 | `mkdir -p ~/.config/environment.d` |
| `docs/building/wsl-ubuntu-24.04.md` | 43 | `mkdir -p ~/.config/environment.d` |
| `docs/systems/ai-content-deployment.md` | 91 | `mkdir -p /srv/canary-content` |
| `recompile.sh` | 144 | `mkdir -p build && cd build` |
| `start.sh` | 8 | `mkdir -p logs` |
| `start_gdb.sh` | 7 | `mkdir -p logs` |
| `tests/build_and_run.sh` | 10 | `mkdir build` |
| `tests/fixture/generate_otbm_loader_fixture.py` | 121 | `output_dir.mkdir(parents=True, exist_ok=True)` |
| `tools/agents/task_ownership.py` | 354 | `args.write_index.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/achievement_validation.py` | 1013 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/achievement_validation.py` | 1064 | `args.markdown.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/build_promotion_handoff.py` | 143 | `args.json_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/build_promotion_handoff.py` | 144 | `args.markdown_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/cyclopedia_validation.py` | 419 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/evaluate_promotion_readiness.py` | 112 | `args.json_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/evaluate_promotion_readiness.py` | 113 | `args.markdown_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/examples/otbm_hd_tibiasr2x_backend.py` | 85 | `args.output_dir.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/generate_risk_report.py` | 110 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/generate_staging_patch.py` | 153 | `args.json_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/generate_staging_patch.py` | 154 | `args.patch_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/imbuement_storage_validation.py` | 307 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/imbuement_validation.py` | 700 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/imbuement_validation.py` | 706 | `args.runtime_plan.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/lib/io_utils.py` | 13 | `p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/materialize_promotion_overlay.py` | 97 | `output_dir.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/materialize_promotion_overlay.py` | 137 | `destination.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/materialize_promotion_overlay.py` | 165 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/normalize_research.py` | 91 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_appearances_tool.py` | 37 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_asset_tool.py` | 17 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_catalog.py` | 342 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd.py` | 56 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd.py` | 178 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd.py` | 442 | `output_sprites.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd.py` | 447 | `work_parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd.py` | 878 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd_batch.py` | 50 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd_batch.py` | 73 | `output_root.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd_batch.py` | 147 | `output_sprites.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd_batch.py` | 152 | `work_root.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd_batch.py` | 158 | `input_dir.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd_batch.py` | 159 | `raw_output_dir.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_hd_tool.py` | 80 | `report_path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_item_audit.py` | 283 | `scan_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_item_audit.py` | 292 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_patch.py` | 260 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_reachability.py` | 116 | `destination.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_reference.py` | 221 | `destination.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_reference.py` | 262 | `destination.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_reference.py` | 642 | `write_diff_to.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_reference.py` | 695 | `output_directory.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_render_tool.py` | 45 | `args.report.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_renderer.py` | 414 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_scan.py` | 178 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_scan.py` | 214 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_script_resolution.py` | 1450 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_spawn_npc_validation.py` | 1233 | `destination.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_sprite_tool.py` | 34 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_sprite_tool.py` | 56 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_storage_graph_analysis.py` | 467 | `destination.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_world_index.py` | 655 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_world_patch.py` | 552 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_world_patch.py` | 564 | `destination.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/otbm_world_patch.py` | 620 | `destination.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/quest_map_validation.py` | 60 | `target.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/render_content.py` | 124 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/render_content.py` | 143 | `base.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/research_provenance.py` | 82 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/research_to_task.py` | 144 | `args.task_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/research_to_task.py` | 145 | `args.report_output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/run_content_pipeline.py` | 49 | `output.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/run_research_pipeline.py` | 63 | `output.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/scan_content.py` | 176 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/scan_ids.py` | 215 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/scan_project.py` | 135 | `output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_achievement_validation.py` | 131 | `registry.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_achievement_validation.py` | 134 | `(root / "data-otservbr-global").mkdir()` |
| `tools/ai-agent/test_content_pipeline.py` | 112 | `(ROOT / "artifacts").mkdir(exist_ok=True)` |
| `tools/ai-agent/test_content_pipeline.py` | 121 | `(ROOT / "artifacts").mkdir(exist_ok=True)` |
| `tools/ai-agent/test_content_pipeline.py` | 143 | `(ROOT / "artifacts").mkdir(exist_ok=True)` |
| `tools/ai-agent/test_cyclopedia_validation.py` | 182 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_cyclopedia_validation.py` | 194 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_imbuement_storage_validation.py` | 41 | `(root / "data/XML").mkdir(parents=True)` |
| `tools/ai-agent/test_imbuement_storage_validation.py` | 42 | `(root / validation.STORAGE_REGISTRY_PATH).parent.mkdir(parents=True)` |
| `tools/ai-agent/test_imbuement_storage_validation.py` | 43 | `(root / validation.BOSS_UNLOCK_PATH).parent.mkdir(parents=True)` |
| `tools/ai-agent/test_materialize_promotion_overlay.py` | 18 | `preview.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_assets.py` | 20 | `self.assets.mkdir()` |
| `tools/ai-agent/test_otbm_hd.py` | 98 | `export_root.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_otbm_hd.py` | 132 | `export_root.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_otbm_hd.py` | 180 | `export_root.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_otbm_hd.py` | 184 | `override_root.mkdir()` |
| `tools/ai-agent/test_otbm_hd_batch.py` | 70 | `root.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_otbm_hd_batch.py` | 87 | `"out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)\n"` |
| `tools/ai-agent/test_otbm_hd_batch.py` | 217 | `output_root.mkdir()` |
| `tools/ai-agent/test_otbm_hd_batch.py` | 276 | `"import argparse\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument('--input-dir');p.add_argument('--output-dir');p.add_argument('--manifest');a=p.parse_args()\nout=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);(out/'1.png').symlink_to(Path(a.input_dir)/'1.png')\n",` |
| `tools/ai-agent/test_otbm_reference.py` | 184 | `reference.mkdir()` |
| `tools/ai-agent/test_otbm_renderer.py` | 107 | `assets.mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_script_resolution.py` | 21 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_runtime_semantics.py` | 25 | `(self.root / "world").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_runtime_semantics.py` | 26 | `(self.root / "monster").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_runtime_semantics.py` | 27 | `(self.root / "npc").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_runtime_semantics.py` | 28 | `(self.root / "scripts").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_validation.py` | 55 | `(self.root / "world").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_validation.py` | 56 | `(self.root / "monster" / "demons").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_validation.py` | 57 | `(self.root / "npc").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_spawn_npc_validation.py` | 58 | `(self.root / "scripts" / "quests" / "sample").mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_storage_graph.py` | 35 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/test_otbm_storage_graph.py` | 211 | `link.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_otbm_world_patch.py` | 240 | `output.mkdir()` |
| `tools/ai-agent/test_promotion_handoff.py` | 50 | `path.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_promotion_handoff.py` | 71 | `path.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_promotion_handoff.py` | 85 | `path.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_promotion_readiness.py` | 21 | `preview.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_promotion_readiness.py` | 48 | `preview.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_quest_map_validation.py` | 141 | `(self.root / "data/quests").mkdir(parents=True)` |
| `tools/ai-agent/test_research_pipeline.py` | 41 | `(ROOT / "artifacts").mkdir(exist_ok=True)` |
| `tools/ai-agent/test_research_pipeline.py` | 78 | `(ROOT / "artifacts").mkdir(exist_ok=True)` |
| `tools/ai-agent/test_research_pipeline.py` | 135 | `(ROOT / "artifacts").mkdir(exist_ok=True)` |
| `tools/ai-agent/test_scan_content.py` | 21 | `monster_dir.mkdir(parents=True)` |
| `tools/ai-agent/test_scan_content.py` | 22 | `quest_dir.mkdir(parents=True)` |
| `tools/ai-agent/test_scan_content.py` | 51 | `npc_dir.mkdir(parents=True)` |
| `tools/ai-agent/test_scan_project.py` | 19 | `(root / "src").mkdir()` |
| `tools/ai-agent/test_scan_project.py` | 21 | `(root / "data" / "monsters").mkdir(parents=True)` |
| `tools/ai-agent/test_scan_project.py` | 36 | `(root / "build").mkdir()` |
| `tools/ai-agent/test_staging_patch.py` | 36 | `source.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_staging_patch.py` | 50 | `source.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_staging_patch.py` | 53 | `target.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_staging_patch.py` | 67 | `source.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_staging_patch.py` | 84 | `source.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_weapon_proficiency_achievement_audit.py` | 70 | `registry.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_weapon_proficiency_achievement_audit.py` | 81 | `cpp.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_weapon_proficiency_achievement_audit.py` | 108 | `proficiencies.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_weapon_proficiency_achievement_audit.py` | 112 | `(root / "data-otservbr-global").mkdir()` |
| `tools/ai-agent/test_weapon_proficiency_forbidden_build_validation.py` | 14 | `baseline.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_weapon_proficiency_forbidden_build_validation.py` | 36 | `items.parent.mkdir(parents=True)` |
| `tools/ai-agent/test_wheel_of_destiny_validation.py` | 296 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/validate_references.py` | 93 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/verify_staging_patch.py` | 197 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/weapon_proficiency_achievement_audit.py` | 505 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/weapon_proficiency_achievement_audit.py` | 510 | `args.markdown.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/weapon_proficiency_forbidden_build_validation.py` | 208 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/weapon_proficiency_forbidden_build_validation.py` | 213 | `args.markdown.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/wheel_of_destiny_validation.py` | 610 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/wheel_of_destiny_validation.py` | 613 | `args.markdown.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/wheel_protocol_validation.py` | 200 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/wheel_protocol_validation.py` | 203 | `args.markdown.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/wheel_task_shop_validation.py` | 139 | `args.output.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/ai-agent/wheel_task_shop_validation.py` | 142 | `args.markdown.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/analytics/test_install_gameplay_analytics_guards.sh` | 9 | `mkdir -p "${TMP_DIR}/bin"` |
| `tools/deploy/canary_staging.py` | 70 | `target.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/deploy/canary_staging.py` | 78 | `destination_file.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/deploy/manifest.py` | 80 | `path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/deploy/release_manager.py` | 110 | `releases_dir.mkdir(parents=True, exist_ok=True)` |
| `tools/deploy/release_manager.py` | 112 | `tmp_dir.mkdir(parents=True, exist_ok=False)` |
| `tools/deploy/release_manager.py` | 117 | `dest_path.parent.mkdir(parents=True, exist_ok=True)` |
| `tools/deploy/run_canary_deployment.py` | 101 | `workspace_root.mkdir(parents=True, exist_ok=True)` |
| `tools/deploy/test_canary_staging.py` | 25 | `(base / "scripts").mkdir(parents=True)` |
| `tools/deploy/test_canary_staging.py` | 26 | `(base / "world").mkdir(parents=True)` |
| `tools/deploy/test_canary_staging.py` | 27 | `(overlay / "scripts").mkdir(parents=True)` |
| `tools/deploy/test_canary_staging.py` | 28 | `(overlay / "new").mkdir(parents=True)` |
| `tools/deploy/test_canary_staging.py` | 47 | `base.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 48 | `overlay.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 49 | `destination.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 59 | `base.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 60 | `overlay.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 78 | `base.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 79 | `overlay.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 83 | `target_path.mkdir(parents=True)` |
| `tools/deploy/test_canary_staging.py` | 99 | `(base / "conflict.lua").mkdir(parents=True)` |
| `tools/deploy/test_canary_staging.py` | 100 | `overlay.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 112 | `repo.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 113 | `datapack.mkdir()` |
| `tools/deploy/test_canary_staging.py` | 114 | `binary.parent.mkdir(parents=True)` |
| `tools/deploy/test_manifest.py` | 25 | `(root / "npc").mkdir()` |
| `tools/deploy/test_path_policy.py` | 17 | `(root / "sub").mkdir()` |
| `tools/deploy/test_path_policy.py` | 24 | `root.mkdir()` |
| `tools/deploy/test_path_policy.py` | 31 | `root.mkdir()` |
| `tools/deploy/test_path_policy.py` | 38 | `root.mkdir()` |
| `tools/deploy/test_path_policy.py` | 40 | `outside.mkdir()` |
| `tools/deploy/test_path_policy.py` | 51 | `root.mkdir()` |
| `tools/deploy/test_release_manager.py` | 38 | `self.root.mkdir()` |
| `tools/deploy/test_release_manager.py` | 40 | `self.source.mkdir()` |
| `tools/deploy/test_release_manager.py` | 41 | `(self.source / "npc").mkdir()` |
| `tools/deploy/test_release_manager.py` | 46 | `source.mkdir()` |
| `tools/deploy/test_release_manager.py` | 83 | `outside.mkdir()` |
| `tools/deploy/test_run_canary_deployment.py` | 26 | `repo.mkdir()` |
| `tools/deploy/test_run_canary_deployment.py` | 27 | `source.mkdir()` |
| `tools/deploy/test_run_canary_deployment.py` | 28 | `base.mkdir()` |
| `tools/deploy/test_run_canary_deployment.py` | 29 | `binary.parent.mkdir(parents=True)` |
| `tools/deploy/test_run_canary_deployment.py` | 31 | `releases.mkdir()` |
| `tools/deploy/test_run_canary_deployment.py` | 98 | `assembled.mkdir()` |
| `tools/deploy/test_run_canary_deployment.py` | 123 | `assembled.mkdir()` |

## Lua test harness signals

| Path | Line | Source |
|---|---:|---|
| `.github/workflows/gameplay-analytics-dry-run.yml` | 76 | `luajit tools/analytics/test_gameplay_analytics_context.lua` |
| `.github/workflows/gameplay-analytics-dry-run.yml` | 77 | `luajit tools/analytics/test_gameplay_analytics_batching.lua` |
| `.github/workflows/gameplay-analytics-dry-run.yml` | 78 | `luajit tools/analytics/test_gameplay_analytics_reliability.lua` |
| `.github/workflows/gameplay-analytics-dry-run.yml` | 79 | `luajit tools/analytics/test_gameplay_analytics_correctness.lua` |
| `.github/workflows/gameplay-analytics-dry-run.yml` | 80 | `luajit tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua` |
| `.github/workflows/gameplay-analytics-dry-run.yml` | 81 | `luajit tools/analytics/test_gameplay_analytics_schema.lua` |
| `.github/workflows/gameplay-analytics-dry-run.yml` | 82 | `luajit tools/analytics/test_gameplay_analytics_supply_loot_prices.lua` |
| `.github/workflows/gameplay-analytics-dry-run.yml` | 83 | `luajit tools/analytics/test_gameplay_analytics_supply_loot_integration.lua` |
| `.github/workflows/gameplay-analytics-spells.yml` | 13 | `- "tools/analytics/test_gameplay_analytics_spell_integration.lua"` |
| `.github/workflows/gameplay-analytics-spells.yml` | 27 | `- "tools/analytics/test_gameplay_analytics_spell_integration.lua"` |
| `.github/workflows/gameplay-analytics-spells.yml` | 53 | `run: luajit tools/analytics/test_gameplay_analytics_spell_integration.lua` |
| `.github/workflows/gameplay-analytics-supply-loot.yml` | 14 | `- "tools/analytics/test_gameplay_analytics_supply_loot_prices.lua"` |
| `.github/workflows/gameplay-analytics-supply-loot.yml` | 15 | `- "tools/analytics/test_gameplay_analytics_supply_loot_integration.lua"` |
| `.github/workflows/gameplay-analytics-supply-loot.yml` | 32 | `- "tools/analytics/test_gameplay_analytics_supply_loot_prices.lua"` |
| `.github/workflows/gameplay-analytics-supply-loot.yml` | 33 | `- "tools/analytics/test_gameplay_analytics_supply_loot_integration.lua"` |
| `.github/workflows/gameplay-analytics-supply-loot.yml` | 61 | `run: luajit tools/analytics/test_gameplay_analytics_supply_loot_prices.lua` |
| `.github/workflows/gameplay-analytics-supply-loot.yml` | 63 | `run: luajit tools/analytics/test_gameplay_analytics_supply_loot_integration.lua` |
| `.github/workflows/gameplay-analytics.yml` | 29 | `- "tools/analytics/test_gameplay_analytics_batching.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 30 | `- "tools/analytics/test_gameplay_analytics_context.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 31 | `- "tools/analytics/test_gameplay_analytics_correctness.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 32 | `- "tools/analytics/test_gameplay_analytics_reliability.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 33 | `- "tools/analytics/test_gameplay_analytics_schema.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 76 | `- "tools/analytics/test_gameplay_analytics_batching.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 77 | `- "tools/analytics/test_gameplay_analytics_context.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 78 | `- "tools/analytics/test_gameplay_analytics_correctness.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 79 | `- "tools/analytics/test_gameplay_analytics_reliability.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 80 | `- "tools/analytics/test_gameplay_analytics_schema.lua"` |
| `.github/workflows/gameplay-analytics.yml` | 147 | `run: luajit tools/analytics/test_gameplay_analytics_context.lua` |
| `.github/workflows/gameplay-analytics.yml` | 149 | `run: luajit tools/analytics/test_gameplay_analytics_batching.lua` |
| `.github/workflows/gameplay-analytics.yml` | 151 | `run: luajit tools/analytics/test_gameplay_analytics_reliability.lua` |
| `.github/workflows/gameplay-analytics.yml` | 153 | `run: luajit tools/analytics/test_gameplay_analytics_correctness.lua` |
| `.github/workflows/gameplay-analytics.yml` | 155 | `run: luajit tools/analytics/test_gameplay_analytics_schema.lua` |
| `.github/workflows/reusable-tests-lua.yml` | 15 | `name: Run Lua Tests` |
| `.github/workflows/reusable-tests-lua.yml` | 36 | `for f in tests/lua/test_*.lua; do` |
| `data-canary/lib/core/load.lua` | 1 | `dofile(DATA_DIRECTORY .. "/lib/core/storages.lua")` |
| `data-canary/lib/core/quests/catalog/init.lua` | 5 | `local catalog = dofile(CORE_DIRECTORY .. "/lib/core/quests/catalog.lua")` |
| `data-canary/lib/lib.lua` | 2 | `dofile(DATA_DIRECTORY .. "/lib/core/load.lua")` |
| `data-otservbr-global/lib/core/load.lua` | 1 | `dofile(DATA_DIRECTORY .. "/lib/core/storages.lua")` |
| `data-otservbr-global/lib/core/load.lua` | 2 | `dofile(DATA_DIRECTORY .. "/lib/core/constants.lua")` |
| `data-otservbr-global/lib/core/quests/catalog/init.lua` | 55 | `local catalog = dofile(CORE_DIRECTORY .. "/lib/core/quests/catalog.lua")` |
| `data-otservbr-global/lib/functions/load.lua` | 1 | `dofile(DATA_DIRECTORY .. "/lib/functions/players.lua")` |
| `data-otservbr-global/lib/lib.lua` | 2 | `dofile(DATA_DIRECTORY .. "/lib/core/load.lua")` |
| `data-otservbr-global/lib/lib.lua` | 5 | `dofile(DATA_DIRECTORY .. "/lib/others/load.lua")` |
| `data-otservbr-global/lib/lib.lua` | 8 | `dofile(DATA_DIRECTORY .. "/lib/quests/quest.lua")` |
| `data-otservbr-global/lib/lib.lua` | 11 | `dofile(DATA_DIRECTORY .. "/lib/tables/load.lua")` |
| `data-otservbr-global/lib/lib.lua` | 14 | `dofile(DATA_DIRECTORY .. "/lib/functions/load.lua")` |
| `data-otservbr-global/lib/others/dawnport.lua` | 1 | `dofile(CORE_DIRECTORY .. "/libs/functions/vocation.lua")` |
| `data-otservbr-global/lib/others/load.lua` | 1 | `dofile(DATA_DIRECTORY .. "/lib/others/dawnport.lua")` |
| `data-otservbr-global/lib/others/load.lua` | 2 | `dofile(DATA_DIRECTORY .. "/lib/others/soulpit.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 1 | `dofile(DATA_DIRECTORY .. "/lib/quests/bigfoot_burden.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 2 | `dofile(DATA_DIRECTORY .. "/lib/quests/demon_oak.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 3 | `dofile(DATA_DIRECTORY .. "/lib/quests/grimvale.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 4 | `dofile(DATA_DIRECTORY .. "/lib/quests/killing_in_the_name_of.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 5 | `dofile(DATA_DIRECTORY .. "/lib/quests/svargrond_arena.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 6 | `dofile(DATA_DIRECTORY .. "/lib/quests/the_cursed_crystal.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 7 | `dofile(DATA_DIRECTORY .. "/lib/quests/the_queen_of_the_banshees.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 8 | `dofile(DATA_DIRECTORY .. "/lib/quests/soul_war.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 9 | `dofile(DATA_DIRECTORY .. "/lib/quests/their_masters_voice.lua")` |
| `data-otservbr-global/lib/quests/quest.lua` | 10 | `dofile(DATA_DIRECTORY .. "/lib/quests/the_primal_ordeal.lua")` |
| `data-otservbr-global/lib/tables/load.lua` | 1 | `dofile(DATA_DIRECTORY .. "/lib/tables/teleport_item_destinations.lua")` |
| `data-otservbr-global/lib/tables/load.lua` | 2 | `dofile(DATA_DIRECTORY .. "/lib/tables/town.lua")` |
| `data-otservbr-global/npc/alesar.lua` | 1 | `dofile(DATA_DIRECTORY .. "/npc/alesar_functions.lua")` |
| `data-otservbr-global/scripts/creaturescripts/others/droploot.lua` | 1 | `dofile(CORE_DIRECTORY .. "/libs/systems/blessing.lua")` |
| `data-otservbr-global/scripts/globalevents/update.lua` | 2 | `dofile(fileToUpdate)` |
| `data-otservbr-global/scripts/spells/monster/gaz'haragoth_summon.lua` | 1 | `dofile(DATA_DIRECTORY .. "/scripts/spells/monster/gaz_functions.lua")` |
| `data-otservbr-global/scripts/systems/gameplay_analytics.lua` | 1 | `local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics.lua")` |
| `data-otservbr-global/scripts/systems/gameplay_analytics.lua` | 2 | `Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_context.lua")` |
| `data-otservbr-global/scripts/systems/gameplay_analytics.lua` | 3 | `Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua")` |
| `data-otservbr-global/scripts/systems/gameplay_analytics.lua` | 4 | `Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua")` |
| `data-otservbr-global/scripts/systems/gameplay_analytics.lua` | 5 | `Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")` |
| `data-otservbr-global/scripts/systems/gameplay_analytics.lua` | 6 | `Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")` |
| `data-otservbr-global/startup/others/load.lua` | 1 | `dofile(DATA_DIRECTORY .. "/startup/others/functions.lua")` |
| `data-otservbr-global/startup/startup.lua` | 1 | `dofile(DATA_DIRECTORY .. "/startup/tables/load.lua")` |
| `data-otservbr-global/startup/startup.lua` | 2 | `dofile(DATA_DIRECTORY .. "/startup/others/load.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 1 | `dofile(DATA_DIRECTORY .. "/startup/tables/chest.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 2 | `dofile(DATA_DIRECTORY .. "/startup/tables/corpse.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 3 | `dofile(DATA_DIRECTORY .. "/startup/tables/create_item.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 4 | `dofile(DATA_DIRECTORY .. "/startup/tables/door_key.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 5 | `dofile(DATA_DIRECTORY .. "/startup/tables/door_level.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 6 | `dofile(DATA_DIRECTORY .. "/startup/tables/door_quest.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 7 | `dofile(DATA_DIRECTORY .. "/startup/tables/item.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 8 | `dofile(DATA_DIRECTORY .. "/startup/tables/item_daily_reward.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 9 | `dofile(DATA_DIRECTORY .. "/startup/tables/item_unmovable.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 10 | `dofile(DATA_DIRECTORY .. "/startup/tables/lever.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 11 | `dofile(DATA_DIRECTORY .. "/startup/tables/teleport.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 12 | `dofile(DATA_DIRECTORY .. "/startup/tables/teleport_item.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 13 | `dofile(DATA_DIRECTORY .. "/startup/tables/tile.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 14 | `dofile(DATA_DIRECTORY .. "/startup/tables/tile_pick.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 15 | `dofile(DATA_DIRECTORY .. "/startup/tables/writeable.lua")` |
| `data-otservbr-global/startup/tables/load.lua` | 16 | `dofile(DATA_DIRECTORY .. "/startup/tables/storage_keys_update.lua")` |
| `data/core.lua` | 4 | `dofile(CORE_DIRECTORY .. "/global.lua")` |
| `data/core.lua` | 5 | `dofile(CORE_DIRECTORY .. "/libs/libs.lua")` |
| `data/core.lua` | 6 | `dofile(CORE_DIRECTORY .. "/stages.lua")` |
| `data/global.lua` | 3 | `dofile(DATA_DIRECTORY .. "/lib/lib.lua")` |
| `data/global.lua` | 7 | `dofile(DATA_DIRECTORY .. "/startup/startup.lua")` |
| `data/lib/core/quests/loader.lua` | 24 | `local loader, errorMessage = loadfile(filePath)` |
| `data/libs/compat/compat.lua` | 1427 | `dofile("config.lua")` |
| `data/libs/functions/load.lua` | 2 | `dofile(CORE_DIRECTORY .. "/libs/functions/bit.lua")` |
| `data/libs/functions/load.lua` | 3 | `dofile(CORE_DIRECTORY .. "/libs/functions/bitwise_flags.lua")` |
| `data/libs/functions/load.lua` | 4 | `dofile(CORE_DIRECTORY .. "/libs/functions/bank.lua")` |
| `data/libs/functions/load.lua` | 5 | `dofile(CORE_DIRECTORY .. "/libs/functions/boss_lever.lua")` |
| `data/libs/functions/load.lua` | 6 | `dofile(CORE_DIRECTORY .. "/libs/functions/combat.lua")` |
| `data/libs/functions/load.lua` | 7 | `dofile(CORE_DIRECTORY .. "/libs/functions/constants.lua")` |
| `data/libs/functions/load.lua` | 8 | `dofile(CORE_DIRECTORY .. "/libs/functions/container.lua")` |
| `data/libs/functions/load.lua` | 9 | `dofile(CORE_DIRECTORY .. "/libs/functions/creature.lua")` |
| `data/libs/functions/load.lua` | 10 | `dofile(CORE_DIRECTORY .. "/libs/functions/fs.lua")` |
| `data/libs/functions/load.lua` | 11 | `dofile(CORE_DIRECTORY .. "/libs/functions/functions.lua")` |
| `data/libs/functions/load.lua` | 12 | `dofile(CORE_DIRECTORY .. "/libs/functions/game.lua")` |
| `data/libs/functions/load.lua` | 13 | `dofile(CORE_DIRECTORY .. "/libs/functions/gematelier.lua")` |
| `data/libs/functions/load.lua` | 14 | `dofile(CORE_DIRECTORY .. "/libs/functions/item.lua")` |
| `data/libs/functions/load.lua` | 15 | `dofile(CORE_DIRECTORY .. "/libs/functions/itemtype.lua")` |
| `data/libs/functions/load.lua` | 16 | `dofile(CORE_DIRECTORY .. "/libs/functions/lever.lua")` |
| `data/libs/functions/load.lua` | 17 | `dofile(CORE_DIRECTORY .. "/libs/functions/modal_window_helper.lua")` |
| `data/libs/functions/load.lua` | 18 | `dofile(CORE_DIRECTORY .. "/libs/functions/monster.lua")` |
| `data/libs/functions/load.lua` | 19 | `dofile(CORE_DIRECTORY .. "/libs/functions/monstertype.lua")` |
| `data/libs/functions/load.lua` | 20 | `dofile(CORE_DIRECTORY .. "/libs/functions/party.lua")` |
| `data/libs/functions/load.lua` | 21 | `dofile(CORE_DIRECTORY .. "/libs/functions/player.lua")` |
| `data/libs/functions/load.lua` | 22 | `dofile(CORE_DIRECTORY .. "/libs/functions/position.lua")` |
| `data/libs/functions/load.lua` | 23 | `dofile(CORE_DIRECTORY .. "/libs/functions/pronouns.lua")` |
| `data/libs/functions/load.lua` | 24 | `dofile(CORE_DIRECTORY .. "/libs/functions/quests.lua")` |
| `data/libs/functions/load.lua` | 25 | `dofile(CORE_DIRECTORY .. "/libs/functions/queue.lua")` |
| `data/libs/functions/load.lua` | 26 | `dofile(CORE_DIRECTORY .. "/libs/functions/revscriptsys.lua")` |
| `data/libs/functions/load.lua` | 27 | `dofile(CORE_DIRECTORY .. "/libs/functions/set.lua")` |
| `data/libs/functions/load.lua` | 28 | `dofile(CORE_DIRECTORY .. "/libs/functions/spawn.lua")` |
| `data/libs/functions/load.lua` | 29 | `dofile(CORE_DIRECTORY .. "/libs/functions/spectators.lua")` |
| `data/libs/functions/load.lua` | 30 | `dofile(CORE_DIRECTORY .. "/libs/functions/string.lua")` |
| `data/libs/functions/load.lua` | 31 | `dofile(CORE_DIRECTORY .. "/libs/functions/tables.lua")` |
| `data/libs/functions/load.lua` | 32 | `dofile(CORE_DIRECTORY .. "/libs/functions/teleport.lua")` |
| `data/libs/functions/load.lua` | 33 | `dofile(CORE_DIRECTORY .. "/libs/functions/tile.lua")` |
| `data/libs/functions/load.lua` | 34 | `dofile(CORE_DIRECTORY .. "/libs/functions/vocation.lua")` |
| `data/libs/libs.lua` | 2 | `dofile(CORE_DIRECTORY .. "/libs/functions/load.lua")` |
| `data/libs/libs.lua` | 5 | `dofile(CORE_DIRECTORY .. "/libs/core/global_storage.lua")` |
| `data/libs/libs.lua` | 8 | `dofile(CORE_DIRECTORY .. "/libs/compat/compat.lua")` |
| `data/libs/libs.lua` | 11 | `dofile(CORE_DIRECTORY .. "/libs/debugging/dump.lua")` |
| `data/libs/libs.lua` | 14 | `dofile(CORE_DIRECTORY .. "/libs/systems/load.lua")` |
| `data/libs/libs.lua` | 17 | `dofile(CORE_DIRECTORY .. "/libs/tables/load.lua")` |
| `data/libs/systems/load.lua` | 2 | `dofile(CORE_DIRECTORY .. "/libs/systems/blessing.lua")` |
| `data/libs/systems/load.lua` | 3 | `dofile(CORE_DIRECTORY .. "/libs/systems/concoctions.lua")` |
| `data/libs/systems/load.lua` | 4 | `dofile(CORE_DIRECTORY .. "/libs/systems/daily_reward.lua")` |
| `data/libs/systems/load.lua` | 5 | `dofile(CORE_DIRECTORY .. "/libs/systems/encounters.lua")` |
| `data/libs/systems/load.lua` | 6 | `dofile(CORE_DIRECTORY .. "/libs/systems/exaltation_forge.lua")` |
| `data/libs/systems/load.lua` | 7 | `dofile(CORE_DIRECTORY .. "/libs/systems/familiar.lua")` |
| `data/libs/systems/load.lua` | 8 | `dofile(CORE_DIRECTORY .. "/libs/systems/features.lua")` |
| `data/libs/systems/load.lua` | 9 | `dofile(CORE_DIRECTORY .. "/libs/systems/hazard.lua")` |
| `data/libs/systems/load.lua` | 10 | `dofile(CORE_DIRECTORY .. "/libs/systems/hireling.lua")` |
| `data/libs/systems/load.lua` | 11 | `dofile(CORE_DIRECTORY .. "/libs/systems/raids.lua")` |
| `data/libs/systems/load.lua` | 12 | `dofile(CORE_DIRECTORY .. "/libs/systems/reward_boss.lua")` |
| `data/libs/systems/load.lua` | 13 | `dofile(CORE_DIRECTORY .. "/libs/systems/vip.lua")` |
| `data/libs/systems/load.lua` | 14 | `dofile(CORE_DIRECTORY .. "/libs/systems/zones.lua")` |
| `data/libs/tables/load.lua` | 2 | `dofile(CORE_DIRECTORY .. "/libs/tables/doors.lua")` |
| `data/libs/tables/load.lua` | 3 | `dofile(CORE_DIRECTORY .. "/libs/tables/windows.lua")` |
| `data/modules/scripts/gamestore/catalog/init.lua` | 30 | `local inlineCategories = dofile(basePath .. "parent_categories.lua")` |
| `data/modules/scripts/gamestore/catalog/init.lua` | 36 | `category = dofile(basePath .. moduleName .. ".lua")` |
| `data/modules/scripts/gamestore/gamestore.lua` | 9 | `dofile(CORE_DIRECTORY .. "/modules/scripts/gamestore/init.lua")` |
| `data/modules/scripts/gamestore/gamestore.lua` | 27 | `local catalogLoader = dofile(CORE_DIRECTORY .. "/modules/scripts/gamestore/catalog_loader.lua")` |
| `data/modules/scripts/gamestore/gamestore.lua` | 28 | `local catalogModules = dofile(CORE_DIRECTORY .. "/modules/scripts/gamestore/catalog/init.lua")` |
| `data/modules/scripts/gamestore/gamestore.lua` | 38 | `category = dofile(catalogBasePath .. moduleName .. ".lua")` |
| `data/modules/scripts/gamestore/gamestore.lua` | 43 | `category = dofile(catalogBasePath .. moduleName .. ".lua")` |
| `data/modules/scripts/gamestore/init.lua` | 4 | `return dofile(gamestoreLibPath .. "/" .. name .. ".lua")` |
| `data/npclib/load.lua` | 1 | `dofile(CORE_DIRECTORY .. "/npclib/npc.lua")` |
| `data/npclib/load.lua` | 2 | `dofile(CORE_DIRECTORY .. "/modules/scripts/npc/npc_dialog.lua")` |
| `data/npclib/load.lua` | 3 | `dofile(CORE_DIRECTORY .. "/npclib/npc_system/npc_handler.lua")` |
| `data/npclib/load.lua` | 4 | `dofile(CORE_DIRECTORY .. "/npclib/npc_system/keyword_handler.lua")` |
| `data/npclib/load.lua` | 5 | `dofile(CORE_DIRECTORY .. "/npclib/npc_system/modules.lua")` |
| `data/npclib/load.lua` | 6 | `dofile(CORE_DIRECTORY .. "/npclib/npc_system/custom_modules.lua")` |
| `data/npclib/load.lua` | 7 | `dofile(CORE_DIRECTORY .. "/npclib/npc_system/bank_system.lua")` |
| `data/scripts/actions/items/blessing_charms.lua` | 1 | `dofile(CORE_DIRECTORY .. "/libs/systems/blessing.lua")` |
| `data/scripts/actions/items/check_bless.lua` | 1 | `dofile(CORE_DIRECTORY .. "/libs/systems/blessing.lua")` |
| `data/scripts/actions/items/potions.lua` | 27 | `local AnalyticsPrices = dofile("data/scripts/lib/gameplay_analytics_prices.lua")` |
| `data/scripts/creaturescripts/player/adventure_blessing.lua` | 1 | `dofile(CORE_DIRECTORY .. "/libs/systems/blessing.lua")` |
| `data/scripts/eventcallbacks/monster/postdroploot_gameplay_analytics.lua` | 9 | `local AnalyticsLoot = dofile("data/scripts/lib/gameplay_analytics_loot.lua")` |
| `data/scripts/eventcallbacks/monster/postdroploot_gameplay_analytics.lua` | 10 | `local AnalyticsPrices = dofile("data/scripts/lib/gameplay_analytics_prices.lua")` |
| `data/scripts/runes/fireball.lua` | 14 | `local AnalyticsSpell = dofile("data/scripts/lib/gameplay_analytics_spell.lua")` |
| `data/scripts/runes/fireball.lua` | 15 | `local AnalyticsPrices = dofile("data/scripts/lib/gameplay_analytics_prices.lua")` |
| `data/scripts/runes/intense_healing_rune.lua` | 16 | `local AnalyticsSpell = dofile("data/scripts/lib/gameplay_analytics_spell.lua")` |
| `data/scripts/runes/intense_healing_rune.lua` | 17 | `local AnalyticsPrices = dofile("data/scripts/lib/gameplay_analytics_prices.lua")` |
| `data/scripts/spells/attack/ethereal_spear.lua` | 18 | `local AnalyticsSpell = dofile("data/scripts/lib/gameplay_analytics_spell.lua")` |
| `data/scripts/spells/healing/ultimate_healing.lua` | 15 | `local AnalyticsSpell = dofile("data/scripts/lib/gameplay_analytics_spell.lua")` |
| `data/scripts/talkactions/gm/bless_status.lua` | 1 | `dofile(CORE_DIRECTORY .. "/libs/systems/blessing.lua")` |
| `docs/agents/MODULE_CATALOG.md` | 50 | `\| Gameplay Analytics dry-run audit \| merged (#140) \| Deterministic Analytics logic/configuration tests without Canary or MariaDB \| \`.github/workflows/gameplay-analytics-dry-run.yml\`, \`tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua\`, \`tools/analytics/test_gameplay_analytics_maintenance_config_dry_run.sh\` \| Run before staging; it complements rather than replaces real engine/database integration. \|` |
| `docs/agents/tasks/active/CAN-20260713-forge-premium-dust.md` | 24 | `- tests/lua/test_exaltation_forge_premium.lua` |
| `docs/agents/tasks/archive/CAN-20260712-achievement-helper-fix.md` | 15 | `- tests/lua/test_achievement_helpers.lua` |
| `docs/agents/tasks/archive/CAN-20260713-equipment-upgrade-handoff-refresh.md` | 101 | `- \`Lua Tests / Run Lua Tests\` job \`86793054420\`: success; \`Run Tests\` succeeded.` |
| `docs/ai-agent/ACHIEVEMENT_HELPER_FIX.md` | 63 | `tests/lua/test_achievement_helpers.lua` |
| `docs/systems/gameplay-analytics-dry-run.md` | 22 | `\`tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua\` uses a deterministic clock and mocked players to cover:` |
| `docs/systems/gameplay-analytics-spells.md` | 73 | `local AnalyticsSpell = dofile("data/scripts/lib/gameplay_analytics_spell.lua")` |
| `src/config/configmanager.cpp` | 35 | `if (luaL_dofile(L, configFileLua.c_str())) {` |
| `src/database/databasemanager.cpp` | 119 | `if (luaL_dofile(L, scriptPath.c_str()) != 0) {` |
| `src/lua/scripts/luascript.cpp` | 558 | `ret = sourceLoadResult ? sourceLoadResult->status : luaL_loadfile(luaState, file.c_str());` |
| `tests/lua/test_achievement_helpers.lua` | 2 | `-- Run: luajit tests/lua/test_achievement_helpers.lua` |
| `tests/lua/test_achievement_helpers.lua` | 66 | `dofile("data/scripts/lib/register_achievements.lua")` |
| `tests/lua/test_exaltation_forge_premium.lua` | 54 | `dofile("data/libs/systems/exaltation_forge.lua")` |
| `tests/lua/test_npc_messaging.lua` | 2 | `-- Run: luajit tests/lua/test_npc_messaging.lua` |
| `tests/lua/test_npc_messaging.lua` | 55 | `dofile("data/npclib/npc.lua")` |
| `tests/lua/test_oasis_lever_door.lua` | 94 | `dofile("data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua")` |
| `tools/analytics/test_gameplay_analytics_batching.lua` | 70 | `local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua")` |
| `tools/analytics/test_gameplay_analytics_context.lua` | 137 | `local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_context.lua")` |
| `tools/analytics/test_gameplay_analytics_correctness.lua` | 86 | `local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")` |
| `tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua` | 105 | `local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")` |
| `tools/analytics/test_gameplay_analytics_correctness_edge_cases.lua` | 128 | `local secondLoad = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")` |
| `tools/analytics/test_gameplay_analytics_reliability.lua` | 83 | `local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")` |
| `tools/analytics/test_gameplay_analytics_schema.lua` | 57 | `local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua")` |
| `tools/analytics/test_gameplay_analytics_spell_integration.lua` | 7 | `local AnalyticsSpell = dofile("data/scripts/lib/gameplay_analytics_spell.lua")` |
| `tools/analytics/test_gameplay_analytics_supply_loot_integration.lua` | 7 | `local AnalyticsLoot = dofile("data/scripts/lib/gameplay_analytics_loot.lua")` |
| `tools/analytics/test_gameplay_analytics_supply_loot_prices.lua` | 7 | `local AnalyticsPrices = dofile("data/scripts/lib/gameplay_analytics_prices.lua")` |
| `tools/analytics/test_validate_gameplay_analytics_batching.py` | 37 | `batching = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_batching.py` | 38 | `reliability = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_context.py` | 62 | `core = 'local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_context.py` | 63 | `context = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_context.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_context.py` | 64 | `schema = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_correctness.py` | 33 | `reliability = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_correctness.py` | 34 | `correctness = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_migrations.py` | 46 | `context = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_context.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_migrations.py` | 47 | `schema = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua")'` |
| `tools/analytics/test_validate_gameplay_analytics_reliability.py` | 49 | `'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")',` |
| `tools/analytics/test_validate_gameplay_analytics_spell_integration.py` | 34 | `broken = self.integrated[path].replace('dofile("data/scripts/lib/gameplay_analytics_spell.lua")', "")` |
| `tools/analytics/test_validate_gameplay_analytics_spell_integration.py` | 40 | `broken = self.integrated[path] + f'\nlocal Analytics = dofile("{validator.CORE_PATH}")\n'` |
| `tools/analytics/test_validate_gameplay_analytics_supply_loot_integration.py` | 51 | `broken = self.loot_callback + f'\nlocal Analytics = dofile("{validator.CORE_PATH}")\n'` |
| `tools/analytics/test_validate_gameplay_analytics_supply_loot_integration.py` | 57 | `broken = self.supply_files[path].replace('dofile("data/scripts/lib/gameplay_analytics_prices.lua")', "")` |
| `tools/analytics/test_validate_gameplay_analytics_supply_loot_integration.py` | 63 | `broken = self.supply_files[path] + f'\nlocal Analytics = dofile("{validator.CORE_PATH}")\n'` |
| `tools/analytics/validate_gameplay_analytics_batching.py` | 55 | `core = 'dofile("data-otservbr-global/scripts/lib/gameplay_analytics.lua")'` |
| `tools/analytics/validate_gameplay_analytics_batching.py` | 56 | `batching = 'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua")'` |
| `tools/analytics/validate_gameplay_analytics_batching.py` | 57 | `reliability = 'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")'` |
| `tools/analytics/validate_gameplay_analytics_context.py` | 122 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics.lua")',` |
| `tools/analytics/validate_gameplay_analytics_context.py` | 123 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_context.lua")',` |
| `tools/analytics/validate_gameplay_analytics_context.py` | 124 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua")',` |
| `tools/analytics/validate_gameplay_analytics_context.py` | 125 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua")',` |
| `tools/analytics/validate_gameplay_analytics_context.py` | 126 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")',` |
| `tools/analytics/validate_gameplay_analytics_correctness.py` | 57 | `reliability = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")'` |
| `tools/analytics/validate_gameplay_analytics_correctness.py` | 58 | `correctness = 'Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")'` |
| `tools/analytics/validate_gameplay_analytics_migrations.py` | 89 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics.lua")',` |
| `tools/analytics/validate_gameplay_analytics_migrations.py` | 90 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_context.lua")',` |
| `tools/analytics/validate_gameplay_analytics_migrations.py` | 91 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua")',` |
| `tools/analytics/validate_gameplay_analytics_migrations.py` | 92 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua")',` |
| `tools/analytics/validate_gameplay_analytics_migrations.py` | 93 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")',` |
| `tools/analytics/validate_gameplay_analytics_reliability.py` | 110 | `'dofile("data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua")' in text,` |
| `tools/analytics/validate_gameplay_analytics_spell_integration.py` | 62 | `'dofile("data/scripts/lib/gameplay_analytics_spell.lua")' in text,` |
| `tools/analytics/validate_gameplay_analytics_supply_loot_integration.py` | 54 | `require('dofile("data/scripts/lib/gameplay_analytics_loot.lua")' in text, "loot callback must use the shared loot helper")` |
| `tools/analytics/validate_gameplay_analytics_supply_loot_integration.py` | 66 | `require('dofile("data/scripts/lib/gameplay_analytics_prices.lua")' in text, f"{label} must load the shared price table")` |

## Manual conclusions required

- Trace each call argument to a fixed literal, configuration, environment, database, player/network or command source.
- Verify whether an existing shell-free native binding can preserve maintained-platform behavior.
- Select a regression that proves no unintended marker command executes.
- Do not copy CrystalServer's denylist-plus-shell construction as the final design.

## Targeted integration evidence

This section was generated on the exact PR head after the broad audit. Results are bounded to name validation, Lua core-library registration, Lua tests and build anchors.

### Server-side name-validation symbols

```text
data/scripts/lib/register_migrations.lua:47:	if not self:_validateName() then
data/scripts/lib/register_migrations.lua:54:function Migration:_validateName()
src/utils/tools.cpp:1714:NameEval_t validateName(const std::string &name) {
src/utils/tools.hpp:167:NameEval_t validateName(const std::string &name);
tests/unit/security/login_session_manager_test.cpp:69:TEST(LoginSessionManagerTest, InvalidCharacterNameIsRejectedAndStillBurnsToken) {
```

### Tracked Lua tests

```text
tests/lua/test_achievement_helpers.lua
tests/lua/test_exaltation_forge_premium.lua
tests/lua/test_npc_messaging.lua
tests/lua/test_oasis_lever_door.lua
```

### Lua test loading and FS references

```text
tests/lua/test_achievement_helpers.lua:66:dofile("data/scripts/lib/register_achievements.lua")
tests/lua/test_exaltation_forge_premium.lua:54:dofile("data/libs/systems/exaltation_forge.lua")
tests/lua/test_npc_messaging.lua:55:dofile("data/npclib/npc.lua")
tests/lua/test_oasis_lever_door.lua:94:dofile("data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua")
```

### Core library registration and filesystem candidates

```text
src/lua/functions/core/core_functions.hpp:27:		CoreLibsFunctions::init(L);
src/lua/functions/core/libs/core_libs_functions.hpp:19:class CoreLibsFunctions final : LuaScriptInterface {
src/lua/functions/core/libs/core_libs_functions.hpp:21:	explicit CoreLibsFunctions(lua_State* L) :
src/lua/functions/core/libs/core_libs_functions.hpp:22:		LuaScriptInterface("CoreLibsFunctions") {
src/lua/functions/core/libs/core_libs_functions.hpp:25:	~CoreLibsFunctions() override = default;
src/lua/functions/core/libs/db_functions.cpp:18:	Lua::registerTable(L, "db");
src/lua/functions/core/libs/db_functions.cpp:19:	Lua::registerMethod(L, "db", "query", DBFunctions::luaDatabaseExecute);
src/lua/functions/core/libs/db_functions.cpp:20:	Lua::registerMethod(L, "db", "queryAffectedRows", DBFunctions::luaDatabaseExecuteAffectedRows);
src/lua/functions/core/libs/db_functions.cpp:21:	Lua::registerMethod(L, "db", "asyncQuery", DBFunctions::luaDatabaseAsyncExecute);
src/lua/functions/core/libs/db_functions.cpp:22:	Lua::registerMethod(L, "db", "storeQuery", DBFunctions::luaDatabaseStoreQuery);
src/lua/functions/core/libs/db_functions.cpp:23:	Lua::registerMethod(L, "db", "asyncStoreQuery", DBFunctions::luaDatabaseAsyncStoreQuery);
src/lua/functions/core/libs/db_functions.cpp:24:	Lua::registerMethod(L, "db", "escapeString", DBFunctions::luaDatabaseEscapeString);
src/lua/functions/core/libs/db_functions.cpp:25:	Lua::registerMethod(L, "db", "escapeBlob", DBFunctions::luaDatabaseEscapeBlob);
src/lua/functions/core/libs/db_functions.cpp:26:	Lua::registerMethod(L, "db", "lastInsertId", DBFunctions::luaDatabaseLastInsertId);
src/lua/functions/core/libs/db_functions.cpp:27:	Lua::registerMethod(L, "db", "tableExists", DBFunctions::luaDatabaseTableExists);
src/lua/functions/core/libs/kv_functions.cpp:19:	Lua::registerTable(L, "kv");
src/lua/functions/core/libs/kv_functions.cpp:20:	Lua::registerMethod(L, "kv", "scoped", KVFunctions::luaKVScoped);
src/lua/functions/core/libs/kv_functions.cpp:21:	Lua::registerMethod(L, "kv", "set", KVFunctions::luaKVSet);
src/lua/functions/core/libs/kv_functions.cpp:22:	Lua::registerMethod(L, "kv", "get", KVFunctions::luaKVGet);
src/lua/functions/core/libs/kv_functions.cpp:23:	Lua::registerMethod(L, "kv", "keys", KVFunctions::luaKVKeys);
src/lua/functions/core/libs/kv_functions.cpp:24:	Lua::registerMethod(L, "kv", "remove", KVFunctions::luaKVRemove);
src/lua/functions/core/libs/kv_functions.cpp:27:	Lua::registerMethod(L, "KV", "scoped", KVFunctions::luaKVScoped);
src/lua/functions/core/libs/kv_functions.cpp:28:	Lua::registerMethod(L, "KV", "set", KVFunctions::luaKVSet);
src/lua/functions/core/libs/kv_functions.cpp:29:	Lua::registerMethod(L, "KV", "get", KVFunctions::luaKVGet);
src/lua/functions/core/libs/kv_functions.cpp:30:	Lua::registerMethod(L, "KV", "keys", KVFunctions::luaKVKeys);
src/lua/functions/core/libs/kv_functions.cpp:31:	Lua::registerMethod(L, "KV", "remove", KVFunctions::luaKVRemove);
src/lua/functions/core/libs/logger_functions.cpp:15:	Lua::registerTable(L, "Spdlog");
src/lua/functions/core/libs/logger_functions.cpp:16:	Lua::registerMethod(L, "Spdlog", "info", LoggerFunctions::luaSpdlogInfo);
src/lua/functions/core/libs/logger_functions.cpp:17:	Lua::registerMethod(L, "Spdlog", "warn", LoggerFunctions::luaSpdlogWarn);
src/lua/functions/core/libs/logger_functions.cpp:18:	Lua::registerMethod(L, "Spdlog", "error", LoggerFunctions::luaSpdlogError);
src/lua/functions/core/libs/logger_functions.cpp:19:	Lua::registerMethod(L, "Spdlog", "debug", LoggerFunctions::luaSpdlogDebug);
src/lua/functions/core/libs/logger_functions.cpp:21:	Lua::registerTable(L, "logger");
src/lua/functions/core/libs/logger_functions.cpp:22:	Lua::registerMethod(L, "logger", "info", LoggerFunctions::luaLoggerInfo);
src/lua/functions/core/libs/logger_functions.cpp:23:	Lua::registerMethod(L, "logger", "warn", LoggerFunctions::luaLoggerWarn);
src/lua/functions/core/libs/logger_functions.cpp:24:	Lua::registerMethod(L, "logger", "error", LoggerFunctions::luaLoggerError);
src/lua/functions/core/libs/logger_functions.cpp:25:	Lua::registerMethod(L, "logger", "debug", LoggerFunctions::luaLoggerDebug);
src/lua/functions/core/libs/logger_functions.cpp:26:	Lua::registerMethod(L, "logger", "trace", LoggerFunctions::luaLoggerTrace);
src/lua/functions/core/libs/metrics_functions.cpp:16:	Lua::registerTable(L, "metrics");
src/lua/functions/core/libs/metrics_functions.cpp:17:	Lua::registerMethod(L, "metrics", "addCounter", MetricsFunctions::luaMetricsAddCounter);
src/lua/functions/core/libs/result_functions.cpp:14:	Lua::registerTable(L, "Result");
src/lua/functions/core/libs/result_functions.cpp:15:	Lua::registerMethod(L, "Result", "getNumber", ResultFunctions::luaResultGetNumber);
src/lua/functions/core/libs/result_functions.cpp:16:	Lua::registerMethod(L, "Result", "getString", ResultFunctions::luaResultGetString);
src/lua/functions/core/libs/result_functions.cpp:17:	Lua::registerMethod(L, "Result", "getStream", ResultFunctions::luaResultGetStream);
src/lua/functions/core/libs/result_functions.cpp:18:	Lua::registerMethod(L, "Result", "next", ResultFunctions::luaResultNext);
src/lua/functions/core/libs/result_functions.cpp:19:	Lua::registerMethod(L, "Result", "free", ResultFunctions::luaResultFree);
```

### Build registration anchors

```text
cmake/modules/CanaryLib.cmake:21:# Add more global sources Note: target_sources works on a specific target, we
cmake/modules/CanaryLib.cmake:23:target_sources(
src/CMakeLists.txt:47:            target_sources(
src/CMakeLists.txt:75:        target_sources(
src/account/CMakeLists.txt:1:target_sources(
src/config/CMakeLists.txt:1:target_sources(
src/creatures/CMakeLists.txt:1:target_sources(
src/database/CMakeLists.txt:1:target_sources(
src/database/databasemanager.cpp:13:#include "lua/functions/core/libs/core_libs_functions.hpp"
src/game/CMakeLists.txt:1:target_sources(
src/game/CMakeLists.txt:34:    target_sources(
src/io/CMakeLists.txt:1:target_sources(
src/items/CMakeLists.txt:1:target_sources(
src/kv/CMakeLists.txt:1:target_sources(
src/lib/CMakeLists.txt:1:target_sources(
src/lib/CMakeLists.txt:10:    target_sources(
src/lua/callbacks/CMakeLists.txt:1:target_sources(
src/lua/creature/CMakeLists.txt:1:target_sources(
src/lua/docgen/CMakeLists.txt:1:target_sources(
src/lua/functions/CMakeLists.txt:1:target_sources(
src/lua/functions/CMakeLists.txt:6:# Note: No target_sources here, just subdirectories
src/lua/functions/core/CMakeLists.txt:1:target_sources(
src/lua/functions/core/CMakeLists.txt:13:            libs/logger_functions.cpp
src/lua/functions/core/CMakeLists.txt:14:            libs/metrics_functions.cpp
src/lua/functions/core/CMakeLists.txt:15:            libs/kv_functions.cpp
src/lua/functions/core/core_functions.hpp:14:#include "lua/functions/core/libs/core_libs_functions.hpp"
src/lua/functions/core/libs/core_libs_functions.hpp:15:#include "lua/functions/core/libs/logger_functions.hpp"
src/lua/functions/core/libs/core_libs_functions.hpp:16:#include "lua/functions/core/libs/metrics_functions.hpp"
src/lua/functions/core/libs/core_libs_functions.hpp:17:#include "lua/functions/core/libs/kv_functions.hpp"
src/lua/functions/core/libs/kv_functions.cpp:10:#include "lua/functions/core/libs/kv_functions.hpp"
src/lua/functions/core/libs/logger_functions.cpp:10:#include "lua/functions/core/libs/logger_functions.hpp"
src/lua/functions/core/libs/metrics_functions.cpp:10:#include "lua/functions/core/libs/metrics_functions.hpp"
src/lua/functions/creatures/CMakeLists.txt:1:target_sources(
src/lua/functions/events/CMakeLists.txt:1:target_sources(
src/lua/functions/items/CMakeLists.txt:1:target_sources(
src/lua/functions/map/CMakeLists.txt:1:target_sources(
src/lua/global/CMakeLists.txt:1:target_sources(
src/lua/modules/CMakeLists.txt:1:target_sources(
src/lua/scripts/CMakeLists.txt:1:target_sources(
src/map/CMakeLists.txt:1:target_sources(
src/security/CMakeLists.txt:1:target_sources(
src/server/CMakeLists.txt:1:target_sources(
src/utils/CMakeLists.txt:1:target_sources(
vcproj/canary.vcxproj:175:    <ClInclude Include="..\src\lua\functions\core\libs\core_libs_functions.hpp" />
vcproj/canary.vcxproj:176:    <ClInclude Include="..\src\lua\functions\core\libs\kv_functions.hpp" />
vcproj/canary.vcxproj:179:    <ClInclude Include="..\src\lua\functions\core\libs\logger_functions.hpp" />
vcproj/canary.vcxproj:180:    <ClInclude Include="..\src\lua\functions\core\libs\metrics_functions.hpp" />
vcproj/canary.vcxproj:408:    <ClCompile Include="..\src\lua\functions\core\libs\kv_functions.cpp" />
vcproj/canary.vcxproj:411:    <ClCompile Include="..\src\lua\functions\core\libs\logger_functions.cpp" />
vcproj/canary.vcxproj:412:    <ClCompile Include="..\src\lua\functions\core\libs\metrics_functions.cpp" />
```
