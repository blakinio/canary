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

#include <mutex>
#include <unordered_map>

// In-memory model of the `cluster_sessions` table's PRIMARY KEY(account_id)
// + UNIQUE(player_id) constraints, used to unit-test ClusterRuntime's
// defense-in-depth wiring without a live database. Mirrors
// FakeRedisClient's role for the Redis side.
class FakeClusterSessionRepository : public IClusterSessionRepository {
public:
	struct Row {
		int32_t playerId = 0;
		int32_t channelId = 0;
		std::string instanceId;
		std::string sessionId;
		uint64_t fencingToken = 0;
		int64_t acquiredAtMs = 0;
		int64_t lastHeartbeatMs = 0;
		int64_t expiresAtMs = 0;
	};

	bool recordAcquire(int32_t accountId, int32_t playerId, int32_t channelId, const std::string &instanceId, const std::string &sessionId, uint64_t fencingToken, int64_t acquiredAtMs, int64_t expiresAtMs) override {
		std::lock_guard lock(mutex);
		if (!nextAcquireSucceeds) {
			return false;
		}
		// Mirror the real table's UNIQUE(player_id): a different account
		// already holding this exact player_id is a real conflict, not
		// something an upsert on account_id alone can resolve away.
		for (const auto &[existingAccountId, row] : rows) {
			if (existingAccountId != accountId && row.playerId == playerId) {
				return false;
			}
		}
		rows[accountId] = Row { playerId, channelId, instanceId, sessionId, fencingToken, acquiredAtMs, acquiredAtMs, expiresAtMs };
		return true;
	}

	bool recordHeartbeat(int32_t accountId, const std::string &sessionId, uint64_t fencingToken, int64_t lastHeartbeatMs, int64_t expiresAtMs) override {
		std::lock_guard lock(mutex);
		const auto it = rows.find(accountId);
		if (it == rows.end() || it->second.sessionId != sessionId) {
			return false;
		}
		it->second.fencingToken = fencingToken;
		it->second.lastHeartbeatMs = lastHeartbeatMs;
		it->second.expiresAtMs = expiresAtMs;
		return true;
	}

	bool recordRelease(int32_t accountId, const std::string &sessionId) override {
		std::lock_guard lock(mutex);
		const auto it = rows.find(accountId);
		if (it == rows.end() || it->second.sessionId != sessionId) {
			return false;
		}
		rows.erase(it);
		return true;
	}

	// Test-only introspection and failure injection.
	[[nodiscard]] bool hasRow(int32_t accountId) const {
		std::lock_guard lock(mutex);
		return rows.contains(accountId);
	}

	[[nodiscard]] std::size_t rowCount() const {
		std::lock_guard lock(mutex);
		return rows.size();
	}

	void setNextAcquireSucceedsForTesting(bool value) {
		std::lock_guard lock(mutex);
		nextAcquireSucceeds = value;
	}

private:
	mutable std::mutex mutex;
	std::unordered_map<int32_t, Row> rows;
	bool nextAcquireSucceeds = true;
};
