#pragma once

#include <nlohmann/json_fwd.hpp>

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <filesystem>
	#include <optional>
	#include <string>
	#include <unordered_map>
	#include <vector>
#endif

namespace game_catalog {

	struct RecordMetadata {
		std::optional<std::string> canonicalKey;
		std::optional<std::string> introducedIn;
		std::optional<std::string> removedIn;
		std::string completeness = "unverified";
		std::string availability = "unknown";
		bool enabled = true;
		std::optional<std::string> sourcePath;
		std::optional<std::string> imageKey;
	};

	struct CatalogManifest {
		std::string schemaVersion;
		std::string protocolProfile;
		std::string runtimeRelease;
		std::string contentTargetRelease;
		std::optional<std::string> verifiedContentThroughRelease;
		std::uint32_t lootChanceDenominator = 0;
		std::optional<std::string> containsContentThroughRelease;
		std::optional<std::string> datapackCommitSha;
		std::optional<std::string> producerBuildId;
		nlohmann::ordered_json releases;
		std::unordered_map<std::string, RecordMetadata> items;
		std::unordered_map<std::string, RecordMetadata> creatures;
		std::unordered_map<std::string, RecordMetadata> loot;
	};

	[[nodiscard]] CatalogManifest loadCatalogManifest(const std::filesystem::path &directory);

} // namespace game_catalog
