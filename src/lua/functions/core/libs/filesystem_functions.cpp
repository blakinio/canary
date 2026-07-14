/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "lua/functions/core/libs/filesystem_functions.hpp"

#include "lua/functions/lua_functions_loader.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <filesystem>
	#include <system_error>
#endif

void FilesystemFunctions::init(lua_State* L) {
	Lua::registerTable(L, "fs");
	Lua::registerMethod(L, "fs", "createDirectory", FilesystemFunctions::luaCreateDirectory);
	Lua::registerMethod(L, "fs", "createDirectories", FilesystemFunctions::luaCreateDirectories);
}

FilesystemOperationResult FilesystemFunctions::createDirectory(const std::string &path, bool recursive) {
	if (path.empty()) {
		return { false, "Path must not be empty." };
	}

	const std::filesystem::path directory(path);
	std::error_code error;
	if (std::filesystem::is_directory(directory, error)) {
		return { true, {} };
	}
	if (error) {
		return { false, error.message() };
	}

	const bool created = recursive ? std::filesystem::create_directories(directory, error) : std::filesystem::create_directory(directory, error);
	if (error) {
		return { false, error.message() };
	}
	if (created) {
		return { true, {} };
	}

	error.clear();
	if (std::filesystem::is_directory(directory, error)) {
		return { true, {} };
	}
	if (error) {
		return { false, error.message() };
	}

	return { false, "Path exists and is not a directory." };
}

int FilesystemFunctions::luaCreateDirectory(lua_State* L) {
	// fs.createDirectory(path)
	if (!Lua::isString(L, 1)) {
		lua_pushboolean(L, false);
		Lua::pushString(L, "Path must be a string.");
		return 2;
	}

	return pushResult(L, createDirectory(Lua::getString(L, 1), false));
}

int FilesystemFunctions::luaCreateDirectories(lua_State* L) {
	// fs.createDirectories(path)
	if (!Lua::isString(L, 1)) {
		lua_pushboolean(L, false);
		Lua::pushString(L, "Path must be a string.");
		return 2;
	}

	return pushResult(L, createDirectory(Lua::getString(L, 1), true));
}

int FilesystemFunctions::pushResult(lua_State* L, const FilesystemOperationResult &result) {
	lua_pushboolean(L, result.success);
	if (result.success) {
		return 1;
	}

	Lua::pushString(L, result.error);
	return 2;
}
