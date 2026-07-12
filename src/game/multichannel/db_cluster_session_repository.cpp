/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/db_cluster_session_repository.hpp"

#include "database/database.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <sstream>
#endif

bool DbClusterSessionRepository::recordAcquire(int32_t accountId, int32_t playerId, int32_t channelId, const std::string &instanceId, const std::string &sessionId, uint64_t fencingToken, int64_t acquiredAtMs, int64_t expiresAtMs) {
	Database &db = Database::getInstance();

	// Clear any *other* account's row for this exact player_id first. In
	// practice player_id -> account_id never changes (a character always
	// belongs to the same account), so this should always be a no-op - but
	// verified against a real MariaDB: without this step, an INSERT that
	// collides only on `cluster_sessions_player_unique` (not the
	// account_id PRIMARY KEY) makes `ON DUPLICATE KEY UPDATE` silently
	// rewrite the *other* account's row's session/channel columns while
	// leaving its account_id untouched - a corrupted, internally
	// inconsistent row instead of a clean error. This DELETE makes the
	// INSERT below only ever collide on account_id, which is safe.
	std::ostringstream clearStalePlayerQuery;
	clearStalePlayerQuery << "DELETE FROM `cluster_sessions` WHERE `player_id` = " << playerId << " AND `account_id` != " << accountId;
	db.executeQuery(clearStalePlayerQuery.str());

	std::ostringstream query;
	query << "INSERT INTO `cluster_sessions` (`account_id`, `player_id`, `channel_id`, `instance_id`, `session_id`, `fencing_token`, `status`, `acquired_at`, `last_heartbeat`, `expires_at`) VALUES ("
		  << accountId << ", "
		  << playerId << ", "
		  << channelId << ", "
		  << db.escapeString(instanceId) << ", "
		  << db.escapeString(sessionId) << ", "
		  << fencingToken << ", "
		  << "'ONLINE', "
		  << acquiredAtMs << ", "
		  << acquiredAtMs << ", "
		  << expiresAtMs
		  << ") ON DUPLICATE KEY UPDATE "
		  << "`player_id` = VALUES(`player_id`), "
		  << "`channel_id` = VALUES(`channel_id`), "
		  << "`instance_id` = VALUES(`instance_id`), "
		  << "`session_id` = VALUES(`session_id`), "
		  << "`fencing_token` = VALUES(`fencing_token`), "
		  << "`status` = VALUES(`status`), "
		  << "`acquired_at` = VALUES(`acquired_at`), "
		  << "`last_heartbeat` = VALUES(`last_heartbeat`), "
		  << "`expires_at` = VALUES(`expires_at`)";

	return db.executeQuery(query.str());
}

bool DbClusterSessionRepository::recordHeartbeat(int32_t accountId, const std::string &sessionId, uint64_t fencingToken, int64_t lastHeartbeatMs, int64_t expiresAtMs) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "UPDATE `cluster_sessions` SET `status` = 'ONLINE', `fencing_token` = " << fencingToken
		  << ", `last_heartbeat` = " << lastHeartbeatMs
		  << ", `expires_at` = " << expiresAtMs
		  << " WHERE `account_id` = " << accountId
		  << " AND `session_id` = " << db.escapeString(sessionId);

	return db.executeQuery(query.str());
}

bool DbClusterSessionRepository::recordRelease(int32_t accountId, const std::string &sessionId) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "DELETE FROM `cluster_sessions` WHERE `account_id` = " << accountId
		  << " AND `session_id` = " << db.escapeString(sessionId);

	return db.executeQuery(query.str());
}
