/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_arena_service.hpp"

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
