/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "creatures/monsters/monster.hpp"
#include "creatures/monsters/monsters.hpp"
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

	struct RuntimeSummonIdentity {
		uint32_t id = 0;

		[[nodiscard]] uint32_t getID() const noexcept {
			return id;
		}
	};

	std::shared_ptr<Monster> makeRuntimeMonster(const std::string &name) {
		const auto monsterType = std::make_shared<MonsterType>(name);
		const auto monster = std::make_shared<Monster>(monsterType);
		monster->setID();
		return monster;
	}

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
	const RuntimeCreatureIdentity secondOwnerCreature { .id = 305 };

	EXPECT_FALSE(binder.bind(first.id, invalid));
	EXPECT_FALSE(binder.bind(static_cast<InstanceId>(9999), creature));
	ASSERT_TRUE(binder.bind(first.id, creature));
	EXPECT_FALSE(binder.bind(second.id, creature));

	ASSERT_TRUE(binder.bind(second.id, secondOwnerCreature));
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

TEST(InstanceCreatureBinderTest, OwnedMasterPassesBoundaryToHeterogeneousSummon) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "summons" });
	const RuntimeCreatureIdentity master { .id = 501 };
	const RuntimeSummonIdentity summon { .id = 502 };
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
	const RuntimeSummonIdentity summon { .id = 602 };
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
	const RuntimeSummonIdentity summon { .id = 702 };

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
	const RuntimeSummonIdentity second { .id = 802 };
	ASSERT_TRUE(binder.bind(instance.id, first));
	ASSERT_TRUE(binder.bind(instance.id, second));

	EXPECT_THROW(manager.close(instance.id), std::logic_error);
	EXPECT_EQ(InstanceState::Closing, *manager.getState(instance.id));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, binder.relation(first, second));
	EXPECT_FALSE(binder.canInteract(first, second));
}

TEST(InstanceCreatureBinderTest, TransactionCommitsNewOwnershipAfterSuccessfulLink) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "commit" });
	const RuntimeCreatureIdentity master { .id = 901 };
	const RuntimeSummonIdentity summon { .id = 902 };
	ASSERT_TRUE(binder.bind(instance.id, master));

	bool linkApplied = false;
	EXPECT_TRUE(binder.inheritAndApply(master, summon, [&] {
		linkApplied = true;
		return true;
	}));

	EXPECT_TRUE(linkApplied);
	ASSERT_TRUE(binder.ownerOf(summon).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(summon));
}

TEST(InstanceCreatureBinderTest, FalseLinkRollsBackOnlyNewlyInheritedOwnership) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "rollback-false" });
	const RuntimeCreatureIdentity master { .id = 1001 };
	const RuntimeSummonIdentity summon { .id = 1002 };
	ASSERT_TRUE(binder.bind(instance.id, master));

	EXPECT_FALSE(binder.inheritAndApply(master, summon, [] { return false; }));
	EXPECT_FALSE(binder.ownerOf(summon).has_value());
	EXPECT_EQ((std::vector<InstanceCreatureId> { 1001 }), manager.getRegisteredCreatureIds(instance.id));
}

TEST(InstanceCreatureBinderTest, ThrowingLinkRollsBackNewOwnershipAndRethrows) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "rollback-throw" });
	const RuntimeCreatureIdentity master { .id = 1101 };
	const RuntimeSummonIdentity summon { .id = 1102 };
	ASSERT_TRUE(binder.bind(instance.id, master));

	EXPECT_THROW(
		binder.inheritAndApply(master, summon, []() -> bool {
			throw std::runtime_error("synthetic link failure");
		}),
		std::runtime_error
	);
	EXPECT_FALSE(binder.ownerOf(summon).has_value());
	EXPECT_EQ((std::vector<InstanceCreatureId> { 1101 }), manager.getRegisteredCreatureIds(instance.id));
}

TEST(InstanceCreatureBinderTest, FailedLinkPreservesPreexistingSameInstanceOwnership) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "preexisting" });
	const RuntimeCreatureIdentity master { .id = 1201 };
	const RuntimeSummonIdentity summon { .id = 1202 };
	ASSERT_TRUE(binder.bind(instance.id, master));
	ASSERT_TRUE(binder.bind(instance.id, summon));

	EXPECT_FALSE(binder.inheritAndApply(master, summon, [] { return false; }));
	ASSERT_TRUE(binder.ownerOf(summon).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(summon));
	EXPECT_EQ((std::vector<InstanceCreatureId> { 1201, 1202 }), manager.getRegisteredCreatureIds(instance.id));
}

TEST(InstanceCreatureBinderTest, RollbackPreservesNewOwnerAndReportsOwnershipRace) {
	InstanceManager manager(makeBinderRegions(2));
	InstanceCreatureBinder binder(manager);
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	const RuntimeCreatureIdentity master { .id = 1251 };
	const RuntimeSummonIdentity summon { .id = 1252 };
	ASSERT_TRUE(binder.bind(first.id, master));

	EXPECT_THROW(
		binder.inheritAndApply(master, summon, [&]() -> bool {
			EXPECT_TRUE(binder.unbind(summon));
			EXPECT_TRUE(binder.bind(second.id, summon));
			return false;
		}),
		std::logic_error
	);

	ASSERT_TRUE(binder.ownerOf(summon).has_value());
	EXPECT_EQ(second.id, *binder.ownerOf(summon));
	EXPECT_EQ((std::vector<InstanceCreatureId> { 1251 }), manager.getRegisteredCreatureIds(first.id));
	EXPECT_EQ((std::vector<InstanceCreatureId> { 1252 }), manager.getRegisteredCreatureIds(second.id));
}

TEST(InstanceCreatureBinderTest, RejectedInheritanceDoesNotRunLinkOperation) {
	InstanceManager manager(makeBinderRegions(2));
	InstanceCreatureBinder binder(manager);
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	const RuntimeCreatureIdentity master { .id = 1301 };
	const RuntimeSummonIdentity summon { .id = 1302 };
	ASSERT_TRUE(binder.bind(first.id, master));
	ASSERT_TRUE(binder.bind(second.id, summon));

	bool linkCalled = false;
	EXPECT_FALSE(binder.inheritAndApply(master, summon, [&] {
		linkCalled = true;
		return true;
	}));
	EXPECT_FALSE(linkCalled);
	EXPECT_EQ(first.id, *binder.ownerOf(master));
	EXPECT_EQ(second.id, *binder.ownerOf(summon));
}

TEST(InstanceCreatureBinderTest, NormalWorldTransactionRunsWithoutCreatingOwnership) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const RuntimeCreatureIdentity master { .id = 1401 };
	const RuntimeSummonIdentity summon { .id = 1402 };

	bool linkCalled = false;
	EXPECT_TRUE(binder.inheritAndApply(master, summon, [&] {
		linkCalled = true;
		return true;
	}));
	EXPECT_TRUE(linkCalled);
	EXPECT_FALSE(binder.ownerOf(master).has_value());
	EXPECT_FALSE(binder.ownerOf(summon).has_value());
}

TEST(InstanceCreatureBinderTest, LegacySetMasterKeepsNormalWorldBehavior) {
	const auto master = makeRuntimeMonster("legacy-master");
	const auto summon = makeRuntimeMonster("legacy-summon");

	EXPECT_TRUE(summon->setMaster(master));
	EXPECT_EQ(master, summon->getMaster());
	EXPECT_TRUE(summon->hasBeenSummoned());
	ASSERT_EQ(1u, master->getSummons().size());
	EXPECT_EQ(summon, master->getSummons().front());
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterCommitsOwnershipAndLink) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "runtime-master-link" });
	const auto master = makeRuntimeMonster("instance-master");
	const auto summon = makeRuntimeMonster("instance-summon");
	ASSERT_TRUE(instance.ok);
	ASSERT_TRUE(binder.bind(instance.id, *master));

	EXPECT_TRUE(summon->setMaster(master, binder));
	EXPECT_EQ(master, summon->getMaster());
	EXPECT_TRUE(summon->hasBeenSummoned());
	ASSERT_TRUE(binder.ownerOf(*summon).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(*summon));
	ASSERT_EQ(1u, master->getSummons().size());
	EXPECT_EQ(summon, master->getSummons().front());
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterRejectsCrossInstanceBeforeMutation) {
	InstanceManager manager(makeBinderRegions(2));
	InstanceCreatureBinder binder(manager);
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	const auto master = makeRuntimeMonster("first-master");
	const auto summon = makeRuntimeMonster("second-summon");
	ASSERT_TRUE(first.ok);
	ASSERT_TRUE(second.ok);
	ASSERT_TRUE(binder.bind(first.id, *master));
	ASSERT_TRUE(binder.bind(second.id, *summon));

	EXPECT_FALSE(summon->setMaster(master, binder));
	EXPECT_FALSE(summon->getMaster());
	EXPECT_FALSE(summon->hasBeenSummoned());
	EXPECT_TRUE(master->getSummons().empty());
	EXPECT_EQ(first.id, *binder.ownerOf(*master));
	EXPECT_EQ(second.id, *binder.ownerOf(*summon));
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterRejectsUnownedMasterForOwnedSummon) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "owned-summon" });
	const auto master = makeRuntimeMonster("unowned-master");
	const auto summon = makeRuntimeMonster("owned-summon");
	ASSERT_TRUE(instance.ok);
	ASSERT_TRUE(binder.bind(instance.id, *summon));

	EXPECT_FALSE(summon->setMaster(master, binder));
	EXPECT_FALSE(summon->getMaster());
	EXPECT_FALSE(summon->hasBeenSummoned());
	EXPECT_TRUE(master->getSummons().empty());
	EXPECT_FALSE(binder.ownerOf(*master).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(*summon));
}

TEST(InstanceCreatureBinderTest, InstanceAwareSetMasterReassignsWithinSameInstance) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "reassign" });
	const auto firstMaster = makeRuntimeMonster("first-master");
	const auto secondMaster = makeRuntimeMonster("second-master");
	const auto summon = makeRuntimeMonster("reassigned-summon");
	ASSERT_TRUE(instance.ok);
	ASSERT_TRUE(binder.bind(instance.id, *firstMaster));
	ASSERT_TRUE(binder.bind(instance.id, *secondMaster));
	ASSERT_TRUE(summon->setMaster(firstMaster, binder));

	EXPECT_TRUE(summon->setMaster(secondMaster, binder));
	EXPECT_EQ(secondMaster, summon->getMaster());
	EXPECT_TRUE(firstMaster->getSummons().empty());
	ASSERT_EQ(1u, secondMaster->getSummons().size());
	EXPECT_EQ(summon, secondMaster->getSummons().front());
	EXPECT_EQ(instance.id, *binder.ownerOf(*summon));
	EXPECT_EQ(3u, manager.registeredCreatureCount(instance.id));
}

TEST(InstanceCreatureBinderTest, InstanceAwareClearMasterPreservesOwnershipBoundary) {
	InstanceManager manager(makeBinderRegions(1));
	InstanceCreatureBinder binder(manager);
	const auto instance = manager.createInstance({ .name = "clear-master" });
	const auto master = makeRuntimeMonster("clear-master");
	const auto summon = makeRuntimeMonster("clear-summon");
	ASSERT_TRUE(instance.ok);
	ASSERT_TRUE(binder.bind(instance.id, *master));
	ASSERT_TRUE(summon->setMaster(master, binder));

	EXPECT_TRUE(summon->setMaster(nullptr, binder));
	EXPECT_FALSE(summon->getMaster());
	EXPECT_TRUE(summon->hasBeenSummoned());
	EXPECT_TRUE(master->getSummons().empty());
	ASSERT_TRUE(binder.ownerOf(*summon).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(*summon));
}
