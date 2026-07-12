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

	std::vector<InstanceMapRegion> makeOwnershipPolicyRegions(std::size_t count) {
		std::vector<InstanceMapRegion> regions;
		regions.reserve(count);
		for (std::size_t index = 0; index < count; ++index) {
			const auto minX = static_cast<uint16_t>(500 + index * 20);
			regions.push_back({
				.slot = toSlotId(static_cast<uint32_t>(index)),
				.minX = minX,
				.minY = 500,
				.minZ = 7,
				.maxX = static_cast<uint16_t>(minX + 9),
				.maxY = 509,
				.maxZ = 7,
				.name = "ownership-policy-region-" + std::to_string(index),
			});
		}
		return regions;
	}

} // namespace

TEST(InstanceCreatureOwnershipPolicyTest, UnownedMasterAndSummonRemainInNormalWorld) {
	InstanceManager manager(makeOwnershipPolicyRegions(1));

	EXPECT_TRUE(manager.inheritCreatureOwnership(100, 200));
	EXPECT_FALSE(manager.getCreatureOwner(100).has_value());
	EXPECT_FALSE(manager.getCreatureOwner(200).has_value());
	EXPECT_EQ(InstanceCreatureRelation::SameWorld, manager.getCreatureRelation(100, 200));
	EXPECT_TRUE(manager.canCreaturesInteract(100, 200));
}

TEST(InstanceCreatureOwnershipPolicyTest, OwnedMasterRegistersSummonInTheSameInstance) {
	InstanceManager manager(makeOwnershipPolicyRegions(1));
	const auto instance = manager.createInstance({ .name = "summon-owner" });
	ASSERT_TRUE(instance.ok);
	ASSERT_TRUE(manager.registerCreature(instance.id, 100));

	EXPECT_TRUE(manager.inheritCreatureOwnership(100, 200));
	ASSERT_TRUE(manager.getCreatureOwner(200).has_value());
	EXPECT_EQ(instance.id, *manager.getCreatureOwner(200));
	EXPECT_EQ(2u, manager.registeredCreatureCount(instance.id));
	EXPECT_EQ(InstanceCreatureRelation::SameInstance, manager.getCreatureRelation(100, 200));
	EXPECT_TRUE(manager.canCreaturesInteract(100, 200));
}

TEST(InstanceCreatureOwnershipPolicyTest, SameOwnerInheritanceIsIdempotent) {
	InstanceManager manager(makeOwnershipPolicyRegions(1));
	const auto instance = manager.createInstance({ .name = "idempotent" });
	ASSERT_TRUE(manager.registerCreature(instance.id, 100));

	EXPECT_TRUE(manager.inheritCreatureOwnership(100, 200));
	EXPECT_TRUE(manager.inheritCreatureOwnership(100, 200));
	EXPECT_EQ(2u, manager.registeredCreatureCount(instance.id));
	EXPECT_EQ((std::vector<InstanceCreatureId> { 100, 200 }), manager.getRegisteredCreatureIds(instance.id));
}

TEST(InstanceCreatureOwnershipPolicyTest, CrossInstanceSummonOwnershipIsRejectedWithoutMutation) {
	InstanceManager manager(makeOwnershipPolicyRegions(2));
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	ASSERT_TRUE(manager.registerCreature(first.id, 100));
	ASSERT_TRUE(manager.registerCreature(second.id, 200));

	EXPECT_FALSE(manager.inheritCreatureOwnership(100, 200));
	EXPECT_EQ(first.id, *manager.getCreatureOwner(100));
	EXPECT_EQ(second.id, *manager.getCreatureOwner(200));
	EXPECT_EQ(1u, manager.registeredCreatureCount(first.id));
	EXPECT_EQ(1u, manager.registeredCreatureCount(second.id));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, manager.getCreatureRelation(100, 200));
	EXPECT_FALSE(manager.canCreaturesInteract(100, 200));
}

TEST(InstanceCreatureOwnershipPolicyTest, UnownedMasterCannotAdoptAnOwnedSummon) {
	InstanceManager manager(makeOwnershipPolicyRegions(1));
	const auto instance = manager.createInstance({ .name = "owned-summon" });
	ASSERT_TRUE(manager.registerCreature(instance.id, 200));

	EXPECT_FALSE(manager.inheritCreatureOwnership(100, 200));
	EXPECT_EQ(instance.id, *manager.getCreatureOwner(200));
	EXPECT_FALSE(manager.getCreatureOwner(100).has_value());
}

TEST(InstanceCreatureOwnershipPolicyTest, InvalidAndSelfInheritanceFailClosed) {
	InstanceManager manager(makeOwnershipPolicyRegions(1));

	EXPECT_FALSE(manager.inheritCreatureOwnership(INVALID_INSTANCE_CREATURE_ID, 200));
	EXPECT_FALSE(manager.inheritCreatureOwnership(100, INVALID_INSTANCE_CREATURE_ID));
	EXPECT_FALSE(manager.inheritCreatureOwnership(100, 100));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, manager.getCreatureRelation(INVALID_INSTANCE_CREATURE_ID, 100));
	EXPECT_FALSE(manager.canCreaturesInteract(INVALID_INSTANCE_CREATURE_ID, 100));
}

TEST(InstanceCreatureOwnershipPolicyTest, InteractionPolicySeparatesNormalWorldAndInstances) {
	InstanceManager manager(makeOwnershipPolicyRegions(2));
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	ASSERT_TRUE(manager.registerCreature(first.id, 101));
	ASSERT_TRUE(manager.registerCreature(first.id, 102));
	ASSERT_TRUE(manager.registerCreature(second.id, 201));

	EXPECT_EQ(InstanceCreatureRelation::SameWorld, manager.getCreatureRelation(301, 302));
	EXPECT_EQ(InstanceCreatureRelation::SameInstance, manager.getCreatureRelation(101, 102));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, manager.getCreatureRelation(101, 201));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, manager.getCreatureRelation(101, 301));

	EXPECT_TRUE(manager.canCreaturesInteract(301, 302));
	EXPECT_TRUE(manager.canCreaturesInteract(101, 102));
	EXPECT_FALSE(manager.canCreaturesInteract(101, 201));
	EXPECT_FALSE(manager.canCreaturesInteract(101, 301));
}

TEST(InstanceCreatureOwnershipPolicyTest, ClosingInstanceRejectsInheritanceAndInteractions) {
	InstanceManager manager(makeOwnershipPolicyRegions(1));
	const auto instance = manager.createInstance({ .name = "closing" });
	ASSERT_TRUE(manager.registerCreature(instance.id, 100));
	ASSERT_TRUE(manager.registerCreature(instance.id, 200));

	EXPECT_THROW(manager.close(instance.id), std::logic_error);
	ASSERT_EQ(InstanceState::Closing, *manager.getState(instance.id));

	EXPECT_FALSE(manager.inheritCreatureOwnership(100, 300));
	EXPECT_FALSE(manager.getCreatureOwner(300).has_value());
	EXPECT_EQ(InstanceCreatureRelation::Isolated, manager.getCreatureRelation(100, 200));
	EXPECT_FALSE(manager.canCreaturesInteract(100, 200));
}

TEST(InstanceCreatureOwnershipPolicyTest, ConcurrentInheritanceRegistersEachSummonOnce) {
	InstanceManager manager(makeOwnershipPolicyRegions(1));
	const auto instance = manager.createInstance({ .name = "concurrent-summons" });
	ASSERT_TRUE(manager.registerCreature(instance.id, 100));

	constexpr int summonCount = 32;
	std::atomic<int> successCount { 0 };
	std::vector<std::thread> threads;
	threads.reserve(summonCount);
	for (int index = 0; index < summonCount; ++index) {
		threads.emplace_back([&manager, &successCount, summonId = static_cast<InstanceCreatureId>(1000 + index)] {
			if (manager.inheritCreatureOwnership(100, summonId)) {
				++successCount;
			}
		});
	}
	for (auto &thread : threads) {
		thread.join();
	}

	EXPECT_EQ(summonCount, successCount.load());
	EXPECT_EQ(static_cast<std::size_t>(summonCount + 1), manager.registeredCreatureCount(instance.id));
}
