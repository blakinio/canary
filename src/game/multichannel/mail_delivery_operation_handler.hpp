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

// IClusterRecordOperationHandler for PLAYER_INBOX/DELIVER_MAIL_ITEM -
// docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md §6.1. Not standalone-
// compilable (transitively requires game/game.hpp for Item/Player/
// IOLoginData/g_saveManager - the same wall as every other engine-glue
// multichannel file), reviewed by hand and verified against a real
// MariaDB instance instead - see TEST_PLAN.md.
class MailDeliveryOperationHandler final : public IClusterRecordOperationHandler {
public:
	// record.recordId is the recipient's player id. Called only after
	// ClusterRecordHandoff has just confirmed this process is the live
	// owner of that player's session (design doc §4.11.3) - reconstructs
	// the item and inserts it directly into the recipient's live in-memory
	// Inbox container, letting that player's own existing, unmodified save
	// pipeline persist it correctly on its own next save.
	[[nodiscard]] ClusterRecordApplyResult applyOwned(const ClusterPendingOperationRecord &record) override;

	// Called only when the recipient is confirmed to have no live owner
	// anywhere in the cluster (fully offline) - applies directly via a
	// throwaway Player load + save, guarded by a real DB transaction
	// (design doc §4.11.2) that re-verifies both this pending-operation row
	// is still PENDING and the recipient is still not ONLINE anywhere,
	// immediately before committing, closing the race window against a
	// concurrent login or a concurrent duplicate applyUnowned attempt from
	// another process.
	[[nodiscard]] ClusterRecordApplyResult applyUnowned(const ClusterPendingOperationRecord &record) override;
};
