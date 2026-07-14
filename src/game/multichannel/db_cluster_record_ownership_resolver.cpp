/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/db_cluster_record_ownership_resolver.hpp"

#include "database/database.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <sstream>
#endif

ClusterRecordOwnership DbClusterRecordOwnershipResolver::resolve(const std::string &recordKind, int32_t recordId, const std::optional<int32_t> &recordChannelId) {
	if (recordKind == multichannel::RecordKindHouse) {
		return resolveHouse(recordId, recordChannelId);
	}
	if (recordKind == multichannel::RecordKindPlayerInbox) {
		return resolvePlayerInbox(recordId);
	}
	// Unknown record kind: nothing safe to assume - fail closed rather than
	// guess (design doc §2 "Fail-closed" requirement).
	return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::Unknown, 0 };
}

ClusterRecordOwnership DbClusterRecordOwnershipResolver::resolveHouse(int32_t houseId, const std::optional<int32_t> &recordChannelId) {
	if (recordChannelId.has_value()) {
		// Static routing metadata already known to the caller - no lookup
		// needed (design doc §4.2).
		return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::OwnedByChannel, *recordChannelId };
	}

	Database &db = Database::getInstance();
	std::ostringstream query;
	query << "SELECT `channel_id` FROM `houses` WHERE `id` = " << houseId << " LIMIT 1;";

	const DBResult_ptr result = db.storeQuery(query.str());
	if (!result) {
		// A house's channel_id is fixed routing metadata that must exist
		// for any real house id - a missing/failed read here means either
		// an invalid house id or a DB problem, neither of which is safe to
		// treat as "this channel owns it." Fail closed.
		return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::Unknown, 0 };
	}

	return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::OwnedByChannel, result->getNumber<int32_t>("channel_id") };
}

ClusterRecordOwnership DbClusterRecordOwnershipResolver::resolvePlayerInbox(int32_t playerId) {
	Database &db = Database::getInstance();

	std::ostringstream query;
	query << "SELECT `channel_id` FROM `cluster_sessions` WHERE `player_id` = " << playerId
		  << " AND `status` = 'ONLINE' LIMIT 1;";

	const DBResult_ptr result = db.storeQuery(query.str());
	if (result) {
		return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::OwnedByChannel, result->getNumber<int32_t>("channel_id") };
	}

	// storeQuery() returns nullptr both for "zero matching rows" and for a
	// real query/connection failure - this project's Database wrapper does
	// not distinguish the two at this call site (confirmed by reading
	// Database::storeQuery directly; every existing store in this codebase
	// already accepts this same ambiguity for its own "no such row" case).
	// For this resolver specifically, that ambiguity is a real safety
	// question - see design doc §14 test 12 - so it is not accepted
	// silently: a cheap, guaranteed-nonempty control query (`SELECT 1`)
	// distinguishes "the DB itself is unreachable/erroring right now" from
	// "the DB is healthy and genuinely has no ONLINE row for this player."
	// Only the latter is reported as NoLiveOwner (safe to apply directly,
	// guarded further per §4.11.2); the former is Unknown (must defer).
	const DBResult_ptr probe = db.storeQuery("SELECT 1;");
	if (!probe) {
		return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::Unknown, 0 };
	}

	return ClusterRecordOwnership { ClusterRecordOwnershipOutcome::NoLiveOwner, 0 };
}
