/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/redis_client.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <string>
#endif

struct LeaderElectionHandle {
	bool acquired = false;
	std::string sessionId;
	uint64_t fencingToken = 0;
	// Set when acquired == false: describes who currently holds the lease,
	// so the caller can report a meaningful "<channel/instance X> is already
	// running this job" message instead of a bare rejection.
	std::string currentHolderSessionId;
	uint64_t currentHolderFencingToken = 0;
};

// Leader election for cluster-singleton background jobs (docs/multichannel/
// OPERATIONS.md "Leader election / cluster-singleton jobs"): exactly one
// channel process may run a given singleton job (house rent charging,
// market offer expiration, daily reward reset, ...) at a time, cluster-wide.
// Reuses the exact same atomic Redis lease/fencing primitive as
// ClusterSessionManager (docs/multichannel/ARCHITECTURE.md §5) - same Lua CAS
// scripts (src/game/multichannel/redis_scripts/), same IRedisClient seam -
// since "exactly one holder, atomic takeover, monotonic fencing token" is
// exactly the leader-election contract too; only the identity being locked
// differs (a job name instead of an account id). Unlike a player session, a
// job leader has no multi-state lifecycle (Acquiring/Saving/Dirty): either
// this process currently holds the lease or it doesn't, and a job run must
// call isFencingTokenCurrent immediately before any side effect that must
// not run twice (same anti-zombie pattern as THREAT_MODEL.md T2) - if the
// token has moved on, this process must skip the run rather than execute it.
//
// This class implements the primitive only. Wiring specific jobs (market
// expiry, house rent, daily reward reset, ...) to actually call
// acquire/renew/isFencingTokenCurrent around their existing logic is left for
// a follow-up - see docs/multichannel/OPERATIONS.md's job inventory table.
class ClusterLeaderElection {
public:
	explicit ClusterLeaderElection(IRedisClient &client) :
		redisClient(client) { }

	ClusterLeaderElection(const ClusterLeaderElection &) = delete;
	ClusterLeaderElection &operator=(const ClusterLeaderElection &) = delete;

	// Attempts to become the leader for jobName. On success, the returned
	// handle's fencingToken is the new, strictly greater-than-before token
	// for this job name. On failure, acquired is false and
	// currentHolderSessionId/currentHolderFencingToken describe the existing
	// leader.
	[[nodiscard]] LeaderElectionHandle acquire(const std::string &jobName, int32_t channelId, const std::string &instanceId, int64_t ttlMs, int64_t nowMs);

	// Renews an already-acquired leadership lease. Returns false (and the
	// caller must treat itself as no longer the leader) if sessionId is not
	// the current holder or the lease had already expired - never silently
	// resurrects a lost lease.
	[[nodiscard]] bool renew(const std::string &jobName, const std::string &sessionId, int64_t ttlMs, int64_t nowMs);

	// Releases an already-acquired leadership lease (e.g. graceful shutdown,
	// or voluntarily stepping down). Returns false if sessionId is not the
	// current holder.
	[[nodiscard]] bool release(const std::string &jobName, const std::string &sessionId);

	// True if fencingToken is still the current token for jobName. A
	// singleton job run must check this immediately before performing any
	// effect that must not happen twice, and must skip the run (not merge or
	// retry) if the token is stale - see THREAT_MODEL.md T2.
	[[nodiscard]] bool isFencingTokenCurrent(const std::string &jobName, uint64_t fencingToken);

	[[nodiscard]] static std::string makeLockKey(const std::string &jobName);

private:
	IRedisClient &redisClient;
};
