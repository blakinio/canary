#include "game/catalog/catalog_export_options.hpp"
#include "game/catalog/game_catalog_exporter.hpp"
#include "items/items.hpp"
#include "creatures/monsters/monsters.hpp"

#include <gtest/gtest.h>
#include <nlohmann/json.hpp>

#ifndef USE_PRECOMPILED_HEADERS
	#include <filesystem>
	#include <fstream>
#endif

namespace game_catalog {
namespace {
	CatalogManifest fixtureManifest() {
		CatalogManifest manifest;
		manifest.protocolProfile = "oteryn-current";
		manifest.runtimeRelease = "15.20";
		manifest.contentTargetRelease = "15.20";
		manifest.verifiedContentThroughRelease = "15.20";
		manifest.containsContentThroughRelease = "15.30";
		manifest.lootChanceDenominator = 100000;
		manifest.producerBuildId = "unit-test";
		manifest.releases = nlohmann::ordered_json::array({
			{
				{ "key", "15.20" }, { "display_label", "15.20" },
				{ "major", 15 }, { "minor", 20 }, { "patch", 0 }, { "build", nullptr },
				{ "release_order", 152000 }, { "protocol_family", "oteryn-current" }, { "released_at", nullptr },
			},
			{
				{ "key", "15.30" }, { "display_label", "15.30" },
				{ "major", 15 }, { "minor", 30 }, { "patch", 0 }, { "build", nullptr },
				{ "release_order", 153000 }, { "protocol_family", "oteryn-current" }, { "released_at", nullptr },
			},
		});

		manifest.items["2516"] = RecordMetadata {
			.canonicalKey = "item:dragon-shield",
			.introducedIn = "15.20",
			.removedIn = std::nullopt,
			.completeness = "complete",
			.availability = "obtainable",
			.enabled = true,
			.sourcePath = "items/items.xml",
			.imageKey = std::nullopt,
		};
		manifest.creatures["dragon"] = RecordMetadata {
			.canonicalKey = "creature:dragon",
			.introducedIn = "15.20",
			.removedIn = std::nullopt,
			.completeness = "complete",
			.availability = "encounterable",
			.enabled = true,
			.sourcePath = "monster/dragons/dragon.lua",
			.imageKey = std::nullopt,
		};
		manifest.loot["dragon|2516|0"] = RecordMetadata {
			.canonicalKey = "loot:dragon:dragon-shield",
			.introducedIn = "15.20",
			.removedIn = std::nullopt,
			.completeness = "complete",
			.availability = "unknown",
			.enabled = true,
			.sourcePath = "monster/dragons/dragon.lua",
			.imageKey = std::nullopt,
		};
		return manifest;
	}

	void populateRuntime(Items &items, Monsters &monsters) {
		items.getItems().resize(2517);
		auto &item = items.getItems()[2516];
		item.loaded = true;
		item.id = 2516;
		item.name = "Dragon Shield";
		item.type = ITEM_TYPE_SHIELD;
		item.weaponType = WEAPON_SHIELD;
		item.defense = 31;
		item.weight = 6000;
		item.pickupable = true;
		item.slotPosition = SLOTP_LEFT | SLOTP_RIGHT;
		item.imbuementSlot = 1;
		item.upgradeClassification = 1;

		auto monster = std::make_shared<MonsterType>("Dragon");
		monster->info.health = 1000;
		monster->info.healthMax = 1000;
		monster->info.experience = 700;
		monster->info.baseSpeed = 180;
		monster->info.armor = 25;
		monster->info.defense = 30;
		monster->info.raceid = 34;
		monster->info.outfit.lookType = 34;
		monster->info.bestiaryClass = "Dragon";
		monster->info.bestiaryRace = BESTY_RACE_DRAGON;
		monster->info.bestiaryOccurrence = 1;
		monster->info.bestiaryToUnlock = 1000;
		monster->info.bestiaryCharmsPoints = 25;
		LootBlock loot;
		loot.id = 2516;
		loot.chance = 100;
		loot.countmin = 1;
		loot.countmax = 1;
		monster->info.lootItems.push_back(loot);
		monsters.monsters.emplace("dragon", std::move(monster));
	}
}

TEST(GameCatalogExportOptions, RequiresOutputAndRejectsDuplicates) {
	char executable[] = "canary";
	char mode[] = "--export-game-catalog-only";
	char output[] = "--game-catalog-output=catalog.json";
	char* argv[] = { executable, mode, output };
	const auto parsed = parseExportOptions(argv);
	ASSERT_TRUE(parsed.requested);
	ASSERT_TRUE(parsed.options.has_value());
	EXPECT_EQ(parsed.options->outputPath, std::filesystem::path("catalog.json"));

	char duplicate[] = "--game-catalog-output=other.json";
	char* duplicateArgv[] = { executable, mode, output, duplicate };
	const auto rejected = parseExportOptions(duplicateArgv);
	EXPECT_FALSE(rejected.options.has_value());
	EXPECT_FALSE(rejected.error.empty());
}

TEST(GameCatalogExporter, ReadsFinalRuntimeValuesAndLootExactly) {
	Items items;
	Monsters monsters;
	populateRuntime(items, monsters);
	const auto document = buildSnapshotDocument(
		fixtureManifest(), items, monsters, "2026-07-28T00:00:00Z",
		"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
	);

	EXPECT_TRUE(validateSnapshotDocument(document).empty());
	ASSERT_EQ(document.at("entities").size(), 2);
	ASSERT_EQ(document.at("relations").size(), 1);
	const auto item = std::ranges::find_if(document.at("entities"), [](const auto &entity) {
		return entity.at("canonical_key") == "item:dragon-shield";
	});
	ASSERT_NE(item, document.at("entities").end());
	EXPECT_EQ(item->at("data").at("defense"), 31);
	EXPECT_EQ(item->at("data").at("weight"), 6000);

	const auto &loot = document.at("relations").front().at("data");
	EXPECT_EQ(loot.at("chance_numerator"), 100);
	EXPECT_EQ(loot.at("chance_denominator"), 100000);
	EXPECT_EQ(loot.at("minimum_count"), 1);
	EXPECT_EQ(loot.at("maximum_count"), 1);
}

TEST(GameCatalogExporter, MissingReviewedMetadataRemainsUnverifiedAndUnknown) {
	Items items;
	Monsters monsters;
	populateRuntime(items, monsters);
	auto manifest = fixtureManifest();
	manifest.items.clear();
	const auto document = buildSnapshotDocument(
		manifest, items, monsters, "2026-07-28T00:00:00Z",
		"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
	);
	const auto item = std::ranges::find_if(document.at("entities"), [](const auto &entity) {
		return entity.at("type") == "item";
	});
	ASSERT_NE(item, document.at("entities").end());
	EXPECT_EQ(item->at("completeness"), "unverified");
	EXPECT_EQ(item->at("availability"), "unknown");
	EXPECT_EQ(item->at("canonical_key"), "item:server-2516");
}

TEST(GameCatalogExporter, FixedInputsProduceByteIdenticalOutput) {
	Items items;
	Monsters monsters;
	populateRuntime(items, monsters);
	const auto manifest = fixtureManifest();
	const auto first = buildSnapshotDocument(
		manifest, items, monsters, "2026-07-28T00:00:00Z",
		"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
	);
	const auto second = buildSnapshotDocument(
		manifest, items, monsters, "2026-07-28T00:00:00Z",
		"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
	);
	EXPECT_EQ(serializeSnapshotDocument(first), serializeSnapshotDocument(second));
}

TEST(GameCatalogExporter, DanglingEndpointsAndInvalidRangesFailClosed) {
	Items items;
	Monsters monsters;
	populateRuntime(items, monsters);
	auto document = buildSnapshotDocument(
		fixtureManifest(), items, monsters, "2026-07-28T00:00:00Z",
		"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
		"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
	);
	document.at("relations").front()["target"] = "item:missing";
	document.at("entities").front()["removed_in"] = "15.20";
	const auto errors = validateSnapshotDocument(document);
	EXPECT_FALSE(errors.empty());
}

TEST(GameCatalogExporter, FailedValidationPreservesPreviousOutput) {
	const auto directory = std::filesystem::temp_directory_path() / "canary-game-catalog-test";
	std::filesystem::create_directories(directory);
	const auto output = directory / "snapshot.json";
	{
		std::ofstream previous(output, std::ios::binary | std::ios::trunc);
		previous << "previous-valid-output\n";
	}

	nlohmann::ordered_json invalid = { { "contract", "wrong" } };
	EXPECT_THROW(publishSnapshotDocument(invalid, output), std::runtime_error);
	std::ifstream input(output, std::ios::binary);
	std::string contents((std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>());
	EXPECT_EQ(contents, "previous-valid-output\n");
	std::filesystem::remove_all(directory);
}

} // namespace game_catalog
