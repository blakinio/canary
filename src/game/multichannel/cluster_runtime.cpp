/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_runtime.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <tuple>
#endif

ClusterRuntime &ClusterRuntime::getInstance() {
	static ClusterRuntime instance;
	return instance;
}

void ClusterRuntime::configure(std::shared_ptr<IRedisClient> client, int32_t newChannelId, std::string newInstanceId, int64_t newLeaseTtlMs, int64_t newHeartbeatIntervalMs, int64_t newFailureGracePeriodMs, std::shared_ptr<IClusterSessionRepository> newSessionRepository) {
	std::lock_guard lock(mutex);
	redisClient = std::move(client);
	sessionManager = std::make_unique<ClusterSessionManager>(*redisClient);
	sessionRepository = std::move(newSessionRepository);
	channelId = newChannelId;
	instanceId = std::move(newInstanceId);
	leaseTtlMs = newLeaseTtlMs;
	heartbeatIntervalMs = newHeartbeatIntervalMs;
	failureGracePeriodMs = newFailureGracePeriodMs;
	tracked.clear();
	enabled = true;
}

void ClusterRuntime::resetForTesting() {
	std::lock_guard lock(mutex);
	redisClient.reset();
	sessionManager.reset();
	sessionRepository.reset();
	tracked.clear();
	enabled = false;
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

	// Fail closed for *new* sessions the instant Redis looks unhealthy - no
	// grace period here, per docs/multichannel/OPERATIONS.md "Redis outage"
	// step 2. Do not even attempt the call: acquire() would either time out
	// (slow) or, if it somehow "succeeded" against a half-broken connection,
	// hand out a session this process cannot safely renew later.
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
	// Best-effort: a failed release (e.g. Redis unreachable at the exact
	// moment of logout) still removes local tracking, since this process is
	// giving up the player either way (it's disconnecting). The lease's own
	// TTL in Redis is what protects against a stale entry outliving it -
	// see redis_scripts/acquire.lua's PEXPIRE belt-and-suspenders.
	std::ignore = sessionManager->release(accountId, it->second.sessionId);
	if (sessionRepository) {
		std::ignore = sessionRepository->recordRelease(accountId, it->second.sessionId);
	}
	tracked.erase(it);
}

std::vector<int32_t> ClusterRuntime::renewAllAndCollectExpired(int64_t nowMs) {
	std::lock_guard lock(mutex);
	std::vector<int32_t> expired;
	if (!enabled || tracked.empty()) {
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
