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

#include <mutex>
#include <unordered_map>

// In-memory model of the Redis CAS and runtime-heartbeat semantics. Logical
// timestamps are supplied by tests, so expiry/race behavior is deterministic.
class FakeRedisClient : public IRedisClient {
public:
	LeaseAcquireOutcome acquireLease(const std::string &lockKey, const std::string &sessionId, const std::string &channelId, const std::string &instanceId, int64_t ttlMs, int64_t nowMs) override {
		std::lock_guard lock(mutex);
		if (!healthy) {
			return {};
		}
		auto &entry = entries[lockKey];

		if (entry.expiresAt > nowMs) {
			return { false, entry.sessionId, entry.fencingToken };
		}

		entry.fencingToken += 1;
		entry.sessionId = sessionId;
		entry.channelId = channelId;
		entry.instanceId = instanceId;
		entry.expiresAt = nowMs + ttlMs;

		return { true, entry.sessionId, entry.fencingToken };
	}

	LeaseRenewOutcome renewLease(const std::string &lockKey, const std::string &sessionId, int64_t ttlMs, int64_t nowMs) override {
		std::lock_guard lock(mutex);
		if (!healthy) {
			return {};
		}
		const auto it = entries.find(lockKey);
		if (it == entries.end() || it->second.sessionId != sessionId) {
			return { false, 0 };
		}
		if (it->second.expiresAt <= nowMs) {
			return { false, 0 };
		}
		it->second.expiresAt = nowMs + ttlMs;
		return { true, it->second.fencingToken };
	}

	bool releaseLease(const std::string &lockKey, const std::string &sessionId) override {
		std::lock_guard lock(mutex);
		if (!healthy) {
			return false;
		}
		const auto it = entries.find(lockKey);
		if (it == entries.end() || it->second.sessionId != sessionId) {
			return false;
		}
		it->second.expiresAt = 0;
		return true;
	}

	std::optional<uint64_t> peekFencingToken(const std::string &lockKey) override {
		std::lock_guard lock(mutex);
		if (!healthy) {
			return std::nullopt;
		}
		const auto it = entries.find(lockKey);
		if (it == entries.end()) {
			return std::nullopt;
		}
		return it->second.fencingToken;
	}

	bool writeChannelRuntimeStatus(const std::string &runtimeKey, const ChannelRuntimeStatus &status, int64_t ttlMs, int64_t nowMs) override {
		std::lock_guard lock(mutex);
		if (!healthy || ttlMs <= 0 || status.channelId <= 0 || !status.hasValidState()) {
			return false;
		}
		runtimeEntries[runtimeKey] = RuntimeEntry { status, nowMs + ttlMs };
		return true;
	}

	std::optional<ChannelRuntimeStatus> readChannelRuntimeStatus(const std::string &runtimeKey, int64_t nowMs) override {
		std::lock_guard lock(mutex);
		if (!healthy) {
			return std::nullopt;
		}
		const auto it = runtimeEntries.find(runtimeKey);
		if (it == runtimeEntries.end()) {
			return std::nullopt;
		}
		if (it->second.expiresAtMs <= nowMs) {
			runtimeEntries.erase(it);
			return std::nullopt;
		}
		return it->second.status;
	}

	[[nodiscard]] bool isHealthy() const override {
		std::lock_guard lock(mutex);
		return healthy;
	}

	[[nodiscard]] RedisPingResult ping() override {
		std::lock_guard lock(mutex);
		RedisPingResult result;
		if (healthy) {
			result.outcome = RedisPingOutcome::Success;
		} else {
			result.outcome = pingFailureOutcome;
			result.detail = "FakeRedisClient: healthy=false (see setHealthyForTesting/setPingFailureOutcomeForTesting)";
		}
		return result;
	}

	void setHealthyForTesting(bool value) {
		std::lock_guard lock(mutex);
		healthy = value;
	}

	// Only consulted by ping() while healthy == false; every other method's
	// failure behavior is controlled by setHealthyForTesting alone, matching
	// the existing convention in this fake.
	void setPingFailureOutcomeForTesting(RedisPingOutcome outcome) {
		std::lock_guard lock(mutex);
		pingFailureOutcome = outcome;
	}

private:
	struct Entry {
		std::string sessionId;
		std::string channelId;
		std::string instanceId;
		uint64_t fencingToken = 0;
		int64_t expiresAt = 0;
	};

	struct RuntimeEntry {
		ChannelRuntimeStatus status;
		int64_t expiresAtMs = 0;
	};

	mutable std::mutex mutex;
	std::unordered_map<std::string, Entry> entries;
	std::unordered_map<std::string, RuntimeEntry> runtimeEntries;
	bool healthy = true;
	RedisPingOutcome pingFailureOutcome = RedisPingOutcome::Other;
};
