#include "game/catalog/game_catalog_exporter.hpp"

#include "config/configmanager.hpp"
#include "core.hpp"
#include "creatures/monsters/monsters.hpp"
#include "game/catalog/catalog_definition_loader.hpp"
#include "items/item.hpp"
#include "utils/const.hpp"

#include <magic_enum/magic_enum.hpp>
#include <mbedtls/sha256.h>
#include <nlohmann/json.hpp>

#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <optional>
#include <regex>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <unordered_map>
#include <utility>
#include <vector>

namespace oteryn::catalog {
namespace {

using Json = nlohmann::ordered_json;

constexpr std::string_view ExportOnlyArgument = "--export-game-catalog-only";
constexpr std::string_view OutputArgumentPrefix = "--game-catalog-output=";
constexpr std::string_view GeneratedAtArgumentPrefix = "--game-catalog-generated-at=";
constexpr std::string_view ContractId = "oteryn.game-catalog";
constexpr std::string_view SchemaVersion = "1.0.0";
constexpr std::string_view ExpectedSchemaSha256 = "099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b";
constexpr std::uintmax_t MaximumManifestBytes = 4U * 1024U * 1024U;
constexpr std::size_t MaximumSnapshotBytes = 256U * 1024U * 1024U;
constexpr std::size_t MaximumStringBytes = 2000U;

struct ReleaseManifest {
	std::string key;
	std::string displayLabel;
	std::uint32_t major = 0;
	std::uint32_t minor = 0;
	std::uint32_t patch = 0;
	std::optional<std::uint32_t> build;
	std::uint64_t releaseOrder = 0;
	std::optional<std::string> protocolFamily;
	std::optional<std::string> releasedAt;
};

struct EntityMetadata {
	std::string canonicalKey;
	std::optional<std::string> introducedIn;
	std::optional<std::string> removedIn;
	std::string completeness;
	bool enabled = true;
	std::optional<std::string> sourcePath;
	std::vector<std::pair<std::string, std::string>> identifiers;
};

struct ItemManifest {
	std::uint16_t serverId = 0;
	EntityMetadata metadata;
	std::optional<std::string> imageKey;
};

struct LootManifest {
	std::string target;
	std::size_t occurrence = 0;
	std::optional<std::string> introducedIn;
	std::optional<std::string> removedIn;
	std::string completeness;
	bool enabled = true;
	std::optional<std::string> sourcePath;
};

struct CreatureManifest {
	std::string registryName;
	EntityMetadata metadata;
	std::optional<std::string> imageKey;
	std::vector<LootManifest> loot;
};

struct ProfileManifest {
	std::string canaryCommitSha;
	std::optional<std::string> datapackCommitSha;
	std::string protocolProfile;
	std::string runtimeRelease;
	std::string contentTargetRelease;
	std::string verifiedContentThroughRelease;
	std::optional<std::string> containsContentThroughRelease;
	std::optional<std::string> mapSha256;
	std::optional<std::string> producerBuildId;
};

struct CatalogManifests {
	ProfileManifest profile;
	std::vector<ReleaseManifest> releases;
	std::vector<ItemManifest> items;
	std::vector<CreatureManifest> creatures;
	std::unordered_map<std::string, std::string> itemAvailability;
	std::unordered_map<std::string, std::string> creatureAvailability;
};

struct RuntimeLoot {
	const LootBlock* block = nullptr;
	std::optional<std::string> containerPath;
	std::size_t occurrence = 0;
};

[[nodiscard]] bool startsWith(const std::string_view value, const std::string_view prefix) {
	return value.size() >= prefix.size() && value.substr(0, prefix.size()) == prefix;
}

[[nodiscard]] std::string toLowerAscii(std::string value) {
	std::transform(value.begin(), value.end(), value.begin(), [](const unsigned char character) {
		return static_cast<char>(std::tolower(character));
	});
	return value;
}

[[nodiscard]] std::string trimEnumPrefix(std::string value) {
	value = toLowerAscii(std::move(value));
	for (const std::string_view prefix : {
	         "item_type_",
	         "item_group_",
	         "weapon_",
	         "combat_",
	         "condition_",
	         "besty_race_",
	         "race_",
	     }) {
		if (startsWith(value, prefix)) {
			return value.substr(prefix.size());
		}
	}
	return value;
}

template <typename Enum>
[[nodiscard]] std::string enumLabel(const Enum value) {
	return trimEnumPrefix(std::string(magic_enum::enum_name(value)));
}

[[nodiscard]] std::string boundedString(const std::string &value, const std::size_t maximum, const std::string_view field) {
	if (value.size() > maximum) {
		throw std::runtime_error(fmt::format("{} exceeds {} bytes", field, maximum));
	}
	return value;
}

void require(const bool condition, const std::string &message) {
	if (!condition) {
		throw std::runtime_error(message);
	}
}

void requireObjectKeys(const Json &value, const std::set<std::string> &allowed, const std::string_view owner) {
	require(value.is_object(), fmt::format("{} must be a JSON object", owner));
	for (const auto &[key, ignored] : value.items()) {
		static_cast<void>(ignored);
		require(allowed.contains(key), fmt::format("{} contains unsupported key '{}'", owner, key));
	}
}

template <typename T>
[[nodiscard]] T requiredValue(const Json &value, const std::string_view key, const std::string_view owner) {
	require(value.contains(key), fmt::format("{} is missing required key '{}'", owner, key));
	try {
		return value.at(key).get<T>();
	} catch (const std::exception &error) {
		throw std::runtime_error(fmt::format("{}.{} has an invalid type: {}", owner, key, error.what()));
	}
}

[[nodiscard]] std::optional<std::string> nullableString(const Json &value, const std::string_view key, const std::string_view owner) {
	require(value.contains(key), fmt::format("{} is missing required key '{}'", owner, key));
	if (value.at(key).is_null()) {
		return std::nullopt;
	}
	return boundedString(requiredValue<std::string>(value, key, owner), MaximumStringBytes, fmt::format("{}.{}", owner, key));
}

[[nodiscard]] Json readJsonFile(const std::filesystem::path &path, const bool requiredFile) {
	std::error_code error;
	if (!std::filesystem::exists(path, error)) {
		if (requiredFile) {
			throw std::runtime_error(fmt::format("Required catalog manifest is missing: {}", path.generic_string()));
		}
		return nullptr;
	}
	require(!error, fmt::format("Cannot inspect catalog manifest {}: {}", path.generic_string(), error.message()));
	require(std::filesystem::is_regular_file(path, error), fmt::format("Catalog manifest is not a regular file: {}", path.generic_string()));
	require(!error, fmt::format("Cannot inspect catalog manifest {}: {}", path.generic_string(), error.message()));
	const auto size = std::filesystem::file_size(path, error);
	require(!error, fmt::format("Cannot read size of catalog manifest {}: {}", path.generic_string(), error.message()));
	require(size <= MaximumManifestBytes, fmt::format("Catalog manifest exceeds {} bytes: {}", MaximumManifestBytes, path.generic_string()));

	std::ifstream input(path, std::ios::binary);
	require(input.is_open(), fmt::format("Cannot open catalog manifest: {}", path.generic_string()));
	std::string content(static_cast<std::size_t>(size), '\0');
	if (size > 0) {
		input.read(content.data(), static_cast<std::streamsize>(size));
		require(input.good() || input.eof(), fmt::format("Cannot read catalog manifest: {}", path.generic_string()));
	}
	require(!startsWith(content, "\xEF\xBB\xBF"), fmt::format("UTF-8 BOM is forbidden in catalog manifest: {}", path.generic_string()));

	try {
		return Json::parse(content);
	} catch (const std::exception &error_) {
		throw std::runtime_error(fmt::format("Malformed catalog manifest {}: {}", path.generic_string(), error_.what()));
	}
}

[[nodiscard]] std::string sha256Bytes(const unsigned char* data, const std::size_t size) {
	std::array<unsigned char, 32> digest {};
	if (mbedtls_sha256(data, size, digest.data(), 0) != 0) {
		throw std::runtime_error("SHA-256 calculation failed");
	}

	std::ostringstream output;
	output << std::hex << std::setfill('0');
	for (const auto byte : digest) {
		output << std::setw(2) << static_cast<unsigned int>(byte);
	}
	return output.str();
}

[[nodiscard]] std::string sha256String(const std::string &value) {
	return sha256Bytes(reinterpret_cast<const unsigned char*>(value.data()), value.size());
}

[[nodiscard]] std::string sha256File(const std::filesystem::path &path) {
	std::ifstream input(path, std::ios::binary);
	require(input.is_open(), fmt::format("Cannot open file for SHA-256: {}", path.generic_string()));

	mbedtls_sha256_context context;
	mbedtls_sha256_init(&context);
	if (mbedtls_sha256_starts(&context, 0) != 0) {
		mbedtls_sha256_free(&context);
		throw std::runtime_error("SHA-256 initialization failed");
	}

	std::array<char, 64U * 1024U> buffer {};
	while (input.good()) {
		input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
		const auto count = input.gcount();
		if (count > 0 && mbedtls_sha256_update(
		                   &context,
		                   reinterpret_cast<const unsigned char*>(buffer.data()),
		                   static_cast<std::size_t>(count)
		               )
		        != 0) {
			mbedtls_sha256_free(&context);
			throw std::runtime_error("SHA-256 update failed");
		}
	}
	require(input.eof(), fmt::format("Failed while reading file for SHA-256: {}", path.generic_string()));

	std::array<unsigned char, 32> digest {};
	if (mbedtls_sha256_finish(&context, digest.data()) != 0) {
		mbedtls_sha256_free(&context);
		throw std::runtime_error("SHA-256 finalization failed");
	}
	mbedtls_sha256_free(&context);

	std::ostringstream output;
	output << std::hex << std::setfill('0');
	for (const auto byte : digest) {
		output << std::setw(2) << static_cast<unsigned int>(byte);
	}
	return output.str();
}

[[nodiscard]] bool matches(const std::string &value, const std::string &expression) {
	return std::regex_match(value, std::regex(expression, std::regex::ECMAScript));
}

void validateCanonicalKey(const std::string &value, const std::string_view owner) {
	require(
		value.size() >= 3 && value.size() <= 180
		    && matches(value, "^[a-z][a-z0-9_-]*:[a-z0-9][a-z0-9._-]*$"),
		fmt::format("{} has invalid canonical key '{}'", owner, value)
	);
}

void validateReleaseKey(const std::string &value, const std::string_view owner) {
	require(
		value.size() <= 32
		    && matches(value, "^[0-9]+(?:\\.[0-9]+){1,3}(?:[-+][A-Za-z0-9.-]+)?$"),
		fmt::format("{} has invalid release key '{}'", owner, value)
	);
}

void validateSha(const std::string &value, const std::size_t minimum, const std::size_t maximum, const std::string_view owner) {
	require(value.size() >= minimum && value.size() <= maximum && matches(value, "^[0-9a-f]+$"), fmt::format("{} has invalid lowercase hexadecimal hash", owner));
}

void validateSourcePath(const std::optional<std::string> &value, const std::string_view owner) {
	if (!value.has_value()) {
		return;
	}
	require(value->size() <= 512, fmt::format("{} source_path exceeds 512 bytes", owner));
	const std::filesystem::path path(*value);
	require(!path.is_absolute(), fmt::format("{} source_path must be relative", owner));
	for (const auto &part : path) {
		require(part != "..", fmt::format("{} source_path must not contain '..'", owner));
	}
}

[[nodiscard]] std::vector<std::pair<std::string, std::string>> parseIdentifiers(const Json &owner, const std::string_view ownerName) {
	if (!owner.contains("identifiers")) {
		return {};
	}
	require(owner.at("identifiers").is_array(), fmt::format("{}.identifiers must be an array", ownerName));
	require(owner.at("identifiers").size() <= 30, fmt::format("{}.identifiers exceeds 30 entries", ownerName));
	std::vector<std::pair<std::string, std::string>> result;
	for (std::size_t index = 0; index < owner.at("identifiers").size(); ++index) {
		const auto &identifier = owner.at("identifiers").at(index);
		requireObjectKeys(identifier, { "namespace", "value" }, fmt::format("{}.identifiers[{}]", ownerName, index));
		const auto nameSpace = requiredValue<std::string>(identifier, "namespace", ownerName);
		const auto value = requiredValue<std::string>(identifier, "value", ownerName);
		require(nameSpace.size() <= 80 && matches(nameSpace, "^[a-z][a-z0-9._-]*$"), fmt::format("{}.identifiers[{}] has invalid namespace", ownerName, index));
		require(!value.empty() && value.size() <= 160, fmt::format("{}.identifiers[{}] has invalid value", ownerName, index));
		result.emplace_back(nameSpace, value);
	}
	std::sort(result.begin(), result.end());
	require(std::adjacent_find(result.begin(), result.end()) == result.end(), fmt::format("{}.identifiers contains duplicates", ownerName));
	return result;
}

[[nodiscard]] EntityMetadata parseEntityMetadata(const Json &value, const std::string_view owner, const std::set<std::string> &extraKeys) {
	std::set<std::string> allowed {
		"canonical_key",
		"introduced_in",
		"removed_in",
		"completeness",
		"enabled",
		"source_path",
		"identifiers",
	};
	allowed.insert(extraKeys.begin(), extraKeys.end());
	requireObjectKeys(value, allowed, owner);

	EntityMetadata result;
	result.canonicalKey = boundedString(requiredValue<std::string>(value, "canonical_key", owner), 180, fmt::format("{}.canonical_key", owner));
	validateCanonicalKey(result.canonicalKey, owner);
	result.introducedIn = nullableString(value, "introduced_in", owner);
	result.removedIn = nullableString(value, "removed_in", owner);
	result.completeness = requiredValue<std::string>(value, "completeness", owner);
	require(
		std::set<std::string> { "complete", "partial", "unverified", "disabled", "missing_dependencies" }.contains(result.completeness),
		fmt::format("{}.completeness is unsupported", owner)
	);
	result.enabled = requiredValue<bool>(value, "enabled", owner);
	result.sourcePath = nullableString(value, "source_path", owner);
	validateSourcePath(result.sourcePath, owner);
	result.identifiers = parseIdentifiers(value, owner);
	return result;
}

[[nodiscard]] ProfileManifest parseProfile(const Json &root) {
	requireObjectKeys(
		root,
		{
			"contract",
			"schema_version",
			"canary_commit_sha",
			"datapack_commit_sha",
			"protocol_profile",
			"runtime_release",
			"content_target_release",
			"verified_content_through_release",
			"contains_content_through_release",
			"map_sha256",
			"producer_build_id",
		},
		"profile.json"
	);
	require(requiredValue<std::string>(root, "contract", "profile.json") == ContractId, "profile.json contract mismatch");
	require(requiredValue<std::string>(root, "schema_version", "profile.json") == SchemaVersion, "profile.json schema_version mismatch");

	ProfileManifest profile;
	profile.canaryCommitSha = requiredValue<std::string>(root, "canary_commit_sha", "profile.json");
	validateSha(profile.canaryCommitSha, 40, 64, "profile.json.canary_commit_sha");
	profile.datapackCommitSha = nullableString(root, "datapack_commit_sha", "profile.json");
	if (profile.datapackCommitSha.has_value()) {
		validateSha(*profile.datapackCommitSha, 40, 64, "profile.json.datapack_commit_sha");
	}
	profile.protocolProfile = boundedString(requiredValue<std::string>(root, "protocol_profile", "profile.json"), 80, "profile.json.protocol_profile");
	require(!profile.protocolProfile.empty(), "profile.json.protocol_profile must not be empty");
	profile.runtimeRelease = requiredValue<std::string>(root, "runtime_release", "profile.json");
	profile.contentTargetRelease = requiredValue<std::string>(root, "content_target_release", "profile.json");
	profile.verifiedContentThroughRelease = requiredValue<std::string>(root, "verified_content_through_release", "profile.json");
	profile.containsContentThroughRelease = nullableString(root, "contains_content_through_release", "profile.json");
	profile.mapSha256 = nullableString(root, "map_sha256", "profile.json");
	if (profile.mapSha256.has_value()) {
		validateSha(*profile.mapSha256, 64, 64, "profile.json.map_sha256");
	}
	profile.producerBuildId = nullableString(root, "producer_build_id", "profile.json");
	if (profile.producerBuildId.has_value()) {
		require(profile.producerBuildId->size() <= 160, "profile.json.producer_build_id exceeds 160 bytes");
	}
	return profile;
}

[[nodiscard]] std::vector<ReleaseManifest> parseReleases(const Json &root) {
	requireObjectKeys(root, { "contract", "schema_version", "releases" }, "releases.json");
	require(requiredValue<std::string>(root, "contract", "releases.json") == ContractId, "releases.json contract mismatch");
	require(requiredValue<std::string>(root, "schema_version", "releases.json") == SchemaVersion, "releases.json schema_version mismatch");
	require(root.at("releases").is_array(), "releases.json.releases must be an array");
	require(!root.at("releases").empty() && root.at("releases").size() <= 512, "releases.json.releases count is out of bounds");

	std::vector<ReleaseManifest> releases;
	for (std::size_t index = 0; index < root.at("releases").size(); ++index) {
		const auto owner = fmt::format("releases.json.releases[{}]", index);
		const auto &value = root.at("releases").at(index);
		requireObjectKeys(
			value,
			{ "key", "display_label", "major", "minor", "patch", "build", "release_order", "protocol_family", "released_at" },
			owner
		);
		ReleaseManifest release;
		release.key = requiredValue<std::string>(value, "key", owner);
		validateReleaseKey(release.key, owner);
		release.displayLabel = boundedString(requiredValue<std::string>(value, "display_label", owner), 48, fmt::format("{}.display_label", owner));
		release.major = requiredValue<std::uint32_t>(value, "major", owner);
		release.minor = requiredValue<std::uint32_t>(value, "minor", owner);
		release.patch = requiredValue<std::uint32_t>(value, "patch", owner);
		require(release.major <= 999 && release.minor <= 999 && release.patch <= 999, fmt::format("{} semantic version component exceeds 999", owner));
		if (!value.at("build").is_null()) {
			release.build = requiredValue<std::uint32_t>(value, "build", owner);
		}
		release.releaseOrder = requiredValue<std::uint64_t>(value, "release_order", owner);
		release.protocolFamily = nullableString(value, "protocol_family", owner);
		release.releasedAt = nullableString(value, "released_at", owner);
		releases.emplace_back(std::move(release));
	}
	std::sort(releases.begin(), releases.end(), [](const auto &left, const auto &right) {
		return std::tie(left.releaseOrder, left.key) < std::tie(right.releaseOrder, right.key);
	});
	return releases;
}

[[nodiscard]] std::vector<ItemManifest> parseItems(const Json &root) {
	requireObjectKeys(root, { "contract", "schema_version", "items" }, "versioning/items.json");
	require(requiredValue<std::string>(root, "contract", "versioning/items.json") == ContractId, "versioning/items.json contract mismatch");
	require(requiredValue<std::string>(root, "schema_version", "versioning/items.json") == SchemaVersion, "versioning/items.json schema_version mismatch");
	require(root.at("items").is_array(), "versioning/items.json.items must be an array");
	require(root.at("items").size() <= 200000, "versioning/items.json.items exceeds 200000 entries");

	std::vector<ItemManifest> result;
	for (std::size_t index = 0; index < root.at("items").size(); ++index) {
		const auto owner = fmt::format("versioning/items.json.items[{}]", index);
		const auto &value = root.at("items").at(index);
		ItemManifest item;
		item.metadata = parseEntityMetadata(value, owner, { "server_id", "image_key" });
		const auto serverId = requiredValue<std::uint32_t>(value, "server_id", owner);
		require(serverId <= std::numeric_limits<std::uint16_t>::max(), fmt::format("{}.server_id exceeds uint16", owner));
		item.serverId = static_cast<std::uint16_t>(serverId);
		item.imageKey = nullableString(value, "image_key", owner);
		if (item.imageKey.has_value()) {
			require(item.imageKey->size() <= 160, fmt::format("{}.image_key exceeds 160 bytes", owner));
		}
		result.emplace_back(std::move(item));
	}
	std::sort(result.begin(), result.end(), [](const auto &left, const auto &right) {
		return left.metadata.canonicalKey < right.metadata.canonicalKey;
	});
	return result;
}

[[nodiscard]] LootManifest parseLootMetadata(const Json &value, const std::string_view owner) {
	requireObjectKeys(
		value,
		{ "target", "occurrence", "introduced_in", "removed_in", "completeness", "enabled", "source_path" },
		owner
	);
	LootManifest result;
	result.target = requiredValue<std::string>(value, "target", owner);
	validateCanonicalKey(result.target, owner);
	result.occurrence = requiredValue<std::size_t>(value, "occurrence", owner);
	require(result.occurrence <= 999999, fmt::format("{}.occurrence is out of bounds", owner));
	result.introducedIn = nullableString(value, "introduced_in", owner);
	result.removedIn = nullableString(value, "removed_in", owner);
	result.completeness = requiredValue<std::string>(value, "completeness", owner);
	require(
		std::set<std::string> { "complete", "partial", "unverified", "disabled", "missing_dependencies" }.contains(result.completeness),
		fmt::format("{}.completeness is unsupported", owner)
	);
	result.enabled = requiredValue<bool>(value, "enabled", owner);
	result.sourcePath = nullableString(value, "source_path", owner);
	validateSourcePath(result.sourcePath, owner);
	return result;
}

[[nodiscard]] std::vector<CreatureManifest> parseCreatures(const Json &root) {
	requireObjectKeys(root, { "contract", "schema_version", "creatures" }, "versioning/creatures.json");
	require(requiredValue<std::string>(root, "contract", "versioning/creatures.json") == ContractId, "versioning/creatures.json contract mismatch");
	require(requiredValue<std::string>(root, "schema_version", "versioning/creatures.json") == SchemaVersion, "versioning/creatures.json schema_version mismatch");
	require(root.at("creatures").is_array(), "versioning/creatures.json.creatures must be an array");
	require(root.at("creatures").size() <= 200000, "versioning/creatures.json.creatures exceeds 200000 entries");

	std::vector<CreatureManifest> result;
	for (std::size_t index = 0; index < root.at("creatures").size(); ++index) {
		const auto owner = fmt::format("versioning/creatures.json.creatures[{}]", index);
		const auto &value = root.at("creatures").at(index);
		CreatureManifest creature;
		creature.metadata = parseEntityMetadata(value, owner, { "registry_name", "image_key", "loot" });
		creature.registryName = boundedString(requiredValue<std::string>(value, "registry_name", owner), 200, fmt::format("{}.registry_name", owner));
		require(!creature.registryName.empty(), fmt::format("{}.registry_name must not be empty", owner));
		creature.imageKey = nullableString(value, "image_key", owner);
		if (creature.imageKey.has_value()) {
			require(creature.imageKey->size() <= 160, fmt::format("{}.image_key exceeds 160 bytes", owner));
		}
		require(value.contains("loot") && value.at("loot").is_array(), fmt::format("{}.loot must be an array", owner));
		require(value.at("loot").size() <= 1000000, fmt::format("{}.loot exceeds 1000000 entries", owner));
		for (std::size_t lootIndex = 0; lootIndex < value.at("loot").size(); ++lootIndex) {
			creature.loot.emplace_back(parseLootMetadata(value.at("loot").at(lootIndex), fmt::format("{}.loot[{}]", owner, lootIndex)));
		}
		std::sort(creature.loot.begin(), creature.loot.end(), [](const auto &left, const auto &right) {
			return std::tie(left.target, left.occurrence) < std::tie(right.target, right.occurrence);
		});
		result.emplace_back(std::move(creature));
	}
	std::sort(result.begin(), result.end(), [](const auto &left, const auto &right) {
		return left.metadata.canonicalKey < right.metadata.canonicalKey;
	});
	return result;
}

[[nodiscard]] std::unordered_map<std::string, std::string> parseAvailability(
	const Json &root,
	const std::string_view entityKey,
	const std::set<std::string> &allowedAvailability,
	const std::string_view owner
) {
	if (root.is_null()) {
		return {};
	}
	requireObjectKeys(root, { "contract", "schema_version", std::string(entityKey) }, owner);
	require(requiredValue<std::string>(root, "contract", owner) == ContractId, fmt::format("{} contract mismatch", owner));
	require(requiredValue<std::string>(root, "schema_version", owner) == SchemaVersion, fmt::format("{} schema_version mismatch", owner));
	require(root.at(entityKey).is_array(), fmt::format("{}.{} must be an array", owner, entityKey));

	std::unordered_map<std::string, std::string> result;
	for (std::size_t index = 0; index < root.at(entityKey).size(); ++index) {
		const auto entryOwner = fmt::format("{}.{}[{}]", owner, entityKey, index);
		const auto &entry = root.at(entityKey).at(index);
		requireObjectKeys(entry, { "canonical_key", "availability" }, entryOwner);
		const auto canonicalKey = requiredValue<std::string>(entry, "canonical_key", entryOwner);
		validateCanonicalKey(canonicalKey, entryOwner);
		const auto availability = requiredValue<std::string>(entry, "availability", entryOwner);
		require(allowedAvailability.contains(availability), fmt::format("{}.availability is unsupported", entryOwner));
		require(result.emplace(canonicalKey, availability).second, fmt::format("{} duplicates canonical_key '{}'", owner, canonicalKey));
	}
	return result;
}

void validateApprovedBackports(const Json &root) {
	if (root.is_null()) {
		return;
	}
	requireObjectKeys(root, { "contract", "schema_version", "entries" }, "overrides/approved-backports.json");
	require(requiredValue<std::string>(root, "contract", "overrides/approved-backports.json") == ContractId, "approved-backports contract mismatch");
	require(requiredValue<std::string>(root, "schema_version", "overrides/approved-backports.json") == SchemaVersion, "approved-backports schema_version mismatch");
	require(root.at("entries").is_array(), "approved-backports entries must be an array");
	std::set<std::string> keys;
	for (std::size_t index = 0; index < root.at("entries").size(); ++index) {
		const auto owner = fmt::format("overrides/approved-backports.json.entries[{}]", index);
		const auto &entry = root.at("entries").at(index);
		requireObjectKeys(entry, { "canonical_key", "target_release", "reason", "evidence" }, owner);
		const auto key = requiredValue<std::string>(entry, "canonical_key", owner);
		validateCanonicalKey(key, owner);
		validateReleaseKey(requiredValue<std::string>(entry, "target_release", owner), owner);
		require(!requiredValue<std::string>(entry, "reason", owner).empty(), fmt::format("{}.reason must not be empty", owner));
		require(!requiredValue<std::string>(entry, "evidence", owner).empty(), fmt::format("{}.evidence must not be empty", owner));
		require(keys.emplace(key + "|" + requiredValue<std::string>(entry, "target_release", owner)).second, fmt::format("{} is duplicated", owner));
	}
}

[[nodiscard]] CatalogManifests loadManifests(const std::filesystem::path &dataDirectory) {
	const auto catalogDirectory = dataDirectory / "catalog";
	CatalogManifests manifests;
	manifests.profile = parseProfile(readJsonFile(catalogDirectory / "profile.json", true));
	manifests.releases = parseReleases(readJsonFile(catalogDirectory / "releases.json", true));
	manifests.items = parseItems(readJsonFile(catalogDirectory / "versioning/items.json", true));
	manifests.creatures = parseCreatures(readJsonFile(catalogDirectory / "versioning/creatures.json", true));
	manifests.itemAvailability = parseAvailability(
		readJsonFile(catalogDirectory / "availability/items.json", false),
		"items",
		{ "obtainable", "quest_only", "boss_only", "event_only", "npc_only", "starter", "registered_only", "admin_only", "unreachable", "unknown" },
		"availability/items.json"
	);
	manifests.creatureAvailability = parseAvailability(
		readJsonFile(catalogDirectory / "availability/creatures.json", false),
		"creatures",
		{ "encounterable", "boss_only", "event_only", "quest_only", "registered_only", "admin_only", "unreachable", "unknown" },
		"availability/creatures.json"
	);
	validateApprovedBackports(readJsonFile(catalogDirectory / "overrides/approved-backports.json", false));
	return manifests;
}

[[nodiscard]] std::unordered_map<std::string, std::uint64_t> releaseOrders(const std::vector<ReleaseManifest> &releases) {
	std::unordered_map<std::string, std::uint64_t> result;
	std::set<std::uint64_t> orders;
	for (const auto &release : releases) {
		require(result.emplace(release.key, release.releaseOrder).second, fmt::format("Duplicate release key '{}'", release.key));
		require(orders.emplace(release.releaseOrder).second, fmt::format("Duplicate release_order {}", release.releaseOrder));
	}
	return result;
}

void validateReleaseReference(
	const std::optional<std::string> &key,
	const std::unordered_map<std::string, std::uint64_t> &orders,
	const std::string_view owner
) {
	if (key.has_value()) {
		require(orders.contains(*key), fmt::format("{} references unknown release '{}'", owner, *key));
	}
}

void validateVersionRange(
	const std::optional<std::string> &introduced,
	const std::optional<std::string> &removed,
	const std::unordered_map<std::string, std::uint64_t> &orders,
	const std::string_view owner
) {
	validateReleaseReference(introduced, orders, owner);
	validateReleaseReference(removed, orders, owner);
	if (introduced.has_value() && removed.has_value()) {
		require(orders.at(*introduced) < orders.at(*removed), fmt::format("{} has invalid version range; removed_in is exclusive", owner));
	}
}

void validateManifests(const CatalogManifests &manifests) {
	const auto orders = releaseOrders(manifests.releases);
	for (const auto &key : {
	         manifests.profile.runtimeRelease,
	         manifests.profile.contentTargetRelease,
	         manifests.profile.verifiedContentThroughRelease,
	     }) {
		require(orders.contains(key), fmt::format("profile.json references unknown release '{}'", key));
	}
	validateReleaseReference(manifests.profile.containsContentThroughRelease, orders, "profile.json.contains_content_through_release");

	std::set<std::string> canonicalKeys;
	std::set<std::uint16_t> itemIds;
	for (const auto &item : manifests.items) {
		require(canonicalKeys.emplace(item.metadata.canonicalKey).second, fmt::format("Duplicate canonical key '{}'", item.metadata.canonicalKey));
		require(itemIds.emplace(item.serverId).second, fmt::format("Multiple item identities target server_id {}", item.serverId));
		validateVersionRange(item.metadata.introducedIn, item.metadata.removedIn, orders, item.metadata.canonicalKey);
	}
	std::set<std::string> registryNames;
	for (const auto &creature : manifests.creatures) {
		require(canonicalKeys.emplace(creature.metadata.canonicalKey).second, fmt::format("Duplicate canonical key '{}'", creature.metadata.canonicalKey));
		require(registryNames.emplace(toLowerAscii(creature.registryName)).second, fmt::format("Multiple creature identities target registry name '{}'", creature.registryName));
		validateVersionRange(creature.metadata.introducedIn, creature.metadata.removedIn, orders, creature.metadata.canonicalKey);
		std::set<std::pair<std::string, std::size_t>> lootKeys;
		for (const auto &loot : creature.loot) {
			require(lootKeys.emplace(loot.target, loot.occurrence).second, fmt::format("{} duplicates loot target '{}' occurrence {}", creature.metadata.canonicalKey, loot.target, loot.occurrence));
			validateVersionRange(loot.introducedIn, loot.removedIn, orders, fmt::format("{} loot {}", creature.metadata.canonicalKey, loot.target));
		}
	}
	for (const auto &[key, availability] : manifests.itemAvailability) {
		static_cast<void>(availability);
		require(canonicalKeys.contains(key), fmt::format("Item availability references unknown canonical key '{}'", key));
	}
	for (const auto &[key, availability] : manifests.creatureAvailability) {
		static_cast<void>(availability);
		require(canonicalKeys.contains(key), fmt::format("Creature availability references unknown canonical key '{}'", key));
	}
}

[[nodiscard]] Json nullable(const std::optional<std::string> &value) {
	return value.has_value() ? Json(*value) : Json(nullptr);
}

[[nodiscard]] Json releaseJson(const ReleaseManifest &release) {
	Json result = Json::object();
	result["key"] = release.key;
	result["display_label"] = release.displayLabel;
	result["major"] = release.major;
	result["minor"] = release.minor;
	result["patch"] = release.patch;
	result["build"] = release.build.has_value() ? Json(*release.build) : Json(nullptr);
	result["release_order"] = release.releaseOrder;
	result["protocol_family"] = nullable(release.protocolFamily);
	result["released_at"] = nullable(release.releasedAt);
	return result;
}

[[nodiscard]] Json identifierJson(std::vector<std::pair<std::string, std::string>> identifiers) {
	std::sort(identifiers.begin(), identifiers.end());
	require(identifiers.size() <= 32, "Entity identifier count exceeds 32");
	Json result = Json::array();
	for (const auto &[nameSpace, value] : identifiers) {
		Json identifier = Json::object();
		identifier["namespace"] = nameSpace;
		identifier["value"] = value;
		result.push_back(std::move(identifier));
	}
	return result;
}

[[nodiscard]] std::string itemCategory(const ItemType &item) {
	if (item.weaponType == WEAPON_SHIELD || item.type == ITEM_TYPE_SHIELD) {
		return "shields";
	}
	if (item.weaponType == WEAPON_AMMO || item.type == ITEM_TYPE_AMMO) {
		return "ammunition";
	}
	if (item.weaponType != WEAPON_NONE) {
		return "weapons";
	}
	const auto type = enumLabel(item.type);
	if (!type.empty() && type != "none") {
		return type;
	}
	const auto group = enumLabel(item.group);
	require(!group.empty() && group != "none", fmt::format("Item {} has no proven runtime category", item.id));
	return group;
}

[[nodiscard]] std::optional<std::string> weaponType(const ItemType &item) {
	if (item.weaponType == WEAPON_NONE) {
		return std::nullopt;
	}
	const auto value = enumLabel(item.weaponType);
	require(!value.empty(), fmt::format("Item {} has unsupported weapon type", item.id));
	return value;
}

[[nodiscard]] std::optional<std::string> combatType(const CombatType_t value) {
	if (value == COMBAT_NONE) {
		return std::nullopt;
	}
	const auto name = enumLabel(value);
	return name.empty() ? std::optional<std::string>(fmt::format("combat_{}", static_cast<std::uint32_t>(value))) : std::optional<std::string>(name);
}

[[nodiscard]] Json itemEntityJson(const ItemManifest &manifest) {
	require(Item::items.hasItemType(manifest.serverId), fmt::format("{} references missing runtime item {}", manifest.metadata.canonicalKey, manifest.serverId));
	const auto &item = Item::items.getItemType(manifest.serverId);
	require(item.id == manifest.serverId && item.loaded, fmt::format("{} references unloaded runtime item {}", manifest.metadata.canonicalKey, manifest.serverId));
	require(!item.name.empty(), fmt::format("{} references an unnamed runtime item {}", manifest.metadata.canonicalKey, manifest.serverId));
	require(item.weight >= 0, fmt::format("{} runtime item has negative weight unsupported by schema v1", manifest.metadata.canonicalKey));

	auto identifiers = manifest.metadata.identifiers;
	identifiers.emplace_back("canary.server_id", std::to_string(item.id));
	if (item.wareId != 0) {
		identifiers.emplace_back("canary.ware_id", std::to_string(item.wareId));
	}

	Json data = Json::object();
	data["server_id"] = item.id;
	data["client_id"] = nullptr;
	data["ware_id"] = item.wareId == 0 ? Json(nullptr) : Json(item.wareId);
	data["name"] = boundedString(item.name, 200, "item.name");
	data["description"] = item.description.empty() ? Json(nullptr) : Json(boundedString(item.description, 2000, "item.description"));
	data["category"] = itemCategory(item);
	const auto runtimeWeaponType = weaponType(item);
	data["weapon_type"] = nullable(runtimeWeaponType);

	const bool weapon = item.weaponType != WEAPON_NONE && item.weaponType != WEAPON_AMMO;
	data["attack"] = (weapon || item.attack != 0) ? Json(item.attack) : Json(nullptr);
	data["defense"] = (weapon || item.isShield() || item.defense != 0) ? Json(item.defense) : Json(nullptr);
	data["extra_defense"] = item.extraDefense != 0 ? Json(item.extraDefense) : Json(nullptr);
	data["armor"] = (item.isArmor() || item.armor != 0) ? Json(item.armor) : Json(nullptr);
	data["range"] = (item.isRanged() || item.isWand() || item.isMissile() || item.isAmmo()) ? Json(item.shootRange) : Json(nullptr);
	data["weight"] = item.weight;
	data["minimum_level"] = item.minReqLevel == 0 ? Json(nullptr) : Json(item.minReqLevel);
	if (item.vocationString.empty()) {
		data["vocations"] = nullptr;
	} else {
		data["vocations"] = Json::array({ boundedString(item.vocationString, 80, "item.vocationString") });
	}
	data["slot_position"] = item.slotPosition;
	data["imbuement_slots"] = item.imbuementSlot;
	data["upgrade_classification"] = item.upgradeClassification;

	const auto element = item.abilities ? combatType(item.abilities->elementType) : std::nullopt;
	data["element_type"] = nullable(element);
	data["element_value"] = item.abilities && item.abilities->elementType != COMBAT_NONE ? Json(item.abilities->elementDamage) : Json(nullptr);
	data["stackable"] = item.stackable;
	data["pickupable"] = item.pickupable;
	data["image_key"] = nullable(manifest.imageKey);

	Json attributes = Json::object();
	if (!item.m_primaryType.empty()) {
		attributes["primary_type"] = boundedString(item.m_primaryType, 80, "item.primary_type");
	}
	if (item.minReqMagicLevel != 0) {
		attributes["minimum_magic_level"] = item.minReqMagicLevel;
	}
	if (item.isDualWielding) {
		attributes["dual_wielding"] = true;
	}
	if (item.proficiencyId != 0) {
		attributes["proficiency_id"] = item.proficiencyId;
	}
	data["attributes"] = std::move(attributes);

	Json entity = Json::object();
	entity["type"] = "item";
	entity["canonical_key"] = manifest.metadata.canonicalKey;
	entity["introduced_in"] = nullable(manifest.metadata.introducedIn);
	entity["removed_in"] = nullable(manifest.metadata.removedIn);
	entity["completeness"] = manifest.metadata.completeness;
	entity["availability"] = "unknown";
	entity["runtime_present"] = true;
	entity["enabled"] = manifest.metadata.enabled;
	entity["identifiers"] = identifierJson(std::move(identifiers));
	entity["source_path"] = nullable(manifest.metadata.sourcePath);
	entity["data"] = std::move(data);
	return entity;
}

[[nodiscard]] Json spellJson(const spellBlock_t &spell) {
	Json result = Json::object();
	result["chance"] = spell.chance;
	result["interval_ms"] = spell.speed;
	result["range"] = spell.range;
	result["minimum_value"] = spell.minCombatValue;
	result["maximum_value"] = spell.maxCombatValue;
	result["combat_spell"] = spell.combatSpell;
	result["melee"] = spell.isMelee;
	result["impact_sound"] = static_cast<std::uint32_t>(spell.soundImpactEffect);
	result["cast_sound"] = static_cast<std::uint32_t>(spell.soundCastEffect);
	return result;
}

[[nodiscard]] Json creatureEntityJson(const CreatureManifest &manifest) {
	const auto monster = g_monsters().getMonsterType(manifest.registryName, true);
	require(monster != nullptr, fmt::format("{} references missing MonsterType '{}'", manifest.metadata.canonicalKey, manifest.registryName));
	require(!monster->name.empty(), fmt::format("{} references unnamed MonsterType '{}'", manifest.metadata.canonicalKey, manifest.registryName));

	auto identifiers = manifest.metadata.identifiers;
	identifiers.emplace_back("canary.monster_registry", toLowerAscii(manifest.registryName));
	if (monster->info.raceid != 0) {
		identifiers.emplace_back("canary.race_id", std::to_string(monster->info.raceid));
	}

	Json elements = Json::array();
	for (const auto &[type, percent] : monster->info.elementMap) {
		Json entry = Json::object();
		entry["type"] = combatType(type).value_or(fmt::format("combat_{}", static_cast<std::uint32_t>(type)));
		entry["percent"] = percent;
		elements.push_back(std::move(entry));
	}

	Json immunities = Json::array();
	for (std::size_t index = 0; index < static_cast<std::size_t>(ConditionType_t::CONDITION_COUNT); ++index) {
		if (monster->info.m_conditionImmunities.test(index)) {
			const auto type = static_cast<ConditionType_t>(index);
			const auto name = enumLabel(type);
			immunities.push_back(Json {
				{ "kind", "condition" },
				{ "type", name.empty() ? fmt::format("condition_{}", index) : name },
			});
		}
	}
	for (std::size_t index = 0; index < static_cast<std::size_t>(CombatType_t::COMBAT_COUNT); ++index) {
		if (monster->info.m_damageImmunities.test(index)) {
			const auto type = static_cast<CombatType_t>(index);
			immunities.push_back(Json {
				{ "kind", "damage" },
				{ "type", combatType(type).value_or(fmt::format("combat_{}", index)) },
			});
		}
	}

	Json attacks = Json::array();
	for (const auto &spell : monster->info.attackSpells) {
		attacks.push_back(spellJson(spell));
	}
	Json defenses = Json::array();
	for (const auto &spell : monster->info.defenseSpells) {
		defenses.push_back(spellJson(spell));
	}

	Json attributes = Json::object();
	attributes["registry_name"] = boundedString(manifest.registryName, 200, "creature.registry_name");
	attributes["race"] = enumLabel(monster->info.race);
	attributes["hostile"] = monster->info.isHostile;
	attributes["attackable"] = monster->info.isAttackable;
	attributes["summonable"] = monster->info.isSummonable;
	attributes["convinceable"] = monster->info.isConvinceable;
	attributes["pushable"] = monster->info.pushable;
	attributes["target_distance"] = monster->info.targetDistance;

	Json data = Json::object();
	data["name"] = boundedString(monster->name, 200, "creature.name");
	data["description"] = nullptr;
	data["race_id"] = monster->info.raceid == 0 ? Json(nullptr) : Json(monster->info.raceid);
	data["look_type"] = monster->info.outfit.lookType == 0 ? Json(nullptr) : Json(monster->info.outfit.lookType);
	data["health"] = monster->info.health;
	data["max_health"] = monster->info.healthMax;
	data["experience"] = monster->info.experience;
	data["speed"] = monster->getBaseSpeed();
	data["armor"] = monster->info.armor;
	data["defense"] = monster->info.defense;
	data["mitigation"] = monster->info.mitigation;
	data["is_boss"] = monster->isBoss();
	data["is_reward_boss"] = monster->info.isRewardBoss;
	data["bestiary_class"] = monster->info.bestiaryClass.empty() ? Json(nullptr) : Json(boundedString(monster->info.bestiaryClass, 120, "creature.bestiary_class"));
	const auto bestiaryRace = enumLabel(monster->info.bestiaryRace);
	data["bestiary_race"] = bestiaryRace.empty() || bestiaryRace == "none" ? Json(nullptr) : Json(bestiaryRace);
	data["bestiary_occurrence"] = monster->info.bestiaryOccurrence == 0 ? Json(nullptr) : Json(monster->info.bestiaryOccurrence);
	data["bestiary_to_kill"] = monster->info.bestiaryToUnlock == 0 ? Json(nullptr) : Json(monster->info.bestiaryToUnlock);
	data["charm_points"] = monster->info.bestiaryCharmsPoints == 0 ? Json(nullptr) : Json(monster->info.bestiaryCharmsPoints);
	data["elements"] = std::move(elements);
	data["immunities"] = std::move(immunities);
	data["attacks"] = std::move(attacks);
	data["defenses"] = std::move(defenses);
	data["attributes"] = std::move(attributes);

	Json entity = Json::object();
	entity["type"] = "creature";
	entity["canonical_key"] = manifest.metadata.canonicalKey;
	entity["introduced_in"] = nullable(manifest.metadata.introducedIn);
	entity["removed_in"] = nullable(manifest.metadata.removedIn);
	entity["completeness"] = manifest.metadata.completeness;
	entity["availability"] = "registered_only";
	entity["runtime_present"] = true;
	entity["enabled"] = manifest.metadata.enabled;
	entity["identifiers"] = identifierJson(std::move(identifiers));
	entity["source_path"] = nullable(manifest.metadata.sourcePath);
	entity["data"] = std::move(data);
	return entity;
}

void flattenLoot(
	const std::vector<LootBlock> &blocks,
	const std::string &parentPath,
	std::unordered_map<std::uint16_t, std::size_t> &occurrences,
	std::vector<RuntimeLoot> &result
) {
	for (std::size_t index = 0; index < blocks.size(); ++index) {
		const auto &block = blocks[index];
		const auto currentPath = parentPath.empty()
			? std::to_string(index)
			: parentPath + "/children/" + std::to_string(index);
		if (block.id != 0) {
			const auto occurrence = occurrences[block.id]++;
			result.push_back(RuntimeLoot {
				.block = &block,
				.containerPath = parentPath.empty() ? std::nullopt : std::optional<std::string>(currentPath),
				.occurrence = occurrence,
			});
		}
		if (!block.childLoot.empty()) {
			flattenLoot(block.childLoot, currentPath, occurrences, result);
		}
	}
}

[[nodiscard]] std::string canonicalSuffix(const std::string &canonicalKey) {
	const auto separator = canonicalKey.find(':');
	require(separator != std::string::npos && separator + 1 < canonicalKey.size(), fmt::format("Invalid canonical key '{}'", canonicalKey));
	return canonicalKey.substr(separator + 1);
}

[[nodiscard]] Json lootConditionData(const LootBlock &block) {
	Json condition = Json::object();
	if (block.subType != -1) {
		condition["sub_type"] = block.subType;
	}
	if (block.actionId != -1) {
		condition["action_id"] = block.actionId;
	}
	if (!block.text.empty()) {
		condition["text"] = boundedString(block.text, 2000, "loot.text");
	}
	if (!block.name.empty()) {
		condition["name"] = boundedString(block.name, 200, "loot.name");
	}
	if (!block.article.empty()) {
		condition["article"] = boundedString(block.article, 80, "loot.article");
	}
	if (block.attack != -1) {
		condition["attack"] = block.attack;
	}
	if (block.defense != -1) {
		condition["defense"] = block.defense;
	}
	if (block.extraDefense != -1) {
		condition["extra_defense"] = block.extraDefense;
	}
	if (block.armor != -1) {
		condition["armor"] = block.armor;
	}
	if (block.shootRange != -1) {
		condition["shoot_range"] = block.shootRange;
	}
	if (block.hitChance != -1) {
		condition["hit_chance"] = block.hitChance;
	}
	if (block.unique) {
		condition["unique"] = true;
	}
	return condition.empty() ? Json(nullptr) : condition;
}

[[nodiscard]] std::vector<Json> lootRelations(
	const CreatureManifest &creature,
	const std::unordered_map<std::string, const ItemManifest*> &itemsByCanonical
) {
	const auto monster = g_monsters().getMonsterType(creature.registryName, true);
	require(monster != nullptr, fmt::format("Cannot collect loot for missing MonsterType '{}'", creature.registryName));

	std::unordered_map<std::uint16_t, std::size_t> occurrences;
	std::vector<RuntimeLoot> runtimeLoot;
	flattenLoot(monster->info.lootItems, "", occurrences, runtimeLoot);

	std::vector<Json> relations;
	for (const auto &metadata : creature.loot) {
		const auto targetIterator = itemsByCanonical.find(metadata.target);
		require(targetIterator != itemsByCanonical.end(), fmt::format("{} loot relation references unexported target '{}'", creature.metadata.canonicalKey, metadata.target));
		const auto targetId = targetIterator->second->serverId;

		const auto runtimeIterator = std::find_if(runtimeLoot.begin(), runtimeLoot.end(), [targetId, &metadata](const RuntimeLoot &candidate) {
			return candidate.block->id == targetId && candidate.occurrence == metadata.occurrence;
		});
		require(runtimeIterator != runtimeLoot.end(), fmt::format("{} loot target '{}' occurrence {} is absent from final MonsterType", creature.metadata.canonicalKey, metadata.target, metadata.occurrence));
		const auto &block = *runtimeIterator->block;
		require(block.chance <= MAX_LOOTCHANCE, fmt::format("{} loot chance exceeds runtime denominator", creature.metadata.canonicalKey));
		require(block.countmin <= block.countmax, fmt::format("{} loot count range is invalid", creature.metadata.canonicalKey));
		require(block.countmax <= std::numeric_limits<std::uint16_t>::max(), fmt::format("{} loot maximum count exceeds schema v1", creature.metadata.canonicalKey));

		const auto relationKey = fmt::format(
			"loot:{}:{}{}",
			canonicalSuffix(creature.metadata.canonicalKey),
			canonicalSuffix(metadata.target),
			metadata.occurrence == 0 ? "" : fmt::format(":{}", metadata.occurrence + 1)
		);
		require(relationKey.size() <= 240, fmt::format("Loot canonical key exceeds 240 bytes: {}", relationKey));

		Json data = Json::object();
		data["chance_numerator"] = block.chance;
		data["chance_denominator"] = MAX_LOOTCHANCE;
		data["minimum_count"] = block.countmin;
		data["maximum_count"] = block.countmax;
		data["container_path"] = nullable(runtimeIterator->containerPath);
		data["condition_data"] = lootConditionData(block);

		Json relation = Json::object();
		relation["type"] = "creature_loot";
		relation["canonical_key"] = relationKey;
		relation["source"] = creature.metadata.canonicalKey;
		relation["target"] = metadata.target;
		relation["introduced_in"] = nullable(metadata.introducedIn);
		relation["removed_in"] = nullable(metadata.removedIn);
		relation["completeness"] = metadata.completeness;
		relation["enabled"] = metadata.enabled;
		relation["source_path"] = nullable(metadata.sourcePath);
		relation["data"] = std::move(data);
		relations.push_back(std::move(relation));
	}
	return relations;
}

void applyAvailability(Json &entities, const CatalogManifests &manifests) {
	for (auto &entity : entities) {
		const auto key = entity.at("canonical_key").get<std::string>();
		if (entity.at("type") == "item") {
			if (const auto iterator = manifests.itemAvailability.find(key); iterator != manifests.itemAvailability.end()) {
				entity["availability"] = iterator->second;
			}
		} else if (const auto iterator = manifests.creatureAvailability.find(key); iterator != manifests.creatureAvailability.end()) {
			entity["availability"] = iterator->second;
		}
	}
}

[[nodiscard]] std::string currentGeneratedAt() {
	const auto now = std::chrono::system_clock::now();
	const auto time = std::chrono::system_clock::to_time_t(now);
	std::tm utc {};
#ifdef _WIN32
	gmtime_s(&utc, &time);
#else
	gmtime_r(&time, &utc);
#endif
	std::ostringstream output;
	output << std::put_time(&utc, "%Y-%m-%dT%H:%M:%SZ");
	return output.str();
}

void validateGeneratedAt(const std::string &value) {
	require(
		matches(value, "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\\.[0-9]+)?Z$"),
		"generated_at must be a UTC RFC3339 timestamp"
	);
}

void validateBundledSchema() {
	const auto schemaPath = std::filesystem::path("schemas/game-catalog/v1/game-catalog-snapshot.schema.json");
	require(std::filesystem::is_regular_file(schemaPath), fmt::format("Bundled Game Catalog schema is missing: {}", schemaPath.generic_string()));
	const auto actual = sha256File(schemaPath);
	require(actual == ExpectedSchemaSha256, fmt::format("Bundled Game Catalog schema SHA-256 mismatch: expected {}, got {}", ExpectedSchemaSha256, actual));
}

[[nodiscard]] Json buildSnapshot(const CatalogManifests &manifests, const GameCatalogExportOptions &options) {
	std::vector<Json> entities;
	entities.reserve(manifests.items.size() + manifests.creatures.size());

	std::unordered_map<std::string, const ItemManifest*> itemsByCanonical;
	for (const auto &item : manifests.items) {
		itemsByCanonical.emplace(item.metadata.canonicalKey, &item);
		entities.push_back(itemEntityJson(item));
	}
	for (const auto &creature : manifests.creatures) {
		entities.push_back(creatureEntityJson(creature));
	}
	std::sort(entities.begin(), entities.end(), [](const auto &left, const auto &right) {
		return std::tie(left.at("type"), left.at("canonical_key")) < std::tie(right.at("type"), right.at("canonical_key"));
	});

	std::vector<Json> relations;
	for (const auto &creature : manifests.creatures) {
		auto creatureRelations = lootRelations(creature, itemsByCanonical);
		relations.insert(relations.end(), std::make_move_iterator(creatureRelations.begin()), std::make_move_iterator(creatureRelations.end()));
	}
	std::sort(relations.begin(), relations.end(), [](const auto &left, const auto &right) {
		return std::tie(left.at("type"), left.at("canonical_key")) < std::tie(right.at("type"), right.at("canonical_key"));
	});

	Json entityArray = Json::array();
	for (auto &entity : entities) {
		entityArray.push_back(std::move(entity));
	}
	applyAvailability(entityArray, manifests);

	Json relationArray = Json::array();
	for (auto &relation : relations) {
		relationArray.push_back(std::move(relation));
	}

	Json releaseArray = Json::array();
	for (const auto &release : manifests.releases) {
		releaseArray.push_back(releaseJson(release));
	}

	const auto coreFolder = std::filesystem::path(g_configManager().getString(CORE_DIRECTORY));
	const auto appearancesPath = coreFolder / "items/appearances.dat";
	const auto appearancesHash = sha256File(appearancesPath);

	const auto generatedAt = options.generatedAt.value_or(currentGeneratedAt());
	validateGeneratedAt(generatedAt);

	Json provenance = Json::object();
	provenance["generated_at"] = generatedAt;
	provenance["canary_commit_sha"] = manifests.profile.canaryCommitSha;
	provenance["datapack_commit_sha"] = nullable(manifests.profile.datapackCommitSha);
	provenance["protocol_profile"] = manifests.profile.protocolProfile;
	provenance["runtime_release"] = manifests.profile.runtimeRelease;
	provenance["content_target_release"] = manifests.profile.contentTargetRelease;
	provenance["verified_content_through_release"] = manifests.profile.verifiedContentThroughRelease;
	provenance["contains_content_through_release"] = nullable(manifests.profile.containsContentThroughRelease);
	provenance["appearances_sha256"] = appearancesHash;
	provenance["map_sha256"] = nullable(manifests.profile.mapSha256);
	provenance["producer_build_id"] = nullable(manifests.profile.producerBuildId);
	provenance["entity_count"] = entityArray.size();
	provenance["relation_count"] = relationArray.size();

	Json result = Json::object();
	result["contract"] = ContractId;
	result["schema_version"] = SchemaVersion;
	result["snapshot"] = std::move(provenance);
	result["releases"] = std::move(releaseArray);
	result["entities"] = std::move(entityArray);
	result["relations"] = std::move(relationArray);
	return result;
}

[[nodiscard]] std::optional<std::uint64_t> optionalReleaseOrder(
	const Json &value,
	const std::string_view field,
	const std::unordered_map<std::string, std::uint64_t> &orders,
	const std::string_view owner
) {
	if (value.at(field).is_null()) {
		return std::nullopt;
	}
	const auto key = value.at(field).get<std::string>();
	require(orders.contains(key), fmt::format("{}.{} references unknown release '{}'", owner, field, key));
	return orders.at(key);
}

void validateSnapshot(const Json &snapshot) {
	requireObjectKeys(snapshot, { "contract", "schema_version", "snapshot", "releases", "entities", "relations" }, "snapshot");
	require(snapshot.at("contract") == ContractId, "Snapshot contract mismatch");
	require(snapshot.at("schema_version") == SchemaVersion, "Snapshot schema_version mismatch");
	require(snapshot.at("releases").is_array() && !snapshot.at("releases").empty() && snapshot.at("releases").size() <= 512, "Snapshot release count is out of bounds");
	require(snapshot.at("entities").is_array() && snapshot.at("entities").size() <= 200000, "Snapshot entity count is out of bounds");
	require(snapshot.at("relations").is_array() && snapshot.at("relations").size() <= 1000000, "Snapshot relation count is out of bounds");
	require(snapshot.at("snapshot").is_object(), "Snapshot provenance must be an object");
	require(snapshot.at("snapshot").at("entity_count") == snapshot.at("entities").size(), "Snapshot entity_count mismatch");
	require(snapshot.at("snapshot").at("relation_count") == snapshot.at("relations").size(), "Snapshot relation_count mismatch");
	validateSha(snapshot.at("snapshot").at("canary_commit_sha").get<std::string>(), 40, 64, "snapshot.canary_commit_sha");
	validateSha(snapshot.at("snapshot").at("appearances_sha256").get<std::string>(), 64, 64, "snapshot.appearances_sha256");

	std::unordered_map<std::string, std::uint64_t> orders;
	std::set<std::uint64_t> uniqueOrders;
	std::uint64_t previousOrder = 0;
	std::string previousKey;
	bool firstRelease = true;
	for (const auto &release : snapshot.at("releases")) {
		const auto key = release.at("key").get<std::string>();
		const auto order = release.at("release_order").get<std::uint64_t>();
		require(orders.emplace(key, order).second, fmt::format("Duplicate release key '{}'", key));
		require(uniqueOrders.emplace(order).second, fmt::format("Duplicate release_order {}", order));
		if (!firstRelease) {
			require(std::tie(previousOrder, previousKey) < std::tie(order, key), "Releases are not deterministically sorted");
		}
		firstRelease = false;
		previousOrder = order;
		previousKey = key;
	}
	for (const std::string_view field : { "runtime_release", "content_target_release", "verified_content_through_release" }) {
		require(orders.contains(snapshot.at("snapshot").at(field).get<std::string>()), fmt::format("Snapshot provenance references unknown {}", field));
	}
	if (!snapshot.at("snapshot").at("contains_content_through_release").is_null()) {
		require(orders.contains(snapshot.at("snapshot").at("contains_content_through_release").get<std::string>()), "Snapshot provenance references unknown contains_content_through_release");
	}

	std::set<std::string> entityKeys;
	std::pair<std::string, std::string> previousEntity;
	bool firstEntity = true;
	for (const auto &entity : snapshot.at("entities")) {
		const auto type = entity.at("type").get<std::string>();
		const auto key = entity.at("canonical_key").get<std::string>();
		validateCanonicalKey(key, key);
		require(entityKeys.emplace(key).second, fmt::format("Duplicate entity canonical key '{}'", key));
		const auto current = std::pair(type, key);
		if (!firstEntity) {
			require(previousEntity < current, "Entities are not deterministically sorted");
		}
		firstEntity = false;
		previousEntity = current;
		const auto introduced = optionalReleaseOrder(entity, "introduced_in", orders, key);
		const auto removed = optionalReleaseOrder(entity, "removed_in", orders, key);
		if (introduced.has_value() && removed.has_value()) {
			require(*introduced < *removed, fmt::format("{} has invalid exclusive version range", key));
		}
		const auto sourcePath = entity.at("source_path").is_null()
			? std::optional<std::string>()
			: std::optional<std::string>(entity.at("source_path").get<std::string>());
		validateSourcePath(sourcePath, key);
		require(entity.at("identifiers").is_array() && entity.at("identifiers").size() <= 32, fmt::format("{} identifier count is out of bounds", key));
	}

	std::set<std::string> relationKeys;
	std::pair<std::string, std::string> previousRelation;
	bool firstRelation = true;
	for (const auto &relation : snapshot.at("relations")) {
		const auto type = relation.at("type").get<std::string>();
		const auto key = relation.at("canonical_key").get<std::string>();
		require(key.size() <= 240 && matches(key, "^loot:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*(?::[0-9]+)?$"), fmt::format("Invalid loot canonical key '{}'", key));
		require(relationKeys.emplace(key).second, fmt::format("Duplicate relation canonical key '{}'", key));
		const auto current = std::pair(type, key);
		if (!firstRelation) {
			require(previousRelation < current, "Relations are not deterministically sorted");
		}
		firstRelation = false;
		previousRelation = current;
		const auto source = relation.at("source").get<std::string>();
		const auto target = relation.at("target").get<std::string>();
		require(entityKeys.contains(source), fmt::format("{} has dangling source '{}'", key, source));
		require(entityKeys.contains(target), fmt::format("{} has dangling target '{}'", key, target));
		const auto introduced = optionalReleaseOrder(relation, "introduced_in", orders, key);
		const auto removed = optionalReleaseOrder(relation, "removed_in", orders, key);
		if (introduced.has_value() && removed.has_value()) {
			require(*introduced < *removed, fmt::format("{} has invalid exclusive version range", key));
		}
		const auto &data = relation.at("data");
		const auto numerator = data.at("chance_numerator").get<std::uint64_t>();
		const auto denominator = data.at("chance_denominator").get<std::uint64_t>();
		require(denominator > 0 && numerator <= denominator, fmt::format("{} has invalid loot probability", key));
		require(data.at("minimum_count").get<std::uint64_t>() <= data.at("maximum_count").get<std::uint64_t>(), fmt::format("{} has invalid loot count range", key));
	}
}

[[nodiscard]] std::string temporaryToken() {
	const auto ticks = std::chrono::steady_clock::now().time_since_epoch().count();
	return fmt::format("{}-{}", static_cast<unsigned long long>(ticks), reinterpret_cast<std::uintptr_t>(&ticks));
}

void writeFile(const std::filesystem::path &path, const std::string &content) {
	std::ofstream output(path, std::ios::binary | std::ios::trunc);
	require(output.is_open(), fmt::format("Cannot open temporary output: {}", path.generic_string()));
	output.write(content.data(), static_cast<std::streamsize>(content.size()));
	require(output.good(), fmt::format("Cannot write temporary output: {}", path.generic_string()));
	output.flush();
	require(output.good(), fmt::format("Cannot flush temporary output: {}", path.generic_string()));
	output.close();
	require(!output.fail(), fmt::format("Cannot close temporary output: {}", path.generic_string()));
}

void publishAtomically(const std::filesystem::path &outputPath, const std::string &content) {
	require(!outputPath.empty() && outputPath.has_filename(), "Game Catalog output path must name a file");
	std::error_code error;
	require(!std::filesystem::is_directory(outputPath, error), "Game Catalog output path must not be a directory");
	require(!error, fmt::format("Cannot inspect Game Catalog output path: {}", error.message()));

	auto parent = outputPath.parent_path();
	if (parent.empty()) {
		parent = ".";
	}
	require(std::filesystem::is_directory(parent, error), fmt::format("Game Catalog output directory does not exist: {}", parent.generic_string()));
	require(!error, fmt::format("Cannot inspect Game Catalog output directory: {}", error.message()));

	const auto token = temporaryToken();
	const auto sidecarPath = std::filesystem::path(outputPath.string() + ".sha256");
	const auto temporaryOutput = parent / fmt::format(".{}.tmp.{}", outputPath.filename().string(), token);
	const auto temporarySidecar = parent / fmt::format(".{}.sha256.tmp.{}", outputPath.filename().string(), token);
	const auto backupOutput = parent / fmt::format(".{}.bak.{}", outputPath.filename().string(), token);
	const auto backupSidecar = parent / fmt::format(".{}.sha256.bak.{}", outputPath.filename().string(), token);
	const auto digest = sha256String(content);

	bool outputBackedUp = false;
	bool sidecarBackedUp = false;
	try {
		writeFile(temporaryOutput, content);
		writeFile(temporarySidecar, digest + "\n");
		require(sha256File(temporaryOutput) == digest, "Temporary Game Catalog output hash verification failed");

		if (std::filesystem::exists(outputPath)) {
			std::filesystem::rename(outputPath, backupOutput);
			outputBackedUp = true;
		}
		if (std::filesystem::exists(sidecarPath)) {
			std::filesystem::rename(sidecarPath, backupSidecar);
			sidecarBackedUp = true;
		}

		std::filesystem::rename(temporarySidecar, sidecarPath);
		std::filesystem::rename(temporaryOutput, outputPath);

		if (outputBackedUp) {
			std::filesystem::remove(backupOutput);
		}
		if (sidecarBackedUp) {
			std::filesystem::remove(backupSidecar);
		}
	} catch (...) {
		std::filesystem::remove(temporaryOutput, error);
		std::filesystem::remove(temporarySidecar, error);
		std::filesystem::remove(outputPath, error);
		std::filesystem::remove(sidecarPath, error);
		if (outputBackedUp) {
			std::filesystem::rename(backupOutput, outputPath, error);
		}
		if (sidecarBackedUp) {
			std::filesystem::rename(backupSidecar, sidecarPath, error);
		}
		throw;
	}
}

void loadExportConfig() {
	const std::filesystem::path configPath("config.lua");
	require(std::filesystem::is_regular_file(configPath), "Export-only mode requires an existing config.lua and will not create one");
	g_configManager().setConfigFileLua(configPath.string());
	require(g_configManager().load(), "Cannot load config.lua");
	const auto useAnyDatapack = g_configManager().getBoolean(USE_ANY_DATAPACK_FOLDER);
	const auto datapackName = g_configManager().getString(DATA_DIRECTORY);
	require(
		useAnyDatapack || datapackName == "data-canary" || datapackName == "data-otservbr-global",
		fmt::format("The datapack folder name '{}' is not allowed by config.lua", datapackName)
	);
}

}

GameCatalogExportArgumentResult parseGameCatalogExportArguments(const std::span<char*> arguments) {
	GameCatalogExportArgumentResult result;
	for (std::size_t index = 1; index < arguments.size(); ++index) {
		const std::string_view argument(arguments[index]);
		if (argument == ExportOnlyArgument) {
			result.requested = true;
			continue;
		}
		if (startsWith(argument, OutputArgumentPrefix)) {
			if (result.options.has_value() && !result.options->outputPath.empty()) {
				result.error = "Duplicate --game-catalog-output argument";
				return result;
			}
			if (!result.options.has_value()) {
				result.options.emplace();
			}
			result.options->outputPath = std::string(argument.substr(OutputArgumentPrefix.size()));
			continue;
		}
		if (startsWith(argument, GeneratedAtArgumentPrefix)) {
			if (!result.options.has_value()) {
				result.options.emplace();
			}
			if (result.options->generatedAt.has_value()) {
				result.error = "Duplicate --game-catalog-generated-at argument";
				return result;
			}
			result.options->generatedAt = std::string(argument.substr(GeneratedAtArgumentPrefix.size()));
		}
	}

	if (!result.requested) {
		result.options.reset();
		return result;
	}
	if (!result.options.has_value() || result.options->outputPath.empty()) {
		result.error = "--game-catalog-output=<path> is required in export-only mode";
		result.options.reset();
		return result;
	}
	if (result.options->generatedAt.has_value() && result.options->generatedAt->empty()) {
		result.error = "--game-catalog-generated-at must not be empty";
		result.options.reset();
	}
	return result;
}

GameCatalogExporter::GameCatalogExporter(Logger &logger) :
	logger(logger) { }

int GameCatalogExporter::run(const GameCatalogExportOptions &options) const {
	try {
		validateBundledSchema();
		loadExportConfig();
		loadAuthoritativeCatalogDefinitions(logger);

		const auto dataDirectory = std::filesystem::path(g_configManager().getString(DATA_DIRECTORY));
		const auto manifests = loadManifests(dataDirectory);
		validateManifests(manifests);

		auto snapshot = buildSnapshot(manifests, options);
		validateSnapshot(snapshot);
		auto serialized = snapshot.dump(2);
		serialized.push_back('\n');
		require(serialized.size() <= MaximumSnapshotBytes, fmt::format("Serialized Game Catalog exceeds {} bytes", MaximumSnapshotBytes));
		publishAtomically(options.outputPath, serialized);

		logger.info(
			"[game-catalog] Exported {} entities and {} relations to {}",
			snapshot.at("snapshot").at("entity_count").get<std::size_t>(),
			snapshot.at("snapshot").at("relation_count").get<std::size_t>(),
			options.outputPath.generic_string()
		);
		return EXIT_SUCCESS;
	} catch (const std::exception &error) {
		logger.error("[game-catalog] Export failed: {}", error.what());
		return EXIT_FAILURE;
	}
}

}
