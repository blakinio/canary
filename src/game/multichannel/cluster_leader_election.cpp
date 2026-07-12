/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_leader_election.hpp"

#include "game/multichannel/cluster_session_manager.hpp"

LeaderElectionHandle ClusterLeaderElection::acquire(const std::string &jobName, int32_t channelId, const std::string &instanceId, int64_t ttlMs, int64_t nowMs) {
	const std::string lockKey = makeLockKey(jobName);
	// Reuses ClusterSessionManager's session-id generator: it is a generic
	// "unique opaque CAS-ownership tag" helper, not something that only
	// makes sense for player sessions.
	const std::string sessionId = ClusterSessionManager::generateSessionId();

	const auto outcome = redisClient.acquireLease(lockKey, sessionId, std::to_string(channelId), instanceId, ttlMs, nowMs);

	LeaderElectionHandle handle;
	if (outcome.acquired) {
		handle.acquired = true;
		handle.sessionId = outcome.sessionId;
		handle.fencingToken = outcome.fencingToken;
	} else {
		handle.acquired = false;
		handle.currentHolderSessionId = outcome.sessionId;
		handle.currentHolderFencingToken = outcome.fencingToken;
	}
	return handle;
}

bool ClusterLeaderElection::renew(const std::string &jobName, const std::string &sessionId, int64_t ttlMs, int64_t nowMs) {
	const std::string lockKey = makeLockKey(jobName);
	const auto outcome = redisClient.renewLease(lockKey, sessionId, ttlMs, nowMs);
	return outcome.renewed;
}

bool ClusterLeaderElection::release(const std::string &jobName, const std::string &sessionId) {
	const std::string lockKey = makeLockKey(jobName);
	return redisClient.releaseLease(lockKey, sessionId);
}

bool ClusterLeaderElection::isFencingTokenCurrent(const std::string &jobName, uint64_t fencingToken) {
	const auto current = redisClient.peekFencingToken(makeLockKey(jobName));
	return current.has_value() && *current == fencingToken;
}

std::string ClusterLeaderElection::makeLockKey(const std::string &jobName) {
	return "cluster:leader:" + jobName;
}
