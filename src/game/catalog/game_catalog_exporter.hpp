#pragma once

#include "game/catalog/catalog_export_options.hpp"
#include "game/catalog/game_catalog_manifest.hpp"

#include <nlohmann/json_fwd.hpp>

#ifndef USE_PRECOMPILED_HEADERS
	#include <filesystem>
	#include <string>
	#include <vector>
#endif

class Items;
class Monsters;

namespace game_catalog {

	struct ExportResult {
		std::filesystem::path outputPath;
		std::string sha256;
		std::size_t entityCount = 0;
		std::size_t relationCount = 0;
	};

	[[nodiscard]] nlohmann::ordered_json buildSnapshotDocument(
		const CatalogManifest &manifest,
		const Items &items,
		const Monsters &monsters,
		const std::string &generatedAt,
		const std::string &canaryCommitSha,
		const std::string &appearancesSha256
	);

	[[nodiscard]] std::vector<std::string> validateSnapshotDocument(const nlohmann::ordered_json &document);
	[[nodiscard]] std::string serializeSnapshotDocument(const nlohmann::ordered_json &document);
	[[nodiscard]] ExportResult publishSnapshotDocument(const nlohmann::ordered_json &document, const std::filesystem::path &outputPath);

} // namespace game_catalog
