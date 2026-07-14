/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/cluster_record_handoff.hpp"
#include "game/multichannel/db_cluster_pending_operation_repository.hpp"
#include "game/multichannel/db_cluster_record_ownership_resolver.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <memory>
	#include <mutex>
	#include <optional>
	#include <string>
#endif

// Production singleton wrapper around ClusterRecordHandoff, mirroring
// ClusterRuntime's own getInstance()+configure() shape: ClusterRecordHandoff
// itself takes constructor-injected interface references for unit
// testability (design doc, tests/unit/game/multichannel/
// cluster_record_handoff_test.cpp), so this wrapper owns the real
// DbClusterPendingOperationRepository/DbClusterRecordOwnershipResolver
// instances (both stateless - no Database handle needs to be injected,
// they call Database::getInstance() internally like every other
// multichannel store) and constructs the orchestrator lazily once enabled.
class ClusterHandoffRuntime {
public:
	static ClusterHandoffRuntime &getInstance() {
		static ClusterHandoffRuntime instance;
		return instance;
	}

	ClusterHandoffRuntime(const ClusterHandoffRuntime &) = delete;
	ClusterHandoffRuntime &operator=(const ClusterHandoffRuntime &) = delete;

	// Must be called once at startup, only when multiChannelEnabled is true
	// (mirrors every other multichannel singleton's configure() contract).
	void configure(int32_t channelId) {
		std::lock_guard lock(mutex);
		thisChannelId = channelId;
		if (!handoff) {
			handoff = std::make_unique<ClusterRecordHandoff>(repository, resolver);
		}
		enabled = true;
	}

	void resetForTesting() {
		std::lock_guard lock(mutex);
		handoff.reset();
		thisChannelId = 0;
		enabled = false;
	}

	[[nodiscard]] bool isEnabled() const {
		std::lock_guard lock(mutex);
		return enabled;
	}

	// Enqueues a new operation. Returns false both when the operationId
	// already exists (already enqueued) and on a real repository error -
	// see IClusterPendingOperationRepository::enqueue's identical contract.
	// A safe no-op when not enabled (single-channel mode).
	[[nodiscard]] bool enqueue(const ClusterPendingOperationRecord &record) {
		std::lock_guard lock(mutex);
		if (!enabled || !handoff) {
			return false;
		}
		return handoff->enqueue(record);
	}

	[[nodiscard]] ClusterRecordOwnership resolveOwnership(const std::string &recordKind, int32_t recordId, const std::optional<int32_t> &recordChannelId) {
		std::lock_guard lock(mutex);
		if (!enabled || !handoff) {
			return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::Unknown, 0 };
		}
		return handoff->resolveOwnership(recordKind, recordId, recordChannelId);
	}

	// Intended to run from the existing multichannel heartbeat cycle
	// (Game::renewClusterSessions) - a safe no-op when not enabled.
	int32_t sweep(const std::string &recordKind, int32_t limit, int64_t nowMs, IClusterRecordOperationHandler &handler) {
		std::lock_guard lock(mutex);
		if (!enabled || !handoff) {
			return 0;
		}
		return handoff->sweep(recordKind, thisChannelId, limit, nowMs, handler);
	}

	// Enqueues durably and, when safe, applies immediately - see
	// ClusterRecordHandoff::enqueueAndTryApplyNow. Returns NotEnqueued when
	// not enabled (single-channel mode) - callers must keep their own
	// existing single-process fallback for that case, exactly as
	// Mailbox::sendItem does.
	[[nodiscard]] ClusterRecordHandoffOutcome enqueueAndTryApplyNow(const ClusterPendingOperationRecord &record, int64_t nowMs, IClusterRecordOperationHandler &handler) {
		std::lock_guard lock(mutex);
		if (!enabled || !handoff) {
			return ClusterRecordHandoffOutcome::NotEnqueued;
		}
		return handoff->enqueueAndTryApplyNow(record, thisChannelId, nowMs, handler);
	}

	[[nodiscard]] int32_t getThisChannelId() const {
		std::lock_guard lock(mutex);
		return thisChannelId;
	}

private:
	ClusterHandoffRuntime() = default;

	mutable std::mutex mutex;
	DbClusterPendingOperationRepository repository;
	DbClusterRecordOwnershipResolver resolver;
	std::unique_ptr<ClusterRecordHandoff> handoff;
	int32_t thisChannelId = 0;
	bool enabled = false;
};

constexpr auto g_clusterHandoffRuntime = ClusterHandoffRuntime::getInstance;
