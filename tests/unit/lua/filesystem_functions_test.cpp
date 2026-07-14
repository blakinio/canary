/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "lua/functions/core/game/global_functions.hpp"
#include "lua/functions/lua_functions_loader.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <filesystem>
	#include <fstream>
	#include <memory>
	#include <string>
	#include <utility>
#endif

namespace {
	class TemporaryDirectory {
	public:
		TemporaryDirectory() {
			const auto unique = std::chrono::steady_clock::now().time_since_epoch().count();
			path = std::filesystem::temp_directory_path() / ("canary-fs-functions-" + std::to_string(unique));
			std::filesystem::create_directories(path);
		}

		~TemporaryDirectory() {
			std::error_code error;
			std::filesystem::remove_all(path, error);
		}

		std::filesystem::path path;
	};

	class LuaFilesystemState {
	public:
		LuaFilesystemState() :
			state(luaL_newstate(), &lua_close) {
			GlobalFunctions::init(state.get());
		}

		std::pair<bool, std::string> call(const char* method, const std::string &path) {
			lua_getglobal(state.get(), "FileSystem");
			lua_getfield(state.get(), -1, method);
			lua_remove(state.get(), -2);
			Lua::pushString(state.get(), path);
			if (lua_pcall(state.get(), 1, LUA_MULTRET, 0) != LUA_OK) {
				const std::string error = lua_tostring(state.get(), -1);
				lua_settop(state.get(), 0);
				return { false, error };
			}

			const int resultCount = lua_gettop(state.get());
			const bool success = resultCount >= 1 && lua_toboolean(state.get(), 1) != 0;
			const std::string error = resultCount >= 2 && lua_isstring(state.get(), 2) ? lua_tostring(state.get(), 2) : "";
			lua_settop(state.get(), 0);
			return { success, error };
		}

	private:
		std::unique_ptr<lua_State, decltype(&lua_close)> state;
	};
} // namespace

TEST(FilesystemFunctionsTest, CreatesSingleAndRecursiveDirectories) {
	TemporaryDirectory temporary;
	LuaFilesystemState lua;

	const auto single = temporary.path / "single directory";
	const auto [singleSuccess, singleError] = lua.call("createDirectory", single.string());
	EXPECT_TRUE(singleSuccess) << singleError;
	EXPECT_TRUE(std::filesystem::is_directory(single));

	const auto [existingSuccess, existingError] = lua.call("createDirectory", single.string());
	EXPECT_TRUE(existingSuccess) << existingError;

	const auto nested = temporary.path / "nested directory" / "child";
	const auto [recursiveSuccess, recursiveError] = lua.call("createDirectories", nested.string());
	EXPECT_TRUE(recursiveSuccess) << recursiveError;
	EXPECT_TRUE(std::filesystem::is_directory(nested));
}

TEST(FilesystemFunctionsTest, RejectsEmptyPathAndExistingFile) {
	LuaFilesystemState lua;
	const auto [emptySuccess, emptyError] = lua.call("createDirectory", "");
	EXPECT_FALSE(emptySuccess);
	EXPECT_FALSE(emptyError.empty());

	TemporaryDirectory temporary;
	const auto file = temporary.path / "existing-file";
	{
		std::ofstream output(file);
		output << "content";
	}

	const auto [fileSuccess, fileError] = lua.call("createDirectory", file.string());
	EXPECT_FALSE(fileSuccess);
	EXPECT_FALSE(fileError.empty());
}

TEST(FilesystemFunctionsTest, DoesNotInterpretShellMetacharacters) {
	TemporaryDirectory temporary;
	LuaFilesystemState lua;
	const auto unique = std::chrono::steady_clock::now().time_since_epoch().count();
	const auto marker = std::filesystem::current_path() / ("canary-fs-shell-marker-" + std::to_string(unique));
	std::error_code error;
	std::filesystem::remove(marker, error);

	const auto hostileName = "unsafe\" & echo injected > " + marker.filename().string() + " & echo \"";
	const auto hostilePath = temporary.path / hostileName;
	const auto [success, creationError] = lua.call("createDirectories", hostilePath.string());

	EXPECT_FALSE(std::filesystem::exists(marker));
#ifndef _WIN32
	EXPECT_TRUE(success) << creationError;
	EXPECT_TRUE(std::filesystem::is_directory(hostilePath));
#endif
	std::filesystem::remove(marker, error);
}
