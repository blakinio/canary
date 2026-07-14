/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_arena_service.hpp"

#include "creatures/monsters/monster.hpp"
#include "creatures/monsters/monsters.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <chrono>
	#include <cstdint>
	#include <string>
	#include <utility>
	#include <vector>
#endif

namespace {

	// Mirrors instance_creature_binder_test.cpp's makeRuntimeMonster(): builds
	// a real Monster with a real runtime id, bypassing Monster::createMonster()
	// and Game::placeCreature() (both need a fully bootstrapped server this
	// unit-test harness doesn't provide - see docs/architecture/
	// instanced-test-arena.md).
	std::shared_ptr<Monster> makeRuntimeMonster(const std::string &name) {
		const auto monsterType = std::make_shared<MonsterType>(name);
		const auto monster = std::make_shared<Monster>(monsterType);
		monster->setID();
		return monster;
	}

	struct RecordedSchedule {
		uint32_t delayMs = 0;
		std::function<void()> callback;
	};

	// Wires InstanceArenaService's full DI seam to synthetic implementations
	// so enterArena()/closeArenaForPlayer()/reapExpiredSessions() are testable
	// without a live Game or dispatcher. The remover mirrors the real
	// Game::removeCreature() hook (game.cpp, "getInstanceManager().
	// unregisterCreature(...)") so a synthetic close() exercises the same
	// registered-creature bookkeeping the production path relies on. The
	// event scheduler records (delay, callback) pairs instead of running them
	// on a real dispatcher, so tests can fire a closing warning on demand.
	struct SyntheticArenaHarness {
		InstanceManager manager;
		std::vector<uint32_t> removedCreatureIds;
		std::vector<RecordedSchedule> scheduledEvents;
		std::vector<std::pair<uint32_t, std::string>> notifiedMessages;
		std::vector<std::pair<uint32_t, Position>> evacuatedPlayers;
		InstanceArenaService service;

		explicit SyntheticArenaHarness(bool monsterFactorySucceeds = true) :
			manager(InstanceArenaService::configuredRegions()),
			service(
				manager,
				[monsterFactorySucceeds](const Position &) -> std::shared_ptr<Monster> {
					return monsterFactorySucceeds ? makeRuntimeMonster("test-arena-monster") : nullptr;
				},
				[this](uint32_t creatureId) {
					removedCreatureIds.push_back(creatureId);
					if (const auto owner = manager.getCreatureOwner(creatureId)) {
						manager.unregisterCreature(*owner, creatureId);
					}
				},
				[this](uint32_t delayMs, std::function<void()> callback) {
					scheduledEvents.push_back({ .delayMs = delayMs, .callback = std::move(callback) });
				},
				[this](uint32_t playerId, const std::string &message) {
					notifiedMessages.emplace_back(playerId, message);
				},
				[this](uint32_t playerId, const Position &returnPosition) {
					evacuatedPlayers.emplace_back(playerId, returnPosition);
				}
			) { }
	};

	// Far enough past ArenaTimeout that closeExpiredInstances() always treats
	// every arena created "now" as expired, regardless of test execution time.
	std::chrono::steady_clock::time_point farFutureExpiry() {
		return std::chrono::steady_clock::now() + InstanceArenaService::ArenaTimeout + std::chrono::seconds(60);
	}

} // namespace

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

TEST(InstanceArenaServiceTest, CreateArenaUsesATimeoutSoIdleArenasExpireAutomatically) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto result = service.createArena();
	ASSERT_TRUE(result.ok);

	// closeExpiredInstances() goes through the same idempotent close() path
	// as a manual close - this proves the arena actually has a nonzero
	// timeout, not just that InstanceManager supports one.
	EXPECT_EQ(1u, manager.closeExpiredInstances(farFutureExpiry()));
	EXPECT_EQ(InstanceState::Destroyed, *service.getState(result.id));
	EXPECT_EQ(0u, service.activeArenaCount());
}

TEST(InstanceArenaServiceTest, EnterArenaReturnsAnEntryPositionInsideTheReservedRegion) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };

	const auto entered = harness.service.enterArena(1, returnPosition);

	ASSERT_TRUE(entered.ok);
	EXPECT_TRUE(harness.service.hasActiveSession(1));
	EXPECT_NE(0u, entered.monsterId);
	// Entry position must be one configured region's minX/minY/minZ corner.
	bool matchedARegion = false;
	for (const auto &configured : InstanceArenaService::configuredRegions()) {
		if (entered.entryPosition.x == configured.minX && entered.entryPosition.y == configured.minY && entered.entryPosition.z == configured.minZ) {
			matchedARegion = true;
		}
	}
	EXPECT_TRUE(matchedARegion);
}

TEST(InstanceArenaServiceTest, EnterArenaRegistersTheSpawnedMonsterWithTheBinder) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };

	const auto entered = harness.service.enterArena(1, returnPosition);

	ASSERT_TRUE(entered.ok);
	ASSERT_NE(0u, entered.monsterId);
	const auto owner = harness.manager.getCreatureOwner(entered.monsterId);
	ASSERT_TRUE(owner.has_value());
	EXPECT_EQ(
		(std::vector<InstanceCreatureId> { static_cast<InstanceCreatureId>(entered.monsterId) }),
		harness.manager.getRegisteredCreatureIds(*owner)
	);
}

TEST(InstanceArenaServiceTest, EnterArenaRollsBackTheWholeArenaWhenTheMonsterFactoryFails) {
	SyntheticArenaHarness harness(/* monsterFactorySucceeds */ false);
	constexpr Position returnPosition { 100, 100, 7 };

	const auto entered = harness.service.enterArena(1, returnPosition);

	EXPECT_FALSE(entered.ok);
	EXPECT_FALSE(entered.error.empty());
	EXPECT_FALSE(harness.service.hasActiveSession(1));
	EXPECT_EQ(0u, harness.service.activeArenaCount()) << "a failed monster spawn must free the reserved region again";
}

TEST(InstanceArenaServiceTest, EnterArenaFailsWhenPlayerAlreadyHasASession) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };

	ASSERT_TRUE(harness.service.enterArena(1, returnPosition).ok);
	const auto second = harness.service.enterArena(1, returnPosition);

	EXPECT_FALSE(second.ok);
	EXPECT_FALSE(second.error.empty());
	EXPECT_EQ(1u, harness.service.activeArenaCount()) << "the failed second enter must not create a stray instance";
}

TEST(InstanceArenaServiceTest, EnterArenaFailsWithoutASessionWhenNoRegionIsFree) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };

	ASSERT_TRUE(harness.service.enterArena(1, returnPosition).ok);
	ASSERT_TRUE(harness.service.enterArena(2, returnPosition).ok);

	const auto third = harness.service.enterArena(3, returnPosition);
	EXPECT_FALSE(third.ok);
	EXPECT_FALSE(harness.service.hasActiveSession(3));
}

TEST(InstanceArenaServiceTest, EnterArenaSchedulesExactlyOneClosingWarningBeforeTheTimeout) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };

	ASSERT_TRUE(harness.service.enterArena(1, returnPosition).ok);

	ASSERT_EQ(1u, harness.scheduledEvents.size());
	const auto expectedDelayMs = std::chrono::duration_cast<std::chrono::milliseconds>(
									 InstanceArenaService::ArenaTimeout - InstanceArenaService::ArenaClosingWarningLeadTime
	)
									 .count();
	EXPECT_EQ(static_cast<uint32_t>(expectedDelayMs), harness.scheduledEvents[0].delayMs);
	EXPECT_TRUE(harness.notifiedMessages.empty()) << "the warning must not fire until the scheduler runs it";
}

TEST(InstanceArenaServiceTest, ClosingWarningFiresWhenTheArenaIsStillActiveAtDelayElapse) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };
	constexpr uint32_t playerId = 1;

	ASSERT_TRUE(harness.service.enterArena(playerId, returnPosition).ok);
	ASSERT_EQ(1u, harness.scheduledEvents.size());

	harness.scheduledEvents[0].callback();

	ASSERT_EQ(1u, harness.notifiedMessages.size());
	EXPECT_EQ(playerId, harness.notifiedMessages[0].first);
	EXPECT_FALSE(harness.notifiedMessages[0].second.empty());
}

TEST(InstanceArenaServiceTest, ClosingWarningIsANoOpAfterTheArenaAlreadyClosed) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };
	constexpr uint32_t playerId = 1;

	ASSERT_TRUE(harness.service.enterArena(playerId, returnPosition).ok);
	ASSERT_EQ(1u, harness.scheduledEvents.size());
	ASSERT_TRUE(harness.service.closeArenaForPlayer(playerId).ok);

	// Simulates the scheduler eventually running the callback it queued
	// before the arena closed - InstanceScopedEvent must make this a no-op.
	harness.scheduledEvents[0].callback();

	EXPECT_TRUE(harness.notifiedMessages.empty()) << "a closed instance must not execute this gameplay callback";
}

TEST(InstanceArenaServiceTest, TimeoutExpiryUsesTheSameCleanupPathAsManualClose) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 100, 100, 7 };

	const auto entered = harness.service.enterArena(1, returnPosition);
	ASSERT_TRUE(entered.ok);
	ASSERT_NE(0u, entered.monsterId);

	EXPECT_EQ(1u, harness.manager.closeExpiredInstances(farFutureExpiry()));

	EXPECT_NE(
		harness.removedCreatureIds.end(),
		std::find(harness.removedCreatureIds.begin(), harness.removedCreatureIds.end(), entered.monsterId)
	) << "expiry must run the same cleanup callback a manual close does";
	EXPECT_FALSE(harness.manager.getCreatureOwner(entered.monsterId).has_value());
}

TEST(InstanceArenaServiceTest, ReapExpiredSessionsEvacuatesAndForgetsATimedOutSession) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 321, 654, 7 };
	constexpr uint32_t playerId = 1;

	ASSERT_TRUE(harness.service.enterArena(playerId, returnPosition).ok);
	ASSERT_EQ(1u, harness.manager.closeExpiredInstances(farFutureExpiry())) << "the instance must expire before reaping can find it";

	harness.service.reapExpiredSessions();

	ASSERT_EQ(1u, harness.evacuatedPlayers.size());
	EXPECT_EQ(playerId, harness.evacuatedPlayers[0].first);
	EXPECT_EQ(returnPosition, harness.evacuatedPlayers[0].second);
	EXPECT_FALSE(harness.service.hasActiveSession(playerId));

	// The stale session is gone - later calls must fail cleanly rather than
	// operate on a Destroyed instance.
	EXPECT_FALSE(harness.service.leaveArena(playerId).ok);
	EXPECT_FALSE(harness.service.closeArenaForPlayer(playerId).ok);
}

TEST(InstanceArenaServiceTest, ReapExpiredSessionsIsANoOpWhileTheArenaIsStillActive) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 321, 654, 7 };
	constexpr uint32_t playerId = 1;

	ASSERT_TRUE(harness.service.enterArena(playerId, returnPosition).ok);

	harness.service.reapExpiredSessions();

	EXPECT_TRUE(harness.evacuatedPlayers.empty());
	EXPECT_TRUE(harness.service.hasActiveSession(playerId));
}

TEST(InstanceArenaServiceTest, LeaveArenaReturnsSavedPositionWithoutReleasingTheRegion) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 123, 456, 7 };

	ASSERT_TRUE(harness.service.enterArena(1, returnPosition).ok);
	const auto left = harness.service.leaveArena(1);

	ASSERT_TRUE(left.ok);
	EXPECT_EQ(returnPosition, left.returnPosition);
	EXPECT_TRUE(harness.service.hasActiveSession(1)) << "leaving must not close the arena";
	EXPECT_EQ(1u, harness.service.activeArenaCount());
}

TEST(InstanceArenaServiceTest, LeaveArenaFailsWithoutAnActiveSession) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto left = service.leaveArena(999);
	EXPECT_FALSE(left.ok);
	EXPECT_FALSE(left.error.empty());
}

TEST(InstanceArenaServiceTest, CloseArenaForPlayerEvacuatesAndReleasesTheRegion) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 321, 654, 7 };

	const auto entered = harness.service.enterArena(1, returnPosition);
	ASSERT_TRUE(entered.ok);
	const auto closed = harness.service.closeArenaForPlayer(1);

	ASSERT_TRUE(closed.ok);
	EXPECT_EQ(returnPosition, closed.evacuationPosition);
	EXPECT_FALSE(harness.service.hasActiveSession(1));
	EXPECT_EQ(0u, harness.service.activeArenaCount());

	// The region must be reusable immediately after a clean close.
	const auto reentered = harness.service.enterArena(1, returnPosition);
	EXPECT_TRUE(reentered.ok);
}

TEST(InstanceArenaServiceTest, CloseArenaForPlayerRemovesTheRegisteredMonsterViaTheInjectedRemover) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 321, 654, 7 };

	const auto entered = harness.service.enterArena(1, returnPosition);
	ASSERT_TRUE(entered.ok);
	ASSERT_NE(0u, entered.monsterId);

	const auto closed = harness.service.closeArenaForPlayer(1);

	ASSERT_TRUE(closed.ok) << "InstanceManager::close() must not throw: the cleanup callback has to empty the registry first";
	EXPECT_NE(
		harness.removedCreatureIds.end(),
		std::find(harness.removedCreatureIds.begin(), harness.removedCreatureIds.end(), entered.monsterId)
	);
	EXPECT_FALSE(harness.manager.getCreatureOwner(entered.monsterId).has_value());
}

TEST(InstanceArenaServiceTest, CloseArenaForPlayerWorksAfterLeaveArenaToo) {
	SyntheticArenaHarness harness;
	constexpr Position returnPosition { 321, 654, 7 };

	ASSERT_TRUE(harness.service.enterArena(1, returnPosition).ok);
	ASSERT_TRUE(harness.service.leaveArena(1).ok);

	const auto closed = harness.service.closeArenaForPlayer(1);
	ASSERT_TRUE(closed.ok);
	EXPECT_EQ(returnPosition, closed.evacuationPosition);
	EXPECT_FALSE(harness.service.hasActiveSession(1));
}

TEST(InstanceArenaServiceTest, CloseArenaForPlayerFailsWithoutAnActiveSession) {
	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);

	const auto closed = service.closeArenaForPlayer(999);
	EXPECT_FALSE(closed.ok);
	EXPECT_FALSE(closed.error.empty());
}

TEST(InstanceArenaServiceTest, TwoPlayersGetIndependentSessionsAndRegions) {
	SyntheticArenaHarness harness;
	constexpr Position returnPositionOne { 100, 100, 7 };
	constexpr Position returnPositionTwo { 200, 200, 7 };

	const auto enteredOne = harness.service.enterArena(1, returnPositionOne);
	const auto enteredTwo = harness.service.enterArena(2, returnPositionTwo);

	ASSERT_TRUE(enteredOne.ok);
	ASSERT_TRUE(enteredTwo.ok);
	EXPECT_NE(enteredOne.entryPosition, enteredTwo.entryPosition);
	EXPECT_NE(enteredOne.monsterId, enteredTwo.monsterId);

	ASSERT_TRUE(harness.service.closeArenaForPlayer(1).ok);
	EXPECT_TRUE(harness.service.hasActiveSession(2)) << "closing one player's arena must not affect the other";
	EXPECT_EQ(1u, harness.service.activeArenaCount());
}
