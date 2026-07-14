/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <string>
#endif

struct FilesystemOperationResult {
	bool success = false;
	std::string error;
};

class FilesystemFunctions {
public:
	static void init(lua_State* L);
	static FilesystemOperationResult createDirectory(const std::string &path, bool recursive);

private:
	static int luaCreateDirectory(lua_State* L);
	static int luaCreateDirectories(lua_State* L);
	static int pushResult(lua_State* L, const FilesystemOperationResult &result);
};
