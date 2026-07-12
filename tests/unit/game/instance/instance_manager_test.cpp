/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_manager.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <stdexcept>
	#include <thread>
	#include <vector>
#endif

namespace {

std::vector<InstanceMapRegion> makeRegions(std::size_t count) {
	std::vector<InstanceMapRegion> regions;
	regions.reserve(count);
	for (std::size_t index = 0; index < count; ++index) {
		const auto minX = static_cast<uint16_t>(100 + index * 20);
		regions.push_back({
			.slot = toSlotId(static_cast<uint32_t>(index)),
			.minX = minX,
			.minY = 100,
			.minZ = 7,
			.maxX = static_cast<uint16_t>(minX + 9),
			.maxY = 109,
			.maxZ = 7,
			.name = "region-" + std::to_string(index),
		});
	}
	return regions;
}

} // namespace

TEST(InstanceManagerTest, CreateReservesAConfiguredRegionAndStartsInCreatingState) {
	InstanceManager manager(makeRegions(4));
	const auto result = manager.createInstance({ .name = "test-dungeon" });

	ASSERT_TRUE(result.ok);
	EXPECT_NE(InstanceId::Invalid, result.id);
	ASSERT_TRUE(manager.getState(result.id).has_value());
	EXPECT_EQ(InstanceState::Creating, *manager.getState(result.id));
	ASSERT_TRUE(manager.getSlot(result.id).has_value());
	ASSERT_TRUE(manager.getRegion(result.id).has_value());
	EXPECT_EQ("region-0", manager.getRegion(result.id)->name);
	EXPECT_EQ(3u, manager.availableSlotCount());
	EXPECT_EQ(4u, manager.totalSlotCount());
}

TEST(InstanceManagerTest, ActivateMovesCreatingToActive) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "test" });

	EXPECT_TRUE(manager.activate(result.id));
	EXPECT_EQ(InstanceState::Active, *manager.getState(result.id));
}

TEST(InstanceManagerTest, ActivateFailsForUnknownOrAlreadyActiveInstance) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "test" });

	EXPECT_FALSE(manager.activate(static_cast<InstanceId>(9999)));

	ASSERT_TRUE(manager.activate(result.id));
	EXPECT_FALSE(manager.activate(result.id)) << "already Active, not Creating - re-activation must be rejected";
}

TEST(InstanceManagerTest, CloseReleasesTheRegionAndRunsCleanupExactlyOnce) {
	InstanceManager manager(makeRegions(2));
	const auto result = manager.createInstance({ .name = "test" });
	manager.activate(result.id);

	int cleanupCalls = 0;
	InstanceId cleanupId {};
	InstanceMapRegion cleanupRegion;
	manager.setCleanupCallback(result.id, [&](InstanceId id, const InstanceMapRegion &region) {
		++cleanupCalls;
		cleanupId = id;
		cleanupRegion = region;
	});

	const auto regionBeforeClose = *manager.getRegion(result.id);
	EXPECT_TRUE(manager.close(result.id));

	EXPECT_EQ(InstanceState::Destroyed, *manager.getState(result.id));
	EXPECT_EQ(1, cleanupCalls);
	EXPECT_EQ(result.id, cleanupId);
	EXPECT_EQ(regionBeforeClose.slot, cleanupRegion.slot);
	EXPECT_EQ(regionBeforeClose.name, cleanupRegion.name);
	EXPECT_EQ(2u, manager.availableSlotCount()) << "the region must be returned to the pool";
}

TEST(InstanceManagerTest, CloseIsIdempotent) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "test" });

	int cleanupCalls = 0;
	manager.setCleanupCallback(result.id, [&](InstanceId, const InstanceMapRegion &) { ++cleanupCalls; });

	EXPECT_TRUE(manager.close(result.id));
	EXPECT_TRUE(manager.close(result.id));
	EXPECT_TRUE(manager.close(result.id));

	EXPECT_EQ(1, cleanupCalls) << "closing an already-closed instance must not re-run cleanup";
	EXPECT_EQ(InstanceState::Destroyed, *manager.getState(result.id));
}

TEST(InstanceManagerTest, CleanupFailureQuarantinesTheRegion) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "dirty" });
	ASSERT_TRUE(result.ok);

	manager.setCleanupCallback(result.id, [](InstanceId, const InstanceMapRegion &) {
		throw std::runtime_error("synthetic cleanup failure");
	});

	EXPECT_THROW(manager.close(result.id), std::runtime_error);
	EXPECT_EQ(InstanceState::Closing, *manager.getState(result.id));
	EXPECT_EQ(0u, manager.availableSlotCount());

	const auto blocked = manager.createInstance({ .name = "must-not-reuse-dirty-region" });
	EXPECT_FALSE(blocked.ok);
}

TEST(InstanceManagerTest, CloseOfUnknownInstanceReturnsFalse) {
	InstanceManager manager(makeRegions(1));
	EXPECT_FALSE(manager.close(static_cast<InstanceId>(424242)));
}

TEST(InstanceManagerTest, CreateInstanceFailsOnceRegionPoolIsExhausted) {
	InstanceManager manager(makeRegions(2));
	const auto first = manager.createInstance({ .name = "a" });
	const auto second = manager.createInstance({ .name = "b" });
	const auto third = manager.createInstance({ .name = "c" });

	EXPECT_TRUE(first.ok);
	EXPECT_TRUE(second.ok);
	EXPECT_FALSE(third.ok);
	EXPECT_FALSE(third.error.empty());
	EXPECT_EQ(InstanceId::Invalid, third.id);
}

TEST(InstanceManagerTest, ClosingFreesTheSameRegionForReuse) {
	InstanceManager manager(makeRegions(1));
	const auto first = manager.createInstance({ .name = "a" });
	ASSERT_TRUE(first.ok);
	const auto firstRegion = *manager.getRegion(first.id);

	const auto blocked = manager.createInstance({ .name = "b" });
	ASSERT_FALSE(blocked.ok);

	ASSERT_TRUE(manager.close(first.id));

	const auto second = manager.createInstance({ .name = "b-retry" });
	ASSERT_TRUE(second.ok);
	ASSERT_TRUE(manager.getRegion(second.id).has_value());
	EXPECT_EQ(firstRegion.slot, manager.getRegion(second.id)->slot);
	EXPECT_EQ(firstRegion.name, manager.getRegion(second.id)->name);
}

TEST(InstanceManagerTest, InstancesWithoutATimeoutAreNeverAutoClosedBySweep) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "no-timeout" });

	const auto closedCount = manager.closeExpiredInstances(std::chrono::steady_clock::now() + std::chrono::hours(24));
	EXPECT_EQ(0u, closedCount);
	EXPECT_EQ(InstanceState::Creating, *manager.getState(result.id));
}

TEST(InstanceManagerTest, ExpiredInstancesAreClosedBySweepAndUnexpiredOnesAreNot) {
	InstanceManager manager(makeRegions(2));
	const auto shortLived = manager.createInstance({ .name = "short", .timeout = std::chrono::seconds(10) });
	const auto longLived = manager.createInstance({ .name = "long", .timeout = std::chrono::seconds(1000) });
	manager.activate(shortLived.id);
	manager.activate(longLived.id);

	const auto now = std::chrono::steady_clock::now();
	const auto closedCount = manager.closeExpiredInstances(now + std::chrono::seconds(20));

	EXPECT_EQ(1u, closedCount);
	EXPECT_EQ(InstanceState::Destroyed, *manager.getState(shortLived.id));
	EXPECT_EQ(InstanceState::Active, *manager.getState(longLived.id));
	EXPECT_EQ(1u, manager.availableSlotCount());
}

TEST(InstanceManagerTest, SweepIsIdempotentAndSafeToCallRepeatedly) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "short", .timeout = std::chrono::seconds(1) });

	int cleanupCalls = 0;
	manager.setCleanupCallback(result.id, [&](InstanceId, const InstanceMapRegion &) { ++cleanupCalls; });

	const auto future = std::chrono::steady_clock::now() + std::chrono::seconds(10);
	EXPECT_EQ(1u, manager.closeExpiredInstances(future));
	EXPECT_EQ(0u, manager.closeExpiredInstances(future)) << "already closed, must not be counted or re-closed again";
	EXPECT_EQ(1, cleanupCalls);
	EXPECT_EQ(1u, manager.availableSlotCount());
}

TEST(InstanceManagerTest, ActiveInstanceCountReflectsCreatingAndActiveOnly) {
	InstanceManager manager(makeRegions(3));
	const auto a = manager.createInstance({ .name = "a" });
	const auto b = manager.createInstance({ .name = "b" });
	manager.activate(a.id);

	EXPECT_EQ(2u, manager.activeInstanceCount());

	manager.close(b.id);
	EXPECT_EQ(1u, manager.activeInstanceCount());
}

TEST(InstanceManagerTest, ConcurrentCloseOfTheSameInstanceRunsCleanupExactlyOnce) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "concurrent" });
	manager.activate(result.id);

	std::atomic<int> cleanupCalls { 0 };
	manager.setCleanupCallback(result.id, [&](InstanceId, const InstanceMapRegion &) { ++cleanupCalls; });

	constexpr int attempts = 16;
	std::vector<std::thread> threads;
	threads.reserve(attempts);
	for (int i = 0; i < attempts; ++i) {
		threads.emplace_back([&manager, id = result.id] { manager.close(id); });
	}
	for (auto &thread : threads) {
		thread.join();
	}

	EXPECT_EQ(1, cleanupCalls.load());
	EXPECT_EQ(InstanceState::Destroyed, *manager.getState(result.id));
	EXPECT_EQ(1u, manager.availableSlotCount());
}

TEST(InstanceManagerTest, ConcurrentCreateNeverReservesTheSameRegionTwice) {
	constexpr std::size_t regionCount = 8;
	InstanceManager manager(makeRegions(regionCount));

	constexpr int attempts = 32;
	std::atomic<int> successCount { 0 };
	std::vector<std::thread> threads;
	threads.reserve(attempts);
	for (int i = 0; i < attempts; ++i) {
		threads.emplace_back([&manager, &successCount] {
			if (manager.createInstance({ .name = "concurrent" }).ok) {
				++successCount;
			}
		});
	}
	for (auto &thread : threads) {
		thread.join();
	}

	EXPECT_EQ(static_cast<int>(regionCount), successCount.load());
	EXPECT_EQ(0u, manager.availableSlotCount());
	EXPECT_EQ(regionCount, manager.activeInstanceCount());
}
