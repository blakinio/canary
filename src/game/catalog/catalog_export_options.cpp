#include "game/catalog/catalog_export_options.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <unordered_set>
#endif

namespace game_catalog {
	namespace {
		constexpr std::string_view ExportOnlyArgument = "--export-game-catalog-only";
		constexpr std::string_view OutputPrefix = "--game-catalog-output=";
		constexpr std::string_view ManifestPrefix = "--game-catalog-manifest-directory=";
		constexpr std::string_view GeneratedAtPrefix = "--game-catalog-generated-at=";
		constexpr std::string_view CommitPrefix = "--game-catalog-canary-commit=";

		[[nodiscard]] std::optional<std::string_view> valueAfterPrefix(const std::string_view value, const std::string_view prefix) {
			if (!value.starts_with(prefix)) {
				return std::nullopt;
			}
			return value.substr(prefix.size());
		}
	}

	ExportOptionParseResult parseExportOptions(const std::span<char*> arguments) {
		ExportOptionParseResult result;
		ExportOptions options;
		std::unordered_set<std::string> seen;

		for (std::size_t index = 1; index < arguments.size(); ++index) {
			const std::string_view argument(arguments[index]);
			if (argument == ExportOnlyArgument) {
				result.requested = true;
				continue;
			}

			const auto parseValue = [&](const std::string_view prefix, const std::string &key, auto &&consumer) -> bool {
				const auto value = valueAfterPrefix(argument, prefix);
				if (!value) {
					return false;
				}
				result.requested = true;
				if (value->empty()) {
					result.error = "Game Catalog argument value must not be empty: " + std::string(prefix);
					return true;
				}
				if (!seen.emplace(key).second) {
					result.error = "Duplicate Game Catalog argument: " + key;
					return true;
				}
				consumer(*value);
				return true;
			};

			if (parseValue(OutputPrefix, "output", [&](const std::string_view value) {
					options.outputPath = std::filesystem::path(value);
				})) {
				if (!result.error.empty()) {
					return result;
				}
				continue;
			}
			if (parseValue(ManifestPrefix, "manifest", [&](const std::string_view value) {
					options.manifestDirectory = std::filesystem::path(value);
				})) {
				if (!result.error.empty()) {
					return result;
				}
				continue;
			}
			if (parseValue(GeneratedAtPrefix, "generated_at", [&](const std::string_view value) {
					options.generatedAt = std::string(value);
				})) {
				if (!result.error.empty()) {
					return result;
				}
				continue;
			}
			if (parseValue(CommitPrefix, "canary_commit", [&](const std::string_view value) {
					options.canaryCommitSha = std::string(value);
				})) {
				if (!result.error.empty()) {
					return result;
				}
				continue;
			}
		}

		if (!result.requested) {
			return result;
		}
		if (options.outputPath.empty()) {
			result.error = "--game-catalog-output=<path> is required in export-only mode.";
			return result;
		}
		if (options.outputPath.filename().empty()) {
			result.error = "Game Catalog output must name a file, not a directory.";
			return result;
		}

		result.options = std::move(options);
		return result;
	}

} // namespace game_catalog
