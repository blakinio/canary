#include "game/catalog/game_catalog_exporter.hpp"

#include "creatures/monsters/monsters.hpp"
#include "items/items.hpp"
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
	#include <unordered_map>
	#include <unordered_set>
#endif

namespace game_catalog {
namespace {
	using Json = nlohmann::ordered_json;
	constexpr std::size_t MaximumEntities = 200000;
	constexpr std::size_t MaximumRelations = 1000000;
	const std::regex ReleaseKeyPattern(R"(^[0-9]+(?:\.[0-9]+){1,3}(?:[-+][A-Za-z0-9.-]+)?$)");
	const std::regex CanonicalKeyPattern(R"(^[a-z][a-z0-9_-]*:[a-z0-9][a-z0-9._-]*$)");
	const std::regex LootKeyPattern(R"(^loot:[a-z0-9][a-z0-9._-]*:[a-z0-9][a-z0-9._-]*(?::[0-9]+)?$)");
	const std::regex GitShaPattern(R"(^[0-9a-f]{40,64}$)");
	const std::regex Sha256Pattern(R"(^[0-9a-f]{64}$)");
	const std::regex DateTimePattern(R"(^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$)");

	[[nodiscard]] Json nullable(const std::optional<std::string> &value) {
		return value ? Json(*value) : Json(nullptr);
	}

	[[nodiscard]] const RecordMetadata &metadataFor(
		const std::unordered_map<std::string, RecordMetadata> &records,
		const std::string &sourceKey
	) {
		static const RecordMetadata Unknown;
		const auto iterator = records.find(sourceKey);
		return iterator == records.end() ? Unknown : iterator->second;
	}

	[[nodiscard]] std::string afterNamespace(const std::string &canonicalKey) {
		const auto delimiter = canonicalKey.find(':');
		return delimiter == std::string::npos ? canonicalKey : canonicalKey.substr(delimiter + 1);
	}

	[[nodiscard]] std::string fallbackCreatureKey(const std::string &registryKey) {
		return "creature:registry-" + transformToSHA256(registryKey).substr(0, 24);
	}

	[[nodiscard]] std::string itemCategory(const ItemType &item) {
		if (!item.m_primaryType.empty()) {
			return asLowerCaseString(item.m_primaryType);
		}
		if (item.isShield()) {
			return "shield";
		}
		if (item.isArmor()) {
			return "armor";
		}
		if (item.isWeapon()) {
			const auto weapon = getWeaponName(item.weaponType);
			return weapon.empty() ? "weapon" : asLowerCaseString(weapon);
		}
		return "item_type_" + std::to_string(static_cast<unsigned int>(item.type));
	}

	[[nodiscard]] Json optionalInteger(const bool present, const std::int64_t value) {
		return present ? Json(value) : Json(nullptr);
	}

	[[nodiscard]] Json spellList(const std::vector<spellBlock_t> &spells) {
		Json result = Json::array();
		for (const auto &spell : spells) {
			result.push_back(Json {
				{ "chance", spell.chance },
				{ "interval", spell.speed },
				{ "range", spell.range },
				{ "minimum_combat_value", spell.minCombatValue },
				{ "maximum_combat_value", spell.maxCombatValue },
				{ "combat_spell", spell.combatSpell },
				{ "melee", spell.isMelee },
			});
		}
		return result;
	}

	[[nodiscard]] Json creatureElements(const MonsterType &monster) {
		Json result = Json::array();
		for (const auto &[type, value] : monster.info.elementMap) {
			result.push_back(Json {
				{ "combat_type", getCombatName(type) },
				{ "combat_type_id", static_cast<unsigned int>(type) },
				{ "percent", value },
			});
		}
		return result;
	}

	[[nodiscard]] Json creatureImmunities(const MonsterType &monster) {
		Json result = Json::array();
		for (std::size_t index = 0; index < monster.info.m_conditionImmunities.size(); ++index) {
			if (monster.info.m_conditionImmunities.test(index)) {
				result.push_back(Json { { "kind", "condition" }, { "id", index } });
			}
		}
		for (std::size_t index = 0; index < monster.info.m_damageImmunities.size(); ++index) {
			if (monster.info.m_damageImmunities.test(index)) {
				result.push_back(Json { { "kind", "damage" }, { "id", index } });
			}
		}
		return result;
	}

	[[nodiscard]] Json commonEntity(
		const std::string &type,
		const std::string &canonicalKey,
		const RecordMetadata &metadata,
		Json data,
		Json identifiers
	) {
		return Json {
			{ "type", type },
			{ "canonical_key", canonicalKey },
			{ "introduced_in", nullable(metadata.introducedIn) },
			{ "removed_in", nullable(metadata.removedIn) },
			{ "completeness", metadata.completeness },
			{ "availability", metadata.availability },
			{ "runtime_present", true },
			{ "enabled", metadata.enabled },
			{ "identifiers", std::move(identifiers) },
			{ "source_path", nullable(metadata.sourcePath) },
			{ "data", std::move(data) },
		};
	}

	void collectLoot(
		const CatalogManifest &manifest,
		const std::string &registryKey,
		const std::string &creatureCanonicalKey,
		const std::vector<LootBlock> &loot,
		const std::unordered_map<std::uint16_t, std::string> &itemKeys,
		Json &relations,
		const std::optional<std::string> &containerPath,
		std::size_t &ordinal,
		const std::string &pathPrefix
	) {
		for (std::size_t index = 0; index < loot.size(); ++index) {
			const auto &block = loot[index];
			const auto item = itemKeys.find(block.id);
			const std::string targetKey = item == itemKeys.end()
				? "item:server-" + std::to_string(block.id)
				: item->second;
			const std::string blockPath = pathPrefix.empty() ? std::to_string(index) : pathPrefix + "." + std::to_string(index);
			const std::string sourceKey = registryKey + "|" + std::to_string(block.id) + "|" + blockPath;
			const auto &metadata = metadataFor(manifest.loot, sourceKey);
			const std::string fallbackKey = "loot:" + afterNamespace(creatureCanonicalKey) + ":" + afterNamespace(targetKey) + ":" + std::to_string(ordinal++);
			const std::string canonicalKey = metadata.canonicalKey.value_or(fallbackKey);

			Json conditionData = Json::object();
			if (block.subType != -1) {
				conditionData["sub_type"] = block.subType;
			}
			if (block.actionId != -1) {
				conditionData["action_id"] = block.actionId;
			}
			if (!block.text.empty()) {
				conditionData["text"] = block.text;
			}
			if (!block.name.empty()) {
				conditionData["name_override"] = block.name;
			}
			if (!block.article.empty()) {
				conditionData["article_override"] = block.article;
			}
			if (block.attack != -1) {
				conditionData["attack_override"] = block.attack;
			}
			if (block.defense != -1) {
				conditionData["defense_override"] = block.defense;
			}
			if (block.extraDefense != -1) {
				conditionData["extra_defense_override"] = block.extraDefense;
			}
			if (block.armor != -1) {
				conditionData["armor_override"] = block.armor;
			}
			if (block.shootRange != -1) {
				conditionData["range_override"] = block.shootRange;
			}
			if (block.hitChance != -1) {
				conditionData["hit_chance_override"] = block.hitChance;
			}
			if (block.unique) {
				conditionData["unique"] = true;
			}

			relations.push_back(Json {
				{ "type", "creature_loot" },
				{ "canonical_key", canonicalKey },
				{ "source", creatureCanonicalKey },
				{ "target", targetKey },
				{ "introduced_in", nullable(metadata.introducedIn) },
				{ "removed_in", nullable(metadata.removedIn) },
				{ "completeness", metadata.completeness },
				{ "enabled", metadata.enabled },
				{ "source_path", nullable(metadata.sourcePath) },
				{ "data", Json {
					{ "chance_numerator", block.chance },
					{ "chance_denominator", manifest.lootChanceDenominator },
					{ "minimum_count", block.countmin },
					{ "maximum_count", block.countmax },
					{ "container_path", nullable(containerPath) },
					{ "condition_data", conditionData.empty() ? Json(nullptr) : conditionData },
				} },
			});

			if (!block.childLoot.empty()) {
				const auto nestedPath = containerPath ? *containerPath + "/" + targetKey : targetKey;
				collectLoot(manifest, registryKey, creatureCanonicalKey, block.childLoot, itemKeys, relations, nestedPath, ordinal, blockPath);
			}
		}
	}

	[[nodiscard]] bool safeRelativePath(const Json &value) {
		if (value.is_null()) {
			return true;
		}
		if (!value.is_string()) {
			return false;
		}
		const auto path = std::filesystem::path(value.get<std::string>());
		if (path.empty() || path.is_absolute()) {
			return false;
		}
		return std::ranges::none_of(path, [](const auto &part) {
			return part == "..";
		});
	}

	void validateReleaseReference(
		const Json &value,
		const std::unordered_map<std::string, std::int64_t> &releaseOrders,
		const std::string &path,
		std::vector<std::string> &errors
	) {
		if (value.is_null()) {
			return;
		}
		if (!value.is_string() || !releaseOrders.contains(value.get<std::string>())) {
			errors.emplace_back(path + " references an unknown release.");
		}
	}

	[[nodiscard]] std::string temporarySuffix() {
		return ".tmp." + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count());
	}

	void writeRestrictedFile(const std::filesystem::path &path, const std::string &contents) {
		std::ofstream output(path, std::ios::binary | std::ios::trunc);
		if (!output) {
			throw std::runtime_error("Cannot create Game Catalog output file: " + path.generic_string());
		}
		output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
		output.flush();
		if (!output) {
			throw std::runtime_error("Cannot fully write Game Catalog output file: " + path.generic_string());
		}
		output.close();
		if (!output) {
			throw std::runtime_error("Cannot close Game Catalog output file: " + path.generic_string());
		}
		std::error_code error;
		std::filesystem::permissions(
			path,
			std::filesystem::perms::owner_read | std::filesystem::perms::owner_write,
			std::filesystem::perm_options::replace,
			error
		);
		if (error) {
			throw std::runtime_error("Cannot restrict Game Catalog output permissions: " + path.generic_string());
		}
	}
}

Json buildSnapshotDocument(
	const CatalogManifest &manifest,
	const Items &items,
	const Monsters &monsters,
	const std::string &generatedAt,
	const std::string &canaryCommitSha,
	const std::string &appearancesSha256
) {
	Json entities = Json::array();
	Json relations = Json::array();
	std::unordered_map<std::uint16_t, std::string> itemKeys;

	for (std::size_t id = 0; id < items.size(); ++id) {
		const auto &item = items.getItemType(id);
		if (!item.loaded || item.id == 0 || item.name.empty()) {
			continue;
		}
		const std::string sourceKey = std::to_string(item.id);
		const auto &metadata = metadataFor(manifest.items, sourceKey);
		const std::string canonicalKey = metadata.canonicalKey.value_or("item:server-" + sourceKey);
		itemKeys[item.id] = canonicalKey;

		Json identifiers = Json::array({ Json { { "namespace", "canary.server_item_id" }, { "value", sourceKey } } });
		if (item.wareId != 0) {
			identifiers.push_back(Json { { "namespace", "canary.ware_id" }, { "value", std::to_string(item.wareId) } });
		}

		Json attributes = Json::object();
		if (!item.vocationString.empty()) {
			attributes["vocation_string"] = item.vocationString;
		}
		if (item.proficiencyId != 0) {
			attributes["proficiency_id"] = item.proficiencyId;
		}
		if (item.isDualWielding) {
			attributes["dual_wielding"] = true;
		}

		const bool weapon = item.weaponType != WEAPON_NONE;
		const bool hasElement = item.abilities && item.abilities->elementType != COMBAT_NONE && item.abilities->elementDamage != 0;
		Json data {
			{ "server_id", item.id },
			{ "client_id", nullptr },
			{ "ware_id", item.wareId == 0 ? Json(nullptr) : Json(item.wareId) },
			{ "name", item.name },
			{ "description", item.description.empty() ? Json(nullptr) : Json(item.description) },
			{ "category", itemCategory(item) },
			{ "weapon_type", weapon ? Json(asLowerCaseString(getWeaponName(item.weaponType))) : Json(nullptr) },
			{ "attack", optionalInteger(item.isWeapon(), item.attack) },
			{ "defense", optionalInteger(weapon || item.isShield(), item.defense) },
			{ "extra_defense", optionalInteger(weapon || item.isShield(), item.extraDefense) },
			{ "armor", optionalInteger(item.isArmor(), item.armor) },
			{ "range", optionalInteger(item.isRanged() || item.isMissile(), item.shootRange) },
			{ "weight", item.weight < 0 ? Json(nullptr) : Json(item.weight) },
			{ "minimum_level", item.minReqLevel == 0 ? Json(nullptr) : Json(item.minReqLevel) },
			{ "vocations", nullptr },
			{ "slot_position", item.slotPosition == 0 ? Json(nullptr) : Json(item.slotPosition) },
			{ "imbuement_slots", item.imbuementSlot == 0 ? Json(nullptr) : Json(item.imbuementSlot) },
			{ "upgrade_classification", item.upgradeClassification == 0 ? Json(nullptr) : Json(item.upgradeClassification) },
			{ "element_type", hasElement ? Json(getCombatName(item.abilities->elementType)) : Json(nullptr) },
			{ "element_value", hasElement ? Json(item.abilities->elementDamage) : Json(nullptr) },
			{ "stackable", item.stackable },
			{ "pickupable", item.pickupable },
			{ "image_key", nullable(metadata.imageKey) },
			{ "attributes", std::move(attributes) },
		};
		entities.push_back(commonEntity("item", canonicalKey, metadata, std::move(data), std::move(identifiers)));
	}

	for (const auto &[registryKey, monster] : monsters.monsters) {
		if (!monster || registryKey.empty() || monster->name.empty()) {
			continue;
		}
		const auto &metadata = metadataFor(manifest.creatures, registryKey);
		const std::string canonicalKey = metadata.canonicalKey.value_or(fallbackCreatureKey(registryKey));
		Json identifiers = Json::array({ Json { { "namespace", "canary.monster_registry_key" }, { "value", registryKey } } });
		if (monster->info.raceid != 0) {
			identifiers.push_back(Json { { "namespace", "canary.monster_race_id" }, { "value", std::to_string(monster->info.raceid) } });
		}

		Json attributes = Json::object();
		if (!monster->typeName.empty() && monster->typeName != monster->name) {
			attributes["type_name"] = monster->typeName;
		}
		attributes["bestiary_stars"] = monster->info.bestiaryStars;
		attributes["bestiary_first_unlock"] = monster->info.bestiaryFirstUnlock;
		attributes["bestiary_second_unlock"] = monster->info.bestiarySecondUnlock;

		Json data {
			{ "name", monster->name },
			{ "description", monster->nameDescription.empty() ? Json(nullptr) : Json(monster->nameDescription) },
			{ "race_id", monster->info.raceid == 0 ? Json(nullptr) : Json(monster->info.raceid) },
			{ "look_type", monster->info.outfit.lookType == 0 ? Json(nullptr) : Json(monster->info.outfit.lookType) },
			{ "health", std::max(monster->info.health, 0) },
			{ "max_health", std::max(monster->info.healthMax, 0) },
			{ "experience", monster->info.experience },
			{ "speed", monster->getBaseSpeed() },
			{ "armor", monster->info.armor },
			{ "defense", monster->info.defense },
			{ "mitigation", monster->info.mitigation },
			{ "is_boss", monster->isBoss() },
			{ "is_reward_boss", monster->info.isRewardBoss },
			{ "bestiary_class", monster->info.bestiaryClass.empty() ? Json(nullptr) : Json(monster->info.bestiaryClass) },
			{ "bestiary_race", monster->info.bestiaryRace == BESTY_RACE_NONE ? Json(nullptr) : Json(std::to_string(static_cast<unsigned int>(monster->info.bestiaryRace))) },
			{ "bestiary_occurrence", monster->info.bestiaryOccurrence == 0 ? Json(nullptr) : Json(monster->info.bestiaryOccurrence) },
			{ "bestiary_to_kill", monster->info.bestiaryToUnlock == 0 ? Json(nullptr) : Json(monster->info.bestiaryToUnlock) },
			{ "charm_points", monster->info.bestiaryCharmsPoints == 0 ? Json(nullptr) : Json(monster->info.bestiaryCharmsPoints) },
			{ "elements", creatureElements(*monster) },
			{ "immunities", creatureImmunities(*monster) },
			{ "attacks", spellList(monster->info.attackSpells) },
			{ "defenses", spellList(monster->info.defenseSpells) },
			{ "attributes", std::move(attributes) },
		};
		entities.push_back(commonEntity("creature", canonicalKey, metadata, std::move(data), std::move(identifiers)));

		std::size_t lootOrdinal = 0;
		collectLoot(manifest, registryKey, canonicalKey, monster->info.lootItems, itemKeys, relations, std::nullopt, lootOrdinal, "");
	}

	auto &entityArray = entities.get_ref<Json::array_t&>();
	std::ranges::sort(entityArray, {}, [](const Json &entity) {
		return std::pair(entity.at("type").get<std::string>(), entity.at("canonical_key").get<std::string>());
	});
	auto &relationArray = relations.get_ref<Json::array_t&>();
	std::ranges::sort(relationArray, {}, [](const Json &relation) {
		return std::pair(relation.at("type").get<std::string>(), relation.at("canonical_key").get<std::string>());
	});

	Json releases = manifest.releases;
	auto &releaseArray = releases.get_ref<Json::array_t&>();
	std::ranges::sort(releaseArray, {}, [](const Json &release) {
		return std::pair(release.at("release_order").get<std::int64_t>(), release.at("key").get<std::string>());
	});

	return Json {
		{ "contract", "oteryn.game-catalog" },
		{ "schema_version", "1.0.0" },
		{ "snapshot", Json {
			{ "generated_at", generatedAt },
			{ "canary_commit_sha", canaryCommitSha },
			{ "datapack_commit_sha", nullable(manifest.datapackCommitSha) },
			{ "protocol_profile", manifest.protocolProfile },
			{ "runtime_release", manifest.runtimeRelease },
			{ "content_target_release", manifest.contentTargetRelease },
			{ "verified_content_through_release", manifest.verifiedContentThroughRelease },
			{ "contains_content_through_release", nullable(manifest.containsContentThroughRelease) },
			{ "appearances_sha256", appearancesSha256 },
			{ "map_sha256", nullptr },
			{ "producer_build_id", nullable(manifest.producerBuildId) },
			{ "entity_count", entities.size() },
			{ "relation_count", relations.size() },
		} },
		{ "releases", std::move(releases) },
		{ "entities", std::move(entities) },
		{ "relations", std::move(relations) },
	};
}

std::vector<std::string> validateSnapshotDocument(const Json &document) {
	std::vector<std::string> errors;
	if (!document.is_object() || document.value("contract", "") != "oteryn.game-catalog" || document.value("schema_version", "") != "1.0.0") {
		errors.emplace_back("Unsupported Game Catalog contract or schema version.");
		return errors;
	}
	if (!document.contains("snapshot") || !document.at("snapshot").is_object()
	    || !document.contains("releases") || !document.at("releases").is_array()
	    || !document.contains("entities") || !document.at("entities").is_array()
	    || !document.contains("relations") || !document.at("relations").is_array()) {
		errors.emplace_back("Game Catalog document is missing required top-level objects or arrays.");
		return errors;
	}

	const auto &snapshot = document.at("snapshot");
	if (!snapshot.value("generated_at", "").empty() && !std::regex_match(snapshot.value("generated_at", ""), DateTimePattern)) {
		errors.emplace_back("snapshot.generated_at is not RFC 3339 shaped.");
	}
	if (!std::regex_match(snapshot.value("canary_commit_sha", ""), GitShaPattern)) {
		errors.emplace_back("snapshot.canary_commit_sha is not a complete lowercase Git SHA.");
	}
	if (!std::regex_match(snapshot.value("appearances_sha256", ""), Sha256Pattern)) {
		errors.emplace_back("snapshot.appearances_sha256 is not lowercase SHA-256.");
	}

	std::unordered_map<std::string, std::int64_t> releaseOrders;
	std::unordered_set<std::int64_t> seenOrders;
	std::pair<std::int64_t, std::string> previousRelease { -1, "" };
	for (const auto &release : document.at("releases")) {
		if (!release.is_object() || !release.contains("key") || !release.at("key").is_string()
		    || !release.contains("release_order") || !release.at("release_order").is_number_integer()) {
			errors.emplace_back("Release records require string key and integer release_order.");
			continue;
		}
		const auto key = release.at("key").get<std::string>();
		const auto order = release.at("release_order").get<std::int64_t>();
		if (!std::regex_match(key, ReleaseKeyPattern) || !releaseOrders.emplace(key, order).second) {
			errors.emplace_back("Release key is invalid or duplicated: " + key);
		}
		if (!seenOrders.emplace(order).second) {
			errors.emplace_back("release_order is duplicated: " + std::to_string(order));
		}
		const std::pair current(order, key);
		if (current < previousRelease) {
			errors.emplace_back("Releases are not deterministically sorted.");
		}
		previousRelease = current;
	}

	for (const auto field : { "runtime_release", "content_target_release", "verified_content_through_release", "contains_content_through_release" }) {
		validateReleaseReference(snapshot.at(field), releaseOrders, std::string("snapshot.") + field, errors);
	}
	if (snapshot.value("entity_count", MaximumEntities + 1) != document.at("entities").size()) {
		errors.emplace_back("Declared entity_count does not match entities array.");
	}
	if (snapshot.value("relation_count", MaximumRelations + 1) != document.at("relations").size()) {
		errors.emplace_back("Declared relation_count does not match relations array.");
	}
	if (document.at("entities").size() > MaximumEntities || document.at("relations").size() > MaximumRelations) {
		errors.emplace_back("Game Catalog document exceeds entity or relation bounds.");
	}

	std::unordered_set<std::string> entityKeys;
	std::pair<std::string, std::string> previousEntity;
	for (const auto &entity : document.at("entities")) {
		if (!entity.is_object()) {
			errors.emplace_back("Entity record is not an object.");
			continue;
		}
		const auto type = entity.value("type", "");
		const auto key = entity.value("canonical_key", "");
		if ((type != "item" && type != "creature") || !std::regex_match(key, CanonicalKeyPattern) || !entityKeys.emplace(key).second) {
			errors.emplace_back("Entity type/key is invalid or duplicated: " + key);
		}
		const std::pair current(type, key);
		if (current < previousEntity) {
			errors.emplace_back("Entities are not deterministically sorted.");
		}
		previousEntity = current;
		validateReleaseReference(entity.at("introduced_in"), releaseOrders, key + ".introduced_in", errors);
		validateReleaseReference(entity.at("removed_in"), releaseOrders, key + ".removed_in", errors);
		if (!safeRelativePath(entity.at("source_path"))) {
			errors.emplace_back("Entity has an unsafe source_path: " + key);
		}
		if (entity.at("introduced_in").is_string() && entity.at("removed_in").is_string()) {
			const auto introduced = releaseOrders[entity.at("introduced_in").get<std::string>()];
			const auto removed = releaseOrders[entity.at("removed_in").get<std::string>()];
			if (removed <= introduced) {
				errors.emplace_back("Entity removed_in is not an exclusive later release: " + key);
			}
		}
	}

	std::unordered_set<std::string> relationKeys;
	std::pair<std::string, std::string> previousRelation;
	for (const auto &relation : document.at("relations")) {
		if (!relation.is_object()) {
			errors.emplace_back("Relation record is not an object.");
			continue;
		}
		const auto type = relation.value("type", "");
		const auto key = relation.value("canonical_key", "");
		if (type != "creature_loot" || !std::regex_match(key, LootKeyPattern) || !relationKeys.emplace(key).second) {
			errors.emplace_back("Relation type/key is invalid or duplicated: " + key);
		}
		const std::pair current(type, key);
		if (current < previousRelation) {
			errors.emplace_back("Relations are not deterministically sorted.");
		}
		previousRelation = current;
		for (const auto endpoint : { "source", "target" }) {
			if (!relation.contains(endpoint) || !relation.at(endpoint).is_string() || !entityKeys.contains(relation.at(endpoint).get<std::string>())) {
				errors.emplace_back("Relation has a dangling endpoint: " + key + "." + endpoint);
			}
		}
		validateReleaseReference(relation.at("introduced_in"), releaseOrders, key + ".introduced_in", errors);
		validateReleaseReference(relation.at("removed_in"), releaseOrders, key + ".removed_in", errors);
		if (!safeRelativePath(relation.at("source_path"))) {
			errors.emplace_back("Relation has an unsafe source_path: " + key);
		}
		const auto &data = relation.at("data");
		if (!data.is_object() || !data.at("chance_numerator").is_number_unsigned()
		    || !data.at("chance_denominator").is_number_unsigned()
		    || data.at("chance_denominator").get<std::uint64_t>() == 0
		    || data.at("chance_numerator").get<std::uint64_t>() > data.at("chance_denominator").get<std::uint64_t>()) {
			errors.emplace_back("Relation has an invalid probability: " + key);
		}
		if (data.at("maximum_count").get<std::uint64_t>() < data.at("minimum_count").get<std::uint64_t>()) {
			errors.emplace_back("Relation has an invalid count range: " + key);
		}
	}
	return errors;
}

std::string serializeSnapshotDocument(const Json &document) {
	const auto errors = validateSnapshotDocument(document);
	if (!errors.empty()) {
		std::ostringstream message;
		message << "Game Catalog snapshot validation failed:";
		for (const auto &error : errors) {
			message << "\n- " << error;
		}
		throw std::runtime_error(message.str());
	}
	return document.dump(-1, ' ', false, nlohmann::json::error_handler_t::strict) + "\n";
}

ExportResult publishSnapshotDocument(const Json &document, const std::filesystem::path &outputPath) {
	const auto serialized = serializeSnapshotDocument(document);
	const auto sha256 = transformToSHA256(serialized);
	const auto sidecarPath = std::filesystem::path(outputPath.string() + ".sha256");
	const auto parent = outputPath.parent_path().empty() ? std::filesystem::current_path() : outputPath.parent_path();
	std::error_code error;
	if (!std::filesystem::is_directory(parent, error) || error) {
		throw std::runtime_error("Game Catalog output parent directory does not exist: " + parent.generic_string());
	}
	for (const auto &path : { outputPath, sidecarPath }) {
		if (std::filesystem::is_directory(path, error) || std::filesystem::is_symlink(path, error)) {
			throw std::runtime_error("Game Catalog output must not be a directory or symlink: " + path.generic_string());
		}
	}

	const auto suffix = temporarySuffix();
	const auto temporaryOutput = std::filesystem::path(outputPath.string() + suffix);
	const auto temporarySidecar = std::filesystem::path(sidecarPath.string() + suffix);
	const auto backupOutput = std::filesystem::path(outputPath.string() + ".backup" + suffix);
	const auto backupSidecar = std::filesystem::path(sidecarPath.string() + ".backup" + suffix);
	bool outputBackedUp = false;
	bool sidecarBackedUp = false;

	try {
		writeRestrictedFile(temporaryOutput, serialized);
		writeRestrictedFile(temporarySidecar, sha256 + "  " + outputPath.filename().string() + "\n");

		if (std::filesystem::exists(outputPath)) {
			std::filesystem::rename(outputPath, backupOutput);
			outputBackedUp = true;
		}
		if (std::filesystem::exists(sidecarPath)) {
			std::filesystem::rename(sidecarPath, backupSidecar);
			sidecarBackedUp = true;
		}
		std::filesystem::rename(temporaryOutput, outputPath);
		std::filesystem::rename(temporarySidecar, sidecarPath);
		if (outputBackedUp) {
			std::filesystem::remove(backupOutput);
		}
		if (sidecarBackedUp) {
			std::filesystem::remove(backupSidecar);
		}
	} catch (...) {
		std::filesystem::remove(temporaryOutput, error);
		std::filesystem::remove(temporarySidecar, error);
		if (!std::filesystem::exists(outputPath) && outputBackedUp) {
			std::filesystem::rename(backupOutput, outputPath, error);
		}
		if (!std::filesystem::exists(sidecarPath) && sidecarBackedUp) {
			std::filesystem::rename(backupSidecar, sidecarPath, error);
		}
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
