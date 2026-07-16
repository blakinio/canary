/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
	#include <string>
	#include <vector>
#endif

// Abstraction over the `cluster_pending_operations` table
// (docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md §5): the durable
// command inbox that lets one channel enqueue an operation targeting a
// record it does not currently own, for whichever channel does currently
// own that record to apply safely through its own live in-memory state.
// `operation_id` as the idempotency key matches `economic_ledger.
// transaction_uuid`'s exact contract. Mirrors IClusterSessionRepository's
// interface/impl/fake split so ClusterRecordHandoff (the orchestration
// layer that uses this) is unit-testable without a live database.
enum class ClusterPendingOperationStatus : uint8_t {
	Pending,
	Applied,
	Failed,
	Abandoned,
};

[[nodiscard]] std::string describeClusterPendingOperationStatus(ClusterPendingOperationStatus status);

struct ClusterPendingOperationRecord {
	std::string operationId;
	std::string recordKind;
	int32_t recordId = 0;
	// Set only for statically-owned record kinds (e.g. "HOUSE"); left unset
	// for dynamically-owned kinds (e.g. "PLAYER_INBOX") whose owner is
	// resolved live via cluster_sessions instead - see the design doc §4.1.
	std::optional<int32_t> recordChannelId;
	std::string operationType;
	// Opaque to the repository - callers serialize/deserialize their own
	// shape. Never logged in full (may carry user-authored text); see the
	// design doc §7.
	std::string payload;
	ClusterPendingOperationStatus status = ClusterPendingOperationStatus::Pending;
	int32_t attempts = 0;
	std::string lastError;
	int32_t enqueuedByChannelId = 0;
	int64_t createdAtMs = 0;
	std::optional<int64_t> appliedAtMs;
};

class IClusterPendingOperationRepository {
public:
	virtual ~IClusterPendingOperationRepository() = default;

	// Inserts a PENDING row for record.operationId. Returns false both when
	// the id already exists (a genuine replay of an already-enqueued
	// operation - the caller must treat this as "already enqueued," not an
	// error) and on a real error - callers cannot distinguish the two from
	// this return value alone, matching EconomicLedgerStore::beginPending's
	// identical contract and reasoning.
	virtual bool enqueue(const ClusterPendingOperationRecord &record) = 0;

	// Every row in every terminal state must go through markApplied/
	// markFailed/markAbandoned exactly once. Implementations must guard
	// each with "... AND status = 'PENDING'" (or the fake's equivalent) to
	// prevent a double-transition race between two sweep passes of the
	// same process, on top of the ownership check that already prevents
	// two *different* processes from both applying (design doc §4.5/§9).
	// Returns false if the row was not found or was not PENDING.
	virtual bool markApplied(const std::string &operationId, int64_t nowMs) = 0;
	virtual bool markFailed(const std::string &operationId, int64_t nowMs, const std::string &reason) = 0;
	virtual bool markAbandoned(const std::string &operationId, int64_t nowMs, const std::string &reason) = 0;

	// Every still-PENDING row for one specific record, oldest first.
	virtual std::vector<ClusterPendingOperationRecord> findPendingForRecord(const std::string &recordKind, int32_t recordId) = 0;

	// Every still-PENDING row for a whole record kind, oldest first - used
	// by the periodic sweep to discover work without needing to already
	// know which specific record ids have pending operations.
	virtual std::vector<ClusterPendingOperationRecord> findPendingForKind(const std::string &recordKind, int32_t limit) = 0;

	// Count of PENDING rows older than nowMs - staleWarningMs - the
	// observability gauge from the design doc §7/§11.
	virtual int64_t countStalePending(int64_t nowMs, int64_t staleWarningMs) = 0;
};
