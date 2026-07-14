#include "server/network/connection/connection.hpp"
#include "server/network/message/networkmessage.hpp"
#include "server/network/protocol/protocolgame.hpp"
#include "server/network/protocol/transport_codec.hpp"

#include "creatures/players/player.hpp"
#include "game/scheduling/dispatcher.hpp"

#include <gtest/gtest.h>

namespace {
	NetworkMessage makeLeaveGameFrame(uint32_t sequence = 1) {
		NetworkMessage message;
		message.add<uint32_t>(sequence);
		message.addByte(0x14);
		message.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);
		return message;
	}

	NetworkMessage makePlainLeaveGamePacket() {
		NetworkMessage message;
		message.addByte(0x14);
		message.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);
		return message;
	}

	struct LeaveGameFixture {
		asio::io_service ioService;
		Connection_ptr connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
		ProtocolGame_ptr protocol = std::make_shared<ProtocolGame>(connection);
		std::shared_ptr<Player> player = std::make_shared<Player>(protocol);

		LeaveGameFixture() {
			connection->attachProtocolForTest(protocol);
			connection->setTransportCodec(TransportCodecs::currentGameSequence());
			protocol->attachPlayerForLeaveGameTest(player);
		}

		bool queueValidatedLeave() {
			connection->beginProtocolCallbackForTest();
			auto message = makeLeaveGameFrame();
			return protocol->onRecvMessage(message);
		}
	};
}

TEST(ProtocolGameLeaveGameTest, ReceivedLeaveOwnsExactObjectsUntilOneParseRemoveAndRelease) {
	LeaveGameFixture fixture;
	fixture.protocol->setLeaveGameRemoveCreatureForTest([](const std::shared_ptr<Player> &) { return true; });
	ASSERT_TRUE(fixture.queueValidatedLeave());

	std::weak_ptr<Connection> connectionWeak = fixture.connection;
	std::weak_ptr<ProtocolGame> protocolWeak = fixture.protocol;
	fixture.connection->close(true);
	fixture.connection.reset();
	fixture.protocol.reset();

	ASSERT_FALSE(connectionWeak.expired());
	ASSERT_FALSE(protocolWeak.expired());

	g_dispatcher().executeSerialEventsForTest();
	const auto afterDispatch = protocolWeak.lock();
	ASSERT_TRUE(afterDispatch);
	EXPECT_EQ(ClientLeaveGameState::Completed, afterDispatch->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, afterDispatch->getClientLeaveParseCountForTest());
	EXPECT_EQ(1, afterDispatch->getClientLeaveRemoveCountForTest());
	EXPECT_EQ(0, afterDispatch->getClientLeaveReleaseCountForTest());

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, afterDispatch->getClientLeaveParseCountForTest());
	EXPECT_EQ(1, afterDispatch->getClientLeaveRemoveCountForTest());
	EXPECT_EQ(1, afterDispatch->getClientLeaveReleaseCountForTest());

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, afterDispatch->getClientLeaveParseCountForTest());
	EXPECT_EQ(1, afterDispatch->getClientLeaveRemoveCountForTest());
	EXPECT_EQ(1, afterDispatch->getClientLeaveReleaseCountForTest());

	EXPECT_TRUE(connectionWeak.expired());
}

TEST(ProtocolGameLeaveGameTest, DuplicateCompletionDoesNotParseRemoveOrReleaseTwice) {
	LeaveGameFixture fixture;
	fixture.protocol->setLeaveGameRemoveCreatureForTest([](const std::shared_ptr<Player> &) { return true; });

	fixture.connection->beginProtocolCallbackForTest();
	auto first = makePlainLeaveGamePacket();
	ASSERT_TRUE(fixture.protocol->sendRecvMessageCallback(first));

	auto duplicate = makePlainLeaveGamePacket();
	EXPECT_FALSE(fixture.protocol->sendRecvMessageCallback(duplicate));

	fixture.connection->close(true);
	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(ClientLeaveGameState::Completed, fixture.protocol->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, fixture.protocol->getClientLeaveParseCountForTest());
	EXPECT_EQ(1, fixture.protocol->getClientLeaveRemoveCountForTest());

	g_dispatcher().executeSerialEventsForTest();
	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, fixture.protocol->getClientLeaveParseCountForTest());
	EXPECT_EQ(1, fixture.protocol->getClientLeaveRemoveCountForTest());
	EXPECT_EQ(1, fixture.protocol->getClientLeaveReleaseCountForTest());
}

TEST(ProtocolGameLeaveGameTest, StaleSessionACannotDetachOrRemoveActiveSessionB) {
	LeaveGameFixture sessionA;
	sessionA.protocol->setLeaveGameRemoveCreatureForTest([](const std::shared_ptr<Player> &) { return true; });
	ASSERT_TRUE(sessionA.queueValidatedLeave());

	std::weak_ptr<ProtocolGame> sessionAWeak = sessionA.protocol;
	sessionA.connection->close(true);
	sessionA.connection.reset();
	sessionA.protocol.reset();

	asio::io_service sessionBIoService;
	auto sessionBConnection = ConnectionManager::getInstance().createConnection(sessionBIoService, nullptr);
	auto sessionBProtocol = std::make_shared<ProtocolGame>(sessionBConnection);
	sessionBConnection->attachProtocolForTest(sessionBProtocol);
	sessionBConnection->setTransportCodec(TransportCodecs::currentGameSequence());
	sessionBProtocol->attachPlayerForLeaveGameTest(sessionA.player);
	sessionBProtocol->setLeaveGameRemoveCreatureForTest([](const std::shared_ptr<Player> &) { return true; });

	g_dispatcher().executeSerialEventsForTest();
	const auto staleA = sessionAWeak.lock();
	ASSERT_TRUE(staleA);
	EXPECT_EQ(ClientLeaveGameState::Rejected, staleA->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, staleA->getClientLeaveParseCountForTest());
	EXPECT_EQ(0, staleA->getClientLeaveRemoveCountForTest());

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, staleA->getClientLeaveReleaseCountForTest());

	sessionBConnection->beginProtocolCallbackForTest();
	auto sessionBLeave = makeLeaveGameFrame();
	ASSERT_TRUE(sessionBProtocol->onRecvMessage(sessionBLeave));
	g_dispatcher().executeSerialEventsForTest();

	EXPECT_EQ(ClientLeaveGameState::Completed, sessionBProtocol->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, sessionBProtocol->getClientLeaveParseCountForTest());
	EXPECT_EQ(1, sessionBProtocol->getClientLeaveRemoveCountForTest());

	sessionBConnection->close(true);
	g_dispatcher().executeSerialEventsForTest();
	g_dispatcher().executeSerialEventsForTest();
}

TEST(ProtocolGameLeaveGameTest, DeniedLogoutRemainsExplicitAndDoesNotCreateDetachedGhost) {
	LeaveGameFixture fixture;
	fixture.protocol->setLeaveGameDeniedForTest(true);
	ASSERT_TRUE(fixture.queueValidatedLeave());

	std::weak_ptr<ProtocolGame> protocolWeak = fixture.protocol;
	fixture.connection->close(true);
	fixture.connection.reset();
	fixture.protocol.reset();

	g_dispatcher().executeSerialEventsForTest();
	const auto deniedProtocol = protocolWeak.lock();
	ASSERT_TRUE(deniedProtocol);
	EXPECT_EQ(ClientLeaveGameState::Denied, deniedProtocol->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, deniedProtocol->getClientLeaveParseCountForTest());
	EXPECT_EQ(0, deniedProtocol->getClientLeaveRemoveCountForTest());
	EXPECT_EQ(0, deniedProtocol->getClientLeaveReleaseCountForTest());

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(ClientLeaveGameState::Denied, deniedProtocol->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, deniedProtocol->getClientLeaveReleaseCountForTest());
	EXPECT_FALSE(protocolWeak.expired());

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, deniedProtocol->getClientLeaveReleaseCountForTest());
}

TEST(ProtocolGameLeaveGameTest, RemoveFailureIsRejectedWithoutCreatingDetachedGhost) {
	LeaveGameFixture fixture;
	fixture.protocol->setLeaveGameRemoveCreatureForTest([](const std::shared_ptr<Player> &) { return false; });
	ASSERT_TRUE(fixture.queueValidatedLeave());

	std::weak_ptr<ProtocolGame> protocolWeak = fixture.protocol;
	fixture.connection->close(true);
	fixture.connection.reset();
	fixture.protocol.reset();

	g_dispatcher().executeSerialEventsForTest();
	const auto rejectedProtocol = protocolWeak.lock();
	ASSERT_TRUE(rejectedProtocol);
	EXPECT_EQ(ClientLeaveGameState::Rejected, rejectedProtocol->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, rejectedProtocol->getClientLeaveParseCountForTest());
	EXPECT_EQ(1, rejectedProtocol->getClientLeaveRemoveCountForTest());
	EXPECT_EQ(0, rejectedProtocol->getClientLeaveReleaseCountForTest());

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(ClientLeaveGameState::Rejected, rejectedProtocol->getClientLeaveGameStateForTest());
	EXPECT_EQ(1, rejectedProtocol->getClientLeaveReleaseCountForTest());
	EXPECT_FALSE(protocolWeak.expired());

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, rejectedProtocol->getClientLeaveReleaseCountForTest());
}
