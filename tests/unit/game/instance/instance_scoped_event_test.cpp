/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_scoped_event.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <vector>
#endif

namespace {

	std::vector<InstanceMapRegion> makeEventRegions(std::size_t count) {
		std::vector<InstanceMapRegion> regions;
		regions.reserve(count);
		for (std::size_t index = 0; index < count; ++index) {
			const auto minX = static_cast<uint16_t>(200 + index * 20);
			regions.push_back({
				.slot = toSlotId(static_cast<uint32_t>(index)),
				.minX = minX,
				.minY = 200,
				.minZ = 7,
				.maxX = static_cast<uint16_t>(minX + 9),
				.maxY = 209,
				.maxZ = 7,
				.name = "event-region-" + std::to_string(index),
			});
		}
		return regions;
	}

} // namespace

TEST(InstanceScopedEventTest, IsLiveOnlyWhileInstanceIsActive) {
	InstanceManager manager(makeEventRegions(1));
	const auto result = manager.createInstance({ .name = "scoped-event" });
	ASSERT_TRUE(result.ok);

	const InstanceScopedEvent event(manager, result.id);
	EXPECT_FALSE(event.isLive()) << "Creating is not yet safe to run gameplay logic against";

	ASSERT_TRUE(manager.activate(result.id));
	EXPECT_TRUE(event.isLive());

	ASSERT_TRUE(manager.close(result.id));
	EXPECT_FALSE(event.isLive()) << "Destroyed must never report live";
}

TEST(InstanceScopedEventTest, IsLiveIsFalseWhileClosingInsideCleanupCallback) {
	InstanceManager manager(makeEventRegions(1));
	const auto result = manager.createInstance({ .name = "scoped-event-closing" });
	ASSERT_TRUE(result.ok);
	ASSERT_TRUE(manager.activate(result.id));

	const InstanceScopedEvent event(manager, result.id);
	bool observedLiveDuringCleanup = true;
	manager.setCleanupCallback(result.id, [&](InstanceId, const InstanceMapRegion &) {
		observedLiveDuringCleanup = event.isLive();
	});

	ASSERT_TRUE(manager.close(result.id));
	EXPECT_FALSE(observedLiveDuringCleanup) << "Closing must already be unsafe to execute against, before Destroyed is reached";
}

TEST(InstanceScopedEventTest, IsLiveIsFalseForUnknownInstanceId) {
	InstanceManager manager(makeEventRegions(1));
	const InstanceScopedEvent event(manager, static_cast<InstanceId>(9999));
	EXPECT_FALSE(event.isLive());
}

TEST(InstanceScopedEventTest, RunIfLiveExecutesCallbackOnlyWhileActive) {
	InstanceManager manager(makeEventRegions(1));
	const auto result = manager.createInstance({ .name = "run-if-live" });
	ASSERT_TRUE(result.ok);
	const InstanceScopedEvent event(manager, result.id);

	int runCount = 0;
	EXPECT_FALSE(event.runIfLive([&] { ++runCount; })) << "Creating must not run the callback";
	EXPECT_EQ(0, runCount);

	ASSERT_TRUE(manager.activate(result.id));
	EXPECT_TRUE(event.runIfLive([&] { ++runCount; }));
	EXPECT_EQ(1, runCount);

	ASSERT_TRUE(manager.close(result.id));
	EXPECT_FALSE(event.runIfLive([&] { ++runCount; })) << "Destroyed must not run the callback";
	EXPECT_EQ(1, runCount);
}

TEST(InstanceScopedEventTest, GetInstanceIdReturnsTheBoundId) {
	InstanceManager manager(makeEventRegions(1));
	const auto result = manager.createInstance({ .name = "bound-id" });
	ASSERT_TRUE(result.ok);

	const InstanceScopedEvent event(manager, result.id);
	EXPECT_EQ(result.id, event.getInstanceId());
}
