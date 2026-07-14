/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "lua/functions/core/libs/filesystem_functions.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <filesystem>
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
} // namespace

TEST(FilesystemFunctionsTest, CreatesSingleAndRecursiveDirectories) {
	TemporaryDirectory temporary;

	const auto single = temporary.path / "single directory";
	const auto singleResult = FilesystemFunctions::createDirectory(single.string(), false);
	EXPECT_TRUE(singleResult.success) << singleResult.error;
	EXPECT_TRUE(std::filesystem::is_directory(single));

	const auto existingResult = FilesystemFunctions::createDirectory(single.string(), false);
	EXPECT_TRUE(existingResult.success) << existingResult.error;

	const auto nested = temporary.path / "nested directory" / "child";
	const auto recursiveResult = FilesystemFunctions::createDirectory(nested.string(), true);
	EXPECT_TRUE(recursiveResult.success) << recursiveResult.error;
	EXPECT_TRUE(std::filesystem::is_directory(nested));
}

TEST(FilesystemFunctionsTest, RejectsEmptyPathAndExistingFile) {
	const auto emptyResult = FilesystemFunctions::createDirectory("", false);
	EXPECT_FALSE(emptyResult.success);
	EXPECT_FALSE(emptyResult.error.empty());

	TemporaryDirectory temporary;
	const auto file = temporary.path / "existing-file";
	{
		std::ofstream output(file);
		output << "content";
	}

	const auto fileResult = FilesystemFunctions::createDirectory(file.string(), false);
	EXPECT_FALSE(fileResult.success);
	EXPECT_FALSE(fileResult.error.empty());
}

TEST(FilesystemFunctionsTest, DoesNotInterpretShellMetacharacters) {
	TemporaryDirectory temporary;
	const auto unique = std::chrono::steady_clock::now().time_since_epoch().count();
	const auto marker = std::filesystem::current_path() / ("canary-fs-shell-marker-" + std::to_string(unique));
	std::error_code error;
	std::filesystem::remove(marker, error);

	const auto hostileName = "unsafe\" & echo injected > " + marker.filename().string() + " & echo \"";
	const auto hostilePath = temporary.path / hostileName;
	const auto result = FilesystemFunctions::createDirectory(hostilePath.string(), true);

	EXPECT_FALSE(std::filesystem::exists(marker));
#ifndef _WIN32
	EXPECT_TRUE(result.success) << result.error;
	EXPECT_TRUE(std::filesystem::is_directory(hostilePath));
#endif
	std::filesystem::remove(marker, error);
}
