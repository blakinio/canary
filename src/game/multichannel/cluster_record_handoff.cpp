/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_record_handoff.hpp"

bool ClusterRecordHandoff::enqueue(const ClusterPendingOperationRecord &record) {
	return repository.enqueue(record);
}

ClusterRecordOwnership ClusterRecordHandoff::resolveOwnership(const std::string &recordKind, int32_t recordId, const std::optional<int32_t> &recordChannelId) {
	return resolver.resolve(recordKind, recordId, recordChannelId);
}

std::optional<ClusterRecordApplyResult> ClusterRecordHandoff::tryApply(const ClusterPendingOperationRecord &record, int32_t thisChannelId, IClusterRecordOperationHandler &handler) {
	const auto ownership = resolver.resolve(record.recordKind, record.recordId, record.recordChannelId);

	if (ownership.outcome == ClusterRecordOwnershipOutcome::Unknown) {
		// Cannot currently confirm who owns this record - fail closed,
		// leave it PENDING for a later sweep (design doc §4.7/§14 test 12).
		return std::nullopt;
	}
	if (ownership.outcome == ClusterRecordOwnershipOutcome::OwnedByChannel) {
		if (ownership.ownerChannelId != thisChannelId) {
			// Another channel owns it live - defer to its own sweep
			// (design doc §4.12).
			return std::nullopt;
		}
		return handler.applyOwned(record);
	}
	// NoLiveOwner - safe for any process to attempt, guarded by the
	// handler's own transactional claim (design doc §4.11.2).
	return handler.applyUnowned(record);
}

bool ClusterRecordHandoff::transitionAfterApply(const std::string &operationId, const ClusterRecordApplyResult &result, int64_t nowMs) {
	switch (result.outcome) {
		case ClusterRecordApplyOutcome::Applied:
			return repository.markApplied(operationId, nowMs);
		case ClusterRecordApplyOutcome::FailedDefinitively:
			return repository.markFailed(operationId, nowMs, result.errorDetail);
		case ClusterRecordApplyOutcome::AlreadyHandled:
			// Another process's applyUnowned already resolved this row (or
			// the handler's own claim found it no longer PENDING) - not an
			// error, no state transition needed here.
			return false;
	}
	return false;
}

int32_t ClusterRecordHandoff::sweep(const std::string &recordKind, int32_t thisChannelId, int32_t limit, int64_t nowMs, IClusterRecordOperationHandler &handler) {
	const auto pending = repository.findPendingForKind(recordKind, limit);

	int32_t transitioned = 0;
	for (const auto &record : pending) {
		const auto result = tryApply(record, thisChannelId, handler);
		if (!result.has_value()) {
			continue;
		}
		if (transitionAfterApply(record.operationId, *result, nowMs)) {
			++transitioned;
		}
	}

	return transitioned;
}

ClusterRecordHandoffOutcome ClusterRecordHandoff::enqueueAndTryApplyNow(const ClusterPendingOperationRecord &record, int32_t thisChannelId, int64_t nowMs, IClusterRecordOperationHandler &handler) {
	if (!repository.enqueue(record)) {
		return ClusterRecordHandoffOutcome::NotEnqueued;
	}

	const auto result = tryApply(record, thisChannelId, handler);
	if (!result.has_value()) {
		// Ownership is elsewhere or not currently confirmable - the row is
		// durably PENDING; a later sweep (this process's own, or the true
		// owner's) will resolve it (design doc §4.12).
		return ClusterRecordHandoffOutcome::EnqueuedDurably;
	}

	transitionAfterApply(record.operationId, *result, nowMs);

	if (result->outcome == ClusterRecordApplyOutcome::FailedDefinitively) {
		return ClusterRecordHandoffOutcome::EnqueuedButFailedDefinitively;
	}
	return ClusterRecordHandoffOutcome::EnqueuedDurably;
}
