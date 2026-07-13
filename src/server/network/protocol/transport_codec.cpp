/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "server/network/protocol/transport_codec.hpp"

#include "server/network/message/networkmessage.hpp"
#include "server/network/message/outputmessage.hpp"
#include "server/network/protocol/protocol.hpp"
#include "utils/tools.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <limits>
#endif

std::optional<uint16_t> TransportCodec::decodeBodySize(uint16_t rawLengthHeader) const {
	uint32_t size = rawLengthHeader;
	if (profile.outerLength == OuterLengthEncoding::ModernBlockCount) {
		size = (size * XTEA_MULTIPLE) + profile.modernLengthExtraBytes;
	}

	if (profile.id == TransportProfileId::CurrentGameSequence) {
		g_logger().info(
			"[CyclopediaE2E] decode body: rawHeader={} profile={} outer={} extra={} decoded={}",
			rawLengthHeader,
			static_cast<uint8_t>(profile.id),
			static_cast<uint8_t>(profile.outerLength),
			profile.modernLengthExtraBytes,
			size
		);
	}

	if (size == 0 || size > std::numeric_limits<uint16_t>::max()) {
		return std::nullopt;
	}

	return static_cast<uint16_t>(size);
}

void TransportCodec::encodeOutbound(Protocol &protocol, OutputMessage &msg) const {
	const bool compressed = msg.getLength() >= 128 && protocol.compression(msg, profile.compression);
	const uint32_t compressionSignal = compressed && profile.sequenceHighBitSignalsCompression ? (1U << 31) : 0;

	const auto writeOuterLength = [&msg, this] {
		if (profile.outerLength == OuterLengthEncoding::ModernBlockCount) {
			msg.writeMessageLength(profile.modernLengthExtraBytes);
		} else {
			msg.writeRawMessageLength();
		}
	};

	if (!protocol.encryptionEnabled) {
		writeOuterLength();
		return;
	}

	if (profile.encryptedPayload == EncryptedPayloadLayout::ModernPaddingByte) {
		msg.writePaddingAmount();
	} else if (profile.encryptedPayload == EncryptedPayloadLayout::LegacyInnerLength) {
		msg.writeLegacyInnerLength();
	}

	encryptXtea(protocol, msg);
	switch (profile.outboundChecksum) {
		case CHECKSUM_METHOD_NONE:
			writeOuterLength();
			break;
		case CHECKSUM_METHOD_ADLER32:
			msg.writeChecksum(adlerChecksum(msg.getOutputBuffer(), msg.getLength()));
			writeOuterLength();
			break;
		case CHECKSUM_METHOD_SEQUENCE:
			msg.writeChecksum(compressionSignal | (++protocol.serverSequenceNumber));
			writeOuterLength();
			if (protocol.serverSequenceNumber >= 0x7FFFFFFF) {
				protocol.serverSequenceNumber = 0;
			}
			break;
	}
}

bool TransportCodec::prepareInbound(Protocol &protocol, NetworkMessage &msg) const {
	if (profile.id == TransportProfileId::CurrentGameSequence) {
		const uint8_t* bytes = msg.getBuffer();
		g_logger().info(
			"[CyclopediaE2E] inbound frame before checksum: length={} position={} bytes={:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X} {:02X}",
			msg.getLength(),
			msg.getBufferPosition(),
			bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6],
			bytes[7], bytes[8], bytes[9], bytes[10], bytes[11], bytes[12], bytes[13]
		);
	}

	if (profile.inboundChecksum != CHECKSUM_METHOD_NONE) {
		const auto recvChecksum = msg.get<uint32_t>();
		if (profile.inboundChecksum == CHECKSUM_METHOD_SEQUENCE) {
			if (recvChecksum == 0) {
				g_logger().warn(
					"[TransportCodec::prepareInbound] rejected zero inbound sequence: length={} position={} currentSequence={}",
					msg.getLength(),
					msg.getBufferPosition(),
					protocol.clientSequenceNumber
				);
				return false;
			}

			const uint32_t checksum = ++protocol.clientSequenceNumber;
			if (protocol.clientSequenceNumber >= 0x7FFFFFFF) {
				protocol.clientSequenceNumber = 0;
			}

			if (recvChecksum != checksum) {
				g_logger().warn(
					"[TransportCodec::prepareInbound] rejected inbound sequence mismatch: received={} expected={} length={} position={}",
					recvChecksum,
					checksum,
					msg.getLength(),
					msg.getBufferPosition()
				);
				return false;
			}
		} else {
			uint32_t checksum;
			if (const int32_t len = msg.getLength() - msg.getBufferPosition();
			    len > 0) {
				checksum = adlerChecksum(msg.getBuffer() + msg.getBufferPosition(), len);
			} else {
				checksum = 0;
			}

			if (recvChecksum != checksum) {
				g_logger().warn(
					"[TransportCodec::prepareInbound] rejected Adler-32 mismatch: received={} expected={} length={} position={}",
					recvChecksum,
					checksum,
					msg.getLength(),
					msg.getBufferPosition()
				);
				return false;
			}
		}
	}

	if (protocol.encryptionEnabled && !decryptXtea(protocol, msg)) {
		g_logger().error("[TransportCodec::prepareInbound] - XTEA decrypt failed");
		return false;
	}

	return true;
}

bool TransportCodec::decryptXtea(Protocol &protocol, NetworkMessage &msg) const {
	const auto checksumLength = profile.inboundChecksum == CHECKSUM_METHOD_NONE ? HEADER_LENGTH : HEADER_LENGTH + CHECKSUM_LENGTH;
	if (msg.getLength() < checksumLength) {
		g_logger().error("[TransportCodec::decryptXtea] - message shorter than transport header: {} < {}", msg.getLength(), checksumLength);
		return false;
	}

	uint16_t msgLength = msg.getLength() - checksumLength;
	uint8_t* buffer = msg.getBuffer() + msg.getBufferPosition();
	if ((msgLength % XTEA_MULTIPLE) != 0) {
		g_logger().error("[TransportCodec::decryptXtea] - invalid block size: {}", msgLength);
		return false;
	}

	size_t messageLength = msgLength;
	protocol.XTEA_transform(buffer, messageLength, false);

	if (profile.encryptedPayload == EncryptedPayloadLayout::LegacyInnerLength) {
		const uint16_t innerLength = msg.get<uint16_t>();
		const uint16_t decryptedLength = innerLength + sizeof(uint16_t);
		if (decryptedLength > msgLength) {
			g_logger().error("[TransportCodec::decryptXtea] - invalid legacy inner length: {} > {}", decryptedLength, msgLength);
			return false;
		}

		msg.setLength(msg.getBufferPosition() + innerLength);
		return true;
	}

	uint8_t paddingSize = msg.getByte();
	if (paddingSize > messageLength) {
		g_logger().error("[TransportCodec::decryptXtea] - invalid modern padding: {} > {}", paddingSize, messageLength);
		return false;
	}

	uint16_t innerLength = messageLength - paddingSize;
	if (innerLength + paddingSize > msgLength) {
		g_logger().error("[TransportCodec::decryptXtea] - invalid modern inner length: {} + {} > {}", innerLength, paddingSize, msgLength);
		return false;
	}

	msg.setLength(messageLength - paddingSize);
	return true;
}

void TransportCodec::encryptXtea(Protocol &protocol, OutputMessage &msg) const {
	size_t paddingBytes = msg.getLength() % XTEA_MULTIPLE;
	if (paddingBytes != 0) {
		msg.addPaddingBytes(XTEA_MULTIPLE - paddingBytes);
	}

	uint8_t* buffer = msg.getOutputBuffer();
	size_t messageLength = msg.getLength();
	protocol.XTEA_transform(buffer, messageLength, true);
}

const TransportCodec &TransportCodecs::get(TransportProfileId id) {
	using enum TransportProfileId;
	switch (id) {
		case CurrentLogin:
			return currentLogin();
		case CurrentGameSequence:
			return currentGameSequence();
		case CurrentGamePlain:
			return currentGamePlain();
		case LegacyRawWithLoginHeader:
			return legacyRawWithLoginHeader();
		case LegacyClassic:
			return legacyClassic();
		default:
			return rawClientFirst();
	}
}

const TransportCodec &TransportCodecs::rawClientFirst() {
	static const TransportCodec codec(ProtocolProfileRegistry::getTransportProfile(TransportProfileId::RawClientFirst));
	return codec;
}

const TransportCodec &TransportCodecs::currentLogin() {
	static const TransportCodec codec(ProtocolProfileRegistry::getTransportProfile(TransportProfileId::CurrentLogin));
	return codec;
}

const TransportCodec &TransportCodecs::currentGameSequence() {
	static const TransportCodec codec(ProtocolProfileRegistry::getTransportProfile(TransportProfileId::CurrentGameSequence));
	return codec;
}

const TransportCodec &TransportCodecs::currentGamePlain() {
	static const TransportCodec codec(ProtocolProfileRegistry::getTransportProfile(TransportProfileId::CurrentGamePlain));
	return codec;
}

const TransportCodec &TransportCodecs::legacyRawWithLoginHeader() {
	static const TransportCodec codec(ProtocolProfileRegistry::getTransportProfile(TransportProfileId::LegacyRawWithLoginHeader));
	return codec;
}

const TransportCodec &TransportCodecs::legacyClassic() {
	static const TransportCodec codec(ProtocolProfileRegistry::getTransportProfile(TransportProfileId::LegacyClassic));
	return codec;
}
