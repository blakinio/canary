/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_runtime.hpp"

#include "game/multichannel/channel_registry.hpp"
#include "game/multichannel/channel_runtime_registry.hpp"
#include "game/multichannel/wall_clock.hpp"

#include "../../../shared/game/multichannel/fake_cluster_session_repository.hpp"
#include "../../../shared/game/multichannel/fake_redis_client.hpp"
#include "injection_fixture.hpp"

#include <gtest/gtest.h>
#include <memory>

namespace {
	ChannelInfo makeChannel(int32_t id) {
		ChannelInfo channel;
		channel.id = id;
		channel.name = "Channel " + std::to_string(id);
		channel.pvpType = "no-pvp";
		channel.externalHost = "127.0.0.1";
		channel.gamePort = 7171 + id;
		channel.statusPort = 7271 + id;
		channel.enabled = true;
		return channel;
	}
} // namespace

class ClusterRuntimeTest : public ::testing::Test {
protected:
	void TearDown() override {
		ClusterRuntime::getInstance().resetForTesting();
	}

	InjectionFixture fixture_ {};
};

TEST_F(ClusterRuntimeTest, DisabledByDefaultIsPermissiveNoOp) {
	auto &runtime = ClusterRuntime::getInstance();
	EXPECT_FALSE(runtime.isEnabled());
	EXPECT_TRUE(runtime.isAcceptingNewSessions());
	EXPECT_TRUE(runtime.acquireForLogin(1, 1, 1, 1000).acquired);
}

TEST_F(ClusterRuntimeTest, SecondLoginForSameAccountIsRejectedWhileFirstIsOnline) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	EXPECT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	EXPECT_FALSE(runtime.acquireForLogin(42, 100, 2, 10010).acquired);
	EXPECT_EQ(1u, runtime.trackedCount());
}

TEST_F(ClusterRuntimeTest, CleanLogoutReleasesAndAllowsReacquire) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	runtime.releaseForLogout(42, 10010);
	EXPECT_EQ(0u, runtime.trackedCount());
	EXPECT_TRUE(runtime.acquireForLogin(42, 100, 1, 10020).acquired);
}

TEST_F(ClusterRuntimeTest, GetTrackedSessionInfoReflectsTheAcquiredHandle) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	EXPECT_FALSE(runtime.getTrackedSessionInfo(42).has_value());

	const auto handle = runtime.acquireForLogin(42, 100, 1, 10000);
	ASSERT_TRUE(handle.acquired);
	const auto info = runtime.getTrackedSessionInfo(42);
	ASSERT_TRUE(info.has_value());
	EXPECT_EQ(handle.sessionId, info->sessionId);
	EXPECT_EQ(handle.fencingToken, info->fencingToken);

	runtime.releaseForLogout(42, 10010);
	EXPECT_FALSE(runtime.getTrackedSessionInfo(42).has_value());
}

TEST_F(ClusterRuntimeTest, HealthyRenewKeepsSessionTracked) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	const auto expired = runtime.renewAllAndCollectExpired(10100);
	EXPECT_TRUE(expired.empty());
	EXPECT_EQ(1u, runtime.trackedCount());
}

TEST_F(ClusterRuntimeTest, LegitimateSupersessionExpiresImmediatelyWithNoGracePeriod) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);

	// Someone else takes the lease directly (bypassing this ClusterRuntime),
	// simulating a legitimate transfer once this process's lease has
	// expired on Redis's own clock.
	const auto stolen = fake->acquireLease(ClusterSessionManager::makeLockKey(42), "other-session", "2", "other-instance", 1000, 11000);
	ASSERT_TRUE(stolen.acquired);

	const auto expired = runtime.renewAllAndCollectExpired(11000);
	ASSERT_EQ(1u, expired.size());
	EXPECT_EQ(42, expired[0]);
	EXPECT_EQ(0u, runtime.trackedCount());
}

TEST_F(ClusterRuntimeTest, OutageBlocksNewLoginsImmediatelyButKeepsExistingSessionBriefly) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(7, 100, 1, 10000).acquired);
	fake->setHealthyForTesting(false);

	EXPECT_FALSE(runtime.isAcceptingNewSessions());
	EXPECT_FALSE(runtime.acquireForLogin(99, 200, 1, 10001).acquired);

	// A brief outage, well within both the grace period and the lease's
	// remaining validity, must not disconnect the already-online account.
	const auto stillOnline = runtime.renewAllAndCollectExpired(10050);
	EXPECT_TRUE(stillOnline.empty());
	EXPECT_EQ(1u, runtime.trackedCount());
}

TEST_F(ClusterRuntimeTest, OutageForcesDisconnectBeforeLeaseCouldBeLegallyStolen) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(7, 100, 1, 10000).acquired);
	fake->setHealthyForTesting(false);

	const auto forcedOut = runtime.renewAllAndCollectExpired(10850);
	ASSERT_EQ(1u, forcedOut.size());
	EXPECT_EQ(7, forcedOut[0]);
	EXPECT_EQ(0u, runtime.trackedCount());
}

// --- cluster_sessions DB defense-in-depth (docs/multichannel/ARCHITECTURE.md §5) ---

TEST_F(ClusterRuntimeTest, AcquireWritesRowToSessionRepository) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	auto repository = std::make_shared<FakeClusterSessionRepository>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500, repository);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	EXPECT_TRUE(repository->hasRow(42));
	EXPECT_EQ(1u, repository->rowCount());
}

TEST_F(ClusterRuntimeTest, CleanLogoutDeletesRowFromSessionRepository) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	auto repository = std::make_shared<FakeClusterSessionRepository>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500, repository);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	ASSERT_TRUE(repository->hasRow(42));

	runtime.releaseForLogout(42, 10010);
	EXPECT_FALSE(repository->hasRow(42));
}

TEST_F(ClusterRuntimeTest, RepositoryFailureOnAcquireRollsBackTheRedisLease) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	auto repository = std::make_shared<FakeClusterSessionRepository>();
	repository->setNextAcquireSucceedsForTesting(false);
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500, repository);

	const auto handle = runtime.acquireForLogin(42, 100, 1, 10000);
	EXPECT_FALSE(handle.acquired);
	EXPECT_EQ(0u, runtime.trackedCount());

	// The Redis lease must have been released again, not left dangling -
	// a subsequent acquire attempt (with the repository fixed) must succeed.
	repository->setNextAcquireSucceedsForTesting(true);
	EXPECT_TRUE(runtime.acquireForLogin(42, 100, 1, 10001).acquired);
}

TEST_F(ClusterRuntimeTest, HealthyRenewUpdatesRepositoryHeartbeat) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	auto repository = std::make_shared<FakeClusterSessionRepository>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500, repository);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	const auto expired = runtime.renewAllAndCollectExpired(10100);
	EXPECT_TRUE(expired.empty());
	EXPECT_TRUE(repository->hasRow(42));
}

TEST_F(ClusterRuntimeTest, OutageForcedDisconnectDeletesRepositoryRow) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	auto repository = std::make_shared<FakeClusterSessionRepository>();
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500, repository);

	ASSERT_TRUE(runtime.acquireForLogin(7, 100, 1, 10000).acquired);
	ASSERT_TRUE(repository->hasRow(7));
	fake->setHealthyForTesting(false);

	const auto forcedOut = runtime.renewAllAndCollectExpired(10850);
	ASSERT_EQ(1u, forcedOut.size());
	EXPECT_FALSE(repository->hasRow(7));
}

// --- Cross-cutting: renewAllAndCollectExpired also drives
// ChannelRuntimeRegistry (docs/multichannel/ARCHITECTURE.md §3.4). The
// existing tests above only ever check session-lease outcomes; the
// heartbeat-publishing side effect through the real call chain (as opposed
// to calling ChannelRuntimeRegistry directly, like channel_runtime_registry_
// test.cpp does) was previously untested. ---

TEST_F(ClusterRuntimeTest, RenewAllPublishesHeartbeatToRuntimeRegistry) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRegistry().setChannelsForTesting({ makeChannel(1) });
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	runtime.renewAllAndCollectExpired(10100);

	const auto availability = g_channelRuntimeRegistry().getAvailability(1, 0, multichannel::wallClockMs());
	EXPECT_TRUE(availability.known);
	EXPECT_TRUE(availability.online);
	EXPECT_EQ(1, availability.playersOnline);
}

TEST_F(ClusterRuntimeTest, RenewAllRecoversHeartbeatPublishingAfterRedisOutage) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRegistry().setChannelsForTesting({ makeChannel(1) });
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	runtime.renewAllAndCollectExpired(10100);
	EXPECT_TRUE(g_channelRuntimeRegistry().getAvailability(1, 0, multichannel::wallClockMs()).online);

	// Outage: publish/refresh fails, the fail-closed cache is cleared -
	// mirrors ChannelRuntimeRegistryTest.RedisOutageClearsPreviouslyFreshSnapshot
	// but driven through the real ClusterRuntime call chain this time.
	fake->setHealthyForTesting(false);
	runtime.renewAllAndCollectExpired(10150);
	EXPECT_FALSE(g_channelRuntimeRegistry().getAvailability(1, 0, multichannel::wallClockMs()).known);

	// Recovery: once Redis is reachable again, the very next cycle resumes
	// publishing cleanly - nothing about a merely-transient outage needs
	// explicit "reconnect" handling, since publishAndRefresh is called
	// unconditionally every cycle regardless of the previous outcome.
	fake->setHealthyForTesting(true);
	runtime.renewAllAndCollectExpired(10200);
	const auto recovered = g_channelRuntimeRegistry().getAvailability(1, 0, multichannel::wallClockMs());
	EXPECT_TRUE(recovered.known);
	EXPECT_TRUE(recovered.online);
}

// --- Graceful shutdown publishes OFFLINE immediately instead of leaving
// other channels/the login gateway to find out only once the heartbeat TTL
// elapses (indistinguishable from a crash until then). ---

TEST_F(ClusterRuntimeTest, PublishOfflineForShutdownMarksChannelOffline) {
	auto &runtime = ClusterRuntime::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRegistry().setChannelsForTesting({ makeChannel(1) });
	runtime.configure(fake, 1, "instance-A", 1000, 200, 500);

	ASSERT_TRUE(runtime.acquireForLogin(42, 100, 1, 10000).acquired);
	runtime.renewAllAndCollectExpired(10100);
	ASSERT_TRUE(g_channelRuntimeRegistry().getAvailability(1, 0, multichannel::wallClockMs()).online);

	runtime.publishOfflineForShutdown(multichannel::wallClockMs());
	EXPECT_FALSE(g_channelRuntimeRegistry().getAvailability(1, 0, multichannel::wallClockMs()).online);
}

TEST_F(ClusterRuntimeTest, PublishOfflineForShutdownIsNoOpWhenDisabled) {
	auto &runtime = ClusterRuntime::getInstance();
	ASSERT_FALSE(runtime.isEnabled());
	// Must not crash even though never configured - GAME_STATE_SHUTDOWN
	// calls this unconditionally regardless of multiChannelEnabled.
	runtime.publishOfflineForShutdown(multichannel::wallClockMs());
}
