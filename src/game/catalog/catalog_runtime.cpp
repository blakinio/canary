#include "canary_server.hpp"

#include "config/configmanager.hpp"
#include "creatures/npcs/npcs.hpp"
#include "creatures/players/components/weapon_proficiency.hpp"
#include "creatures/players/grouping/familiars.hpp"
#include "creatures/players/imbuements/imbuements.hpp"
#include "creatures/players/storages/storages.hpp"
#include "creatures/players/vocations/vocation.hpp"
#include "game/catalog/catalog_export_options.hpp"
#include "game/catalog/game_catalog_exporter.hpp"
#include "game/catalog/game_catalog_manifest.hpp"
#include "game/game.hpp"
#include "game/scheduling/dispatcher.hpp"
#include "items/item.hpp"
#include "lib/thread/thread_pool.hpp"
#include "lua/creature/events.hpp"
#include "lua/modules/modules.hpp"
#include "lua/scripts/lua_environment.hpp"
#include "lua/scripts/scripts.hpp"
#include "utils/benchmark.hpp"
#include "utils/tools.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdlib>
	#include <ctime>
	#include <fstream>
	#include <stdexcept>
#endif

namespace {
	[[nodiscard]] std::string readBinaryFile(const std::filesystem::path &path) {
		std::error_code error;
		if (!std::filesystem::is_regular_file(path, error) || error || std::filesystem::is_symlink(path, error)) {
			throw std::runtime_error("Game Catalog provenance file is unavailable: " + path.generic_string());
		}
		std::ifstream input(path, std::ios::binary);
		if (!input) {
			throw std::runtime_error("Cannot read Game Catalog provenance file: " + path.generic_string());
		}
		return std::string(std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>());
	}

	[[nodiscard]] std::string resolveGeneratedAt(const game_catalog::ExportOptions &options) {
		if (options.generatedAt) {
			return *options.generatedAt;
		}
		return fmt::format("{:%FT%TZ}", fmt::gmtime(std::time(nullptr)));
	}

	[[nodiscard]] std::string resolveCanaryCommitSha(const game_catalog::ExportOptions &options) {
		if (options.canaryCommitSha) {
			return *options.canaryCommitSha;
		}
#if defined(GIT_RETRIEVED_STATE) && GIT_RETRIEVED_STATE
		if (std::string_view(GIT_HEAD_SHA1).size() >= 40) {
			return GIT_HEAD_SHA1;
		}
#endif
		if (const char* environment = std::getenv("CANARY_GAME_CATALOG_COMMIT_SHA"); environment && *environment != '\0') {
			return environment;
		}
		throw std::runtime_error("Exact Canary commit SHA is unavailable. Build with Git metadata or pass --game-catalog-canary-commit=<sha>.");
	}

}

void CanaryServer::loadGameCatalogDefinitions() {
	Benchmark modulesBenchmark;
	logger.info("Initializing Lua environment for Game Catalog export...");
	if (!g_luaEnvironment().getLuaState()) {
		g_luaEnvironment().initState();
	}

	const auto startupLoadTelemetry = g_configManager().getBoolean(LUA_STARTUP_LOAD_TELEMETRY);
	const auto timedLoad = [this, startupLoadTelemetry](std::string moduleName, const auto &loader) {
		if (!startupLoadTelemetry) {
			if (!loader()) {
				modulesLoadHelper(false, std::move(moduleName));
			}
			return;
		}

		Benchmark benchmark;
		const bool loaded = loader();
		const auto duration = benchmark.duration();
		if (!loaded) {
			modulesLoadHelper(false, moduleName);
		}
		logger.info("Loaded {} in {:.3f} ms", moduleName, duration);
	};

	auto coreFolder = g_configManager().getString(CORE_DIRECTORY);
	timedLoad("proficiencies.json", [] {
		return WeaponProficiency::loadFromJson();
	});
	timedLoad("appearances.dat", [&coreFolder] {
		return g_game().loadAppearanceProtobuf(coreFolder + "/items/appearances.dat") == ERROR_NONE;
	});
	timedLoad("XML/vocations.xml", [] {
		return g_vocations().loadFromXml();
	});
	timedLoad("XML/outfits.xml", [] {
		return Outfits::getInstance().loadFromXml();
	});
	timedLoad("XML/familiars.xml", [] {
		return Familiars::getInstance().loadFromXml();
	});
	timedLoad("XML/imbuements.xml", [] {
		return g_imbuements().loadFromXml();
	});
	timedLoad("XML/storages.xml", [] {
		return g_storages().loadFromXML();
	});
	timedLoad("items.xml", [] {
		return Item::items.loadFromXml();
	});

	const auto datapackFolder = g_configManager().getString(DATA_DIRECTORY);
	timedLoad("core.lua", [&coreFolder] {
		return g_luaEnvironment().loadFile(coreFolder + "/core.lua", "core.lua") == 0;
	});
	timedLoad(coreFolder + "/scripts/libs", [&coreFolder] {
		return g_scripts().loadScripts(coreFolder + "/scripts/lib", true, false);
	});
	timedLoad(coreFolder + "/scripts", [&coreFolder] {
		return g_scripts().loadScripts(coreFolder + "/scripts", false, false);
	});
	timedLoad("npclib", [] {
		return g_npcs().load(true, false);
	});
	timedLoad("events/events.xml", [] {
		return g_events().loadFromXml();
	});
	timedLoad("modules/modules.xml", [] {
		return g_modules().loadFromXml();
	});
	timedLoad(datapackFolder + "/scripts/libs", [&datapackFolder] {
		return g_scripts().loadScripts(datapackFolder + "/scripts/lib", true, false);
	});
	timedLoad(datapackFolder + "/scripts", [&datapackFolder] {
		return g_scripts().loadScripts(datapackFolder + "/scripts", false, false);
	});
	timedLoad(datapackFolder + "/monster", [&datapackFolder] {
		return g_scripts().loadScripts(datapackFolder + "/monster", false, false);
	});

	if (startupLoadTelemetry) {
		logger.info("Loaded Game Catalog definitions in {:.3f} seconds.", modulesBenchmark.duration() / 1000.0);
	}
}

int CanaryServer::exportGameCatalogOnly(const game_catalog::ExportOptions &options) {
	const auto stopExportRuntime = [] {
		g_dispatcher().shutdown();
		g_threadPool().shutdown();
	};

	try {
		loadConfigLua();
		validateDatapack();
		loadGameCatalogDefinitions();

		const auto dataDirectory = std::filesystem::path(g_configManager().getString(DATA_DIRECTORY));
		const auto manifestDirectory = options.manifestDirectory.empty() ? dataDirectory / "catalog" : options.manifestDirectory;
		const auto manifest = game_catalog::loadCatalogManifest(manifestDirectory);
		const auto appearancesPath = std::filesystem::path(g_configManager().getString(CORE_DIRECTORY)) / "items" / "appearances.dat";
		const auto appearancesSha256 = transformToSHA256(readBinaryFile(appearancesPath));
		const auto generatedAt = resolveGeneratedAt(options);
		const auto canaryCommitSha = resolveCanaryCommitSha(options);
		const auto document = game_catalog::buildSnapshotDocument(
			manifest,
			Item::items,
			g_monsters(),
			generatedAt,
			canaryCommitSha,
			appearancesSha256
		);
		const auto result = game_catalog::publishSnapshotDocument(document, options.outputPath);
		logger.info(
			"Game Catalog export completed: {} (sha256 {}, {} entities, {} relations).",
			result.outputPath.generic_string(),
			result.sha256,
			result.entityCount,
			result.relationCount
		);
		stopExportRuntime();
		return EXIT_SUCCESS;
	} catch (const std::exception &error) {
		logger.error("[GameCatalog] Export failed: {}", error.what());
		stopExportRuntime();
		return EXIT_FAILURE;
	}
}
