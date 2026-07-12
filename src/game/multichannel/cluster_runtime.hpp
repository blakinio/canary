/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/cluster_session_manager.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <memory>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <unordered_map>
	#include <vector>
#endif

class ClusterRuntime {
public:
	static ClusterRuntime &getInstance();

	ClusterRuntime(const ClusterRuntime &) = delete;
	ClusterRuntime &operator=(const ClusterRuntime &) = delete;

	void configure(std::shared_ptr<IRedisClient> client, int32_t channelId, std::string instanceId, int64_t leaseTtlMs, int64_t heartbeatIntervalMs, int64_t failureGracePeriodMs);
	void resetForTesting();

	[[nodiscard]] bool isEnabled() const;
	[[nodiscard]] bool isAcceptingNewSessions() const;

	ClusterSessionHandle acquireForLogin(int32_t accountId, int32_t channelId, int64_t nowMs);
	void releaseForLogout(int32_t accountId, int64_t nowMs);

	// Renews session leases and, in the same cluster cycle, publishes this
	// process's channel heartbeat, refreshes the fail-closed runtime snapshot,
	// and queues the diagnostic DB mirror write.
	std::vector<int32_t> renewAllAndCollectExpired(int64_t nowMs);

	[[nodiscard]] std::size_t trackedCount() const;

	struct TrackedSessionInfo {
		std::string sessionId;
		uint64_t fencingToken = 0;
	};

	[[nodiscard]] std::optional<TrackedSessionInfo> getTrackedSessionInfo(int32_t accountId) const;

private:
	ClusterRuntime() = default;

	struct TrackedSession {
		std::string sessionId;
		uint64_t fencingToken = 0;
		int64_t expiresAtMs = 0;
	};

	mutable std::mutex mutex;
	std::shared_ptr<IRedisClient> redisClient;
	std::unique_ptr<ClusterSessionManager> sessionManager;
	int32_t channelId = 0;
	std::string instanceId;
	int64_t leaseTtlMs = 30000;
	int64_t heartbeatIntervalMs = 5000;
	int64_t failureGracePeriodMs = 10000;
	int64_t runtimeStartedAtMs = 0;
	bool enabled = false;

	std::unordered_map<int32_t, TrackedSession> tracked;
};

constexpr auto g_clusterRuntime = ClusterRuntime::getInstance;
