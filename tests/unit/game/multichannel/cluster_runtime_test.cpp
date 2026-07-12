/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_runtime.hpp"

#include "../../../shared/game/multichannel/fake_cluster_session_repository.hpp"
#include "../../../shared/game/multichannel/fake_redis_client.hpp"

#include <gtest/gtest.h>
#include <memory>

class ClusterRuntimeTest : public ::testing::Test {
protected:
	void TearDown() override {
		ClusterRuntime::getInstance().resetForTesting();
	}
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

	// leaseTtlMs=1000, heartbeatIntervalMs=200: with no successful renew
	// since acquire at 10000, the lease's own expiry (11000) is within one
	// heartbeat interval by 10800 - integrity must win over availability
	// even though the 500ms failureGracePeriodMs alone hasn't elapsed here.
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
