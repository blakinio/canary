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

TEST(InstanceArenaServiceTest, EnterArenaReturnsAnEntryPositionInsideTheReservedRegion) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	constexpr Position returnPosition { 100, 100, 7 };

	const auto entered = service.enterArena(1, returnPosition);

	ASSERT_TRUE(entered.ok);
	EXPECT_TRUE(service.hasActiveSession(1));
	// Entry position must be one configured region's minX/minY/minZ corner.
	bool matchedARegion = false;
	for (const auto &configured : InstanceArenaService::configuredRegions()) {
		if (entered.entryPosition.x == configured.minX && entered.entryPosition.y == configured.minY && entered.entryPosition.z == configured.minZ) {
			matchedARegion = true;
		}
	}
	EXPECT_TRUE(matchedARegion);
}

TEST(InstanceArenaServiceTest, EnterArenaFailsWhenPlayerAlreadyHasASession) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	constexpr Position returnPosition { 100, 100, 7 };

	ASSERT_TRUE(service.enterArena(1, returnPosition).ok);
	const auto second = service.enterArena(1, returnPosition);

	EXPECT_FALSE(second.ok);
	EXPECT_FALSE(second.error.empty());
	EXPECT_EQ(1u, service.activeArenaCount()) << "the failed second enter must not create a stray instance";
}

TEST(InstanceArenaServiceTest, EnterArenaFailsWithoutASessionWhenNoRegionIsFree) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	constexpr Position returnPosition { 100, 100, 7 };

	ASSERT_TRUE(service.enterArena(1, returnPosition).ok);
	ASSERT_TRUE(service.enterArena(2, returnPosition).ok);

	const auto third = service.enterArena(3, returnPosition);
	EXPECT_FALSE(third.ok);
	EXPECT_FALSE(service.hasActiveSession(3));
}

TEST(InstanceArenaServiceTest, LeaveArenaReturnsSavedPositionWithoutReleasingTheRegion) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	constexpr Position returnPosition { 123, 456, 7 };

	ASSERT_TRUE(service.enterArena(1, returnPosition).ok);
	const auto left = service.leaveArena(1);

	ASSERT_TRUE(left.ok);
	EXPECT_EQ(returnPosition, left.returnPosition);
	EXPECT_TRUE(service.hasActiveSession(1)) << "leaving must not close the arena";
	EXPECT_EQ(1u, service.activeArenaCount());
}

TEST(InstanceArenaServiceTest, LeaveArenaFailsWithoutAnActiveSession) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto left = service.leaveArena(999);
	EXPECT_FALSE(left.ok);
	EXPECT_FALSE(left.error.empty());
}

TEST(InstanceArenaServiceTest, CloseArenaForPlayerEvacuatesAndReleasesTheRegion) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	constexpr Position returnPosition { 321, 654, 7 };

	ASSERT_TRUE(service.enterArena(1, returnPosition).ok);
	const auto closed = service.closeArenaForPlayer(1);

	ASSERT_TRUE(closed.ok);
	EXPECT_EQ(returnPosition, closed.evacuationPosition);
	EXPECT_FALSE(service.hasActiveSession(1));
	EXPECT_EQ(0u, service.activeArenaCount());

	// The region must be reusable immediately after a clean close.
	const auto reentered = service.enterArena(1, returnPosition);
	EXPECT_TRUE(reentered.ok);
}

TEST(InstanceArenaServiceTest, CloseArenaForPlayerWorksAfterLeaveArenaToo) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	constexpr Position returnPosition { 321, 654, 7 };

	ASSERT_TRUE(service.enterArena(1, returnPosition).ok);
	ASSERT_TRUE(service.leaveArena(1).ok);

	const auto closed = service.closeArenaForPlayer(1);
	ASSERT_TRUE(closed.ok);
	EXPECT_EQ(returnPosition, closed.evacuationPosition);
	EXPECT_FALSE(service.hasActiveSession(1));
}

TEST(InstanceArenaServiceTest, CloseArenaForPlayerFailsWithoutAnActiveSession) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto closed = service.closeArenaForPlayer(999);
	EXPECT_FALSE(closed.ok);
	EXPECT_FALSE(closed.error.empty());
}

TEST(InstanceArenaServiceTest, TwoPlayersGetIndependentSessionsAndRegions) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	constexpr Position returnPositionOne { 100, 100, 7 };
	constexpr Position returnPositionTwo { 200, 200, 7 };

	const auto enteredOne = service.enterArena(1, returnPositionOne);
	const auto enteredTwo = service.enterArena(2, returnPositionTwo);

	ASSERT_TRUE(enteredOne.ok);
	ASSERT_TRUE(enteredTwo.ok);
	EXPECT_NE(enteredOne.entryPosition, enteredTwo.entryPosition);

	ASSERT_TRUE(service.closeArenaForPlayer(1).ok);
	EXPECT_TRUE(service.hasActiveSession(2)) << "closing one player's arena must not affect the other";
	EXPECT_EQ(1u, service.activeArenaCount());
}
