/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_leader_election.hpp"

#include "../../../shared/game/multichannel/fake_redis_client.hpp"

#include <atomic>
#include <gtest/gtest.h>
#include <set>
#include <thread>
#include <vector>

class ClusterLeaderElectionTest : public ::testing::Test {
protected:
	FakeRedisClient redisClient;
	ClusterLeaderElection election { redisClient };
};

TEST_F(ClusterLeaderElectionTest, FirstAcquireSucceedsWithFencingTokenOne) {
	const auto handle = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	EXPECT_TRUE(handle.acquired);
	EXPECT_EQ(1u, handle.fencingToken);
	EXPECT_FALSE(handle.sessionId.empty());
}

TEST_F(ClusterLeaderElectionTest, SecondAcquireWhileHeldIsRejected) {
	const auto first = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(first.acquired);

	const auto second = election.acquire("market.expire", 2, "instance-2", 30000, 1500);
	EXPECT_FALSE(second.acquired);
	EXPECT_EQ(first.sessionId, second.currentHolderSessionId);
	EXPECT_EQ(first.fencingToken, second.currentHolderFencingToken);
}

TEST_F(ClusterLeaderElectionTest, DifferentJobsDoNotContend) {
	const auto marketJob = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	const auto houseJob = election.acquire("house.rent", 1, "instance-1", 30000, 1000);
	EXPECT_TRUE(marketJob.acquired);
	EXPECT_TRUE(houseJob.acquired);
}

TEST_F(ClusterLeaderElectionTest, RenewByOwnerSucceedsAndKeepsSameFencingToken) {
	const auto handle = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(handle.acquired);

	EXPECT_TRUE(election.renew("market.expire", handle.sessionId, 30000, 5000));
	EXPECT_TRUE(election.isFencingTokenCurrent("market.expire", handle.fencingToken));
}

TEST_F(ClusterLeaderElectionTest, RenewByNonOwnerFails) {
	const auto handle = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(handle.acquired);

	EXPECT_FALSE(election.renew("market.expire", "not-the-real-session-id", 30000, 5000));
}

TEST_F(ClusterLeaderElectionTest, RenewAfterExpiryFailsAndDoesNotResurrectLeadership) {
	const auto handle = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(handle.acquired);

	// now = 1000 + 30000 + 1 -> past expiry
	EXPECT_FALSE(election.renew("market.expire", handle.sessionId, 30000, 31001));
}

TEST_F(ClusterLeaderElectionTest, ReleaseByOwnerSucceeds) {
	const auto handle = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(handle.acquired);
	EXPECT_TRUE(election.release("market.expire", handle.sessionId));

	// Leadership is free again immediately.
	const auto reacquired = election.acquire("market.expire", 2, "instance-2", 30000, 1001);
	EXPECT_TRUE(reacquired.acquired);
}

TEST_F(ClusterLeaderElectionTest, ReleaseByNonOwnerFails) {
	const auto handle = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(handle.acquired);
	EXPECT_FALSE(election.release("market.expire", "not-the-real-session-id"));
}

TEST_F(ClusterLeaderElectionTest, FencingTokenIsMonotonicAcrossReleaseReacquireCycles) {
	const auto first = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(first.acquired);
	ASSERT_TRUE(election.release("market.expire", first.sessionId));

	const auto second = election.acquire("market.expire", 1, "instance-1", 30000, 2000);
	ASSERT_TRUE(second.acquired);
	ASSERT_TRUE(election.release("market.expire", second.sessionId));

	const auto third = election.acquire("market.expire", 1, "instance-1", 30000, 3000);
	ASSERT_TRUE(third.acquired);

	EXPECT_EQ(1u, first.fencingToken);
	EXPECT_EQ(2u, second.fencingToken);
	EXPECT_EQ(3u, third.fencingToken);
}

TEST_F(ClusterLeaderElectionTest, ExpiredLeaseCanBeReacquiredWithHigherFencingToken) {
	const auto first = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(first.acquired);

	// Never released - simulates a crashed zombie leader.
	const auto second = election.acquire("market.expire", 2, "instance-2", 30000, 31001);
	EXPECT_TRUE(second.acquired);
	EXPECT_GT(second.fencingToken, first.fencingToken);
}

TEST_F(ClusterLeaderElectionTest, StaleFencingTokenIsNoLongerCurrentAfterTakeover) {
	const auto first = election.acquire("market.expire", 1, "instance-1", 30000, 1000);
	ASSERT_TRUE(first.acquired);
	const auto second = election.acquire("market.expire", 2, "instance-2", 30000, 31001);
	ASSERT_TRUE(second.acquired);

	// The zombie leader from `first` must see its token as no longer
	// current - this is the check a job run must perform before any
	// side effect that must not happen twice (THREAT_MODEL.md T2).
	EXPECT_FALSE(election.isFencingTokenCurrent("market.expire", first.fencingToken));
	EXPECT_TRUE(election.isFencingTokenCurrent("market.expire", second.fencingToken));
}

TEST_F(ClusterLeaderElectionTest, ConcurrentAcquireHasExactlyOneWinner) {
	constexpr int racerCount = 16;
	std::vector<std::thread> threads;
	std::vector<LeaderElectionHandle> results(racerCount);
	std::atomic<int> readyCount { 0 };
	std::atomic<bool> go { false };

	for (int i = 0; i < racerCount; ++i) {
		threads.emplace_back([&, i] {
			readyCount.fetch_add(1);
			while (!go.load()) {
				std::this_thread::yield();
			}
			results[static_cast<std::size_t>(i)] = election.acquire("market.expire", i, "instance-" + std::to_string(i), 30000, 1000);
		});
	}

	while (readyCount.load() < racerCount) {
		std::this_thread::yield();
	}
	go.store(true);

	for (auto &thread : threads) {
		thread.join();
	}

	int acquiredCount = 0;
	std::set<uint64_t> fencingTokensSeen;
	for (const auto &result : results) {
		if (result.acquired) {
			++acquiredCount;
			fencingTokensSeen.insert(result.fencingToken);
		}
	}

	EXPECT_EQ(1, acquiredCount);
	EXPECT_EQ(1u, fencingTokensSeen.size());
	EXPECT_EQ(1u, *fencingTokensSeen.begin());
}

TEST(ClusterLeaderElectionKeyTest, LockKeyIsScopedPerJobName) {
	EXPECT_NE(ClusterLeaderElection::makeLockKey("market.expire"), ClusterLeaderElection::makeLockKey("house.rent"));
	EXPECT_EQ(ClusterLeaderElection::makeLockKey("market.expire"), ClusterLeaderElection::makeLockKey("market.expire"));
}
