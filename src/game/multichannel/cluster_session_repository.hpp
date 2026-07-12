/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <string>
#endif

// Abstraction over the `cluster_sessions` DB table (docs/multichannel/
// ARCHITECTURE.md §5) - the defense-in-depth layer that holds even if
// Redis is wiped, wrong, or bypassed entirely: `PRIMARY KEY(account_id)`
// and `UNIQUE(player_id)` guarantee at most one online character per
// account, cluster-wide, at the database level, independent of whatever
// Redis currently believes. ClusterRuntime calls this alongside (never
// instead of) the Redis-backed ClusterSessionManager, on the same
// acquire/renew/release events.
class IClusterSessionRepository {
public:
	virtual ~IClusterSessionRepository() = default;

	// Upserts the row for accountId (`INSERT ... ON DUPLICATE KEY UPDATE`,
	// matching the same "latest acquire wins" semantics already used for
	// `account_house_ownership`). Returns false on a real DB error (query
	// failure, not merely "a row already existed") - the caller treats that
	// as a hard failure and releases the Redis lease it just acquired,
	// rather than silently proceeding on a lease the defense-in-depth layer
	// could not actually persist.
	virtual bool recordAcquire(int32_t accountId, int32_t playerId, int32_t channelId, const std::string &instanceId, const std::string &sessionId, uint64_t fencingToken, int64_t acquiredAtMs, int64_t expiresAtMs) = 0;

	virtual bool recordHeartbeat(int32_t accountId, const std::string &sessionId, uint64_t fencingToken, int64_t lastHeartbeatMs, int64_t expiresAtMs) = 0;

	virtual bool recordRelease(int32_t accountId, const std::string &sessionId) = 0;
};
