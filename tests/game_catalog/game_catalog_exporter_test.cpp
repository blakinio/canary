#include "game/catalog/game_catalog_exporter.hpp"

#include <gtest/gtest.h>

#include <array>
#include <string>
#include <vector>

namespace oteryn::catalog {
namespace {

[[nodiscard]] GameCatalogExportArgumentResult parse(const std::vector<std::string> &values) {
	std::vector<std::string> storage = values;
	std::vector<char*> arguments;
	arguments.reserve(storage.size());
	for (auto &value : storage) {
		arguments.push_back(value.data());
	}
	return parseGameCatalogExportArguments(arguments);
}

TEST(GameCatalogExportArgumentsTest, IgnoresCatalogOptionsWithoutExportOnlyFlag) {
	const auto result = parse({ "canary", "--game-catalog-output=ignored.json" });

	EXPECT_FALSE(result.requested);
	EXPECT_FALSE(result.options.has_value());
	EXPECT_TRUE(result.error.empty());
}

TEST(GameCatalogExportArgumentsTest, RequiresOutputPath) {
	const auto result = parse({ "canary", "--export-game-catalog-only" });

	EXPECT_TRUE(result.requested);
	EXPECT_FALSE(result.options.has_value());
	EXPECT_EQ(result.error, "--game-catalog-output=<path> is required in export-only mode");
}

TEST(GameCatalogExportArgumentsTest, ParsesDeterministicExportOptions) {
	const auto result = parse(
		{
			"canary",
			"--export-game-catalog-only",
			"--game-catalog-output=/tmp/game-catalog.json",
			"--game-catalog-generated-at=2026-01-01T00:00:00Z",
		}
	);

	ASSERT_TRUE(result.requested);
	ASSERT_TRUE(result.options.has_value());
	EXPECT_TRUE(result.error.empty());
	EXPECT_EQ(result.options->outputPath.generic_string(), "/tmp/game-catalog.json");
	ASSERT_TRUE(result.options->generatedAt.has_value());
	EXPECT_EQ(*result.options->generatedAt, "2026-01-01T00:00:00Z");
}

TEST(GameCatalogExportArgumentsTest, RejectsDuplicateOutputPath) {
	const auto result = parse(
		{
			"canary",
			"--export-game-catalog-only",
			"--game-catalog-output=first.json",
			"--game-catalog-output=second.json",
		}
	);

	EXPECT_TRUE(result.requested);
	EXPECT_EQ(result.error, "Duplicate --game-catalog-output argument");
}

TEST(GameCatalogExportArgumentsTest, RejectsDuplicateGeneratedAt) {
	const auto result = parse(
		{
			"canary",
			"--export-game-catalog-only",
			"--game-catalog-output=game-catalog.json",
			"--game-catalog-generated-at=2026-01-01T00:00:00Z",
			"--game-catalog-generated-at=2026-01-02T00:00:00Z",
		}
	);

	EXPECT_TRUE(result.requested);
	EXPECT_EQ(result.error, "Duplicate --game-catalog-generated-at argument");
}

TEST(GameCatalogExportArgumentsTest, RejectsEmptyGeneratedAt) {
	const auto result = parse(
		{
			"canary",
			"--export-game-catalog-only",
			"--game-catalog-output=game-catalog.json",
			"--game-catalog-generated-at=",
		}
	);

	EXPECT_TRUE(result.requested);
	EXPECT_FALSE(result.options.has_value());
	EXPECT_EQ(result.error, "--game-catalog-generated-at must not be empty");
}

}
}
