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
#include "game/multichannel/cluster_session_repository.hpp"

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

	// Must be called once at startup, only when multiChannelEnabled is true
	// (see CanaryServer::initializeMultichannelCluster). A default-
	// constructed (unconfigured) ClusterRuntime always reports isEnabled()
	// == false and every operation is a safe no-op, so call sites that run
	// unconditionally (e.g. Player::onRemoveCreature) never need their own
	// multiChannelEnabled check.
	//
	// sessionRepository is the `cluster_sessions` DB defense-in-depth layer
	// (docs/multichannel/ARCHITECTURE.md §5) - optional (nullptr skips it
	// entirely, e.g. in unit tests) but should always be provided in
	// production; see DbClusterSessionRepository.
	void configure(std::shared_ptr<IRedisClient> client, int32_t channelId, std::string instanceId, int64_t leaseTtlMs, int64_t heartbeatIntervalMs, int64_t failureGracePeriodMs, std::shared_ptr<IClusterSessionRepository> sessionRepository = nullptr);

	// Test-only hook mirroring ChannelRegistry::setChannelsForTesting.
	void resetForTesting();

	[[nodiscard]] bool isEnabled() const;
	[[nodiscard]] bool isAcceptingNewSessions() const;

	// Attempts to acquire the account-wide lease for a fresh login. Returns
	// the handle as-is (acquired == false means "already online elsewhere",
	// the caller must reject the login with a clear message) - unless Redis
	// itself is unreachable, in which case this returns a not-acquired
	// handle immediately without even attempting the call, consistent with
	// isAcceptingNewSessions() being fail-closed. If a sessionRepository is
	// configured and its write fails, the just-acquired Redis lease is
	// released and a not-acquired handle is returned too - the
	// defense-in-depth layer failing to persist is treated the same as
	// Redis refusing the lease in the first place.
	ClusterSessionHandle acquireForLogin(int32_t accountId, int32_t playerId, int32_t channelId, int64_t nowMs);

	// Clean logout: releases the lease and stops tracking the account. Safe
	// to call even if the account was never tracked (no-op).
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
	std::shared_ptr<IClusterSessionRepository> sessionRepository;
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
