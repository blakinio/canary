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
#include "game/multichannel/cluster_record_ownership.hpp"

// Cross-process DB-row handoff orchestration - docs/multichannel/
// CROSS_PROCESS_DB_ROW_HANDOFF.md. Ties an injected
// IClusterPendingOperationRepository (the durable command inbox) to an
// injected IClusterRecordOwnershipResolver (who currently owns a record)
// so a periodic per-channel sweep can safely apply exactly the operations
// this process either owns live or can safely apply as genuinely unowned -
// never anything it cannot currently confirm. Fully unit-testable against
// fakes of both injected interfaces (design doc §14); the real production
// wiring uses DbClusterPendingOperationRepository +
// DbClusterRecordOwnershipResolver, both engine-glue and reviewed by hand
// + real MariaDB, matching this project's established methodology.

enum class ClusterRecordApplyOutcome : uint8_t {
	Applied,
	// Business-level failure (e.g. mailbox full) - will not be retried
	// automatically (design doc §4.13): retrying a definitively-failed
	// business operation is not safe to assume idempotent at the business
	// level, only at the row level.
	FailedDefinitively,
	// The handler's own claim (design doc §4.11.2, applyUnowned only)
	// found the operation already resolved by another process - not an
	// error, no state transition needed here.
	AlreadyHandled,
};

struct ClusterRecordApplyResult {
	ClusterRecordApplyOutcome outcome = ClusterRecordApplyOutcome::FailedDefinitively;
	// For FailedDefinitively: human-readable reason, becomes the row's
	// last_error. Never the raw payload/user content (design doc §7).
	std::string errorDetail;
};

// Outcome of ClusterRecordHandoff::enqueueAndTryApplyNow - tells the
// enqueuing call site (e.g. Mailbox::sendItem) whether it is now safe to
// treat the source state (the physical item) as consumed.
enum class ClusterRecordHandoffOutcome : uint8_t {
	// No durable row exists (a real enqueue failure, or a duplicate
	// operationId) - the caller must not treat anything as consumed.
	NotEnqueued,
	// A row now exists durably, and a synchronous apply attempt came back
	// with a definitive business failure (e.g. mailbox full). The row
	// itself is a FAILED audit entry, not a pending retry - the caller
	// must still not treat the source state as consumed (mirrors today's
	// single-process "destination rejected the item, nothing moved"
	// behavior).
	EnqueuedButFailedDefinitively,
	// A row now exists durably - either applied synchronously right here,
	// or safely deferred to a later sweep because this process is not the
	// record's confirmed owner right now. Either way, the source state's
	// fate is now captured durably; the caller must treat it as consumed.
	EnqueuedDurably,
};

// One handler per record kind (registered by whatever engine wiring code
// calls ClusterRecordHandoff::sweep - PR 1 registers none; PR 2 registers
// PLAYER_INBOX). A handler covering more than one operation_type under
// the same record kind dispatches internally on record.operationType,
// per the design doc §6.3 "small, closed dispatch table, not a
// virtual-class-per-kind hierarchy" preference.
class IClusterRecordOperationHandler {
public:
	virtual ~IClusterRecordOperationHandler() = default;

	// Called only after ClusterRecordHandoff has just confirmed, via the
	// injected ownership resolver, that this process is the record's
	// current live owner - safe to mutate the record's live in-memory
	// state directly (design doc §4.11.3). No extra locking is needed
	// inside this method: exactly one process can ever reach it for a
	// given record at a time, by construction of the ownership check.
	[[nodiscard]] virtual ClusterRecordApplyResult applyOwned(const ClusterPendingOperationRecord &record) = 0;

	// Called only after the ownership resolver confirmed NoLiveOwner (only
	// reachable for dynamically-owned kinds, e.g. a fully offline
	// PLAYER_INBOX record). Multiple processes' sweeps may call this for
	// the *same* record concurrently - the handler is responsible for its
	// own transactional claim-then-apply (design doc §4.11.2): re-verify,
	// inside one DB transaction, that this pending-operation row is still
	// PENDING and the target is still genuinely unowned, before performing
	// the direct write. Returning AlreadyHandled (not Applied) is the
	// correct, expected outcome when another process's own attempt won
	// that race - it must not be treated as an error.
	[[nodiscard]] virtual ClusterRecordApplyResult applyUnowned(const ClusterPendingOperationRecord &record) = 0;
};

class ClusterRecordHandoff {
public:
	ClusterRecordHandoff(IClusterPendingOperationRepository &repository, IClusterRecordOwnershipResolver &resolver) :
		repository(repository), resolver(resolver) { }

	ClusterRecordHandoff(const ClusterRecordHandoff &) = delete;
	ClusterRecordHandoff &operator=(const ClusterRecordHandoff &) = delete;

	// Enqueues a new operation. Returns false both when operationId already
	// exists (already enqueued - a safe no-op from the caller's
	// perspective) and on a real repository error - see
	// IClusterPendingOperationRepository::enqueue's identical contract.
	[[nodiscard]] bool enqueue(const ClusterPendingOperationRecord &record);

	// Resolves current ownership for one record - exposed directly for
	// callers (e.g. a future GM command, design doc §11) that only need
	// the read, not a full sweep.
	[[nodiscard]] ClusterRecordOwnership resolveOwnership(const std::string &recordKind, int32_t recordId, const std::optional<int32_t> &recordChannelId);

	// Attempts to apply every currently-PENDING operation of recordKind
	// that this process (thisChannelId) either owns live or can safely
	// apply as genuinely unowned, using handler. A record whose ownership
	// resolves to another channel, or cannot currently be confirmed
	// (Unknown), is left untouched - the next sweep (this process's or the
	// true owner's) re-resolves from scratch (design doc §4.12). Returns
	// the number of rows this call transitioned out of PENDING (Applied or
	// FailedDefinitively) - AlreadyHandled and deferred rows are not
	// counted. Intended to run from the existing per-channel periodic
	// cycle (design doc §10), not a new scheduler.
	int32_t sweep(const std::string &recordKind, int32_t thisChannelId, int32_t limit, int64_t nowMs, IClusterRecordOperationHandler &handler);

	// Enqueues a new operation and, when this process can safely do so
	// right now (it already is the record's confirmed owner, or the record
	// is confirmed to have no live owner anywhere), also attempts to apply
	// it synchronously in the same call - avoiding the latency of waiting
	// for the next sweep tick for the common case. handler.applyOwned() is
	// only ever called when thisChannelId is the freshly-resolved owner
	// (never assumed from the caller), matching applyOwned's own contract.
	// When ownership resolves to another channel, or cannot currently be
	// confirmed, no apply is attempted here at all - the row is left
	// PENDING for that owner's own sweep (or a later retry) to resolve.
	[[nodiscard]] ClusterRecordHandoffOutcome enqueueAndTryApplyNow(const ClusterPendingOperationRecord &record, int32_t thisChannelId, int64_t nowMs, IClusterRecordOperationHandler &handler);

private:
	// Resolves ownership fresh and dispatches to the matching handler verb;
	// std::nullopt means "deferred, nothing attempted" (owner is another
	// channel, or ownership cannot currently be confirmed). Shared by
	// sweep() and enqueueAndTryApplyNow() so both use identical dispatch
	// rules.
	std::optional<ClusterRecordApplyResult> tryApply(const ClusterPendingOperationRecord &record, int32_t thisChannelId, IClusterRecordOperationHandler &handler);

	// Transitions the row per result.outcome (Applied -> markApplied,
	// FailedDefinitively -> markFailed, AlreadyHandled -> no-op). Returns
	// whether a state transition actually happened (false for
	// AlreadyHandled or if the underlying repository call itself reports
	// no row was affected, e.g. a concurrent transition already moved it
	// out of PENDING).
	bool transitionAfterApply(const std::string &operationId, const ClusterRecordApplyResult &result, int64_t nowMs);

	IClusterPendingOperationRepository &repository;
	IClusterRecordOwnershipResolver &resolver;
};
