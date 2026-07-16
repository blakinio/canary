/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/mail_delivery_payload.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <charconv>
	#include <iomanip>
	#include <sstream>
	#include <vector>
#endif

std::string multichannel::hexEncode(const std::string &raw) {
	static constexpr char digits[] = "0123456789abcdef";
	std::string out;
	out.reserve(raw.size() * 2);
	for (const unsigned char byte : raw) {
		out.push_back(digits[byte >> 4]);
		out.push_back(digits[byte & 0x0F]);
	}
	return out;
}

std::optional<std::string> multichannel::hexDecode(const std::string &hex) {
	if (hex.size() % 2 != 0) {
		return std::nullopt;
	}
	std::string out;
	out.reserve(hex.size() / 2);
	for (std::size_t i = 0; i < hex.size(); i += 2) {
		unsigned int byte = 0;
		const auto result = std::from_chars(hex.data() + i, hex.data() + i + 2, byte, 16);
		if (result.ec != std::errc {}) {
			return std::nullopt;
		}
		out.push_back(static_cast<char>(byte));
	}
	return out;
}

namespace {
	std::vector<std::string> splitPipe(const std::string &value) {
		std::vector<std::string> fields;
		std::size_t start = 0;
		while (true) {
			const auto pos = value.find('|', start);
			if (pos == std::string::npos) {
				fields.push_back(value.substr(start));
				break;
			}
			fields.push_back(value.substr(start, pos - start));
			start = pos + 1;
		}
		return fields;
	}

	template <typename T>
	std::optional<T> parseInteger(const std::string &field) {
		T value {};
		const auto result = std::from_chars(field.data(), field.data() + field.size(), value);
		if (result.ec != std::errc {} || result.ptr != field.data() + field.size()) {
			return std::nullopt;
		}
		return value;
	}
} // namespace

std::string multichannel::serializeMailDeliveryPayload(const MailDeliveryPayload &payload) {
	std::ostringstream stream;
	stream << payload.itemId << '|'
		   << payload.itemCount << '|'
		   << hexEncode(payload.writer) << '|'
		   << payload.writtenDate << '|'
		   << hexEncode(payload.text) << '|'
		   << payload.itemAttributesHex;
	return stream.str();
}

std::optional<multichannel::MailDeliveryPayload> multichannel::deserializeMailDeliveryPayload(const std::string &payload) {
	const auto fields = splitPipe(payload);
	if (fields.size() != 6) {
		return std::nullopt;
	}

	const auto itemId = parseInteger<uint16_t>(fields[0]);
	const auto itemCount = parseInteger<uint16_t>(fields[1]);
	const auto writer = hexDecode(fields[2]);
	const auto writtenDate = parseInteger<int64_t>(fields[3]);
	const auto text = hexDecode(fields[4]);
	// itemAttributesHex (fields[5]) is stored and returned as-is (already
	// hex, produced directly from the item's own attribute byte stream) -
	// not decoded here, the caller decodes it only when actually
	// reconstructing an Item, which this pure module has no dependency on.

	if (!itemId.has_value() || !itemCount.has_value() || !writer.has_value() || !writtenDate.has_value() || !text.has_value()) {
		return std::nullopt;
	}

	MailDeliveryPayload result;
	result.itemId = *itemId;
	result.itemCount = *itemCount;
	result.writer = *writer;
	result.writtenDate = *writtenDate;
	result.text = *text;
	result.itemAttributesHex = fields[5];
	return result;
}
