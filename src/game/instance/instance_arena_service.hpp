/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_creature_binder.hpp"
#include "game/instance/instance_manager.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstddef>
	#include <optional>
	#include <string>
	#include <vector>
#endif

// The Instanced Test Arena's real consumer of InstanceManager (see
// docs/architecture/instanced-test-arena.md for the full region-selection
// evidence). Deliberately not a generic dungeon/instance framework: the
// region list is fixed and specific to this one administrator-only vertical
// slice.
//
// Takes the shared InstanceManager by reference (Game::getInstanceManager())
// rather than owning a second one - this program must not create an
// alternative manager, registry or binder.
class InstanceArenaService {
public:
	explicit InstanceArenaService(InstanceManager &manager) noexcept :
		manager(manager), binder(manager) { }

	InstanceArenaService(const InstanceArenaService &) = delete;
	InstanceArenaService &operator=(const InstanceArenaService &) = delete;

	// The two same-size, non-overlapping, evidence-backed regions this
	// feature is configured with. This is the single place the exact
	// coordinates from docs/architecture/instanced-test-arena.md are
	// written down; Game's InstanceManager member is constructed from this
	// list so there is exactly one region configuration in the codebase.
	[[nodiscard]] static std::vector<InstanceMapRegion> configuredRegions();

	struct CreateResult {
		bool ok = false;
		InstanceId id = InstanceId::Invalid;
		std::string error;
	};

	// Reserves a free arena region, creates the instance and activates it
	// immediately - the arena has no multi-step Creating setup phase.
	// Fails without creating a record when both regions are already
	// reserved.
	[[nodiscard]] CreateResult createArena();

	// Idempotent; delegates directly to InstanceManager::close().
	bool closeArena(InstanceId id);

	[[nodiscard]] std::optional<InstanceState> getState(InstanceId id) const;
	[[nodiscard]] std::optional<InstanceMapRegion> getRegion(InstanceId id) const;

	[[nodiscard]] InstanceManager &getManager() noexcept {
		return manager;
	}

	[[nodiscard]] InstanceCreatureBinder &getBinder() noexcept {
		return binder;
	}

	[[nodiscard]] std::size_t activeArenaCount() const;

private:
	InstanceManager &manager;
	InstanceCreatureBinder binder;
};
