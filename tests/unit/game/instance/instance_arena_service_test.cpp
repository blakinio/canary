/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_arena_service.hpp"

TEST(InstanceArenaServiceTest, ConfiguredRegionsAreTwoNonOverlappingSameSizeRegions) {
	const auto regions = InstanceArenaService::configuredRegions();
	ASSERT_EQ(2u, regions.size());

	for (const auto &region : regions) {
		EXPECT_TRUE(region.isValid());
	}

	const auto width = [](const InstanceMapRegion &region) {
		return static_cast<int>(region.maxX) - static_cast<int>(region.minX);
	};
	const auto height = [](const InstanceMapRegion &region) {
		return static_cast<int>(region.maxY) - static_cast<int>(region.minY);
	};
	EXPECT_EQ(width(regions[0]), width(regions[1]));
	EXPECT_EQ(height(regions[0]), height(regions[1]));
	EXPECT_EQ(regions[0].minZ, regions[1].minZ);
	EXPECT_EQ(regions[0].maxZ, regions[1].maxZ);

	EXPECT_FALSE(regions[0].overlaps(regions[1]));
	EXPECT_NE(regions[0].slot, regions[1].slot);
}

TEST(InstanceArenaServiceTest, CreateArenaReservesARegionAndActivatesImmediately) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto result = service.createArena();

	ASSERT_TRUE(result.ok);
	EXPECT_NE(InstanceId::Invalid, result.id);
	ASSERT_TRUE(service.getState(result.id).has_value());
	EXPECT_EQ(InstanceState::Active, *service.getState(result.id));
	ASSERT_TRUE(service.getRegion(result.id).has_value());
}

TEST(InstanceArenaServiceTest, TwoArenasGetDifferentConfiguredRegions) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto first = service.createArena();
	const auto second = service.createArena();

	ASSERT_TRUE(first.ok);
	ASSERT_TRUE(second.ok);
	ASSERT_TRUE(service.getRegion(first.id).has_value());
	ASSERT_TRUE(service.getRegion(second.id).has_value());
	EXPECT_NE(service.getRegion(first.id)->slot, service.getRegion(second.id)->slot);
	EXPECT_EQ(2u, service.activeArenaCount());
}

TEST(InstanceArenaServiceTest, CreateArenaFailsWithoutChangingStateWhenNoRegionIsFree) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	ASSERT_TRUE(service.createArena().ok);
	ASSERT_TRUE(service.createArena().ok);

	const auto third = service.createArena();
	EXPECT_FALSE(third.ok);
	EXPECT_EQ(InstanceId::Invalid, third.id);
	EXPECT_FALSE(third.error.empty());
	EXPECT_EQ(2u, service.activeArenaCount());
}

TEST(InstanceArenaServiceTest, CloseArenaReleasesTheRegionForReuse) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto first = service.createArena();
	ASSERT_TRUE(first.ok);

	EXPECT_TRUE(service.closeArena(first.id));
	EXPECT_EQ(InstanceState::Destroyed, *service.getState(first.id));

	const auto reused = service.createArena();
	EXPECT_TRUE(reused.ok);
}

TEST(InstanceArenaServiceTest, GetBinderReturnsABinderBoundToTheSameManager) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto result = service.createArena();
	ASSERT_TRUE(result.ok);

	EXPECT_TRUE(service.getBinder().bind(result.id, 1234));
	EXPECT_EQ(result.id, manager.getCreatureOwner(1234));
}
