#include "game/catalog/catalog_definition_loader.hpp"

#include "config/configmanager.hpp"
#include "core.hpp"
#include "creatures/npcs/npcs.hpp"
#include "creatures/players/components/weapon_proficiency.hpp"
#include "creatures/players/grouping/familiars.hpp"
#include "creatures/players/imbuements/imbuements.hpp"
#include "creatures/players/storages/storages.hpp"
#include "creatures/players/vocations/vocation.hpp"
#include "game/game.hpp"
#include "lua/creature/events.hpp"
#include "lua/modules/modules.hpp"
#include "lua/scripts/lua_environment.hpp"
#include "lua/scripts/scripts.hpp"

#include <functional>
#include <stdexcept>
#include <string>
#include <string_view>

namespace oteryn::catalog {
namespace {

void requireLoaded(Logger &logger, const std::string_view identifier, const std::function<bool()> &loader) {
	logger.info("[game-catalog] Loading {}", identifier);
	if (!loader()) {
		throw std::runtime_error(fmt::format("Cannot load authoritative catalog dependency: {}", identifier));
	}
}

}

void loadAuthoritativeCatalogDefinitions(Logger &logger) {
	if (!g_luaEnvironment().getLuaState()) {
		g_luaEnvironment().initState();
	}

	auto coreFolder = g_configManager().getString(CORE_DIRECTORY);
	const auto datapackFolder = g_configManager().getString(DATA_DIRECTORY);

	requireLoaded(logger, "proficiencies.json", [] {
		return WeaponProficiency::loadFromJson();
	});
	requireLoaded(logger, "appearances.dat", [&coreFolder] {
		return g_game().loadAppearanceProtobuf(coreFolder + "/items/appearances.dat") == ERROR_NONE;
	});
	requireLoaded(logger, "XML/vocations.xml", [] {
		return g_vocations().loadFromXml();
	});
	requireLoaded(logger, "XML/outfits.xml", [] {
		return Outfits::getInstance().loadFromXml();
	});
	requireLoaded(logger, "XML/familiars.xml", [] {
		return Familiars::getInstance().loadFromXml();
	});
	requireLoaded(logger, "XML/imbuements.xml", [] {
		return g_imbuements().loadFromXml();
	});
	requireLoaded(logger, "XML/storages.xml", [] {
		return g_storages().loadFromXML();
	});
	requireLoaded(logger, "items.xml", [] {
		return Item::items.loadFromXml();
	});

	requireLoaded(logger, "core.lua", [&coreFolder] {
		return g_luaEnvironment().loadFile(coreFolder + "/core.lua", "core.lua") == 0;
	});
	requireLoaded(logger, coreFolder + "/scripts/lib", [&coreFolder] {
		return g_scripts().loadScripts(coreFolder + "/scripts/lib", true, false);
	});
	requireLoaded(logger, coreFolder + "/scripts", [&coreFolder] {
		return g_scripts().loadScripts(coreFolder + "/scripts", false, false);
	});
	requireLoaded(logger, "npclib", [] {
		return g_npcs().load(true, false);
	});
	requireLoaded(logger, "events/events.xml", [] {
		return g_events().loadFromXml();
	});
	requireLoaded(logger, "modules/modules.xml", [] {
		return g_modules().loadFromXml();
	});
	requireLoaded(logger, datapackFolder + "/scripts/lib", [&datapackFolder] {
		return g_scripts().loadScripts(datapackFolder + "/scripts/lib", true, false);
	});
	requireLoaded(logger, datapackFolder + "/scripts", [&datapackFolder] {
		return g_scripts().loadScripts(datapackFolder + "/scripts", false, false);
	});
	requireLoaded(logger, datapackFolder + "/monster", [&datapackFolder] {
		return g_scripts().loadScripts(datapackFolder + "/monster", false, false);
	});
}

}
