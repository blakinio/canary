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
#include "game/game.hpp"

namespace {
	std::shared_ptr<Monster> createAndPlaceArenaMonster(const Position &position) {
		const auto &monster = Monster::createMonster(InstanceArenaService::MonsterName);
		if (!monster || !g_game().placeCreature(monster, position, false, true)) {
			return nullptr;
		}
		return monster;
	}

	void removeArenaCreature(uint32_t creatureId) {
		if (const auto &creature = g_game().getCreatureByID(creatureId)) {
			g_game().removeCreature(creature);
		}
	}
} // namespace

InstanceArenaService::InstanceArenaService(InstanceManager &manager) :
	InstanceArenaService(manager, &createAndPlaceArenaMonster, &removeArenaCreature) { }

InstanceArenaService::InstanceArenaService(InstanceManager &manager, MonsterFactory monsterFactory, CreatureRemover creatureRemover) :
	manager(manager), binder(manager), monsterFactory(std::move(monsterFactory)), creatureRemover(std::move(creatureRemover)) { }

std::vector<InstanceMapRegion> InstanceArenaService::configuredRegions() {
	// Coordinates verified in docs/architecture/instanced-test-arena.md:
	// both regions sit inside the existing "Tps Room" GM/test hall on
	// data-canary/world/canary.otbm, confirmed zero-mechanic by a full-map
	// OTBM item audit + script resolution run cross-referenced against
	// both boxes. Same 12x7 size, non-overlapping, 8-tile buffer between
	// them.
	return {
		InstanceMapRegion {
			.slot = toSlotId(0),
			.minX = 19976,
			.minY = 19988,
			.minZ = 7,
			.maxX = 19987,
			.maxY = 19994,
			.maxZ = 7,
			.name = "InstanceTestArenaSlotOne",
		},
		InstanceMapRegion {
			.slot = toSlotId(1),
			.minX = 19996,
			.minY = 19988,
			.minZ = 7,
			.maxX = 20007,
			.maxY = 19994,
			.maxZ = 7,
			.name = "InstanceTestArenaSlotTwo",
		},
	};
}

InstanceArenaService::CreateResult InstanceArenaService::createArena() {
	auto result = manager.createInstance({ .name = "instance-test-arena" });
	if (!result.ok) {
		return { .ok = false, .id = InstanceId::Invalid, .error = result.error };
	}

	if (!manager.activate(result.id)) {
		manager.close(result.id);
		return { .ok = false, .id = InstanceId::Invalid, .error = "failed to activate arena instance" };
	}

	return { .ok = true, .id = result.id, .error = {} };
}

bool InstanceArenaService::closeArena(InstanceId id) {
	return manager.close(id);
}

std::optional<InstanceState> InstanceArenaService::getState(InstanceId id) const {
	return manager.getState(id);
}

std::optional<InstanceMapRegion> InstanceArenaService::getRegion(InstanceId id) const {
	return manager.getRegion(id);
}

std::size_t InstanceArenaService::activeArenaCount() const {
	return manager.activeInstanceCount();
}

InstanceArenaService::EnterResult InstanceArenaService::enterArena(uint32_t playerId, const Position &returnPosition) {
	// Held across the whole operation (not just the "already has a session"
	// check) to avoid a create-under-race double session for the same
	// player. Safe from deadlock: nothing else ever holds InstanceManager's
	// internal mutex while trying to acquire this one.
	std::scoped_lock lock(sessionMutex);
	if (sessions.contains(playerId)) {
		return { .ok = false, .entryPosition = {}, .error = "You already have an active instance arena. Close it first." };
	}

	const auto created = createArena();
	if (!created.ok) {
		return { .ok = false, .entryPosition = {}, .error = created.error };
	}

	// InstanceManager::close() refuses to release a region while any
	// creature id remains registered (it quarantines the instance instead)
	// - this cleanup callback is what actually removes the arena's
	// creatures so a normal close() can succeed. Runs outside
	// InstanceManager's own lock and never touches sessionMutex.
	manager.setCleanupCallback(created.id, [this](InstanceId instanceId, const InstanceMapRegion &) {
		for (const auto creatureId : manager.getRegisteredCreatureIds(instanceId)) {
			creatureRemover(creatureId);
		}
	});

	const auto region = manager.getRegion(created.id);
	if (!region) {
		manager.close(created.id);
		return { .ok = false, .entryPosition = {}, .error = "internal error: created arena has no region" };
	}

	const Position entryPosition { region->minX, region->minY, region->minZ };

	// A few tiles in from the entry corner, still well inside the 12x7
	// region - never on top of where the player is about to be teleported.
	const Position monsterPosition {
		static_cast<uint16_t>(region->minX + 4),
		static_cast<uint16_t>(region->minY + 3),
		region->minZ,
	};

	const auto &monster = monsterFactory(monsterPosition);
	if (!monster) {
		manager.close(created.id);
		return { .ok = false, .entryPosition = {}, .error = "failed to spawn the arena monster" };
	}

	// Only after the factory assigned a real, nonzero runtime id (the
	// production factory does this via Game::placeCreature()).
	if (!binder.bind(created.id, monster)) {
		creatureRemover(monster->getID());
		manager.close(created.id);
		return { .ok = false, .entryPosition = {}, .error = "failed to register the arena monster" };
	}

	sessions.emplace(playerId, PlayerSession { .instanceId = created.id, .returnPosition = returnPosition });
	return { .ok = true, .entryPosition = entryPosition, .monsterId = monster->getID(), .error = {} };
}

InstanceArenaService::LeaveResult InstanceArenaService::leaveArena(uint32_t playerId) {
	std::scoped_lock lock(sessionMutex);
	const auto it = sessions.find(playerId);
	if (it == sessions.end()) {
		return { .ok = false, .returnPosition = {}, .error = "You do not have an active instance arena." };
	}

	// The arena instance stays reserved - only closeArenaForPlayer() (or a
	// future timeout) releases it.
	return { .ok = true, .returnPosition = it->second.returnPosition, .error = {} };
}

InstanceArenaService::CloseResult InstanceArenaService::closeArenaForPlayer(uint32_t playerId) {
	std::scoped_lock lock(sessionMutex);
	const auto it = sessions.find(playerId);
	if (it == sessions.end()) {
		return { .ok = false, .evacuationPosition = {}, .error = "You do not have an active instance arena." };
	}

	// manager.close() runs the cleanup callback registered in enterArena()
	// outside InstanceManager's own lock, but this call happens while
	// sessionMutex is held - that callback must never try to re-acquire
	// sessionMutex (it doesn't: it only touches InstanceManager and Game).
	const auto session = it->second;
	manager.close(session.instanceId);
	sessions.erase(it);
	return { .ok = true, .evacuationPosition = session.returnPosition, .error = {} };
}

bool InstanceArenaService::hasActiveSession(uint32_t playerId) const {
	std::scoped_lock lock(sessionMutex);
	return sessions.contains(playerId);
}
