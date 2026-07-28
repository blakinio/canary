#pragma once

#include <filesystem>
#include <optional>
#include <span>
#include <string>

class Logger;

namespace oteryn::catalog {

struct GameCatalogExportOptions {
	std::filesystem::path outputPath;
	std::optional<std::string> generatedAt;
};

struct GameCatalogExportArgumentResult {
	bool requested = false;
	std::optional<GameCatalogExportOptions> options;
	std::string error;
};

[[nodiscard]] GameCatalogExportArgumentResult parseGameCatalogExportArguments(std::span<char*> arguments);

class GameCatalogExporter {
public:
	explicit GameCatalogExporter(Logger &logger);

	[[nodiscard]] int run(const GameCatalogExportOptions &options) const;

private:
	Logger &logger;
};

}
