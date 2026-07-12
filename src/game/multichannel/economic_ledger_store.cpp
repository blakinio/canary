/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/economic_ledger_store.hpp"

#include "database/database.hpp"
#include "game/multichannel/economic_ledger_id.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <sstream>
#endif

std::string EconomicLedgerStore::deterministicUuid(const std::string &namespaceTag, uint64_t naturalKey) {
	return multichannel::computeDeterministicLedgerUuid(namespaceTag, naturalKey);
}

namespace {
	std::string optionalIntToSql(const std::optional<int32_t> &value) {
		return value.has_value() ? std::to_string(*value) : "NULL";
	}
} // namespace

bool EconomicLedgerStore::beginPending(const EconomicLedgerRecord &record, int64_t nowMs) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "INSERT INTO `economic_ledger` (`transaction_uuid`, `operation_type`, `account_id`, `player_id`, `source_channel_id`, `target_channel_id`, `amount`, `currency`, `item_id`, `item_count`, `status`, `created_at`, `updated_at`) VALUES ("
		  << db.escapeString(record.transactionUuid) << ", "
		  << db.escapeString(record.operationType) << ", "
		  << optionalIntToSql(record.accountId) << ", "
		  << optionalIntToSql(record.playerId) << ", "
		  << optionalIntToSql(record.sourceChannelId) << ", "
		  << optionalIntToSql(record.targetChannelId) << ", "
		  << record.amount << ", "
		  << db.escapeString(record.currency) << ", "
		  << optionalIntToSql(record.itemId) << ", "
		  << optionalIntToSql(record.itemCount) << ", "
		  << "'PENDING', "
		  << nowMs << ", "
		  << nowMs
		  << ")";

	// A failure here - whether a duplicate-key rejection (this exact
	// transaction was already attempted) or any other real DB error - must
	// be treated identically by the caller: do not perform the money/item
	// effect this row was meant to guard. Financial code fails closed.
	return db.executeQuery(query.str());
}

bool EconomicLedgerStore::markCommitted(const std::string &transactionUuid, int64_t nowMs) {
	Database &db = Database::getInstance();
	std::ostringstream query;
	query << "UPDATE `economic_ledger` SET `status` = 'COMMITTED', `updated_at` = " << nowMs
		  << " WHERE `transaction_uuid` = " << db.escapeString(transactionUuid);
	return db.executeQuery(query.str());
}

bool EconomicLedgerStore::markFailed(const std::string &transactionUuid, int64_t nowMs) {
	Database &db = Database::getInstance();
	std::ostringstream query;
	query << "UPDATE `economic_ledger` SET `status` = 'FAILED', `updated_at` = " << nowMs
		  << " WHERE `transaction_uuid` = " << db.escapeString(transactionUuid);
	return db.executeQuery(query.str());
}
