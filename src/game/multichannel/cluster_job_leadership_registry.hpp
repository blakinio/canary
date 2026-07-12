/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/cluster_leader_election.hpp"
#include "game/multichannel/redis_client.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <memory>
	#include <mutex>
	#include <string>
	#include <unordered_map>
#endif

// Redis-backed cache for cluster-singleton job leadership (docs/multichannel/
// OPERATIONS.md "Leader election / cluster-singleton jobs"), built on top of
// ClusterLeaderElection (docs/multichannel/ARCHITECTURE.md §10a). Mirrors
// ChannelRuntimeRegistry's split: the actual Redis acquire/renew work happens
// once per heartbeat cycle via renewOrAcquire(); job call sites only ever
// call the cheap, I/O-free isLeader() to decide whether to run for real.
//
// A Redis outage - like every other multichannel fast path - fails closed:
// renewOrAcquire() immediately stops reporting leadership the first cycle a
// renew fails, rather than optimistically continuing to run a job it can no
// longer prove it still owns (THREAT_MODEL.md T2's anti-zombie reasoning,
// applied here to jobs instead of sessions). Once Redis is reachable again,
// a merely-transient outage recovers cleanly on the next cycle (the
// remembered lease was never actually touched while unreachable); a real
// takeover by another process is not reversed.
class ClusterJobLeadershipRegistry {
public:
	static ClusterJobLeadershipRegistry &getInstance() {
		static ClusterJobLeadershipRegistry instance;
		return instance;
	}

	ClusterJobLeadershipRegistry(const ClusterJobLeadershipRegistry &) = delete;
	ClusterJobLeadershipRegistry &operator=(const ClusterJobLeadershipRegistry &) = delete;

	void configure(std::shared_ptr<IRedisClient> client, int32_t newChannelId, std::string newInstanceId) {
		std::lock_guard lock(mutex);
		redisClient = std::move(client);
		election = redisClient ? std::make_unique<ClusterLeaderElection>(*redisClient) : nullptr;
		channelId = newChannelId;
		instanceId = std::move(newInstanceId);
		jobs.clear();
		enabled = redisClient != nullptr;
	}

	void resetForTesting() {
		std::lock_guard lock(mutex);
		redisClient.reset();
		election.reset();
		jobs.clear();
		enabled = false;
	}

	[[nodiscard]] bool isEnabled() const {
		std::lock_guard lock(mutex);
		return enabled;
	}

	// Renews this process's lease for jobName if it already remembers one
	// (whether or not it currently believes it is the leader), or attempts
	// a fresh acquire as a fallback when there is nothing to renew yet, or
	// the renew above just failed. Intended to be called once per
	// heartbeat cycle per job name this process wants to compete for - see
	// Game::renewClusterSessions.
	//
	// A failed renew deliberately keeps the remembered sessionId instead
	// of discarding it: whether the failure is a transient Redis outage or
	// a real takeover by another process, the remembered id is exactly
	// what a later renew needs to succeed cleanly once - in the
	// outage case - Redis is healthy again and this lease, from Redis's
	// own perspective, was never actually touched while unreachable. The
	// fallback acquire in the same cycle only ever succeeds once any
	// existing lease (ours or someone else's) has genuinely expired.
	void renewOrAcquire(const std::string &jobName, int64_t ttlMs, int64_t nowMs) {
		std::lock_guard lock(mutex);
		if (!enabled) {
			return;
		}

		const auto it = jobs.find(jobName);
		if (it != jobs.end()) {
			if (election->renew(jobName, it->second.sessionId, ttlMs, nowMs)) {
				it->second.currentlyLeader = true;
				return;
			}
			it->second.currentlyLeader = false;
		}

		const auto handle = election->acquire(jobName, channelId, instanceId, ttlMs, nowMs);
		if (handle.acquired) {
			jobs[jobName] = JobLease { handle.sessionId, true };
		}
	}

	// Cheap, I/O-free: true only if this process currently believes it
	// holds the lease for jobName (kept fresh by renewOrAcquire on the
	// heartbeat cycle). Always false while disabled (multiChannelEnabled
	// is false or this registry was never configured), so a single-node
	// deployment's jobs are never gated by this check.
	[[nodiscard]] bool isLeader(const std::string &jobName) const {
		std::lock_guard lock(mutex);
		if (!enabled) {
			return false;
		}
		const auto it = jobs.find(jobName);
		return it != jobs.end() && it->second.currentlyLeader;
	}

private:
	ClusterJobLeadershipRegistry() = default;

	struct JobLease {
		std::string sessionId;
		bool currentlyLeader = false;
	};

	mutable std::mutex mutex;
	std::shared_ptr<IRedisClient> redisClient;
	std::unique_ptr<ClusterLeaderElection> election;
	int32_t channelId = 0;
	std::string instanceId;
	std::unordered_map<std::string, JobLease> jobs;
	bool enabled = false;
};

constexpr auto g_clusterJobLeadershipRegistry = ClusterJobLeadershipRegistry::getInstance;
