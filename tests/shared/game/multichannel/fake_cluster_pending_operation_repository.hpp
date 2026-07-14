/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/cluster_pending_operation_repository.hpp"

#include <algorithm>
#include <mutex>
#include <unordered_map>

// In-memory model of the `cluster_pending_operations` table's
// PRIMARY KEY(operation_id) idempotency contract, used to unit-test
// ClusterRecordHandoff without a live database. Mirrors
// FakeClusterSessionRepository's role for cluster_sessions.
class FakeClusterPendingOperationRepository : public IClusterPendingOperationRepository {
public:
	bool enqueue(const ClusterPendingOperationRecord &record) override {
		std::lock_guard lock(mutex);
		if (!nextEnqueueSucceeds) {
			return false;
		}
		if (rows.contains(record.operationId)) {
			// PRIMARY KEY(operation_id) rejection - the real DB's identical
			// replay-protection behavior.
			return false;
		}
		rows[record.operationId] = record;
		return true;
	}

	bool markApplied(const std::string &operationId, int64_t nowMs) override {
		return transition(operationId, ClusterPendingOperationStatus::Applied, nowMs, "");
	}

	bool markFailed(const std::string &operationId, int64_t nowMs, const std::string &reason) override {
		return transition(operationId, ClusterPendingOperationStatus::Failed, nowMs, reason);
	}

	bool markAbandoned(const std::string &operationId, int64_t nowMs, const std::string &reason) override {
		return transition(operationId, ClusterPendingOperationStatus::Abandoned, nowMs, reason);
	}

	std::vector<ClusterPendingOperationRecord> findPendingForRecord(const std::string &recordKind, int32_t recordId) override {
		std::lock_guard lock(mutex);
		std::vector<ClusterPendingOperationRecord> result;
		for (const auto &[id, record] : rows) {
			if (record.recordKind == recordKind && record.recordId == recordId && record.status == ClusterPendingOperationStatus::Pending) {
				result.push_back(record);
			}
		}
		sortByCreatedAt(result);
		return result;
	}

	std::vector<ClusterPendingOperationRecord> findPendingForKind(const std::string &recordKind, int32_t limit) override {
		std::lock_guard lock(mutex);
		std::vector<ClusterPendingOperationRecord> result;
		for (const auto &[id, record] : rows) {
			if (record.recordKind == recordKind && record.status == ClusterPendingOperationStatus::Pending) {
				result.push_back(record);
			}
		}
		sortByCreatedAt(result);
		if (static_cast<int32_t>(result.size()) > limit) {
			result.resize(static_cast<std::size_t>(limit));
		}
		return result;
	}

	int64_t countStalePending(int64_t nowMs, int64_t staleWarningMs) override {
		std::lock_guard lock(mutex);
		int64_t count = 0;
		for (const auto &[id, record] : rows) {
			if (record.status == ClusterPendingOperationStatus::Pending && record.createdAtMs < nowMs - staleWarningMs) {
				++count;
			}
		}
		return count;
	}

	// Test-only introspection and failure injection.
	[[nodiscard]] std::optional<ClusterPendingOperationRecord> findByIdForTesting(const std::string &operationId) const {
		std::lock_guard lock(mutex);
		const auto it = rows.find(operationId);
		if (it == rows.end()) {
			return std::nullopt;
		}
		return it->second;
	}

	[[nodiscard]] std::size_t rowCountForTesting() const {
		std::lock_guard lock(mutex);
		return rows.size();
	}

	void setNextEnqueueSucceedsForTesting(bool value) {
		std::lock_guard lock(mutex);
		nextEnqueueSucceeds = value;
	}

private:
	bool transition(const std::string &operationId, ClusterPendingOperationStatus newStatus, int64_t nowMs, const std::string &reason) {
		std::lock_guard lock(mutex);
		const auto it = rows.find(operationId);
		if (it == rows.end() || it->second.status != ClusterPendingOperationStatus::Pending) {
			return false;
		}
		it->second.status = newStatus;
		it->second.appliedAtMs = nowMs;
		it->second.lastError = reason;
		++it->second.attempts;
		return true;
	}

	static void sortByCreatedAt(std::vector<ClusterPendingOperationRecord> &records) {
		std::sort(records.begin(), records.end(), [](const auto &a, const auto &b) {
			return a.createdAtMs < b.createdAtMs;
		});
	}

	mutable std::mutex mutex;
	std::unordered_map<std::string, ClusterPendingOperationRecord> rows;
	bool nextEnqueueSucceeds = true;
};
