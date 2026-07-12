/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/cluster_session_repository.hpp"

// Real, database-backed IClusterSessionRepository. See
// docs/multichannel/ARCHITECTURE.md §5 - this is the defense-in-depth
// counterpart to the Redis-backed ClusterSessionManager, not a
// replacement for it.
class DbClusterSessionRepository final : public IClusterSessionRepository {
public:
	bool recordAcquire(int32_t accountId, int32_t playerId, int32_t channelId, const std::string &instanceId, const std::string &sessionId, uint64_t fencingToken, int64_t acquiredAtMs, int64_t expiresAtMs) override;
	bool recordHeartbeat(int32_t accountId, const std::string &sessionId, uint64_t fencingToken, int64_t lastHeartbeatMs, int64_t expiresAtMs) override;
	bool recordRelease(int32_t accountId, const std::string &sessionId) override;
};
