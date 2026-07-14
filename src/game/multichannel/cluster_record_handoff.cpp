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

int32_t ClusterRecordHandoff::sweep(const std::string &recordKind, int32_t thisChannelId, int32_t limit, int64_t nowMs, IClusterRecordOperationHandler &handler) {
	const auto pending = repository.findPendingForKind(recordKind, limit);

	int32_t transitioned = 0;
	for (const auto &record : pending) {
		const auto ownership = resolver.resolve(record.recordKind, record.recordId, record.recordChannelId);

		ClusterRecordApplyResult result;
		if (ownership.outcome == ClusterRecordOwnershipOutcome::Unknown) {
			// Cannot currently confirm who owns this record - fail closed,
			// leave it PENDING for a later sweep (design doc §4.7/§14 test 12).
			continue;
		} else if (ownership.outcome == ClusterRecordOwnershipOutcome::OwnedByChannel) {
			if (ownership.ownerChannelId != thisChannelId) {
				// Another channel owns it live - defer to its own sweep
				// (design doc §4.12).
				continue;
			}
			result = handler.applyOwned(record);
		} else {
			// NoLiveOwner - safe for any process to attempt, guarded by the
			// handler's own transactional claim (design doc §4.11.2).
			result = handler.applyUnowned(record);
		}

		switch (result.outcome) {
			case ClusterRecordApplyOutcome::Applied:
				if (repository.markApplied(record.operationId, nowMs)) {
					++transitioned;
				}
				break;
			case ClusterRecordApplyOutcome::FailedDefinitively:
				if (repository.markFailed(record.operationId, nowMs, result.errorDetail)) {
					++transitioned;
				}
				break;
			case ClusterRecordApplyOutcome::AlreadyHandled:
				// Another process's applyUnowned already resolved this row
				// (or the handler's own claim found it no longer PENDING) -
				// not an error, no state transition needed here.
				break;
		}
	}

	return transitioned;
}
