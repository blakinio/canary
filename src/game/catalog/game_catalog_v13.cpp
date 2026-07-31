#include "game/catalog/game_catalog_v13.hpp"

#include "creatures/npcs/npcs.hpp"
#include "utils/tools.hpp"

#include <nlohmann/json.hpp>

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <chrono>
	#include <fstream>
	#include <regex>
	#include <set>
	#include <sstream>
	#include <stdexcept>
	#include <unordered_set>
#endif

namespace game_catalog {
	namespace {
		using Json = nlohmann::ordered_json;
		const std::regex CanonicalKeyPattern(R"(^[a-z][a-z0-9_-]*:[a-z0-9][a-z0-9._-]*$)");

		[[nodiscard]] std::string normalizeRegistryKey(const std::string &registryKey) {
			std::string value;
			value.reserve(registryKey.size());
			bool separator = false;
			for (const unsigned char character : registryKey) {
				const auto lowered = static_cast<char>(std::tolower(character));
				if (std::isalnum(character) || lowered == '.' || lowered == '_' || lowered == '-') {
					value.push_back(lowered);
					separator = false;
				} else if (!value.empty() && !separator) {
					value.push_back('-');
					separator = true;
				}
			}
			while (!value.empty() && value.back() == '-') {
				value.pop_back();
			}
			if (value.empty()) {
				value = "registry-" + transformToSHA256(registryKey).substr(0, 24);
			}
			return value;
		}

		[[nodiscard]] std::string normalizeNpcSourcePath(const std::string &source) {
			std::string normalized = source;
			std::ranges::replace(normalized, '\\', '/');
			const std::string marker = "/npc/";
			const auto markerPosition = normalized.rfind(marker);
			if (markerPosition != std::string::npos) {
				normalized = "npc/" + normalized.substr(markerPosition + marker.size());
			} else if (!normalized.starts_with("npc/")) {
				throw std::runtime_error("NPC registration source is outside the runtime npc directory: " + source);
			}

			const std::filesystem::path path(normalized);
			if (path.empty() || path.is_absolute() || std::ranges::any_of(path, [](const auto &part) { return part == ".."; })) {
				throw std::runtime_error("NPC registration source is not a safe relative path: " + source);
			}
			return path.generic_string();
		}

		[[nodiscard]] std::string itemCanonicalKey(const CatalogManifest &manifest, const std::uint16_t itemId) {
			const auto sourceKey = std::to_string(itemId);
			const auto metadata = manifest.items.find(sourceKey);
			if (metadata != manifest.items.end() && metadata->second.canonicalKey) {
				return *metadata->second.canonicalKey;
			}
			return "item:server-" + sourceKey;
		}

		[[nodiscard]] Json currencyRecord(const CatalogManifest &manifest, const std::uint16_t currencyId) {
			return Json {
				{ "item", itemCanonicalKey(manifest, currencyId) },
				{ "server_id", currencyId },
			};
		}

		[[nodiscard]] std::string runtimePathKey(const std::vector<std::size_t> &runtimePath) {
			std::ostringstream output;
			for (std::size_t index = 0; index < runtimePath.size(); ++index) {
				if (index != 0) {
					output << '.';
				}
				output << runtimePath[index];
			}
			return output.str();
		}

		[[nodiscard]] Json storageRequirement(const ShopBlock &shop) {
			if (shop.itemStorageKey == 0) {
				return nullptr;
			}
			return Json {
				{ "key", shop.itemStorageKey },
				{ "value", shop.itemStorageValue },
			};
		}

		void appendOffer(
			Json &relations,
			const CatalogManifest &manifest,
			const std::string &npcCanonicalKey,
			const std::string &sourcePath,
			const std::uint16_t currencyId,
			const ShopBlock &shop,
			const std::vector<std::size_t> &runtimePath,
			const std::string &direction,
			const std::uint32_t price
		) {
			if (price == 0) {
				return;
			}
			if (shop.itemId == 0) {
				throw std::runtime_error("NPC shop offer has an empty runtime item id.");
			}

			const auto target = itemCanonicalKey(manifest, shop.itemId);
			const auto conditional = shop.itemStorageKey != 0;
			relations.push_back(Json {
				{ "type", direction == "buy" ? "npc_buy_offer" : "npc_sell_offer" },
				{ "canonical_key", "shop:" + npcCanonicalKey + ":" + direction + ":" + target + ":" + runtimePathKey(runtimePath) },
				{ "source", npcCanonicalKey },
				{ "target", target },
				{ "introduced_in", nullptr },
				{ "removed_in", nullptr },
				{ "completeness", "unverified" },
				{ "availability", conditional ? "conditional" : "registered_only" },
				{ "enabled", true },
				{ "source_path", sourcePath },
				{ "data", Json {
							  { "runtime_path", runtimePath },
							  { "item_name", shop.itemName },
							  { "item_subtype", shop.itemSubType },
							  { "priced_item_count", 1 },
							  { "price_amount", price },
							  { "currency", currencyRecord(manifest, currencyId) },
							  { "storage_requirement", storageRequirement(shop) },
							  { "attributes", Json::object() },
						  } },
			});
		}

		void appendOffers(
			Json &relations,
			const CatalogManifest &manifest,
			const std::string &npcCanonicalKey,
			const std::string &sourcePath,
			const std::uint16_t currencyId,
			const std::vector<ShopBlock> &shops,
			std::vector<std::size_t> &runtimePath
		) {
			for (std::size_t index = 0; index < shops.size(); ++index) {
				runtimePath.push_back(index);
				const auto &shop = shops[index];
				appendOffer(relations, manifest, npcCanonicalKey, sourcePath, currencyId, shop, runtimePath, "buy", shop.itemBuyPrice);
				appendOffer(relations, manifest, npcCanonicalKey, sourcePath, currencyId, shop, runtimePath, "sell", shop.itemSellPrice);
				appendOffers(relations, manifest, npcCanonicalKey, sourcePath, currencyId, shop.childShop, runtimePath);
				runtimePath.pop_back();
			}
		}

		[[nodiscard]] bool safeRelativePath(const Json &value) {
			if (!value.is_string()) {
				return false;
			}
			const std::filesystem::path path(value.get<std::string>());
			return !path.empty() && !path.is_absolute() && std::ranges::none_of(path, [](const auto &part) { return part == ".."; });
		}

		[[nodiscard]] std::vector<std::string> validateV13SnapshotDocument(const Json &document) {
			std::vector<std::string> errors;
			if (!document.is_object() || document.value("contract", "") != "oteryn.game-catalog" || document.value("schema_version", "") != "1.3.0") {
				errors.emplace_back("Unsupported Game Catalog 1.3 contract.");
				return errors;
			}
			if (!document.contains("snapshot") || !document.at("snapshot").is_object()
			    || !document.contains("entities") || !document.at("entities").is_array()
			    || !document.contains("relations") || !document.at("relations").is_array()) {
				errors.emplace_back("Game Catalog 1.3 document is missing required collections.");
				return errors;
			}

			Json baseline = document;
			baseline["schema_version"] = "1.2.0";
			Json baselineEntities = Json::array();
			for (const auto &entity : document.at("entities")) {
				if (entity.value("type", "") != "npc") {
					baselineEntities.push_back(entity);
				}
			}
			Json baselineRelations = Json::array();
			for (const auto &relation : document.at("relations")) {
				const auto type = relation.value("type", "");
				if (type != "npc_buy_offer" && type != "npc_sell_offer") {
					baselineRelations.push_back(relation);
				}
			}
			baseline["entities"] = std::move(baselineEntities);
			baseline["relations"] = std::move(baselineRelations);
			baseline["snapshot"]["entity_count"] = baseline.at("entities").size();
			baseline["snapshot"]["relation_count"] = baseline.at("relations").size();
			const auto baselineErrors = validateSnapshotDocument(baseline);
			errors.insert(errors.end(), baselineErrors.begin(), baselineErrors.end());

			const auto &snapshot = document.at("snapshot");
			if (snapshot.value("entity_count", std::size_t {}) != document.at("entities").size()
			    || snapshot.value("relation_count", std::size_t {}) != document.at("relations").size()) {
				errors.emplace_back("Game Catalog 1.3 snapshot counts do not match collections.");
			}

			std::unordered_set<std::string> entityKeys;
			for (const auto &entity : document.at("entities")) {
				const auto key = entity.value("canonical_key", "");
				if (!entityKeys.emplace(key).second) {
					errors.emplace_back("Duplicate entity canonical key: " + key);
				}
				if (entity.value("type", "") != "npc") {
					continue;
				}
				if (!std::regex_match(key, CanonicalKeyPattern) || !key.starts_with("npc:")) {
					errors.emplace_back("Invalid NPC canonical key: " + key);
				}
				if (!safeRelativePath(entity.value("source_path", Json(nullptr)))) {
					errors.emplace_back("NPC source_path must be a safe relative path: " + key);
				}
				if (!entity.contains("data") || !entity.at("data").is_object()
				    || entity.at("data").value("registration_status", "") != "runtime_registered") {
					errors.emplace_back("NPC entity is missing runtime registration data: " + key);
				}
			}

			std::unordered_set<std::string> relationKeys;
			for (const auto &relation : document.at("relations")) {
				const auto key = relation.value("canonical_key", "");
				if (!relationKeys.emplace(key).second) {
					errors.emplace_back("Duplicate relation canonical key: " + key);
				}
				const auto type = relation.value("type", "");
				if (type != "npc_buy_offer" && type != "npc_sell_offer") {
					continue;
				}
				if (!entityKeys.contains(relation.value("source", "")) || !entityKeys.contains(relation.value("target", ""))) {
					errors.emplace_back("NPC offer references an unknown endpoint: " + key);
				}
				if (!safeRelativePath(relation.value("source_path", Json(nullptr)))) {
					errors.emplace_back("NPC offer source_path must be a safe relative path: " + key);
				}
				if (!relation.contains("data") || !relation.at("data").is_object()
				    || !relation.at("data").contains("runtime_path") || !relation.at("data").at("runtime_path").is_array()
				    || relation.at("data").value("price_amount", std::uint32_t {}) == 0) {
					errors.emplace_back("NPC offer is missing runtime pricing data: " + key);
				}
			}
			return errors;
		}

		void writeRestrictedFile(const std::filesystem::path &path, const std::string &contents) {
			std::ofstream output(path, std::ios::binary | std::ios::trunc);
			if (!output) {
				throw std::runtime_error("Cannot create Game Catalog output file: " + path.generic_string());
			}
			output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
			output.close();
			if (!output) {
				throw std::runtime_error("Cannot write Game Catalog output file: " + path.generic_string());
			}
			std::error_code error;
			std::filesystem::permissions(path, std::filesystem::perms::owner_read | std::filesystem::perms::owner_write, std::filesystem::perm_options::replace, error);
			if (error) {
				throw std::runtime_error("Cannot restrict Game Catalog output permissions: " + path.generic_string());
			}
		}
	}

	Json buildV13SnapshotDocument(
		const CatalogManifest &manifest,
		const Items &items,
		const Monsters &monsters,
		const Npcs &npcs,
		const std::string &generatedAt,
		const std::string &canaryCommitSha,
		const std::string &appearancesSha256
	) {
		if (manifest.schemaVersion != "1.3.0") {
			throw std::runtime_error("Game Catalog 1.3 adapter requires schema_version 1.3.0.");
		}

		auto baselineManifest = manifest;
		baselineManifest.schemaVersion = "1.2.0";
		auto document = buildSnapshotDocument(baselineManifest, items, monsters, generatedAt, canaryCommitSha, appearancesSha256);
		document["schema_version"] = "1.3.0";
		auto &entities = document["entities"];
		auto &relations = document["relations"];
		std::set<std::string> npcCanonicalKeys;

		for (const auto &[registryKey, npcType] : npcs.getNpcTypes()) {
			if (!npcType || registryKey.empty()) {
				continue;
			}
			if (npcType->getRegistrationSources().size() != 1) {
				throw std::runtime_error("NPC runtime registration source is missing or ambiguous: " + registryKey);
			}
			const auto sourcePath = normalizeNpcSourcePath(*npcType->getRegistrationSources().begin());
			const auto canonicalKey = "npc:" + normalizeRegistryKey(registryKey);
			if (!npcCanonicalKeys.emplace(canonicalKey).second) {
				throw std::runtime_error("NPC canonical key collision: " + canonicalKey);
			}

			entities.push_back(Json {
				{ "type", "npc" },
				{ "canonical_key", canonicalKey },
				{ "introduced_in", nullptr },
				{ "removed_in", nullptr },
				{ "completeness", "unverified" },
				{ "availability", "registered_only" },
				{ "runtime_present", true },
				{ "enabled", true },
				{ "identifiers", Json::array({ Json { { "namespace", "canary.npc_registry_key" }, { "value", registryKey } } }) },
				{ "source_path", sourcePath },
				{ "data", Json {
							  { "registry_key", registryKey },
							  { "runtime_name", npcType->name },
							  { "display_name", nullptr },
							  { "type_name", npcType->typeName },
							  { "name_description", npcType->nameDescription },
							  { "aliases", Json::array() },
							  { "registration_status", "runtime_registered" },
							  { "currency", currencyRecord(manifest, npcType->info.currencyId) },
							  { "attributes", Json { { "dynamic_player_offers_included", false } } },
						  } },
			});

			std::vector<std::size_t> runtimePath;
			appendOffers(relations, manifest, canonicalKey, sourcePath, npcType->info.currencyId, npcType->info.shopItemVector, runtimePath);
		}

		auto &entityArray = entities.get_ref<Json::array_t &>();
		std::ranges::sort(entityArray, {}, [](const Json &entity) {
			return std::pair(entity.at("type").get<std::string>(), entity.at("canonical_key").get<std::string>());
		});
		auto &relationArray = relations.get_ref<Json::array_t &>();
		std::ranges::sort(relationArray, {}, [](const Json &relation) {
			return std::pair(relation.at("type").get<std::string>(), relation.at("canonical_key").get<std::string>());
		});
		document["snapshot"]["entity_count"] = entities.size();
		document["snapshot"]["relation_count"] = relations.size();
		return document;
	}

	ExportResult publishV13SnapshotDocument(const Json &document, const std::filesystem::path &outputPath) {
		const auto errors = validateV13SnapshotDocument(document);
		if (!errors.empty()) {
			std::ostringstream message;
			message << "Game Catalog 1.3 validation failed:";
			for (const auto &error : errors) {
				message << "\n- " << error;
			}
			throw std::runtime_error(message.str());
		}
		if (outputPath.empty()) {
			throw std::runtime_error("Game Catalog output path is empty.");
		}

		const auto serialized = serializeSnapshotDocument(document);
		const auto sha256 = transformToSHA256(serialized);
		const auto sidecarPath = std::filesystem::path(outputPath.string() + ".sha256");
		const auto suffix = ".tmp." + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count());
		const auto temporaryOutput = std::filesystem::path(outputPath.string() + suffix);
		const auto temporarySidecar = std::filesystem::path(sidecarPath.string() + suffix);
		std::error_code error;
		if (!outputPath.parent_path().empty()) {
			std::filesystem::create_directories(outputPath.parent_path(), error);
			if (error) {
				throw std::runtime_error("Cannot create Game Catalog output directory: " + error.message());
			}
		}

		try {
			writeRestrictedFile(temporaryOutput, serialized);
			writeRestrictedFile(temporarySidecar, sha256 + "  " + outputPath.filename().string() + "\n");
			std::filesystem::remove(outputPath, error);
			error.clear();
			std::filesystem::rename(temporaryOutput, outputPath, error);
			if (error) {
				throw std::runtime_error("Cannot publish Game Catalog output: " + error.message());
			}
			std::filesystem::remove(sidecarPath, error);
			error.clear();
			std::filesystem::rename(temporarySidecar, sidecarPath, error);
			if (error) {
				throw std::runtime_error("Cannot publish Game Catalog checksum sidecar: " + error.message());
			}
		} catch (...) {
			std::filesystem::remove(temporaryOutput, error);
			std::filesystem::remove(temporarySidecar, error);
			throw;
		}

		return ExportResult {
			.outputPath = outputPath,
			.sha256 = sha256,
			.entityCount = document.at("entities").size(),
			.relationCount = document.at("relations").size(),
		};
	}

} // namespace game_catalog
