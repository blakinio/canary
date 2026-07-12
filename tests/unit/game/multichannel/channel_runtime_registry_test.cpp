/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#include "game/multichannel/channel_runtime_registry.hpp"

#include "../../../shared/game/multichannel/fake_redis_client.hpp"

#include <gtest/gtest.h>
#include <memory>

namespace {
	ChannelRuntimeStatus makeStatus(int32_t channelId, int64_t nowMs, int32_t playersOnline = 0, std::string state = "ONLINE") {
		ChannelRuntimeStatus status;
		status.channelId = channelId;
		status.instanceId = "instance-" + std::to_string(channelId);
		status.nodeId = "node-" + std::to_string(channelId);
		status.startedAtMs = nowMs - 10000;
		status.lastHeartbeatMs = nowMs;
		status.status = std::move(state);
		status.playersOnline = playersOnline;
		status.buildSha = "build";
		status.mapHash = "map";
		status.dataHash = "data";
		return status;
	}

	ChannelInfo makeChannel(int32_t id, int32_t maxPlayers = 0) {
		ChannelInfo channel;
		channel.id = id;
		channel.name = "Channel " + std::to_string(id);
		channel.gamePort = 7171 + id;
		channel.statusPort = 7271 + id;
		channel.maxPlayers = maxPlayers;
		channel.sortOrder = id;
		return channel;
	}
} // namespace

class ChannelRuntimeRegistryTest : public ::testing::Test {
protected:
	void TearDown() override {
		g_channelRuntimeRegistry().resetForTesting();
	}
};

TEST_F(ChannelRuntimeRegistryTest, FreshOnlineHeartbeatIsOfferable) {
	constexpr int64_t nowMs = 100000;
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRuntimeRegistry().configure(fake, 1000);

	const auto own = makeStatus(1, nowMs, 12);
	ASSERT_TRUE(g_channelRuntimeRegistry().publishAndRefresh(own, 1000, { 1 }, nowMs));

	const auto availability = g_channelRuntimeRegistry().getAvailability(1, 100, nowMs);
	EXPECT_TRUE(availability.known);
	EXPECT_TRUE(availability.online);
	EXPECT_FALSE(availability.full);
	EXPECT_EQ(12, availability.playersOnline);
}

TEST_F(ChannelRuntimeRegistryTest, FullAndMaintenanceChannelsAreNotOffered) {
	constexpr int64_t nowMs = 200000;
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRuntimeRegistry().configure(fake, 1000);

	ASSERT_TRUE(fake->writeChannelRuntimeStatus(ChannelRuntimeRegistry::runtimeKey(2), makeStatus(2, nowMs, 50), 1000, nowMs));
	ASSERT_TRUE(fake->writeChannelRuntimeStatus(ChannelRuntimeRegistry::runtimeKey(3), makeStatus(3, nowMs, 0, "MAINTENANCE"), 1000, nowMs));
	ASSERT_TRUE(g_channelRuntimeRegistry().publishAndRefresh(makeStatus(1, nowMs), 1000, { 1, 2, 3 }, nowMs));

	const auto channels = g_channelRuntimeRegistry().getLoginListChannels({ makeChannel(1, 100), makeChannel(2, 50), makeChannel(3, 100) }, nowMs);
	ASSERT_EQ(1u, channels.size());
	EXPECT_EQ(1, channels.front().id);
	EXPECT_TRUE(g_channelRuntimeRegistry().getAvailability(2, 50, nowMs).full);
	EXPECT_FALSE(g_channelRuntimeRegistry().getAvailability(3, 100, nowMs).online);
}

TEST_F(ChannelRuntimeRegistryTest, CrashedChannelDisappearsAfterTtl) {
	constexpr int64_t firstHeartbeatMs = 300000;
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRuntimeRegistry().configure(fake, 1000);

	ASSERT_TRUE(fake->writeChannelRuntimeStatus(ChannelRuntimeRegistry::runtimeKey(2), makeStatus(2, firstHeartbeatMs), 1000, firstHeartbeatMs));
	ASSERT_TRUE(g_channelRuntimeRegistry().publishAndRefresh(makeStatus(1, firstHeartbeatMs), 1000, { 1, 2 }, firstHeartbeatMs));
	EXPECT_TRUE(g_channelRuntimeRegistry().getAvailability(2, 100, firstHeartbeatMs).online);

	const int64_t afterCrashMs = firstHeartbeatMs + 1001;
	ASSERT_TRUE(g_channelRuntimeRegistry().publishAndRefresh(makeStatus(1, afterCrashMs), 1000, { 1, 2 }, afterCrashMs));
	const auto crashed = g_channelRuntimeRegistry().getAvailability(2, 100, afterCrashMs);
	EXPECT_FALSE(crashed.known);
	EXPECT_FALSE(crashed.online);
}

TEST_F(ChannelRuntimeRegistryTest, RedisOutageClearsPreviouslyFreshSnapshot) {
	constexpr int64_t nowMs = 400000;
	auto fake = std::make_shared<FakeRedisClient>();
	g_channelRuntimeRegistry().configure(fake, 1000);

	ASSERT_TRUE(g_channelRuntimeRegistry().publishAndRefresh(makeStatus(1, nowMs), 1000, { 1 }, nowMs));
	ASSERT_TRUE(g_channelRuntimeRegistry().getAvailability(1, 100, nowMs).online);

	fake->setHealthyForTesting(false);
	EXPECT_FALSE(g_channelRuntimeRegistry().publishAndRefresh(makeStatus(1, nowMs + 100), 1000, { 1 }, nowMs + 100));
	const auto unavailable = g_channelRuntimeRegistry().getAvailability(1, 100, nowMs + 100);
	EXPECT_FALSE(unavailable.known);
	EXPECT_FALSE(unavailable.online);
}

TEST_F(ChannelRuntimeRegistryTest, LocallyStaleHeartbeatIsRejectedEvenBeforeRedisTtl) {
	constexpr int64_t heartbeatMs = 500000;
	g_channelRuntimeRegistry().setStatusesForTesting(1000, { makeStatus(1, heartbeatMs) });

	EXPECT_TRUE(g_channelRuntimeRegistry().getAvailability(1, 100, heartbeatMs + 1000).online);
	EXPECT_FALSE(g_channelRuntimeRegistry().getAvailability(1, 100, heartbeatMs + 1001).online);
}
