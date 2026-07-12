/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_runtime.hpp"

#include "database/database.hpp"
#include "database/databasetasks.hpp"
#include "game/multichannel/channel_registry.hpp"
#include "game/multichannel/channel_runtime_registry.hpp"
#include "lib/logging/log_with_spd_log.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <cstdlib>
	#include <sstream>
	#include <tuple>
#endif

namespace {
	int64_t wallClockMs() {
		return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
	}

	std::string environmentOr(const char* name, std::string fallback) {
		const char* value = std::getenv(name);
		if (value && *value != '\0') {
			return value;
		}
		return fallback;
	}

#ifndef BUILD_TESTS
	void queueRuntimeStatusMirror(const ChannelRuntimeStatus &status) {
		Database &db = Database::getInstance();
		std::ostringstream query;
		query << "INSERT INTO `channel_runtime_status` (`channel_id`, `instance_id`, `node_id`, `started_at`, `last_heartbeat`, `status`, `players_online`, `build_sha`, `map_hash`, `data_hash`) VALUES ("
			  << status.channelId << ", "
			  << db.escapeString(status.instanceId) << ", "
			  << db.escapeString(status.nodeId) << ", "
			  << status.startedAtMs << ", "
			  << status.lastHeartbeatMs << ", "
			  << db.escapeString(status.status) << ", "
			  << status.playersOnline << ", "
			  << db.escapeString(status.buildSha) << ", "
			  << db.escapeString(status.mapHash) << ", "
			  << db.escapeString(status.dataHash)
			  << ") ON DUPLICATE KEY UPDATE "
			  << "`instance_id` = VALUES(`instance_id`), `node_id` = VALUES(`node_id`), `started_at` = VALUES(`started_at`), "
			  << "`last_heartbeat` = VALUES(`last_heartbeat`), `status` = VALUES(`status`), `players_online` = VALUES(`players_online`), "
			  << "`build_sha` = VALUES(`build_sha`), `map_hash` = VALUES(`map_hash`), `data_hash` = VALUES(`data_hash`);";

		g_databaseTasks().execute(query.str(), [channelId = status.channelId](DBResult_ptr, bool success) {
			if (!success) {
				g_logger().error("[multichannel] Failed to update channel_runtime_status mirror for channel {}.", channelId);
			}
		});
	}
#endif
} // namespace

ClusterRuntime &ClusterRuntime::getInstance() {
	static ClusterRuntime instance;
	return instance;
}

void ClusterRuntime::configure(std::shared_ptr<IRedisClient> client, int32_t newChannelId, std::string newInstanceId, int64_t newLeaseTtlMs, int64_t newHeartbeatIntervalMs, int64_t newFailureGracePeriodMs, std::shared_ptr<IClusterSessionRepository> newSessionRepository) {
	const auto runtimeClient = client;
	{
		std::lock_guard lock(mutex);
		redisClient = std::move(client);
		sessionManager = std::make_unique<ClusterSessionManager>(*redisClient);
		sessionRepository = std::move(newSessionRepository);
		channelId = newChannelId;
		instanceId = std::move(newInstanceId);
		leaseTtlMs = newLeaseTtlMs;
		heartbeatIntervalMs = newHeartbeatIntervalMs;
		failureGracePeriodMs = newFailureGracePeriodMs;
		runtimeStartedAtMs = wallClockMs();
		tracked.clear();
		enabled = true;
	}
	g_channelRuntimeRegistry().configure(runtimeClient, newLeaseTtlMs);
}

void ClusterRuntime::resetForTesting() {
	{
		std::lock_guard lock(mutex);
		redisClient.reset();
		sessionManager.reset();
		sessionRepository.reset();
		tracked.clear();
		runtimeStartedAtMs = 0;
		enabled = false;
	}
	g_channelRuntimeRegistry().resetForTesting();
}

bool ClusterRuntime::isEnabled() const {
	std::lock_guard lock(mutex);
	return enabled;
}

bool ClusterRuntime::isAcceptingNewSessions() const {
	std::lock_guard lock(mutex);
	if (!enabled) {
		return true;
	}
	return redisClient->isHealthy();
}

ClusterSessionHandle ClusterRuntime::acquireForLogin(int32_t accountId, int32_t playerId, int32_t forChannelId, int64_t nowMs) {
	std::lock_guard lock(mutex);
	if (!enabled) {
		ClusterSessionHandle handle;
		handle.acquired = true;
		handle.status = ClusterSessionStatus::Online;
		return handle;
	}

	if (!redisClient->isHealthy()) {
		ClusterSessionHandle handle;
		handle.acquired = false;
		handle.status = ClusterSessionStatus::Offline;
		return handle;
	}

	auto handle = sessionManager->acquire(accountId, forChannelId, instanceId, leaseTtlMs, nowMs);
	if (!handle.acquired) {
		return handle;
	}

	const int64_t expiresAtMs = nowMs + leaseTtlMs;
	if (sessionRepository && !sessionRepository->recordAcquire(accountId, playerId, forChannelId, instanceId, handle.sessionId, handle.fencingToken, nowMs, expiresAtMs)) {
		// The defense-in-depth layer could not persist this lease - do not
		// hand out a session the database side disputes. Release the Redis
		// lease we just took so a later attempt (by this process or another)
		// is not blocked by a lease nothing actually recorded.
		std::ignore = sessionManager->release(accountId, handle.sessionId);
		ClusterSessionHandle failed;
		failed.acquired = false;
		failed.status = ClusterSessionStatus::Offline;
		return failed;
	}

	tracked[accountId] = TrackedSession { handle.sessionId, handle.fencingToken, expiresAtMs };
	return handle;
}

void ClusterRuntime::releaseForLogout(int32_t accountId, int64_t /*nowMs*/) {
	std::lock_guard lock(mutex);
	if (!enabled) {
		return;
	}
	const auto it = tracked.find(accountId);
	if (it == tracked.end()) {
		return;
	}
	std::ignore = sessionManager->release(accountId, it->second.sessionId);
	if (sessionRepository) {
		std::ignore = sessionRepository->recordRelease(accountId, it->second.sessionId);
	}
	tracked.erase(it);
}

std::vector<int32_t> ClusterRuntime::renewAllAndCollectExpired(int64_t nowMs) {
	std::vector<int32_t> expired;
	ChannelRuntimeStatus ownStatus;
	int64_t runtimeTtlMs = 0;
	const int64_t runtimeNowMs = wallClockMs();

	{
		std::lock_guard lock(mutex);
		if (!enabled) {
			return expired;
		}

		for (auto it = tracked.begin(); it != tracked.end();) {
			const int32_t accountId = it->first;
			auto &session = it->second;

			const bool renewed = sessionManager->renew(accountId, session.sessionId, leaseTtlMs, nowMs);
			if (renewed) {
				session.expiresAtMs = nowMs + leaseTtlMs;
				if (sessionRepository) {
					// Best-effort, matching the mirror-not-gate posture used
					// elsewhere: a transient DB hiccup during a routine
					// heartbeat must not force-disconnect a player whose Redis
					// lease (the fast path, already confirmed above) is fine.
					std::ignore = sessionRepository->recordHeartbeat(accountId, session.sessionId, session.fencingToken, nowMs, session.expiresAtMs);
				}
				++it;
				continue;
			}

			if (redisClient->isHealthy()) {
				// Redis answered fine and still said no: this session was
				// legitimately superseded (someone else now holds the lease,
				// or it had already expired on Redis's own clock). There is no
				// grace period for a real supersession - relinquish now.
				expired.push_back(accountId);
				it = tracked.erase(it);
				continue;
			}

			// Redis is unreachable (isHealthy() above just came back false for
			// this account's renew attempt). Keep playing locally, but only up
			// to whichever comes first: the configured failure grace period
			// since this lease was last genuinely renewed, or this lease's own
			// remaining validity running out (leaving no margin for one more
			// renew attempt before another process could legally steal it) -
			// see OPERATIONS.md "Redis outage" steps 3-4.
			const int64_t lastRenewedAtMs = session.expiresAtMs - leaseTtlMs;
			const bool pastGracePeriod = (nowMs - lastRenewedAtMs) >= failureGracePeriodMs;
			const bool lastChanceBeforeExpiry = nowMs >= (session.expiresAtMs - heartbeatIntervalMs);
			if (pastGracePeriod || lastChanceBeforeExpiry) {
				// This process is relinquishing the account before anyone else
				// can legally take over - unlike the supersession branch above,
				// nothing has overwritten the DB row yet, so it must be cleared
				// here (a database write, a separate failure domain from the
				// Redis outage this branch exists for). Leaving a stale ONLINE
				// row behind would eventually block every future login for this
				// account once Redis recovers - worse than the row simply not
				// existing.
				if (sessionRepository) {
					std::ignore = sessionRepository->recordRelease(accountId, session.sessionId);
				}
				expired.push_back(accountId);
				it = tracked.erase(it);
				continue;
			}

			++it;
		}

		ownStatus.channelId = channelId;
		ownStatus.instanceId = instanceId;
		ownStatus.startedAtMs = runtimeStartedAtMs;
		ownStatus.lastHeartbeatMs = runtimeNowMs;
		ownStatus.playersOnline = static_cast<int32_t>(tracked.size());
		runtimeTtlMs = leaseTtlMs;
	}

	const auto channels = g_channelRegistry().getAllChannels();
	std::vector<int32_t> channelIds;
	channelIds.reserve(channels.size());
	for (const auto &channel : channels) {
		channelIds.push_back(channel.id);
		if (channel.id == ownStatus.channelId) {
			ownStatus.status = channel.maintenance ? "MAINTENANCE" : "ONLINE";
			ownStatus.nodeId = environmentOr("CANARY_NODE_ID", channel.externalHost);
			ownStatus.mapHash = environmentOr("CANARY_MAP_HASH", channel.mapHash.empty() ? "unknown" : channel.mapHash);
		}
	}

	if (ownStatus.nodeId.empty()) {
		ownStatus.nodeId = environmentOr("CANARY_NODE_ID", "unknown");
	}
	if (ownStatus.mapHash.empty()) {
		ownStatus.mapHash = environmentOr("CANARY_MAP_HASH", "unknown");
	}
	ownStatus.buildSha = environmentOr("CANARY_BUILD_SHA", "unknown");
	ownStatus.dataHash = environmentOr("CANARY_DATA_HASH", "unknown");

	const bool heartbeatPublished = g_channelRuntimeRegistry().publishAndRefresh(ownStatus, runtimeTtlMs, channelIds, runtimeNowMs);
	if (!heartbeatPublished) {
		g_logger().error("[multichannel] Channel {} heartbeat publication/refresh failed; runtime availability cache was cleared (fail-closed).", ownStatus.channelId);
	}

#ifndef BUILD_TESTS
	queueRuntimeStatusMirror(ownStatus);
#endif
	return expired;
}

std::size_t ClusterRuntime::trackedCount() const {
	std::lock_guard lock(mutex);
	return tracked.size();
}

std::optional<ClusterRuntime::TrackedSessionInfo> ClusterRuntime::getTrackedSessionInfo(int32_t accountId) const {
	std::lock_guard lock(mutex);
	const auto it = tracked.find(accountId);
	if (it == tracked.end()) {
		return std::nullopt;
	}
	return TrackedSessionInfo { it->second.sessionId, it->second.fencingToken };
}
