/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
	#include <string>
#endif

namespace multichannel {
	// Everything needed to reconstruct a mailed item on the applying
	// process, independent of which process enqueued it - design doc §6.1.
	// itemAttributesHex is the item's own Item::serializeAttr() byte stream
	// (the same primitive IOLoginDataSave::saveItems already uses per-item),
	// hex-encoded so it can safely live in cluster_pending_operations.payload
	// (a TEXT column - raw binary would risk charset/collation corruption,
	// confirmed by this project's own `attributes` columns on player_items/
	// player_inboxitems all being typed `blob`, never `text`).
	struct MailDeliveryPayload {
		uint16_t itemId = 0;
		uint16_t itemCount = 0;
		// Only set for a written letter (ITEM_LETTER with a WRITER attribute) -
		// mirrors Mailbox::sendItem's existing writer/date/text extraction.
		std::string writer;
		int64_t writtenDate = 0;
		std::string text;
		std::string itemAttributesHex;
	};

	// Pure, dependency-free (de)serialization to/from
	// ClusterPendingOperationRecord::payload - pipe-delimited, each field
	// hex-encoded so the delimiter can never appear inside a field's own
	// content (writer/text are user-authored and could otherwise contain
	// '|' or any other separator candidate). Exposed for unit testing.
	[[nodiscard]] std::string serializeMailDeliveryPayload(const MailDeliveryPayload &payload);
	[[nodiscard]] std::optional<MailDeliveryPayload> deserializeMailDeliveryPayload(const std::string &payload);

	// Shared byte-exact hex codec, one implementation for every call site
	// that needs to fill/read itemAttributesHex: the enqueue side
	// (Mailbox::sendItem, hex-encoding Item::serializeAttr's raw byte
	// stream) and the apply side (MailDeliveryOperationHandler, decoding it
	// back before Item::unserializeAttr). Also used internally by
	// serialize/deserialize above for writer/text.
	[[nodiscard]] std::string hexEncode(const std::string &raw);
	[[nodiscard]] std::optional<std::string> hexDecode(const std::string &hex);
} // namespace multichannel
