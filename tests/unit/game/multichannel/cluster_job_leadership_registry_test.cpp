/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/multichannel/cluster_job_leadership_registry.hpp"

#include "../../../shared/game/multichannel/fake_redis_client.hpp"

#include <gtest/gtest.h>
#include <memory>

class ClusterJobLeadershipRegistryTest : public ::testing::Test {
protected:
	void TearDown() override {
		ClusterJobLeadershipRegistry::getInstance().resetForTesting();
	}
};

TEST_F(ClusterJobLeadershipRegistryTest, DisabledByDefaultNeverClaimsLeadership) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	EXPECT_FALSE(registry.isEnabled());
	EXPECT_FALSE(registry.isLeader("market.expire"));
}

TEST_F(ClusterJobLeadershipRegistryTest, FirstRenewOrAcquireClaimsLeadership) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	registry.configure(fake, 1, "instance-A");

	EXPECT_FALSE(registry.isLeader("market.expire"));
	registry.renewOrAcquire("market.expire", 30000, 1000);
	EXPECT_TRUE(registry.isLeader("market.expire"));
}

TEST_F(ClusterJobLeadershipRegistryTest, DifferentJobsAreIndependent) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	registry.configure(fake, 1, "instance-A");

	registry.renewOrAcquire("market.expire", 30000, 1000);
	EXPECT_TRUE(registry.isLeader("market.expire"));
	EXPECT_FALSE(registry.isLeader("house.rent"));
}

TEST_F(ClusterJobLeadershipRegistryTest, AnotherInstanceCannotClaimAnAlreadyHeldJob) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	registry.configure(fake, 1, "instance-A");
	registry.renewOrAcquire("market.expire", 30000, 1000);
	ASSERT_TRUE(registry.isLeader("market.expire"));

	// A second process (bypassing this registry) tries to take the same
	// job lease directly while it is still held and unexpired - it must
	// be rejected, exactly like a session lease would be.
	const auto stolen = fake->acquireLease(ClusterLeaderElection::makeLockKey("market.expire"), "other-session", "2", "other-instance", 30000, 1500);
	EXPECT_FALSE(stolen.acquired);
}

TEST_F(ClusterJobLeadershipRegistryTest, RepeatedRenewOrAcquireKeepsLeadershipAcrossCycles) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	registry.configure(fake, 1, "instance-A");

	registry.renewOrAcquire("market.expire", 30000, 1000);
	ASSERT_TRUE(registry.isLeader("market.expire"));

	registry.renewOrAcquire("market.expire", 30000, 10000);
	EXPECT_TRUE(registry.isLeader("market.expire"));
}

TEST_F(ClusterJobLeadershipRegistryTest, LosingTheLeaseAfterOutageStopsClaimingLeadership) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	registry.configure(fake, 1, "instance-A");

	registry.renewOrAcquire("market.expire", 30000, 1000);
	ASSERT_TRUE(registry.isLeader("market.expire"));

	fake->setHealthyForTesting(false);
	registry.renewOrAcquire("market.expire", 30000, 5000);
	EXPECT_FALSE(registry.isLeader("market.expire"));
}

TEST_F(ClusterJobLeadershipRegistryTest, RecoversLeadershipAfterOutageEnds) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	registry.configure(fake, 1, "instance-A");

	registry.renewOrAcquire("market.expire", 30000, 1000);
	fake->setHealthyForTesting(false);
	registry.renewOrAcquire("market.expire", 30000, 5000);
	ASSERT_FALSE(registry.isLeader("market.expire"));

	fake->setHealthyForTesting(true);
	registry.renewOrAcquire("market.expire", 30000, 6000);
	EXPECT_TRUE(registry.isLeader("market.expire"));
}

TEST_F(ClusterJobLeadershipRegistryTest, ResetForTestingClearsLeadership) {
	auto &registry = ClusterJobLeadershipRegistry::getInstance();
	auto fake = std::make_shared<FakeRedisClient>();
	registry.configure(fake, 1, "instance-A");
	registry.renewOrAcquire("market.expire", 30000, 1000);
	ASSERT_TRUE(registry.isLeader("market.expire"));

	registry.resetForTesting();
	EXPECT_FALSE(registry.isEnabled());
	EXPECT_FALSE(registry.isLeader("market.expire"));
}
