/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/multichannel/cluster_record_ownership.hpp"

// Real, database-backed IClusterRecordOwnershipResolver. See
// docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md §4.1.
//
// PLAYER_INBOX resolves via the existing `cluster_sessions` table (the
// same source multichannel::findOnlineChannelForPlayer already reads).
// HOUSE resolves via the recordChannelId already carried on the pending
// operation row (static routing metadata, no lookup needed) or, if not
// provided, a plain `houses.channel_id` read.
class DbClusterRecordOwnershipResolver final : public IClusterRecordOwnershipResolver {
public:
	ClusterRecordOwnership resolve(const std::string &recordKind, int32_t recordId, const std::optional<int32_t> &recordChannelId) override;

private:
	ClusterRecordOwnership resolvePlayerInbox(int32_t playerId);
	ClusterRecordOwnership resolveHouse(int32_t houseId, const std::optional<int32_t> &recordChannelId);
};
