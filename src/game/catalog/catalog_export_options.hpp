#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <filesystem>
	#include <optional>
	#include <span>
	#include <string>
	#include <string_view>
#endif

namespace game_catalog {

	struct ExportOptions {
		std::filesystem::path outputPath;
		std::filesystem::path manifestDirectory;
		std::optional<std::string> generatedAt;
		std::optional<std::string> canaryCommitSha;
	};

	struct ExportOptionParseResult {
		bool requested = false;
		std::optional<ExportOptions> options;
		std::string error;
	};

	[[nodiscard]] ExportOptionParseResult parseExportOptions(std::span<char*> arguments);

} // namespace game_catalog
