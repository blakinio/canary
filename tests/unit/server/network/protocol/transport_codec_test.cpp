#include "server/network/connection/connection.hpp"
#include "server/network/message/networkmessage.hpp"
#include "server/network/protocol/protocol.hpp"
#include "server/network/protocol/transport_codec.hpp"

#include "game/scheduling/dispatcher.hpp"

#include <gtest/gtest.h>

namespace {
	class TransportTestProtocol final : public Protocol {
	public:
		explicit TransportTestProtocol(const Connection_ptr &connection) :
			Protocol(connection) { }

		void onRecvFirstMessage(NetworkMessage &) override { }
		void parsePacket(NetworkMessage &) override { }
	};

	NetworkMessage makeSequenceFrame(uint32_t sequence, uint8_t opcode = 0x14) {
		NetworkMessage message;
		message.add<uint32_t>(sequence);
		message.addByte(opcode);
		message.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);
		return message;
	}

	void closeConnection(const Connection_ptr &connection) {
		connection->close(true);
		g_dispatcher().executeSerialEventsForTest();
	}
}

TEST(TransportCodecTest, SequenceMismatchDoesNotAdvanceAcceptedSequence) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<TransportTestProtocol>(connection);
	const auto &codec = TransportCodecs::currentGameSequence();

	auto mismatchFrame = makeSequenceFrame(2);
	const auto mismatch = codec.prepareInbound(*protocol, mismatchFrame);
	EXPECT_EQ(InboundTransportStatus::SequenceMismatch, mismatch.status);
	ASSERT_TRUE(mismatch.receivedSequence.has_value());
	ASSERT_TRUE(mismatch.expectedSequence.has_value());
	EXPECT_EQ(2, *mismatch.receivedSequence);
	EXPECT_EQ(1, *mismatch.expectedSequence);

	auto acceptedFrame = makeSequenceFrame(1);
	const auto accepted = codec.prepareInbound(*protocol, acceptedFrame);
	EXPECT_EQ(InboundTransportStatus::Accepted, accepted.status);
	EXPECT_TRUE(accepted.accepted());

	closeConnection(connection);
}

TEST(TransportCodecTest, ZeroSequenceDoesNotAdvanceAcceptedSequence) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<TransportTestProtocol>(connection);
	const auto &codec = TransportCodecs::currentGameSequence();

	auto zeroFrame = makeSequenceFrame(0);
	const auto zero = codec.prepareInbound(*protocol, zeroFrame);
	EXPECT_EQ(InboundTransportStatus::ZeroSequence, zero.status);
	ASSERT_TRUE(zero.expectedSequence.has_value());
	EXPECT_EQ(1, *zero.expectedSequence);

	auto acceptedFrame = makeSequenceFrame(1);
	EXPECT_EQ(InboundTransportStatus::Accepted, codec.prepareInbound(*protocol, acceptedFrame).status);

	closeConnection(connection);
}

TEST(TransportCodecTest, DuplicateSequenceDoesNotConsumeNextSequence) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<TransportTestProtocol>(connection);
	const auto &codec = TransportCodecs::currentGameSequence();

	auto firstFrame = makeSequenceFrame(1);
	EXPECT_EQ(InboundTransportStatus::Accepted, codec.prepareInbound(*protocol, firstFrame).status);

	auto duplicateFrame = makeSequenceFrame(1);
	const auto duplicate = codec.prepareInbound(*protocol, duplicateFrame);
	EXPECT_EQ(InboundTransportStatus::SequenceMismatch, duplicate.status);
	ASSERT_TRUE(duplicate.expectedSequence.has_value());
	EXPECT_EQ(2, *duplicate.expectedSequence);

	auto secondFrame = makeSequenceFrame(2);
	EXPECT_EQ(InboundTransportStatus::Accepted, codec.prepareInbound(*protocol, secondFrame).status);

	closeConnection(connection);
}

TEST(TransportCodecTest, MalformedFrameDoesNotAdvanceAcceptedSequence) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<TransportTestProtocol>(connection);
	const auto &codec = TransportCodecs::currentGameSequence();

	NetworkMessage malformedFrame;
	malformedFrame.addByte(0x14);
	malformedFrame.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);
	EXPECT_EQ(InboundTransportStatus::MalformedFrame, codec.prepareInbound(*protocol, malformedFrame).status);

	auto acceptedFrame = makeSequenceFrame(1);
	EXPECT_EQ(InboundTransportStatus::Accepted, codec.prepareInbound(*protocol, acceptedFrame).status);

	closeConnection(connection);
}
