/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_session_lookup.hpp"

#include "database/database.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <sstream>
#endif

std::optional<int32_t> multichannel::findOnlineChannelForPlayer(int32_t playerId) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "SELECT `channel_id` FROM `cluster_sessions` WHERE `player_id` = " << playerId
		  << " AND `status` = 'ONLINE' LIMIT 1;";

	const DBResult_ptr result = db.storeQuery(query.str());
	if (!result) {
		return std::nullopt;
	}

	return result->getNumber<int32_t>("channel_id");
}
