/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/mail_delivery_operation_handler.hpp"

#include "creatures/players/player.hpp"
#include "database/database.hpp"
#include "game/game.hpp"
#include "game/multichannel/mail_delivery_payload.hpp"
#include "game/scheduling/save_manager.hpp"
#include "io/iologindata.hpp"
#include "items/containers/inbox/inbox.hpp"
#include "lib/logging/log_with_spd_log.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <sstream>
#endif

namespace {
	// Same primitive IOLoginDataLoad::loadItems already uses per-item
	// (Item::CreateItem + unserializeAttr against a PropStream) - reused,
	// not reinvented.
	std::shared_ptr<Item> reconstructItem(const multichannel::MailDeliveryPayload &payload) {
		const auto &item = Item::CreateItem(payload.itemId, payload.itemCount);
		if (!item) {
			return nullptr;
		}

		const auto rawAttributes = multichannel::hexDecode(payload.itemAttributesHex);
		if (!rawAttributes.has_value()) {
			return nullptr;
		}

		PropStream propStream;
		propStream.init(rawAttributes->data(), rawAttributes->size());
		if (!item->unserializeAttr(propStream)) {
			return nullptr;
		}

		return item;
	}

	// Mirrors Mailbox::sendItem's existing post-insert transform exactly:
	// every item sent through the mailbox (letters AND parcels - both have
	// unstamped/stamped item id pairs, see utils_definitions.hpp) is
	// unconditionally transformed to id+1 once it lands in the recipient's
	// inbox. The transform does not itself preserve custom attributes, so
	// writer/date/text (already extracted into the payload at enqueue time,
	// for the same reason the original code extracts them before
	// transforming) must be re-applied afterward - but only for letters,
	// same as the original.
	void applyStampedLetterAttributes(const std::shared_ptr<Item> &insertedItem, const multichannel::MailDeliveryPayload &payload) {
		const auto &newItem = g_game().transformItem(insertedItem, insertedItem->getID() + 1);
		if (newItem && newItem->getID() == ITEM_LETTER_STAMPED && !payload.writer.empty()) {
			newItem->setAttribute(ItemAttribute_t::WRITER, payload.writer);
			newItem->setAttribute(ItemAttribute_t::DATE, payload.writtenDate);
			newItem->setAttribute(ItemAttribute_t::TEXT, payload.text);
		}
	}
} // namespace

ClusterRecordApplyResult MailDeliveryOperationHandler::applyOwned(const ClusterPendingOperationRecord &record) {
	const auto payload = multichannel::deserializeMailDeliveryPayload(record.payload);
	if (!payload.has_value()) {
		return { ClusterRecordApplyOutcome::FailedDefinitively, "malformed mail delivery payload" };
	}

	const auto &player = g_game().getPlayerByGUID(static_cast<uint32_t>(record.recordId));
	if (!player) {
		// Should not happen: ClusterRecordHandoff just confirmed, moments
		// earlier in the same synchronous sweep, that this process owns
		// this player's live session. Treat as a transient inconsistency,
		// not a business failure - leave the row PENDING for a later sweep
		// to retry rather than permanently marking it FAILED.
		g_logger().warn("[MailDeliveryOperationHandler] - Confirmed live owner but player id {} not found; deferring.", record.recordId);
		return { ClusterRecordApplyOutcome::AlreadyHandled, "" };
	}

	const auto &item = reconstructItem(*payload);
	if (!item) {
		return { ClusterRecordApplyOutcome::FailedDefinitively, "failed to reconstruct mailed item" };
	}

	const auto &playerInbox = player->getInbox();
	if (g_game().internalAddItem(playerInbox, item, INDEX_WHEREEVER, FLAG_NOLIMIT) != RETURNVALUE_NOERROR) {
		return { ClusterRecordApplyOutcome::FailedDefinitively, "recipient inbox rejected the item (full or invalid)" };
	}

	applyStampedLetterAttributes(item, *payload);

	if (player->isOnline()) {
		player->onReceiveMail();
	}

	return { ClusterRecordApplyOutcome::Applied, "" };
}

ClusterRecordApplyResult MailDeliveryOperationHandler::applyUnowned(const ClusterPendingOperationRecord &record) {
	const auto payload = multichannel::deserializeMailDeliveryPayload(record.payload);
	if (!payload.has_value()) {
		return { ClusterRecordApplyOutcome::FailedDefinitively, "malformed mail delivery payload" };
	}

	Database &db = Database::getInstance();
	ClusterRecordApplyResult outcome { ClusterRecordApplyOutcome::AlreadyHandled, "" };

	// Design doc §4.11.2: one explicit transaction spanning the row-lock
	// read, the direct-apply write, and the implicit "this is now applied"
	// state together - the only place this mechanism uses an explicit
	// multi-statement transaction, narrowly, for exactly this race.
	const bool committed = DBTransaction::executeWithinTransactionRollbackOnFailure([&]() {
		// Lock this row (guaranteed to exist - we are processing an
		// existing PENDING row) to serialize against a concurrent
		// applyUnowned attempt for the *same* operation from another
		// process's sweep.
		std::ostringstream lockQuery;
		lockQuery << "SELECT `status` FROM `cluster_pending_operations` WHERE `operation_id` = " << db.escapeString(record.operationId) << " FOR UPDATE;";
		const auto lockResult = db.storeQuery(lockQuery.str());
		if (!lockResult || lockResult->getString("status") != "PENDING") {
			// Already resolved by another process (or the row vanished) -
			// not our job anymore, not an error.
			return false;
		}

		std::ostringstream onlineCheckQuery;
		onlineCheckQuery << "SELECT 1 FROM `cluster_sessions` WHERE `player_id` = " << record.recordId << " AND `status` = 'ONLINE' LIMIT 1;";
		if (db.storeQuery(onlineCheckQuery.str())) {
			// A login raced in since ownership was resolved as NoLiveOwner -
			// defer to that channel's own sweep (applyOwned) instead of
			// racing a direct write against its live in-memory state.
			return false;
		}

		std::shared_ptr<Player> tmpPlayer = std::make_shared<Player>(nullptr);
		if (!IOLoginData::loadPlayerById(tmpPlayer, static_cast<uint32_t>(record.recordId))) {
			outcome = { ClusterRecordApplyOutcome::FailedDefinitively, "recipient player row not found" };
			return false;
		}
		tmpPlayer->setOnline(false);

		const auto &item = reconstructItem(*payload);
		if (!item) {
			outcome = { ClusterRecordApplyOutcome::FailedDefinitively, "failed to reconstruct mailed item" };
			return false;
		}

		const auto &playerInbox = tmpPlayer->getInbox();
		if (g_game().internalAddItem(playerInbox, item, INDEX_WHEREEVER, FLAG_NOLIMIT) != RETURNVALUE_NOERROR) {
			outcome = { ClusterRecordApplyOutcome::FailedDefinitively, "recipient inbox rejected the item (full or invalid)" };
			return false;
		}

		applyStampedLetterAttributes(item, *payload);

		if (!g_saveManager().savePlayer(tmpPlayer)) {
			outcome = { ClusterRecordApplyOutcome::FailedDefinitively, "failed to save recipient after offline delivery" };
			return false;
		}

		outcome = { ClusterRecordApplyOutcome::Applied, "" };
		return true;
	});

	if (!committed && outcome.outcome == ClusterRecordApplyOutcome::Applied) {
		// The transaction itself failed to commit after we thought we
		// succeeded - do not report success for an uncommitted write.
		return { ClusterRecordApplyOutcome::FailedDefinitively, "offline delivery transaction failed to commit" };
	}

	return outcome;
}
