/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_creature_binder.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <stdexcept>
	#include <vector>
#endif

namespace {

	struct RuntimeCreatureIdentity {
		uint32_t id = 0;

		[[nodiscard]] uint32_t getID() const noexcept {
			return id;
		}
	};

	std::vector<InstanceMapRegion> makeBinderRegions(std::size_t count) {
		std::vector<InstanceMapRegion> regions;
		regions.reserve(count);
		for (std::size_t index = 0; index < count; ++index) {
			const auto minX = static_cast<uint16_t>(800 + index * 20);
			regions.push_back({
				.slot = toSlotId(static_cast<uint32_t>(index)),
				.minX = minX,
				.minY = 800,
				.minZ = 7,
				.maxX = static_cast<uint16_t>(minX + 9),
				.maxY = 809,
				.maxZ = 7,
				.name = "binder-region-" + std::to_string(index),
			});
		}
		return regions;
	}

} // namespace

TEST(InstanceCreatureBinderTest, BindsRuntimeObjectUsingItsStableId) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "runtime-bind" });
	const RuntimeCreatureIdentity creature { .id = 101 };

	ASSERT_TRUE(instance.ok);
	EXPECT_TRUE(binder.bind(instance.id, creature));
	ASSERT_TRUE(binder.ownerOf(creature).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(creature));
	EXPECT_EQ((std::vector<InstanceCreatureId> { 101 }), manager.getRegisteredCreatureIds(instance.id));
}

TEST(InstanceCreatureBinderTest, DoesNotDependOnRuntimeObjectLifetimeAfterBind) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "identity-only" });
	ASSERT_TRUE(instance.ok);

	{
		const RuntimeCreatureIdentity shortLivedCreature { .id = 202 };
		ASSERT_TRUE(binder.bind(instance.id, shortLivedCreature));
	}

	ASSERT_TRUE(binder.ownerOf(202).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(202));
	EXPECT_TRUE(binder.unbind(202));
	EXPECT_FALSE(binder.ownerOf(202).has_value());
}

TEST(InstanceCreatureBinderTest, RejectsInvalidUnknownClosingAndCrossInstanceBindings) {
	InstanceManager manager(makeBinderRegions(2));
	InstanceCreatureBinder binder(manager);
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	const RuntimeCreatureIdentity invalid {};
	const RuntimeCreatureIdentity creature { .id = 303 };

	EXPECT_FALSE(binder.bind(first.id, invalid));
	EXPECT_FALSE(binder.bind(static_cast<InstanceId>(9999), creature));
	ASSERT_TRUE(binder.bind(first.id, creature));
	EXPECT_FALSE(binder.bind(second.id, creature));

	EXPECT_THROW(manager.close(second.id), std::logic_error);
	const RuntimeCreatureIdentity closingCreature { .id = 304 };
	EXPECT_FALSE(binder.bind(second.id, closingCreature));
	EXPECT_FALSE(binder.ownerOf(closingCreature).has_value());
}

TEST(InstanceCreatureBinderTest, UnbindUsesAuthoritativeOwnerAndIsIdempotentSafe) {
	InstanceManager manager(makeBinderRegions(2));
	InstanceCreatureBinder binder(manager);
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	const RuntimeCreatureIdentity creature { .id = 404 };
	ASSERT_TRUE(binder.bind(first.id, creature));

	EXPECT_TRUE(binder.unbind(creature));
	EXPECT_FALSE(binder.unbind(creature));
	EXPECT_FALSE(binder.ownerOf(creature).has_value());
	EXPECT_EQ(0u, manager.registeredCreatureCount(first.id));
	EXPECT_EQ(0u, manager.registeredCreatureCount(second.id));
}

TEST(InstanceCreatureBinderTest, OwnedMasterPassesBoundaryToSummon) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "summons" });
	const RuntimeCreatureIdentity master { .id = 501 };
	const RuntimeCreatureIdentity summon { .id = 502 };
	ASSERT_TRUE(binder.bind(instance.id, master));

	EXPECT_TRUE(binder.inherit(master, summon));
	ASSERT_TRUE(binder.ownerOf(summon).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(summon));
	EXPECT_EQ(InstanceCreatureRelation::SameInstance, binder.relation(master, summon));
	EXPECT_TRUE(binder.canInteract(master, summon));
}

TEST(InstanceCreatureBinderTest, CrossInstanceMasterAssignmentFailsWithoutMutation) {
	InstanceManager manager(makeBinderRegions(2));
	InstanceCreatureBinder binder(manager);
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	const RuntimeCreatureIdentity master { .id = 601 };
	const RuntimeCreatureIdentity summon { .id = 602 };
	ASSERT_TRUE(binder.bind(first.id, master));
	ASSERT_TRUE(binder.bind(second.id, summon));

	EXPECT_FALSE(binder.inherit(master, summon));
	EXPECT_EQ(first.id, *binder.ownerOf(master));
	EXPECT_EQ(second.id, *binder.ownerOf(summon));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, binder.relation(master, summon));
	EXPECT_FALSE(binder.canInteract(master, summon));
}

TEST(InstanceCreatureBinderTest, NormalWorldObjectsKeepExistingInteractionBehavior) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const RuntimeCreatureIdentity master { .id = 701 };
	const RuntimeCreatureIdentity summon { .id = 702 };

	EXPECT_TRUE(binder.inherit(master, summon));
	EXPECT_FALSE(binder.ownerOf(master).has_value());
	EXPECT_FALSE(binder.ownerOf(summon).has_value());
	EXPECT_EQ(InstanceCreatureRelation::SameWorld, binder.relation(master, summon));
	EXPECT_TRUE(binder.canInteract(master, summon));
}

TEST(InstanceCreatureBinderTest, ClosingOwnerFailsClosedForRuntimeObjects) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "closing" });
	const RuntimeCreatureIdentity first { .id = 801 };
	const RuntimeCreatureIdentity second { .id = 802 };
	ASSERT_TRUE(binder.bind(instance.id, first));
	ASSERT_TRUE(binder.bind(instance.id, second));

	EXPECT_THROW(manager.close(instance.id), std::logic_error);
	EXPECT_EQ(InstanceState::Closing, *manager.getState(instance.id));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, binder.relation(first, second));
	EXPECT_FALSE(binder.canInteract(first, second));
}
