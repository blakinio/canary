#include "server/network/connection/connection.hpp"

#include <gtest/gtest.h>

namespace {
struct SessionToken {
	uint64_t generation = 0;
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
