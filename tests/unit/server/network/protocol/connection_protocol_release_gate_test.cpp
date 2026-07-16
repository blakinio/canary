#include "server/network/connection/connection.hpp"

#include "game/scheduling/dispatcher.hpp"
#include "server/network/protocol/protocol.hpp"

#include <gtest/gtest.h>

namespace {
	struct SessionToken {
		uint64_t generation = 0;
	};

	struct ProtocolProbe {
		uint32_t parseCount = 0;
		uint32_t releaseCount = 0;
		uint8_t parsedOpcode = 0;
		bool connectionAliveDuringParse = false;
	};

	class LifetimeTestProtocol final : public Protocol {
	public:
		LifetimeTestProtocol(const Connection_ptr &connection, uint64_t generation, std::shared_ptr<uint64_t> currentGeneration, std::shared_ptr<ProtocolProbe> probe) :
			Protocol(connection), generation(generation), currentGeneration(std::move(currentGeneration)), probe(std::move(probe)) { }

		void onRecvFirstMessage(NetworkMessage &) override { }

		void parsePacket(NetworkMessage &message) override {
			++probe->parseCount;
			probe->connectionAliveDuringParse = static_cast<bool>(getConnection());
			probe->parsedOpcode = message.getByte();

			// The queued callback carries session A's exact identity. It may finish
			// its own packet, but it cannot clear a replacement session B.
			if (*currentGeneration == generation) {
				*currentGeneration = 0;
			}
		}

		void release() override {
			++probe->releaseCount;
		}

	private:
		uint64_t generation;
		std::shared_ptr<uint64_t> currentGeneration;
		std::shared_ptr<ProtocolProbe> probe;
	};
}

TEST(ConnectionProtocolReleaseGateTest, ReleasesImmediatelyWithoutQueuedCallback) {
	ProtocolReleaseGate gate;

	EXPECT_EQ(ProtocolReleaseAction::ReleaseNow, gate.requestRelease());
	EXPECT_FALSE(gate.hasPendingCallback());
}

TEST(ConnectionProtocolReleaseGateTest, DefersReleaseUntilQueuedClientPacketCompletes) {
	ProtocolReleaseGate gate;

	gate.beginCallback();
	EXPECT_TRUE(gate.hasPendingCallback());
	EXPECT_EQ(ProtocolReleaseAction::DeferUntilCallbackCompletes, gate.requestRelease());

	// This is the deterministic dispatcher boundary: the already-received client
	// packet executes before ProtocolGame::release() is allowed to detach Player.
	EXPECT_TRUE(gate.completeCallback());
	EXPECT_FALSE(gate.hasPendingCallback());

	// Completion consumes the pending release exactly once.
	EXPECT_FALSE(gate.completeCallback());
}

TEST(ConnectionProtocolReleaseGateTest, QueuedLeaveGameOwnsMessageAndConnectionUntilDispatcherCompletion) {
	asio::io_service ioService;
	const auto currentGeneration = std::make_shared<uint64_t>(1);
	const auto probe = std::make_shared<ProtocolProbe>();

	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocolA = std::make_shared<LifetimeTestProtocol>(connection, 1, currentGeneration, probe);
	connection->attachProtocolForTest(protocolA);

	NetworkMessage leaveGame;
	leaveGame.addByte(0x14);
	leaveGame.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);

	connection->beginProtocolCallbackForTest();
	ASSERT_TRUE(protocolA->sendRecvMessageCallback(leaveGame));

	// Prove the dispatcher callback owns a message copy rather than Connection::m_msg
	// or this caller-owned object.
	leaveGame.getBuffer()[NetworkMessage::INITIAL_BUFFER_POSITION] = 0xFF;
	leaveGame.reset();

	std::weak_ptr<Connection> connectionWeak = connection;
	connection->close(true);
	connection.reset();
	protocolA.reset();

	// ConnectionManager ownership was removed by close(); only the queued callback's
	// exact shared_ptr keeps the Connection and its Protocol alive now.
	ASSERT_FALSE(connectionWeak.expired());

	// Simulate replacement session B before stale A executes. The exact A callback
	// may parse once but must not clear B.
	*currentGeneration = 2;
	g_dispatcher().executeSerialEventsForTest();

	EXPECT_EQ(1, probe->parseCount);
	EXPECT_EQ(0x14, probe->parsedOpcode);
	EXPECT_TRUE(probe->connectionAliveDuringParse);
	EXPECT_EQ(2, *currentGeneration);
	EXPECT_EQ(0, probe->releaseCount);

	// resumeWork() queued release only after parsePacket completed. Drain that exact
	// release and prove both parse and release remain one-shot.
	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, probe->parseCount);
	EXPECT_EQ(1, probe->releaseCount);

	g_dispatcher().executeSerialEventsForTest();
	EXPECT_EQ(1, probe->parseCount);
	EXPECT_EQ(1, probe->releaseCount);
	EXPECT_TRUE(connectionWeak.expired());
}

TEST(ConnectionProtocolReleaseGateTest, StaleSessionCompletionCannotClearReplacementSession) {
	ProtocolReleaseGate sessionAGate;
	const auto sessionA = std::make_shared<SessionToken>(SessionToken { .generation = 1 });
	const auto sessionB = std::make_shared<SessionToken>(SessionToken { .generation = 2 });
	std::shared_ptr<SessionToken> currentSession = sessionA;
	bool sessionARemoved = false;

	// A. Session A has one received packet queued on the dispatcher.
	sessionAGate.beginCallback();

	// B/C. Its transport closes, but release is held until the queued leave-game
	// callback has completed. No sleep or retry window is involved.
	EXPECT_EQ(ProtocolReleaseAction::DeferUntilCallbackCompletes, sessionAGate.requestRelease());
	ASSERT_TRUE(sessionAGate.completeCallback());

	// D/E. The exact A session is removed and B becomes current.
	if (currentSession == sessionA) {
		sessionARemoved = true;
		currentSession.reset();
	}
	ASSERT_TRUE(sessionARemoved);
	currentSession = sessionB;

	// F/G. A delayed callback carries A's exact identity. It cannot mutate B.
	const auto staleSessionACallback = [&] {
		if (currentSession == sessionA) {
			currentSession.reset();
		}
	};
	staleSessionACallback();

	ASSERT_TRUE(currentSession);
	EXPECT_EQ(sessionB, currentSession);
	EXPECT_EQ(2, currentSession->generation);
}
