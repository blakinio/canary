/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "items/containers/mailbox/mailbox.hpp"

#include "creatures/players/player.hpp"
#include "game/game.hpp"
#include "game/multichannel/cluster_handoff_runtime.hpp"
#include "game/multichannel/cluster_operation_id.hpp"
#include "game/multichannel/cluster_record_ownership.hpp"
#include "game/multichannel/mail_delivery_operation_handler.hpp"
#include "game/multichannel/mail_delivery_payload.hpp"
#include "game/multichannel/wall_clock.hpp"
#include "game/scheduling/save_manager.hpp"
#include "io/iologindata.hpp"
#include "items/containers/inbox/inbox.hpp"
#include "map/spectators.hpp"

ReturnValue Mailbox::queryAdd(int32_t, const std::shared_ptr<Thing> &thing, uint32_t, uint32_t, const std::shared_ptr<Creature> &) {
	const auto &item = thing->getItem();
	if (item && Mailbox::canSend(item)) {
		return RETURNVALUE_NOERROR;
	}
	return RETURNVALUE_NOTPOSSIBLE;
}

ReturnValue Mailbox::queryMaxCount(int32_t, const std::shared_ptr<Thing> &, uint32_t count, uint32_t &maxQueryCount, uint32_t) {
	maxQueryCount = std::max<uint32_t>(1, count);
	return RETURNVALUE_NOERROR;
}

ReturnValue Mailbox::queryRemove(const std::shared_ptr<Thing> &, uint32_t, uint32_t, const std::shared_ptr<Creature> & /*= nullptr */) {
	return RETURNVALUE_NOTPOSSIBLE;
}

std::shared_ptr<Cylinder> Mailbox::queryDestination(int32_t &, const std::shared_ptr<Thing> &, std::shared_ptr<Item> &, uint32_t &) {
	return getMailbox();
}

void Mailbox::addThing(const std::shared_ptr<Thing> &thing) {
	return addThing(0, thing);
}

void Mailbox::addThing(int32_t, const std::shared_ptr<Thing> &thing) {
	if (!thing) {
		return;
	}

	const auto &item = thing->getItem();
	if (item && Mailbox::canSend(item)) {
		sendItem(item);
	}
}

void Mailbox::updateThing(const std::shared_ptr<Thing> &, uint16_t, uint32_t) {
	//
}

void Mailbox::replaceThing(uint32_t, const std::shared_ptr<Thing> &) {
	//
}

void Mailbox::removeThing(const std::shared_ptr<Thing> &, uint32_t) {
	//
}

void Mailbox::postAddNotification(const std::shared_ptr<Thing> &thing, const std::shared_ptr<Cylinder> &oldParent, int32_t index, CylinderLink_t) {
	getParent()->postAddNotification(thing, oldParent, index, LINK_PARENT);
}

void Mailbox::postRemoveNotification(const std::shared_ptr<Thing> &thing, const std::shared_ptr<Cylinder> &newParent, int32_t index, CylinderLink_t) {
	getParent()->postRemoveNotification(thing, newParent, index, LINK_PARENT);
}

bool Mailbox::sendItem(const std::shared_ptr<Item> &item) const {
	std::string receiver;
	if (!getReceiver(item, receiver)) {
		return false;
	}

	/**No need to continue if its still empty**/
	if (receiver.empty()) {
		return false;
	}

	if (item && item->getContainer() && item->getTile()) {
		for (const auto &spectator : Spectators().find<Player>(item->getTile()->getPosition())) {
			spectator->getPlayer()->autoCloseContainers(item->getContainer());
		}
	}

	// Local fast path takes priority even in multichannel mode (design doc
	// §10): only when the recipient is not part of this process's own live
	// state do we ever consider a cross-channel handoff. With multichannel
	// enabled, a "not found locally" result must NOT fall back to loading a
	// possibly-stale offline copy from this process's own DB connection -
	// that copy could belong to a player who is actually online on another
	// channel right now (docs/multichannel/CROSS_PROCESS_DB_ROW_HANDOFF.md
	// §0). With multichannel disabled, this is exactly today's existing
	// allowOffline=true behavior, completely unchanged.
	const bool allowOfflineLocalLoad = !g_clusterHandoffRuntime().isEnabled();
	const auto &player = g_game().getPlayerByName(receiver, allowOfflineLocalLoad);
	std::string writer;
	time_t date = getTimeNow();
	std::string text;
	if (item && item->getID() == ITEM_LETTER && !item->getAttribute<std::string>(ItemAttribute_t::WRITER).empty()) {
		writer = item->getAttribute<std::string>(ItemAttribute_t::WRITER);
		date = item->getAttribute<time_t>(ItemAttribute_t::DATE);
		text = item->getAttribute<std::string>(ItemAttribute_t::TEXT);
	}
	if (player && item) {
		const auto &playerInbox = player->getInbox();
		const auto &itemParent = item->getParent();
		if (g_game().internalMoveItem(itemParent, playerInbox, INDEX_WHEREEVER, item, item->getItemCount(), nullptr, FLAG_NOLIMIT) == RETURNVALUE_NOERROR) {
			const auto &newItem = g_game().transformItem(item, item->getID() + 1);
			if (newItem && newItem->getID() == ITEM_LETTER_STAMPED && !writer.empty()) {
				newItem->setAttribute(ItemAttribute_t::WRITER, writer);
				newItem->setAttribute(ItemAttribute_t::DATE, date);
				newItem->setAttribute(ItemAttribute_t::TEXT, text);
			}
			if (player->isOnline()) {
				player->onReceiveMail();
			} else {
				g_saveManager().savePlayer(player);
			}
			return true;
		}
		return false;
	}

	if (!item || !g_clusterHandoffRuntime().isEnabled()) {
		// Either genuinely no such recipient (single-channel mode already
		// ruled that out above via allowOfflineLocalLoad=true), or
		// multichannel is disabled and there is nothing else to try.
		return false;
	}

	return sendItemAcrossCluster(item, receiver, writer, date, text);
}

bool Mailbox::sendItemAcrossCluster(const std::shared_ptr<Item> &item, const std::string &receiver, const std::string &writer, time_t date, const std::string &text) const {
	const uint32_t recipientGuid = IOLoginData::getGuidByName(receiver);
	if (recipientGuid == 0) {
		// No such player - matches today's behavior when getPlayerByName
		// cannot find or load the name at all.
		return false;
	}

	multichannel::MailDeliveryPayload payload;
	payload.itemId = item->getID();
	payload.itemCount = item->getItemCount();
	payload.writer = writer;
	payload.writtenDate = static_cast<int64_t>(date);
	payload.text = text;

	// Same primitive IOLoginDataSave::saveItems already uses per-item, hex-
	// encoded for safe storage in the payload TEXT column (design doc §5).
	PropWriteStream propWriteStream;
	item->serializeAttr(propWriteStream);
	std::size_t attributesSize = 0;
	const char* attributes = propWriteStream.getStream(attributesSize);
	payload.itemAttributesHex = multichannel::hexEncode(std::string(attributes, attributesSize));

	ClusterPendingOperationRecord record;
	record.operationId = multichannel::generateRandomOperationId();
	record.recordKind = multichannel::RecordKindPlayerInbox;
	record.recordId = static_cast<int32_t>(recipientGuid);
	record.operationType = "DELIVER_MAIL_ITEM";
	record.payload = multichannel::serializeMailDeliveryPayload(payload);
	record.enqueuedByChannelId = g_clusterHandoffRuntime().getThisChannelId();
	record.createdAtMs = multichannel::wallClockMs();

	MailDeliveryOperationHandler handler;
	const auto outcome = g_clusterHandoffRuntime().enqueueAndTryApplyNow(record, record.createdAtMs, handler);

	if (outcome == ClusterRecordHandoffOutcome::NotEnqueued || outcome == ClusterRecordHandoffOutcome::EnqueuedButFailedDefinitively) {
		// Not safely captured durably, or a definitive business rejection -
		// the item was never touched, exactly like today's "destination
		// rejected it" behavior: leave it where it is, do not silently drop.
		return false;
	}

	// Durably captured - either delivered synchronously just now, or
	// safely queued for a later sweep because this process is not (or
	// cannot currently confirm it is) the recipient's live owner. Either
	// way the item's fate is no longer this process's local state to keep -
	// remove it from wherever it currently sits (mirrors internalMoveItem's
	// removal-from-source above, which has no local destination to move
	// *into* here).
	g_game().internalRemoveItem(item, item->getItemCount());
	return true;
}

bool Mailbox::getReceiver(const std::shared_ptr<Item> &item, std::string &name) const {
	const std::shared_ptr<Container> &container = item->getContainer();
	if (container) {
		for (const std::shared_ptr<Item> &containerItem : container->getItemList()) {
			if (containerItem->getID() == ITEM_LABEL && getReceiver(containerItem, name)) {
				return true;
			}
		}
		return false;
	}

	const std::string &text = item->getAttribute<std::string>(ItemAttribute_t::TEXT);
	if (text.empty()) {
		return false;
	}

	name = getFirstLine(text);
	trimString(name);
	return true;
}

bool Mailbox::canSend(const std::shared_ptr<Item> &item) {
	return !item->hasOwner() && (item->getID() == ITEM_PARCEL || item->getID() == ITEM_LETTER);
}
