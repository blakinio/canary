#pragma once

#include "game/catalog/game_catalog_exporter.hpp"
#include "game/catalog/game_catalog_manifest.hpp"

#include <nlohmann/json_fwd.hpp>

#ifndef USE_PRECOMPILED_HEADERS
	#include <filesystem>
	#include <string>
#endif

class Items;
class Monsters;
class Npcs;

namespace game_catalog {

	[[nodiscard]] nlohmann::ordered_json buildV13SnapshotDocument(
		const CatalogManifest &manifest,
		const Items &items,
		const Monsters &monsters,
		const Npcs &npcs,
		const std::string &generatedAt,
		const std::string &canaryCommitSha,
		const std::string &appearancesSha256
	);

	[[nodiscard]] ExportResult publishV13SnapshotDocument(
		const nlohmann::ordered_json &document,
		const std::filesystem::path &outputPath
	);

} // namespace game_catalog
