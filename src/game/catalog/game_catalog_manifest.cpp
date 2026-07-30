#include "game/catalog/game_catalog_manifest.hpp"

#include <nlohmann/json.hpp>

#ifndef USE_PRECOMPILED_HEADERS
	#include <fstream>
	#include <stdexcept>
#endif

namespace game_catalog {
	namespace {
		using Json = nlohmann::ordered_json;
		constexpr std::uintmax_t MaximumManifestBytes = 16 * 1024 * 1024;

		[[nodiscard]] Json readJsonFile(const std::filesystem::path &path, const bool required) {
			std::error_code error;
			if (!std::filesystem::exists(path, error)) {
				if (required) {
					throw std::runtime_error("Required Game Catalog manifest file is missing: " + path.generic_string());
				}
				return Json::object();
			}
			if (error || !std::filesystem::is_regular_file(path, error) || std::filesystem::is_symlink(path, error)) {
				throw std::runtime_error("Game Catalog manifest path must be a regular non-symlink file: " + path.generic_string());
			}
			const auto size = std::filesystem::file_size(path, error);
			if (error || size == 0 || size > MaximumManifestBytes) {
				throw std::runtime_error("Game Catalog manifest file size is invalid: " + path.generic_string());
			}

			std::ifstream input(path, std::ios::binary);
			if (!input) {
				throw std::runtime_error("Cannot read Game Catalog manifest file: " + path.generic_string());
			}
			Json value;
			try {
				input >> value;
			} catch (const nlohmann::json::exception &exception) {
				throw std::runtime_error("Invalid Game Catalog manifest JSON in " + path.generic_string() + ": " + exception.what());
			}
			return value;
		}

		[[nodiscard]] std::string requiredString(const Json &value, const std::string_view key, const std::filesystem::path &path) {
			const auto iterator = value.find(std::string(key));
			if (iterator == value.end() || !iterator->is_string() || iterator->get_ref<const std::string &>().empty()) {
				throw std::runtime_error("Game Catalog manifest field [" + std::string(key) + "] must be a non-empty string in " + path.generic_string());
			}
			return iterator->get<std::string>();
		}

		[[nodiscard]] std::uint32_t requiredPositiveUint32(const Json &value, const std::string_view key, const std::filesystem::path &path) {
			const auto iterator = value.find(std::string(key));
			if (iterator == value.end() || !iterator->is_number_unsigned()) {
				throw std::runtime_error("Game Catalog manifest field [" + std::string(key) + "] must be a positive unsigned integer in " + path.generic_string());
			}
			const auto number = iterator->get<std::uint64_t>();
			if (number == 0 || number > std::numeric_limits<std::uint32_t>::max()) {
				throw std::runtime_error("Game Catalog manifest field [" + std::string(key) + "] is outside uint32 bounds in " + path.generic_string());
			}
			return static_cast<std::uint32_t>(number);
		}

		[[nodiscard]] std::optional<std::string> nullableString(const Json &value, const std::string_view key, const std::filesystem::path &path) {
			const auto iterator = value.find(std::string(key));
			if (iterator == value.end() || iterator->is_null()) {
				return std::nullopt;
			}
			if (!iterator->is_string() || iterator->get_ref<const std::string &>().empty()) {
				throw std::runtime_error("Game Catalog manifest field [" + std::string(key) + "] must be null or a non-empty string in " + path.generic_string());
			}
			return iterator->get<std::string>();
		}

		void mergeVersioning(std::unordered_map<std::string, RecordMetadata> &records, const Json &document, const std::filesystem::path &path) {
			if (!document.is_object()) {
				throw std::runtime_error("Game Catalog versioning manifest must be an object: " + path.generic_string());
			}
			for (const auto &[sourceKey, value] : document.items()) {
				if (!value.is_object() || sourceKey.empty()) {
					throw std::runtime_error("Game Catalog versioning entries must be keyed objects: " + path.generic_string());
				}
				auto &metadata = records[sourceKey];
				metadata.canonicalKey = nullableString(value, "canonical_key", path);
				metadata.introducedIn = nullableString(value, "introduced_in", path);
				metadata.removedIn = nullableString(value, "removed_in", path);
				if (const auto completeness = value.find("completeness"); completeness != value.end()) {
					if (!completeness->is_string() || completeness->get_ref<const std::string &>().empty()) {
						throw std::runtime_error("Game Catalog completeness must be a non-empty string: " + path.generic_string());
					}
					metadata.completeness = completeness->get<std::string>();
				}
				metadata.sourcePath = nullableString(value, "source_path", path);
				metadata.imageKey = nullableString(value, "image_key", path);
			}
		}

		void mergeAvailability(std::unordered_map<std::string, RecordMetadata> &records, const Json &document, const std::filesystem::path &path) {
			if (!document.is_object()) {
				throw std::runtime_error("Game Catalog availability manifest must be an object: " + path.generic_string());
			}
			for (const auto &[sourceKey, value] : document.items()) {
				if (!value.is_object() || sourceKey.empty()) {
					throw std::runtime_error("Game Catalog availability entries must be keyed objects: " + path.generic_string());
				}
				auto &metadata = records[sourceKey];
				const auto availability = value.find("availability");
				if (availability != value.end()) {
					if (!availability->is_string() || availability->get_ref<const std::string &>().empty()) {
						throw std::runtime_error("Game Catalog availability must be a non-empty string: " + path.generic_string());
					}
					metadata.availability = availability->get<std::string>();
				}
				const auto enabled = value.find("enabled");
				if (enabled != value.end()) {
					if (!enabled->is_boolean()) {
						throw std::runtime_error("Game Catalog enabled flag must be boolean: " + path.generic_string());
					}
					metadata.enabled = enabled->get<bool>();
				}
			}
		}

		void loadRecordFamily(
			std::unordered_map<std::string, RecordMetadata> &records,
			const std::filesystem::path &directory,
			const std::string_view family
		) {
			const auto versioningPath = directory / "versioning" / (std::string(family) + ".json");
			const auto availabilityPath = directory / "availability" / (std::string(family) + ".json");
			mergeVersioning(records, readJsonFile(versioningPath, false), versioningPath);
			mergeAvailability(records, readJsonFile(availabilityPath, false), availabilityPath);
		}
	}

	CatalogManifest loadCatalogManifest(const std::filesystem::path &directory) {
		if (directory.empty()) {
			throw std::runtime_error("Game Catalog manifest directory must not be empty.");
		}
		std::error_code error;
		if (!std::filesystem::is_directory(directory, error) || error) {
			throw std::runtime_error("Game Catalog manifest directory does not exist: " + directory.generic_string());
		}

		const auto profilePath = directory / "profile.json";
		const auto releasesPath = directory / "releases.json";
		const auto profile = readJsonFile(profilePath, true);
		const auto releases = readJsonFile(releasesPath, true);
		if (!profile.is_object()) {
			throw std::runtime_error("Game Catalog profile manifest must be an object: " + profilePath.generic_string());
		}
		if (!releases.is_array() || releases.empty()) {
			throw std::runtime_error("Game Catalog releases manifest must be a non-empty array: " + releasesPath.generic_string());
		}
		if (requiredString(profile, "contract", profilePath) != "oteryn.game-catalog") {
			throw std::runtime_error("Unsupported Game Catalog contract in profile manifest.");
		}
		const auto schemaVersion = requiredString(profile, "schema_version", profilePath);
		if (schemaVersion != "1.0.0" && schemaVersion != "1.1.0" && schemaVersion != "1.2.0" && schemaVersion != "1.3.0") {
			throw std::runtime_error("Unsupported Game Catalog schema version in profile manifest.");
		}

		CatalogManifest manifest;
		manifest.schemaVersion = schemaVersion;
		manifest.protocolProfile = requiredString(profile, "protocol_profile", profilePath);
		manifest.runtimeRelease = requiredString(profile, "runtime_release", profilePath);
		manifest.contentTargetRelease = requiredString(profile, "content_target_release", profilePath);
		manifest.verifiedContentThroughRelease = schemaVersion == "1.0.0"
			? std::optional<std::string>(requiredString(profile, "verified_content_through_release", profilePath))
			: nullableString(profile, "verified_content_through_release", profilePath);
		if (schemaVersion == "1.2.0" || schemaVersion == "1.3.0") {
			manifest.lootRollMaximum = requiredPositiveUint32(profile, "loot_roll_maximum", profilePath);
		} else {
			manifest.lootChanceDenominator = requiredPositiveUint32(profile, "loot_chance_denominator", profilePath);
		}
		manifest.containsContentThroughRelease = nullableString(profile, "contains_content_through_release", profilePath);
		manifest.datapackCommitSha = nullableString(profile, "datapack_commit_sha", profilePath);
		manifest.producerBuildId = nullableString(profile, "producer_build_id", profilePath);
		manifest.releases = releases;

		loadRecordFamily(manifest.items, directory, "items");
		loadRecordFamily(manifest.creatures, directory, "creatures");
		loadRecordFamily(manifest.loot, directory, "loot");
		return manifest;
	}

} // namespace game_catalog
