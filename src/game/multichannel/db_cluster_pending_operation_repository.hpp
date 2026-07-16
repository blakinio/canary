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

// Real, database-backed IClusterPendingOperationRepository. See
// docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md §5.
class DbClusterPendingOperationRepository final : public IClusterPendingOperationRepository {
public:
	bool enqueue(const ClusterPendingOperationRecord &record) override;
	bool markApplied(const std::string &operationId, int64_t nowMs) override;
	bool markFailed(const std::string &operationId, int64_t nowMs, const std::string &reason) override;
	bool markAbandoned(const std::string &operationId, int64_t nowMs, const std::string &reason) override;
	std::vector<ClusterPendingOperationRecord> findPendingForRecord(const std::string &recordKind, int32_t recordId) override;
	std::vector<ClusterPendingOperationRecord> findPendingForKind(const std::string &recordKind, int32_t limit) override;
	int64_t countStalePending(int64_t nowMs, int64_t staleWarningMs) override;
};
