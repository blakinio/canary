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

std::vector<multichannel::ClusterOnlinePlayerEntry> multichannel::listOnlinePlayers() {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "SELECT `cs`.`account_id`, `cs`.`player_id`, `p`.`name`, `cs`.`channel_id` "
		  << "FROM `cluster_sessions` `cs` "
		  << "INNER JOIN `players` `p` ON `p`.`id` = `cs`.`player_id` "
		  << "WHERE `cs`.`status` = 'ONLINE' "
		  << "ORDER BY `cs`.`channel_id` ASC, `p`.`name` ASC;";

	std::vector<ClusterOnlinePlayerEntry> entries;
	const DBResult_ptr result = db.storeQuery(query.str());
	if (!result) {
		return entries;
	}

	do {
		ClusterOnlinePlayerEntry entry;
		entry.accountId = result->getNumber<int32_t>("account_id");
		entry.playerId = result->getNumber<int32_t>("player_id");
		entry.playerName = result->getString("name");
		entry.channelId = result->getNumber<int32_t>("channel_id");
		entries.push_back(std::move(entry));
	} while (result->next());

	return entries;
}

std::optional<multichannel::ClusterSessionLockInfo> multichannel::findSessionLockInfo(int32_t playerId) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "SELECT `account_id`, `player_id`, `channel_id`, `instance_id`, `session_id`, "
			 "`fencing_token`, `status`, `acquired_at`, `last_heartbeat`, `expires_at` "
			 "FROM `cluster_sessions` WHERE `player_id` = "
		  << playerId << " LIMIT 1;";

	const DBResult_ptr result = db.storeQuery(query.str());
	if (!result) {
		return std::nullopt;
	}

	ClusterSessionLockInfo info;
	info.accountId = result->getNumber<int32_t>("account_id");
	info.playerId = result->getNumber<int32_t>("player_id");
	info.channelId = result->getNumber<int32_t>("channel_id");
	info.instanceId = result->getString("instance_id");
	info.sessionId = result->getString("session_id");
	info.fencingToken = result->getNumber<uint64_t>("fencing_token");
	info.status = result->getString("status");
	info.acquiredAtMs = result->getNumber<int64_t>("acquired_at");
	info.lastHeartbeatMs = result->getNumber<int64_t>("last_heartbeat");
	info.expiresAtMs = result->getNumber<int64_t>("expires_at");
	return info;
}
