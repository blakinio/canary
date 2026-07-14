/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */


#include "lua/functions/core/game/global_functions.hpp"

#include <gtest/gtest.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <filesystem>
	#include <memory>
	#include <optional>
	#include <stdexcept>
	#include <string>
#endif

namespace {
	struct LuaDirectoryResult {
		bool success = false;
		std::optional<std::string> error;
	};

	class FileSystemFunctionsTest : public ::testing::Test {
	protected:
		void SetUp() override {
			previousPath = std::filesystem::current_path();
			const auto suffix = std::chrono::steady_clock::now().time_since_epoch().count();
			temporaryPath = std::filesystem::temp_directory_path() / ("canary-filesystem-functions-" + std::to_string(suffix));
			std::filesystem::create_directories(temporaryPath);
			std::filesystem::current_path(temporaryPath);

			luaState.reset(luaL_newstate());
			ASSERT_NE(luaState, nullptr);
			luaL_openlibs(luaState.get());
			GlobalFunctions::init(luaState.get());
		}

		void TearDown() override {
			luaState.reset();
			std::filesystem::current_path(previousPath);
			std::error_code error;
			std::filesystem::remove_all(temporaryPath, error);
		}

		LuaDirectoryResult call(const char* method, const std::filesystem::path &path) {
			auto* L = luaState.get();
			lua_getglobal(L, "FileSystem");
			lua_getfield(L, -1, method);
			lua_remove(L, -2);
			lua_pushstring(L, path.string().c_str());
			if (lua_pcall(L, 1, 2, 0) != LUA_OK) {
				const std::string error = lua_tostring(L, -1) ? lua_tostring(L, -1) : "unknown Lua error";
				lua_settop(L, 0);
				ADD_FAILURE() << error;
				return {};
			}

			LuaDirectoryResult result;
			result.success = lua_toboolean(L, -2) != 0;
			if (lua_isstring(L, -1)) {
				result.error = lua_tostring(L, -1);
			}
			lua_settop(L, 0);
			return result;
		}

		std::filesystem::path previousPath;
		std::filesystem::path temporaryPath;
		std::unique_ptr<lua_State, decltype(&lua_close)> luaState { nullptr, &lua_close };
	};
} // namespace

TEST_F(FileSystemFunctionsTest, CreatesSingleDirectoryAndAcceptsExistingDirectory) {
	const auto path = temporaryPath / "reports with spaces";
	auto created = call("createDirectory", path);
	EXPECT_TRUE(created.success);
	EXPECT_FALSE(created.error.has_value());
	EXPECT_TRUE(std::filesystem::is_directory(path));

	auto existing = call("createDirectory", path);
	EXPECT_TRUE(existing.success);
	EXPECT_FALSE(existing.error.has_value());
}

TEST_F(FileSystemFunctionsTest, CreatesMissingParentDirectories) {
	const auto path = temporaryPath / "reports" / "bugs" / "Player Name";
	auto result = call("createDirectories", path);
	EXPECT_TRUE(result.success);
	EXPECT_FALSE(result.error.has_value());
	EXPECT_TRUE(std::filesystem::is_directory(path));
}

TEST_F(FileSystemFunctionsTest, TreatsShellMetacharactersAsLiteralPathCharacters) {
	const std::filesystem::path literalPath = "player$(touch marker)";
	auto result = call("createDirectory", literalPath);
	EXPECT_TRUE(result.success);
	EXPECT_TRUE(std::filesystem::is_directory(temporaryPath / literalPath));
	EXPECT_FALSE(std::filesystem::exists(temporaryPath / "marker"));
}

TEST_F(FileSystemFunctionsTest, ReturnsErrorWhenSingleDirectoryParentIsMissing) {
	auto result = call("createDirectory", std::filesystem::path("missing") / "child");
	EXPECT_FALSE(result.success);
	ASSERT_TRUE(result.error.has_value());
	EXPECT_FALSE(result.error->empty());
}
