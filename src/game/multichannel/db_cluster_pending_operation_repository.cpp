/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/db_cluster_pending_operation_repository.hpp"

#include "database/database.hpp"
#include "lib/logging/log_with_spd_log.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <sstream>
#endif

std::string describeClusterPendingOperationStatus(ClusterPendingOperationStatus status) {
	switch (status) {
		case ClusterPendingOperationStatus::Pending:
			return "PENDING";
		case ClusterPendingOperationStatus::Applied:
			return "APPLIED";
		case ClusterPendingOperationStatus::Failed:
			return "FAILED";
		case ClusterPendingOperationStatus::Abandoned:
			return "ABANDONED";
	}
	return "PENDING";
}

namespace {
	std::string optionalIntToSql(const std::optional<int32_t> &value) {
		return value.has_value() ? std::to_string(*value) : "NULL";
	}

	ClusterPendingOperationRecord rowToRecord(const DBResult_ptr &result) {
		ClusterPendingOperationRecord record;
		record.operationId = result->getString("operation_id");
		record.recordKind = result->getString("record_kind");
		record.recordId = result->getNumber<int32_t>("record_id");
		// 0 is never a valid channel id (ChannelContext::DefaultSingleChannelId
		// is 1) - matches the existing optionalIntColumn convention already
		// used for channel_switch_audit.source_channel_id via COALESCE.
		const auto recordChannelId = result->getNumber<int32_t>("record_channel_id");
		if (recordChannelId != 0) {
			record.recordChannelId = recordChannelId;
		}
		record.operationType = result->getString("operation_type");
		record.payload = result->getString("payload");

		const std::string status = result->getString("status");
		if (status == "APPLIED") {
			record.status = ClusterPendingOperationStatus::Applied;
		} else if (status == "FAILED") {
			record.status = ClusterPendingOperationStatus::Failed;
		} else if (status == "ABANDONED") {
			record.status = ClusterPendingOperationStatus::Abandoned;
		} else {
			record.status = ClusterPendingOperationStatus::Pending;
		}

		record.attempts = result->getNumber<int32_t>("attempts");
		record.lastError = result->getString("last_error");
		record.enqueuedByChannelId = result->getNumber<int32_t>("enqueued_by_channel_id");
		record.createdAtMs = result->getNumber<int64_t>("created_at");

		const auto appliedAt = result->getNumber<int64_t>("applied_at");
		if (appliedAt != 0) {
			record.appliedAtMs = appliedAt;
		}

		return record;
	}

	std::vector<ClusterPendingOperationRecord> runPendingQuery(const std::string &sql) {
		Database &db = Database::getInstance();
		std::vector<ClusterPendingOperationRecord> records;
		const DBResult_ptr result = db.storeQuery(sql);
		if (!result) {
			return records;
		}
		do {
			records.push_back(rowToRecord(result));
		} while (result->next());
		return records;
	}
} // namespace

bool DbClusterPendingOperationRepository::enqueue(const ClusterPendingOperationRecord &record) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "INSERT INTO `cluster_pending_operations` (`operation_id`, `record_kind`, `record_id`, `record_channel_id`, `operation_type`, `payload`, `status`, `attempts`, `last_error`, `enqueued_by_channel_id`, `created_at`) VALUES ("
		  << db.escapeString(record.operationId) << ", "
		  << db.escapeString(record.recordKind) << ", "
		  << record.recordId << ", "
		  << optionalIntToSql(record.recordChannelId) << ", "
		  << db.escapeString(record.operationType) << ", "
		  << db.escapeString(record.payload) << ", "
		  << "'PENDING', "
		  << "0, "
		  << "'', "
		  << record.enqueuedByChannelId << ", "
		  << record.createdAtMs
		  << ")";

	// A failure here - duplicate key (already enqueued) or any other real
	// error - must be treated identically by the caller: the operation is
	// not safely known to be newly enqueued. Matches EconomicLedgerStore::
	// beginPending's identical contract.
	return db.executeQuery(query.str());
}

bool DbClusterPendingOperationRepository::markApplied(const std::string &operationId, int64_t nowMs) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "UPDATE `cluster_pending_operations` SET `status` = 'APPLIED', `applied_at` = " << nowMs
		  << ", `attempts` = `attempts` + 1"
		  << " WHERE `operation_id` = " << db.escapeString(operationId)
		  << " AND `status` = 'PENDING'";

	const auto affectedRows = db.executeQueryAffectedRows(query.str());
	if (!affectedRows.has_value()) {
		g_logger().error("[DbClusterPendingOperationRepository::markApplied] - Failed to mark operation {} applied.", operationId);
		return false;
	}
	return *affectedRows > 0;
}

bool DbClusterPendingOperationRepository::markFailed(const std::string &operationId, int64_t nowMs, const std::string &reason) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "UPDATE `cluster_pending_operations` SET `status` = 'FAILED', `applied_at` = " << nowMs
		  << ", `attempts` = `attempts` + 1"
		  << ", `last_error` = " << db.escapeString(reason)
		  << " WHERE `operation_id` = " << db.escapeString(operationId)
		  << " AND `status` = 'PENDING'";

	const auto affectedRows = db.executeQueryAffectedRows(query.str());
	if (!affectedRows.has_value()) {
		g_logger().error("[DbClusterPendingOperationRepository::markFailed] - Failed to mark operation {} failed.", operationId);
		return false;
	}
	return *affectedRows > 0;
}

bool DbClusterPendingOperationRepository::markAbandoned(const std::string &operationId, int64_t nowMs, const std::string &reason) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "UPDATE `cluster_pending_operations` SET `status` = 'ABANDONED', `applied_at` = " << nowMs
		  << ", `last_error` = " << db.escapeString(reason)
		  << " WHERE `operation_id` = " << db.escapeString(operationId)
		  << " AND `status` = 'PENDING'";

	const auto affectedRows = db.executeQueryAffectedRows(query.str());
	if (!affectedRows.has_value()) {
		g_logger().error("[DbClusterPendingOperationRepository::markAbandoned] - Failed to abandon operation {}.", operationId);
		return false;
	}
	return *affectedRows > 0;
}

std::vector<ClusterPendingOperationRecord> DbClusterPendingOperationRepository::findPendingForRecord(const std::string &recordKind, int32_t recordId) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "SELECT `operation_id`, `record_kind`, `record_id`, COALESCE(`record_channel_id`, 0) AS `record_channel_id`, `operation_type`, `payload`, `status`, `attempts`, `last_error`, `enqueued_by_channel_id`, `created_at`, COALESCE(`applied_at`, 0) AS `applied_at` "
		  << "FROM `cluster_pending_operations` WHERE `record_kind` = " << db.escapeString(recordKind)
		  << " AND `record_id` = " << recordId
		  << " AND `status` = 'PENDING'"
		  << " ORDER BY `created_at` ASC;";

	return runPendingQuery(query.str());
}

std::vector<ClusterPendingOperationRecord> DbClusterPendingOperationRepository::findPendingForKind(const std::string &recordKind, int32_t limit) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "SELECT `operation_id`, `record_kind`, `record_id`, COALESCE(`record_channel_id`, 0) AS `record_channel_id`, `operation_type`, `payload`, `status`, `attempts`, `last_error`, `enqueued_by_channel_id`, `created_at`, COALESCE(`applied_at`, 0) AS `applied_at` "
		  << "FROM `cluster_pending_operations` WHERE `record_kind` = " << db.escapeString(recordKind)
		  << " AND `status` = 'PENDING'"
		  << " ORDER BY `created_at` ASC LIMIT " << limit << ";";

	return runPendingQuery(query.str());
}

int64_t DbClusterPendingOperationRepository::countStalePending(int64_t nowMs, int64_t staleWarningMs) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "SELECT COUNT(*) AS `count` FROM `cluster_pending_operations` WHERE `status` = 'PENDING' AND `created_at` < " << (nowMs - staleWarningMs) << ";";

	const DBResult_ptr result = db.storeQuery(query.str());
	if (!result) {
		return 0;
	}
	return result->getNumber<int64_t>("count");
}
